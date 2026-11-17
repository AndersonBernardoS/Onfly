"""Testes adicionais: códigos de saída do CLI (0 sucesso, 2 entrada/argumento inválido).

`helpers.run_cli` exige código 0. Por isso este arquivo tem um executor próprio, que devolve o
processo sem verificar o código, reaproveitando a mesma montagem de PYTHONPATH.
"""

import os
import subprocess
import sys

import pytest
from helpers import PROJECT_ROOT, SRC_DIR

SAMPLE = str(PROJECT_ROOT / "data" / "exemplo-validacao.csv")
RATES = str(PROJECT_ROOT / "data" / "taxas_cambio.csv")


def run_raw(args: list[str]) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", *args],
        cwd=str(PROJECT_ROOT),
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_success_exits_with_zero(tmp_path):
    """Entrada válida termina com código 0 e grava o relatório."""
    output = tmp_path / "report.json"

    process = run_raw(["--input", SAMPLE, "--rates", RATES, "--output", str(output)])

    assert process.returncode == 0, process.stderr
    assert output.exists()


# Cada caso viola o contrato do CLI de um jeito diferente: valor fora da faixa, tipo errado,
# argumento obrigatório ausente, arquivo inexistente e CSV sem as colunas esperadas. Todos são
# "entrada/argumento inválido" no README, então todos devem dar 2, e não 1 (erro inesperado).
@pytest.mark.parametrize(
    ("case", "extra_args"),
    [
        ("top_zero", ["--input", SAMPLE, "--rates", RATES, "--top", "0"]),
        ("top_not_integer", ["--input", SAMPLE, "--rates", RATES, "--top", "abc"]),
        ("missing_input_argument", ["--rates", RATES]),
        ("input_file_not_found", ["--input", "nao_existe.csv", "--rates", RATES]),
        ("rates_file_not_found", ["--input", SAMPLE, "--rates", "nao_existe.csv"]),
    ],
)
def test_invalid_input_exits_with_two(tmp_path, case, extra_args):
    """Argumento ou arquivo de entrada inválido termina com código 2 e não grava relatório."""
    output = tmp_path / "report.json"

    process = run_raw([*extra_args, "--output", str(output)])

    assert process.returncode == 2, f"{case}: {process.stderr}"
    assert not output.exists()


def test_missing_columns_exits_with_two(tmp_path):
    """CSV de reservas sem as colunas obrigatórias termina com código 2."""
    bad_input = tmp_path / "reservas.csv"
    bad_input.write_text("reservation_id\nR-1\n", encoding="utf-8")
    output = tmp_path / "report.json"

    process = run_raw(["--input", str(bad_input), "--rates", RATES, "--output", str(output)])

    assert process.returncode == 2, process.stderr
    assert not output.exists()
