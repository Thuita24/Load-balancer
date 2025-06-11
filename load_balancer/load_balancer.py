# load_balancer.py
import math

TOTAL_SLOTS = 512
VIRTUAL_SERVERS_PER_SERVER = 9

class ConsistentHashMap:
    def __init__(self):
        self.hash_ring = [None] * TOTAL_SLOTS  # Initialize empty ring
        self.server_slots = {}  # Map server_id -> list of occupied slots

    def hash_request(self, i):
        return (i ** 2 + 2 * i + 17) % TOTAL_SLOTS

    def hash_virtual_server(self, server_id, replica_id):
        return (server_id ** 2 + replica_id + 2 * replica_id + 25) % TOTAL_SLOTS

    def add_server(self, server_id):
        print(f"Adding server {server_id}...")
        self.server_slots[server_id] = []
        for replica_id in range(VIRTUAL_SERVERS_PER_SERVER):
            slot = self.hash_virtual_server(server_id, replica_id)
            slot = self._find_free_slot(slot)
            self.hash_ring[slot] = (server_id, replica_id)
            self.server_slots[server_id].append(slot)
        print(f"Server {server_id} added with slots: {self.server_slots[server_id]}")

    def remove_server(self, server_id):
        print(f"Removing server {server_id}...")
        if server_id in self.server_slots:
            for slot in self.server_slots[server_id]:
                self.hash_ring[slot] = None
            del self.server_slots[server_id]
            print(f"Server {server_id} removed.")

    def route_request(self, request_id):
        request_slot = self.hash_request(request_id)
        slot = request_slot
        while self.hash_ring[slot] is None:
            slot = (slot + 1) % TOTAL_SLOTS  # Linear probing
            if slot == request_slot:
                print("Error: No servers available!")
                return None
        server_id, replica_id = self.hash_ring[slot]
        print(f"Request {request_id} routed to Server {server_id} (Replica {replica_id}) at slot {slot}")
        return server_id

    def _find_free_slot(self, start_slot):
        slot = start_slot
        while self.hash_ring[slot] is not None:
            slot = (slot + 1) % TOTAL_SLOTS  # Linear probing
        return slot

# Example usage:
if __name__ == "__main__":
    ch = ConsistentHashMap()
    ch.add_server(1)
    ch.add_server(2)
    ch.add_server(3)

    for req_id in [101, 202, 303, 404, 505]:
        ch.route_request(req_id)

    ch.remove_server(2)

    for req_id in [101, 202, 303, 404, 505]:
        ch.route_request(req_id)
