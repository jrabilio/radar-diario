#!/usr/bin/env python3
"""Gera uma ficha .md por empresa em brain/clientes/, cruzando:

  1. brain/dados-ntics/faturamento_ntics_2020_2025.md
     - Tabela de aportes por cliente x ano (2020-2025)
     - Tabelas de pipeline por ano (produto, AE, tipo, resultado)
  2. brain/dados-ntics/SALIC_2026_INDICE_COMPLETO.json
     - Volume de patrocínio público declarado (base 2024+2025)

Regras de negócio aplicadas (de brain/institucional/PIPELINE_NTICS_V2.md):
  REGRA #0 — nunca inventar. Sem dado, escrever "não localizado".
  REGRA #1 — AE "Externo - Incentiv" é plataforma CONCORRENTE, não receita NTICS.
  Cota mínima NTICS por projeto: R$ 250.000.

Uso:  python3 tools/gerar_fichas_clientes.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

SPACE = Path(__file__).resolve().parent.parent
BRAIN = SPACE / "brain"
FATURAMENTO = BRAIN / "dados-ntics" / "faturamento_ntics_2020_2025.md"
SALIC = BRAIN / "dados-ntics" / "SALIC_2026_INDICE_COMPLETO.json"
SAIDA = BRAIN / "clientes"

COTA_MINIMA = 250_000.0
ANOS = ["2020", "2021", "2022", "2023", "2024", "2025"]
CONCORRENTE = "externo - incentiv"

# Um termo que aparece em mais empresas que isso não identifica ninguém.
# "brasil" e "banco" batem em centenas — casar por eles agrega o índice inteiro.
TETO_TERMO_GENERICO = 40
# Acima disso, "mesmo grupo" deixa de ser afirmável.
TETO_ENTIDADES_GRUPO = 6

# Nomes que aparecem escritos de formas diferentes entre as abas da planilha.
# chave = forma normalizada encontrada; valor = nome canônico da empresa.
ALIASES = {
    "nu bank": "Nubank",
    "nubank": "Nubank",
    "whirlpool sa": "Whirlpool",
    "whirlpool": "Whirlpool",
    "aster maquinas": "Áster Máquinas",
    "cnh case": "CNH",
    "cnh new holand": "CNH",
    "cnh": "CNH",
    "comin new holand": "Comin — New Holland",
    "dall oglio new holand": "Dall'Oglio — New Holland",
    "cosan mobil": "Cosan / Mobil",
    "mobil": "Cosan / Mobil",
    "btg pactual mobiauto": "BTG Pactual | Mobiauto",
    "gru aeroporto": "GRU Aeroporto",
    "peroxidos": "Peróxidos",
    "peroxidos do brasil": "Peróxidos",
    "ctg brasil": "CTG Brasil",
    # Grafias divergentes entre as abas da planilha — mesma empresa.
    "robobank": "Rabobank",          # typo na aba de pipeline
    "whirlpopol": "Whirlpool",       # typo na aba de pipeline
    "copergas": "Copergás",
    "m dias": "M Dias Branco",
    "m dias branco": "M Dias Branco",
    "porto de itapoa": "Porto de Itapoá",
    "statkraft": "StatKraft",
    "wilson sons": "Wilson & Sons",
    "wilson e sons": "Wilson & Sons",
    "aksel": "Aksell Química",
    "aksell quimica": "Aksell Química",
    "jaepel": "Jaepel Papeis",
    "jaepel papeis": "Jaepel Papeis",
}

# Linhas da planilha que não são empresa (iniciativas internas, totalizadores).
NAO_EMPRESA = {
    "captacao agem", "captacao cepe", "captacao komedi", "captacao orquestra",
    "venda realizada", "total geral", "total", "empresa", "clientes renovacao",
    "prospects quentes", "no header", "plano de acao do mes",
}


def norm(t: str) -> str:
    """Normalização usada também na busca do índice SALIC (REGRA #2)."""
    t = t.lower()
    t = unicodedata.normalize("NFKD", t).encode("ASCII", "ignore").decode("ASCII")
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())


def slug(nome: str) -> str:
    s = norm(nome).replace(" ", "-")
    return re.sub(r"-+", "-", s).strip("-")


def canonico(bruto: str) -> str:
    """Resolve o nome da empresa para a forma canônica."""
    limpo = bruto.strip()
    limpo = re.sub(r"\s*\bTotal\b\s*$", "", limpo, flags=re.I)
    limpo = limpo.replace("\\|", "|").strip()
    n = norm(limpo)
    if n in NAO_EMPRESA or n.startswith("captacao "):
        return ""
    if n in ALIASES:
        return ALIASES[n]
    return limpo


def moeda(v: str) -> float | None:
    """'R$ 1.234,56' -> 1234.56 ; vazio -> None."""
    v = v.strip()
    if not v or v in {"-", "—"}:
        return None
    v = v.replace("R$", "").replace("\xa0", "").strip()
    v = v.replace(".", "").replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return None


def brl(v: float | None) -> str:
    if v is None:
        return "não localizado"
    return f"R$ {v:,.2f}".replace(",", "@").replace(".", ",").replace("@", ".")


ESCAPE = "\x00PIPE\x00"


def celulas(linha: str) -> list[str]:
    """Divide uma linha de tabela markdown em células.

    O `\\|` escapado faz parte do texto da célula (ex.: "BTG Pactual \\| Mobiauto")
    e não pode ser tratado como separador.
    """
    if not linha.startswith("|"):
        return []
    linha = linha.replace("\\|", ESCAPE)
    partes = linha.split("|")[1:-1] if linha.rstrip().endswith("|") else linha.split("|")[1:]
    return [p.replace(ESCAPE, "|").strip() for p in partes]


def eh_separador(linha: str) -> bool:
    return bool(re.match(r"^\|[\s:|-]+\|?\s*$", linha))


# ─────────────────────────────── parsing ────────────────────────────────


def ler_aportes(linhas: list[str]) -> dict[str, dict]:
    """Tabela 1: aportes por cliente x ano. Termina no primeiro cabeçalho novo."""
    empresas: dict[str, dict] = {}
    for linha in linhas[2:]:
        if not linha.startswith("|") or eh_separador(linha):
            if empresas:
                break
            continue
        c = celulas(linha)
        if len(c) < 9 or not c[0]:
            break
        nome = canonico(c[0])
        if not nome or norm(nome) in {"total geral", ""}:
            continue
        reg = empresas.setdefault(nome, {"aportes": {}, "total": None})
        for i, ano in enumerate(ANOS):
            v = moeda(c[2 + i])
            if v:
                reg["aportes"][ano] = reg["aportes"].get(ano, 0.0) + v
        t = moeda(c[8])
        if t is not None:
            reg["total"] = (reg["total"] or 0.0) + t
    return empresas


def ler_pipelines(linhas: list[str]) -> dict[str, list[dict]]:
    """Todas as abas de pipeline: cabeçalho com 'Empresa' e 'Tipo'."""
    negocios: dict[str, list[dict]] = {}
    i = 0
    while i < len(linhas):
        c = celulas(linhas[i])
        if len(c) >= 5 and norm(c[0]) == "empresa" and norm(c[1]) == "tipo":
            cols = [norm(x) for x in c]
            i += 1
            if i < len(linhas) and eh_separador(linhas[i]):
                i += 1
            while i < len(linhas) and linhas[i].startswith("|"):
                if eh_separador(linhas[i]):
                    i += 1
                    continue
                d = celulas(linhas[i])
                if not d or not d[0] or len(d) < 4:
                    break
                if norm(d[0]) in {"venda realizada", "empresa", "total"}:
                    i += 1
                    continue
                nome = canonico(d[0])
                if not nome:
                    i += 1
                    continue

                def pega(*nomes: str) -> str:
                    for alvo in nomes:
                        if alvo in cols:
                            k = cols.index(alvo)
                            if k < len(d):
                                return d[k].strip()
                    return ""

                valor = None
                for campo in ("aporte 2024", "aporte 2025", "contratos fechados",
                              "previsao aporte", "previsao faturamento"):
                    valor = moeda(pega(campo))
                    if valor:
                        break

                negocios.setdefault(nome, []).append({
                    "tipo": pega("tipo"),
                    "produto": pega("produto interesse"),
                    "valor": valor,
                    "ano": pega("ano de fechamento"),
                    "ae": pega("ae"),
                    "renovacao": pega("percentual de renovacao"),
                    "resultado": pega("resultado final", "forma pgto"),
                })
                i += 1
            continue
        i += 1
    return negocios


# Razões sociais no SALIC que não são dedutíveis do nome comercial.
# Só entram aqui casamentos CONFERIDOS à mão.
SALIC_ALIAS = {
    "Nubank": "nu financeira s a sociedade de credito financiamento e investimento",
}

# Só formas jurídicas e conectivos. Palavras de setor ("saneamento", "agro",
# "mineracao") NÃO entram: são justamente o que distingue "Agro Amazônia" de
# "Amazônia Máquinas" e "J Mendes - Ferro" de "Genésio Mendes".
STOP_TOKEN = {
    "ltda", "sa", "cia", "eireli", "epp", "s", "a", "do", "da", "de", "dos", "das",
    "e", "em", "para", "grupo", "participacoes", "holding",
}


def buscar_salic(nome: str, indice: dict, palavras: dict) -> tuple[dict | None, str, str]:
    """Retorna (entrada, como_encontrou, confianca).

    confianca ∈ {ALTA, MEDIA, BAIXA, —}. REGRA #0: casamento duvidoso é marcado
    como duvidoso, não apresentado como fato.
    """
    n = norm(nome)

    if nome in SALIC_ALIAS:
        chave = SALIC_ALIAS[nome]
        if chave in indice:
            return indice[chave], "razão social conferida à mão", "ALTA"

    if n in indice:
        return indice[n], "nome idêntico no índice", "ALTA"

    for sufixo in (" sa", " s a", " ltda", " do brasil", " brasil", " s a brasil"):
        if n + sufixo in indice:
            return indice[n + sufixo], f"nome + '{sufixo.strip()}'", "ALTA"

    # Siglas curtas (CTG, GRU, BT, RCI) costumam ser o nome da empresa — não
    # filtrar por tamanho, senão sobra só a palavra genérica ("brasil", "banco")
    # e o casamento agrega o índice inteiro.
    tokens = [t for t in n.split() if len(t) > 1 and t not in STOP_TOKEN]
    if not tokens:
        return None, "nome sem token distintivo para buscar", "—"

    com_hits = [(t, palavras.get(t, [])) for t in tokens]
    com_hits = [(t, h) for t, h in com_hits if h]
    if not com_hits:
        return None, f"nenhum termo ({', '.join(tokens)}) existe no índice", "—"

    token, cands = min(com_hits, key=lambda th: len(th[1]))

    # Se nem o termo mais raro do nome é raro, o nome não tem nada que
    # identifique a empresa neste índice. "CTG Brasil" sem 'ctg' vira 'brasil'.
    if len(cands) > TETO_TERMO_GENERICO:
        ausentes = [t for t in tokens if not palavras.get(t)]
        return None, (f"o termo mais raro do nome ('{token}') aparece em {len(cands)} empresas — "
                      f"genérico demais para casar"
                      + (f"; o que identificaria ({', '.join(ausentes)}) não está no índice"
                         if ausentes else "")), "—"

    # Exige TODOS os termos do nome na razão social candidata.
    # Casar por um termo só produz erro grosseiro ("M Dias Branco" → "Dias Pastorinho").
    completos = [c for c in cands if all(t in c.split() for t in tokens)]

    if not completos:
        return None, (f"'{token}' existe no índice, mas nenhuma razão social contém "
                      f"todos os termos ({', '.join(tokens)}) — casar assim daria empresa errada"), "—"

    if len(completos) == 1:
        return indice[completos[0]], f"razão social contém '{' + '.join(tokens)}'", "MEDIA"

    if len(completos) > TETO_ENTIDADES_GRUPO:
        return None, (f"{len(completos)} razões sociais distintas contêm '{' + '.join(tokens)}' — "
                      f"não dá para afirmar que são o mesmo grupo"), "—"

    # Poucas entidades jurídicas do mesmo grupo: somar, não escolher uma.
    return _agregar(completos, indice, tokens), \
        f"{len(completos)} entidades do grupo somadas", "MEDIA"


def _agregar(chaves: list[str], indice: dict, tokens: list[str]) -> dict:
    """Consolida várias razões sociais do mesmo grupo numa entrada só."""
    entradas = [indice[k] for k in chaves]
    ufs: dict[str, dict] = {}
    for e in entradas:
        for uf, d in e.get("distribuicao_uf", {}).items():
            alvo = ufs.setdefault(uf, {"projetos": 0, "valor": 0.0})
            alvo["projetos"] += d.get("projetos", 0)
            alvo["valor"] += d.get("valor", 0.0)
    projetos: list[dict] = []
    for e in entradas:
        projetos.extend(e.get("exemplos_projetos", []))
    projetos.sort(key=lambda p: p.get("valor") or 0, reverse=True)
    return {
        "nome_original": " + ".join(e.get("nome_original", "?") for e in entradas),
        "total_projetos": sum(e.get("total_projetos", 0) for e in entradas),
        "valor_total": sum(e.get("valor_total", 0.0) for e in entradas),
        "distribuicao_uf": ufs,
        "exemplos_projetos": projetos,
        "_entidades": [e.get("nome_original", "?") for e in entradas],
    }


# ─────────────────────────────── ficha ──────────────────────────────────


def montar_ficha(nome: str, dados: dict, hoje: str) -> str:
    aportes = dados.get("aportes", {})
    total_ntics = dados.get("total")
    negocios = dados.get("negocios", [])
    salic, como, conf = dados.get("salic", (None, "", "—"))

    via_concorrente = [d for d in negocios if norm(d.get("ae", "")) == CONCORRENTE]
    proprios = [d for d in negocios if norm(d.get("ae", "")) != CONCORRENTE]
    anos_com_aporte = sorted(a for a, v in aportes.items() if v)
    aes = sorted({d["ae"] for d in proprios if d["ae"]})
    produtos = sorted({d["produto"] for d in proprios if d["produto"]})

    if total_ntics and total_ntics > 0:
        status = "Cliente" if len(anos_com_aporte) > 1 else "Cliente — ciclo único"
    elif via_concorrente:
        status = "⚠️ Prospect — aporte histórico foi via Incentiv (concorrente), não NTICS"
    else:
        status = "Prospect — sem aporte NTICS registrado"

    L = [
        f"# {nome}",
        "",
        f"**Ano-base:** 2026  ",
        f"**Status:** {status}  ",
        f"**Última atualização:** {hoje} (gerado por `tools/gerar_fichas_clientes.py`)",
        "",
        "---",
        "",
        "## Relação com a NTICS",
        "",
        "| Campo | Valor |",
        "|---|---|",
        f"| Total aportado 2020-2025 (NTICS direta) | {brl(total_ntics)} |",
        f"| Anos com aporte | {', '.join(anos_com_aporte) if anos_com_aporte else 'nenhum'} |",
        f"| AE responsável | {', '.join(aes) if aes else 'não localizado'} |",
        f"| Produtos negociados | {', '.join(produtos) if produtos else 'não localizado'} |",
        "",
    ]

    if anos_com_aporte:
        L += ["### Aportes por ano", "",
              "| Ano | Valor |", "|---|---|"]
        L += [f"| {a} | {brl(aportes[a])} |" for a in anos_com_aporte]
        L += [f"| **Total** | **{brl(total_ntics)}** |", ""]

    if via_concorrente:
        L += [
            "### ⚠️ Atenção — aporte via plataforma concorrente",
            "",
            "Registros com AE **\"Externo - Incentiv\"**. Pela REGRA #1 do `PIPELINE_NTICS_V2.md`,",
            "a Incentiv é plataforma concorrente — isso **não é receita NTICS** e não caracteriza",
            "a empresa como cliente NTICS.",
            "",
            "| Ano | Produto | Valor | Resultado |",
            "|---|---|---|---|",
        ]
        L += [f"| {d['ano'] or '—'} | {d['produto'] or '—'} | {brl(d['valor'])} | {d['resultado'] or '—'} |"
              for d in via_concorrente]
        L.append("")

    if proprios:
        L += ["### Histórico comercial (pipeline NTICS)", "",
              "| Ano | Tipo | Produto | Valor | AE | Resultado |", "|---|---|---|---|---|---|"]
        for d in sorted(proprios, key=lambda x: x["ano"] or ""):
            L.append(f"| {d['ano'] or '—'} | {d['tipo'] or '—'} | {d['produto'] or '—'} | "
                     f"{brl(d['valor'])} | {d['ae'] or '—'} | {d['resultado'] or '—'} |")
        L.append("")

    L += ["---", "", "## Capacidade de investimento — SALIC 2024+2025", ""]
    if salic:
        vol = salic.get("valor_total", 0.0)
        n_proj = salic.get("total_projetos", 0) or 1
        ticket = vol / n_proj
        ufs = salic.get("distribuicao_uf", {})
        uf_top = max(ufs.items(), key=lambda kv: kv[1].get("valor", 0))[0] if ufs else "—"
        selo = {"ALTA": "✅ casamento confiável", "MEDIA": "⚠️ casamento provável — confirmar razão social",
                "BAIXA": "🔴 casamento incerto — NÃO usar sem conferir"}.get(conf, "")
        L += [
            f"Casado no índice SALIC como **{salic.get('nome_original', '—')}** — {como}.",
            "",
            f"**Confiança do casamento: {conf}** — {selo}",
            "",
            "| Métrica | Valor |",
            "|---|---|",
            f"| Volume declarado 2024+2025 | {brl(vol)} |",
            f"| Projetos patrocinados | {salic.get('total_projetos', 0)} |",
            f"| Ticket médio por projeto | {brl(ticket)} |",
            f"| UF principal | {uf_top} |",
            "",
            f"**FIT contra a cota mínima de {brl(COTA_MINIMA)}:** "
            + ("✅ ticket médio acima da cota" if ticket >= COTA_MINIMA
               else "⚠️ ticket médio abaixo da cota — avaliar projeto de menor porte ou cota compartilhada"),
            "",
        ]
        exemplos = salic.get("exemplos_projetos", [])[:5]
        if exemplos:
            L += ["### Projetos que já patrocinou", "",
                  "| PRONAC | Projeto | UF | Valor |", "|---|---|---|---|"]
            L += [f"| {p.get('pronac', '—')} | {p.get('nome', '—')} | {p.get('uf', '—')} | {brl(p.get('valor'))} |"
                  for p in exemplos]
            L.append("")
    else:
        L += [f"Não localizada no índice SALIC ({como}).", "",
              "Isso não significa que a empresa não patrocina — pode estar sob outra razão social.",
              "Vale conferir manualmente antes de descartar.", ""]

    L += [
        "---",
        "",
        "## A preencher manualmente",
        "",
        "<!-- O que o gerador não sabe. Preencher conforme a relação evolui. -->",
        "",
        "**Contatos:**",
        "",
        "| Nome | Cargo | Email | Nível |",
        "|---|---|---|---|",
        "|  |  |  | entrada / decisor |",
        "",
        "> Regra de busca de decisor: exigir pessoa **atual** no cargo e devolver dois níveis",
        "> (entrada e decisor). Ver `memory/feedback_lead-hunter-pessoa-atual-e-dois-niveis.md`.",
        "",
        "**Contexto do relacionamento:**",
        "",
        "**Próximos passos:**",
        "",
        "- [ ] ",
        "",
        "---",
        "",
        "*Fontes: `dados-ntics/faturamento_ntics_2020_2025.md` (aportes e pipeline) · "
        "`dados-ntics/SALIC_2026_INDICE_COMPLETO.json` (volume público, base 2024+2025).*  ",
        "*Números não conferidos manualmente — REGRA #0: conferir na fonte antes de usar em proposta.*",
    ]
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="não escreve arquivos")
    args = ap.parse_args()

    if not FATURAMENTO.exists() or not SALIC.exists():
        print("ERRO: fontes não encontradas em brain/dados-ntics/", file=sys.stderr)
        return 1

    linhas = FATURAMENTO.read_text(encoding="utf-8").splitlines()
    empresas = ler_aportes(linhas)
    negocios = ler_pipelines(linhas)

    for nome, lista in negocios.items():
        empresas.setdefault(nome, {"aportes": {}, "total": None})["negocios"] = lista
    for reg in empresas.values():
        reg.setdefault("negocios", [])

    _salic = json.load(SALIC.open(encoding="utf-8"))
    indice, palavras = _salic["indice_busca"], _salic["indice_palavras"]
    conf_contagem = {"ALTA": 0, "MEDIA": 0, "BAIXA": 0, "—": 0}
    for nome, reg in empresas.items():
        reg["salic"] = buscar_salic(nome, indice, palavras)
        conf_contagem[reg["salic"][2]] += 1

    hoje = date.today().isoformat()
    SAIDA.mkdir(parents=True, exist_ok=True)
    escritos = 0
    for nome, reg in sorted(empresas.items()):
        destino = SAIDA / f"{slug(nome)}.md"
        if destino.exists() and "gerar_fichas_clientes.py" not in destino.read_text(encoding="utf-8"):
            print(f"  preservado (escrito à mão): {destino.name}")
            continue
        if not args.dry_run:
            destino.write_text(montar_ficha(nome, reg, hoje), encoding="utf-8")
        escritos += 1

    print(f"\nempresas: {len(empresas)} | fichas: {escritos}"
          + (" (dry-run)" if args.dry_run else ""))
    print("casamento SALIC — "
          + " · ".join(f"{k}: {v}" for k, v in conf_contagem.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
