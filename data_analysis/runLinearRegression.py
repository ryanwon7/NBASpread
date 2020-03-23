import mysql.connector
import numpy as np
from sklearn.model_selection import KFold
from sklearn.linear_model import LinearRegression as linreg
import random

nbadb = mysql.connector.connect(
    host="localhost",
    user="nbauser",
    passwd="",
    database="nbadatabase"
)
db_cursor = nbadb.cursor()


def retrieve_mysql_data():
    sql_query_string = """SELECT * FROM rollinggamedata;"""
    # sql_query_string = """SELECT * FROM gamedata;"""
    db_cursor.execute(sql_query_string)
    game_data = db_cursor.fetchall()
    return np.asarray(game_data, dtype=np.float32)


def standardize_add_bias(data, ref_data):
    mean = np.mean(ref_data, axis=0)
    stddev = np.std(ref_data, axis=0, ddof=1)
    standardized = (data - mean) / stddev
    bias = np.insert(standardized, 0, 1, axis=1)
    return bias


def main():
    game_data = retrieve_mysql_data()
    db_cursor.close()
    nbadb.close()

    sum_correct = 0
    sum_total = 0
    veg_avgs = np.zeros(shape=20)
    avgs = np.zeros(shape=20)

    for i in range(0, 20):
        random.seed(i)
        np.random.shuffle(game_data)
        x_data = game_data[:, :-2]
        y_data = game_data[:, -2]
        vegas_data = game_data[:, -1]
        kf = KFold(n_splits=5, shuffle=False)

        for train_index, test_index in kf.split(x_data):
            train_x_raw, test_x_raw = x_data[train_index], x_data[test_index]
            train_y, test_y = y_data[train_index], y_data[test_index]

            X_train = standardize_add_bias(train_x_raw, train_x_raw)
            X_test = standardize_add_bias(test_x_raw, train_x_raw)

            reg = linreg().fit(X_train, train_y)
            y_exp = X_test.dot(reg.coef_) + reg.intercept_
            for pred, act, veg in zip(np.nditer(y_exp), np.nditer(test_y), np.nditer(vegas_data)):
                sum_total += 1
                if pred > veg and act > veg:
                    sum_correct += 1
                elif pred < veg and act < veg:
                    sum_correct += 1

            veg_avgs[i] = np.mean(np.abs(vegas_data[test_index] - test_y))
            avgs[i] = np.mean(np.abs(np.round(y_exp * 2) / 2 - test_y))

    print("Average deviation from actual point spread: {:.3f}".format(np.mean(avgs)))


if __name__ == '__main__':
    main()
