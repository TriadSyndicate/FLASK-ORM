
from flask import jsonify
from models.fixture import Fixture
from functions import convert_object_ids_to_string


class FixtureController:
    def __init__(self):
        self.fixture = Fixture()
        
    # get all fixtures
    def get_all_fixtures(self):
        try:
            fixtures = self.fixture.get_all_fixtures()
            serialized_fixtures = [convert_object_ids_to_string(fixture) for fixture in fixtures]
            return jsonify({"fixtures": serialized_fixtures}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500