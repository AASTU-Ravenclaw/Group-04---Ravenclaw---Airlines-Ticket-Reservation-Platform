import json
import pika
import threading
import time
from django.conf import settings
from .models import Notification
from pika.exceptions import AMQPConnectionError


def start_consumer():
    """
    Starts the RabbitMQ consumer in a separate thread, with connection retries.
    """
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            params = pika.URLParameters(settings.RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            channel.exchange_declare(exchange="booking_events", exchange_type="fanout")

            result = channel.queue_declare(queue="", exclusive=True)
            queue_name = result.method.queue
            channel.queue_bind(exchange="booking_events", queue=queue_name)

            print(f"Notification Service successfully connected. Waiting for messages in {queue_name}")

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    event_type = data.get("event_type")
                    payload = data.get("data")

                    user_id = payload.get("user_id")
                    booking_id = payload.get("booking_id")
                    timestamp = payload.get("timestamp")

                    message_text = ""
                    if event_type == "booking_created":
                        message_text = (
                            f"Booking confirmed for flight {payload.get('flight_id')}"
                        )
                    elif event_type == "booking_cancelled":
                        message_text = f"Booking {booking_id} has been cancelled."

                    if not Notification.objects(
                        booking_id=booking_id, event_type=event_type
                    ).first():
                        Notification(
                            user_id=user_id,
                            booking_id=booking_id,
                            event_type=event_type,
                            message=message_text,
                            payload=payload,
                            timestamp=timestamp,
                        ).save()
                        print(f" [x] Saved notification for user {user_id}")

                except Exception as e:
                    print(f" [!] Error processing message: {e}")

            channel.basic_consume(
                queue=queue_name, on_message_callback=callback, auto_ack=True
            )
            channel.start_consuming()
            return 

        except AMQPConnectionError as e:
            if attempt < max_retries - 1:
                print(f"Could not connect to RabbitMQ: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Could not connect to RabbitMQ: {e}. Maximum retries ({max_retries}) reached. Consumer failed to start.")
                break # Exit loop if max retries reached
        except Exception as e:
            # Handle non-AMQP errors (e.g., config issues)
            print(f"An unexpected error occurred: {e}")
            break


def run_consumer_thread():
    # Run the consumer in a background thread so it doesn't block Django
    t = threading.Thread(target=start_consumer)
    t.daemon = True
    t.start()