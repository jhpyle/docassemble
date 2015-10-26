---
layout: docs
title: Documentation of docassemble
short_title: Documentation
---

The **docassemble** documentation is a reference guide to all the
features of **docassemble**.

Another way to figure out how to do things in **docassemble** is to go
through the [demonstration] and click "Script" to see the [YAML]
source of each question.  The [YAML] code that generates the
[demonstration] interview is annotated with explanatory comments.

<ul>
{% for section in site.data.docs %}
<li>{{ section.title }}</li>
<ul>
{% include docs_section.html items=section.docs %}
</ul>
{% endfor %}
</ul>

[demonstration]: {{ site.baseurl }}/demo.html
