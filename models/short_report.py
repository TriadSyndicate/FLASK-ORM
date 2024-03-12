# models.short_report

from mongoengine import *

# list with strengths & weaknesses
class attribute_list(EmbeddedDocument):
    attribute = StringField(unique=True)


class short_report(DynamicDocument):
    report_id = ObjectIdField(primary_key=True)
    player_id = ReferenceField('Player')
    match_id = ReferenceField('Match')
    game_context = StringField()
    report_date = DateField()
    player_profile = StringField()
    match_view = StringField()
    scout_name = StringField()
    formation = StringField()
    position = StringField()
    position_played = StringField()
    physical_profile = StringField()
    summary = StringField()
    grade = StringField()
    action = StringField()
    time_ready = DateField()
    conclusion = StringField()
    strengths = EmbeddedDocumentListField(attribute_list)
    weaknesses = EmbeddedDocumentListField(attribute_list)
    meta = {
    'collection': 'short_reports',
    'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.player import Player
        from models.match import Match

        self.game_context = values.get('game_context', '')
        self.scout_name = values.get('scout_name', '')
        self.formation = values.get('formation', '')
        self.physical_profile = values.get('physical_profile', '')
        self.conclusion = values.get('conclusion', '')
        self.position = values.get('position', '')
        self.summary = values.get('summary', '')
        self.grade = values.get('grade', '')
    
    @classmethod
    def create_short_report(cls, player_id, match_id, 
                            formation, position_played,
                            report_date, scout_name, 
                            player_profile, match_view, game_context, position, 
                            physical_profile, summary, conclusion, grade, action,
                            time_ready, strengths, weaknesses):
        short_report_data = {
            "player_id": player_id,
            "match_id": match_id, 
            "formation": formation,
            "position_played": position_played,
            "report_date": report_date,
            "scout_name": scout_name,
            "player_profile": player_profile,
            "match_view": match_view,
            "game_context": game_context,
            "position": position,
            "physical_profile": physical_profile,
            "summary": summary,
            "conclusion": conclusion,
            "grade": grade,
            "action": action,
            "time_ready": time_ready,
            "strengths": strengths,
            "weaknesses": weaknesses
        }
        short_report = cls(**short_report_data)
        try:
            short_report.save()
            return str(short_report.id)
        except Exception as e:
            return {"error": f"Failed to create short report: {str(e)}"}
