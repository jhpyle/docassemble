---
layout: docs
title: Documentation of docassemble
short_title: Documentation
---

<ul>
{% for section in site.data.docs %}
<li>{{ section.title }}</li>
<ul>
{% include docs_section.html items=section.docs %}
</ul>
{% endfor %}
</ul>
