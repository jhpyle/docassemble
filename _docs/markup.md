---
layout: docs
title: Marking up text
short_title: Markup
---

**docassemble** allows you to format your text using [Markdown] and to
use [Mako] to make your documents "smart."  These [markup] methods
works on `question` text, field labels, `interview help` text, the
content of [documents], and other text elements.

## Markdown

The syntax of [Markdown] is explained well
[elsewhere](http://www.makotemplates.org/).

When generating [documents], **docassemble** uses [Pandoc] to convert
your [Markdown] to PDF, RTF, and HTML.

Here are some examples of things you can do with Markdown:

{% highlight yaml %}
---
question: |
  This is *italic text*.
  This is **bold text**.
  This is __also bold text__.
  This is _underlined text_.

  > This is some block-quoted
  > text

  ### This is a heading

  Here is a bullet list:

  * Apple
  * Peach
  * Pear

  Here is a numbered list:

  1. Nutmeg
  2. Celery
  3. Oregano

  This is equivalent to the above:

  #. Nutmeg
  #. Celery
  #. Oregano

  Here is a [link to a web site](http://google.com).
---
{% endhighlight %}


[documents]: {{ site.baseurl }}/docs/documents.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
[mark up]: https://en.wikipedia.org/wiki/Markup_language
[Pandoc]: http://johnmacfarlane.net/pandoc/
