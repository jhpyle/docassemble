import re

def url_sanitize(url):
    return re.sub(r'\s', ' ', url)
