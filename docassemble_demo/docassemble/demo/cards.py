import re

__all__ = ['card_start', 'card_end']


def card_start(label, color=None, icon=None):
    if color not in ('primary',
                     'secondary',
                     'success',
                     'danger',
                     'warning',
                     'info',
                     'light',
                     'dark',
                     'link'):
        color_text = ''
    else:
        color_text = ' text-bg-' + color
    if icon is None:
        icon_text = ''
    else:
        icon_text = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', str(icon))
        if not re.search(r'^fa[a-z] fa-', icon_text):
            icon_text = 'fas fa-' + icon
        icon_text = '<i class="' + icon_text + '"></i> '
    return f'<div class="card{color_text} mb-3" markdown="span"><div class="card-body" markdown="1"><h2 class="card-title h4" markdown="span">{icon_text}{label}</h2>'


def card_end():
    return '</div></div>'
