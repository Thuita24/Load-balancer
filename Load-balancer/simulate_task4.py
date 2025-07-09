# simulate_task4.py
import matplotlib.pyplot as plt
from hashing import ConsistentHashRing
from collections import defaultdict

# Task A-1: Fixed 3 servers, 10,000 requests
ring = ConsistentHashRing(num_servers=3, slots=512, virtual_nodes=9)
request_count = defaultdict(int)

for request_id in range(10000):
    server = ring.get_server_for_request(request_id)
    request_count[server] += 1

# Plot A-1
plt.figure(figsize=(8, 5))
plt.bar(request_count.keys(), request_count.values(), color='skyblue')
plt.title("Task A-1: Load Distribution with 3 Servers (Consistent Hashing)")
plt.xlabel("Server")
plt.ylabel("Requests Handled")
plt.tight_layout()
plt.savefig("task_a1_bar_chart.png")
plt.close()

# Task A-2: Varying N from 2 to 6, 10,000 requests each
avg_requests = []
num_servers_range = range(2, 7)

for n in num_servers_range:
    ring = ConsistentHashRing(num_servers=n, slots=512, virtual_nodes=9)
    request_count = defaultdict(int)
    for request_id in range(10000):
        server = ring.get_server_for_request(request_id)
        request_count[server] += 1
    avg = sum(request_count.values()) / len(request_count)
    avg_requests.append(avg)

# Plot A-2
plt.figure(figsize=(8, 5))
plt.plot(list(num_servers_range), avg_requests, marker='o', color='green')
plt.title("Task A-2: Average Load vs Number of Servers")
plt.xlabel("Number of Servers")
plt.ylabel("Average Requests per Server")
plt.grid(True)
plt.tight_layout()
plt.savefig("task_a2_line_chart.png")
plt.close()

