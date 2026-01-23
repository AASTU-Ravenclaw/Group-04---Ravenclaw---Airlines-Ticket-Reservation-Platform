import json
import threading
import time
from django.conf import settings
from .producer import publish_event
from .models import Booking
from opentelemetry import trace
from opentelemetry.propagate import extract
from confluent_kafka import Consumer, KafkaError


def start_flight_event_consumer():
    """
    Starts a Kafka consumer for flight events in a separate thread.
    Listens for flight events and enriches them with user IDs from active bookings.
    """
    print("Starting flight event consumer (Resilient)")
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            consumer = Consumer({
                "bootstrap.servers": ",".join(settings.KAFKA_BROKERS),
                "group.id": "booking_service_enrichment",
                "enable.auto.commit": False,
                "auto.offset.reset": "earliest",
            })

            consumer.subscribe(["flight_events"])

            print("Booking Service Flight Consumer connected. Waiting for messages in flight_events")

            tracer = trace.get_tracer(__name__)

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

            try:
                while True:
                    message = consumer.poll(1.0)
                    if message is None:
                        continue
                    if message.error():
                        print(f" [!] Kafka error: {message.error()}")
                        continue

                    try:
                        data = json.loads(message.value().decode("utf-8"))
                        event_type = data.get("event_type")
                        idempotency_key = data.get("idempotency_key")
                        payload = data.get("data")

                        print(f"Booking Consumer received: {event_type} - {payload}")

                        headers = {k: (v.decode("utf-8") if v else "") for k, v in (message.headers() or [])}
                        context = extract(headers)

                        with tracer.start_as_current_span("kafka.consume", context=context, attributes={
                            "messaging.system": "kafka",
                            "messaging.destination": "flight_events",
                            "messaging.destination_kind": "topic",
                            "messaging.kafka.message_key": event_type,
                            "messaging.message_id": idempotency_key,
                        }):
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

                        consumer.commit(message=message)

                    except Exception as e:
                        print(f" [!] Error processing flight event: {e}")
                        # Commit offset to drop the problematic message
                        consumer.commit(message=message)

            finally:
                stop_event.set()
                consumer.close()
            return

        except KafkaError as e:
            if attempt < max_retries - 1:
                print(f"Could not connect to Kafka: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Could not connect to Kafka: {e}. Maximum retries ({max_retries}) reached. Consumer failed to start.")
                break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break
