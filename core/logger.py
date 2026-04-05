"""Sistema de logs estruturados em JSON."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """Formata logs como JSON estruturado."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(tz=__import__('datetime').timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "message": record.getMessage(),
        }
        if hasattr(record, "metadata"):
            log_entry["metadata"] = record.metadata
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


def configurar_logger(nome: str = "agente_allpfit", nivel: int = logging.DEBUG) -> logging.Logger:
    """Configura e retorna logger com saída em arquivo JSON e console.

    Args:
        nome: Nome do logger.
        nivel: Nível mínimo de log.

    Returns:
        Logger configurado.
    """
    logger = logging.getLogger(nome)

    if logger.handlers:
        return logger

    logger.setLevel(nivel)

    # Handler para console (formato legível)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_fmt = logging.Formatter("[%(asctime)s] %(levelname)s | %(module)s | %(message)s", datefmt="%H:%M:%S")
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # Handler para arquivo (formato JSON)
    logs_dir = Path(__file__).parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)
    hoje = datetime.now().strftime("%Y-%m-%d")
    arquivo_log = logs_dir / f"agente_{hoje}.log"

    file_handler = logging.FileHandler(arquivo_log, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(JsonFormatter())
    logger.addHandler(file_handler)

    return logger


def log_com_metadata(logger: logging.Logger, nivel: int, mensagem: str, **metadata: object) -> None:
    """Loga mensagem com metadados extras no JSON.

    Args:
        logger: Logger a usar.
        nivel: Nível do log (ex: logging.INFO).
        mensagem: Mensagem de log.
        **metadata: Campos extras para incluir no JSON.
    """
    record = logger.makeRecord(
        logger.name, nivel, "(unknown)", 0, mensagem, (), None
    )
    record.metadata = metadata  # type: ignore[attr-defined]
    logger.handle(record)
