# models.watchlist

from mongoengine import *

class WatchList(DynamicDocument):
    player_id = ReferenceField('Player')
    scout_name = StringField()
    category = StringField()
    add_date = StringField()

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.player import Player
        self.scout_name = values['scout_name']
        self.category = values['category']
        self.add_date = values['add_date']


class PlayerInList(EmbeddedDocument):
    player_id = ReferenceField('Player', dbref=False)
    addedDate = ListField(DateTimeField())
    removedDate = ListField(DateTimeField())
    onList=BooleanField()


class NewWatchList(DynamicDocument):
    scout_id = StringField()
    category = StringField()
    players = EmbeddedDocumentListField(PlayerInList, default=[])
