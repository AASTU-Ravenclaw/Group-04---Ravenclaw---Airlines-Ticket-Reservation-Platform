import json
import uuid
import threading
import queue
import time
from django.conf import settings
from opentelemetry import trace
from opentelemetry.propagate import inject
from confluent_kafka import Producer, KafkaError

class AsyncKafkaProducer:
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._tracer = trace.get_tracer(__name__)

    def publish(self, event_type, body, exchange='booking_events'):
        """
        Non-blocking publish. Puts message in local queue and returns immediately.
        """
        self._queue.put((event_type, body, exchange))

    def _run_loop(self):
        producer = None
        bootstrap_servers = ",".join(settings.KAFKA_BROKERS)
        
        print("--> Starting AsyncKafkaProducer background thread")

        while True:
            try:
                # 1. Establish/Re-establish connection
                if producer is None:
                    try:
                        producer = Producer({
                            "bootstrap.servers": bootstrap_servers,
                            "acks": "all",
                            "linger.ms": 50,
                            "enable.idempotence": True,
                            "message.send.max.retries": 5,
                        })
                        print("--> AsyncKafkaProducer connected to Kafka")
                    except Exception as e:
                        print(f"--> Connection failed: {e}. Retrying in 5s...")
                        time.sleep(5)
                        continue

                # 2. Get message from queue
                try:
                    # Wait up to 1s for a message to allow heartbeat processing
                    item = self._queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                event_type, body, exchange = item

                # 3. Publish
                try:
                    idempotency_key = str(uuid.uuid4())
                    message = {
                        'event_type': event_type,
                        'idempotency_key': idempotency_key,
                        'data': body
                    }

                    headers = {}
                    inject(headers)
                    kafka_headers = [(k, str(v).encode("utf-8")) for k, v in headers.items()]

                    with self._tracer.start_as_current_span("kafka.publish", attributes={
                        "messaging.system": "kafka",
                        "messaging.destination": exchange,
                        "messaging.destination_kind": "topic",
                        "messaging.kafka.message_key": event_type,
                        "messaging.message_id": idempotency_key,
                    }):
                        producer.produce(
                            exchange,
                            value=json.dumps(message).encode("utf-8"),
                            key=event_type.encode("utf-8"),
                            headers=kafka_headers,
                        )
                        producer.poll(0)
                        producer.flush(10)
                    
                    print(f"--> [Async] Event Published: {event_type} (key: {idempotency_key})")
                    
                except KafkaError as e:
                    print(f"--> [Error] Lost connection during publish: {e}")
                    # Re-queue the message to be tried again after reconnect
                    self._queue.put(item)
                    if producer:
                        try:
                            producer.flush(5)
                        except Exception:
                            pass
                    producer = None
                    time.sleep(1)
                except Exception as e:
                    print(f"--> [Error] Failed to publish {event_type}: {e}")
                    # Don't re-queue bad data
                finally:
                    self._queue.task_done()
                    
            except Exception as e:
                print(f"--> [Critical] Producer Loop Error: {e}")
                if producer:
                    try:
                        producer.flush(5)
                    except Exception:
                        pass
                producer = None
                time.sleep(5)

# Singleton instance
_producer = AsyncKafkaProducer()

def publish_event(event_type, body, exchange='booking_events'):
    _producer.publish(event_type, body, exchange)
