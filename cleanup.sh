#!/bin/bash

echo "🧹 Limpando ambiente Docker..."

# Parar todos os containers
echo "🛑 Parando todos os containers..."
docker stop $(docker ps -aq) 2>/dev/null || echo "Nenhum container rodando"

# Remover containers
echo "🗑️ Removendo containers..."
docker rm $(docker ps -aq) 2>/dev/null || echo "Nenhum container para remover"

# Limpar redes
echo "🌐 Limpando redes Docker..."
docker network prune -f

# Limpar volumes não utilizados
echo "💾 Limpando volumes não utilizados..."
docker volume prune -f

# Verificar processos na porta 8000
echo "🔍 Verificando processos na porta 8000..."
lsof -i :8000 2>/dev/null || echo "Porta 8000 livre"

# Verificar processos na porta 8001
echo "🔍 Verificando processos na porta 8001..."
lsof -i :8001 2>/dev/null || echo "Porta 8001 livre"

echo "✅ Limpeza concluída!"
echo "Agora você pode executar: ./start.sh"
