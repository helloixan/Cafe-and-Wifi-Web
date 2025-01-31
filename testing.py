import requests

ENDPOINT = "http://127.0.0.1:5000"

response = requests.get(url=f"{ENDPOINT}/all")
cafes = response.json()
print(cafes)