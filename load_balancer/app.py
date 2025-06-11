# app.py
from flask import Flask, jsonify, request
import os
import subprocess
import time
from load_balancer import ConsistentHashMap

app = Flask(__name__)
ch = ConsistentHashMap()

# Track running servers
servers = []

@app.route('/rep', methods=['GET'])
def get_replicas():
    return jsonify({"servers": servers}), 200

@app.route('/add', methods=['POST'])
def add_server():
    data = request.get_json()
    server_id = data.get("server_id")
    if server_id in servers:
        return jsonify({"error": "Server already exists."}), 400

    container_name = f"server_{server_id}"
    # Spawn server container using Docker command
    os.system(f'docker run -d --rm --network net1 --name {container_name} -e SERVER_ID={server_id} my_server_image')
    
    servers.append(server_id)
    ch.add_server(server_id)
    time.sleep(1)  # Wait for container to start
    return jsonify({"message": f"Server {server_id} added."}), 200

@app.route('/rm', methods=['DELETE'])
def remove_server():
    data = request.get_json()
    server_id = data.get("server_id")
    if server_id not in servers:
        return jsonify({"error": "Server not found."}), 400

    container_name = f"server_{server_id}"
    os.system(f'docker stop {container_name}')
    
    servers.remove(server_id)
    ch.remove_server(server_id)
    return jsonify({"message": f"Server {server_id} removed."}), 200

@app.route('/home', methods=['GET'])
def route_home():
    request_id = int(request.args.get("request_id", 0))
    server_id = ch.route_request(request_id)
    if server_id is None:
        return jsonify({"error": "No servers available."}), 503

    # Forward request to the selected server
    target_url = f"http://server_{server_id}:5000/home"
    response = os.popen(f'curl -s {target_url}').read()
    return response, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
