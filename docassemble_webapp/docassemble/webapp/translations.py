from flask import session, request
from flask_login import current_user
from docassemble.base.functions import set_language, parse_accept_language
from docassemble.base.config import daconfig
DEFAULT_LANGUAGE = daconfig.get('language', 'en')

def setup_translation():
    language = None
    if current_user.is_authenticated:
        language = current_user.language 
    if not language:
        if 'language' in session:
            language = session['language']
        elif 'Accept-Language' in request.headers:
            langs = parse_accept_language(request.headers['Accept-Language'])
            if len(langs) > 0:
                language = langs[0]
            else:
                language = DEFAULT_LANGUAGE
        else:
            language = DEFAULT_LANGUAGE
    session['language'] = language
    set_language(language)

