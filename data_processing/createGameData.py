import mysql.connector
from tqdm import tqdm


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


def create_training_data():
    sql_query_string = """SELECT * FROM boxscores;"""
    db_cursor.execute(sql_query_string)
    boxscores = db_cursor.fetchall()

    for game in tqdm(boxscores):
        home_season_stats, away_season_stats = retrieve_season_info(game[0], game[3], game[38])
        home_recent_stats = calculate_recent_four_factors(game[0], game[2], game[38])
        away_recent_stats = calculate_recent_four_factors(game[3], game[2], game[38])
        betting_data = retrieve_betting_data(game[0], game[3], game[2])
        sql_insert_string = """INSERT INTO gamedata VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s); """
        db_cursor.execute(sql_insert_string, (home_season_stats[2], home_season_stats[3],
                                              home_season_stats[4], home_season_stats[5], home_season_stats[6],
                                              home_season_stats[8], home_season_stats[9], home_season_stats[10],
                                              home_season_stats[11], home_season_stats[12], home_season_stats[13],
                                              home_season_stats[14], home_season_stats[16], home_season_stats[17],
                                              home_recent_stats[0], home_recent_stats[1], home_recent_stats[2],
                                              home_recent_stats[3], away_season_stats[2], away_season_stats[3],
                                              away_season_stats[4], away_season_stats[5], away_season_stats[6],
                                              away_season_stats[8], away_season_stats[9], away_season_stats[10],
                                              away_season_stats[11], away_season_stats[12], away_season_stats[13],
                                              away_season_stats[14], away_season_stats[16], away_season_stats[17],
                                              away_recent_stats[0], away_recent_stats[1], away_recent_stats[2],
                                              away_recent_stats[3], betting_data, game[5]-game[4]))
        nbadb.commit()


def retrieve_season_info(home_team, away_team, season):
    sql_query_string = """SELECT * FROM seasonstats WHERE team=%s AND season=%s;"""
    db_cursor.execute(sql_query_string, (home_team, season))
    home_stats = db_cursor.fetchall()
    db_cursor.execute(sql_query_string, (away_team, season))
    away_stats = db_cursor.fetchall()
    return home_stats[0], away_stats[0]


def calculate_recent_four_factors(team, game_date, season):
    sql_query_string = """SELECT * FROM boxscores WHERE (home=%s OR away =%s) AND date<%s AND season=%s ORDER BY date DESC;"""
    db_cursor.execute(sql_query_string, (team, team, game_date, season))
    game_stats = db_cursor.fetchall()
    if len(game_stats) < 5:
        sql_query_string = """SELECT * FROM boxscores WHERE (home=%s OR away =%s) AND season=%s;"""
        db_cursor.execute(sql_query_string, (team, team, season))
        game_stats = db_cursor.fetchall()
    else:
        game_stats = game_stats[:5]
    sum_fgm, sum_fga = sum(row[6] for row in game_stats), sum(row[7] for row in game_stats)
    sum_ftm, sum_fta = sum(row[12] for row in game_stats), sum(row[13] for row in game_stats)
    sum_3pm = sum(row[9] for row in game_stats)
    sum_to = sum(row[20] for row in game_stats)
    sum_oreb, sum_oppreb, sum_opporeb = sum(row[15] for row in game_stats), sum(row[32] for row in game_stats), sum(row[31] for row in game_stats)

    efg = effective_field_goal_pct(sum_fgm, sum_3pm, sum_fga)
    tov = turnover_pct(sum_fga, sum_fta, sum_to)
    oreb = offensive_rebound_percentage(sum_oreb, sum_oppreb, sum_opporeb)
    ftf = free_throw_factor(sum_ftm, sum_fga)

    return [efg, tov, oreb, ftf]


def retrieve_betting_data(home_team, away_team, game_date):
    sql_query_string = """SELECT * FROM bettingdata WHERE home=%s AND away=%s AND date=%s;"""
    db_cursor.execute(sql_query_string, (home_team, away_team, game_date))
    betting_data = db_cursor.fetchall()
    return betting_data[0][3]


def main():
    create_training_data()

    db_cursor.close()
    nbadb.close()


if __name__ == '__main__':
    main()