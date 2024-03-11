from flask import jsonify, request
from controllers.player_controller import PlayerController
from functions import convert_object_ids_to_string, return_oid
from models.goal import Goal
from models.match import Match, MatchStats  # Assuming Match class is defined in models.match
from mongoengine import DoesNotExist
from bson.json_util import dumps
from models.player import Player, Stats
from models.team import Team
from functions import return_oid
class MatchController:
    def __init__(self):
        self.match = Match()
        self.player = Player()
        self.PC = PlayerController()
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
            result = self.match.create_match(match_data)
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

    def match_data_upload(self, data):
        try:
            home_data = data['HomeTeam']
            away_data = data['AwayTeam']
            comp_data = data['Competition']

            home_id = return_oid(home_data['teamID'])
            away_id = return_oid(away_data['teamID'])

            match_id = return_oid(comp_data['MatchID'])
            self.PC.increment_team_matches(home_id, match_id)
            self.PC.increment_team_matches(away_id, match_id)

            home_players = home_data['Starters'] + home_data['Subs']
            away_players = away_data['Starters'] + away_data['Subs']

            home_match_stats, home_career_stats, home_events = self.PC.parse_player_stats(
                team_data=home_players, away_data=away_players, match_id=match_id)
            away_match_stats, away_career_stats, away_events = self.PC.parse_player_stats(
                team_data=away_players, away_data=home_players, match_id=match_id)
            print(
                f'RETURNED DATA\nhome_match_stats: {home_match_stats}\nhome_career_stats: {home_career_stats}\nhome_events: {home_events}\n')
            print(
                f'RETURNED DATA\naway_match_stats: {away_match_stats}\naway_career_stats: {away_career_stats}\naway_events: {away_events}\n')
            match_events = sorted(home_events + away_events, key=lambda x: int(x['minute']))

            for player in home_career_stats + away_career_stats:
                player.update(
                    set__stats=player['stats'],
                    set__performance=player['performance'],
                    add_to_set__matches=match_id
                )
            # Assuming `Team` is your MongoEngine model
            Team.objects(id__in=[home_id, away_id]).update(add_to_set__matches=match_id)
            # Update the document
            result = Match.objects(id=match_id).update(set__home_stats = home_match_stats, 
                                                       set__away_stats= away_match_stats, 
                                                       set__match_events = match_events, 
                                                       set__data_entered=True)
            if result > 0:
                # Document was updated
                updated_match_document = Match.objects.get(id=match_id)
                return jsonify({"match": Match.convert_object_ids_to_string(updated_match_document.to_mongo())}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
