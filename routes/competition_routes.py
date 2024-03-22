
from flask import Blueprint
from controllers.competition_controller import CompetitionController



competition_controller = CompetitionController()
competitions_blueprint = Blueprint('competitions', __name__)

@competitions_blueprint.route('/get-by-id/<competition_id>', methods=['GET'])
def get_competition_by_id(competition_id):
    return competition_controller.get_competition_by_id(competition_id=competition_id)