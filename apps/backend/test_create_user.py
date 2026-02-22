import requests
import json

# Test user creation
url = "http://localhost:8000/users"
data = {
    "email": "admin@company.com",
    "password": "demo123",
    "full_name": "Admin User"
}

print("Testing user creation...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

response = requests.post(url, json=data)

print(f"\nStatus Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 201:
    print("\n✅ User created successfully!")
    user_data = response.json()
    print(f"User ID: {user_data['id']}")
    print(f"Email: {user_data['email']}")
else:
    print(f"\n❌ Failed to create user")
    try:
        error = response.json()
        print(f"Error details: {json.dumps(error, indent=2)}")
    except:
        print(f"Error: {response.text}")
