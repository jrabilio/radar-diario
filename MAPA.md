# MAPA — ABILIO'S SPACE

Consolidação iniciada em **04/08/2026**, **encerrada em 05/08/2026**. As pastas `CLAUDE BRAIN`, `CLAUDE 2` (Desktop) e `Claude` (Documents) foram varridas; o que tinha valor veio para cá. As três originais foram para a Lixeira e a quarentena `_revisar/` não existe mais.

> `Documents/Claude` era **subconjunto exato** de `Desktop/CLAUDE 2` — mesmos 257 arquivos, mesmos tamanhos, nada exclusivo. Ignorada.

---

## Vivo — usa no dia a dia

| Pasta | O que é |
|-------|---------|
| `brain/` | Base de conhecimento e memória persistente. Entrada: [brain/INDEX.md](brain/INDEX.md) |
| `config/claude-global/` | `CLAUDE-global.md`, `settings.json` e `instalar.sh` do sistema de memória |
| `skills/brain-capturar/` | Captura diária de memória + os dois hooks. Substitui a `dream` |
| `skills/brain-curar/` | Curadoria semanal — contradições, obsolescência, integridade |
| `skills/agendadas-nuvem/` | 3 skills que **rodam hoje** como Cloud Routines — ver abaixo |
| `skills/bundles/` | 2 skills empacotadas: `pesquisa-empresa-ntics`, `curadoria-pipeline-ntics` |
| `tools/` `workflows/` `docs/` | Framework WAT. SOP da memória: [workflows/retroalimentar_brain.md](workflows/retroalimentar_brain.md) |
| `tools/legado/` | Scripts de rotina que **não roda mais**, guardados por terem valor: gerador do HTML do relatório executivo e o envio por SMTP |
| `financas/` | App de controle financeiro pessoal (Fase 1). **Fora do git deste repo** — ver abaixo. SOP: [workflows/controle_financeiro.md](workflows/controle_financeiro.md) |

### Dentro de `brain/`

- **`memory/`** — 40 arquivos + [MEMORY.md](brain/memory/MEMORY.md) como índice. O ativo mais valioso: perfil, 6 projetos, 11 feedbacks, 21 referências de sistema.
- **`clientes/`**, **`institucional/`**, **`conhecimento/`**, **`dados-ntics/`** — pipeline NTICS, faturamento 2020-2025, catálogo LAB LEAN, índice SALIC 2026.
- **`guias/`** — PDFs (guia código zero, 5 skills, planejamento PMO 2026 v12).
- **`templates/`** — ata, cliente, decisão, projeto.
- **`processos/`** *(novo em 05/08)* — arquivo de receitas das rotinas que morreram: 18 `skills-agendadas/` + `atas-reuniao/`. Consultar antes de recriar qualquer automação.
- **`conhecimento/estudos-empresas/`** *(novo)* — 30 estudos de prospect. **`referencias/dashboards/`** *(novo)* — 3 painéis preservados.
- `conversas/`, `decisoes/`, `ideias/`, `projetos-anteriores/` vieram vazias da origem — mantidas com `.gitkeep` porque o INDEX documenta a estrutura.

---

## Rotinas na nuvem

Quatro rodando. Nenhuma depende deste Mac — é exatamente por isso que estão vivas.

| Rotina | Quando (BRT) | Cron (UTC) | Entrega |
|---|---|---|---|
| Radar Diário | 07h00 | `0 10 * * *` | GitHub Pages (público) + WhatsApp |
| **Relatório Executivo** | **06h45** | `45 9 * * *` | **Google Drive (privado) + WhatsApp** |
| Auditoria fase/status | 02h30 | `30 5 * * *` | Artefato |
| Varredura completa | segundas 07h | `0 10 * * 1` | Artefato |

O **Relatório Executivo** foi ressuscitado em 05/08/2026 ([trig_016gPDoRZ4sghXNKfSSA7QXV](https://claude.ai/code/routines/trig_016gPDoRZ4sghXNKfSSA7QXV)).
Ele havia morrido em 17/07 porque tinha duas metades em máquinas diferentes: o Cowork gerava
o HTML e um **LaunchAgent no Mac** enviava por SMTP às 07:30. A skill legada até avisava
`NÃO enviar e-mail aqui`. Morta a camada local, nada mais saía.

A versão nova roda inteira na nuvem e **não usa e-mail**. Não é preferência: a conta
`@ecotransformax` é Google Workspace, e o Google
[bloqueia App Password em conta de organização](https://support.google.com/accounts/answer/185833?hl=pt-BR)
desde a virada para OAuth em março de 2025. O conector Gmail também não resolveria — só tem
`create_draft`, sem método de envio.

> ⚠️ A rotina é proibida de commitar. O relatório traz clipping interno do Grupo NEST e o
> remote é público. A entrega é no Drive, e só lá.

### Credenciais nas rotinas

As rotinas na nuvem **não enxergam** o `.env` local — a documentação é explícita quanto a
isso. Quando precisam de segredo, ele vai no prompt da rotina (privado na conta do Abilio).
É o que a `Radar Diário` já fazia, e o que o Relatório Executivo faz com a chave do CallMeBot.

> ⚠️ A `Radar Diário` carrega um `GITHUB_TOKEN` (`github_pat_…`) com permissão de escrita, em
> texto puro no prompt. Entra na lista de rotação.

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

## `_revisar/` — resolvido em 05/08/2026

A quarentena tinha 197 arquivos íntegros que **não rodavam mais** (nenhum LaunchAgent da NTICS instalado, nada no `launchctl`, saídas paradas desde 17/07). Foi liquidada aplicando as recomendações do LEIA-ME em bloco.

**Guardado:**

| De | Para | O quê |
|---|---|---|
| `skills-agendadas/` | `brain/processos/skills-agendadas/` | 18 SKILL.md — receitas de processo, não código morto |
| `atas-reuniao/` | `brain/processos/atas-reuniao/` | `classify_meeting.py` + SOP (lógica de negócio) |
| `relatorio-diario/` | `tools/legado/` | `gerar_relatorio_template.py`, `enviar_relatorio.py` |
| `estudos-noturnos/` | `brain/conhecimento/estudos-empresas/` | 30 estudos de prospect — pesquisa não vence |
| `artifacts/` | `brain/referencias/dashboards/` | 3 painéis: auditoria fase/status, monitor, varredura de segunda |

**Descartado (Lixeira, recuperável):** 80 relatórios executivos + 43 culturais + 3 saídas do monitor (clipping perde validade), infra de agendamento (`plist`, `organizar_arquivos.py`, `INSTRUCOES_RELATORIO.md`), `publicar-github-pages.md` (substituído por `tools/publish_git.py`), a skill `dream` (substituída por `brain-capturar`), `SKILL.md.versao-antiga` e `classify_meeting_run13.py` (a versão guardada é superset — mapeia 5 membros a mais do ClickUp).

**Antes de mover as originais**, conferi arquivo a arquivo o que existia só nelas: 100% caía num descarte já declarado (182 `Artifacts/*/versions`, os 123 HTMLs, `run/`, logs, scripts `nord`, `SKILL.mdC`). Nada foi esquecido.

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

## Credenciais — centralizadas no `.env`, rotação pendente

As três credenciais que estavam em texto puro foram para o `.env` da raiz (gitignored) e os arquivos de origem sumiram junto com o `_revisar/`:

| Onde estava | O quê | Agora |
|---|---|---|
| `atas-reuniao/secrets.env` | `ANTHROPIC_API_KEY` | `.env` → `ANTHROPIC_API_KEY` |
| `com.ntics.relatoriodiario.plist` | App Password do Gmail | `.env` → `GMAIL_USER` / `GMAIL_APP_PASSWORD` |
| `skills-agendadas/monitor-automacoes/SKILL.md:58` | **Segunda** App Password, inline num comando de exemplo | linha reescrita para dar `source` no `.env` |

A terceira não estava no inventário original — apareceu numa varredura do que foi guardado. É uma App Password **diferente** da do plist, o que significa que existem duas emitidas.

> ⚠️ **Ação sua:** rotacionar as três. API key em [console.anthropic.com](https://console.anthropic.com/settings/keys); as duas App Passwords em [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) — revogar **todas** as entradas antigas e emitir uma só, atualizando o `.env`.

## Pendências

1. ⚠️ **Gerar uma App Password na conta `@ecotransformax` e pôr em `GMAIL_APP_PASSWORD`.** Está vazia de propósito: a operação passou de `@ntics` para `@ecotransformax` (remetente e destinatário do relatório, e a conta do espelho do brain), e App Password é **por conta** — a antiga, da `@ntics`, não autentica na nova. Enquanto estiver vazia o script para com mensagem clara, em vez de falhar com erro de autenticação. Requer Verificação em 2 Etapas ativa na conta.
2. **Rotacionar as outras credenciais:** `ANTHROPIC_API_KEY`, as **duas** App Passwords antigas da `@ntics` (revogar ambas) e o `GITHUB_TOKEN` que está em texto puro no prompt da rotina `Radar Diário`.
3. ⚠️ **O backup do brain no Drive não está rodando.** `tools/brain_sync_drive.py` espelha para `BRAIN_DRIVE_CONTA` (`@ecotransformax`), mas **essa conta não está montada nesta máquina** — a única em `~/Library/CloudStorage/` é `@ntics`. O script falha com erro claro, sem destruir nada. Resolver adicionando a conta no app Google Drive. Enquanto isso, o brain existe **só** neste Mac.
4. **Esvaziar a Lixeira** quando estiver confortável — as 3 pastas originais (32 MB) e o `_revisar/` estão lá, recuperáveis até então.
5. ~~Fallback morto no `enviar_relatorio.py`~~ — **resolvido em 05/08**: o script foi parametrizado (remetente, destinatário e assunto vêm do `.env`), o fallback que lia plists inexistentes saiu, e as pastas de trabalho deixaram de apontar para `~/Desktop/CLAUDE/` (que foi para a Lixeira) e passaram a `.tmp/`.
6. `config/claude-global/CLAUDE-global.md` perdeu o e-mail pessoal da linha de identidade (repo público). O `~/.claude/CLAUDE.md` em uso **não** foi alterado — mas rodar `instalar.sh` sobrescreve com esta versão. Sem prejuízo prático: o Claude já recebe o e-mail pelo próprio ambiente.
