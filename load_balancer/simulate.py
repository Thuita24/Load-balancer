from load_balancer import RoundRobinBalancer

rr = RoundRobinBalancer()

# Add 3 servers
rr.add_server(1)
rr.add_server(2)
rr.add_server(3)

# Simulate 30 requests
for i in range(1, 31):
    rr.route_request(i)

# Plot results
rr.plot_server_load()
