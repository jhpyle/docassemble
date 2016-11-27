---
layout: docs
title: Requirements
short_title: Requirements
---

The **docassemble** application is modular.  There is a core [Python]
module, [`docassemble.base`], that parses interviews and determines
what question should be asked next, and there is a separate [Python]
module, [`docassemble.webapp`], that contains the code for the web
application and the [text messaging interface].

For all of the features of **docassemble** to be available, several
other applications need to run concurrently, including:

* A web server;
* A SQL server;
* A [redis] server, multiple databases of which are used;
* A [rabbitmq] server;
* A [Celery] background process;
* A [cron] background process that invokes **docassemble** scripts at
hourly, daily, weekly, and monthly intervals;
* A [syslogng] background process that pushes log file entries to a
  central location;
* A watchdog background process that terminates any web application
processes that are stuck in an infinite loop; and
* A [supervisor] background process that orchestrates these applications.

It is highly recommended, therefore, that you not try to install
**docassemble** manually, but rather that you install [Docker] and run
**docassemble** from its [Docker image].

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

* [DateUtil](https://dateutil.readthedocs.io/en/stable/) - used in the
  demo file to calculate whether an injury took place within the
  statute of limitations period

[YAML]: https://en.wikipedia.org/wiki/YAML
[SQLAlchemy]: http://www.sqlalchemy.org/
[`docassemble.base`]: {{ site.baseurl }}/docs/installation#docassemble.base
[`docassemble.webapp`]: {{ site.baseurl }}/docs/installation.html#docassemble.webapp
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[text messaging interface]: {{ site.baseurl }}/docs/sms.html
[Celery]: http://www.celeryproject.org/
[Docker image]: {{ site.baseurl }}/docs/docker.html
[Docker]: https://www.docker.com/
