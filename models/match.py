#models.match

from mongoengine import Document, ReferenceField, StringField, BooleanField, \
    IntField, EmbeddedDocumentListField, EmbeddedDocument, ListField
from bson import ObjectId

from models.player import Goal, Player
from models.competition import Competition 
from models.team import Team


class MatchStats(EmbeddedDocument):
    match_id = ReferenceField('Match', dbref=False)
    player_id = ReferenceField('Player', dbref=False)
    starter = BooleanField(default=False)
    min_played = IntField(default=0)
    goals = EmbeddedDocumentListField(Goal, default=[])
    assists = IntField(default=0)
    yellow_cards = IntField(default=0)
    red_cards = IntField(default=0)
    own_goals = IntField(default=0)

class Match(Document):
    competition_id = ReferenceField('Competition', dbref=False)
    home_team = ReferenceField('Team', dbref=False)
    away_team = ReferenceField('Team', dbref=False)
    date = StringField()
    venue = StringField(default=None)
    match_url = StringField(default=None)
    home_stats = EmbeddedDocumentListField(MatchStats, dbref=False, default=[])
    away_stats = EmbeddedDocumentListField(MatchStats, dbref=False, default=[])
    data_entered = BooleanField(default=False)
    match_events = ListField(default=[])

    meta = {
        'collection': 'matches',
        'strict': False
    }
    

    @classmethod
    def create_match(cls, competition_id, home_team, away_team, date, venue, match_url, home_stats, away_stats, data_entered, match_events):
        match_data = {
            "competition_id": competition_id,
            "home_team": home_team,
            "away_team": away_team,
            "date": date,
            "venue": venue,
            "match_url": match_url,
            "home_stats": home_stats,
            "away_stats": away_stats,
            "data_entered": data_entered,
            "match_events": match_events,
        }
        match = cls(**match_data)
        try:
            match.save()
            return str(match.id)
        except Exception as e:
            return {"error": f"Failed to create match: {str(e)}"}

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
    def get_all_matches(cls):
        try:
            matches = cls.objects()  # Retrieve all documents from the collection
            serialized_matches = [cls.convert_object_ids_to_string(match.to_mongo()) for match in matches]
            return serialized_matches  # Return serialized matches as a list of dictionaries
        except Exception as e:
            return {"error": f"Failed to retrieve matches: {str(e)}"}


    @classmethod
    def get_match_by_id(cls, match_id):
        try:
            match = cls.objects(id=ObjectId(match_id)).first()
            return cls.convert_object_ids_to_string(match.to_mongo())
        except Exception as e:
            return {"error": f"Failed to retrieve match: {str(e)}"}

    @classmethod
    def get_matches_by_competitionId(cls, competition_id):
        try:
            matches = cls.objects(competition_id=ObjectId(competition_id))
            return [cls.convert_object_ids_to_string(match.to_mongo()) for match in matches]
        except Exception as e:
            return {"error": f"Failed to retrieve matches: {str(e)}"}

    @classmethod
    def get_matches_by_matchId_array(cls, match_ids):
        try:
            object_ids = [ObjectId(match_id) for match_id in match_ids]
            matches = cls.objects(id__in=object_ids)
            return [cls.convert_object_ids_to_string(match.to_mongo()) for match in matches]
        except Exception as e:
            return {"error": f"Failed to retrieve matches: {str(e)}"}
        
