---
layout: docs
title: Requirements
short_title: Requirements
---

The docassemble module depends on:

* [Mako Templates for Python](http://www.makotemplates.org/)
* [PyYAML](http://pyyaml.org/)
* [Python-Markdown](https://pythonhosted.org/Markdown)
* [html2text](https://github.com/aaronsw/html2text)
* [Nodebox English Linguistics library](https://www.nodebox.net/code/index.php/Linguistics)
* [Pandoc](http://johnmacfarlane.net/pandoc/), which depends on [LaTeX](http://www.latex-project.org/) if you want to convert to PDF
* [httplib2](https://pypi.python.org/pypi/httplib2)
* [us](https://pypi.python.org/pypi/us)
* [SmartyPants](https://pypi.python.org/pypi/mdx_smartypants)
* [PyRTF-ng](https://github.com/nekstrom/pyrtf-ng)

The web application depends on:

* [Flask](http://flask.pocoo.org/)
* [Bootstrap](http://getbootstrap.com) (hotlinked)
* [Jasny Bootstrap](http://jasny.github.io/bootstrap/) (hotlinked)
* [jQuery](http://jquery.com/) (hotlinked)
* [jQuery Validation](http://jqueryvalidation.org/) (hotlinked)
* [PostgreSQL](http://www.postgresql.org/) (other databases compatible with [SQLAlchemy](http://www.sqlalchemy.org/) would probably work as well)
* [psycopg2](http://initd.org/psycopg/)
* [WTForms](https://wtforms.readthedocs.org/en/latest/)
* [rauth](https://github.com/litl/rauth)
* [simplekv](https://github.com/mbr/simplekv)
* [Flask-KVSession](https://pypi.python.org/pypi/Flask-KVSession)
* [Flask-User](https://pythonhosted.org/Flask-User)
* [Pillow](https://pypi.python.org/pypi/Pillow/)
* [PyPDF](https://pypi.python.org/pypi/pyPdf/1.13)
* [pdftoppm](http://www.foolabs.com/xpdf/download.html)
* [ImageMagick](http://http://www.imagemagick.org/) (This is needed for adjusting the rotation of user-supplied JPEGs.  The web app will not fail if it is missing.)
* A web server
* A mail server

To run the demo question file you will need:

* [DateUtil](https://moin.conectiva.com.br/DateUtil)
