# Entrega — Consolidador de reservas de hotel

## Resumo

Encontrei e corrigi **5 defeitos** no CLI. Os 5 testes fornecidos passam sem alteração. A amostra de
validação bate campo a campo com as tabelas do README. O relatório do arquivo real passou a considerar
as **300** reservas; antes, só 200 eram lidas.

| Execução | Antes | Depois |
|-|-|-|
| `pytest -q` | 5 failed | **5 passed** |
| Amostra (`exemplo-validacao.csv`) | 12 reservas, **-33** noites, R$ **5962.41**, média **0.00** | 12 reservas, **28** noites, R$ **7566.00**, média **270.21** |
| Arquivo real (`reservas_hoteis.csv`) | **200** reservas, 153 confirmadas, **-1393** noites, R$ 193218.53 | **300** reservas, **235** confirmadas, **1347** noites, R$ **396170.00** |

## Defeitos corrigidos

| # | Arquivo | Defeito | Causa raiz (uma frase) | Correção |
|-|-|-|-|-|
| 1 | `services/stay_calculator.py` | Noites negativas em estadias que viram o mês ou o ano | Subtraía o **dia do mês** (`checkout.day - checkin.day`) em vez da diferença entre as datas. | `(checkout - checkin).days * rooms` |
| 2 | `services/status_policy.py` | `NO_SHOW` entrava em noites, valores, `by_month` e `top_hotels` | A regra excluía só `CANCELLED` (`!=`), em vez de aceitar só `CONFIRMED`. | `status == "CONFIRMED"` |
| 3 | `services/currency_converter.py` | Valores em USD/EUR muito abaixo do real e com imprecisão | **Dividia** pela taxa em vez de multiplicar e convertia para `float`, contrariando a regra de usar `Decimal`. | `amount * rate`, só com `Decimal` |
| 4 | `services/report_builder.py` | `top_hotels` mostrava os hotéis de **menor** valor | A ordenação usava o valor crescente como chave. | Chave `(-amount, hotel_id)`: valor decrescente, empate por `hotel_id` crescente |
| 5 | `repositories/csv_reservation_repository.py` | Só as 200 primeiras reservas do arquivo eram lidas | Um `if len(rows) == 200: break` interrompia a leitura do CSV. | Limite removido; o arquivo é lido inteiro |

O defeito 5 não aparece na amostra (12 linhas) nem nos testes fornecidos. Ele só aparece ao rodar o
CLI no arquivo real: o resumo mostrava `Reservas: 200`, mas o CSV tem 300 linhas de dados. Das 100
reservas descartadas, 82 eram `CONFIRMED`.

## Como investiguei

Fiz a investigação junto com o **Claude Code** (Claude Opus 5.5). A IA fez a maior parte do
diagnóstico: leu o código, comparou com as regras do README e apontou onde estava cada defeito.
**Eu apliquei todas as correções no código**, validei os resultados e decidi o que entrava na
entrega. A sessão completa está em [`uso-de-ia/`](uso-de-ia/), e a divisão detalhada de tarefas,
em [`declaracao.md`](uso-de-ia/declaracao.md).

1. **Leitura das regras e do ambiente.** Pedi à IA uma análise do README e da pasta. Ela resumiu
   a tarefa e as restrições, verificou o ambiente (Python 3.11.9 na `.venv`, pytest ainda não
   instalado, política de execução do PowerShell bloqueando o `Activate.ps1`, pasta ainda sem git)
   e instalou o `requirements-dev.txt`. Eu criei o repositório, o commit inicial com o código
   original e a branch de trabalho.
2. **Linha de base.** A IA rodou `pytest -q` (5 falhas) e o CLI na amostra. As mensagens de falha
   já apontavam sintomas: `-28 == 3` nas noites e o ranking invertido `['H04', 'H03', 'H02']`.
3. **Comparação linha a linha.** Pedi que a IA cruzasse o `output/exemplo.json` com os dados. Ela
   escreveu o script [`compare.py`](evidencias/compare.py), que calcula cada reserva da amostra de
   dois jeitos: com a fórmula do código original e com a regra do README. Só 4 das 12 linhas
   divergiam, cada uma ligada a um defeito:
   - EX-03, que vira o mês com 2 quartos: **-52** noites em vez de 10 (defeito 1);
   - EX-02 (USD) e EX-09 (EUR): **36.90** e **25.51** em vez de 1084.00 e 882.00 (defeito 3);
   - EX-05 (`NO_SHOW`): entrava nos totais (defeito 2).

   Somando as 9 confirmadas com as regras corretas, o resultado foi exatamente 28 noites e
   R$ 7566.00, que são os valores do README.
4. **Localização no código.** A IA leu o código-fonte e apontou cada fórmula divergente com
   arquivo e linha (`stay_calculator`, `status_policy`, `currency_converter`), além da ordenação
   do ranking no `report_builder`.
5. **Arquivo real.** A IA rodou o CLI original no `reservas_hoteis.csv` (saída guardada em
   [`report_bug.json`](evidencias/report_bug.json)) e notou que o resumo mostrava 200 reservas
   para um arquivo de 300. Ela encontrou o `break` no repositório (defeito 5). Eu considerei
   inaceitável descartar cerca de 100 reservas e pedi a análise de onde corrigir. A IA também
   verificou que os dados estão consistentes: só 3 status e 3 moedas, todas com taxa, nenhum ID
   duplicado, nenhum check-out anterior ao check-in e 93 estadias que viram o mês.
6. **Correção.** Apliquei as 5 correções no código. A IA revisou o diff e sugeriu simplificar o
   conversor (`Decimal(str(amount * rate))` → `amount * rate`), sugestão que eu apliquei.
7. **Validação.** Rodei `pytest` e o CLI depois das correções. A IA conferiu `output/exemplo.json`
   campo a campo com as tabelas do README e calculou de forma independente, direto do CSV, os
   totais esperados para o arquivo real (300 / 235 / 1347 / R$ 396170.00), que bateram com a saída
   do CLI.
8. **Entendimento dos artefatos.** Analisei o `compare.py` e o `report_bug.json` e pedi à IA que
   explicasse por que foram criados e de onde vinham os dados, antes de incluí-los aqui como
   evidência.

Também verificamos pontos que **já estavam corretos** e não precisaram de mudança: arredondamento
half-up só em `format_money`, contagem por status antes do filtro, `by_month` pelo mês do check-in
em ordem crescente, `generated_at` com offset `-03:00`, códigos de saída e validação de `--top`.

> `evidencias/compare.py` reproduz **de propósito** as fórmulas com defeito, para comparação. Ele é
> uma evidência da investigação e não faz parte do CLI. Para rodá-lo a partir da raiz do projeto:
> `python entrega/evidencias/compare.py data/exemplo-validacao.csv`.

## Como validar

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest -q

$env:PYTHONPATH="src"
python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -q
PYTHONPATH=src python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json
```

Saídas esperadas no stdout:

```
# exemplo-validacao.csv
Reservas: 12 | Confirmadas: 9 | Noites: 28 | Total BRL: 7566.00

# reservas_hoteis.csv
Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00
```

Em `output/exemplo.json`, `summary`, `by_month` e `top_hotels` são idênticos às tabelas da seção
"Amostra de validação" do README, incluindo `average_nightly_rate_brl = "270.21"` e o ranking
H01, H02, H12, H10, H09.

## Testes adicionados

Os 5 testes fornecidos não cobrem várias regras do README, entre elas o defeito 5, que nenhum deles
detecta. A meu pedido, a IA escreveu **22 testes** em 6 arquivos, que eu revisei. Os testes
fornecidos não foram alterados. Todos os novos usam o `run_cli`
de `tests/helpers.py`, ou seja, testam o CLI de ponta a ponta, como os testes originais.

| Arquivo | Testes | O que protege |
|-|-|-|
| [`tests/test_all_rows.py`](../tests/test_all_rows.py) | 2 | Leitura do arquivo inteiro: reservas depois da 200ª entram nas contagens, nos valores e no ranking (defeito 5) |
| [`tests/test_rounding.py`](../tests/test_rounding.py) | 3 | Soma exata com arredondamento só no fim (`4.07`, e não `4.08`), half-up (`100.125 → 100.13`, e não `100.12`), média sobre totais exatos |
| [`tests/test_top_hotels_extra.py`](../tests/test_top_hotels_extra.py) | 5 | Desempate por `hotel_id` crescente, valor antes do desempate, agregação por hotel com moeda e quartos, limite do `--top` |
| [`tests/test_by_month.py`](../tests/test_by_month.py) | 2 | Virada de **ano** com vários quartos, mês do check-in, ordem crescente, `CANCELLED`/`NO_SHOW` fora do agrupamento |
| [`tests/test_edge_cases.py`](../tests/test_edge_cases.py) | 3 | Arquivo sem `CONFIRMED` (média `"0.00"`, listas vazias), formato do dinheiro (`"1234567.50"`), schema completo (chaves, ordem, tipos, `report_version`, offset `-03:00`) |
| [`tests/test_exit_codes.py`](../tests/test_exit_codes.py) | 7 | Código 0 em sucesso; código 2 para `--top 0`, `--top abc`, `--input` ausente, arquivos inexistentes e colunas ausentes, sem gravar relatório |

Os valores esperados foram escolhidos para **diferenciar a implementação certa da errada**. Cada
teste tem comentários explicando o motivo do valor escolhido.

**Como verificamos que os testes realmente detectam defeitos:**

- **Contra o código original** (commit inicial): 9 dos 22 testes novos falham, incluindo os 2 de
  `test_all_rows.py`. Os 13 que passam cobrem regras que já estavam corretas (half-up, schema,
  códigos de saída) e servem como proteção contra regressões.
- **Contra defeitos injetados** numa cópia do código corrigido, cada mutação foi detectada só
  pelos testes novos (os 5 fornecidos continuaram passando em todas):

  | Defeito injetado | Testes que falharam |
  |-|-|
  | `ROUND_HALF_EVEN` no lugar de `ROUND_HALF_UP` | `test_rounding.py` (2) |
  | Arredondar cada conversão antes de somar | `test_rounding.py` (2) |
  | Chave do ranking invertida (`hotel_id` antes do valor) | `test_top_hotels_extra.py` (2) |
  | Desempate por `hotel_id` decrescente | `test_top_hotels_extra.py` (1) |
  | Erro de leitura devolvendo código 1 em vez de 2 | `test_exit_codes.py` (3) |
  | Média sem proteção contra zero noites | `test_edge_cases.py` (1) |

## Resultado do `pytest`

```
$ pytest -q
...........................                                              [100%]
27 passed in 15.06s
```

5 testes fornecidos (sem alteração) + 22 testes adicionais.

`ruff check src tests` → `All checks passed!`

## Uso de IA

Usei o Claude Code (Claude Opus 5.5) no diagnóstico, na verificação, na escrita dos testes
adicionais e na redação destes documentos. As correções no código da aplicação (`src/`) foram
aplicadas por mim. A declaração está em
[`uso-de-ia/declaracao.md`](uso-de-ia/declaracao.md) e a exportação da sessão em
[`uso-de-ia/`](uso-de-ia/).
