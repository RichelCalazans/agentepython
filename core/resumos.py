"""Gerador de resumos automáticos de notas do vault."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import yaml

from core.config import AppConfig
from core.logger import configurar_logger
from core.ollama import consultar_ollama

logger = configurar_logger()


def _carregar_notas_por_periodo(
    vault_path: str,
    dias: int = 7,
) -> list[dict[str, str]]:
    """Carrega notas do vault criadas dentro do período especificado.

    Args:
        vault_path: Caminho do vault Obsidian.
        dias: Quantidade de dias para trás a considerar.

    Returns:
        Lista de dicionários com título e conteúdo das notas.
    """
    vault = Path(vault_path)
    if not vault.exists():
        return []

    data_limite = datetime.now() - timedelta(days=dias)
    notas: list[dict[str, str]] = []

    for arquivo in vault.rglob("*.md"):
        try:
            texto = arquivo.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        titulo = arquivo.stem
        data_nota = None
        conteudo = texto

        # Extrai frontmatter
        if texto.startswith("---"):
            partes = texto.split("---", 2)
            if len(partes) >= 3:
                try:
                    meta = yaml.safe_load(partes[1]) or {}
                    titulo = meta.get("titulo", titulo)
                    data_str = str(meta.get("data", ""))
                    if data_str:
                        try:
                            data_nota = datetime.fromisoformat(data_str)
                        except ValueError:
                            pass
                    conteudo = partes[2].strip()
                except yaml.YAMLError:
                    pass

        # Se não tem data no frontmatter, usa data de modificação do arquivo
        if data_nota is None:
            stat = arquivo.stat()
            data_nota = datetime.fromtimestamp(stat.st_mtime)

        if data_nota >= data_limite:
            notas.append({
                "titulo": titulo,
                "conteudo": conteudo[:500],  # Limita para não estourar prompt
                "data": data_nota.strftime("%d/%m/%Y"),
            })

    return notas


def _periodo_para_dias(periodo: str) -> int:
    """Converte string de período para número de dias.

    Args:
        periodo: String como 'dia', 'semana', 'mes'.

    Returns:
        Número de dias correspondente.
    """
    mapa = {
        "dia": 1,
        "hoje": 1,
        "semana": 7,
        "quinzena": 15,
        "mes": 30,
        "mês": 30,
    }
    return mapa.get(periodo.lower(), 7)


def gerar_resumo(periodo: str, config: AppConfig) -> str:
    """Gera resumo das notas de um período usando a IA.

    Args:
        periodo: Período do resumo ('dia', 'semana', 'mes').
        config: Configuração completa do app.

    Returns:
        Texto do resumo gerado pela IA.
    """
    dias = _periodo_para_dias(periodo)
    notas = _carregar_notas_por_periodo(config.obsidian.vault_path, dias)

    if not notas:
        return f"Nenhuma nota encontrada nos últimos {dias} dia(s)."

    # Monta contexto para a IA
    notas_texto = "\n\n".join(
        f"- **{n['titulo']}** ({n['data']}): {n['conteudo']}"
        for n in notas
    )

    prompt = (
        f"Resuma as seguintes {len(notas)} notas dos últimos {dias} dias da AllpFit. "
        "Organize por categorias (operacional, pessoal, financeiro, etc). "
        "Destaque itens urgentes ou pendentes. "
        "Seja conciso e prático.\n\n"
        f"Notas:\n{notas_texto}"
    )

    try:
        resposta = consultar_ollama(prompt, config.ollama)
        logger.info("Resumo gerado para período: %s (%d notas)", periodo, len(notas))
        return resposta
    except Exception as e:
        logger.error("Erro ao gerar resumo: %s", e)
        return f"Erro ao gerar resumo: {e}"


def gerar_resumo_simples(periodo: str, config: AppConfig) -> str:
    """Gera resumo offline (sem IA) listando notas do período.

    Args:
        periodo: Período do resumo.
        config: Configuração completa do app.

    Returns:
        Lista formatada das notas do período.
    """
    dias = _periodo_para_dias(periodo)
    notas = _carregar_notas_por_periodo(config.obsidian.vault_path, dias)

    if not notas:
        return f"Nenhuma nota encontrada nos últimos {dias} dia(s)."

    linhas = [f"📋 Notas dos últimos {dias} dia(s) ({len(notas)} encontradas):\n"]
    for n in notas:
        linhas.append(f"• **{n['titulo']}** ({n['data']})")
        preview = n["conteudo"][:100].replace("\n", " ")
        linhas.append(f"  {preview}")
        linhas.append("")

    return "\n".join(linhas)
