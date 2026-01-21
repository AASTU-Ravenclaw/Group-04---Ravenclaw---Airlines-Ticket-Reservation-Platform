from mongoengine import Document, StringField, DateTimeField, BooleanField, DictField
import datetime


class Notification(Document):
    meta = {
        "collection": "notifications",
        "indexes": ["user_id", ("user_id", "-timestamp"), "idempotency_key", "event_idempotency_key"],
    }

    user_id = StringField(required=True)
    booking_id = StringField(required=False)
    event_type = StringField(required=True)
    message = StringField(required=True)
    payload = DictField()
    is_read = BooleanField(default=False)
    timestamp = StringField(default=datetime.datetime.utcnow().isoformat)
    idempotency_key = StringField(unique=True, required=True)
    event_idempotency_key = StringField(required=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "message": self.message,
            "event_type": self.event_type,
            "is_read": self.is_read,
            "timestamp": self.timestamp,
        }
