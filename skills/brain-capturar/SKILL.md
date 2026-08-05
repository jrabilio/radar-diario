---
name: brain-capturar
description: Consolidação de memória do Abilio — lê as sessões interativas recentes, extrai só o que muda o comportamento em sessões futuras, e grava no brain resolvendo contradições com o que já existe. Roda a cada 24h via hook local. Substitui a skill `dream`.
---

# brain-capturar — captura diária

Você é o sistema de consolidação de memória do Abilio Jr. Roda **localmente**, porque só esta máquina tem as transcrições das conversas.

**Regra absoluta:** só salvar o que muda como o Claude se comporta nas próximas sessões. Quantidade não é qualidade — 1 aprendizado real vale mais que 10 registros de operação.

> Esta skill substitui a `dream`. Herda o filtro de utilidade e a etapa de otimização da versão que rodava no Cowork (`dream-memory-consolidation`), e acrescenta o **protocolo de contradição** e o **gate de saúde** — as duas coisas cuja falta deixou o brain com memórias se contradizendo por dois meses.

---

## Etapa 1 — Ler as sessões

```bash
python3 tools/brain_sessions.py
```

Devolve JSON com as sessões desde a última captura, já filtrado: só falas humanas (num arquivo típico, 92% dos registros `type: user` são resultado de ferramenta, não fala do Abilio), sem subagentes, sem system-reminder, e **sem as sessões da própria rotina** — senão a memória se retroalimenta com o próprio raciocínio.

Se não vier nenhuma sessão, pule para a Etapa 5 e reporte isso.

## Etapa 2 — Filtro de utilidade

Para cada padrão identificado, aplicar o teste:

> **"Isso muda como o Claude vai se comportar nas próximas sessões?"**

**Vale salvar**
- Correção explícita ("não é assim", "para de fazer", "prefiro", "muda")
- Validação de abordagem não-óbvia ("perfeito", "exatamente assim", "isso sim")
- Decisão sobre workflow ou automação com impacto futuro
- Contexto de cliente/projeto necessário para entender pedidos futuros
- Fato descoberto sobre um sistema que contradiz o que estava registrado

**Não vale salvar**
- Detalhe de implementação que não afeta comportamento
- Registro de "o que aconteceu hoje" sem implicação prática
- Informação já coberta por arquivo existente
- Estado efêmero (tarefa rodou, tarefa falhou, arquivo foi movido)
- Padrão de código, path, convenção — deriva do repo

## Etapa 3 — Protocolo de contradição ⚠️

**Esta é a etapa que não existia, e a ausência dela custou caro.** Em 04/08/2026 a auditoria achou `reference_pmo-processo-ntics.md` (02/05) afirmando que o ClickUp *é* a fonte da verdade e `project_pmo-planejamento-mensal.md` (04/07) afirmando que *não é*. As duas conviveram dois meses. O Dream escreveu a segunda e nunca revisitou a primeira.

Antes de gravar qualquer memória que afirme um fato sobre sistema, processo, caminho ou estado:

1. **Procurar** o que já existe sobre o assunto:
   ```bash
   grep -ril "<assunto>" brain/memory/
   ```
2. **Ler** os arquivos que aparecerem. Se algum afirmar algo incompatível, **resolver explicitamente** — escolha uma:
   - **(a) atualizar no lugar** — quando é o mesmo assunto e o arquivo continua sendo o dono dele. Preferir sempre que der.
   - **(b) marcar a antiga** com um bloco datado, apontando para onde está a verdade agora:
     ```markdown
     > ⚠️ **Correção de DD/MM/AAAA — <o que mudou>.**
     > Este arquivo afirmava <X>. <Evidência do contrário>.
     > Vale o registro mais recente: <Y>.
     ```
   - **(c) mover para `brain/memory/arquivo/`** — quando a memória inteira virou histórico, não só um trecho.
3. **Nunca deixar as duas de pé.** Se você não conseguir decidir qual está certa, grave a nova, marque a antiga com a divergência e **reporte no status final** para o Abilio decidir.

## Etapa 4 — Escrever

Destino por natureza do aprendizado:

| O que é | Onde vai |
|---|---|
| Correção ou validação de abordagem | `feedback_*.md` |
| Contexto de cliente ou projeto | `project_*.md` |
| Sistema externo, credencial, onde as coisas ficam | `reference_*.md` |
| Preferência ou perfil | `user_perfil.md` |

Checar o `MEMORY.md` antes de criar — **preferir atualizar > criar duplicata**.

Formato obrigatório:

```markdown
---
name: nome-curto
description: uma linha específica que ajude a decidir relevância no futuro
type: user | project | feedback | reference
status: vivo
revisar_em: AAAA-MM-DD
fonte: sessão <id-curto> · AAAA-MM-DD
---

[corpo]

**Why:** [por que isso importa]
**How to apply:** [quando e como usar]
```

`revisar_em` = hoje + validade do tipo: `project` 60d · `reference` 90d · `user` 180d · `feedback` 365d.

**Não escrever conteúdo no `MEMORY.md`** — ele é só índice, uma linha por entrada, no formato `- [arquivo.md](arquivo.md) — gancho de uma frase`. Manter abaixo de 200 linhas.

## Etapa 5 — Gate de saúde

```bash
python3 tools/brain_check.py
```

**Não encerre com erro em pé.** Código de saída 1 significa índice quebrado, wikilink morto ou frontmatter inválido — conserte antes de terminar. Código 2 são avisos: resolva os que couberem na captura e deixe o resto para a curadoria semanal.

Depois, carimbar a data:

```bash
date +%F > brain/memory/.ultima-captura
```

Esse arquivo é o que alimenta o watchdog. Sem ele, a próxima sessão avisa que a captura nunca rodou.

## Etapa 5b — Espelhar no Drive

```bash
python3 tools/brain_sync_drive.py
```

Espelho de ida para o Google Drive, na conta definida em `BRAIN_DRIVE_CONTA` no `.env` da raiz. O brain passa a existir em dois lugares — se este Mac morrer, a memória não morre junto.

O que pode acontecer:

| Saída | O que significa | O que fazer |
|---|---|---|
| código 2 | a conta não está montada no Drive | não é falha da captura — reporte no status e siga |
| `RECUSADO` | a trava barrou: brain local pequeno demais, ou o sync apagaria >30% do Drive | **não use `--force` por conta própria** — significa que algo está errado na origem. Investigue e leve ao Abilio |
| sucesso | espelhado | anote quantos arquivos mudaram para o status |

⚠️ O Abilio **não edita nada no Drive**. Se o tool avisar que há arquivos mais novos lá, é sintoma de problema (outro dispositivo, sync mal resolvido) — reporte em vez de ignorar.

## Etapa 6 — Status final

O Abilio confere as automações no começo do dia e quer algo escaneável em 30 segundos (`feedback_resumo-fim-de-automacao.md`). Terminar assim:

```
🧠 BRAIN — captura DD/MM/AAAA

✅ Lido: N sessões, M falas
📝 Salvo: <arquivo> — <por que passou no filtro>
🔀 Contradição: <o que conflitava e como foi resolvido>   (se houve)
🗑️ Descartado: <o que apareceu e não valeu, e por quê>
⚠️ Atenção: <o que precisa de decisão sua>                (se houver)
🩺 Saúde: <saída do brain_check>
🔄 Drive: <N arquivos atualizados · ou o motivo de não ter espelhado>
```

Sempre listar o **descartado**. É o que mostra que o filtro funcionou em vez de ter passado batido.

---

## Contexto

- **Abilio Jr.** — NTICS, projetos culturais incentivados
- **Brain:** `/Users/abiliomartins/Projetos/ABILIO'S SPACE/brain/`
- **Memória viva:** `brain/memory/` · **histórico:** `brain/memory/arquivo/`
- Responder sempre em português
- ⚠️ O remote deste repo é **público**. `brain/` está no `.gitignore` — nunca versionar memória aqui.
