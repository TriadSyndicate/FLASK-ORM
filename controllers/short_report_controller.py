#short_report_controller.py
from flask import jsonify, request
from functions import return_oid, convert_object_ids_to_string
from models.short_report import attribute_list, short_report, shortReport

class ShortReportController:
    def __init__(self):
        from models.short_report import short_report
        from controllers.player_controller import PlayerController
        from controllers.match_controller import MatchController
        self.PC = PlayerController()
        self.MC = MatchController()
        # creating shortreport POST method
    def upload_short_report(self):
        try:
                        # get JSON data from the request
            data = request.get_json()

            # Extract player_id and match_id from the request
            player_id = return_oid(data['player_id'])
            match_id = return_oid(data['match_id'])
            player_team_id = return_oid(data['player_team_id'])

            # Fetch player and match details
            player = self.PC.fetch_player_details(player_id)
            player_details = {
                'player_name': player['name'],
                'date_of_birth': player['dob'],
                'shirt_number': player['jersey_num'],
            }

            match = self.MC.fetch_match_details(match_id)

            # Determine the opposition club based on the home and away teams
            opposition_club = match['away_team'] if match['home_team'] == player_team_id else \
                match['home_team']
            # Calculate total minutes played in the match
            mins_played = 0  # initialize to 0
            for stats in (match['away_stats'] + match['home_stats']):
                if stats['player_id'] == player_team_id:
                    mins_played = stats['min_played']

            game_date = match['date']

            match_details = {
                'opposition_club': opposition_club,
                'mins_played': mins_played,
                'game_date': game_date,
            }
            # Return the extracted details

            if 'error' in player_details:
                return jsonify({'error': player_details['error']}), 404
            if 'error' in match_details:
                return jsonify({'error': match_details['error']}), 404

            # Combine all details with received scouting report data
            strengths_data = {key: value for key, value in data.items() if key.startswith('strength')}
            weaknesses_data = {key: value for key, value in data.items() if key.startswith('weakness')}

            strengths = [attribute_list(attribute=value) for value in strengths_data.values()]
            weaknesses = [attribute_list(attribute=value) for value in weaknesses_data.values()]

            saving_short_report = short_report.create_short_report(
                player_id=data['player_id'],
                match_id=data['match_id'],
                formation=data['formation'],
                position_played=data['positionPlayed'],
                report_date=data['reportDate'],
                scout_name=data['scoutName'],
                player_profile=data['playerProfile'],
                match_view=data['matchView'],
                game_context=data['gameContext'],
                position=data['position'],
                physical_profile=data['physicalProfile'],
                summary=data['gameSummary'],
                conclusion=data['playerConclusion'],
                grade=data['grade'],
                action=data['nextAction'],
                time_ready=data['readyTimes'],
                strengths=strengths,
                weaknesses=weaknesses
            )
            
            return jsonify({"Short Report": convert_object_ids_to_string(saving_short_report)}), 200
    
        except Exception as e:
            return jsonify({"error": str(e)}), 500