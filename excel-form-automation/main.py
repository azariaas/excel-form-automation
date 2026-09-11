"""Ponto de entrada: percorre a planilha e envia cada linha pendente ao formulário-alvo."""

from __future__ import annotations

import argparse
import logging

from automation.config import ConfigError, load_config
from automation.excel_handler import (
    get_row_data,
    is_row_marked,
    load_workbook_file,
    map_headers,
    mark_row,
    save_workbook_file,
)
from automation.form_filler import FormSubmissionError, fill_and_submit, start_driver

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Automação de preenchimento de formulário a partir de planilha.")
    parser.add_argument("--config", default="data/config.json", help="Caminho do arquivo de configuração JSON.")
    parser.add_argument("--headless", action="store_true", help="Executa o navegador em modo headless.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        logger.error(str(exc))
        return

    try:
        wb = load_workbook_file(config.spreadsheet_path)
    except FileNotFoundError as exc:
        logger.error(str(exc))
        return

    driver = start_driver(headless=args.headless)

    sent = skipped = errors = 0

    try:
        for sheet_name in wb.sheetnames:
            location_code = sheet_name.strip().upper()
            target = config.targets.get(location_code)
            if not target:
                logger.warning("Aba '%s' não possui alvo configurado — pulando.", sheet_name)
                continue

            ws = wb[sheet_name]
            logger.info("Processando aba '%s' → %s", sheet_name, target.url)

            headers = map_headers(ws, config.header_row)
            key_field = config.fields[0]
            key_column = headers.get(key_field.lower())
            if not key_column:
                logger.error(
                    "Coluna-chave '%s' não encontrada na aba '%s' — pulando aba.", key_field, sheet_name
                )
                continue

            for row in ws.iter_rows(min_row=config.data_start_row):
                key_cell = ws.cell(row=row[0].row, column=key_column)

                if not key_cell.value or not str(key_cell.value).strip():
                    continue

                if is_row_marked(key_cell, config.highlight_color):
                    skipped += 1
                    continue

                data = get_row_data(ws, row[0].row, headers, config.fields)

                try:
                    fill_and_submit(driver, target, data)
                    mark_row(row, config.highlight_color)
                    save_workbook_file(wb, config.spreadsheet_path)
                    logger.info("Enviado: %s", data.get(key_field, "(sem identificação)"))
                    sent += 1
                except FormSubmissionError as exc:
                    logger.error("Falha ao enviar %s: %s", data.get(key_field, "(sem identificação)"), exc)
                    errors += 1
    finally:
        driver.quit()

    logger.info("Concluído — %s enviados, %s pulados (já enviados), %s erros.", sent, skipped, errors)


if __name__ == "__main__":
    main()
