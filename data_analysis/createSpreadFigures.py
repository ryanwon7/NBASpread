import matplotlib.pyplot as plt
import mysql.connector
import numpy as np

nbadb = mysql.connector.connect(
    host="localhost",
    user="nbauser",
    passwd="",
    database="nbadatabase"
)
db_cursor = nbadb.cursor()


def standardize(data, ref_data):
    mean = np.mean(ref_data, axis=0)
    stddev = np.std(ref_data, axis=0, ddof=1)
    standardized = (data - mean) / stddev
    return standardized


def retrieve_mysql_data():
    sql_query_string = """SELECT * FROM rollinggamedata;"""
    # sql_query_string = """SELECT * FROM gamedata;"""
    db_cursor.execute(sql_query_string)
    game_data = db_cursor.fetchall()
    return np.asarray(game_data, dtype=np.float32)


def main():
    game_data = retrieve_mysql_data()
    db_cursor.close()
    nbadb.close()

    act = game_data[:, -2]
    veg = game_data[:, -1]
    plt.figure(figsize=(15, 5))
    plt.scatter(veg, act, edgecolor='black', s=20)
    plt.xlabel('Vegas Spread')
    plt.ylabel('Actual Spread')
    plt.title('Comparison of Vegas Spread vs Actual Spread')
    plt.show()


if __name__ == '__main__':
        main()