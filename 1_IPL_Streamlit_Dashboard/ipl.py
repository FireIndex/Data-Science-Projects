# season of team
# season of player

import math
import pandas as pd
import numpy as np

# DEFAULT_MATCHES="https://docs.google.com/spreadsheets/d/e/2PACX-1vRy2DUdUbaKx_Co9F0FSnIlyS-8kp4aKv_I0-qzNeghiZHAI_hw94gKG22XTxNJHMFnFVKsO4xWOdIs/pub?gid=1655759976&single=true&output=csv"
# DEFAULT_BALLS="https://docs.google.com/spreadsheets/d/e/2PACX-1vRu6cb6Pj8C9elJc5ubswjVTObommsITlNsFy5X0EiBY7S-lsHEUqx3g_M16r50Ytjc0XQCdGDyzE_Y/pub?output=csv"

class IPL:
    OBJECT_NUMBER = 0

    def __init__(self, ipl_matches="data/IPL_Matches_2008_2022.csv", ipl_balls="data/IPL_Ball_by_Ball_2008_2022.csv"):
        self.matches = pd.read_csv(ipl_matches)
        self.balls = pd.read_csv(ipl_balls)
        self.Data_Optimization()

        self.limited_ball_match = self.balls.merge(self.matches[['ID','Season','MatchNumber','Team1','Team2', 'WinningTeam', 'Player_of_Match']], on='ID', how='inner').copy()
        
        IPL.OBJECT_NUMBER += 1
        print("IPL object created", IPL.OBJECT_NUMBER)


    # Data Cleaning
    def Data_Optimization(self):
        self.balls.ID = self.balls.ID.astype(np.int32)
        self.balls.innings = self.balls.innings.astype(np.int8)
        self.balls.overs = self.balls.overs.astype(np.int8)
        self.balls.ballnumber = self.balls.ballnumber.astype(np.int8)
        self.balls.batter = self.balls.batter.astype('category')
        self.balls.bowler = self.balls.bowler.astype('category')
        self.balls['non-striker'] = self.balls['non-striker'].astype('category')
        self.balls.extra_type = self.balls.extra_type.astype('category')
        self.balls.batsman_run = self.balls.batsman_run.astype(np.int8)
        self.balls.extras_run = self.balls.extras_run.astype(np.int8)
        self.balls.total_run = self.balls.total_run.astype(np.int8)
        self.balls.non_boundary = self.balls.non_boundary.astype(np.int8)
        self.balls.isWicketDelivery = self.balls.isWicketDelivery.astype(np.int8)
        self.balls.player_out = self.balls.player_out.astype('category')
        self.balls.kind = self.balls.kind.astype('category')
        self.balls.fielders_involved = self.balls.fielders_involved.astype('category')
        self.balls.BattingTeam = self.balls.BattingTeam.astype('category')

        self.matches.loc[self.matches['Season'] == '2007/08', 'Season'] = '2008'
        self.matches.loc[self.matches['Season'] == '2009/10', 'Season'] = '2010'
        self.matches.loc[self.matches['Season'] == '2020/21', 'Season'] = '2020'

        self.balls = self.balls[self.balls.innings.isin([1, 2])]#.copy() # Excluding Super overs


    # utility functions
    def allSeasons_API(self):
        seasons = ['All'] + np.unique(self.matches['Season']).tolist()
        return {"seasons": seasons, "total_seasons": len(seasons)}

    def allTeams_API(self):
        all_teams = np.unique(np.append(self.matches['Team1'], self.matches['Team2'])).copy()

        response = {"teams": all_teams.tolist(), "total_teams": len(all_teams)}
        return response

    def allPlayers_API(self):
        Team1Players = self.matches['Team1Players'].copy()
        Team2Players = self.matches['Team2Players'].copy()

        all_players = np.unique(Team1Players.str.lstrip("['").str.rstrip("']").str.split("', '").sum() + Team2Players.str.lstrip("['").str.rstrip("']").str.split("', '").sum())

        response = {"total_players": len(all_players), "players": all_players.tolist()}
        return response

    def teamPlayers_API(self, team):
        valid_teams = self.allTeams_API()['teams']
        if team not in valid_teams:
            return {"error": "Invalid team name"}

        # Don't want against player
        if_team1 = self.matches[self.matches['Team1'] == team].copy()
        if_team2 = self.matches[self.matches['Team2'] == team].copy()
        players = np.unique(if_team1['Team1Players'].str.lstrip("['").str.rstrip("']").str.split("', '").sum() + if_team2['Team2Players'].str.lstrip("['").str.rstrip("']").str.split("', '").sum())

        response = {"team": team, "total_players": len(players), "players": players.tolist()}
        return response


    # team carier team against team
    def teamRecord_API(self, team, seasons=['All']):
        valid_teams = self.allTeams_API()['teams']
        if team not in valid_teams:
            return {"error": "Invalid team name"}
        
        valid_seasons = self.allSeasons_API()['seasons']
        if not all(season in valid_seasons for season in seasons):
            return {"error": "One or more invalid season names provided"}

        ball_match = self.limited_ball_match.copy()

        if not seasons or seasons == [] or type(seasons) != list:
            return {'overall': {}, 'against': {'team':{}, 'season':{}}, 'delta':{}, 'help':{}, 'message': 'privide seasons in list os string'}
        elif 'All' not in seasons:
            ball_match = ball_match[ball_match['Season'].isin(seasons)].copy()
        else:
            pass # return all

        team_df = ball_match[(ball_match['Team1'] == team) | (ball_match['Team2'] == team)].copy()
        team_df['Against'] = np.where(team_df['Team1'] == team, team_df['Team2'], team_df['Team1'])
        team_df.Against = team_df.Against.astype('category')
        beforeLastMatch_df = team_df[team_df.ID < team_df.ID.max()].copy()
        
        AgainstTeam, AgainstSeason, delts = {}, {}, {}
        OverAll = self.teamRecord(team, team_df)
        BeforeLast = self.teamRecord(team, beforeLastMatch_df)

        for key in OverAll:
            delts[key] = round(OverAll.get(key, 0) - BeforeLast.get(key, 0), 2)

        groupByAgainstTeam = team_df.groupby('Against', observed=False) # observed=False to error in numbers for categorical data
        for name, data in groupByAgainstTeam:
            AgainstTeam[name] = self.teamRecord(team, data)

        groupByAgainstSeason = team_df.groupby('Season')
        for name, data in groupByAgainstSeason:
            AgainstSeason[name] = self.teamRecord(team, data)

        return {
            'overall': OverAll,
            'against': {
                'team': AgainstTeam,
                'season': AgainstSeason
            },
            'delta': delts,
            'help': {
                'Matches': 'Total matches played by team',
                'Wins': 'Total matches won by team',
                'Losses': 'Total matches lost by team',
                'Ties': 'Total matches tied by team',
                'Runs': 'Total runs scored by team',
                'Wickets': 'Total wickets taken by team',
                'Balls': 'Total balls faced by team',
                'Run Rate': 'Average runs scored by team per over',
                'Con. Runs': 'Total runs conceded by team',
                'Con. Wickets': 'Total wickets lost by team',
                'Con. Balls': 'Total balls bowled by team',
                'Con. Run Rate': 'Average runs conceded by team per over',
                'Win %': 'Winning percentage of team',
                'Title': 'Total titles won by team'
            }
        }

    def teamRecord(self, team, data, against=None):
        matches_played = data.ID.nunique()
        win = data[data.WinningTeam == team].ID.nunique() # team win = conceded loss
        loss = data[data.WinningTeam != team].ID.nunique() # team loss = conceded win
        noResult = matches_played - win - loss
        title = data[(data.MatchNumber == 'Final') & (data.WinningTeam == team)].ID.nunique()
        winningPercentage = round((win/matches_played)*100, 2) if matches_played else 0
        
        batting_df = data[data.BattingTeam == team]
        bowling_df = data[data.BattingTeam != team]

        total_runs = batting_df.total_run.sum() # How many runs scored by team # [batsman_run + extras = totals] extras are added to the batting team's total, but are not credited to the batter
        total_balls = (batting_df.extra_type != 'wides').sum() # How many balls faced by team
        total_wickets = bowling_df.isWicketDelivery.sum() # How many wickets get by team
        total_conceded_runs = bowling_df.total_run.sum() # How many runs conceded by team # [batsman_run + extras = totals] extras are added to the batting team's total, but are not credited to the batter
        total_conceded_balls = (bowling_df.extra_type != 'wides').sum() # How many balls bowled by team
        total_conceded_wickets = batting_df.isWicketDelivery.sum() # How many wickets lost by team

        run_rate = round(total_runs/(total_balls/6), 2) if total_balls and total_conceded_balls else 0
        conceded_run_rate = round(total_conceded_runs/(total_conceded_balls/6), 2) if total_balls and total_conceded_balls else 0

        return {
            'Matches': int(matches_played),
            'Wins': int(win),
            'Losses': int(loss),
            'Ties': int(noResult),
            'Runs': int(total_runs),
            'Wickets': int(total_wickets),
            'Balls': int(total_balls),
            'Run Rate': round(float(run_rate), 2),
            'Con. Runs': int(total_conceded_runs),
            'Con. Wickets': int(total_conceded_wickets),
            'Con. Balls': int(total_conceded_balls),
            'Con. Run Rate': round(float(conceded_run_rate), 2),
            'Win %': round(float(winningPercentage), 2),
            'Title': int(title),
        }


    # batsman carier & batsman against team
    def batsmanRecord_API(self, batsman, seasons=['All']):
        valid_players = self.allPlayers_API()['players']
        if batsman not in valid_players:
            return {"error": "Invalid player name"}

        valid_seasons = self.allSeasons_API()['seasons']
        if not all(season in valid_seasons for season in seasons):
            return {"error": "One or more invalid season names provided"}

        ball_match = self.limited_ball_match.copy()

        if not seasons or seasons == [] or type(seasons) != list:
            return {'overall': {}, 'against': {'team':{}, 'season':{}}, 'delta':{}, 'help':{}, 'message': 'privide seasons in list os string'}
        elif 'All' not in seasons:
            ball_match = ball_match[ball_match['Season'].isin(seasons)].copy()
        else:
            pass # return all

        # Add BattingTeam: Determine the bowling team using vectorized operations
        # Use a boolean mask to identify where BattingTeam is equal to Team1
        mask = ball_match['BattingTeam'] == ball_match['Team1']
        # Create the BowlingTeam column using where:
        # If BattingTeam == Team1, use Team2; otherwise, use Team1
        ball_match['BowlingTeam'] = ball_match['Team2'].where(mask, ball_match['Team1']).astype('category')

        filter_batsman = ball_match[ball_match['batter'] == batsman]
        beforeLastMatch_df = filter_batsman[filter_batsman.ID < filter_batsman.ID.max()].copy()
        
        AgainstTeam, AgainstSeason, delts = {}, {}, {}
        OverAll = self.batsmanRecord(batsman, ball_match)
        BeforeLast = self.batsmanRecord(batsman, beforeLastMatch_df)

        for key in OverAll:
            if key == 'Highest Score':
                delts[key] = float(OverAll.get(key, 0).replace('*', '')) - float(BeforeLast.get(key, 0).replace('*', ''))
                continue
            delts[key] = round(OverAll.get(key, 0) - BeforeLast.get(key, 0), 2)

        groupByAgainstTeam = filter_batsman.groupby('BowlingTeam', observed=False) # observed=False to error in numbers for categorical data
        for name, data in groupByAgainstTeam:
            AgainstTeam[name] = self.batsmanRecord(batsman, data)

        groupByAgainstSeason = filter_batsman.groupby('Season')
        for name, data in groupByAgainstSeason:
            AgainstSeason[name] = self.batsmanRecord(batsman, data)

        return {
            'overall': OverAll,
            'against': {
                'team': AgainstTeam,
                'season': AgainstSeason
            },
            'delta': delts,
            'help': {
                'Innings': 'Total innings played by batsman',
                'Runs': 'Total runs scored by batsman',
                'Not Out': 'Total not out innings played by batsman',
                'Highest Score': 'Highest score made by batsman',
                'Fifties (50s)': 'Total fifties scored by batsman',
                'Hundreds (100s)': 'Total hundreds scored by batsman',
                'Fours': 'Total fours scored by batsman',
                'Sixes': 'Total sixes scored by batsman',
                'Average': 'Average runs scored by batsman',
                'Strike Rate': 'Strike rate of batsman',
                'Man of Match': 'Number of times batsman Man of Match'
            }
        }
    
    def batsmanRecord(self, batsman_name, df):
        outs = df[df['player_out'] == batsman_name].shape[0] # may be run out when he was not batting

        batsman_df = df[df['batter'] == batsman_name]

        ball_count = batsman_df.shape[0]
        innings = batsman_df.ID.nunique()
        total_runs = batsman_df.batsman_run.sum()
        fours = batsman_df[(batsman_df.batsman_run == 4) & (batsman_df.non_boundary == 0)].shape[0]
        sixes = batsman_df[(batsman_df.batsman_run == 6) & (batsman_df.non_boundary == 0)].shape[0]
        avg = round(total_runs/outs, 2) if outs else 0 # np.inf
        noballs = batsman_df[~(batsman_df.extra_type == 'wides')].shape[0] # number of balls
        strike_rate = round((total_runs/noballs) * 100, 2) if noballs else 0 # np.nan

        inniBatsTotalRuns = batsman_df[['ID', 'batsman_run']].groupby('ID').sum()
        fifties = inniBatsTotalRuns[(inniBatsTotalRuns.batsman_run >= 50) & (inniBatsTotalRuns.batsman_run < 100)].shape[0]
        hundreds = inniBatsTotalRuns[inniBatsTotalRuns.batsman_run >= 100].shape[0]
        highest_score = None

        try:
            highest_score = inniBatsTotalRuns.batsman_run.sort_values(ascending=False).head(1).values[0]
            high_score_ID = inniBatsTotalRuns.batsman_run.sort_values(ascending=False).head(1).index[0]

            # Check did batsman out while making high_score or not, if out then simply return HIGH SCORE else use ASTRIC (*) mean did not out
            did_out = (batsman_df[batsman_df.ID == high_score_ID].player_out == batsman_name).any()
            if not did_out:
                highest_score = str(highest_score) + '*'
                pass
        except:
            highest_score = inniBatsTotalRuns.batsman_run.max()

        not_out = innings - outs
        mom = batsman_df['ID'][batsman_df.Player_of_Match == batsman_name].nunique()


        return {
            'Innings': int(innings),
            'Runs': int(total_runs),
            'Not Out': int(not_out),
            'Highest Score': str(highest_score), # int(highest_score) if str(highest_score).isdigit() else highest_score,
            'Fifties (50s)': int(fifties),
            'Hundreds (100s)': int(hundreds),
            'Fours': int(fours),
            'Sixes': int(sixes),
            'Average': round(float(avg), 2),
            'Strike Rate': round(float(strike_rate), 2),
            'Man of Match': int(mom)
        }


    # bowler carier & bowler against team
    def bowlerRecord_API(self, bowler, seasons=['All']):
        valid_players = self.allPlayers_API()['players']
        if bowler not in valid_players:
            return {"error": "Invalid player name"}

        valid_seasons = self.allSeasons_API()['seasons']
        if not all(season in valid_seasons for season in seasons):
            return {"error": "One or more invalid season names provided"}

        ball_match = self.limited_ball_match.copy()

        if not seasons or seasons == [] or type(seasons) != list:
            return {'overall': {}, 'against': {'team':{}, 'season':{}}, 'delta':{}, 'help':{}, 'message': 'privide seasons in list os string'}
        elif 'All' not in seasons:
            ball_match = ball_match[ball_match['Season'].isin(seasons)].copy()
        else:
            pass # return all

        # Add bowler_run, isBowlerWicket: Determine the bowling team using vectorized operations
        # Use vectorized operations to compute 'bowler_run'
        ball_match['bowler_run'] = np.where(
            ball_match['extra_type'].isin(['penalty', 'legbyes', 'byes']),
            0,  # If extra_type is in ['penalty', 'legbyes', 'byes'], set bowler_run to 0
            ball_match['total_run']  # Otherwise, set bowler_run to total_run
        )

        ball_match['isBowlerWicket'] = np.where(
            ball_match['kind'].isin(['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket']),
            ball_match['isWicketDelivery'],  # If kind is in ['caught', 'caught and bowled', 'bowled', 'stumped', 'lbw', 'hit wicket'], set isBowlerWicket to isWicketDelivery
            0  # Otherwise, set isBowlerWicket to 0
        ).astype(np.int8)
        filter_bowler = ball_match[ball_match['bowler'] == bowler].copy()
        beforeLastMatch_df = filter_bowler[filter_bowler.ID < filter_bowler.ID.max()].copy()
        
        AgainstTeam, AgainstSeason, delts = {}, {}, {}
        OverAll = self.bowlerRecord(bowler, ball_match)
        BeforeLast = self.bowlerRecord(bowler, beforeLastMatch_df)

        for key in OverAll:
            if key == 'Best Figure Fraction':
                os, bs = OverAll.get(key, '0/0').split('/'), BeforeLast.get(key, '0/0').split('/')
                delts[key] = f'{int(os[0]) - int(bs[0])}/{int(os[1]) - int(bs[1])}'
                continue
            delts[key] = round(OverAll.get(key, 0) - BeforeLast.get(key, 0), 2)

        groupByAgainstTeam = filter_bowler.groupby('BattingTeam', observed=False)
        for name, data in groupByAgainstTeam:
            AgainstTeam[name] = self.bowlerRecord(bowler, data)

        groupByAgainstSeason = filter_bowler.groupby('Season')
        for name, data in groupByAgainstSeason:
            AgainstSeason[name] = self.bowlerRecord(bowler, data)

        return {
            'overall': OverAll,
            'against': {
                'team': AgainstTeam,
                'season': AgainstSeason
            },
            'delta': delts,
            'help': {
                'Innings': 'Total innings bowled by bowler',
                'Wickets': 'Total wickets taken by bowler',
                '3+W': 'Total innings where bowler took 3 or more wickets',
                'Best Figure Fraction': 'Best figure of bowler in fraction',
                'Average': 'Average runs conceded by bowler',
                'Economy': 'Economy rate of bowler',
                'Strike Rate': 'Strike rate of bowler',
                'Man of Match': 'Number of times bowler Man of Match',
                'Fours': 'Total fours conceded by bowler',
                'Sixes': 'Total sixes conceded by bowler',
                'Best Figure': 'Best figure of bowler'
            }
        }

    def bowlerRecord(self, bowler_name, df):
        bowler_df = df[df['bowler'] == bowler_name]

        innings = bowler_df.ID.unique().shape[0]
        noballs = bowler_df[~(bowler_df.extra_type.isin(['wides', 'noballs']))].shape[0]
        total_runs = bowler_df['bowler_run'].sum()
        eco = round((total_runs/noballs) * 6, 2) if noballs else 0
        fours = bowler_df[(bowler_df.batsman_run == 4) & (bowler_df.non_boundary == 0)].shape[0]
        sixes = bowler_df[(bowler_df.batsman_run == 6) & (bowler_df.non_boundary == 0)].shape[0]

        wicket = bowler_df.isBowlerWicket.sum()
        avg = round((total_runs/wicket), 2) if wicket else 0 # np.inf
        strike_rate = round((noballs/wicket) * 6, 2) if wicket else 0 # np.nan

        groupByID = bowler_df[['ID','isBowlerWicket', 'bowler_run']].groupby('ID').sum()
        w3 = groupByID[(groupByID.isBowlerWicket >= 3)].shape[0]

        best_wicket = groupByID.sort_values(['isBowlerWicket', 'bowler_run'], ascending=[False, True]).head(1).values
        best_figure_fraction = f'{best_wicket[0][0]}/{best_wicket[0][1]}' if best_wicket.size > 0 else '0/0'

        num, den = best_figure_fraction.split('/')
        best_figure = int(num)/int(den) if int(den) != 0 else 0

        mom = bowler_df[bowler_df.Player_of_Match == bowler_name].drop_duplicates('ID', keep='first').shape[0]

        return {
            'Innings': int(innings),
            'Wickets': int(wicket),
            '3+W': int(w3),
            'Best Figure Fraction': str(best_figure_fraction),
            'Average': round(float(avg), 2),
            'Economy': round(float(eco), 2),
            'Strike Rate': round(float(strike_rate), 2),
            'Man of Match': int(mom),
            'Fours': int(fours),
            'Sixes': int(sixes),
            'Best Figure': round(float(best_figure), 2),
        }


    # player against player
    def playerComparison_API(self, *players):
        valid_players = self.allPlayers_API()['players']
        # Check if all provided player are valid
        if not all(player in valid_players for player in players):
            return {"error": "One or more invalid team names provided"}

        response = {'batsman_comparison': {}, 'bowler_comparison': {}}
        for player in players:
            response['batsman_comparison'][player] = self.batsmanRecord_API(player)
            response['bowler_comparison'][player] = self.bowlerRecord_API(player)

        return response


# if __name__ == '__main__':
#     ipl = IPL()

#     team1 = 'Royal Challengers Bangalore'
#     team2 = 'Chennai Super Kings'

#     # print(ipl.teams_API())
#     print(ipl.teamvteam_API(team1, team2))