#!/usr/bin/env python3
"""Extrai as falas humanas das sessões recentes do Claude Code.

Antes isso era instrução para o modelo ("navegar em ~/.claude/projects/").
Virou script porque é determinístico e porque o filtro importa muito: num
arquivo de sessão típico, ~92% dos registros marcados `type: user` são
resultados de ferramenta, não fala do Abilio. Sem filtrar, o modelo lê
saída de `ls` achando que é pedido do usuário.

Uso:
    python3 tools/brain_sessions.py                  desde a última captura
    python3 tools/brain_sessions.py --desde 2026-08-01
    python3 tools/brain_sessions.py --tudo           ignora a data de corte
    python3 tools/brain_sessions.py --resumo         só a lista de sessões
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

SPACE = Path(__file__).resolve().parent.parent
ULTIMA_CAPTURA = SPACE / "brain" / "memory" / ".ultima-captura"
PROJETOS = Path.home() / ".claude" / "projects"

MAX_FALAS = 60
MAX_CHARS = 2000
TRECHO_RESPOSTA = 400

# A rotina gera transcrição própria. Sem excluir, a captura seguinte leria o
# próprio raciocínio e "aprenderia" consigo mesma — memória se retroalimentando
# até virar eco. Falha que o desenho antigo não previa.
PROPRIA_ROTINA = re.compile(
    r"brain[- ]?(capturar|curar)|dream|consolida\w* de mem[óo]ria", re.I
)


def texto_do_conteudo(conteudo) -> str:
    if isinstance(conteudo, str):
        return conteudo
    if not isinstance(conteudo, list):
        return ""
    partes = [b.get("text", "") for b in conteudo
              if isinstance(b, dict) and b.get("type") == "text"]
    return "\n".join(p for p in partes if p)


def eh_fala_humana(reg: dict) -> bool:
    """Separa o que o Abilio digitou do que a ferramenta devolveu."""
    if reg.get("type") != "user":
        return False
    if "toolUseResult" in reg:          # eco de ferramenta
        return False
    if reg.get("isMeta"):               # system-reminder e afins
        return False
    if reg.get("isSidechain"):          # subagente, não é o usuário
        return False
    if reg.get("userType") not in (None, "external"):
        return False
    return bool(texto_do_conteudo(reg.get("message", {}).get("content")).strip())


def ler_sessao(caminho: Path) -> dict | None:
    titulo_ai = titulo_custom = None
    falas: list[dict] = []
    respostas: dict[str, str] = {}
    cwd = branch = None
    inicio = fim = None
    ultimo_uuid = None

    for linha in caminho.open(encoding="utf-8", errors="replace"):
        try:
            reg = json.loads(linha)
        except json.JSONDecodeError:
            continue

        tipo = reg.get("type")
        if tipo == "ai-title":
            titulo_ai = reg.get("aiTitle") or titulo_ai
            continue
        if tipo == "custom-title":
            titulo_custom = reg.get("customTitle") or titulo_custom
            continue

        ts = reg.get("timestamp")
        if ts:
            inicio = inicio or ts
            fim = ts

        if eh_fala_humana(reg):
            cwd = cwd or reg.get("cwd")
            branch = branch or reg.get("gitBranch")
            txt = texto_do_conteudo(reg["message"]["content"]).strip()
            ultimo_uuid = reg.get("uuid")
            falas.append({"quando": ts, "texto": txt[:MAX_CHARS], "uuid": ultimo_uuid})
        elif tipo == "assistant" and ultimo_uuid and ultimo_uuid not in respostas:
            # primeira resposta após a fala — dá contexto ao que foi pedido
            txt = texto_do_conteudo(reg.get("message", {}).get("content")).strip()
            if txt:
                respostas[ultimo_uuid] = txt[:TRECHO_RESPOSTA]

    if not falas:
        return None

    for f in falas:
        f["resposta"] = respostas.get(f.pop("uuid"), "")

    return {
        "sessao": caminho.stem,
        "titulo": titulo_custom or titulo_ai or "(sem título)",
        "projeto": caminho.parent.name,
        "cwd": cwd,
        "branch": branch,
        "inicio": inicio,
        "fim": fim,
        "falas": falas[:MAX_FALAS],
        "total_falas": len(falas),
    }


def corte(args) -> date | None:
    if args.tudo:
        return None
    if args.desde:
        return datetime.strptime(args.desde, "%Y-%m-%d").date()
    if ULTIMA_CAPTURA.exists():
        try:
            return datetime.strptime(ULTIMA_CAPTURA.read_text().strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", help="data de corte AAAA-MM-DD")
    ap.add_argument("--tudo", action="store_true")
    ap.add_argument("--resumo", action="store_true")
    args = ap.parse_args()

    if not PROJETOS.is_dir():
        print(f"ERRO: {PROJETOS} não existe", file=sys.stderr)
        return 1

    desde = corte(args)
    sessoes, ignoradas = [], []

    for arq in sorted(PROJETOS.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
        if desde and date.fromtimestamp(arq.stat().st_mtime) < desde:
            continue
        s = ler_sessao(arq)
        if not s:
            continue
        alvo = f"{s['titulo']} {s['falas'][0]['texto'][:200]}"
        if PROPRIA_ROTINA.search(alvo):
            ignoradas.append(s["titulo"])
            continue
        sessoes.append(s)

    if args.resumo:
        print(f"corte: {desde or 'nenhum'} · {len(sessoes)} sessões · "
              f"{len(ignoradas)} ignoradas (própria rotina)\n")
        for s in sessoes:
            print(f"  {(s['inicio'] or '')[:10]}  {s['total_falas']:3} falas  "
                  f"{s['titulo'][:52]:54} {s['projeto'][:30]}")
        for t in ignoradas:
            print(f"  ignorada: {t[:60]}")
        return 0

    print(json.dumps({
        "corte": desde.isoformat() if desde else None,
        "gerado_em": date.today().isoformat(),
        "ignoradas_propria_rotina": ignoradas,
        "sessoes": sessoes,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
