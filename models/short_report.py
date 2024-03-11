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



class shortReport(EmbeddedDocument):
    report_id = ReferenceField(short_report)
