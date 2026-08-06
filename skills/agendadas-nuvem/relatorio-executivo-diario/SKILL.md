---
name: relatorio-executivo-diario
description: Relatório Executivo — newsletters, mercado, ESG e clipping Grupo NEST (06h45 BRT, Cloud Routine)
---

Você é um assistente executivo. Gere o Relatório Executivo de Notícias Diário em HTML com
quatro blocos: newsletters, mercado (+ M&A), ESG e clipping Grupo NEST. Deposite o
resultado no Google Drive e avise no WhatsApp.

## O que mudou em relação à versão antiga (05/08/2026)

A versão anterior desta rotina morreu porque tinha duas metades em máquinas diferentes: o
Cowork gerava o HTML, e um LaunchAgent **no Mac do Abilio** enviava por e-mail às 07:30.
Quando o LaunchAgent deixou de existir, o relatório parou de chegar — última saída em
17/07/2026.

Esta versão roda inteira na nuvem e não depende de máquina nenhuma:

| Antes | Agora |
|---|---|
| Salvava em pasta local do Mac | Salva no Google Drive (conector) |
| LaunchAgent enviava por SMTP | Sem e-mail — a conta `@ecotransformax` é Workspace e não permite App Password |
| Artefato no Cowork | Aviso no WhatsApp com o link do Drive |

**Nunca** tente escrever em `/Users/...`, ler o `.env` do repositório ou usar
`tools/notify_whatsapp.py`: a rotina não enxerga o Mac nem variáveis de ambiente locais.
As credenciais do CallMeBot vêm no próprio prompt da rotina.

**Nunca** faça commit ou push do relatório neste repositório. O remote é **público** —
serve o GitHub Pages da newsletter — e o Bloco 4 traz clipping interno do Grupo NEST.

## REGRAS DE QUALIDADE

1. **Profundidade nos e-mails**: leia o corpo da mensagem quando o snippet mencionar: fato
   relevante, CVM, B3, dólar, Selic, Copom, M&A, aquisição, fusão, resultado, lucro,
   prejuízo, IPCA, safra, alta/queda com %, R$ com 3+ dígitos, escândalo, novo CEO. Caso
   contrário, o snippet basta. Nord Research: SEMPRE ler o corpo. Orçamento: até 3 leituras
   de corpo por execução (Nord não conta).
2. **Links corretos**: use a URL exata retornada pela busca. Se só voltou home ou categoria,
   faça uma busca extra com o título entre aspas. Se ainda assim não houver URL da matéria,
   omita o link — **não invente**.
3. **Sem repetição**: antes de montar, leia o HTML do dia anterior no Drive e extraia os
   títulos. Descarte manchetes com 3+ palavras-chave em comum. Desdobramentos novos: marque
   com `[ATUALIZAÇÃO]`.
4. **Frescor**: priorize D-0 ou D-1. Ignore matérias com mais de 72h.
5. **Sem auto-citação**: use `-site:ntics.com.br` nas buscas de ESG e mercado.
6. **Sumário executivo**: 3 bullets antes do Bloco 1 com os destaques do dia.

## Passo 1 — Gmail (conector)

Data de hoje: `YYYY/MM/DD`. Se não houver resultado no dia, use D-1.

**Busca A**: `from:news@agroespresso.com OR from:entrepoderes@mail.beehiiv.com OR from:news@cafecomseudinheiro.com after:YYYY/MM/DD` — até 5 resultados
**Busca B**: `from:renato.breia@mail.nordresearch.com.br OR from:contato@mail.nordresearch.com.br after:YYYY/MM/DD` — até 3 resultados

De cada newsletter extraia: título, 2–3 manchetes com explicação de 2–4 linhas, até 2 links
internos relevantes, e o marcador `[IMPORTANTE]` quando envolver fato relevante, M&A ou
impacto de mercado.

## Passo 2 — Web: 10 buscas paralelas

**1 — Negócios + M&A**: `"Brazil Journal" OR NeoFeed OR InfoMoney OR Exame mercado negócios fusão aquisição compra deal empresa Brasil [mês ano] -site:ntics.com.br`
**2 — Mercado do dia**: `Ibovespa fechamento "[data D-0 ou D-1]" dólar bolsa Brasil`
**3 — Regulatório**: `CVM B3 fato relevante comunicado "[mês ano]"`
**4 — ESG**: `ESG sustentabilidade green bond descarbonização governança Brasil empresas "[mês ano]" -site:ntics.com.br`

**5 a 10 — Clipping Grupo NEST.** Calcule a segunda-feira da semana corrente:

```python
from datetime import date, timedelta
hoje = date.today()
data_segunda_str = (hoje - timedelta(days=hoje.weekday())).strftime("%Y/%m/%d")
```

**5**: `"NTICS Projetos" after:DATA_SEGUNDA -site:ntics.com.br -site:ntics.co`
**6**: `"Ecotransforma" after:DATA_SEGUNDA -site:ntics.com.br`
**7**: `"Ecotransforma SB" after:DATA_SEGUNDA`
**8**: `"Sustentabilidade e Cultura Produções" after:DATA_SEGUNDA`
**9**: `"Cultura Ambiental Produções" after:DATA_SEGUNDA`
**10**: `"Oliveira Produções" after:DATA_SEGUNDA`

**Extração**:
- Bloco 2 mercado: 2 notícias por portal (Brazil Journal, NeoFeed, InfoMoney, Exame, B3, CVM), resumo de 2 linhas.
- Bloco 2 M&A: até 4 deals com valor, partes e contexto estratégico. Priorize D-0/D-1.
- Bloco 3 ESG: 3 notícias com resumo de 2 linhas e link direto.
- Bloco 4 Clipping: **todas** as matérias e menções da semana corrente (DATA_SEGUNDA até
  hoje) sobre qualquer empresa do Grupo NEST — portais regionais, sites de prefeitura,
  imprensa local, blogs. Agrupe por empresa. Sem menções: escreva "Sem menções identificadas
  esta semana (DATA_SEGUNDA a DATA_HOJE)" — **nunca** substitua por perfis de redes sociais.

## Passo 3 — Deduplicação

Busque no Drive, na pasta `Relatorios-Executivos`, o HTML mais recente. Extraia os títulos já
publicados e descarte o que se repetir:

```bash
grep -oP '(?<=<h3 class="news-title">)[^<]+' relatorio_anterior.html
```

## Passo 4 — Gerar o HTML

O template vem do próprio repositório desta rotina: `tools/legado/gerar_relatorio_template.py`.
Ele espera as variáveis abaixo no escopo e grava em `output_path`.

```python
sumario = ["destaque 1", "destaque 2", "destaque 3"]

bloco1 = [
    {"fonte": "Agro Espresso",         "cor": "#2E6B30", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
    {"fonte": "Entre Poderes",         "cor": "#1A2744", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
    {"fonte": "Nord Research",         "cor": "#7B1818", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
    {"fonte": "Café com Seu Dinheiro", "cor": "#5C3317", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
]

bloco2_mercado = [
    {"portal": "B3 / Mercado",  "cor": "#1A6B3C", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
    {"portal": "NeoFeed",       "cor": "#1A6B3C", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
    {"portal": "Brazil Journal","cor": "#1A6B3C", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
    {"portal": "CVM",           "cor": "#1A6B3C", "noticias": [{"titulo": "...", "resumo": "...", "link": ""}]},
]

bloco2_ma = [{"titulo": "...", "resumo": "Partes, valor, contexto estratégico.", "link": ""}]

bloco3 = [
    {"portal": "ESG / Sustentabilidade", "cor": "#2E7D5A", "noticias": [
        {"titulo": "...", "resumo": "...", "link": ""},
    ]},
]

bloco4_ntics = [
    {"empresa": "Ecotransforma", "fonte": "Portal XYZ", "titulo": "...", "resumo": "...", "link": ""},
]
data_segunda_clipping = "DD/MM/YYYY"
nota_clipping = ""

output_path = f"/tmp/Relatorio_Executivo_{hoje.strftime('%d-%m-%Y')}.html"
exec(open("tools/legado/gerar_relatorio_template.py").read())
```

Confira que o arquivo existe e tem tamanho plausível (dezenas de KB) antes de seguir.

## Passo 5 — Depositar no Google Drive

Use o conector do Google Drive. Pasta de destino: **`Relatorios-Executivos`** na raiz do
Drive da conta `abilio@ecotransformax.com.br`. Se não existir, crie.

Nome do arquivo: `Relatorio_Executivo_DD-MM-AAAA.html`.

Guarde o **link de visualização** do arquivo criado — ele vai na mensagem do WhatsApp.

Se o upload falhar, **pare e relate**. Não tente salvar em outro lugar, e principalmente não
faça commit no repositório.

## Passo 6 — Avisar no WhatsApp

O prompt da rotina traz `CALLMEBOT_PHONE` e `CALLMEBOT_APIKEY`. Chame a API direto:

```
https://api.callmebot.com/whatsapp.php?phone=<PHONE>&apikey=<APIKEY>&text=<mensagem url-encoded>
```

Formato da mensagem — o **link vai na segunda linha**, porque o CallMeBot trunca mensagens
longas e o que importa não pode ser cortado:

```
📊 Relatório Executivo — DD/MM
🔗 <link do Drive>

🔦 <destaque 1 do sumário>

Blocos: N boletins · N mercado · N M&A · N ESG · N clipping
```

HTTP 200 significa enfileirado com sucesso. Se falhar, relate — o relatório já está salvo
no Drive de qualquer forma, e o aviso pode ser reenviado.

## Passo 7 — Fechar

Resuma no chat:

```
Relatório Executivo — [DATA]
✅ Drive: Relatorios-Executivos/Relatorio_Executivo_[DATA].html
✅ WhatsApp: avisado

Sumário: [3 bullets]
Bloco 1: [N] boletins | [M] leituras de corpo
Bloco 2 Mercado: [N] portais | M&A: [N] transações
Bloco 3 ESG: [N] notícias
Bloco 4 Clipping: [N] menções esta semana (DD/MM a DD/MM)
Duplicatas descartadas: [N]
```
