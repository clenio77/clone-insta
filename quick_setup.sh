#!/bin/bash

echo "🚀 Setup rápido do Instagram Clone"
echo ""

# Instalar requests se necessário
echo "📦 Verificando dependências..."
if ! python3 -c "import requests" 2>/dev/null; then
    echo "📥 Instalando requests..."
    pip3 install requests
fi

# Executar script Python
echo "👤 Criando usuários de demonstração..."
python3 create_demo_users.py

echo ""
echo "✅ Setup concluído!"
echo "📱 Acesse: http://localhost:3000"
