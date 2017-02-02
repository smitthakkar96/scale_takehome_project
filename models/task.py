from datetime import datetime

from mongoengine import DynamicDocument, StringField, IntField, ListField, DictField
from mongoengine import DateTimeField


class Task(DynamicDocument):
    created_at = DateTimeField(default = datetime.now())
    completed_at = DateTimeField(default = None)
    status = StringField(default="pending")
    instruction = StringField()
    deadLine = DateTimeField()
    params = DictField()
    type = StringField()