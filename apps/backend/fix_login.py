import re

# Ler o arquivo
with open('c:/Users/USER/CloudGuardian/apps/frontend/login.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Fazer as substituições APENAS onde necessário
content = content.replace('value="demo123"', 'value="demo1234"')
content = content.replace("password: 'demo123'", "password: 'demo1234'")
content = content.replace('"password": "demo123"', '"password": "demo1234"')

# Salvar
with open('c:/Users/USER/CloudGuardian/apps/frontend/login.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Login.html atualizado com senha demo1234")
