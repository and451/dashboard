# Multi-stage build para Painéis AEB
# Stage 1: Build do frontend
FROM node:18-alpine AS frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend com frontend estático
FROM python:3.14-slim
WORKDIR /app

# Instalar dependências do backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código do backend
COPY backend/ ./

# Copiar build do frontend para servir como estático
COPY --from=frontend /app/frontend/dist ./static

# Expor porta
EXPOSE 8000

# Comando de start
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
