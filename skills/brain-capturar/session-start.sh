#!/bin/bash
# session-start.sh — roda no hook SessionStart. Duas funções, ambas baratas:
#   1. watchdog: imprime o estado do brain (sem LLM, sem token)
#   2. dispara a rotina pendente, injetando a instrução como contexto da sessão
#
# Por que SessionStart e não ~/.claude/CLAUDE.md, como fazia o Dream: aquela
# corrente tinha três elos (hook → CLAUDE.md global → flag) e os três estavam
# quebrados em 04/08/2026. Aqui o hook fala direto com a sessão.

set -u

# Mesma resolução em três níveis do should-brain.sh: env → ponteiro → padrão.
SPACE_PADRAO="$HOME/Projetos/ABILIO'S SPACE"
PONTEIRO="$HOME/.claude/brain-space-path"
if [ -n "${BRAIN_SPACE:-}" ]; then
    SPACE="$BRAIN_SPACE"
elif [ -s "$PONTEIRO" ]; then
    SPACE="$(head -1 "$PONTEIRO")"
else
    SPACE="$SPACE_PADRAO"
fi
CHECK="$SPACE/tools/brain_check.py"
PENDENTE_CAPTURA="$HOME/.claude/.brain-pending"
PENDENTE_CURADORIA="$HOME/.claude/.brain-curar-pending"

[ -f "$CHECK" ] || exit 0

saude=$(cd "$SPACE" && python3 "$CHECK" --quiet 2>/dev/null)

pedidos=""
if [ -f "$PENDENTE_CAPTURA" ]; then
    pedidos="Há captura de memória pendente (passaram 24h). Rode a skill \`brain-capturar\` em background e depois apague a flag com \`rm $PENDENTE_CAPTURA\`."
fi
if [ -f "$PENDENTE_CURADORIA" ]; then
    pedidos="$pedidos
Há curadoria semanal pendente. Se a curadoria na nuvem não estiver ativa, rode a skill \`brain-curar\` e apague \`$PENDENTE_CURADORIA\`."
fi

[ -z "$saude" ] && [ -z "$pedidos" ] && exit 0

contexto="Estado do BRAIN nesta máquina:
${saude:-brain íntegro}
${pedidos}"

python3 - "$contexto" <<'PY'
import json, sys
print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "SessionStart",
        "additionalContext": sys.argv[1],
    }
}, ensure_ascii=False))
PY

exit 0
