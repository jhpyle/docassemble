# do not pre-load
import requests


def get_time():
    r = requests.get('http://worldclockapi.com/api/json/est/now', timeout=60)
    if r.status_code != 200:
        raise RuntimeError("Could not obtain the time")
    return r.json()['currentDateTime']
