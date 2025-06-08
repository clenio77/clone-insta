#!/usr/bin/env python3
"""
Script de teste para verificar se a API está funcionando corretamente.
Execute este script após iniciar o backend.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("🧪 Testando API do Instagram Clone...")
    
    # Teste 1: Verificar se a API está rodando
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API está rodando!")
        else:
            print("❌ API não está respondendo corretamente")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Certifique-se de que o backend está rodando.")
        return
    
    # Teste 2: Registrar um usuário de teste
    test_user = {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword",
        "bio": "This is a test user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        if response.status_code == 200:
            print("✅ Registro de usuário funcionando!")
        elif response.status_code == 400 and "already registered" in response.text:
            print("ℹ️  Usuário de teste já existe")
        else:
            print(f"❌ Erro no registro: {response.text}")
    except Exception as e:
        print(f"❌ Erro no teste de registro: {e}")
    
    # Teste 3: Login
    login_data = {
        "username": "testuser",
        "password": "testpassword"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login funcionando!")
            
            # Teste 4: Verificar perfil do usuário
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/users/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Perfil do usuário: {user_data['username']}")
            else:
                print("❌ Erro ao buscar perfil do usuário")
                
        else:
            print(f"❌ Erro no login: {response.text}")
    except Exception as e:
        print(f"❌ Erro no teste de login: {e}")
    
    print("\n🎉 Testes concluídos!")
    print("📱 Acesse http://localhost:3000 para usar a aplicação")
    print("📚 Documentação da API: http://localhost:8000/docs")

if __name__ == "__main__":
    test_api()
