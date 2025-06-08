#!/bin/bash

echo "🔧 Corrigindo permissões Docker..."

# Parar containers
echo "🛑 Parando containers..."
docker-compose down

# Remover volumes e rebuild
echo "🗑️ Removendo volumes..."
docker-compose down -v

# Limpar cache do Docker
echo "🧹 Limpando cache Docker..."
docker system prune -f

# Corrigir permissões locais
echo "📁 Corrigindo permissões locais..."
sudo chown -R $USER:$USER ./frontend/node_modules 2>/dev/null || true
sudo chmod -R 755 ./frontend 2>/dev/null || true

# Rebuild sem cache
echo "🔨 Rebuilding containers..."
docker-compose build --no-cache

# Iniciar novamente
echo "🚀 Iniciando containers..."
docker-compose up -d

echo "✅ Correção concluída!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8001"
echo ""
echo "Para ver logs: docker-compose logs -f"
