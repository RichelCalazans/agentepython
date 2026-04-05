"""Adapter genérico para WhatsApp (preparado para Evolution API, WPPConnect, etc)."""

from __future__ import annotations

import re

import requests

from core.logger import configurar_logger

from adapters.base import MensagemRecebida, MensageriaAdapter, RespostaEnviada

logger = configurar_logger()

MAX_WHATSAPP_MSG = 4096


class AdapterWhatsApp(MensageriaAdapter):
    """Adapter para WhatsApp via Evolution API ou similar.

    Args:
        api_url: URL base da API do WhatsApp (ex: http://localhost:8080).
        api_key: Chave de autenticação da API.
        instance: Nome da instância na Evolution API.
    """

    def __init__(self, api_url: str = "", api_key: str = "", instance: str = "allpfit") -> None:
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.instance = instance

    def receber_mensagem(self, dados_brutos: dict) -> MensagemRecebida:
        """Normaliza payload do WhatsApp para MensagemRecebida.

        Suporta formatos da Evolution API e payload genérico.

        Args:
            dados_brutos: JSON do webhook do WhatsApp.

        Returns:
            Mensagem normalizada.
        """
        # Tenta formato Evolution API
        data = dados_brutos.get("data", {})
        if data:
            message = data.get("message", {})
            texto = message.get("conversation", "") or message.get("extendedTextMessage", {}).get("text", "")
            remetente = data.get("key", {}).get("remoteJid", "desconhecido")
        else:
            # Formato genérico/simplificado
            texto = dados_brutos.get("text", "") or dados_brutos.get("message", "")
            remetente = dados_brutos.get("sender", "") or dados_brutos.get("from", "desconhecido")

        return MensagemRecebida(
            texto=texto,
            remetente=remetente,
            origem="whatsapp",
            dados_brutos=dados_brutos,
        )

    def enviar_resposta(self, remetente: str, mensagem: str) -> RespostaEnviada:
        """Envia resposta via API do WhatsApp.

        Args:
            remetente: Número/JID do destinatário.
            mensagem: Texto da resposta.

        Returns:
            Resultado do envio.
        """
        if not self.api_url:
            logger.warning("API do WhatsApp não configurada, resposta não enviada")
            return RespostaEnviada(sucesso=False, mensagem="API não configurada")

        mensagem_formatada = self.formatar_resposta(mensagem)
        partes = self._quebrar_mensagem(mensagem_formatada)

        for parte in partes:
            try:
                url = f"{self.api_url}/message/sendText/{self.instance}"
                payload = {
                    "number": remetente,
                    "text": parte,
                }
                headers = {"apikey": self.api_key, "Content-Type": "application/json"}
                resp = requests.post(url, json=payload, headers=headers, timeout=10)

                if resp.status_code not in (200, 201):
                    logger.error("Erro ao enviar WhatsApp: %d", resp.status_code)
                    return RespostaEnviada(sucesso=False, mensagem=f"Erro HTTP {resp.status_code}")
            except requests.RequestException as e:
                logger.error("Falha na conexão com API WhatsApp: %s", e)
                return RespostaEnviada(sucesso=False, mensagem=str(e))

        return RespostaEnviada(sucesso=True, mensagem="Enviado com sucesso")

    def formatar_resposta(self, texto: str) -> str:
        """Converte Markdown genérico para formato WhatsApp.

        Args:
            texto: Texto com Markdown padrão.

        Returns:
            Texto com formatação WhatsApp (*negrito*, _itálico_, ~tachado~).
        """
        # **negrito** → *negrito* (WhatsApp)
        resultado = re.sub(r"\*\*(.+?)\*\*", r"*\1*", texto)
        # Headers ## → *negrito*
        resultado = re.sub(r"^#{1,6}\s+(.+)$", r"*\1*", resultado, flags=re.MULTILINE)
        return resultado

    def _quebrar_mensagem(self, texto: str) -> list[str]:
        """Quebra mensagem longa em partes de até MAX_WHATSAPP_MSG chars.

        Args:
            texto: Texto potencialmente longo.

        Returns:
            Lista de partes da mensagem.
        """
        if len(texto) <= MAX_WHATSAPP_MSG:
            return [texto]

        partes: list[str] = []
        while texto:
            if len(texto) <= MAX_WHATSAPP_MSG:
                partes.append(texto)
                break

            # Tenta quebrar em parágrafo
            pos = texto.rfind("\n\n", 0, MAX_WHATSAPP_MSG)
            if pos == -1:
                pos = texto.rfind("\n", 0, MAX_WHATSAPP_MSG)
            if pos == -1:
                pos = texto.rfind(" ", 0, MAX_WHATSAPP_MSG)
            if pos == -1:
                pos = MAX_WHATSAPP_MSG

            partes.append(texto[:pos].strip())
            texto = texto[pos:].strip()

        return partes
