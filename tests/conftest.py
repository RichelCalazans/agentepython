"""Fixtures compartilhadas para os testes."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from core.config import AppConfig, ObsidianConfig, OllamaConfig, SegurancaConfig, ServidorConfig, SubpastasConfig


@pytest.fixture
def vault_temporario(tmp_path: Path) -> Path:
    """Cria um vault temporário para testes."""
    notas_dir = tmp_path / "Notas"
    tarefas_dir = tmp_path / "Tarefas"
    ideias_dir = tmp_path / "Ideias"
    notas_dir.mkdir()
    tarefas_dir.mkdir()
    ideias_dir.mkdir()
    return tmp_path


@pytest.fixture
def config_teste(vault_temporario: Path) -> AppConfig:
    """Configuração de teste com vault temporário."""
    return AppConfig(
        ollama=OllamaConfig(
            url="http://127.0.0.1:11434/api/generate",
            model="gemma4:e4b",
            timeout=5,
            max_retries=1,
        ),
        obsidian=ObsidianConfig(
            vault_path=str(vault_temporario),
            subpastas=SubpastasConfig(),
        ),
        servidor=ServidorConfig(porta=5001, host="127.0.0.1"),
        seguranca=SegurancaConfig(token_secreto="test-token", rate_limit_por_minuto=100),
    )


@pytest.fixture
def nota_markdown(vault_temporario: Path) -> Path:
    """Cria uma nota de exemplo no vault."""
    conteudo = (
        "---\n"
        'titulo: "Reposição de Halteres"\n'
        "data: 2025-04-01T10:00:00\n"
        'origem: "terminal"\n'
        'remetente: "richel"\n'
        'tags: ["equipamento", "haltere", "reposicao"]\n'
        'categoria: "operacional"\n'
        'prioridade: "alta"\n'
        "---\n\n"
        "- Repor 3 halteres de 10kg\n"
        "- Verificar estoque de anilhas\n"
        "- Prazo: segunda-feira\n"
    )
    arquivo = vault_temporario / "Notas" / "Reposição de Halteres.md"
    arquivo.write_text(conteudo, encoding="utf-8")
    return arquivo


@pytest.fixture
def varias_notas(vault_temporario: Path) -> list[Path]:
    """Cria várias notas de exemplo no vault."""
    notas = [
        {
            "nome": "Treino do João",
            "categoria": "pessoal",
            "tags": '["aluno", "treino"]',
            "conteudo": "Treino de hipertrofia para o aluno João. Foco em membros superiores.",
        },
        {
            "nome": "Pagamento Março",
            "categoria": "financeiro",
            "tags": '["pagamento", "mensalidade"]',
            "conteudo": "Mensalidade de março paga via PIX. Valor: R$150,00.",
        },
        {
            "nome": "Post Instagram",
            "categoria": "marketing",
            "tags": '["instagram", "post"]',
            "conteudo": "Criar post sobre promoção de verão. Fotos novas dos equipamentos.",
        },
    ]
    arquivos: list[Path] = []
    for nota in notas:
        conteudo = (
            "---\n"
            f'titulo: "{nota["nome"]}"\n'
            "data: 2025-04-03T14:00:00\n"
            f'categoria: "{nota["categoria"]}"\n'
            f'tags: {nota["tags"]}\n'
            'prioridade: "media"\n'
            "---\n\n"
            f'{nota["conteudo"]}\n'
        )
        arquivo = vault_temporario / "Notas" / f"{nota['nome']}.md"
        arquivo.write_text(conteudo, encoding="utf-8")
        arquivos.append(arquivo)
    return arquivos
