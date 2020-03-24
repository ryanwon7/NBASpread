import mysql.connector
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import neighbors
from sklearn.model_selection import GridSearchCV
import random

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
    random.seed(0)
    game_data = retrieve_mysql_data()
    db_cursor.close()
    nbadb.close()

    np.random.shuffle(game_data)
    X = game_data[:, :-2]
    y = game_data[:, -2]
    vegas_data = game_data[:, -1]
    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.33, shuffle=False)
    X_train = standardize(x_train, x_train)
    X_test = standardize(x_test, x_train)

    model_parameters = {'n_neighbors': list(range(1, 30))}

    knn = neighbors.KNeighborsRegressor()

    model = GridSearchCV(knn, model_parameters, cv=5)
    model.fit(x_train, y_train)
    k = model.best_params_['n_neighbors']
    print("Optimal k value selected by GridSearchCV: {}".format(k))
    knn.set_params(n_neighbors=k)
    knn.fit(X_train, y_train)
    y_exp = knn.predict(X_test)
    avg = np.mean(np.abs(np.round(y_exp * 2) / 2 - y_test))
    print("Average deviation from actual point spread: {:.3f}".format(avg))

    sum_total = 0
    sum_correct = 0
    sum_correct_outcome = 0
    for pred, act, veg in zip(np.nditer(y_exp), np.nditer(y_test), np.nditer(vegas_data)):
        sum_total += 1
        if pred > veg and act > veg:
            sum_correct += 1
        elif pred < veg and act < veg:
            sum_correct += 1
        if pred > 0 and act > 0:
            sum_correct_outcome += 1
        elif pred < 0 and act < 0:
            sum_correct_outcome += 1
    print("Percentage of correct spread predictions: {}".format(sum_correct / sum_total))
    print("Percentage of correct game predictions: {}".format(sum_correct_outcome / sum_total))

if __name__ == '__main__':
    main()
