#players_routes.py

from flask import Blueprint, jsonify, request
from controllers.player_controller import PlayerController
from app import get_database_connection
import json
from functions import *

player_controller = PlayerController()
players_blueprint = Blueprint('players', __name__)

@players_blueprint.route('/get-all', methods=['GET'])
def get_players_specific():
    collection_ids_str = request.args.get('ids')
    collection_ids = [ObjectId(id.strip()) for id in collection_ids_str.split(',')]
    return player_controller.getPlayerSpecific(collection_ids)

# insert / create player / move player
# Insert Player Endpoint
@players_blueprint.route('/insert', methods=['POST'])
def insert_player():
    player_data = json.loads(request.data)
    return player_controller.insert_player(player_data)

# Move Player
@players_blueprint.route('/move', methods=['POST'])
def move_player():
    data = json.loads(request.data)
    return player_controller.move_player(data)

# Get specific player by Id
@players_blueprint.route('/get-by-id/<player_id>')
def get_player_by_id(player_id):
    return player_controller.get_player_by_id(player_id=player_id)
    