# simulate_task4_a3.py
import requests

response = requests.get("http://localhost:5000/rep")
print(f"Status Code: {response.status_code}")
print(response.json())

payload = {
    "n" : 2,
    "hostnames" : ["S5", "S8"]
}

response = requests.post("http://localhost:5000/add", json=payload)
print(f"Status Code: {response.status_code}")
print(response.json())

payload = {
    "n" : 2,
    "hostnames" : ["S5", "S8"]
}

response = requests.delete("http://localhost:5000/rm", json=payload)
print(f"Status Code: {response.status_code}")
print(response.json())

response = requests.get("http://localhost:5000/other")
print(f"Status Code: {response.status_code}")
print(response.json())

for _ in range(10):
    try:
        response = requests.get("http://localhost:5000/home", timeout=2)
        print(response.status_code, response.json())
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)

import subprocess
server_container = "app-server1-1"
try:
    subprocess.run(["docker", "stop", server_container])
    print(f"Container stopped: {server_container}")
except subprocess.CalledProcessError as e:
    print(f"Failed to stop container {server_container}: {e}")

for _ in range(10):
    try:
        response = requests.get("http://localhost:5000/home", timeout=2)
        print(response.status_code, response.json())
    except requests.exceptions.RequestException as e:
        print("Request failed:", e)





