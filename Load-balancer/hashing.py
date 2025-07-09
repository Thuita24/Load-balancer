class ConsistentHashRing:
    def __init__(self, num_servers=3, slots=512, virtual_nodes=9):
        self.num_servers = num_servers
        self.slots = slots
        self.virtual_nodes = virtual_nodes
        self.hash_ring = [None] * slots
        self.server_map = {}
        self._initialize_ring()

    def H(self, i):
        hash_value = pow(i, 2) + 2*i + 17
        return hash_value % self.slots

    def Phi(self, i, j):
        key = f"{i}-{j}"
        hash_value = pow(i, 2) + pow(j, 2) + 2*j + 25
        return hash_value % self.slots

    def _initialize_ring(self):
        for server_id in range(self.num_servers):
            for replica_id in range(self.virtual_nodes):
                original_slot = self.Phi(server_id, replica_id)
                slot = original_slot
                i = 1
                while self.hash_ring[slot] is not None:
                    slot = (original_slot + i + (i * i)) % self.slots  # Quadratic probing
                    i += 1
                    if i >= self.slots:
                        raise Exception("Hash ring is full.")
                self.hash_ring[slot] = f"Server-{server_id}"
                self.server_map[slot] = f"Server-{server_id}"

    def get_server_for_request(self, request_id):
        original_slot = self.H(request_id)
        slot = original_slot
        i = 1
        while self.hash_ring[slot] is None:
            slot = (original_slot + i + (i * i)) % self.slots  # Quadratic probing
            i += 1
            if i >= self.slots:
                return None
        return self.hash_ring[slot]