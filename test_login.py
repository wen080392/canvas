import requests

def test_login():
    url = "http://localhost:8000/token"
    data = {
        "username": "admin@company.com",
        "password": "demo1234"
    }
    
    try:
        print(f"Attempting login with {data['username']}...")
        response = requests.post(url, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Login Successful!")
        else:
            print("Login Failed.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_login()
