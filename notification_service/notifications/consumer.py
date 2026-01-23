from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
import json
import threading
import time
from opentelemetry import trace
from opentelemetry.propagate import extract
from confluent_kafka import Consumer, KafkaError

def start_consumer():
    """
    Starts the Kafka consumer in a separate thread, with connection retries.
    """
    max_retries = 10
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            consumer = Consumer({
                "bootstrap.servers": ",".join(settings.KAFKA_BROKERS),
                "group.id": "notification_service_main",
                "enable.auto.commit": False,
                "auto.offset.reset": "earliest",
            })

            consumer.subscribe(["booking_events"])

            print("Notification Service successfully connected. Waiting for messages in booking_events")

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

                    # print("Callback called with body:", message.value())
                    try:
                        data = json.loads(message.value().decode("utf-8"))
                        event_type = data.get("event_type")
                        payload = data.get("data")
                        idempotency_key = data.get("idempotency_key")

                        print(f"Notification Consumer received: {event_type}")

                        headers = {k: (v.decode("utf-8") if v else "") for k, v in (message.headers() or [])}
                        context = extract(headers)

                        with tracer.start_as_current_span("kafka.consume", context=context, attributes={
                            "messaging.system": "kafka",
                            "messaging.destination": "booking_events",
                            "messaging.destination_kind": "topic",
                            "messaging.kafka.message_key": event_type,
                            "messaging.message_id": idempotency_key,
                        }):
                            # Handle enriched flight events (from booking service)
                            if event_type.startswith("flight_"):
                                # Check if this event has already been processed
                                if Notification.objects(event_idempotency_key=idempotency_key).first():
                                    print(f" [x] Duplicate event {event_type} ignored: {idempotency_key}")
                                    consumer.commit(message=message)
                                    continue

                                user_bookings = payload.get("userBookings", [])
                                flight_number = payload.get("flight_number")
                                timestamp = payload.get("timestamp")

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
                        
                        consumer.commit(message=message)

                    except Exception as e:
                        print(f" [!] Error processing message: {e}")
                        # Drop message if error (commit offset)
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
                break # Exit loop if max retries reached
        except Exception as e:
            # Handle non-Kafka errors (e.g., config issues)
            print(f"An unexpected error occurred: {e}")
            break


def run_consumer_thread():
    # Run the consumer in a background thread so it doesn't block Django
    t = threading.Thread(target=start_consumer)
    t.daemon = True
    t.start()
