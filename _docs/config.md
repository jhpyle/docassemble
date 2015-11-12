---
layout: docs
title: System-wide Configuration
short_title: Configuration
---

## Location of the configuration file

To run the **docassemble** web application, you tell your web browser
to launch a WSGI file.  The standard WSGI file, `docassemble.wsgi`,
looks like this:

{% highlight python %}
import docassemble.webapp.config
docassemble.webapp.config.load(filename="/etc/docassemble/config.yml")
from docassemble.webapp.server import app as application
{% endhighlight %}

The first two lines load the **docassemble** configuration, and the
third imports the [Flask] application server.  The configuration is
stored in a [YAML] file, which by default is located in
`/etc/docassemble/config.yaml`.  If you wish, you can edit the WSGI
file and tell it to load the configuration from a file in a different
location.  You might want to do this if you have multiple virtual
hosts, each running a different WSGI application on a single server.

The configuration file needs to be readable by the web server, but
should not be readable by other users of the system because it may
contain sensitive information, such as Google and Facebook API keys.

## Configuration default values

{% highlight yaml %}
debug: false
root: /demo
exitpage: /
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: none
  password: none
  host: none
  port: none
appname: docassemble
brandname: docassemble
uploads: /usr/share/docassemble/files
webapp: /var/lib/docassemble/docassemble.wsgi
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
{% endhighlight %}

By default, `imagemagick`, `pdftoppm_command`, and `oauth` are
undefined.

## Standard configuration directives

### debug

Set this to `true` on development servers.  It enables the following
features:

* The "Source" button in the web app, which shows the [YAML] source code used
  to generate the current question.
* Viewing [LaTeX] and [Markdown] source in document attachments.

### root

This depends on how you configured your web server during [installation]
Set this to `null` if the WSGI application runs from the root of the
URL.  If your server runs from url path `/da`, set `root` to `/da`.

### exitpage

This is the default URL to which the user should be directed after
clicking a button that runs an `exit` or `leave` command.  (See
the [Setting Variables] section.)

For example:

{% highlight yaml %}
exitpage: http://example.com/pages/thankyou.html
{% endhighlight %}

### db

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
{% endhighlight %}

If you are using multiple servers in load-balanced arrangement, you
will want to set this to the central database server.

### appname and brandname

These are branding names.

The `appname` appears in the web browser tab.  The `brandname` appears
in the navigation bar.

The `brandname` will default to the `appname` if `brandname` is not
specified.

### uploads

This is the directory in which uploaded files are stored.  If you are
using a [multi-server arrangement], this needs to point to a central
network drive.

### webapp

This is the path to the [WSGI] file loaded by the web server.

**docassemble** needs to know this filename because the server needs
to reset itself after an add-on package is updated.  This happens by
"touch"ing (updating the modification time of) the [WSGI] file.

If you are using a [multi-server arrangement], the [WSGI] file needs to be
stored on a central network drive.  When a package is updated, all
servers need to reset, not just the server that happened to process
the package update.

### mail

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

### use_progress_bar

This controls whether the web app will show a progress bar at the top
of the screen.  The progress of the bar can be controlled by setting
the `progress` [modifier] on questions.

### default_interview

If no [interview] is specified in the URL when the web browser first
connects to the **docassemble** server, this interview will be used.
The interview needs to be specified in package name:relative file path
format.  For example:

{% highlight yaml %}
default_interview: docassemble.demo:data/questions/questions.yml
{% endhighlight %}

### flask_log

**docassemble** uses the [Flask] web framework.  This is the path to the
[Flask] log file.  Most errors write to the standard web server error
logs, but there are some that will only write to this log file.

### language and locale

These directives set the default [language and locale settings] for **docassemble**.

{% highlight yaml %}
language: en
locale: US.utf8
{% endhighlight %}

### default_admin_account

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

### secretkey

The [Flask] web framework needs a secret key in order to manage
session information and provide [protection] against
[cross-site request forgery].  Set the `secretkey` to a random value
that cannot be guessed.

### png_resolution and png_screen_resolution

When users supply PDF files and **docassemble** includes those files
within a [document], the PDF pages are converted to PNG images in
order to be included within RTF files.  `png_resolution` defines the
dots per inch to be used during this conversion.

PDF files are also converted to PNG for previewing within the web app,
but at a lower resolution.  `png_screen_resolution` defines the dots
per inch to be used for conversion of PDF pages to PNG files for
display in the web browser.

### show_login

If set to false, users will not see a "Sign in" link in the
upper-right-hand corner of the web app.

## Enabling optional features

### Image conversion

If you have ImageMagick and pdftoppm installed on your system, you
need to tell **docassemble** the names of the commands to use.

{% highlight yaml %}
imagemagick: convert
pdftoppm_command: pdftoppm
{% endhighlight %}

### Facebook and Google login

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

### Pre-defined variables for all interviews

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

### Currency symbol

You can set a default currency symbol if the symbol generated by
the locale is not what you want:

{% highlight yaml %}
currency_symbol: €
{% endhighlight %}

This symbol will be used in the user interface when a field has the
`datatype` of `currency`.  It will also be used in the
`currency_symbol()` function defined in `docassemble.base.util`.

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
