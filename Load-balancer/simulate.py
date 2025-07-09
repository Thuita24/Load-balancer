from hashing import ConsistentHashRing
import matplotlib.pyplot as plt


ring = ConsistentHashRing(num_servers=3, slots=512, virtual_nodes=9)

# Track request counts
request_counts = {}

for request_id in range(1, 31):
    server = ring.get_server_for_request(request_id)
    if server:
        print(f"Request {request_id} routed to {server}")
        if server in request_counts:
            request_counts[server] += 1
        else:
            request_counts[server] = 1
    else:
        print(f"Request {request_id} could not be routed")

# Plot the results
if request_counts:
    plt.bar(request_counts.keys(), request_counts.values(), color='skyblue')
    plt.xlabel('Server')
    plt.ylabel('Number of Requests')
    plt.title('Server Load Distribution')
    plt.tight_layout()
    plt.savefig("server_load_distribution.png")
    print("Graph saved as 'server_load_distribution.png'")
else:
    print("No requests were routed.")

