import os
from flask import Flask, jsonify

app = Flask(__name__)

# Get server ID from environment variable or use container name as fallback
SERVER_ID = os.environ.get('SERVER_ID', os.environ.get('HOSTNAME', 'unknown'))

@app.route('/home', methods=['GET'])
def home():
    if SERVER_ID == 'unknown':
        return jsonify({"message": "Error: Server ID not set", "status": "failed"})
    return jsonify({"message": f"Hello from Server: {SERVER_ID}", "status": "successful"})

@app.route('/heartbeat', methods=['GET'])
def heartbeat():
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
