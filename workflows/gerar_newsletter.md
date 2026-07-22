# Workflow: Gerar Radar Diário (relatório matinal)

## Objetivo
Produzir e publicar um briefing matinal seccionado: manchete do dia, indicadores de
mercado e seções temáticas com 2–3 notícias **recentes e específicas** cada, resumidas,
sem repetir o que já saiu. Publicar no GitHub Pages e avisar no WhatsApp.

## Inputs necessários
- `config/sources.json` — seções, queries, roteamento do Gmail, regras de curadoria.
- `.env` com: `GITHUB_REPO`, `GITHUB_TOKEN`, `NEWSLETTER_PUBLIC_URL`,
  `CALLMEBOT_PHONE`, `CALLMEBOT_APIKEY`.
- Data da edição (default: hoje).

## Passos

### 1. Ler configuração e histórico
- Leia `config/sources.json` (seções na ordem do array `secoes`; regras em `curadoria`).
- Leia `site/manifest.json` e os `.md` das últimas edições (janela `janela_dedupe_dias`)
  para **não repetir** notícias já publicadas.

### 2. Indicadores de mercado
`tools/market_data.py --out .tmp/mercado.json` → injeta a lista em `edition.json.mercado`.

### 3. Coletar por seção (bruto → `.tmp/`)
Para cada seção **ativa**, rode suas `queries` via **WebSearch**:
- Priorize resultados das últimas **24–48h** (`curadoria.frescor_horas`). Descarte
  evergreen ('o que é', 'guia', 'tendências para o ano') e opinião genérica.
- Para os candidatos mais fortes, use `tools/scrape_single_site.py --url <url>` para
  puxar o **texto real** e resumir com fidelidade (não resuma pelo título).
- Guarde os candidatos por seção (ex.: `.tmp/coleta_<id>.json`).

**Gmail:** rode a `query` do config via conector; roteie por remetente conforme
`gmail.roteamento` (Agro Espresso → `agro`; Café com seu Dinheiro → `mercado_ma`).
Extraia manchete/trecho/link de cada edição recebida.

> Fonte que falhar (rede/rate limit) → logar e seguir. Nunca travar a edição inteira.

### 3.5. Filtrar já publicados (anti-repetição — determinístico)
Junte os candidatos coletados numa lista e passe por:
`tools/filter_seen.py --candidates .tmp/candidatos.json --dias <janela_dedupe_dias> --out .tmp/novos.json`
Isso remove qualquer URL já publicada (sempre) e títulos parecidos dentro da janela,
comparando contra `site/history.json`. Cure **somente** a partir de `.tmp/novos.json`.
(O histórico é gravado automaticamente pelo `build_edition.py` a cada edição.)

### 4. Selecionar + resumir (papel do agente)
Aplique `curadoria.regras`:
- Por seção: escolha até `max_itens` (2–3), resumo de **3–4 frases**, pt-BR neutro,
  sempre com `url` e `fonte` reais.
- Escolha **1 manchete**: o fato mais relevante do dia (de qualquer seção).
- **Omita** seções sem notícia relevante e recente (não preencher com enrolação).
- Dedupe contra o histórico do passo 1.

Monte `.tmp/edition.json`:
```json
{
  "data": "AAAA-MM-DD",
  "titulo": "Radar Diário",
  "manchete": {"titulo": "...", "resumo": "...", "url": "...", "fonte": "..."},
  "mercado": [ ...indicadores... ],
  "secoes": [
    {"titulo": "Mercado Financeiro & Aquisições", "itens": [
      {"titulo": "...", "resumo": "...", "url": "https://...", "fonte": "..."}
    ]}
  ]
}
```

### 5. Montar a edição
`tools/build_edition.py --input .tmp/edition.json` → gera
`site/editions/AAAA-MM-DD.html` + `.md`, atualiza `manifest.json` e `index.html`.
(Seções vazias são omitidas automaticamente.)

### 6. Publicar
`tools/publish_git.py --data AAAA-MM-DD` (use `--dry-run` para testar sem push).

### 7. Avisar no WhatsApp
`tools/notify_whatsapp.py --edition .tmp/edition.json`
Compõe automaticamente a mensagem-resumo (manchete + 1 destaque por seção + link direto
para a edição, usando `NEWSLETTER_PUBLIC_URL`). Use `--dry-run` para conferir antes.

## Saída esperada
- **Formato:** página HTML seccionada no GitHub Pages + versão Markdown.
- **Destino:** `NEWSLETTER_PUBLIC_URL` (link enviado no WhatsApp).

## Edge cases
- **Fonte fora do ar / rate limit** → pular, logar, continuar.
- **Dia fraco (poucas seções com notícia)** → publicar as que tiverem; avisar o dono se
  o total ficar muito baixo.
- **Só resultados evergreen numa seção** → melhor omitir a seção do que publicar algo atemporal.
- **Falha no push** → checar `GITHUB_TOKEN`.
- **WhatsApp não chega** → checar setup CallMeBot; a edição já está publicada (aviso reenviável).

## Aprendizados
_(Atualize: queries que trazem notícia fresca de verdade, veículos mais confiáveis por
seção, sites que exigem tratamento especial no scrape, etc.)_
