import requests

def check_api_health() -> dict:

    response = requests.get('http://ml-service:8000/health')

    return response.json()
