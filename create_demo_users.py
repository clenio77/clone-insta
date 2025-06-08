#!/usr/bin/env python3
"""
Script para criar usuários de demonstração no Instagram Clone
"""

try:
    import requests
except ImportError:
    print("❌ Módulo 'requests' não encontrado!")
    print("💡 Para instalar, execute:")
    print("   pip install requests")
    print("   ou")
    print("   cd backend && source venv/bin/activate && pip install requests")
    exit(1)

import json

BASE_URL = "http://localhost:8001"

# Usuários de demonstração
demo_users = [
    {
        "username": "john_doe",
        "email": "john@example.com",
        "full_name": "John Doe",
        "password": "password123",
        "bio": "Photographer and travel enthusiast 📸✈️"
    },
    {
        "username": "jane_smith",
        "email": "jane@example.com", 
        "full_name": "Jane Smith",
        "password": "password123",
        "bio": "Food blogger and chef 🍕👩‍🍳"
    },
    {
        "username": "mike_wilson",
        "email": "mike@example.com",
        "full_name": "Mike Wilson", 
        "password": "password123",
        "bio": "Fitness trainer and motivational speaker 💪🏋️"
    },
    {
        "username": "sarah_jones",
        "email": "sarah@example.com",
        "full_name": "Sarah Jones",
        "password": "password123", 
        "bio": "Artist and designer 🎨✨"
    },
    {
        "username": "alex_brown",
        "email": "alex@example.com",
        "full_name": "Alex Brown",
        "password": "password123",
        "bio": "Tech enthusiast and gamer 🎮💻"
    }
]

def create_demo_users():
    print("🎭 Criando usuários de demonstração...")
    
    created_users = []
    
    for user_data in demo_users:
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if response.status_code == 200:
                print(f"✅ Usuário criado: {user_data['username']}")
                created_users.append(user_data)
            elif response.status_code == 400 and "already registered" in response.text:
                print(f"ℹ️  Usuário já existe: {user_data['username']}")
                created_users.append(user_data)
            else:
                print(f"❌ Erro ao criar {user_data['username']}: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ Erro: Não foi possível conectar à API.")
            print("   Certifique-se de que o backend está rodando em http://localhost:8001")
            return []
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
    
    return created_users

def create_demo_follows(users):
    """Criar algumas conexões entre usuários"""
    print("\n👥 Criando conexões entre usuários...")
    
    # john_doe segue jane_smith e sarah_jones
    follow_connections = [
        ("john_doe", "jane_smith"),
        ("john_doe", "sarah_jones"),
        ("jane_smith", "mike_wilson"),
        ("jane_smith", "alex_brown"),
        ("mike_wilson", "john_doe"),
        ("sarah_jones", "jane_smith"),
        ("alex_brown", "mike_wilson"),
        ("alex_brown", "sarah_jones")
    ]
    
    for follower, followed in follow_connections:
        try:
            # Login do follower
            login_data = {
                "username": follower,
                "password": "password123"
            }
            
            login_response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                
                # Seguir usuário
                follow_response = requests.post(
                    f"{BASE_URL}/users/{followed}/follow", 
                    headers=headers
                )
                
                if follow_response.status_code == 200:
                    print(f"✅ {follower} agora segue {followed}")
                else:
                    print(f"⚠️  {follower} já segue {followed}")
            
        except Exception as e:
            print(f"❌ Erro ao criar conexão {follower} -> {followed}: {e}")

def main():
    print("🚀 Configurando Instagram Clone com dados de demonstração...")
    print("=" * 60)
    
    # Verificar se a API está rodando
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ API não está respondendo. Execute './start.sh' primeiro.")
            return
    except:
        print("❌ Não foi possível conectar à API. Execute './start.sh' primeiro.")
        return
    
    # Criar usuários
    created_users = create_demo_users()
    
    if created_users:
        # Criar conexões
        create_demo_follows(created_users)
        
        print("\n" + "=" * 60)
        print("🎉 Configuração concluída!")
        print("\n📱 Acesse: http://localhost:3000")
        print("\n👤 Usuários disponíveis:")
        print("   Username: john_doe   | Senha: password123")
        print("   Username: jane_smith | Senha: password123") 
        print("   Username: mike_wilson| Senha: password123")
        print("   Username: sarah_jones| Senha: password123")
        print("   Username: alex_brown | Senha: password123")
        print("\n💡 Dica: Faça login com qualquer um desses usuários!")
        
    else:
        print("❌ Não foi possível criar usuários de demonstração.")

if __name__ == "__main__":
    main()
