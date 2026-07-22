#!/usr/bin/env python3
"""
setup_github.py — Cria o repositório, dá push e ativa o GitHub Pages (Layer 3 / WAT).

Idempotente: pode rodar de novo sem quebrar (reaproveita repo/Pages existentes).
Lê GITHUB_TOKEN do .env. Descobre o usuário pelo token, cria o repo público
(default: 'radar-diario'), publica a pasta site/ e ativa o Pages na branch main (raiz).
Ao final, grava GITHUB_REPO e NEWSLETTER_PUBLIC_URL no .env.

Uso:
  python3 tools/setup_github.py [--nome radar-diario]
"""

import argparse
import os
import subprocess
import sys
import warnings

warnings.filterwarnings("ignore")

import requests
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
ENV = os.path.join(ROOT, ".env")
load_dotenv(ENV)

API = "https://api.github.com"


def gh(method: str, path: str, token: str, **kw):
    headers = {"Authorization": f"Bearer {token}",
               "Accept": "application/vnd.github+json",
               "X-GitHub-Api-Version": "2022-11-28"}
    return requests.request(method, f"{API}{path}", headers=headers, timeout=30, **kw)


def git(*args, check=True):
    return subprocess.run(["git", "-C", SITE, *args],
                          capture_output=True, text=True, check=check)


def set_env_var(chave: str, valor: str) -> None:
    """Atualiza (ou adiciona) uma variável no .env, preservando o resto."""
    linhas, achou = [], False
    if os.path.exists(ENV):
        with open(ENV, encoding="utf-8") as fh:
            linhas = fh.read().splitlines()
    for i, ln in enumerate(linhas):
        if ln.strip().startswith(f"{chave}="):
            linhas[i] = f"{chave}={valor}"
            achou = True
            break
    if not achou:
        linhas.append(f"{chave}={valor}")
    with open(ENV, "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria repo + Pages e publica site/.")
    parser.add_argument("--nome", help="Nome do repositório (default: GITHUB_REPO ou 'radar-diario').")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("ERRO: preencha GITHUB_TOKEN no .env (token com escopo 'repo').", file=sys.stderr)
        return 1

    # 1) Usuário dono do token
    r = gh("GET", "/user", token)
    if r.status_code != 200:
        print(f"ERRO: token inválido? (HTTP {r.status_code}) {r.text[:200]}", file=sys.stderr)
        return 1
    user = r.json()["login"]

    repo_cfg = (args.nome or os.environ.get("GITHUB_REPO", "") or "radar-diario").strip()
    nome = repo_cfg.split("/")[-1]  # aceita 'owner/nome' ou só 'nome'
    full = f"{user}/{nome}"
    print(f"Usuário: {user} | Repositório: {full}")

    # 2) Cria o repo (público; Pages grátis exige público). Se já existir, segue.
    r = gh("GET", f"/repos/{full}", token)
    if r.status_code == 404:
        r = gh("POST", "/user/repos", token, json={
            "name": nome, "private": False, "auto_init": False,
            "description": "Radar Diário — briefing automático gerado pela automação."})
        if r.status_code not in (201,):
            print(f"ERRO ao criar repo (HTTP {r.status_code}): {r.text[:300]}", file=sys.stderr)
            return 1
        print("Repositório criado.")
    else:
        print("Repositório já existe — reaproveitando.")

    # 3) Push da pasta site/
    if not os.path.isdir(os.path.join(SITE, ".git")):
        git("init"); git("branch", "-M", "main")
    if not git("config", "user.email", check=False).stdout.strip():
        git("config", "user.email", "newsletter-bot@local")
        git("config", "user.name", "Newsletter Bot")
    if not os.path.exists(os.path.join(SITE, ".nojekyll")):
        open(os.path.join(SITE, ".nojekyll"), "w").close()
    git("add", "-A")
    if git("status", "--porcelain").stdout.strip():
        git("commit", "-m", "Publicação inicial")
    remote = f"https://x-access-token:{token}@github.com/{full}.git"
    if git("remote", "get-url", "origin", check=False).returncode == 0:
        git("remote", "set-url", "origin", remote)
    else:
        git("remote", "add", "origin", remote)
    push = git("push", "-u", "origin", "main", check=False)
    if push.returncode != 0:
        print(f"ERRO no push:\n{push.stderr.replace(token, '***')}", file=sys.stderr)
        return 1
    print("Push concluído.")

    # 4) Ativa o Pages (branch main, raiz). 409 = já ativado.
    r = gh("POST", f"/repos/{full}/pages", token,
           json={"source": {"branch": "main", "path": "/"}})
    if r.status_code in (201, 202):
        print("GitHub Pages ativado.")
    elif r.status_code == 409:
        print("GitHub Pages já estava ativado.")
    else:
        print(f"AVISO: não consegui ativar o Pages via API (HTTP {r.status_code}). "
              f"Ative manualmente em Settings > Pages (branch main, /root).", file=sys.stderr)

    public_url = f"https://{user}.github.io/{nome}"
    set_env_var("GITHUB_REPO", full)
    set_env_var("NEWSLETTER_PUBLIC_URL", public_url)
    print(f"\n.env atualizado:\n  GITHUB_REPO={full}\n  NEWSLETTER_PUBLIC_URL={public_url}")
    print(f"\nEm ~1 min o site estará no ar em: {public_url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
