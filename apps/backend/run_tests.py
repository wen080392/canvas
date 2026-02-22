#!/usr/bin/env python
"""Start backend server and run tests"""
import subprocess
import time
import sys
import os

os.chdir(r'c:\Users\USER\CloudGuardian\apps\backend')

# Start server
print("Iniciando servidor...")
server_proc = subprocess.Popen(
    [sys.executable, 'run_dev_server.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for server to start
print("Aguardando 5 segundos...")
time.sleep(5)

# Run tests
print("\nRodando testes...")
test_result = subprocess.run(
    [sys.executable, 'test_all_endpoints.py'],
    capture_output=False,
    text=True
)

# Stop server
print("\nParando servidor...")
server_proc.terminate()

sys.exit(test_result.returncode)
