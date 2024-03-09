# models.short_list

from mongoengine import *

class ShortList(DynamicDocument):
    scout_id = StringField()
    date = DateTimeField()
    player_ids = ListField(ReferenceField('Player', dbref=False))
    category = StringField()
    week = IntField()

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.player import Player


class PlayersSList(EmbeddedDocument):
    player_id = ReferenceField('Player', required=True)
    scout_id = ListField(StringField())

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.player import Player


class HeadShortList(DynamicDocument):
    scout_id = StringField()
    date = DateTimeField()
    players = EmbeddedDocumentListField(PlayersSList, default=[])
    category = StringField()
    week = IntField()

    def __init__(self, *args, **values):
        super().__init__(*args, **values)


