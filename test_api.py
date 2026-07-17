import requests
r = requests.get('http://localhost:8000/api/v1/agents/health')
print(r.status_code, r.json())
