# Workflow: <Nome do Workflow>

## Objetivo
<O que este workflow entrega, em uma frase.>

## Inputs necessários
- `<input_1>` — <descrição>
- `<input_2>` — <descrição>

## Passos
1. <Ação> → executar `tools/<script>.py` com `<args>`
2. <Ação> → ...
3. <Ação> → ...

## Saída esperada
- **Formato:** <ex.: linha em Google Sheets, rascunho de e-mail, JSON em `.tmp/`>
- **Destino:** <onde o dono do projeto acessa o resultado>

## Edge cases
- **<Falha possível>** → <como reagir>
- **Rate limit / API fora do ar** → <estratégia de retry / backoff>
- **Dados faltando** → <o que fazer / o que perguntar>

## Aprendizados
<Atualize conforme descobrir constraints, timing, comportamentos inesperados.>
