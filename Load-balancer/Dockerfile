FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install -r requirements.txt

ENV SERVER_ID=default

EXPOSE 6000

CMD ["python", "load_balancer.py"]