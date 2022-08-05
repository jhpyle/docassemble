import re
from docassemble.base.util import log, get_config
from googleapiclient.discovery import build

__all__ = ['translate_phrase']


def translate_phrase(phrase, source_language, target_language):
    try:
        api_key = get_config('google')['api key']
    except:
        log("Could not translate because Google API key was not in Configuration.")
        return phrase
    try:
        service = build('translate', 'v2',
                        developerKey=api_key)
        resp = service.translations().list(
            source=source_language,
            target=target_language,
            q=[phrase]
        ).execute()
        return re.sub(r'&#39;', r"'", str(resp['translations'][0]['translatedText']))
    except Exception as err:
        log("translation failed: " + err.__class__.__name__ + ": " + str(err))
        return phrase
