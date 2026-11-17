# Declaração de uso de IA

## Ferramenta e modelo

- **Ferramenta:** Claude Code (extensão do VS Code, Windows)
- **Modelo:** Claude Opus 5.5 (`claude-opus-5-5`), da Anthropic
- **Sessão:** uma única sessão, exportada nesta pasta (`sessao-01.jsonl`, formato nativo do Claude Code)

## O que a IA fez

- Leu o README e resumiu a tarefa, as restrições e a lista de entrega.
- Verificou a configuração do ambiente: Python 3.11.9 na `.venv`, ausência do pytest, política de
  execução do PowerShell, ausência de repositório git e de GitHub CLI. Instalou o
  `requirements-dev.txt` na `.venv`.
- Rodou `pytest` e o CLI para registrar o estado inicial (5 falhas).
- Leu o código-fonte e os testes e **apontou os 5 defeitos** com arquivo e linha, incluindo o limite
  de 200 linhas, que nenhum teste fornecido cobre.
- Escreveu o script de comparação linha a linha (`compare.py`) e gerou `report_bug.json` rodando o
  CLI original no arquivo real.
- Analisou o perfil do `reservas_hoteis.csv` (status, moedas, duplicidades, viradas de mês) e
  calculou de forma independente os totais esperados do arquivo completo (300 / 235 / 1347 /
  R$ 396170.00).
- Revisou os diffs que eu apliquei e sugeriu uma simplificação (`return amount * rate`).
- Levantou as regras do README sem cobertura nos testes fornecidos, verificou essas regras no código
  corrigido (nenhum defeito adicional encontrado) e, **a meu pedido, escreveu os 22 testes
  adicionais** em `tests/`, com comentários explicando cada valor esperado.
- Comprovou que os testes novos detectam defeitos: rodou-os contra o código original (9 falhas) e
  contra 6 defeitos injetados numa cópia do código corrigido (todos detectados).
- Redigiu este documento e o `README-ENTREGA.md`, ajustados depois conforme as minhas revisões.

## O que eu fiz

- Decidi o caminho com IA e conduzi a sessão: pedi análise e diagnóstico, **não pedi que o código
  da aplicação (`src/`) fosse corrigido pela IA**.
- Criei o repositório git, o commit inicial com o estado original e a branch de trabalho.
- Ajustei a política de execução do PowerShell e ativei a `.venv`.
- **Apliquei pessoalmente todas as correções no código** (os 5 defeitos), incluindo a simplificação
  do conversor de câmbio.
- Questionei e decidi corrigir o limite de 200 linhas, por considerar inaceitável descartar cerca de
  100 reservas.
- Rodei os testes e o CLI após as correções e validei os resultados.
- Perguntei se havia espaço para mais testes, pedi que a IA os criasse e **revisei os 22 testes
  adicionais** antes de incluí-los.
- Analisei os artefatos da investigação (`compare.py`, `report_bug.json`), pedi explicação sobre a
  origem deles e os incluí na entrega como evidência.
- Revisei os textos de entrega e publiquei o repositório.
