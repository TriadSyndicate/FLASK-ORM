from flask import jsonify
from functions import convert_object_ids_to_string
from models.competition import Competition

class CompetitionController:
    def __init__(self):
        self.competition = Competition()
        
    def get_all_competitions(self):
        try:
            competitions = self.competition.get_all_competitions()
            serialized_competitions = [convert_object_ids_to_string(competition) 
                                       for competition in competitions
                                       ]
            return jsonify({"competitions": serialized_competitions}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    def get_competition_by_id(self, competition_id):
        try:
            competition = self.competition.get_competition_by_id(competition_id)
            return jsonify({"competition": convert_object_ids_to_string(competition)}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500