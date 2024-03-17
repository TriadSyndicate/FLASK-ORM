import threading
from flask import jsonify, request
from controllers.player_controller import PlayerController
from functions import convert_object_ids_to_string, return_oid
from models.goal import Goal
from models.match import Match, MatchStats  # Assuming Match class is defined in models.match
from mongoengine import DoesNotExist
from bson.json_util import dumps
from models.player import Player, Stats
from models.team import Team
from functions import return_oid
class MatchController:
    def __init__(self):
        self.match = Match()
        self.player = Player()
        self.PC = PlayerController()
    def create_match(
        self,
        competition_id,
        home_team,
        away_team,
        date,
        venue,
        home_stats,
        away_stats,
        data_entered,
        match_events,
    ):
        try:
            match_data = {
                "competition_id": competition_id,
                "home_team": home_team,
                "away_team": away_team,
                "date": date,
                "venue": venue,
                "home_stats": home_stats,
                "away_stats": away_stats,
                "data_entered": data_entered,
                "match_events": match_events,
            }
            result = self.match.create_match(match_data)
            return (
                jsonify(
                    {"message": "Match created successfully", "match_id": str(result)}
                ),
                201,
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_all_matches(self):
        try:
            # Use keyword arguments when instantiating Match
            matches = self.match.get_all_matches()
            serialized_matches = [
                self.match.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_match_by_id(self, match_id):
        try:
            # Use keyword arguments when instantiating Match
            match_obj = self.match.get_match_by_id(match_id)
            serialized_match = self.match.convert_object_ids_to_string(match_obj)
            if match_obj:
                return jsonify(serialized_match), 200
            return jsonify({"message": "Match not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_matches_by_competitionId(self, competitionId):
        try:
            # Use keyword arguments when instantiating Match
            matches = self.match.get_matches_by_competitionId(competitionId)
            serialized_matches = [
                self.match.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def get_matches_by_matchId_array(self, matchIds):
        try:
            # Use keyword arguments when instantiating Match
            matches = self.match.get_matches_by_matchId_array(matchIds)
            serialized_matches = [
                self.match.convert_object_ids_to_string(match)
                for match in matches
            ]
            return jsonify({"matches": serialized_matches}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    def match_data_upload(self, data):
        try:
            home_data = data['HomeTeam']
            away_data = data['AwayTeam']
            comp_data = data['Competition']

            home_id = return_oid(home_data['teamID'])
            away_id = return_oid(away_data['teamID'])

            match_id = return_oid(comp_data['MatchID'])
            self.PC.increment_team_matches(home_id, match_id)
            self.PC.increment_team_matches(away_id, match_id)

            home_players = home_data['Starters'] + home_data['Subs']
            away_players = away_data['Starters'] + away_data['Subs']

            home_match_stats, home_career_stats, home_events = self.PC.parse_player_stats(
                team_data=home_players, away_data=away_players, match_id=match_id)
            away_match_stats, away_career_stats, away_events = self.PC.parse_player_stats(
                team_data=away_players, away_data=home_players, match_id=match_id)
            print(
                f'RETURNED DATA\nhome_match_stats: {home_match_stats}\nhome_career_stats: {home_career_stats}\nhome_events: {home_events}\n')
            print(
                f'RETURNED DATA\naway_match_stats: {away_match_stats}\naway_career_stats: {away_career_stats}\naway_events: {away_events}\n')
            match_events = sorted(home_events + away_events, key=lambda x: int(x['minute']))

            for player in home_career_stats + away_career_stats:
                player.update(
                    set__stats=player['stats'],
                    set__performance=player['performance'],
                    add_to_set__matches=match_id
                )
            # Assuming `Team` is your MongoEngine model
            Team.objects(id__in=[home_id, away_id]).update(add_to_set__matches=match_id)
            # Update the document
            result = Match.objects(id=match_id).update(set__home_stats = home_match_stats, 
                                                       set__away_stats= away_match_stats, 
                                                       set__match_events = match_events, 
                                                       set__data_entered=True)
            if result > 0:
                # Document was updated
                updated_match_document = Match.objects.get(id=match_id)
                return jsonify({"match": Match.convert_object_ids_to_string(updated_match_document.to_mongo())}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    # Fetch match by id and return document
    def fetch_match_details(self, match_id):
        try:
            # Try to find a match with the given ID
            match = Match.objects.get(id=match_id)
            return match
        except DoesNotExist:
            # If match not found, return an error message
            return {'error': 'Match not found'}

    def edit_match(self, data):        
        home_data = data['HomeTeam']
        away_data = data['AwayTeam']
        comp_data = data['Competition']

        match_id = return_oid(comp_data['MatchID'])
        db_match = Match.objects(id=match_id)

        home_players = home_data['Starters'] + home_data['Subs']
        away_players = away_data['Starters'] + away_data['Subs']

        home_match_stats, home_career_stats, home_events = self.PC.parse_player_stats(
            team_data=home_players, away_data=away_players, match_id=match_id)
        away_match_stats, away_career_stats, away_events = self.PC.parse_player_stats(
            team_data=away_players, away_data=home_players, match_id=match_id)
        match_events = sorted(home_events + away_events, key=lambda x: int(x['minute']))
        Match.objects(id=match_id).update(set__home_stats = home_match_stats, 
                                                            set__away_stats= away_match_stats, 
                                                            set__match_events = match_events, 
                                                            set__data_entered=True)

        def update_match_data_thread():
            self.update_match_data(db_match, home_match_stats, match_events, away_match_stats)

        # Start a new thread to run update_match_data
        threading.Thread(target=update_match_data_thread).start()

        updated_match_document = Match.objects.get(id=match_id)
        return jsonify({"match": Match.convert_object_ids_to_string(updated_match_document.to_mongo())}), 200


    def update_match_data(db_match, home_match_stats, match_events, away_match_stats):
        db_match_stats_players = {stat['player_id'] for stat in db_match['home_stats'] + db_match['away_stats']}
        match_stats_players = {stat['player_id'] for stat in home_match_stats}

        players_only_in_db = db_match_stats_players - match_stats_players
        players_only_in_match = match_stats_players - db_match_stats_players
        unique_players = players_only_in_db.union(players_only_in_match)

        for players_id in unique_players:
            performance = get_stats(return_oid(players_id))
            stats = get_player_stats(return_oid(players_id))
            db.players.update_one(
                {'_id': return_oid(return_oid(players_id))},
                {
                    '$set': {
                        'stats': stats.to_mongo(),
                        'performance': performance,
                    },
                }
            )

        for match_stats in home_match_stats:
            val = False
            for db_match_stats in db_match['home_stats'] + db_match['away_stats']:
                if match_stats['player_id'] == db_match_stats['player_id']:
                    val = True

                    if get_player_performance_match(match_events, match_stats,
                                                    home_match_stats) != get_player_performance_match(
                        db_match['match_events'], db_match_stats, home_match_stats):
                        performance = get_stats(match_stats['player_id'])
                        stats = get_player_stats(match_stats['player_id'])
                        db.players.update_one(
                            {'_id': return_oid(match_stats['player_id'])},
                            {
                                '$set': {
                                    'stats': stats.to_mongo(),
                                    'performance': performance,
                                },
                            }
                        )
                    else:
                        print('no changes',
                            get_player_performance_match(match_events, match_stats, home_match_stats).to_dict())

        for match_stats in away_match_stats:
            for db_match_stats in db_match['home_stats'] + db_match['away_stats']:
                if match_stats['player_id'] == db_match_stats['player_id']:

                    if get_player_performance_match(match_events, match_stats,
                                                    away_match_stats) != get_player_performance_match(
                        db_match['match_events'], db_match_stats, away_match_stats):
                        print(match_stats['player_id'],
                            get_player_performance_match(match_events, match_stats, away_match_stats).to_dict())
                    else:
                        print('nosisi', get_player_performance_match(match_events, match_stats, away_match_stats).to_dict())


    def get_player_performance_match(match_events, match_stats, all_stats):
        detailed_stats = PlayerPerformance()
        start_min = 0
        end_min = 0
        if match_stats['starter'] is True:
            detailed_stats = check_and_fill(detailed_stats, 'appearances', 1)
            detailed_stats = check_and_fill(detailed_stats, 'starts', 1)
            end_min = 90
        for event in match_events:

            if 'assist' in event:
                # print('event', event)
                event['playerId'] = event['assisterId']
            if return_oid(match_stats['player_id']) == return_oid(event['playerId']):
                print('event', event)

                if 'PlayerSubbedOut' in event:
                    end_min = int(event['minute'])
                if 'PlayerSubbedIn' in event:
                    detailed_stats = check_and_fill(detailed_stats, 'appearances', 1)
                    start_min = int(event['minute'])
                    end_min = 90
                if 'goal' in event:
                    detailed_stats = check_and_fill(detailed_stats, 'goals', 1)
                if 'assist' in event:
                    detailed_stats = check_and_fill(detailed_stats, 'assists', 1)
        mins = end_min - start_min
        detailed_stats = check_and_fill(detailed_stats, 'mins', mins)

        detailed_stats = PC.get_player_performance_for_match(match_events, start_min, end_min, detailed_stats, all_stats)

        return detailed_stats