import re

__all__ = ['prog_disclose']

def prog_disclose(template, classname=None):
    if classname is None:
        classname = ' bg-light'
    else:
        classname = ' ' + classname.strip()
    the_id = re.sub(r'[^A-Za-z0-9]', '', template.instanceName)
    return """\
<a class="collapsed" data-toggle="collapse" href="#{}" role="button" aria-expanded="false" aria-controls="collapseExample"><span class="pdcaretopen"><i class="fas fa-caret-down"></i></span><span class="pdcaretclosed"><i class="fas fa-caret-right"></i></span> {}</a>
<div class="collapse" id="{}"><div class="card card-body{} pb-1">{}</div></div>\
""".format(the_id, template.subject_as_html(trim=True), the_id, classname, template.content_as_html())
