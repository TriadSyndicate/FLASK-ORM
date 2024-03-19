from datetime import datetime
import time
from bson import ObjectId
from flask import jsonify, request
import pytz
from functions import convert_object_ids_to_string, print_and_return_error, return_oid

from mongoengine import DoesNotExist

from models.player import Player, PlayerPerformance, PlayerTeam, Stats
from models.goal import Goal
from models.match import MatchStats, Match
from models.team import Team
from functions import return_oid
from dateutil import parser
from mongoengine.queryset.visitor import Q

class PlayerController:
    def __init__(self):
        from models.match import Match, MatchStats 
        self.match = Match()
        self.player = Player()
        
        
    # get all players method
    def get_all_players(self):
        try:
            players = self.player.get_all_players()
            print('players_all', players)
            serialized_players = [convert_object_ids_to_string(player)
                                  for player in players
                                ]
            return jsonify({"players": serialized_players}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    def check_if_add(self, player, match, team_id):
        utc = pytz.UTC
        date_string = match['date']
        # Check if the date string contains additional information in parentheses
        if "(" in date_string and ")" in date_string:
            # Extract the date without the additional information
            date_string_without_info = date_string.split("(")[0].strip()
        else:
            date_string_without_info = date_string
        # Parse the date string with or without the additional information
        input_date_obj = datetime.strptime(date_string_without_info, "%a %b %d %Y %H:%M:%S GMT%z")
        # Format the datetime object as dd/mm/yyyy
        input_date_obj = input_date_obj.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=utc)
        player_teams = sorted(player['teams'], key=lambda x: x['reg_date'])
        print(player['_id'])
        print('sorted teams', player_teams)

        for i in range(len(player_teams)):
            t = player_teams[i]
            if t['team_id'] == return_oid(team_id):
                start_date = parser.parse(t['reg_date'])
                start_date = pytz.utc.localize(start_date)
                print('on_team', t['on_team'], t['team_id'])
                if t['on_team'] is False:
                    # Get the next team's registration date as the end_date
                    try:
                        end_date = parser.parse(player['teams'][i + 1]['reg_date'])
                        end_date = utc.localize(end_date)
                    except:
                        return False
                else:
                    # If no next team, set end_date to None or any other placeholder
                    end_date = None
                if end_date is not None:
                    if start_date <= input_date_obj <= end_date:
                        if return_oid(t['team_id']) == return_oid(team_id):
                            return True
                elif start_date <= input_date_obj:
                    if return_oid(t['team_id']) == return_oid(team_id):
                        return True
        return False
    
    
    def increment_team_matches(self, team_id, match_id):
        # Fetch match information
        try:
            match_info = self.match.get_match_by_id(match_id=match_id)
        except DoesNotExist:
            # Handle the case where the match does not exist
            return
        # Fetch team roster and matches
        team_info = Team.objects.get(id=team_id)
        # Fetch possible players for the team
        possible_players = Player.objects.filter(teams__team_id=team_id)
        # Iterate through team matches
        for team_match in team_info.matches:
            if team_match == match_id:
                return  # Match already processed, no need to increment again

        count = 0

        # Iterate through possible players
        for player in possible_players:
            # Check if the player should be added based on some criteria (check_if_add function)
            should_add = self.check_if_add(player, match_info, team_id)

            if should_add:
                count += 1
                # Update possible_matches field
                player.update(add_to_set__possible_matches=match_id)
                
                # Ensure player_performance is a dictionary before attempting to use .get()
                player_performance = player.performance or {}

                # Update team_matches count in the performance field
                player_performance['team_matches'] = player_performance.get('team_matches', 0) + 1

                # Save the changes back to the database
                player.update(set__performance=player_performance)
        
    def check_and_fill(cls,stats, attrb, add):
        if attrb in stats:
            stats[attrb] += add
        else:
            stats[attrb] = add
        return stats
    
    def match_data_upload_detailed_stats(self, player, detailed_stats, match_data, start_mins, end_mins):
        # MATCH DATA IS ENEMY DATA
        print('detailed stats')
        print(detailed_stats)
        clean_sheet = True
        for player in match_data:
            if player['Goal']:
                for goal in player['goalEvent']:
                    if start_mins < goal['minute'] < end_mins:
                        clean_sheet = False
                        print('checkAndFill detailedStats', detailed_stats)
                        detailed_stats = self.check_and_fill(detailed_stats, 'conceded', 1)
        if clean_sheet:
            detailed_stats = self.check_and_fill(detailed_stats, 'clean_sheets', 1)
        # Calculate 'mins_90s'
        if 'mins' in detailed_stats:
            detailed_stats['mins_90s'] = detailed_stats['mins'] / 90
        else:
            print("Error: 'mins' not present in detailed_stats.")
            detailed_stats['mins_90s'] = 0

        # Calculate 'percent_matches'
        if 'appearances' in detailed_stats and 'team_matches' in detailed_stats:
            detailed_stats['percent_matches'] = ((detailed_stats['appearances'] / detailed_stats['team_matches']) * 100) if \
                detailed_stats['team_matches'] > 0 else 0
        else:
            print("Error: 'appearances' or 'team_matches' not present in detailed_stats.")
            detailed_stats['percent_matches'] = 0

        # Calculate 'percent_potential_mins'
        if 'mins' in detailed_stats and 'appearances' in detailed_stats:
            detailed_stats['percent_potential_mins'] = (
                    detailed_stats['mins'] / (90 * detailed_stats['appearances']) * 100) if detailed_stats[
                                                                                                'appearances'] > 0 else 0
        else:
            print("Error: 'mins' or 'appearances' not present in detailed_stats.")
            detailed_stats['percent_potential_mins'] = 0

        # Calculate 'goals_per_90'
        if 'goals' in detailed_stats and 'mins_90s' in detailed_stats:
            detailed_stats['goals_per_90'] = (detailed_stats['goals'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                                        'mins_90s'] > 0 else 0
        else:
            print("Error: 'goals' or 'mins_90s' not present in detailed_stats.")
            detailed_stats['goals_per_90'] = 0

        # Calculate 'mins_per_goal'
        if 'mins' in detailed_stats and 'goals' in detailed_stats and detailed_stats['goals'] > 0:
            detailed_stats['mins_per_goal'] = detailed_stats['mins'] / detailed_stats['goals']
        else:
            print("Error: 'mins' or 'goals' not present in detailed_stats.")
            detailed_stats['mins_per_goal'] = 0

        # Calculate 'assists_per_90'
        if 'assists' in detailed_stats and 'mins_90s' in detailed_stats:
            detailed_stats['assists_per_90'] = (detailed_stats['assists'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                                            'mins_90s'] > 0 else 0
        else:
            print("Error: 'assists' or 'mins_90s' not present in detailed_stats.")
            detailed_stats['assists_per_90'] = 0

        # Calculate 'goal_contributions'
        if 'assists' in detailed_stats and 'goals' in detailed_stats:
            detailed_stats['goal_contributions'] = detailed_stats['assists'] + detailed_stats['goals']
        else:
            print("Error: 'assists' or 'goals' not present in detailed_stats.")
            detailed_stats['goal_contributions'] = 0

        # Calculate 'goal_contributions_per_90'
        if 'goal_contributions' in detailed_stats and 'mins_90s' in detailed_stats:
            detailed_stats['goal_contributions_per_90'] = (
                    detailed_stats['goal_contributions'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                                'mins_90s'] > 0 else 0
        else:
            print("Error: 'goal_contributions' or 'mins_90s' not present in detailed_stats.")
            detailed_stats['goal_contributions_per_90'] = 0

        # Calculate 'conceded_per_90'
        if 'conceded' in detailed_stats and 'mins_90s' in detailed_stats:
            detailed_stats['conceded_per_90'] = (detailed_stats['conceded'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                                                'mins_90s'] > 0 else 0
        else:
            print("Error: 'conceded' or 'mins_90s' not present in detailed_stats.")
            detailed_stats['conceded_per_90'] = 0


        # TODO:
        # team_matches ---- DONE IN increment_team_matches
        # mins_90s
        # percent_matches(need team_matches to be incremented first)
        # percent_potential_mins
        # goals_per_90
        # mins_per_goal
        # assists_per_90
        # goal_contributions(goals+assists)
        # goal_contributions_per_90
        # conceded_per_90
        return detailed_stats
    
    def parse_player_stats(self, team_data, away_data, match_id):
        print('BEGINNING MATCH DATA PARSE')
        #print(f'CURRENT TEAM DATA: \n{team_data}\nMATCH ID: {match_id}\n\n')
        # new_career_stats for player documents stats update
        # team_stats for match document stats update
        # match_events for holding all events contained in match data
        new_career_stats = []
        team_stats = []
        match_events = []

        # loop over every player in the given team
        for player in team_data:
            print(player)
            try:
                print("playerid", player['PlayerID'])
                player_id = return_oid(player['PlayerID'])
            except:
                print("playerid", player['player_id'])
                player_id = return_oid(player['player_id'])
            db_player = Player.objects(id=player_id).first()
            career_stats = db_player['stats']
            if 'performance' in db_player:
                if isinstance(db_player['performance'], dict):
                    detailed_stats = db_player['performance']
                elif isinstance(db_player['performance'], list):
                    detailed_stats = PlayerPerformance()
                else:
                    # Handle other cases or raise an exception if needed
                    detailed_stats = PlayerPerformance()
            else:
                detailed_stats = PlayerPerformance()
            match_stats = MatchStats(match_id=match_id, player_id=player_id)

            career_stats = self.check_and_fill(career_stats, 'match_day_squad', 1)
            min_played = 0

            # min_played formulae
            # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # sub in: min_played += 90 - minute_subbed_in
            # sub out (if min_played == 0): min_played = minute_subbed_out
            # sub out (if min_played > 0): min_played = abs(minute_subbed_out - (90 - min_played))

            # check for key existence then query its value
            # prevents KeyErrors as the logic is evaluated left to right, and exits if the first key check fails
            # if the check passes loop through all subEvents for that player, total minutes played, and append to event list
            start_mins = 0
            end_mins = 90
            flag = False
            if ('SubOut' in player.keys() and player['SubOut'] == 'YES') \
                    or ('SubIn' in player.keys() and player['SubIn'] == 'YES'):
                # print(player['Name'],player['SubOut'],player['SubIn'])
                for event in player['subEvent']:
                    if 'PlayerSubbedOut' in event.keys():
                        if event['minute'] == 0:
                            print('player subbed min0', player['Name'])
                            flag = True
                        end_mins = event['minute']
                        min_played = abs(event['minute'] - (90 - min_played)) if min_played else event['minute']
                    elif 'PlayerSubbedIn' in event.keys():
                        start_mins = abs(event['minute'])
                        detailed_stats = self.check_and_fill(detailed_stats, 'appearances', 1)
                        min_played += 90 - event['minute']
                    match_events.append(event)

            # increment starter specific stats
            if player['starter'] == 'YES':
                min_played = 90 if not min_played else min_played
                print('flag for', player['Name'], flag)
                if flag:
                    min_played = 0
                # min_played is equal to a full match if no minutes have been calculated, else use the value generated above
                career_stats = self.check_and_fill(career_stats, 'starter', 1)
                career_stats = self.check_and_fill(career_stats, 'starter_minutes', min_played)
                detailed_stats = self.check_and_fill(detailed_stats, 'appearances', 1)
                detailed_stats = self.check_and_fill(detailed_stats, 'starts', 1)
                match_stats['starter'] = True

            detailed_stats = self.check_and_fill(detailed_stats, 'mins', min_played)

            career_stats = self.check_and_fill(career_stats, 'min_played', min_played)

            match_stats['min_played'] += min_played

            # check for all possible event indicators and parse events if they exist, adding them to the event list
            if player['Goal']:
                for goal in player['goalEvent']:
                    detailed_stats = self.check_and_fill(detailed_stats, 'goals', 1)
                    new_goal = Goal(minute=int(goal['minute']), match_id=match_id)
                    career_stats['goals'].append(new_goal)
                    match_stats['goals'].append(new_goal)
                    match_events.append(goal)

            if player['Assist']:
                detailed_stats = self.check_and_fill(detailed_stats, 'assists', 1)
                career_stats = self.check_and_fill(career_stats, 'assists', player['Assist'])
                # career_stats['assists'] += player['Assist']
                match_stats['assists'] += player['Assist']
                for assist in player['assistEvent']:
                    match_events.append(assist)

            if 'OwnGoal' in player.keys() and player['OwnGoal']:
                if 'own_goals' in career_stats:
                    career_stats['own_goals'] += 1
                    match_stats['own_goals'] += 1
                    for own_goal in player['ownGoalEvent']:
                        match_events.append(own_goal)
                else:
                    career_stats['own_goals'] = 1

            if 'YellowCard' in player.keys():
                if len(player['yellowCardEvent']) > 1:
                    career_stats = self.check_and_fill(career_stats, 'red_cards', 1)
                    # career_stats['red_cards'] += 1
                    match_stats['red_cards'] += 1
                else:
                    career_stats = self.check_and_fill(career_stats, 'yellow_cards', 1)
                    # career_stats['yellow_cards'] += 1
                    match_stats['yellow_cards'] += 1
                for yellow_card in player['yellowCardEvent']:
                    match_events.append(yellow_card)

            if 'RedCard' in player.keys():
                career_stats = self.check_and_fill(career_stats, 'red_cards', 1)
                # career_stats['red_cards'] += 1
                match_stats['red_cards'] += 1
                match_events.append(player['redCardEvent'])

            # if the player has not had this match recorded add the updated db entry to a list for upload after full parse
            if match_id not in db_player['matches']:
                db_player['stats'] = career_stats

                db_player['performance'] = performance = self.match_data_upload_detailed_stats(player=db_player,
                                                                                            detailed_stats=detailed_stats,
                                                                                            match_data=away_data,
                                                                                            start_mins=start_mins,
                                                                                            end_mins=end_mins)

                if isinstance(db_player['performance'], PlayerPerformance):
                    db_player['performance'] = db_player['performance'].to_dict()
                print('career', career_stats)
                new_career_stats.append(db_player)

            team_stats.append(match_stats)

        return team_stats, new_career_stats, match_events,
    def get_regex_from_year(cls, year):
        str_year = str(year)
        regex = f".+20[{str_year[-2]}-9][{str_year[-1]}-9]|20[{int(str_year[-2]) + 1}-9][0-9]."
        return regex
    
    def convert_object_ids_to_string(cls, data):
        if isinstance(data, dict):
            return {key: cls.convert_object_ids_to_string(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [cls.convert_object_ids_to_string(item) for item in data]
        elif isinstance(data, ObjectId):
            return str(data)
        else:
            return data
    
    def getPlayerSpecific(self, collection_ids):
        try:
            current_year = datetime.now().year
            find_year = current_year - 21
            regex = self.get_regex_from_year(find_year)
            pipeline = [
                {
                    '$match': {
                        'comps': {
                            '$in':
                                collection_ids

                        }
                    }
                }, {
                    '$lookup': {
                        'from': 'players',
                        'localField': 'roster',
                        'foreignField': '_id',
                        'as': 'matched_players'
                    }
                }, {
                    '$lookup': {
                        'from': 'teams',
                        'localField': 'matched_players.teams.team_id',
                        'foreignField': '_id',
                        'as': 'team_names'
                    }
                }, {
                    '$unwind': '$team_names'
                }, {
                    '$unwind': '$matched_players'
                }, {
                    '$match': {
                        'matched_players.dob': {
                            '$regex': regex
                        }
                    }
                }, {
                    '$addFields': {
                        'name': '$matched_players.name',
                        'dob': '$matched_players.dob',
                        'nationality': '$matched_players.nationality',
                        'jersey_num': '$matched_players.jersey_num',
                        'id': '$matched_players._id',
                        'position': '$matched_players.position',
                        'matches': {
                            '$size': '$matched_players.matches'
                        },
                        'stats': '$matched_players.stats',
                        'yearCount': True
                    }
                }, {
                    '$group': {
                        '_id': '$id',
                        'name': {
                            '$first': '$name'
                        },
                        'dob': {
                            '$first': '$dob'
                        },
                        'nationality': {
                            '$first': '$nationality'
                        },
                        'jersey_num': {
                            '$first': '$jersey_num'
                        },
                        'matches': {
                            '$first': '$matches'
                        },
                        'position':{
                            '$first': '$position'
                        },
                        'id': {
                            '$first': '$matched_players._id'
                        },
                        'stats': {
                            '$first': '$stats'
                        },
                        'yearCount': {
                            '$first': '$yearCount'
                        },
                        'team_names': {
                            '$push': '$team_names.name'
                        }
                    }
                }, {
                    '$project': {
                        'name': 1,
                        'dob': 1,
                        'nationality': 1,
                        'jersey_num': 1,
                        'id': 1,
                        'matches': 1,
                        'stats': 1,
                        'yearCount': 1,
                        'team_names': 1,
                        'position':1,
                        '_id': 0
                    }
                }
            ]
            start_time = time.time()
            docs = Team.objects.aggregate(pipeline)
            result_list = [self.convert_object_ids_to_string(team) for team in docs]
            print(list(docs))
            # docs = sorted(players_cursor, key=lambda x: x['name'])
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Execution time for cursor: {execution_time} seconds")

            return jsonify({"players": result_list}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    # fetching player details
    def fetch_player_details(self, player_id):
        try:
            # Try to find player with the given ID
            player = Player.objects.get(id=player_id)
            # Return the extracted details
            return player

        except DoesNotExist:
            # If player not found, return an error message
            return {'error': 'Player not found'}
        
    # Method to get team_matches -- PC hamza
    def get_team_matches(self, player):
        dates = []
        utc = pytz.UTC
        team_matches_played = []
        for i in range(len(player['teams'])):
            # print(player['teams'][i + 1]['reg_date'])
            t = player['teams'][i]
            # Assuming t['team_id'] holds the team model you're searching for
            team_id = t['team_id'].id

            # Query matches where either away_team or home_team matches the team_id
            matches = Match.objects.filter(
                Q(away_team=team_id) | Q(home_team=team_id)
            )
            start_date = parser.parse(t['reg_date'])
            start_date = utc.localize(start_date)
            
            if t['on_team'] is False:
                # Get the next team's registration date as the end_date
                try:
                    end_date = parser.parse(player['teams'][i + 1]['reg_date'])
                    end_date = utc.localize(end_date)
                except:
                    end_date = None
            else:
                # If no next team, set end_date to None or any other placeholder
                end_date = None

            for m in matches:
                if m['date'] is not None:
                    if m['date'] != "":
                        date, _ = parser.parse(m['date'], fuzzy_with_tokens=True)

                        if date.tzinfo is None or date.tzinfo.utcoffset(date) is None:
                            # Date is naive, localize it
                            date = utc.localize(date)  # Make date offset-aware
                # date = utc.localize(date)
                if 'data_entered' in m:
                    if end_date is not None:
                        if end_date >= date >= start_date:
                            team_matches_played.append(m)
                    else:
                        if start_date <= date:
                            team_matches_played.append(m)
        # stats we need team_matches, md_squad, appearences, starts, mins , 90s, %matches played, %pot mins, goals,
        # gp90, mpg, assisits, ap90, goal controbutions, conceded, cp90, clean sheets
        return team_matches_played
    
    # Minutes played in a match, args - playerId, MatchId -- derives
    def mins_played_in_match(self, player_id, match_id):
        match_id = return_oid(match_id)
        player_id = return_oid(player_id)

        # Execute the query with filtering and projection
        result = Match.objects.only(
            'home_stats', 'away_stats', 'match_events'
        ).filter(
            id=match_id,
        ).first()
        print('560 result', result)
        # Convert the result to dictionary format if needed
        result = result.to_mongo().to_dict() if result else None
        stats = []
        mins_played = {}
        played = False

        # some matches are empty hence the need to enclose a try except in a try except for empty stuffs
        try:
            try:
                stats = (result['away_stats'])
            except KeyError:
                stats = (result['home_stats'])
        except KeyError:
            print('no stats for match')
        for s in stats:
            if s['min_played'] > 0:
                played = True
            if s['starter'] is True:
                played = True
                min_out = s['min_played']
                mins_played.update({'start': 0})
                mins_played.update({'end': min_out})
            else:
                if 'match_events' in result:
                    for events in result['match_events']:
                        if 'PlayerSubbedIn' in events:
                            played = True
                    min_in = 90 - (s['min_played'])
                    mins_played.update({'start': min_in})
                    mins_played.update({'end': 90})
        return mins_played, played, result

    def get_away_or_home(self, player_id, match_id):
        # Convert the match_id to ObjectId
        match_id = ObjectId(match_id)
        # Perform the query using the Match model
        result = Match.objects.filter(
            id=match_id,
            home_stats__player_id=player_id, away_stats__player_id=player_id
        ).first()
        return result
    
    # Goals conceded per match fn 
    def goals_conceded_per_match(self, matches, player_id):
        conceded = 0
        played = {}
        start_time = time.time()
        start_time = time.time()
        mins_played, did_he_play, result = self.mins_played_in_match(match_id=matches.id, player_id=player_id)
        if 'home_stats' in result:
            played.update({'enemy': 'away_stats'})
        else:
            played.update({'enemy': 'home_stats'})
        print('mpim', time.time() - start_time)
        if mins_played:
            start_min = mins_played['start']
            end_min = mins_played['end']
            for stats in matches[played['enemy']]:
                for g in stats['goals']:
                    min = abs(g['minute'])
                    if min > start_min:
                        conceded += 1
        return conceded, did_he_play

    def get_clean_conceded_appear(self, team_matches, player_id):
        clean_sheets = 0
        conceded_here = 0
        appearences = 0

        for match in team_matches:
            conceded, did_he_play = self.goals_conceded_per_match(match, player_id)
            conceded_here += conceded
            if conceded == 0:
                clean_sheets += 1
            if did_he_play:
                appearences += 1
        return clean_sheets, conceded_here, appearences
    
        
    def get_player_long_stats(self, player_id):
        # player_id = fc.return_oid('6520178d639acd1462890726')
        pp = PlayerPerformance()
        player = Player.objects.get(id=return_oid(player_id))

        start_time = time.time()
        players_teams_matches = self.get_team_matches(player)
        print("Time taken for get_team_matches:", time.time() - start_time)

        pp.team_matches = len(players_teams_matches)
        
        start_time = time.time()
        # Get player matches matchIds
        match_ids = [match_id.id for match_id in player['matches']]
        pp.clean_sheets, pp.conceded, pp.appearances = self.get_clean_conceded_appear(
            Match.objects.filter(id__in=match_ids),
            player.id)
        print("Time taken for cca:", time.time() - start_time)

        pp.starts = player['stats']['starter']

        pp.mins = player['stats']['min_played']
        pp.mins_90s = pp.mins / 90 if pp.mins > 0 else 0
        pp.percent_matches = (
                                     pp.appearances / pp.team_matches) * 100 if pp.team_matches > 0 else 0  # Ensure non-zero denominator
        pp.percent_potential_mins = (
                pp.mins / (90 * pp.appearances) * 100) if pp.appearances > 0 else 0  # Ensure non-zero denominator
        pp.goals = len(player['stats']['goals'])
        if pp.mins_90s > 0:
            pp.goals_per_90 = pp.goals / pp.mins_90s
        else:
            pp.goals_per_90 = 0

        if pp.goals > 0:
            pp.mins_per_goal = pp.mins / pp.goals
        else:
            pp.mins_per_goal = 0
        pp.assists = player['stats']['assists']
        pp.assists_per_90 = pp.assists / pp.mins_90s if pp.mins_90s > 0 else 0  # Ensure non-zero denominator
        pp.goal_contributions = pp.goals + pp.assists
        if pp.mins_90s > 0:
            pp.goal_contributions_per_90 = pp.goal_contributions / pp.mins_90s
        else:
            pp.goal_contributions_per_90 = 0
        # print(self.mins_played_in_match(player_id=player['_id'], match_id=players_teams_matches[1]['_id']))

        pp.conceded_per_90 = pp.conceded / pp.mins_90s if pp.mins_90s > 0 else 0  # Ensure non-zero denominator
        start_time = time.time()

        print("Time taken for clean_sheets:", time.time() - start_time)
        print('player_id', player.id)
        return pp.to_dict()
    
    # get player stats - bryce fn
    def get_player_stats(self, player_id):
        try:
            player = Player.objects.get(id=return_oid(player_id))
            stats = Stats()
            matches = Match.objects.filter(id__in=[mid.id for mid in player.matches])
            for match in matches:
                for match_stats in match['home_stats'] + match['away_stats']:
                    if match_stats['player_id'] == return_oid(player_id):
                        print(match_stats)
                        stats['match_day_squad'] += 1
                        min_played = match_stats['min_played']
                        if match_stats['starter']:
                            stats['starter'] += 1
                            stats['starter_minutes'] += min_played
                        else:
                            stats['sub_minutes'] += min_played
                        stats['min_played'] += min_played
                        for m in match_stats['goals']:
                            stats['goals'].append(m)
                        stats['assists'] += match_stats['assists']
                        stats['yellow_cards'] += match_stats['yellow_cards']
                        stats['red_cards'] += match_stats['red_cards']
                        if 'own_goals' in match_stats.keys():
                            stats['own_goals'] += match_stats['own_goals']
                        break
            print('allstats', stats)

            return stats
        except Exception as e:
            print_and_return_error(e)
            
    def get_player_performance_match(self, match_events, match_stats, all_stats):
        detailed_stats = PlayerPerformance()
        start_min = 0
        end_min = 0
        if match_stats['starter'] is True:
            detailed_stats = self.check_and_fill(detailed_stats, 'appearances', 1)
            detailed_stats = self.check_and_fill(detailed_stats, 'starts', 1)
            end_min = 90
        for event in match_events:
            if 'assist' in event:
                event['playerId'] = event['assisterId']
            if match_stats['player_id'].id == return_oid(event['playerId']):
                print('event', event)

                if 'PlayerSubbedOut' in event:
                    end_min = int(event['minute'])
                if 'PlayerSubbedIn' in event:
                    detailed_stats = self.check_and_fill(detailed_stats, 'appearances', 1)
                    start_min = int(event['minute'])
                    end_min = 90
                if 'goal' in event:
                    detailed_stats = self.check_and_fill(detailed_stats, 'goals', 1)
                if 'assist' in event:
                    detailed_stats = self.check_and_fill(detailed_stats, 'assists', 1)
        mins = end_min - start_min
        detailed_stats = self.check_and_fill(detailed_stats, 'mins', mins)

        detailed_stats = self.get_player_performance_for_match(match_events, start_min, end_min, detailed_stats, all_stats)

        return detailed_stats
    
    def get_player_performance_for_match(self, match_events, start_mins, end_mins, detailed_stats, all_stats):
        # MATCH DATA IS ENEMY DATA
        clean_sheet = True
        for events in match_events:
            if 'goal' in events:
                yes = False
                for players in all_stats:
                    # print('allstats',players)
                    if return_oid(events['playerId']) == return_oid(players['player_id'].id):
                        # print('event in same team')
                        yes = True
                if not yes:
                    if start_mins < events['minute'] < end_mins:
                        clean_sheet = False
                        detailed_stats = self.check_and_fill(detailed_stats, 'conceded', 1)
        if clean_sheet:
            detailed_stats = self.check_and_fill(detailed_stats, 'clean_sheets', 1)
        detailed_stats['mins_90s'] = detailed_stats['mins'] / 90
        detailed_stats['percent_matches'] = ((detailed_stats['appearances'] / detailed_stats['team_matches']) * 100) if \
            detailed_stats['team_matches'] > 0 else 0
        # potential mins=(pp.mins / (90 * pp.appearances) * 100)
        detailed_stats['percent_potential_mins'] = (
                detailed_stats['mins'] / (90 * detailed_stats['appearances']) * 100) if detailed_stats[
                                                                                            'appearances'] > 0 else 0
        detailed_stats['goals_per_90'] = (detailed_stats['goals'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                                       'mins_90s'] > 0 else 0
        detailed_stats['mins_per_goal'] = (detailed_stats['mins'] / detailed_stats['goals']) if detailed_stats[
                                                                                                    'goals'] > 0 else 0
        detailed_stats['assists_per_90'] = (detailed_stats['assists'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                                           'mins_90s'] > 0 else 0
        detailed_stats['goal_contributions'] = detailed_stats['assists'] + detailed_stats['goals']
        detailed_stats['goal_contributions_per_90'] = (
                detailed_stats['goal_contributions'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                          'mins_90s'] > 0 else 0
        detailed_stats['conceded_per_90'] = (detailed_stats['conceded'] / detailed_stats['mins_90s']) if detailed_stats[
                                                                                                             'mins_90s'] > 0 else 0
        return detailed_stats
    
    # def check_for_duplicate_player(self, name):
    #     # Query the database to check for players with the given name
    #     existing_player = Player.objects(name=name).first()
    #     return existing_player is not None  # Return True if a player with the given name exists, otherwise False
    
    # for dob, name, jersey_num - checker
    def check_for_duplicate_player(self, name, dob, jersey_num):
        # Query the database to check for players with the same name, dob, and jersey_num
        existing_player = Player.objects(name=name, dob=dob, jersey_num=jersey_num).first()
        return existing_player is not None  # Return True if a player with the same attributes exists, otherwise False
    
    def insert_player(self, player_data):
        try:
            name = player_data['names'].strip().title()
            nationality = player_data['nationality']
            dob = player_data['dob']
            # Check if dob is not an empty string
            if dob:
                # Convert the string to a datetime object
                original_dob = datetime.strptime(dob, '%Y-%m-%d')
                # Format the datetime object into the desired format 'dd/mm/yyyy'
                dob = original_dob.strftime('%d/%m/%Y')
            position = player_data['position']
            jersey_num = player_data['jersey_num']
            #supporting_file = player_data['supporting_file']
            reg_date = player_data['reg_date']

            # Check for duplicate player
            if self.check_for_duplicate_player(name, dob, jersey_num):
                return jsonify({"message": "This player already exists in the database. Please use move player instead"}), 200

            # Get team from database
            db_team = Team.objects(id=ObjectId(player_data['team_id'])).get()

            # Create new player object
            new_player = Player(
                name=name,
                dob=dob,
                nationality=nationality,
                jersey_num=jersey_num,
                #supporting_file=supporting_file,
                position=position
            )
            
            # Create player club association
            player_club = PlayerTeam(team_id=db_team.id, reg_date=reg_date, on_team=True)
            new_player.teams.append(player_club)

            # Save player to the database
            new_player.save()

            # Add player to team roster
            db_team.update(add_to_set__roster=new_player.id)

            return jsonify({"player": convert_object_ids_to_string(new_player.to_mongo())}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    # Move player atp
    def move_player(self, data):
        try: 
            player_id = return_oid(data['player_id'])
            db_player = Player.objects(id=player_id).first()
            if not db_player:
                return jsonify({"error": 'Player not found check ID'}), 404

            if data['old_team_id']:
                old_team_id = return_oid(data['old_team_id'])
                # update player docs
                db_player.teams.filter(team_id=old_team_id).update(set__on_team=False)
                old_team = Team.objects(id=old_team_id).first()
                if old_team:
                    old_team.update(pull__roster=player_id)

            new_team_id = return_oid(data['new_team_id'])
            reg_date = data['reg_date']

            new_team = PlayerTeam(team_id=new_team_id, reg_date=reg_date, on_team=True)
            db_player.teams.append(new_team)
            db_player.save()

            new_team = Team.objects(id=new_team_id).first()
            if new_team:
                new_team.update(add_to_set__roster=player_id)

            return jsonify({"player": convert_object_ids_to_string(db_player.to_mongo())}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
