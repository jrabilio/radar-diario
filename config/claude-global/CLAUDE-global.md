# Instruções Globais — Abilio Jr.

## Identidade do Usuário

Meu nome é Abilio Jr. Trabalho com vendas, gestão de clientes e operações. Responda sempre em português. Seja direto em perguntas simples e detalhado em pesquisa/estratégia. Nunca invente informações — cite fontes quando fizer afirmações factuais.

## SecondBrain

Base de conhecimento local em `/Users/abiliomartins/Projetos/ABILIO'S SPACE/brain/`.

Quando a tarefa envolver contexto histórico de cliente, projeto ou decisão passada:
1. Ler `INDEX.md` primeiro para navegar até a nota específica
2. Nunca carregar o brain inteiro — ir direto à pasta/arquivo relevante
3. Estrutura: `clientes/`, `projetos/`, `atas-reuniao/`, `decisoes/`, `conhecimento/`, `referencias/`

## Sistema de Memória Persistente

Memória em `/Users/abiliomartins/Projetos/ABILIO'S SPACE/brain/memory/`.

### Leitura no início da sessão

Ao iniciar sessão, ler `memory/MEMORY.md` para identificar memórias relevantes à tarefa. Ler os arquivos específicos referenciados, não todos.

### Tipos de Memória

- **`user_*.md`** — perfil do usuário: papel, preferências, contexto profissional
- **`project_*.md`** — contexto de projeto: objetivos, stakeholders, decisões, prazos. Converter datas relativas para absolutas.
- **`feedback_*.md`** — correções e validações. Salvar quando Abilio corrigir uma abordagem ou validar decisão não-óbvia.
- **`reference_*.md`** — ponteiros para sistemas externos (onde ficam coisas, credenciais, dashboards)

### Formato de Arquivo de Memória

```markdown
---
name: nome-curto
description: uma linha específica que ajude a decidir relevância em sessões futuras
type: user | project | feedback | reference
---

[corpo — para feedback/project usar **Why:** e **How to apply:**]
```

### Quando Salvar — Papel da rotina

**Não criar arquivos de memória durante a sessão.** A consolidação é responsabilidade da rotina `brain-capturar` (a cada 24h). Na sessão, quando houver aprendizado relevante:
1. Apresentar o aprendizado no chat de forma clara (como regra, diagnóstico ou decisão)
2. Mencionar que a rotina vai consolidar na próxima rodada
3. Não criar arquivos `.md` avulsos de memória

> Ver `feedback_nao-criar-arquivo-de-memoria-na-sessao.md` para o contexto completo.

**Exceção:** se Abilio explicitamente pedir "salva isso num arquivo" referindo-se a um documento de trabalho real (não à memória do sistema), criar normalmente em pasta adequada.

### O Que NÃO Salvar

- Padrões de código, convenções, arquitetura, paths — derivam do repo
- Histórico git — `git log` resolve
- Receita de bug/fix — o fix está no código
- Coisas já documentadas neste CLAUDE.md
- Estado efêmero da conversa atual (use TodoList, não memória)

Se Abilio pedir para salvar algo dessa lista, perguntar: "o que foi surpreendente ou não-óbvio sobre isso? Essa parte vale memória."

### Regras Anti-Duplicata

Antes de salvar memória nova, checar MEMORY.md se já existe sobre o tema. Preferir atualizar > criar duplicata.

### MEMORY.md é só índice

Uma linha por entrada: `- [Título](arquivo.md) — gancho de uma frase`. Nunca escrever conteúdo de memória direto no MEMORY.md. Manter abaixo de 200 linhas.

### Antes de Aplicar Memória Existente

- Memória que cita arquivo/função/flag = snapshot congelado. Verificar antes de recomendar.
- Se memória conflita com observação atual: confiar no observado e atualizar/remover a memória stale.

## Retroalimentação do Brain (Consolidação Automática)

O hook `SessionStart` já injeta o estado do brain e avisa quando há captura ou curadoria
pendente — não é preciso checar flag manualmente. Quando o aviso aparecer:
1. Rodar a skill `brain-capturar` (ou `brain-curar`) como subagent em background
2. Deletar a flag: `rm ~/.claude/.brain-pending` (ou `.brain-curar-pending`)

A `brain-capturar` lê transcrições recentes, extrai padrões (correções, decisões, preferências) e atualiza os arquivos de memória. Roda automaticamente a cada 24h.

## Protocolo de Revisão Pré-Execução

Antes de rodar qualquer workflow não-trivial:
1. Identificar pelo MEMORY.md quais `feedback_*.md` são relevantes à área
2. Ler antes de começar
3. Aplicar regras já conhecidas sem esperar nova correção

## Memória vs. Outras Formas de Persistência

- Decisão sobre abordagem atual → Plan/TodoList, não memória
- Lista de passos da tarefa atual → TodoWrite, não memória
- Algo que importa em sessões futuras → memória
