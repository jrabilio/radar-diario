# Workflow: Controle Financeiro Pessoal

## Objetivo
Manter o controle financeiro em dia com esforço quase zero: importar extratos, resolver a
fila de classificação e fechar o mês. A meta da spec é **menos de 15 minutos** do download
dos arquivos ao relatório pronto, contra mais de 1 hora no processo manual.

## Onde mora
Aplicativo em [financas/](../financas/). É um app coeso, não um conjunto de tools soltas —
por isso tem estrutura própria, dependências próprias e ponto de entrada próprio.

- Especificação: [financas/docs/spec-app-financas.md](../financas/docs/spec-app-financas.md)
- Regras vinculantes para quem edita o código: [financas/CLAUDE.md](../financas/CLAUDE.md)
- Decisões de implementação e ambiguidades resolvidas: [financas/docs/decisoes.md](../financas/docs/decisoes.md)

**Estado: Fase 1 (núcleo).** A projeção de saldo e o simulador, que são o produto final,
são da Fase 2 e ainda não existem.

## Inputs necessários
- Extratos e faturas exportados por você, em **OFX ou CSV**. O sistema **não faz login em
  banco** — sem scraping, sem Open Finance, sem credencial armazenada (spec, seção 4).
- `financas/config/contas_seed.json` preenchido com o resultado da Fase 0.
- Nada de `.env`. A Fase 1 não usa API nenhuma.

## Pré-requisito bloqueante: Fase 0

**Não rode nada antes disso.** Preencha
[financas/docs/fase-0-inventario.md](../financas/docs/fase-0-inventario.md): para cada
conta e cartão, o formato que a instituição exporta, a entidade dona (PF, ECO, SB), a moeda
em que a fatura é paga, e os dias de fechamento e vencimento.

Enquanto não estiver preenchido, `./fin conta list` mostra `ok = NAO` e todo relatório avisa
que os números não são confiáveis. Isso é proposital: entidade ou moeda erradas corrompem o
custo de vida silenciosamente.

## Passos

### Rotina semanal — 10 minutos

1. Baixe os arquivos disponíveis das contas ativas.
2. Importe cada um:
   ```bash
   cd financas
   ./fin importar --conta <id> --arquivo <caminho>
   ```
   Para conta nova ou layout de CSV ainda não conferido, rode antes com `--simular`: ele
   processa e reporta sem gravar nada.
3. Resolva a fila: `./fin pendencias`
4. Ensine o sistema em vez de classificar caso a caso. Uma regra resolve todas as
   ocorrências futuras:
   ```bash
   ./fin categoria list
   ./fin regra add --padrao IFOOD --categoria 10
   ```

### Rotina mensal — 20 minutos

5. Registre transferências que o extrato não identifica sozinho:
   ```bash
   ./fin transferir --tipo aporte --data 25/03/2026 --conta-origem 9 \
                    --valor 5000,00 --destino-externo XP
   ```
6. Feche o mês nos dois regimes:
   ```bash
   ./fin mes --competencia 2026-03                       # caixa: quanto saiu da conta
   ./fin mes --competencia 2026-03 --regime competencia  # quanto eu gastei
   ```

## Saída esperada
- **Formato:** relatório no terminal, uma seção por moeda de liquidação.
- **Destino:** banco SQLite local em `financas/dados/financas.db`, com backup automático
  antes de cada importação. Nada vai para nuvem — são dados financeiros pessoais.

## Edge cases

- **"arquivo já importado"** → é o comportamento correto. A importação é idempotente por
  design; rodar duas vezes não duplica nada.
- **Layout de CSV não casa** → o adaptador imprime o cabeçalho real do seu arquivo. Corrija
  o bloco em `financas/config/csv_layouts.json` com base nele e marque `"verificado": true`.
- **Aviso de layout não verificado** → os layouts de Capital One, Chase e Apple Card foram
  escritos de memória e nunca conferidos contra export real. Confira os valores contra o
  total impresso na fatura antes de confiar.
- **PDF** → não implementado na Fase 1. A leitura de PDF depende da API do Claude e a spec
  define a Fase 1 como "sem LLM". Use OFX/CSV, ou `./fin lancar` para lançamento manual.
- **Moeda diferente da conta** → a importação falha de propósito. O sistema nunca converte
  moeda, e nunca soma BRL com USD. Consolidar seria inventar um número que não existe.
- **"parcelamento não detectado"** → compra cara no cartão que entrou como à vista. Se foi
  parcelada e passar batido, a projeção erra por meses. Confira na fatura.
- **Mês marcado como não confiável** → há compra sem classificação. O custo de vida está
  incompleto até a fila ser resolvida.

## Aprendizados

- **Use `./fin`, nunca o comando `financas`.** Nesta máquina os arquivos `.pth` nascem com a
  flag `UF_HIDDEN` do macOS e o `site.py` do Python ignora `.pth` oculto, o que quebra a
  instalação editável a cada `uv sync`. Detalhe em `financas/docs/decisoes.md`, D7.
- **O motor de regras começa vazio e é assim mesmo.** A ferramenta anterior não exporta
  dados, então não há histórico para importar (spec, seção 18). A classificação automática
  só chega aos 85% depois de dois a três meses de uso. É custo aceito, não problema.
- **Fixtures são sintéticas.** Ninguém testou o parser contra um extrato real do Itaú ou do
  Chase. Na primeira importação de cada conta nova, use `--simular` e confira os totais.
- **Python 3.12 via `uv`**, isolado do sistema. O Python 3.9 do macOS não atende a spec.
