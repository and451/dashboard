# PoC — Plataforma de Painéis AEB (Orçamento / SERPRO)

Prova de conceito que demonstra a arquitetura proposta em
`../_analise/PROPOSTA_ARQUITETURA.md`: um painel de **execução orçamentária**
(domínio do DaaS SERPRO / SIAFI, UO 24205) reconstruído como **frontend + backend
próprios**, documentado e programável, sem dependência de licenças do Power BI.

> Os dados são **sintéticos** (gerados em `backend/app/data.py`), com o mesmo formato
> dimensional da fonte real (programa, ação, PTRES, função, grupo de despesa, fonte;
> dotação/empenhado/liquidado/pago). Em produção, esse módulo seria substituído por um
> repositório que lê o Data Warehouse populado via ELT (Python + dbt).

## Estrutura

```
sistema-paineis/
  backend/    FastAPI (API + camada semântica + OpenAPI/Swagger)
  frontend/   React + TypeScript + Vite + ECharts
```

## Pré-requisitos
- Python 3.11+ (testado em 3.14)
- Node.js 18+ (testado em 24)

## 1. Backend (porta 8000)

```powershell
cd backend
python -m pip install --user -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000/api/v1/orcamento/kpis
- **Documentação interativa (Swagger):** http://localhost:8000/docs
- Esquema OpenAPI: http://localhost:8000/openapi.json

### Endpoints — Orçamento
| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Status |
| GET | `/api/v1/orcamento/dimensoes` | Valores para os filtros |
| GET | `/api/v1/orcamento/kpis` | Cards: dotação, empenhado, liquidado, pago, % |
| GET | `/api/v1/orcamento/serie-mensal` | Série mensal (linha) |
| GET | `/api/v1/orcamento/ranking?por=programa` | Ranking por dimensão (barras) |
| GET | `/api/v1/orcamento/registros` | Tabela detalhada (paginada) |

Todos aceitam filtros: `ano`, `programa`, `acao`, `funcao`, `grupo_despesa`, `fonte`.

### Endpoints — Auditoria (Saldos Alongados)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/auditoria/saldos-alongados` | Contas com saldo inalterado por N meses |
| GET | `/api/v1/auditoria/saldos-alongados/resumo` | Resumo agregado da auditoria |

Parâmetros: `meses` (3–36, default 12), `min_meses` (2–12, default 3).

## 2. Frontend (porta 5173)

```powershell
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173
- O Vite faz proxy de `/api` → `http://localhost:8000` (ver `vite.config.ts`).
- Build de produção: `npm run build` (saída em `dist/`).

## O que o PoC demonstra
- **Camada semântica única** (regras de negócio centralizadas em `services.py`).
- **API documentada** automaticamente (OpenAPI/Swagger) — resolve a falta de documentação.
- **Frontend acessível** com KPIs, série temporal e rankings, filtros dinâmicos.
- **Sem licença por usuário**: qualquer pessoa acessa via navegador.

## 3. APIs alternativas ao DaaS SERPRO

O sistema foi projetado para consumir múltiplas fontes de dados orçamentários, reduzindo a dependência exclusiva do DaaS SERPRO:

| Fonte | Tipo | Autenticação | Dados | URL |
|---|---|---|---|---|
| **Siconfi API** | REST (JSON) | Não | MSC Orçamentária, RREO | `http://apidatalake.tesouro.gov.br/docs/siconfi/` |
| **Portal da Transparência** | REST (JSON) | Chave de API | Despesas (empenho/liq/pag) | `https://portaldatransparencia.gov.br/api-de-dados` |
| **Tesouro Transparente** | REST (JSON) | Não | RREO, relatórios fiscais | `https://www.tesourotransparente.gov.br` |
| **SIAFI / Tesouro Gerencial** | Arquivos / Web Services | Gov.br | Saldos contábeis, execução | Acesso interno via SIAFI Web |
| **DaaS SERPRO** | SQL/ODBC | Paga | Tabelas `WD_*` | Via contrato SERPRO |

A lógica de auditoria (`backend/app/auditoria.py`) consome dados sintéticos no PoC, mas já está estruturada para receber:
- Arquivos Excel exportados do SIAFI / Tesouro Gerencial (via `renomeia_arquivos`)
- Respostas da API Siconfi (`/msc_orcamentaria`)
- Respostas da API Portal da Transparência (detalhamento de despesas)

## Próximos passos (para virar produção)
1. Substituir `data.py` por leitura do Data Warehouse (PostgreSQL) populado por **ELT (dbt)**.
2. Implementar conectores para **API Siconfi** e **Portal da Transparência** como fontes primárias.
3. Manter o **DaaS SERPRO** como fonte complementar/validação (tabelas `WD_*`).
4. Adicionar **autenticação gov.br/SSO + RBAC** e auditoria (LGPD).
5. Aplicar o **Design System gov.br** e validar acessibilidade (eMAG).
6. CI/CD, testes (pytest/vitest) e observabilidade.
