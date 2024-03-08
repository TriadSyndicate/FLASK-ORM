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


def update_player_stats(team, match_id):
    # get match id and ensure it's the correct type, and set up the stats list to return at the end
    # match_id = match_id if type(match_id) is ObjectId else ObjectId(match_id)
    stats_list = []
    # squad: starters vs. subbed
    for squad in team:
        # each player that was in the starters or subbed list
        for player in team[squad]:

            # get player id and find that player in the db, if they have this match recorded somehow then skip
            player_id = ObjectId(player['PlayerID'])
            db_player = db.players.find_one({'_id': player_id})
            if db_player:
                if match_id in db_player['matches']:
                    continue

                # create player_stats to increment career stats and match_stats to record just this match's stats
                career_stats = db_player['stats']
                match_stats = MatchStats(match_id=match_id, player_id=player_id)

                # increment number of match day squads and set min_played to 0
                career_stats['match_day_squad'] += 1
                min_played = 0

                # if the player is a starter, increment their starter count and calculate minutes played
                # min_played is 90 if they started and never came out, else equal to the minute they subbed out
                # increment starter minutes by min_played and flip the single match stat starter parameter to true
                if player['starter'] == 'YES':
                    career_stats['starter'] += 1
                    min_played = 90 if player['SubOut'] == 'NO' else int(player['SubMinute'])
                    career_stats['starter_minutes'] += min_played
                    match_stats['starter'] = True

                # if the player was a sub, their min_played are equal to 0 unless they subbed in
                # if subbed in, min_played is equal to 90 - their sub in time
                # increment their sub minutes by min_played
                elif player['substitute'] == 'YES':
                    min_played = 90 - int(player['SubMinute']) if player['SubIn'] == 'YES' else 0
                    career_stats['sub_minutes'] += min_played

                # increment career stats by min_played and set match_stats to min_played
                career_stats['min_played'] += min_played
                match_stats['min_played'] = min_played

                # if the player scored a goal, split goal minutes list by ',' and loop for how many they scored
                # creating a new goal object each time and appending them to both career and match stats goals lists
                if player['Goal']:
                    goal_mins = player['GoalMinute'].split(',')
                    for i in range(0, int(player['Goal'])):
                        goal = Goal(minute=int(goal_mins[i]), match_id=match_id)
                        career_stats['goals'].append(goal.to_mongo())
                        match_stats['goals'].append(goal.to_mongo())

                # update the player's career stats
                db.players.update_one({'_id': player_id},
                                      {
                                          '$set': {'stats': career_stats},
                                          '$addToSet': {'matches': match_id}
                                      })

                # append the player's match stats to the list of all player's match stats
                stats_list.append(match_stats.to_mongo())

    # return this team's individual player's match stats in a list to be uploaded to the match document
    return stats_list

# upload match data - endpoint
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