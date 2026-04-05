"""Categorização automática de notas por conteúdo."""

from __future__ import annotations

import re

from core.parser import NotaExtraida


# Palavras-chave por categoria
CATEGORIAS: dict[str, list[str]] = {
    "operacional": [
        "equipamento", "haltere", "anilha", "esteira", "manutenção", "repor",
        "reposição", "limpeza", "estoque", "material", "máquina", "aparelho",
        "conserto", "reforma", "trocar", "comprar", "fornecedor",
    ],
    "pessoal": [
        "aluno", "aluna", "treino", "avaliação", "ficha", "medida",
        "anamnese", "prescrição", "exercício", "aula", "horário",
        "matrícula", "frequência", "resultado",
    ],
    "financeiro": [
        "pagamento", "mensalidade", "custo", "receita", "despesa",
        "fatura", "boleto", "pix", "dinheiro", "preço", "desconto",
        "investimento", "lucro", "caixa", "salário",
    ],
    "marketing": [
        "instagram", "post", "redes sociais", "promoção", "campanha",
        "divulgação", "foto", "vídeo", "story", "marketing", "evento",
        "parceria", "publicidade", "anúncio",
    ],
    "estrategico": [
        "meta", "plano", "expansão", "objetivo", "estratégia",
        "crescimento", "futuro", "longo prazo", "projeto", "visão",
        "ideia", "inovação", "melhoria",
    ],
}

# Palavras-chave para prioridade
PRIORIDADE_ALTA: list[str] = [
    "urgente", "urgência", "hoje", "agora", "imediato", "até amanhã",
    "prazo", "crítico", "importante", "quebrou", "estragou", "parou",
    "emergência", "rápido", "já",
]

PRIORIDADE_BAIXA: list[str] = [
    "quando puder", "sem pressa", "eventualmente", "talvez",
    "considerar", "pensar sobre", "futuro", "algum dia",
]


def categorizar_nota(nota: NotaExtraida) -> NotaExtraida:
    """Categoriza uma nota automaticamente baseado no conteúdo.

    Analisa título e conteúdo para determinar categoria, prioridade e tags.
    Modifica a nota in-place e a retorna.

    Args:
        nota: Nota a ser categorizada.

    Returns:
        A mesma nota com categoria, prioridade e tags preenchidos.
    """
    texto = f"{nota.titulo} {nota.conteudo}".lower()

    # Detectar categoria
    melhor_categoria = ""
    melhor_score = 0
    for categoria, palavras in CATEGORIAS.items():
        score = sum(1 for p in palavras if p in texto)
        if score > melhor_score:
            melhor_score = score
            melhor_categoria = categoria

    nota.categoria = melhor_categoria or "operacional"

    # Detectar prioridade
    if any(p in texto for p in PRIORIDADE_ALTA):
        nota.prioridade = "alta"
    elif any(p in texto for p in PRIORIDADE_BAIXA):
        nota.prioridade = "baixa"
    else:
        nota.prioridade = "media"

    # Detectar tags automaticamente
    tags: set[str] = set()
    for categoria, palavras in CATEGORIAS.items():
        for palavra in palavras:
            if palavra in texto:
                tags.add(palavra)
    # Limita a 5 tags mais relevantes
    nota.tags = sorted(tags)[:5]

    return nota


def categorizar_notas(notas: list[NotaExtraida]) -> list[NotaExtraida]:
    """Categoriza uma lista de notas.

    Args:
        notas: Lista de notas a categorizar.

    Returns:
        Lista de notas categorizadas.
    """
    return [categorizar_nota(nota) for nota in notas]
