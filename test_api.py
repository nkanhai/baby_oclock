import requests
import json

print("Testing API at http://localhost:8080/api/feeds")
try:
    response = requests.get('http://localhost:8080/api/feeds')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Error: {e}")
