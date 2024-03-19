# models.fixture

from mongoengine import *

from functions import convert_object_ids_to_string

class Round(EmbeddedDocument):
    matchups = ListField(ReferenceField('Match'))
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models.match import Match

class Fixture(Document):
    competition = ReferenceField('Competition')
    comp_year = StringField(default=None)
    rounds = EmbeddedDocumentListField('Round', default=[])
    meta = {
    'collection': 'fixtures',
    'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.competition import Competition
    
    # get all fixtures
    @classmethod
    def get_all_fixtures(cls):
        try:
            fixtures = cls.objects()
            serialized_fixtures = [convert_object_ids_to_string(fixture.to_mongo()) for fixture in fixtures]
            return serialized_fixtures
        except Exception as e:
            return {"error": f"Failed to retrieve fixtures: {str(e)}"}