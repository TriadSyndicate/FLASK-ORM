# models.team
from bson import ObjectId
from mongoengine import *

class Team(Document): 
    name = StringField(required=True)
    roster = ListField(ReferenceField('Player', dbref=True, default=[]))
    matches = ListField(ReferenceField('Match', dbref=True, default=[]))
    comps = ListField(ReferenceField('Competition', dbref=True, default=[]))
    meta = {
        'collection': 'teams',
        'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.match import Match
        from models.competition import Competition
        from models.player import Player
        self.name = values['name']
        self.roster = values['roster']
        self.matches = values['matches']
        self.comps = values['comps']
        
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
            serialized_teams = [cls.convert_object_ids_to_string(team.to_mongo() for team in teams)]
            return serialized_teams
        except Exception as e :
            return {"error": f"Failed to retrieve teams: {str(e)}"}
    