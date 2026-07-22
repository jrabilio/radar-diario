# workflows/ — Camada de Instruções (Layer 1)

SOPs (procedimentos operacionais padrão) em Markdown. Cada workflow descreve,
em linguagem clara, **o que** fazer e **como**, sem escrever o código.

## Estrutura de cada workflow

Todo arquivo em `workflows/` deve conter:

1. **Objetivo** — o que este workflow entrega.
2. **Inputs necessários** — dados/parâmetros exigidos antes de começar.
3. **Tools utilizadas** — quais scripts de `tools/` chamar, e em que ordem.
4. **Saída esperada** — formato e destino do resultado (ex.: Google Sheets).
5. **Edge cases** — como lidar com falhas, rate limits, dados faltando.

Use `_template.md` como ponto de partida.

> Não crie nem sobrescreva workflows sem confirmar com o dono do projeto.
