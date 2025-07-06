FROM python:3.9-slim

WORKDIR /app

COPY app.py .
COPY load_balancer.py .

RUN apt-get update && apt-get install -y curl

RUN pip install flask matplotlib

EXPOSE 6000

CMD ["python", "app.py"]

