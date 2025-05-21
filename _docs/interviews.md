---
layout: docs
title: How to write an interview
short_title: Interviews
---

# <a name="whatis"></a>What is a **docassemble** interview?

An "interview" in **docassemble** is a [YAML] file that
**docassemble** reads, and on the basis of what it finds, asks
questions of a user.

**docassemble** stores the user's answers in "variables."  The values
of these variables may be incorporated into the the text of [questions],
or into the text of [documents].

The interview can ask users different questions depending on what the
answers to earlier questions were.

# <a name="simple interview"></a>The contents of an interview file

The interview file is a series of possible questions that could
potentially be asked, arranged in no particular order.  Which
questions will be asked, and the order in which they are asked, will
be determined by **docassemble**.  All you need to do is give
**docassemble** an end goal.

The end goal might be as simple as "show the exit screen."  This will
instruct **docassemble** to try to show the exit screen.  But
**docassemble** will doubtless find that in order to show the exit
screen, it will need some piece of information.  It will look for a
question in the [YAML] file that will provide that information, and it
will try to ask that question.  But it may find that in order to ask
that question, it needs to know another piece of information, and it
will look for a question that provides that information, and so forth
and so on.  The first question will turn out to be something basic,
like "What is your name?" and **docassemble** might not reach the exit
screen until 20 questions have been asked and answered.

In addition to questions, the [YAML] file can contain bits of logic,
written as lines of [Python] code.  For example:

{% highlight yaml %}
code: |
  if user.age >= 65:
    recommended_insurance = "Medicare"
  elif user.age < 18:
    if household.is_low_income:
      recommended_insurance = "CHIP"
    else:
      recommended_insurance = "parent coverage"
  else:
    if household.is_low_income:
      recommended_insurance = "Medicaid"
    else:
      recommended_insurance = "Private Insurance"
{% endhighlight %}

If the interview ever needs to know the recommended insurance, it will
run this code.  If it does not know the user's age, it will ask.  If
the user is under 65, **docassemble** will ask questions to determine
whether the household is low-income.

A [YAML] interview file is simply a text file consisting of "blocks"
separated by `---`.  For example, this interview has three blocks:

{% include side-by-side.html demo="animal" %}

The first block is a "question" that defines the variable `favorite_animal`.

The second block is a "question" that defines the variable `favorite_vegetable`.

The third block is a "question" that is marked as `mandatory`.  This
is not really a question, since it offers the user no option except
clicking the "Exit" button.  It refers to the variable `favorite_animal`.

When **docassemble** presents this interview to the user, it follows
these steps:

1. It scans the file and processes everything that is "[`mandatory`]."  It
  treats everything else as optional.
2. It finds a [`mandatory`] question in the third block and tries to
   ask the question.
3. It can't assemble the question because `favorite_animal` is not defined,
so it looks for a question that defines `favorite_animal`.
4. It looks through the blocks for a question that defines
`favorite_animal`, and finds it in the first block.
5. It asks the user for his or her favorite animal, and goes back to
step 1.  This time around, it is able to ask the `mandatory` question,
and the interview stops there because the only thing the user can do
is press the "Exit" button.

The order of the blocks in the file is irrelevant; **docassemble**
would do the same thing regardless of the order of the blocks.

Note that the second block, containing the question about the user's
favorite vegetable, was never used because it was never needed.

This is a very simple interview; there are more types of blocks that
you can write.  These blocks are explained in the following sections:

* [Initial Blocks] - Explains special blocks you can write that have
  an effect on whole interview.
* [Question Blocks] - Explains the basics of the [`question`] block, which presents a
  screen to the user (which usually asks a question but does not need to).
* [Setting Variables] - Explains how to collect information from users
  using `question` blocks.
* [Question Modifiers] - Explains ways you can enhance questions with
  special features, for example by adding help text or icons.
* [Code] - Explains `code` blocks, which are like `question`s except
  that instead of presenting something to the user, they run [Python]
  code that defines variables or does other things that computer code
  can do.
* [Interview Logic] - Explains [`mandatory`] and [`initial`] blocks and how
  **docassemble** processes your interview [YAML] to produce an interview.
* [Markup] - Explains how to change the formatting of text in
  **docassemble**.
* [Documents] - Explains how to assemble documents in PDF and RTF
  format based on the user's answers to the interview questions.
* [Objects] - Explains the use of Python objects to simplify the way
  information is organized.
* [Groups] - Explains how to gather information into special variables
  that contain zero or more items representing a group of some sort.
* [Functions] - Explains how to use special [Python] functions to
  simplify and generalize the way questions are asked.
* [Legal Applications] - Explains some special objects types that are
  useful for interviews created by legal practitioners.
* [Special Variables] - Describes variables that have special
  properties, as well as variable names you aren't allowed to use
  because they would conflict with the functionality of
  **docassemble** and [Python].

# <a name="yaml"></a>Brief introduction to YAML

**docassemble** interviews are written in [YAML] format, rather than
assembled using a [graphical user interface], because once developers
have climbed the **docassemble** learning curve, the text format is
ideal for managing the complexity of advanced interviews, since it
allows developers to copy-and-paste, search-and-replace, and organize
text into multiple files.  [YAML] was chosen as the format because it
is the cleanest-looking of data formats that are both machine-readable
and human-readable.

The hardest part about learning **docassemble** is not writing
[Python] code, since sophisticated interviews can be built using
nothing more complicated than a few [if/else statements].  The more
difficult aspect may be learning [YAML].  While the [YAML] format
looks simple, it can be frustrating.

To understand [YAML], you first need to understand the difference
between a "list" and a "dictionary."

A "list" is an ordered collection of things.  If my to-do list for a
Saturday afternoon was first to take out the garbage, and then to
sweep the porch, this could be represented in [YAML] as:

{% highlight yaml %}
- Sweep the porch
- Take out the garbage
{% endhighlight %}

A "dictionary," by contrast, associates things with other things.  For
example, if I have some legal terms that I want to associate with an
explanation, I could put this in a [YAML] dictionary:

{% highlight yaml %}
lawyer: A person who represents you.
judge: A person who decides who wins or loses a court case.
{% endhighlight %}

While a list has an order to it (e.g., I need to first sweep the porch and
then take out the garbage), the dictionary is just a jumble of words
and definitions.  More generally, it associates "keys" with "values."

[YAML] interprets lines of text and figures out whether you are
talking about a list or a dictionary depending on what punctuation you
use.  If it sees a hyphen, it thinks you are talking about a list.  If
it sees a colon, it thinks you are talking about a dictionary.

Lists and dictionaries can be combined.  You can have a dictionary of
lists and a list of dictionaries.  If I wanted to express the to-do
lists of multiple people, I could write:

{% highlight yaml %}
Frank:
  - Sweep the porch
  - Take out the garbage
  - Clean the toilets
Sally:
  - Rake the leaves
  - Mow the lawn
{% endhighlight %}

Here, you have a dictionary with two keys: "Frank" and "Sally."  The
value of the "Frank" key is a list with three items, and the value of
the "Sally" key is a list with two items.

If you are familiar with [Python]'s data notation, this translates
into:

{% highlight python %}
{"Frank": ["Sweep the porch", "Take out the garbage", "Clean the toilets"], "Sally": ["Rake the leaves", "Mow the lawn"]}
{% endhighlight %}

The [JSON] representation is the same.

You can also have a list of dictionaries:

{% highlight yaml %}
- title: Tale of Two Cities
  author: Charles Dickens
- title: Moby Dick
  author: Herman Melville
- title: Green Eggs and Ham
  author: Dr. Seuss
{% endhighlight %}

In [Python]'s data notation, this translates into:

{% highlight python %}
[{'title': 'Tale of Two Cities', 'author': 'Charles Dickens'}, {'title': 'Moby Dick', 'author': 'Herman Melville'}, {'title': 'Green Eggs and Ham', 'author': 'Dr. Seuss'}]
{% endhighlight %}

[YAML] also allows you to divide up data into separate "documents"
using the `---` separator.  Here is an example of using three
documents to describe three different books:

{% highlight yaml %}
title: Tale of Two Cities
author: Charles Dickens
---
title: Moby Dick
author: Herman Melville
---
title: Green Eggs and Ham
author: Dr. Seuss
{% endhighlight %}

[YAML]'s simplicity results from its use of simple punctuation marks.
However, be careful about data that might confuse the computer.  For
example, how should the computer read this shopping list?

{% highlight yaml %}
- apples
- bread
- olive oil, the good stuff
- shortening: for cookies
- flour
{% endhighlight %}

In [Python], this will be interpreted as:

{% highlight python %}
['apples', 'bread', 'olive oil, the good stuff', {'shortening': 'for cookies'}, 'flour']
{% endhighlight %}

This is a list of apples, bread, olive oil, a dictionary, and flour.
That's not what you wanted!

You wanted `shortening: for cookies` to be a piece of text.  But the
computer assumed you wanted to indicate a dictionary.  [YAML]'s clean
appearance makes it readable, but this kind of problem is the downside
to [YAML].

You can get around this problem by putting quote marks around text:

{% highlight yaml %}
- apples
- bread
- olive oil
- "shortening: for cookies"
- flour
{% endhighlight %}

This will result in all of the list elements being interpreted as
plain text.  In [Python]:

{% highlight python %}
['apples', 'bread', 'olive oil', 'shortening: for cookies', 'flour']
{% endhighlight %}

[YAML] also allows text to be block quoted:

{% highlight yaml %}
title: |
  Raspberry Jam: a "Fancy" Way to Eat Fruit
author: |
  Jeanne Trevaskis
{% endhighlight %}

The pipe character `|` followed by a line break indicates the start of
the quote.  The indentation is important because it indicates where
the block quote ends.  As long as you are indenting each line of text,
you can write anything you want in the text (e.g., colons, quotation
marks) without worrying that the computer will misinterpret what you
are writing.

The following values in [YAML] are special:

* `null`, `Null`, `NULL` -- these become `None` in [Python]
* `true`, `True`, `TRUE` -- these become `True` in [Python]
* `false`, `False`, `FALSE` -- these become `False` in [Python]
* numbers such as `54`, `3.14` -- these become numbers in [Python]

These values will not be interpreted as literal pieces of text, but as
values with special meaning in [Python].  This can cause confusion in
your interviews, so if you ever use "True" and "False" as a label or
value, make sure to enclose it in quotation marks.

This [YAML] text:

{% highlight yaml %}
loopy: 'TRUE'
smart: false
pretty: TRUE
energetic: "false"
{% endhighlight %}

becomes the following in [Python]:

{% highlight python %}
{'loopy': 'TRUE', 'smart': False, 'pretty': True, 'energetic': 'false'}
{% endhighlight %}

One feature of [YAML] that is rarely used, but that you may see, is
the use of "explicit mapping."  Instead of writing:

{% highlight yaml %}
apple: red
orange: orange
banana: yellow
{% endhighlight %}

You can write:

{% highlight yaml %}
? apple
: red
? orange
: orange
? banana
: yellow
{% endhighlight %}

Both mean the same thing.  You might want to use this technique if
your labels in a [`fields`] specifier are long.  For example, instead
of writing:

{% highlight yaml %}
question: |
  Please answer these questions.
fields:
  "Where were you born?": place_of_birth
  "What were the last words of the first President to fly in a Zeppelin?": words
{% endhighlight %}

you could write:

{% highlight yaml %}
question: |
  Please answer these questions.
fields:
  ? Where were you born?
  : place_of_birth
  ? |
    What were the last words of the
    first President to fly in a Zeppelin?
  : words
{% endhighlight %}

Note that many punctuation marks, including `"`, `'`, `%`, `?`, `~`, `|`, `#`, `>`, `:`, `!`, `{`, `}`,
`[`, and `]`, have special meaning in [YAML], so if you use them in
your text, make sure to use quotation marks or block quotes.

For more information about [YAML], see the [YAML specification].

# <a name="htdevelop"></a>How to develop your own interviews

To write and test your own interviews, you will need:

1. A **docassemble** server (see [Docker]);
2. An account on the [username and password system] of that server,
   where the privileges of the account are "developer" or "admin."

There are several to develop your own interviews:

1. When logged in, go to the "Playground" from the menu in the upper
   right hand corner.  The [playground] allows you to quickly edit and
   run interview [YAML].
2. Create a [package] on your local computer and then install it on
   the **docassemble** server either through [GitHub] or by uploading a ZIP
   file.
3. Create a [package], push it to [GitHub], and then edit your
   interviews using [GitHub]'s web interface.  (You can also upload
   static files using [GitHub].)  To run your interview, update your
   [package] on **docassemble** (which will retrieve your code from
   [GitHub]).

For more information about the development workflow, see the
[development overview] section.

# <a name="invocation"></a>How you run a **docassemble** interview

Users start an interview by going to its URL, which is the
`/interview` path on your site with the `i` URL parameter set to the
name of the interview.

For example, the [demo interview], which is hosted on the site
`demo.docassemble.org`, can be accessed with this URL.

[{{ site.demourl }}/interview?i=docassemble.demo:data/questions/questions.yml]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/questions.yml){:target="_blank"}

Here, the interview file name is
`docassemble.demo:data/questions/questions.yml`.  This tells
**docassemble** to look for a Python package named `docassemble.demo`
and then within that package, look for the file `questions.yml`
located in the subdirectory `data/questions`.

You can make your own [packages] and then install them on your site.
If the name of your site is `interview.example.com`, the name of your
package is `docassemble.mypackage`, and the name of your interview
file is `myinterview.yml`, your users can access the interview at:

> https://interview.example.com/interview?i=docassemble.mypackage:data/questions/myinterview.yml
{: .blockquote}

If your interview is in the [Playground], the name of the interview
will be something like `docassemble.playground1:myinterview.yml` where
`1` is your user ID.  Or, if your interview is in a "project" inside
your Playground, and the project is called `testing`, the name of the
interview will be something like
`docassemble.playground1testing:myinterview.yml`.  You can see the
name of the interview in the URL while you are testing the interview,
or in the URL available using the "Share" button in the Playground.
The interview file name is the `i` parameter in the URL.

Note that while you are using an interview, the URL in the location
bar will change.  It will end with `#page1`, then `#page2`, then
`#page3`, etc., as the interview progresses.  These tags have no
direct effect and the page number has no particular meaning; these
tags exist because of their side effect, which is to enable the user
to click the browser's back button in order to go back one screen.

The remainder of this subsection will discuss ways that you can
customize the way that interviews are invoked.  This is a fairly
advanced topic, so if you are new, feel free to skip to the section on
[how answers are stored].

URLs to `/interview` with an `i` parameter are not meant to be
understood by users; they are primarily meant to make clear to the
developer where the interview file is located in the Python package.
If you want a more readable URL, you can use:

> https://interview.example.com/start/mypackage/myinterview/
{: .blockquote}

which launches the same interview as

> https://interview.example.com/interview?i=docassemble.mypackage:data/questions/myinterview.yml
{: .blockquote}

Once the user visits a URL like `/start/mypackage/myinterview/`, the
URL in the location bar will change to `/run/mypackage/myinterview/`.
This is because `/start` will cause a new session to be created,
whereas `/run` will continue an existing session that is operating in
the user's browser.

If you want to use **docassemble** to give users a list of interviews
from which to choose, there is a special page of the site, located at
`/list`, which displays a [list of interviews] available on your site.

> https://interview.example.com/list
{: .blockquote}

This list is not automatically-generated.  You need to configure the
list using the [`dispatch`] configuration directive.  The list of
interviews can also be [embedded] into a page of another web site.
This page is highly [configurable].  You can also replace the default
`/list` page with an interview using the [`dispatch interview`]
configuration directive.  Within that interview, you can use the
[`interview_menu()`] function within that interview to present the
list of interviews in whatever way you want.

The [`dispatch`] configuration directive also allows your users to
start new sessions in specific interviews at human-readable URLs like:

> https://interview.example.com/start/eviction/<br>
> https://interview.example.com/start/namechange/
{: .blockquote}

Once the user visits a URL like `/start/eviction/`, the URL in the
location bar will change to `/run/eviction/`.

If the user visits the main (or "root") URL for the site, e.g.,
`https://interview.example.com`, the user will be redirected to the
URL indicated by the [`root redirect url`] configuration directive.  A
typical way to use this feature is to direct users to a web site
outside of **docassemble** where they can find out information about
the services you offer.

If you don't have a [`root redirect url`] set, the user will be
redirected to `/interview` and will start the interview indicated by
the [`default interview`] configuration directive.

This can be useful when you have one primary interview on your site
and you want users to be able to start it by visiting an easy-to-type
URL such as:

> https://interview.example.com
{: .blockquote}

If you have set [`root redirect url`], your [`default interview`]
interview will still be accessible at:

> https://interview.example.com/interview
{: .blockquote}

If you do not have a [`default interview`], but you have configured a
`/list` page using the [`dispatch`] configuration directive, then the
user who visits the "root" URL of your site will be redirected to
`/list`.

However, if the user had previously been using another interview
during the same browser session, going to
`https://interview.example.com/` (without a [`root redirect url`])
will resume the original session.

If you want your users who are in the middle of an interview to be
able to begin a different interview, you can enable [`show dispatch
link`] in the [configuration], and then in the menu, the user will see
a link called "Available Interviews," which directs to your `/list`
page.  You can also use the [`menu_items` special variable] within an
interview to provide options on the pull-down menu for starting other
interviews.  Within the body of an interview question, you can insert
a link to another interview using the [`interview_url()`] function
with an `i` parameter indicating the interview.

## <a name="iframe"></a>Embedding the interview into a web page with an iframe

You can embed an interview into a web page by inserting an [iframe]
into the [HTML] of the page.

{% highlight html %}
<iframe style="width: 500px; height: 700px;" src="https://demo.docassemble.org/interview?i=docassemble.demo:data/questions/questions.yml&reset=1"></iframe>
{% endhighlight %}

You should adjust the width and height of the [iframe] based on what
makes sense for the web page.  **docassemble** can handle a variety of
sizes, but make sure you test the user experience both on desktop
and on mobile.  Since embedded interviews are often less than ideal for
mobile users, you can use the [`go full screen`] feature to cause the
interview to "go full screen" on the user's device once the user
starts interacting with it.

There is a [Drupal module] and a [WordPress plugin] for embedding
interviews using an [iframe].

When embedding using an [iframe], set the [`allow embedding`]
directive in the [Configuration] to `True`.  When you do this,
**docassemble** will refrain from setting the `X-Frame-Options` header
to `SAMEORIGIN` (which would otherwise tell the browser not to show
the [iframe]).  In addition, this will cause a flag on the cookies to
be set so that cross-site cookie sharing is allowed.

Web browsers are generally permissive about allowing [iframe]s even
when the host domain and [iframe] domain are different.  However, some
browsers, such as Safari, might block the content because of
[Cross-Origin Resource Sharing] concerns.

It may also help to set [`cross site domains`] in your [Configuration]
to include the protocol and domain of the host site.  For example:

{% highlight yaml %}
cross site domains:
  - https://example.com
{% endhighlight %}

When this is set, your server will respond to requests with special
headers that indicate to the browser that your server consents to
allowing `https://example.com` to embed its content.

Even after you set [`cross site domains`], some browsers may still
block the [iframe] content if the top-level domain of the host server
is different from the top-level domain of the **docassemble** server.
Thus, if your host web site is `example.com`, you could edit your
[DNS] so that your **docassemble** server runs on a subdomain of
`example.com`, such as `interviews.example.com`.

Another way that a browser can be persuaded to allow an [iframe] is if
the browser's history includes a visit to the **docassemble** site.
This indicates to the browser that the user has consented to receive
content from the **docassemble** server.  For example, when a host
site on `example.com` tries to show the user an [iframe] with content
from `legalinterviewbot.com`, the browser will consult the user's
browser history, see that the user once visited a page on
`legalinterviewbot.com`, so it will conclude that it is safe to show
the content to the user.

One way to establish this browser history is to have a link on your
host site that points to an HTML file on your **docassemble** site,
which then redirects the user back to your host site.  This HTML file
can be hosted from the "static" folder of one of your packages.  For
example, if your package name is `docassemble.missouri`, and the file
name is `start.html`, you can point the users to the path
`/packagestatic/docassemble.missouri/start.html` on your
**docassemble** server.  The content of the HTML could be something
like:

{% highlight html %}
<!DOCTYPE html>
<html>
    <head>
        <title>Redirecting...</title>
        <meta http-equiv="refresh" content="1; url = https://example.com/custody/interview.html" />
    </head>
    <body>
        <p>Starting your interview on example.com...</p>
    </body>
</html>
{% endhighlight %}

Another way to redirect the user is to run some [JavaScript] like:

{% highlight javascript %}
window.location = "https://example.com/custody.interview.html";
{% endhighlight %}

Different browsers protect user privacy in different ways.  Some users
may have installed plug-ins that interfere with [iframe] embedding.
The way that browsers behave is usually not well-documented, and it
can change at any time.  Thus, the most stable solution to any future
cross-site scripting problems you might encounter is to make the host
site act as a proxy for the **docassemble** server, following the
model discussed in the section on [installing on a machine already
using a web server].  Unfortunately, this is a fairly complex set-up,
and it may not be possible to configure this set-up on all sites.

## <a name="div"></a>Embedding the interview into a web page directly

A **docassemble** interview can be embedded into a `<div>` element in
a page of another web site, provided that the web page loads the
resources that **docassemble** needs.  This takes more care and setup
than [using an iframe] because you need to reconcile the [CSS] and
[JavaScript] that **docassemble** needs with the [CSS] and
[JavaScript] already contained within the host web site.

The [Drupal module] and [WordPress plugin] both support embedding
interviews into `<div>` elements.

**docassemble** depends on the [CSS] classes of [Bootstrap 5] being
defined.  Your site's [CSS] should be loaded after the [CSS] needed by
**docassemble**, so that it overrides the **docassemble** [CSS] rules.
(The [Drupal module] and [WordPress plugin] are configured to do
this.)  The [CSS] of your site will thus affect the styling of the
**docassemble** interview.  This is generally a good thing because you
will probably want the interview to have the same look-and-feel as
your site.  However, some of the changes that your site's [CSS] will
make to the look-and-feel of your interview will not be desirable.
For example, you might see excessive padding between form fields.  You
will likely need to make edits to your site's [CSS] to adjust these
parameters.

Another complication is that **docassemble** requires [jQuery].  There
might be problems due to incompatible versions of [jQuery].
**docassemble** also requires a number of other [JavaScript]
libraries.  These libraries will probably not have an effect on your
site, but it is possible that they will.

To get started with embedding **docassemble** into a web page (if you
aren't using the [Drupal module] or the [WordPress plugin]), log in to
your **docassemble** server as an administrator or developer, then
navigate to `/test_embed`.  You will see your default interview there,
inside of a box.  Do "View Source" in your browser to see how it
works.  Here is an example of what the source will look like on a
server with the URL `https://interview.example.com`:

{% highlight html %}
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="https://interview.example.com/favicon.ico">
    <link rel="apple-touch-icon" sizes="180x180" href="https://interview.example.com/apple-touch-icon.png">
    <link rel="icon" type="image/png" href="https://interview.example.com/favicon-32x32.png" sizes="32x32">
    <link rel="icon" type="image/png" href="https://interview.example.com/favicon-16x16.png" sizes="16x16">
    <link rel="manifest" href="https://interview.example.com/manifest.json">
    <link rel="mask-icon" href="https://interview.example.com/safari-pinned-tab.svg" color="#698aa7">
    <meta name="theme-color" content="#83b3dd">
    <script defer src="https://interview.example.com/static/fontawesome/js/all.js"></script>
    <link href="https://interview.example.com/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://interview.example.com/static/app/bundle.css" rel="stylesheet">
    <title>Embed test</title>
  </head>
  <body>
    <div>
      <p>Here is some content before the interview.</p>
    </div>
    <div style="width: 100%; padding: 40px">
      <div id="dablock" class="dabody dajs-embedded dahide-navbar" style="width: 100%; height: 80vh; border-style: solid; border-width: 1px; border-color: #777">
      </div>
    </div>
    <div>
      <p>Here is some content after the interview.
    </div>

    <script src="https://interview.example.com/static/app/bundle.js"></script>
    <script src="https://maps.googleapis.com/maps/api/js?key=egsdSdgER344tuTYUgsdDErEdx34res2e44sdrg&libraries=places"></script>
    <script src="https://interview.example.com/interview?js_target=dablock&i=docassemble.base%3Adata%2Fquestions%2Fdefault-interview.yml"></script>
  </body>
</html>
{% endhighlight %}

The idea behind `/test_embed` is that you can selectively copy and
paste its source code into another web site in order to embed a
**docassemble** interview into that web site.

Notice that the last `<script>` is a call to `/interview`, which is
the standard endpoint for a **docassemble** interview.  (You can pass
a URL parameter `i` to `/test_embed` to indicate a different interview
to be used here.)  The `/interview` URL contains `&js_target=dablock`.
This indicates that instead of returning HTML, the endpoint should
return [JavaScript].  The value of the parameter is `dablock`, which
is the `id` attribute of a `<div>` on the page.  The [JavaScript],
when run, will load the **docassemble** interview into the `<div>`
designated with `id="dablock"`.

A **docassemble** interview will only be styled correctly if the
appropriate [CSS] resources are present, and the [JavaScript] code
loaded through the call to `/interview` will only work if other
[JavaScript] resources, such as [jQuery] and the [jQuery Validation
Plugin], are loaded.

Thus, you will need to edit your web site to make sure that all of the
necessary [CSS] and [JavaScript] resources are loaded.

The lines beginning with `<link rel=` and `<meta` are probably not
necessary for you to include; most of them relate to [favicon] setup,
and your site may have its own [favicon] that you want to use.
However, these lines may be important if your site does not already
have similar lines in its header:

{% highlight html %}
    <meta charset="utf-8">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
{% endhighlight %}

These lines can have an effect on how your interview looks on a mobile
device.

You can use a different `id` than `dablock` as long as you are
consistent between the `id` of the `<div>` and your `js_target=`
URL parameter in the `<script>` that uses the `/interview` endpoint.
You can position the `<div>` wherever you want, but you will want to
make sure you give it an appropriate height and width.  You will also
want to make sure that you use appropriate [CSS] so that the interview
works well on devices of all sizes.

Note that with the exception of [Font Awesome], [Bootstrap], the
Google Maps API, and the [JavaScript] that launches the interview
using a request to `/interview`, all of the [CSS] and [JavaScript]
dependencies of **docassemble** are combined into the files
`bundle.css` and `bundle.js`.  If you want, you can un-bundle these.

The [CSS] files, unbundled, would be:

{% highlight html %}
    <link href="https://interview.example.com/static/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://interview.example.com/static/bootstrap-fileinput/css/fileinput.min.css" rel="stylesheet">
    <link href="https://interview.example.com/static/labelauty/source/jquery-labelauty.css" rel="stylesheet">
    <link href="https://interview.example.com/static/bootstrap-combobox/css/bootstrap-combobox.css" rel="stylesheet">
    <link href="https://interview.example.com/static/bootstrap-slider/dist/css/bootstrap-slider.css" rel="stylesheet">
    <link href="https://interview.example.com/static/app/app.css" rel="stylesheet">
{% endhighlight %}

The [JavaScript] files, unbundled, would be:

{% highlight html %}
    <script src="https://interview.example.com/static/app/jquery.min.js"></script>
    <script src="https://interview.example.com/static/app/jquery.validate.min.js"></script>
    <script src="https://interview.example.com/static/app/additional-methods.min.js"></script>
    <script src="https://interview.example.com/static/popper/umd/popper.min.js"></script>
    <script src="https://interview.example.com/static/popper/umd/tooltip.min.js"></script>
    <script src="https://interview.example.com/static/bootstrap/js/bootstrap.min.js"></script>
    <script src="https://interview.example.com/static/bootstrap-slider/dist/bootstrap-slider.js"></script>
    <script src="https://interview.example.com/static/bootstrap-fileinput/js/fileinput.js"></script>
    <script src="https://interview.example.com/static/bootstrap-fileinput/themes/fas/theme.min.js"></script>
    <script src="https://interview.example.com/static/app/app.js"></script>
    <script src="https://interview.example.com/static/app/socket.io.min.js"></script>
    <script src="https://interview.example.com/static/labelauty/source/jquery-labelauty.js"></script>
    <script src="https://interview.example.com/static/bootstrap-combobox/js/bootstrap-combobox.js"></script>
{% endhighlight %}

If you want to load all of the [JavaScript] dependencies except for
[jQuery], use the following:

{% highlight html %}
    <script src="https://interview.example.com/static/app/bundlenojquery.js"></script>
{% endhighlight %}

Another complication of embedding is avoidance of problems with
[CORS].  Problems with [CORS] were discussed in the previous section
on [using an iframe], and these problems are even more likely to arise
when embedding in a `<div>`.

To get around these problems, set [`cross site domains`] in your
[Configuration] to the URL of your site:

{% highlight yaml %}
allow embedding: True
cross site domains:
  - https://example.com
{% endhighlight %}

Also set the [`allow embedding`] directive in the [Configuration] to
`True`, so that cross-site cookie sharing is allowed.

{% highlight yaml %}
allow embedding: True
{% endhighlight %}

Even after you set [`cross site domains`] and [`allow embedding`],
some browsers, such as Firefox, may still block the content if the
top-level domain of the host server is different from the top-level
domain of the **docassemble** server.  Thus, if your host web site is
example.com, you should run your **docassemble** server on a subdomain
of example.com, such as interviews.example.com.

If you still encounter problems on some browsers, consider setting up
your host server to act as a proxy, following the model discussed in
the subsection on [installing on a machine already using a web
server].

## <a name="reset"></a>Starting an interview from the beginning

The **docassemble** web application uses browser cookies to keep track
of the user's current interview session.  If the user starts an
interview, then navigates to a different page, and then navigates to
`/interview` on the **docassemble** site with an `i` parameter that is
the same as the `i` parameter of the interview they were using before,
the user will resume where they had left off in their existing
session.

<a name="new_session"></a>If you want to be able to provide your users
with a URL that always starts a fresh interview session, and will not
resume an existing session, include `&new_session=1` in the URL.
Whenever this link is clicked (or the [iframe] is drawn), the
interview will start at the beginning, even if the user had just been
in a session of the same interview.  The prior session, if any, is
preserved.

If you add `&reset=1` to the end of an `/interview` URL, this will
have the same effect as `&new_session=1`, but if the user had just
been in a session with the same interview, that session will be
deleted.  In this cirumstance, adding `&reset=1` is like a "restart"
operation.

For other session restarting options, see the `'restart'` and
`'new_session'` options for the [`url_of()`] and [`command()`]
functions, and the `restart` and `new_session` [special buttons].

<a name="from_list"></a>If the user has been in an interview session
and then navigates to a different interview, the user will see an
informational message at the top of the screen such as:

* Starting a new interview.  To go back to your previous interview, go
to My Interviews on the menu.
* Starting a new interview.  To go back to your previous interview, log
in to see a list of your interviews.
* Entering a different interview.  To go back to your previous
interview, go to My Interviews on the menu.
* Entering a different interview.  To go back to your previous
interview, log in to see a list of your interviews.

This message is not shown when the user starts an interview session by
clicking a link on the My Interviews page. The informational message
is suppressed by the inclusion of `&from_list=1` in the URL parameters
of the link.

## <a name="resume"></a>Resuming an interview with a POST request

If you do not want your users' browsers to pass a session ID as a URL
parameter (`session`) to a [GET] request to `/interview`, you can
cause the user's browser to send a [POST] request to `/resume` with
the following parameters:

* `i` containing the name of the interview (e.g.,
  `docassemble.mypackage:data/questions/myinterview.yml`)
* `session` containing the session ID of the session.

The server will respond with a 302 redirect to `/interview`.  All
parameters that you pass to [POST], except for `session`, will become
URL parameters of the [GET] request that the browser will send after
the redirect.  Thus you can set [`url_args`] using the parameters of
the [POST] request to `/resume`.

# <a name="howstored"></a>How answers are stored

When a user starts a new interview session, a new "variable store" or
set of "interview answers" is created.  The interview answers are
stored in a [Python dictionary] containing the names of the variables
that get defined during the course of the interview, such as
`favorite_animal` in the example interview above.  This dictionary is
saved in **docassemble**'s database.

Because this [Python dictionary] can contain data structures and
complicated [Python objects], before it can be saved in a database, it
needs to "frozen" into a form that can be stored in a database and
then "thawed" later.  The method that **docassemble** uses to "freeze"
and "thaw" the interview answers is [Python]'s [pickle] method.

**docassemble** keeps a snapshot of the interview answers for every
step of the session.  If the user presses the back button,
**docassemble** will restore the variable store to the next earliest
version.  This has the effect of an "undo," and there is no "redo"
button.

Since the back button performs a permanent "undo," you should not
encourage your end users to click the "Back" button as a means of
changing past answers.  Instead, you should provide [review screens]
where users can quickly find the answer they want to change, and
change it without losing their work.

Since the interview answers are stored in a [Python] data structure
that can contain [Python objects], you have a great deal of
flexibility in how you can structure the information you collect.
This also means that the interview answers cannot easily be reduced to
a spreadsheet the way that the results of a [Google Form] can be.  If
you want to be able to store a session's interview answers in a
spreadsheet form, you can write [Python] code to do so.  There are
also some helpful [Objects] and [Functions] that you can use, such as
the [`DAStore`] object, the [`SQLObject`], and the [`write_record()`]
function.

# <a name="comingback"></a>Leaving an interview and coming back

If the user is not logged in through **docassemble**'s
[username and password system], then the user's progress through an
interview will be lost if the web browser is closed.

If the user is logged in, however, then when the user logs in again,
the user will be able to resume the interview where he left off.

If a new user starts an interview without being logged in, and then
clicks the "Sign in or sign up to save answers" link to log in, and
then clicks the link to register, the user will immediately be
directed back to the interview they had been using, and they will
immediately pick up where they left off, the only difference being
that they are now logged in.

If a logged-in user leaves an interview without completing it, closes
their browser, then opens their browser at a later time, and visits
the interview link again, they will start a new session for the
interview indicated by the `i` parameter.  If they then log in using
the menu in the corner, they will be directed to the `/interviews`
page, where they will see two interview sessions listed, including
their original session and the session they just started.

If your users will only ever need to use a single session of an
interview, you might want to change the code of your interview so that
they have a different experience.  For example, you might want to
start your interview with a multiple-choice question that asks the
user if they are a new user or a returning user.  If they are a
returning user.

{% highlight yaml %}
question: |
  Are you here for the first time, or returning?
field: user_new_or_returning
buttons:
  - First time: new
  - Returning: returning
---
mandatory: True
code: |
  if user_new_or_returning == 'returning':
    command('exit', url=url_of('login'))
{% endhighlight %}

Running [`command()`] with `'exit'` deletes the current interview
session.  The `url` keyword parameter redirects the user to a
particular page.  The function [`url_of()`] with the parameter
`'login'` returns the URL for the **docassemble** login page.

For other exiting options, see the `'exit'`, `'leave'`, `'logout'`, and
`'exit_logout'` options for the [`url_of()`] and [`command()`]
functions.

# <a name="jinja2"></a>Using Jinja2 templating to build the YAML of an interview

When specifying the [YAML] of an interview, you have the option of
using [Jinja2] templating to construct your [YAML].  The vast majority
of **docassemble** developers will not need to do this, so this should
be considered an advanced feature.

By default, interview YAML files are not processed with [Jinja2].  To
turn on [Jinja2] processing, add `# use jinja` to the very first line
of a [YAML] file.  (This needs to be written exactly this way on the
first line.)

{% include demo-side-by-side.html demo="jinjayaml" %}

This example demonstrates the use of the `include` command.  The
`jinjayaml-included.yml` file is located in the same directory as the
YAML file.  Its contents are:

{% highlight yaml %}
question: |
  What is your favorite fruit?
fields:
  - Fruit: favorite_fruit
---
{% endhighlight %}

In this context, the [Jinja2] `include` command acts much like the
**docassemble** [`include` block].  However, the [Jinja2] command can
do things that the [`include` block] cannot do; for example, you can
set the contents of a [YAML] file to be a partial block, such as a
list of `fields`, and then include that file in the middle of one or
more `question` blocks.

Note that all that [Jinja2] does is take [YAML] and convert it to
[YAML].  The way that [Jinja2] is used in this context is very
different from the way that [Mako] is used inside [Markdown] text or
the way that [Jinja2] is used to assemble [DOCX documents]. For
example, you cannot run **docassemble** [functions] or refer to
variables in the interview answers.  The [YAML] is processed by
[Jinja2] when the interview is first loaded into the memory of the web
server process.  [Jinja2] functions as a preprocessor only; it cannot
be used to make dynamic changes to the way an interview works.

In the above example, the [Jinja2] `include` directive was used to
include a file in the "questions" folder of the same package.  If you
want to refer to a file in another package, you can write a complete
filename such as `docassemble.missouri:data/questions/toinclude.yml`.

The following variables are available in the [Jinja2] context:

  * `__config__`: the [Configuration] of the server, as a Python `dict`.
  * `__version__`: the current version of **docassemble** installed on
    the server.
  * `__architecture__`: the value returned by `platform.machine()` (e.g., `'x86_64'`).
  * `__filename__`: the name of the [YAML] file for which [Jinja2] was invoked.
  * `__current_package__`: the package containing the [YAML] file for which [Jinja2] was invoked.
  * `__interview_filename__`: the name of the [YAML] file that was
    invoked to run the current interview.
  * `__interview_package__`: the package containing the [YAML] file that was
    invoked to run the current interview.
  * `__parent_filename__`: if the current [YAML] file (`__filename__`)
    was included through an [`include` block], `__parent_filename__`
    will contain the name of the [YAML] file that contained the
    [`include` block].  Otherwise, `__parent_filename__` will be the
    same as `__interview_filename__`.
  * `__parent_package__`: the package containing `__parent_filename`.
  * `__debug__`: the value of the [`debug`] Configuration directive (the
    default is `True`.
  * `__hostname__`: the value of the [`external hostname`] Configuration
    directive (the default is `localhost`).

In addition, you can make variables available in the [Jinja2] context on
your server by setting the [`jinja data`] directive in your
[Configuration].  For example:

{% highlight yaml %}
jinja data:
  verbosity: 2
  region: Delaware
{% endhighlight %}

This will make the variables `verbosity` and `region` available for
use in [Jinja2] directives.

Note that the variables passed to [Jinja2] are fixed at the time that
[Jinja2] is invoked.  For example, if you use the [Jinja2] `include`
directive, the `__filename__` will not be the filename of the included
file; it will continue to be whatever it was when the [YAML] filename
containing `# use jinja` was encountered.

[`include` block]: {{ site.baseurl }}/docs/initial.html#include
[`jinja data`]: {{ site.baseurl }}/docs/config.html#jinja data
[Configuration]: {{ site.baseurl }}/docs/config.html
[functions]: {{ site.baseurl }}/docs/functions.html
[DOCX documents]: {{ site.baseurl }}/docs/documents.html#docx template file
[Markdown]: https://daringfireball.net/projects/markdown/
[Mako]: https://www.makotemplates.org/
[YAML specification]: https://yaml.org/spec/1.2.2/
[if/else statements]: {{ site.baseurl }}/docs/code.html#if
[graphical user interface]: https://en.wikipedia.org/wiki/Graphical_user_interface
[GitHub]: https://github.com/
[package]: {{ site.baseurl }}/docs/packages.html
[packages]: {{ site.baseurl }}/docs/packages.html
[playground]: {{ site.baseurl }}/docs/playground.html
[demonstration page]: {{ site.baseurl }}/demo.html
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[Python]: https://www.python.org/
[Initial Blocks]: {{ site.baseurl }}/docs/initial.html
[Question Blocks]: {{ site.baseurl }}/docs/questions.html
[questions]: {{ site.baseurl }}/docs/questions.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[Question Modifiers]: {{ site.baseurl }}/docs/modifiers.html
[Code]: {{ site.baseurl }}/docs/code.html
[Interview Logic]: {{ site.baseurl }}/docs/logic.html
[Objects]: {{ site.baseurl }}/docs/objects.html
[Groups]: {{ site.baseurl }}/docs/groups.html
[Markup]: {{ site.baseurl }}/docs/markup.html
[Functions]: {{ site.baseurl }}/docs/functions.html
[Documents]: {{ site.baseurl }}/docs/documents.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[Roles]: {{ site.baseurl }}/docs/roles.html
[Errors]: {{ site.baseurl }}/docs/errors.html
[username and password system]: {{ site.baseurl }}/docs/users.html
[Python dictionary]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[JSON]: https://en.wikipedia.org/wiki/JSON
[Special Variables]: {{ site.baseurl }}/docs/special.html
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[`default interview`]: {{ site.baseurl }}/docs/config.html#default interview
[embedded]: {{ site.baseurl }}/docs/config.html#dispatch
[list of interviews]: {{ site.baseurl }}/docs/config.html#dispatch
[demo interview]: {{ site.baseurl }}/demo.html
[iframe]: https://www.w3schools.com/TAgs/tag_iframe.asp
[HTML]: https://en.wikipedia.org/wiki/HTML
[`go full screen`]: {{ site.baseurl }}/docs/initial.html#go full screen
[`dispatch interview`]: {{ site.baseurl }}/docs/config.html#dispatch interview
[`interview_menu()`]: {{ site.baseurl }}/docs/functions.html#interview_menu
[`menu_items` special variable]: {{ site.baseurl }}/docs/special.html#menu_items
[configured otherwise]: {{ site.baseurl }}/docs/config.html#session list interview
[`root redirect url`]: {{ site.baseurl }}/docs/config.html#root redirect url
[`command()`]: {{ site.baseurl }}/docs/functions.html#command
[`url_of()`]: {{ site.baseurl }}/docs/functions.html#url_of
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
[configurable]: {{ site.baseurl }}/docs/config.html#customization
[`show dispatch link`]: {{ site.baseurl }}/docs/config.html#show dispatch link
[special buttons]: {{ site.baseurl }}/docs/questions.html#special buttons
[Legal Applications]: {{ site.baseurl }}/docs/legal.html
[`interview_url()`]: {{ site.baseurl }}/docs/functions.html#interview_url
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[jQuery]: https://jquery.com/
[jQuery Validation Plugin]: https://jqueryvalidation.org/maxlength-method
[using an iframe]: #iframe
[Bootstrap 5]: https://getbootstrap.com/
[Bootstrap]: https://getbootstrap.com/
[Ajax]: https://en.wikipedia.org/wiki/Ajax_(programming)
[favicon]: https://en.wikipedia.org/wiki/Favicon
[Font Awesome]: https://fontawesome.com
[jQuery]: https://jquery.com/
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[CORS]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`cross site domains`]: {{ site.baseurl }}/docs/config.html#cross site domain
[GET]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
[POST]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
[`url_args`]: {{ site.baseurl }}/docs/special.html#url_args
[pickle]: https://docs.python.org/3.12/library/pickle.html
[review screens]: {{ site.baseurl }}/docs/fields.html#review
[Python objects]: https://docs.python.org/3/tutorial/classes.html
[Google Form]: https://www.google.com/forms/about/
[`DAStore`]: {{ site.baseurl }}/docs/objects.html#DAStore
[`write_record()`]: {{ site.baseurl }}/docs/functions.html#write_record
[development overview]: {{ site.baseurl }}/docs/development.html
[section on YAML]: #yaml
[how answers are stored]: #howstored
[Drupal module]: https://github.com/jhpyle/docassemble_embed
[WordPress plugin]: https://github.com/jhpyle/docassemble-embedder
[installing on a machine already using a web server]: {{ site.baseurl }}/docs/docker.html#forwarding
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
[`SQLObject`]: {{ site.baseurl }}/docs/objects.html#SQLObject
[`allow embedding`]: {{ site.baseurl }}/docs/config.html#allow embedding
[Jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
[`debug`]: {{ site.baseurl }}/docs/config.html#debug
[`external hostname`]: {{ site.baseurl }}/docs/config.html#external hostname
