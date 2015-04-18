import html2text
from markdown import markdown

the_string = """\
1. This is *cool*.
1. This is the best!
1. I am not an antelope, regardless of what you might say."""

html = markdown(the_string)
print html2text.html2text(html)
