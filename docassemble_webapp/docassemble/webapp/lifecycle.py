import re
from flask import session, request, g
from docassemble.base.functions import parse_accept_language
from docassemble.base.language.control import set_language
from docassemble.base.language.words import word
from docassemble.base.thread_context import empty_globals, global_context
from docassemble.webapp.config import DEFAULT_LANGUAGE, DEBUG, daconfig
from docassemble.webapp.interview.helpers import get_part

def init_app(app):
    @app.template_filter('word')
    def word_filter(text):
        return word(str(text))


    @app.context_processor
    def utility_processor():

        def user_designator(the_user):
            if the_user.email:
                return the_user.email
            return re.sub(r'.*\$', '', the_user.social_id)
        if 'language' in session:
            set_language(session['language'])
            lang = session['language']
        elif 'Accept-Language' in request.headers:
            langs = parse_accept_language(request.headers['Accept-Language'])
            if len(langs) > 0:
                set_language(langs[0])
                lang = langs[0]
            else:
                set_language(DEFAULT_LANGUAGE)
                lang = DEFAULT_LANGUAGE
        else:
            set_language(DEFAULT_LANGUAGE)
            lang = DEFAULT_LANGUAGE

        def in_debug():
            return DEBUG
        return {'word': word, 'in_debug': in_debug, 'user_designator': user_designator, 'get_part': get_part, 'current_language': lang, 'color_scheme': session.get('color_scheme', 0)}


    @app.before_request
    def setup_variables():
        # reset_local_variables()
        global_object = empty_globals()
        g.global_context_token = global_context(global_object)
        g.global_context_token.__enter__()


    @app.teardown_request
    def teardown_variables(exc):
        token = getattr(g, 'global_context_token', None)
        if bool(token):
            token.__exit__(exc, exc, exc.__traceback__ if exc else None)


    @app.after_request
    def apply_security_headers(response):
        if request.endpoint is not None and request.endpoint.startswith('api_'):
            session.modified = False
        if app.config['SESSION_COOKIE_SECURE']:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        if 'embed' in g:
            return response
        response.headers["X-Content-Type-Options"] = 'nosniff'
        response.headers["X-XSS-Protection"] = '1'
        if daconfig.get('allow embedding', False) is not True:
            response.headers["X-Frame-Options"] = 'SAMEORIGIN'
            response.headers["Content-Security-Policy"] = "frame-ancestors 'self';"
        elif daconfig.get('cross site domains', []):
            response.headers["Content-Security-Policy"] = "frame-ancestors 'self' " + ' '.join(daconfig['cross site domains']) + ';'
        return response
