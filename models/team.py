# models.team
from mongoengine import *

class Team(Document): 
    name = StringField(required=True)
    roster = ListField(ReferenceField('Player', dbref=True, default=[]))
    matches = ListField(ReferenceField('Match', dbref=True, default=[]))
    comps = ListField(ReferenceField('Competition', dbref=True, default=[]))

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.match import Match
        from models.competition import Competition
        from models.player import Player
        self.name = values['name']
        self.roster = values['roster']
        self.matches = values['matches']
        self.comps = values['comps']