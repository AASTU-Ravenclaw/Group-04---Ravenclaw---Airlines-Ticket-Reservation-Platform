import pika
import os
import sys

rabbitmq_url = os.environ.get('RABBITMQ_URL_TEST', 'amqp://guest:guest@rabbitmq.airlines.svc.cluster.local:5672/')
print(f"Connecting to {rabbitmq_url}...")

try:
    params = pika.URLParameters(rabbitmq_url)
    connection = pika.BlockingConnection(params)
    print("Successfully connected!")
    connection.close()
except Exception as e:
    print(f"Connection failed: {e}")
