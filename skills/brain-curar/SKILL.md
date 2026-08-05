---
name: brain-curar
description: Curadoria semanal do brain — resolve o que o brain_check apontou, confere memórias vencidas contra a realidade, caça contradições entre memórias e aposenta o que virou histórico. Roda como Cloud Routine semanal sobre o repositório privado do brain.
---

# brain-curar — curadoria semanal

Você mantém o brain **honesto**. A captura diária faz ele crescer; você impede que ele apodreça.

Esta é a camada que o Dream nunca teve. O resultado da falta dela, auditado em 04/08/2026: 19 de 40 memórias sem data, um wikilink apontando para arquivo inexistente, duas memórias afirmando o oposto sobre o ClickUp por dois meses, e uma memória descrevendo pastas que já não existiam se lendo como atual.

**Regra absoluta:** na dúvida, **manter**. Você corrige e aposenta — não apaga conhecimento.

---

## Etapa 1 — Diagnóstico

```bash
python3 tools/brain_check.py --json
```

Trabalhe a partir da saída. **Erros** (código 1) são obrigatórios; **avisos** (código 2) são o trabalho de curadoria.

## Etapa 2 — Consertar o que é mecânico

| Problema apontado | O que fazer |
|---|---|
| Arquivo fora do índice | Acrescentar a linha no `MEMORY.md`, na seção certa (Vivo ou Arquivo) |
| Índice aponta para arquivo inexistente | Remover a linha, ou restaurar o arquivo se o sumiço foi engano |
| Wikilink não resolve | Corrigir o alvo — quase sempre falta o prefixo (`[[norteador-skill]]` → `[[reference_norteador-skill]]`) |
| Frontmatter incompleto ou `type`/`status` inválido | Preencher; `status` tem que bater com a pasta |
| `MEMORY.md` acima de 200 linhas | Comprimir os ganchos, nunca remover entradas |

## Etapa 3 — Memórias vencidas: conferir contra a realidade

Para cada memória que o check listou como vencida, **não basta renovar a data**. Verificar se o que ela afirma ainda é verdade:

- Cita caminho? `ls` nele.
- Descreve automação? Ela ainda roda? (Cloud Routines via `RemoteTrigger list`; local via `launchctl list`)
- Descreve processo? Bate com o que as memórias mais recentes dizem?
- Descreve estado de projeto? Está congelado num snapshot antigo?

Então escolher:

- **Confirmada** → atualizar `revisar_em` para hoje + validade do tipo, e registrar no rodapé que foi conferida.
- **Parcialmente desatualizada** → corrigir o trecho e marcar com bloco `> ⚠️ Correção de DD/MM/AAAA`.
- **Virou histórico** → mover para `brain/memory/arquivo/`, trocar `status: arquivo`, mover a linha no índice para a seção Arquivo.

> Exemplo real: `reference_cloud-routines-migracao.md` registrava a migração para Cloud Routines como "planejada, não iniciada". Em 04/08/2026 descobriu-se que **duas rotinas já estavam rodando na nuvem** havia semanas. A memória estava mentindo por omissão de atualização — exatamente o que esta etapa existe para pegar.

## Etapa 4 — Caçar contradições

O `brain_check` acha duplicata por semelhança de `description`, mas **não acha contradição** — duas memórias podem falar do mesmo sistema com descrições bem diferentes e conclusões opostas.

Agrupar as memórias vivas por assunto (ClickUp, e-mail, GitHub, norteador, PMO, pipeline comercial…) e, dentro de cada grupo, comparar as afirmações factuais. Procurar especificamente:

- "X é a fonte da verdade" vs "X não é confiável"
- "isso está configurado" vs "isso nunca foi feito"
- "roda às 6h" vs "roda às 1h"
- caminho A vs caminho B para a mesma coisa

Achou? Aplicar o **protocolo de contradição** (o mesmo da `brain-capturar`): a mais recente com evidência vence, a antiga recebe bloco `> ⚠️ Correção de DD/MM/AAAA` apontando para ela, ou vai para `arquivo/`. **Nunca deixar as duas de pé.**

Se não der para decidir qual está certa, marque a divergência nas duas e **leve para o Abilio no relatório**.

## Etapa 5 — Enxugar

Só cortar o que é **genuinamente** redundante ou obsoleto.

- **Mesclar** quando dois arquivos cobrem o mesmo tema com sobreposição > 70%
- **Comprimir** só se a versão curta preserva 100% da informação acionável
- **Nunca remover:** regra de feedback, contexto de cliente, referência de sistema, preferência do usuário

## Etapa 6 — Fechar

```bash
python3 tools/brain_check.py
date +%F > brain/memory/.ultima-curadoria
```

Não encerre com erro em pé. Se estiver rodando na nuvem sobre o repositório privado, **commitar e fazer push** — a mensagem descreve o que mudou:

```
curadoria: <N> vencidas conferidas, <M> aposentadas, <K> contradições resolvidas
```

## Etapa 7 — Relatório

```
🧹 BRAIN — curadoria DD/MM/AAAA

🩺 Saúde: <erros e avisos antes> → <depois>
🔧 Consertado: <índice, wikilinks, frontmatter>
📅 Vencidas: N conferidas — <quais confirmadas, quais corrigidas>
📦 Aposentadas: <o que foi para arquivo/ e por quê>
🔀 Contradições: <o que conflitava, quem venceu, com que evidência>
⚠️ Precisa de você: <divergência que não deu para decidir sozinho>
```

---

## Contexto

- **Abilio Jr.** — NTICS, projetos culturais incentivados
- **Memória viva:** `brain/memory/` · **histórico:** `brain/memory/arquivo/`
- Validade por tipo: `project` 60d · `reference` 90d · `user` 180d · `feedback` 365d
- Responder sempre em português
- ⚠️ Rodando na nuvem, você **não** tem acesso à máquina do Abilio. Verificação de caminho local é impossível ali — nesse caso, marcar a memória como "a conferir localmente" em vez de afirmar que o caminho sumiu.
