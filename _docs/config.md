---
layout: docs
title: System-wide Configuration
short_title: Configuration
---

# Location of the configuration file

To run the **docassemble** web application, you tell your web browser
to launch a WSGI file.  The standard WSGI file, `docassemble.wsgi`,
looks like this:

{% highlight python %}
import os, site
import docassemble.webapp.config
docassemble.webapp.config.load(filename="/usr/share/docassemble/config.yml")
os.environ["PYTHONUSERBASE"] = docassemble.webapp.config.daconfig.get('packages', "/usr/share/docassemble/local")
os.environ["XDG_CACHE_HOME"] = docassemble.webapp.config.daconfig.get('packagecache', "/usr/share/docassemble/cache")
site.addusersitepackages("") 
from docassemble.webapp.server import app as application
{% endhighlight %}

The second and third lines load the **docassemble** configuration, and
the last line imports the [Flask] application server.  The
configuration is stored in a [YAML] file, which by default is located
in `/usr/share/docassemble/config.yaml`.  If you wish, you can edit
the WSGI file and tell it to load the configuration from a file in a
different location.  You might want to do this if you have multiple
virtual hosts, each running a different WSGI application on a single
server.

The configuration file needs to be readable and writable by the web
server, but should not be readable by other users of the system
because it may contain sensitive information, such as Google and
Facebook API keys.

# How to edit the configuration file

The configuration file can be edited through the web app by any user
with `admin` privileges.  The editing screen is located on the menu
under "Configuration."  After the configuration [YAML] is saved, the
server is restarted.

You can also edit the configuration file directly on the file system.
You will need to be able to do so if you make edits to the
configuration file through the web application that render the web
application inoperative.

# Configuration default values

{% highlight yaml %}
debug: false
root: /
exitpage: /
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: none
  password: none
  host: none
  port: none
  table_prefix: none
appname: docassemble
brandname: docassemble
uploads: /usr/share/docassemble/files
packages: /usr/share/docassemble/local
packagecache: /usr/share/docassemble/cache
webapp: /usr/share/docassemble/docassemble.wsgi
mail:
  default_sender: None #'"Administrator" <no-reply@example.com>'
  username: none
  password: none
  server: localhost
  port: 25
  use_ssl: false
  use_tls: false
use_progress_bar: false
default_interview: docassemble.demo:data/questions/questions.yml
flask_log: /tmp/flask.log
language: en
locale: US.utf8
default_admin_account:
  nickname: admin
  email: admin@admin.com
  password: password
secretkey: 38ihfiFehfoU34mcq_4clirglw3g4o87
png_resolution: 300
png_screen_resolution: 72
show_login: true
xsendfile: true
{% endhighlight %}

By default, `imagemagick`, `pdftoppm`, `pacpl`, `avconv`, and `oauth` are
undefined.

The key `config_file` does not appear in the configuration file, but
it will be set to the file path for the configuration file.  (The
function `docassemble.webapp.config.load` sets it.)

# Standard configuration directives

## debug

Set this to `true` on development servers.  It enables the following
features:

* The "Source" button in the web app, which shows the [YAML] source code used
  to generate the current question.
* Viewing [LaTeX] and [Markdown] source in document attachments.

## root

This depends on how you configured your web server during [installation]
Set this to `/` if the WSGI application runs from the root of the
domain.  If your server runs from url path `/da/`, set `root` to
`/da/`.  Always use a trailing slash.

## exitpage

This is the default URL to which the user should be directed after
clicking a button that runs an `exit` or `leave` command.  (See
the [Setting Variables] section.)

For example:

{% highlight yaml %}
exitpage: http://example.com/pages/thankyou.html
{% endhighlight %}

## db

This tells the **docassemble** web app where to find the database in
which to store users' answers, login information, and other information.

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: none
  password: none
  host: none
  port: none
  table_prefix: none
{% endhighlight %}

If you are using multiple servers in load-balanced arrangement, you
will want to set this to the central database server.

If you want separatte **docassemble** systems to share the same
database, you can set a `table_prefix`.

## appname and brandname

These are branding names.

The `appname` appears in the web browser tab.  The `brandname` appears
in the navigation bar.

The `brandname` will default to the `appname` if `brandname` is not
specified.

## uploads

This is the directory in which uploaded files are stored.  If you are
using a [multi-server arrangement], this needs to point to a central
network drive.

## packages

This is the directory in which **docassemble** extension packages are
installed.  The PYTHONUSERBASE environment variable is set to this
value and [pip] is called with `--install-option=--user`.  When Python
looks for packages, it will look here.  This is normally `~/.local`,
but it is a good practice to avoid using the web server user's home
directory.

## packagecache

When [pip] runs, it needs a directory in which to cache files.  The
XDG_CACHE_HOME environment variable is set to this value.  This is
normally `~/.cache`, but it is a good practice to avoid using the web
server user's home directory.

On Mac and Windows, make sure that the web server user has a home
directory to which [pip] can write.  (See pip/utils/appdirs.py.)

## webapp

This is the path to the [WSGI] file loaded by the web server.

**docassemble** needs to know this filename because the server needs
to reset itself after an add-on package is updated.  This happens by
"touch"ing (updating the modification time of) the [WSGI] file.

If you are using a [multi-server arrangement], the [WSGI] file needs to be
stored on a central network drive.  When a package is updated, all
servers need to reset, not just the server that happened to process
the package update.

## mail

**docassemble** needs to send e-mail, for example to reset people's
passwords, or to let users of a multi-user interview know that it is
their turn to start answering questions.

The default configuration assumes that a mail server is installed on
the same machine as the web server.

If you are going to send mail, you should at least set the `default_sender`:

{% highlight yaml %}
mail:
  default_sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

## use_progress_bar

This controls whether the web app will show a progress bar at the top
of the screen.  The progress of the bar can be controlled by setting
the `progress` [modifier] on questions.

## default_interview

If no [interview] is specified in the URL when the web browser first
connects to the **docassemble** server, this interview will be used.
The interview needs to be specified in package name:relative file path
format.  For example:

{% highlight yaml %}
default_interview: docassemble.demo:data/questions/questions.yml
{% endhighlight %}

## flask_log

**docassemble** uses the [Flask] web framework.  This is the path to the
[Flask] log file.  Most errors write to the standard web server error
logs, but there are some that will only write to this log file.

## language and locale

These directives set the default [language and locale settings] for **docassemble**.

{% highlight yaml %}
language: en
locale: US.utf8
{% endhighlight %}

## default_admin_account

These settings are only used by the setup script `create_tables.py` in
the `docassemble.webapp` as part of the [installation] of
**docassemble**.  Using the information defined here, that script sets
up a single account in the [user login system] with "admin"
privileges.

{% highlight yaml %}
default_admin_account:
  nickname: admin
  email: admin@admin.com
  password: password
{% endhighlight %}

After `create_tables.py` runs, you can delete the
`default_admin_account` information from the configuration file.

## secretkey

The [Flask] web framework needs a secret key in order to manage
session information and provide [protection] against
[cross-site request forgery].  Set the `secretkey` to a random value
that cannot be guessed.

## png_resolution and png_screen_resolution

When users supply PDF files and **docassemble** includes those files
within a [document], the PDF pages are converted to PNG images in
order to be included within RTF files.  `png_resolution` defines the
dots per inch to be used during this conversion.

PDF files are also converted to PNG for previewing within the web app,
but at a lower resolution.  `png_screen_resolution` defines the dots
per inch to be used for conversion of PDF pages to PNG files for
display in the web browser.

## show_login

If set to false, users will not see a "Sign in" link in the
upper-right-hand corner of the web app.

## xsendfile

If your web server is not configured to support X-SENDFILE headers,
set this to False.  Use of X-SENDFILE is recommended because it allows
the web server, rather than the Python [WSGI] server, to serve files.
This is particularly useful when serving sound files, since the web
browser typically asks for only a range of bytes from the sound file
at a time, and the [WSGI] server does not support the HTTP Range
header.

# Enabling optional features

## Image conversion

If you have ImageMagick and pdftoppm installed on your system, you
need to tell **docassemble** the names of the commands to use.

{% highlight yaml %}
imagemagick: convert
pdftoppm: pdftoppm
{% endhighlight %}

## Sound file conversion

If you have pacpl (the [Perl Audio Converter]) and/or avconv installed
on your system, you need to tell **docassemble** the name of the
commands to use.  If the applications are not installed on your
system, do not include these lines.

{% highlight yaml %}
pacpl: pacpl
avconv: avconv
{% endhighlight %}

If you have ffmpeg instead of avconv, you can do:

{% highlight yaml %}
avconv: ffmpeg
{% endhighlight %}

## Facebook and Google login

If you want to enable logging in with Facebook or with Google, you
will need to tell **docassemble** your oauth keys:

{% highlight yaml %}
oauth:
  facebook:
    enable: true
    id: 423759825983740
    secret: 34993a09909c0909b9000a090d09f099
  google:
    enable: true
    id: 23123018240-32239fj28fj4fuhf394h3984eurhfurh.apps.googleusercontent.com
    secret: DGE34gdgerg3GDG545tgdfRf
{% endhighlight %}

You can disable these login methods by setting `enable` to false.

## Pre-defined variables for all interviews

If you would like to pass variable definitions from the configuration
into the interviews, you can set values of the `initial_dict`:

{% highlight yaml %}
initial_dict:
  host_company: Example, Inc.
  host_url: http://example.com
{% endhighlight %}

Then, in all of the interviews running on the server, you can include
things like:

{% highlight yaml %}
---
sets: splash_screen
question: Welcome to the interview.
subquestion: |
  Web hosting has been graciously provided by ${ host_company }.
---
{% endhighlight %}

## Translations of words and phrases

If your server will offer interviews in languages other than English,
you will want to make sure that built-in words and phrases used within
**docassemble**, such as "Continue" and "Sign in," are translated into
the user's language.

The `words` directive loads one or more [YAML] files in order:

{% highlight yaml %}
words:
  - docassemble.demo:data/translations/words.yml
{% endhighlight %}

Each [YAML] file listed under `words` must be in the form of a
dictionary in which the keys are languages (two-character [ISO-639-1]
codes) and the values are dictionaries with the translations of words
or phrases.

Assuming the following is the content of the
`data/translations/words.yml` file in `docassemble.demo`:

{% highlight yaml %}
es:
  Continue: Continuar
  Help: ¡Ayuda!
{% endhighlight %}

then if the interview calls `set_language('es')` (Spanish) and
**docassemble** code subsequently calls `word('Help')`, the result
will be `¡Ayuda!`.

For more information about how **docassemble** handles different
languages, see the [language and locale settings] section and the
[functions] section (specifically the functions `set_language()` and
`word()`).

## Currency symbol

You can set a default currency symbol if the symbol generated by
the locale is not what you want:

{% highlight yaml %}
currency_symbol: €
{% endhighlight %}

This symbol will be used in the user interface when a field has the
`datatype` of `currency`.  It will also be used in the
`currency_symbol()` function defined in `docassemble.base.util`.

## URL to central file server

If you are using a [multi-server arrangement] and your `uploads` and
`packages` directories are mounted on a network drive, you can reduce
bandwidth on your web server by setting `fileserver` to a URL path to
a dedicated file server:

{% highlight yaml %}
fileserver: files.example.com/da/
{% endhighlight %}

Always use a trailing slash.

If this directive is not set, the value of `root` will be used to
create URLs to uploaded files and static files.

## voicerss

{% highlight yaml %}
voicerss:
  enable: false
  key: 347593849874e7454b9872948a87987d
  languages:
    en:
      GB: en-gb
      US: en-us
    es:
      MX: es-mx
    fr:
      FR: fr-fr
{% endhighlight %}

# Using your own configuration variables

Feel free to use the configuration file to pass your own variables to
your code.  To retrieve their values, use the `get_config()` function from
`docassemble.base.util`:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
code: |
  twilio_api_key = get_config('twilio api key')
{% endhighlight %}

`get_config()` will return `None` if you ask it for a value that does
not exist in the configuration.

The values retrieved by `get_config()` are the result of importing the
[YAML] in the configuration file.  As a result, the values may be
text, lists, or dictionaries, or any nested combination of these
types, depending on what is written in the configuration file.

It is a good practice to use the configuration file to store any
sensitive information, such as passwords and API keys.  This allows
you to share your code on [GitHub] without worrying about redacting it
first.

[Flask]: http://flask.pocoo.org/
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
[LaTeX]: http://www.latex-project.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[installation]: {{ site.baseurl }}/docs/installation.html
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[interview]: {{ site.baseurl }}/docs/interviews.html
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[Flask]: http://flask.pocoo.org/
[language and locale settings]: {{ site.baseurl }}/docs/language.html
[user login system]: {{ site.baseurl }}/docs/users.html
[protection]: http://flask-wtf.readthedocs.org/en/latest/csrf.html
[cross-site request forgery]: https://en.wikipedia.org/wiki/Cross-site_request_forgery
[document]: {{ site.baseurl }}/docs/documents.html
[functions]:  {{ site.baseurl }}/docs/functions.html
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[GitHub]: https://github.com/
[Perl Audio Converter]: http://vorzox.wix.com/pacpl
[pip]: https://en.wikipedia.org/wiki/Pip_%28package_manager%29
[list of language codes]: http://www.voicerss.org/api/documentation.aspx
