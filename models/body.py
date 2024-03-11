# models.body

from mongoengine import *


class Body(Document):
    name = StringField(required=True)
    competitions = ListField(ReferenceField('Competition', dbref=False), default=[])
    meta = {
    'collection': 'bodies',
    'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.competition import Competition
        self.name = values['name']
