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
default interview: docassemble.demo:data/questions/default-interview.yml
language: en
locale: en_US.utf8
default admin account:
  nickname: admin
  email: admin@admin.com
  password: password
voicerss:
  enable: False
  key: ae8734983948ebc98239e9898f998432
  dialects:
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
* Viewing [Markdown] source in document attachments.

This can be overridden using the [`debug` feature].

## <a name="allow demo"></a>Allowing sample interviews in production mode

By default, when `debug` is `False`, users without the privileges of
`admin` or `developer` cannot run the sample interviews in the
`docassemble.base` and `docassemble.demo` packages.  If you would like
to allow users to run these interviews, you can set `allow demo` to `True`.

{% highlight yaml %}
allow demo: True
{% endhighlight %}

## <a name="enable playground"></a>Enabling the Playground

By default, the [Playground] is available, even when [`debug`] is
false.  You can disable the [Playground] by setting:

{% highlight yaml %}
enable playground: False
{% endhighlight %}

When `enable playground` is false, administrators and developers will
not be able to access the [Playground] or its associated features, and
users will not be able to use [Playground] interviews.

## <a name="package protection"></a>Allowing developers to install the same package

By default, users with `developer` [privileges] have ownership over
the packages they directly install, and other developers cannot create
packages by the same name.  If you want to allow developers to work on
the same packages, set the `package protection` directive to `False`.

{% highlight yaml %}
package protection: False
{% endhighlight %}

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

You should also set `url root` if you are using [Auth0] logins.

However, there are some circumstances when **docassemble** code runs
outside the context of an HTTP request.  For example, if you have a
[scheduled task] that uses [`send_sms()`] to send a text message with
a media attachment, the URL for the media attachment will be unknown
unless it is set in the configuration.

## <a name="root redirect url"></a>Redirecting the root of the server

By default, if the user accesses the root URL of the server (which is
`/` unless configured differently using [`url root`]), the user is
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
same domain as your **docassemble** server.  To do this, you will need
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
the site.  They will see a page like this:

![Interview list]({{ site.baseurl }}/img/interviewlist.png){: .maybe-full-width }

If you want to take advantage of the `/start/` shortcuts but you do
not want the interview listed in the interview list, set `unlisted:
True` in the [`metadata`] of the interview.

The `/list` URL accepts a URL parameter `tag`.  If `tag=estates`, then
`/list` will only list interviews where `estates` is one of the
[`tags`] in the interview [`metadata`].

You can also control whether an interview appears in the `/list` by
adding the [`required privileges`] specifier to the interview
[`metadata`].

If you would like to embed the list of interviews into another web
site, you can send a [GET request] to `/list?embedded=1` to obtain a
snippet of [HTML].  For example, the [HTML] snippet might look like
this:

{% highlight html %}
<ul class="dastart">
  <li><a href="/interview?i=docassemble.demo%3Adata%2Fquestions%2Fquestions.yml">Demonstration interview</a></li>
  <li><a href="/interview?i=docassemble.base%3Adata%2Fquestions%2Fexamples%2Fmadlibs.yml">Mad libs</a></li>
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
* The part that retrieves the interview list is the [JavaScript] call
  to [`$.get()`], which is between `<script type="text/javascript">` and
  `</script>`.  The part that plugs the [HTML] into the screen is the
  call to [`.html()`].
* [jQuery] needs to be loaded before the call to `$.get()`.  [jQuery]
  is very common on web sites, so it may already be loaded on your
  site.
* The [JavaScript] code is wrapped in a call to
  [`$( document ).ready`].  This may not be necessary on your site,
  but it can help avoid the potential problem where call to
  [`.html()`] takes place before the `<div id="interviews"></div>`
  [HTML] even exists on the screen.

You can also call `/list?json=1` to obtain a [JSON] version of the
available interviews.

By default, the main menu does not contain a link to the `/list` page,
but you can add it to the main menu using the [`show dispatch link`]
directive.

## <a name="customization"></a>Customization of administrative pages

When the user is interacting with an interview, the page can be
customized with a [`features`] block.  If you want to customize the
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
* `main page`: the pages of interviews.  (This one is special; see below.)

The aspects of the page that can be manipulated are:

* `tab title`: the [HTML] title, which is displayed in the web browser
  tab.
* `title`: the title of the page in the navigation bar.
* `heading`: the large font heading that displays the title of the
  page in the main body of the page.
* `pre`: text that appears after the heading but before the rest of
  the content of a page.  This is empty by default.
* `submit`: text that appears before the submit buttons on a page that
  has one or more submit buttons.  This is empty by default.
* `post`: text that appears after the content of a page.  This is
  empty by default.
* `extra css`: raw [HTML] tags that you can insert into the `<head>` of the
  page, usually to incorporate [CSS] files.  This is empty by default.
* `extra javascript`: raw [HTML] tags that you can insert at the end
  of the `<body>` of the page, usually to include [Javascript] in
  `<script>` tags.  This is empty by default.

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

<a name="main page pre"></a><a name="main page submit"></a><a
name="main page post"></a>The `main page` directive is special because
it relates to actual interviews, which are different from
administrative pages.  The directives that work with the `main
page` prefix are:

* `main page back button label`
* `main page continue button label`
* `main page exit label`
* `main page exit link`
* `main page help label`
* `main page logo`
* `main page post`
* `main page pre`
* `main page resume button label`
* `main page right`
* `main page short title`
* `main page submit`
* `main page subtitle`
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
of the screens during interviews, see the [screen parts] section.

<a name="start page template"></a><a name="interview page template"></a>
There are two pages that you can customize even more extensively:

* The [start page] that shows a list of available interviews.
* The list of saved interview sessions.

For these pages, you can specify an [HTML] template to use.  Use the
`start page template` and `interview page template` directives to
point to files in the "templates" directory of a package.

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
On the interviews page, there is a bit of [JavaScript] that 
asks the user "are you sure?" before deleting all of the interview.
The start page does not use [JavaScript].

You can also customize these pages using [CSS].  The
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

## <a name="allow anonymous access">Requiring login for all interviews</a>

If you want to require users to be logged in before they can run any
interviews, set `allow anonymous access` to `False`.

{% highlight yaml %}
allow anonymous access: False
{% endhighlight %}

The default is `True`.  You can also forbid anonymous access on an
interview-by-interview basis using [`required privileges`].

## <a name="administrative interviews">Administrative interviews</a>

The `administrative interviews` directive adds hyperlinks to
interviews to the main menu.

Suppose you have two interviews, `inspect.yml` and `manage.yml`, that
you use frequently.  You can list them in the [Configuration] as
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
the interview.  The label will be the [`short title`] as specified in
the [`metadata`], or if that is not defined the label will be the
[`title`].

These interview links will always be shown in the main menu; however,
a link to an interview will not be shown if the user is currently in a
session of that interview.

If you want the links in the menu to appear only for users in a given
role, you can set the [`required privileges for listing`] specifier in
the [`metadata`] to a list of [privileges].  In that case, only users
who have one of the listed privileges will see the link in the menu.
If a [`required privileges for listing`] specifier does not exist, the
[`required privileges`] specifier will be used to determine if the
link in the menu is shown.

The names and privileges that will be used for purposes of the main
menu can be overridden by specifying an item in the `administrative
interviews` list in the form of a [YAML] dictionary instead of the
name of the interview file.  For example:

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
required.  The `title` key can be set to a single name, or to a [YAML]
dictionary where the keys are languages and the values are the titles
to be used for that language.

The hyperlinks from the menu contain the `&new_session=1`, which means
that a new session will be started every time the user clicks the
interview.  In many situations, you will not want the clicking of the
link from the menu to result in a proliferation of interview
sessions.  You may want to set up the `metadata` of your
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
be one session per user.  This means that if the user already has a
session in the interview, the `&new_session=1` directive will not
result in a new session being started; instead, the original session
will be resumed.

The [`hidden`] specifier means that sessions in this interview will be
hidden on the "My Interviews" page.

It is a good practice to make your "administrative" interviews simple
so that they feel more like control panels than interviews.  For
example, you might want to have a single screen with buttons created
using [`action_button_html()`].  Or if you need multiple screens, you
can have a variable to keep track of the current screen, and then use
[`menu_items`] and [`url_action()`] to provide the user with a menu
for navigating from screen to screen.

## <a name="resume interview after login"></a>Always go back to the current interview after logging in

If a user starts an interview as an anonymous user and then registers
or logs in, they generally be taken to the "My Interviews" page.
However, if the interview session they started is their only interview
session, then the "My Interviews" page is skipped and the user is sent
right back into the interview they had started.

The "My Interviews" page is shown to users with more than one session
because it resolves confusion for users who may have visited the
interview for purposes of resuming an existing interview session, but
finding themselves not logged in, they log in.  Some users may expect
to resume the session they just started; other users may expect to
resume their original session.  By sending users to the My Interviews
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
not be sent to the "My Interviews" page, but will be redirected back
into the interview they just started.

## <a name="auto resume interview"></a>Automatically resuming or starting an interview

The "My Interviews" page at `/interviews` normally displays a list of
the user's interview sessions.  By default, users are directed to
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
`docassemble.eviction:data/questions/defend.yml` interview.  Or, if
they have no such session, a new session will 

If you set an `auto resume interview`, you may wish to set [`show
interviews link`] to `False` if the "My Interviews" menu is not useful
on your server.

## <a name="page after login"></a>Customizing the page that appears after login

By default, the user is directed to the "My Interviews" page after
logging in.  This can be customized with the `page after login`
directive:

{% highlight yaml %}
page after login: profile
{% endhighlight %}

In this example, the user will be directed to the "Profile" page after
logging in.  See the documentation for the [`url_of()`] function to
see what names to use for each page of the web site.  (The name you
give is effectively passed to [`url_of()`].)  Instead of passing the
name of a page of a web site, you can also pass a URL beginning with
`http://` or `https://`, or a path beginning with `/`, such as
`/start/taxes`, in which case the user will be taken to that page on
the server.

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
will be directed to `config`.  Each item in `page after login` is
processed in order, and the first match is used.  If no items match,
the user is directed to "My Interviews."

## <a name="global css"></a><a name="global javascript"></a><a name="raw global css"></a><a name="raw global javascript"></a>CSS and Javascript customization

You can use the [`javascript` features setting] and the
[`css` features setting] to modify the [JavaScript] and [CSS] for a
particular interview.

By using `global javascript` and `global css`, you can apply
[JavaScript] and [CSS] on a more global level.  These directives allow
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

Note that the [`global css`] and [`global javascript`] directives can
only refer to file names; if you want to write raw `<link>`, `<meta>`,
or `<script>` content, you can use the `raw global css` and `raw
global javascript` directives:

{% highlight yaml %}
raw global css: |
  <meta property="og:title" content="Child Custody Interview" />
raw global javascript: |
  <script>
    (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
    (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
    m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
    })(window,document,'script','https://www.google-analytics.com/analytics.js','ga');
    ga('create', 'UA-77777777-1', 'auto');
  </script>
{% endhighlight %}

## <a name="bootstrap theme"></a>Bootstrap theme

Using the `bootstrap theme` directive, you can change the look and
feel of your site's web interface by substituting a non-standard [CSS]
file in place of the standard [CSS] file used by [Bootstrap].

{% highlight yaml %}
bootstrap theme: docassemble.demo:data/static/lumen.min.css
{% endhighlight %}

You can also refer to files on the internet:

{% highlight yaml %}
bootstrap theme: https://bootswatch.com/4/minty/bootstrap.min.css
{% endhighlight %}

There are many alternative [Bootstrap] themes available on
[Bootswatch].  (Use [Bootstrap] 4 themes, not [Bootstrap] 3 themes.)
Note that you may need to use apply additional [CSS] changes in order
to get a [Bootstrap] theme to work with **docassemble**.  For example,
by default **docassemble** assumes that the navigation bar is 56
pixels in height.  But if your theme makes the navigation bar 66
pixels tall, you will need to add the following styles:

{% highlight css %}
.pad-for-navbar         { padding-top: 76px; }
.top-for-navbar         { top: 76px;         }
{% endhighlight %}

Also, some of the colors that **docassemble** uses in the navigation
bar might not work well with every theme.  You can override these
colors with [CSS] like the following:

{% highlight css %}
span.daactivetext       { color: yellow;         }
span.daactivetext:hover { color: #ffff99;        }
i.chat-active           { color: #45bf41;        }
i.chat-active:hover     { color: #55cf51;        }
i.chat-inactive         { color: #4f4f4f;        }
i.chat-inactive:hover   { color: #5f5f5f;        }
{% endhighlight %}

These styles refer to the yellow "Help" button that appears when
question-specific help is available, the green icons that appear in
the navigation bar when [live help] features are available, and the
grey color that these icons become when [live help] is no longer
available.

You can also control the [Bootstrap] theme on a per-interview basis
with the [`bootstrap theme` feature].  You can also alter [CSS] on a
per-interview basis using the [`css` features setting].

## <a name="inverse navbar"></a>Inverted Bootstrap navbar

By default, **docassemble** uses [Bootstrap]'s "dark" (formerly known
as "inverted") style of navigation bar so that the navigation bar
stands out from the white background.  If you do not want to use the
inverted navbar, set the `inverse navbar` to `False`.

{% highlight yaml %}
inverse navbar: False
{% endhighlight %}

You can also control this on a per-interview basis with the
[`inverse navbar` feature].

## <a name="button size"></a>Button size

By default, most buttons in the **docassemble** user interface are
regular size [Bootstrap] buttons.  If you want the buttons to be
"large" size, set the following in your configuration:

{% highlight yaml %}
button size: large
{% endhighlight %}

If you want the buttons to be "small" size, set the following in your configuration:

{% highlight yaml %}
button size: small
{% endhighlight %}

The default value is `medium`.

## <a name="default icons"></a>Using standard sets of icons

[Font Awesome] is enabled on all pages. **docassemble** includes the
free version (5.2.0) of [Font Awesome].  This allows you to refer to
[Font Awesome] icons using raw HTML.

In addition, **docassemble** allows you to use Google's [Material
Icons] in your raw HTML.  Since the [Material Icons] are just a font,
they are enabled by default and there is no configuration directive to
enable the use of [Material Icons].

You can also use [Font Awesome] or [Material Icons] for [decorations]
and [inline icons], without writing any raw [HTML].

By default, when you include [decorations], or you [include inline
icons], you can only refer to image files that you [have predefined].  An
inline image reference that does not have a corresponding predefined
image will appear literally (e.g., `:cow:`).  However, if you set the
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
instead of `:circle:`.  This will result in `<i class="far
fa-circle"></i>` instead of `<i class="fas fa-circle"></i>`.

To use a different [Font Awesome] style by default, set the `font
awesome prefix` directive.  For example, to use the "brand" style by
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
favicon mask color: "#698aa7"
favicon theme color: "#83b3dd"
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

If you are using [Docker] with [S3] or [Azure blob storage], and you
omit the `host` or set it to `null`, then **docassemble** will
automatically find the hostname of the central SQL server in cloud
storage.

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

By default, the [NGINX] HTTPS configuration contains:

{% highlight text %}
ssl_certificate /etc/ssl/docassemble/nginx.crt;
ssl_certificate_key /etc/ssl/docassemble/nginx.key;
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

Here is an example.  Install [`s4cmd`] if you have not done so already:

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
passwords, or to let users of a [multi-user interview] know that it is
their turn to start answering questions.

By default, **docassemble** assumes that an [SMTP] server is installed
on the same machine as the web server and that it uses port 25.

<a name="default sender"></a>If you are going to send mail, you should
at least set the `default sender` directive, which sets the return
address on any e-mails generated from **docassemble**:

{% highlight yaml %}
mail:
  default sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

The default set-up of a local [SMTP] server will probably not be
appropriate for your situation, as most internet service providers
block outgoing e-mail.

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

### <a name="mailgun api"></a>Using the Mailgun API

Another way to send e-mail using [Mailgun] is through its API.  If you
use the API, mail is sent to [Mailgun] using [HTTP], rather than
[SMTP].  This may be more reliable than [SMTP], since internet service
providers may slow down or block [SMTP] traffic as a way of protecting
against spam.

To use this method, obtain an API key from [Mailgun] and set it as the
`mailgun api key`.  Also set your [Mailgun] domain as the `mailgun
domain`.

{% highlight yaml %}
mail:
  default sender: '"Example, Inc." <no-reply@mg.example.com>'
  mailgun api key: key-b21b28f6e29be1f463478238d172813e
  mailgun domain: mg.example.com
{% endhighlight %}

If necessary, you can also configure the URL used by the [Mailgun]
API.  The default is `https://api.mailgun.net/v3/%s/messages.mime`.

{% highlight yaml %}
mailgun api url: https://api.mailgun.net/v3/%s/messages.mime
{% endhighlight %}

(The `mailgun domain` will be substituted in place of the `%s`.)

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

The `language` needs to be a lowercase [ISO-639-1] or [ISO-639-3]
code.  This will serve as the default language for the server.  You
can override this in a session by calling the [`set_language()`]
function in an [`initial`] block.

The `locale` needs to be a locale name that will be accepted by
the [locale] library.  The locale is primarily used for determining
the formatting of numbers and currency values.  For example, some
locales use `.` to indicate decimals and some use `,`.

The locale can be changed later in Python code by calling
[`set_locale()`] followed by [`update_locale()`].  However, changing
the locale is is not [thread-safe]; this means that if two users are
using your system simultaneously, and one is in Japan and expects
currency to be in Yen, and the other is in France and expects currency
to be in Euros, the code that runs [`update_locale()`] for the French
user could cause the Japanese user to see the Euro symbol in place of
the Yen symbol in a [`question`].

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
[phonenumbers] library ([ISO 3166-1 alpha-2] format).

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
addresses).  If possible, the e-mail will contain the error message.

{% highlight yaml %}
error notification email:
  - jsmith@example.com
  - tjoseph@example.com
{% endhighlight %}

Information about errors is also available in the [Logs].

## <a name="verbose error messages"></a>Whether error messages contain details

By default, when the user sees an error on the screen, information
about the error is shown.  To turn this off, set `verbose error
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
screen, which can be confusing.  You can add some additional content
to this screen so that the user sees something other than the error
message:

{% highlight yaml %}
error help: |
  We are sorry, our computer has malfunctioned.  Please call
  202-555-1515 for assistance, or visit our [web site](https://example.com).
{% endhighlight %}

The format of the `error help` is [Markdown].

You can also set this on a per-interview basis using [`error help`]
inside the [`metadata`].

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

## <a name="allow non-idempotent questions"></a> Non-idempotent question check

You can set `allow non-idempotent questions: False` in order to
enforce strict idempotency of [`question`]s with generic objects,
iterators, or multiple choice selections.  If an interview has
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

> Input not processed because the question changed.  Please continue.

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
interview normally.  The input they submitted before seeing the
message is discarded, but the problem should not be a permanent
problem.  However, if the user continues to see the message, and it
prevents the user from proceeding, there is a flaw in the interview
logic that needs to be fixed; an immediate solution would be to set
`allow non-idempotent questions` to `True`, but the long-term solution
is to fix the logic in the interview.

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
setup (i.e., it is connecting to a populated SQL database).  If you
have an existing system, the way to control package installation is
through the [Package Management] interface or the
[API](https://docassemble.org/docs/api.html#package_install).

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

## <a name="admin can delete account"></a>Whether the administrator can delete user accounts

By default, administrators can [edit user accounts] and mark them
inactive.  If an account is inactive, the user cannot log in and the
user cannot register using the same e-mail address.  Marking an
account as inactive does not delete the user's data.

When administrators [edit user accounts], they can also delete the
user's account.  Since the deletion of the information is permanent,
you might want to turn off this feature for safety reasons.  To do so,
set `admin can delete account` to `False`:

{% highlight yaml %}
admin can delete account: False
{% endhighlight %}

## <a name="user can delete account"></a>Whether users can delete their accounts

By default, users have the power to delete their own accounts and all
of their data.  To disable this, you can set `user can delete account`
to `False`:

{% highlight yaml %}
user can delete account: False
{% endhighlight %}

<a name="delete account deletes shared"></a>If users have joined
[multi-user interviews] with other people, it is ambiguous who "owns"
the data in the interview.  By default, shared interviews are not
deleted from the server when users delete their data.  However, if you
want to give users the power to delete any session of a [multi-user
interview], even if other people used it, you can set `delete account
deletes shared` to `True`.

{% highlight yaml %}
delete account deletes shared: True
{% endhighlight %}

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

## <a name="backup days"></a>Number of days of backups to keep

The [Docker] setup creates 14 days of daily backups.  The number of
days can be changed using the `backup days` directive.

{% highlight yaml %}
backup days: 7
{% endhighlight %}

If you set `backup days` to `0`, the daily backup process will be
disabled.

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

## <a name="maximum content length"></a>Limiting size of HTTP requests

By default, as a security precaution, the web application rejects any
HTTP request larger than 16 megabytes.  This limit can be extended by
setting `maximum content length` to a different number of bytes.

{% highlight yaml %}
maximum content length: 26214400
{% endhighlight %}

This sets the limit to 25 megabytes.

To have no limit, set `maximum content length` to `None`.

If you are using [Docker] and [NGINX], then after changing this value,
you will need to do a complete restart of the system for the change to
take effect.  (That is, `docker stop -t 600 <container ID>` followed
by `docker start <container ID>`.)

## <a name="png resolution"></a><a name="png screen resolution"></a>Image conversion resolution

When users supply PDF files and **docassemble** includes those files
within a [document], the PDF pages are converted to PNG images in
order to be included within RTF files.  The `png resolution` directive
defines the dots per inch to be used during this conversion.

PDF files are also converted to PNG for previewing within the web app,
but at a lower resolution.  The `png screen resolution` directive
defines the dots per inch to be used for conversion of PDF pages to
PNG files for display in the web browser.

## <a name="ocr dpi"></a>OCR resolution

If you use the [`ocr_file()`] function, the pages of the PDF file will
be converted to images before being read by the OCR engine.  By
default, the resolution used is 300 dpi.  To change this to something
else, set the `ocr dpi` directive:

{% highlight yaml %}
ocr dpi: 500
{% endhighlight %}

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
character.  You can alter these requirements using the `password
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
describes what the password complexity requirements are.  You can
manually override this error message by setting the `error message`
directive within the `password complexity` directive to what you want
the error message to be.

## <a name="show login"></a>Hiding the login link

If the `show login` directive is set to `False`, users will not see a
"Sign in or sign up to save answers" link in the upper-right-hand
corner of the web app.

{% highlight yaml %}
show login: False
{% endhighlight %}

The default behavior is to show the "Sign in or sign up to save
answers" link.  If `show login` is `False`, users will see an "Exit"
option.  The appearance and behavior of the "Exit" option is
configurable in the interview [`metadata`] using the directives [`exit
link`] and [`exit label`].  There is also a [`show login` metadata
directive] that contols this feature on a per-interview basis.

## <a name="show profile link"></a>Hiding the profile link

If the `show profile link` directive is set to `False`, logged-in
users will not see a "Profile" link in the web app menu.  Instead,
they will see a "Change Password" link.

{% highlight yaml %}
show profile link: False
{% endhighlight %}

Note that users with `admin` privileges will always see the "Profile"
link.

## <a name="show interviews link"></a>Hiding the "my interviews" link

If the `show interviews link` directive is set to `False`, logged-in
users will not see a "My Interviews" link in the web app menu.

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
server.  If authentication succeeds, **docassemble** will check to see
if a user with that e-mail address already exists in the
**docassemble** login system.  If so, the user will be logged in as
that user.  If the user does not already exist, then a user with that
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
generated if the e-mail address exists on the [LDAP] server.  The
`bind email` and `bind password` are necessary so that **docassemble**
can connect to the [LDAP] server and run a search for the e-mail
address in question.  When it does so, it searches within the `base
dn` for an entry with the attribute `mail`.  If one or more entries
are found, the error message is raised.  If your server uses a
different attribute for the e-mail address, you can set the directive
`search pattern` under `ldap login`.  By default, `search pattern` is
set to `mail=%s`.  (The `%s` is replaced with the e-mail address when
the search is run.)

You may wish to [disable registration] entirely when using `ldap
login`.  In that case, it is not necessary to set the `base dn`, `bind
email`, and `bind password` directives.

## <a name="xsendfile"></a>Support for xsendfile

If your web server is not configured to support X-Sendfile headers,
set the `xsendfile` directive to `False`.

{% highlight yaml %}
xsendfile: False
{% endhighlight %}

Use of X-Sendfile is recommended because it allows the web server,
rather than the Python [WSGI] server, to serve files.  This is
particularly useful when serving sound files, since the web browser
typically asks for only a range of bytes from the sound file at a
time, and the [WSGI] server does not support the HTTP Range header.

This variable can be set using the [Docker] environment variable
[`XSENDFILE`].

However, there are some problems with the implementation of X-Sendfile
that can sometimes cause problems.  If you get random JavaScript
errors in your application, look at the network console, and if it
reports 0-byte JavaScript files being served, try setting `xsendfile:
False` in your Configuration.  This has been an issue when
**docassemble** operates behind a load balancer on [ECS].  On [Docker], if you
set [`BEHINDHTTPSLOADBALANCER`] to `true`, then `xsendfile` will be
set to `False` by default when the initial Configuration is first
created.

## <a name="websockets"></a><a name="websockets ip"></a><a name="websockets port"></a>Configuring the websockets server

The [live help] features depend on a [WebSocket] server.  On [Docker],
there is a [supervisor] service called `websockets` that runs the
`docassemble.webapp.socketserver` module.  By default, the server runs
on port 5000 on the localhost network (127.0.0.1).  This can be
configured:

{% highlight yaml %}
websockets ip: 75.34.2.14
websockets port: 5001
{% endhighlight %}

<a name="expose websockets"></a>The most common reason you might want
the server to run on an IP address other than 127.0.0.1 is if you are
running **docassemble** in a [Docker] container and want to connect to
the server from outside the container.  This is necessary in order to
run a [Docker] container [behind a reverse proxy].  If you set:

{% highlight yaml %}
expose websockets: True
{% endhighlight %}

then the server will attempt to connect to the first network that is
not the local network.  Typically, inside a [Docker] container, there
are two networks, `lo` and `eth0`.  Setting `expose websockets` to
`true` will cause the server to connect to whatever address is
associated with the `eth0` network.

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

If you are using [Docker] with [S3] or [Azure blob storage], and you
omit the `log server` or set it to `null`, then **docassemble** will
automatically find the hostname of the central log server in cloud
storage.

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

## <a name="session lifetime seconds"></a>Flask session lifetime

By default, [Flask] remembers sessions for 31 days.  To set this
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
directive.  The number refers to the milliseconds between each call to
the server.

{% highlight yaml %}
checkin interval: 6000
{% endhighlight %}

If you set the `checkin interval` to `0`, this will turn off the
check-in mechanism altogether.  This might be useful if you do not
need the check-in feature and you want to prevent unnecessary traffic
and CPU usage.

The features that rely on the `checkin interval` being greater than
zero include:

- Notifications of the results of [background tasks].
- The [check in] feature.
- The [live help] features.

Other than setting `checkin interval` to `0`, it is probably not a
good idea to reduce this value below `6000`.  If requests to modify a
single interview come in too frequently, problems can occur.

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
dictionary in which the keys are languages ([ISO-639-1] or [ISO-639-3]
codes) and the values are dictionaries with the translations of words
or phrases.

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

Users of **docassemble** have contributed translations of built-in
system phrases.  These are available in the `docassemble.base`
package, which is part of the core **docassemble** code.  To see a
list of translation [YAML] files that are available, see the [list of
files on GitHub].  For example, you can use the Italian translation
file by including `docassemble.base:data/sources/it-words.yml` in your
`words` directive.  Note that these user-contributed files have been
added at various times and may not be 100% complete.

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
`datatype` of [`currency`].  It will also be used as the return value
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

There are other ways to customize currency features.  In an interview,
you can configure the currency symbol using the [`set_locale()`]
function with the keyword parameter `currency_symbol`.  In addition,
you can set a field-specific currency symbol using the [`currency
symbol` field modifier].  See also the section on [customizing based
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

This will also enable you to use the [Google Maps Geocoding API] (see
the [`.geolocate()`] method), and will also enable the [Google Cloud
Translation API] for the feature in Utilities for translating system
words into other languages.

As of June 2018, Google
[requires that you enable billing](https://developers.google.com/maps/documentation/geolocation/usage-and-billing)
on the API key in order to use the geocoding feature.  To avoid charges, you may want to 
[restrict the API](https://developers.google.com/maps/faq#usage_cap) to no more than 2,500 
requests per day.

If you also specify a specific `google maps api key`, this key will be
used for the [`map_of()`] feature and the [address autocomplete]
feature instead of the `api key`.

{% highlight yaml %}
google:
  api key: UIJGeyD-23aSdgSE34gEGRg3GDRGdrge9z-YUia
  google maps api key: YyFeyuE-36grDgEE34jETRy3WDjGerye0y-wrRb
{% endhighlight %}

If you use both geocoding and Google Maps, you will probably want to
use a separate `google maps api key` because you can secure it
differently.  Note that the [`map_of()`] feature and the [address
autocomplete] feature put the API key in the [JavaScript] source, and
the communications with Google's server will come from the user's
computer.  By contrast, when you use the [`.geolocate()`] method, the
communications with Google's server come from your server.  Thus, you
may wish to secure the `api key` using IP addresses, and secure the
`google maps api key` using "Referer" headers.

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

To do this, go on the [Google Developers Console] and create an "app."
Within this app, create a [service account].  When you create the
service account, you will be provided with "credentials."  Download
the [JSON] (not p12) credential file for the service account.

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
  analytics id: UA-77777777-1
{% endhighlight %}

When this is configured, [JavaScript] for [Google Analytics] will be
inserted into your interview pages, and [pageview] events will be sent
to [Google Analytics] for any `question` that has an [`id`] defined.
These [pageview] events will record a view on an artificial path.  For
example, suppose you have the following question:

{% highlight yaml %}
id: lead certification
question: |
  Does your landlord have a valid lead certification?
yesno: lead_certification_exists
{% endhighlight %}

Suppose this question is part of the interview `answer.yml` in the
package `docassemble.eviction`.  In that case, the `pageview` will
record a view of the following pseudo-URL on your site:

> /eviction/answer/lead_certification

Since the [`id`] is also used as a unique identifier for a
[`question`], you might to use a different identifier for purposes of
Google Analytics.  If so, tag your question with [`ga id`] instead of
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
included that initializes [Segment].  When the user arrives at a
question with an [`id`], a [Segment] event will be fired with the
[`id`] as a name.

{% highlight yaml %}
segment id: ZAfFSeR6BTWiEfGnT8YpujspehLtswJP
{% endhighlight %}

Since the [`id`] is also used as a unique identifier for a
[`question`], you might to use a different identifier for purposes of
Segment.  If so, tag your question with [`segment id`] modifier (not
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
of the question to speech.  This relies on the [VoiceRSS] web service.
You will need to obtain an API key from [VoiceRSS] and set the
configuration below in order for this feature to function.  (The
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
feature to work.  The `key` is the [VoiceRSS] API key.  The
`dialects` key refers to a dictionary that associates languages with
the dialect to be used with that language.  For more information about
dialects, see the [VoiceRSS] documentation.

Sometimes, the language code you use in your interview is not the same
as the language code that [VoiceRSS] uses for that language.  In this
case, you can add a `language map` to your [VoiceRSS] configuration to
remap your language code so that it is compatible with [VoiceRSS].

For example, suppose the language code used in your interview is `zho`
for Chinese.  But the language that [VoiceRSS] recognizes for Chinese
is `zh`, and the dialects that [VoiceRSS] recognizes for `zh` include
`cn`, `hk`, and `tw`.  Suppose you want to use `cn` as the dialect.
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

## <a name="babel dates map"></a>Translation of dates

Many of the [date functions] rely on the [`babel.dates`] package.
This package does not support every language.  For example, if you run
`set_language('ht')`, functions that use [`babel.dates`] will return
an error.  You can set a different language to be used by
[`babel.dates`] as an alternative by setting the `babel dates map`
directive to a dictionary that translate language codes into
alternative language codes.  For example:

{% highlight yaml %}
babel dates map:
  ht: fr
{% endhighlight %}


## <a name="ocr languages"></a>OCR language settings

The [`ocr_file()`] function uses the [Tesseract]<span></span> [optical
character recognition] (OCR) application to extract text from image
files and PDF files.  One of the options for the OCR process is the
language being recognized.  The codes for language that [Tesseract]
may be different from those that **docassemble** uses.  If you are
using [ISO-639-1] for your language codes, the code that [Tesseract]
uses is the [ISO-639-3] code that corresponds to the [ISO-639-1] code
that **docassemble** uses, and **docassemble** can make this
conversion automatically.  However, in some cases this does not work,
so there is an override, which is controlled by the `ocr languages`
directive.  The default value maps Chinese to Traditional Chinese:

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

If you are using [Amazon S3] to store shared files, your access keys,
[bucket] name, and [region name] are in stored in the Configuration
as follows:

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
`endpoint url: https://mys3service.com`).  By default, [Amazon S3] is
used.

You will need to create the [bucket] before using it; **docassemble**
will not create it for you.

If you are using [Docker], you should not define an `s3` directive in
the Configuration using the web application when you already have a
server running.  The [S3] configuration is used throughout the boot
process and the shutdown process.  If you want to start using [S3],
you should start a new container using [`docker run`] with the
[`S3BUCKET`], [`S3REGION`], and other `S3` environment variables set.

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

### <a name="kubernetes"></a>kubernetes

If you are running **docassemble** from within a [Kubernetes]
deployment, add this to your Configuration

{% highlight yaml %}
kubernetes: True
{% endhighlight %}

This is necessary because when **docassemble** runs in a [multi-server
arrangement], each **docassemble** web server instance needs to allow
other **docassemble** web instances to send messages to it through
[supervisor].  Each web server instance advertises the hostname or IP
address through which its [supervisor] can be accessed.  Normally,
this can be obtained using the computer's hostname, but within a
[Kubernetes] cluster, this hostname is not one that other web servers
can resolve.  If `kubernetes` is set to `True`, then **docassemble**
will use the IP address of the Pod as the hostname.

## <a name="api privileges"></a>API usage

By default, only users with privileges of `admin` or `developer` may
obtain an API key in order to use the **docassemble** [API].  You can
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
`two factor authentication` as follows:

{% highlight yaml %}
two factor authentication:
  enable: True
{% endhighlight %}

Logged-in users will then see an option on their "Profile" page for
configuring two-factor authentication.  By default, only
administrators and developers see an option on their [user profile] to
configure second-factor authentication.  To configure which privileges
have the option of using second factor authentication, set the `allow
for` subdirective to the full list of [privileges] for which you want
the feature to be available.

{% highlight yaml %}
two factor authentication:
  allow for:
    - admin
    - developer
    - user
    - advocate
{% endhighlight %}

Regardless of these settings, two-factor authentication is not
available to users who sign in with [external authentication
methods](#oauth) or who are using the [phone login] feature.  It is
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

By default, two-factor authentication is optional for all users.  As
usual, two-factor authentication is not compatible with [external
authentication methods](#oauth) or the [phone login] feature, so you
will want to disable those features if you want to enforce two-factor
authentication.

The default value of `enable` is True, so you can omit the
`enable` line.  You can write `two factor authentication: True`
to enable two-factor authentication with all of the default options.

## <a name="playground examples"></a>List of examples in the Playground

As a development aid, the [Playground] contains an [examples area]
with a list of short sample interviews that demonstrate particular
features.  The interviews shown here are controlled by the file
[`docassemble.base:data/questions/example-list.yml`].  If you would
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
the [Playground] examples section.  The URL under `documentation` will
be the URL behind the "View documentation" link in the [Playground]
examples section.  The blocks of the interview that will be shown on
the screen are based on the `example start` and `example end` items.
In this example, block "1" is the [`question`] block, and block "2" is
the [`code`] block.  (Block "0" is the [`metadata`] block.)  So the
[`question`] block and the [`code`] block will be shown, but not the
[`metadata`] block.

## <a name="vim"></a><a name="keymap">Changing the mode of the editor in the Playground

If the `keymap` directive is set to `vim`, `emacs`, or `sublime`, then
the in-browser text editors in the [Playground] will emulate [Vim],
[Emacs], or [Sublime Text], respectively.  This uses the [Vim bindings
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
**docassemble**.  If users will see `https://docassemble.example.com` in
the location bar on the web browser, `external hostname` will be
`docassemble.example.com`.

{% highlight yaml %}
external hostname: docassemble.example.com
{% endhighlight %}

This variable is only effective if **docassemble** is running on
[Docker].  It is typically set by the [`DAHOSTNAME`] environment
variable when the [`docker run`] command is run for the first time.

If you change `external hostname`, you need to do a complete restart
of the system for the change to take effect.  (That is, `docker
stop -t 600 <container ID>` followed by `docker start <container ID>`.)

## <a name="behind https load balancer"></a>When behind a proxy

Set the `behind https load balancer` directive to `True` if you are
running **docassemble** in a configuration where **docassemble**
itself is running [HTTP], but requests are being forwarded to it by a
server running HTTPS.  This might be your configuration if you are
using a [load balancer] or you are running [Docker] on machine that
[forwards] HTTPS requests to [Docker] on a non-standard [HTTP] port.

This variable is typically set using the [Docker] environment variable
[`BEHINDHTTPSLOADBALANCER`].

If you change this variable, you need to do a complete restart of the
system for the change to take effect.  (That is, 
`docker stop -t 600 <container ID>` followed by `docker start <container ID>`.)

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
[`docker run`] command is run for the first time.  You can change the
`use https`, `use lets encrypt`, and `lets encrypt email` variables on
a running server, but they will only be effective if you restart the
system using `docker stop -t 600 <container ID>` followed by 
`docker start <container ID>`.

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

## <a name="update on start"></a>Whether software is updated on start

By default, when a [Docker] container starts, whether it is starting
for the first time during a [`docker run`] process, or restarting during a
[`docker start`] process, one of the steps taken during the container
initialization process is the updating of Python packages.

This process is necessary in order to install any custom Python
packages you have, such as interviews you have created.  If you
replace a container with [`docker stop -t 600`], [`docker rm`], and
[`docker run`], you will want the new container to have the
appropriate software on it.  When you use [Package Management] or the
[packages folder] of the [Playground] to install a package on your
system, the packages that get installed are tracked in the SQL
database.  When you start up a new [Docker] container that uses that
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
update on start: False
{% endhighlight %}

Alternatively, if you want the update process to run during the
[`docker run`] process but not subsequently, you can set:

{% highlight yaml %}
update on start: initial
{% endhighlight %}

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
[redis URI].  To specify a non-standard port, use the form
`redis://192.168.0.2:7000`.

If you are using [Docker] with [S3] or [Azure blob storage], and you
omit the `redis` directive or set it to `null`, then **docassemble**
will automatically find the hostname of the central redis server in
cloud storage.

**docassemble** uses three [Redis] "databases."  By default, it uses
0, 1, and 2.  If you want it to use different database numbers, you
can set `redis database offset` to a number.

{% highlight yaml %}
redis database offset: 3
{% endhighlight %}

In this case, **docassemble** will use databases 3, 4, and 5 instead
of 0, 1, and 2.

## <a name="rabbitmq"></a>RabbitMQ server location

By default, **docassemble** assumes that the [RabbitMQ] server is located
on the same server as the web server.  You can designate a different
[RabbitMQ] server by setting the `rabbitmq` directive:

{% highlight yaml %}
rabbitmq: amqp://guest@192.168.0.2//
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

## <a name="libreoffice"></a><a name="pandoc"></a><a name="convertapi secret"></a>Document conversion

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

By default, **docassemble** uses [LibreOffice] to convert DOCX
templates to PDF format.  Alternatively, you can use [ConvertAPI], a
web service for file conversion.  To enable this, sign up with
[ConvertAPI] and set the `convertapi secret` to the "Secret" that
[ConvertAPI] generates for you.

{% highlight yaml %}
convertapi secret: SrWh4XfuOje5jYx1
{% endhighlight %}

Enabling [ConvertAPI] can be useful if you are using [`docx template
file`] to generate PDF files, but the standard [LibreOffice]
conversion does not work properly due to incompatibilities between
[Microsoft Word] and [LibreOffice].

## <a name="pandoc engine"></a>Pandoc's LaTeX engine

By default, [Pandoc] uses `pdflatex` to generate PDF files from
[Markdown].  If you would like to use a different engine, you can
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

The default is `False`.  The setting can also be made on a
per-interview basis by setting the [`pdf/a` features setting].

<a name="tagged pdf"></a>When using [`docx template file`], you also
have the option of creating a "tagged PDF," which is similar to
[PDF/A].  You can set this as a server-wide default:

{% highlight yaml %}
tagged pdf: True
{% endhighlight %}

This setting can also be made on a per-interview basis by setting the
[`tagged pdf` features setting].

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

## <a name="image upload type"></a>Converting the format of uploaded images

If you are using `maximum image size`, you can also cause images to be
converted to [PNG], [JPEG], or [BMP] by the browser during the upload
process by setting the `image upload type` to `png`, `jpeg`, or `bmp`.

{% highlight yaml %}
image upload type: jpeg
{% endhighlight %}

## <a name="celery processes"></a>Number of concurrent background tasks

**docassemble** uses [Celery] to execute background tasks.  The
[Celery] system is able to execute multiple tasks concurrently.  The
number of concurrent processes is limited by default to the number of
CPU cores on the machine.  If you want to increase the number of
processes, set the `celery processes` directive.

{% highlight yaml %}
celery processes: 15
{% endhighlight %}

This value will be passed directly to [Celery]'s [`worker_concurrency`]
configuration variable.

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
the HTTP request.  However, if your server is behind a proxy, this
latter method may not be accurate, so should [`url root`] in order for
the [Microsoft Word sidebar] to work correctly.

Note that a Word sidebar is just a web page that consists of an [HTML]
file with some [CSS] and [JavaScript] files associated with it.  These
files can be hosted on any site on the internet as long as HTTPS is in
use.  (Microsoft requires HTTPS.)  When your Microsoft Word
application accesses this web page, you can click the "Use a different
server" button to instruct the sidebar to access the [Playground] on
any server to which you have access.  Then the [JavaScript] on the page
will communicate directly with that server and pass information back
and forth between Microsoft Word and the [Playground] on the server.

Your **docassemble** server can serve as the host for the web page.
If your server's hostname is https://interviews.example.com, then the
sidebar will be available at
https://interviews.example.com/officetaskpane.  If you create an [XML
manifest file] for the sidebar from the [Utilities] page of your
server, you will see this URL embedded in the XML.

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

## <a name="oauth"></a>Facebook, Twitter, Google, Auth0, and Azure login

If you want to enable logging in with Facebook, Twitter, Google,
Auth0, or Microsoft Azure, you will need to tell **docassemble** your
[OAuth2] keys for these services:

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
[installation] page's sections on [Facebook], [Twitter], [Google],
[Auth0], and [Azure].

Note that in [YAML], dictionary keys must be unique.  So you can only
have one `ouath:` line in your configuration.  Put all of your
[OAuth2] configuration details (for Google logins, Google Drive
integration, OneDrive integration, etc.) within a single `oauth`
directive.

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
with interviewees through text messaging, the [call forwarding]
feature for connecting interviewees with operators over the phone, and
the [fax sending] feature.

These features are enabled using a `twilio` configuration directive.
Here is an example:

{% highlight yaml %}
twilio:
  sms: True
  voice: True
  fax: True
  account sid: ACfad8e668d876f5473fb232a311243b58
  auth token: 87559c7a427c25e34e20c654e8b05234
  number: "+12762410114"
  whatsapp number: "+12762268342"
  dispatch:
    color: docassemble.base:data/questions/examples/buttons-code-color.yml
    doors: docassemble.base:data/questions/examples/doors.yml
  default interview: docassemble.base:data/questions/default-interview.yml
{% endhighlight %}

The `sms: True` line tells **docassemble** that you intend to use the
text messaging features.

The `voice: True` line tells **docassemble** that you intend to use the
[call forwarding] feature.

The `fax: True` line tells **docassemble** that you intend to use the
[fax sending] feature.

The `account sid` is a value you copy and paste from your [Twilio]
account dashboard.

The `auth token` is another value you copy and paste from your
[Twilio] account dashboard.  This is only necessary if you intend to
use the [`send_sms()`] function or the [phone login] feature.

The `number` is the phone number you purchased.  The phone number
must be written in [E.164] format.  This is the phone number with
which your users will exchange [SMS] messages.

The `whatsapp number` (optional) is the phone number you use for
sending [WhatsApp] messages.  The number must be written in [E.164]
format.

The `dispatch` configuration allows you to direct users to different
interviews.  For example, with the above configuration, you can tell
your prospective users to "text 'color' to 276-241-0114."  Users who
initiate a conversation by sending the SMS message "help" to the
[Twilio] phone number will be started into the
`docassemble.base:data/questions/examples/sms.yml` interview.

The [`default interview`] configuration allows you to set an interview
that will be used in case the user's initial message does not match up
with a `dispatch` entry.  If you do not set a [`default interview`], the
global [`default interview`] will be used.  If you want unknown
messages to be ignored, set [`default interview`] to `null`.

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
    fax: True
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
    fax: False
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

## <a name="user agent"></a>User agent for downloading files

Functions such as [`path_and_mimetype()`] will download files from the
internet.  When the server downloads the file, it reports its [user
agent] as `curl/7.64.0` by default.  This might cause problems
for your interviews because some web sites may not want to serve files
to a user that identifies itself as a "robot."

To use a different [user agent], you can set the `user agent`
configuration directive.  For example:

{% highlight yaml %}
user agent: Mozilla/5.0 (X11; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0
{% endhighlight %}

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

## <a name="editable mimetypes"></a><a name="editable extensions"></a>Editable file types

By default, the only file types that can be edited in the folders of
the Playground are `text` [MIME] types and file types that are used in
**docassemble**, like [YAML], [CSS], [JavaScript], and [HTML].  Other
types are presumed to be non-editable, and there is no "Edit" button
next to the file in the Playground folder.

You can make additional file types editable using `editable mimetypes`
or `editable extensions`.  For example, if you wanted to be able to
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

The template text would be inserted as a single "run," meaning that it
cannot contain any proper paragraph breaks, only manual line breaks.

There is a newer system of inserting Markdown [`template`]s into
[`docx template file`]s, which can handle multiple paragraphs and a
wider variety of Markdown.  However, this new system is not backwards
compatible with the original system, because under the new system you
need to include the [`template`] as follows:

> {% raw %}{{p the_template }}{% endraw %}

To upgrade to the new system today, set the following in your
Configuration:

{% highlight yaml %}
new markdown to docx: True
{% endhighlight %}

The new system will become the default at some point in the future, so
when you have time, you should adapt your DOCX files if you are using
`{% raw %}{{r ... }}{% endraw %}` to insert [`template`]s.

## <a name="web server"></a>Choosing Apache instead of NGINX

By default, the web server used with [Docker] is [NGINX].  You can
change this to [Apache] by adding the following to your Configuration:

{% highlight yaml %}
web server: apache
{% endhighlight %}

The default is `nginx`.  After changing this, you will need to do a
[`docker stop -t 600`] followed by a [`docker start`].  This feature
requires system version 0.5.0 or later.

See also the [`DAWEBSERVER`] environment variable.

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
URLs to files will link directly to the cloud provider.  However, this
can cause problems with [Cross-Origin Resource Sharing], and will not
work if you are using an [S3]-compatible cloud storage system that
is not accessible from the user's network.  If you would rather serve
files from the server itself, set `use cloud urls` to `False`.

{% highlight yaml %}
use cloud urls: False
{% endhighlight %}

# <a name="get_config"></a>Adding your own configuration variables

Feel free to use the configuration file to pass your own variables to
your code.  To retrieve their values, use the [`get_config()`] function:

{% highlight yaml %}
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
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`root`]: #root
[Pandoc]: http://johnmacfarlane.net/pandoc/
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
[Auth0]: {{ site.baseurl }}/docs/installation.html#auth0
[Azure]: {{ site.baseurl }}/docs/installation.html#azure
[invited by an administrator]: {{ site.baseurl }}/docs/users.html#invite
[`root`]: #root
[`docassemble.webapp.fix_postgresql_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/fix_postgresql_tables.py
[`docassemble.webapp.install_certs`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/install_certs.py
[`brandname`]: #brandname
[`appname`]: #appname
[PYTHONUSERBASE]: https://docs.python.org/3.6/using/cmdline.html#envvar-PYTHONUSERBASE
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[`cert install directory`]: #cert install directory
[HTTPS]: {{ site.baseurl }}/docs/docker.html#https
[startup process]: {{ site.github.repository_url }}/blob/master/Docker/initialize.sh
[URI]: https://en.wikipedia.org/wiki/Uniform_Resource_Identifier
[`azure`]: #azure
[`s3`]: #s3
[`s4cmd`]: https://github.com/bloomreach/s4cmd
[Facebook, Twitter, Google, or Azure]: #oauth
[`certs`]: #certs
[`log`]: #log
[locale]: https://docs.python.org/3/library/locale.html
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
[Emacs]: https://www.gnu.org/software/emacs/
[Sublime Text]: https://www.sublimetext.com/
[Vim bindings option]: https://codemirror.net/demo/vim.html
[Emacs bindings option]: https://codemirror.net/demo/emacs.html
[Sublime Text bindings option]: https://codemirror.net/demo/sublime.html
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
[privileges]: {{ site.baseurl }}/docs/users.html
[bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[PDF/A]: https://en.wikipedia.org/wiki/PDF/A
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[`pdf/a` features setting]: {{ site.baseurl }}/docs/initial.html#pdfa
[`tagged pdf` features setting]: {{ site.baseurl }}/docs/initial.html#tagged pdf
[Jinja2]: http://jinja.pocoo.org/docs/2.9/
[Flask]: http://flask.pocoo.org/
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
[Bootswatch]: https://bootswatch.com/
[live help]: {{ site.baseurl }}/docs/livehelp.html
[`bootstrap theme` feature]: {{ site.baseurl }}/docs/initial.html#bootstrap theme
[`inverse navbar` feature]: {{ site.baseurl }}/docs/initial.html#inverse navbar
[`map_of()`]: {{ site.baseurl }}/docs/functions.html#map_of
[decorations]: {{ site.baseurl }}/docs/modifiers.html#decoration
[image buttons]: {{ site.baseurl }}/docs/fields.html#image button
[MySQL]: https://en.wikipedia.org/wiki/MySQL
[PNG]: https://en.wikipedia.org/wiki/Portable_Network_Graphics
[JPEG]: https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
[BMP]: https://en.wikipedia.org/wiki/BMP_file_format
[customizing]: #start page template
[`interview_list()`]: {{ site.baseurl }}/docs/functions.html#interview_list
[`interview_menu()`]: {{ site.baseurl }}/docs/functions.html#interview_menu
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`ServerAdmin`]: https://httpd.apache.org/docs/2.4/mod/core.html#ServerAdmin
[background tasks]: {{ site.baseurl }}/docs/background.html#background
[`worker_concurrency`]: http://docs.celeryproject.org/en/latest/userguide/configuration.html#worker-concurrency
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
[`pre`]: {{ site.baseurl }}/docs/initial.html#pre
[`submit`]: {{ site.baseurl }}/docs/initial.html#submit
[`post`]: {{ site.baseurl }}/docs/initial.html#post
[`show interviews link`]: #show interviews link
[`BEHINDHTTPSLOADBALANCER`]: {{ site.baseurl }}/docs/docker.html#BEHINDHTTPSLOADBALANCER
[`DAHOSTNAME`]: {{ site.baseurl }}/docs/docker.html#DAHOSTNAME
[`DAWEBSERVER`]: {{ site.baseurl }}/docs/docker.html#DAWEBSERVER
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
[ConvertAPI]: https://www.convertapi.com
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
[ECS]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
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
[`babel.dates`]: http://babel.pocoo.org/en/latest/api/dates.html
[edit user accounts]: {{ site.baseurl }}/docs/admin.html#edit user profile
[user profile]: {{ site.baseurl }}/docs/admin.html#profile
[multi-user interview]: {{ site.baseurl }}/docs/special.html#multi_user
[multi-user interviews]: {{ site.baseurl }}/docs/special.html#multi_user
[`show dispatch link`]: #show dispatch link
[`short title`]: {{ site.baseurl }}/docs/initial.html#metadata
[`title`]: {{ site.baseurl }}/docs/initial.html#metadata
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
