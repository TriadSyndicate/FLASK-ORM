# get_collection_routes.py
from flask import Blueprint, jsonify, request
from controllers.match_controller import MatchController
from controllers.player_controller import PlayerController
from controllers.team_controller import TeamController
from controllers.competition_controller import CompetitionController
from controllers.fixture_controller import FixtureController
from controllers.body_controller import BodyController
from app import get_database_connection
import json
from functions import *

# Initialize the MatchController and the blueprint
db = get_database_connection()
match_controller = MatchController()
player_controller = PlayerController()
team_controller = TeamController()
competition_controller = CompetitionController()
fixture_controller = FixtureController()
body_controller = BodyController()

get_collection_blueprint = Blueprint('get-collection', __name__)

# get all matches
@get_collection_blueprint.route("/matches", methods=["GET"])
def get_all_matches():
    return match_controller.get_all_matches()
# get all players
@get_collection_blueprint.route("/players", methods=["GET"])
def get_all_players():
    return player_controller.get_all_players()
# get all teams
@get_collection_blueprint.route("/teams", methods=["GET"])
def get_all_teams():
    return team_controller.get_all_teams()

# get all competitions
@get_collection_blueprint.route("/competitions", methods=["GET"])
def get_all_competitions():
    return competition_controller.get_all_competitions()

# get all fixtures
@get_collection_blueprint.route("/fixtures", methods=["GET"])
def get_all_fixtures():
    return fixture_controller.get_all_fixtures()

# get all bodies
@get_collection_blueprint.route("/bodies", methods=["GET"])
def get_all_bodies():
    return body_controller.get_all_bodies()
