#!/bin/bash

echo "🎭 Criando usuários de demonstração no Instagram Clone..."
echo "=" * 60

BASE_URL="http://localhost:8001"

# Verificar se a API está rodando
echo "🔍 Verificando se a API está rodando..."
if ! curl -s "$BASE_URL/docs" > /dev/null; then
    echo "❌ API não está respondendo. Execute './start.sh' primeiro."
    exit 1
fi

echo "✅ API está rodando!"

# Função para criar usuário
create_user() {
    local username=$1
    local email=$2
    local full_name=$3
    local bio=$4
    
    echo "👤 Criando usuário: $username"
    
    response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$username\",
            \"email\": \"$email\",
            \"full_name\": \"$full_name\",
            \"password\": \"password123\",
            \"bio\": \"$bio\"
        }")
    
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ]; then
        echo "✅ Usuário criado: $username"
    elif [ "$http_code" = "400" ]; then
        echo "ℹ️  Usuário já existe: $username"
    else
        echo "❌ Erro ao criar $username (HTTP: $http_code)"
    fi
}

# Função para fazer login e obter token
get_token() {
    local username=$1
    
    response=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"username\": \"$username\",
            \"password\": \"password123\"
        }")
    
    echo "$response" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4
}

# Função para seguir usuário
follow_user() {
    local follower=$1
    local followed=$2
    
    echo "👥 $follower seguindo $followed..."
    
    token=$(get_token "$follower")
    
    if [ -n "$token" ]; then
        response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/users/$followed/follow" \
            -H "Authorization: Bearer $token")
        
        http_code="${response: -3}"
        
        if [ "$http_code" = "200" ]; then
            echo "✅ $follower agora segue $followed"
        else
            echo "⚠️  $follower já segue $followed"
        fi
    fi
}

# Criar usuários
echo ""
echo "👤 Criando usuários..."

create_user "john_doe" "john@example.com" "John Doe" "Photographer and travel enthusiast 📸✈️"
create_user "jane_smith" "jane@example.com" "Jane Smith" "Food blogger and chef 🍕👩‍🍳"
create_user "mike_wilson" "mike@example.com" "Mike Wilson" "Fitness trainer and motivational speaker 💪🏋️"
create_user "sarah_jones" "sarah@example.com" "Sarah Jones" "Artist and designer 🎨✨"
create_user "alex_brown" "alex@example.com" "Alex Brown" "Tech enthusiast and gamer 🎮💻"

# Criar conexões
echo ""
echo "👥 Criando conexões entre usuários..."

follow_user "john_doe" "jane_smith"
follow_user "john_doe" "sarah_jones"
follow_user "jane_smith" "mike_wilson"
follow_user "jane_smith" "alex_brown"
follow_user "mike_wilson" "john_doe"
follow_user "sarah_jones" "jane_smith"
follow_user "alex_brown" "mike_wilson"
follow_user "alex_brown" "sarah_jones"

echo ""
echo "=" * 60
echo "🎉 Configuração concluída!"
echo ""
echo "📱 Acesse: http://localhost:3000"
echo ""
echo "👤 Usuários disponíveis:"
echo "   Username: john_doe    | Senha: password123"
echo "   Username: jane_smith  | Senha: password123"
echo "   Username: mike_wilson | Senha: password123"
echo "   Username: sarah_jones | Senha: password123"
echo "   Username: alex_brown  | Senha: password123"
echo ""
echo "💡 Dica: Faça login com qualquer um desses usuários!"
