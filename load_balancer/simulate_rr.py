from load_balancer import RoundRobinBalancer

# Initialize the balancer
rr = RoundRobinBalancer()

# Add 3 servers
for i in range(3):
    rr.add_server(i)

# Route 30 simulated requests
for request_id in range(1, 31):
    rr.route_request(request_id)

# Generate and save the load distribution graph
rr.plot_server_load()
