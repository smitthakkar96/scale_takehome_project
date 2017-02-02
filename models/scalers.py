from mongoengine import DynamicDocument, StringField, IntField, ListField
from mongoengine import ReferenceField
from .task import Task

class Scaler(DynamicDocument):
    firstname = StringField()
    lastname = StringField()
    tasksAssigned = ListField(ReferenceField(Task), default=[])
    active_tasks = IntField(default=0)