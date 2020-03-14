import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import mysql.connector
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from tqdm import tqdm

driver = webdriver.Chrome(executable_path='E:/Downloads/chromedriver_win32/chromedriver.exe')
nbadb = mysql.connector.connect(
    host="localhost",
    user="nbauser",
    passwd="",
    database="nbadatabase"
)
db_cursor = nbadb.cursor()
month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

def generate_date_range(start_date, end_date):
    start = datetime.datetime.strptime(start_date, "%m-%d-%Y")
    end = datetime.datetime.strptime(end_date, "%m-%d-%Y")
    return [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]


def navigate_to_date(date):
    driver.find_element(By.XPATH, '//button[@class="button button--stretch button--hollow-primary"]').click()
    curr_date_list = driver.find_elements(By.XPATH,
                                          '//div[@class="spin-selector__popup spin-selector__popup--open"]//div[@class="spin-selector__value active"]')
    time.sleep(0.1)
    curr_year, curr_month, curr_date = curr_date_list[0].text, curr_date_list[1].text, curr_date_list[2].text
    recurse_to_number(int(date.strftime("%Y")), int(curr_year))
    recurse_to_number(int(date.strftime("%d")), int(curr_date))
    recurse_to_month(int(date.strftime("%m")) - 1, month_list.index(curr_month), month_list)
    driver.find_element(By.XPATH, '//a[@class="button button--block button--solid-primary" and text()="Apply"]').click()


def recurse_to_number(target, current):
    if target == current:
        return
    else:
        next_num = (current + 1) if target > current else (current - 1)
        element = driver.find_element(By.XPATH,
                                      '//div[@class="spin-selector__popup spin-selector__popup--open"]//div[@class="spin-selector__value" and text()=' + str(
                                          next_num) + ']')
        driver.execute_script("arguments[0].click();", element)
        recurse_to_number(target, next_num)


def recurse_to_month(target_month, current_month, months):
    if target_month == current_month:
        return
    else:
        next_num = (current_month + 1) if target_month > current_month else (current_month - 1)
        element = driver.find_element(By.XPATH,
                                      '//div[@class="spin-selector__popup spin-selector__popup--open"]//div[@class="spin-selector__value" and text()="' +
                                      months[next_num].lower().capitalize() + '"]')
        driver.execute_script("arguments[0].click();", element)
        recurse_to_month(target_month, next_num, months)


def adjust_abrev(team_abrev):
    if team_abrev == 'BKN':
        return 'BRK'
    elif team_abrev == 'CHR':
        return 'CHO'
    elif team_abrev == 'GS':
        return 'GSW'
    elif team_abrev == 'NY':
        return 'NYK'
    elif team_abrev == 'SAN':
        return 'SAS'
    else:
        return team_abrev


def scoreboard_loading():
    return len(driver.find_elements(By.XPATH, '//div[@class="scoreboard loading"]')) != 0


def no_games_played():
    return len(driver.find_elements(By.XPATH, '//div[@class="no-matchups"]')) != 0


def parse_betting_data():
    soup_parse = BeautifulSoup(driver.page_source, 'html.parser')
    box_scores = soup_parse.find_all('div', class_='scores-matchup__container')
    return_data = []
    for box_score in box_scores:
        away_spread = box_score.find('div', class_='graph--duel__header--middle graph--duel__header--middle-multiple-values').contents[0].text
        home_spread = box_score.find('div', class_='graph--duel__header--middle graph--duel__header--middle-multiple-values').contents[1].text
        away_team = adjust_abrev(box_score.find_all('div', class_='graph--duel__header-label')[0].text)
        home_team = adjust_abrev(box_score.find_all('div', class_='graph--duel__header-label')[1].text)
        over_under = box_score.find_all('div', class_='graph--duel__header-value')[5].text
        if home_spread == 'Ev':
            home_spread = '0'
            away_spread = '0'
        if home_spread == '':
            home_spread = '0'
            away_spread = '0'
            over_under = '0'
        return_data.append([home_team, away_team, home_spread, away_spread, over_under])
    return return_data


def sql_insert(date, bet_datalist):
    sql_string = "INSERT INTO bettingdata VALUES"
    formatted_date = date.strftime("%Y-%m-%d")
    for i, bet_data in enumerate(bet_datalist):
        if i:
            sql_string += ','
        value_string = " ('" + formatted_date + "', '" + bet_data[0] + "', '" + bet_data[1] + "', " + bet_data[2] + \
                       ", " + bet_data[3] + ", " + bet_data[4] + ")"
        sql_string += value_string
    sql_string += ';'
    db_cursor.execute(sql_string)
    nbadb.commit()


def main():
    # start_date, end_date = "10-28-2014", "04-16-2015"  # 2014-2015 NBA season
    # start_date, end_date = "10-27-2015", "04-14-2016"  # 2015-2016 NBA season
    # start_date, end_date = "10-25-2016", "04-13-2017"  # 2016-2017 NBA season
    start_date, end_date = "10-17-2017", "04-12-2018"  # 2017-2018 NBA season
    date_generated = generate_date_range(start_date, end_date)
    driver.get("https://www.oddsshark.com/nba/scores")

    for date in tqdm(date_generated):
        navigate_to_date(date)
        WebDriverWait(driver, 1).until(ec.visibility_of_element_located((By.XPATH, "//div[@id='oslive-scoreboard' and @class='scoreboard loading']")))
        WebDriverWait(driver, 10).until(ec.visibility_of_element_located((By.XPATH, "//div[@id='oslive-scoreboard' and @class='scoreboard']")))
        if no_games_played():
            continue
        bet_data = parse_betting_data()
        sql_insert(date, bet_data)

    print('\nCompleted scraping all games from the season. Closing SQL and Selenium connections.')
    db_cursor.close()
    nbadb.close()
    driver.close()


if __name__ == '__main__':
    main()
