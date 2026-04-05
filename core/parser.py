"""Parser XML robusto para extrair notas da resposta da IA."""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

from core.logger import configurar_logger

logger = configurar_logger()


@dataclass
class NotaExtraida:
    """Representa uma nota extraída da resposta da IA."""
    titulo: str
    conteudo: str
    tags: list[str] = field(default_factory=list)
    categoria: str = ""
    prioridade: str = "media"


def _extrair_com_xml(resposta: str) -> list[NotaExtraida]:
    """Tenta extrair notas usando parser XML real.

    Args:
        resposta: Texto da resposta da IA.

    Returns:
        Lista de notas extraídas.
    """
    notas: list[NotaExtraida] = []

    # Envolve em root para lidar com múltiplas notas
    xml_wrapped = f"<root>{resposta}</root>"

    try:
        root = ET.fromstring(xml_wrapped)
    except ET.ParseError:
        # Tenta limpar caracteres problemáticos e re-parsear
        xml_limpo = re.sub(r"&(?!amp;|lt;|gt;|apos;|quot;)", "&amp;", xml_wrapped)
        try:
            root = ET.fromstring(xml_limpo)
        except ET.ParseError:
            return []

    # Busca tags <nota> ou diretamente <titulo>/<conteudo>
    for nota_elem in root.iter("nota"):
        titulo_elem = nota_elem.find("titulo")
        conteudo_elem = nota_elem.find("conteudo")
        if titulo_elem is not None and conteudo_elem is not None:
            titulo = (titulo_elem.text or "").strip()
            conteudo = (conteudo_elem.text or "").strip()
            if titulo and conteudo:
                notas.append(NotaExtraida(titulo=titulo, conteudo=conteudo))

    # Se não encontrou <nota>, busca <titulo>/<conteudo> diretos
    if not notas:
        titulos = list(root.iter("titulo"))
        conteudos = list(root.iter("conteudo"))
        for t, c in zip(titulos, conteudos):
            titulo = (t.text or "").strip()
            conteudo = (c.text or "").strip()
            if titulo and conteudo:
                notas.append(NotaExtraida(titulo=titulo, conteudo=conteudo))

    return notas


def _extrair_com_regex(resposta: str) -> list[NotaExtraida]:
    """Fallback: extrai notas usando regex (backup do parser XML).

    Args:
        resposta: Texto da resposta da IA.

    Returns:
        Lista de notas extraídas.
    """
    padrao = r"<titulo>(.*?)</titulo>\s*<conteudo>(.*?)</conteudo>"
    matches = re.findall(padrao, resposta, re.IGNORECASE | re.DOTALL)
    notas: list[NotaExtraida] = []
    for titulo, conteudo in matches:
        titulo = titulo.strip()
        conteudo = conteudo.strip()
        if titulo and conteudo:
            notas.append(NotaExtraida(titulo=titulo, conteudo=conteudo))
    return notas


def extrair_notas(resposta: str) -> list[NotaExtraida]:
    """Extrai notas da resposta da IA usando XML parser com fallback regex.

    Args:
        resposta: Texto completo da resposta da IA.

    Returns:
        Lista de NotaExtraida encontradas.
    """
    if not resposta or not resposta.strip():
        return []

    # Tenta parser XML primeiro
    notas = _extrair_com_xml(resposta)
    if notas:
        logger.debug("Notas extraídas via parser XML: %d", len(notas))
        return notas

    # Fallback para regex
    notas = _extrair_com_regex(resposta)
    if notas:
        logger.debug("Notas extraídas via regex (fallback): %d", len(notas))
    else:
        logger.debug("Nenhuma nota encontrada na resposta")

    return notas


def limpar_resposta(resposta: str, notas: list[NotaExtraida]) -> str:
    """Remove tags XML da resposta e substitui por confirmações.

    Args:
        resposta: Resposta original da IA.
        notas: Notas que foram extraídas e salvas.

    Returns:
        Resposta limpa com confirmações.
    """
    resposta_limpa = resposta

    # Remove blocos <nota>...</nota>
    resposta_limpa = re.sub(
        r"<nota>.*?</nota>",
        "",
        resposta_limpa,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Remove tags soltas de <titulo> e <conteudo>
    resposta_limpa = re.sub(
        r"<titulo>.*?</titulo>\s*<conteudo>.*?</conteudo>",
        "",
        resposta_limpa,
        flags=re.IGNORECASE | re.DOTALL,
    )

    # Adiciona confirmações
    for nota in notas:
        resposta_limpa += f"\n✅ Nota '{nota.titulo}' salva no Obsidian!"

    return resposta_limpa.strip()
