---
layout: docs
title: Future development ideas
short_title: Future
---

# Roadmap

Typically, **docassemble** development proceeds based on what features
users request.  If you would like to see a feature in **docassemble**,
ask about it in the #questions channel on [Slack].

Some ideas for future development in 2020 include:

* A React-based front end; and
* Integration with Zapier

# Contributing

If you would like to contribute development resources to the project,
the top priorities are:

* Add-on modules that make it easy to access third party services from
  a docassemble interview.  Examples of such add-on modules include
  the [Docusign integration] and the [Spot API integration].  Ideally
  these add-ons will do more than simply provide a Python interface to
  an API, but will also integrate with **docassemble** objects.
* Add-on modules for electronic case filing in court systems, such as
  the Tyler Technologies e-filing API.
* An add-on module for integration with Ethereum (or something
  similar) for storing persistent data.  It could be useful if data
  gathered during an interview could be stored on the blockchain
  instead of on a **docassemble** server; the end-user would then own
  the data and be able to retrieve it later using a key.
* A multi-mode syntax highlighter for CodeMirror that recognizes YAML
  as YAML but recogizes Python when it is embedded in YAML (typically,
  as the value associated with the key `code` in a dictionary.  The
  highlighter could also colorize Mako templating inside of block
  text.
* A similar multi-mode syntax highlighter for commonly used text editors
* Providing development support to important dependency packages like
  [`python-docx-template`], [`docx`], and [`pattern`].
* A Microsoft Word add-in that provides [Jinja2] linting and/or syntax
  highlighting.

[Jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
[`pattern`]: http://www.clips.ua.ac.be/pages/pattern-en
[`python-docx-template`]: http://docxtpl.readthedocs.io/en/latest/
[`docx`]: https://python-docx.readthedocs.io/en/latest/
[Docusign integration]: https://github.com/radiant-law/docassemble-docusign
[Spot API integration]: https://github.com/jhpyle/docassemble-spot
[Slack]: {{ site.slackurl }}
