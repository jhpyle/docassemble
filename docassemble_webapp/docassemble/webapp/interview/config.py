from markupsafe import Markup
from docassemble.base.parse import set_initial_dict
from docassemble.base.functions import DANav
from docassemble.webapp.config import daconfig, COOKIELESS_SESSIONS, DEFAULT_LANGUAGE

initial_dict = {'_internal': {'session_local': {}, 'device_local': {}, 'user_local': {}, 'dirty': {}, 'progress': 0, 'tracker': 0, 'docvar': {}, 'doc_cache': {}, 'steps': 1, 'steps_offset': 0, 'secret': None, 'informed': {}, 'livehelp': {'availability': 'unavailable', 'mode': 'help', 'roles': [], 'partner_roles': []}, 'answered': set(), 'answers': {}, 'objselections': {}, 'starttime': None, 'modtime': None, 'accesstime': {}, 'tasks': {}, 'gather': [], 'event_stack': {}, 'misc': {}}, 'url_args': {}, 'nav': DANav()}

if 'initial dict' in daconfig:
    initial_dict.update(daconfig['initial dict'])

set_initial_dict(initial_dict)

if COOKIELESS_SESSIONS:
    INDEX_PATH = '/i'
    HTML_INDEX_PATH = '/interview'
else:
    INDEX_PATH = '/interview'
    HTML_INDEX_PATH = '/i'

def get_page_parts():
    the_page_parts = {}
    if 'global footer' in daconfig:
        if isinstance(daconfig['global footer'], dict):
            the_page_parts['global footer'] = {}
            for lang, val in daconfig['global footer'].items():
                the_page_parts['global footer'][lang] = Markup(val)
        else:
            the_page_parts['global footer'] = {'*': Markup(str(daconfig['global footer']))}

    for page_key in ('login page', 'register page', 'interview page', 'start page', 'profile page', 'reset password page', 'forgot password page', 'change password page', '404 page', 'error page'):
        for part_key in ('title', 'tab title', 'extra css', 'extra javascript', 'heading', 'pre', 'submit', 'post', 'footer', 'navigation bar html'):
            key = page_key + ' ' + part_key
            if key in daconfig:
                if isinstance(daconfig[key], dict):
                    the_page_parts[key] = {}
                    for lang, val in daconfig[key].items():
                        the_page_parts[key][lang] = Markup(val)
                else:
                    the_page_parts[key] = {'*': Markup(str(daconfig[key]))}

    the_main_page_parts = {}
    lang_list = set()
    main_page_parts_list = (
        'main page back button label',
        'main page continue button label',
        'main page corner back button label',
        'main page exit label',
        'main page exit link',
        'main page exit url',
        'main page footer',
        'main page help label',
        'main page logo',
        'main page navigation bar html',
        'main page post',
        'main page pre',
        'main page resume button label',
        'main page right',
        'main page short logo',
        'main page short title',
        'main page submit',
        'main page subtitle',
        'main page title url opens in other window',
        'main page title url',
        'main page title',
        'main page under')
    for key in main_page_parts_list:
        if key in daconfig and isinstance(daconfig[key], dict):
            for lang in daconfig[key]:
                lang_list.add(lang)
    lang_list.add(DEFAULT_LANGUAGE)
    lang_list.add('*')
    for lang in lang_list:
        the_main_page_parts[lang] = {}
    for key in main_page_parts_list:
        for lang in lang_list:
            if key in daconfig:
                if isinstance(daconfig[key], dict):
                    the_main_page_parts[lang][key] = daconfig[key].get(lang, daconfig[key].get('*', ''))
                else:
                    the_main_page_parts[lang][key] = daconfig[key]
            else:
                the_main_page_parts[lang][key] = ''
        if the_main_page_parts[DEFAULT_LANGUAGE][key] == '' and the_main_page_parts['*'][key] != '':
            the_main_page_parts[DEFAULT_LANGUAGE][key] = the_main_page_parts['*'][key]
    return (the_page_parts, the_main_page_parts)

(page_parts, main_page_parts) = get_page_parts()
