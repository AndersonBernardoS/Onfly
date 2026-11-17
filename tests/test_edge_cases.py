"""Testes adicionais: casos de borda e contrato do relatório (schema e formato)."""

from datetime import datetime, timedelta

from helpers import run_cli


def test_no_confirmed_reservations_produces_zeros(tmp_path):
    """Sem CONFIRMED: contagens preservadas, totais zerados, média "0.00" e listas vazias."""
    # O README pede explicitamente "sem noites, '0.00'" para a média. Sem esse cuidado, o código
    # dividiria por zero e cairia em erro inesperado (código de saída 1).
    rows = [
        {"reservation_id": "R-1", "status": "CANCELLED", "amount": "100.00"},
        {"reservation_id": "R-2", "status": "NO_SHOW", "amount": "200.00"},
    ]

    report = run_cli(tmp_path, rows)

    assert report["summary"] == {
        "total_reservations": 2,
        "confirmed_reservations": 0,
        "cancelled_reservations": 1,
        "no_show_reservations": 1,
        "total_room_nights": 0,
        "total_amount_brl": "0.00",
        "average_nightly_rate_brl": "0.00",
    }
    assert report["by_month"] == []
    assert report["top_hotels"] == []


def test_money_is_plain_string_with_two_decimals(tmp_path):
    """Dinheiro sai como string com 2 casas, sem separador de milhar nem notação científica."""
    # "1234567.5" testa ao mesmo tempo:
    #   - completar a segunda casa decimal ("...50");
    #   - não usar separador de milhar ("1,234,567.50" ou "1.234.567,50");
    #   - não cair em notação científica ("1.2345675E+6"), possível com Decimal mal formatado.
    report = run_cli(tmp_path, [{"reservation_id": "R-1", "amount": "1234567.5"}])

    assert report["summary"]["total_amount_brl"] == "1234567.50"
    assert report["by_month"][0]["total_brl"] == "1234567.50"
    assert report["top_hotels"][0]["total_brl"] == "1234567.50"


def test_report_schema_matches_contract(tmp_path):
    """Chaves, tipos, report_version e offset de generated_at seguem o contrato do README."""
    # O README proíbe mudar nomes, tipos ou semântica dos campos. Este teste trava o contrato:
    # qualquer campo renomeado, adicionado, removido ou com tipo trocado (ex.: int virar str)
    # quebra aqui.
    report = run_cli(tmp_path, [{"reservation_id": "R-1"}])

    assert list(report) == ["report_version", "generated_at", "summary", "by_month", "top_hotels"]
    assert report["report_version"] == "1.0"

    # generated_at é ignorado na comparação de valores, mas o offset fixo -03:00 faz parte do contrato.
    generated_at = datetime.fromisoformat(report["generated_at"])
    assert generated_at.utcoffset() == timedelta(hours=-3)

    integer_fields = [
        "total_reservations",
        "confirmed_reservations",
        "cancelled_reservations",
        "no_show_reservations",
        "total_room_nights",
    ]
    money_fields = ["total_amount_brl", "average_nightly_rate_brl"]
    assert list(report["summary"]) == integer_fields + money_fields
    assert all(type(report["summary"][field]) is int for field in integer_fields)
    assert all(isinstance(report["summary"][field], str) for field in money_fields)

    month = report["by_month"][0]
    assert list(month) == ["month", "reservations", "room_nights", "total_brl"]
    assert (type(month["reservations"]), type(month["room_nights"]), type(month["total_brl"])) == (int, int, str)

    hotel = report["top_hotels"][0]
    assert list(hotel) == ["hotel_id", "hotel_name", "room_nights", "total_brl"]
    assert (type(hotel["room_nights"]), type(hotel["total_brl"])) == (int, str)
