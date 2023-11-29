from flask import Flask, jsonify, request
from pymongo import MongoClient
from controllers.match_controller import MatchController
import urllib
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
app = Flask(__name__)


def get_database_connection():
    db_username = urllib.parse.quote_plus(os.getenv("DB_USERNAME"))
    db_password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    db_uri = os.getenv("DB_URI") % (db_username, db_password)
    client = MongoClient(db_uri)
    return client["ea_eye"]  # Return the desired database name


# Get the database connection
db = get_database_connection()

# Initialize the MatchController
match_controller = MatchController(db)


# Routes for match-related endpoints
@app.route("/matches", methods=["GET"])
def get_all_matches():
    return match_controller.get_all_matches()


@app.route("/matches/<match_id>", methods=["GET"])
def get_match_by_id(match_id):
    return match_controller.get_match_by_id(match_id)


@app.route("/matches/competition/<competition_id>", methods=["GET"])
def get_matches_by_competitionId(competition_id):
    return match_controller.get_matches_by_competitionId(competition_id)


@app.route("/matches/matchIds", methods=["POST"])
def get_matches_by_matchId_array():
    match_ids = request.json.get("matchIds", [])
    return match_controller.get_matches_by_matchId_array(match_ids)


@app.route("/matches/create", methods=["POST"])
def create_match():
    data = request.json
    competition_id = data.get("competition_id")
    home_team = data.get("home_team")
    # Get other data fields similarly...
    # Ensure you have proper validations and error handling for missing fields

    return match_controller.create_match(
        competition_id, home_team, ...
    )  # Pass required arguments


if __name__ == "__main__":
    app.run(debug=True)
