"""Testes do motor de busca."""

from pathlib import Path

from core.busca import buscar_notas, formatar_resultados
from core.config import ObsidianConfig, SubpastasConfig


class TestBuscarNotas:
    def test_busca_por_termo(self, nota_markdown: Path, config_teste):
        resultados = buscar_notas("halteres", config_teste.obsidian)
        assert len(resultados) >= 1
        assert any("Haltere" in r.titulo for r in resultados)

    def test_busca_sem_resultados(self, vault_temporario: Path):
        config = ObsidianConfig(vault_path=str(vault_temporario), subpastas=SubpastasConfig())
        resultados = buscar_notas("xyz_inexistente_abc", config)
        assert len(resultados) == 0

    def test_busca_com_varias_notas(self, varias_notas: list[Path], config_teste):
        resultados = buscar_notas("treino aluno", config_teste.obsidian)
        assert len(resultados) >= 1

    def test_busca_com_filtro_categoria(self, varias_notas: list[Path], config_teste):
        resultados = buscar_notas("categoria:financeiro pagamento", config_teste.obsidian)
        assert all(r.categoria == "financeiro" for r in resultados if r.categoria)

    def test_busca_vault_inexistente(self):
        config = ObsidianConfig(vault_path="/caminho/inexistente", subpastas=SubpastasConfig())
        resultados = buscar_notas("qualquer coisa", config)
        assert len(resultados) == 0

    def test_busca_query_vazia(self, config_teste):
        resultados = buscar_notas("", config_teste.obsidian)
        assert len(resultados) == 0

    def test_max_resultados(self, varias_notas: list[Path], config_teste):
        resultados = buscar_notas("nota", config_teste.obsidian, max_resultados=1)
        assert len(resultados) <= 1


class TestFormatarResultados:
    def test_sem_resultados(self):
        texto = formatar_resultados([])
        assert "Nenhuma nota encontrada" in texto

    def test_com_resultados(self, nota_markdown: Path, config_teste):
        resultados = buscar_notas("halteres", config_teste.obsidian)
        texto = formatar_resultados(resultados)
        assert "Encontrei" in texto
