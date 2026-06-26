import copy
from flask_login import current_user
from docassemble.base.interview_cache import get_interview
from docassemble.base.language.words import word
from docassemble.webapp.config import daconfig
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage

@hookimpl(specname='server_interview_menu')
def interview_menu(absolute_urls, start_new, tag):
    interview_info = []
    for key, yaml_filename in sorted(daconfig['dispatch'].items()):
        try:
            interview = get_interview(yaml_filename)
            if interview.is_unlisted():
                continue
            if current_user.is_anonymous:
                if not interview.allowed_to_see_listed(is_anonymous=True):
                    continue
            else:
                if not interview.allowed_to_see_listed(has_roles=[role.name for role in current_user.roles]):
                    continue
            if interview.source is None:
                package = None
            else:
                package = interview.source.get_package()
            titles = interview.get_title({'_internal': {}})
            tags = interview.get_tags({'_internal': {}})
            metadata = copy.deepcopy(interview.consolidated_metadata)
            if 'tags' in metadata:
                del metadata['tags']
            interview_title = titles.get('full', titles.get('short', word('Untitled')))
            subtitle = titles.get('sub', None)
            status_class = None
            subtitle_class = None
        except:
            interview_title = yaml_filename
            tags = set()
            metadata = {}
            package = None
            subtitle = None
            status_class = 'dainterviewhaserror'
            subtitle_class = 'dainvisible'
            logmessage("interview_dispatch: unable to load interview file " + yaml_filename)
        if tag is not None and tag not in tags:
            continue
        if absolute_urls:
            if start_new:
                url = url_for('interview.run_interview', dispatch=key, _external=True, reset='1')
            else:
                url = url_for('interview.redirect_to_interview', dispatch=key, _external=True)
        else:
            if start_new:
                url = url_for('interview.run_interview', dispatch=key, reset='1')
            else:
                url = url_for('interview.redirect_to_interview', dispatch=key)
        interview_info.append({'link': url, 'title': interview_title, 'status_class': status_class, 'subtitle': subtitle, 'subtitle_class': subtitle_class, 'filename': yaml_filename, 'package': package, 'tags': sorted(tags), 'metadata': metadata})
    return interview_info
