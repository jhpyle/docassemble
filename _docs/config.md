---
layout: docs
title: System-wide configuration
short_title: Configuration
---

# <a name="configfile"></a>Location of the configuration file

**docassemble** reads its configuration directives from a [YAML] file,
which by default is located in `/usr/share/docassemble/config/config.yml`.
If you are using [Docker] and [S3] or [Azure blob storage],
**docassemble** will attempt to copy the configuration file from your
[S3] bucket or [Azure blob storage] container before starting.

# <a name="edit"></a>How to edit the configuration file

The configuration file can be edited through the web application by
any user with `admin` privileges.  The editing screen is located on
the menu under "Configuration."  After the configuration [YAML] is
saved, the server is restarted.

You can also edit the configuration file directly on the file system.
(You may need to be able to do so if you make edits to the
configuration file through the web application that render the web
application inoperative.)

# <a name="sample"></a>Sample configuration file

Here is an example of what a configuration file may look like:

{% highlight yaml %}
debug: True
exitpage: https://docassemble.org
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: localhost
  port: Null
  table prefix: Null
secretkey: 28asflwjeifwlfjsd2fejfiefw3g4o87
default title: docassemble
default short title: doc
mail:
  username: Null
  password: Null
  server: localhost
  default sender: '"Administrator" <no-reply@example.com>'
default interview: docassemble.demo:data/questions/questions.yml
language: en
locale: en_US.utf8
default admin account:
  nickname: admin
  email: admin@admin.com
  password: password
voicerss:
  enable: False
  key: ae8734983948ebc98239e9898f998432
  languages:
    en: us
    es: mx
    fr: fr
s3:
  enable: False
  access key id: FWIEJFIJIDGISEJFWOEF
  secret access key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
  bucket: yourbucketname
  region: us-west-2
azure:
  enable: False
  account name: example-com
  account key: 1TGSCr2P2uSw9/CLoucfNIAEFcqakAC7kiVwJsKLX65X3yugWwnNFRgQRfRHtenGVcc5KujusYUNnXXGXruDCA==
  container: yourcontainername
ec2: False
words:
  - docassemble.base:data/sources/us-words.yml
{% endhighlight %}

At a bare minimum, your configuration file should set the
[`secretkey`] and [`default sender`] directives:

{% highlight yaml %}
secretkey: 28asflwjeifwlfjsd2fejfiefw3g4o87
mail:
  default sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

# <a name="directives"></a>Configuration directives

## <a name="debug"></a>Development vs. production

Set the `debug` directive to `True` on development servers and `False`
on production servers.  The default is `True`.

{% highlight yaml %}
debug: True
{% endhighlight %}

Setting `debug` to `True` enables the following features:

* The "Source" button in the web app, which shows the [YAML] source code used
  to generate the current question, an explanation of the path the
  interview took to get to the current question, and [readability
  statistics] for the question and the help text.
* Viewing [LaTeX] and [Markdown] source in document attachments.

## <a name="root"></a>Path to web application

Set the `root` directive if you have configured **docassemble** to run
from a sub-location on your web server.  The default is `/`.

{% highlight yaml %}
root: /da/
{% endhighlight %}

The value of `root` depends on how you configured your web server
during [installation].  If the [WSGI] application runs from the URL
`https://docassemble.example.com/da/`, set `root` to `/da/`.  Always
use a trailing slash.

If the [WSGI] application runs from the root of your web server (e.g.,
https://docassemble.example.com/), do not set this directive, or set
it to `/`.

## <a name="url root"></a>URL of application

The optional directive `url root` indicates the part of the URL that
comes before the [`root`].

{% highlight yaml %}
url root: http://example.com
{% endhighlight %}

It is normally not necessary for **docassemble** to know how it is
being accessed from the web, because the URL is provided to the web
application with every HTTP request.

However, there are some circumstances when **docassemble** code runs
outside the context of an HTTP request.  For example, if you have a
[scheduled task] that uses [`send_sms()`] to send a text message with
a media attachment, the URL for the media attachment will be unknown
unless it is set in the configuration.

## <a name="dispatch"></a>Interview shortcuts

The `dispatch` directive allows users to start interviews with
user-friendly URLs like `https://example.com/start/legal`.

{% highlight yaml %}
dispatch:
  legal: docassemble.demo:data/questions/questions.yml
  madlibs: docassemble.base:data/questions/examples/madlibs.yml
{% endhighlight %}

In this example, the URL shortcuts `/start/legal` and `/start/madlibs`
are enabled.

In addition, when you define the [`dispatch`] directive, your users
can see a list of available interviews by going to the URL `/list` on
the site.  They will see a page like this:

![Interview list]({{ site.baseurl }}/img/interviewlist.png){: .maybe-full-width }

If you want to take advantage of the `/start/` shortcuts but you do
not want the interview listed in the interview list, set `unlisted:
True` in the [`metadata`] of the interview.

If you would like to embed the list of interviews into another web
site, you can send a [GET request] to `/list?embedded=1` to obtain a
snippet of [HTML].  For example, the [HTML] snippet might look like
this:

{% highlight html %}
<ul class="dastart">
  <li><a href="/?i=docassemble.demo%3Adata%2Fquestions%2Fquestions.yml">Demonstration interview</a></li>
  <li><a href="/?i=docassemble.base%3Adata%2Fquestions%2Fexamples%2Fmadlibs.yml">Mad libs</a></li>
</ul>
{% endhighlight %}

On your web site, you can embed this into the body of a page.  You can
use the `dastart` [CSS] class to apply styles to this list.

Here is an example of a complete page of [HTML] that demonstrates how
you can embed the result of `/list?embedded=1` into a page:

{% highlight html %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>Page of a web site</title>
    <style>
      ul.dastart {
        list-style-type: circle;
      }
      ul.dastart li {
        font-size: 12px;
      }
      ul.dastart a {
        text-decoration: none;
      }
      ul.dastart a:hover {
        text-decoration: underline;
      }
    </style>
  </head>
  <body>
    <h1>Hello, world!</h1>
    
    <p>I thought you might be interested in some interviews.</p>
    
    <div id="interviews"></div>
    
    <p>Goodbye.</p>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.2.1/jquery.min.js"></script>
    <script type="text/javascript">
      $.get("https://demo.docassemble.org/list?embedded=1", function(data){
        $("#interviews").html(data);
      }).fail(function(){
        $("#interviews").html('<span style="color: red">Error: unable to get list of interviews.</span>');
      });
    </script>
  </body>
</html>
{% endhighlight %}

You can [try this out here]({{ site.baseurl }}/static/test-embed.html){:target="_blank"}.

On your web site, you may need to edit files in different places in
order to control the various parts of the [HTML] response.  Some things
to note about this example:

* The place where you want the interview list to appear is designated
  by `<div id="interviews"></div>`.
* The part between `<style>` and `</style>` is optional and simply
  demonstrates how the list of interviews can be styled.  The [CSS]
  commands could also be put in a separate [CSS] file.
* The part that retrieves the interview list is the [Javascript] call
  to [`$.get()`], which is between `<script type="text/javascript">` and
  `</script>`.  The part that plugs the [HTML] into the screen is the
  call to [`.html()`].
* [jQuery] needs to be loaded before the call to `$.get()`.  [jQuery]
  is very common on web sites, so it may already be loaded on your
  site.
* The [Javascript] code is wrapped in a call to
  [`$( document ).ready`].  This may not be necessary on your site,
  but it can help avoid the potential problem where call to
  [`.html()`] takes place before the `<div id="interviews"></div>`
  [HTML] even exists on the screen.

You can also call `/list?json=1` to obtain a [JSON] version of the
available interviews.

## <a name="start page template"></a><a name="interview page template"></a><a name="start page title"></a><a name="interview page title"></a><a name="start page heading"></a><a name="interview page heading"></a>Customization of pages

There are two pages that you can customize:

* The [start page] that shows a list of available interviews.
* The list of saved interviews.

You can customize the titles.  There are two types of titles:

* A "page title" that appears in the browser tab and in the top
navigation bar; and
* A "heading" that appears in the body of the page.

You can customize these titles with the following directives:

{% highlight yaml %}
start page title: Missouri interviews
start page heading: Interviews available to Missouri residents
interview page title: Your interviews
interview page heading: Interviews you have started
{% endhighlight %}

If you want to customize more than the titles, you can specify an
[HTML] template to use.  Use the `start page template` and `interview
page template` directives to point to files in the "templates"
directory of a package.

{% highlight yaml %}
start page template: docassemble.missouri:data/templates/my_start_page.html
interview page template: docassemble.missouri:data/templates/my_interview_page.html
{% endhighlight %}

To see what the standard templates look like, see:

* [`start.html`]
* [`interviews.html`]

You might want to use these as a starting point.  Note that
**docassemble** uses [Flask], which uses [Jinja2] HTML templates.

These templates use [Jinja2] to load a standard [HTML] framework.  If
you want, you can replace the entire body of the page using these
templates.  However, if you do so, you may wish to include 
`{% raw %}{{ extra_css }}{% endraw %}` in the `<head>` and 
`{% raw %}{{ extra_js }}{% endraw %}` at the end of the `<body>`.
On the interviews page, there is a bit of [Javascript] that 
asks the user "are you sure?" before deleting all of the interview.
The start page does not use [Javascript].

You can also customize the appearance of these pages using [CSS].  The
[HTML] elements in the standard template use some classes do nothing;
they are just placeholders for customization.  For example, to
customize [`start.html`] and [`interviews.html`], you could include
the following in a [CSS] file that you include with [`global css`]
(which is discussed in the next section):

{% highlight css %}
h1.dastartpage {
  font-size: 15px;
}
ul.dastartpage {
  background-color: red;
}
ul.dastartpage li {
  font-weight: bold;
}
h3.dainterviewpage {
  font-decoration: underline;
}
p.dainterviewpage {
  color: #aaaaaa;
}
table.dainterviewpage td {
  border-style: solid;
  border-width: 1px;
}
{% endhighlight %}

## <a name="session list interview"></a><a name="dispatch interview"></a>Replacing built-in pages with interviews

Instead of [customizing] the start page and the interview page, you
can replace them with interviews.

{% highlight yaml %}
session list interview: docassemble.base:data/questions/examples/session-interview.yml
dispatch interview: docassemble.base:data/questions/examples/list-interview.yml
{% endhighlight %}

The [`interview_list()`] function allows you write an interview that
accesses information about the interview sessions of a logged-in user.
Here is an example interview,
`docassemble.base:data/questions/examples/session-interview.yml`,
which mimics the style of the standard list of interview sessions.

{% include side-by-side.html demo="session-interview" %}

The [`interview_menu()`] function allows you write an interview that
accesses information about the interviews available on the start page.
Here is an example interview,
`docassemble.base:data/questions/examples/list-interview.yml`, which
mimics the style of the standard start page:

{% include side-by-side.html demo="list-interview" %}

## <a name="global css"></a><a name="global javascript"></a>CSS and Javascript customization

You can use the [`javascript` features setting] and the
[`css` features setting] to modify the [Javascript] and [CSS] for a
particular interview.

By using `global javascript` and `global css`, you can apply
[Javascript] and [CSS] on a more global level.  These directives allow
you to include [Javascript] and [CSS] files in every interview and
also in the [start page] and the page showing the list of interviews.
The directive should refer to files located in the "static" directory
of a package:

{% highlight yaml %}
global css: docassemble.missouri:data/static/missouri.css
global javascript: docassemble.missouri:data/static/missouri.js
{% endhighlight %}

If you have more than one [CSS] file or more than one [Javascript]
file, you can use these directives to refer to a list of files:

{% highlight yaml %}
global css: 
  - docassemble.missouri:data/static/missouri.css
  - docassemble.midwest:data/static/look_and_feel.css
{% endhighlight %}

These [Javascript] and [CSS] files are loaded after the other
[Javascript] and [CSS] files on the page.

## <a name="bootstrap theme"></a>Bootstrap theme

Using the `bootstrap theme` directive, you can change the look and
feel of your site's web interface by substituting a non-standard [CSS]
file in place of the standard [CSS] file used by [Bootstrap].

{% highlight yaml %}
bootstrap theme: docassemble.webapp:data/static/paper.min.css
{% endhighlight %}

You can also refer to files on the internet:

{% highlight yaml %}
bootstrap theme: https://bootswatch.com/paper/bootstrap.min.css
{% endhighlight %}

There are many alternative [Bootstrap] themes available on
[Bootswatch].  Note that you may need to use apply additional [CSS]
changes in order to get a [Bootstrap] theme to work with
**docassemble**.  For example, by default **docassemble** assumes that
the navigation bar is 50 pixels in height.  But if your theme makes
the navigation bar 60 pixels tall, you will need to add the following
styles:

{% highlight css %}
.pad-for-navbar         { padding-top: 70px; }
.top-for-navbar         { top: 70px;         }
{% endhighlight %}

Also, some of the colors that **docassemble** uses in the navigation
bar might not work well with every theme.  You can override these
colors with [CSS] like the following:

{% highlight css %}
.backbuttoncolor        { color: #539ac7;        }
.backbuttoncolor:hover  { color: #539ac7;
                          text-decoration: none; }
span.daactivetext       { color: yellow;         }
span.daactivetext:hover { color: #ffff99;        }
i.chat-active           { color: #45bf41;        }
i.chat-active:hover     { color: #55cf51;        }
i.chat-inactive         { color: #4f4f4f;        }
i.chat-inactive:hover   { color: #5f5f5f;        }
{% endhighlight %}

These styles refer to the blue back button, the yellow "Help" button
that appears when question-specific help is available, the green icons
that appear in the navigation bar when [live help] features are
available, and the grey color that these icons become when [live help]
is no longer available.

You can also control the [Bootstrap] theme on a per-interview basis
with the [`bootstrap theme` feature].  You can also alter [CSS] on a
per-interview basis using the [`css` features setting].

## <a name="inverse navbar"></a>Inverted Bootstrap navbar

By default, **docassemble** uses the [inverted navbar] option in
[Bootstrap] so that the navigation bar stands out from the white
background.  If you do not want to use the inverted navbar, set the
`inverse navbar` to `False`.

{% highlight yaml %}
inverse navbar: False
{% endhighlight %}

You can also control this on a per-interview basis with the
[`inverse navbar` feature].

## <a name="button size"></a>Button size

By default, most buttons in the **docassemble** user interface are
"large" size [Bootstrap] buttons.  If you want the buttons to be
"normal" size, set the following in your configuration:

{% highlight yaml %}
button size: normal
{% endhighlight %}

The default value is `large`.

## <a name="favicon"></a>Custom favicon in browser tab

The icon in the browser tab is known as a [favicon].  This is the icon
associated with the web application.  By default, **docassemble** uses
the **docassemble** logo for this icon.

If users "pin" your application to their device's main menu, this icon
will be used to create the resulting icon.  Microsoft, Apple, and
Google have their own conventions for doing this.

In order to "brand" your application in a custom way, create a square
logo and go to
[http://realfavicongenerator.net](http://realfavicongenerator.net) in
order to generate [favicon] files from it.  Upload a square image that
is at least 512x512 in size.  In addition to uploading your file, you
will need to make some choices about different colors that should be
used in different circumstances.  At the end, you will download a Zip
file containing a number of graphics files and other files.

Put the contents of this Zip file in a folder in a **docassemble**
package and then add a `favicon` directive to the configuration,
pointing to this folder.  For example:

{% highlight yaml %}
favicon: docassemble.abcincorporated:data/static/favicon
{% endhighlight %}

In this example, `data/static/favicon` in the
`docassemble.abcincorporated` package is a folder that is expected to
contain the following files, which were contained in the Zip file:

* `android-chrome-192x192.png`
* `android-chrome-512x512.png`
* `apple-touch-icon.png`
* `browserconfig.xml`
* `favicon-16x16.png`
* `favicon-32x32.png`
* `favicon.ico`
* `manifest.json`
* `mstile-150x150.png`
* `safari-pinned-tab.svg`

In addition to providing you with a Zip file containing the above
files, the above web site will instruct you to place particular
`<link>` and `<meta>` tags in the HTML of your site.  **docassemble**
does this for you automatically, so you can ignore most of this.
However, two of the lines are important.  The will look like this:

{% highlight html %}
<link rel="mask-icon" href="/safari-pinned-tab.svg" color="#698aa7">
<meta name="theme-color" content="#83b3dd">
{% endhighlight %}

Note the `color` in the first line and the `content` in the second
line.  Then add the following two lines to your configuration,
corresponding to the above two lines:

{% highlight yaml %}
favicon mask color: #698aa7
favicon theme color: #83b3dd
{% endhighlight %}

If you do not specify `favicon mask color` or `favicon theme color`,
your custom [favicon] will still work, but **docassemble** will choose
colors for you.  (The colors above are the defaults.)

If any of the above files is missing, your [favicon] will probably
still work in most circumstances.  The most important file is
`favicon.ico`, a special graphics file in Microsoft's [ICO] format.

Note that if you have set the [`root`] directive (if your
**docassemble** site at `https://example.com/something/` instead of
`https://example.com/`), you will need to account for this when you
generate the [favicon] files using the above web site.  This is
important because the `manifest.json` and `browserconfig.xml` files
contain URL references.  If your site is at `/something/`, then
`manifest.json` will need to refer to
`"/something/android-chrome-192x192.png"` instead of
`"/android-chrome-192x192.png"`.

Note that most web browsers will store a cache of the [Favicon], so
that when you make a change to your app's [Favicon], it may seem that
your change is not working when it actually is.  If it seems that your
[Favicon] has not taken effect, try accessing the app a web browser
that you do not normally use.

## <a name="icon size"></a>Icon size

The size of icons in [decorations] and in [image buttons] is not
specified in [CSS].  To change these sizes, you can edit these
configuration directives:

{% highlight yaml %}
decoration size: 2.0
decoration units: em
button icon size: 4.0
button icon units: em
{% endhighlight %}

## <a name="exitpage"></a>Exit page

The `exitpage` directive contains the default URL to which the user
should be directed after clicking a button that runs an [`exit`] or
[`leave`] command.  (See the [Setting Variables] section.)

For example:

{% highlight yaml %}
exitpage: http://example.com/pages/thankyou.html
{% endhighlight %}

## <a name="db"></a>SQL database

The `db` section of the configuration tells the **docassemble** web
app where to find the SQL database in which to store users' answers,
login information, and other information.

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: localhost
  port: 5432
  table prefix: Null
{% endhighlight %}

The `prefix` is a [SQLAlchemy] prefix.  If you use a database other
than [PostgreSQL], change this.  For [MySQL], use `mysql://`

<a name="db host"></a>**docassemble** will connect to the SQL database
at the hostname `host` on the port `port`, and will authenticate with
the `user` and `password`.  It will connect to the database called
`name`.  If you want separate **docassemble** systems to share the
same database, you can set a `table prefix`.

## <a name="appname"></a><a name="brandname"></a>Branding

The `appname` and `brandname` directives control the name of the
application in various contexts.

{% highlight yaml %}
appname: Legal Helper
brandname: Legal Helper Application
{% endhighlight %}

On administration pages, the `appname` appears in the web browser tab,
and the `brandname` appears in the navigation bar.

The `appname` is also used in e-mails that are generated by the
[user login system].

The `appname` defaults to `docassemble`.  The `brandname` will default
to the `appname` if `brandname` is not specified.

## <a name="default title"></a><a name="default short title"></a>Default name in navigation bar

The `default title` and `default short title` directives control the
names that are displayed in the web browser tab and the navigation bar
of interviews that do not specify these titles in their [`metadata`].

The "short" title appears on mobile devices, while the long title
appears on larger screens.

{% highlight yaml %}
default title: Abramsom Baker and Calloway, LLP
default short title: ABC LLP
{% endhighlight %}

If not specified, the `default title` will default to the
[`brandname`].

## <a name="uploads"></a>Uploads directory

The `uploads` directive indicates the directory in which uploaded files are stored.

{% highlight yaml %}
uploads: /netmount/files/docassemble/uploads
{% endhighlight %}

If you are using a [multi-server arrangement] and not using [S3] or
[Azure blob storage], this needs to point to a central network drive.

The default value is `/usr/share/docassemble/files`.

## <a name="packages"></a>Python directory

The `packages` directive indicates the base directory into which
**docassemble** extension packages will be installed.  The
[PYTHONUSERBASE] environment variable is set to this value and [pip]
is called with `--install-option=--user`.  When [Python] looks for
packages, it will look here.  [Python]'s default value is `~/.local`,
but **docassemble** changes it to the value of this directive, or
`/usr/share/docassemble/local` if the directive is not defined.

{% highlight yaml %}
packages: /netmount/files/docassemble/local
{% endhighlight %}

If you are using a [multi-server arrangement] and not using [S3] or
[Azure blob storage], this needs to point to a central network drive.

## <a name="webapp"></a>Path to WSGI application

The `webapp` directive indicates the path to the [WSGI] file loaded by
the web server.

{% highlight yaml %}
webapp: /netmount/files/docassemble/webapp/docassemble.wsgi
{% endhighlight %}

**docassemble** needs to know this filename because the server needs
to reset itself after an add-on package is updated.  The web server is
reset by updating the modification time of the [WSGI] file.

The default value is `/usr/share/docassemble/webapp/docassemble.wsgi`.

## <a name="certs"></a>Path to SSL certificates

The `certs` directive indicates a central location where SSL
certificates for the web server can be found.  The location can be a
file path, an [S3] path, or an [Azure blob storage] path.  This is
only relevant if you are using [HTTPS].

For example, you might keep your certificates on a network drive:

{% highlight yaml %}
certs: /netmount/files/docassemble/certs
{% endhighlight %}

By default, the [Apache] HTTPS configuration contains:

{% highlight text %}
SSLCertificateFile /etc/ssl/docassemble/apache.crt
SSLCertificateKeyFile /etc/ssl/docassemble/apache.key 
SSLCertificateChainFile /etc/ssl/docassemble/apache.ca.pem
{% endhighlight %}

When using a [multi-server arrangement] or [Docker], the [supervisor]
process on each web server executes the
[`docassemble.webapp.install_certs`] module during the
[startup process].  This module copies certificates from the location
indicated by `certs` to `/etc/ssl/docassemble` before starting the web
server.  This is a convenience feature.  Otherwise, you would have to
manually install the SSL certificates on every new **docassemble** web
server you create.

The value of `certs` can be a file path, an [Amazon S3]<span></span>
[URI] (e.g., `s3://exampledotcom/certs`), or an
[Azure blob storage]<span></span> [URI] (e.g.,
`blob://youraccountname/yourcontainername/certs`).  The contents of
the directory are copied to `/etc/ssl/docassemble`.

If you leave the `certs` setting undefined (which is recommended),
**docassemble** will look in `/usr/share/docassemble/certs` if the
[`s3`] and [`azure`] settings are not enabled.

If [`s3`] is enabled, it will look for [S3] keys with the prefix
`certs/` in the `bucket` defined in the [`s3`] configuration.

If [`azure`] is enabled, it will look for [Azure blob storage] objects
with the prefix `certs/` in the `container` defined in the [`azure`]
configuration.

Here is an example.  Install [`s3cmd`] if you have not done so already:

{% highlight bash %}
apt-get install s3cmd
{% endhighlight %}

Then do:

{% highlight bash %}
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.crt s3://yourbucket/certs/apache.crt
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.key s3://yourbucket/certs/apache.key
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.ca.pem s3://yourbucket/certs/apache.ca.pem
{% endhighlight %}

If your [`s3`] configuration has `bucket: yourbucket`, then you do not
need to set a `certs` configuration, because **docassemble** will by
default look in `s3://yourbucket/certs`.  However, if the certificates
are stored in another location, you can specify a different location:

{% highlight yaml %}
certs: s3://otherbucket/certificates
{% endhighlight %}

If you want to use a location other than `/etc/ssl/docassemble`, you
can change the [`cert install directory`] setting (see below).  You will
also, of course, need to change the web server configuration file.

## <a name="mail"></a>E-mail configuration

**docassemble** needs to send e-mail, for example to reset people's
passwords, or to let users of a multi-user interview know that it is
their turn to start answering questions.

By default, **docassemble** assumes that an SMTP server is installed
on the same machine as the web server and that it uses port 25.

<a name="default sender"></a>If you are going to send mail, you should
at least set the `default sender` directive, which sets the return
address on any e-mails generated from **docassemble**:

{% highlight yaml %}
mail:
  default sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

To use another SMTP server as the mail server, do something like:

{% highlight yaml %}
mail:
  default sender: '"Administrator" <no-reply@example.com>'
  username: mailuser
  password: abc123
  server: smtp.example.com
  port: 25
  use ssl: False
  use tls: True
{% endhighlight %}

If you are hosting **docassemble** in the cloud, you will probably
have to use a separate SMTP server in order to send e-mail.

A free option is [Mailgun].  You can sign up with [Mailgun], provide a
credit card (which will only be charged if you exceed the free tier),
configure some [DNS] entries, and then set your configuration to
something like this:

{% highlight yaml %}
mail:
  default sender: '"Example, Inc." <no-reply@mg.example.com>'
  username: 'postmaster@mg.example.com'
  password: '5a4a0c5f3da35f3bc10f0462364c26dd'
  server: 'smtp.mailgun.org'
{% endhighlight %}

## <a name="default interview"></a>Default interview

If no [interview] is specified in the URL when the web browser first
connects to the **docassemble** server, the interview indicated by
`default interview` will be used.  The interview needs to be specified
in "package name:relative file path" format.  For example:

{% highlight yaml %}
default interview: docassemble.base:data/questions/examples/attachment.yml
{% endhighlight %}

If this directive is not set, **docassemble** will redirect to a page
showing a [list of available interviews] determined by the
[`dispatch`] directive.  However, if the [`dispatch`] directive is not
defined, users will be directed to the demonstration interview,
`docassemble.demo:data/questions/questions.yml`.

## <a name="flask log"></a><a name="celery flask log"></a>Flask log file location

**docassemble** uses the [Flask] web framework.  The `flask log` and
`celery flask log` directives contain the paths to the [Flask] log
files for the web application and the [Celery] background workers,
respectively.  Most errors write to the `docassemble.log` file located
in `/usr/share/docassemble/log` (or the directory indicated by
[`log`], or to standard web server error logs, but there are some
errors, typically those that are [Flask]-related, that will only write
to these log files.

{% highlight yaml %}
flask log: /tmp/docassemble-log/flask.log
celery flask log: /tmp/docassemble-log/celery-flask.log
{% endhighlight %}

The default locates for the [Flask] log files are `/tmp/flask.log` and
`/tmp/celery-flask.log`.

## <a name="language"></a><a name="dialect"></a><a name="locale"></a>Default language, locale, and dialect

These directives set the default [language and locale settings] for
**docassemble** interviews.

{% highlight yaml %}
language: en
locale: en_US.utf8
dialect: us
{% endhighlight %}

The `language` needs to be a lowercase [ISO-639-1] code.  The `locale`
needs to be a locale name that will be accepted by the [locale]
library.

The dialect is only relevant for the text-to-speech feature, which is
controlled by the [special variable `speak_text`].  See the
[`voicerss`] configuration for more information about configuring this
feature.  The default dialect is only used as a fallback, in case the
dialect cannot be determined any other way.  It is better to set the
dialect using [`set_language()`] or the [`voicerss`] configuration.

## <a name="country"></a>Default country

The `country` directive sets the default country for **docassemble**.

{% highlight yaml %}
country: US
{% endhighlight %}

The country is primarily relevant for interpreting telephone numbers.
The code needs to be a valid country code accepted by the
[phonenumbers] library.

## <a name="os locale"></a>Operating system locale

If you are using [Docker], the `os locale` directive will set the
default operating system locale.

{% highlight yaml %}
os locale: en_US.UTF-8 UTF-8
{% endhighlight %}

## <a name="other os locales"></a>Other available locales

If your interviews use locale and language settings that your
operating system does not support, you will get an error.

On [Docker], you can enable locales other than the [`os locale`] in
the operating system by providing a list of locales to the `other os
locales` directive:

{% highlight yaml %}
other os locales:
  - en_GB.UTF-8 UTF-8
  - es_MX.UTF-8 UTF-8
{% endhighlight %}

## <a name="debian packages"></a>Debian packages to install

On [Docker], you can ensure that particular [Debian] packages are
installed by providing a list of packages to the `debian packages`
directive:

{% highlight yaml %}
debian packages:
  - r-base
  - r-cran-effects
{% endhighlight %}

These packages will be installed when the [Docker] container starts.

## <a name="default admin account"></a>Default administrator account credentials

When a **docassemble** SQL database is first initialized, an
administrative user is created.  By default, this user has the e-mail
address `admin@admin.com` and the password `password`.  As soon as the
web server comes on-line, you can log in and change the e-mail address
and password to something more secure.

However, you can also use the `default admin account` directive in the
configuration so that a more secure e-mail address and password are
used during the setup process.

{% highlight yaml %}
default admin account:
  email: admin@example.com
  password: 67Gh_Secret_2jx
{% endhighlight %}

The settings are only used by the [`docassemble.webapp.create_tables`]
module during the initial setup process.  Using the information
defined here, that script sets up a single account in the
[user login system] with "admin" privileges.

After [`create_tables`] runs for the first time, you can delete the
`default admin account` information from the configuration file.

## <a name="use alembic"></a>Database table upgrades

By default, **docassemble** uses [alembic] to upgrade the SQL database
from one version to another.  To turn this off, you can add:

{% highlight yaml %}
use alembic: False
{% endhighlight %}

## <a name="secretkey"></a>Secret key for Flask

The [Flask] web framework needs a secret key in order to manage
session information and provide [protection] against
[cross-site request forgery].  Set the `secretkey` to a random value
that cannot be guessed.

{% highlight yaml %}
secretkey: CnFUCzajSgjVZKD1xFfMQdFW8o9JxnBL
{% endhighlight %}

The [startup process] on [Docker] sets the `secretkey` to a random
value.

## <a name="password secretkey"></a>Secret key for passwords

The `password secretkey` is used in the process of encrypting
interview answers for users who log in using
[Facebook, Twitter, Google, or Azure].  It defaults to the same value as
`secretkey`.  If this value changes, users who log in through
Facebook, Twitter, Google or Azure will not be able to resume stored
interviews.

## <a name="require referer"></a>Allowing referer blocking

By default, when HTTPS is used, **docassemble** uses a form of
[CSRF protection] that checks whether the [referer header] matches the
host.  For privacy reasons, some users set their browsers to disable
the sending of the referer header.  If the [referer header] is
missing, the [CSRF protection] mechanism will generate an error.  To
bypass this security feature, set:

{% highlight yaml %}
require referer: False
{% endhighlight %}

The default setting is `True`.

## <a name="png resolution"></a><a name="png screen resolution"></a>Image conversion resolution

When users supply PDF files and **docassemble** includes those files
within a [document], the PDF pages are converted to PNG images in
order to be included within RTF files.  The `png resolution` directive
defines the dots per inch to be used during this conversion.

PDF files are also converted to PNG for previewing within the web app,
but at a lower resolution.  The `png screen resolution` directive
defines the dots per inch to be used for conversion of PDF pages to
PNG files for display in the web browser.

<a name="ocr dpi"></a>OCR resolution

If you use the [`ocr_file()`] function, the pages of the PDF file will
be converted to images before being read by the OCR engine.  By
default, the resolution used is 300 dpi.  To change this to something
else, set the `ocr dpi` directive:

{% highlight yaml %}
ocr dpi: 500
{% endhighlight %}

## <a name="show login"></a>Hiding the login link

If the `show login` directive is set to `False`, users will not see a
"Sign in or sign up to save answers" link in the upper-right-hand
corner of the web app.

{% highlight yaml %}
show login: False
{% endhighlight %}

The default behavior is to show the "Sign in or sign up to save
answers" link.

## <a name="allow registration"></a>Invitation-only registration

If the `allow registration` directive is set to `False`, users will
not be allowed to register to become users of the site unless they are
[invited by an administrator].

{% highlight yaml %}
allow registration: False
{% endhighlight %}

The default behavior is to allow any user to register.

## <a name="email confirmation"></a>E-mail confirmation

If you want to verify e-mail addresses of users, you can set the
`email confirmation privileges` directive to a list of [privileges] for which
e-mail confirmation should be a requirement of logging in.

{% highlight yaml %}
email confirmation privileges:
  - admin
  - developer
  - advocate
{% endhighlight %}

By default, e-mail confirmation is not required for any privileges (i.e.,
the `email confirmation privileges` is an empty list.  Also, the default
administrative user is confirmed when initially created, so you will
never need to confirm that user's e-mail.

Before you enable this feature, make sure you have a working
[email configuration](#mail).

## <a name="xsendfile"></a>Support for xsendfile

If your web server is not configured to support X-SENDFILE headers,
set the `xsendfile` directive to `False`.

{% highlight yaml %}
xsendfile: False
{% endhighlight %}

Use of X-SENDFILE is recommended because it allows the web server,
rather than the Python [WSGI] server, to serve files.  This is
particularly useful when serving sound files, since the web browser
typically asks for only a range of bytes from the sound file at a
time, and the [WSGI] server does not support the HTTP Range header.

## <a name="log"></a>Directory for log files

**docassemble** writes messages to a log files stored in the directory
indicated by the `log` directive.  These messages are helpful for
debugging problems with interviews.

{% highlight yaml %}
log: /tmp/docassemble-log
{% endhighlight %}

The default directory is `/usr/share/docassemble/log`.

If a `log server` is set, **docassemble** will write messages to TCP
port 514 on that server, and will not write to the `log` directory.

## <a name="interview delete days"></a>Days of inactivity before interview deletion

When the [scheduled tasks] feature is [enabled] on the server,
**docassemble** will delete interviews after 90 days of inactivity.
To change the number of days, set the `interview delete days`
directive in the configuration.  For example:

{% highlight yaml %}
interview delete days: 180
{% endhighlight %}

If `interview delete days` is set to `0`, interviews will never be
deleted through [scheduled tasks].

## <a name="checkin interval"></a>Polling frequency

By default, the user interface polls the server every six seconds to
"check in" to see if anything has happened that it needs to know
about, and to let the server know that the user is still active.

You can change this interval by setting the `checkin interval`
directive.  The number refers to the milliseconds between each call to
the server.

{% highlight yaml %}
checkin interval: 6000
{% endhighlight %}

## <a name="docassemble git url"></a>Alternative GitHub location for docassemble

The [Packages] feature updates the **docassemble** software directly
from [GitHub].  If you need to change the location of this repository
to your own [fork] of **docassemble**, you can add this directive.

{% highlight yaml %}
docassemble git url: https://github.com/yourusername/docassemble
{% endhighlight %}

The default value is `'{{ site.github.repository_url }}'`.

This directive only has an effect during [initial database setup].

## Pre-defined variables for all interviews

If you would like to pass variable definitions from the configuration
into the interviews, you can set values of the `initial dict`:

{% highlight yaml %}
initial dict:
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

## <a name="words"></a>Translations of words and phrases

If your server will offer interviews in languages other than English,
you will want to make sure that built-in words and phrases used within
**docassemble**, such as "Continue" and "Sign in," are translated into
the user's language.

The `words` directive loads one or more [YAML] files in order:

{% highlight yaml %}
words:
  - docassemble.base:data/sources/us-words.yml
{% endhighlight %}

Each [YAML] file listed under `words` must be in the form of a
dictionary in which the keys are languages ([ISO-639-1] codes) and the
values are dictionaries with the translations of words or phrases.

Assuming the following is the content of the
`data/sources/words.yml` file in [`docassemble.base`]:

{% highlight yaml %}
es:
  Continue: Continuar
  Help: ¡Ayuda!
{% endhighlight %}

then if the interview calls `set_language('es')` (Spanish) and
**docassemble** code subsequently calls `word('Help')`, the result
will be `¡Ayuda!`.

When you are logged in as a developer or administrator, you can go to
the "Utilities" page from the main menu, where you will find a utility
for generating a draft [YAML] file for translating all of the words
and phrases that **docassemble** uses and that might be presented to
the user.  If you have set up a [Google API key](#google), it will use
the [Google Cloud Translation API] to prepare "first draft"
translations for any [ISO-639-1] language you designate.

For more information about how **docassemble** handles different
languages, see the [language and locale settings] section and the
[functions] section (specifically the functions [`set_language()`] and
[`word()`]).

## <a name="currency_symbol"></a>Currency symbol

You can set a default currency symbol if the symbol generated by
the locale is not what you want:

{% highlight yaml %}
currency symbol: €
{% endhighlight %}

This symbol will be used in the user interface when a [field] has the
`datatype` of [`currency`].  It will also be used in the
[`currency_symbol()`] function defined in [`docassemble.base.util`].

## <a name="fileserver"></a>URL to central file server

If you are using a [multi-server arrangement] you can reduce
bandwidth on your web server(s) by setting `fileserver` to a URL path to
a dedicated file server:

{% highlight yaml %}
fileserver: https://files.example.com/da/
{% endhighlight %}

Always use a trailing slash.

If this directive is not set, the value of [`root`] will be used to
create URLs to uploaded files and static files.

Note that if you are using [Azure blob storage] or [S3], the URLs to
files will point directly to files stored in the cloud, so there would
be no reason for a **docassemble** file server.

## <a name="google"></a>Google API key

If you have a Google API key, you can include it as follows:

{% highlight yaml %}
google:
  api key: UIJGeyD-23aSdgSE34gEGRg3GDRGdrge9z-YUia
{% endhighlight %}

This is required for the use of the [`map_of()`] feature.

This will also enable you to use the [Google Maps Geocoding API]
without limits (see the [`.geolocate()`] method), and will also enable
the [Google Cloud Translation API].

If you specify a specific `google maps api key`, this key will be used
for the [`map_of()`] feature instead of the `api key`.

If you use both geocoding and Google Maps, you will probably want to
use a separate `google maps api key` because you can secure it
differently.  Note that the [`map_of()`] feature puts its API key in
the [Javascript] source, and the contact with Google's server will
come from the user's computer.  By contrast, when you use the
[`.geolocate()`] method, the contact with Google's server comes from
your server.  Thus, you may wish to secure the `api key` using IP
addresses, and secure the `google maps api key` using "Referer"
headers.

## <a name="voicerss"></a>VoiceRSS API key

If the [special variable `speak_text`] is set to `True`, **docassemble**
will present the user with an audio control that will convert the text
of the question to speech.  This relies on the [VoiceRSS] web service.
You will need to obtain an API key from [VoiceRSS] and set the
configuration below in order for this feature to function.  (The
service allows 350 free requests per day.)

{% highlight yaml %}
voicerss:
  enable: True
  key: 347593849874e7454b9872948a87987d
  languages:
    en: us
    es: mx
    fr: fr
{% endhighlight %}

The `enable` key must be set to `True` in order for the text-to-speech
feature to work.  The `key` is the [VoiceRSS] API key.  The
`languages` key refers to a dictionary that associates languages with
default dialects to be used with that language.

## <a name="ocr languages"></a>OCR language settings

The [`ocr_file()`] function uses the [Tesseract]<span></span>
[optical character recognition] (OCR) application to extract text from
image files and PDF files.  One of the options for the OCR process is
the language being recognized.  The codes for language that
[Tesseract] uses are different from those that **docassemble** uses.
In most cases, the code that [Tesseract] uses is the [ISO-639-3] code
that corresponds to the [ISO-639-1] code that **docassemble** uses,
and **docassemble** can make this conversion automatically.  However,
in some cases this does not work, so there is an override, which is
controlled by the `ocr languages` directive.  The default value maps
Chinese to Traditional Chinese:

{% highlight yaml %}
ocr languages:
  zh: chi-tra
{% endhighlight %}

If all of the Chinese documents that you want to OCR are written in
Simplified Chinese, and all the Uzbek documents are written in
Cyrillic, you could set the following:

{% highlight yaml %}
ocr languages:
  zh: chi-sim
  uz: uzb-cyrl
{% endhighlight %}

For more information, see the documentation of the [`ocr_file()`] function.

## <a name="aws"></a>Amazon Web Services directives

### <a name="s3"></a>s3

If you are using [Amazon S3] to store shared files, enter your access
keys, [bucket] name, and [region name] as follows:

{% highlight yaml %}
s3:
  enable: True
  access key id: FWIEJFIJIDGISEJFWOEF
  secret access key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
  bucket: yourbucketname
  region: us-west-1
{% endhighlight %}

You will need to create the [bucket] before using it; **docassemble**
will not create it for you.

### <a name="azure"></a>azure

If you are using [Azure blob storage] to store shared files, enter
your account name, account key, and container name as follows:

{% highlight yaml %}
azure:
  enable: False
  account name: example-com
  account key: 1TGSCr2P2uSw9/CLoucfNIAEFcqakAC7kiVwJsKLX65X3yugWwnNFRgQRfRHtenGVcc5KujusYUNnXXGXruDCA==
  container: yourcontainername
{% endhighlight %}

You will need to create the container before using it; **docassemble**
will not create it for you.

### <a name="ec2"></a>ec2

If you are running **docassemble** from within an [Amazon EC2]
instance, or a [Docker] container within such an instance, set this to
true:

{% highlight yaml %}
ec2: True
{% endhighlight %}

This is necessary because when **docassemble** runs in a
[multi-server arrangement], each **docassemble** web server instance
needs to allow other **docassemble** web instances to send messages to
it through [supervisor].  Each web server instance advertises the
hostname or IP address through which its [supervisor] can be accessed.
Normally, this can be obtained using the computer's hostname, but
within an [EC2] instance or [Docker] container, this hostname is not
one that other web servers can resolve.  If `ec2` is set to `True`,
then **docassemble** will determine the hostname by calling
`http://169.254.169.254/latest/meta-data/local-ipv4`.

### <a name="ec2 ip url"></a>ec2 ip url

If `ec2` is set to `True`, **docassemble** will determine the hostname
by calling `http://169.254.169.254/latest/meta-data/local-ipv4`.  If
this URL does not work for some reason, but a different URL would
work, you can change the URL that **docassemble** uses by setting the
`ec2 ip url` configuration item.

{% highlight yaml %}
ec2 ip url: http://169.254.169.254/latest/meta-data/local-ipv4
{% endhighlight %}

## <a name="password login"></a>Password login

If `password login` is set to `False`, then users will not see an
option for entering their username and password on the login screen;
they will only see buttons for other login methods that you have
enabled.  The default value is `True`.

Since there is a possibility that your other login methods will fail,
there is a "back door" that bypasses this setting, so that you as the
administrator can still log in using a username and password.  Instead
of going to `/user/sign-in` in the web browser, go to
`/user/sign-in?admin=1`.  The username and password fields will be
shown, regardless of the `password login` setting.

## <a name="phone login"></a>Phone number login

If `phone login` is set to `True`, then **docassemble** will allow
users to log in with a phone number.  For this system to work, the
[`twilio`] configuration must be set up.  The user needs to put in his
or her phone number, and then a random verification code will be sent
to that phone number via [SMS].  The user needs to type in that code
in order to log in.  As with the
[external authentication methods](#oauth), registration happens
automatically upon the first login.  Subsequent logins will also
require entering a random verification code.

The details of how this login system functions, such as the number of
digits in the verification code and the number of seconds that the
code remains valid, can be [configured](#brute force).

## <a name="mfa"></a>Two-factor authentication

For added security, you can allow users who log in with passwords to
enable two-factor authentication on their accounts.  The two-factor
authentication system can use [Google Authenticator], [Authy], or
another compatible app.  Or, if you have set up a [`twilio`]
configuration, the system can send a verification code to the user in
an [SMS] message.

To give your users the option of using two-factor authentication, set
`two factor authentication` to `True`.  Logged-in users will then see
an option on their "Profile" page for configuring two-factor
authentication.  By default, only administrators and developers see an
option on their user profile to configure second-factor
authentication.  To configure which privileges have the option of using
second factor authentication, set `two factor authentication privileges` to
the full list of [privileges] you want to be able to use the feature.

{% highlight yaml %}
two factor authentication: True
two factor authentication privileges:
  - admin
  - developer
  - user
  - advocate
{% endhighlight %}

Two-factor authentication is not available to users who sign in with
[external authentication methods](#oauth) or who are using the
[phone login] feature.

## <a name="vim"></a>Vim-like editor in Playground

If the `vim` directive is set to `True`, then the in-browser text
editors in the [Playground] will emulate [Vim].  This uses the
[Vim bindings option] of [CodeMirror].

## <a name="external hostname"></a>URL to the site

The `external hostname` is the hostname by which users will access
**docassemble**.  This variable is only used if **docassemble** is
running on [Docker].

{% highlight yaml %}
external hostname: docassemble.example.com
{% endhighlight %}

## <a name="behind https load balancer"></a>When behind a proxy

Set the `behind https load balancer` directive to `True` if you are
running **docassemble** in a configuration where **docassemble**
itself is running HTTP, but requests are being forwarded to it by a
server running HTTPS.  This might be your configuration if you are
using a [load balancer] or you are running [Docker] on machine that
[forwards] HTTPS requests to [Docker] on a non-standard HTTP port.

## <a name="cross site domain"></a>Cross-Origin Resource Sharing (CORS)

Set the `cross site domain` directive if you want your [Apache] server
to be configured to send `Access-Control-Allow-Origin` headers in
order to permit [Cross-Origin Resource Sharing].  If you set it to
`*`, resource sharing will be allowed to any origin.  Or, you could
set it to, e.g., `api.example.com` to limit sharing to a particular
domain.  This variable is only used if **docassemble** is running on
[Docker].

## <a name="incoming mail domain"></a>E-mail domain of the site

If you use the [e-mail receiving] feature, set the `incoming mail
domain` to whatever e-mail domain will direct e-mail to the
**docassemble** server configured to perform the `all` or `mail`
services.

{% highlight yaml %}
incoming mail domain: mail.example.com
{% endhighlight %}

The [`interview_email()`] function will then return an e-mail address
with `@mail.example.com` at the end.

If `incoming mail domain` is not specified, the value of
[`external hostname`] will be used.

## <a name="cert install directory"></a>Location of SSL certificates

The `cert install directory` directive indicates the directory where
the web server expects SSL certificates to reside.  By default, this
is `/etc/ssl/docassemble`, but you can change it to wherever the web
server will look for SSL certificates.  This is only applicable if you
are using HTTPS.

In a [multi-server arrangement] or [Docker], a [supervisor] process
will run as root upon startup that will copy files from the [`certs`]
directory to the `cert install directory` and set appropriate file
permissions on the certificates.

## <a name="log server"></a>Log server hostname

If the `log server` directive is set, **docassemble** will write log
messages to TCP port 514 on the hostname indicated by `log server`
instead of writing them to
`/usr/share/docassemble/log/docassemble.log` (or whatever other
directory is set in [`log`]).

## <a name="redis"></a>Redis server location

By default, **docassemble** assumes that the [Redis] server is located
on the same server as the web server.  You can designate a different
[Redis] server by setting the `redis` directive:

{% highlight yaml %}
redis: redis://192.168.0.2
{% endhighlight %}

The `redis` directive needs to be written in the form of a
[redis URI].

## <a name="rabbitmq"></a>RabbitMQ server location

By default, **docassemble** assumes that the [RabbitMQ] server is located
on the same server as the web server.  You can designate a different
[RabbitMQ] server by setting the `rabbitmq` directive:

{% highlight yaml %}
rabbitmq: amqp://guest@192.168.0.2//
{% endhighlight %}

The `rabbitmq` directive needs to be written in the form of an [AMQP
URI].

## <a name="imagemagick"></a><a name="pdftoppm"></a>Image conversion

By default, **docassemble** assumes that you have [ImageMagick] and
pdftoppm installed on your system, and that they are accessible
through the commands `convert` and `pdftoppm`, respectively.  If you
do not have these applications on your system, you need to set the
configuration variables to null:

{% highlight yaml %}
imagemagick: Null
pdftoppm: Null
{% endhighlight %}

If you have the applications, but you want to specify a particular
path, you can set the path using the configuration variables:

{% highlight yaml %}
imagemagick: /usr/local/bin/convert
pdftoppm: /usr/local/bin/pdftoppm
{% endhighlight %}

## <a name="pacpl"></a><a name="avconv"></a>Sound file conversion

By default, **docassemble** assumes that you have pacpl (the
[Perl Audio Converter] and/or [avconv] installed on your system, and
that they are accessible through the commands `pacpl` and
`avconv`, respectively.  If you do not have these applications on
your system, you need to set the configuration variables to null:

{% highlight yaml %}
pacpl: Null
avconv: Null
{% endhighlight %}

You can also set these variables to tell **docassemble** to use a
particular path on your system to run these applications.

If you have [ffmpeg] instead of [avconv], you can do:

{% highlight yaml %}
avconv: ffmpeg
{% endhighlight %}

## <a name="libreoffice"></a><a name="pandoc"></a>Document conversion

**docassemble** requires that you have [Pandoc] installed on your
system.  It assumes that it can be run using the command `pandoc`.
If you need to specify a different path, you can do so in the configuration:

{% highlight yaml %}
pandoc: /opt/pandoc/bin/pandoc
{% endhighlight %}

By default, **docassemble** assumes that you have [LibreOffice]
installed on your system, and that it is accessible through the
command `libreoffice`.  If you do not have LibreOffice on your system,
you need to set the configuration variable to null:

{% highlight yaml %}
libreoffice: Null
{% endhighlight %}

You can also use this configuration variable to set a different path
for the application.  There are different versions of [LibreOffice]
that go by different names:

{% highlight yaml %}
libreoffice: soffice
{% endhighlight %}

## <a name="pdfa"></a>Producing PDF/A files

If you want the [PDF] files produced by interviews on your server to be
in [PDF/A] format, you can set this as a default:

{% highlight yaml %}
pdf/a: True
{% endhighlight %}

The default is `False`.  The setting can also be made on a
per-interview basis by setting the [`pdf/a` features setting].

## <a name="maximum image size"></a>Limiting size of uploaded images

If your users upload digital photos into your interviews, the uploads
may take a long time.  Using the [`maximum image size` field modifier]
or the [`maximum image size` interview feature], you can cause your
users' web browsers to reduce the size of your images before uploading
them.  For example, if `maximum image size` is set to 1200, then the
image will be reduced in size if it is taller or wider than 1200
pixels.

Note that the image file type of the uploaded file may be changed to
[PNG] during the conversion process.  Different browsers behave
differently.

If you would like to set a site-wide default value for the maximum
image size, you can use the `maximum image size` configuration
directive:

{% highlight yaml %}
maximum image size: 1200
{% endhighlight %}

This is just a default value; it can be overridden for a given
interview using the [`maximum image size` interview feature] and it
can be overridden for a given field using the
[`maximum image size` field modifier].  To override the setting in
order to allow image uploads of any resolution, use `None` as the
override value.

## <a name="timezone"></a>Setting the time zone

Functions like [`as_datetime()`] that deal with dates will use a
default time zone if an explicit timezone is not supplied.  If you set
the `timezone` directive to something like `America/Los_Angeles`, this
will be used as the default time zone.  Otherwise, the default time
zone will be set to the time zone of the server.

{% highlight yaml %}
timezone: America/Los_Angeles
{% endhighlight %}

## <a name="pypi"></a>Sharing packages on PyPI

If you want users of your server to be able to publish packages to
[PyPI] from the [packages folder] of the [Playground], set `pypi` to `True`:

{% highlight yaml %}
pypi: True
{% endhighlight %}

You can also tweak the operation of **docassemble**'s interaction with
[PyPI] by setting the following optional directives (which you should
never need to do):

{% highlight yaml %}
pypi url: https://pypi.python.org/pypi
pypirc path: /var/www/.pypirc
{% endhighlight %}

The `pypi url` directive refers to the repository to use for publishing.
It should not have a trailing slash.

The `pypirc path` directive refers to the file where the repository
URL will be stored.  You may need to edit this if you run
**docassemble** on a non-standard operating system.

## <a name="oauth"></a>Facebook, Twitter, Google, and Azure login

If you want to enable logging in with Facebook, Twitter, Google, or Microsoft
Azure, you will need to tell **docassemble** your [OAuth2] keys for
these services:

{% highlight yaml %}
oauth:
  facebook:
    enable: True
    id: 423759825983740
    secret: 34993a09909c0909b9000a090d09f099
  google:
    enable: True
    id: 23123018240-32239fj28fj4fuhf394h3984eurhfurh.apps.googleusercontent.com
    secret: DGE34gdgerg3GDG545tgdfRf
  twitter:
    enable: True
    id: Iweh63ReKfOCttaUBE3t27TET
    secret: hfieegGgrht5re3hfhsRGStYUbDDAgerergrggSDGHtrErE7rf
  azure:
    enable: True
    id: e378beb1-0bfb-45bc-9b4b-604dcf640c87
    secret: UwHEze20pzSO+lvywJOjcos3v7Kd6Y7tsaCYTG7Panc=
{% endhighlight %}

You can disable these login methods by setting `enable` to `False` or
by removing the configuration entirely.

For more information about how to obtain these keys, see the
[installation] page's sections on [Facebook], [Twitter], [Google], and
[Azure].

## <a name="googledrive"></a>Google Drive configuration

To enable the [Google Drive synchronization] feature, add
a `googledrive` entry to your [`oauth`](#oauth) configuration with
your [OAuth2] keys for [Google Drive].

{% highlight yaml %}
oauth:
  googledrive:
    enable: True
    id: 23123018240-32239fj28fj4fuhf394h3984eurhfurh.apps.googleusercontent.com
    secret: DGE34gdgerg3GDG545tgdfRf
{% endhighlight %}

For more information about obtaining these keys, see the 
[Google Drive]({{ site.baseurl }}/docs/installation.html#google drive)
section of the [installation] page.

Note that in [YAML], dictionary keys must be unique.  So you can
only have one `ouath:` line in your configuration.  Put all of your
[OAuth2] configuration details (for Google logins, Google Drive
integration, etc.) within a single `oauth` directive.

## <a name="github"></a>GitHub configuration

To enable the [GitHub integration] feature, add
a `github` entry to your [`oauth`](#oauth) configuration with
your [OAuth2] keys for [GitHub].

{% highlight yaml %}
oauth:
  github:
    enable: True
    id: 78df98b2573io5d78a1b
    secret: 75dc98473847a7c938f8beeee87f322fcb980232
{% endhighlight %}

For more information about obtaining these keys, see the 
[GitHub integration]({{ site.baseurl }}/docs/installation.html#github)
section of the [installation] page.

## <a name="twilio"></a>Twilio configuration

There are several features of **docassemble** that involve integration
with the [Twilio] service, including the [`send_sms()`] function for
sending text messages, the [text messaging interface] for interacting
with interviewees through text messaging, and the [call forwarding]
feature for connecting interviewees with operators over the phone.

These features are enabled using a `twilio` configuration directive.
Here is an example:

{% highlight yaml %}
twilio:
  sms: True
  voice: True
  account sid: ACfad8e668d876f5473fb232a311243b58
  auth token: 87559c7a427c25e34e20c654e8b05234
  number: "+12762410114"
  dispatch:
    color: docassemble.base:data/questions/examples/buttons-code-color.yml
    doors: docassemble.base:data/questions/examples/doors.yml
  default interview: docassemble.demo:data/questions/questions.yml
{% endhighlight %}

The `sms: True` line tells **docassemble** that you intend to use the
text messaging features.

The `voice: True` line tells **docassemble** that you intend to use the
[call forwarding] feature.

The `account sid` is a value you copy and paste from your [Twilio]
account dashboard.

The `auth token` is another value you copy and paste from your
[Twilio] account dashboard.  This is only necessary if you intend to
use the [`send_sms()`] function or the [phone login] feature.

The `number` is the phone number you purchased.  The phone number
must be written in [E.164] format.  This is the phone number with
which your users will exchange [SMS] messages.

The `dispatch` configuration allows you to direct users to different
interviews.  For example, with the above configuration, you can tell
your prospective users to "text 'color' to 276-241-0114."  Users who
initiate a conversation by sending the SMS message "help" to the
[Twilio] phone number will be started into the
`docassemble.base:data/questions/examples/sms.yml` interview.

The `default interview` configuration allows you to set an interview
that will be used in case the user's initial message does not match up
with a `dispatch` entry.  If you do not set a `default interview`, the
global [`default interview`] will be used.  If you want unknown
messages to be ignored, set `default interview` to `null`.

### <a name="multiple twilio"></a>Multiple Twilio configurations

You can use multiple [Twilio] configurations on the same server.  You
might wish to do this if you want to advertise more than one [Twilio]
number to your users.  You can do this by specifying the `twilio`
directive as a list of dictionaries, and giving each dictionary a
`name`.  In this example, there are two configurations, one named
`default`, and one named `bankruptcy`:

{% highlight yaml %}
twilio:
  - name: default
    sms: True
    voice: True
    account sid: ACfad8e668d876f5473fb232a311243b58
    auth token: auth token: 87559c7a427c25e34e20c654e8b05234
    number: "+12762410114"
    default interview: docassemble.base:data/questions/examples/sms.yml
    dispatch:
      color: docassemble.base:data/questions/examples/buttons-code-color.yml
      doors: docassemble.base:data/questions/examples/doors.yml
    default interview: docassemble.demo:data/questions/questions.yml
  - name: bankruptcy
    sms: True
    voice: False
    account sid: ACfad8e668d876f5473fb232a311243b58
    auth token: auth token: 87559c7a427c25e34e20c654e8b05234
    number: "+12768571217"
    default interview: docassemble.bankruptcy:data/questions/bankruptcy.yml
    dispatch:
      adversary: docassemble.base:data/questions/adversary-case.yml
      chapter7: docassemble.base:data/questions/bankruptcy.yml
{% endhighlight %}

When you call [`send_sms()`], you can indicate which configuration
should be used:

{% highlight python %}
send_sms(to='202-943-0949', body='Hi there!', config='bankruptcy')
{% endhighlight %}

This will cause the message to be sent from 276-857-1217.

If no configuration is named `default`, the first configuration will
be used as the default.  The [call forwarding] feature uses the
default configuration.

## <a name="brute force"></a>Protecting against multiple login attempts

By default, users who unsuccessfully log in are blocked after 10
failed attempts.  This threshold can be configured with `attempt
limit`.

The time period for blocking defaults to 86,400 seconds (one day).
The number of seconds of blocking can be configured with `ban period`.

When you use the [phone login] feature, the user needs to enter a 5
digit code that they receive via SMS.  The number of digits in this
code can be configured with `verification code digits`.  The code is
only valid for a limited period of time.  This period of time defaults
to 180 seconds and is configurable with `verification code timeout`.

{% highlight yaml %}
attempt limit: 5
ban period: 3600
verification code digits: 6
verification code timeout: 360
{% endhighlight %}

## <a name="loop limit"></a><a name="recursion limit"></a>Infinite loop protection

Since **docassemble** allows you to write code in a declarative
fashion, it needs to do a lot of looping and recursion.  If you make a
mistake in your [interview logic] and use circular reasoning, you may
send **docassemble** into an infinite loop.  Sometimes these infinite
loops can be detected and a warning raised, but other times they are
hard to detect because even deliberate code could loop or recurse for
a long time.  Thus, **docassemble** has hard limits on the amount of
looping and recursion it will do.  By default, these limits are set to
500 loops and 500 recursions.  If you get an error that "there appears to
be an infinite loop" or "there appears to be a circularity," then
these limits were exceeded.  If you want to change these limits on a
global level in your system, you can include use the `loop limit` and
`recursion limit` directives:

{% highlight yaml %}
loop limit: 600
recursion limit 600
{% endhighlight %}

It is important that some reasonable limit be in place, because if the
server is in development mode, an infinite loop could result in the
memory of the machine being exceeded, which could
cause the system to crash.

You can also change these limits on a per-interview basis with the
[`loop limit` and `recursion limit` features]

# <a name="get_config"></a>Adding your own configuration variables

Feel free to use the configuration file to pass your own variables to
your code.  To retrieve their values, use the [`get_config()`] function from
[`docassemble.base.util`]:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
code: |
  trello_api_key = get_config('trello api key')
{% endhighlight %}

[`get_config()`] will return `None` if you ask it for a value that does
not exist in the configuration.

The values retrieved by [`get_config()`] are the result of importing the
[YAML] in the configuration file.  As a result, the values may be
text, lists, or dictionaries, or any nested combination of these
types, depending on what is written in the configuration file.

It is a good practice to use the configuration file to store any
sensitive information, such as passwords and API keys.  This allows
you to share your code on [GitHub] without worrying about redacting it
first.

# <a name="alternatelocation"></a>Using a configuration file in a different location

If you want **docassemble** to read its configuration from a location
other than `/usr/share/docassemble/config/config.yml`, you can set the
`DA_CONFIG_FILE` environment variable to another file location.  You
might want to do this if you have multiple virtual hosts, each running
a different [WSGI] application on a single server.

Note that the configuration file needs to be readable and writable by
the web server, but should not be readable by other users of the
system because it may contain sensitive information, such as Google
and Facebook API keys.

[VoiceRSS]: http://www.voicerss.org/
[Flask]: http://flask.pocoo.org/
[YAML]: https://en.wikipedia.org/wiki/YAML
[LaTeX]: http://www.latex-project.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[installation]: {{ site.baseurl }}/docs/installation.html
[upgrades]: {{ site.baseurl }}/docs/installation.html#upgrade
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[interview]: {{ site.baseurl }}/docs/interviews.html
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[Flask]: http://flask.pocoo.org/
[language and locale settings]: {{ site.baseurl }}/docs/language.html
[user login system]: {{ site.baseurl }}/docs/users.html
[interview logic]: {{ site.baseurl }}/docs/logic.html
[protection]: http://flask-wtf.readthedocs.org/en/latest/csrf.html
[cross-site request forgery]: https://en.wikipedia.org/wiki/Cross-site_request_forgery
[document]: {{ site.baseurl }}/docs/documents.html
[functions]: {{ site.baseurl }}/docs/functions.html
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[ISO-639-3]: https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
[GitHub]: https://github.com/
[Perl Audio Converter]: http://vorzox.wix.com/pacpl
[pip]: https://en.wikipedia.org/wiki/Pip_%28package_manager%29
[list of language codes]: http://www.voicerss.org/api/documentation.aspx
[supervisor]: http://supervisord.org/
[S3]: {{ site.baseurl }}/docs/docker.html#persistent s3
[Azure blob storage]: {{ site.baseurl }}/docs/docker.html#persistent azure
[Amazon S3]: https://aws.amazon.com/s3/
[avconv]: https://libav.org/avconv.html
[ffmpeg]: https://www.ffmpeg.org/
[Google Maps Geocoding API]: https://developers.google.com/maps/documentation/geocoding/intro
[Amazon EC2]: https://aws.amazon.com/ec2/
[EC2]: https://aws.amazon.com/ec2/
[Docker]: {{ site.baseurl }}/docs/docker.html
[fully qualified domain name]: https://en.wikipedia.org/wiki/Fully_qualified_domain_name
[`exit`]: {{ site.baseurl }}/docs/questions.html#exit
[`leave`]: {{ site.baseurl }}/docs/questions.html#leave
[`progress` modifier]: {{ site.baseurl }}/docs/modifiers.html#progress
[`word()`]: {{ site.baseurl }}/docs/functions.html#word
[`set_language()`]: {{ site.baseurl }}/docs/functions.html#set_language
[`currency_symbol()`]: {{ site.baseurl }}/docs/functions.html#currency_symbol
[`currency`]: {{ site.baseurl }}/docs/fields.html#currency
[field]: {{ site.baseurl }}/docs/fields.html#fields
[special variable `speak_text`]: {{ site.baseurl }}/docs/special.html#speak_text
[`get_config()`]: {{ site.baseurl }}/docs/functions.html#get_config
[`docassemble.demo`]: {{ site.baseurl }}/docs/installation.html#docassemble.demo
[`docassemble.webapp`]: {{ site.baseurl }}/docs/installation.html#docassemble.webapp
[`docassemble.webapp.create_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[`create_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[`docassemble.wsgi`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble.wsgi
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`root`]: #root
[Pandoc]: http://johnmacfarlane.net/pandoc/
[LibreOffice]: https://www.libreoffice.org/
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[scheduled task]: {{ site.baseurl }}/docs/background.html#scheduled
[enabled]: {{ site.baseurl }}/docs/background.html#enabling
[`as_datetime()`]: {{ site.baseurl }}/docs/functions.html#as_datetime
[`pytz`]: http://pytz.sourceforge.net/
[`speak_text`]: {{ site.baseurl }}/docs/special.html#speak_text
[call forwarding]: {{ site.baseurl }}/docs/livehelp.html#phone
[`send_sms()`]: {{ site.baseurl }}/docs/functions.html#send_sms
[text messaging interface]: {{ site.baseurl }}/docs/sms.html
[Twilio]: https://twilio.com
[Redis]: http://redis.io/
[RabbitMQ]: https://www.rabbitmq.com/
[AMQP URI]: https://www.rabbitmq.com/uri-spec.html
[redis URI]: https://www.iana.org/assignments/uri-schemes/prov/redis
[`os locale`]: #os locale
[ImageMagick]: http://www.imagemagick.org/
[Debian]: https://www.debian.org/
[`voicerss`]: #voicerss
[E.164]: https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers
[SMS]: https://en.wikipedia.org/wiki/Short_Message_Service
[SQLAlchemy]: http://www.sqlalchemy.org/
[PostgreSQL]: https://www.postgresql.org/
[Packages]: {{ site.baseurl }}/docs/packages.html
[fork]: https://en.wikipedia.org/wiki/Fork_(software_development)
[initial database setup]: {{ site.baseurl }}/docs/installation.html#setup
[Facebook]: {{ site.baseurl }}/docs/installation.html#facebook
[Twitter]: {{ site.baseurl }}/docs/installation.html#twitter
[Google]: {{ site.baseurl }}/docs/installation.html#google
[Azure]: {{ site.baseurl }}/docs/installation.html#azure
[invited by an administrator]: {{ site.baseurl }}/docs/users.html#invite
[`root`]: #root
[`docassemble.webapp.fix_postgresql_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/fix_postgresql_tables.py
[`docassemble.webapp.install_certs`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/install_certs.py
[`brandname`]: #brandname
[`appname`]: #appname
[PYTHONUSERBASE]: https://docs.python.org/2.7/using/cmdline.html#envvar-PYTHONUSERBASE
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[`cert install directory`]: #cert install directory
[HTTPS]: {{ site.baseurl }}/docs/docker.html#https
[startup process]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[URI]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
[`azure`]: #azure
[`s3`]: #s3
[`s3cmd`]: http://s3tools.org/s3cmd
[Facebook, Twitter, Google, or Azure]: #oauth
[`certs`]: #certs
[`log`]: #log
[locale]: https://docs.python.org/2/library/locale.html
[phonenumbers]: https://github.com/daviddrysdale/python-phonenumbers
[`secretkey`]: #secretkey
[`default sender`]: #default sender
[Python]: https://www.python.org/
[Celery]: http://www.celeryproject.org/
[`ocr_file()`]: {{ site.baseurl }}/docs/functions.html#ocr_file
[Tesseract]: https://en.wikipedia.org/wiki/Tesseract_(software)
[`default interview`]: #default interview
[readability statistics]: https://pypi.python.org/pypi/textstat/
[Playground]: {{ site.baseurl }}/docs/playground.html
[packages folder]: {{ site.baseurl }}/docs/playground.html#packages
[Vim]: http://www.vim.org/
[Vim bindings option]: https://codemirror.net/demo/vim.html
[CodeMirror]: http://codemirror.net/
[e-mail receiving]: {{ site.baseurl }}/docs/background.html#email
[`external hostname`]: #external hostname
[`dispatch`]: #dispatch
[list of available interviews]: #dispatch
[Google Cloud Translation API]: https://cloud.google.com/translate/
[`.geolocate()`]: {{ site.baseurl }}/docs/objects.html#Address.geolocate
[`interview_email()`]: {{ site.baseurl }}/docs/functions.html#interview_email
[favicon]: https://en.wikipedia.org/wiki/Favicon
[ICO]: https://en.wikipedia.org/wiki/ICO_(file_format)
[optical character recognition]: https://en.wikipedia.org/wiki/Optical_character_recognition
[PyPI]: https://pypi.python.org/pypi
[load balancer]: {{ site.baseurl }}/docs/scalability.html
[forwards]: {{ site.baseurl }}/docs/docker.html#forwarding
[Google Drive synchronization]: {{ site.baseurl }}/docs/playground.html#google drive
[GitHub integration]: {{ site.baseurl }}/docs/packages.html#github
[OAuth2]: https://oauth.net/2/
[Google Drive]: https://drive.google.com
[Mailgun]: https://www.mailgun.com/
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
[phone login]: #phone login
[`twilio`]: #twilio
[Google Authenticator]: https://en.wikipedia.org/wiki/Google_Authenticator
[Authy]: https://authy.com/
[privileges]: {{ site.baseurl }}/docs/roles.html
[bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[PDF/A]: https://en.wikipedia.org/wiki/PDF/A
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[`pdf/a` features setting]: {{ site.baseurl }}/docs/initial.html#pdfa
[Jinja2]: http://jinja.pocoo.org/docs/2.9/
[Flask]: http://flask.pocoo.org/
[`interviews.html`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/templates/pages/interviews.html
[`start.html`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/templates/pages/start.html
[HTML]: https://en.wikipedia.org/wiki/HTML
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[`javascript` features setting]: {{ site.baseurl }}/docs/initial.html#javascript
[`css` features setting]: {{ site.baseurl }}/docs/initial.html#css
[start page]: #dispatch
[GET request]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
[`global css`]: #global css
[`global javascript`]: #global javascript
[alembic]: http://alembic.zzzcomputing.com/en/latest/
[CSRF protection]: http://flask-wtf.readthedocs.io/en/stable/csrf.html
[referer header]: https://en.wikipedia.org/wiki/HTTP_referer
[jQuery]: https://jquery.com/
[`$( document ).ready`]: https://api.jquery.com/ready/
[`$.get()`]: https://api.jquery.com/jquery.get/
[`.html()`]: https://api.jquery.com/html/
[`maximum image size` field modifier]: {{ site.baseurl }}/docs/fields.html#maximum image size
[`maximum image size` interview feature]: {{ site.baseurl }}/docs/initial.html#maximum image size
[`loop limit` and `recursion limit` features]: {{ site.baseurl }}/docs/initial.html#loop limit
[region name]: http://docs.aws.amazon.com/general/latest/gr/rande.html
[Bootstrap]: http://getbootstrap.com/
[inverted navbar]: https://getbootstrap.com/docs/3.3/components/#navbar-inverted
[Bootswatch]: https://bootswatch.com/
[live help]: {{ site.baseurl }}/docs/livehelp.html
[`bootstrap theme` feature]: {{ site.baseurl }}/docs/initial.html#bootstrap theme
[`inverse navbar` feature]: {{ site.baseurl }}/docs/initial.html#inverse navbar
[`map_of()`]: {{ site.baseurl }}/docs/functions.html#map_of
[decorations]: {{ site.baseurl }}/docs/modifiers.html#decoration
[image buttons]: {{ site.baseurl }}/docs/fields.html#image button
[MySQL]: https://en.wikipedia.org/wiki/MySQL
[PNG]: https://en.wikipedia.org/wiki/Portable_Network_Graphics
[customizing]: #start page template
[`interview_list()`]: {{ site.baseurl }}/docs/functions.html#interview_list
[`interview_menu()`]: {{ site.baseurl }}/docs/functions.html#interview_menu
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
