"""Testes do parser XML."""

from core.parser import NotaExtraida, extrair_notas, limpar_resposta


class TestExtrairNotas:
    def test_nota_com_tags_completas(self):
        resposta = (
            "Aqui está sua nota:\n"
            "<nota>\n"
            "<titulo>Reposição de Equipamentos</titulo>\n"
            "<conteudo>- Repor 3 halteres de 10kg\n- Verificar estoque</conteudo>\n"
            "</nota>"
        )
        notas = extrair_notas(resposta)
        assert len(notas) == 1
        assert notas[0].titulo == "Reposição de Equipamentos"
        assert "halteres" in notas[0].conteudo

    def test_multiplas_notas(self):
        resposta = (
            "<nota><titulo>Nota 1</titulo><conteudo>Conteúdo 1</conteudo></nota>\n"
            "<nota><titulo>Nota 2</titulo><conteudo>Conteúdo 2</conteudo></nota>"
        )
        notas = extrair_notas(resposta)
        assert len(notas) == 2
        assert notas[0].titulo == "Nota 1"
        assert notas[1].titulo == "Nota 2"

    def test_tags_sem_nota_wrapper(self):
        resposta = "<titulo>Teste</titulo><conteudo>Conteúdo teste</conteudo>"
        notas = extrair_notas(resposta)
        assert len(notas) == 1
        assert notas[0].titulo == "Teste"

    def test_resposta_sem_notas(self):
        resposta = "Olá! Tudo bem? Como posso ajudar?"
        notas = extrair_notas(resposta)
        assert len(notas) == 0

    def test_resposta_vazia(self):
        assert extrair_notas("") == []
        assert extrair_notas("   ") == []

    def test_xml_malformado_fallback_regex(self):
        resposta = "<titulo>Teste Regex</titulo> <conteudo>Fallback funciona</conteudo>"
        notas = extrair_notas(resposta)
        assert len(notas) == 1
        assert notas[0].titulo == "Teste Regex"

    def test_titulo_com_acentos(self):
        resposta = "<nota><titulo>Manutenção Elétrica</titulo><conteudo>Verificar fiação</conteudo></nota>"
        notas = extrair_notas(resposta)
        assert len(notas) == 1
        assert notas[0].titulo == "Manutenção Elétrica"

    def test_conteudo_multilinhas(self):
        resposta = (
            "<nota><titulo>Lista</titulo><conteudo>\n"
            "- Item 1\n"
            "- Item 2\n"
            "- Item 3\n"
            "</conteudo></nota>"
        )
        notas = extrair_notas(resposta)
        assert len(notas) == 1
        assert "Item 1" in notas[0].conteudo


class TestLimparResposta:
    def test_remove_tags_e_adiciona_confirmacao(self):
        notas = [NotaExtraida(titulo="Teste", conteudo="Conteúdo")]
        resposta = "Pronto! <nota><titulo>Teste</titulo><conteudo>Conteúdo</conteudo></nota>"
        limpa = limpar_resposta(resposta, notas)
        assert "<nota>" not in limpa
        assert "Nota 'Teste' salva no Obsidian!" in limpa

    def test_sem_notas_mantem_resposta(self):
        resposta = "Olá, tudo bem?"
        limpa = limpar_resposta(resposta, [])
        assert limpa == "Olá, tudo bem?"
