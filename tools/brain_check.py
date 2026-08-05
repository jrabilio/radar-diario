#!/usr/bin/env python3
"""Confere a saúde do brain. Determinístico — sem LLM, roda em milissegundos.

Existe porque o Dream mandava o modelo "remover memórias contraditadas" e
"nunca duplicar", mas nada verificava. Resultado auditado em 04/08/2026:
19 de 40 arquivos sem data, 1 wikilink apontando para arquivo inexistente,
e duas memórias afirmando o oposto sobre o ClickUp por dois meses.

Regra da casa (CLAUDE.md, arquitetura WAT): se dá para escrever um `if`,
é tool — não é trabalho de modelo.

Uso:
    python3 tools/brain_check.py            relatório completo
    python3 tools/brain_check.py --quiet    uma linha (para hook de sessão)
    python3 tools/brain_check.py --json     saída estruturada

Código de saída: 0 = sem erro · 1 = erro · 2 = só avisos
"""
from __future__ import annotations

import argparse
import difflib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

SPACE = Path(__file__).resolve().parent.parent
MEM = SPACE / "brain" / "memory"
INDICE = MEM / "MEMORY.md"
ARQUIVO = MEM / "arquivo"
ULTIMA_CAPTURA = MEM / ".ultima-captura"

TIPOS = {"user", "project", "feedback", "reference"}
STATUS = {"vivo", "arquivo"}
LIMITE_INDICE = 200
DIAS_CAPTURA_ATRASADA = 2
SEMELHANCA_DUPLICATA = 0.82

# Quanto tempo cada tipo de memória sobrevive sem revisão.
VALIDADE_DIAS = {"project": 60, "reference": 90, "user": 180, "feedback": 365}


class Resultado:
    def __init__(self) -> None:
        self.erros: list[str] = []
        self.avisos: list[str] = []
        self.info: dict = {}

    def erro(self, msg: str) -> None:
        self.erros.append(msg)

    def aviso(self, msg: str) -> None:
        self.avisos.append(msg)

    @property
    def codigo(self) -> int:
        return 1 if self.erros else (2 if self.avisos else 0)


def frontmatter(texto: str) -> dict[str, str]:
    if not texto.startswith("---"):
        return {}
    fim = texto.find("\n---", 3)
    if fim == -1:
        return {}
    campos = {}
    for linha in texto[3:fim].splitlines():
        if ":" in linha:
            k, _, v = linha.partition(":")
            campos[k.strip()] = v.strip()
    return campos


def memorias() -> list[Path]:
    vivos = sorted(p for p in MEM.glob("*.md") if p.name != "MEMORY.md")
    arquivados = sorted(ARQUIVO.glob("*.md")) if ARQUIVO.is_dir() else []
    return vivos + arquivados


def rel(p: Path) -> str:
    return str(p.relative_to(MEM))


# ───────────────────────────── verificações ─────────────────────────────


def checar_indice(r: Resultado, arquivos: list[Path]) -> None:
    if not INDICE.exists():
        r.erro("MEMORY.md não existe — o brain não tem índice")
        return
    texto = INDICE.read_text(encoding="utf-8")

    linhas = texto.count("\n") + 1
    r.info["linhas_indice"] = linhas
    if linhas > LIMITE_INDICE:
        r.erro(f"MEMORY.md tem {linhas} linhas (limite {LIMITE_INDICE})")

    citados = {m for m in re.findall(r"\]\(((?:arquivo/)?[^)]+\.md)\)", texto)}
    reais = {rel(p) for p in arquivos}

    for fantasma in sorted(citados - reais):
        r.erro(f"índice aponta para arquivo que não existe: {fantasma}")
    for orfao in sorted(reais - citados):
        r.erro(f"arquivo fora do índice: {orfao}")


def checar_wikilinks(r: Resultado, arquivos: list[Path]) -> None:
    nomes = {p.stem for p in arquivos}
    for p in arquivos:
        for alvo in set(re.findall(r"\[\[([^\]]+)\]\]", p.read_text(encoding="utf-8"))):
            if alvo not in nomes:
                r.erro(f"{rel(p)}: wikilink [[{alvo}]] não resolve")


def checar_frontmatter(r: Resultado, arquivos: list[Path]) -> None:
    faltando_novos = []
    for p in arquivos:
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if not fm:
            r.erro(f"{rel(p)}: sem frontmatter")
            continue
        for campo in ("name", "description", "type"):
            if not fm.get(campo):
                r.erro(f"{rel(p)}: frontmatter sem '{campo}'")
        if fm.get("type") and fm["type"] not in TIPOS:
            r.erro(f"{rel(p)}: type '{fm['type']}' fora de {sorted(TIPOS)}")

        status = fm.get("status")
        if not status:
            faltando_novos.append(rel(p))
        elif status not in STATUS:
            r.erro(f"{rel(p)}: status '{status}' fora de {sorted(STATUS)}")
        else:
            esperado = "arquivo" if p.parent == ARQUIVO else "vivo"
            if status != esperado:
                r.erro(f"{rel(p)}: status '{status}' mas o arquivo está em "
                       f"{'arquivo/' if esperado == 'arquivo' else 'memory/'}")

    if faltando_novos:
        r.aviso(f"{len(faltando_novos)} memórias sem os campos novos "
                f"(status/revisar_em/fonte) — migração pendente")
        r.info["sem_campos_novos"] = faltando_novos


def checar_validade(r: Resultado, arquivos: list[Path]) -> None:
    hoje = date.today()
    vencidas = []
    for p in arquivos:
        if p.parent == ARQUIVO:
            continue  # arquivo não vence, já é histórico
        fm = frontmatter(p.read_text(encoding="utf-8"))
        prazo = fm.get("revisar_em")
        if not prazo:
            continue
        try:
            quando = datetime.strptime(prazo, "%Y-%m-%d").date()
        except ValueError:
            r.erro(f"{rel(p)}: revisar_em '{prazo}' não é uma data AAAA-MM-DD")
            continue
        if quando < hoje:
            vencidas.append((rel(p), (hoje - quando).days))
    if vencidas:
        r.aviso(f"{len(vencidas)} memórias vencidas para revisão")
        r.info["vencidas"] = sorted(vencidas, key=lambda x: -x[1])


def checar_caminhos(r: Resultado, arquivos: list[Path]) -> None:
    """Memória que cita caminho morto é memória que induz ao erro."""
    padrao = re.compile(r"/Users/[A-Za-z0-9_./'\- ]+")
    ignorar = re.compile(r"[\[\]<>*?]|YYYY|AAAA|DD/MM|\.\.\.|nome-|exemplo")
    for p in arquivos:
        for bruto in set(padrao.findall(p.read_text(encoding="utf-8"))):
            caminho = bruto.rstrip(".,;:`)'\" ")
            if ignorar.search(caminho) or len(caminho) < 20:
                continue
            if not Path(caminho).exists():
                r.aviso(f"{rel(p)}: cita caminho que não existe — {caminho}")


def checar_duplicatas(r: Resultado, arquivos: list[Path]) -> None:
    descrs = []
    for p in arquivos:
        d = frontmatter(p.read_text(encoding="utf-8")).get("description", "")
        if d:
            descrs.append((rel(p), d))
    for i, (a, da) in enumerate(descrs):
        for b, db in descrs[i + 1:]:
            razao = difflib.SequenceMatcher(None, da.lower(), db.lower()).ratio()
            if razao >= SEMELHANCA_DUPLICATA:
                r.aviso(f"possível duplicata ({razao:.0%}): {a} ↔ {b}")


def checar_captura(r: Resultado) -> None:
    """O watchdog: denuncia quando a rotina para de rodar."""
    if not ULTIMA_CAPTURA.exists():
        r.aviso("captura nunca rodou (sem .ultima-captura)")
        r.info["dias_sem_captura"] = None
        return
    try:
        quando = datetime.strptime(ULTIMA_CAPTURA.read_text().strip()[:10], "%Y-%m-%d").date()
    except ValueError:
        r.erro(".ultima-captura com conteúdo inválido")
        return
    dias = (date.today() - quando).days
    r.info["dias_sem_captura"] = dias
    if dias > DIAS_CAPTURA_ATRASADA:
        r.aviso(f"captura atrasada — última há {dias} dias")


# ──────────────────────────────── saída ─────────────────────────────────


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quiet", action="store_true", help="uma linha, para hook")
    ap.add_argument("--json", action="store_true", dest="como_json")
    args = ap.parse_args()

    if not MEM.is_dir():
        print(f"ERRO: {MEM} não existe", file=sys.stderr)
        return 1

    r = Resultado()
    arquivos = memorias()
    r.info["memorias_vivas"] = sum(1 for p in arquivos if p.parent == MEM)
    r.info["memorias_arquivadas"] = sum(1 for p in arquivos if p.parent == ARQUIVO)

    checar_indice(r, arquivos)
    checar_wikilinks(r, arquivos)
    checar_frontmatter(r, arquivos)
    checar_validade(r, arquivos)
    checar_caminhos(r, arquivos)
    checar_duplicatas(r, arquivos)
    checar_captura(r)

    if args.como_json:
        print(json.dumps({"erros": r.erros, "avisos": r.avisos,
                          "info": r.info, "codigo": r.codigo},
                         ensure_ascii=False, indent=2))
        return r.codigo

    if args.quiet:
        if not r.erros and not r.avisos:
            return 0
        partes = []
        if r.erros:
            partes.append(f"{len(r.erros)} erro(s)")
        dias = r.info.get("dias_sem_captura")
        if dias is None:
            partes.append("captura nunca rodou")
        elif dias > DIAS_CAPTURA_ATRASADA:
            partes.append(f"captura atrasada ({dias}d)")
        if r.info.get("vencidas"):
            partes.append(f"{len(r.info['vencidas'])} memórias vencidas")
        if r.info.get("sem_campos_novos"):
            partes.append(f"{len(r.info['sem_campos_novos'])} sem migrar")
        icone = "❌" if r.erros else "⚠️"
        print(f"{icone}  brain: {' · '.join(partes)} — rode /brain-capturar")
        return r.codigo

    print(f"BRAIN — {r.info['memorias_vivas']} memórias vivas, "
          f"{r.info['memorias_arquivadas']} arquivadas, "
          f"índice com {r.info.get('linhas_indice', '?')} linhas\n")

    if r.erros:
        print(f"ERROS ({len(r.erros)})")
        for e in r.erros:
            print(f"  ✗ {e}")
        print()
    if r.avisos:
        print(f"AVISOS ({len(r.avisos)})")
        for a in r.avisos:
            print(f"  ! {a}")
        print()
    if vencidas := r.info.get("vencidas"):
        print("VENCIDAS PARA REVISÃO")
        for nome, dias in vencidas:
            print(f"  {dias:4}d  {nome}")
        print()
    if not r.erros and not r.avisos:
        print("✓ tudo em ordem")

    return r.codigo


if __name__ == "__main__":
    raise SystemExit(main())
