import requests



headers = {
    'x-rapidapi-host': "api-nba-v1.p.rapidapi.com",
    'x-rapidapi-key': "de511463c3mshfb2c1db7c6b6418p13b349jsn58d54e265fd8"
    }



for i in range(1,5):
    url = "https://api-nba-v1.p.rapidapi.com/statistics/games/gameId/" + str(i)
    response = requests.request("GET", url, headers=headers)
    print(response.text)