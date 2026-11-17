"""Testes adicionais: exatidão monetária (Decimal, half-up, arredondar só na serialização).

Cada valor esperado foi escolhido para dar um resultado DIFERENTE em uma implementação errada.
Um teste que passa com qualquer estratégia de arredondamento não protege nada.
"""

from helpers import run_cli


def test_sum_exact_values_and_round_only_at_the_end(tmp_path):
    """Os valores exatos são somados e o arredondamento acontece uma vez, na serialização."""
    # USD 0.25 x 5.42 = 1.355 BRL (exato, 3 casas).
    #   Correto:  1.355 + 1.355 + 1.355 = 4.065  -> half-up -> "4.07"
    #   Errado:   arredondar cada linha antes: 1.36 x 3 = 4.08
    rows = [{"reservation_id": f"R-{i}", "currency": "USD", "amount": "0.25"} for i in range(3)]

    summary = run_cli(tmp_path, rows)["summary"]

    assert summary["total_amount_brl"] == "4.07"


def test_rounding_is_half_up_not_bankers(tmp_path):
    """Empate na terceira casa arredonda para cima (half-up), e não para o par (half-even)."""
    # 100.125 está exatamente no meio entre 100.12 e 100.13.
    #   ROUND_HALF_UP   -> 100.13  (regra do README)
    #   ROUND_HALF_EVEN -> 100.12  (padrão do Decimal e do round() do Python)
    # O "2" antes do "5" é par: é esse caso que diferencia as duas estratégias.
    summary = run_cli(tmp_path, [{"reservation_id": "R-1", "amount": "100.125"}])["summary"]

    assert summary["total_amount_brl"] == "100.13"


def test_average_nightly_rate_uses_exact_totals(tmp_path):
    """average_nightly_rate_brl = total exato / noites, arredondado só no final."""
    # R$ 100.00 em 3 noites (10/01 -> 13/01) = 33.333... -> "33.33".
    # Uma divisão inteira daria "33.00", e uma média sobre totais já arredondados poderia
    # acumular erro em outros cenários.
    summary = run_cli(
        tmp_path,
        [{"reservation_id": "R-1", "amount": "100.00", "checkin_date": "2025-01-10", "checkout_date": "2025-01-13"}],
    )["summary"]

    assert summary["total_room_nights"] == 3
    assert summary["average_nightly_rate_brl"] == "33.33"
