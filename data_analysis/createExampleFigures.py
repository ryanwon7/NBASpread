import mysql.connector
import sys
import plotly.graph_objects as go
import numpy as np
import os

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

    efg = []
    to_pct = []
    o_reb = []
    ft = []

    for game in records:
        if game[0] == team_string:
            efg.append(effective_field_goal_pct(game[6], game[9], game[7]))
            to_pct.append(turnover_pct(game[7], game[13], game[20]))
            o_reb.append(offensive_rebound_percentage(game[15], game[32], game[31]))
            ft.append(free_throw_factor(game[12], game[7]))
            pass
        else:
            efg.append(effective_field_goal_pct(game[22], game[25], game[23]))
            to_pct.append(turnover_pct(game[23], game[29], game[36]))
            o_reb.append(offensive_rebound_percentage(game[31], game[16], game[15]))
            ft.append(free_throw_factor(game[28], game[23]))

    return np.asarray(efg), np.asarray(to_pct), np.asarray(o_reb), np.asarray(ft)


def main():
    if not os.path.exists("../images"):
        os.mkdir("../images")

    team = "PHI"
    start_date, end_date = "2017-10-17", "2018-04-12"  # 2017-2018 NBA season
    efg, tov, oreb, ftfga = retrieve_stats(team, start_date, end_date)

    x_linspace = np.arange(82)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=x_linspace, y=efg, mode='lines+markers'))
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=x_linspace, y=tov, mode='lines+markers'))
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(x=x_linspace, y=oreb, mode='lines+markers'))
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(x=x_linspace, y=ftfga, mode='lines+markers'))

    fig1.update_layout(
        title={
            'text': "76ers Effective Field Goal 2017-2018",
            'x': 0.5
        },
        xaxis_title="Season Games",
        yaxis_title="EFG (%)",
        font=dict(
            family="Courier New, monospace",
            size=22,
            color="#7f7f7f"
        )
    )
    fig2.update_layout(
        title={
            'text': "76ers Turnover 2017-2018",
            'x': 0.5
        },
        xaxis_title="Season Games",
        yaxis_title="TO (%)",
        font=dict(
            family="Courier New, monospace",
            size=22,
            color="#7f7f7f"
        )
    )
    fig3.update_layout(
        title={
            'text': "76ers Offensive Rebound 2017-2018",
            'x': 0.5
        },
        xaxis_title="Season Games",
        yaxis_title="OREB (%)",
        font=dict(
            family="Courier New, monospace",
            size=22,
            color="#7f7f7f"
        )
    )
    fig4.update_layout(
        title={
            'text': "76ers Free Throw Factor 2017-2018",
            'x': 0.5
        },
        xaxis_title="Season Games",
        yaxis_title="FTF (%)",
        font=dict(
            family="Courier New, monospace",
            size=22,
            color="#7f7f7f"
        )
    )
    fig1.show()
    fig1.write_image("images/76ers_EFG_17-18.jpeg")
    fig2.show()
    fig2.write_image("images/76ers_TOV_17-18.jpeg")
    fig3.show()
    fig3.write_image("images/76ers_OREB_17-18.jpeg")
    fig4.show()
    fig4.write_image("images/76ers_FTF_17-18.jpeg")


if __name__ == '__main__':
    main()
