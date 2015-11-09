---
layout: docs
title: Documentation of docassemble
short_title: Documentation
---

This documentation is intended more as a reference guide than as a
manual that you have to read before getting started.

The best way to learn about **docassemble** is to study working
examples.  There is a full-featured sample interview linked from the
[demonstration page].  The full source code of that interview is
available on the [demonstration page], and while you are using the
interview you can click "Source" in the navigation bar to toggle
display of the source code for the question and an explanation of the
path **docassemble** took to decide to ask that question.

Another good way to start learning about **docassemble** is to start
creating your own interview.  There is a "Hello, world" [tutorial]
that explains how to create a simple interview.  Once you get that
working, you can experiment with adding more questions to it.

### Table of Contents

<ul>
{% for section in site.data.docs %}
<li>{{ section.title }}</li>
<ul>
{% include docs_section.html items=section.docs %}
</ul>
{% endfor %}
</ul>

[demonstration]: {{ site.baseurl }}/demo.html
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
[demonstration page]: {{ site.baseurl}}/demo.html
[tutorial]: {{ site.baseurl}}/docs/helloworld.html
