---
layout: docs
title: Documentation of docassemble
short_title: Documentation
order: 20
---

This documentation is intended more as a reference guide than as a
manual that you have to read before getting started.

The best way to learn about **docassemble** is to start creating your
own interview.  There is a "Hello, world" [tutorial] that explains how
to create a simple interview.  Once you get that working, you can
experiment with adding more questions to it.

The best way to learn about more advanced **docassemble** features is
to study working examples.  The sections of this documentation site
contain a number of side-by-side examples comparing source code to
screenshots.  You can click on the screenshots to run the interviews.
The code next to the screenshots is often only an excerpt of the full
interview.  To see the full source code of the interview, hover over
the source code and click the button that appears in the lower right
corner.  In addition, while you are developing interviews in the
[Playground], you can browse working examples of many of
**docassemble**'s features.

There is also a full-featured sample interview linked from the
[demonstration page].  The full source code of that interview is
available on the [demonstration page].  While you are using the
interview you can click "Source" in the navigation bar to toggle
display of the source code for the question and an explanation of the
path **docassemble** took to decide to ask that question.

## Table of Contents

For a narrative version of the sections of the documentation, see the [Overview].

<ul class="interiortoc">
{% for section in site.data.docs %}
<li>{{ section.title }}</li>
<ul>
{% include docs_section.html items=section.docs %}
</ul>
{% endfor %}
</ul>

[Overview]: {{ site.baseurl }}/docs/overview.html
[demonstration]: {{ site.baseurl }}/demo.html
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
[demonstration page]: {{ site.baseurl}}/demo.html
[tutorial]: {{ site.baseurl}}/docs/helloworld.html
[Playground]: {{ site.baseurl}}/docs/playground.html
