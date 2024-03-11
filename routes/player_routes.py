#players_routes.py

from flask import Blueprint, jsonify, request
from controllers.player_controller import PlayerController
from app import get_database_connection
import json
from functions import *

player_controller = PlayerController()
players_blueprint = Blueprint('players', __name__)

@players_blueprint.route('/players/get-players', methods=['GET'])
def get_players_specific():
    collection_ids_str = request.args.get('ids')
    collection_ids = [ObjectId(id.strip()) for id in collection_ids_str.split(',')]
    return player_controller.getPlayerSpecific(collection_ids)