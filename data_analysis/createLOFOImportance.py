import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_selection import f_regression, mutual_info_regression
from numpy import genfromtxt
from sklearn import preprocessing

categories = ['ht_ppg', 'ht_rpg', 'ht_apg', 'ht_spg', 'ht_bpg', 'ht_topg', 'ho_ppg', 'ho_rpg', 'ho_apg', 'ho_spg',
              'ho_bpg', 'ho_topg','h_ortg', 'h_drtg', 'h_efg', 'h_tov', 'h_oreb', 'h_ftf', 'at_ppg', 'at_rpg', 'at_apg',
              'at_spg', 'at_bpg', 'at_topg', 'ao_ppg',  'ao_rpg', 'ao_apg', 'ao_spg', 'ao_bpg', 'ao_topg', 'a_ortg',
              'a_drtg', 'a_efg', 'a_tov', 'a_reb', 'a_ftf']
my_data = genfromtxt('export_rollinggamedata.csv', delimiter=',')
full_data = np.delete(my_data, (0), axis=0)
X = preprocessing.scale(full_data[:, :-1])
y = full_data[:, -1]

f_test, _ = f_regression(X, y)
f_test /= np.max(f_test)

mi = mutual_info_regression(X, y)
mi /= np.max(mi)


plt.figure(figsize=(15, 5))
for i in range(len(categories)):
    plt.subplot(6, 6, i + 1)
    plt.scatter(X[:, i], y, edgecolor='black', s=20)
    plt.xlabel("{}".format(categories[i]), fontsize=10)
    if i % 6 == 0:
        plt.ylabel("$y$", fontsize=14)

    print("{} === F-test={:.2f}, MI={:.2f}".format(categories[i], f_test[i], mi[i]))
    plt.title("F-test={:.2f}, MI={:.2f}".format(f_test[i], mi[i]),
              fontsize=12)
plt.show()
'''
plt.bar(np.arange(4), mi[14:18], align='center', alpha=0.5)
plt.xticks(np.arange(4), categories[14:18], fontsize=18)
plt.ylabel('Metric %', fontsize=26)
plt.title('Mutual Info Metrics: Home Four Factors Statistics', fontsize=36)

plt.show()
'''