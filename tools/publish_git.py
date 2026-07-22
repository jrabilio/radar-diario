#!/usr/bin/env python3
"""
publish_git.py — Publica o repositório (raiz) no GitHub Pages (Layer 3 / WAT).

O projeto inteiro é o repositório `radar-diario`. A pasta docs/ é a raiz do site
(GitHub Pages serve de /docs). Este script faz commit e push do que mudou.
Segredos (.env) e arquivos temporários ficam de fora via .gitignore.

Requer no .env:
  GITHUB_REPO   = usuario/nome-do-repo
  GITHUB_TOKEN  = token com permissão de escrita no repositório

Uso:
  python3 tools/publish_git.py --data 2026-07-21
  python3 tools/publish_git.py --data 2026-07-21 --dry-run   # commit local, sem push
"""

import argparse
import os
import subprocess
import sys

from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
load_dotenv(os.path.join(ROOT, ".env"))


def git(*args, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", ROOT, *args],
                          capture_output=True, text=True, check=check)


def ensure_repo():
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        git("init"); git("branch", "-M", "main")
    if not git("config", "user.email", check=False).stdout.strip():
        git("config", "user.email", "newsletter-bot@local")
        git("config", "user.name", "Newsletter Bot")
    os.makedirs(DOCS, exist_ok=True)
    nojekyll = os.path.join(DOCS, ".nojekyll")
    if not os.path.exists(nojekyll):
        open(nojekyll, "w").close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Publica o repositório no GitHub Pages.")
    parser.add_argument("--data", required=True, help="Data da edição (mensagem de commit).")
    parser.add_argument("--dry-run", action="store_true", help="Commita local, sem push.")
    args = parser.parse_args()

    ensure_repo()
    git("add", "-A")
    if not git("status", "--porcelain").stdout.strip():
        print("Nada novo para publicar.")
        return 0
    git("commit", "-m", f"Edição {args.data}")
    print(f"Commit criado para a edição {args.data}.")

    if args.dry_run:
        print("--dry-run: push pulado.")
        return 0

    repo = os.environ.get("GITHUB_REPO", "").strip()
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not repo or not token:
        print("ERRO: defina GITHUB_REPO e GITHUB_TOKEN no .env.", file=sys.stderr)
        return 1

    remote = f"https://x-access-token:{token}@github.com/{repo}.git"
    if git("remote", "get-url", "origin", check=False).returncode == 0:
        git("remote", "set-url", "origin", remote)
    else:
        git("remote", "add", "origin", remote)

    push = git("push", "-u", "origin", "main", check=False)
    if push.returncode != 0:
        print(f"ERRO no push:\n{push.stderr.replace(token, '***')}", file=sys.stderr)
        return 1

    public = os.environ.get("NEWSLETTER_PUBLIC_URL", f"https://github.com/{repo}")
    print(f"Publicado! {public}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
