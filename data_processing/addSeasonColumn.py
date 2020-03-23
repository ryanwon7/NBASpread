import mysql.connector

nbadb = mysql.connector.connect(
    host="localhost",
    user="nbauser",
    passwd="",
    database="nbadatabase"
)
db_cursor = nbadb.cursor()
team_list = ['ATL', 'BOS', 'BRK', 'CHO', 'CHI', 'CLE', 'DAL', 'DEN', 'DET', 'GSW', 'HOU', 'IND', 'LAC', 'LAL', 'MEM',
             'MIA', 'MIL', 'MIN', 'NOP', 'NYK', 'OKC', 'ORL', 'PHI', 'PHO', 'POR', 'SAC', 'SAS', 'TOR', 'UTA', 'WAS']


def retrieve_and_update(season_start, season_end):
    season_string = season_start[2:4] + '-' + season_end[2:4]
    sql_update_string = """UPDATE boxscores SET season=%s WHERE date>=%s AND date<=%s;"""
    db_cursor.execute(sql_update_string, (season_string, season_start, season_end))
    nbadb.commit()


def main():
    start_end_dates = [["2014-10-28", "2015-04-16"], ["2015-10-27", "2016-04-14"], ["2016-10-25", "2017-04-13"], ["2017-10-17", "2018-04-12"]]
    for date_set in start_end_dates:
        retrieve_and_update(date_set[0], date_set[1])

    db_cursor.close()
    nbadb.close()


if __name__ == '__main__':
    main()