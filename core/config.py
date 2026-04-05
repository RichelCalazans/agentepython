"""Carregamento e validação de configuração a partir de config.yaml."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class OllamaConfig:
    url: str = "http://127.0.0.1:11434/api/generate"
    model: str = "gemma4:e4b"
    timeout: int = 60
    max_retries: int = 3


@dataclass
class SubpastasConfig:
    notas: str = "Notas"
    tarefas: str = "Tarefas"
    ideias: str = "Ideias"


@dataclass
class ObsidianConfig:
    vault_path: str = ""
    subpastas: SubpastasConfig = field(default_factory=SubpastasConfig)


@dataclass
class ServidorConfig:
    porta: int = 5000
    host: str = "127.0.0.1"


@dataclass
class SegurancaConfig:
    token_secreto: str = "allpfit-secret-2025"
    rate_limit_por_minuto: int = 30


@dataclass
class AppConfig:
    ollama: OllamaConfig = field(default_factory=OllamaConfig)
    obsidian: ObsidianConfig = field(default_factory=ObsidianConfig)
    servidor: ServidorConfig = field(default_factory=ServidorConfig)
    seguranca: SegurancaConfig = field(default_factory=SegurancaConfig)


def _dict_to_dataclass(cls: type, data: dict[str, Any]) -> Any:
    """Converte um dicionário em dataclass, recursivamente."""
    if not isinstance(data, dict):
        return data
    field_types = {f.name: f.type for f in cls.__dataclass_fields__.values()}
    kwargs: dict[str, Any] = {}
    for key, value in data.items():
        if key in field_types:
            field_type = field_types[key]
            # Resolve string type annotations
            if isinstance(field_type, str):
                field_type = eval(field_type)
            if hasattr(field_type, "__dataclass_fields__") and isinstance(value, dict):
                kwargs[key] = _dict_to_dataclass(field_type, value)
            else:
                kwargs[key] = value
    return cls(**kwargs)


def carregar_config(caminho: str | Path | None = None) -> AppConfig:
    """Carrega configuração do arquivo YAML.

    Args:
        caminho: Caminho para o config.yaml. Se None, busca no diretório do projeto.

    Returns:
        AppConfig com todas as configurações carregadas.
    """
    if caminho is None:
        caminho = Path(__file__).parent.parent / "config.yaml"
    else:
        caminho = Path(caminho)

    if not caminho.exists():
        return AppConfig()

    with open(caminho, "r", encoding="utf-8") as f:
        dados = yaml.safe_load(f) or {}

    return _dict_to_dataclass(AppConfig, dados)
