# do not pre-load
import random
import re
import string

__all__ = ['start_accordion', 'next_accordion', 'end_accordion']

r = random.SystemRandom()


def _get_section_id(section):
    section_id = re.sub(r'[^a-z0-9]+', '-', section.lower())
    if len(section_id) > 0:
        section_id += '-'
    section_id += (''.join(r.choice(string.ascii_lowercase) for i in range(5)))
    return section_id


def _header(section_id):
    return f"""\
<div class="row mb-3">
  <div class="col">
    <div class="accordion" id="{section_id}">
    """


def _section_start(section_id, section, showing):
    if showing:
        show = ' show'
        expanded = 'true'
        collapsed = ''
    else:
        show = ''
        expanded = 'false'
        collapsed = ' collapsed'
    return f"""\
      <div class="accordion-item">
        <h2 class="accordion-header">
          <button class="accordion-button{collapsed}" type="button" data-bs-toggle="collapse" data-bs-target="#collapse-{section_id}" aria-expanded="{expanded}" aria-controls="collapse-{section_id}">{section}</button>
        </h2>
        <div id="collapse-{section_id}" class="accordion-collapse collapse{show}" data-bs-parent="#{section_id}">
          <div class="accordion-body">
"""


def _section_end():
    return """\
          </div>
        </div>
      </div>
"""


def _footer():
    return """\
    </div>
  </div>
</div>
    """


def start_accordion(section, showing=False):
    """Returns HTML for the start of a series of accordion
    sections. The end_accordion() function must be called at some
    point later in the page, or else the HTML will be corrupted. If
    you want the section to be open when the page loads, set
    showing=True.

    """
    section_id = _get_section_id(section)
    return _header(section_id) + _section_start(section_id, section, showing)


def next_accordion(section, showing=False):
    """Returns HTML for ending a previous according section and
    starting a new accordion section. Can only be used after
    start_accordion(). If you want the section to be open when the
    page loads, set showing=True.

    """
    section_id = _get_section_id(section)
    return _section_end() + _section_start(section_id, section, showing)


def end_accordion():
    """Returns HTML for ending a series of accordion sections. Can
    only be used after next_accordion or start_accordion().

    """
    return _section_end() + _footer()
