# matches_routes.py
from flask import Blueprint, jsonify, request
from controllers.match_controller import MatchController
from app import get_database_connection
import json
from functions import *
# Initialize the MatchController and the blueprint
db = get_database_connection()
match_controller = MatchController(db)
matches_blueprint = Blueprint('matches', __name__)

@matches_blueprint.route("/matches", methods=["GET"])
def get_all_matches():
    return match_controller.get_all_matches()

@matches_blueprint.route("/matches/<match_id>", methods=["GET"])
def get_match_by_id(match_id):
    return match_controller.get_match_by_id(match_id)

@matches_blueprint.route("/matches/competition/<competition_id>", methods=["GET"])
def get_matches_by_competitionId(competition_id):
    return match_controller.get_matches_by_competitionId(competition_id)

@matches_blueprint.route("/matches/matchIds", methods=["POST"])
def get_matches_by_matchId_array():
    match_ids = request.json.get("matchIds", [])
    return match_controller.get_matches_by_matchId_array(match_ids)

@matches_blueprint.route("/matches/create", methods=["POST"])
def create_match():
    data = request.json
    competition_id = data.get("competition_id")
    home_team = data.get("home_team")
    # Get other data fields similarly...
    # Ensure you have proper validations and error handling for missing fields

    return match_controller.create_match(
        competition_id, home_team, ...
    )  # Pass required arguments


# upload match data - endpoint
# TODO: INCREMENT A TOTAL POSSIBLE GAMES COUNTER FOR ALL PLAYERS ON TEAM WHO WERE NOT MATCH DAY SQUAD
@matches_blueprint.route('/api/v2/upload-match-data', methods=['POST'])
def upload_match_data_v2():
    try:
        # load in match data from html request
        data = json.loads(request.data)

        # get relevant match and team id's and perform type checking/casting for safety
        match_id = data['Competition']['MatchID']
        home_id = data['HomeTeam']['teamID']
        away_id = data['AwayTeam']['teamID']
        # match_id = match_id if type(match_id) is ObjectId else ObjectId(match_id)
        match_id = return_oid(match_id)
        # home_id = home_id if type(home_id) is ObjectId else ObjectId(home_id)
        home_id = return_oid(home_id)
        # away_id = away_id if type(away_id) is ObjectId else ObjectId(away_id)
        away_id = return_oid(away_id)

        # add match id to team's list of played matches
        db.teams.update_many({'_id': {'$in': [home_id, away_id]}}, {'$addToSet': {'matches': match_id}})
        # db.teams.update_one({'_id': home_id}, {'$addToSet': {'matches': match_id}})
        # db.teams.update_one({'_id': away_id}, {'$addToSet': {'matches': match_id}})

        # update the stats for each player on the home and away teams
        home_stats = update_player_stats(data['HomeTeam']['Players'], match_id)
        away_stats = update_player_stats(data['AwayTeam']['Players'], match_id)

        # add each team's individual player's match stats to the match document in the db
        db.matches.update_one({'_id': match_id},
                              {
                                  '$set': {
                                      'data_entered': True,
                                      'home_stats': home_stats,
                                      'away_stats': away_stats
                                  }
                              })

        return SUCCESS_200

    except Exception as e:
        traceback.print_exception(type(e), e, e.__traceback__)
        return edit_html_desc(ERROR_400, str(e))