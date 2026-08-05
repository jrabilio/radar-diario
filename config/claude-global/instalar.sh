#!/bin/bash
# instalar.sh — Configura o sistema de memória automática no Claude Code
# Execute uma única vez no Terminal:
#   bash "$HOME/Projetos/ABILIO'S SPACE/config/claude-global/instalar.sh"

set -e

CLAUDE_DIR="$HOME/.claude"
SPACE_DIR="$HOME/Projetos/ABILIO'S SPACE"
BRAIN_DIR="$SPACE_DIR/brain"
INSTALL_DIR="$SPACE_DIR/config/claude-global"
SKILLS_DIR="$SPACE_DIR/skills"

echo "🧠 Instalando sistema de memória automática..."
echo ""

# 1. Criar estrutura ~/.claude se não existir
mkdir -p "$CLAUDE_DIR/skills"
echo "✓ Pasta ~/.claude criada/verificada"

# 2. Instalar CLAUDE.md global
if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    echo ""
    echo "⚠️  Já existe um CLAUDE.md em ~/.claude/CLAUDE.md"
    echo "   Fazendo backup em ~/.claude/CLAUDE.md.backup"
    cp "$CLAUDE_DIR/CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md.backup"
fi
cp "$INSTALL_DIR/CLAUDE-global.md" "$CLAUDE_DIR/CLAUDE.md"
echo "✓ CLAUDE.md instalado em ~/.claude/"

# 3. Instalar as skills de retroalimentação do brain
for skill in brain-capturar brain-curar; do
    mkdir -p "$CLAUDE_DIR/skills/$skill"
    cp -R "$SKILLS_DIR/$skill/." "$CLAUDE_DIR/skills/$skill/"
done
chmod +x "$CLAUDE_DIR/skills/brain-capturar/"*.sh
echo "✓ Skills brain-capturar e brain-curar instaladas em ~/.claude/skills/"

# 4. Instalar settings.json (com merge se já existir)
if [ -f "$CLAUDE_DIR/settings.json" ]; then
    echo ""
    echo "⚠️  Já existe um settings.json em ~/.claude/settings.json"
    echo "   Fazendo backup em ~/.claude/settings.json.backup"
    cp "$CLAUDE_DIR/settings.json" "$CLAUDE_DIR/settings.json.backup"
    echo ""
    echo "   ATENÇÃO: Você já tem configurações no settings.json."
    echo "   Adicione manualmente o bloco de hooks abaixo ao seu settings.json existente:"
    echo ""
    echo '   "hooks": {'
    echo '     "Stop": [{'
    echo '       "matcher": "",'
    echo '       "hooks": [{'
    echo '         "type": "command",'
    echo '         "command": "bash ~/.claude/skills/brain-capturar/should-brain.sh"'
    echo '       }]'
    echo '     }]'
    echo '   }'
    echo ""
else
    cp "$INSTALL_DIR/settings.json" "$CLAUDE_DIR/settings.json"
    echo "✓ settings.json instalado em ~/.claude/"
fi

# 5. Inicializar o marco de captura (alimenta o watchdog do brain_check)
date +%F > "/memory/.ultima-captura"
echo "✓ Retroalimentação do brain inicializada (próxima captura em 24h)"

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "O que foi configurado:"
echo "  • CLAUDE.md global com protocolo de memória"
echo "  • Skills /brain-capturar e /brain-curar"
echo "  • Hook automático: roda ao fim de cada sessão Claude Code"
echo "  • SecondBrain em: $BRAIN_DIR"
echo "  • Memória persistente em: $BRAIN_DIR/memory/"
echo ""
echo "Para usar:"
echo "  • O sistema funciona automaticamente a cada 24h"
echo "  • Para consolidar manualmente: /brain-capturar (diária) ou /brain-curar (semanal)"
echo "  • Para navegar o brain: abra ABILIO'S SPACE/brain no Desktop"
