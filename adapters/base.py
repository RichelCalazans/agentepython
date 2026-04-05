"""Interface base para adapters de mensageria."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class MensagemRecebida:
    """Mensagem normalizada recebida de qualquer canal."""
    texto: str
    remetente: str
    origem: str  # "terminal", "whatsapp", etc.
    dados_brutos: dict | None = None


@dataclass
class RespostaEnviada:
    """Resultado do envio de uma resposta."""
    sucesso: bool
    mensagem: str


class MensageriaAdapter(ABC):
    """Interface abstrata para adapters de mensageria."""

    @abstractmethod
    def receber_mensagem(self, dados_brutos: dict) -> MensagemRecebida:
        """Normaliza dados brutos em MensagemRecebida.

        Args:
            dados_brutos: Dados do request HTTP.

        Returns:
            Mensagem normalizada.
        """

    @abstractmethod
    def enviar_resposta(self, remetente: str, mensagem: str) -> RespostaEnviada:
        """Envia resposta ao remetente.

        Args:
            remetente: Identificador do destinatário.
            mensagem: Texto da resposta.

        Returns:
            Resultado do envio.
        """

    @abstractmethod
    def formatar_resposta(self, texto: str) -> str:
        """Formata texto para o canal de destino.

        Args:
            texto: Texto em formato genérico.

        Returns:
            Texto formatado para o canal.
        """
