from flask import Flask, request, jsonify
import requests
import threading
import time
import docker
import logging
import hashlib
import uuid

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ConsistentHashingLoadBalancer:
    def __init__(self):
        self.num_slots = 1024
        self.num_replicas = 100
        self.servers = []
        self.virtual_nodes = {}
        self.client = docker.from_env()
        self.heartbeat_interval = 5
        self.lock = threading.Lock()
        threading.Thread(target=self.heartbeat_check, daemon=True).start()

    def hash_key(self, key):
        return int(hashlib.md5(str(key).encode()).hexdigest(), 16) % self.num_slots

    def hash_virtual_node(self, server_id, replica_index):
        return self.hash_key(f"{server_id}:{replica_index}")

    def add_server(self, hostname):
        with self.lock:
            if hostname in self.servers:
                return True
            try:
                # Check if container already exists
                container = self.client.containers.get(hostname)
                if container.status != 'running':
                    logging.warning(f"Container {hostname} exists but is not running.")
                    return False
            except docker.errors.NotFound:
                # Create container if not found
                container = self.client.containers.run(
                    'server_image',
                    name=hostname,
                    network='load_balancer_network',
                    environment={"SERVER_ID": hostname},
                    detach=True
                )
            self.servers.append(hostname)
            for i in range(self.num_replicas):
                slot = self.hash_virtual_node(hostname, i)
                self.virtual_nodes[slot] = hostname
            logging.info(f"Server {hostname} registered")
            return True

    def remove_server(self, hostname):
        with self.lock:
            if hostname not in self.servers:
                return True
            try:
                container = self.client.containers.get(hostname)
                container.stop()
                container.remove()
            except Exception as e:
                logging.warning(f"Error stopping container {hostname}: {str(e)}")
            self.servers.remove(hostname)
            for i in range(self.num_replicas):
                slot = self.hash_virtual_node(hostname, i)
                if slot in self.virtual_nodes and self.virtual_nodes[slot] == hostname:
                    del self.virtual_nodes[slot]
            logging.info(f"Server {hostname} removed")
            return True

    def get_server(self, request_id):
        with self.lock:
            if not self.virtual_nodes:
                return None
            slot = self.hash_key(request_id)
            sorted_slots = sorted(self.virtual_nodes)
            for s in sorted_slots:
                if slot <= s:
                    return self.virtual_nodes[s]
            return self.virtual_nodes[sorted_slots[0]]  # Wrap around

    def heartbeat_check(self):
        while True:
            with self.lock:
                for server in self.servers[:]:
                    try:
                        response = requests.get(f"http://{server}:5000/heartbeat", timeout=2)
                        if response.status_code != 200:
                            raise Exception("Non-200 response")
                        logging.info(f"Heartbeat OK: {server}")
                    except Exception:
                        logging.error(f"Heartbeat failed: {server}")
                        self.remove_server(server)
                        new_server = f"server{int(time.time())}"
                        self.add_server(new_server)
            time.sleep(self.heartbeat_interval)

load_balancer = ConsistentHashingLoadBalancer()

@app.route('/home', methods=['GET'])
def home():
    request_id = uuid.uuid4().int % 1_000_000
    server = load_balancer.get_server(request_id)
    if not server:
        return jsonify({"message": "No servers available", "status": "failed"}), 503
    try:
        response = requests.get(f"http://{server}:5000/home")
        return response.json()
    except Exception as e:
        return jsonify({"message": f"Error contacting {server}: {str(e)}", "status": "failed"}), 500

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    n = data.get('n', 0)
    hostnames = data.get('hostnames', [])
    if len(hostnames) != n:
        return jsonify({"message": "Invalid number of hostnames", "status": "failed"}), 400
    for hostname in hostnames:
        if not load_balancer.add_server(hostname):
            return jsonify({"message": f"Failed to add {hostname}", "status": "failed"}), 500
    return rep()

@app.route('/rm', methods=['DELETE'])
def remove():
    data = request.get_json()
    n = data.get('n', 0)
    hostnames = data.get('hostnames', [])
    if len(hostnames) != n:
        return jsonify({"message": "Invalid number of hostnames", "status": "failed"}), 400
    for hostname in hostnames:
        if not load_balancer.remove_server(hostname):
            return jsonify({"message": f"Failed to remove {hostname}", "status": "failed"}), 500
    return rep()

@app.route('/rep', methods=['GET'])
def rep():
    return jsonify({
        "message": {
            "N": len(load_balancer.servers),
            "replicas": load_balancer.servers,
            "status": "successful"
        }
    })

if __name__ == '__main__':
    for i in range(1, 4):
        load_balancer.add_server(f"server{i}")
    app.run(host='0.0.0.0', port=5000)
