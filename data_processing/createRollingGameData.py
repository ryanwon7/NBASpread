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
        home_season_stats, away_season_stats = retrieve_season_info(game[0], game[3], game[2], game[38])
        home_recent_stats = calculate_recent_four_factors(game[0], game[2], game[38])
        away_recent_stats = calculate_recent_four_factors(game[3], game[2], game[38])
        betting_data = retrieve_betting_data(game[0], game[3], game[2])
        sql_insert_string = """INSERT INTO rollinggamedata VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
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


def retrieve_season_info(home_team, away_team, game_date, season):
    home_stats = retrieve_stats(home_team, game_date, season, "home")
    away_stats = retrieve_stats(away_team, game_date, season, "away")
    return home_stats, away_stats


def retrieve_stats(team, game_date, season, location):
    sql_string = """SELECT * FROM boxscores WHERE (home=%s OR away =%s) AND date<%s AND season=%s;"""
    db_cursor.execute(sql_string, (team, team, game_date, season))
    records = db_cursor.fetchall()
    if len(records) < 5:
        sql_query_string = """SELECT * FROM seasonstats WHERE team=%s AND season=%s;"""
        db_cursor.execute(sql_query_string, (team, season))
        team_stats = db_cursor.fetchall()
        return team_stats[0]
    else:
        teams_home_stats = retrieve_splits_stats(team, game_date, season, "home")
        teams_away_stats = retrieve_splits_stats(team, game_date, season,  "away")
        season_stats = calculate_season_stats(teams_home_stats, teams_away_stats, len(records))
        return season_stats


def calculate_season_stats(home_stats, away_stats, gp):
    ppg = (home_stats[0] + away_stats[0])/gp
    rpg = (home_stats[1] + away_stats[1])/gp
    apg = (home_stats[2] + away_stats[2])/gp
    spg = (home_stats[3] + away_stats[3])/gp
    bpg = (home_stats[4] + away_stats[4])/gp
    topg = (home_stats[5] + away_stats[5])/gp
    posspg = (home_stats[6] + away_stats[6])/gp
    o_ppg = (home_stats[7] + away_stats[7]) / gp
    o_rpg = (home_stats[8] + away_stats[8]) / gp
    o_apg = (home_stats[9] + away_stats[9]) / gp
    o_spg = (home_stats[10] + away_stats[10]) / gp
    o_bpg = (home_stats[11] + away_stats[11]) / gp
    o_topg = (home_stats[12] + away_stats[12]) / gp
    o_posspg = (home_stats[13] + away_stats[13])/gp
    ortg = 100 * (home_stats[0] + away_stats[0]) / (posspg * gp)
    drtg = 100 * (home_stats[7] + away_stats[7]) / (o_posspg * gp)

    stats_unrounded = [ppg, rpg, apg, spg, bpg, posspg, topg, o_ppg, o_rpg, o_apg, o_spg, o_bpg, o_topg, o_posspg, ortg, drtg]
    rounded_stats = [round(num, 4) for num in stats_unrounded]
    rounded_stats.insert(0, 'team')
    rounded_stats.insert(0, 'season')
    return rounded_stats

def retrieve_splits_stats(team_string, game_date, season, location):
    sql_string = "SELECT * FROM boxscores WHERE " + location + "='" + team_string +"' AND date<'" + game_date + \
                 "' AND season='" + season +"';"
    db_cursor.execute(sql_string)
    records = db_cursor.fetchall()
    if location == 'home':
        mod1, mod2 = 0, 0
    else:
        mod1, mod2 = 1, 16

    teampts = sum(game[4 + mod1] for game in records)
    teamreb = sum(game[16 + mod2] for game in records)
    teamast = sum(game[17 + mod2] for game in records)
    teamstl = sum(game[18 + mod2] for game in records)
    teamblk = sum(game[19 + mod2] for game in records)
    teamto = sum(game[20 + mod2] for game in records)
    teamfga = sum(game[7 + mod2] for game in records)
    teamfta = sum(game[13 + mod2] for game in records)
    teamoreb = sum(game[15 + mod2] for game in records)
    opppts = sum(game[5 - mod1] for game in records)
    oppreb = sum(game[32 - mod2] for game in records)
    oppast = sum(game[33 - mod2] for game in records)
    oppstl = sum(game[34 - mod2] for game in records)
    oppblk = sum(game[35 - mod2] for game in records)
    oppto = sum(game[36 - mod2] for game in records)
    oppfga = sum(game[23 - mod2] for game in records)
    oppfta = sum(game[29 - mod2] for game in records)
    opporeb = sum(game[31 - mod2] for game in records)
    teamposs = 0.96 * (teamfga + teamto + 0.44*teamfta - teamoreb)
    oppposs = 0.96 * (oppfga + oppto + 0.44*oppfta - opporeb)

    return [teampts, teamreb, teamast, teamstl, teamblk, teamto, teamposs, opppts, oppreb, oppast, oppstl, oppblk, oppto, oppposs]


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