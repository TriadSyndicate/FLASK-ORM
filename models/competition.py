from bson import ObjectId
from mongoengine import *

from functions import convert_object_ids_to_string


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
        
    # get all competitions
    @classmethod
    def get_all_competitions(cls):
        try:
            competitions = cls.objects()  # Retrieve all documents from the collection
            serialized_competitions = [convert_object_ids_to_string(competition.to_mongo()) for competition in competitions]
            return serialized_competitions  # Return serialized competitions as a list of dictionaries
        except Exception as e:
            return {"error": f"Failed to retrieve competitions: {str(e)}"}
        
    # Get specific player by Id
    @classmethod
    def get_competition_by_id(cls, competition_id):
        try:
            competition = cls.objects(id=ObjectId(competition_id)).first()
            return convert_object_ids_to_string(competition.to_mongo())
        except Exception as e:
            return {"error": f"Failed to retrieve competition: {str(e)}"}
