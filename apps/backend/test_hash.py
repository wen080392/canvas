import sys
sys.path.insert(0, 'C:\\Users\\USER\\CloudGuardian\\apps\\backend')

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

senha = "demo1234"
print(f"Testando hash da senha: {senha}")
print(f"Tamanho: {len(senha)} bytes")

try:
    hash_result = pwd_context.hash(senha)
    print(f"✅ Hash gerado com sucesso!")
    print(f"Hash: {hash_result[:50]}...")
except Exception as e:
    print(f"❌ Erro: {e}")
