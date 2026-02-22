import requests
import json

# Test user creation
print("="*50)
print("TESTE 1: Criar usuário")
print("="*50)
url_users = "http://localhost:8000/users"
data = {
    "email": "admin@company.com",
    "password": "demo1234",
    "full_name": "Admin User"
}

response = requests.post(url_users, json=data)
print(f"Status: {response.status_code}")
if response.status_code == 201:
    print("✅ Usuário criado com sucesso!")
    print(f"Dados: {json.dumps(response.json(), indent=2)}")
else:
    print(f"❌ Erro ao criar usuário")
    print(f"Resposta: {response.text}")

# Test login
print("\n" + "="*50)
print("TESTE 2: Login")
print("="*50)
url_token = "http://localhost:8000/token"
login_data = {
    "username": "admin@company.com",
    "password": "demo1234"
}

response = requests.post(url_token, data=login_data)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✅ Login realizado com sucesso!")
    token_data = response.json()
    print(f"Token: {token_data['access_token'][:50]}...")
else:
    print(f"❌ Erro no login")
    print(f"Resposta: {response.text}")
