# models.country

from mongoengine import *


class Country(Document):
    name = StringField(required=True)
    teams = ListField(ReferenceField('Team', dbref=True, default=[]))

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.team import Team
        self.name = values['name']
        self.teams = values['teams']
