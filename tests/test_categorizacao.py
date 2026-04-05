"""Testes do módulo de categorização."""

from core.categorizacao import categorizar_nota, categorizar_notas
from core.parser import NotaExtraida


class TestCategorizarNota:
    def test_categoria_operacional(self):
        nota = NotaExtraida(titulo="Repor halteres", conteudo="Comprar 3 halteres de 10kg para a academia")
        resultado = categorizar_nota(nota)
        assert resultado.categoria == "operacional"

    def test_categoria_pessoal(self):
        nota = NotaExtraida(titulo="Treino do João", conteudo="Montar ficha de treino para o aluno João")
        resultado = categorizar_nota(nota)
        assert resultado.categoria == "pessoal"

    def test_categoria_financeiro(self):
        nota = NotaExtraida(titulo="Pagamentos", conteudo="Cobrar mensalidade atrasada via pix")
        resultado = categorizar_nota(nota)
        assert resultado.categoria == "financeiro"

    def test_categoria_marketing(self):
        nota = NotaExtraida(titulo="Redes Sociais", conteudo="Criar post no instagram sobre promoção")
        resultado = categorizar_nota(nota)
        assert resultado.categoria == "marketing"

    def test_categoria_estrategico(self):
        nota = NotaExtraida(titulo="Expansão", conteudo="Plano de expansão e metas para o próximo ano")
        resultado = categorizar_nota(nota)
        assert resultado.categoria == "estrategico"

    def test_prioridade_alta(self):
        nota = NotaExtraida(titulo="Urgente", conteudo="A esteira quebrou e precisa consertar hoje urgente")
        resultado = categorizar_nota(nota)
        assert resultado.prioridade == "alta"

    def test_prioridade_baixa(self):
        nota = NotaExtraida(titulo="Ideia", conteudo="Quando puder, considerar pintar a fachada")
        resultado = categorizar_nota(nota)
        assert resultado.prioridade == "baixa"

    def test_prioridade_media_padrao(self):
        nota = NotaExtraida(titulo="Nota normal", conteudo="Anotar coisas diversas")
        resultado = categorizar_nota(nota)
        assert resultado.prioridade == "media"

    def test_tags_automaticas(self):
        nota = NotaExtraida(titulo="Equipamentos", conteudo="Estoque de haltere e anilha baixo")
        resultado = categorizar_nota(nota)
        assert len(resultado.tags) > 0
        assert any("haltere" in t for t in resultado.tags)

    def test_categorizar_lista(self):
        notas = [
            NotaExtraida(titulo="Treino", conteudo="Ficha do aluno"),
            NotaExtraida(titulo="Custo", conteudo="Pagamento de conta"),
        ]
        resultados = categorizar_notas(notas)
        assert len(resultados) == 2
        assert all(r.categoria for r in resultados)
