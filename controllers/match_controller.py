from bson import ObjectId
from flask import jsonify, request
from models.match import MatchModel
from pymongo import MongoClient


class MatchController:
    def __init__(self, db):
        self.match_model = MatchModel(db)

    def create_match(
        self,
        competition_id,
        home_team,
        away_team,
        date,
        venue,
        home_stats,
        away_stats,
        data_entered,
        match_events,
    ):
        try:
            result = self.match_model.create_match(
                competition_id,
                home_team,
                away_team,
                date,
                venue,
                home_stats,
                away_stats,
                data_entered,
                match_events,
            )
            return (
                jsonify(
                    {"message": "Match created successfully", "match_id": str(result)}
                ),
                201,
            )  # 201 for resource created
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # 500 for internal server error

    def get_all_matches(self):
        try:
            matches = self.match_model.get_all_matches()
            serialized_matches = [
                self.match_model.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200  # 200 for OK
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # 500 for internal server error

    def get_match_by_id(self, match_id):
        try:
            match = self.match_model.get_match_by_id(match_id)
            match = self.match_model.convert_object_ids_to_string(match)
            print(match)
            if match:
                return jsonify(match), 200  # 200 for OK
            return jsonify({"message": "Match not found"}), 404  # 404 for not found
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # 500 for internal server error

    def get_matches_by_competitionId(self, competitionId):
        try:
            matches = self.match_model.get_matches_by_competitionId(competitionId)
            serialized_matches = [
                self.match_model.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200  # 200 for OK
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # 500 for internal server error

    def get_matches_by_matchId_array(self, matchIds):
        try:
            matches = self.match_model.get_matches_by_matchId_array(matchIds)
            serialized_matches = [
                self.match_model.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200  # 200 for OK
        except Exception as e:
            return jsonify({"error": str(e)}), 500  # 500 for internal server error
