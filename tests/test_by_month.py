"""Testes adicionais: agrupamento mensal (by_month)."""

from helpers import run_cli


def test_year_boundary_with_multiple_rooms_counts_in_checkin_month(tmp_path):
    """Estadia que vira o ano conta as noites inteiras no mês do check-in."""
    # 30/12/2024 -> 02/01/2025 = 3 noites x 2 quartos = 6 room_nights.
    # Três regras de uma vez:
    #   - diferença de datas na virada de ANO (o teste fornecido cobre só a virada de mês);
    #   - multiplicação por quartos;
    #   - by_month usa o mês do CHECK-IN ("2024-12"), sem dividir as noites entre os meses.
    rows = [{"reservation_id": "R-1", "checkin_date": "2024-12-30", "checkout_date": "2025-01-02", "rooms": "2"}]

    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_room_nights"] == 6
    assert report["by_month"] == [
        {"month": "2024-12", "reservations": 1, "room_nights": 6, "total_brl": "100.00"}
    ]


def test_by_month_is_sorted_and_ignores_non_billable(tmp_path):
    """Meses em ordem crescente; CANCELLED e NO_SHOW não criam mês nem somam nele."""
    # Fevereiro entra antes de janeiro, para provar que a ordem vem do sort e não da inserção.
    # Março só tem NO_SHOW e abril só tem CANCELLED: os dois meses não podem aparecer.
    # Janeiro tem um NO_SHOW junto de uma confirmada: "reservations" deve ser 1, não 2.
    rows = [
        {"reservation_id": "R-1", "checkin_date": "2025-02-10", "checkout_date": "2025-02-11", "amount": "50.00"},
        {"reservation_id": "R-2", "checkin_date": "2025-01-31", "checkout_date": "2025-02-02", "amount": "80.00"},
        {"reservation_id": "R-3", "status": "NO_SHOW", "checkin_date": "2025-01-05", "checkout_date": "2025-01-06"},
        {"reservation_id": "R-4", "status": "NO_SHOW", "checkin_date": "2025-03-01", "checkout_date": "2025-03-02"},
        {"reservation_id": "R-5", "status": "CANCELLED", "checkin_date": "2025-04-01", "checkout_date": "2025-04-02"},
    ]

    report = run_cli(tmp_path, rows)

    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 1, "room_nights": 2, "total_brl": "80.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 1, "total_brl": "50.00"},
    ]
