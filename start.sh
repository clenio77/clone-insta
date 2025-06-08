#!/bin/bash

echo "🚀 Iniciando Instagram Clone..."

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado. Por favor, instale o Docker primeiro."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não encontrado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Parar containers existentes
echo "🛑 Parando containers existentes..."
docker-compose down

# Construir e iniciar os serviços
echo "🔨 Construindo e iniciando os serviços..."
docker-compose up --build -d

echo "✅ Serviços iniciados com sucesso!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📚 Documentação da API: http://localhost:8001/docs"
echo ""
echo "Para parar os serviços, execute: docker-compose down"
echo "Para ver os logs, execute: docker-compose logs -f"
