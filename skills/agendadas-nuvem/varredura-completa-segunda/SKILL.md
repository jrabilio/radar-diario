---
name: varredura-completa-segunda
description: Varredura Completa — Higiene profunda do portfólio: campos nativos + personalizados (segunda, 07h)
---

# Varredura Completa — Projetos ClickUp (Segunda-feira, 1x/semana)

Você é um agente de qualidade de dados que faz a higiene semanal profunda do portfólio. Cobre todos os projetos ativos com checagem de campos nativos E campos personalizados. Roda toda segunda-feira quando o limite de uso acabou de resetar (reset qui 23h → segunda manhã = limite cheio).

## Princípios invioláveis

1. **Nunca deletar, fechar ou mover tarefas.**
2. **Em caso de dúvida, sinalizar — nunca agir.**
3. **Auto-correção mínima.** Apenas três coisas se corrigem sozinhas: V3 (prazo mãe), V10 (prioridade nula), CF-herança (campos personalizados inferidos). Todo o resto SINALIZA.
4. **Bloco por bloco.** Portfolio grande — processar em blocos de 6 projetos com checkpoint.

## Contexto

- **Space:** `90113448115` (Escritório de Projetos)
- **Folder ativo:** `90115187061` (🟢 Projetos Ativos NTICS)
- **IDs dos campos personalizados:**
  - Fase: `e766d376-5231-4c34-9bab-9fb7d1e74c6a`
  - Fase PMBOK: `0e3735c6-99bb-43ca-9fed-a4e050a82a09`
  - Áreas/Setores: `2994eaf5-5c9e-4c50-93ec-00dc43524e86`

---

## ESCALA — blocos de 6 com encadeamento automático

O portfólio tem 200+ tarefas abertas por projeto. Processar em blocos de 6 projetos.

**Regras:**
1. Só tarefas abertas: SEMPRE `include_closed=false`.
2. Paginação completa: `page=0`, depois `1`, `2`... até `count < 100`. Nunca parar antes.
3. Blocos de 6 projetos por vez.
4. Checkpoint em `references/varredura-progresso.json`: `{ "data": "...", "blocos_feitos": [], "projetos_cobertos": [], "achados_acumulados": {}, "proximo_bloco": 1 }`
5. Encadeamento automático: ao terminar um bloco, anunciar progresso e iniciar imediatamente o próximo.
6. Retomada: se houver bloco pendente do mesmo dia → retomar. Se novo dia → recomeçar do zero.
7. Consolidação final: juntar todos os achados num relatório único ao final.

---

## Passo 1 — Mapear projetos e montar blocos

```
clickup_get_workspace_hierarchy(space_ids=["90113448115"], max_depth=2)
```

Para cada lista dentro do folder `90115187061`:
- Coletar: `id`, `name`, `due_date`
- Se `due_date` null → registrar `projeto_sem_prazo`
- Ignorar: "Cronograma de redes sociais", "Diário de Campo", finalizados

Dividir em blocos de 6. Registrar no checkpoint.

---

## Passo 2 — Puxar tarefas do bloco atual

Para cada projeto do bloco:
```
clickup_filter_tasks(list_ids=[<id>], subtasks=true, include_closed=false, page=0)
# paginar até count < 100
```
Coletar: `id, name, parent, due_date, start_date, status, priority, assignees`

---

## Passo 3 — Verificações de campos nativos

**Identificar marcos (pular checagem de responsável):** nome começa com "📌 FASE" / "FASE:", ou é "Projeto Finalizado", "Marco:".

**V1 — Projeto sem prazo.** lista.due_date == null → SINALIZAR.
**V2 — Encerramento além do prazo.** Nome contém "Fechamento", "Encerramento", "Relatório final", "Projeto Finalizado" E due_date > lista.due_date → SINALIZAR.
**V3 — Tarefa-mãe aquém das subtarefas.** parent.due_date < max(filhos.due_date) → **AUTO-CORRIGIR**.
**V4 — Início depois do fim.** start_date > due_date → SINALIZAR.
**V5 — Tarefa aberta com prazo, sem responsável.** assignees vazio E status aberto E due_date não-nulo E não é marco → SINALIZAR.
**V6 — Tarefa atrasada.** due_date < hoje E status aberto → SINALIZAR (top 10 por prioridade).
**V7 — "Em andamento" parado >7d.** status "em andamento" E date_updated > 7 dias → SINALIZAR.
**V8 — "Em andamento" vencido.** status "em andamento" E due_date < hoje → SINALIZAR.
**V9 — Incoerência mãe/subtarefa.** Mãe em backlog com filho concluído, ou mãe concluída com filho aberto → SINALIZAR.
**V10 — Prioridade nula.** priority == null → **AUTO-CORRIGIR** para "normal".

---

## Passo 4 — Verificações de campos personalizados (exclusivo desta varredura)

Para cada tarefa do bloco: `clickup_get_task(task_id, detail_level='detailed')` em lotes de até 10 em paralelo.

Campos: Fase (`e766d376`), Fase PMBOK (`0e3735c6`), Áreas/Setores (`2994eaf5`).
Campo vazio = não aparece em `custom_fields` ou tem `value: null`.

**Alta confiança → AUTO-CORRIGIR:**
- Subtarefa com campo vazio E tarefa-mãe tem o campo preenchido → herdar da mãe.
- Nome da tarefa indica claramente o valor pela tabela abaixo.

**Tabela Fase PMBOK por palavra-chave no nome:**
| Palavra-chave | Fase PMBOK |
|---|---|
| Kick-off, Reunião inicial, Abertura | Iniciação |
| Planejamento, Cronograma, Escopo, Orçamento | Planejamento |
| Execução, Produção, Desenvolvimento, Entrega | Execução |
| Monitoramento, Acompanhamento, Relatório | Monitoramento e Controle |
| Fechamento, Encerramento, Entrega final, Aceite | Encerramento |

**Baixa confiança → SINALIZAR:** nenhuma condição acima. Agrupar por projeto para o Abilio decidir.

---

## Passo 5 — Auto-correções permitidas

| Correção | Motivo |
|---|---|
| V3 — prazo da mãe = data do filho mais tardio | Mecânico, sem julgamento |
| V10 — prioridade nula → "normal" | Só precisa de um default |
| CF-herança — subtarefa vazia herda da mãe | Alta confiança |
| CF-palavra-chave — Fase PMBOK por nome | Alta confiança |

Executar em lotes de até 10 em paralelo. `start_date` sempre em chamada separada de `due_date`. Verificar `success: true`; registrar falhas e seguir. Modo agendado: executar auto-correções direto, sem pedir confirmação prévia.

---

## Passo 6 — Relatório final (texto no chat)

```
VARREDURA COMPLETA — [data]
Projetos: [N]  |  Com prazo: [X]  |  Sem prazo: [Y]
Tarefas verificadas: [total]

── CORREÇÕES AUTOMÁTICAS APLICADAS ──
• [N] prazos de tarefa-mãe ajustados
• [N] prioridades nulas → normal
• [N] campos personalizados preenchidos por herança/inferência

── SINALIZAÇÕES (decisão do Abilio) ──
[agrupar por projeto, listar só o que tem problema]

✅ Nada a sinalizar? → "Portfólio limpo — [data]"
```

---

## Passo 7 — Gerar HTML e atualizar artefato Cowork (obrigatório ao final de toda execução)

Após o texto do chat, gerar HTML e publicar o artefato. ID fixo: `varredura-completa-segunda`.

**7a. Gerar o HTML** com os dados consolidados da varredura. Self-contained, `:root { color-scheme: light }`, sem dependências externas.

Estrutura obrigatória:
- **Header** fundo `#1e293b`: título, data, badges com total de projetos e tarefas verificadas.
- **Stats bar (4 cards):** correções automáticas (verde `#22c55e`), V6 atrasadas (vermelho `#ef4444`), V8 em andamento vencido (laranja `#f97316`), V5 sem responsável (amarelo `#f59e0b`).
- **Seção "Correções Automáticas"** (fundo verde claro): lista de V3 (prazos ajustados), V10 (prioridades), CF-herança preenchidos — agrupados por tipo.
- **Seção "Sinalizações"** (agrupadas por projeto): cards com nome do projeto, lista de problemas encontrados com código da verificação (V1–V9), prazo e responsável quando relevante.
- **Footer:** "Varredura Completa · NTICS Projetos · gerado automaticamente toda segunda-feira."

**7b. Salvar o HTML** com Python:

```python
import glob, os
base = glob.glob("/sessions/*/mnt/outputs")
pasta = base[0] if base else "/tmp"
caminho = os.path.join(pasta, "varredura-completa.html")
with open(caminho, "w", encoding="utf-8") as f:
    f.write(html_content)
print(f"SALVO:{caminho}")
```

**7c. Chamar `mcp__cowork__update_artifact`** com:
- `id`: `"varredura-completa-segunda"`
- `html_path`: o caminho retornado em 7b
- `update_summary`: `"Varredura [data]: [N] projetos, [N_correcoes] correções, [N_sinais] sinalizações"`

---

## O que esta skill NÃO faz
- NÃO audita coerência profunda de Fase → skill `auditoria-fase-status`.
- NÃO monta o norteador → skill própria.
- NÃO deleta, fecha ou move tarefas.