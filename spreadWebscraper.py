import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def generate_date_range(start_date, end_date):
    start = datetime.datetime.strptime(start_date, "%m-%d-%Y")
    end = datetime.datetime.strptime(end_date, "%m-%d-%Y")
    return [start + datetime.timedelta(days=x) for x in range(0, (end - start).days)]


def navigate_to_date(driver, date):
    driver.find_element(By.XPATH, '//button[@class="button button--stretch button--hollow-primary"]').click()
    curr_date_list = driver.find_elements(By.XPATH, '//div[@class="spin-selector__popup spin-selector__popup--open"]//div[@class="spin-selector__value active"]')
    curr_year, curr_month, curr_date = curr_date_list[0].text, curr_date_list[1].text, curr_date_list[2].text
    month_list = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    recurse_to_number(driver, int(date.strftime("%Y")), int(curr_year))
    recurse_to_month(driver, int(date.strftime("%m"))-1, month_list.index(curr_month), month_list)
    recurse_to_number(driver, int(date.strftime("%d")), int(curr_date))
    driver.find_element(By.XPATH, '//a[@class="button button--block button--solid-primary" and text()="Apply"]').click()


def recurse_to_number(driver, target, current):
    if target == current:
        return
    else:
        next_num = (current + 1) if target > current else (current - 1)
        element = driver.find_element(By.XPATH, '//div[@class="spin-selector__popup spin-selector__popup--open"]//div[@class="spin-selector__value" and text()=' + str(next_num) + ']')
        driver.execute_script("arguments[0].click();", element)
        recurse_to_number(driver, target, next_num)


def recurse_to_month(driver, target_month, current_month, months):
    if target_month == current_month:
        return
    else:
        next_num = (current_month + 1) if target_month > current_month else (current_month - 1)
        element = driver.find_element(By.XPATH, '//div[@class="spin-selector__popup spin-selector__popup--open"]//div[@class="spin-selector__value" and text()="' + months[next_num].lower().capitalize() + '"]')
        driver.execute_script("arguments[0].click();", element)
        recurse_to_month(driver, target_month, next_num, months)


def scoreboard_loading(driver):
    return len(driver.find_elements(By.XPATH, '//div[@class="scoreboard loading"]')) != 0


def no_games_played(driver):
    return len(driver.find_elements(By.XPATH, '//div[@class="no-matchups"]')) != 0


def main():
    start_date = "1-28-2020"
    end_date = "03-14-2020"
    date_generated = generate_date_range(start_date, end_date)

    driver = webdriver.Chrome(executable_path='E:/Downloads/chromedriver_win32/chromedriver.exe')
    driver.get("https://www.oddsshark.com/nba/scores")
    initial_load = True

    for date in date_generated:
        while scoreboard_loading(driver):
            time.sleep(0.05)
        navigate_to_date(driver, date)
        if no_games_played(driver):
            continue
        soup_parse = BeautifulSoup(driver.page_source, 'html.parser')
        box_scores = soup_parse.find_all('div', class_='scores-matchup__container')
        for box_score in box_scores:
            away_spread = box_score.find('div', class_='graph--duel__header--middle graph--duel__header--middle-multiple-values').contents[0].text
            home_spread = box_score.find('div', class_='graph--duel__header--middle graph--duel__header--middle-multiple-values').contents[1].text
            away_team = box_score.find_all('div', class_='graph--duel__header-label')[0].text
            home_team = box_score.find_all('div', class_='graph--duel__header-label')[1].text
            over_under = box_score.find_all('div', class_='graph--duel__header-value')[5].text
            print('(Away) {} spread: {}'.format(away_team, away_spread))
            print('(Home) {} spread: {}'.format(home_team, home_spread))
            print('Over/Under: {}\n'.format(over_under))
        print(date.strftime("%m-%d-%Y"))


if __name__ == '__main__':
    main()
