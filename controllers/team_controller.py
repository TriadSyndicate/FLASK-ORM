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
            