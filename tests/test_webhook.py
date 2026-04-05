"""Testes do webhook e endpoints."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from adapters.terminal import AdapterTerminal
from agente import criar_app


@pytest.fixture
def client(config_teste, tmp_path):
    """Cria um cliente de teste Flask."""
    # Escreve um config.yaml temporário
    import yaml
    config_path = tmp_path / "config.yaml"
    config_dict = {
        "ollama": {
            "url": config_teste.ollama.url,
            "model": config_teste.ollama.model,
            "timeout": config_teste.ollama.timeout,
            "max_retries": config_teste.ollama.max_retries,
        },
        "obsidian": {
            "vault_path": config_teste.obsidian.vault_path,
            "subpastas": {
                "notas": "Notas",
                "tarefas": "Tarefas",
                "ideias": "Ideias",
            },
        },
        "servidor": {
            "porta": config_teste.servidor.porta,
            "host": config_teste.servidor.host,
        },
        "seguranca": {
            "token_secreto": config_teste.seguranca.token_secreto,
            "rate_limit_por_minuto": 100,
        },
    }
    config_path.write_text(yaml.dump(config_dict), encoding="utf-8")

    app = criar_app(str(config_path))
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthCheck:
    def test_health_retorna_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_stats_retorna_contadores(self, client):
        resp = client.get("/stats")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "notas_criadas" in data
        assert "uptime_segundos" in data


class TestWebhook:
    def test_json_invalido(self, client):
        resp = client.post("/webhook", data="not json", content_type="text/plain")
        assert resp.status_code == 400

    def test_mensagem_vazia(self, client):
        resp = client.post("/webhook", json={"text": "", "sender": "teste"})
        assert resp.status_code == 400

    @patch("api.webhook.consultar_ollama")
    def test_mensagem_simples(self, mock_ollama, client):
        mock_ollama.return_value = "Olá! Tudo bem sim."
        resp = client.post("/webhook", json={"text": "Oi, tudo bem?", "sender": "teste"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "sucesso"

    @patch("api.webhook.consultar_ollama")
    def test_mensagem_com_nota(self, mock_ollama, client):
        mock_ollama.return_value = (
            "Pronto, salvei sua nota!\n"
            "<nota><titulo>Halteres</titulo>"
            "<conteudo>Repor 3 halteres de 10kg</conteudo></nota>"
        )
        resp = client.post("/webhook", json={"text": "Salva: repor halteres", "sender": "richel"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "sucesso"
        assert "Halteres" in data["resposta"]

    def test_busca_por_mensagem(self, client, nota_markdown):
        resp = client.post("/webhook", json={"text": "busca sobre halteres", "sender": "teste"})
        assert resp.status_code == 200

    def test_resumo_por_mensagem(self, client):
        resp = client.post("/webhook", json={"text": "resumo da semana", "sender": "teste"})
        assert resp.status_code == 200


class TestAdapterWhatsApp:
    def test_payload_evolution_api(self):
        from adapters.whatsapp import AdapterWhatsApp
        adapter = AdapterWhatsApp()
        dados = {
            "data": {
                "key": {"remoteJid": "5582999999999@s.whatsapp.net"},
                "message": {"conversation": "Oi, salva isso!"},
            }
        }
        msg = adapter.receber_mensagem(dados)
        assert msg.texto == "Oi, salva isso!"
        assert "5582" in msg.remetente
        assert msg.origem == "whatsapp"

    def test_formatacao_markdown_whatsapp(self):
        from adapters.whatsapp import AdapterWhatsApp
        adapter = AdapterWhatsApp()
        texto = "**Título** e mais texto"
        formatado = adapter.formatar_resposta(texto)
        assert formatado == "*Título* e mais texto"

    def test_quebra_mensagem_longa(self):
        from adapters.whatsapp import AdapterWhatsApp
        adapter = AdapterWhatsApp()
        texto = "A" * 5000
        partes = adapter._quebrar_mensagem(texto)
        assert len(partes) >= 2
        assert all(len(p) <= 4096 for p in partes)
