# do not pre-load

__all__ = ['prog_disclose']


def prog_disclose(template, classname=None):
    if classname is None:
        classname = ' bg-secondary-subtle'
    else:
        classname = ' ' + classname.strip()
    return f"""\
<details class="mb-2">
  <summary class="text-primary">
    {template.subject_as_html(trim=True)}
  </summary>
  <div class="card card-body{classname} pb-0">
    {template.content_as_html()}
  </div>
</details>
"""
