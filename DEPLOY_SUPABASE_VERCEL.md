# Deploy Supabase + Vercel — Guia Passo a Passo

> Alternativa ao Render: Supabase (PostgreSQL + API REST) + Vercel (Frontend).
> O backend FastAPI continua servindo os dados dos outros domínios; o Supabase
> substitui apenas a fonte de dados do Orçamento (Tesouro/SIAFI).

---

## 1. Criar projeto no Supabase

1. Acesse https://supabase.com e crie uma conta (ou login com GitHub)
2. Clique em **New Project**
3. Escolha:
   - **Name**: `paineis-aeb` (ou qualquer nome)
   - **Database Password**: gere uma senha forte (salve em local seguro)
   - **Region**: `South America (São Paulo)` — latência menor
4. Aguarde a criação (~2 minutos)

---

## 2. Criar a tabela no Supabase

1. No projeto Supabase, vá em **SQL Editor** (menu lateral)
2. Cole o conteúdo de `supabase/schema.sql`
3. Clique em **Run** — isso cria a tabela `public.orcamento` com índices e RLS

---

## 3. Carregar os dados do Tesouro

### 3.1 Instalar dependências

```bash
cd supabase
pip install -r requirements.txt   # psycopg2-binary
```

### 3.2 Obter a Connection String

1. No Supabase, vá em **Project Settings** → **Database**
2. Em **Connection string**, copie a URI:
   ```
   postgresql://postgres.xxxx:[SENHA]@aws-0-sa-east-1.pooler.supabase.com:5432/postgres
   ```
3. Substitua `[SENHA]` pela senha do passo 1

### 3.3 Criar o arquivo `.env`

```bash
cp .env.example .env
```

Edite `.env` e preencha:
```bash
DATABASE_URL=postgresql://postgres.xxxx:SENHA@aws-0-sa-east-1.pooler.supabase.com:5432/postgres
```

> ⚠️ **NUNCA** commite o `.env` — ele está no `.gitignore`.

### 3.4 Rodar o seed

```bash
python seed_orcamento.py
```

Esperado ao final:
```
Carga OK. Validacao 2026 (UO 24205):
  PLOA(8)           = 144337668.00
  LOA Inicial(9)    = 144337668.00
  LOA Atualizada(13)= 144337668.00
  Empenhado(29)     = 54141930.11
  Pago(34)          = ...
```

---

## 4. Configurar o Backend FastAPI para usar o Supabase

O backend já detecta automaticamente se `DATABASE_URL` está configurada:
- **Se `DATABASE_URL` existe** → usa os dados reais do Supabase
- **Se não existe** → fallback para dados locais (CSV ou sintéticos)

### 4.1 Testar localmente

```bash
cd backend
pip install -r requirements.txt   # instala psycopg2-binary se ainda não tiver
set DATABASE_URL=postgresql://postgres.xxxx:SENHA@aws-0-sa-east-1.pooler.supabase.com:5432/postgres
python -m uvicorn app.main:app --reload --port 8000
```

Acesse http://localhost:8000/docs e teste:
- `GET /api/v1/orcamento/kpis` → deve retornar dados reais do Tesouro
- `GET /api/v1/orcamento/dimensoes` → deve listar programas reais

---

## 5. Deploy do Backend (opcional — ver nota abaixo)

### Opção A: Manter backend local/VM (mais simples)
- O frontend na Vercel aponta para seu backend (ex: `https://sua-vm.com`)
- Configure `VITE_API_URL=https://sua-vm.com` no frontend

### Opção B: Deploy backend na nuvem (Render/Railway)
- Siga o README principal para deploy no Render
- Configure a variável `DATABASE_URL` no painel do Render

> **Nota:** Com Supabase, você pode também usar o **pgREST** do próprio Supabase
> como API REST, eliminando a necessidade do backend FastAPI para o domínio
> Orçamento. Isso será documentado em versão futura.

---

## 6. Deploy do Frontend na Vercel

### 6.1 Preparar o frontend

Edite `frontend/.env` (crie a partir de `.env.example`):
```bash
VITE_API_URL=http://localhost:8000          # desenvolvimento
# VITE_API_URL=https://sua-api.com          # produção (alterar antes do deploy)
```

### 6.2 Conectar ao Vercel

1. Acesse https://vercel.com e login com GitHub
2. **Add New Project** → importe o repositório `and451/dashboard`
3. Configure:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `sistema-paineis/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Em **Environment Variables**, adicione:
   ```
   VITE_API_URL=https://sua-api-url.com   # URL do backend FastAPI
   ```
5. Clique em **Deploy**

### 6.3 Configurar o `vercel.json` (já existe na raiz)

O arquivo `sistema-paineis/vercel.json` já está configurado para build do frontend.

---

## 7. Verificar a integração

1. Acesse o frontend na Vercel (URL fornecida após deploy)
2. Abra o painel **Orçamento / Execução**
3. Verifique se os KPIs mostram valores reais (ex: Dotação ~R$ 144M para 2026)
4. Teste os filtros por programa/ação — devem refletir os dados do Tesouro

---

## Troubleshooting

### "psycopg2 não instalado"
```bash
pip install psycopg2-binary
```

### "DATABASE_URL não configurada"
Verifique se o arquivo `.env` existe e está correto, ou defina a variável:
```bash
set DATABASE_URL=postgresql://...   # Windows
export DATABASE_URL=postgresql://... # Linux/Mac
```

### "CORS blocked"
Verifique se a URL do frontend está na lista de origens permitidas no `main.py`.

### Dados não aparecem no painel
- Verifique se o seed rodou sem erros
- Teste diretamente no Supabase: SQL Editor → `select count(*) from public.orcamento`
- Verifique os logs do backend para erros de conexão

---

## Próximos passos

- [ ] Expôr mais domínios no Supabase (Contratos, TransfereGov, etc.)
- [ ] Usar o pgREST do Supabase como API REST direta
- [ ] Implementar Row Level Security (RLS) por unidade gestora (UG)
- [ ] Cachear queries frequentes com Redis
