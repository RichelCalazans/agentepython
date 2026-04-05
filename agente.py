"""Agente AllpFit — Ponto de entrada principal.

Assistente de IA pessoal para gestão da AllpFit Maceió.
Integra Ollama (IA local) com Obsidian (notas) via Flask.
"""

from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask

from adapters.terminal import AdapterTerminal
from adapters.whatsapp import AdapterWhatsApp
from api.health import registrar_health_routes
from api.webhook import registrar_webhook_routes
from core.config import carregar_config
from core.logger import configurar_logger


def criar_app(config_path: str | None = None) -> Flask:
    """Cria e configura a aplicação Flask.

    Args:
        config_path: Caminho para config.yaml. Se None, usa o padrão.

    Returns:
        Aplicação Flask configurada.
    """
    config = carregar_config(config_path)
    logger = configurar_logger()

    app = Flask(__name__)

    # Seleciona adapter (terminal por padrão, WhatsApp se configurado)
    adapter = AdapterTerminal()

    # Registra blueprints
    health_bp = registrar_health_routes(config)
    webhook_bp = registrar_webhook_routes(config, adapter)
    app.register_blueprint(health_bp)
    app.register_blueprint(webhook_bp)

    logger.info(
        "Agente AllpFit iniciado | Modelo: %s | Vault: %s | Porta: %d",
        config.ollama.model,
        config.obsidian.vault_path,
        config.servidor.porta,
    )

    # Guarda config no app para acesso se necessário
    app.config["ALLPFIT"] = config

    return app


def main() -> None:
    """Inicia o servidor do Agente AllpFit."""
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    config = carregar_config(config_path)

    print(
        f"\n{'='*50}\n"
        f"  AGENTE ALLPFIT - Assistente da Academia\n"
        f"  Modelo: {config.ollama.model}\n"
        f"  Servidor: http://{config.servidor.host}:{config.servidor.porta}\n"
        f"  Vault: {config.obsidian.vault_path}\n"
        f"{'='*50}\n"
    )

    app = criar_app(config_path)
    app.run(
        host=config.servidor.host,
        port=config.servidor.porta,
        debug=True,
    )


if __name__ == "__main__":
    main()
