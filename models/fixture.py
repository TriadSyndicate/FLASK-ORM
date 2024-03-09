# models.fixture

from mongoengine import *

class Round(EmbeddedDocument):
    matchups = ListField(ReferenceField('Match'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models.match import Match
        self.matchups = kwargs['matchups']


class Fixture(Document):
    competition = ReferenceField('Competition')
    comp_year = StringField(default=None)
    rounds = EmbeddedDocumentListField('Round', default=[])

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.competition import Competition
        self.competition = values['competition']
        self.comp_year = values['comp_year']
        self.rounds = values['rounds']
