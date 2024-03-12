
from flask import Blueprint, jsonify, request
from controllers.team_controller import TeamController
from functions import convert_object_ids_to_string, return_oid
from app import get_database_connection
from models.team import Team
from mongoengine import DoesNotExist
import json

# initialize the Team Controller and the blueprint
db = get_database_connection()

team_controller = TeamController()
teams_blueprint = Blueprint('teams', __name__)

@teams_blueprint.route('/get-all', methods=["GET"])
def get_all_teams():
    return team_controller.get_all_teams()

@teams_blueprint.route('/get-by-id/<team_id>', methods=['GET'])
def get_team_by_id(team_id):
    return team_controller.get_team_by_id(team_id)

@teams_blueprint.route('/with-players/get-by-id/<team_id>', methods=['GET'])
def get_team_and_players_by_id(team_id):
    return team_controller.get_team_and_players_by_id(team_id)