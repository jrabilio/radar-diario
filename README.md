# Automação de Newsletter

Automação diária que **coleta** conteúdo (sites, Gmail, busca web), **seleciona e
resume** os melhores itens, **publica** no GitHub Pages e **avisa** no WhatsApp.
Construída sobre a arquitetura **WAT** (Workflows, Agents, Tools) — ver [CLAUDE.md](CLAUDE.md).

## Estrutura

```
config/sources.json      # fontes de conteúdo (sites, query Gmail, temas)
workflows/               # SOPs em Markdown (o "como fazer")
  gerar_newsletter.md    # workflow principal (diário)
tools/                   # scripts Python determinísticos
  scrape_single_site.py  # raspa sites/blogs
  build_edition.py       # monta a edição (HTML + Markdown)
  publish_git.py         # publica no GitHub Pages
  notify_whatsapp.py     # aviso via CallMeBot
site/                    # repositório publicado (GitHub Pages)
.tmp/                    # dados intermediários (descartáveis)
.env                     # segredos (NÃO versionar)
```

## Setup (uma vez)

1. **Dependências** (já instaladas em `.venv/`):
   ```bash
   python3 -m venv .venv
   ./.venv/bin/pip install -r requirements.txt
   ```
2. **Segredos:** `cp .env.example .env` e preencha:
   - `GITHUB_REPO`, `GITHUB_TOKEN`, `NEWSLETTER_PUBLIC_URL`
   - `CALLMEBOT_PHONE`, `CALLMEBOT_APIKEY`
3. **Fontes:** edite `config/sources.json`.
4. **GitHub Pages:** crie o repositório, ative Pages na branch `main` (raiz).

## Rodar

Peça ao agente: _"gere a newsletter de hoje"_. Ele segue
[workflows/gerar_newsletter.md](workflows/gerar_newsletter.md).

Testar as tools isoladamente:
```bash
./.venv/bin/python tools/scrape_single_site.py --url <URL> --links
./.venv/bin/python tools/build_edition.py --input .tmp/edition.json
./.venv/bin/python tools/publish_git.py --data 2026-07-21 --dry-run
./.venv/bin/python tools/notify_whatsapp.py --message "teste"
```
