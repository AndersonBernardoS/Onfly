"""Testes adicionais: ranking de hotéis (desempate, agregação e limite do --top).

O teste fornecido (`test_top_hotels.py`) cobre só a ordem decrescente com valores distintos.
"""

from helpers import run_cli


def test_tie_is_broken_by_hotel_id_ascending(tmp_path):
    """Hotéis com o mesmo total ficam em ordem crescente de hotel_id."""
    # Os hotéis entram fora de ordem (H03, H01, H02), assim o teste não passa por acaso só por
    # preservar a ordem de inserção.
    rows = [
        {"reservation_id": "R-1", "hotel_id": "H03", "hotel_name": "Hotel C", "amount": "500.00"},
        {"reservation_id": "R-2", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "500.00"},
        {"reservation_id": "R-3", "hotel_id": "H02", "hotel_name": "Hotel B", "amount": "500.00"},
    ]

    report = run_cli(tmp_path, rows)

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H01", "H02", "H03"]


def test_higher_total_wins_over_tie_breaker(tmp_path):
    """O valor decide antes do hotel_id: H09 com mais dinheiro vem antes de H01."""
    # Protege contra uma inversão da chave (hotel_id primeiro, valor depois), que também passaria
    # no teste de empate acima.
    rows = [
        {"reservation_id": "R-1", "hotel_id": "H01", "hotel_name": "Hotel A", "amount": "100.00"},
        {"reservation_id": "R-2", "hotel_id": "H09", "hotel_name": "Hotel Z", "amount": "100.01"},
    ]

    report = run_cli(tmp_path, rows)

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H09", "H01"]


def test_reservations_of_same_hotel_are_aggregated(tmp_path):
    """Várias reservas do mesmo hotel somam noites e valores numa única linha do ranking."""
    # R-1: 1 noite x 1 quarto = 1 noite, R$ 100.00
    # R-2: 1 noite x 2 quartos = 2 noites, USD 50.00 x 5.42 = R$ 271.00
    # Total do hotel: 3 noites, R$ 371.00. Mistura moeda e quartos para cobrir os dois na agregação.
    rows = [
        {"reservation_id": "R-1", "hotel_id": "H01", "amount": "100.00"},
        {"reservation_id": "R-2", "hotel_id": "H01", "amount": "50.00", "currency": "USD", "rooms": "2"},
    ]

    report = run_cli(tmp_path, rows)

    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 3, "total_brl": "371.00"}
    ]


def test_top_limits_ranking_size(tmp_path):
    """--top N devolve exatamente N hotéis quando há mais do que N."""
    # 7 hotéis com valores crescentes (100, 200, ..., 700). Com --top 2, só os dois maiores ficam.
    rows = [
        {"reservation_id": f"R-{i}", "hotel_id": f"H{i:02}", "amount": f"{i * 100}.00"} for i in range(1, 8)
    ]

    report = run_cli(tmp_path, rows, top=2)

    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H07", "H06"]


def test_top_returns_fewer_items_when_there_are_fewer_hotels(tmp_path):
    """Com menos hotéis que --top, o ranking traz só os hotéis existentes, sem preencher."""
    report = run_cli(tmp_path, [{"reservation_id": "R-1"}], top=5)

    assert len(report["top_hotels"]) == 1
