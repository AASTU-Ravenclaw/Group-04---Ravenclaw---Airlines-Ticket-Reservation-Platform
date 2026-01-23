import os
from kafka import KafkaAdminClient

brokers = os.environ.get('KAFKA_BROKERS', 'kafka.airlines.svc.cluster.local:9092')
bootstrap_servers = [b.strip() for b in brokers.split(',') if b.strip()]
print(f"Connecting to Kafka at {bootstrap_servers}...")

try:
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers, client_id="notification-service-test")
    topics = admin.list_topics()
    print(f"Successfully connected! Topics: {sorted(topics)}")
    admin.close()
except Exception as e:
    print(f"Connection failed: {e}")
