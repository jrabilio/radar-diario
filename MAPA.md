# MAPA — ABILIO'S SPACE

Consolidação de **04/08/2026**. As pastas `CLAUDE BRAIN`, `CLAUDE 2` (Desktop) e `Claude` (Documents) foram varridas; o que tinha valor veio para cá, separado entre **o que está vivo** e **o que precisa da sua decisão**.

> `Documents/Claude` era **subconjunto exato** de `Desktop/CLAUDE 2` — mesmos 257 arquivos, mesmos tamanhos, nada exclusivo. Ignorada.

---

## Vivo — usa no dia a dia

| Pasta | O que é |
|-------|---------|
| `brain/` | Base de conhecimento e memória persistente. Entrada: [brain/INDEX.md](brain/INDEX.md) |
| `config/claude-global/` | `CLAUDE-global.md`, `settings.json` e `instalar.sh` do sistema de memória |
| `skills/dream/` | Skill de consolidação de memória + hook de 24h |
| `skills/bundles/` | 2 skills empacotadas: `pesquisa-empresa-ntics`, `curadoria-pipeline-ntics` |
| `tools/` `workflows/` `docs/` | Framework WAT já existente (newsletter) |
| `financas/` | App de controle financeiro pessoal (Fase 1). **Fora do git deste repo** — ver abaixo. SOP: [workflows/controle_financeiro.md](workflows/controle_financeiro.md) |

### Dentro de `brain/`

- **`memory/`** — 40 arquivos + [MEMORY.md](brain/memory/MEMORY.md) como índice. O ativo mais valioso: perfil, 6 projetos, 11 feedbacks, 21 referências de sistema.
- **`clientes/`**, **`institucional/`**, **`conhecimento/`**, **`dados-ntics/`** — pipeline NTICS, faturamento 2020-2025, catálogo LAB LEAN, índice SALIC 2026.
- **`guias/`** — PDFs (guia código zero, 5 skills, planejamento PMO 2026 v12).
- **`templates/`** — ata, cliente, decisão, projeto.
- `conversas/`, `decisoes/`, `ideias/`, `referencias/`, `projetos-anteriores/` vieram vazias da origem — mantidas com `.gitkeep` porque o INDEX documenta a estrutura.

---

## `financas/` — app pessoal, fora do controle de versão

Aplicativo de controle financeiro (Fase 1: núcleo). Mora dentro do SPACE, mas tem **git
próprio, sem remote**, e o `.gitignore` da raiz ignora a pasta inteira.

**Por quê:** o remote deste repositório (`jrabilio/radar-diario`) é **público**, porque
serve o GitHub Pages da newsletter. A spec do app traz dados financeiros reais — custo de
vida, percentual de renda aportada, valores de reembolso, nomes das PJs — e o seed lista
as instituições e cartões. Nada disso pode ser indexado publicamente.

O que **é** versionado aqui: [workflows/controle_financeiro.md](workflows/controle_financeiro.md),
o SOP da rotina, sem nenhum número pessoal.

---

## `_revisar/` — parado, aguarda sua decisão

197 arquivos que vieram íntegros mas **não rodam mais**. Evidência e recomendação item a item em [_revisar/LEIA-ME.md](_revisar/LEIA-ME.md).

Resumo: nenhum LaunchAgent da NTICS está instalado, nada carregado no `launchctl`, e as saídas pararam há semanas (relatório diário 17/07, cultural 19/06, estudos 30/06).

---

## Paths reescritos

71 substituições em 36 arquivos. O material herdado apontava para `/Users/abiliojr/` — usuário que não existe nesta máquina — e para a estrutura antiga de pastas. Mapeamento aplicado:

| Antigo | Novo |
|---|---|
| `~/Desktop/CLAUDE BRAIN` | `ABILIO'S SPACE/brain` |
| `~/Desktop/CLAUDE/automacoes` | `_revisar/rotinas-paradas/relatorio-diario` |
| `~/Desktop/CLAUDE/Diario` | `_revisar/saidas-historicas/relatorios-diarios` |
| `~/Documents/Claude/Scheduled` | `_revisar/rotinas-paradas/skills-agendadas` |
| `~/Documents/Claude/Projects/GITHUB` | `.tmp/github-publish` (clone de trabalho, gitignored) |
| `/Users/abiliojr/` | `/Users/abiliomartins/` |

Validado depois: sintaxe OK em todos os `.sh`, `.py` e no plist; nenhum path citado que não exista, fora placeholders e arquivos criados em runtime.

---

## Verificação de integridade

| Conjunto | Resultado |
|---|---|
| `brain/memory/` (40) | idêntico por MD5, exceto os 8 que eu reescrevi |
| `relatorios-diarios/` (80) | 80/80 idênticos |
| `relatorios-culturais/` (43) | 43/43 idênticos — 1 truncado na primeira cópia, recopiado |
| `estudos-noturnos/` (30) | 30/30 idênticos |

---

## Descartado

| Item | Motivo |
|---|---|
| `Documents/Claude` inteira | Subconjunto exato de `CLAUDE 2` |
| `Artifacts/*/versions/` (182 arquivos, ~4 MB) | Snapshot diário redundante com os relatórios datados |
| `atas-reuniao/run/01..12` | 12 cópias byte-idênticas do mesmo script (MD5) |
| `automacoes/logs/` (5) | Regenerável |
| `automacoes/nord/` (3 scripts) | Liam um temporário de sessão em `/var/folders/…` que não existe mais |

---

## Pendências

1. **Apagar as pastas originais.** ⚠️ **Ainda não foi feito** — `~/Desktop/CLAUDE BRAIN`, `~/Desktop/CLAUDE 2` e `~/Documents/Claude` continuam intactas. A consolidação foi por cópia.
2. **Credenciais** (tratar depois, conforme combinado): `ANTHROPIC_API_KEY` em `_revisar/rotinas-paradas/atas-reuniao/secrets.env` e App Password do Gmail no `com.ntics.relatoriodiario.plist`. Ambos já cobertos pelo `.gitignore`.
3. **Decidir o `_revisar/`** — ver [_revisar/LEIA-ME.md](_revisar/LEIA-ME.md).
