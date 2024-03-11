import datetime
from flask import jsonify, request
import pytz
from functions import convert_object_ids_to_string, return_oid

from mongoengine import DoesNotExist

from models.player import Player, PlayerPerformance
from models.goal import Goal
from models.match import MatchStats
from models.team import Team
from functions import return_oid
from dateutil import parser

class PlayerController:
    def __init__(self):
        from models.match import Match, MatchStats 
        self.match = Match()
        self.player = Player()
        
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