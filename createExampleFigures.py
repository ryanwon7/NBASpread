import mysql.connector
import sys
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np

nbadb = mysql.connector.connect(
    host="localhost",
    user="nbauser",
    passwd="",
    database="nbadatabase"
)
db_cursor = nbadb.cursor()


def effective_field_goal_pct(field_goals_made, three_pointers_made, field_goals_attempted):
    return (field_goals_made + 0.5 * three_pointers_made) / field_goals_attempted


def turnover_pct(field_goals_attempted, free_throws_attempted, turnovers):
    return turnovers / (field_goals_attempted + 0.44 * free_throws_attempted + turnovers)


def offensive_rebound_percentage(offensive_rebounds, opponent_total_rebounds, opponent_offensive_rebounds):
    opponent_defensive_rebounds = opponent_total_rebounds - opponent_offensive_rebounds
    return offensive_rebounds / (offensive_rebounds + opponent_defensive_rebounds)


def free_throw_factor(free_throws_made, field_goals_attempted):
    return free_throws_made / field_goals_attempted


def retrieve_stats(team_string, season_start, season_end):
    sql_string = "SELECT * FROM boxscores WHERE (home='" + team_string + "' OR away='" + team_string + "') AND date>='" \
                 + season_start + "' AND date<= '" + season_end + "' ORDER BY date ASC;"
    db_cursor.execute(sql_string)
    records = db_cursor.fetchall()
    if db_cursor.rowcount != 82:
        print("Error when retrieving game records for team {}.".format(team_string))
        sys.exit()

    efg = [];
    to_pct = [];
    o_reb = [];
    ft = []

    for game in records:
        if game[0] == team_string:
            efg.append(effective_field_goal_pct(game[6], game[9], game[7]))
            to_pct.append(turnover_pct(game[7], game[13], game[20]))
            o_reb.append(offensive_rebound_percentage(game[15], game[32], game[31]))
            ft.append(free_throw_factor(game[12], game[7]))
        else:
            efg.append(effective_field_goal_pct(game[22], game[25], game[23]))
            to_pct.append(turnover_pct(game[23], game[29], game[36]))
            o_reb.append(offensive_rebound_percentage(game[31], game[16], game[15]))
            ft.append(free_throw_factor(game[28], game[23]))

    return np.asarray(efg), np.asarray(to_pct), np.asarray(o_reb), np.asarray(ft)


def main():
    team = "PHI"
    start_date, end_date = "2017-10-17", "2018-04-12"  # 2017-2018 NBA season
    efg, tov, oreb, ftfga = retrieve_stats(team, start_date, end_date)

    x_linspace = np.arange(82)

    fig = make_subplots(rows=2, cols=2, subplot_titles=("Effective Field Goal Percentage", "Turnover Percentage",
                                                        "Offensive Rebound Percentage", "Free Throw Factor"))
    fig.add_trace(go.Scatter(x=x_linspace, y=efg, mode='lines+markers', name='Effective Field Goal %'), row=1, col=1)
    fig.add_trace(go.Scatter(x=x_linspace, y=tov, mode='lines+markers', name='Turnover %'), row=1, col=2)
    fig.add_trace(go.Scatter(x=x_linspace, y=oreb, mode='lines+markers', name='Offensive Rebound %'), row=2, col=1)
    fig.add_trace(go.Scatter(x=x_linspace, y=ftfga, mode='lines+markers', name='Free Throw Factor'), row=2, col=2)

    # Update xaxis properties
    fig.update_xaxes(title_text="Season Games", row=1, col=1)
    fig.update_xaxes(title_text="Season Games", row=1, col=2)
    fig.update_xaxes(title_text="Season Games", row=2, col=1)
    fig.update_xaxes(title_text="Season Games", row=2, col=2)

    # Update yaxis properties
    fig.update_yaxes(title_text="EFG (%)", row=1, col=1)
    fig.update_yaxes(title_text="TOV (%)", row=1, col=2)
    fig.update_yaxes(title_text="OREB (%)", row=2, col=1)
    fig.update_yaxes(title_text="FTF (%)", row=2, col=2)

    fig.update_layout(
        title={
            'text': "Philadelphia 76ers in the 2017-2018 Season",
            'y': 0.5,
            'x': 0.44,
            'xanchor': 'center',
            'yanchor': 'top'},
        font=dict(
            family="Courier New, monospace",
            size=22,
            color="#7f7f7f"
        )
    )
    fig.show()


if __name__ == '__main__':
    main()
