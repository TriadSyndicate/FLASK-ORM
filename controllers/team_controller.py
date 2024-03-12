# team_controller
from flask import jsonify, request
from functions import convert_object_ids_to_string, return_oid
from models.team import Team
from mongoengine import *



class TeamController:
    def __init__(self):
        self.team = Team()
    def get_all_teams(self):
        try: 
            teams = self.team.get_all_teams()
            serialized_teams = [convert_object_ids_to_string(team) for team in teams]
            return jsonify({"teams": serialized_teams}),200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    def get_team_by_id(self, team_id):
        try:
            team_obj = self.team.get_team_by_id(team_id)
            serialized_team = convert_object_ids_to_string(team_obj)
            if(team_obj):
                return jsonify(serialized_team), 200
            return jsonify({"message": "Team not found"}), 404
        except Exception as e:
            return jsonify({"error" : str(e)}), 500
    def get_team_and_players_by_id(self, team_id):
        try:
            team_obj = self.team.get_team_by_id(team_id)
            from models.player import Player
            player_ids = [return_oid(str(player_id)) for player_id in team_obj['roster']]
            player_ids = [player_id for player_id in player_ids if player_id is not None]
            team_players = Player.objects(id__in=player_ids)
            team_obj['roster'] = [player.to_mongo() for player in team_players]
            return jsonify(convert_object_ids_to_string(team_obj)), 200
        except Exception as e:
            return jsonify({"error" : str(e)}), 500
            
            