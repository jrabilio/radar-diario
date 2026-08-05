#!/bin/bash
# should-brain.sh — decide se está na hora de capturar ou curar o brain.
# Roda no hook Stop do Claude Code, ao fim de cada sessão. Barato: só compara datas.
#
# Substitui should-dream.sh. Diferenças que importam:
#   - lê a data de brain/memory/.ultima-captura (o mesmo arquivo que o
#     brain_check usa como watchdog) em vez de um timestamp solto em ~/.claude,
#     então não existe estado duplicado que possa divergir;
#   - marca curadoria separada da captura, com cadência própria;
#   - nunca falha a sessão: qualquer erro sai com 0.

set -u

# Resolve o SPACE em três níveis, para que mover a pasta não quebre o hook de novo:
#   1. $BRAIN_SPACE (env)  2. ~/.claude/brain-space-path  3. padrão embutido
# O apóstrofo de ABILIO'S não pode ficar dentro de ${VAR:-default}: ali o bash
# o trata como abertura de aspas simples e o script inteiro não parseia.
SPACE_PADRAO="$HOME/Projetos/ABILIO'S SPACE"
PONTEIRO="$HOME/.claude/brain-space-path"
if [ -n "${BRAIN_SPACE:-}" ]; then
    SPACE="$BRAIN_SPACE"
elif [ -s "$PONTEIRO" ]; then
    SPACE="$(head -1 "$PONTEIRO")"
else
    SPACE="$SPACE_PADRAO"
fi
MEM="$SPACE/brain/memory"
PENDENTE_CAPTURA="$HOME/.claude/.brain-pending"
PENDENTE_CURADORIA="$HOME/.claude/.brain-curar-pending"

DIAS_CAPTURA=1
DIAS_CURADORIA=7

[ -d "$MEM" ] || exit 0

# dias_desde <arquivo> — imprime a idade em dias, ou 9999 se não existir/for inválido
dias_desde() {
    local arq="$1"
    [ -f "$arq" ] || { echo 9999; return; }
    local quando
    quando=$(head -c 10 "$arq" 2>/dev/null)
    local epoch
    epoch=$(date -j -f "%Y-%m-%d" "$quando" +%s 2>/dev/null) || { echo 9999; return; }
    echo $(( ( $(date +%s) - epoch ) / 86400 ))
}

if [ "$(dias_desde "$MEM/.ultima-captura")" -ge "$DIAS_CAPTURA" ]; then
    touch "$PENDENTE_CAPTURA"
fi

if [ "$(dias_desde "$MEM/.ultima-curadoria")" -ge "$DIAS_CURADORIA" ]; then
    touch "$PENDENTE_CURADORIA"
fi

exit 0
