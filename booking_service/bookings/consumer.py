import json
import pika
import threading
import time
import os
from django.conf import settings
from .producer import publish_event
from .models import Booking
from pika.exceptions import AMQPConnectionError


def start_flight_event_consumer():
    """
    Starts a RabbitMQ consumer for flight events in a separate thread.
    Listens for flight events and enriches them with user IDs from active bookings.
    """
    print("Starting flight event consumer (Resilient)")
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            params = pika.URLParameters(settings.RABBITMQ_URL)
            params.heartbeat = 600
            connection = pika.BlockingConnection(params)
            channel = connection.channel()

            # Durable Exchange
            channel.exchange_declare(exchange="flight_events", exchange_type="fanout", durable=True)

            # Durable, Named Queue (Shared by replicas, survives restarts)
            queue_name = "booking_service_enrichment"
            channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind
            channel.queue_bind(exchange="flight_events", queue=queue_name)

            # QoS: Process 1 message at a time, preventing overload
            channel.basic_qos(prefetch_count=1)

            print(f"Booking Service Flight Consumer connected. Waiting for messages in {queue_name}")

            def callback(ch, method, properties, body):
                try:
                    data = json.loads(body)
                    event_type = data.get("event_type")
                    idempotency_key = data.get("idempotency_key")
                    payload = data.get("data")

                    print(f"Booking Consumer received: {event_type} - {payload}")

                    flight_id = payload.get("flight_id")

                    # Find all active (non-cancelled) bookings for this flight
                    active_bookings = Booking.objects.filter(
                        flight_id=flight_id,
                        status='CONFIRMED'
                    )

                    # Extract user IDs and booking IDs from active bookings
                    booking_data = list(active_bookings.values('user_id', 'booking_id'))

                    print(f"Found {len(booking_data)} active bookings for flight {flight_id}")

                    if booking_data:
                        # Create enriched event data
                        enriched_payload = payload.copy()
                        enriched_payload['userBookings'] = [
                            {'user_id': str(item['user_id']), 'booking_id': str(item['booking_id'])}
                            for item in booking_data
                        ]

                        print(f"Enriched payload: {enriched_payload}")

                        # Publish enriched event to notification service
                        publish_event(event_type, enriched_payload)

                        print(f" [x] Enriched flight event {event_type} for {len(booking_data)} users")
                    else:
                        print(f" [x] No active bookings found for flight {flight_id}")
                    
                    # Manual Ack: Confirm processing success
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                except Exception as e:
                    print(f" [!] Error processing flight event: {e}")
                    # Requeue=False -> Dead Letter or Drop (prevent infinite loop)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

            channel.basic_consume(
                queue=queue_name, on_message_callback=callback
                # auto_ack=False is default
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
                break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
