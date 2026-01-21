from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from pika.exceptions import AMQPConnectionError
import pika
import json
import threading
import time
import os

def start_consumer():
    """
    Starts the RabbitMQ consumer in a separate thread, with connection retries.
    """
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            params = pika.URLParameters(settings.RABBITMQ_URL)
            params.heartbeat = 600
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # Durable Exchange
            channel.exchange_declare(exchange="booking_events", exchange_type="fanout", durable=True)

            # Durable Named Queue
            queue_name = "notification_service_main"
            channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind
            channel.queue_bind(exchange="booking_events", queue=queue_name)

            # QoS
            channel.basic_qos(prefetch_count=1)

            print(f"Notification Service successfully connected. Waiting for messages in {queue_name}")

            def callback(ch, method, properties, body):
                # print("Callback called with body:", body)
                try:
                    data = json.loads(body)
                    event_type = data.get("event_type")
                    payload = data.get("data")
                    idempotency_key = data.get("idempotency_key")

                    print(f"Notification Consumer received: {event_type}")

                    # Handle enriched flight events (from booking service)
                    if event_type.startswith("flight_"):
                        # Check if this event has already been processed
                        if Notification.objects(event_idempotency_key=idempotency_key).first():
                            print(f" [x] Duplicate event {event_type} ignored: {idempotency_key}")
                            ch.basic_ack(delivery_tag=method.delivery_tag)
                            return

                        user_bookings = payload.get("userBookings", [])
                        flight_number = payload.get("flight_number")
                        timestamp = payload.get("timestamp")

                        # print(f"Flight event {event_type} for flight {flight_number}, user_bookings: {user_bookings}")

                        message_text = ""
                        if event_type == "flight_delayed":
                            new_time = payload.get("new_departure_time")
                            message_text = f"Flight {flight_number} has been delayed. New departure time: {new_time}"
                        elif event_type == "flight_cancelled":
                            message_text = f"Flight {flight_number} has been cancelled."
                        elif event_type == "flight_boarding":
                            message_text = f"Flight {flight_number} is now boarding."

                        # Create notification for each affected user booking
                        for user_booking in user_bookings:
                            user_id = user_booking['user_id']
                            booking_id = user_booking['booking_id']
                            key = f"{idempotency_key}_{user_id}_{booking_id}"
                            
                            # Check for duplicate notifications
                            if not Notification.objects(idempotency_key=key).first():
                                try:
                                    notification = Notification(
                                        user_id=user_id,
                                        booking_id=booking_id,
                                        event_type=event_type,
                                        message=message_text,
                                        payload=payload,
                                        timestamp=timestamp,
                                        idempotency_key=key,
                                        event_idempotency_key=idempotency_key,
                                    )
                                    notification.save()
                                    # print(f" [x] Saved flight notification for user {user_id}, booking {booking_id}")
                                except Exception as e:
                                    print(f" [x] Failed to save flight notification for user {user_id}, booking {booking_id}: {e}")
                                    continue

                                # Send real-time notification via WebSocket
                                try:
                                    channel_layer = get_channel_layer()
                                    async_to_sync(channel_layer.group_send)(
                                        f'notifications_{user_id}',
                                        {
                                            'type': 'notification_message',
                                            'message': notification.to_dict()
                                        }
                                    )
                                except Exception as e:
                                    print(f" [x] Failed to send WebSocket notification: {e}")
                            else:
                                pass
                                # print(f" [x] Duplicate notification ignored for user {user_id}")

                    # Handle regular booking events
                    else:
                        user_id = payload.get("user_id")
                        booking_id = payload.get("booking_id")
                        timestamp = payload.get("timestamp")

                        message_text = ""
                        if event_type == "booking_created":
                            message_text = f"Booking confirmed for flight {payload.get('flight_id')}"
                        elif event_type == "booking_cancelled":
                            message_text = f"Booking {booking_id} has been cancelled."

                        if message_text:
                            # Check for duplicate events using idempotency key
                            if not Notification.objects(idempotency_key=idempotency_key).first():
                                try:
                                    notification = Notification(
                                        user_id=user_id,
                                        booking_id=booking_id,
                                        event_type=event_type,
                                        message=message_text,
                                        payload=payload,
                                        timestamp=timestamp,
                                        idempotency_key=idempotency_key,
                                        event_idempotency_key=idempotency_key,
                                    )
                                    notification.save()
                                    print(f" [x] Saved notification for user {user_id}")

                                    # Send real-time notification via WebSocket
                                    channel_layer = get_channel_layer()
                                    async_to_sync(channel_layer.group_send)(
                                        f'notifications_{user_id}',
                                        {
                                            'type': 'notification_message',
                                            'message': notification.to_dict()
                                        }
                                    )
                                except Exception as e:
                                    print(f" [!] Failed to process booking notification: {e}")
                            else:
                                print(f" [x] Duplicate event ignored: {idempotency_key}")
                    
                    # Manual Ack
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                except Exception as e:
                    print(f" [!] Error processing message: {e}")
                    # Drop message if error (logging it)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_consume(
                queue=queue_name, on_message_callback=callback
            )

            # Start a background thread to periodically update liveness file
            stop_event = threading.Event()

            def health_loop():
                while not stop_event.is_set():
                    try:
                        with open("/tmp/healthy", "w") as f:
                            f.write(str(time.time()))
                    except Exception:
                        pass
                    time.sleep(5)

            t = threading.Thread(target=health_loop, daemon=True)
            t.start()

            # Begin consuming messages (blocking until error/stop)
            channel.start_consuming()

            # Stop health loop if we exit consuming
            stop_event.set()
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
