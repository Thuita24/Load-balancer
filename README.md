**# Consistent Hashing-Based Load Balancer **

# Features
•	Load balancing using Consistent Hashing
•	Server health monitoring via heartbeat checks
•	Dynamic scaling (add/remove servers via API)
•	Fault tolerance with auto removal of dead servers
•	Dockerized for easy deployment
•	Performance experiments (Task A1–A4) via simulation scripts


Project Structure
•	Load-balancer/
•	├── Dockerfile (Load balancer)
•	├── app.py (Load balancer Flask application)
•	├── hashing.py (ConsistentHashRing class logic)
•	├── simulate_task4_a*.py (Performance simulation scripts)
•	├── server/ (Backend Flask server)
•	│   ├── Dockerfile
•	│   └── server.py
•	├── docker-compose.yml
•	└── README.md

Prerequisites
•	Python 3.9+
•	Docker & Docker Compose
•	Ubuntu or WSL2 on Windows
•	VS Code 


Setup (Development Environment)
1. Clone the Repository
   git clone https://github.com/Thuita24/Load-balancer.git

2. Navigate to the repository:
   cd Load-Balancer-Distributed-System

3. Create a Virtual Environment
   python3 -m venv .venv

     4. Activate the virtual environment:

   source  .venv\Scripts\activate (Windows)

5. Install Dependencies
   pip install -r requirements.txt
Running with Docker
1. Build Docker Images:
 docker-compose build

2. Start Services:
 docker-compose up -d

3. Check Containers: 
docker ps
API Endpoints
•	GET /home: Route request to a server
•	GET /rep: List of active servers
•	POST /add: Add servers (JSON payload)
•	DELETE /rm: Remove servers (JSON payload)
Testing with Postman
•	Use GET, POST, DELETE requests with relevant body content
•	Test /home, /rep, /add, /rm
