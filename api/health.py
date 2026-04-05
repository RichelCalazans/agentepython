"""Endpoints de health check e estatísticas."""

from __future__ import annotations

import os
import time
from pathlib import Path

import requests
from flask import Blueprint, jsonify

from core.config import AppConfig

# Contadores globais (simples, sem persistência)
_stats = {
    "notas_criadas": 0,
    "buscas_realizadas": 0,
    "resumos_gerados": 0,
    "erros": 0,
    "inicio": time.time(),
}


def incrementar_stat(chave: str) -> None:
    """Incrementa um contador de estatísticas.

    Args:
        chave: Nome do contador a incrementar.
    """
    if chave in _stats:
        _stats[chave] += 1


def registrar_health_routes(app_config: AppConfig) -> Blueprint:
    """Cria e retorna blueprint com rotas de health check.

    Args:
        app_config: Configuração do app para verificar dependências.

    Returns:
        Blueprint com as rotas registradas.
    """
    bp = Blueprint("health", __name__)

    @bp.route("/health", methods=["GET"])
    def health_check():
        uptime = int(time.time() - _stats["inicio"])
        horas = uptime // 3600
        minutos = (uptime % 3600) // 60
        segundos = uptime % 60

        # Verifica Ollama
        ollama_status = "offline"
        try:
            resp = requests.get(
                app_config.ollama.url.replace("/api/generate", "/api/tags"),
                timeout=3,
            )
            if resp.status_code == 200:
                ollama_status = "connected"
        except requests.RequestException:
            pass

        # Verifica Obsidian vault
        vault_path = Path(app_config.obsidian.vault_path)
        obsidian_status = "writable" if vault_path.exists() and os.access(vault_path, os.W_OK) else "inaccessible"

        return jsonify({
            "status": "ok",
            "ollama": ollama_status,
            "obsidian": obsidian_status,
            "uptime": f"{horas}h {minutos}m {segundos}s",
        })

    @bp.route("/stats", methods=["GET"])
    def stats():
        uptime = int(time.time() - _stats["inicio"])
        return jsonify({
            "notas_criadas": _stats["notas_criadas"],
            "buscas_realizadas": _stats["buscas_realizadas"],
            "resumos_gerados": _stats["resumos_gerados"],
            "erros": _stats["erros"],
            "uptime_segundos": uptime,
        })

    return bp
