"""Salvamento de notas no Obsidian com frontmatter YAML."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from core.config import ObsidianConfig
from core.logger import configurar_logger
from core.parser import NotaExtraida

logger = configurar_logger()


def _limpar_titulo(titulo: str) -> str:
    """Remove caracteres inválidos para nome de arquivo.

    Args:
        titulo: Título original da nota.

    Returns:
        Título sanitizado para uso como nome de arquivo.
    """
    return "".join(c for c in titulo if c.isalnum() or c in " _-").strip()


def _gerar_frontmatter(
    nota: NotaExtraida,
    origem: str = "terminal",
    remetente: str = "richel",
) -> str:
    """Gera frontmatter YAML para a nota.

    Args:
        nota: Nota com dados extraídos.
        origem: Canal de origem da mensagem.
        remetente: Quem enviou a mensagem.

    Returns:
        String com frontmatter YAML formatado.
    """
    agora = datetime.now().isoformat(timespec="seconds")
    tags_str = ", ".join(f'"{t}"' for t in nota.tags) if nota.tags else ""
    tags_line = f"tags: [{tags_str}]" if tags_str else "tags: []"

    frontmatter = (
        "---\n"
        f'titulo: "{nota.titulo}"\n'
        f"data: {agora}\n"
        f'origem: "{origem}"\n'
        f'remetente: "{remetente}"\n'
        f"{tags_line}\n"
        f'categoria: "{nota.categoria}"\n'
        f'prioridade: "{nota.prioridade}"\n'
        "---\n\n"
    )
    return frontmatter


def _determinar_subpasta(nota: NotaExtraida, config: ObsidianConfig) -> str:
    """Determina a subpasta com base na categoria da nota.

    Args:
        nota: Nota a categorizar.
        config: Configuração do Obsidian.

    Returns:
        Nome da subpasta.
    """
    mapa = {
        "operacional": config.subpastas.notas,
        "pessoal": config.subpastas.notas,
        "financeiro": config.subpastas.notas,
        "marketing": config.subpastas.notas,
        "estrategico": config.subpastas.ideias,
        "tarefa": config.subpastas.tarefas,
    }
    return mapa.get(nota.categoria, config.subpastas.notas)


def salvar_nota(
    nota: NotaExtraida,
    config: ObsidianConfig,
    origem: str = "terminal",
    remetente: str = "richel",
) -> str:
    """Salva uma nota como arquivo .md no vault do Obsidian com frontmatter.

    Args:
        nota: Nota extraída a salvar.
        config: Configuração do Obsidian (caminho do vault, subpastas).
        origem: Canal de origem (terminal, whatsapp, etc.).
        remetente: Nome do remetente.

    Returns:
        Caminho completo do arquivo criado.

    Raises:
        OSError: Se não conseguir criar o diretório ou escrever o arquivo.
    """
    subpasta = _determinar_subpasta(nota, config)
    diretorio = Path(config.vault_path) / subpasta
    diretorio.mkdir(parents=True, exist_ok=True)

    titulo_limpo = _limpar_titulo(nota.titulo)
    if not titulo_limpo:
        titulo_limpo = f"nota_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    caminho = diretorio / f"{titulo_limpo}.md"

    frontmatter = _gerar_frontmatter(nota, origem, remetente)
    conteudo_completo = frontmatter + nota.conteudo

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo_completo)

    logger.info("Nota salva: %s", caminho)
    return str(caminho)


def salvar_notas(
    notas: list[NotaExtraida],
    config: ObsidianConfig,
    origem: str = "terminal",
    remetente: str = "richel",
) -> list[str]:
    """Salva múltiplas notas no vault do Obsidian.

    Args:
        notas: Lista de notas a salvar.
        config: Configuração do Obsidian.
        origem: Canal de origem.
        remetente: Nome do remetente.

    Returns:
        Lista de caminhos dos arquivos criados.
    """
    caminhos: list[str] = []
    for nota in notas:
        try:
            caminho = salvar_nota(nota, config, origem, remetente)
            caminhos.append(caminho)
        except OSError as e:
            logger.error("Erro ao salvar nota '%s': %s", nota.titulo, e)
    return caminhos
