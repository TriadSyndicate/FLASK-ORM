# models.goal
from mongoengine import EmbeddedDocument, IntField, ReferenceField

class Goal(EmbeddedDocument):
    minute = IntField(default=None)
    match_id = ReferenceField('Match', dbref=False)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.match import Match
        self.minute = values['minute']
