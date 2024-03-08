from mongoengine import *
from bson.objectid import ObjectId

class Goal(EmbeddedDocument):
    minute = IntField(default=None)
    match_id = ReferenceField('Match', dbref=False)
    nt_match_id = ReferenceField('NtMatch', dbref=False)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.minute = values['minute']




class PlayerTeam(EmbeddedDocument):
    team_id = ReferenceField('Team', dbref=False)
    reg_date = StringField(default=None)
    on_team = BooleanField(default=True)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.team_id = values['team_id']
        self.reg_date = values['reg_date']
        self.on_team = values['on_team']

class Stats(EmbeddedDocument):
    match_day_squad = IntField(default=0)
    starter = IntField(default=0)
    min_played = IntField(default=0)
    starter_minutes = IntField(default=0)
    sub_minutes = IntField(default=0)
    goals = EmbeddedDocumentListField(Goal, default=[])
    assists = IntField(default=0)
    yellow_cards = IntField(default=0)
    red_cards = IntField(default=0)
    clean_sheets = IntField(default=0)
    own_goals = IntField(default=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



class PlayerPerformance(EmbeddedDocument):
    team_matches = IntField(default=0)
    appearances = IntField(default=0)
    starts = IntField(default=0)
    mins = IntField(default=0)
    mins_90s = IntField(default=0)
    percent_matches = IntField(default=0)
    percent_potential_mins = IntField(default=0)
    goals = IntField(default=0)
    goals_per_90 = IntField(default=0)
    mins_per_goal = IntField(default=0)
    penalties = IntField(default=0)
    assists = IntField(default=0)
    assists_per_90 = IntField(default=0)
    goal_contributions = IntField(default=0)
    goal_contributions_per_90 = IntField(default=0)
    conceded = IntField(default=0)
    conceded_per_90 = IntField(default=0)
    clean_sheets = IntField(default=0)

    def to_dict(self):
        return {
            'team_matches': self.team_matches,
            'appearances': self.appearances,
            'starts': self.starts,
            'mins': self.mins,
            'mins_90s': self.mins_90s,
            'percent_matches': self.percent_matches,
            'percent_potential_mins': self.percent_potential_mins,
            'goals': self.goals,
            'goals_per_90': self.goals_per_90,
            'mins_per_goal': self.mins_per_goal,
            'penalties': self.penalties,
            'assists': self.assists,
            'assists_per_90': self.assists_per_90,
            'goal_contributions': self.goal_contributions,
            'goal_contributions_per_90': self.goal_contributions_per_90,
            'conceded': self.conceded,
            'conceded_per_90': self.conceded_per_90,
            'clean_sheets': self.clean_sheets,
            # Add other fields as needed
        }
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Player(DynamicDocument):
    name = StringField(required=True)
    first_name = StringField()
    last_name = StringField()
    dob = StringField()
    nationality = StringField(default='none')
    jersey_num = IntField(default=0)
    position = StringField(default=None)
    stats = EmbeddedDocumentField(Stats)
    performance = EmbeddedDocumentListField(PlayerPerformance)
    teams = EmbeddedDocumentListField(PlayerTeam, default=[])
    matches = ListField(ReferenceField('Match', dbref=False))
    supporting_file = StringField(default=None)

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.name = values['name']
        # self.first_name = self.name.split()[0]
        # self.last_name = self.name.split()[1]
        self.dob = values['dob']
        self.nationality = values['nationality']
        self.jersey_num = values['jersey_num']
        self.supporting_file = values['supporting_file']
        self.position = values['position']
        self.stats = Stats().to_mongo()