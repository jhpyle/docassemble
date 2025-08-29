---
layout: docs
title: System-wide configuration
short_title: Configuration
---

# <a name="configfile"></a>Location of the configuration file

**docassemble** reads its configuration directives from a [YAML] file,
which is located in `/usr/share/docassemble/config/config.yml`. If you
are using [Docker] with [S3], [S3]-compatible object storage, or
[Azure blob storage], **docassemble** will attempt to copy the
configuration file from your [S3] bucket or [Azure blob storage]
container before starting.

# <a name="edit"></a>How to edit the configuration file

The configuration file can be edited through the web application by
any user with `admin` privileges. The editing screen is located on
the menu under "Configuration."  After the configuration [YAML] is
saved, the web application is restarted.

Some Configuration directives do not fully take effect until the
entire system is restarted, in which case you would need to [`docker
stop`] and then [`docker start`] your [Docker] container.

You can also edit the configuration file directly on the file system.
You may need to do so if the web application becomes inoperative due
to a problem with the configuration.

If you are using [Docker] and you try to edit
`/usr/share/docassemble/config/config.yml` on the file system, keep in
mind that under some conditions the `config.yml` file may be
overwritten by a file located in another place. If you are using [S3]
or [Azure blob storage], the version of `config.yml` located in the
cloud always overwrites the local copy, so you should edit
`config.yml` using the cloud provider's web interface while the
container is stopped, and then start the container again. If you are
not using [S3] or [Azure blob storage], the [Docker] container's
initialization script will copy `config.yml` from
`/usr/share/docassemble/backup/config.yml`. If you are using a Docker
volume for [data storage], you can stop the container and edit this
file in the volume, then start the container.

After editing the `config.yml` file manually, you can restart the web
application by running `supervisorctl start reset`.

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
  port: null
  table prefix: null
secretkey: 28asflwjeifwlfjsd2fejfiefw3g4o87
default title: docassemble
default short title: doc
mail:
  username: null
  password: null
  server: localhost
  default sender: '"Administrator" <no-reply@example.com>'
default interview: docassemble.demo:data/questions/default-interview.yml
language: en
locale: en_US.utf8
default admin account:
  nickname: admin
  email: admin@example.com
  password: password
voicerss:
  enable: False
  key: ae8734983948ebc98239e9898f998432
  dialects:
    en: us
    es: mx
    fr: fr
  voices:
    en: Amy
    es: Juana
    fr: Axel
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
on production servers. The default is `True`.

{% highlight yaml %}
debug: True
{% endhighlight %}

Setting `debug` to `True` enables the following features:

* The "Source" button in the web app, which shows the [YAML] source code used
  to generate the current question, an explanation of the path the
  interview took to get to the current question, and [readability
  statistics] for the question and the help text.
* Viewing [Markdown] source in document attachments.

This can be overridden using the [`debug` feature].

Note that even if `debug` is `False`, the "Source" button will still
be present when running interviews in the [Playground]. This is
because the [Playground] is a development tool, not a means of
deploying interviews in production. For more information on how to
install your interviews as packages, see the [Packages] section.

Note that if you set `debug` to `True`, then the sample interviews
that come packaged with **docassemble** in the `docassemble.base` and
`docassemble.demo` packages will not be accessible to ordinary users
unless you choose to set `allow demo: True`. Note that default `default
interview` is initially set to
`docassemble.base:data/questions/default-interview.yml`, so if you set
`debug: False`, you should change `default interview` to one of your
own interviews.

## <a name="development site is protected"></a>Whether error messages should appear in the web browser

By default, error messages that relate to the YAML source code display
in the browser if the user is logged in and has `admin` or `developer`
privileges, but otherwise they only display in the `docassemble.log`
file. If you have a development server with [`debug`] set to `True`
that is not accessible to the internet, you might wish for these error
messages to display in the browser even if the user is anonymous or
does not have `admin` or `developer` privileges. If so, you can set
`development site is protected` to `True`, and then all users will see
these informational error messages.

{% highlight yaml %}
development site is protected: True
{% endhighlight %}

## <a name="allow demo"></a>Allowing sample interviews in production mode

By default, when `debug` is `False`, users without the privileges of
`admin` or `developer` cannot run the sample interviews in the
`docassemble.base` and `docassemble.demo` packages. If you would like
to allow users to run these interviews, you can set `allow demo` to `True`.

{% highlight yaml %}
allow demo: True
{% endhighlight %}

## <a name="enable playground"></a>Enabling the Playground

By default, the [Playground] is available, even when [`debug`] is
false. You can disable the [Playground] by setting:

{% highlight yaml %}
enable playground: False
{% endhighlight %}

When `enable playground` is false, administrators and developers will
not be able to access the [Playground] or its associated features, and
users will not be able to use [Playground] interviews.

## <a name="enable sharing playgrounds"></a>Enable users to use each others' Playgrounds

By default, administrators and developers have a private [Playground]
that only they can access. If you want to enable administrators and
developers to access each other's playgrounds, you can set `enable
sharing playgrounds` to true:

{% highlight yaml %}
enable sharing playgrounds: True
{% endhighlight %}

The default is false.

When enabled, the dropdown menu on the Playground page that is used to
access Playground "projects" will have an additional menu item,
[Browse Other Playgrounds], which can be used to enter the Playgrounds
of other users who have `admin` or `developer` privileges.

When `enable sharing playgrounds` is true, all users with `admin` or
`developer` privileges will have read and write access to other users'
Playgrounds. Therefore, this feature should only be used if the
developers using the server trust each other.

## <a name="collect statistics"></a>Allow statistics collection

If you set `collect statistics` to `True`, then **docassemble** will
use [Redis] to keep track of the number of interview sessions
initiated.

{% highlight yaml %}
collect statistics: True
{% endhighlight %}

The default is `False`.

## <a name="allow log viewing"></a>Allowing the viewing of logs

By default, a user with `admin` or `developer` privileges can view log
files by going to Logs from the menu. To disable this feature, set
`allow log viewing` to `False`.

{% highlight yaml %}
allow log viewing: False
{% endhighlight %}

## <a name="developer can install"></a>Whether users with developer accounts can install packages

By default, any user with `admin` or `developer` privileges can use
the Package Management page and install Playground packages on the
system. If you want those features to be available only to users with
`admin` privileges, set `developer can install` to `False`.

{% highlight yaml %}
developer can install: False
{% endhighlight %}

## <a name="root owned"></a>Whether files on the server are owned by root

By default, the **docassemble** Configuration and packages can be
updated through the web interface. Accordingly, the Configuration
file and the Python packages are owned by the `www-data` user.

However, if you set `root owned` to `True`, and you also set `allow
upgrading`, `enable playground`, and `allow configuration editing` ,
then as extra security, files that no longer need to be editable by
`www-data` will be owned by `root` instead of `www-data`.

{% highlight yaml %}
root owned: True
{% endhighlight %}

## <a name="package protection"></a>Allowing developers to install the same package

By default, users with `developer` [privileges] have ownership over
the packages they directly install, and other developers cannot create
packages by the same name. If you want to allow developers to work on
the same packages, set the `package protection` directive to `False`.

{% highlight yaml %}
package protection: False
{% endhighlight %}

## <a name="root"></a>Path to web application

Set the `root` directive if you have configured **docassemble** to run
from a sub-location on your web server. The default is `/`.

{% highlight yaml %}
root: /da/
{% endhighlight %}

The value of `root` depends on how you configured your web server
during [installation]. If the [WSGI] application runs from the URL
`https://docassemble.example.com/da/`, set `root` to `/da/`. Always
use a trailing slash.

If the [WSGI] application runs from the root of your web server (e.g.,
https://docassemble.example.com/), do not set this directive, or set
it to `/`.

## <a name="url root"></a>URL of application

The directive `url root` indicates the part of the URL that comes
before the [`root`].

{% highlight yaml %}
url root: http://example.com
{% endhighlight %}

It is normally not necessary for **docassemble** to know how it is
being accessed from the web, because the URL is provided to the web
application with every HTTP request.

However, there are some circumstances when **docassemble** code runs
outside the context of an HTTP request. For example, if you have a
[scheduled task] that uses [`send_sms()`] to send a text message with
a media attachment, the URL for the media attachment will be unknown
unless `url root` is set correctly in the configuration.

You need to make sure [`url root`] is set correctly if you use [Auth0]
logins or you use any of the [live help] features.

If you correctly specified [`DAHOSTNAME`] and
[`BEHINDHTTPSLOADBALANCER`] (if your server is behind a proxy that
provides SSL termination) when you first started **docassemble**, then
[`url root`] should be correct.

[`url root`] should match up with what you see in the location bar
when you access the server.

## <a name="root redirect url"></a>Redirecting the root of the server

By default, if the user accesses the root URL of the server (which is
`/` unless configured differently using [`root`]), the user is
redirected to:

* The URL indicated by `root redirect url`, if it is defined in the
  Configuration, but if it is not defined then the user is redirected
  to
* Their current interview, if they have started one, but if they have
  not started an interview already, then they are directed to
* The [`default interview`], if it is defined, but if it is not
  defined then the user is redirected to
* A list of available interviews, if [`dispatch`] is set up, but if
  not then the user is redirected to
* A factory default interview
  (`docassemble.base:data/questions/default-interview.yml`).

If you want the user to be directed to some other URL, you can define
the `root redirect url` directive:

{% highlight yaml %}
root redirect url: https://example.com/site/intro.html
{% endhighlight %}

In this example, if the user access the root path, they will be
redirected to a web site.

The `root redirect url` can also be a relative path:

{% highlight yaml %}
root redirect url: /site/intro.html
{% endhighlight %}

This can be useful if you want to operate a static web site on the
same domain as your **docassemble** server. To do this, you will need
to configure your web server to handle the `/site/` path, or operate
**docassemble** on a non-standard port and set up a reverse proxy that
redirects traffic to the non-standard port.

## <a name="dispatch"></a>Interview shortcuts

The `dispatch` directive allows users to start interviews with
user-friendly URLs like `https://example.com/start/legal`.

{% highlight yaml %}
dispatch:
  legal: docassemble.demo:data/questions/questions.yml
  madlibs: docassemble.base:data/questions/examples/madlibs.yml
{% endhighlight %}

A `dispatch` directive is a lookup table; it must be structured as a
[YAML] dictionary where the keys are shortcut names and the values are
interview names.

In the above example, the URL shortcuts `/start/legal` and
`/start/madlibs` are enabled.

In addition, when you define the [`dispatch`] directive, your users
can see a list of available interviews by going to the URL `/list` on
the site. They will see a page like this:

{% include image.html alt="Interview list" src="interviewlist.png" class="maybe-full-width" %}

If you want to take advantage of the `/start/` shortcuts but you do
not want the interview listed in the interview list, set `unlisted:
True` in the [`metadata`] of the interview.

The `/list` URL accepts a URL parameter `tag`. If `tag=estates`, then
`/list` will only list interviews where `estates` is one of the
[`tags`] in the interview [`metadata`].

You can also control whether an interview appears in the `/list` by
adding the [`required privileges`] specifier to the interview
[`metadata`].

If you would like to embed the list of interviews into another web
site, you can send a [GET request] to `/list?embedded=1` to obtain a
snippet of [HTML]. For example, the [HTML] snippet might look like
this:

{% highlight html %}
<ul class="dastart">
  <li><a href="/interview?i=docassemble.demo%3Adata%2Fquestions%2Fquestions.yml">Demonstration interview</a></li>
  <li><a href="/interview?i=docassemble.base%3Adata%2Fquestions%2Fexamples%2Fmadlibs.yml">Mad libs</a></li>
</ul>
{% endhighlight %}

On your web site, you can embed this into the body of a page. You can
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
order to control the various parts of the [HTML] response. Some things
to note about this example:

* The place where you want the interview list to appear is designated
  by `<div id="interviews"></div>`.
* The part between `<style>` and `</style>` is optional and simply
  demonstrates how the list of interviews can be styled. The [CSS]
  commands could also be put in a separate [CSS] file.
* The part that retrieves the interview list is the [JavaScript] call
  to [`$.get()`], which is between `<script type="text/javascript">` and
  `</script>`. The part that plugs the [HTML] into the screen is the
  call to [`.html()`].
* [jQuery] needs to be loaded before the call to `$.get()`. [jQuery]
  is very common on web sites, so it may already be loaded on your
  site.
* The [JavaScript] code is wrapped in a call to
  [`$( document ).ready`]. This may not be necessary on your site,
  but it can help avoid the potential problem where call to
  [`.html()`] takes place before the `<div id="interviews"></div>`
  [HTML] even exists on the screen.

You can also call `/list?json=1` to obtain a [JSON] version of the
available interviews.

By default, the main menu does not contain a link to the `/list` page,
but you can add it to the main menu using the [`show dispatch link`]
directive.

## <a name="grid classes"></a>Customization of column widths

**docassemble** uses the [Bootstrap grid system] for its mobile
responsive layout. The widths of columns that are used in various
parts of the application can be customized using the `grid classes`
directive.

The following example shows the default values.

{% highlight yaml %}
grid classes:
  user: offset-lg-3 col-lg-6 offset-md-2 col-md-8 offset-sm-1 col-sm-10
  admin: col-md-7 col-lg-6
  admin wide: col-sm-10
  vertical navigation:
    bar: offset-xl-1 col-xl-2 col-lg-3 col-md-3
    body: col-lg-6 col-md-9
    right: d-none d-lg-block col-lg-3 col-xl-2
    right small screen: d-block d-lg-none
  flush left:
    body: offset-xxl-1 col-xxl-5 col-lg-6 col-md-8
    right: d-none d-lg-block col-xxl-5 col-lg-6
    right small screen: d-block d-lg-none
  centered:
    body: offset-lg-3 col-lg-6 offset-md-2 col-md-8
    right: d-none d-lg-block col-lg-3
    right small screen: d-block d-lg-none
  label width: md-4
  field width: md-8
  grid breakpoint: md
  item grid breakpoint: md
{% endhighlight %}

`user` refers to administrative screens that end users see, like the
login screen. `admin` refers to administrative screens that only
administrators can see, like the User List. `admin wide` refers to
administrative screens that are wider than others, like the
Configuration.

The `vertical navigation`, `flush left`, and `centered` directives
refer to modes in an interview when different column widths must be
used. The default mode is `centered`. If you set `centered: False` in
the [`features`], then the `flush left` directive is used. However, if
you have a vertical navigation bar enabled in your interview, the
`vertical navigation` directive is used.

Under these directives, `body` refers to the width of the main part of
the screen. `right` refers to the width of the `right` screen part
that is positioned to the right of the `body`. On small screens, the
`right` part is invisible and the same contents appear below the
`body`, between the `under` part (if any) and the `post` part (if
any). The `right small screen` directive refers to the size of this
version of the `right` screen part. Under `vertical navigation`, the
`bar` refers to the width of the vertical navigation bar.

The `label width`, `field width`, `grid breakpoint`, and `item grid
breakpoint` are not classes, but rather parts of classes. The actual
classes used will be prefixed with `col-` or `offset-`, depending on
the context. The default values of `md-4` and `md-8` mean that when
labels and fields appear side-by-side, the width of the labels is half
of the width of the fields, and below the `md` breakpoint, the labels
appear above the fields. The `grid breakpoint` is a default value for
the [`grid` field modifier]. It indicates the breakpoint in
[Bootstrap]'s grid system when the side-by-side arrangement should be
shown. The default is `md`. Likewise, the `item grid breakpoint` is a
default value for the [`item grid` field modifier].

## <a name="alert html"></a><a name="alert container html"></a>Customization of alerts

When the front end needs to alert the user about something, it places
a [Bootstrap alert] at the top of the screen. The HTML of these alerts
can be customized using `alert html` an `alert container html`.

{% highlight yaml %}
alert html: |
  <div class="da-alert alert alert-%s alert-dismissible fade show" role="alert">%s<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>
alert container html: |
  <div class="datopcenter col-sm-7 col-md-6 col-lg-5" id="daflash">%s</div>
{% endhighlight %}

In `alert html`, the first `%s` represents the [Bootstrap color] of
the alert, while the second `%s` represents the HTML of the content of
the message. In `alert container html`, the `%s` represents one or
more `alert html` `<div>`s.

## <a name="customization"></a>Customization of administrative pages

When the user is interacting with an interview, the page can be
customized with a [`features`] block. If you want to customize the
appearance of other pages on the site, you can do so in the
Configuration using directives like `login page heading` or `profile
page title`.

The names of these directives have two parts: the first part is the
name of the page, and the second is the name of the aspect of the page
you wish to customize.

The available page names are:

* `start page`: the [start page] that shows a list of available interviews.
* `register page`: the page where the user registers for an account.
* `login page`: the page where the user logs in.
* `interview page`: the page that shows a list of saved interview sessions.
* `profile page`: the page where the user can edit his or her name.
* `change password page`: the page where users can change their password.
* `forgot password page`: the page where users can type in their
  e-mail address and receive an e-mail with a link to reset their password.
* `reset password page`: the page where users are directed when they
  forget their password.
* `404 page`: the page users see when they try to visit a URL that
  does not exist on the server.
* `error page`: the page users see when Flask traps a Python exception.
* `main page`: the pages of interviews. (This one is special; see below.)

The aspects of the page that can be manipulated are:

* `tab title`: the [HTML] title, which is displayed in the web browser
  tab.
* `title`: the title of the page in the navigation bar.
* `navigation bar html`: raw [HTML] tags that you can insert into the
  navigation bar. The contents will be placed inside of a `<ul>` in a
  `<div>`:
  `<div class="collapse navbar-collapse" id="danavbar-collapse"><ul class="navbar-nav ms-auto">`.
  For best results, use `<li class="nav-item">` elements containing
  `<a class="nav-link" href="#">` elements. On large screens, the
  items will appear in the navigation bar, and on small screens, the
  items will appear as menu items.
* `heading`: the large font heading that displays the title of the
  page in the main body of the page.
* `pre`: text that appears after the heading but before the rest of
  the content of a page. This is empty by default.
* `submit`: text that appears before the submit buttons on a page that
  has one or more submit buttons. This is empty by default.
* `post`: text that appears after the content of a page. This is
  empty by default.
* `footer`: text that appears at the bottom of the screen, in a 60px
  tall box with the [Bootstrap] `light` color.
* `extra css`: raw [HTML] tags that you can insert into the `<head>` of the
  page, usually to incorporate [CSS] files. This is empty by default.
* `extra javascript`: raw [HTML] tags that you can insert at the end
  of the `<body>` of the page, usually to include [Javascript] in
  `<script>` tags. This is empty by default.

All of the directives accept [HTML], except you will not want to use
[HTML] in the `tab title`, since it will not be displayed as [HTML].

Here are some examples of using these directives:

{% highlight yaml %}
start page title: Missouri interviews
start page heading: Interviews available to Missouri residents
interview page title: Your interviews
interview page heading: Interviews you have started
interview page extra css: |
  <link href="https://example.com/css/mystyles.css" rel="stylesheet">
login page pre: |
  <p>Unauthorized access to this site is <strong>strictly</strong>
  prohibited!</p>
register page extra javascript: |
  <script>
    console.log("We are registering.")
  </script>
{% endhighlight %}

You can also use these directives to provide different language to be
used depending on the user's language.

{% highlight yaml %}
start page title:
  en: Available tools
  es: Herramientas disponibles
{% endhighlight %}

If you want to include the same [CSS] or [JavaScript] files in every
page of the site, including administrative pages and interview pages,
you can use the [`global css`] and [`global javascript`] directives.

If you want to set a `footer` that is available on all pages, you can
set `global footer` instead of `start page footer` and `interview page
footer`, etc. In the context of an interview, you can set the
`footer` [screen part] to `off` in order to turn off the `global
footer` or the `main page footer`. You can also set the `main page
footer` to `off` if you have a `global footer` that you do not want to
appear during interviews.

<a name="main page pre"></a><a name="main page submit"></a><a
name="main page post"></a><a name="main page footer"></a>The
`main page` directive is special because
it relates to actual interviews, which are different from
administrative pages. The directives that work with the `main
page` prefix are:

* `main page back button label`
* `main page continue button label`
* `main page corner back button label`
* `main page exit label`
* `main page exit link`
* `main page footer`
* `main page help label`
* `main page logo`
* `main page navigation bar html`
* `main page post`
* `main page pre`
* `main page resume button label`
* `main page right`
* `main page short logo`
* `main page short title`
* `main page submit`
* `main page subtitle`
* `main page title url opens in other window`
* `main page title url`
* `main page title`
* `main page under`

You can set these when you want special content to be set by default
for various parts of the screen for all interviews running on your
server.

{% highlight yaml %}
main page post: |
  <p>This interview was sponsored in part by a grant from the Example Foundation.</p>
{% endhighlight %}

You can set the directives to a dictionary where the keys are
languages and the values are the text.

{% highlight yaml %}
main page post:
  en: |
    <p class="smallprint">This interview was sponsored in part by a grant from the Example Foundation.</p>
  es: |
    <p class="smallprint">Esta entrevista fue patrocinada en parte por una beca de la Fundación Ejemplo.</p>
{% endhighlight %}

For information about other ways to set defaults for different parts
of the screens during interviews, and what these screen parts mean,
see the [screen parts] section.

<a name="start page template"></a><a name="interview page template"></a>
There are two pages that you can customize even more extensively:

* The [start page] that shows a list of available interviews.
* The list of saved interview sessions.

For these pages, you can specify an [HTML] template to use. Use the
`start page template` and `interview page template` directives to
point to files in the "templates" directory of a package.

{% highlight yaml %}
start page template: docassemble.missouri:data/templates/my_start_page.html
interview page template: docassemble.missouri:data/templates/my_interview_page.html
{% endhighlight %}

To see what the standard templates look like, see:

* [`start.html`]
* [`interviews.html`]

You might want to use these as a starting point. Note that
**docassemble** uses [Flask], which uses [Jinja2] HTML templates.

These templates use [Jinja2] to load a standard [HTML] framework. If
you want, you can replace the entire body of the page using these
templates. However, if you do so, you may wish to include
`{% raw %}{{ extra_css }}{% endraw %}` in the `<head>` and
`{% raw %}{{ extra_js }}{% endraw %}` at the end of the `<body>`.
On the interviews page, there is a bit of [JavaScript] that
asks the user "are you sure?" before deleting all of the interview.
The start page does not use [JavaScript].

You can also customize these pages using [CSS]. The
[HTML] elements in the standard template use some classes do nothing;
they are just placeholders for customization. For example, to
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

## <a name="allow anonymous access">Requiring login for all interviews</a>

If you want to require users to be logged in before they can run any
interviews, set `allow anonymous access` to `False`.

{% highlight yaml %}
allow anonymous access: False
{% endhighlight %}

The default is `True`. You can also forbid anonymous access on an
interview-by-interview basis using [`required privileges`].

## <a name="administrative interviews">Administrative interviews</a>

The `administrative interviews` directive adds hyperlinks to
interviews (or other things) to the main menu.

Suppose you have two interviews, `inspect.yml` and `manage.yml`, that
you use frequently. You can list them in the [Configuration] as
follows:

{% highlight yaml %}
administrative interviews:
  - docassemble.missouri:data/questions/inspect.yml
  - docassemble.missouri:data/questions/manage.yml
{% endhighlight %}

Then, there will be hyperlinks in the menu to:

* `/interview?i=docassemble.missouri:data/questions/inspect.yml&new_session=1`
* `/interview?i=docassemble.missouri:data/questions/manage.yml&new_session=1`

The labels for these hyperlinks will be taken from the [`metadata`] of
the interview. The label will be the [`short title`] as specified in
the [`metadata`], or if that is not defined the label will be the
[`title`].

These interview links will always be shown in the main menu; however,
a link to an interview will not be shown if the user is currently in a
session of that interview.

If you want the links in the menu to appear only for users in a given
role, you can set the [`required privileges for listing`] specifier in
the [`metadata`] to a list of [privileges]. In that case, only users
who have one of the listed privileges will see the link in the menu.
If a [`required privileges for listing`] specifier does not exist, the
[`required privileges`] specifier will be used to determine if the
link in the menu is shown.

The titles and privileges that will be used for purposes of the menu
can be overridden by specifying an item in the `administrative
interviews` list in the form of a [YAML] dictionary instead of the
name of the interview file. For example:

{% highlight yaml %}
administrative interviews:
  - interview: docassemble.missouri:data/questions/inspect.yml
    title: Inspect
    required privileges:
      - admin
      - advocate
  - interview: docassemble.missouri:data/questions/manage.yml
    title:
      en: Inspect
      es: Inspeccionar
    required privileges:
      - admin
{% endhighlight %}

When listing an item in dictionary form, only the `interview` key is
required. The `title` key can be set to a single name, or to a [YAML]
dictionary where the keys are languages and the values are the titles
to be used for that language.

The hyperlinks from the menu will contain the `&new_session=1` URL
parameter, which means that a new session will be started every time
the user clicks the interview. In many situations, you will not want
the clicking of the link from the menu to result in a proliferation of
interview sessions. You may want to set up the `metadata` of your
administrative interviews as follows:

{% highlight yaml %}
metadata:
  title: Manager
  required privileges:
    - admin
  sessions are unique: True
  hidden: True
{% endhighlight %}

The [`sessions are unique`] specifier means that there will only ever
be one session per user. This means that if the user already has a
session in the interview, the `&new_session=1` directive will not
result in a new session being started; instead, the original session
will be resumed.

The [`hidden`] specifier means that sessions in this interview will be
hidden on the [My Interviews] page.

It is a good practice to make your "administrative" interviews simple
so that they feel more like control panels than interviews. For
example, you might want to have a single screen with buttons created
using [`action_button_html()`]. Or if you need multiple screens, you
can have a variable to keep track of the current screen, and then use
[`menu_items`] and [`url_action()`] to provide the user with a menu
for navigating from screen to screen.

The `administrative interviews` directive can also be used to add URLs
of your own choosing to the menu. Provide a dictionary with keys for
`url` and `title`:

{% highlight yaml %}
administrative interviews:
  - url: https://secret.example.com/
    title: Secret Site
{% endhighlight %}

As with `interview` entries, you can specify the title in different
languages, and you can limit the appearance of the menu item based on
the user's privileges. For example:

{% highlight yaml %}
administrative interviews:
  - url: https://portal.example.com/
    title:
      en: Portal
      es: El Portal
    required privileges:
      - admin
{% endhighlight %}

## <a name="resume interview after login"></a>Always go back to the current interview after logging in

If a user starts an interview as an anonymous user and then registers
or logs in, they generally be taken to the [My Interviews] page.
However, if the interview session they started is their only interview
session, then the [My Interviews] page is skipped and the user is sent
right back into the interview they had started.

The [My Interviews] page is shown to users with more than one session
because it resolves confusion for users who may have visited the
interview for purposes of resuming an existing interview session, but
finding themselves not logged in, they log in. Some users may expect
to resume the session they just started; other users may expect to
resume their original session. By sending users to the My Interviews
page, **docassemble** lets users know that they have two sessions and
can make a choice.

If you want users to always be redirected to the session they just
started, you can set `resume interview after login` to `True`.

{% highlight yaml %}
resume interview after login: True
{% endhighlight %}

The default value is `False`.

If `resume interview after login` is set to `True`, users who start
out conducting an interview as an anonymous user and then log in will
not be sent to the [My Interviews] page, but will be redirected back
into the interview they just started.

## <a name="auto resume interview"></a>Automatically resuming or starting an interview

The [My Interviews] page at `/interviews` normally displays a list of
the user's interview sessions. By default, users are directed to
`/interviews` when they log in.

If your server only offers a single interview, for example,
`docassemble.eviction:data/questions/defend.yml`, you might not want
your users to look at a list of sessions; you might simply want them
to resume their existing session, if they have one, or start a new
session in that interview.

To accomplish this, you can set the following:

{% highlight yaml %}
auto resume interview: docassemble.eviction:data/questions/defend.yml
{% endhighlight %}

When this is set, then whenever a user logs in, the user
will be redirected to their first interview session involving the
`docassemble.eviction:data/questions/defend.yml` interview. Or, if
they have no such session, a new session will

If you set an `auto resume interview`, you may wish to set [`show
interviews link`] to `False` if the [My Interviews] menu is not useful
on your server.

## <a name="page after login"></a>Customizing the page that appears after login

By default, the user is directed to the [My Interviews] page after
logging in or registering. This can be customized with the `page
after login` directive:

{% highlight yaml %}
page after login: profile
{% endhighlight %}

In this example, the user will be directed to the "Profile" page after
logging in or registering. See the documentation for the [`url_of()`]
function to see what names to use for each page of the web site. (The
name you give is effectively passed to [`url_of()`].)  Instead of
passing the name of a page of a web site, you can also pass a URL
beginning with `http://` or `https://`, or a path beginning with `/`,
such as `/start/taxes`, in which case the user will be taken to that
page on the server.

You can also set up different pages for users with different
[privileges]:

{% highlight yaml %}
page after login:
  - admin: config
  - developer: playground
{% endhighlight %}

In this example, users with [privileges] of `admin` will be directed to
the [Configuration] page, while users with privileges of `developer`
will be directed to the [Playground].

If a user has [privileges] of both `admin` and `developer`, the user
will be directed to `config`. Each item in `page after login` is
processed in order, and the first match is used. If no items match,
the user is directed to "My Interviews."

If a `next` parameter is present on the login or register page, the
user will be redirected to that location instead of the `page after
login`.

## <a name="javascript defer"></a>JavaScript loading

The `javascript defer` setting should be set to `True` for faster
JavaScript loading. This causes the `<script>` tags to have the
`defer` attribute set.

{% highlight yaml %}
javascript defer: True
{% endhighlight %}

For backwards compatibility, it is set to `False` by default, in case
you have `raw global javascript` that depends on jQuery and that will
fail if scripts are loaded with `defer`.

## <a name="global css"></a><a name="global javascript"></a><a name="raw global css"></a><a name="raw global javascript"></a>CSS and Javascript customization

You can use the [`javascript` features setting] and the
[`css` features setting] to modify the [JavaScript] and [CSS] for a
particular interview.

By using `global javascript` and `global css`, you can apply
[JavaScript] and [CSS] on a more global level. These directives allow
you to include [JavaScript] and [CSS] files in every interview and
also in the [start page] and the page showing the list of interviews.
The directive should refer to files located in the "static" directory
of a package:

{% highlight yaml %}
global css: docassemble.missouri:data/static/missouri.css
global javascript: docassemble.missouri:data/static/missouri.js
{% endhighlight %}

If you have more than one [CSS] file or more than one [JavaScript]
file, you can use these directives to refer to a list of files:

{% highlight yaml %}
global css:
  - docassemble.missouri:data/static/missouri.css
  - docassemble.midwest:data/static/look_and_feel.css
{% endhighlight %}

You can also refer to files on the internet:

{% highlight yaml %}
global css: https://example.com/css/site_style.css
global javascript: https://example.com/js/tracker.js
{% endhighlight %}

These [JavaScript] and [CSS] files are loaded after the other
[JavaScript] and [CSS] files on the page.

The [`global css`] and [`global javascript`] directives can only refer
to file names; if you want to write raw `<link>`, `<meta>`, or
`<script>` content, you can use the `raw global css` and `raw global
javascript` directives:

{% highlight yaml %}
raw global css: |
  <meta property="og:title" content="Child Custody Interview" />
raw global javascript: |
  <script defer>
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
    ga('create', 'UA-77777777-1', 'auto');
  </script>
{% endhighlight %}

The `raw global css` content is inserted into the `<head>` of the
page, while the `raw global javascript` is inserted into the end of
the `<body>` of the page. There is no requirement that the `raw
global css` content relate to [CSS], or that that the `raw global
javascript` content relate to [JavaScript]; the names simply refer to
the conventions about where [CSS] and [JavaScript] are typically
placed in the [HTML] page.

You should set the `defer` attribute in any `<script>` tags
you include in `raw global javascript` if `javascript defer` (see the
previous section) is set to `True`. If you don't set the `defer`
attribute, your code may run in an unpredictable order relative to the
loading of other files.

## <a name="bootstrap theme"></a>Bootstrap theme

Using the `bootstrap theme` directive, you can change the look and
feel of your site's web interface by substituting a non-standard [CSS]
file in place of the standard [CSS] file used by [Bootstrap].

{% highlight yaml %}
bootstrap theme: docassemble.demo:data/static/lumen.min.css
{% endhighlight %}

You can also refer to files on the internet:

{% highlight yaml %}
bootstrap theme: https://bootswatch.com/5/minty/bootstrap.min.css
{% endhighlight %}

There are many alternative [Bootstrap] themes available on
[Bootswatch]. (Use [Bootstrap] 5 themes.) Note that you may need to
use apply additional [CSS] changes in order to get a [Bootstrap] theme
to work with **docassemble**. For example, by default **docassemble**
assumes that the navigation bar is 56 pixels in height. But if your
theme makes the navigation bar 66 pixels tall, you will need to add
the following styles:

{% highlight css %}
.da-pad-for-navbar {
    padding-top: 76px;
}
@media (min-width: 576px) {
    body.dasignature.da-pad-for-navbar {
	    padding-top: 76px;
    }
}
.da-top-for-navbar {
    top: 76px;
}
{% endhighlight %}

Also, some of the colors that **docassemble** uses in the navigation
bar might not work well with every theme. You can override these
colors with [CSS] like the following:

{% highlight css %}
span.daactivetext       { color: yellow;         }
span.daactivetext:hover { color: #ffff99;        }
i.da-chat-active           { color: #45bf41;        }
i.da-chat-active:hover     { color: #55cf51;        }
i.da-chat-inactive         { color: #4f4f4f;        }
i.da-chat-inactive:hover   { color: #5f5f5f;        }
{% endhighlight %}

These styles refer to the yellow "Help" button that appears when
question-specific help is available, the green icons that appear in
the navigation bar when [live help] features are available, and the
grey color that these icons become when [live help] is no longer
available.

You can also control the [Bootstrap] theme on a per-interview basis
with the [`bootstrap theme` feature]. You can also alter [CSS] on a
per-interview basis using the [`css` features setting].

## <a name="inverse navbar"></a>Inverted Bootstrap navbar

By default, **docassemble** uses [Bootstrap]'s "dark" (formerly known
as "inverted") style of navigation bar so that the navigation bar
stands out from the white background. If you do not want to use the
inverted navbar, set the `inverse navbar` to `False`.

{% highlight yaml %}
inverse navbar: False
{% endhighlight %}

You can also control this on a per-interview basis with the
[`inverse navbar` feature].

## <a name="auto color scheme"></a>Automatic color scheme switching

By default, if the OS or browser indicates that the user is using a
"dark" color scheme, **docassemble** will activate the "dark" color
scheme in Bootstrap by adding `data-bs-theme="dark"` to the `<html>`
element. (This does not apply if the interview is embedded in a
`<div>`.)

If you do not want the "dark" color scheme to be activated
automatically, set `auto color scheme` to `False`. The default value
is `True`.

{% highlight yaml %}
auto color scheme: False
{% endhighlight %}

## <a name="button colors"></a>Button color

The colors of buttons in the **docassemble** user interface can be
customized using [Bootstrap colors].

You can choose a different [Bootstrap] color than the default by
setting one or more items under the `button colors` directive:

{% highlight yaml %}
button colors:
  "continue": primary
  "answer yes": primary
  "answer no": secondary
  "answer maybe": warning
  "clear": warning
  "back": link
  "register": primary
  "new session": primary
  "leave": warning
  "url": link
  "restart": warning
  "refresh": success
  "signin": info
  "exit": danger
  "logout": danger
  "send": primary
  "download": primary
  "review": secondary
  "add": secondary
  "edit": secondary
  "delete": danger
  "undelete": info
  "reorder": info
  "navigation bar login": primary
  "help": info
  "question help": info
  "back to question": info
  "labelauty": primary
  "labelauty nota": primary
  "labelauty aota": primary
{% endhighlight %}

The above example lists the default colors. The meanings of the keys
in this dictionary are as follows:

* `continue` refers to Continue buttons and buttons that act like
  Continue buttons.
* `answer yes` refers to the "Yes" button in a `yesno` question.
* `answer no` refers to the "No" button in a `yesno` question.
* `answer maybe` refers to the "Maybe" button in a `yesnomaybe` question.
* `clear` refers to the "Clear" button in a `signature` question.
* `back` refers to the "Back" button when the `question back button`
  feature is used.
* `register` refers to the button that is generated when the value of
  an item in a `buttons` list is `register`.
  refers to `register`
* `new session` refers to the button that is generated when the value of
  an item in a `buttons` list is `register`.
* `leave` refers to the button that is generated when the value of
  an item in a `buttons` list is `register`.
* `restart` refers to the button that is generated when the value of
  an item in a `buttons` list is `restart`.
* `refresh` refers to the button that is generated when the value of
  an item in a `buttons` list is `refresh`.
* `signin` refers to the button that is generated when the value of
  an item in a `buttons` list is `signin`.
* `exit` refers to the button that is generated when the value of
  an item in a `buttons` list is `exit`.
* `logout` refers to the button that is generated when the value of
  an item in a `buttons` list is `logout`.
* `send` refers to the button for sending an e-mail from the
  `attachment` user interface.
* `download` refers to the button for sending an e-mail from the
  `attachment` user interface.
* `review` refers to the buttons that are generated as part of a
  `review` screen. This is also customizable with `review button
  color` under `features`.
* `add` refers to the button that is generated by the `.add_action()`
  method of a `DAList`.
* `edit` refers to the button for editing an item in a `table`.
* `delete` refers to the button for deleting an item in a `table` or
  `list collect`.
* `undelete` refers to the button for un-deleting an item in a `list
  collect`.
* `reorder` refers to the buttons for changing the order of an item in
  a `table`.
* `navigation bar login` refers to the "Sign in" button that appears
  in the upper right corner of the screen if `login link style` is set
  to `button`.
* `help`: refers to the question mark icons that appear when there is
  `help` text related to an option in a list of options.
* `question help`: refers to the button that is available when
  the `question help button` feature is being used and there is `help`
  text associated with the current `question`.
* `back to question`: refers to the "Back to question" button that
  appears when the user is viewing the "help" tab on a `question`
  screen.
* `labelauty`: refers to the default color of a selected item in a
  radio button or checkbox list. Labelauty is the name of the JQuery
  add-on that is used to style radio buttons and checkboxes.
* `labelauty nota`: refers to the default color of a selected "None of
  the above" item in a checkbox list.
* `labelauty aota`: refers to the default color of a selected "All of
  the above" item in a checkbox list.

One reason to set `button colors` is to avoid biasing the user toward
clicking a particular button. For example you might want to set `no:
primary` so that the "No" selection is the same colors as the "Yes"
selection. Or you might want to set `exit: secondary` because the
default color of `danger` might discourage users from clicking a
button to leave the interview.

If you simply want different colors, then before editing `button
colors`, you may wish to consider creating your own [Bootstrap theme]
in which the concepts of `primary`, `warning`, `danger`, `success`,
etc. are associated with different colors than blue, yellow, red, and
green.

## <a name="button style"></a>Button style

There are two button styles: `normal` and `outline`. The normal style
uses [Bootstrap] styles like `btn btn-success`. The outline style
uses styles like `btn btn-outline-success`. The default is `normal`.

{% highlight yaml %}
button style: outline
{% endhighlight %}

## <a name="button size"></a>Button size

By default, most buttons in the **docassemble** user interface are
regular size [Bootstrap] buttons. If you want the buttons to be
"large" size, set the following in your configuration:

{% highlight yaml %}
button size: large
{% endhighlight %}

If you want the buttons to be "small" size, set the following in your configuration:

{% highlight yaml %}
button size: small
{% endhighlight %}

The default value is `medium`.

## <a name="footer css class"></a>Default CSS class for the footer

By default, if you use a footer, the footer has the CSS class
`bg-secondary-subtle`, in addition to the class `dafooter`. If you
would like to use a different class instead of `bg-secondary-subtle`,
you can set this class using `footer css class`.

{% highlight yaml %}
footer css class: bg-dark text-white
{% endhighlight %}

## <a name="table css class"></a>Default CSS class for Markdown tables

By default, when a [Markdown] table is converted to HTML, `<table>`
elements will be given the [CSS] class `table table-striped`. This
can be varied by setting the [`table css class`] specifier on the
[`question`] (or using the [`default screen parts`] or [`metadata`]).
If you want to set a global default for this setting, you can set
`table css class` in the [Configuration]:

{% highlight yaml %}
table css class: table table-bordered
{% endhighlight %}

You can also use `table css class` to specify a class for the
`<thead>` within the table. If you set `table css class` to `table
table-bordered, thead-dark`, then the `<table>` will have the class
`table table-bordered` and the `<thead>` will have the class
`thead-dark`.

## <a name="default icons"></a>Using standard sets of icons

[Font Awesome] is enabled on all pages. **docassemble** includes the
free version [Font Awesome]. This allows you to refer to [Font
Awesome] icons using raw HTML.

In addition, **docassemble** allows you to use Google's [Material
Icons] in your raw HTML. Since the [Material Icons] are just a font,
they are enabled by default and there is no configuration directive to
enable the use of [Material Icons].

You can also use [Font Awesome] or [Material Icons] for [decorations]
and [inline icons], without writing any raw [HTML].

By default, when you include [decorations], or you [include inline
icons], you can only refer to image files that you [have predefined]. An
inline image reference that does not have a corresponding predefined
image will appear literally (e.g., `:cow:`). However, if you set the
`default icons` configuration directive to `font awesome`, then
references to any images that you have not predefined will be treated
as references to icons in the [Font Awesome] collection.

{% highlight yaml %}
default icons: font awesome
{% endhighlight %}

Then you can have an interview like this:

{% include side-by-side.html demo="font-awesome" %}

The "solid" style of the icons ([CSS] class `fas`) is used by default.

If you want to use icons in a different style, you can add a special
prefix to your icon reference, writing, e.g., `:far-fa-circle:`
instead of `:circle:`. This will result in `<i class="far
fa-circle"></i>` instead of `<i class="fas fa-circle"></i>`.

To use a different [Font Awesome] style by default, set the `font
awesome prefix` directive. For example, to use the "brand" style by
default, you can use:

{% highlight yaml %}
font awesome prefix: fab
{% endhighlight %}

Alternatively, you can use the [Material Icons] for icon references
that are not predefined image files:

{% highlight yaml %}
default icons: material icons
{% endhighlight %}

Note that when you set `default icons`, no validation is performed to
ensure that the image you reference actually exists in [Font Awesome]
or the [Material Icons].

## <a name="favicon"></a>Custom favicon in browser tab

The icon in the browser tab is known as a [favicon]. This is the icon
associated with the web application. By default, **docassemble** uses
the **docassemble** logo for this icon.

If users "pin" your application to their device's main menu, this icon
will be used to create the resulting icon. Microsoft, Apple, and
Google have their own conventions for doing this.

In order to "brand" your application in a custom way, create a square
logo and go to
[https://realfavicongenerator.net](https://realfavicongenerator.net) in
order to generate [favicon] files from it. Upload a square image that
is at least 512x512 in size. In addition to uploading your file, you
will need to make some choices about different colors that should be
used in different circumstances. At the end, you will download a Zip
file containing a number of graphics files and other files:

* `android-chrome-192x192.png`
* `android-chrome-512x512.png`
* `apple-touch-icon.png`
* `browserconfig.xml`
* `favicon-16x16.png`
* `favicon-32x32.png`
* `favicon.ico`
* `mstile-150x150.png`
* `safari-pinned-tab.svg`
* `site.webmanifest`

If any of the above files is missing, your [favicon] will probably
still work in most circumstances. The most important file is
`favicon.ico`, a special graphics file in Microsoft's [ICO] format.

To instruct **docassemble** to use these files for the [Favicon], you
need to set a directive in the configuration like this:

{% highlight yaml %}
favicon: docassemble.abcincorporated:data/static
{% endhighlight %}

This indicates that **docassemble** should use the [Favicon] files
located in the `data/static` folder of the **docassemble** add-on
package called `docassemble.abcincorporated`, which is installed on
your server. For more information about how **docassemble** uses
packages, see the [Packages] section.

To create a package (called, for example,
`docassemble.abcincorporated`), you can use the Playground. First,
upload the [Favicon] files to the "Static" folder of the Playground.
Then go to the "Packages" folder of the Playground and create ("Add")
a new package called `abcincorporated`. Under "Static files," select
all of the [Favicon] files you uploaded. Click "Save" to save the
package definition, then click the "Install" button at the bottom of
the screen to install the package on your server.

If you are creating package outside of the Playground, you can store
your [Favicon] files in a subfolder under `data/static`. For example,
you can create a subfolder called `favicon`. Then your Configuration
would contain:

{% highlight yaml %}
favicon: docassemble.abcincorporated:data/static/favicon
{% endhighlight %}

In addition to providing you with a Zip file containing the above
files, the above web site will instruct you to place particular
`<link>` and `<meta>` tags in the HTML of your site. **docassemble**
does this for you automatically, so you can ignore most of this.
However, two of the lines are important. The will look like this:

{% highlight html %}
<link rel="mask-icon" href="/safari-pinned-tab.svg?v=2" color="#698aa7">
<meta name="msapplication-TileColor" content="#da532c">
<meta name="theme-color" content="#83b3dd">
{% endhighlight %}

Note the `color` in the first line and the `content` in the second and
third lines. Then add the following three lines to your
configuration, corresponding to the above three lines:

{% highlight yaml %}
favicon mask color: "#698aa7"
favicon tile color: "#da532c"
favicon theme color: "#83b3dd"
{% endhighlight %}

If you do not specify `favicon mask color`, `favicon tile color`, or
`favicon theme color`, your custom [favicon] will still work, but
**docassemble** will choose colors for you. (The colors above are the
defaults.)

Note that most web browsers will store a cache of the [Favicon], so
that when you make a change to your app's [Favicon], it may seem that
your change is not working when it actually is. The way that web
browsers cache the [Favicon] is different from the way they cache
other resources, so even if you do a forced reload of the page, you
will still see the cached [Favicon].

**docassemble** tries to mitigate this problem by appending `?v=`
followed by the version number of the package referenced in `favicon`
to the URLs for the [Favicon] files. That way, when you install a new
version of your package, web browsers will think that the [Favicon]
has changed, and they will download a new version. (The server
actually ignores the `v` URL parameter, but browsers assume it is
significant.) **docassemble** assumes the version number is the value
of the variable `__version__` defined in the `__init__.py` file of the
package. The Playground sets this variable when it creates a package,
but if you are creating packages on your own, you will need to update
this variable manually.

You can also manually specify a `v` parameter by specifying `favicon
version`:

{% highlight yaml %}
favicon version: 2
{% endhighlight %}

You can then change this number every time you want the web browser to
download a new [Favicon].

Note that
[https://realfavicongenerator.net](https://realfavicongenerator.net)
also has an option for setting the version number of your files. You
may need to use this as well to force applications to retrieve new
icons for your files. This adds, for example, `?v=2` to URLs
referenced in the `browserconfig.xml` and `site.webmanifest` URLs,
much in the same way the above `favicon version` directive will result
in `?v=2` being appended to URLs in the HTML source.

Because of caching, it can be difficult to test changes to your
[Favicon]. One way to check to see if the server is delivering the
correct [Favicon] is to manually visit the [Favicon] file by entering
the `/favicon.ico` address in your browser location bar, and then
forcing a page reload. If you see the correct image in the browser,
then the server is delivering the right file, but you are just not
seeing it because of a caching issue.

Note that if you have set the [`root`] directive (if your
**docassemble** site at `https://example.com/something/` instead of
`https://example.com/`), you will need to account for this when you
generate the [favicon] files using the above web site. This is
important because the `manifest.json` and `browserconfig.xml` files
contain URL references. If your site is at `/something/`, then
`manifest.json` will need to refer to
`"/something/android-chrome-192x192.png"` instead of
`"/android-chrome-192x192.png"`.

## <a name="robots"></a>Controlling the robots.txt file

By default, **docassemble** discourages web crawlers by returning the
following in response to a request for the `/robots.txt` file:

{% highlight text %}
User-agent: *
Disallow: /
{% endhighlight %}

If you want to set a permissive `/robots.txt` file, for example if you
want [social meta tags] to work, you can set `allow robots` to `True`.

{% highlight yaml %}
allow robots: True
{% endhighlight %}

Then, `/robots.txt` will return:

{% highlight text %}
User-agent: *
Disallow:
{% endhighlight %}

If you want to customize the `/robots.txt` file, leave `allow robots`
unset and set `robots` to a reference to a file in a package.

{% highlight yaml %}
robots: docassemble.missouri:data/static/robots.txt
{% endhighlight %}

Then the contents of the referenced file will be returned in response
to a request for the `robots.txt` file.

## <a name="social"></a>Social meta tags

You can control the [meta tags] on **docassemble** pages by setting the
`social` directive.

{% highlight yaml %}
social:
  description: |
    A site that will solve your legal problems
  image: docassemble.missouri:data/static/logo.png
  twitter:
    description: |
      The greatest legal services site in Missouri.
    site: "@missourilaw"
    creator: "@missourilaw"
    image: docassemble.missouri:data/static/logofortwitter.png
  fb:
    app_id: "1447731792112118"
    admins: "556880902, 547009392"
  og:
    description: |
      The greatest legal services site in Missouri.
    image: https://missourilaw.org/images/missourilaw.jpg
{% endhighlight %}

The resulting HTML will include the following in the `<head>`:

{% highlight html %}
<meta name="description" content="A site that will solve your legal problems">
<meta name="image" content="https://docassemble.missourilaw.org/packagestatic/docassemble.missouri/logo.png?v=1.0.2">
<meta itemprop="name" content="Missouri Law: Interviews">
<meta itemprop="description" content="A site that will solve your legal problems">
<meta itemprop="image" content="https://docassemble.missourilaw.org/packagestatic/docassemble.missouri/logo.png?v=1.0.2">
<meta name="twitter:card" content="summary">
<meta name="twitter:description" content="The greatest legal services site in Missouri.">
<meta name="twitter:site" content="@missourilaw">
<meta name="twitter:creator" content="@missourilaw">
<meta name="twitter:image" content="https://docassemble.missourilaw.org/packagestatic/docassemble.missouri/logofortwitter.png?v=1.0.2">
<meta name="twitter:title" content="Missouri Law: Interviews">
<meta name="og:title" content="Missouri Law: Interviews">
<meta name="og:description" content="The greatest legal services site in Missouri.">
<meta name="og:image" content="https://missourilaw.org/images/missourilaw.jpg">
<meta name="og:url" content="https://docassemble.missourilaw.org/list">
<meta name="og:locale" content="en_US">
<meta name="og:site_name" content="Missouri Law">
<meta name="og:type" content="website">
<meta name="fb:app_id" content="1447731792112118">
<meta name="fb:admins" content="556880902, 547009392">
{% endhighlight %}

In this example, the server is `https://docassemble.missourilaw.org`,
the [`brandname`] is `Missouri Law`, the version of the
`docassemble.missouri` package is 1.0.2, and the page that was
accessed was the [list of available interviews] (`/list`).

The `image` references are special because if you set them to a
reference to a static file in a package, they will be replaced with a
full URL to that file. Alternatively, you can provide a full URL.

Note that the `itemprop="name"`, `twitter:title`, and `og:title`
fields were populated automatically. Since the title of the page
varies from page to page, you can't set this value in the
Configuration. For administrative pages, these fields are set to the
[`brandname`] followed by a colon, followed by the name of the page.
Note that these page names are [customizable](#customization). For
example, to change the name from "Interviews" to "Get Started," you
could set `start page title: Get Started`.

Likewise, `og:url` field is automatically set to the URL of the page,
and this cannot be changed.

By default, `twitter:card` is set to `summary`, `og:site_name` is set
to the value of [`brandname`], `og:locale` is determined from the
[`locale`], and `og:type` is set to `website`. These can be
specifically overridden.

The `social` directive sets server-wide defaults. Administrative
pages will reflect these tags. On interview pages, these defaults can
be overridden using the `social` specifier under the interview
[`metadata`].

Note that by default, the **docassemble** server disallows web
crawling by returning a restrictive `/robots.txt` file. That means
that as a practical matter, sites will not be able to consume your
[meta tags]. The `/robots.txt` file can be [customized](#robots) so
that your [meta tags] are accessible.

## <a name="icon size"></a>Icon size

The size of icons in [decorations] and in [image buttons] is not
specified in [CSS]. To change these sizes, you can edit these
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
[`leave`] command. (See the [Setting Variables] section.)

For example:

{% highlight yaml %}
exitpage: https://example.com/pages/thankyou.html
{% endhighlight %}

## <a name="logoutpage"></a>Page after logout

The `logoutpage` directive contains the default URL to which a
logged-in user should be directed after logging out. By default, the
user is redirected to the login page after logging out.

{% highlight yaml %}
logoutpage: https://example.com/pages/comeagain.html
{% endhighlight %}

## <a name="db"></a>SQL database

The `db` section of the Configuration indicates where **docassemble**
can find the SQL database in which to store users' answers, login
information, and other information.

The `db` directives should be treated as read-only. The primary way
you would adjust your database configuration is when starting a new
server for the first time. At that time, you can set [Docker]
configuration variables [`DBHOST`], [`DBNAME`], [`DBUSER`],
[`DBPASSWORD`], and other related variables in order to specify that a
particular SQL database should be used. For example, you would set
these environment variables if you were using a cloud-based managed
database system like [RDS].

The password should only contain alphanumeric characters. The special
characters `_`, `~`, `/`, `-`, `^`, `*`, `?`, and `!` may be used.

Changing the `db` directives after you already have a working system
can easily lead to an unbootable system. You should not change the
values using the web-based front end unless you really know what you
are doing.

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: localhost
  port: 5432
  table prefix: null
  backup: True
{% endhighlight %}

The `prefix` is a [SQLAlchemy] prefix. If you use a database other
than [PostgreSQL], change this.

<a name="db host"></a>**docassemble** will connect to the SQL database
at the hostname `host` on the port `port`, and will authenticate with
the `user` and `password`. It will connect to the database called
`name`. If you want separate **docassemble** systems to share the
same database, you can set a `table prefix`.

If you are using [Docker] with [S3], [S3]-compatible object storage,
or [Azure blob storage], and you omit the `host` or set it to `null`,
then **docassemble** will automatically find the hostname of the
central SQL server in cloud storage.

The value of `backup` is only applicable if you are using [Docker] and
the `host` is off-site. If `backup` is true (which is the default),
then the SQL database will be backed up on a daily basis. You will
want to set it to `false` if backing up the SQL database could lead to
the exhaustion of hard drive space.

If you want to connect to a [PostgreSQL] server using an SSL
certificate, you can use the `ssl mode`, `ssl cert`, `ssl key`, and/or
`ssl root cert`:

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: someserver.example.com
  port: 5432
  ssl mode: require
  ssl cert: postgresql.crt
  ssl key: postgresql.key
  ssl root cert: postgresql_root.crt
{% endhighlight %}

The possible values of `ssl mode` are `disable`, `allow`,
`prefer`,`require`, `verify-ca`, and `verify-full`. This corresponds
with the `sslmode` parameter of [libpq].

The `ssl cert`, `ssl key`, and `ssl root cert` parameters correspond
with the `sslcert`, `sslkey`, and `sslrootcert` parameters of [libpq].
These parameters must refer to the names of files present in the
**docassemble** certificates directory. If you are using [S3] or
[Azure Blob Storage], these files are stored under `certs/`;
otherwise, the files must be present in
`/usr/share/docassemble/certs/` at the time the system initializes
(from there, they will be copied into other directories). For
instructions on loading your own certificates when using [Docker], see
[managing certificates with Docker]. See also the [`certs`]
Configuration directive.

After changing the `db` configuration, you need to restart the server
(typically by doing `docker stop -t 600 <containerID>` followed by
`docker start <containerID>`) in order for the change to take effect.

## <a name="sql ping"></a>Avoiding SQL errors

If your **docassemble** server runs in an environment in which
persistent SQL connections will periodically be severed, you can set
`sql ping` to `True` in order to avoid errors.

{% highlight yaml %}
sql ping: True
{% endhighlight %}

There is an overhead cost to using this, so only enable this if you
get SQL errors when trying to connect after a period of inactivity.

## <a name="variables snapshot db"></a>SQL database for storing snapshots of interview answers

You can use the [`store_variables_snapshot()`] function to save
unencrypted interview answers in [JSON] format to rows in a SQL
database. By default, the SQL database that
[`store_variables_snapshot()`] uses is the same as the database
configured with [`db`]. However, you can use a separate database
by specifying a `variables snapshot db` in your Configuration.

{% highlight yaml %}
variables snapshot db:
  name: snapshots
  user: docassemble
  password: abc123
{% endhighlight %}

The format is the same as that of [`db`]. It is recommended that you
use [PostgreSQL] for the database that stores variable snapshots,
because if you do, then **docassemble** will use the [JSONB] data type
for the [JSON] version of the interview answers, which will enable
fast and convenient querying of the data.

## <a name="appname"></a><a name="brandname"></a>Branding

The `appname` and `brandname` directives control the name of the
application in various contexts.

{% highlight yaml %}
appname: Legal Helper
brandname: Legal Helper Application
{% endhighlight %}

The `appname` is used in e-mails that are generated by the
[user login system].

The `appname` defaults to `docassemble`. The `brandname` will default
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

If you are using a [multi-server arrangement] and not using [S3],
[S3]-compatible object storage, or [Azure blob storage], this needs to
point to a central network drive.

The default value is `/usr/share/docassemble/files`.

## <a name="packages"></a>Python directory

The `packages` directive indicates the base directory into which
**docassemble** extension packages will be installed. The
[PYTHONUSERBASE] environment variable is set to this value and [pip]
is called with `--install-option=--user`. When [Python] looks for
packages, it will look here. [Python]'s default value is `~/.local`,
but **docassemble** changes it to the value of this directive, or
`/usr/share/docassemble/local` if the directive is not defined.

{% highlight yaml %}
packages: /netmount/files/docassemble/local
{% endhighlight %}

If you are using a [multi-server arrangement] and not using [S3],
[S3]-compatible object storage, or [Azure blob storage], this needs to
point to a central network drive.

## <a name="webapp"></a>Path to WSGI application

The `webapp` directive indicates the path to the [WSGI] file loaded by
the web server.

{% highlight yaml %}
webapp: /netmount/files/docassemble/webapp/docassemble.wsgi
{% endhighlight %}

**docassemble** needs to know this filename because the server needs
to reset itself after an add-on package is updated. The web server is
reset by updating the modification time of the [WSGI] file.

The default value is `/usr/share/docassemble/webapp/docassemble.wsgi`.

## <a name="certs"></a>Path to SSL certificates

The `certs` directive indicates a central location where SSL
certificates can be found. The location can be a file path, an [S3]
path (beginning with `s3://`), or an [Azure blob storage] path
(beginning with `blob://`). In most cases, you should leave
this directive alone.

You might keep your certificates on a network drive:

{% highlight yaml %}
certs: /netmount/files/docassemble/certs
{% endhighlight %}

When the server is running, it expects certificates to reside in
`/etc/ssl/docassemble`. For example, by default, the [NGINX] HTTPS
configuration contains:

{% highlight text %}
ssl_certificate /etc/ssl/docassemble/nginx.crt;
ssl_certificate_key /etc/ssl/docassemble/nginx.key;
{% endhighlight %}

The [supervisor] process executes the
[`docassemble.webapp.install_certs`] module during the [startup
process]. This module copies certificates from the location indicated
by `certs` to `/etc/ssl/docassemble` before starting the server.

The value of `certs` can be a file path, an [S3]<span></span>
[URI] (e.g., `s3://exampledotcom/certs`), or an
[Azure blob storage]<span></span> [URI] (e.g.,
`blob://youraccountname/yourcontainername/certs`). The contents of
the directory are copied to `/etc/ssl/docassemble`.

If you leave the `certs` setting undefined (which is recommended),
**docassemble** will look in `/usr/share/docassemble/certs` if the
[`s3`] and [`azure`] settings are not enabled.

If you are using [Docker] and you are not using [S3] or [Azure blob
storage], you can create a volume, copy your certificates there, and
then mount that volume as `/usr/share/docassemble/certs` when you
execute `docker run`. For more information on how to do this, see
[managing certificates with Docker].

If [`s3`] is enabled, **docassemble** will look for [S3] keys with the
prefix `certs/` in the `bucket` defined in the [`s3`] configuration.

If [`azure`] is enabled, it will look for [Azure blob storage] objects
with the prefix `certs/` in the `container` defined in the [`azure`]
configuration.

You can upload certificate files to [S3] or [Azure blob storage] using
the web interface. It is also possible to copy certificate files to S3
from the command line. For example, if you are using Linux locally,
install [`s4cmd`] (if you have not done so already):

{% highlight bash %}
apt-get install s4cmd
{% endhighlight %}

Then do:

{% highlight bash %}
s4cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.crt s3://yourbucket/certs/nginx.crt
s4cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.key s3://yourbucket/certs/nginx.key
{% endhighlight %}

If your [`s3`] configuration has `bucket: yourbucket`, then you do not
need to set a `certs` configuration, because **docassemble** will by
default look in `s3://yourbucket/certs`. However, if the certificates
are stored in another location, you can specify a different location:

{% highlight yaml %}
certs: s3://otherbucket/certificates
{% endhighlight %}

## <a name="mail"></a>E-mail configuration

**docassemble** needs to send e-mail, for example to reset people's
passwords, or to let users of a [multi-user interview] know that it is
their turn to start answering questions.

Before you set up your e-mail configuration, make sure that you are
not using the default fake e-mail address of `admin@example.com` as the
e-mail address of the administrative user. If you forget your
password, you will want to be able to reset it using the "forgot my
password" feature, which relies on e-mailing an address you can
access.

<a name="default sender"></a>If you are going to send mail, you should
at least set the `default sender` directive, which sets the return
address on any e-mails generated from **docassemble**:

{% highlight yaml %}
mail:
  default sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

In order to send e-mail, you will need to sign up with an e-mail
sending service. You can use an external [SMTP] server, or you can use
an e-mail service with an HTTP-based API. The latter is recommended
because [SMTP] is slow.

### <a name="smtp"></a>Using an external [SMTP] server

To use another [SMTP] server as the mail server, do something like:

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
have to use a separate [SMTP] server in order to send e-mail.

A free option is [Mailgun]. You can sign up with [Mailgun], provide a
credit card, configure some [DNS] entries, and then set your
configuration to something like this:

{% highlight yaml %}
mail:
  default sender: '"Example, Inc." <no-reply@mg.example.com>'
  username: 'postmaster@mg.example.com'
  password: '5a4a0c5f3da35f3bc10f0462364c26dd'
  server: 'smtp.mailgun.org'
{% endhighlight %}

### <a name="mailgun api"></a>Using the Mailgun API

Another way to send e-mail using [Mailgun] is through its API. If you
use the API, mail is sent to [Mailgun] using [HTTP], rather than
[SMTP]. This may be more reliable than [SMTP], since internet service
providers may slow down or block [SMTP] traffic as a way of protecting
against spam.

To use this method, obtain an API key from [Mailgun] and set it as the
`mailgun api key`. Also set your [Mailgun] domain as the `mailgun
domain`.

{% highlight yaml %}
mail:
  default sender: '"Example, Inc." <no-reply@mg.example.com>'
  mailgun api key: key-b21b28f6e29be1f463478238d172813e
  mailgun domain: mg.example.com
{% endhighlight %}

If necessary, you can also configure the URL used by the [Mailgun]
API. The default is `https://api.mailgun.net/v3/%s/messages.mime`.

{% highlight yaml %}
mailgun api url: https://api.mailgun.net/v3/%s/messages.mime
{% endhighlight %}

(The `mailgun domain` will be substituted in place of the `%s`.)

Mailgun domains created in their EU region have a different base URL.
To cater for this, you can  configure the URL used by the [Mailgun]
API as follows:

{% highlight yaml %}
mailgun api url: https://api.eu.mailgun.net/v3/%s/messages.mime
{% endhighlight %}

### <a name="sendgrid api"></a>Using the SendGrid API

You can send e-mail using the [SendGrid API]. First, sign up for
[SendGrid] and obtain an API key. Under `mail` in your Configuration,
set `sendgrid api key` to the API key.

{% highlight yaml %}
mail:
  default sender: '"Example, Inc." <no-reply@mg.example.com>'
  sendgrid api key: s8_MK.S.GmtjGD6krnOl4FkkPGTYe3I8fHqIi2NGZ057k7S-ZhuQfOF2ItWYBW97w6Kzu
{% endhighlight %}

### <a name="microsoft api"></a>Using the Graph API on Microsoft Azure

You can send email using the [Microsoft Graph API] on [Microsoft Azure].

* Log into the [Azure Portal].
* Go to App Registrations.
* Create a New Registration. Give it a name like "Email sending" or
  whatever you want. Setting up a Redirect URI is not necessary.
* Note the "Application (client) ID." This will need to go into your
  `mail` configuration as the `azure client id`.
* Note the "Directory (tenant) ID." This will need to go into your
  `mail` configuration as the `azure tenant id`.
* Go into API Permissions and add a permission. Select Microsoft
  Graph, then Application Permissions, then `Mail.Send`. Click "Grant
  admin consent."
* Go into Certificates & Secrets. Add a new client secret. Call it
  "Email sending secret" or whatever you want. Copy the "Value." This
  will need to go into your `mail` configuration as the `azure client
  secret`.

Then edit your Configuration and add the codes you obtained. For example:

{% highlight yaml %}
mail:
  default sender: '"Example, Inc." <no-reply@example.com>'
  azure client id: "72f3829c-f887-8273-b716-9827e727b91a"
  azure tenant id: "82392784-bced-7ee5-94fa-7326347873c4"
  azure client secret: "oj238~2jo23rj02Y3r72y9~u203r9u27yr-82082"
  default sender: '"Philadelphia Legal Assistance" <bhanson@philalegal.org>'
{% endhighlight %}

You will only be able to send mail from senders whose mailboxes your
App Registration has privileges of accessing.

### <a name="mail multiple"></a>Using multiple mail configurations

You can configure multiple mail configurations and then choose which
configuration you want to use for a particular interview or when you
call [`send_email()`].

For example, suppose that you wanted to send e-mail from an account
belonging to ABC, Inc. in one interview and send e-mail from an
account belonging to DEF, Inc. in another interview.

You could set your configuration as follows:

{% highlight yaml %}
mail:
  - default sender: '"ABC, Inc." <helpdesk@mg.abc.com>'
    sendgrid api key: s8_MK.S.GmtjGD6krnOl4FkkPGTYe3I8fHqIi2NGZ057k7S-ZhuQfOF2ItWYBW97w6Kzu
    name: abc
  - default sender: '"DEF, Inc." <info@mg.def.com>'
    mailgun api key: key-b21b28f6e29be1f463478238d172813e
    mailgun domain: mg.example.com
    name: def
{% endhighlight %}

Then, in the interview that should use ABC, Inc.'s server, you would
set the [`email config`] to `abc`

{% highlight yaml %}
metadata:
  email config: abc
{% endhighlight %}

In the interview that should use DEF, Inc.'s server, you would
set the [`email config`] to `def`

{% highlight yaml %}
metadata:
  email config: def
{% endhighlight %}

You could also specify the e-mail configuration in a call to
[`send_email()`]:

{% highlight python %}
send_email(to=recipient, sender=sales_associate, template=offer_template, config='def')
{% endhighlight %}

When you are using multiple e-mail configurations, keep in mind that
**docassemble** sometimes sends e-mail outside of the interview
context, such as user invitation e-mails, error notifications, forgot
password e-mails, etc. In these situations, **docassemble** will use
the default configuration, which is the configuration tagged with
`name: default`, or if no configuration has `default` as the `name`,
the first configuration will be used.

## <a name="default interview"></a>Default interview

If no [interview] is specified in the URL when the web browser first
connects to the **docassemble** server, the interview indicated by
`default interview` will be used. The interview needs to be specified
in "package name:relative file path" format. For example:

{% highlight yaml %}
default interview: docassemble.base:data/questions/examples/attachment.yml
{% endhighlight %}

If this directive is not set, **docassemble** will redirect to a page
showing a [list of available interviews] determined by the
[`dispatch`] directive. However, if the [`dispatch`] directive is not
defined, users will be directed to a placeholder interview,
`docassemble.base:data/questions/default-interview.yml`.

## <a name="log format"></a>Log format

Log messages written to the log files will by default contain the IP
address, interview file, session ID, and user e-mail address, in
addition to the log message itself.

The format of the log message is determined by the `log format`, the
default value of which is:

{% highlight yaml %}
log format: docassemble: ip=%(clientip)s i=%(yamlfile)s uid=%(session)s user=%(user)s %(message)s
{% endhighlight %}

If you would like to shorten the log messages, you could change it to
something like:

{% highlight yaml %}
log format: docassemble: i=%(yamlfile)s %(message)s
{% endhighlight %}

## <a name="flask log"></a><a name="celery flask log"></a>Flask log file location

**docassemble** uses the [Flask] web framework. The `flask log` and
`celery flask log` directives contain the paths to the [Flask] log
files for the web application and the [Celery] background workers,
respectively. Most errors write to the `docassemble.log` file located
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

## <a name="debug startup process"></a>Log messages during the startup process

If the web application is slow to startup after a restart (i.e., after
the Configuration is saved, or after a package is installed, you can
set `debug startup process` to `True` in order to see log messages in
the `uwsgi.log` log file showing the timing of various parts of the
web application startup process.

{% highlight yaml %}
debug startup process: True
{% endhighlight %}

The log should look something like this:

{% highlight text %}
0.000s server: starting
0.071s config: load complete
4.179s backend: starting
4.179s backend: getting email configuration
4.179s backend: finished getting email configuration
4.179s backend: configuring common functions
4.179s backend: finished configuring common functions
4.179s backend: processing translations
4.840s backend: finished processing translations
4.840s backend: obtaining cloud object
4.840s backend: finished obtaining cloud object
4.840s backend: completed
4.892s server: done importing modules
4.896s server: creating session store
4.896s server: setting up Flask
4.903s server: finished setting up Flask
4.903s server: setting up logging
4.903s server: finished setting up logging
4.903s server: getting page parts from configuration
4.903s server: finished getting page parts from configuration
5.776s server: making directories that do not already exist
5.776s server: finished making directories that do not already exist
5.776s server: building documentation
6.218s server: finished building documentation
6.218s server: entering app context
6.218s server: entering request context
6.235s server: loading preloaded interviews
6.458s server: finished loading preloaded interviews
6.458s server: copying playground modules
6.504s server: finished copying playground modules
6.504s server: deleting LibreOffice macro file if necessary
6.504s server: fixing API keys
6.504s server: starting importing add-on modules
7.490s server: finished importing add-on modules
7.490s server: running app
{% endhighlight %}

The period of four seconds at the start is taken up by loading a large
number of necessary Python modules. If your system takes much longer
than four seconds to reach `backend: starting`, your system may have
insufficient CPU or memory.

The time between `processing translations` and `finished processing
translations` can be reduced by removing unnecessary lines from the
[`words`] configuration.

The time between `finished getting page parts from configuration` and
`making directories that do not already exist` consists of loading
necessary Python functions.

The time between `starting importing add-on modules` and `finished
importing add-on modules` can be reduced by uninstalling unnecessary
add-on packages, adding `# do not pre-load` to the top of module files
that should not load when the system starts, and removing files from
the Modules folders of users' Playgrounds.

If you want to see logs of the initial system startup process (the
process that happens when you do `docker run`, see the log files
mentioned in the [Troubleshooting] section, in particular the log
files at `/var/log/supervisor/initialize*`.

Check the `worker.log` file for information about package
installation.

## <a name="language"></a><a name="dialect"></a><a name="voice"></a><a name="locale"></a>Default language, locale, dialect, and voice

These directives set the default [language and locale settings] for
the **docassemble** server.

{% highlight yaml %}
language: en
locale: en_US.utf8
dialect: us
voice: Amy
{% endhighlight %}

The `language` needs to be a lowercase [ISO-639-1] or [ISO-639-3]
code.

`language` controls the default language, which is the language that
will be used when:

* the user's browser requests a language that the **docassemble**
  server does not support, or
* **docassemble** code is running in a context where it has not been
  told what language to use.

The languages that **docassemble** supports are determined by the
[`words`] configuration. **docassemble** always supports English;
whether other languages are supported depends on whether [`words`]
files are included that provide translations for system phrases. So if
you change the `language` to `es`, you will also need to edit your
[`words`] configuration so that it includes a translation file for
Spanish words.

You can [control the
language](https://docassemble.org/docs/language.html#bpmulti) used in
an interview session by calling the [`set_language()`] function in an
[`initial`] block. You can write interviews in such a way that they
support multiple languages. For more information, see the the
[language support] section of the documentation.

The `locale` needs to be a locale name that will be accepted by
the [locale] library. The locale is primarily used for determining
the formatting of numbers and currency values. For example, some
locales use `.` to indicate decimals and some use `,`.

The locale can be changed later in Python code by calling
[`set_locale()`] followed by [`update_locale()`]. However, changing
the locale is is not [thread-safe]; this means that if two users are
using your system simultaneously, and one is in Japan and expects
currency to be in Yen, and the other is in France and expects currency
to be in Euros, the code that runs [`update_locale()`] for the French
user could cause the Japanese user to see the Euro symbol in place of
the Yen symbol in a [`question`].

The `dialect` and `voice` are only relevant for the text-to-speech
feature, which is controlled by the [special variable `speak_text`].
See the [`voicerss`] configuration for more information about
configuring this feature. The default dialect and default voice are
only used as a fallback, in case the dialect and voice cannot be
determined any other way. It is better to set the dialect and voice
using [`set_language()`] or the [`voicerss`] configuration.

## <a name="country"></a>Default country

The `country` directive sets the default country for **docassemble**.

{% highlight yaml %}
country: US
{% endhighlight %}

The country is primarily relevant for interpreting telephone numbers.
The code needs to be a valid country code accepted by the
[phonenumbers] library ([ISO 3166-1 alpha-2] format).

## <a name="os locale"></a>Operating system locale

If you are using [Docker], the `os locale` directive will set the
default operating system locale.

{% highlight yaml %}
os locale: so_SO.UTF-8 UTF-8
{% endhighlight %}

The `os locale` must exactly match one of the [locale values]
that [Ubuntu]/[Debian] recognizes. The default value is `en_US.UTF-8
UTF-8`, which is appropriate for servers in the United States.

When the server starts, the value of `os locale` is appended to
`/etc/locale.gen` (if not already there in uncommented form) and
`locale-gen` and `update-locale` are run.

After changing `os locale`, you will need to restart your container
(`docker stop -t 600 <container ID>` followed by `docker start <container ID>`).

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

Each `other os locales` value must exactly match one of the [locale
values] that [Ubuntu]/[Debian] recognizes (listed in the
`/etc/locale.gen` file on an [Ubuntu]/[Debian] system).

When the server starts, each of the `other os locales` is appended to
`/etc/locale.gen` (if not already there in uncommented form) and
`locale-gen` and `update-locale` are run.

After changing `other os locales`, you will need to restart your
container (`docker stop -t 600 <container ID>` followed by `docker
start <container ID>`).

## <a name="server administrator email"></a>E-mail address of server administrator

On [Docker], you can provide an e-mail address to the [NGINX] web
server, so that if your server has an error, users are told an
appropriate e-mail address to contact.

{% highlight yaml %}
server administrator email: support@example.com
{% endhighlight %}

## <a name="error notification email"></a>E-mail address to which error messages shall be sent

If `error notification email` is set to an e-mail address or a list of
e-mail addresses, then if any user sees an error message, the server
will try to send an e-mail notification to this e-mail address (or
addresses). If possible, the e-mail will contain the error message.

{% highlight yaml %}
error notification email:
  - jsmith@example.com
  - tjoseph@example.com
{% endhighlight %}

Information about errors is also available in the [Logs].

## <a name="suppress error notificiations"></a>Suppressing notifications about certain types of errors

If you receive error notifications that are not helpful, you can
suppress errors by the class of error by defining the `suppress error
notificiations` directive:

{% highlight yaml %}
suppress error notificiations:
  - ZeroDivisionError
  - ReadTimeout
{% endhighlight %}

This means that if the name of the class of error is
`ZeroDivisionError` or `ReadTimeout`, no notification will be sent.

## <a name="session error redirect url"></a>Redirecting user in case of session error

If the user tries to access a non-existent session, the default
behavior is to start a new session in the interview and display an
error message to the user. If you would rather redirect the user to a
different URL, you can set `session error redirect url` to the URL to
which you want to redirect users in this circumstance.

{% highlight yaml %}
session error redirect url: https://example.com/launch_page.html
{% endhighlight %}

You can set the `session error redirect url` to a template into which
the named parameters `i` and `error` can be inserted. The `i`
parameter refers to the URI-encoded interview filename, and the
`error` refers to an error message (also safe for inclusion in a URL
parameter), which will be either `answers_fetch_fail` (in case there
was an error retrieving the interview answers, such as a decryption
error) or `answers_missing` (in case no session could be found).

{% highlight yaml %}
session error redirect url: https://example.com/error_page?filename={i:s}&error_code={error:s}
{% endhighlight %}

## <a name="verbose error messages"></a>Whether error messages contain details

By default, when the user sees an error on the screen, information
about the error is shown. To turn this off, set `verbose error
messages` to `False`.

{% highlight yaml %}
verbose error messages: False
{% endhighlight %}

If you set `verbose error messages`, you should also set [`error
help`] in your interviews or set the [`error help` directive].

## <a name="error notification variables"></a>Whether to include interview variables in error notification

If `error notification variables` is set to true, then when an error
notification e-mail is sent, the interview variables will be attached
as a JSON file.

The default value is the value of [`debug`]; that is, the variables
will be included if the server is a development server, but not
included if the server is a production server.

Putting the interviews variables into a file and e-mailing them lowers
security, especially when server-side encryption is being used.

{% highlight yaml %}
error notification variables: True
{% endhighlight %}

In the case of some errors, obtaining the interview variables is not
possible; in that case, the variables will not be attached.

## <a name="error help"></a>Help text to display when there is an error

When an error happens, the user will see the error message on the
screen, which can be confusing. You can add some additional content
to this screen so that the user sees something other than the error
message:

{% highlight yaml %}
error help: |
  We are sorry, our computer has malfunctioned. Please call
  202-555-1515 for assistance, or visit our [web site](https://example.com).
{% endhighlight %}

The format of the `error help` is [Markdown].

You can also set this on a per-interview basis using [`error help`]
inside the [`metadata`].

## <a name="ubuntu packages"></a><a name="debian packages"></a>ubuntu packages to install

On [Docker], you can ensure that particular [Ubuntu] packages are
installed by providing a list of packages to the `ubuntu packages`
directive:

{% highlight yaml %}
ubuntu packages:
  - r-base
  - r-cran-effects
{% endhighlight %}

These packages will be installed when the [Docker] container starts.

For backwards compatibility, the directive `debian packages` works the
same way.

## <a name="allow non-idempotent questions"></a>Non-idempotent question check

You can set `allow non-idempotent questions: False` in order to
enforce strict idempotency of [`question`]s with generic objects,
iterators, or multiple choice selections. If an interview has
non-idempotent logic, there is a risk that variables will be set
improperly.

The `allow non-idempotent questions` directive currently defaults to
`True`, but in the future, it will default to `False`, which may break
some interviews.

To make sure you are ready for this change, set the following on your
development server:

{% highlight yaml %}
allow non-idempotent questions: False
{% endhighlight %}

Then test your interviews to see if this message is shown in the
screen at any point:

> Input not processed because the question changed. Please continue.
{: .blockquote}

A message will also be written to the logs beginning with `index: not
the same question name`.

If these messages appear, take a close look at the logic of your
interview.

Users may see this message if:

* The interview logic is non-idempotent, meaning that the user sees
  one `question`, but if they immediately refresh the screen, they see
  a different question.
* They have the interview open in more than one device, browser, or
  browser tab, and they proceed with the interview in one tab and then
  try to proceed with the interview in the other;
* You have a multi-user interview and two users have the interview
  open at the same time, and the actions of one user change the
  interview logic for the other user.

If your interviews work with `allow non-idempotent questions` set to
`False`, ist is recommended that you set `allow non-idempotent
questions` to `False` on your production server.

If a user sees this message, they can usually proceed with the
interview normally. The input they submitted before seeing the
message is discarded, but the problem should not be a permanent
problem. However, if the user continues to see the message, and it
prevents the user from proceeding, there is a flaw in the interview
logic that needs to be fixed; an immediate solution would be to set
`allow non-idempotent questions` to `True`, but the long-term solution
is to fix the logic in the interview.

## <a name="restrict input variables"></a>Restricting the browser from setting arbitrary variables

By default, the **docassemble** [front end] is designed to be flexible
for [JavaScript] developers. A POST request to `/interview` is
capable of setting arbitrary variable names in the interview answers;
the field names are simply base64-encoded variable names. This allows
[JavaScript] developers to build their own front ends or heavily
customize the standard front end.

However, when this kind of flexibility exists on the [JavaScript] side
of the application, you need to trust that your users will not try to
manipulate their interview answers. For example, if you have a
variable in your interview called `user_has_paid`, you wouldn't want
users to manipulate their web browser and set `user_has_paid` to
`True`.

If you enable `restrict input variables`, then the web browser will
only be able to set variables that are present on the current
question. What question counts as the current question depends on the
interview logic. When the browser submits input, then before any
variables are set, the interview logic is evaluated and the current
question is determined. If the incoming variables are not part of the
current question, then the input is rejected.

{% highlight yaml %}
restrict input variables: True
{% endhighlight %}

If you enable `restrict input variables`, then your interview logic
must be idempotent for all questions. Note that the `allow
non-idempotent questions` directive (despite its general-sounding
name) only enforces idempotency for questions with generic objects,
iterators, or multiple choice selections. The `restrict input
variables` is more strict; it enforces idempotency for all questions
and also prevents the browser from altering the variable names or data
types.

Enabling `restrict input variables: True` is generally a good
practice. If you want to add additional fields to a [`question`]
using [JavaScript], you can use the [`allowed to set`] modifier to
enable those field names.

## <a name="python packages"></a>Python packages to install

On [Docker], you can ensure that particular [Python] packages are
installed by providing a list of packages to the `python packages`
directive:

{% highlight yaml %}
python packages:
  - stripe
  - slackclient
{% endhighlight %}

These packages will be installed when the [Docker] container starts.

The `python packages` directive should not be used to control the
installation of packages on a machine that is part of an existing
setup (i.e., it is connecting to a populated SQL database). If you
have an existing system, the way to control package installation is
through the [Package Management] interface or the
[API](https://docassemble.org/docs/api.html#package_install).

## <a name="default admin account"></a>Default administrator account credentials

When a **docassemble** SQL database is first initialized, an
administrative user is created. By default, this user has the e-mail
address `admin@example.com` and the password `password`. As soon as the
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

You can also specify the first and last name of the admin user:

{% highlight yaml %}
default admin account:
  email: admin@example.com
  password: 67Gh_Secret_2jx
  first_name: Roger
  last_name: Jones
{% endhighlight %}

The settings are only used by the [`docassemble.webapp.create_tables`]
module during the initial setup process. Using the information
defined here, that script sets up a single account in the
[user login system] with "admin" privileges.

You can also use `default admin account` to initialize an API key:

{% highlight yaml %}
default admin account:
  email: admin@example.com
  password: 67Gh_Secret_2jx
  api key: Dbah81njFzdMLw07hnU2TBYA4eClcRw1
{% endhighlight %}

The API key must be exactly 32 characters long. It will be owned by
the default admin user and will have no constraints on IP address or
`Referer`.

After [`create_tables`] runs for the first time, you can (and should)
delete the `default admin account` information from the configuration
file.

## <a name="admin can delete account"></a>Whether the administrator can delete user accounts

By default, administrators can [edit user accounts] and mark them
inactive. If an account is inactive, the user cannot log in and the
user cannot register using the same e-mail address. Marking an
account as inactive does not delete the user's data.

When administrators [edit user accounts], they can also delete the
user's account. Since the deletion of the information is permanent,
you might want to turn off this feature for safety reasons. To do so,
set `admin can delete account` to `False`:

{% highlight yaml %}
admin can delete account: False
{% endhighlight %}

## <a name="user can delete account"></a>Whether users can delete
their accounts

By default, users have the power to delete their own accounts and all
of their data. To disable this, you can set `user can delete account`
to `False`:

{% highlight yaml %}
user can delete account: False
{% endhighlight %}

<a name="delete account deletes shared"></a>If users have joined
[multi-user interviews] with other people, it is ambiguous who "owns"
the data in the interview. By default, shared interviews are not
deleted from the server when users delete their data. However, if you
want to give users the power to delete any session of a [multi-user
interview], even if other people used it, you can set `delete account
deletes shared` to `True`.

{% highlight yaml %}
delete account deletes shared: True
{% endhighlight %}

## <a name="user can request developer account"></a>Whether users can request developer accounts

By default, if `enable playground` is not set to `False`, then users
can submit a request for a developer account on the user profile
page. To prevent users from requesting developer accounts, you can
set `user can request developer account` to `False`:

{% highlight yaml %}
user can request developer account: False
{% endhighlight %}

## <a name="use alembic"></a>Database table upgrades

By default, **docassemble** uses [alembic] to upgrade the SQL database
from one version to another. To turn this off, you can add:

{% highlight yaml %}
use alembic: False
{% endhighlight %}

## <a name="secretkey"></a>Secret key for Flask

The [Flask] web framework needs a secret key in order to manage
session information, provide [protection] against [cross-site request
forgery], and to help encrypt passwords. Set the `secretkey` to a
random value that cannot be guessed.

{% highlight yaml %}
secretkey: CnFUCzajSgjVZKD1xFfMQdFW8o9JxnBL
{% endhighlight %}

The [startup process] on [Docker] sets the `secretkey` to a random
value.

After you already have a working system, you should not change the
`secretkey`. If you do, none of your passwords or API keys will work.

## <a name="backup days"></a>Number of days of backups to keep

The [Docker] setup creates 14 days of daily backups. The number of
days can be changed using the `backup days` directive.

{% highlight yaml %}
backup days: 7
{% endhighlight %}

If you set `backup days` to `0`, the daily backup process will be
disabled.

## <a name="backup file storage"></a>Whether to backup file storage

By default, files that users upload and files that are generated by
the system (e.g., uploaded files, `DAFile` files, document assembly
results, etc.) are backed up in daily snapshots. However, this can
take up a lot of space, and having snapshots of files may not be
important to you. To exclude these files from the daily backups, set
`backup file storage` to `false`.

{% highlight yaml %}
backup file storage: false
{% endhighlight %}

## <a name="password secretkey"></a>Secret key for passwords

The `password secretkey` is used in the process of encrypting
interview answers for users who log in using [third-party logins]. It
defaults to the same value as `secretkey`. If this value changes,
users who log in through [third-party logins] will not be able to
resume stored interviews.

## <a name="require referer"></a>Allowing referer blocking

By default, when HTTPS is used, **docassemble** uses a form of
[CSRF protection] that checks whether the [referer header] matches the
host. For privacy reasons, some users set their browsers to disable
the sending of the referer header. If the [referer header] is
missing, the [CSRF protection] mechanism will generate an error. To
bypass this security feature, set:

{% highlight yaml %}
require referer: False
{% endhighlight %}

The default setting is `True`.

## <a name="maximum content length"></a>Limiting size of HTTP requests

By default, as a security precaution, the web application rejects any
HTTP request larger than 16 megabytes. If you encounter this limit,
you may see an error like "413 Request Entity Too Large."

This limit can be extended by setting `maximum content length` to a
different number of bytes.

{% highlight yaml %}
maximum content length: 26214400
{% endhighlight %}

This sets the limit to 25 megabytes.

To have no limit, set `maximum content length` to `None`.

If you are using [Docker] and [NGINX], then after changing this value,
you will need to do a complete restart of the system for the change to
take effect. (That is, `docker stop -t 600 <container ID>` followed
by `docker start <container ID>`.)

## <a name="signature pen thickness scaling factor"></a>Scaling factor for thickness of signature line

If you think the line thickness of users' signatures is either too
thick or too thin, you can set the `signature pen thickness scaling
factor`. If you want a 10% thicker line, set `signature pen thickness
scaling factor` to 1.1. If you want a 50% thinner line, set it to 0.5.

{% highlight yaml %}
signature pen thickness scaling factor: 0.5
{% endhighlight %}

## <a name="png resolution"></a><a name="png screen resolution"></a>Image conversion resolution

When users supply PDF files and **docassemble** includes those files
within a [document], the PDF pages are converted to PNG images in
order to be included within DOCX and RTF files. The `png resolution`
directive defines the dots per inch to be used during this conversion.

{% highlight yaml %}
png resolution: 500
{% endhighlight %}

PDF files are also converted to PNG for previewing within the web app,
but at a lower resolution. The `png screen resolution` directive
defines the dots per inch to be used for conversion of PDF pages to
PNG files for display in the web browser.

{% highlight yaml %}
png screen resolution: 72
{% endhighlight %}

When converting page images, the actual DPI used will be scaled based
on the page size. If the long edge of the page is 11 inches and the
`png resolution` is 500, then the DPI will be 500. However if the long
edge of the page is 22 inches, the DPI will be 250.

## <a name="ocr dpi"></a>OCR resolution

If you use the [`ocr_file()`] function, the pages of the PDF file will
be converted to images before being read by the OCR engine. By
default, the resolution used is 300 dpi. To change this to something
else, set the `ocr dpi` directive:

{% highlight yaml %}
ocr dpi: 500
{% endhighlight %}

The actual DPI used will be scaled based on the page size. If the long
edge of the page is 11 inches and the `ocr dpi` is 500, then the DPI
will be 500. However if the long edge of the page is 22 inches, the
DPI will be 250.

## <a name="retype password"></a>Controlling whether registering users need to retype their passwords

By default, users when registering must type in their passwords twice.
To allow users to register after only typing the password once, you
can set the `retype password` directive to `False`.

{% highlight yaml %}
retype password: False
{% endhighlight %}

## <a name="password complexity"></a>Controlling password complexity

By default, users when registering must select a password that is at
least six characters long and that contains at least one lower case
letter, at least one upper case letter, and at least one digit
character. You can alter these requirements using the `password
complexity` directive.

{% highlight yaml %}
password complexity:
  length: 8
  uppercase: 0
  lowercase: 1
  digits: 2
  punctuation: 1
{% endhighlight %}

In this example, passwords must be eight characters in length, must
contain at least one lower case character, must contain at least two
digit characters, and must contain at least one punctuation character.

If you leave out any one of these directives, the default value for
that setting will be used.

Changing the `password complexity` directive has no effect on users
who have already set their passwords.

If a user tries to set a password that does not meet the password
complexity requirements, an error message will be displayed that
describes what the password complexity requirements are. You can
manually override this error message by setting the `error message`
directive within the `password complexity` directive to what you want
the error message to be.

## <a name="login link style"></a>Changing the style of the login link

By default, when a user is not logged in, there is a link in the upper
right corner labeled "Sign in or sign up to save answers."  You can
change the style of this by setting `login link style` to `button`:

{% highlight yaml %}
login link style: button
{% endhighlight %}

Then, the user will instead see a "Sign up" link and a "Sign in"
button. The [Bootstrap] color of the "Sign in" button can be changed
using [`button colors`].

## <a name="show login"></a>Hiding the login link

If the `show login` directive is set to `False`, users will not see a
"Sign in or sign up to save answers" link in the upper-right-hand
corner of the web app.

{% highlight yaml %}
show login: False
{% endhighlight %}

The default behavior is to show the "Sign in or sign up to save
answers" link. If `show login` is `False`, users will see an "Exit"
option. The appearance and behavior of the "Exit" option is
configurable in the interview [`metadata`] using the directives [`exit
link`] and [`exit label`]. There is also a [`show login` metadata
directive] that contols this feature on a per-interview basis.

## <a name="show profile link"></a>Hiding the profile link

If the `show profile link` directive is set to `False`, logged-in
users will not see a "Profile" link in the web app menu. Instead,
they will see a "Change Password" link (unless [`allow changing
password`] is false).

{% highlight yaml %}
show profile link: False
{% endhighlight %}

Note that users with `admin` or `developer` privileges will always see
the "Profile" link.

## <a name="allow changing password"></a>Allowing users to change their passwords

If `allow changing password` is set to `False`, then only users with
`admin` or `developer` privileges will be able to change their
passwords.

{% highlight yaml %}
allow changing password: False
{% endhighlight %}

## <a name="user profile fields"></a>Fields available to users when registering

By default, logged-in users without privileges of `admin` or
`developer` can only edit their first and last names on their user
profiles, and when they register they can only set their e-mail
address and password.

If you would like to expand the fields available to the user on the
registration page and in the user profile, you can set `user profile
fields` to a list of fields that you wish to be editable.

{% highlight yaml %}
user profile fields:
  - first_name
  - last_name
  - country
  - subdivisionfirst
  - subdivisionsecond
  - subdivisionthird
  - organization
  - timezone
  - language
{% endhighlight %}

Although you can expose the `language` field to the user for editing,
this is not recommended because the `language` field is a special
code. The field is not a multiple-choice list; developers can use any
code of their choosing to represent a language or a dialect of a
language. You can use an interview to ask the user for their language
and then set the field in the user profile using [`set_user_info()`].

## <a name="show interviews link"></a>Hiding the "my interviews" link

If the `show interviews link` directive is set to `False`, logged-in
users will not see a [My Interviews] link in the web app menu.

{% highlight yaml %}
show interviews link: False
{% endhighlight %}

Note that users with `admin` privileges will always see the "My
Interviews" link.

## <a name="show dispatch link"></a>Showing the "available interviews" link

If the `show dispatch link` directive is set to `True`, and you have
configured the [`dispatch`] directive, then logged-in users will see
an "Available Interviews" link in the web app menu, which will direct
them to the `/list` page of your site.

{% highlight yaml %}
show dispatch link: True
{% endhighlight %}

By default, this is not shown in the web app menu.

## <a name="allow registration"></a>Invitation-only registration

If the `allow registration` directive is set to `False`, users will
not be allowed to register to become users of the site unless they are
[invited by an administrator].

{% highlight yaml %}
allow registration: False
{% endhighlight %}

The default behavior is to allow any user to register.

## <a name="allow forgot password"></a>Password reset

By default, there is a "Forgot your password?" link on the login page
that allows a user to reset their password after receiving an e-mail
at their e-mail address. You can disable this feature with the `allow
forgot password` directive:

{% highlight yaml %}
allow forgot password: False
{% endhighlight %}

Note that by default, interview answers are encrypted with the user's
password. If the user forgets their password and resets it with the
"Forgot your password?" feature, they will not be able to access their
past interview sessions (unless `multi_user` is set to `True` in the
interview answers, which disables encryption). By contrast, when a
user changes their password, their sessions are re-encrypted with the
new password, and the user does not lose access to their sessions.

## <a name="authorized registration domains"></a>Restricting e-mail/password registration to particular domains

The `authorized registration domains` directive can be used to
restrict registraion to one or more e-mail domains.

{% highlight yaml %}
authorized registration domains:
  - abclegal.org
  - missourilegalhelp.org
{% endhighlight %}

This directive only applies to username/password registration.

## <a name="confirm registration"></a>E-mail confirmation after registration

By default, users who register can start using the site right away.
To require e-mail validation first, set `confirm registration` to
`True`:

{% highlight yaml %}
confirm registration: True
{% endhighlight %}

This feature enables enhanced privacy. If someone tries to register
using the e-mail of someone who has already registered, the fact that
the e-mail address is already registered is not revealed.

## <a name="email confirmation"></a>E-mail confirmation for certain privileges

If you are using `confirm registration` but you want to verify e-mail
addresses only for specific user privileges, you can set the `email
confirmation privileges` directive to a list of [privileges] for which
e-mail confirmation should be a requirement of logging in.

{% highlight yaml %}
confirm registration: True
email confirmation privileges:
  - admin
  - developer
  - advocate
{% endhighlight %}

By default, e-mail confirmation is not required for any privileges (i.e.,
the `email confirmation privileges` is an empty list. Also, the default
administrative user is confirmed when initially created, so you will
never need to confirm that user's e-mail.

Before you enable this feature, make sure you have a working
[email configuration](#mail).

## <a name="suppress login alerts"></a>Suppressing alerts during login and logout

By default, the Flask-User package flashes an alert saying "You have
signed in successfully," "You have signed out successfully," and "You
have registered successfully." To suppress these messages, set
`suppress login alerts` to true.

{% highlight yaml %}
suppress login alerts: True
{% endhighlight %}

## <a name="ldap login"></a>LDAP login

If you want to connect the **docassemble** login system to a local [LDAP]
([Active Directory]) server, add an `ldap login` section to the
Configuration.

At a minimum, the following directives must be set:

{% highlight yaml %}
ldap login:
  enable: True
  server: 192.168.1.124
{% endhighlight %}

If `ldap login` is enabled, then when a user tries to log in, the
user's e-mail address and password will be checked against the [LDAP]
server. If authentication succeeds, **docassemble** will check to see
if a user with that e-mail address already exists in the
**docassemble** login system. If so, the user will be logged in as
that user. If the user does not already exist, then a user with that
e-mail address will be created in the **docassemble** login system and
will be logged in as that user.

If the password does not authenticate, then the login process will
proceed as normal; if a user already exists in the **docassemble**
login system with that username and password, the user will be logged
in as that user.

Thus, the [LDAP] login system can coexist with the standard
**docassemble** login system.

You can also set the `base dn`, `bind email`, and `bind password`
directives:

{% highlight yaml %}
ldap login:
  enable: True
  server: 192.168.1.124
  base dn: "ou=users,dc=example,dc=com"
  bind email: "jsmith@example.com"
  bind password: "xxsecretxx"
{% endhighlight %}

If these additional directives are set, then when a user tries to
register on the **docassemble** system, an error message will be
generated if the e-mail address exists on the [LDAP] server. The
`bind email` and `bind password` are necessary so that **docassemble**
can connect to the [LDAP] server and run a search for the e-mail
address in question. When it does so, it searches within the `base
dn` for an entry with the attribute `mail`. If one or more entries
are found, the error message is raised. If your server uses a
different attribute for the e-mail address, you can set the directive
`search pattern` under `ldap login`. By default, `search pattern` is
set to `mail=%s`. (The `%s` is replaced with the e-mail address when
the search is run.)

You may wish to [disable registration] entirely when using `ldap
login`. In that case, it is not necessary to set the `base dn`, `bind
email`, and `bind password` directives.

## <a name="xsendfile"></a>Support for xsendfile

If your web server is not configured to support X-Sendfile headers,
set the `xsendfile` directive to `False`.

{% highlight yaml %}
xsendfile: False
{% endhighlight %}

Use of X-Sendfile is recommended because it allows the web server,
rather than the Python [WSGI] server, to serve files. This is
particularly useful when serving sound files, since the web browser
typically asks for only a range of bytes from the sound file at a
time, and the [WSGI] server does not support the HTTP Range header.

This variable can be set using the [Docker] environment variable
[`XSENDFILE`].

However, there are some problems with the implementation of X-Sendfile
that can sometimes cause problems. If you get random JavaScript
errors in your application, look at the network console, and if it
reports 0-byte JavaScript files being served, try setting `xsendfile:
False` in your Configuration. This has been an issue when
**docassemble** operates behind a load balancer on [ECS]. On [Docker], if you
set [`BEHINDHTTPSLOADBALANCER`] to `true`, then `xsendfile` will be
set to `False` by default when the initial Configuration is first
created.

## <a name="websockets"></a><a name="websockets ip"></a><a name="websockets port"></a>Configuring the websockets server

The [live help] features depend on a [WebSocket] server. On [Docker],
there is a [supervisor] service called `websockets` that runs the
`docassemble.webapp.socketserver` module. By default, the server runs
on port 5000 on the localhost network (127.0.0.1). This can be
configured:

{% highlight yaml %}
websockets ip: 75.34.2.14
websockets port: 5001
{% endhighlight %}

<a name="expose websockets"></a>The most common reason you might want
the server to run on an IP address other than 127.0.0.1 is if you are
running **docassemble** in a [Docker] container and want to connect to
the server from outside the container. This is necessary in order to
run a [Docker] container [behind a reverse proxy]. If you set:

{% highlight yaml %}
expose websockets: True
{% endhighlight %}

then the server will attempt to connect to the first network that is
not the local network. Typically, inside a [Docker] container, there
are two networks, `lo` and `eth0`. Setting `expose websockets` to
`true` will cause the server to connect to whatever address is
associated with the `eth0` network.

## <a name="http port"></a>Alternative port for HTTP

By default, if you are not using [HTTPS], the **docassemble** web
application runs on port 80. When running [Docker], you can map any
port on the host to port 80 in the container. However, if you are
using a system like Heroku which expects HTTP to be available at a
specific port other than port 80, you can set `http port` to the port
number.

## <a name="log"></a>Directory for log files

**docassemble** writes messages to a log files stored in the directory
indicated by the `log` directive. These messages are helpful for
debugging problems with interviews.

{% highlight yaml %}
log: /tmp/docassemble-log
{% endhighlight %}

The default directory is `/usr/share/docassemble/log`.

If a `log server` is set, **docassemble** will write messages to TCP
port 514 on that server, and will not write to the `log` directory.

If you are using [Docker] with [S3], [S3]-compatible object storage,
or [Azure blob storage], and you omit the `log server` or set it to
`null`, then **docassemble** will automatically find the hostname of
the central log server in cloud storage.

## <a name="interview delete days"></a>Days of inactivity before interview deletion

When the [scheduled tasks] feature is [enabled] on the server,
**docassemble** will delete interviews after 90 days of inactivity.
To change the number of days, set the `interview delete days`
directive in the configuration. For example:

{% highlight yaml %}
interview delete days: 180
{% endhighlight %}

If `interview delete days` is set to `0`, interviews will never be
deleted through [scheduled tasks].

<a name="interview delete days by filename"></a>If you want to
override `interview delete days` for particular interviews, you can
set `interview delete days by filename` to a dictionary in which the
keys are interview filenames and the values are days in integers.

{% highlight yaml %}
interview delete days by filename:
  docassemble.missouri:data/questions/custody.yml: 10
  docassemble.missouri:data/questions/support.yml: 20
{% endhighlight %}

## <a name="user auto delete"></a>Automatic user account deletion

While `interview delete days` and `interview delete days by filename`
result in sessions being deleted, the user accounts associated with
inactive sessions are unaffected, and users are still able to log in
even if their sessions have been deleted.

If you want user accounts to be automatically deleted if a user does
not log in after a period of time, you can enable this with `user auto
delete`.

{% highlight yaml %}
user auto delete:
  inactivity days: 90
{% endhighlight %}

The `inactivity days` refers to the number of days of inactivity after
which the user account will be deleted.

Additional sub-directives that can appear under `user auto delete` include
`enable`, `privileges`, and `delete shared`.

{% highlight yaml %}
user auto delete:
  enable: True
  inactivity days: 90
  privileges:
    - user
    - advocate
  delete shared: True
{% endhighlight %}

The `enable` sub-directive can be set to `False` if you want to
disable auto deletion but keep `user auto delete` in the
Configuration.

The `privileges` sub-directive refers to a list of user [privileges]
for which auto-deletion should apply. The default is that only users
with the privilege of `user` can be auto-deleted; users with `admin`,
`advocate` or `developer` privileges (who do not also have the `user`
privilege) will not have their accounts deleted.

The `delete shared` directive refers to the type of user deletion that
should occur. If `True`, then all sessions accessed by the user will
be deleted, even if the session is a multi-user session and other
users of the session still have accounts. The default is `False`.

If `inactivity days` is `0`, this has the effect of `enable: False`.

Inactivity is measured based on when the user last logged in. Use of
the API counts as a log in. If a user logged in more than `inactivity
days` ago but an interview session to which the user has access was
modified within the `inactivity days` period, then the user's account
will not be deleted.

## <a name="session lifetime seconds"></a>Flask session lifetime

By default, [Flask] remembers sessions for 31 days. To set this
period to a different amount, set `session lifetime seconds` to a
number of seconds after which the sessions should expire.

For example, to expire a session after 24 hours, include:

{% highlight yaml %}
session lifetime seconds: 86400
{% endhighlight %}

## <a name="checkin interval"></a>Polling frequency

By default, the user interface polls the server every six seconds to
"check in" to see if anything has happened that it needs to know
about, and to let the server know that the user is still active.

You can change this interval by setting the `checkin interval`
directive. The number refers to the milliseconds between each call to
the server.

{% highlight yaml %}
checkin interval: 6000
{% endhighlight %}

If you set the `checkin interval` to `0`, this will turn off the
check-in mechanism altogether. This might be useful if you do not
need the check-in feature and you want to prevent unnecessary traffic
and CPU usage.

The features that rely on the `checkin interval` being greater than
zero include:

- Notifications of the results of [background tasks].
- The [check in] feature.
- The [live help] features.

Other than setting `checkin interval` to `0`, it is probably not a
good idea to reduce this value below `6000`. If requests to modify a
single interview come in too frequently, problems can occur.

## <a name="stable version"></a>Using the bugfix-only version

By default, when you press "Upgrade" on the [Package Management] page,
you will download the latest version of **docassemble**. If you want
to stay on the 1.0.x series, which includes bug fixes only and no
feature changes or new features, set `stable version` to `True`.

{% highlight yaml %}
stable version: True
{% endhighlight %}

## <a name="docassemble git url"></a>Alternative GitHub location for docassemble

The [Packages] feature updates the **docassemble** software directly
from [GitHub]. If you need to change the location of this repository
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

If your server will be used by people who speak languages other than
English, you will want to make sure that built-in words and phrases
used within **docassemble**, such as "Continue" and "Sign in," are
translated into the user's language.

The `words` directive loads one or more [YAML], [XLSX], or [XLIFF]
files in order:

{% highlight yaml %}
words:
  - docassemble.mypackage:data/sources/es-words.yml
{% endhighlight %}

Each [YAML] file listed under `words` must be in the form of a
dictionary in which the keys are languages ([ISO-639-1] or [ISO-639-3]
codes) and the values are dictionaries with the translations of words
or phrases.

Assuming the following is the content of the
`data/sources/es-words.yml` file in `docassemble.mypackage`:

{% highlight yaml %}
es:
  Continue: Continuar
  Help: ¡Ayuda!
{% endhighlight %}

then if interview calls `set_language('es')` (Spanish) and
**docassemble** code subsequently calls `word('Help')`, the result
will be `¡Ayuda!`.

When a user visits a page on the **docassemble** server, the user's
browser tells **docassemble** the user's preferred language. This
language is in the browser settings. If the user's preferred language
is Spanish (`es`), then **docassemble** will try to provide Spanish
translations if they are available in any of the files listed under
`words`. If a translation of a given phrase is not available,
**docassemble** will try to provide a translation of the phrase for
whatever language is specified in [`language`] in the
Configuration. If no translation is available for that language,
**docassemble** will use an English version of the phrase.

When you are logged in as a developer or administrator, you can go to
the "Utilities" page from the main menu, where you will find a utility
for generating a draft [YAML], [XLSX], or [XLIFF] file for translating
all of the words and phrases that **docassemble** uses and that might
be presented to the user. If you have set up a [Google API
key](#google), it will use the [Google Cloud Translation API] to
prepare "first draft" translations for any [ISO-639-1] language you
designate.

When you have prepared a translation file and you want to use it on
your server, you will need to put the file into the "sources" folder
of a package and install that package on your server using [Package
Management]. For more information about how to create packages,
**docassemble**, see the [Packages] section.

Users of **docassemble** have contributed translations of built-in
system phrases. These are available in the `docassemble.base`
package, which is part of the core **docassemble** code. To see a
list of translation [YAML] files that are available, see the [list of
files on GitHub]. For example, you can use the Italian translation
file by including `docassemble.base:data/sources/it-words.yml` in your
`words` directive. Note that these user-contributed files have been
added at various times and may not be 100% complete; the
`words-es.yml` file, for example, contains minimal translations, while
the `words-es.xlf` file contains translations for most phrases used by
the system.

The `words` feature with language `en` can be used to translate the
default English phrases into alternative phrases, if you want to
change the default phrases that are used in **docassemble**.

If **docassemble** is not able to read any of the files listed under
`words`, errors will be written to the `uwsgi.log` file, which
you can find in [Logs]. If you find that your translations are not
being used, make sure to check `uwsgi.log` for errors.

For more information about how **docassemble** handles different
languages, see the [language and locale settings] section and the
[functions] section (specifically the functions [`set_language()`] and
[`word()`]).

## <a name="currency symbol"></a>Currency symbol

You can set a default currency symbol if the symbol generated by
the locale is not what you want:

{% highlight yaml %}
currency symbol: €
{% endhighlight %}

This symbol will be used in the user interface when a [field] has the
`datatype` of [`currency`]. It will also be used as the return value
of the [`currency_symbol()`] function.

Setting `currency symbol` in the configuration has the same effect as
running the following from a Python module:

{% highlight python %}
import docassemble.base.functions
docassemble.base.functions.update_language_function('*', 'currency_symbol', lambda: '€')
{% endhighlight %}

This will also affect the behavior of the [`currency()`] function;
instead of using the locale's method of formatting a currency value,
the currency symbol will be printed, followed by the numerical value.

There are other ways to customize currency features. In an interview,
you can configure the currency symbol using the [`set_locale()`]
function with the keyword parameter `currency_symbol`. In addition,
you can set a field-specific currency symbol using the [`currency
symbol` field modifier]. See also the section on [customizing based
on language and locale].

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

Note that if you are using [Azure blob storage], [S3]-compatible
object storage [S3], the URLs to files will point directly to files
stored in the cloud, so there would be no reason for a **docassemble**
file server.

## <a name="geocoder service"></a>Geocoding

The [`.geocode()`] and [`.normalize()`] methods of [`Address`] depend on
an API for geocoding. By default, the [Google Maps Geocoding API] is
used. You can use the [Azure Maps API] instead by setting `geocoder
service` to `azure maps`:

{% highlight yaml %}
geocoder service: azure maps
{% endhighlight %}

The `azure maps` setting requires you to set the `primary key`
directive under the `azure maps` directive. See the [Azure Maps API
key section](#azure_maps) for more information.

The default value is `google maps`:

{% highlight yaml %}
geocoder service: google maps
{% endhighlight %}

The `google maps` setting requires you to set the `api key` directive
under the `google` directive. See the
[Google API key section](#google) for more information.

To disable geocoding, set `geocoder service` to `null`.

{% highlight yaml %}
geocoder service: null
{% endhighlight %}

Geocoding is performed by the [GeoPy] package, which supports a number
of other geocoders besides Google Maps and Azure Maps. The
`docassemble.base.geocode` module can be extended to include support
other geocoders. Make a request on the [Slack] if you need support
for a different geocoding service.

## <a name="azure_maps"></a>Azure Maps API key

If you set [`geocoder service`] to `azure maps`, you need to enable
the [Azure Maps API] on your [Azure] account and obtain a [primary
key]. Then plug this [primary key] into your Configuration as
follows:

{% highlight yaml %}
azure maps:
  primary key: AS9W5FS2HS5EFAEFafASFARefa
{% endhighlight %}

## <a name="google"></a>Google API key

If you want to use the [`.geocode()`] method, which uses the [Google
Maps Geocoding API], or the feature in Utilities for translating
system words into other languages, which uses the [Google Cloud
Translation API], you need to obtain a Google API key and plug it into
your Configuration:

{% highlight yaml %}
google:
  api key: UIJGeyD-23aSdgSE34gEGRg3GDRGdrge9z-YUia
{% endhighlight %}

The `api key` under `google` is used when the server sends requests to
Google; thus, in the Google Cloud Console, you should add security to
the API key based on the IP address of the machine making the
request. If you migrate to a different server with a different IP
address, remember to add your new IP address to the list of allowable
IP addresses.

**docassemble** also has features, including [address autocomplete]
and the [`map_of()`] function, which cause the user's web browser to
call the Google API. For these features, you need to go into Google
Cloud Console, enable the [Google Places API] (the "New" version),
and create an API key for accessing this API. When you obtain the API
key, place it under the `google` directive as the `google maps api
key`:

{% highlight yaml %}
google:
  google maps api key: YyFeyuE-36grDgEE34jETRy3WDjGerye0y-wrRb
  use places api new: True
{% endhighlight %}

Setting `use places api new: True` enables the use of the "New"
[Google Places API], which all users should use or transition to in
2025.

The [address autocomplete] and [`map_of()`] features require sharing
the API key with the web browser, which means your API key is not
secret. Google allows you to add security based on the `Referer`
header, so that the API key can only be used when it is called from a
particular web site.

Therefore, if you use both the server-side features and the
client-side features, obtain two separate API keys from Google, and
lock down the `api key` based on the IP address of your server, and
lock down the `google maps api key` based on the URL of your site.

If you use the [Google Cloud Translation API] for the feature in
[Utilities] that [translates system phrases] into other languages, you
can control how many phrases are translated in a single request to the
API.

{% highlight yaml %}
google translate words at a time: 40
{% endhighlight %}

The default number is 20.

## <a name="service account credentials"></a>Google service account credentials

If you want to integrate with [Google Docs] or [Google Drive], you can
add `service account credentials`, which is a [JSON] object you obtain
from the [Google Developers Console].

To do this, go on the [Google Developers Console] and create a "project"
(or use a project you have already created). Under "Enabled APIs and
Services," enable the [Google Sheets API], the [Google Drive API], and
any other APIs you might want to use. Within the project, create a
[service account]. When you create the service account, you will be
provided with "credentials."  Download the [JSON] (not p12) credential
file for the service account.

Then, in the configuration, set `service account credentials` under
[`google`] to the literal contents of the [JSON] file you downloaded.
(Make sure to provide the necessary indentation so that the [YAML] is
valid.)

For example:

{% highlight yaml %}
google:
  service account credentials: |
    {
      "type": "service_account",
      "project_id": "redacted",
      "private_key_id": "redacted",
      "private_key": "-----BEGIN PRIVATE KEY-----REDACTED-----END PRIVATE KEY-----\n",
      "client_email": "googledocs@redacted.iam.gserviceaccount.com",
      "client_id": "redacted",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://accounts.google.com/o/oauth2/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/googledocs%40redacted.iam.gserviceaccount.com"
    }
{% endhighlight %}

## <a name="google analytics"></a>Google Analytics ID

If you want to use [Google Analytics] on the screens in your interviews,
you can set `analytics id` within the `google` directive:

{% highlight yaml %}
google:
  analytics id: G-9876543210
{% endhighlight %}

When this is configured, [JavaScript] for [Google Analytics] will be
inserted into your interview pages, and [pageview] events will be sent
to [Google Analytics] for any `question` that has an [`id`] defined.

If you are using [Google Analytics 4], set the `analytics id` to the GA4
"measurement ID" (beginning with `G-`). If you are using Google's
older system, set the `analytics id` to the "tracking ID" (beginning
with `UA-`).

It is possible to use both a `UA-` and `G-` ID at the same time if
`analytics id` refers to a list of IDs.

{% highlight yaml %}
google:
  analytics id:
    - G-9876543210
    - UA-77777777-1
{% endhighlight %}

The [pageview] events that **docassemble** sends will record a view on
an artificial path. For example, suppose you have the following
question:

{% highlight yaml %}
id: lead certification
question: |
  Does your landlord have a valid lead certification?
yesno: lead_certification_exists
{% endhighlight %}

Suppose this question is part of the interview `answer.yml` in the
package `docassemble.eviction`. In that case, the `pageview` will
record a view of the following pseudo-URL on your site:

> /eviction/answer/lead_certification
{: .blockquote}

Since the [`id`] is also used as a unique identifier for a
[`question`], you might to use a different identifier for purposes of
Google Analytics. If so, tag your question with [`ga id`] instead of
an [`id`]:

{% highlight yaml %}
id: lead certification
ga id: landlordLeadCert
question: |
  Does your landlord have a valid lead certification?
yesno: lead_certification_exists
{% endhighlight %}

## <a name="segment id"></a>Segment ID

[Segment] is an analytics aggregator that feeds data about user
behavior to other tools, such as Amplitude, Customer.io, FullStory,
and Google Analytics.

If you set a `segment id` in the Configuration, [JavaScript] will be
included that initializes [Segment]. When the user arrives at a
question with an [`id`], a [Segment] event will be fired with the
[`id`] as a name.

{% highlight yaml %}
segment id: ZAfFSeR6BTWiEfGnT8YpujspehLtswJP
{% endhighlight %}

Since the [`id`] is also used as a unique identifier for a
[`question`], you might to use a different identifier for purposes of
Segment. If so, tag your question with [`segment id`] modifier (not
to be confused with the `segment id` Configuration directive) instead
of an [`id`]:

{% highlight yaml %}
id: lead certification
segment id: landlordLeadCert
question: |
  Does your landlord have a valid lead certification?
yesno: lead_certification_exists
{% endhighlight %}

You can also send [Segment] messages with arguments, using the
[`segment`] specifier pointing to a dictionary with keys for `id` and
`arguments`:

{% highlight yaml %}
id: lead certification
segment:
  id: landlord
  arguments:
    certification: lead
question: |
  Does your landlord have a valid lead certification?
yesno: lead_certification_exists
{% endhighlight %}

## <a name="voicerss"></a>VoiceRSS API key

If the [special variable `speak_text`] is set to `True`, **docassemble**
will present the user with an audio control that will convert the text
of the question to speech. This relies on the [VoiceRSS] web service.
You will need to obtain an API key from [VoiceRSS] and set the
configuration below in order for this feature to function. (The
service allows 350 free requests per day.)

{% highlight yaml %}
voicerss:
  enable: True
  key: 347593849874e7454b9872948a87987d
  dialects:
    en: us
    es: mx
    fr: fr
{% endhighlight %}

The `enable` key must be set to `True` in order for the text-to-speech
feature to work. The `key` is the [VoiceRSS] API key. The
`dialects` key refers to a dictionary that associates languages with
the dialect to be used with that language. For more information about
dialects, see the [VoiceRSS] documentation.

Sometimes, the language code you use in your interview is not the same
as the language code that [VoiceRSS] uses for that language. In this
case, you can add a `language map` to your [VoiceRSS] configuration to
remap your language code so that it is compatible with [VoiceRSS].

For example, suppose the language code used in your interview is `zho`
for Chinese. But the language that [VoiceRSS] recognizes for Chinese
is `zh`, and the dialects that [VoiceRSS] recognizes for `zh` include
`cn`, `hk`, and `tw`. Suppose you want to use `cn` as the dialect.
You would set your `voicerss` configuration as follows:

{% highlight yaml %}
voicerss:
  enable: True
  key: 347593849874e7454b9872948a87987d
  language map:
    zho: zh
  dialects:
    zh: cn
{% endhighlight %}

You can set the default "voice" for a given language:

{% highlight yaml %}
voicerss:
  enable: True
  key: 347593849874e7454b9872948a87987d
  voices:
    it: Pietro
{% endhighlight %}

You can set the default "voice" for a given dialect of a given
language:

{% highlight yaml %}
voicerss:
  enable: True
  key: 347593849874e7454b9872948a87987d
  voices:
    en:
      us: Amy
      au: Jack
    fr:
      ca: Logan
{% endhighlight %}

You can set the audio format for [VoiceRSS] audio files:

{% highlight yaml %}
voicerss:
  enable: True
  key: 347593849874e7454b9872948a87987d
  format: 44khz_16bit_stereo
{% endhighlight %}

The default format is `16khz_16bit_stereo`.


## <a name="babel dates map"></a>Translation of dates

Many of the [date functions] rely on the [`babel.dates`] package.
This package does not support every language. For example, if you run
`set_language('ht')`, functions that use [`babel.dates`] will return
an error. You can set a different language to be used by
[`babel.dates`] as an alternative by setting the `babel dates map`
directive to a dictionary that translate language codes into
alternative language codes. For example:

{% highlight yaml %}
babel dates map:
  ht: fr
{% endhighlight %}


## <a name="ocr languages"></a>OCR language settings

The [`ocr_file()`] function uses the [Tesseract]<span></span> [optical
character recognition] (OCR) application to extract text from image
files and PDF files. One of the options for the OCR process is the
language being recognized. The codes for language that [Tesseract]
may be different from those that **docassemble** uses. If you are
using [ISO-639-1] for your language codes, the code that [Tesseract]
uses is the [ISO-639-3] code that corresponds to the [ISO-639-1] code
that **docassemble** uses, and **docassemble** can make this
conversion automatically. However, in some cases this does not work,
so there is an override, which is controlled by the `ocr languages`
directive. The default value maps Chinese to Traditional Chinese:

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

## <a name="aws"></a><a name="s3"></a>s3

If you are using [Amazon S3] or an [S3]-compatible object storage
service to store shared files, your access keys, [bucket] name, and
[region name] are in stored in the Configuration as follows:

{% highlight yaml %}
s3:
  enable: True
  access key id: FWIEJFIJIDGISEJFWOEF
  secret access key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
  bucket: yourbucketname
  region: us-west-1
{% endhighlight %}

There is also an option under `s3` called `endpoint url` that you can
set if you are using an [S3]-compatible object storage service. (e.g.,
`endpoint url: https://mys3service.com`). By default, [Amazon S3] is
used. If you are using an [S3]-compatible object storage service, the
`region` directive may not be necessary.

You will need to create the [bucket] before using it; **docassemble**
will not create it for you.

If your S3 bucket uses encryption, you can specify your server-side
encryption information under `server side encryption`. E.g.,

{% highlight yaml %}
s3:
  enable: True
  access key id: FWIEJFIJIDGISEJFWOEF
  secret access key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
  bucket: yourbucketname
  region: us-west-1
  server side encryption:
    algorithm: null
    customer algorithm: AES256
    customer key: 91F8F26A0783345D16C4249990B54B6E
    KMS key ID: null
{% endhighlight %}

If you are using [Docker], you should not define an `s3` directive in
the Configuration using the web application when you already have a
server running. The [S3] configuration is used throughout the boot
process and the shutdown process. If you want to start using [S3],
you should start a new container using [`docker run`] with the
[`S3BUCKET`] and other `S3` environment variables set. For more
information, see the [Docker section].

## <a name="azure"></a>azure

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

## <a name="ec2"></a>ec2

If you are running **docassemble** from within an [Amazon EC2] or
[Lightsail] instance, set this to true:

{% highlight yaml %}
ec2: True
{% endhighlight %}

This is necessary because when **docassemble** runs in a [multi-server
arrangement], each **docassemble** web server instance needs to allow
other **docassemble** web instances to send messages to it through
[supervisor]. Each web server instance advertises the hostname or IP
address through which its [supervisor] can be accessed. Normally,
this can be obtained using the computer's hostname, but within an
[EC2] or [Lightsail] instance, this hostname is not one that other web
servers can resolve. If `ec2` is set to `True`, then **docassemble**
will determine the hostname by calling
`http://169.254.169.254/latest/meta-data/local-ipv4`.

## <a name="ec2 ip url"></a>ec2 ip url

If `ec2` is set to `True`, **docassemble** will determine the hostname
by calling `http://169.254.169.254/latest/meta-data/local-ipv4`. If
this URL does not work for some reason, but a different URL would
work, you can change the URL that **docassemble** uses by setting the
`ec2 ip url` configuration item.

{% highlight yaml %}
ec2 ip url: http://169.254.169.254/latest/meta-data/local-ipv4
{% endhighlight %}

## <a name="kubernetes"></a>kubernetes

If you are running **docassemble** from within a [Kubernetes]
deployment, add this to your Configuration

{% highlight yaml %}
kubernetes: True
{% endhighlight %}

This is necessary because when **docassemble** runs in a [multi-server
arrangement], each **docassemble** web server instance needs to allow
other **docassemble** web instances to send messages to it through
[supervisor]. Each web server instance advertises the hostname or IP
address through which its [supervisor] can be accessed. Normally,
this can be obtained using the computer's hostname, but within a
[Kubernetes] cluster, this hostname is not one that other web servers
can resolve. If `kubernetes` is set to `True`, then **docassemble**
will use the IP address of the Pod as the hostname.

## <a name="api privileges"></a>API usage

By default, only users with privileges of `admin` or `developer` may
obtain an API key in order to use the **docassemble** [API]. You can
change this by editing the `api privileges`.

{% highlight yaml %}
api privileges:
  - admin
  - developer
  - user
{% endhighlight %}

## <a name="password login"></a>Password login

If `password login` is set to `False`, then users will not see an
option for entering their username and password on the login screen;
they will only see buttons for other login methods that you have
enabled. The default value is `True`.

Since there is a possibility that your other login methods will fail,
there is a "back door" that bypasses this setting, so that you as the
administrator can still log in using a username and password. Instead
of going to `/user/sign-in` in the web browser, go to
`/user/sign-in?admin=1`. The username and password fields will be
shown, regardless of the `password login` setting.

## <a name="phone login"></a>Phone number login

If `phone login` is set to `True`, then **docassemble** will allow
users to log in with a phone number. For this system to work, the
[`twilio`] configuration must be set up. The user needs to put in his
or her phone number, and then a random verification code will be sent
to that phone number via [SMS]. The user needs to type in that code
in order to log in. As with the
[external authentication methods](#oauth), registration happens
automatically upon the first login. Subsequent logins will also
require entering a random verification code.

The details of how this login system functions, such as the number of
digits in the verification code and the number of seconds that the
code remains valid, can be [configured](#brute force).

## <a name="mfa"></a>Two-factor authentication

For added security, you can allow users who log in with passwords to
enable two-factor authentication on their accounts. The two-factor
authentication system can use [Google Authenticator], [Authy], or
another compatible app. Or, if you have set up a [`twilio`]
configuration, the system can send a verification code to the user in
an [SMS] message.

To give your users the option of using two-factor authentication, set
`two factor authentication` as follows:

{% highlight yaml %}
two factor authentication:
  enable: True
{% endhighlight %}

Logged-in users will then see an option on their "Profile" page for
configuring two-factor authentication. By default, only
administrators and developers see an option on their [user profile] to
configure second-factor authentication. To configure which privileges
have the option of using second factor authentication, set the `allow
for` subdirective to the full list of [privileges] for which you want
the feature to be available.

{% highlight yaml %}
two factor authentication:
  allowed for:
    - admin
    - developer
    - user
    - advocate
{% endhighlight %}

Regardless of these settings, two-factor authentication is not
available to users who sign in with [external authentication
methods](#oauth) or who are using the [phone login] feature. It is
only available when the first authentication method is a standard
e-mail and password combination.

If you want to enable of the two methods and disable the other, you
can use the `allow sms` and `allow app` subdirectives.

{% highlight yaml %}
two factor authentication:
  allow sms: False
  allow app: True
{% endhighlight %}

By default, `allow sms` and `allow app` are both True.

If you want users with certain privileges to be required to use
two-factor authentication, use the `required for` subdirective:

{% highlight yaml %}
two factor authentication:
  required for:
    - developer
    - admin
{% endhighlight %}

By default, two-factor authentication is optional for all users. As
usual, two-factor authentication is not compatible with [external
authentication methods](#oauth) or the [phone login] feature, so you
will want to disable those features if you want to enforce two-factor
authentication.

The default value of `enable` is True, so you can omit the
`enable` line. You can write `two factor authentication: True`
to enable two-factor authentication with all of the default options.

## <a name="auto login"></a>Automatic login

The `auto login` directive causes users to automatically redirect to a
third-party login service when they arrive at the `/user/sign-in` endpoint.

If you have only one alternative login method, you can [`password
login`] to `False` and set `auto login` to `True`:

{% highlight yaml %}
auto login: True
password login: False
{% endhighlight %}

If you have multiple alternative login methods, and you want one of
them to be automatic, you can set `auto login` to the name of the
login method:

{% highlight yaml %}
auto login: google
password login: False
{% endhighlight %}

Valid values are `phone`, `google`, `facebook`, `auth0`, `keycloak`,
`authentik`, `zitadel`, `miniorange`, and `azure`.

If you wish to prevent the user from being automatically redirected
when they visit `/user/sign-in`, you can add `from_logout=1` to the URL
parameters. (This is how the logout process avoids an immediate login
when `logoutpage` is not defined and the user is directed back to the
login page after they log out.)

## <a name="playground examples"></a>List of examples in the Playground

As a development aid, the [Playground] contains an [examples area]
with a list of short sample interviews that demonstrate particular
features. The interviews shown here are controlled by the file
[`docassemble.base:data/questions/example-list.yml`]. If you would
rather use a list of your own, you can define `playground examples`:

{% highlight yaml %}
playground examples: docassemble.michigan:data/questions/examples.yml
{% endhighlight %}

This will replace all of the example interviews with the examples you specify.

You can also set `playground examples` to a list of files:

{% highlight yaml %}
playground examples:
  - docassemble.base:data/questions/example-list.yml
  - docassemble.michigan:data/questions/examples.yml
{% endhighlight %}

In this example, the standard list
([`docassemble.base:data/questions/example-list.yml`]) will be used
first, and then the example categories and interviews from the
`docassemble.michigan` package will be included after.

For example, suppose the file
`docassemble.michigan:data/questions/examples.yml` contained:

{% highlight yaml %}
- Slack:
    - slack-example
    - slack-example-2
{% endhighlight %}

This would assume that there was an interview
`docassemble.michigan:data/questions/slack-example.yml` and an
interview `docassemble.michigan:data/questions/slack-example-2.yml`.

It would also assume that there were PNG screenshots for this
interviews available in the `data/static` folder of the
`docassemble.michigan` package called `slack-example.png` and
`slack-example-2.png`.

There are some [`metadata`] headers specific to example interviews.
For example, suppose the [`metadata`] of `slack-example.yml` was:

{% highlight yaml %}
metadata:
  title: Test Slack Posting
  short title: Test Slack
  documentation: "https://michigan.example.com/docs/using_slack.html"
  example start: 1
  example end: 2
---
question: |
  What do you want to post on Slack?
fields:
  - Message: the_message
---
code: |
  post_to_slack(the_message)
  message_posted
{% endhighlight %}

The `short` title, "Test Slack," will be used in the navigation bar of
the [Playground] examples section. The URL under `documentation` will
be the URL behind the "View documentation" link in the [Playground]
examples section. The blocks of the interview that will be shown on
the screen are based on the `example start` and `example end` items.
In this example, block "1" is the [`question`] block, and block "2" is
the [`code`] block. (Block "0" is the [`metadata`] block.)  So the
[`question`] block and the [`code`] block will be shown, but not the
[`metadata`] block.

## <a name="vim"></a><a name="keymap">Changing the mode of the editor in the Playground

If the `keymap` directive is set to `vim`, `emacs`, or `sublime`, then
the in-browser text editors in the [Playground] will emulate [Vim],
[Emacs], or [Sublime Text], respectively. This uses the [Vim bindings
option], [Emacs bindings option], and [Sublime Text bindings option]
of [CodeMirror].

For [Vim]:

{% highlight yaml %}
keymap: vim
{% endhighlight %}

For [Emacs]:

{% highlight yaml %}
keymap: emacs
{% endhighlight %}

For [Sublime Text]:

{% highlight yaml %}
keymap: sublime
{% endhighlight %}

## <a name="external hostname"></a>URL to the site

The `external hostname` is the hostname by which users will access
**docassemble**. If users will see `https://docassemble.example.com` in
the location bar on the web browser, `external hostname` will be
`docassemble.example.com`.

{% highlight yaml %}
external hostname: docassemble.example.com
{% endhighlight %}

This variable is only effective if **docassemble** is running on
[Docker]. It is typically set by the [`DAHOSTNAME`] environment
variable when the [`docker run`] command is run for the first time.

If you change `external hostname`, you need to do a complete restart
of the system for the change to take effect. (That is, `docker
stop -t 600 <container ID>` followed by `docker start <container ID>`.)

## <a name="behind https load balancer"></a>When behind a proxy

Set the `behind https load balancer` directive to `True` if you are
running **docassemble** in a configuration where **docassemble**
itself is running [HTTP], but requests are being forwarded to it by a
server running HTTPS. This might be your configuration if you are
using a [load balancer] or you are running [Docker] in a context where
a web server or web service [forwards] HTTPS requests to [Docker] on
port 80 or a non-standard [HTTP] port.

This variable is typically set using the [Docker] environment variable
[`BEHINDHTTPSLOADBALANCER`].

This is important because if **docassemble** thinks that it is serving
requests on port 80, it won't set the `secure` flag on cookies.
However, if the user's browser actually is accessing the site over
HTTPS, then users will get cookies that lack the `secure` flag. The
mismatch between the use of HTTPS and the flag on the cookies can
cause site to reject the cookies. The symptom of the browser
rejecting cookies can be the continual reloading of the screen or the
Continue button acting like a reload button. Cookies are necessary
for **docassemble**'s session system, so the site will not function
unless cookies work. Thus it is very important to set `behind https
load balancer` if you are using a load balancer or proxy.

Also make sure that the proxy server you are using sets the
`X-Forwarded-*` headers. **docassemble** needs these headers in
certain circumstances in order to form correct URLs. Specifically,
the proxy server should set the following headers:

* `X-Forwarded-For`
* `X-Forwarded-Host`
* `X-Forwarded-Port`
* `X-Forwarded-Proto`

You can test whether your proxy server is sending these headers to
your **docassemble** server by visiting `/headers` on your site.

## <a name="use lets encrypt"></a><a name="lets encrypt email"></a>Using Let's Encrypt

If you are using [Docker] and you want your server to use [HTTPS] set
up through [Let's Encrypt], you can set the following in your
[Configuration].

{% highlight yaml %}
external hostname: docassemble.example.com
use https: True
use lets encrypt: True
lets encrypt email: jsmith@example.com
{% endhighlight %}

These variables are typically set through the environment variables
[`DAHOSTNAME`], [`USEHTTPS`], [`USELETSENCRYPT`], and [`LETSENCRYPTEMAIL`] when the
[`docker run`] command is run for the first time. You can change the
`use https`, `use lets encrypt`, and `lets encrypt email` variables on
a running server, but they will only be effective if you restart the
system using `docker stop -t 600 <container ID>` followed by
`docker start <container ID>`.

## <a name="nginx ssl protocols"></a>SSL protocols

The `nginx ssl protocols` directive indicates the SSL protocols that
[NGINX] should accept (assuming you are using [NGINX]). You might
want to set it to `TLSv1 TLSv1.1 TLSv1.2 TLSv1.3` if you need to support older
browsers.

{% highlight yaml %}
nginx ssl protocols: TLSv1 TLSv1.1 TLSv1.2 TLSv1.3
{% endhighlight %}

The value is passed directly to the [NGINX] directive
[`ssl_protocols`]. The default is `TLSv1.2 TLSv1.3`.

This variable is typically set through the environment variable
[`DASSLPROTOCOLS`]. You can change `nginx ssl protocols` on a running
server, but the change will only be effective if you restart the
system using `docker stop -t 600 <container ID>` followed by `docker
start <container ID>`.

## <a name="nginx ssl ciphers"></a>SSL ciphers

The `nginx ssl ciphers` directive indicates the SSL ciphers that
[NGINX] should accept (assuming you are using [NGINX]).

{% highlight yaml %}
nginx ssl ciphers: ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-CHACHA20-POLY1305;
{% endhighlight %}

The value is passed directly to the [NGINX] directive
[`ssl_ciphers`]. The default is `HIGH:!aNULL:!MD5`.

This variable is typically set through the environment variable
[`DASSLCIPHERS`]. You can change `nginx ssl ciphers` on a running
server, but the change will only be effective if you restart the
system using `docker stop -t 600 <container ID>` followed by `docker
start <container ID>`.

## <a name="cross site domains"></a>Cross-Origin Resource Sharing (CORS)

Set the `cross site domains` directive if you want the web server to
send `Access-Control-Allow-Origin` headers in order to permit
[Cross-Origin Resource Sharing].

{% highlight yaml %}
cross site domains:
  - https://example.com
  - https://help.example.com
{% endhighlight %}

It is important to specify the protocol as well as the domain.

See also [`allow embedding`].

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

## <a name="allow updates"></a>Whether software updating is allowed

By default, a user with privileges of administrator or developer can
install Python packages on the server, or update existing Python
packages. To disable updating of packages through the user interface
and the API, set `allow updates` to `false`.

{% highlight yaml %}
allow updates: false
{% endhighlight %}

Note that the [Playground] also allows users to change the code on the
system, so if you set `allow updates: false`, you will probably also
want to set [`enable playground`] to `false`.

## <a name="update on start"></a>Whether software is updated on start

By default, when a [Docker] container starts, whether it is starting
for the first time during a [`docker run`] process, or restarting during a
[`docker start`] process, one of the steps taken during the container
initialization process is the updating of Python packages.

This process is necessary in order to install any custom Python
packages you have, such as interviews you have created. If you
replace a container with [`docker stop -t 600`], [`docker rm`], and
[`docker run`], you will want the new container to have the
appropriate software on it. When you use [Package Management] or the
[packages folder] of the [Playground] to install a package on your
system, the packages that get installed are tracked in the SQL
database. When you start up a new [Docker] container that uses that
SQL database, the update process will install the packages listed in
the database.

This is the main reason why launching a [Docker] container can take a
long time.

By default, the update process happens any time the container starts,
which is both during the [`docker run`] process and also during the
[`docker start`] process.

If you do not want your container to go through this update process
when the container starts, you can set:

{% highlight yaml %}
update on start: false
{% endhighlight %}

Alternatively, if you want the update process to run during the
[`docker run`] process but not subsequently, you can set:

{% highlight yaml %}
update on start: initial
{% endhighlight %}

## <a name="allow configuration editing"></a>Whether the configuration can be edited

If you want to prevent administrators from editing the configuration
through the web interface or the API, you can set `allow configuration
editing` to `False`.

{% highlight yaml %}
allow configuration editing: False
{% endhighlight %}

## <a name="log server"></a>Log server hostname

If the `log server` directive is set, **docassemble** will write log
messages to TCP port 514 on the hostname indicated by `log server`
instead of writing them to
`/usr/share/docassemble/log/docassemble.log` (or whatever other
directory is set in [`log`]).

## <a name="redis"></a>Redis server location

The `redis` directive indicates where **docassemble** can find the
[Redis] server that it should used for storing [Flask] session state,
API keys, background task information, and other data that are stored
in [Redis].

The `redis` directive should be treated as read-only. The primary way
you would adjust your [Redis] configuration is when starting a new
server for the first time. At that time, you can set [Docker]
configuration variable [`REDIS`] in order to specify that a particular
external [Redis] database should be used. For example, you would set
this environment variable if you were using a cloud-based managed
Redis system like [ElastiCache for Redis].

Changing the `redis` directive after you already have a working system
can lead to major problems, such as API keys not working. You should
not change the `redis` value using the web-based front end unless you
really know what you are doing.

In the default [Docker] configuration, `redis` directive is set to
`null`.

{% highlight yaml %}
redis: null
{% endhighlight %}

This indicates that the [Redis] server is located on the same server
as the web server.

If `redis` is set to a something else, then an external `redis` server
is used.

{% highlight yaml %}
redis: redis://192.168.0.2
{% endhighlight %}

The `redis` directive needs to be written in the form of a
[redis URI]. To specify a non-standard port, use the form
`redis://192.168.0.2:7000`. To specify a password, use the form
`redis://:xxsecretxx@192.168.0.2` or
`redis://192.168.0.2?password=xxsecretxx`. You can specify a
username along with the password
(`redis://jsmith:xxsecretxx@192.168.0.2`), but [Redis] does not use
usernames, so this may not work.

To use SSL, use the prefix `rediss://` instead of `redis://`. You can
provide your own certificates to Redis if necessary. If you are using
[S3] or [Azure blob storage], you need to copy the certificate files
to `certs/` in the bucket or container. Otherwise, you need to make
sure the certificate files are in `/usr/share/docassemble/certs` when
the server initializes (from there, the files are copied into working
directories). For more information, see [managing certificates with
Docker] and [`certs`]. The certificate files must have the following
names, which correspond with particular [parameters for connecting to
Redis with Python].

* `redis_ca.crt` - for the `ssl_ca_certs` file (certificate authority certificate)
* `redis.crt` - for the `ssl_certfile` file (certificate)
* `redis.key` - for the `ssl_keyfile` (certificate key)

If the URL begins with `rediss://`, the connection is initialized with
the parameter `ssl=True`. If any of the above files are present, the
`ssl_ca_certs`, `ssl_certfile`, and/or `ssl_keyfile` parameters will
be used as well.

If you are using [Docker] with [S3] or [Azure blob storage], and you
omit the `redis` directive or set it to `null`, then **docassemble**
will automatically find the hostname of the central redis server in
cloud storage.

**docassemble** uses three [Redis] "databases."  By default, it uses
databases 0, 1, and 2. If you want it to use different database
numbers, you can set `redis database offset` to a number.

{% highlight yaml %}
redis database offset: 3
{% endhighlight %}

In this case, **docassemble** will use databases 3, 4, and 5 instead
of 0, 1, and 2.

If you reference a database number in your URI (e.g., using
`redis://192.168.0.2?db=1` or `redis://192.168.0.2/1`), then the
referenced database will be used as the `redis database offset`.
However, if you also include `redis database offset` in your
Configuration, the value of `redis database offset` will override
whatever is specified in the URI.

## <a name="rabbitmq"></a>RabbitMQ server location

By default, **docassemble** assumes that the [RabbitMQ] server is located
on the same server as the web server. You can designate a different
[RabbitMQ] server by setting the `rabbitmq` directive:

{% highlight yaml %}
rabbitmq: pyamqp://guest@rabbitmqserver.local//
{% endhighlight %}

The `rabbitmq` directive needs to be written in the form of an [AMQP
URI].

If you are using [Docker] with [S3] or [Azure blob storage], and you
omit the `rabbitmq` directive or set it to `null`, then
**docassemble** will automatically find the hostname of the central
[RabbitMQ] server in cloud storage.

## <a name="imagemagick"></a><a name="pdftoppm"></a>Image conversion

By default, **docassemble** assumes that you have [ImageMagick] and
pdftoppm installed on your system, and that they are accessible
through the commands `convert` and `pdftoppm`, respectively. If you
do not have these applications on your system, you need to set the
configuration variables to null:

{% highlight yaml %}
imagemagick: null
pdftoppm: null
{% endhighlight %}

If you have the applications, but you want to specify a particular
path, you can set the path using the configuration variables:

{% highlight yaml %}
imagemagick: /usr/local/bin/convert
pdftoppm: /usr/local/bin/pdftoppm
{% endhighlight %}

## <a name="pacpl"></a><a name="ffmpeg"></a>Sound file conversion

By default, **docassemble** assumes that you have pacpl (the
[Perl Audio Converter] and/or [ffmpeg] installed on your system, and
that they are accessible through the commands `pacpl` and
`ffmpeg`, respectively. If you do not have these applications on
your system, you need to set the configuration variables to null:

{% highlight yaml %}
pacpl: null
ffmpeg: null
{% endhighlight %}

You can also set these variables to tell **docassemble** to use a
particular path on your system to run these applications.

## <a name="libreoffice"></a><a name="pandoc"></a><a name="gotenberg url"></a><a name="convertapi secret"></a><a name="cloudconvert secret"></a>Document conversion

**docassemble** requires that you have [Pandoc] installed on your
system. It assumes that it can be run using the command `pandoc`.
If you need to specify a different path, you can do so in the configuration:

{% highlight yaml %}
pandoc: /opt/pandoc/bin/pandoc
{% endhighlight %}

By default, **docassemble** uses [LibreOffice] through [unoconv] to
convert DOCX templates to PDF format. If your **docassemble** server
was created many years ago, you may need to enable [unoconv] with the
[`enable unoconv`] directive; otherwise, **docassemble** will call
[LibreOffice] directly.

Instead of using [unoconv], you can use an external [Gotenberg] server
for DOCX to PDF conversion. If you have a [Gotenberg] server that is
accessible from within the **docassemble** container on hostname
`mygotenberg`, port 3000, you would disable [unoconv] and set the
`gotenberg url` to the following:

{% highlight yaml %}
enable unoconv: false
gotenberg url: http://mygotenberg:3000
{% endhighlight %}

Then, all DOCX-to-PDF conversion will use this server.

There are many ways to deploy a [Gotenberg] server alongside a
**docassemble** container. [Gotenberg] is available as a [Docker]
container, so you can run a [Gotenberg] container on the same server
where you are hosting a **docassemble** container. In order for one
[Docker] container running on a host to talk to another [Docker]
container, you need to make sure that **docassemble** container can
reach the [Gotenberg] container; this can be moderately difficult
because of the way networking works with [Docker]. One way is to
create a bridge network and run both the [Gotenberg] and
**docassemble** containers on that network:

{% highlight bash %}
docker network create --driver bridge docassemble-net
docker run -d --name gotenberg \
--restart always \
--network docassemble-net \
-p 3000:3000 \
gotenberg/gotenberg:7
docker run -d --name docassemble \
--restart always \
--network docassemble-net \
-v dabackup:/usr/share/docassemble/backup \
-p 80:80 \
jhpyle/docassemble
{% endhighlight %}

Then you can set the `gotenberg url` as follows:

{% highlight yaml %}
enable unoconv: false
gotenberg url: http://gotenberg:3000
{% endhighlight %}

The `gotenberg url` can be prepopulated in the **docassemble**
configuration using the [`GOTENBERGURL`] environment variable.

Disabling [unoconv] when using [Gotenberg] is important not only to
save memory but to prevent any conflicts between [Gotenberg]'s use of
[LibreOffice] and the **docassemble**'s use of [LibreOffice], if the
containers are running on the same host. After you change `enable
unoconv`, you need to do a `docker stop`/`docker start` for the change
to fully take effect.

Another third party service that you can use is [ConvertAPI], a web
service for file conversion. To enable this, sign up with
[ConvertAPI] and set the `convertapi secret` to the "Secret" that
[ConvertAPI] generates for you.

{% highlight yaml %}
convertapi secret: SrWh4XfuOje5jYx1
{% endhighlight %}

You can also use [CloudConvert]. Sign up with [CloudConvert], go
to the Dashboard, go to Authorization, API keys under "API V2," and
click "Create New API key."  Copy the API key into your Configuration
as the `cloudconvert secret`:

{% highlight yaml %}
cloudconvert secret: afwefhwfperowewERQWrasfASEf234Frthe33t4ge4rgf3evn3480w9ejfornv9n40923nvqiniQWeeorgmkbwyeghgpojrgbu
{% endhighlight %}

Enabling [ConvertAPI] or [CloudConvert] can be useful if you are using
[`docx template file`] to generate PDF files, but the standard
[LibreOffice] conversion does not work properly due to
incompatibilities between [Microsoft Word] and [LibreOffice].

## <a name="pandoc engine"></a>Pandoc's LaTeX engine

By default, [Pandoc] uses `pdflatex` to generate PDF files from
[Markdown]. If you would like to use a different engine, you can
specify it using the `pandoc engine` directive:

{% highlight yaml %}
pandoc engine: xelatex
{% endhighlight %}

## <a name="pdfa"></a>Producing PDF/A files

If you want the [PDF] files produced by interviews on your server to be
in [PDF/A] format, you can set this as a default:

{% highlight yaml %}
pdf/a: True
{% endhighlight %}

The default is `False`. The setting can also be made on a
per-interview basis by setting the [`pdf/a` features setting].

<a name="tagged pdf"></a>When using [`docx template file`], you also
have the option of creating a "tagged PDF," which is similar to
[PDF/A]. You can set this as a server-wide default:

{% highlight yaml %}
tagged pdf: True
{% endhighlight %}

This setting can also be made on a per-interview basis by setting the
[`tagged pdf` features setting].

## <a name="default rendering font"></a>Changing the default font for rendering PDF fields

When `pdf template file` is used with `editable: False`, [pdftk] is
used to convert form fields to rendered text. The default font that
[pdftk] uses may not have support for characters that you want to
use. You can specify a different font for a particular `attachment`
using [`rendering font`].

To specify a font that should be used by default instead of [pdftk]'s
Arial font, you can specify a `default rendering font` in the
Configuration.

{% highlight yaml %}
default rendering font: /usr/share/fonts/truetype/msttcorefonts/Arial.ttf
{% endhighlight %}

For more information about what font file to use, see [`rendering font`].

## <a name="enable unoconv"></a>Using unoconv instead of LibreOffice for processing DOCX files

Starting with system version 1.3.18, a [unoconv] listener is
available, which keeps LibreOffice in memory and uses it to convert
files with a client/server model. **docassemble** uses LibreOffice to
convert DOCX to PDF and other formats, as well as to update references
within a DOCX after `docx template file` is used to assemble a
document.

The [unoconv] listener will run only if `enable unoconv` is set to
`True` in your Configuration. If `enable unoconv` is missing or is not
set to `True`, `unoconv` will not be used. If you started using
**docassemble** before 1.3.18 and you want to use [unoconv], set the
following in your Configuration, and then do a [system upgrade].

{% highlight yaml %}
enable unoconv: True
{% endhighlight %}

This is part of the default configuration if you created your server
since version 1.3.18.

After changing `enable unoconv`, you need to restart your system with
`docker stop`/`docker start`.

See also the [`ENABLEUNOCONV`] environment variable.

## <a name="maximum image size"></a>Limiting size of uploaded images

If your users upload digital photos into your interviews, the uploads
may take a long time. Using the [`maximum image size` field modifier]
or the [`maximum image size` interview feature], you can cause your
users' web browsers to reduce the size of your images before uploading
them. For example, if `maximum image size` is set to 1200, then the
image will be reduced in size if it is taller or wider than 1200
pixels.

Note that the image file type of the uploaded file may be changed to
[PNG] during the conversion process. Different browsers behave
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
[`maximum image size` field modifier]. To override the setting in
order to allow image uploads of any resolution, use `None` as the
override value.

## <a name="image upload type"></a>Converting the format of uploaded images

If you are using `maximum image size`, you can also cause images to be
converted to [PNG], [JPEG], or [BMP] by the browser during the upload
process by setting the `image upload type` to `png`, `jpeg`, or `bmp`.

{% highlight yaml %}
image upload type: jpeg
{% endhighlight %}

## <a name="celery processes"></a><a name="max celery processes"></a>Number of concurrent background tasks

**docassemble** uses [Celery] to execute background tasks. The
[Celery] system is able to execute multiple tasks concurrently. The
number of concurrent workers is set by default to the number of CPU
cores on the machine, except that the number of workers will not be
larger than the number of gigabytes of total memory divided by 2. For
example:

* If a machine has 4 CPU cores and 16GB of RAM, four [Celery] workers
  will be started (CPU limited)
* If a machine has 32 CPU cores and 16GB of RAM, eight [Celery]
  workers will be started (memory limited).

The number of CPUs is determined by calling `nproc --all`. Note that
the result may be the same or may be different from the number of
`vCPUs` that a virtual machine has.

If you want to manually override this formula, set the `celery
processes` directive.

{% highlight yaml %}
celery processes: 15
{% endhighlight %}

This will cause 15 [Celery] workers to be spawned.

Note that there are two [Celery] systems: one called `celerysingle`
with a single worker, and one called `celery` with one or more
workers. The `celerysingle` system is used for background processes
that will perform parallel processing and use every CPU in the
machine; it would be dangerous to run more than one such process at a
time. The `celery` system is used for all other tasks, which [Celery]
may run in parallel on all the available worker processes. Thus, if
the `celery processes` is `15`, the [`worker_concurrency`] will be `1`
for `celerysingle` and `14` for `celery`. You can see this if you do
`ps ax | grep celery` on the server.

If you want the number of [Celery] processes to scale with CPU but you
think your system can handle more concurrency than the standard
formula would provide, you can set a higher maximum:

{% highlight yaml %}
max celery processes: 10
{% endhighlight %}

This setting will mean that:

* If a machine has 8 CPUs and 4GB of RAM, the number of celery
  processes will be 8 (`1` for `celerysingle` and `7` for `celery`).
* If a machine has 32 CPUs and 4GB of RAM, the number of celery
  processes will be 10 (`1` for `celerysingle` and `9` for `celery`).

It is important not to spawn too many [Celery] workers because each of
them loads software into its own memory space, which could cause your
memory to be exhausted.

## <a name="run oauthlib on http"></a>Using oauthlib on http servers

If you use the `oauthlib` library and users access your server using
`http://` rather than `https://`, set `run oauthlib on http` to
`True`.

{% highlight yaml %}
run oauthlib on http: True
{% endhighlight %}

This will set the environment variable `OAUTHLIB_INSECURE_TRANSPORT`
to `1`.

## <a name="office addin url"></a>Microsoft Word sidebar

You will need to set `office addin url` if you are running a
[Microsoft Word sidebar] from a location other than your own server.

As a security measure, when a [Microsoft Word sidebar] communicates
with your server, your **docassemble** server will only allow
communications that come from a particular hostname on the internet.

The `office addin url` directive in the Configuration specifies which
hostname is allowed.

{% highlight yaml %}
office addin url: https://sidebar.example.com
{% endhighlight %}

This means that your server will only allow [Microsoft Word sidebar]
communications that originate from https://sidebar.example.com.

If you don't set `office addin url`, the value of [`url root`] will be
used, and if [`url root`] is not set, the URL will be discerned from
the HTTP request. However, if your server is behind a proxy, this
latter method may not be accurate, so should [`url root`] in order for
the [Microsoft Word sidebar] to work correctly.

Note that a Word sidebar is just a web page that consists of an [HTML]
file with some [CSS] and [JavaScript] files associated with it. These
files can be hosted on any site on the internet as long as HTTPS is in
use. (Microsoft requires HTTPS.)  When your Microsoft Word
application accesses this web page, you can click the "Use a different
server" button to instruct the sidebar to access the [Playground] on
any server to which you have access. Then the [JavaScript] on the page
will communicate directly with that server and pass information back
and forth between Microsoft Word and the [Playground] on the server.

Your **docassemble** server can serve as the host for the web page.
If your server's hostname is https://interviews.example.com, then the
sidebar will be available at
https://interviews.example.com/officetaskpane. If you create an [XML
manifest file] for the sidebar from the [Utilities] page of your
server, you will see this URL embedded in the XML.

## <a name="timezone"></a>Setting the time zone

Functions like [`as_datetime()`] that deal with dates will use a
default time zone if an explicit timezone is not supplied. If you set
the `timezone` directive to something like `America/Los_Angeles`, this
will be used as the default time zone. Otherwise, the default time
zone will be set to the time zone of the server.

{% highlight yaml %}
timezone: America/Los_Angeles
{% endhighlight %}

For a list of valid time zones, see the [tz database].

If you change the `timezone`, you need to do a `docker stop` and
`docker start` so that the operating system recognizes the change.

## <a name="pypi"></a>Sharing packages on PyPI

If you want users of your server with `developer` privleges to be able
to publish packages to [PyPI] from the [packages folder] of the
[Playground], set `pypi` to `True`:

{% highlight yaml %}
pypi: True
{% endhighlight %}

Then, a user with `developer` privileges can configure a [PyPI]
username and password on their [Profile]. Typically, the username is
`__token__` and the password is a long security token beginning with
`pypi-`. This is available from [PyPI] when you create an account and
create an API token. If using `twine` from the command line, you would
set up this username and password in a `.pypirc` file. **docassemble**
runs `twine` to upload to [PyPI] and it passes this username and
password to `twine`.

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
URL will be stored. You may need to edit this if you run
**docassemble** on a non-standard operating system.

## <a name="oauth"></a>Facebook, Google, Auth0, Keycloak, Authentik, Zitadel, miniOrange, and Azure login

If you want to enable logging in with Facebook, Google, Auth0,
KeyCloak, Authentik, Zitadel, miniOrange, or Microsoft Azure, you will
need to tell **docassemble** your [OAuth2] keys for these services:

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
  auth0:
    enable: True
    id: ceyd6imTYxTNmuj2CYpwH_cEhdWt93e6
    secret: LLGEBDrrgDFDfBsFjErsdSdsntkrtAbfa4ee3ss_adfdSDFEWEsfgHTerjNsd3dD
    domain: example.auth0.com
  keycloak:
    enable: True
    id: example
    secret: ifYzXtUv7WlSkWjMbHwgvgk0aACoXTcF
    domain: "keycloak.mysite.com"
    protocol: "https://"
    realm: master
  authentik:
    enable: True
    id: 29zWxVegWUEaIh75WTOAg9jUnbpAOiuc683JmL2s
    secret: 6dg8kgi8I87xcYxaOu2LSamj7cWE4j6VxC1bPcGTIl4ddMXr3Xaq6IBLo3TupITFylydPciPLULOKxIff3LmT7FxIOmEcnAsUdQf7OG3334S4FlMzEXhGFgFOARnYcVo
    application slug: myapplication-authentik
    domain: myserver:9000
    protocol: "http://"
  zitadel:
    enable: True
    id: 168422810448705515@yourprojectname
    domain: your-instance-name-edy3i2.zitadel.cloud
  miniorange:
    enable: True
    id: TQBwKWUcsECMUIkCctjxLQjPFXdIsnYU
    secret: lTUyixltiJmMMKhXYulCBrKWbFbXPrdy
    domain: myserver.com
  azure:
    enable: True
    id: e378beb1-0bfb-45bc-9b4b-604dcf640c87
    secret: UwHEze20pzSO+lvywJOjcos3v7Kd6Y7tsaCYTG7Panc=
{% endhighlight %}

You can disable these login methods by setting `enable` to `False` or
by removing the configuration entirely.

For more information about how to obtain these keys, see the
[installation] page's sections on [Facebook], [Google], [Auth0],
[Keycloak], [Authentik], [Zitadel], [miniOrange] and [Azure].

Note that in [YAML], dictionary keys must be unique. So you can only
have one `ouath:` line in your configuration. Put all of your
[OAuth2] configuration details (for Google logins, Google Drive
integration, OneDrive integration, etc.) within a single `oauth`
directive.

If an external authentication method is used, the decryption key for
server-side encryption is based on information sent back by the
external authentication provider. Encryption still happens (e.g., when
`multi_user` is not set to `True`), but the encryption key is not a
secret The protection offered by server-side encryption will be less,
because a resourceful hacker could figure out the encryption key for
decrypting interview answers, based on information stored unencrypted
on the server.

<a name="allow external auth with admin accounts"></a>By default,
users who log with an authentication mechanism other than
username/password cannot have their privileges elevated to
`admin`. However, if you want to take the risk that administrators
could be locked out of their accounts if the external authentication
mechanism fails, you can set `allow external auth with admin accounts`
to `True`:

{% highlight yaml %}
allow external auth with admin accounts: True
{% endhighlight %}

<a name="allow external auth with multiple methods"></a>By default, a
use who signs in for the first time (registers) with one external
authentication method cannot then log in using a different external
authentication method that is connected with the same email address.

However, if you want to allow users to do this, set `allow external
auth with multiple methods` to `True`:

{% highlight yaml %}
allow external auth with multiple methods: True
{% endhighlight %}

The default is `False`.

Note that if you enable this feature, users may experience an apparent
loss in access to sessions. While they are allowed to log in to the
same account, because it has the same email address, the encryption
key will be different because the authentication method is different.

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

## <a name="onedrive"></a>OneDrive configuration

To enable the [OneDrive synchronization] feature, add
a `onedrive` entry to your [`oauth`](#oauth) configuration with
your [OAuth2] keys for [OneDrive].

{% highlight yaml %}
oauth:
  onedrive:
    enable: True
    id: 7df57ca4-d736-84b3-9aec-746c63b8e88d
    secret: "xcyTW522[bip)BIWXY92YsT"
{% endhighlight %}

For more information about obtaining these keys, see the
[OneDrive]({{ site.baseurl }}/docs/installation.html#onedrive)
section of the [installation] page.

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
  whatsapp number: "+12762268342"
  mms attachments: False
  dispatch:
    color: docassemble.base:data/questions/examples/buttons-code-color.yml
    doors: docassemble.base:data/questions/examples/doors.yml
  default interview: docassemble.base:data/questions/default-interview.yml
{% endhighlight %}

The `sms: True` line tells **docassemble** that you intend to use the
text messaging features. This should be set to `True` even if you only
intend to use [WhatsApp].

The `voice: True` line tells **docassemble** that you intend to use the
[call forwarding] feature.

The `account sid` is a value you copy and paste from your [Twilio]
account dashboard.

The `auth token` is another value you copy and paste from your
[Twilio] account dashboard. This is only necessary if you intend to
use the [`send_sms()`] function or the [phone login] feature.

The `number` is the phone number you purchased. The phone number
must be written in [E.164] format. This is the phone number with
which your users will exchange [SMS] messages.

The `whatsapp number` (optional) is the phone number you use for
sending [WhatsApp] messages. The number must be written in [E.164]
format.

The `mms attachments` (optional) option allows you to indicate whether
MMS should be used to deliver documents to the user when a `question`
has `attachments`, `attachment`, or `attachment code`. When `mms
attachments` is `True` (which is the default), **docassemble** will
only deliver PDF attachments (because Twilio blocks other content
types). If you set `mms attachments: False`, then instead of using
MMS, **docassemble** will include hyperlinks to PDF, RTF, and DOCX
attachments.

The `dispatch` configuration allows you to direct users to different
interviews. For example, with the above configuration, you can tell
your prospective users to "text 'color' to 276-241-0114."  Users who
initiate a conversation by sending the SMS message "help" to the
[Twilio] phone number will be started into the
`docassemble.base:data/questions/examples/sms.yml` interview.

The [`default interview`] configuration allows you to set an interview
that will be used in case the user's initial message does not match up
with a `dispatch` entry. If you do not set a [`default interview`], the
global [`default interview`] will be used. If you want unknown
messages to be ignored, set [`default interview`] to `null`.

### <a name="multiple twilio"></a>Multiple Twilio configurations

You can use multiple [Twilio] configurations on the same server. You
might wish to do this if you want to advertise more than one [Twilio]
number to your users. You can do this by specifying the `twilio`
directive as a list of dictionaries, and giving each dictionary a
`name`. In this example, there are two configurations, one named
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
    default interview: docassemble.base:data/questions/default-interview.yml
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
be used as the default. The [call forwarding] feature uses the
default configuration.

## <a name="fax provider"></a>Fax configuration

The [fax sending] feature was previously provided by [Twilio], but
[Twilio] discontinued support for sending faxes in 2021. If you want
to use the [`send_fax()`] function, you will need to create an account
with [ClickSend] or [Telnyx].

When using [ClickSend] or [Telnyx], set `fax provider` to
either `clicksend` or `telnyx`. The default value is `clicksend`.

### <a name="clicksend"></a>ClickSend configuration

Sending faxes through [ClickSend] is enabled by setting `fax provider`
to `clicksend` and specifying a `clicksend` configuration directive.

Here is an example:

{% highlight yaml %}
fax provider: clicksend
clicksend:
  api username: "dev@example.com"
  api key: "F8BE02C1-D95E-D3A9-297B-0028EFB6163B"
  number: "+12762510247"
  from email: "jsmith@example.com"
{% endhighlight %}

The `api username` is the username that you use to log into
[ClickSend]. This is usually the e-mail address that you used when
you created the account.

The `api key` is a code that you can find in the [ClickSend] dashboard
under "API credentials."  You may need to generate the API Key.

The `number` is the fax phone number you purchased. You can find the
phone number under Numbers, Fax in the [ClickSend] dashboard. The
phone number must be written in [E.164] format.

The `from email` is a field that [ClickSend] uses in its Fax API. The
documentation describes it as "An email address where the reply should
be emailed to."

After setting up your phone number, you need to go to Messaging
Settings, then go to the Fax tab, then go to the Delivery Reports
tab. Then click "Add new rule."  Add a rule called "post fax delivery
report" with "Match For" set to "All reports."  Set the "Action" to
"URL," and under "URL," type in the address of your docassemble server
followed by `/clicksend_fax_callback`. For example, if your server is
at `https://docassemble.example.com`, you would write
`https://docassemble.example.com/clicksend_fax_callback`. Then make
sure that the rule is set to "enabled."

#### <a name="multiple clicksend"></a>Multiple ClickSend configurations

You can use multiple [ClickSend] configurations on the same server.
You might wish to do this if you want to use more than one [ClickSend]
fax number and/or account to send faxes. You can do this by
specifying the `clicksend` directive as a list of dictionaries, and
giving each dictionary a `name`. In this example, there are two
configurations, one named `default`, and one named `bankruptcy`:

{% highlight yaml %}
clicksend:
  - name: default
    api username: "dev@example.com"
    api key: "F8BE02C1-D95E-D3A9-297B-0028EFB6163B"
    number: "+12762510247"
    from email: "jsmith@example.com"
  - name: bankruptcy
    api username: "dev2@example.com"
    api key: "E7CE2453-253F-E3C1-3562-0129EDB727BC"
    number: "+13012503257"
    from email: "help@example.com"
{% endhighlight %}

When you call [`send_fax()`], you can indicate which configuration
should be used:

{% highlight python %}
send_fax(to='202-943-0949', welcome_fax, config='bankruptcy')
{% endhighlight %}

This will cause the fax to be sent from 301-250-3257.

If no configuration is named `default`, the first configuration will
be used as the default.

### <a name="telnyx"></a>Telnyx configuration

Sending faxes through [Telnyx] is enabled by setting `fax provider`
to `telnyx` and specifying a `telnyx` configuration directive.

Here is an example:

{% highlight yaml %}
fax provider: telnyx
telnyx:
  number: "+16052519139"
  api key: "KEY017D2E7B3D5C992F50E721E560AD262F_pYbe5lWyefduFhfUv2eUdd"
  app id: "1823943157766443451"
{% endhighlight %}

The `api key` is a code that you can find in the [Telnyx] portal
under "API Keys."  You may need to generate the API Key.

The `app id` is the "App ID" of the "Fax Application" you want to use.

The `number` is the fax phone number you purchased. You can find the
phone number under Numbers in the [Telnyx] portal. The
phone number must be written in [E.164] format.

To set up Telnyx for use with **docassemble**, go to [Telnyx] and sign
up for an account. You will need to provide your credit card
information and add some money to your Balance.

Go to "Numbers" and then "Search & Buy Numbers" to set up a phone
number to use for faxing. Make a note of the phone number; you will
need to put the phone number into your `telnyx` configuration as the
`number`, in [E.164] format (e.g., `+12025551515`).

Go to "API Keys" and create an API key for use with "Telnyx API v2."
Make a note of the API key; you will need to put the API key into your
`telnyx` configuration as the `api key`.

Go to "Programmable Fax" and click "Add new App."  Give your "Fax
Application" a name like "docassemble fax" (or whatever you
want). Make a note of the "App ID"; this is what you will need to set
in your `telnyx` configuration as the `app id`. Under "Send a webhook
to the URL," put in the URL of your server, followed by
`/telnyx_fax_callback`. For example, if your server is at
`https://docassemble.example.com`, you would write
`https://docassemble.example.com/telnyx_fax_callback`. Then, under
"Outbound Settings," set the "Outbound Voice Profile" to "Default" or
to whatever other Outbound Voice Profile you want to use. You can
click "Outbound Voice Profile" in the navigation menu to see the
Outbound Voice Profiles that are configured on your account.

#### <a name="multiple telnyx"></a>Multiple Telnyx configurations

You can use multiple [Telnyx] configurations on the same server.
You might wish to do this if you want to use more than one [Telnyx]
fax number and/or account to send faxes. You can do this by
specifying the `telnyx` directive as a list of dictionaries, and
giving each dictionary a `name`. In this example, there are two
configurations, one named `default`, and one named `bankruptcy`:

{% highlight yaml %}
telnyx:
  - name: default
    number: "+16052519139"
    api key: "KEY017D2E7B3D5C992F50E721E560AD262F_pYbe5lWyefduFhfUv2eUdd"
    app id: "1823943157766443451"
  - name: bankruptcy
    number: "+12025552033"
    api key: "KEY017D2F7B5D5C992Y51E731E860BD365E_qYZbf7lUyeRdrFjfJv3eYfe"
    app id: "1924953657746434242"
{% endhighlight %}

When you call [`send_fax()`], you can indicate which configuration
should be used:

{% highlight python %}
send_fax(to='202-943-0949', welcome_fax, config='bankruptcy')
{% endhighlight %}

This will cause the fax to be sent from 301-250-3257.

If no configuration is named `default`, the first configuration will
be used as the default.

## <a name="user agent"></a>User agent for downloading files

Functions such as [`path_and_mimetype()`] will download files from the
internet. When the server downloads the file, it reports its [user
agent] as `curl/7.64.0` by default. This might cause problems
for your interviews because some web sites may not want to serve files
to a user that identifies itself as a "robot."

To use a different [user agent], you can set the `user agent`
configuration directive. For example:

{% highlight yaml %}
user agent: Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0
{% endhighlight %}

## <a name="brute force"></a>Protecting against multiple login attempts

By default, users who unsuccessfully log in are blocked after 10
failed attempts. This is a form of security protection against bots
that try to guess passwords by repeatedly logging in.

The block is based on IP address, so if users share an outgoing WAN IP
address, all of those users are blocked.

The threshold of 10 failed attempts can be configured with `attempt limit`.

The time period for blocking defaults to 86,400 seconds (one day).
The number of seconds of blocking can be configured with `ban period`.

{% highlight yaml %}
attempt limit: 5
ban period: 3600
{% endhighlight %}

Restarting the server will clear out all IP address bans. The server
can be restarted [through the API]({{ site.baseurl
}}/docs/api.html#restart) or by going to the Configuration and
pressing Save (without making any changes).

This feature can be turned off by setting `ip address ban enabled` to
false.

{% highlight yaml %}
ip address ban enabled: False
{% endhighlight %}

## <a name="phone login"></a>Phone login verification codes

When you use the [phone login] feature, the user needs to enter a 5
digit code that they receive via SMS. The number of digits in this
code can be configured with `verification code digits`. The code is
only valid for a limited period of time. This period of time defaults
to 180 seconds and is configurable with `verification code timeout`.

{% highlight yaml %}
verification code digits: 6
verification code timeout: 360
{% endhighlight %}

## <a name="loop limit"></a><a name="recursion limit"></a>Infinite loop protection

Since **docassemble** allows you to write code in a declarative
fashion, it needs to do a lot of looping and recursion. If you make a
mistake in your [interview logic] and use circular reasoning, you may
send **docassemble** into an infinite loop. Sometimes these infinite
loops can be detected and a warning raised, but other times they are
hard to detect because even deliberate code could loop or recurse for
a long time. Thus, **docassemble** has hard limits on the amount of
looping and recursion it will do. By default, these limits are set to
500 loops and 500 recursions. If you get an error that "there appears to
be an infinite loop" or "there appears to be a circularity," then
these limits were exceeded. If you want to change these limits on a
global level in your system, you can include use the `loop limit` and
`recursion limit` directives:

{% highlight yaml %}
loop limit: 600
recursion limit: 600
{% endhighlight %}

It is important that some reasonable limit be in place, because if the
server is in development mode, an infinite loop could result in the
memory of the machine being exceeded, which could
cause the system to crash.

You can also change these limits on a per-interview basis with the
[`loop limit` and `recursion limit` features]

## <a name="editable mimetypes"></a><a name="editable extensions"></a>Editable file types

By default, the only file types that can be edited in the folders of
the Playground are `text` [MIME] types and file types that are used in
**docassemble**, like [YAML], [CSS], [JavaScript], and [HTML]. Other
types are presumed to be non-editable, and there is no "Edit" button
next to the file in the Playground folder.

You can make additional file types editable using `editable mimetypes`
or `editable extensions`. For example, if you wanted to be able to
edit RTF files in the Playground folders, you could add:

{% highlight yaml %}
editable mimetypes:
  - application/rtf
{% endhighlight %}

Or if you had a text file format that was not associated with a [MIME]
type and that ended in `.law`, you could add:

{% highlight yaml %}
editable extensions:
  - law
{% endhighlight %}

## <a name="new markdown to docx"></a>Inserting Markdown templates in Word files

Originally, when inserting the results of a [`template`] in DOCX file
that you assemble using [`docx template file`], you would include the
template as follows:

> {% raw %}{{r the_template }}{% endraw %}
{: .blockquote}

The template text would be inserted as a single "run," meaning that it
cannot contain any proper paragraph breaks, only manual line breaks.

There is a newer system of inserting Markdown [`template`]s into
[`docx template file`]s, which can handle multiple paragraphs and a
wider variety of Markdown. However, this new system is not backwards
compatible with the original system, because under the new system you
need to include the [`template`] as follows:

> {% raw %}{{p the_template }}{% endraw %}
{: .blockquote}

To upgrade to the new system today, set the following in your
Configuration:

{% highlight yaml %}
new markdown to docx: True
{% endhighlight %}

The new system will become the default at some point in the future, so
when you have time, you should adapt your DOCX files if you are using
`{% raw %}{{r ... }}{% endraw %}` to insert [`template`]s.

## <a name="web server"></a>Choosing Apache instead of NGINX

By default, the web server used with [Docker] is [NGINX]. You can
change this to [Apache] by adding the following to your Configuration:

{% highlight yaml %}
web server: apache
{% endhighlight %}

The default is `nginx`. After changing this, you will need to do a
[`docker stop -t 600`] followed by a [`docker start`]. This feature
requires system version 0.5.0 or later.

See also the [`DAWEBSERVER`] environment variable.

## <a name="use nginx to serve files"></a>Using NGINX to serve files

The `X-Accel-Redirect` feature of [NGINX] allows Python, running
inside of `uwsgi`, to serve a file in response to an HTTP request by
returning an empty response instead of a response with the content of
the file in the body. Python tells [NGINX] the file to be served by
setting the `X-Accel-Redirect` header of the empty response to the
file system path. [NGINX] intercepts the response and serves the file to the
user. This increases efficiency because Python code does not have to
process the contents of the file.

The value of `use nginx to serve files` is `False` unless set to
`True` in the Configuration.

{% highlight yaml %}
use nginx to serve files: True
{% endhighlight %}

If you use [NGINX], the value of this should be `True` unless the
`X-Accel-Redirect` feature causes problems for some reason. The
default value is `False` only for backwards compatibility with system
versions prior to 1.7.8; a change to the NGINX configuration is
required to enable this feature to work. In the default Configuration
for new systems, `use nginx to serve files` is `True`.

See also the [`USENGINXTOSERVEFILES`] environment variable.

## <a name="use minio"></a>Use of MinIO

If you are using [MinIO] in combination with an [S3](#s3)
configuration, and you would like the bucket to be created when the
container starts, then set `use minio` to `True`.

{% highlight yaml %}
use minio: True
{% endhighlight %}

See also the [`USEMINIO`] environment variable for [Docker].

## <a name="use cloud urls"></a>URLs pointing to files in cloud server

If you are using [S3] or [Azure blob storage], then for efficiency,
URLs to files can link directly to the cloud provider (using temporary
URLs). To enable this, set `use cloud urls` to `True`:

{% highlight yaml %}
use cloud urls: True
{% endhighlight %}

However, this can cause problems with [Cross-Origin Resource Sharing],
and will not work if you are using an [S3]-compatible cloud storage
system that is not accessible from the user's network.

The default is to serve files from the **docassemble** application server.

## <a name="admin full width"></a>Wide-screen appearance of administrative screens

By default, **docassemble** uses the [Bootstrap] `container` class for
administrative screens, which is responsive but fixed-width at
particular breakpoints. If you want to use the [Bootstrap]
`container-fluid` class instead, set:

{% highlight yaml %}
admin full width: True
{% endhighlight %}

This will result in full width screens.

## <a name="wrap lines in playground"></a>Line wrapping in the Playground

By default, the editor in the Playground will wrap long lines. To see
whether a line is wrapped, you can look at the line number. To
turn off line wrapping, set:

{% highlight yaml %}
wrap lines in playground: False
{% endhighlight %}

## <a name="allow embedding"></a>Allowing interviews to be embedded in another site

By default, cookies will be sent with the [SameSite] flag set to
`Lax`, so that cookies will not work if the address in the location
bar does not match the address of the **docassemble** server. This
will prevent the embedding of a **docassemble** interview in a
third-party site. To enable embedding, set `allow embedding` to
`True`.

{% highlight yaml %}
allow embedding: True
{% endhighlight %}

If `allow embedding` is `True`, cookies will be sent with the
[SameSite] flag set to `'None'`. If `allow embedding` is `False`, the
cookies will be sent with the [SameSite] flag set to `'Strict'`. If
`allow embedding` is set to `'Lax'`, the cookies will be sent with the
[SameSite] flag set to `'Lax'`. The default is `'Lax'`.

If you set `allow embedding` to `True`, your site must use HTTPS or
else some browsers will refuse to save cookies, and your users will
not be able to use the site. If you are using a load balancer or a
proxy server that provides SSL termination, you must set `behind https
load balancer` to `True`.

Note that if you set `allow embedding: False`, users will have trouble
logging in through third-party single-sign-on mechanisms.

See also [`cross site domains`].

## <a name="pagination limit"></a>Pagination limit

The [API]({{ site.baseurl }}/docs/api.html), the [My Interviews] page,
and the [user list] page employ pagination when providing a long list
of items. By default, 100 items are returned per page. This number
can be changed to a number between 2 and 1000 using the `pagination
limit` directive.

{% highlight yaml %}
pagination limit: 50
{% endhighlight %}

## <a name="pip index"></a>Python package index

By default, Python packages are installed from [PyPI] using
`pip`. However, `pip` can be configured to use a different package
index (`--index-url`). To configure this, set the `pip index url`
directive.

{% highlight yaml %}
pip index url: https://myserver.com
{% endhighlight %}

The `pip` configuration also allows you to configure additional
package index sites (`--extra-index-url`). You can set this as well.

{% highlight yaml %}
pip extra index urls: https://myserver.com https://myotherserver.com
{% endhighlight %}

## <a name="jinja data"></a>Variables for Jinja2 YAML preprocessor

When using [Jinja2] as a [YAML preprocessor], you can pass variables
from the Configuration to the [Jinja2] context.

{% highlight yaml %}
jinja data:
  verbosity: 2
  region: Delaware
{% endhighlight %}

## <a name="locktimeout"></a>Concurrency lock timeout

Python code that runs inside a **docassemble** session needs to have
exclusive access to the interview answers between the time it reads
the interview answers from the database and the time it writes the
interview answers to the database. It would be a problem if, for
example, a [scheduled task] tried to make changes to the interview
answers of a session at the same time that the web application was
assembling a document.

**docassemble** uses a [Redis]-based locking mechanism to ensure that
when one Python process is using the interview answers of a session,
other processes that want to use those interview answers must wait for
the first process to finish before retrieving the interview answers
from the database.

For example, suppose your interview logic, upon receiving input from
the user's web browser, launches a background task, but then the
interview logic performs a computation task that takes two seconds to
complete. The background task will start running inside of a [Celery]
worker while the web application is still performing its computation
task. Before retrieving the interview answers, the background task
will check [Redis] to see whether the interview answers are in use by
another process, and it will wait until the interview answers are
free.

However, what would happen if there is a bug in the computation code
that causes it to run forever? At some point the web browser will give
up on the process and it will be terminated in 90 seconds or
so. How long should a process be able to maintain exclusive access to
the interview answers? If a process can lock up the interview answers for
a long period of time, the user could perceive that the server has
"crashed."

To avoid this problem, there is a limit on how long a process can keep
the interview answers locked. This is set to four seconds by default.

You can change this period to something else by setting `concurrency
lock timeout`:

{% highlight yaml %}
concurrency lock timeout: 10
{% endhighlight %}

This means that the lock on the interview answers will automatically
expire after 10 seconds, after which a waiting Python process (such as a
[scheduled task] or [background task]) can step in and seize control.

Whatever the `concurrency lock timeout` period is, you should consider
it to be a threshold for when you decide to move a computation to a
background task. If `concurrency lock timeout` is `4` (the default),
then any computation that takes more than four seconds should be moved
to a background task. For example, if you have a complicated document
that takes six seconds to assemble, your user will see a spinner in
the web application because it will take at least six seconds for the
server to respond to the HTTP request from the browser. This is a
dangerous situation for the integrity of your interview answers,
because after four seconds have elapsed, your document assembly task
will still be proceeding, but its exclusive lock on the
interview answers will have expired, and another web application
process, a [background task], or a [scheduled task] could start
using the interview answers.

The [background task] enables computations to run for a long time
without tying up the interview answers. Although the [background task]
waits for the interview answers to be available before reading them,
it does not put a hold on the interview answers while the background
task is proceeding. If the background task needs to save changes to
the interview answers, it does so through a separate
[`background_response_action()`] process, which waits for the
interview answers to be available and then takes control of the
interview answers so that it can save information to them.

Changing `concurrency lock timeout` is generally not recommended. An
HTTP request to a server should return quickly, and if you need to
perform long-running computations, the [background tasks] system is
the best way to run those computations.

## <a name="permissions"></a>Permissions

You can customize **docassemble**'s [privileges] system using the
`permissions` directive. This allows you to specify that users with a
particular [privilege] have the permission to perform particular
actions on the server that normally are limited to users with special
privileges like `admin`, `developer`, and `advocate`.

{% highlight yaml %}
permissions:
  apiuser:
    - access_user_info
    - edit_user_active_status
    - edit_user_password
  playgroundadmin:
    - playground_control
{% endhighlight %}

The permissions available are as follows:

* `demo_interviews` - run interviews in `docassemble.base` and
  `docassemble.demo` if `debug` is `False` and `allow demo` is not `True`
* `access_sessions` - list and see other users' session
* `edit_sessions` - delete other users' sessions
* `access_user_info` - see information about other users
* `access_user_api_info` - see information about other users' API keys
* `create_user` - create a new user and invite a user
* `edit_user_info` - set information in a user profile
* `edit_user_api_info` - modify others users' API keys
* `edit_user_active_status` - set a user account to inactive or active
* `delete_user` - delete a user account and its data. Since deleting a
  user also involves deleting sessions, a user must also have
  `access_sessions` and `edit_sessions` permissions in order to delete
  users.
* `edit_user_password` - change another user's password (however, only
  an `admin` can change the password of a user with `admin`,
  `developer`, or `advocate` privileges)
* `template_parse` - access the `/api/fields` API
* `access_privileges` - see a list of the available privileges defined
  in the system
* `edit_privileges` - add or delete custom privileges (also requires
  `access_privileges`)
* `edit_user_privileges` - edit the privileges of other users
  (however, only an `admin` can edit the privileges of user with
  `admin`, `developer`, or `advocate` privileges, or convey those
  privileges to a user)
* `playground_control` - can perform actions in any user's Playground
* `log_user_in` - can use the [`/api/login_url`] endpoint of the [API]

If you are using the [API] and you have `admin` privileges, you can
create API keys under your user profile that have limited permissions,
just as you can limit the privileges associated with custom
[privileges]. When you create an API key, you can choose to limit the
powers of the API key to one or more of the above permissions.

The special privilege `anonymous` can be used if you want to confer
privileges on users who are not logged in. For example:

{% highlight yaml %}
permissions:
  anonymous:
    - create_user
    - access_user_info
{% endhighlight %}

However, please be aware of the security implications of giving
elevated privileges to non-logged in users.

## <a name="supervisor"></a>Username and password for the supervisord daemon

For increased security when using a [multi-server arrangement],
**docassemble** has the option of using a username and password when
**docassemble** containers need to send [supervisor] commands to
themselves or to others. The username and password are set through the
[Docker] environment variables `DASUPERVISORUSERNAME` and
`DASUPERVISORPASSWORD`. The values of these variables are stored in
the `supervisor` directive of the Configuration, which is a dictionary
with keys `user` and `password`. This directive should be considered
read-only; it will be set from environment variables when the server
starts and never be changed. Although the `supervisor` directive will
be visible when calling [`get_config()`], it should not appear in your
Configuration YAML.

## <a name="module whitelist"></a><a name="module blacklist"></a>Controlling which docassemble add-on modules are loaded

By default, when docassemble starts or restarts (specifically, when
the `docassemble.webapp.server` module loads), it searches through the
`.py` files located within the `docassemble` namespace and `import`s
the module if the `.py` file contains a line that starts with `#
pre-load`, `class`, or `docassemble.base.util.update`. However, if the
first line of the module is `# do not pre-load`, then the module is
not imported. Note that the Modules folder in each developer's
Playground (and each project therein) is part of the `docassemble`
namespace, so all of those modules are eligible for being
automatically imported.

This means that if you write modules containing code that has global
side effects, you need to be mindful that you do not have multiple
conflicting versions of that code installed on your server. Even
though you may not run any interviews that use a module, that module
will be automatically loaded into memory when **docassemble**
starts. Code that has global effects includes:

* [`SQLObject`] class declarations
* [`CustomDataType`] class declarations
* [`docassemble.base.util.update_word_collection()`] function calls
* [`docassemble.base.util.update_locale()`] function calls
* [`docassemble.base.util.update_language_function()`] function calls
* [`docassemble.base.util.update_nice_numbers()`] function calls
* [`docassemble.base.util.update_ordinal_numbers()`] function calls
* [`docassemble.base.util.update_ordinal_function()`] function calls
* [Custom endpoints]({{ site.baseurl }}/docs/recipes.html#flask page)

The `module whitelist` and `module blacklist` Configuration directives
allow you to override the normal methods that **docassemble** uses to
choose which modules are automatically loaded.

{% highlight yaml %}
module whitelist:
  - docassemble.familylaw.objects
  - docassemble.mypackage.*
{% endhighlight %}

If you specify a `module whitelist`, then **docassemble** will load
all installed modules that match the module names listed, and will not
load any other modules. Even if you include `# pre-load` in a module
file, it will not automatically load unless the module matches one of
the items under `module whitelist`.

The wildcard character `*` can be used. In the example above, all
modules under `docassemble.mypackage` will be loaded.

Note that all module files that match `module whitelist` entries will
be loaded, regardless of whether they would otherwise have been
preloaded based on their content, and regardless of whether the file
contains the line `# do not pre-load`.

{% highlight yaml %}
module blacklist:
  - docassemble.playground*
  - docassemble.familylaw.oldobjects
{% endhighlight %}

If you specify a `module blacklist`, then any modules in the
`docassemble` namespace that match any of the items under `module
blacklist` will not be automatically loaded. In the example above, all
modules in every user's Playground are prevented from loading
automatically. The module `docassemble.familylaw.oldobjects` is also
singled out for exclusion.

Note that `module blacklist` only affects the auto-loading of
modules. If you have an interview that loads a module using
[`imports`] or [`modules`], or you load code that `import`s the
module, the module will still be loaded. `module blacklist` only
affects the auto-loading of modules that happens when **docassemble**
starts.

## <a name="celery modules"></a>Modules to be loaded in Celery

The [Celery] system, which handles background tasks, can be extended
using the `celery modules` directive in order to support launching
background tasks from [custom endpoints]. If you want to launch
background tasks from inside of interview logic, the `celery modules`
directive is not necessary and should not be used.

The `celery modules` directive accepts a list of modules that [Celery]
should load.

{% highlight yaml %}
celery modules:
  - docassemble.mypackage.custombg
{% endhighlight %}

Here is an example of what such a module might look like:

{% highlight python %}
# do not pre-load
from docassemble.webapp.worker_common import workerapp, bg_context, worker_controller as wc

@workerapp.task
def custom_comma_and_list(*pargs):
    with bg_context():
        return wc.util.comma_and_list(*pargs)
{% endhighlight %}

It is important to use the `# do not pre-load` directive on the first
line so that **docassemble** will not load the module in the wrong order.

The type of code that you can call within such a module is limited. It
is important that you do not import docassemble modules like
`docassemble.base.util` into a module loaded inside of Celery. If you
want to access names from `docassemble.base.util`, do so in the manner
shown above, where the function `comma_and_list()` in
`docassemble.base.util` is accessed by calling
`wc.util.comma_and_list()` inside of the `bg_context()` context.

Even then, some code in `docassemble.base.util` may not work as you
expect because it assumes that it is being called from within
interview logic, where the identity of the current user is known and
there is a specific session in a specific interview. Those
circumstances are not present in the context of a custom API endpoint.

## <a name="config from"></a>Importing configuration directives

The following sections, [Using AWS Secrets Manager](#aws_secrets) and
[Using Azure Key Vault](#azure_secrets), discuss how you can refer to
an [AWS Secret] or an [Azure Key Vault] Secret in your Configuration
using an [Amazon Resource Name] or [Key Vault Reference], and
**docassemble** will transparently replace reference with the contents
of the secret. The `config from` directive allows you to import
multiple Configuration directives from one of these secrets. For
example, suppose your entire Configuration consisted of this:

{% highlight yaml %}
debug: False
timezone: America/New_York
config from: arn:aws:secretsmanager:us-west-2:916432579235:secret:Config-AHE2yI
{% endhighlight %}

Suppose that your [AWS Secret], which in this example is named
`Config`, consists of the following [JSON] string:

{% highlight javascript %}
{
  "language": "en",
  "debug": true,
  "my db": {
    "name": "demo",
    "user": "docassemble",
    "password": "abc123",
    "host": "localhost",
    "port": "5432"
  }
}
{% endhighlight %}

When the Configuration loads, the [ARN] string will be replaced with
the dictionary data structure represented by the [JSON], and it will
be as though the Configuration consisted of this:

{% highlight yaml %}
debug: False
timezone: America/New_York
config from:
  language: en
  debug: True
  my db:
    name: demo
    user: docassemble
    password: abc123
    host: localhost
    port: 5432
{% endhighlight %}

The `config from` directive overlays its contents on top of the
Configuration. (It uses the Python `update()` method of the `dict`
object.)  The result is that your Configuration will effectively be
the following:

{% highlight yaml %}
debug: True
timezone: America/New_York
language: en
my db:
  name: demo
  user: docassemble
  password: abc123
  host: localhost
  port: 5432
{% endhighlight %}

However, the `config.yml` file on your server will only consist of:

{% highlight yaml %}
debug: False
timezone: America/New_York
config from: arn:aws:secretsmanager:us-west-2:916432579235:secret:Config-AHE2yI
{% endhighlight %}

Note that in this example, the `debug` directive was overridden from
`False` to `True` by the importing of directives from the `config
from` reference.

The `config from` directive allows you to maintain all of your
Configuration (or as much of your Configuration as you want) in a
secret on [AWS] or [Microsoft Azure]. Every time the server restarts,
the server will retrieve the `config from` secret from the cloud and
apply it to your Configuration. The contents of the Configuration
will not be stored in a file on the server; only the [ARN] reference
or [Key Vault Reference] will be visible in the `config.yml` file.

# <a name="aws_secrets"></a>Using AWS Secrets Manager

The Configuration supports the use of [AWS Secrets Manager]. When the
Configuration YAML is parsed, any string that begins with
`arn:aws:secretsmanager:` (even if it is inside of a nested structure)
will be treated as a request to incorporate by reference the contents
of an [AWS Secret] stored in the [AWS Secrets Manager] system.

For example, suppose your Configuration contains:

```
db: arn:aws:secretsmanager:us-west-2:916432579235:secret:DbConfig-AHE2yI
```

This indicates that you want the [`db`] configuration to be retrieved
from the [AWS Secret] called `DbConfig` that you have defined in your
[AWS Secrets Manager] account. The string
`arn:aws:secretsmanager:us-west-2:916432579235:secret:DbConfig-AHE2yI`
is an [Amazon Resource Name] that you can find in the properties of
the [AWS Secret].

The contents of the `DbConfig` secret will need to be a valid [JSON]
string referring to a [JavaScript] "object."  For example, this would
be a valid value for the `DbConfig` secret:

{% highlight javascript %}
{
  "prefix": "postgresql+psycopg2://",
  "name": "docassembledb",
  "user": "docassemble",
  "password": "ofiwf2438f34ferw",
  "host": "db.example.com",
}
{% endhighlight %}

This will have the same effect as having the following in your
Configuration:

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassembledb
  user: docassemble
  password: ofiwf2438f34ferw
  host: db.example.com
{% endhighlight %}

Effectively, the server replaces the [ARN] string with a [JSON]-converted
version of the [AWS Secret]. The contents of the secret are not
placed into the `config.yml` file. The contents exist in the memory
of **docassemble** but not on the file system.

In order to retrieve the contents of an [AWS Secret], **docassemble**
needs to authenticate with [AWS]. There are two ways this
authentication can happen:

1. Through EC2 role authentication (recommended);
2. With the `AWSACCESSKEY` and `AWSSECRETACCESSKEY` environment
   variables (possible, not not recommended).

The first method only works if you are running **docassemble** from an
[EC2] instance or some other server that can assume an "instance role."
If your server requests an [AWS Secret] from [AWS Secrets Manager] and
[AWS] can tell that the request is coming from a server that has an
[IAM] role to which is attached a "policy" that allows access to
secrets, then [AWS Secrets Manager] will allow access to the contents
of the secret even though your server did not provide any
authentication keys. This is a very clean way of retrieving secrets
because it does not involve storing access keys in the environment or
in a file.

You can use the second method (setting the `AWSACCESSKEY` and
`AWSSECRETACCESSKEY` environment variables) if your server is not
running on [EC2]. However, this is less secure because on [Docker],
it involves placing sensitive access keys in the environment.

# <a name="azure_secrets"></a>Using Azure Key Vault

The Configuration supports the use of [Azure Key Vault]. When the
Configuration [YAML] is parsed, any string that begins with
`@Microsoft.KeyVault(` (even if it is inside of a nested structure)
will be treated as a request to incorporate by reference the contents
of a Secret stored in the [Azure Key Vault] system.

To reference a secret in your Configuration, use a [Key Vault
Reference]. For example, suppose you have a [Key Vault] named
`abcincsecrets` that has a secret in it named `OAuthConfig` with a
"content type" of `application/x-yaml` and the following contents:

{% highlight yaml %}
github:
  enable: True
  id: ba45316c5951436328bc
  secret: 68e37cebd352f1ea36b6147cd52ff661c413f4b1
{% endhighlight %}

You could set the following in your Configuration:

{% highlight yaml %}
oauth: "@Microsoft.KeyVault(VaultName=abcincsecrets;SecretName=OAuthConfig)"
{% endhighlight %}

If authentication with [Azure Key Vault] succeeds, this will have the
same effect as having the following in your Configuration:

{% highlight yaml %}
oauth:
  github:
    enable: True
    id: ba45316c5951436328bc
    secret: 68e37cebd352f1ea36b6147cd52ff661c413f4b1
{% endhighlight %}

If authentication does not succeed, the `oauth` directive will be
defined as the string `'@Microsoft.KeyVault(VaultName=abcincsecrets;SecretName=OAuthConfig)'`.

A [Key Vault Reference] can be expressed a number of ways:

{% highlight text %}
@Microsoft.KeyVault(VaultName=abcincsecrets;SecretName=OAuthConfig)
@Microsoft.KeyVault(VaultName=abcincsecrets;SecretName=OAuthConfig;SecretVersion=812ebcd3b1273de76ed5405537f7ff27)
@Microsoft.KeyVault(SecretUri=https://abcincsecrets.vault.azure.net/secrets/OAuthConfig/)
@Microsoft.KeyVault(SecretUri=https://abcincsecrets.vault.azure.net/secrets/OAuthConfig)
@Microsoft.KeyVault(SecretUri=https://abcincsecrets.vault.azure.net/secrets/OAuthConfig/812ebcd3b1273de76ed5405537f7ff27/)
@Microsoft.KeyVault(SecretUri=https://abcincsecrets.vault.azure.net/secrets/OAuthConfig/812ebcd3b1273de76ed5405537f7ff27)
{% endhighlight %}

To start using [Azure Key Vault], open the [Azure Portal], search for
"Key vaults," and click "New" to create a new [Key Vault]. Give it a
name. Under "Access policy," choose "Azure role-based access
control."

There are two ways you can set up authentication to allow your
**docassemble** server to read secrets from your [Key Vault]:

* You can tell the [Key Vault] to allow access to your [Azure Virtual
  Machine] on the basis of the machine's [Identity]. This is the
  recommended method because it does not require storing any IDs or
  secrets in your **docassemble** server.
* [Registering] an Azure "app," telling the [Key Vault] to allow access to
  the "service principal" of that "app," and then passing the "app"'s
  "client ID," "secret," and "tenant ID" to **docassemble** as
  environment variables through Docker.

To use the first method, go to [Azure Portal] and open the Virtual
Machine that will run your **docassemble** server. Go to the
"Identity" section. Under the "System assigned" tab, set Status to
"On."  Press "Save."  Then open your [Key Vault] and go to the "Access
control (IAM)" section. Click the "Add role assignment" button.
Choose the role called "Key Vault Secrets User" and click Next. Under
"Assign access to," select "Managed identity."  Click "Select
members."  Select "Virtual Machine."  Your Virtual Machine should now
appear as an option; click it. Then press "Select."  Then press
"Next."  Then press "Review + assign."

To use the second method, go to [Azure Portal] and search for "App
registrations."

If you already have an app that you are using for **docassemble**, you
can use this app for retrieving secrets, if you want; you just need to
note the "Application (client) ID" and the "Directory (tenant) ID" in
the "Overview" section of the "app."  If you have already created a
"secret" for the "app" and you know what it is, go find it. If you
have not created any "client secrets" for the "app" yet, or you can't
locate the value of a secret you have created, go to the "Certificates
& secrets" section, create a new "client secret, and note the "Value"
of the secret.

If you do not already have an app, create one by clicking "New
registration."  Give it a name and press "Register."  Then open the
app and go to the "Certificates & secrets" section and click "New
client secret."  Type in a description of the secret, set an
expiration date, and click "Add."  Then, copy and save the "Value" of
the secret you just created; [Azure Portal] will not let you see this
value later, so you need to copy and save it now. Then go to the
Overview section and note the "Application (client) ID" and "Directory
(tenant) ID."

You will need to pass these three environment variables to `docker
run`:

* `AZURE_CLIENT_ID` -- the "Application (client) ID" associated with
  the "app."
* `AZURE_TENANT_ID` -- the "Directory (tenant) ID" associated with the
  "app."
* `AZURE_CLIENT_SECRET` -- the "Value" of a "client secret" listed in
  the "Certificates & secrets" section of the "app."

Note that Azure forces you to choose an expiration date for the secret
in the next two years. This means that before the secret expires, you
will need to re-run `docker run` with a new secret.

Once you have an "app" and you know what values you are going to use
for `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_CLIENT_SECRET`,
open your [Key Vault] and go to the "Access control (IAM)" section.
Click the "Add role assignment" button. Choose the role called "Key
Vault Secrets User" and click Next. Under "Assign access to," select
"User, group, or service principal."  Then click "Select members."
Under "Select," type in the name of your "app"; when it comes up,
click it, and press "Select."  Then press "Next."  Then
press "Review + assign."  Now you have told your Key Vault to allow
access to your "app," which means that anyone with the "Application
(client) ID," "Directory (tenant) ID," and "secret" associated with the
"app" can access the values of "Secrets" in your Key Vault.

Now that you have a "Key Vault" and you have told the "Key Vault" to
allow access to your **docassemble** server, you can create one or
more "Secrets" in the "Key Vault."  Open your "Key Vault" and go to
the "Secrets" section. Click "Generate/Import."  Give your secret a
name like "Test."  For the Value, you can type anything you want, but
[Azure Portal] only allows you to enter a single line. If you want
the secret to be interpreted as [JSON], set the "Content type" to
`application/json`. If you want your secret to contain a complex data
structure, you will need to use [Azure PowerShell] or [Azure CLI].
For example, you could create a file called `secrets.json` containing
a [JSON] data structure you want to use in your Configuration, and
then you could upload it to your [Azure Key Vault] by running the
following [Azure CLI] commands:

{% highlight bash %}
az keyvault secret set --vault-name=abcincsecrets --name=SomeSecrets --file=secrets.json --encoding=utf-8
az keyvault secret set-attributes --vault-name=abcincsecrets --name=SomeSecrets --content-type="application/json"
{% endhighlight %}

**docassemble** respects the following content types:

* `application/json` for [JSON]
* `application/x-yaml` for [YAML]

If the content type of the secret is set to something else, or it is
left unset, **docassemble** will process the secret as plain text.

For example, if you just want to store a single string in a secret,
you can do:

{% highlight bash %}
az keyvault secret set --vault-name=abcincsecrets --name=myapikey --value="AD42C533B22A5343F32D27E"
{% endhighlight %}

# <a name="get_config"></a>Adding your own configuration variables

Feel free to use the configuration file to pass your own variables to
your code. To retrieve their values, use the [`get_config()`] function:

{% highlight yaml %}
code: |
  trello_api_key = get_config('trello api key')
{% endhighlight %}

[`get_config()`] will return `None` if you ask it for a value that does
not exist in the configuration.

The values retrieved by [`get_config()`] are the result of importing the
[YAML] in the configuration file. As a result, the values may be
text, lists, or dictionaries, or any nested combination of these
types, depending on what is written in the configuration file.

It is a good practice to use the configuration file to store any
sensitive information, such as passwords and API keys. This allows
you to share your code on [GitHub] without worrying about redacting it
first.

# <a name="alternatelocation"></a>Using a configuration file in a different location

If you want **docassemble** to read its configuration from a location
other than `/usr/share/docassemble/config/config.yml`, you can set the
`DA_CONFIG_FILE` environment variable to another file location. You
might want to do this if you have multiple virtual hosts, each running
a different [WSGI] application on a single server.

Note that the configuration file needs to be readable and writable by
the web server, but should not be readable by other users of the
system because it may contain sensitive information, such as Google
and Facebook API keys.

[SameSite]: https://www.chromestatus.com/feature/5088147346030592
[VoiceRSS]: https://www.voicerss.org/
[Flask]: https://flask.pocoo.org/
[YAML]: https://en.wikipedia.org/wiki/YAML
[LaTeX]: https://www.latex-project.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[installation]: {{ site.baseurl }}/docs/installation.html
[upgrades]: {{ site.baseurl }}/docs/installation.html#upgrade
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[multi-server arrangement]: {{ site.baseurl }}/docs/scalability.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[interview]: {{ site.baseurl }}/docs/interviews.html
[WSGI]: https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[Flask]: https://flask.pocoo.org/
[language and locale settings]: {{ site.baseurl }}/docs/language.html
[user login system]: {{ site.baseurl }}/docs/users.html
[interview logic]: {{ site.baseurl }}/docs/logic.html
[protection]: https://flask-wtf.readthedocs.org/en/latest/csrf.html
[cross-site request forgery]: https://en.wikipedia.org/wiki/Cross-site_request_forgery
[document]: {{ site.baseurl }}/docs/documents.html
[functions]: {{ site.baseurl }}/docs/functions.html
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[ISO-639-3]: https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
[GitHub]: https://github.com/
[Perl Audio Converter]: https://vorzox.wix.com/pacpl
[pip]: https://en.wikipedia.org/wiki/Pip_%28package_manager%29
[list of language codes]: https://www.voicerss.org/api/documentation.aspx
[supervisor]: http://supervisord.org
[S3]: {{ site.baseurl }}/docs/docker.html#persistent s3
[Azure blob storage]: {{ site.baseurl }}/docs/docker.html#persistent azure
[Amazon S3]: https://aws.amazon.com/s3/
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
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`root`]: #root
[Pandoc]: https://pandoc.org
[LibreOffice]: https://www.libreoffice.org/
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[`required privileges`]: {{ site.baseurl }}/docs/initial.html#required privileges
[`required privileges for listing`]: {{ site.baseurl }}/docs/initial.html#required privileges
[`tags`]: {{ site.baseurl }}/docs/initial.html#tags
[`error help`]: {{ site.baseurl }}/docs/initial.html#error help
[`error help` directive]: #error help
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[scheduled task]: {{ site.baseurl }}/docs/background.html#scheduled
[enabled]: {{ site.baseurl }}/docs/background.html#enabling
[`as_datetime()`]: {{ site.baseurl }}/docs/functions.html#as_datetime
[`speak_text`]: {{ site.baseurl }}/docs/special.html#speak_text
[call forwarding]: {{ site.baseurl }}/docs/livehelp.html#phone
[`send_sms()`]: {{ site.baseurl }}/docs/functions.html#send_sms
[`send_fax()`]: {{ site.baseurl }}/docs/functions.html#send_fax
[text messaging interface]: {{ site.baseurl }}/docs/sms.html
[Twilio]: https://twilio.com
[Redis]: https://redis.io/
[RabbitMQ]: https://www.rabbitmq.com/
[AMQP URI]: https://www.rabbitmq.com/uri-spec.html
[redis URI]: https://www.iana.org/assignments/uri-schemes/prov/redis
[`os locale`]: #os locale
[ImageMagick]: https://www.imagemagick.org/
[Debian]: https://www.debian.org/
[`voicerss`]: #voicerss
[E.164]: https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers
[SMS]: https://en.wikipedia.org/wiki/Short_Message_Service
[SQLAlchemy]: https://www.sqlalchemy.org/
[PostgreSQL]: https://www.postgresql.org/
[Packages]: {{ site.baseurl }}/docs/packages.html
[fork]: https://en.wikipedia.org/wiki/Fork_(software_development)
[initial database setup]: {{ site.baseurl }}/docs/installation.html#setup
[Facebook]: {{ site.baseurl }}/docs/installation.html#facebook
[Google]: {{ site.baseurl }}/docs/installation.html#google
[Auth0]: {{ site.baseurl }}/docs/installation.html#auth0
[Keycloak]: {{ site.baseurl }}/docs/installation.html#keycloak
[Authentik]: {{ site.baseurl }}/docs/installation.html#authentik
[Zitadel]: {{ site.baseurl }}/docs/installation.html#zitadel
[miniOrange]: {{ site.baseurl }}/docs/installation.html#miniorange
[Azure]: {{ site.baseurl }}/docs/installation.html#azure
[invited by an administrator]: {{ site.baseurl }}/docs/users.html#invite
[`root`]: #root
[`docassemble.webapp.fix_postgresql_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/fix_postgresql_tables.py
[`docassemble.webapp.install_certs`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/install_certs.py
[`brandname`]: #brandname
[`appname`]: #appname
[PYTHONUSERBASE]: https://docs.python.org/3.12/using/cmdline.html#envvar-PYTHONUSERBASE
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[HTTPS]: {{ site.baseurl }}/docs/docker.html#https
[startup process]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[URI]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
[`azure`]: #azure
[`s3`]: #s3
[`s4cmd`]: https://github.com/bloomreach/s4cmd
[third-party logins]: #oauth
[`certs`]: #certs
[`log`]: #log
[locale]: https://docs.python.org/3/library/locale.html
[phonenumbers]: https://github.com/daviddrysdale/python-phonenumbers
[`secretkey`]: #secretkey
[`default sender`]: #default sender
[Python]: https://www.python.org/
[Celery]: https://docs.celeryq.dev/en/stable/
[`ocr_file()`]: {{ site.baseurl }}/docs/functions.html#ocr_file
[Tesseract]: https://en.wikipedia.org/wiki/Tesseract_(software)
[`default interview`]: #default interview
[readability statistics]: https://pypi.python.org/pypi/textstat/
[Playground]: {{ site.baseurl }}/docs/playground.html
[packages folder]: {{ site.baseurl }}/docs/playground.html#packages
[Vim]: https://www.vim.org/
[Emacs]: https://www.gnu.org/software/emacs/
[Sublime Text]: https://www.sublimetext.com/
[Vim bindings option]: https://codemirror.net/demo/vim.html
[Emacs bindings option]: https://codemirror.net/demo/emacs.html
[Sublime Text bindings option]: https://codemirror.net/demo/sublime.html
[CodeMirror]: https://codemirror.net/
[e-mail receiving]: {{ site.baseurl }}/docs/background.html#email
[`external hostname`]: #external hostname
[`dispatch`]: #dispatch
[list of available interviews]: #dispatch
[Google Cloud Translation API]: https://cloud.google.com/translate/
[`Address`]: {{ site.baseurl }}/docs/objects.html#Address
[`.geocode()`]: {{ site.baseurl }}/docs/objects.html#Address.geocode
[`.normalize()`]: {{ site.baseurl }}/docs/objects.html#Address.normalize
[`interview_email()`]: {{ site.baseurl }}/docs/functions.html#interview_email
[favicon]: https://en.wikipedia.org/wiki/Favicon
[ICO]: https://en.wikipedia.org/wiki/ICO_(file_format)
[optical character recognition]: https://en.wikipedia.org/wiki/Optical_character_recognition
[PyPI]: https://pypi.python.org/pypi
[load balancer]: {{ site.baseurl }}/docs/scalability.html
[forwards]: {{ site.baseurl }}/docs/docker.html#forwarding
[Google Drive synchronization]: {{ site.baseurl }}/docs/playground.html#google drive
[OneDrive synchronization]: {{ site.baseurl }}/docs/playground.html#onedrive
[GitHub integration]: {{ site.baseurl }}/docs/packages.html#github
[OAuth2]: https://oauth.net/2/
[Google Drive]: https://drive.google.com
[OneDrive]: https://onedrive.live.com/about/en-us/
[Mailgun]: https://www.mailgun.com/
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
[phone login]: #phone login
[`template`]: {{ site.baseurl }}/docs/initial.html#template
[`twilio`]: #twilio
[Google Authenticator]: https://en.wikipedia.org/wiki/Google_Authenticator
[Authy]: https://authy.com/
[privilege]: {{ site.baseurl }}/docs/users.html
[privileges]: {{ site.baseurl }}/docs/users.html
[bucket]: https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[PDF/A]: https://en.wikipedia.org/wiki/PDF/A
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[`pdf/a` features setting]: {{ site.baseurl }}/docs/initial.html#pdfa
[`tagged pdf` features setting]: {{ site.baseurl }}/docs/initial.html#tagged pdf
[Jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
[Flask]: https://flask.pocoo.org/
[`interviews.html`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/templates/pages/interviews.html
[`start.html`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/templates/pages/start.html
[HTML]: https://en.wikipedia.org/wiki/HTML
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[`javascript` features setting]: {{ site.baseurl }}/docs/initial.html#javascript
[`css` features setting]: {{ site.baseurl }}/docs/initial.html#css
[start page]: #dispatch
[GET request]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol#Request_methods
[`global css`]: #global css
[`global javascript`]: #global javascript
[alembic]: https://alembic.zzzcomputing.com/en/latest/
[CSRF protection]: https://flask-wtf.readthedocs.io/en/stable/csrf.html
[referer header]: https://en.wikipedia.org/wiki/HTTP_referer
[jQuery]: https://jquery.com/
[`$( document ).ready`]: https://api.jquery.com/ready/
[`$.get()`]: https://api.jquery.com/jquery.get/
[`.html()`]: https://api.jquery.com/html/
[`maximum image size` field modifier]: {{ site.baseurl }}/docs/fields.html#maximum image size
[`maximum image size` interview feature]: {{ site.baseurl }}/docs/initial.html#maximum image size
[`loop limit` and `recursion limit` features]: {{ site.baseurl }}/docs/initial.html#loop limit
[region name]: https://docs.aws.amazon.com/general/latest/gr/rande.html
[Bootstrap]: https://getbootstrap.com/
[Bootswatch]: https://bootswatch.com/
[live help]: {{ site.baseurl }}/docs/livehelp.html
[`bootstrap theme` feature]: {{ site.baseurl }}/docs/initial.html#bootstrap theme
[`inverse navbar` feature]: {{ site.baseurl }}/docs/initial.html#inverse navbar
[`map_of()`]: {{ site.baseurl }}/docs/functions.html#map_of
[decorations]: {{ site.baseurl }}/docs/modifiers.html#decoration
[image buttons]: {{ site.baseurl }}/docs/fields.html#image button
[PNG]: https://en.wikipedia.org/wiki/Portable_Network_Graphics
[JPEG]: https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
[BMP]: https://en.wikipedia.org/wiki/BMP_file_format
[customizing]: #start page template
[`interview_list()`]: {{ site.baseurl }}/docs/functions.html#interview_list
[`interview_menu()`]: {{ site.baseurl }}/docs/functions.html#interview_menu
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`ServerAdmin`]: https://httpd.apache.org/docs/2.4/mod/core.html#ServerAdmin
[background task]: {{ site.baseurl }}/docs/background.html#background
[background tasks]: {{ site.baseurl }}/docs/background.html#background
[`worker_concurrency`]: https://docs.celeryproject.org/en/latest/userguide/configuration.html#worker-concurrency
[`features`]: {{ site.baseurl }}/docs/initial.html#features
[fax sending]: {{ site.baseurl }}/docs/functions.html#send_fax
[API]: {{ site.baseurl }}/docs/api.html
[check in]: {{ site.baseurl }}/docs/background.html#check in
[SMTP]: https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
[JSON]: https://en.wikipedia.org/wiki/JSON
[include inline icons]: {{ site.baseurl }}/docs/markup.html#emoji
[inline icons]: {{ site.baseurl }}/docs/markup.html#emoji
[have predefined]: {{ site.baseurl }}/docs/initial.html#im
[Font Awesome]: https://fontawesome.com
[Material Icons]: https://material.io/icons/
[disable registration]: #allow registration
[LDAP]: https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol
[Active Directory]: https://en.wikipedia.org/wiki/Active_Directory
[`show interviews link`]: #show interviews link
[`BEHINDHTTPSLOADBALANCER`]: {{ site.baseurl }}/docs/docker.html#BEHINDHTTPSLOADBALANCER
[`DAHOSTNAME`]: {{ site.baseurl }}/docs/docker.html#DAHOSTNAME
[`DAWEBSERVER`]: {{ site.baseurl }}/docs/docker.html#DAWEBSERVER
[`USENGINXTOSERVEFILES`]: {{ site.baseurl }}/docs/docker.html#USENGINXTOSERVEFILES
[Let's Encrypt]: https://letsencrypt.org/
[Configuration]: {{ site.baseurl }}/docs/config.html
[`USEHTTPS`]: {{ site.baseurl }}/docs/docker.html#USEHTTPS
[`USELETSENCRYPT`]: {{ site.baseurl }}/docs/docker.html#USELETSENCRYPT
[`LETSENCRYPTEMAIL`]: {{ site.baseurl }}/docs/docker.html#LETSENCRYPTEMAIL
[`XSENDFILE`]: {{ site.baseurl }}/docs/docker.html#XSENDFILE
[service account]: https://cloud.google.com/iam/docs/understanding-service-accounts
[Google Developers Console]: https://console.developers.google.com/
[`google`]: #google
[Google Docs]: https://docs.google.com
[Google Analytics]: https://analytics.google.com
[pageview]: https://developers.google.com/analytics/devguides/collection/analyticsjs/pages#tracking_virtual_pageviews
[`path_and_mimetype()`]: {{ site.baseurl }}/docs/functions.html#path_and_mimetype
[user agent]: https://en.wikipedia.org/wiki/User_agent
[address autocomplete]: {{ site.baseurl }}/docs/fields.html#address autocomplete
[`debug`]: #debug
[Logs]: {{ site.baseurl }}/docs/admin.html#logs
[`url root`]: #url root
[`debug` feature]: {{ site.baseurl }}/docs/initial.html#debug
[`exit link`]: {{ site.baseurl }}/docs/initial.html#exit link
[`exit label`]: {{ site.baseurl }}/docs/initial.html#exit label
[Microsoft Word sidebar]: {{ site.baseurl }}/docs/playground.html#word addin
[Utilities]: {{ site.baseurl }}/docs/admin.html#utilities
[XML manifest file]: {{ site.baseurl }}/docs/admin.html#word addin manifest
[`show login` metadata directive]: {{ site.baseurl }}/docs/initial.html#show login
[translates system phrases]: {{ site.baseurl }}/docs/admin.html#translate
[`url_of()`]: {{ site.baseurl }}/docs/functions.html#url_of
[screen parts]: {{ site.baseurl }}/docs/questions.html#screen parts
[screen part]: {{ site.baseurl }}/docs/questions.html#screen parts
[ConvertAPI]: https://www.convertapi.com
[CloudConvert]: https://cloudconvert.com
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[Microsoft Word]: https://en.wikipedia.org/wiki/Microsoft_Word
[WhatsApp]: https://www.twilio.com/whatsapp
[`allow non-idempotent questions`]: {{ site.baseurl }}/docs/initial.html#allow non-idempotent questions
[ISO 3166-1 alpha-2]: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[MIME]: https://en.wikipedia.org/wiki/Media_type
[Segment]: https://segment.com/
[`id`]: {{ site.baseurl }}/docs/modifiers.html#id
[`ga id`]: {{ site.baseurl }}/docs/modifiers.html#ga id
[`segment id`]: {{ site.baseurl }}/docs/modifiers.html#segment id
[`segment`]: {{ site.baseurl }}/docs/modifiers.html#segment
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[ECS]: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
[list of files on GitHub]: https://github.com/jhpyle/docassemble/tree/master/docassemble_base/docassemble/base/data/sources
[examples area]: {{ site.baseurl }}/docs/playground.html#examples
[`docassemble.base:data/questions/example-list.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/example-list.yml
[`code`]: {{ site.baseurl }}/docs/code.html#code
[behind a reverse proxy]: {{ site.baseurl }}/docs/docker.html#forwarding
[data storage]: {{ site.baseurl }}/docs/docker.html#data storage
[Package Management]: {{ site.baseurl }}/docs/admin.html#package management
[`docker start`]: https://docs.docker.com/engine/reference/commandline/start/
[`docker run`]: https://docs.docker.com/engine/reference/commandline/run/
[`docker start`]: https://docs.docker.com/engine/reference/commandline/start/
[`docker stop -t 600`]: https://docs.docker.com/engine/reference/commandline/stop/
[`docker rm`]: https://docs.docker.com/engine/reference/commandline/rm/
[WebSocket]: https://en.wikipedia.org/wiki/WebSocket
[date functions]: {{ site.baseurl }}/docs/functions.html#date functions
[`babel.dates`]: https://babel.pocoo.org/en/latest/api/dates.html
[edit user accounts]: {{ site.baseurl }}/docs/admin.html#edit user profile
[user profile]: {{ site.baseurl }}/docs/admin.html#profile
[multi-user interview]: {{ site.baseurl }}/docs/special.html#multi_user
[multi-user interviews]: {{ site.baseurl }}/docs/special.html#multi_user
[`show dispatch link`]: #show dispatch link
[`short title`]: {{ site.baseurl }}/docs/initial.html#short title
[`title`]: {{ site.baseurl }}/docs/initial.html#title
[`sessions are unique`]: {{ site.baseurl }}/docs/initial.html#sessions are unique
[`hidden`]: {{ site.baseurl }}/docs/initial.html#hidden
[`action_button_html()`]: {{ site.baseurl }}/docs/functions.html#action_button_html
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`menu_items`]: {{ site.baseurl }}/docs/special.html#menu_items
[`S3BUCKET`]: {{ site.baseurl }}/docs/docker.html#S3BUCKET
[`S3REGION`]: {{ site.baseurl }}/docs/docker.html#S3BUCKET
[NGINX]: https://www.nginx.com/
[uWSGI]: https://uwsgi-docs.readthedocs.io/en/latest/
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`set_locale()`]: {{ site.baseurl }}/docs/functions.html#set_locale
[`update_locale()`]: {{ site.baseurl }}/docs/functions.html#update_locale
[thread-safe]: https://en.wikipedia.org/wiki/Thread_safety
[`currency symbol` field modifier]: {{ site.baseurl }}/docs/fields.html#currency
[`currency()`]: {{ site.baseurl }}/docs/functions.html#currency
[customizing based on language and locale]: {{ site.baseurl }}/docs/language.html#customizing
[MinIO]: https://min.io/
[`USEMINIO`]: {{ site.baseurl }}/docs/docker.html#USEMINIO
[Kubernetes]: https://kubernetes.io/
[front end]: {{ site.baseurl }}/docs/frontend.html
[`allowed to set`]: {{ site.baseurl }}/docs/modifiers.html#allowed to set
[SendGrid API]: https://sendgrid.com/solutions/email-api/
[SendGrid]: https://sendgrid.com/
[social meta tags]: #social
[`brandname`]: #brandname
[`locale`]: #locale
[meta tags]: https://en.wikipedia.org/wiki/Meta_element
[`ssl_protocols`]: https://nginx.org/en/docs/http/configuring_https_servers.html
[`ssl_ciphers`]: https://nginx.org/en/docs/http/configuring_https_servers.html
[`DASSLPROTOCOLS`]: {{ site.baseurl }}/docs/docker.html#DASSLPROTOCOLS
[`DASSLCIPHERS`]: {{ site.baseurl }}/docs/docker.html#DASSLCIPHERS
[Docker section]: {{ site.baseurl }}/docs/docker.html#persistent s3
[`store_variables_snapshot()`]: {{ site.baseurl }}/docs/functions.html#store_variables_snapshot
[`db`]: #db
[JSONB]: https://www.postgresql.org/docs/current/functions-json.html
[user list]: {{ site.baseurl }}/docs/admin.html#user list
[My Interviews]: {{ site.baseurl }}/docs/admin.html#my interviews
[`table css class`]: {{ site.baseurl }}/docs/questions.html#table css class
[`default screen parts`]: {{ site.baseurl }}/docs/initial.html#default screen parts
[XLSX]: https://en.wikipedia.org/wiki/Office_Open_XML
[XLIFF]: https://en.wikipedia.org/wiki/XLIFF
[libpq]: https://www.postgresql.org/docs/current/libpq-ssl.html
[ARN]: https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
[Amazon Resource Name]: https://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html
[AWS Secret]: https://aws.amazon.com/secrets-manager/
[AWS Secrets Manager]: https://aws.amazon.com/secrets-manager/
[AWS]: https://aws.amazon.com
[IAM]: https://aws.amazon.com/iam/
[Key Vault Reference]: https://docs.microsoft.com/en-us/azure/app-service/app-service-key-vault-references
[Azure Key Vault]: https://azure.microsoft.com/en-us/services/key-vault/
[Key Vault]: https://azure.microsoft.com/en-us/services/key-vault/
[Azure Portal]: https://portal.azure.com
[Identity]: https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview
[Azure Virtual Machine]: https://azure.microsoft.com/en-us/services/virtual-machines/
[Registering]: https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app
[Azure PowerShell]: https://docs.microsoft.com/en-us/powershell/azure/
[Azure CLI]: https://docs.microsoft.com/en-us/cli/azure/
[Microsoft Azure]: https://azure.microsoft.com
[Azure Maps API]: https://docs.microsoft.com/en-us/azure/azure-maps/
[GeoPy]: https://geopy.readthedocs.io/en/latest/#geocoders
[Slack]: {{ site.slackurl }}
[`geocoder service`]: #geocoder service
[primary key]: https://docs.microsoft.com/en-us/azure/azure-maps/how-to-manage-authentication#view-authentication-details
[Bootstrap colors]: https://getbootstrap.com/docs/5.2/components/buttons/#examples
[`button colors`]: #button colors
[Bootstrap theme]: #bootstrap theme
[`allow embedding`]: #allow embedding
[ClickSend]: https://www.clicksend.com/us/
[`cross site domains`]: #cross site domains
[YAML preprocessor]: {{ site.baseurl }}/docs/interviews.html#jinja2
[unoconv]: https://github.com/unoconv/unoconv
[system upgrade]: {{ site.baseurl }}/docs/docker.html#upgrading
[`/api/login_url`]: {{ site.baseurl }}/docs/api.html#login_url
[managing certificates with Docker]: {{ site.baseurl }}/docs/docker.html#own certificates
[Telnyx]: https://telnyx.com/
[parameters for connecting to Redis with Python]: https://redis-py.readthedocs.io/en/stable/connections.html
[Ubuntu]: https://ubuntu.com/
[Debian]: https://www.debian.org
[`enable playground`]: #enable playground
[`allow changing password`]: #allow changing password
[Browse Other Playgrounds]: {{ site.baseurl }}/docs/playground.html#other users
[`words`]: #words
[language support]: https://docassemble.org/docs/language.html
[`language`]: {{ site.baseurl }}/docs/config.html#language
[`background_response_action()`]: {{ site.baseurl }}/docs/background.html#background_response_action
[`set_user_info()`]: {{ site.baseurl }}/docs/functions.html#set_user_info
[`SQLObject`]: {{ site.baseurl }}/docs/objects.html#SQLObject
[`CustomDataType`]: {{ site.baseurl }}/docs/fields.html#custom datatype
[`docassemble.base.util.update_word_collection()`]: {{ site.baseurl }}/docs/functions.html#update_word_collection
[`docassemble.base.util.update_locale()`]: {{ site.baseurl }}/docs/functions.html#update_locale
[`docassemble.base.util.update_language_function()`]: {{ site.baseurl }}/docs/functions.html#update_language_function
[`docassemble.base.util.update_nice_numbers()`]: {{ site.baseurl }}/docs/functions.html#update_nice_numbers
[`docassemble.base.util.update_ordinal_numbers()`]: {{ site.baseurl }}/docs/functions.html#update_ordinal_numbers
[`docassemble.base.util.update_ordinal_function()`]: {{ site.baseurl }}/docs/functions.html#update_ordinal_function
[`imports`]: {{ site.baseurl }}/docs/initial.html#imports
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[Bootstrap grid system]: https://getbootstrap.com/docs/5.2/layout/grid/
[Bootstrap alert]: https://getbootstrap.com/docs/5.2/components/alerts/
[Bootstrap color]: https://getbootstrap.com/docs/5.2/customize/color/
[Lightsail]: https://aws.amazon.com/lightsail/
[tz database]: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
[locale values]: {{ site.baseurl }}/img/locales.txt
[custom endpoints]: {{ site.baseurl }}/docs/recipes.html#custom api
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[`email config`]: {{ site.baseurl }}/docs/initial.html#email config
[Google Analytics 4]: https://developers.google.com/analytics/devguides/collection/ga4
[Google Sheets API]: https://developers.google.com/sheets/api/guides/concepts
[Google Drive API]: https://developers.google.com/drive/api/guides/about-sdk
[`enable unoconv`]: #enable unoconv
[`ENABLEUNOCONV`]: {{ site.baseurl }}/docs/docker.html#ENABLEUNOCONV
[Gotenberg]: https://gotenberg.dev/
[`GOTENBERGURL`]: {{ site.baseurl }}/docs/docker.html#GOTENBERGURL
[`grid` field modifier]: {{ site.baseurl }}/docs/fields.html#grid
[`item grid` field modifier]: {{ site.baseurl }}/docs/fields.html#item grid
[`password login`]: #password login
[pdftk]: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/
[`rendering font`]: {{ site.baseurl }}/docs/documents.html#rendering font
[Troubleshooting]: {{ site.baseurl }}/docs/docker.html#troubleshooting
[`DBHOST`]: {{ site.baseurl }}/docs/docker.html#DBHOST
[`DBNAME`]: {{ site.baseurl }}/docs/docker.html#DBNAME
[`DBUSER`]: {{ site.baseurl }}/docs/docker.html#DBUSER
[`DBPASSWORD`]: {{ site.baseurl }}/docs/docker.html#DBPASSWORD
[`REDIS`]: {{ site.baseurl }}/docs/docker.html#REDIS
[RDS]: https://aws.amazon.com/rds/
[ElastiCache for Redis]: https://aws.amazon.com/elasticache/redis/
[`docker start`]: https://docs.docker.com/engine/reference/commandline/start/
[`docker stop`]: https://docs.docker.com/engine/reference/commandline/stop/
[Profile]: {{ site.baseurl }}/docs/users.html#profile
[Microsoft Graph API]: https://learn.microsoft.com/en-us/graph/api/user-sendmail
[Place Autocomplete]: https://developers.google.com/maps/documentation/places/web-service/place-autocomplete
[Google Places API]: https://developers.google.com/maps/documentation/places/web-service/op-overview
