# Painéis AEB — Sistema Completo de Gestão

Sistema completo de painéis de gestão para a Agência Espacial Brasileira (UO 24205), com **13 painéis** organizados por domínio, backend FastAPI modular e frontend React com TypeScript.

> **Status atual (Jun/2026):** Dashboard de Orçamento já está em produção com dados reais do Tesouro Gerencial via Supabase. Outros painéis ainda usam dados sintéticos.

---

## Arquitetura de Produção (Deploy Real)

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│   Vercel        │───────→│   Render.com    │───────→│   Supabase      │
│  (Frontend)     │  CORS   │  (Backend API)  │  REST   │  (PostgreSQL)   │
│ painel-vercel/  │         │  FastAPI        │         │  Dados Tesouro  │
└─────────────────┘         └─────────────────┘         └─────────────────┘
```

### URLs de Produção

| Componente | URL | Status |
|---|---|---|
| **Frontend (Vercel)** | `https://dashboard-one-snowy-70.vercel.app` | ✅ Online |
| **Backend (Render)** | `https://dashboard-api-x17n.onrender.com` | ✅ Online |
| **Supabase** | `https://jcmxxdbheuymophxyysk.supabase.co` | ✅ Online |

### Configuração de Deploy

#### Vercel (Frontend)
- **Root Directory:** `painel-vercel` (não `frontend/`) — HTML estático que conecta direto ao Supabase
- **Framework Preset:** "Other" (sem build)
- **Build Command:** vazio
- **Output Directory:** vazio
- Não precisa de variáveis de ambiente (chave anon do Supabase está no código)

> ⚠️ **IMPORTANTE:** O `frontend/` (React/Vite) foi descontinuado para o painel de orçamento. O dashboard ativo está em `painel-vercel/index.html`.

#### Render (Backend FastAPI)
- Variáveis de ambiente:
  - `SUPABASE_URL` = `https://jcmxxdbheuymophxyysk.supabase.co`
  - `SUPABASE_KEY` = `<anon key>`
  - `CORS_ORIGINS` = `https://dashboard-one-snowy-70.vercel.app`
- Comando de start: `uvicorn app.main:app --host 0.0.0.0 --port 10000`

#### Supabase (Banco de Dados)
- Tabela: `public.orcamento` — dados orçamentários do Tesouro Gerencial
- Views agregadas:
  - `orcamento_cards` — KPIs por ano/UO
  - `orcamento_por_acao` — execução por ação
- RLS habilitado para leitura pública via chave anon

---

## Painéis Disponíveis

| Grupo | Painel | Unidade(s) | Status |
|---|---|---|---|
| **Financeiro** | Orçamento / Execução | COF / DPOA / DGSE | ✅ **Dados reais do Tesouro** |
| **Financeiro** | Auditoria — Saldos Alongados | Auditoria (SIAFI) | 🟡 Dados sintéticos |
| **Administrativo** | Contratos e Aquisições | COAD / DCONT / DIAP / DIPA / DSG | 🟡 Dados sintéticos |
| **Administrativo** | RH — Gestão de Pessoas | CGP / DPOA-CGP | 🟡 Dados sintéticos |
| **Institucional** | Comunicação — ARI | ARI | 🟡 Dados sintéticos |
| **Institucional** | Eventos — GAB | GAB Presidência | 🟡 Dados sintéticos |
| **Institucional** | Publicações DOU | AUDIN | 🟡 Dados sintéticos |
| **Técnico** | Educação — AEB Escola | DGSE / DIEN / URRN | 🟡 Dados sintéticos |
| **Técnico** | Operações Espaciais | DGSE | 🟡 Dados sintéticos |
| **Técnico** | TransfereGov | URSJC | 🟡 Dados sintéticos |
| **Técnico** | Acordos Internacionais | ACI | 🟡 Dados sintéticos |
| **Estratégico** | Governança e Integridade | DPOA/Assessoria | 🟡 Dados sintéticos |
| **Estratégico** | Planejamento Estratégico — DGEP | DGEP | 🟡 Dados sintéticos |

---

## Estrutura do Projeto

```
paineis-fepese-main/
├── painel-vercel/              # 🎯 Dashboard Orçamento (HTML estático → Supabase)
│   └── index.html               # Painel ativo em produção
├── painel-aeb-orcamento/        # Versão anterior com dados estáticos (JSON embed)
│   └── painel_orcamento.html
├── sistema-paineis/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── services.py     # Fallback: psycopg2 → Supabase REST → dados locais
│   │   │   ├── supabase_rest.py # Cliente REST do Supabase (firewall)
│   │   │   ├── main.py          # FastAPI + CORS
│   │   │   └── dominios/        # 11 módulos por domínio
│   │   └── requirements.txt
│   ├── frontend/                # React/Vite (descontinuado para orçamento)
│   │   └── src/
│   └── vercel.json              # Configuração: aponta para painel-vercel/
├── supabase/
│   ├── views.sql                # Views agregadas (orcamento_cards, orcamento_por_acao)
│   └── seed_orcamento.py        # Script para popular dados do Tesouro
└── DEPLOY_SUPABASE_VERCEL.md   # Guia completo de deploy
```

---

## Principais Atualizações (Jun/2026)

### 1. Integração Supabase ✅
- Dados reais do Tesouro Gerencial carregados no Supabase
- Backend conecta via API REST (porta 443) devido a restrições de firewall
- Views SQL agregadas para evitar limite de 1000 linhas da API REST

### 2. Deploy Vercel + Render ✅
- Frontend na Vercel (HTML estático, sem build)
- Backend no Render.com (FastAPI)
- CORS configurado entre Vercel e Render

### 3. Fallback de Conexão ✅
O `services.py` tenta conexão em ordem:
1. **psycopg2** (PostgreSQL direto) — funciona em redes sem firewall
2. **Supabase REST API** (porta 443) — contorna firewall
3. **Dados locais** (CSV/JSON) — fallback offline

---

## Pendências / Próximos Passos

### 🔴 Prioridade Alta
1. **Design do painel de orçamento** — Replicar visual do Power BI exatamente:
   - Sidebar com filtros e menu ("Abrir Menu de Filtros", "Remover Filtros", etc.)
   - Logo AEB com círculo e satélite no header
   - Gráfico de linha para série histórica (com área preenchida)
   - Gauges semicirculares para indicadores
   - Gráfico de barras por diretoria
   - Fundo com estrelas (tema espacial)
   - Ver screenshot no arquivo `EXECUCAO - AEB - teste.xlsx` ou no Power BI original

2. **Painel de Transferências Voluntárias** — Criar segundo dashboard igual ao primeiro, mas com dados de TV (crédito recebido, empenhado, liquidado, pago)

### 🟡 Prioridade Média
3. Conectar outros 11 painéis ao Supabase ou APIs reais
4. Implementar autenticação (gov.br/SSO)
5. CI/CD com GitHub Actions

---

## Desenvolvimento Local

### Backend (porta 8000)

```powershell
cd backend
python -m pip install --user -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

### Frontend React (porta 5173) — Descontinuado para Orçamento

```powershell
cd frontend
npm install
npm run dev
```

> O `frontend/` ainda serve para os outros 12 painéis. O painel de orçamento usa `painel-vercel/index.html`.

---

## Variáveis de Ambiente

### Backend (.env)
```bash
SUPABASE_URL=https://jcmxxdbheuymophxyysk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
# DATABASE_URL=postgresql://... (opcional, para conexão direta)
```

---

## Fontes de Dados

| Fonte | Tipo | Status | Dados |
|---|---|---|---|
| **Supabase (Tesouro)** | PostgreSQL via REST | ✅ Ativo | Orçamento AEB UO 24205 |
| **Siconfi API** | REST (JSON) | 🟡 Futuro | MSC Orçamentária, RREO |
| **Portal da Transparência** | REST (JSON) | 🟡 Futuro | Despesas detalhadas |
| **SIAFI / Tesouro Gerencial** | Arquivos / WS | 🟡 Futuro | Saldos contábeis |

---

## Histórico de Deploy

| Data | Evento |
|---|---|
| Jun 2026 | Criação do projeto com dados sintéticos |
| Jun 2026 | Integração com Supabase e dados reais do Tesouro |
| Jun 2026 | Deploy backend no Render.com |
| Jun 2026 | Deploy frontend na Vercel (iterações de build/CORS) |
| Jun 2026 | Configuração final: `painel-vercel/` como root directory |

---

## Licença

Este projeto é propriedade da Agência Espacial Brasileira (AEB).

