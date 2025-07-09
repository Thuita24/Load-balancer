.PHONY: all build run clean test

all: build run

build:
	docker-compose build

run:
	docker-compose up -d

clean:
	docker-compose down
	docker system prune -f

test:
	python3 test_requests.py
