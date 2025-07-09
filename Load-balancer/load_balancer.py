from flask import Flask, jsonify,request
from hashing import ConsistentHashRing
import requests
import random

app = Flask(__name__)
HSLOTS = 512
K = 9
ring = ConsistentHashRing(num_servers=3, slots=512, virtual_nodes=9)

@app.route('/request/<int:request_id>', methods=['GET'])
def route_request(request_id):
    server = ring.get_server_for_request(request_id)
    #get message
    if server:
        return jsonify({
            "message": f"Request ID {request_id} routed to {server}",
            "status": "successful"
        }), 200
    else:
        return jsonify({
            "message": "No available server found.",
            "status": "error"
        }), 503

@app.route('/servers', methods=['GET'])
def servers():
    return jsonify({
        "server_map": ring.server_map
    }), 200

@app.route("/rep", methods=["GET"])
def get_replicas():
    return jsonify({"message": {"N": len(servers), "replicas": servers, "status": "successful"}}), 200

@app.route("/add", methods=["POST"])
def add_servers():
    global hash_ring
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if not isinstance(n, int) or n <= 0 or len(hostnames) > n:
        return jsonify({"message": "Error: Invalid n or hostname list length exceeds n", "status": "failure"}), 400

    new_servers = hostnames[:n] if hostnames else [f"server{random.randint(100, 999)}:5000" for _ in range(n)]
    servers.extend(new_servers)

    # Update hash ring with new servers
    hash_ring = ConsistentHashRing(servers, HSLOTS, K)
    return jsonify({"message": {"N": len(servers), "replicas": servers, "status": "successful"}}), 200

@app.route("/rm", methods=["DELETE"])
def remove_servers():
    data = request.json
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if not isinstance(n, int) or n <= 0 or n > len(servers) or len(hostnames) > n:
        return jsonify({"message": "Error: Invalid n or hostname list length exceeds n", "status": "failure"}), 400

    remove_list = hostnames[:n] if hostnames else [s for s in servers[:n]]
    for server in remove_list:
        if server in servers:
            servers.remove(server)
            n -= 1
    
    # Randomly remove servers if n > 0
    while n > 0:
        servers.remove(random.choice(servers))
        n -= 1

    # Update hash ring with servers
    new_hash_ring = ConsistentHashRing(servers, HSLOTS, K)
    global hash_ring
    hash_ring = new_hash_ring  # Replace the old ring

    return jsonify({"message": {"N": len(servers), "replicas": servers, "status": "successful"}}), 200

def is_server_alive(server):
    """Checks if a server is active by sending a heartbeat to it."""
    try:
        res = requests.get(f"http://{server}/heartbeat", timeout=2)
        return res.status_code == 200
    except requests.RequestException:
        return False



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
