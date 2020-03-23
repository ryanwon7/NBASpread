import mysql.connector
import sys
from tqdm import tqdm

nbadb = mysql.connector.connect(
    host="localhost",
    user="nbauser",
    passwd="",
    database="nbadatabase"
)
db_cursor = nbadb.cursor()
team_list = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM',
             'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']


def retrieve_stats(team_string, season_start, season_end, location):
    sql_string = """SELECT * FROM boxscores WHERE " + location + "=%s AND date>=%s AND date<=%s;"""
    db_cursor.execute(sql_string, (team_string, season_start, season_end))
    records = db_cursor.fetchall()
    if db_cursor.rowcount != 41:
        print("Error when retrieving {} records for team {}.".format(location, team_string))
        sys.exit()
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


def calculate_season_stats(home_stats, away_stats):
    ppg = (home_stats[0] + away_stats[0])/82
    rpg = (home_stats[1] + away_stats[1])/82
    apg = (home_stats[2] + away_stats[2])/82
    spg = (home_stats[3] + away_stats[3])/82
    bpg = (home_stats[4] + away_stats[4])/82
    topg = (home_stats[5] + away_stats[5])/82
    posspg = (home_stats[6] + away_stats[6])/82
    o_ppg = (home_stats[7] + away_stats[7]) / 82
    o_rpg = (home_stats[8] + away_stats[8]) / 82
    o_apg = (home_stats[9] + away_stats[9]) / 82
    o_spg = (home_stats[10] + away_stats[10]) / 82
    o_bpg = (home_stats[11] + away_stats[11]) / 82
    o_topg = (home_stats[12] + away_stats[12]) / 82
    o_posspg = (home_stats[13] + away_stats[13])/82
    ortg = 100 * (home_stats[0] + away_stats[0]) / (posspg * 82)
    drtg = 100 * (home_stats[7] + away_stats[7]) / (o_posspg * 82)

    stats_unrounded = [ppg, rpg, apg, spg, bpg, posspg, topg, o_ppg, o_rpg, o_apg, o_spg, o_bpg, o_topg, o_posspg, ortg, drtg]
    return [round(num, 4) for num in stats_unrounded]


def split_calculate_season_stats(split_stats):
    ppg = (split_stats[0]) / 41
    rpg = (split_stats[1]) / 41
    apg = (split_stats[2]) / 41
    spg = (split_stats[3]) / 41
    bpg = (split_stats[4]) / 41
    topg = (split_stats[5]) / 41
    posspg = (split_stats[6]) / 41
    o_ppg = (split_stats[7]) / 41
    o_rpg = (split_stats[8]) / 41
    o_apg = (split_stats[9]) / 41
    o_spg = (split_stats[10]) / 41
    o_bpg = (split_stats[11]) / 41
    o_topg = (split_stats[12]) / 41
    o_posspg = (split_stats[13]) / 41
    ortg = 100 * (split_stats[0]) / (posspg * 41)
    drtg = 100 * (split_stats[7]) / (o_posspg * 41)

    stats_unrounded = [ppg, rpg, apg, spg, bpg, posspg, topg, o_ppg, o_rpg, o_apg, o_spg, o_bpg, o_topg, o_posspg, ortg,
                       drtg]
    return [round(num, 4) for num in stats_unrounded]


def commit_sql_insert(season_stats, team, start, end):
    season_string = start[2:4] + '-' + end[2:4]
    sql_string = "INSERT INTO seasonstats VALUES ('" + season_string + "', '" + team + "', " + str(season_stats[0]) + \
                 ", " + str(season_stats[1]) + ", " +  str(season_stats[2]) + ", " + str(season_stats[3]) + ", " + \
                 str(season_stats[4]) + ", " + str(season_stats[5]) + ", " + str(season_stats[6]) + ", " + str(season_stats[7]) \
                 + ", " + str(season_stats[8]) + ", " + str(season_stats[9]) + ", " + str(season_stats[10]) + ", " + str(season_stats[11]) \
                 + ", " + str(season_stats[12]) + ", " + str(season_stats[13]) + ", " + str(season_stats[14]) + ", " + str(season_stats[15]) + ");"
    db_cursor.execute(sql_string)
    nbadb.commit()


def main():
    start_end_dates = [["2014-10-28", "2015-04-16"], ["2015-10-27", "2016-04-14"], ["2016-10-25", "2017-04-13"], ["2017-10-17", "2018-04-12"]]
    for team in tqdm(team_list):
        for date_set in start_end_dates:
            home_stats = retrieve_stats(team, date_set[0], date_set[1], "home")
            away_stats = retrieve_stats(team, date_set[0], date_set[1], "away")
            season_stats = calculate_season_stats(home_stats, away_stats)
            commit_sql_insert(season_stats, team, date_set[0], date_set[1])

    db_cursor.close()
    nbadb.close()


if __name__ == '__main__':
    main()