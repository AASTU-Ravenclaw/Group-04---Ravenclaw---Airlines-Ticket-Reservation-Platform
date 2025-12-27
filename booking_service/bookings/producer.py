import pika
import json
from django.conf import settings

def publish_event(event_type, body):

    try:
        # Connect to RabbitMQ
        params = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        channel.exchange_declare(exchange='booking_events', exchange_type='fanout')

        message = {
            'event_type': event_type,
            'data': body
        }

        channel.basic_publish(
            exchange='booking_events',
            routing_key=event_type,
            body=json.dumps(message)
        )
        
        print(f"--> Event Published: {event_type}")
        connection.close()
    except Exception as e:
        print(f"--> Failed to publish event: {str(e)}")