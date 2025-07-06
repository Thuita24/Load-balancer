# app.py
from flask import Flask, jsonify, request
import os
import time
from load_balancer import RoundRobinBalancer

app = Flask(__name__)
rr = RoundRobinBalancer()

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
    os.system(f'docker run -d --rm --network net1 --name {container_name} load-balancer-server{server_id}')
    
    servers.append(server_id)
    rr.add_server(server_id)
    time.sleep(1)
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
    rr.remove_server(server_id)
    return jsonify({"message": f"Server {server_id} removed."}), 200

@app.route('/request/<int:request_id>', methods=['GET'])
def route_request(request_id):
    server_id = rr.route_request(request_id)
    if server_id is None:
        return jsonify({"error": "No servers available."}), 503

    target_url = f"http://server_{server_id}:5000/home"
    response = os.popen(f'curl -s {target_url}').read()
    return response, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)




