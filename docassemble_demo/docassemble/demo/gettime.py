import requests

def get_time():
    r = requests.get('http://worldclockapi.com/api/json/est/now')
    if r.status_code != 200:
        raise Exception("Could not obtain the time")
    return r.json()['currentDateTime']
