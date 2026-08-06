#!/usr/bin/env python3
"""Espelha o brain/ no Google Drive. Só de ida: a máquina é a verdade.

O Abilio não edita nada no Drive — ali é repositório, só o Claude ajusta.
Por isso o sync propaga exclusão: sumiu na máquina, some no Drive.

A trava de segurança existe porque essa mesma propagação é perigosa: um brain
local corrompido ou meio-copiado destruiria o backup justamente quando ele
deveria salvar. Já aconteceu algo do gênero nesta máquina — em 04/08/2026 uma
cópia do Desktop (que fica no iCloud) estourou o timeout e gravou um arquivo
truncado de 0 byte.

Uso:
    python3 tools/brain_sync_drive.py --dry-run
    python3 tools/brain_sync_drive.py
    python3 tools/brain_sync_drive.py --force     # ignora a trava
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

SPACE = Path(__file__).resolve().parent.parent
BRAIN = SPACE / "brain"
CHECK = SPACE / "tools" / "brain_check.py"
load_dotenv(SPACE / ".env")

# Fica no .env, não aqui: este repositório é público e a conta é um e-mail pessoal.
CONTA = os.environ.get("BRAIN_DRIVE_CONTA", "")
NUVEM = Path.home() / "Library" / "CloudStorage"
PASTA_ESPELHO = "00. CLAUDE BRAIN"

PISO_ARQUIVOS = 30          # abaixo disso o brain local está quebrado
TETO_EXCLUSAO = 0.30        # apagar mais que isso do Drive exige --force
# _ESTADO.md só existe no destino. Sem excluí-lo, o --delete o apaga a cada
# rodada e ele reaparece — churn inútil que ainda inflava a contagem de
# exclusões contra a trava de segurança.
EXCLUIR = [".DS_Store", "__pycache__/", "*.pyc", "_ESTADO.md"]


def destino() -> Path | None:
    """Localiza a raiz do Drive da conta certa. Nunca cai em outra conta.

    `BRAIN_DRIVE_DEST` força um destino — serve para testar a trava e a
    propagação de exclusão sem mexer no Drive de verdade.
    """
    forcado = os.environ.get("BRAIN_DRIVE_DEST")
    if forcado:
        return Path(forcado)
    if not CONTA:
        return None
    alvo = NUVEM / f"GoogleDrive-{CONTA}"
    if not alvo.is_dir():
        return None
    for nome in ("Meu Drive", "My Drive"):
        raiz = alvo / nome
        if raiz.is_dir():
            return raiz / PASTA_ESPELHO
    return None


def contas_disponiveis() -> list[str]:
    if not NUVEM.is_dir():
        return []
    return [p.name for p in NUVEM.iterdir() if p.name.startswith("GoogleDrive-")]


def saude() -> dict:
    try:
        r = subprocess.run([sys.executable, str(CHECK), "--json"],
                           capture_output=True, text=True, cwd=SPACE, timeout=60)
        return json.loads(r.stdout)
    except Exception as e:  # o backup não depende do check
        return {"erros": [f"brain_check não rodou: {e}"], "avisos": [], "info": {}}


def rsync(origem: Path, alvo: Path, dry: bool) -> list[str]:
    cmd = ["rsync", "-a", "--delete", "--itemize-changes"]
    for e in EXCLUIR:
        cmd += ["--exclude", e]
    if dry:
        cmd.append("--dry-run")
    cmd += [f"{origem}/", f"{alvo}/"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"ERRO no rsync:\n{r.stderr}", file=sys.stderr)
        raise SystemExit(1)
    return [l for l in r.stdout.splitlines() if l.strip()]


def separa(linhas: list[str]) -> tuple[list[str], list[str]]:
    apagar = [l.split(None, 1)[1] for l in linhas if l.startswith("*deleting")]
    mudar = [l.split(None, 1)[1] for l in linhas
             if not l.startswith("*deleting") and not l.startswith(".")]
    return mudar, apagar


def mais_novos_no_drive(origem: Path, alvo: Path) -> list[str]:
    """Ele não edita lá — se algo é mais novo no Drive, é sinal de problema."""
    achados = []
    for d in alvo.rglob("*"):
        if not d.is_file() or d.name.startswith("_ESTADO"):
            continue
        rel = d.relative_to(alvo)
        o = origem / rel
        if o.is_file() and d.stat().st_mtime > o.stat().st_mtime + 2:
            achados.append(str(rel))
    return achados


def conta_por_pasta(raiz: Path) -> dict[str, int]:
    fora = {}
    for p in sorted(raiz.iterdir()):
        if p.is_dir():
            fora[p.name] = sum(1 for x in p.rglob("*") if x.is_file())
    fora["(raiz)"] = sum(1 for x in raiz.iterdir() if x.is_file())
    return fora


def escreve_estado(alvo: Path, s: dict, mudados: int, apagados: int) -> None:
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    linhas = [
        "# Espelho do BRAIN — NÃO EDITE AQUI",
        "",
        "> Esta pasta é um **espelho de ida**. A verdade mora no Mac, em",
        "> `~/Projetos/ABILIO'S SPACE/brain/`. Qualquer coisa editada aqui é",
        "> **sobrescrita no próximo sync**, e uma exclusão feita lá apaga aqui.",
        "",
        f"**Última sincronia:** {agora}",
        f"**Nesta rodada:** {mudados} arquivo(s) atualizado(s), {apagados} removido(s)",
        "",
        "## Saúde do brain na origem",
        "",
    ]
    erros, avisos = s.get("erros", []), s.get("avisos", [])
    if erros:
        linhas.append(f"❌ **{len(erros)} erro(s)** — o backup foi feito assim mesmo, "
                      "mas a origem precisa de conserto:")
        linhas += [f"- {e}" for e in erros]
    elif avisos:
        linhas.append(f"⚠️ {len(avisos)} aviso(s), nenhum erro:")
        linhas += [f"- {a}" for a in avisos]
    else:
        linhas.append("✅ sem erros nem avisos")

    info = s.get("info", {})
    if info:
        linhas += ["", "## Conteúdo", "",
                   f"- memórias vivas: {info.get('memorias_vivas', '?')}",
                   f"- memórias arquivadas: {info.get('memorias_arquivadas', '?')}"]
        dias = info.get("dias_sem_captura")
        if dias is not None:
            linhas.append(f"- dias desde a última captura: {dias}")

    linhas += ["", "---", "*Gerado por `tools/brain_sync_drive.py`.*"]
    (alvo / "_ESTADO.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="ignora a trava de segurança")
    args = ap.parse_args()

    if not BRAIN.is_dir():
        print(f"ERRO: {BRAIN} não existe", file=sys.stderr)
        return 1

    alvo = destino()
    if alvo is None:
        if not CONTA:
            print("ERRO: BRAIN_DRIVE_CONTA não está definida.\n", file=sys.stderr)
            print("Defina no .env da raiz do SPACE a conta Google cujo Drive espelha o\n"
                  "brain, por exemplo:  BRAIN_DRIVE_CONTA=voce@exemplo.com\n"
                  "(fica no .env, e não no código, porque este repositório é público)",
                  file=sys.stderr)
            disp = contas_disponiveis()
            print("\nContas montadas hoje: " + (", ".join(disp) if disp else "nenhuma"),
                  file=sys.stderr)
            return 2
        print(f"ERRO: a conta {CONTA} não está montada no Google Drive.\n", file=sys.stderr)
        disp = contas_disponiveis()
        print("Contas montadas hoje: " + (", ".join(disp) if disp else "nenhuma"), file=sys.stderr)
        print("\nPara resolver: abra o app Google Drive → ícone de engrenagem →\n"
              "'Adicionar outra conta' → entre com " + CONTA + ".\n"
              "A pasta aparece em ~/Library/CloudStorage/ e o sync passa a funcionar.",
              file=sys.stderr)
        return 2

    # Conta só o que o rsync de fato leva: incluir os arquivos de EXCLUIR aqui
    # fazia a conferência final acusar diferença a cada rodada — alarme falso que
    # ensina a ignorar o aviso justamente quando ele for verdadeiro.
    _ignorados = {".DS_Store", "_ESTADO.md"}
    locais = sum(1 for p in BRAIN.rglob("*")
                 if p.is_file()
                 and p.name not in _ignorados
                 and "__pycache__" not in p.parts
                 and p.suffix != ".pyc")
    print(f"origem : {BRAIN}  ({locais} arquivos)")
    print(f"destino: {alvo}\n")

    if locais < PISO_ARQUIVOS and not args.force:
        print(f"RECUSADO: o brain local tem só {locais} arquivos (piso: {PISO_ARQUIVOS}).\n"
              "Isso parece brain quebrado, não brain enxuto — sincronizar agora\n"
              "destruiria o backup. Confira a origem, ou use --force se for intencional.",
              file=sys.stderr)
        return 1

    novo = not alvo.exists()
    if novo:
        print("espelho ainda não existe — será criado")
        if not args.dry_run:
            alvo.mkdir(parents=True, exist_ok=True)
    else:
        divergentes = mais_novos_no_drive(BRAIN, alvo)
        if divergentes:
            print(f"⚠️  {len(divergentes)} arquivo(s) mais novo(s) no Drive que na máquina.")
            print("   Você não deveria editar lá — isso sugere outro dispositivo ou sync mal resolvido.")
            print("   Serão sobrescritos:")
            for d in divergentes[:10]:
                print(f"     {d}")
            if len(divergentes) > 10:
                print(f"     ... e mais {len(divergentes) - 10}")
            print()

    if not args.dry_run and not alvo.exists():
        alvo.mkdir(parents=True, exist_ok=True)

    previa = rsync(BRAIN, alvo if alvo.exists() else alvo, dry=True) if alvo.exists() else []
    mudar, apagar = separa(previa)

    if apagar and not novo and not args.force:
        no_drive = sum(1 for p in alvo.rglob("*") if p.is_file())
        if no_drive and len(apagar) / no_drive > TETO_EXCLUSAO:
            pct = len(apagar) * 100 // no_drive
            print(f"RECUSADO: o sync apagaria {len(apagar)} de {no_drive} arquivos "
                  f"do Drive ({pct}%).\n"
                  f"Acima do teto de {int(TETO_EXCLUSAO * 100)}%. Se a remoção for "
                  "intencional (ex.: aposentar uma pasta),\nrode de novo com --force.",
                  file=sys.stderr)
            return 1

    print(f"a atualizar: {len(mudar)} · a remover: {len(apagar)}")
    for m in mudar[:15]:
        print(f"  + {m}")
    if len(mudar) > 15:
        print(f"  ... e mais {len(mudar) - 15}")
    for a in apagar[:10]:
        print(f"  - {a}")
    if len(apagar) > 10:
        print(f"  ... e mais {len(apagar) - 10}")

    if args.dry_run:
        print("\n(dry-run — nada foi escrito)")
        return 0

    rsync(BRAIN, alvo, dry=False)
    escreve_estado(alvo, saude(), len(mudar), len(apagar))

    destino_arquivos = sum(1 for p in alvo.rglob("*") if p.is_file()) - 1  # menos _ESTADO.md
    print(f"\n✅ espelhado: {destino_arquivos} arquivos no Drive")
    if destino_arquivos != locais:
        print(f"⚠️  origem tem {locais} — diferença de {abs(destino_arquivos - locais)}, "
              "confira as exclusões")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
