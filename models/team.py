# models.team
from bson import ObjectId
from mongoengine import *

from functions import return_oid

class PastPlayer(EmbeddedDocument):
    _id = ObjectIdField(default=ObjectId, required=True, primary_key=True)
    player_id = ReferenceField('Team', dbref=False)
    start_date = StringField(default=None)
    end_date = StringField(default=None)
class Team(Document): 
    name = StringField(required=True)
    roster = ListField(ReferenceField('Player', dbref=False, default=[]))
    matches = ListField(ReferenceField('Match', dbref=False, default=[]))
    comps = ListField(ReferenceField('Competition', dbref=False, default=[]))
    past_players = EmbeddedDocumentListField(PastPlayer, default=[])
    meta = {
        'collection': 'teams',
        'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.match import Match
        from models.competition import Competition
        from models.player import Player
        self.player = Player()
        self.competition = Competition()
        
    @classmethod
    def convert_object_ids_to_string(cls, data):
        if isinstance(data, dict):
            return {key: cls.convert_object_ids_to_string(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls.convert_object_ids_to_string(item) for item in data]
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data
    
    @classmethod
    def get_team_by_id(cls, team_id):
        try:
            team = cls.objects(id=ObjectId(team_id)).first()
            return cls.convert_object_ids_to_string(team.to_mongo())
        except Exception as e:
            return {"error": f"Failed to retrieve team: {str(e)}"}
        
    @classmethod
    def get_all_teams(cls):
        try:
            teams = cls.objects()
            serialized_teams = [cls.convert_object_ids_to_string(team.to_mongo()) for team in teams]
            return serialized_teams
        except Exception as e :
            return {"error": f"Failed to retrieve teams: {str(e)}"}
    