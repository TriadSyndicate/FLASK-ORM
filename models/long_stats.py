# models.long_stats

class PlayerPerformance:
    def __init__(self):
        self.team_matches = None
        self.appearances = None
        self.starts = None
        self.mins = None
        self.mins_90s = None
        self.percent_matches = None
        self.percent_potential_mins = None
        self.goals = None
        self.goals_per_90 = None
        self.mins_per_goal = None
        self.penalties = None
        self.assists = None
        self.assists_per_90 = None
        self.goal_contributions = None
        self.goal_contributions_per_90 = None
        self.conceded = None
        self.conceded_per_90=None
        self.clean_sheets=None

    def __str__(self):
        return (
            f"Team Matches: {self.team_matches}\n"
            f"Appearances: {self.appearances}\n"
            f"Starts: {self.starts}\n"
            f"Mins: {self.mins}\n"
            f"Mins per 90s: {self.mins_90s}\n"
            f"Percent Matches: {self.percent_matches}\n"
            f"Percent Potential Mins: {self.percent_potential_mins}\n"
            f"Goals: {self.goals}\n"
            f"Goals per 90: {self.goals_per_90}\n"
            f"Mins per Goal: {self.mins_per_goal}\n"
            f"Penalties: {self.penalties}\n"
            f"Assists: {self.assists}\n"
            f"Assists per 90: {self.assists_per_90}\n"
            f"Goal Contributions: {self.goal_contributions}\n"
            f"Goal Contributions per 90: {self.goal_contributions_per_90}\n"
            f"Conceded: {self.conceded}\n"
            f"Conceded per 90: {self.conceded_per_90}\n"
            f"Clean Sheets: {self.clean_sheets}"
        )

    def to_dict(self):
        return self.__dict__
