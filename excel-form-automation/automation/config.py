"""Carregamento e validação da configuração da automação."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class ConfigError(Exception):
    """Erro de configuração inválida ou ausente."""


@dataclass
class TargetConfig:
    code: str
    url: str
    field_selectors: dict[str, str]
    consent_checkbox_selector: str | None
    submit_button_selector: str


@dataclass
class AppConfig:
    spreadsheet_path: Path
    header_row: int
    data_start_row: int
    highlight_color: str
    fields: list[str]
    targets: dict[str, TargetConfig]


def load_config(path: str | Path) -> AppConfig:
    """Lê e valida o arquivo de configuração JSON."""
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(
            f"Arquivo de configuração não encontrado: {config_path}. "
            "Copie data/config.example.json para data/config.json e ajuste os valores."
        )

    with config_path.open(encoding="utf-8") as f:
        raw = json.load(f)

    required_keys = ["spreadsheet_path", "header_row", "data_start_row", "fields", "targets"]
    missing = [key for key in required_keys if key not in raw]
    if missing:
        raise ConfigError(f"Configuração incompleta. Chaves ausentes: {missing}")

    targets = {}
    for code, target_raw in raw["targets"].items():
        targets[code.strip().upper()] = TargetConfig(
            code=code.strip().upper(),
            url=target_raw["url"],
            field_selectors=target_raw["field_selectors"],
            consent_checkbox_selector=target_raw.get("consent_checkbox_selector"),
            submit_button_selector=target_raw.get("submit_button_selector", "button[type='submit']"),
        )

    return AppConfig(
        spreadsheet_path=Path(raw["spreadsheet_path"]),
        header_row=raw["header_row"],
        data_start_row=raw["data_start_row"],
        highlight_color=raw.get("highlight_color", "FFFF00"),
        fields=raw["fields"],
        targets=targets,
    )
