# models.recommendation_report

from mongoengine import *

class recommendation_report(DynamicDocument):
    report_id = ObjectIdField(primary_key=True)
    player_id = ReferenceField('Player') 
    match_id = ReferenceField('Match') 
    report_date = DateField()
    scout_name = StringField()
    scout_role = StringField()
    preferred_foot = StringField()
    shirt_number = IntField()
    position_played = StringField()
    player_profile = StringField()
    likes = StringField()
    explain_likes = StringField()
    improve = StringField()
    explain_improve = StringField()
    recommendation_monitor = StringField()
    meta = {
    'collection': 'recommendation_reportv2',
    'strict': False
    }

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        from models.player import Player
        from models.match import Match
        self.report_date = values['report_date']
        self.scout_name = values['scout_name']
        self.scout_role = values['scout_role']
        self.preferred_foot = values['preferred_foot']
        self.position_played = values['position_played']
        self.player_profile = values['player_profile']
        self.explain_likes = values['explain_likes']
        self.explain_improve = values['explain_improve']
        self.recommendation_monitor = values['recommendation_monitor']


class YesOrNoReport(EmbeddedDocument):
    scout_name = StringField()
    player_id = ReferenceField('Player')
    match_id = ReferenceField('Match')
    report_date = DateField()
    conclusion = StringField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from models.player import Player
        from models.match import Match
