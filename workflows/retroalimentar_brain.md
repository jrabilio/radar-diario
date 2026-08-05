# Retroalimentação do BRAIN

**Objetivo:** manter a memória do Abilio crescendo *e* honesta, sem depender de ninguém lembrar de rodar nada.

Substitui o sistema Dream, parado desde 20/07/2026. O diagnóstico do que deu errado e o desenho novo estão em `brain/memory/reference_claude-brain-estrutura.md` e no `MAPA.md`.

---

## As três camadas

| Camada | O quê | Onde vive |
|---|---|---|
| **Ferramenta** | Acha as sessões, confere a saúde, gera as fichas | `tools/brain_*.py`, `tools/gerar_fichas_clientes.py` |
| **Julgamento** | Decide o que virou aprendizado e como reconciliar conflito | `skills/brain-capturar/`, `skills/brain-curar/` |
| **Relógio** | Dispara a cada 24h e denuncia quando não dispara | hooks `Stop` + `SessionStart` em `~/.claude/settings.json` |

A regra que separa as camadas: **se dá para escrever um `if`, é tool.** O Dream misturava as duas e o modelo pulava a parte mecânica — foi assim que 19 memórias ficaram sem data e um wikilink morto passou despercebido.

---

## Cadências

| Rotina | Quando | Onde roda | Por quê ali |
|---|---|---|---|
| `brain-capturar` | a cada 24h | **local** | as transcrições só existem nesta máquina; nuvem não as enxerga |
| `brain-curar` | semanal | **nuvem** (Cloud Routine) | só precisa do brain; roda com o Mac desligado |
| `gerar_fichas_clientes.py` | mensal ou sob demanda | qualquer um | só precisa dos dados do repo |

---

## Ferramentas

### `tools/brain_check.py` — o gate

```bash
python3 tools/brain_check.py            # relatório
python3 tools/brain_check.py --quiet    # uma linha, para hook
python3 tools/brain_check.py --json     # estruturado
```

Saída: `0` sem problema · `1` erro · `2` só avisos.

Confere índice↔arquivos, wikilinks, frontmatter, memórias vencidas, caminhos citados que não existem, limite de 200 linhas do índice, suspeita de duplicata, e **dias desde a última captura** — este último é o watchdog.

### `tools/brain_sessions.py` — a leitura

```bash
python3 tools/brain_sessions.py           # desde a última captura
python3 tools/brain_sessions.py --resumo  # só a lista
python3 tools/brain_sessions.py --tudo    # ignora o corte
```

Filtra o que importa: num arquivo de sessão típico **92% dos registros `type: user` são resultado de ferramenta**, não fala humana. Também exclui as sessões da própria rotina — senão a memória aprende com o próprio raciocínio.

### `tools/gerar_fichas_clientes.py` — os dados

```bash
python3 tools/gerar_fichas_clientes.py --dry-run
python3 tools/gerar_fichas_clientes.py
```

Cruza `faturamento_ntics_2020_2025.md` × `SALIC_2026_INDICE_COMPLETO.json` e escreve uma ficha por empresa em `brain/clientes/`. Preserva fichas editadas à mão. Casamento com o SALIC é graduado em ALTA/MÉDIA e **recusa o incerto em vez de chutar** — REGRA #0 do `PIPELINE_NTICS_V2.md`.

---

## O relógio

`Stop` → `should-brain.sh` marca `~/.claude/.brain-pending` (24h) e `.brain-curar-pending` (7 dias).

`SessionStart` → `session-start.sh` roda o check e injeta o estado como contexto da sessão, disparando a rotina pendente.

Usar `SessionStart` em vez do `~/.claude/CLAUDE.md` **elimina um elo da cadeia que quebrou**: o Dream dependia de hook → CLAUDE.md global → flag, e em 04/08/2026 os três estavam ausentes.

O aviso aparece assim, sem custo de token:

```
⚠️  brain: captura atrasada (11d) · 2 memórias vencidas — rode /brain-capturar
```

---

## Regra que atravessa tudo: contradição

Antes de gravar qualquer memória que afirme um fato sobre sistema, processo ou estado:

1. `grep -ril "<assunto>" brain/memory/`
2. Se algo existente afirmar o contrário, resolver — atualizar no lugar, marcar a antiga com bloco `> ⚠️ Correção de DD/MM/AAAA`, ou mover para `arquivo/`.
3. **Nunca deixar as duas de pé.** Não deu para decidir? Marque a divergência e leve ao Abilio.

Existe porque duas memórias afirmaram o oposto sobre o ClickUp por dois meses sem nada notar.

---

## Quando algo falhar

| Sintoma | Causa provável |
|---|---|
| Nenhum aviso na abertura da sessão | Hook não registrado — `jq '.hooks' ~/.claude/settings.json` |
| "captura nunca rodou" e não some | A rotina não está carimbando `brain/memory/.ultima-captura` |
| Captura lendo saída de ferramenta como pedido | `brain_sessions.py` não foi usado; não ler `.jsonl` na unha |
| Memória repetindo o que a rotina pensou | Filtro de própria-rotina falhou — conferir o regex em `brain_sessions.py` |
| `brain_check` acusando caminho morto | Bom sinal: é o check funcionando. Corrigir a memória |

---

## Manutenção

- Skills instaladas em `~/.claude/skills/` por `config/claude-global/instalar.sh`. Editou aqui? Rode o instalador de novo.
- Validades por tipo em `tools/brain_check.py` (`VALIDADE_DIAS`) — mudou lá, muda em todo lugar.
- ⚠️ O remote deste repo é **público**. `brain/` e `_revisar/` estão no `.gitignore`. Memória vai para o repositório **privado**, nunca para cá.
