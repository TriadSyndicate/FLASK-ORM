# app.py
from flask import Flask, jsonify, request
from pymongo import MongoClient
from controllers.match_controller import MatchController
import urllib
from dotenv import load_dotenv
from mongoengine import connect
import os

load_dotenv()  # Load environment variables from .env file
app = Flask(__name__)

def get_database_connection():
    db_username = urllib.parse.quote_plus(os.getenv("DB_USERNAME"))
    db_password = urllib.parse.quote_plus(os.getenv("DB_PASSWORD"))
    db_uri = os.getenv("DB_URI") % (db_username, db_password)
    db = connect(alias='default', host=db_uri)
    connect(alias='default', host=db_uri)
    return db
# Get the database connection
get_database_connection()

# Initialize the MatchController
match_controller = MatchController()

# Brief landing page if someone somehow ends up on the API's home page
@app.route('/')
def index():
    return '<h1>Lighthouse Sports API</h1>' \
           '<p>Please contact administrator for access</p>'

if __name__ == "__main__":
    from routes.matches_routes import matches_blueprint
    from routes.player_routes import players_blueprint
    from routes.teams_routes import teams_blueprint
    from routes.get_collection_routes import get_collection_blueprint
    # Register the match routes blueprint
    app.register_blueprint(matches_blueprint, url_prefix='/api/matches')
    app.register_blueprint(players_blueprint, url_prefix='/api/players')
    app.register_blueprint(teams_blueprint, url_prefix="/api/teams")
    app.register_blueprint(get_collection_blueprint, url_prefix='/api/get-collection')
    app.run(debug=True)
