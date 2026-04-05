"""Cliente Ollama com retry, backoff exponencial e tratamento de erros."""

from __future__ import annotations

import logging
import time

import requests

from core.config import OllamaConfig
from core.logger import configurar_logger, log_com_metadata

logger = configurar_logger()

PROMPT_SISTEMA = (
    "Você é o assistente pessoal do Richel na AllpFit Maceió.\n\n"
    "## REGRAS PARA SALVAR NOTAS\n"
    "SEMPRE que o usuário pedir para 'salvar', 'anotar', 'criar nota', 'lembrar', ou 'registrar', "
    "você DEVE OBRIGATORIAMENTE formatar usando tags XML:\n\n"
    "<nota>\n"
    "<titulo>Título Descritivo</titulo>\n"
    "<conteudo>Conteúdo detalhado com bullet points.</conteudo>\n"
    "</nota>\n\n"
    "## REGRAS PARA CLASSIFICAÇÃO\n"
    "Ao criar uma nota, classifique mentalmente:\n"
    "- Categoria: operacional, pessoal, financeiro, marketing, estrategico\n"
    "- Prioridade: alta (urgente/prazo curto), media (importante), baixa (quando puder)\n"
    "- Tags: palavras-chave relevantes separadas por vírgula\n\n"
    "## REGRAS PARA BUSCAS\n"
    "Se o usuário pedir para 'buscar', 'procurar', 'encontrar notas', responda:\n"
    '<busca query="termo de busca" />\n\n'
    "## REGRAS PARA RESUMOS\n"
    "Se o usuário pedir 'resumo', 'resumir', 'o que tenho pendente', responda:\n"
    '<resumo periodo="semana" />\n\n'
    "Se não for um pedido especial, apenas responda normalmente de forma útil e amigável.\n\n"
    "Mensagem do usuário: {mensagem}"
)


class OllamaOfflineError(Exception):
    """Ollama não está acessível."""


def consultar_ollama(mensagem: str, config: OllamaConfig) -> str:
    """Envia mensagem ao Ollama e retorna a resposta.

    Implementa retry com backoff exponencial em caso de falhas transitórias.

    Args:
        mensagem: Mensagem do usuário.
        config: Configuração de conexão com Ollama.

    Returns:
        Texto da resposta da IA.

    Raises:
        OllamaOfflineError: Se o Ollama não responder após todas as tentativas.
    """
    prompt = PROMPT_SISTEMA.format(mensagem=mensagem)
    payload = {
        "model": config.model,
        "prompt": prompt,
        "stream": False,
    }

    ultimo_erro: Exception | None = None

    for tentativa in range(1, config.max_retries + 1):
        try:
            log_com_metadata(
                logger, logging.DEBUG, "Enviando para Ollama",
                tentativa=tentativa, modelo=config.model,
            )

            resposta = requests.post(
                config.url,
                json=payload,
                timeout=config.timeout,
            )

            if resposta.status_code == 200:
                dados = resposta.json()
                texto = dados.get("response", "")
                if not texto:
                    logger.warning("Ollama retornou resposta vazia")
                    return "Desculpe, não consegui processar sua mensagem. Tente novamente."
                return texto

            logger.warning(
                "Ollama retornou status %d (tentativa %d/%d)",
                resposta.status_code, tentativa, config.max_retries,
            )
            ultimo_erro = Exception(f"Status HTTP {resposta.status_code}")

        except requests.exceptions.Timeout:
            logger.warning(
                "Timeout na comunicação com Ollama (tentativa %d/%d)",
                tentativa, config.max_retries,
            )
            ultimo_erro = requests.exceptions.Timeout("Ollama timeout")

        except requests.exceptions.ConnectionError as e:
            logger.warning(
                "Ollama não acessível (tentativa %d/%d): %s",
                tentativa, config.max_retries, e,
            )
            ultimo_erro = e

        except requests.exceptions.JSONDecodeError as e:
            logger.error("Resposta inválida do Ollama: %s", e)
            ultimo_erro = e

        # Backoff exponencial: 2s, 4s, 8s...
        if tentativa < config.max_retries:
            espera = 2 ** tentativa
            logger.info("Aguardando %ds antes de tentar novamente...", espera)
            time.sleep(espera)

    raise OllamaOfflineError(
        f"Ollama não respondeu após {config.max_retries} tentativas. "
        f"Último erro: {ultimo_erro}"
    )
