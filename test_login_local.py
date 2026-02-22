import requests

URL = "http://localhost:8000/token"
CREDENTIALS = {
    "username": "admin@company.com",
    "password": "password"
}

try:
    print(f"Testing login at {URL} with {CREDENTIALS['username']}...")
    response = requests.post(URL, data=CREDENTIALS)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("LOGIN SUCCESSFUL! Backend is working.")
    else:
        print("LOGIN FAILED! Backend rejected credentials.")
        
except Exception as e:
    print(f"CONNECTION ERROR: {e}")
