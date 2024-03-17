# matches_routes.py
from flask import Blueprint, jsonify, request
from controllers.match_controller import MatchController
from app import get_database_connection
import json
from functions import *

# Initialize the MatchController and the blueprint
db = get_database_connection()
match_controller = MatchController()
matches_blueprint = Blueprint('matches', __name__)

@matches_blueprint.route("/get-all", methods=["GET"])
def get_all_matches():
    return match_controller.get_all_matches()

@matches_blueprint.route("/get-by-id/<match_id>", methods=["GET"])
def get_match_by_id(match_id):
    return match_controller.get_match_by_id(match_id)

@matches_blueprint.route("/competition/<competition_id>", methods=["GET"])
def get_matches_by_competitionId(competition_id):
    return match_controller.get_matches_by_competitionId(competition_id)

@matches_blueprint.route("/matchIds", methods=["POST"])
def get_matches_by_matchId_array():
    match_ids = request.json.get("matchIds", [])
    return match_controller.get_matches_by_matchId_array(match_ids)


# upload match data - endpoint
@matches_blueprint.route('/upload-match-data', methods=['POST'])
def upload_match_data_v2():
    # load in match data from html request
    data = json.loads(request.data)
    return match_controller.match_data_upload(data=data)

# edit match - endpoint 
@matches_blueprint.route('/edit-match', methods=['POST'])
def edit_match():
    data = json.loads(request.data)
    return match_controller.edit_match(data=data)
