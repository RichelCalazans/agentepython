"""Adapter para uso via terminal/curl."""

from __future__ import annotations

from core.logger import configurar_logger

from adapters.base import MensagemRecebida, MensageriaAdapter, RespostaEnviada

logger = configurar_logger()


class AdapterTerminal(MensageriaAdapter):
    """Adapter para receber mensagens via curl/terminal."""

    def receber_mensagem(self, dados_brutos: dict) -> MensagemRecebida:
        """Normaliza payload de curl para MensagemRecebida.

        Args:
            dados_brutos: JSON do POST request.

        Returns:
            Mensagem normalizada.
        """
        return MensagemRecebida(
            texto=dados_brutos.get("text", ""),
            remetente=dados_brutos.get("sender", "terminal"),
            origem="terminal",
            dados_brutos=dados_brutos,
        )

    def enviar_resposta(self, remetente: str, mensagem: str) -> RespostaEnviada:
        """No terminal, a resposta vai no body do HTTP response.

        Args:
            remetente: Identificador do destinatário.
            mensagem: Texto da resposta.

        Returns:
            Sempre sucesso (a resposta vai no JSON de retorno).
        """
        logger.info("Resposta para %s: %s", remetente, mensagem[:100])
        return RespostaEnviada(sucesso=True, mensagem=mensagem)

    def formatar_resposta(self, texto: str) -> str:
        """Terminal não precisa de formatação especial.

        Args:
            texto: Texto a formatar.

        Returns:
            Texto sem alterações.
        """
        return texto
