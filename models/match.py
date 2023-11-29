from bson import ObjectId


class MatchModel:
    def __init__(self, db):
        self.matches = db["matches"]

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
        result = self.matches.insert_one(match_data)
        return result.inserted_id

    # Convert objectIds to Strin
    def convert_object_ids_to_string(self, data):
        if isinstance(data, dict):
            serialized_data = {}
            for key, value in data.items():
                serialized_data[key] = self.convert_object_ids_to_string(value)
            return serialized_data
        elif isinstance(data, list):
            return [self.convert_object_ids_to_string(item) for item in data]
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data

    # Get all matches
    def get_all_matches(self):
        try:
            matches = self.matches.find()  # Retrieve all documents from the collection
            serialized_matches = []
            for match in matches:
                serialized_match = self.convert_object_ids_to_string(match)
                serialized_matches.append(serialized_match)
            return serialized_matches  # Return serialized matches as a list of dictionaries
        except Exception as e:
            return {
                "error": str(e)
            }  # Returning an error dictionary if an exception occurs

    def get_match_by_id(self, match_id):
        return self.matches.find_one({"_id": ObjectId(match_id)})

    # Get all matches based on competition Id
    def get_matches_by_competitionId(self, competitionId):
        return self.matches.find({"competition_id": ObjectId(competitionId)})

    # Get matches based from array with matchIds
    def get_matches_by_matchId_array(self, matchIds):
        try:
            # Convert string IDs to ObjectId
            object_ids = [ObjectId(match_id) for match_id in matchIds]
            query = {"_id": {"$in": object_ids}}
            matches = self.matches.find(query)
            return list(matches)
        except Exception as e:
            return {"error": str(e)}

    # Other CRUD operations as needed
