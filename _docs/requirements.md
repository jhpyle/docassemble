---
layout: docs
title: Requirements
short_title: Requirements
---

The core **docassemble** module ([`docassemble.base`]) depends on:

* [Mako Templates for Python](http://www.makotemplates.org/) - for
  embedding data and logic in templates for questions and documents
* [PyYAML](http://pyyaml.org/) - for processing [YAML] interview files
* [Python-Markdown](https://pythonhosted.org/Markdown) - for
  converting Markdown to HTML
* [Pillow](https://pypi.python.org/pypi/Pillow/) - for inserting
  images into RTF files
* [PyRTF-ng](https://github.com/nekstrom/pyrtf-ng) - for inserting
  images into RTF files
* [Nodebox English Linguistics library](https://www.nodebox.net/code/index.php/Linguistics) -
  for verb conjugation and pluralization, used in utility functions
  that aid in making question templates as general as possible
* [Pandoc](http://johnmacfarlane.net/pandoc/) - for converting
  documents from Markdown to PDF, RTF, and HTML; depends on
  [LaTeX](http://www.latex-project.org/) for PDF conversion
* [PDFtk](https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/) for
  filling form fields in PDF files
* [httplib2](https://pypi.python.org/pypi/httplib2) - for retrieving
  interviews through HTTP
* [us](https://pypi.python.org/pypi/us) - for utility functions that
  provide a list of U.S. states
* [SmartyPants](https://pypi.python.org/pypi/mdx_smartypants) - for
  converting straight quotes to curly quotes
* [html2text](https://pypi.python.org/pypi/html2text) - for converting
  HTML to text for the plain text part of an e-mail.

The web application ([`docassemble.webapp`]) depends on:

* [Bootstrap](http://getbootstrap.com) (hotlinked) - for the user
  interface
* [Jasny Bootstrap](http://jasny.github.io/bootstrap/) (hotlinked) -
  for styling file uploads
* [jQuery](http://jquery.com/) (hotlinked) - to support Bootstrap
* [jQuery Validation](http://jqueryvalidation.org/) (hotlinked) - for
  validation of form input
* [Flask](http://flask.pocoo.org/) - Python web framework
* [Flask-KVSession](https://pypi.python.org/pypi/Flask-KVSession) -
  for handling Flask sessions
* [Flask-User](https://pythonhosted.org/Flask-User) - for a
  username/password system
* [Flask-Mail](https://pythonhosted.org/Flask-Mail/) - for sending e-mail
* [SQLAlchemy] - used to store data in a
  SQL server
* [WTForms](https://wtforms.readthedocs.org/en/latest/) - required by
  Flask
* [Pygments](http://pygments.org) - for showing [YAML] in a special
  debug mode
* [rauth](https://github.com/litl/rauth) - required by Flask-User
* [simplekv](https://github.com/mbr/simplekv) - required by
  Flask-KVSession
* [PyPDF](https://pypi.python.org/pypi/pyPdf/1.13) - for determining
  number of pages in a PDF upload
* [pdftoppm](http://www.foolabs.com/xpdf/download.html) - for
  converting PDF files into page images
* [ImageMagick](http://http://www.imagemagick.org/) - needed for
  adjusting the rotation of user-supplied JPEGs; the web app will not
  fail if it is missing
* [Perl Audio Converter](http://vorzox.wix.com/pacpl) - for converting
  audio files into the various formats needed for using HTML5 audio
  tag
* [avconv](https://libav.org/avconv.html) - for converting video files
  into the various formats needed for using the HTML video tag
* [pygeocoder](https://bitbucket.org/xster/pygeocoder/wiki/Home) - for
  accessing the Google Geocoder API
* [PostgreSQL](http://www.postgresql.org/) and
  [psycopg2](http://initd.org/psycopg/) - for storing user data; other
  databases compatible with [SQLAlchemy] will also work
* A web server - for serving the web application
* An SMTP server - for allowing users to e-mail documents to themselves
  and to facilitate the username/password system

To run the demo question file (`docassemble.demo`) you will need:

* [DateUtil](https://moin.conectiva.com.br/DateUtil) - used in the
  demo file to calculate whether an injury took place within the
  statute of limitations period

[YAML]: https://en.wikipedia.org/wiki/YAML
[SQLAlchemy]: http://www.sqlalchemy.org/
[`docassemble.base`]: {{ site.baseurl }}/docs/installation#docassemble.base
[`docassemble.webapp`]: {{ site.baseurl }}/docs/installation.html#docassemble.webapp
