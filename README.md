# Painéis AEB — Sistema Completo de Gestão

Sistema completo de painéis de gestão para a Agência Espacial Brasileira (UO 24205), com **13 painéis** organizados por domínio, backend FastAPI modular e frontend React com TypeScript.

> **Dados sintéticos** gerados para PoC. Em produção, substituir por conexão com Data Warehouse ou APIs governamentais (Siconfi, Portal da Transparência, SIAFI).

## Painéis Disponíveis

| Grupo | Painel | Unidade(s) |
|---|---|---|
| **Financeiro** | Orçamento / Execução | COF / DPOA / DGSE |
| **Financeiro** | Auditoria — Saldos Alongados | Auditoria (SIAFI) |
| **Administrativo** | Contratos e Aquisições | COAD / DCONT / DIAP / DIPA / DSG |
| **Administrativo** | RH — Gestão de Pessoas | CGP / DPOA-CGP |
| **Institucional** | Comunicação — ARI | ARI |
| **Institucional** | Eventos — GAB | GAB Presidência |
| **Institucional** | Publicações DOU | AUDIN |
| **Técnico** | Educação — AEB Escola | DGSE / DIEN / URRN |
| **Técnico** | Operações Espaciais | DGSE |
| **Técnico** | TransfereGov | URSJC |
| **Técnico** | Acordos Internacionais | ACI |
| **Estratégico** | Governança e Integridade | DPOA/Assessoria |
| **Estratégico** | Planejamento Estratégico — DGEP | DGEP |

## Estrutura do Projeto

```
sistema-paineis/
├── backend/
│   ├── app/
│   │   ├── dominios/          # 11 módulos por domínio
│   │   │   ├── contratos_*
│   │   │   ├── rh_*
│   │   │   ├── comunicacao_*
│   │   │   ├── educacao_*
│   │   │   ├── operacoes_*
│   │   │   ├── governanca_*
│   │   │   ├── eventos_*
│   │   │   ├── transferegov_*
│   │   │   ├── dou_*
│   │   │   ├── acordo_*
│   │   │   └── dgep_*
│   │   ├── auditoria.py       # Lógica de saldos alongados
│   │   ├── main.py            # 40+ endpoints FastAPI
│   │   └── schemas.py         # 30+ schemas Pydantic
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api.ts             # Cliente API com todos os endpoints
│   │   ├── App.tsx            # Menu lateral com 13 painéis
│   │   ├── pages/             # 13 páginas React
│   │   └── components/        # EChart wrapper
│   ├── .env.example
│   └── package.json
├── vercel.json                # Configuração Vercel
└── README.md
```

## Pré-requisitos

- **Python 3.11+** (testado em 3.14)
- **Node.js 18+** (testado em 24)

## Desenvolvimento Local

### 1. Backend (porta 8000)

```powershell
cd backend
python -m pip install --user -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- **Documentação Swagger:** http://localhost:8000/docs
- **OpenAPI Schema:** http://localhost:8000/openapi.json

### 2. Frontend (porta 5173)

```powershell
cd frontend
npm install
npm run dev
```

- App: http://localhost:5173
- O Vite faz proxy de `/api` → `http://localhost:8000` (ver `vite.config.ts`).
- Build de produção: `npm run build` (saída em `dist/`).

## Endpoints da API

### Orçamento
| Método | Rota | Descrição |
|---|---|---|
| GET | `/health` | Status |
| GET | `/api/v1/orcamento/dimensoes` | Valores para filtros |
| GET | `/api/v1/orcamento/kpis` | KPIs: dotação, empenhado, liquidado, pago |
| GET | `/api/v1/orcamento/serie-mensal` | Série mensal |
| GET | `/api/v1/orcamento/ranking?por=programa` | Ranking por dimensão |
| GET | `/api/v1/orcamento/registros` | Tabela detalhada |

Filtros: `ano`, `programa`, `acao`, `funcao`, `grupo_despesa`, `fonte`.

### Auditoria (Saldos Alongados)
| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/v1/auditoria/saldos-alongados` | Contas com saldo inalterado |
| GET | `/api/v1/auditoria/saldos-alongados/resumo` | Resumo agregado |

Parâmetros: `meses` (3–36, default 12), `min_meses` (2–12, default 3).

### Outros Domínios
Cada domínio possui endpoints similares:
- `/api/v1/{dominio}/kpis` — KPIs agregados
- `/api/v1/{dominio}` — Dados detalhados
- `/api/v1/{dominio}/por-{agregacao}` — Agregações (status, área, país, etc.)

Domínios: `contratos`, `rh`, `comunicacao`, `educacao`, `operacoes`, `governanca`, `eventos`, `transferegov`, `dou`, `acordos`, `dgep`.

## Deploy em Produção

### Opção 1: Vercel (Frontend) + Servidor Python (Backend)

#### Frontend no Vercel

1. Conecte o repositório ao Vercel
2. Configure as variáveis de ambiente:
   - `VITE_API_URL`: URL do backend em produção
3. O arquivo `vercel.json` já está configurado para build automático

#### Backend em Servidor Python

Opções: Railway, Render, AWS, Azure, ou servidor próprio.

**Exemplo com Railway:**

```bash
# Instale Railway CLI
npm install -g @railway/cli

# Login e criar projeto
railway login
railway init

# Adicionar backend
railway add backend
railway up

# Configurar porta 8000 e comando de start
railway variables set PORT=8000
railway variables set COMMAND="uvicorn app.main:app --host 0.0.0.0 --port $PORT"
```

### Opção 2: Vercel + Supabase (Backend + Banco)

1. **Criar projeto Supabase**
   - Crie um projeto em https://supabase.com
   - Obtenha `SUPABASE_URL` e `SUPABASE_ANON_KEY`

2. **Adicionar extensão pgREST**
   - Supabase já inclui pgREST (API REST automática)

3. **Migrar dados para Supabase**
   - Use o SQL Editor para criar tabelas equivalentes aos schemas Pydantic
   - Importe dados dos módulos sintéticos ou conecte a fontes reais

4. **Configurar frontend**
   - `VITE_API_URL`: URL do Supabase (ex: `https://xxx.supabase.co`)
   - Atualize `api.ts` para usar cliente Supabase em vez de fetch

### Opção 3: Docker (Backend + Frontend em um container)

```dockerfile
# Dockerfile (raiz do projeto)
FROM node:18 AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.14
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ ./
COPY --from=frontend /app/frontend/dist ./static
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t paineis-aeb .
docker run -p 8000:8000 paineis-aeb
```

## Variáveis de Ambiente

### Frontend
```bash
VITE_API_URL=http://localhost:8000  # Desenvolvimento
VITE_API_URL=https://api.exemplo.com  # Produção
```

### Backend (opcional)
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SUPABASE_URL=...
SUPABASE_KEY=...
```

## Fontes de Dados em Produção

O sistema foi projetado para consumir múltiplas fontes:

| Fonte | Tipo | Autenticação | Dados |
|---|---|---|---|
| **Siconfi API** | REST (JSON) | Não | MSC Orçamentária, RREO |
| **Portal da Transparência** | REST (JSON) | Chave de API | Despesas (empenho/liq/pag) |
| **Tesouro Transparente** | REST (JSON) | Não | RREO, relatórios fiscais |
| **SIAFI / Tesouro Gerencial** | Arquivos / Web Services | Gov.br | Saldos contábeis, execução |
| **DaaS SERPRO** | SQL/ODBC | Paga | Tabelas `WD_*` |

## Próximos Passos

1. **Substituir dados sintéticos** por conexão com Data Warehouse ou APIs reais
2. **Implementar autenticação** (gov.br/SSO + RBAC) e auditoria (LGPD)
3. **Aplicar Design System gov.br** e validar acessibilidade (eMAG)
4. **CI/CD**: GitHub Actions para testes e deploy automático
5. **Testes**: pytest (backend) + vitest (frontend)
6. **Observabilidade**: logs, métricas e tracing

## Licença

Este projeto é propriedade da Agência Espacial Brasileira (AEB).
