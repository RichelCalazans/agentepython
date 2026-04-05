"""Motor de busca de notas no vault do Obsidian."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from core.config import ObsidianConfig
from core.logger import configurar_logger

logger = configurar_logger()


@dataclass
class ResultadoBusca:
    """Um resultado de busca com metadados e trecho relevante."""
    titulo: str
    caminho: str
    score: float
    trecho: str
    data: str
    categoria: str
    tags: list[str]


def _carregar_nota(caminho: Path) -> dict[str, str | list[str]]:
    """Carrega uma nota .md e extrai frontmatter + conteúdo.

    Args:
        caminho: Caminho do arquivo .md.

    Returns:
        Dicionário com metadados e conteúdo.
    """
    try:
        texto = caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}

    resultado: dict[str, str | list[str]] = {
        "titulo": caminho.stem,
        "conteudo": texto,
        "caminho": str(caminho),
        "data": "",
        "categoria": "",
        "tags": [],
    }

    # Extrai frontmatter YAML
    if texto.startswith("---"):
        partes = texto.split("---", 2)
        if len(partes) >= 3:
            try:
                meta = yaml.safe_load(partes[1]) or {}
                resultado["titulo"] = meta.get("titulo", caminho.stem)
                resultado["data"] = str(meta.get("data", ""))
                resultado["categoria"] = meta.get("categoria", "")
                resultado["tags"] = meta.get("tags", [])
                resultado["conteudo"] = partes[2].strip()
            except yaml.YAMLError:
                pass

    return resultado


def _calcular_tfidf(query_tokens: list[str], doc_tokens: list[str], total_docs: int, doc_freq: dict[str, int]) -> float:
    """Calcula score TF-IDF simplificado.

    Args:
        query_tokens: Tokens da busca.
        doc_tokens: Tokens do documento.
        total_docs: Total de documentos no corpus.
        doc_freq: Frequência de cada token no corpus.

    Returns:
        Score de relevância.
    """
    if not doc_tokens or not query_tokens:
        return 0.0

    tf = Counter(doc_tokens)
    score = 0.0
    for token in query_tokens:
        if token in tf:
            term_freq = tf[token] / len(doc_tokens)
            # IDF com suavização: +1 no numerador para que documentos únicos tenham score > 0
            inv_doc_freq = math.log(1 + (total_docs + 1) / (doc_freq.get(token, 0) + 1))
            score += term_freq * inv_doc_freq
    return score


def _tokenizar(texto: str) -> list[str]:
    """Tokeniza texto em palavras normalizadas.

    Args:
        texto: Texto a tokenizar.

    Returns:
        Lista de tokens em minúsculas.
    """
    return re.findall(r"\w+", texto.lower())


def _extrair_trecho(conteudo: str, query_tokens: list[str], tamanho: int = 150) -> str:
    """Extrai trecho relevante do conteúdo.

    Args:
        conteudo: Conteúdo completo da nota.
        query_tokens: Tokens da busca para encontrar contexto.
        tamanho: Tamanho máximo do trecho.

    Returns:
        Trecho com contexto ao redor do match.
    """
    conteudo_lower = conteudo.lower()
    melhor_pos = 0
    for token in query_tokens:
        pos = conteudo_lower.find(token)
        if pos >= 0:
            melhor_pos = pos
            break

    inicio = max(0, melhor_pos - 30)
    fim = min(len(conteudo), inicio + tamanho)
    trecho = conteudo[inicio:fim].strip()

    if inicio > 0:
        trecho = "..." + trecho
    if fim < len(conteudo):
        trecho = trecho + "..."

    return trecho


def _parsear_filtros(query: str) -> tuple[str, dict[str, str]]:
    """Extrai filtros especiais da query (tags:X, prioridade:X, data:>X).

    Args:
        query: String de busca com possíveis filtros.

    Returns:
        Tupla com (query limpa, dicionário de filtros).
    """
    filtros: dict[str, str] = {}
    query_limpa = query

    # tags:valor
    match = re.search(r"tags?:(\S+)", query)
    if match:
        filtros["tags"] = match.group(1)
        query_limpa = query_limpa.replace(match.group(0), "").strip()

    # prioridade:valor
    match = re.search(r"prioridade:(\S+)", query)
    if match:
        filtros["prioridade"] = match.group(1)
        query_limpa = query_limpa.replace(match.group(0), "").strip()

    # categoria:valor
    match = re.search(r"categoria:(\S+)", query)
    if match:
        filtros["categoria"] = match.group(1)
        query_limpa = query_limpa.replace(match.group(0), "").strip()

    # data:>YYYY-MM-DD
    match = re.search(r"data:>(\S+)", query)
    if match:
        filtros["data_apos"] = match.group(1)
        query_limpa = query_limpa.replace(match.group(0), "").strip()

    return query_limpa, filtros


def _aplicar_filtros(nota: dict[str, str | list[str]], filtros: dict[str, str]) -> bool:
    """Verifica se a nota passa nos filtros.

    Args:
        nota: Dados da nota.
        filtros: Filtros a aplicar.

    Returns:
        True se a nota passa em todos os filtros.
    """
    if "tags" in filtros:
        tags_nota = nota.get("tags", [])
        if isinstance(tags_nota, list):
            if not any(filtros["tags"].lower() in t.lower() for t in tags_nota):
                return False

    if "prioridade" in filtros:
        # Prioridade está no frontmatter dentro do conteúdo bruto
        conteudo = str(nota.get("conteudo", ""))
        if filtros["prioridade"].lower() not in conteudo.lower():
            return False

    if "categoria" in filtros:
        if filtros["categoria"].lower() != str(nota.get("categoria", "")).lower():
            return False

    if "data_apos" in filtros:
        data_nota = str(nota.get("data", ""))
        if data_nota and data_nota < filtros["data_apos"]:
            return False

    return True


def buscar_notas(query: str, config: ObsidianConfig, max_resultados: int = 5) -> list[ResultadoBusca]:
    """Busca notas no vault do Obsidian por relevância.

    Suporta busca full-text com ranking TF-IDF e filtros especiais.

    Args:
        query: Texto de busca (pode incluir filtros como tags:X, prioridade:alta).
        config: Configuração do Obsidian.
        max_resultados: Número máximo de resultados a retornar.

    Returns:
        Lista de resultados ordenados por relevância.
    """
    vault = Path(config.vault_path)
    if not vault.exists():
        logger.warning("Vault não encontrado: %s", vault)
        return []

    query_limpa, filtros = _parsear_filtros(query)
    query_tokens = _tokenizar(query_limpa)

    if not query_tokens and not filtros:
        return []

    # Carrega todas as notas
    arquivos = list(vault.rglob("*.md"))
    notas_dados: list[dict[str, str | list[str]]] = []
    for arq in arquivos:
        dados = _carregar_nota(arq)
        if dados:
            notas_dados.append(dados)

    if not notas_dados:
        return []

    # Calcula document frequency para TF-IDF
    doc_freq: dict[str, int] = Counter()
    docs_tokenizados: list[list[str]] = []
    for nota in notas_dados:
        tokens = _tokenizar(f"{nota['titulo']} {nota['conteudo']}")
        docs_tokenizados.append(tokens)
        for token in set(tokens):
            doc_freq[token] += 1

    # Busca e ranqueia
    resultados: list[ResultadoBusca] = []
    for i, nota in enumerate(notas_dados):
        if not _aplicar_filtros(nota, filtros):
            continue

        score = _calcular_tfidf(query_tokens, docs_tokenizados[i], len(notas_dados), doc_freq)

        # Boost por match no título
        titulo_tokens = _tokenizar(str(nota["titulo"]))
        for qt in query_tokens:
            if qt in titulo_tokens:
                score *= 2.0

        if score > 0 or (not query_tokens and filtros):
            conteudo = str(nota.get("conteudo", ""))
            trecho = _extrair_trecho(conteudo, query_tokens)
            tags = nota.get("tags", [])

            resultados.append(ResultadoBusca(
                titulo=str(nota["titulo"]),
                caminho=str(nota["caminho"]),
                score=score,
                trecho=trecho,
                data=str(nota.get("data", "")),
                categoria=str(nota.get("categoria", "")),
                tags=tags if isinstance(tags, list) else [],
            ))

    resultados.sort(key=lambda r: r.score, reverse=True)
    return resultados[:max_resultados]


def formatar_resultados(resultados: list[ResultadoBusca]) -> str:
    """Formata resultados de busca como texto legível.

    Args:
        resultados: Lista de resultados de busca.

    Returns:
        Texto formatado com os resultados.
    """
    if not resultados:
        return "Nenhuma nota encontrada para essa busca."

    linhas: list[str] = [f"Encontrei {len(resultados)} nota(s):\n"]
    for i, r in enumerate(resultados, 1):
        linhas.append(f"**{i}. {r.titulo}**")
        if r.categoria:
            linhas.append(f"   Categoria: {r.categoria}")
        if r.tags:
            linhas.append(f"   Tags: {', '.join(r.tags)}")
        if r.data:
            linhas.append(f"   Data: {r.data}")
        linhas.append(f"   {r.trecho}")
        linhas.append("")

    return "\n".join(linhas)
