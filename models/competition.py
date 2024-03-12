from mongoengine import *


class Competition(Document):
    name = StringField(required=True)
    teams = ListField(ReferenceField('Team', dbref=False, default=[]))
    body_id = ReferenceField('Body', dbref=False, default=None)
    meta = {
    'collection': 'competitions',
    'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.body import Body
        from models.team import Team
