#!/usr/bin/env python3
"""
_template.py — Ponto de partida para novas ferramentas (Layer 3 / WAT).

Copie este arquivo, renomeie e implemente uma única responsabilidade.
Execução isolada e testável:
    python3 tools/_template.py --exemplo "valor"
"""

import argparse
import json
import os
import sys

from dotenv import load_dotenv

# Carrega variáveis do .env na raiz do projeto.
load_dotenv()


def run(exemplo: str) -> dict:
    """Faz o trabalho e retorna dados estruturados."""
    # api_key = os.environ["ALGUMA_API_KEY"]  # segredos sempre via .env
    return {"ok": True, "exemplo": exemplo}


def main() -> int:
    parser = argparse.ArgumentParser(description="Descreva o que esta tool faz.")
    parser.add_argument("--exemplo", required=True, help="Um argumento de exemplo.")
    args = parser.parse_args()

    try:
        result = run(args.exemplo)
    except Exception as exc:  # falhe de forma clara
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1

    # Saída estruturada em JSON no stdout.
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
