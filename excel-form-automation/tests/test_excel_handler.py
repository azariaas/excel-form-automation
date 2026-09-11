from openpyxl import Workbook

from automation.excel_handler import get_row_data, is_row_marked, map_headers, mark_row

HIGHLIGHT_COLOR = "FFFF00"


def _build_sheet():
    wb = Workbook()
    ws = wb.active
    ws.append([])  # linha 1
    ws.append([])  # linha 2
    ws.append(["full_name", "phone", "email"])  # linha 3 = cabeçalho
    ws.append(["Maria Fictícia", "(11) 90000-0001", "maria.ficticia@example.com"])  # linha 4
    return ws


def test_map_headers_normalizes_and_maps_columns():
    ws = _build_sheet()
    headers = map_headers(ws, header_row=3)
    assert headers == {"full_name": 1, "phone": 2, "email": 3}


def test_get_row_data_extracts_configured_fields():
    ws = _build_sheet()
    headers = map_headers(ws, header_row=3)
    data = get_row_data(ws, row_number=4, headers=headers, fields=["full_name", "phone", "email"])
    assert data == {
        "full_name": "Maria Fictícia",
        "phone": "(11) 90000-0001",
        "email": "maria.ficticia@example.com",
    }


def test_get_row_data_returns_empty_string_for_missing_column():
    ws = _build_sheet()
    headers = map_headers(ws, header_row=3)
    data = get_row_data(ws, row_number=4, headers=headers, fields=["document_id"])
    assert data == {"document_id": ""}


def test_row_marking_round_trip():
    ws = _build_sheet()
    row = list(ws.iter_rows(min_row=4, max_row=4))[0]

    assert is_row_marked(row[0], HIGHLIGHT_COLOR) is False

    mark_row(row, HIGHLIGHT_COLOR)

    assert is_row_marked(row[0], HIGHLIGHT_COLOR) is True
