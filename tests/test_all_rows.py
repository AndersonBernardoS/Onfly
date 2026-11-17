"""Testes adicionais: o arquivo de reservas é lido por inteiro.

Cobre o defeito 5 (limite fixo de 200 linhas em `CsvReservationRepository.read`), que nenhum
teste fornecido detecta, porque todos usam poucas linhas.
"""

from helpers import run_cli


def test_reads_every_row_beyond_200(tmp_path):
    """Reservas depois da linha 200 entram nas contagens e nos totais."""
    # 200 confirmadas + 50 canceladas. As canceladas ficam DEPOIS da linha 200 de propósito:
    # se a leitura parar na 200ª reserva, `cancelled_reservations` dá 0 e `total_reservations`
    # dá 200. Assim o teste falha com uma mensagem que aponta direto para o corte.
    rows = [{"reservation_id": f"R-{i:03}", "amount": "100.00"} for i in range(200)]
    rows += [{"reservation_id": f"C-{i:03}", "status": "CANCELLED", "amount": "999.00"} for i in range(50)]

    summary = run_cli(tmp_path, rows)["summary"]

    assert summary["total_reservations"] == 250
    assert summary["confirmed_reservations"] == 200
    assert summary["cancelled_reservations"] == 50
    # 200 confirmadas x R$ 100.00 x 1 noite. As canceladas (R$ 999.00) não podem entrar no valor.
    assert summary["total_room_nights"] == 200
    assert summary["total_amount_brl"] == "20000.00"


def test_rows_after_200_are_billed(tmp_path):
    """Uma reserva confirmada na posição 201 entra no valor e no ranking."""
    # 200 canceladas e só UMA confirmada, a 201ª. Com o limite de 200 linhas, o relatório sairia
    # com valor zero e ranking vazio. Isso mostra que o corte perde dinheiro, não só contagem.
    rows = [{"reservation_id": f"C-{i:03}", "status": "CANCELLED"} for i in range(200)]
    rows.append({"reservation_id": "R-201", "hotel_id": "H99", "hotel_name": "Hotel Final", "amount": "321.00"})

    report = run_cli(tmp_path, rows)

    assert report["summary"]["total_amount_brl"] == "321.00"
    assert [hotel["hotel_id"] for hotel in report["top_hotels"]] == ["H99"]
