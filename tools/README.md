# tools/ — Camada de Execução (Layer 3)

Scripts Python determinísticos que fazem o trabalho real: chamadas de API,
transformações de dados, operações de arquivo, consultas.

## Convenções

- **Um script, uma responsabilidade.** Nome descritivo: `scrape_single_site.py`,
  `send_newsletter.py`, `summarize_articles.py`.
- **Sempre executável de forma isolada** e testável pela linha de comando.
  Ex.: `python3 tools/scrape_single_site.py --url https://exemplo.com`
- **Segredos vêm do `.env`** (via `python-dotenv`), nunca hardcoded.
- **Entrada/saída previsíveis.** Aceite argumentos (argparse) e retorne dados
  estruturados (JSON no stdout ou arquivo em `.tmp/`).
- **Falhe de forma clara.** Mensagens de erro úteis e exit codes corretos.

## Template base

Use `_template.py` como ponto de partida para novas ferramentas.
