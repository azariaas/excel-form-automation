"""Gera uma planilha de exemplo com dados totalmente fictícios.

Cria data/input_example.xlsx com a mesma estrutura esperada por main.py:
cabeçalho na linha 3, dados a partir da linha 4, uma aba por 'localização'.
"""

from pathlib import Path

from openpyxl import Workbook

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "input_example.xlsx"

HEADERS = ["full_name", "phone", "email", "document_id", "notes"]

SAMPLE_ROWS = {
    "LOC1": [
        ["Maria Fictícia", "(11) 90000-0001", "maria.ficticia@example.com", "000.000.000-00", "Preferência à tarde"],
        ["João Exemplo", "(11) 90000-0002", "joao.exemplo@example.com", "111.111.111-11", ""],
    ],
    "LOC2": [
        ["Ana Teste", "(19) 90000-0003", "ana.teste@example.com", "222.222.222-22", "Ligar antes de enviar"],
    ],
}


def build_workbook() -> Workbook:
    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name, rows in SAMPLE_ROWS.items():
        ws = wb.create_sheet(sheet_name)
        ws.append([])  # linha 1 (livre)
        ws.append([])  # linha 2 (livre)
        ws.append(HEADERS)  # linha 3 = cabeçalho
        for row in rows:
            ws.append(row)  # a partir da linha 4

    return wb


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    wb = build_workbook()
    wb.save(OUTPUT_PATH)
    print(f"Planilha de exemplo criada em: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
