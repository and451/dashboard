# Ponte de Dados Reais — do `_extracao/` para o sistema

> Substitui gradualmente os `*_data.py` sintéticos por dados reais extraídos dos
> painéis Power BI (engenharia reversa do `DataModel` via pbixray — ver
> `../_analise/extract_datamodel.py` e `../_extracao/`).

## Domínios com ponte de dados reais — CONCLUÍDOS

### 1. Contratos (COAD/DSG) — CONCLUÍDO

**Padrão aplicado (sem quebrar nada):** trocou-se apenas a *fonte* dos dados;
`schemas.py`, `contratos_services.py`, os endpoints e o frontend (`ContratosPage`)
ficaram **intactos**. Só `contratos_data.py` mudou + uma pasta de dados.

- Dados reais em `backend/app/dados_reais/contratos_dsg/` (11 CSVs do painel
  "Panorama de Contratos - DSG", copiados de `_extracao/COAD/DSG/.../dados/`).
- `contratos_data.py` agora lê e **normaliza** esses CSVs para o schema `Contrato`
  (stdlib `csv`, sem pandas). Dois formatos de origem tratados:
  1. `<Serviço> - Contratos` (Contratada/Instrumento/Valor_instrumento/...) →
     agrupado por fornecedor, com Termos Aditivos dobrados em `aditivos`.
  2. `Contratações Gerais - DSG` (Empresa/Objeto/Valor do Contrato/...) → 1:1.
- Há **fallback para o gerador sintético** se a pasta de dados não existir
  (mantém o sistema rodável na VM antes de copiar os dados).
- Resultado: **29 contratos reais** (Money Turismo, Ágil Vigilância, Correios,
  Claro, Água Mineral Prime...), KPIs reais, 9/9 testes passando.

#### Execução real (CONCLUÍDO)
- `pct_execucao` e `saldo_executar` agora vêm do **join Contratos ↔ Empenhos ↔
  Pagamentos** (ligação por `ID_contrato`); a consolidada cruza com "Controle de
  Empenhos" por Número do Processo. Resultado: 25 contratos, execução média ~57,5%.
- `pct` é limitado a 0–100% e `saldo` a ≥ 0 (alguns contratos plurianuais têm
  pagamentos acumulados > empenho capturado — lacuna na origem; brutos preservados).
- Dedup robusto: fornecedor normalizado + valor ao milhar, **preferindo o registro
  consolidado** (mais rico) sobre o por-serviço.

#### Limitações remanescentes
- `area` só tem `DSG`. Os demais contratos da COAD (DCONT/DIAP/DIPA) têm painéis
  próprios e podem ser anexados na mesma normalização.
- `modalidade` do formato por-serviço fica "Não informado" (a origem não traz);
  `empenhado`/`pago` brutos não são expostos no schema `Contrato` atual (campos
  candidatos a adicionar em `schemas.py`/`api.ts`).

### 2. TransfereGov (URSJC) — CONCLUÍDO

**Padrão aplicado:** mesmo que Contratos — apenas `transferegov_data.py` mudou + pasta de dados.

- Dados reais em `backend/app/dados_reais/transferegov/` (4 CSVs do painel
  "URSJC-Painel de Programas - TransfereGov", copiados de `_extracao/URSJC/.../dados/`):
  - `programas.csv` — programas e metas
  - `planos_acao.csv` — planos de ação e valores
  - `trfs.csv` — transferências financeiras (TRFs)
  - `programacoes_financeiras.csv` — **ponte** id_programacao → id_plano_acao
- `transferegov_data.py` lê e **normaliza** esses CSVs para o schema `ProgramaTransfere`,
  com join programas → planos → TRFs para `valor_total`, `valor_executado` e `pct_execucao`.
- Há **fallback para o gerador sintético** se a pasta de dados não existir.
- Resultado: **63 programas reais**, R$ 382M programado, **R$ 116M executado**.

#### Correção do join de execução (CONCLUÍDO)
- A primeira versão joinava `trfs.id_programacao` direto contra `id_plano_acao`
  (chaves distintas) → `valor_executado` ≈ R$ 105k (quase zero). **Corrigido**: a
  TRF referencia `id_programacao`, que a tabela `programacoes_financeiras` liga a
  `id_plano_acao`. Após a correção: **R$ 116M executado** (≈ total TRF004 R$ 118,9M),
  35 programas com execução. `pct` limitado a 0–100% (execução plurianual).

#### Limitações remanescentes
- `repasses` ainda usa contagem de TRFs (não o valor detalhado por convenente).
- `dt_inicio` e `dt_fim_prevista` ficam vazios (requer join com `metas.csv` ou `termos_execucao.csv`).
- `gerar_repasses()` permanece sintética (join mais complexo com `notas_credito.csv`).

### 3. Orçamento / Execução (COF) — CONCLUÍDO

**Padrão aplicado:** apenas `app/data.py` mudou + uma pasta de dados; `services.py`,
endpoints e `OrcamentoPage` intactos.

- Dados reais em `backend/app/dados_reais/orcamento_cof/Base_Orcamentaria.csv`
  (extraído do painel COF; base SIAFI/Tesouro Gerencial, 11.065 linhas, enxugado
  para ~15 colúnas → 2 MB).
- A base é **formato longo (EAV)**: cada linha é uma fase orçamentária
  (`CO_ITEM_INFORMACAO`) com valor em `SALDORITEMINFORMAO`. `data.py` **pivota** as
  fases para o schema `Registro`: 9→dotação inicial, 13→dotação atual,
  29→empenhado, 31→liquidado, 34→pago.
- Dimensões reais: programa (Cod+Título), ação, PTRES, função, grupo de despesa e
  **fonte = resultado primário** (`NO_IN_RESULTADO_LEI_CEOR`, proxy — não há coluna
  de fonte de recursos na base). UO 24205.
- Há **fallback sintético** se o CSV não existir.
- Resultado: **725 registros**, anos 2016–2026. Ex. 2024: dotação R$ 135,6M,
  empenhado 99,3%, liquidado 58,2%, pago 55,6%; Programa Espacial Brasileiro R$ 93,5M.

#### Limitações conhecidas desta etapa
- A base tem **um snapshot por ano** (mês 14 fechamento; 2026 no mês 6), não mensal.
  Mapeado para mês 12/6 → a "série mensal" vira 1 ponto por ano (KPIs e rankings
  corretos; o gráfico de série poderia virar "por ano" no frontend).
- `funcao` fica só com o código (a base não traz o nome da função).

## Como replicar para outro domínio
1. Em `_extracao/<UNIDADE>/<...>/<Painel>/` identifique as tabelas-fonte
   (`schema.csv`, `resumo.json`) e os CSVs em `dados/`.
2. Copie os CSVs necessários para `backend/app/dados_reais/<dominio>/`.
3. No `<dominio>_data.py`, escreva `_carregar_reais()` que lê os CSVs e mapeia
   para o schema Pydantic do domínio; mantenha o sintético como fallback.
4. Não altere services/endpoints/frontend se o schema for preservado.

## Próximos candidatos (alto valor, dados volumosos já extraídos)
- **DGSE - orçamento** (~419 mil linhas) e **DIEN AEB Escola** (~258 mil).
- **COAD/DCONT/DIAP/DIPA** — anexar os demais contratos da COAD ao domínio Contratos.
- Expor `empenhado`/`pago` no schema `Contrato` (e `Registro`) para os gráficos.
