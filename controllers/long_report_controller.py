#long_report_controller.py

from flask import jsonify, request
from functions import return_oid, convert_object_ids_to_string
from models.long_report import LongReport, LongReportUniqueAttributes


class LongReportController:
    def __init__(self):
        from models.long_report import LongReport
        from controllers.player_controller import PlayerController
        from controllers.match_controller import MatchController
        
        self.PC = PlayerController()
        self.MC = MatchController()
        
    def _handle_errors(self, error_message):
        # Private method to handle errors by returning a JSON response with an error message
        return jsonify({'error': error_message}), 404

    def upload_long_report(self):
        data = request.get_json()
        player_id = return_oid(data['player_id'])
        match_id = return_oid(data['match_id'])
        player_team_id = return_oid(data['player_team_id'])

        player_details = self.PC.fetch_player_details(player_id)
        match_details = self.MC.fetch_match_details(match_id)

        if 'error' in player_details:
            return self._handle_errors(player_details['error'])
        if 'error' in match_details:
            return self._handle_errors(match_details['error'])

        # unique_attributes_data = {}
        unique_attributes_data = []

        for attribute_data in data['unique_attributes']:
            x = LongReportUniqueAttributes(
                attribute=attribute_data['attribute'],
                score=attribute_data['score'],
                comment=attribute_data['comment']).to_mongo()
            unique_attributes_data.append(x)

        # for attribute_data in data['unique_attributes']:
        #     for attribute_key, attribute_value in attribute_data.items():
        #         x = LongReportUniqueAttributes(score=attribute_value['score'],
        #                                        comment=attribute_value['comment']).to_mongo()
        #         unique_attributes_data.update({attribute_key: x})

        long_report_data = LongReport(
            player_id=player_id,
            match_id=match_id,
            match_view=data['match_view'],
            report_date=data['report_date'],
            formation=data['formation'],
            position_played=data['position_played'],
            scout_name=data['scout_name'],
            player_profile=data['player_profile'],
            game_context=data['game_context'],
            height=data['height'],
            build=data['build'],
            unique_attributes=unique_attributes_data,
            summary_PMS=data['summary_PMS'],
            summary_PST=data['summary_PST'],
            overall_thoughts=data['overall_thoughts'],
            grade=data['grade'],
            next_action=data['next_action'],
            duration_till_ready=data['duration_till_ready']
        )

        self.db.long_reports.insert_one(long_report_data.to_mongo())

        return SUCCESS_201