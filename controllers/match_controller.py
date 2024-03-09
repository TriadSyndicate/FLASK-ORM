from flask import jsonify
from models.match import Match  # Assuming Match class is defined in models.match

class MatchController:
    def __init__(self):
        self.match = Match()
        
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
            match_data = {
                "competition_id": competition_id,
                "home_team": home_team,
                "away_team": away_team,
                "date": date,
                "venue": venue,
                "home_stats": home_stats,
                "away_stats": away_stats,
                "data_entered": data_entered,
                "match_events": match_events,
            }
            # Use keyword arguments when instantiating Match
            match = Match(db=self.db, **match_data)
            result = self.match.create_match()
            return (
                jsonify(
                    {"message": "Match created successfully", "match_id": str(result)}
                ),
                201,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_all_matches(self):
        try:
            # Use keyword arguments when instantiating Match
            matches = self.match.get_all_matches()
            serialized_matches = [
                self.match.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_match_by_id(self, match_id):
        try:
            # Use keyword arguments when instantiating Match
            match_obj = self.match.get_match_by_id(match_id)
            serialized_match = self.match.convert_object_ids_to_string(match_obj)
            if match_obj:
                return jsonify(serialized_match), 200
            return jsonify({"message": "Match not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_matches_by_competitionId(self, competitionId):
        try:
            # Use keyword arguments when instantiating Match
            matches = self.match.get_matches_by_competitionId(competitionId)
            serialized_matches = [
                self.match.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_matches_by_matchId_array(self, matchIds):
        try:
            # Use keyword arguments when instantiating Match
            matches = self.match.get_matches_by_matchId_array(matchIds)
            serialized_matches = [
                self.match.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
