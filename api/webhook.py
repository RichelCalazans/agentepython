"""Webhook Flask robusto com rate limiting e autenticação."""

from __future__ import annotations

import re
import time
from collections import defaultdict
from functools import wraps
from typing import Any, Callable

from flask import Blueprint, Response, jsonify, request

from adapters.base import MensageriaAdapter
from api.health import incrementar_stat
from core.busca import buscar_notas, formatar_resultados
from core.categorizacao import categorizar_notas
from core.config import AppConfig
from core.logger import configurar_logger
from core.obsidian import salvar_notas
from core.ollama import OllamaOfflineError, consultar_ollama
from core.parser import extrair_notas, limpar_resposta
from core.resumos import gerar_resumo, gerar_resumo_simples

logger = configurar_logger()

# Rate limiting simples em memória
_request_counts: dict[str, list[float]] = defaultdict(list)


def _sanitizar_input(texto: str) -> str:
    """Remove caracteres potencialmente maliciosos do input.

    Args:
        texto: Texto recebido do usuário.

    Returns:
        Texto sanitizado.
    """
    # Remove caracteres de controle (exceto newline e tab)
    texto = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", texto)
    # Limita tamanho
    return texto[:2000]


def _verificar_rate_limit(ip: str, limite: int) -> bool:
    """Verifica se o IP excedeu o rate limit.

    Args:
        ip: Endereço IP do cliente.
        limite: Máximo de requests por minuto.

    Returns:
        True se dentro do limite, False se excedeu.
    """
    agora = time.time()
    # Remove entries mais velhas que 60s
    _request_counts[ip] = [t for t in _request_counts[ip] if agora - t < 60]
    if len(_request_counts[ip]) >= limite:
        return False
    _request_counts[ip].append(agora)
    return True


def _detectar_comando_busca(texto: str) -> str | None:
    """Detecta se a mensagem é um comando de busca.

    Args:
        texto: Texto da mensagem.

    Returns:
        Query de busca se detectado, None caso contrário.
    """
    padroes = [
        r"^busca(?:r)?\s+(?:sobre\s+)?(.+)$",
        r"^procura(?:r)?\s+(?:sobre\s+)?(.+)$",
        r"^encontra(?:r)?\s+notas?\s+(?:sobre\s+)?(.+)$",
        r"^mostra(?:r)?\s+notas?\s+(?:de\s+|sobre\s+)?(.+)$",
    ]
    texto_lower = texto.strip().lower()
    for padrao in padroes:
        match = re.match(padrao, texto_lower)
        if match:
            return match.group(1).strip()
    return None


def _detectar_comando_resumo(texto: str) -> str | None:
    """Detecta se a mensagem é um pedido de resumo.

    Args:
        texto: Texto da mensagem.

    Returns:
        Período do resumo se detectado, None caso contrário.
    """
    texto_lower = texto.strip().lower()
    padroes = {
        r"resum[oa]\s+d[oa]\s+(dia|semana|mes|mês|hoje|quinzena)": None,
        r"resum[oa]\s+(semanal|diário|mensal)": None,
        r"o\s+que\s+tenho\s+pendente": "semana",
        r"quais?\s+tarefas?\s+pendentes?": "semana",
        r"resumo": "semana",
    }
    for padrao, periodo_fixo in padroes.items():
        match = re.search(padrao, texto_lower)
        if match:
            if periodo_fixo:
                return periodo_fixo
            # Mapeia variações
            periodo = match.group(1) if match.lastindex else "semana"
            mapa = {"semanal": "semana", "diário": "dia", "mensal": "mes"}
            return mapa.get(periodo, periodo)
    return None


def registrar_webhook_routes(config: AppConfig, adapter: MensageriaAdapter) -> Blueprint:
    """Cria e retorna blueprint com rotas do webhook.

    Args:
        config: Configuração do app.
        adapter: Adapter de mensageria a usar.

    Returns:
        Blueprint com as rotas registradas.
    """
    webhook_bp = Blueprint("webhook", __name__)

    @webhook_bp.route("/webhook", methods=["POST"])
    def receber_mensagem():
        # Rate limiting
        ip = request.remote_addr or "unknown"
        if not _verificar_rate_limit(ip, config.seguranca.rate_limit_por_minuto):
            logger.warning("Rate limit excedido para IP: %s", ip)
            return jsonify({"status": "erro", "mensagem": "Muitas requisições. Aguarde um minuto."}), 429

        # Token de autenticação (opcional via header)
        token = request.headers.get("X-Auth-Token", "")
        if config.seguranca.token_secreto and token and token != config.seguranca.token_secreto:
            return jsonify({"status": "erro", "mensagem": "Token inválido"}), 401

        # Recebe e normaliza mensagem
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"status": "erro", "mensagem": "JSON inválido"}), 400

        msg = adapter.receber_mensagem(dados)
        msg.texto = _sanitizar_input(msg.texto)

        if not msg.texto.strip():
            return jsonify({"status": "erro", "mensagem": "Mensagem vazia"}), 400

        logger.info("[%s] Mensagem de %s: %s", msg.origem, msg.remetente, msg.texto[:100])

        # Detecta comandos de busca
        query_busca = _detectar_comando_busca(msg.texto)
        if query_busca:
            incrementar_stat("buscas_realizadas")
            resultados = buscar_notas(query_busca, config.obsidian)
            resposta_texto = formatar_resultados(resultados)
            resposta_formatada = adapter.formatar_resposta(resposta_texto)
            return jsonify({"status": "sucesso", "resposta": resposta_formatada})

        # Detecta comandos de resumo
        periodo_resumo = _detectar_comando_resumo(msg.texto)
        if periodo_resumo:
            incrementar_stat("resumos_gerados")
            try:
                resposta_texto = gerar_resumo(periodo_resumo, config)
            except Exception:
                resposta_texto = gerar_resumo_simples(periodo_resumo, config)
            resposta_formatada = adapter.formatar_resposta(resposta_texto)
            return jsonify({"status": "sucesso", "resposta": resposta_formatada})

        # Fluxo normal: consulta IA
        try:
            resposta_ia = consultar_ollama(msg.texto, config.ollama)
        except OllamaOfflineError as e:
            logger.error("Ollama offline: %s", e)
            incrementar_stat("erros")
            return jsonify({
                "status": "erro",
                "mensagem": "O cérebro da IA está offline no momento. Tente novamente em alguns minutos.",
            }), 503

        # Extrai e salva notas
        notas = extrair_notas(resposta_ia)
        if notas:
            notas = categorizar_notas(notas)
            caminhos = salvar_notas(notas, config.obsidian, msg.origem, msg.remetente)
            incrementar_stat("notas_criadas")
            logger.info("%d nota(s) salva(s): %s", len(caminhos), caminhos)

        resposta_limpa = limpar_resposta(resposta_ia, notas)
        resposta_formatada = adapter.formatar_resposta(resposta_limpa)

        # Envia resposta via adapter (para WhatsApp envia de volta)
        adapter.enviar_resposta(msg.remetente, resposta_formatada)

        return jsonify({"status": "sucesso", "resposta": resposta_formatada})

    return webhook_bp
