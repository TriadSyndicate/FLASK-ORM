# models.long_report

from mongoengine import *

# Define an embedded document for unique attributes in the long report
class LongReportUniqueAttributes(EmbeddedDocument):
    attribute = StringField()
    score = IntField(unique=True, required=True)
    comment = StringField()


# Define the main document for the long report
class LongReport(DynamicDocument):
    # Fields for the long report
    report_id = ObjectIdField(primary_key=True)  # Primary key for the long report
    player_id = ReferenceField('Player')  # Reference to the Player model
    match_id = ReferenceField('Match')  # Reference to the Match model
    match_view = StringField()
    report_date = DateTimeField(required=True)  # Date and time of the report
    min_played = IntField(required=True)  # Number of minutes played
    formation = StringField(required=True)  # String field for the formation
    position_played = StringField(required=True)  # String field for the position played
    scout_name = StringField(required=True)  # String field for the scout's name
    player_profile = StringField(required=True)  # String Field for the player profile
    game_context = StringField(required=True)  # String field for the game context
    height = StringField(required=True)  # Integer field for the player's height
    build = StringField(required=True)  # String field for the player's build
    unique_attributes = EmbeddedDocumentListField('LongReportUniqueAttributes')  # List of unique attributes
    summary_PMS = StringField()  # String field for the summary_PMS
    summary_PST = StringField()  # String field for the summary_PST
    overall_thoughts = StringField()  # String field for overall thoughts
    grade = StringField(required=True)  # String field for the grade
    next_action = StringField()  # String field for the next action
    duration_till_ready = StringField()  # String field for the duration till ready

    # Meta class to specify the collection name in MongoDB
    meta = {'collection': 'long_reports'}

    # Constructor to initialize certain fields
    def __init__(self, *args, **values):
        # Call the constructor of the parent class (DynamicDocument)
        super().__init__(*args, **values)
        from models.match import Match
        from models.player import Player
        # Assign specific values to fields during initialization
        self.match_view = values['match_view']
        self.game_context = values['game_context']
        self.scout_name = values['scout_name']
        self.formation = values['formation']
        self.build = values['build']
        self.summary_PMS = values['summary_PMS']
        self.summary_PST = values['summary_PST']
        self.overall_thoughts = values['overall_thoughts']
        self.grade = values['grade']
        self.next_action = values['next_action']
        self.duration_till_ready = values['duration_till_ready']