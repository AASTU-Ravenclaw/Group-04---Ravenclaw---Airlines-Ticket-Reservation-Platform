import pika
import json
import uuid
import threading
import queue
import time
from django.conf import settings

class AsyncAMQPProducer:
    def __init__(self):
        self._queue = queue.Queue()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def publish(self, event_type, body, exchange='booking_events'):
        """
        Non-blocking publish. Puts message in local queue and returns immediately.
        """
        self._queue.put((event_type, body, exchange))

    def _run_loop(self):
        connection = None
        channel = None
        
        print("--> Starting AsyncAMQPProducer background thread")

        while True:
            try:
                # 1. Establish/Re-establish connection
                if connection is None or connection.is_closed:
                    try:
                        params = pika.URLParameters(settings.RABBITMQ_URL)
                        params.heartbeat = 600
                        params.blocked_connection_timeout = 300
                        connection = pika.BlockingConnection(params)
                        channel = connection.channel()
                        print("--> AsyncAMQPProducer connected to RabbitMQ")
                    except Exception as e:
                        print(f"--> Connection failed: {e}. Retrying in 5s...")
                        time.sleep(5)
                        continue

                # 2. Get message from queue
                try:
                    # Wait up to 1s for a message to allow heartbeat processing
                    item = self._queue.get(timeout=1.0)
                except queue.Empty:
                    # Process heartbeats to keep connection alive during idle times
                    if connection and not connection.is_closed:
                        connection.process_data_events()
                    continue

                event_type, body, exchange = item

                # 3. Publish
                try:
                    # Ensure exchange exists (idempotent, using durable=True)
                    channel.exchange_declare(exchange=exchange, exchange_type='fanout', durable=True)
                    
                    idempotency_key = str(uuid.uuid4())
                    message = {
                        'event_type': event_type,
                        'idempotency_key': idempotency_key,
                        'data': body
                    }
                    
                    channel.basic_publish(
                        exchange=exchange,
                        routing_key=event_type,
                        body=json.dumps(message),
                        properties=pika.BasicProperties(
                            delivery_mode=2,  # Persistent
                            content_type='application/json'
                        )
                    )
                    
                    print(f"--> [Async] Event Published: {event_type} (key: {idempotency_key})")
                    
                except (pika.exceptions.AMQPConnectionError, pika.exceptions.StreamLostError) as e:
                    print(f"--> [Error] Lost connection during publish: {e}")
                    # Re-queue the message to be tried again after reconnect
                    self._queue.put(item)
                    connection = None # Force reconnect
                    time.sleep(1)
                except Exception as e:
                    print(f"--> [Error] Failed to publish {event_type}: {e}")
                    # Don't re-queue bad data
                finally:
                    self._queue.task_done()
                    
            except Exception as e:
                print(f"--> [Critical] Producer Loop Error: {e}")
                connection = None
                time.sleep(5)

# Singleton instance
_producer = AsyncAMQPProducer()

def publish_event(event_type, body, exchange='booking_events'):
    _producer.publish(event_type, body, exchange)
