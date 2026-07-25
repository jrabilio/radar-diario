#!/usr/bin/env python3
"""
notify_whatsapp.py — Envia aviso no WhatsApp via CallMeBot (Layer 3 / WAT).

Setup (uma vez): https://www.callmebot.com/blog/free-api-whatsapp-messages/
  1) Adicione +34 644 51 95 23 aos contatos
  2) Envie: "I allow callmebot to send me messages"
  3) Guarde a apikey recebida no .env

Requer no .env:
  CALLMEBOT_PHONE   = seu número com DDI, ex.: +5511999998888
  CALLMEBOT_APIKEY  = a chave recebida

Uso:
  python3 tools/notify_whatsapp.py --message "Nova edição no ar: https://..."
"""

import argparse
import json
import os
import re
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

import requests
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

API = "https://api.callmebot.com/whatsapp.php"


def _repo_de_remote() -> str:
    """Extrai 'owner/repo' do git remote origin (https ou ssh). '' se falhar."""
    try:
        url = subprocess.run(
            ["git", "-C", ROOT, "remote", "get-url", "origin"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""
    # https://github.com/owner/repo(.git)  |  git@github.com:owner/repo(.git)
    m = re.search(r"github\.com[/:]([^/]+)/(.+?)(?:\.git)?/?$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else ""


def public_base() -> str:
    """URL pública do GitHub Pages, robusta a config ausente na nuvem.

    Ordem: NEWSLETTER_PUBLIC_URL → GITHUB_REPO → git remote origin.
    Assim o link sobrevive mesmo quando o ambiente da nuvem não tem o .env.
    """
    base = os.environ.get("NEWSLETTER_PUBLIC_URL", "").strip().rstrip("/")
    if base:
        return base
    repo = os.environ.get("GITHUB_REPO", "").strip() or _repo_de_remote()
    if repo and "/" in repo:
        owner, name = repo.split("/", 1)
        return f"https://{owner}.github.io/{name}"
    return ""


def compor_de_edicao(caminho: str) -> str:
    """Monta a mensagem-resumo a partir de um edition.json."""
    with open(caminho, encoding="utf-8") as fh:
        ed = json.load(fh)

    data = ed.get("data", "")
    try:  # AAAA-MM-DD → DD/MM
        y, m, d = data.split("-")
        data_fmt = f"{d}/{m}"
    except ValueError:
        data_fmt = data

    linhas = [f'📡 {ed.get("titulo", "Radar")} — {data_fmt}']

    # Link logo abaixo do título: o CallMeBot pode truncar mensagens longas,
    # então garantimos que o link fique no topo, onde nunca é cortado.
    base = public_base()
    if base and data:
        linhas.append(f'🔗 {base}/editions/{data}.html')
    elif base:
        linhas.append(f'🔗 {base}')
    else:
        print("AVISO: sem URL pública (NEWSLETTER_PUBLIC_URL/GITHUB_REPO/remote) "
              "— mensagem sairá sem link.", file=sys.stderr)

    # Linha de mercado (dólar, índices) logo abaixo do título.
    merc = ed.get("mercado", [])
    if merc:
        partes = []
        for i in merc:
            pct = i.get("variacao_pct")
            if pct is None:
                partes.append(f'{i.get("nome","")} {i.get("valor","")}')
            else:
                seta = "▲" if pct > 0 else ("▼" if pct < 0 else "•")
                partes.append(f'{i.get("nome","")} {i.get("valor","")} {seta}{abs(pct):.2f}%')
        linhas.append("📊 " + " · ".join(partes))
    linhas.append("")

    if ed.get("manchete", {}).get("titulo"):
        linhas += [f'🔦 {ed["manchete"]["titulo"]}', ""]

    destaques = []
    for sec in ed.get("secoes", []):
        itens = sec.get("itens", [])
        if itens:
            destaques.append(f'• {sec["titulo"]}: {itens[0]["titulo"]}')
    if destaques:
        linhas += ["Nesta edição:"] + destaques

    return "\n".join(linhas).strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Envia mensagem no WhatsApp (CallMeBot).")
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--message", help="Texto livre da mensagem.")
    grupo.add_argument("--edition", help="edition.json — compõe a mensagem-resumo automaticamente.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Só imprime a mensagem, sem enviar.")
    args = parser.parse_args()

    if args.edition:
        try:
            mensagem = compor_de_edicao(args.edition)
        except (OSError, json.JSONDecodeError, KeyError) as exc:
            print(f"ERRO ao compor de {args.edition}: {exc}", file=sys.stderr)
            return 1
    else:
        mensagem = args.message

    if args.dry_run:
        print(mensagem)
        return 0

    phone = os.environ.get("CALLMEBOT_PHONE", "").strip()
    apikey = os.environ.get("CALLMEBOT_APIKEY", "").strip()
    if not phone or not apikey:
        print("ERRO: defina CALLMEBOT_PHONE e CALLMEBOT_APIKEY no .env.", file=sys.stderr)
        return 1

    params = {
        "phone": phone,
        "text": mensagem,
        "apikey": apikey,
    }
    try:
        resp = requests.get(API, params=params, timeout=30)
    except requests.RequestException as exc:
        print(f"ERRO de rede ao enviar WhatsApp: {exc}", file=sys.stderr)
        return 1

    # CallMeBot devolve texto/HTML. 200 normalmente = enfileirado com sucesso.
    if resp.status_code == 200:
        print("Aviso enviado no WhatsApp.")
        return 0
    print(f"ERRO CallMeBot (HTTP {resp.status_code}): {resp.text[:300]}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
