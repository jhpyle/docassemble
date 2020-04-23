---
layout: docs
title: Initial blocks
short_title: Initial Blocks
---

This section discusses blocks that will typically appear at the
beginning of the [YAML] of your [interview].

If you are new to **docassemble**, you probably will not need to use
"initial blocks" until you attempt something more advanced, so you can
skip this section and proceed to the [section on questions].

# <a name="metadata"></a>Interview title and other `metadata`

{% highlight yaml %}
---
metadata:
  title: |
    Advice on Divorce
  short title: |
    Divorce
  description: |
    A divorce advice interview
  authors:
    - name: John Doe
      organization: Example, Inc.
  revision_date: 2015-09-28
---
{% endhighlight %}

A `metadata` block contains information about the interview, such as
the name of the author.  It must be a [YAML] dictionary, but each the
dictionary items can contain any arbitrary [YAML] structure.

<a name="title"></a>If a `title` is defined, it will be displayed in
the navigation bar in the web app.  If a `short title` is provided, it
will be displayed in place of the `title` when the size of the screen
is small.

<a name="logo"></a>If a `logo` is defined, it will be displayed in the
navigation bar in the web app in place of the `title` and `short
title`.  The content of the `logo` should be raw [HTML].  If you
include an image, you should size it to be about 20 pixels in height.

<a name="tab title"></a>If a `tab title` is provided, it will be
displayed as the title of the browser tab.  Otherwise, the `title`
will be used.

<a name="subtitle"></a>If a `subtitle` is provided, it will be
displayed as the subtitle of the interview in the "Interviews" list
available to a logged-in user at `/interviews`.

<a name="title url"></a>If a `title url` is provided, clicking on the
title will open the given URL.  Otherwise, the default behavior is
that clicking the title does nothing except that when the user is on a
help screen, clicking the title takes the user back to the question.

<a name="title url opens in other window"></a>If you provide a `title
url` and you do not want the URL to open in another browser window or
tab, set `title url opens in other window` to `False`.  The default is
that the link does open another window or tab.

<a name="date format"></a>If a `date format` is provided, this will be
used as the default date format when the [`format_date()`] function is
called, or the [`.format_date()`] method of the [`DADateTime`] object
is called (which is used when [`DADateTime`] objects are reduced to
text).

<a name="datetime format"></a>If a `datetime format` is provided, this
will be used as the default date/time format when the
[`format_datetime()`] function is called, or the
[`.format_datetime()`] method of the [`DADateTime`] object is called.

<a name="time format"></a>If a `time format` is provided, this will be
used as the default time format when the [`format_time()`] function is
called, or the [`.format_time()`] method of the [`DADateTime`] object
is called.

These values can be overridden using the [`set_parts()` function].

The `metadata` block and the [`set_parts()` function] can be used to
modify other aspects of the navigation bar.

<a name="exit link"></a>If an `exit link` is provided, the behavior of
the "Exit" link can be modified.  (The "Exit" menu option is displayed
when the [`show login` configuration directive] is set to `False` or
the [`show login` metadata specifier] in an interview is set to
`False`.)  The value can be either `exit`, `leave,` or `logout`.  If
it is `exit`, then when the user clicks the link, they will be logged
out (if they are logged in) and their interview answers will be
deleted from the server.  If it is `leave`, the user will be logged
out (if they are logged in), but the interview answers will not be
deleted from the server.  (It can be important to keep the interview
answers on the server if [background tasks] are still running.)  If it
is `logout`, then if the user is logged in, the user will be logged
out, but if the user is not logged in, this will have the same effect
as `leave`.

<a name="exit url"></a>If an `exit url` is provided, the user will be
redirected to the given URL.  If no `exit url` is provided, the user
will be directed to the [`exitpage`] if the `exit link` is `exit` or
`leave`, and directed to the login page if the user is logged in and
`exit link` is `logout`.  The `exit url` also functions as an
interview-level default value in place of the system-wide
[`exitpage`], which is used by the [`command()`] function and used on
[special pages] that show `buttons` or `choices` that allows users to
`exit` or `leave`.

<a name="exit label"></a>If `exit label` is provided, the given text
will be used in place of the word "Exit" on the "Exit" menu option.
This text is passed through the [`word()`] function, so that it can be
translated into different languages.

<a name="unlisted"></a>If you set `unlisted: True` for an interview
that has an entry in the [`dispatch`] list in your [configuration],
the interview will be exempted from display in the list of interviews
available at `/list`.  For more information about this, see the
documentation for the [`dispatch`] configuration directive.

<a name="hidden"></a>If you set `hidden: True`, then interview
sessions for this interview will be omitted from the "My Interviews"
listing of sessions.  (They will still be deleted by the "Delete All"
button, though.)

<a name="tags"></a>You can set `tags` to a list of one or more "tags"
as a way of categorizing the interview.

{% highlight yaml %}
metadata:
  title: Write your will
  tags:
    - estates
    - wills
{% endhighlight %}

The list of available interviews at `/list` and the list of interview
sessions at `/interviews` make use of the metadata `tags` for
filtering purposes.  Note that the `metadata` of an interview are
static, while the tags of a particular session of an interview are
dynamic, and can be changed with [`session_tags()`].

<a name="sessions are unique"></a>If you set `sessions are unique` to
`True`, then **docassemble** will resume an existing session for the
user, if the user already has an existing session.  This requires that
the user be logged in, so the user will be redirected to the login
screen if they try to access an interview for which `sessions are
unique` is set to `True`.  You can also set `sessions are unique` to a
list of roles, in which case uniqueness will be enforced only if the
user has one of the listed roles.

<a name="required privileges"></a>If you set `required privileges` to
a list of one or more privileges, then a user will only be able to use
the interview if they have one of the given privileges.  If
`anonymous` is included as one of the required privileges, then users
who are not logged in will be able to use the interview.  However,
note that `anonymous` is not actually a [privilege] in
**docassemble**'s [privilege] management system; only logged-in users
actually have [privileges].  If no `required privileges` are listed,
then the default is that the interview can be used by anybody.

{% highlight yaml %}
metadata:
  title: Administrative interview
  short title: Admin
  description: |
    A management dashboard
  sessions are unique: True
  required privileges:
    - admin
    - developer
    - advocate
{% endhighlight %}

If there are multiple [`metadata`] blocks in the [YAML] of an
interview that set `required privileges`, the `required privileges`
settings of later [`metadata`] blocks will override the `required
privileges` settings of earlier [`metadata`] blocks.  Setting
`required privileges: []` will ensure that the interview can be used,
notwithstanding the `required privileges` settings of any earlier
[`metadata`] blocks.

<a name="required privileges for listing"></a>The `required privileges
for listing` metadata specifier is like `required privileges`, except
it only controls whether the interview will be shown in the list of
interviews available at `/list`.  The `required privileges` metadata
specifier also controls whether the interview will be listed.  For
more information about the `/list` page, see the documentation for the
[`dispatch`] configuration directive.

<a name="error action"></a>You can set an `error action` if you want
your interview to do something substantive in the event that your
interview encounters an error that it would otherwise show to the
user.

A simple application of `error action` would be to replace the error
screen with a [`question`]:

{% include side-by-side.html demo="error-action" %}

When the interview encounters an error, the interview will run the
[action] given by `error action`.  In this case, `error action` is
`on_error`, and calling this [action] shows a [`question`] to the
user.

An [action] can also run code that changes the interview logic.  For
example, an `error action` could skip through the remainder of the
questions and present a final screen:

{% include side-by-side.html demo="error-action-2" %}

If the attempt to run the error action also results in an error, the
latter error is shown on the screen in the usual fashion.

See [`error help`] and [`verbose error messages`] for other ways to
customize error messages.

<a name="pre"></a><a name="submit"></a><a name="post"></a>The
[`metadata`] block also accepts specifiers for default content to be
inserted into various parts of the screen.

{% include side-by-side.html demo="metadata-screen-parts" %}

You can provide different values for different languages by setting
each directive to a dictionary in which the keys are languages and the
values are content.

{% highlight yaml %}
metadata:
  post:
    en: |
      This interview was sponsored in part by a grant from the Example Foundation.
    es: |
      Esta entrevista fue patrocinada en parte por una beca de la Fundación Ejemplo.
{% endhighlight %}

For information about other ways to set defaults for different parts
of the screens during interviews, see the [screen parts] section.

<a name="error help">The [`metadata`] block also accepts the specifier
`error help`.  This is [Markdown]-formatted text that will be included
on any error screen that appears to the user during the interview.
You can also provide this text on a server-wide basis using the
[`error help`] directive in the [Configuration].

{% include side-by-side.html demo="error-help" %}

To support multiple languages, you can set `error help` to a
dictionary where the keys are language codes and the values are the
error text to be shown:

{% include side-by-side.html demo="error-help-language" %}

This will not always be reliable, because an error might happen before
the user's language is known.

<a name="show login">The [`metadata`] block also accepts the specifier
`show login`, which can be `true` or `false`.  This controls whether
the user sees a "Sign in or sign up to save answers" link in the upper
right-hand corner during the interview.  If `show login` is not
specified in the [`metadata`], the [Configuration] directive [`show
login`] determines whether this link is available.

{% include side-by-side.html demo="show-login" %}

<a name="suppress loading util"></a>By default, all of the functions
and classes of [`docassemble.base.util`] are imported into the
namespace of a **docassemble** interview.  If you want to load names
manually using a [`modules`] block, you can set `suppress loading
util` to `True`:

{% highlight yaml %}
metadata:
  suppress loading util: True
{% endhighlight %}

If `suppress loading util` is `True`, the only name that will be
imported into your interview is [`process_action`].

<a name="social"></a>You can control the [meta tags] returned by an
interview by setting `social`.

{% include side-by-side.html demo="social" %}

This results in the following [HTML] inside of the `<head>` tag:

{% highlight html %}
<meta name="image" content="https://demo.docassemble.org/packagestatic/docassemble.base/court.png?v=1.1.5">
<meta name="description" content="A demonstration of meta tags.">
<meta itemprop="description" content="A demonstration of meta tags.">
<meta itemprop="image" content="https://demo.docassemble.org/packagestatic/docassemble.base/court.png?v=1.1.5">
<meta itemprop="name" content="Social meta tags">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="Social meta tag demo">
<meta name="twitter:site" content="@docassemble">
<meta name="twitter:description" content="An interview that demonstrates meta tags.">
<meta name="twitter:image" content="https://docassemble.org/img/docassemble-logo-sq-125.jpg">
<meta name="twitter:image:alt" content="Docassemble logo">
<meta name="og:image" content="https://demo.docassemble.org/packagestatic/docassemble.demo/crown.png?v=1.1.5">
<meta name="og:description" content="A one-page guided interview demonstrating meta tags.">
<meta name="og:title" content="Social meta tags">
<meta name="og:url" content="https://demo.docassemble.org/interview?i=docassemble.base%3Adata%2Fquestions%2Fexamples%2Fsocial.yml">
<meta name="og:site_name" content="docassemble">
<meta name="og:locale" content="en_US">
<meta name="og:type" content="website">
{% endhighlight %}

In this example, the **docassemble** server is
`https://demo.docassemble.org`, the version of the `docassemble.demo`
package is 1.1.5, the [`brandname`] of the server is `docassemble`,
and the [`locale`] of the server is `en_US.utf8`.

The `image` references are special because if you set them to a
reference to a static file, they will be replaced with a full URL to
that file.  Alternatively, you can provide a full URL.  The example
contains references to a file within the same package (`court.png`), a
file in a different package
(`docassemble.demo:data/static/crown.png`), and an external URL
(`https://docassemble.org/img/docassemble-logo-sq-125.jpg`).

Note that the `itemprop="name"`, `twitter: title`, and `og:title` are
all set to the `title` of the page.  This can be overridden by setting
the top-level `name`, `title` under `twitter`, and `title` under `og`.

By default, `twitter:card` is set to `summary`, `og:url` is set to the
URL for the interview, `og:site_name` is set to the value of
[`brandname`], `og:locale` is determined from the [`locale`], and
`og:type` is set to `website`.  These defaults can be specifically
overridden.

Server-wide default values for [meta tags] can be set using the
[`social`] Configuration directive.

Note that by default, the **docassemble** server disallows web
crawling by returning a restrictive `/robots.txt` file.  That means
that as a practical matter, sites will not be able to consume your
[meta tags].  The `/robots.txt` file can be customized using the
[`allow robots`] directive so that your [meta tags] are accessible.

<a name="example start"></a><a name="example start"></a>If you look at
example interviews that are used in the documentation, you will see
`example start` and `example end` in the `metadata`.  These indicate
the YAML blocks that should be excerpted and included in the
documentation.  There is a script in the [GitHub repository] called
`make-screenshots.sh`, which calls `get_yaml_from_example.py`, which
scans the [YAML] files in a directory and outputs [YAML] containing
the excerpts, which is then processed by the [Jekyll] documentation
site that is hosted on [GitHub Pages].

## <a name="overlapping metadata"></a>Effect of multiple `metadata` blocks

An interview can contain multiple metadata blocks.  Values in later
blocks override earlier blocks.  The values over later `metadata`
blocks are effectively superimposed on top of earlier `metadata`
blocks.

If you write [YAML] files to be [`include`]d into other interviews, it
is a best practice not to include [`metadata`] in [YAML] files that
will be included into other interviews.

# <a name="objects"></a>Creating `objects`

{% highlight yaml %}
---
objects:
  - spouse: Individual
  - user.case: Case
---
{% endhighlight %}

An `objects` block creates objects that may be referenced in your
interview.  See [objects] for more information about objects in
**docassemble**.

If your interview references the variable `spouse`, **docassemble**
will find the above `objects` block and process it.  It will define
`spouse` as an instance of the object class `Individual` and define
`user.case` as an instance of the object class `Case`.

The use of objects in **docassemble** interviews is highly encouraged.
However, the objects you use as variables need to inherit from the
class `DAObject`.  Otherwise, **docassemble** might not be able to
find the appopriate [`code` blocks] or questions necessary to define
them.  This is because of the way **docassemble** keeps track of the
names of variables.

A code block like this would effectively do the same thing as the
`objects` block above:

{% highlight yaml %}
---
code: |
  spouse = Individual('spouse')
  user.initializeAttribute('case', Case)
---
{% endhighlight %}

This code is more complicated than normal Python code for object
initialization because the full name of the variable needs to be
supplied to the function that creates and initializes the object.  The
base class [`DAObject`] keeps track of variable names.

In some situations, running `spouse = Individual()` will correctly
detect the variable name `spouse`, but in other situations, the name
cannot be detected.  Running `spouse = Individual('spouse')` will
always set the name correctly.

Whenever possible, you should use `objects` blocks rather than code to
initialize your objects because `objects` blocks are clean and
readable.

You can also use `objects` blocks to initialize attributes of the
objects you create.  For information on how to do this, see the
documentation for the [`using()`] method.

## <a name="objects from file"></a>Importing `objects from file`

{% highlight yaml %}
---
objects from file:
  - claims: claim_list.yml
---
{% endhighlight %}

An `objects from file` block imports objects or other data elements
that you define in a separate [YAML] or [JSON] data file located in
the [sources folder] of the current package.  If the interview file
containing the `objects from file` block is
`data/questions/manage_claims.yml`, **docassemble** will expect the
data file to be located at `data/sources/claim_list.yml`.

For more information about how this works, and about how to format the
data file, see the documentation for the
[`objects_from_file()` function].  The example above is equivalent to
running `claims = objects_from_file('claim_list.yml', name='claims')`.

If you set `use objects` to `True`, then the `use_objects` keyword
parameter of the [`objects_from_file()` function] will be used.

{% highlight yaml %}
---
use objects: True
objects from file:
  - claims: claim_list.yml
---
{% endhighlight %}

This is equivalent to running 
`claims = objects_from_file('claim_list.yml', name='claims', use_objects=True)`.

# <a name="include"></a>Incorporation by reference: `include`

{% highlight yaml %}
---
include:
  - basic-questions.yml
  - docassemble.helloworld:questions.yml
---
{% endhighlight %}

The `include` block incorporates the questions in another [YAML]
file, almost as if the contents of the other [YAML] file appeared in
place of the `include` block.  When the `include`d file is parsed,
files referenced within it will be assumed to be located in the
`include`d file's package.

When a filename is provided without a package name, **docassemble**
will look first in the `data/questions` directory of the current
package (i.e., the package within which the [YAML] file being read is
located), and then in the `data/questions` directory of
[`docassemble.base`].

You can include question files from other packages by explicitly
referring to their package names.  E.g.,
`docassemble.helloworld:questions.yml` refers to the file
`questions.yml` in the `docassemble/helloworld/data/questions`
directory of that package.

# <a name="im"></a>Images

## <a name="image sets"></a>With attribution: `image sets`

{% highlight yaml %}
---
image sets:
  freepik:
    attribution: |
      Icon made by [Freepik](http://www.flaticon.com/authors/freepik)
    images:
      baby: crawling.svg
      people: users6.svg
      injury: accident3.svg
---
{% endhighlight %}

An `image sets` block defines the names of icons that you can use to
decorate your questions.

The file names refer to files located in the `data/static` directory
of the package in which the [YAML] file is located.

Since most free icons available on the internet require attribution,
the `image sets` block allows you to specify what attribution text
to use for particular icons.  The web app shows the appropriate
attribution text at the bottom of any page that uses one of the
icons.  The example above is for a collection of icons obtained from
the web site Freepik, which offers free icons under an
attribution-only license.

The `image sets` block must be in the form of a [YAML] dictionary, where
the names are the names of collections of icons.  The collection
itself is also a dictionary containing terms `images` and (optionally)
an `attribution`.  The `images` collection is a dictionary that
assigns names to icon files, so that you can refer to icons by a name
of your choosing rather than by the name of the image file.

For information on how to use the icons you have defined in an `image
sets` block, see `decoration` in the [question modifiers] section, `buttons`
in the [setting variables] section, and "Inserting inline icons" in
the [markup] section.

## <a name="images"></a>Without attribution: `images`

{% highlight yaml %}
---
images:
  bills: money146.svg
  children: children2.svg
---
{% endhighlight %}

An `images` block is just like an `image sets` block, except that it
does not set any attribution information.  It is simpler because you
do not need to give a name to a "set" of images.

The above `images` block is essentially equivalent to writing:

{% highlight yaml %}
---
image sets:
  unspecified:
    images:
      bills: money146.svg
      children: children2.svg
---
{% endhighlight %}

# <a name="mods"></a>Python modules

## <a name="imports"></a>Importing the module itself: `imports`

{% highlight yaml %}
---
imports:
  - datetime
  - us
---
{% endhighlight %}

`imports` loads a Python module name into the namespace in which your
code and question templates are evaluated.  The example above is
equivalent to running the following Python code:

{% highlight python %}
import datetime
import us
{% endhighlight %}

## <a name="modules"></a>Importing all names in a module: `modules`

{% highlight yaml %}
---
modules:
  - datetime
---
{% endhighlight %}

Like `imports`, `modules` loads Python modules into the namespace in
which your code and question templates are evaluated, except that it
imports all of the names that the module exports.  The example above
is equivalent to running the following Python code:

{% highlight python %}
from datetime import *
{% endhighlight %}

# <a name="data"></a>Storing structured `data` in a variable

The `data` block allows you to specify a data structure in [YAML] in a
block and have it available as a [Python] data structure.

For example, in this interview we create a [Python] list and then
re-use it in two questions to offer a multiple-choice list.

{% include side-by-side.html demo="data-simple" %}

In [Python], the variable `fruits` is this:

{% highlight python %}
[u'Apple', u'Orange', u'Peach', u'Pear']
{% endhighlight %}

You can also use the `data` block to create more complex data
structures.  You can also use [Mako] in the data structure.

{% include side-by-side.html demo="data" %}

`data` blocks do not work the same way as [`template`] blocks.  The
[Mako] templating in a `data` block is evaluated at the time the
variable indicted by `variable name` is defined.  The text stored in
the data structure is the result of processing the [Mako] templating.
The [Mako] templating is not re-evaluated automatically each time a
[`question`] is shown.

You can also import data from [YAML] files using the
[`objects_from_file()` function].

## <a name="use objects"></a>Structured data in object form

If you set `use objects: True` in a [`data`] block, then lists in your
[YAML] will become [`DAList`]s in the resulting data structure, and
dictionaries in your [YAML] will become [`DADict`]s.  The `.gathered`
attribute of these objects will be set to `True`.

In addition, when `use objects: True` is enabled, any dictionaries in
the data structure will be transformed into a [`DAContext`] object if
the keys of the dictionary are a non-empty subset of `question`,
`document`, `docx`, `pdf`, and `pandoc`.

This is a useful shorthand for creating [`DAContext`] objects.  For
example:

{% include demo-side-by-side.html demo="context" %}

# <a name="data from code"></a>Storing structured `data` in a variable using code

The `data from code` block works just like the [`data`] block, except
that [Python] code is used instead of text or [Mako] markup.

{% include side-by-side.html demo="data-code" %}

## <a name="use objects from code"></a>Structured data from code in object form

The [`use objects`] modifier can also be used with `data from code`.

{% include demo-side-by-side.html demo="context-code" %}

# <a name="reset"></a>Keeping variables fresh: `reset`

The `reset` block will cause variables to be undefined every time a
screen loads.

This can be helpful in a situation where a variable is set by a
[`code` block] and the value of the variable ought to be considered
afresh based on the user's latest input.

{% highlight yaml %}
---
reset:
  - client_is_guilty
  - opposing_party_is_guilty
---
{% endhighlight %}

Effectively, this causes variables to act like functions.

Another way to use this feature is to set the [`reconsider` modifier]
on a [`code`] block.  This will have the same effect as `reset`, but
it will apply automatically to all of the variables that are capable
of being assigned by the [`code`] block.

The `reset` block and the [`reconsider` modifier] are computationally
inefficient because they cause extra code to be run every time a new
screen loads.  For a more computationally efficient alternative, see
the [`reconsider()`] function

# <a name="on change"></a>Running code when a variable changes: `on change`

If you allow users to go back and change their answers, you may
find situations where using [`depends on`] is not sufficient to
invalidate variables that depend on a variable that has been altered.

In this situation, you can write a block of [Python] code in an `on
change` block that will be executed when a variable is changed.

{% include side-by-side.html demo="on-change" %}

If the user finishes this interview and then changes his mind about
whether he is married (indicated by the variable `married`), this will
invalidate the answers to the questions about income.  If he had said
at the outset that he was married, the questions would have asked
about the income of both himself and his spouse.

Tagging the `income[i].amount` question with `depends on: married`
would not work because in the context of a change to `married`, the
variable `i` is not defined.

The `on change` block states explicitly what should be done if the
variable `married` changes: the `.amount` attributes should be
invalidated and the `income` list should be reopened for gathering.
Calling `income.reset_gathered()` with `mark_incomplete=True` will
undefine the `.complete` attributes on each of the income items.  This
is important because otherwise the existing items would still be
considered "complete," and thus the `.amount` attributes would not be
re-defined by the interview logic.

The `on change` specifier needs to point to a [YAML] dictionary in
which the keys are variable names and the values are [Python] code
that will be run when the given variable changes value.

The code is only run when the variable exists and is altered, not when
the variable is undefined and is then defined.

It is important that `on change` code runs to completion without
encountering any undefined variables.  It runs during a different part
of the screen loading process than other code.  The code runs before
[`modules`] and [`imports`] blocks have loaded (although the standard
**docassemble** functions from `docassemble.base.util`, such as
[`undefine()`] and [`invalidate()`], are available).  If you need to refer
to names from custom modules, bring them into the namespace manually
with a line like `from docassemble.missouri import MyObject`.

You can have more than one `on change` block in your interview.  If
more than one block refers to the same variable, all of the code
blocks will be run.  The code blocks will be run in the order in which
the blocks appear in the [YAML] file.

# <a name="order"></a>Changing order of precedence

As explained in [how **docassemble** finds questions for variables],
if there is more than one [`question`] or [`code`] block that offers
to define a particular variable, blocks that are later in the [YAML]
file will be tried first.

If you would like to specify the order of precedence of blocks in a
more explicit way, so that you can order the blocks in the [YAML] file
in whatever way you want, you can tag two or more blocks with [`id`]s
and insert an `order` block indicating the order of precedence of the
blocks.

For example, suppose you have an interview with two blocks that could
define the variable `favorite_fruit`.  Normally, **docassemble** will
try the the second block first because it appears later in the [YAML]
file; the second block will "override" the first.

{% include side-by-side.html demo="supersede-regular" %}

However, if you actually want the first block to be tried first, you
can manually specify the order of blocks:

{% include side-by-side.html demo="supersede-order" %}

Another way to override the order in which blocks will be tried is by
using the [`id` and `supersedes`] question modifiers.

# <a name="terms"></a><a name="auto terms"></a>Vocabulary `terms` and `auto terms`

Sometimes you will use vocabulary terms that the user may or may not
know.  Instead of interrupting the flow of your questions to define
every term, you can define certain vocabulary words, and
**docassemble** will turn them into hyperlinks wherever they appear in
curly brackets.  When the user clicks on the hyperlink, a popup
appears with the word's definition.

{% include side-by-side.html demo="terms" %}

If you want the terms to be highlighted every time they are used,
whether in curly brackets or not, use `auto terms`.

{% include side-by-side.html demo="auto-terms" %}

You can also use `terms` and `auto terms` as [question modifiers], in which
case the terms will apply only to the question, not to the interview
as a whole.  When you use `terms` and `auto terms` as initial blocks,
you cannot use [Mako] templating in the definitions, but when you use
them as [question modifiers], you can use [Mako] templating.

# <a name="template"></a>The `template` block

The word "template" has a number of different meanings.  If you are
interested in how to insert variables into the text of your questions
or documents using the [Mako] templating syntax, see [markup].  If you
are interested in document assembly based on forms or document
templates, see the [Documents] section.

A `template` block allows you to assign text to a variable and then
re-use the text by referring to a variable.

{% include side-by-side.html demo="template" %}

The `content` of a `template` may contain [Mako] and [Markdown].

The name after `template:` is a [variable name] that you can refer to
elsewhere.

The `template` block, like [`question`] and [`code`] blocks, offers to
define a variable.  So when **docassemble** needs to know the
definition of `disclaimer` and finds that `disclaimer` is not defined,
it will look for a [`question`], [`code`], or `template` block that offers
to define `disclaimer`.  If it finds the `template` block above, it
will define the `disclaimer` variable.

Optionally, a `template` can have a `subject`:

{% include side-by-side.html demo="template-subject" %}

You can refer to the two parts of the template by writing, e.g.,
`disclaimer.subject` and `disclaimer.content`.

Note that writing `${ disclaimer }` has the same effect as writing `${
disclaimer.content }`.  You can also write `${ disclaimer.show() }`
(for interchangability with images).

To convert the subject and the content to HTML, you can write
`disclaimer.subject_as_html()` and `disclaimer.content_as_html()`.
These methods take the optional keyword argument `trim`.  If `True`,
the resulting HTML will not be in a `<p>` element.  (The default is
`False`.)

[`template`] objects are also useful for defining the content of e-mails.  See
[`send_email()`] for more information on using templates with e-mails.

You might prefer to write text in [Markdown] files, rather than in
[Markdown] embedded within [YAML].  To facilitate this,
**docassemble** allows you to create a `template` that references a
separate [Markdown] file.

{% include side-by-side.html demo="template-file" %}

The file [`disclaimer.md`] is a simple [Markdown] file containing the
disclaimer from the previous example.

The `content file` is assumed to refer to a file in the "templates"
folder of the same package as the interview source, unless a specific
package name is indicated.  (e.g., `content file:`
[`docassemble.demo:data/templates/hello_template.md`])

In the example above, the sample interview is in the file
[`docassemble.base:data/questions/examples/template-file.yml`], while
the [Markdown] file is located at
[`docassemble.base:data/templates/disclaimer.md`].

If the `content file` specifier refers to a dictionary in which the
only key is `code`, the `code` will be evaluated as [Python] code, and
the result will be used as the file.

{% include side-by-side.html demo="template-file-code" %}

In this example, the `code` evaluated to the name of a file in the
templates folder.  The `code` may also evaluate to a URL, [`DAFile`],
[`DAFileList`], [`DAFileCollection`], or [`DAStaticFile`].

A `template` can also be inserted into a [`docx template file`].  This
can be useful when you want to insert multiple paragraphs of text into
a DOCX file.  Ordinarily, when you insert text into a [`docx template
file`], newlines are replaced with spaces.  The effect of inserting a
[`template`] into a [`docx template file`] is controlled by the [`new
markdown to docx`] directive in the [Configuration].  If you set `new
markdown to docx: True` in the [Configuration], then you should insert
a `template` using:

> {% raw %}{{p the_template }}{% endraw %}

However, if you don't set the [`new markdown to docx`] directive (the
default of which is `False`), then you need to insert the [`template`]
using:

> {% raw %}{{r the_template }}{% endraw %}

In the future, the default will change to `True`.

# <a name="table"></a>The `table` block

The `table` works in much the same way as a `template`, except its
content is a table that will be formatted appropriately whether it is
included in a [question] or in a [document].

This block should be used when each row of your table represents an
item in a [group]; that is, you do not know how many rows the table
will contain, because the information is in a [list], [dictionary], or
[set].  If you just want to format some text in a table format, see
the documentation about [tables] in the [markup] section.

In the following example, the variable `fruit` is a [`DAList`] of
objects of type [`Thing`], each of which represents a fruit.  Each row
in the resulting table will describe one of the fruits.

{% include side-by-side.html demo="table" %}

The `table: fruit_table` line indicates the name of the variable that
will hold the template for table.  The [`question`] block includes the
table simply by referring to the variable `fruit_table`.

The `rows: fruit` line indicates the variable containing the [group]
of items that represent rows in the table.  The `fruit` variable is a
[`DAList`] that gets populated during the interview.

Next, `columns` describes the header of each column and what should be
printed in each cell under that header.  Like a [`fields`] list within
a [`question`], `columns` must contain a [YAML] list where each item
is a key/value pair (a one-item dictionary) where the key is the
header of the column and the value is a [Python expression]
representing the contents of the cell for that column, for a given row.

In the example above, the header of the first column is "Fruit Name"
and the [Python expression] that produces the name of the fruit is
`row_item.name`.

There are two special variables available to these
[Python expression]s:

* `row_item`: this is the item in the [group] corresponding to the
  current row.
* `row_index`: this is `0` for the first row, `1` for the second row,
  `2` for the third row, etc. 

You can pretend that the [Python expression]s are evaluated in a
context like this:

{% highlight python %}
row_index = 0
for row_item in fruit:
  # evaluation takes place here
  row_index = row_index + 1
{% endhighlight %}

In this example, the first column will show name of the fruit
(`row_item.name`) and the second column will show the number of seeds
(`row_item.seeds`).

The header of each column is plain text (not a [Python expression]).
The header can include [Mako] and [Markdown].

If you have a complicated header, you can use the special keys
`header` and `cell` to describe the header and the cell separately.
(This is similar to using [`label` and `field`] within a [`fields`]
list.)

{% include side-by-side.html demo="table-alt" %}

You can use [Python] to create cells with content that is computed
from the items of a [group].

{% include side-by-side.html demo="table-python" %}

The above example prints the name of the fruit as a plural noun, and
inflates the number of seeds.

Remember that the [Python] code here is an [expression], not a block
of code.  If you want to use if/then/else logic in a cell, you will
need to use [Python]'s one-line form of if/then/else:

{% include side-by-side.html demo="table-if-then" %}

When `fruit_table` is inserted into the [`question`], the result will
be a [Markdown]-formatted table.

This:

{% highlight yaml %}
question: |
  Information about fruit
subquestion: |
  Here is a fruity summary.

  ${ fruit_table }
{% endhighlight %}

will have the effect of this:

{% highlight yaml %}
question: |
  Information about fruit
subquestion: |
  Here is a fruity summary.

  Fruit Name |Number of Seeds
  -----------|---------------
  Apples     |4
  Oranges    |3
  Pears      |6
{% endhighlight %}

For more information about [Markdown]-formatted tables, see the
documentation about [tables] in the [markup] section.

Instead of using a `table` block, you could construct your own
[Markdown] tables manually using a [Mako] "for" loop.  For example:

{% include side-by-side.html demo="table-mako" %}

The advantages of using the `table` block are:

* The `table` block describes the content of a table in a conceptual
  rather than visual way.  In [Markdown], simple tables look simple,
  but complicated tables can look messy.  The `table` block allows you
  to map out your ideas in outline form rather than squeezing
  everything into a single line that has a lot of punctuation marks.
* The `table` block will attempt to set the relative table widths in a
  sensible way based on the actual contents of the table.  If you
  create your own tables in [Markdown], and the text in any cell
  wraps, the relative table widths of the columns will be decided
  based on the relative widths of the cells in the divider row
  (`----|---------`).  You might not know in advance what the relative
  sizes of the text will be in each column.

The `table` block acts like a `template` block in that the variable it
sets will be a **docassemble** object.  The `.content` attribute will
be set to the text of the table in [Markdown] format.

If the variable indicated by `rows` is empty, the table will display
with only the headers.  To suppress this, you can add `show if empty:
False` to the `table` block.  The resulting `.content` will be the
empty string, `""`.

{% include side-by-side.html demo="table-empty" %}

If you would like a message to display in place of the table in the
event that there are no `rows` to display, you can set `show if empty`
to this message.  [Mako] and [Markdown] can be used.  The message will
become the `.content` of the resulting object.

{% include side-by-side.html demo="table-empty-message" %}

If you include a table in the content of an [`attachment`], you might
find that the table is too wide, or not wide enough.  [Pandoc] breaks
lines, determines the relative width of columns, and determines the
final width of a table based on the characters in the divider row
(`----|---------`).

By default, **docassemble** will construct a divider row that is no longer
than 65 characters.  This should work for standard applications (12
point font, letter size paper).

You can change the number of characters from 65 to something else by
setting value of [`table width`] in a [`features`] block.

{% include side-by-side.html demo="table-width" %}

You can also use `table` blocks with [`DADict`] objects:

{% include side-by-side.html demo="table-dict" %}

When `rows` refers to a [`DADict`], then in the `columns`, `row_index`
represents the "key" and `row_item` represents the value of each item
in the dictionary.

You can pretend that the [Python expression]s under `columns` are
evaluated in a context like this:

{% highlight python %}
for row_index in sorted(income):
  row_item = fruit[row_index]
  # evaluation takes place here
{% endhighlight %}

Note that running `sorted()` on a dictionary returns an alphabetically
sorted list of keys of the dictionary.  In [Python], dictionaries are
inherently unordered.  The keys are sorted is this fashion so that
the order of the rows in a table does not change every time the table
appears on the screen.

<a name="require gathered"></a>By default, the display of a table
will require that the table is gathered.  If you want to display a
table with the items in a group that have been completely gathered so
far, you can set `require gathered: False` in the table definition.

{% include side-by-side.html demo="table-require-gathered" %}

<a name="show incomplete"></a>When displaying a table using `require
gathered: False`, an item will not be shown unless it has been
completely gathered.  If you want to show unfinished items, set `show
incomplete: True`.

{% include side-by-side.html demo="table-show-incomplete" %}

<a name="not available label"></a>By default, a column for which
information is not known will be displayed as "n/a."  You can
customize this by setting `not available label`.  In this example, the
label is set to a blank value:

{% include side-by-side.html demo="table-not-available-label" %}

## <a name="export"></a>Exporting tables to Excel and other formats

You can call the `export()` method on a `table` to get a [`DAFile`]
representation of the table.

For example, this interview provides a Microsoft Excel .xlsx file
representation of a table:

{% include side-by-side.html demo="table-export" %}

This function uses the [`pandas`] module to export to various formats.

The `export()` method takes a filename, which is parsed to determine
the file format you want to use.  This can also be provided as the
`filename` keyword parameter.  If you omit the filename, you can
indicate the file format using the `file_format` keyword parameter.
The default file format is `'xlsx'`.  The valid file formats include
`csv`, `xlsx`, and `json`.

The `title` keyword parameter indicates the name of the data set.
This is used as the name of the Microsoft Excel sheet.

When the `xlsx` format is used, you can set the `freeze_panes` keyword
parameter to `False` to turn off the Microsoft Excel "freeze panes"
feature.

Here are some examples of usage:

* `fruit_table.export('fruit.xlsx')`: returns a Microsoft Excel file
  called `fruit.xlsx`.
* `fruit_table.export('fruit.xlsx', title='Fruits')`: returns a Microsoft Excel file
  called `fruit.xlsx` where the sheet is named "Fruits".
* `fruit_table.export('fruit.xlsx', title='Fruits', freeze_panes=False)`: returns a Microsoft Excel file
  called `fruit.xlsx` where the sheet is named "Fruits" and the
  "freeze panes" feature is turned off.
* `fruit_table.export('fruit.csv')`: returns a comma-separated values
  file called `fruit.csv`.
* `fruit_table.export(file_format='csv')`: returns a comma-separated values
  file called `file.csv`.
* `fruit_table.export()`: returns a Microsoft Excel file called
  `file.xlsx`.

## <a name="as_df"></a>Converting tables to a pandas dataframe

If you want to work with your table as a [`pandas`] dataframe, you can
call `fruit_table.as_df()` to obtain the information for the table as
a [`pandas`] dataframe object.  However, note that objects from the
[`pandas`] package cannot necessarily be "pickled" by Python, so it is
best if you call this method from functions in Python modules, or in
such a way that the results do not get saved to variables in the
interview.

## <a name="groups edit"></a>Using tables to edit groups

You can use a `table` to provide the user with an interface for
editing an already-gathered [`DAList`] or [`DADict`].

{% include side-by-side.html demo="edit-list" %}

For more information about this feature, see the section on [editing
an already-gathered list] in the section on [groups].

# <a name="sections"></a>Defining the sections for the navigation bar

You can add use the [`navigation bar`] feature or the
[`nav.show_sections()`] function to show your users the "sections" of
the interview and what the current section of the interview is.

Here is a complete example.

{% include side-by-side.html demo="sections" %}

Subsections are supported, but only one level of nesting is allowed.

If your interview uses [multiple languages], you can specify more than
one `sections` block and modify each one with a `language` modifier:

{% highlight yaml %}
---
language: en
sections:
  - Introduction
  - Fruit
  - Vegetables
  - Conclusion
---
language: es
sections:
  - Introducción
  - Fruta
  - Vegetales
  - Conclusión
---
{% endhighlight %}

If no language is specified, the fallback language `*` is used.

In the example above, the [`section`] modifier referred to sections
using the same text that is displayed to the user.  However, in some
circumstances, you might want to use a shorthand to refer to a
section, and update the actual section names displayed to the user
without having to make changes in numerous places in your interview.
You can do this by using key/value pairs in your `sections` block, and
using the special key `subsections` to indicate subsections:

{% include side-by-side.html demo="sections-keywords" %}

The keywords for section names need to be valid [Python names].  When
choosing keywords, make sure not to use the names of variables that
already exist in your interview.

This is because the keywords can be used to make the left-hand
navigation bar clickable.  If a keyword for a section is a variable
that exists in the interview, clicking on the section will cause an
[action] to be launched that seeks a definition of that variable.

The recommended way to use this feature is to set up [`review`] blocks
that have [`event`] set to the keyword of each section that you want
to be clickable.

{% include side-by-side.html demo="sections-keywords-review" %}

Note that if you use [`review`] blocks in an interview with sections,
every question should have a `section` defined.  Otherwise, when your
users jump around the interview, their section may not be appropriate
for the question they are currently answering.  Alternatively, you
could use [`code` blocks] and the [`nav.set_section()`] function to
make sure that the section is set appropriately.

By default, users are only able to click on sections that they have
visited.  If you want users to be able to click on any section at any
time, set `progressive` to `False`:

{% include side-by-side.html demo="sections-non-progressive" %}

By default, subsections are not shown until the user has entered one
of the subsections.  If you want subsections to be opened by default,
set `auto open` to `True`.

{% include side-by-side.html demo="sections-auto-open" %}

# <a name="interview help"></a>Assisting users with `interview help`

{% highlight yaml %}
---
interview help:
  heading: How to use this web site
  content: |
    Answer each question.  At the end, you will get a prize.
---
{% endhighlight %}

An `interview help` block adds text to the "Help" page of every
question in the interview.  If the question has `help` text of its
own, the `interview help` will appear after the question-specific
help.

You can also add audio to your interview help:

{% highlight yaml %}
---
interview help:
  heading: How to use this web site
  audio: answer_each_question.mp3
  content: |
    Answer each question.  At the end, you will get a prize.
---
{% endhighlight %}

You can also add video to help text using the `video` specifier.

See the [question modifiers] section for an explanation of how audio and video
file references work.

You can also provide a `label` as part of the `interview help`.  This
label will be used instead of the word "Help" in the navigation bar as
a label for the "Help" tab.

{% highlight yaml %}
---
interview help:
  label: More info
  heading: More information about this web site
  content: |
    If you are not sure what the right answer is, provide
    your best guess.
    
    You are answering these questions under the pains and
    penalties of perjury.  Your answers will be 
    shared with the special prosecutor.
---
{% endhighlight %}

Note that if you provide question-specific [`help`], and you include a
`label` as part of that help, that label will override the default
label provided in the `interview help` (except if [`question help
button`] is enabled).

# <a name="def"></a>Mako functions: `def`

{% highlight yaml %}
def: adorability
mako: |
  <%def name="describe_as_adorable(person)"> \
  ${ person } is adorable. \
  </%def>
{% endhighlight %}

A `def` block allows you to define [Mako] "[def]" functions that you
can re-use later in your question or document templates.  You can use
the above function by doing:

{% highlight yaml %}
---
question: |
  ${ describe_as_adorable(spouse) } Am I right?
yesno: user_agrees_spouse_is_adorable
usedefs:
 - adorability
---
{% endhighlight %}

Due to the way **docassemble** parses interviews, the `def` block
needs to be defined before it is used.

Note the `\` marks at the end of the lines in the `mako` definition.
Without these marks, there would be an extra newline inserted.  You
may or may not want this extra newline.

# <a name="default role"></a>Setting the `default role`

{% highlight yaml %}
default role: client
code: |
  if user_logged_in() and user_has_privilege('advocate'):
    user = advocate
    role = 'advocate'
  else:
    user = client
    role = 'client'
  set_info(user=user, role=role)
---
{% endhighlight %}

If your interview uses the [roles] feature for multi-user interviews,
the `default role` specifier will define what role or roles will be
required for any question that does not contain an explicit `role`
specifier.

When you use the [roles] feature, you need to have some way of telling
your interview logic what the role of the interviewee is.

If you include `code` within the same block as your `default role`
specifier, that code will be executed every time the interview logic
is processed, as if it was marked as `initial`.  For this reason, any
`default role` specifier that contains code should be placed earlier
in the interview file than and `mandatory` questions or [`code` blocks].

In the example above, the interview has two roles: "client" and
"advocate".  The special variable `role` is set in the `code` block,
which is executed every time the interview logic is processed.

In addition, the [`set_info()`] function is called.  This lets the
linguistic functions know who the `user` is, so that questions can ask
"What is your date of birth?" or "What is John Smith's date of birth"
depending on whether the current user is John Smith or not.

# <a name="default language"></a>Setting the `default language`

{% highlight yaml %}
---
default language: es
---
{% endhighlight %}

This sets the language to use for all of the remaining questions in
the file for which the [`language` modifier] is not specified.  The
purpose of this is to save typing; otherwise you would have to set the
[`language` modifier] for each question.  Note that this does not extend to
questions in [`include`]d files.

If your interview only uses one language, it is not necessary to (and
probably not a good idea to) set a `default language`.

See [language support] for more information about how to create
[multi-lingual interviews].  See [question modifiers] for information
about the `language` setting of a question.

# <a name="translations"></a>Translation files

One way that **docassemble** supports [multi-lingual interviews] is
through the [`language` modifier] on a [`question`] and the [`default
language`] block, which sets a default value for the [`language`
modifier].  Your interview can contain [`question`]s in English that
don't have a [`language` modifier], and [`question`]s in French that
have the `language: fr` modifier set.  If the current language in an
interview (as determined by the [`set_language()`] function) is French
(`fr`), then when **docassemble** seeks a block to set a given
variable, it will search the French blocks first.

This method of creating [multi-lingual interviews] is good if the
person who translates text from English to French is someone who
understands how **docassemble** [YAML] files work.

There is another method of creating [multi-lingual interviews] that
may be preferable if the translator is someone who does not understand
how **docassemble** [YAML] files work.  This second method extracts
the phrases from an interview (specifically, everywhere in the YAML
where [Mako] templating is allowed) and lists them all in an Excel
spreadsheet.  The spreadsheet can then be given to a French
translator, and the translator fills out a column in the spreadsheet
with the translation of each phrase.  Then the completed spreadsheet
can be stored in the [sources] folder of a package and referenced in
an interview using the `translations` block:

{% highlight yaml %}
translations:
  - custody.xlsx
{% endhighlight %}

Then, if the current language in an interview is French, the interview
will use the French version of each phrase.

This allows you to support multi-lingual interviews while having a
code base that is all in one language.

To obtain such a spreadsheet for a given interview, visit the
[Utilities] page and go to the section called [Download an interview phrase translation file].

The `translations` block is only capable of defining translations for
blocks that come after the `translations` block.  Therefore, it is a
good practice to make sure that the `translations` block is placed as
one of the very first blocks in your interview [YAML] file.

The [language support] for more information about how to create
[multi-lingual interviews].  See [question modifiers] for information
about the `language` setting of a question.

# <a name="default screen parts"></a>Default screen parts

The `default screen parts` allows you to write [Mako] and [Markdown]
to create text that will appear by default in parts of the screen on
every page.

{% include side-by-side.html demo="default-screen-parts" %}

When using this, make sure you do not cause your interview to go into
an infinite loop.  If any of your screen parts require information
from the user, your interview will need to pose a [`question`] to the
user to gather that information, but in order to pose the
[`question`], it will need the information.  To avoid this, you can
use the [`defined()`] function or other methods.

For information about other ways to set defaults for different parts
of the screens during interviews, see the [screen parts] section.

# <a name="default validation messages"></a>Custom validation messages

The **docassemble** user interface uses the [jQuery Validation Plugin]
to pop up messages when the user does not enter information for a
required field, or if a number does not meet a minimum, or if an
e-mail address is not valid, and other circumstances.

The messages that are displayed can be customized in a number of ways.

On a server-wide level, the messages can be customized the same way
other built-in phrases in **docassemble** can be customized: using the
[`words`] directive in the [Configuration] to make a "translation
table" between the built-in text to the values you want to be used in
their place.

On an interview-wide level, the messages can be customized using a
`default validation messages` block:

{% include side-by-side.html demo="default-validation-messages" %}

Within an individual field in a `question`, you can use the
[`validation messages`] field modifier to define what validation
messages should be used.  These will override the `default validation
messages`.

Each validation message has a code.  In the above example, the codes
used were `required` and `max`.  The complete list of codes is:

* `required` for `This field is required.` There is a default text transformation for
  language `en` that translates this to "You need to fill this in."
  This is the standard message that users see when they fail to
  complete a required field.
* `multiple choice required` for `You need to select one.` This is shown for 
  multiple-choice fields.
* `combobox required` for `You need to select one or type in a new
  value.` This is shown for [`combobox`] fields.
* `checkboxes required` for `Check at least one option, or check "%s"`
  This is shown for [`checkboxes`] fields with a "None of the above"
  option.  It is also used for [`yesno`] fields with [`uncheck
  others`] set, which is shown when the user does not check any of the
  [`yesno`] fields.  `%s` is a code that is replaced with the label of
  the "None of the above" choice.
* `minlength` for `You must type at least %s characters.`  This is shown when there is
  a [`minlength`] field modifier. 
* `maxlength` for `You cannot type more than %s characters.`  This is shown when there is
  a [`maxlength`] field modifier. 
* `checkbox minmaxlength` for `Please select exactly %s.`  This is shown when there is a
  [`checkboxes`] field with a [`minlength`] field modifier that is the
  same as the [`maxlength`] field modifier.
* `checkbox minlength` for `Please select at least %s.`  This is shown when there is a
  [`checkboxes`] field with a [`minlength`] field modifier set to
  something other than `1`.
* `checkbox maxlength` for `Please select no more than %s.`  This is shown when there is a
  [`checkboxes`] field with a [`maxlength`] field modifier.
* `date` for `You need to enter a valid date.` This is shown for [`date`] fields
  when the text entered is not an actual date.
* `date minmax` for `You need to enter a date between %s and %s.` This is shown for
  [`date`] fields with [`min`] and [`max`] set.
* `date min` for `You need to enter a date on or after %s.` This is shown for
  [`date`] fields with [`min`] set.
* `date max` for `You need to enter a date on or before %s.` This is shown for
  [`date`] fields with [`max`] set.
* `time` for `You need to enter a valid time.` This is shown for [`time`] fields.
* `datetime` for `You need to enter a valid date and time.` This is shown for
  [`datetime`] fields.
* `email` for `You need to enter a complete e-mail address.` This is shown for
  [`email`] fields.
* `number` for `You need to enter a number.` This is shown for numeric fields
  (`number`, `currency`, `float`, and `integer`) when the input is not
  valid.
* `min` for `You need to enter a number that is at least %s.` This is shown for
  numeric fields with a [`min`] field modifier.
* `max` for `You need to enter a number that is at most %s.` This is shown for
  numeric fields with a [`max`] field modifier.
* `file` for `You must provide a file.` This is shown for [file upload fields].
* `accept` for `Please upload a file with a valid file format.` This is shown for
  [file upload fields] with an [`accept`] field modifier.

# <a name="machine learning storage"></a>Machine learning training data
 
If you use [machine learning] in your interviews, then by default,
**docassemble** will use training data associated with the
particular interview in the particular [package] in which the
interview resides.

If you would like your interview to share training data with another
interview, you can use the `machine learning storage` specifier to
point to the training data of another interview.

For example, suppose you have developed an interview called
`child_custody.yml` that uses [machine learning], and you have built
rich training sets for variables within this interview.  Then you
decide to develop another interview, in the same [package], called
`child_support.yml`, which uses many of the same variables.  It would
be a lot of work to maintain two identical training sets in two
places.

In this scenario, you can add the following block to the
`child_support.yml` interview:

{% highlight yaml %}
---
machine learning storage: ml-child_custody.json
---
{% endhighlight %}

`ml-child_custody.json` is the name of a file in the `data/sources`
directory of the [package].  This file contains the training data for
the `child-custody.yml` interview.  The naming convention for these
data files is to start with the name of the interview [YAML] file, add
`ml-` to the beginning, and replace `.yml` with `.json`.

Now, both the `child-custody.yml` and `child-support.yml` interviews
will use `ml-child_custody.json` as "storage" area for training data.
In the [Training] interface, you will find this data set under the
name `child_custody`.

If you had run the `child-support.yml` interview before adding
`machine learning storage`, you may still see a data set called
`child-support` in the [Training] interface.  If you are using the
[Playground], you may see a file called `ml-child-support.json` in the
[Sources folder].  To get rid of this, go into the [Playground] and
delete the `ml-child-support.json` file from the [Sources folder].
Then go into the [Training] interface and delete any "items" that
exist within the `child-support` interview.

If you want, you can set `machine learning storage` to a name that
does not correspond with an actual interview.  For example, you could
include `machine learning storage: ml-family-law.json` in both the
`child-custody.yml` and `child-support.yml` interviews.  Even though
there is no interview called `family-law.yml`, this will still work.
If you are using the [Playground], a file called `ml-family-law.json`
will automatically be created in the `Sources folder`.

You can also share "storage" areas across packages.  Suppose you are
working within a package called `docassemble.missourifamilylaw`, but
you want to take advantage of training sets in a package called
`docassemble.generalfamilylaw`.  You can write:

{% highlight yaml %}
---
machine learning storage: docassemble.generalfamilylaw:data/sources/ml-family.json
---
{% endhighlight %}

For more information about managing training data, see the
[machine learning] section on [packaging your training sets]

# <a name="features"></a>Optional `features`

The `features` block sets some optional features of the interview.

## <a name="debug"></a>Whether debugging features are available

If the [`debug` directive] in the [Configuration] is `True`, then by
default, the navigation bar will contain a "Source" link that shows
information about how the interview arrived at the question being
shown.  If the [`debug` directive] is `False`, then this will not be
shown.

This can be overridden in the `features` by setting `debug` to `True`
or `False` depending on the behavior you want.

The following example demonstrates turning the `debug` feature off.

{% include side-by-side.html demo="debug-mode" %}

On the server that hosts the demonstration interviews, the [`debug`
directive] is `True`, so the "Source" link is normally shown.  Setting
`debug: False` makes the "Source" link disappear.

## <a name="centered"></a>Whether interview is centered

If you do not want your interview questions to be centered on the
screen, set `centered` to `False`.

{% include side-by-side.html demo="centered" %}

## <a name="progress bar"></a>Progress bar

The `progress bar` feature controls whether a progress bar is shown
during the interview.  You can use the [`progress`] modifier or the
[`set_progress()`] function to indicate the setting of the progress
bar.

{% include side-by-side.html demo="progress-features" %}

If you want the progress bar to display the percentage, include `show
progress bar percentage: True`:

{% include side-by-side.html demo="progress-features-percentage" %}

By default, if you do not set the [`progress`] modifier on a
[`question`], then each time the user takes a step, the progress bar
will advance 5% of the way toward the end.

The 5% figure is known as the `progress bar multiplier` and it is
configurable:

{% highlight yaml %}
features:
  progress bar: True
  progress bar multiplier: 0.01
{% endhighlight %}

The default is 0.05. 

If you set `progress bar method: stepped`, the progress bar advances a
different way when there is no [`progress`] modifier.

{% highlight yaml %}
features:
  progress bar: True
  progress bar method: stepped
{% endhighlight %}

Instead of advancing toward 100%, it advances toward the next greatest
[`progress`] value that is defined on a [`question`] in the interview.
(Note that **docassemble** cannot predict the future, so whether the
[`question`] with the next highest [`progress`] value will actually be
reached is unknown; **docassemble** just looks at all the
[`question`]s in the interview that have [`progress`] values defined.)
The amount by which it advances is determined by `progress bar
multiplier`.

To use the default method for advancing the progress bar, omit
`progress bar method`, or set it to `default`.

{% highlight yaml %}
features:
  progress bar: True
  progress bar method: default
{% endhighlight %}

## <a name="navigation bar"></a>Navigation bar

The `navigation` feature controls whether a navigation bar is
shown during the interview.  You can use the [`sections`] initial
block or the [`nav.set_sections()`] function to define the sections of
your interview.  The [`section`] modifier or the [`nav.set_section()`]
function can be used to change the current section.

{% include side-by-side.html demo="sections" %}

Note that the section list is not shown on small devices, such as
smartphones.  To show a smartphone user a list of sections, you can
use the [`nav.show_sections()`] function.

If you want the navigation bar to be horizontal across the top of the
page, set `navigation` to `horizontal`:

{% include side-by-side.html demo="sections-horizontal" %}

## <a name="question back button"></a><a name="navigation back button"></a>Back button style

By default, there is a "Back" button located in the upper-left corner
of the page.  (However, the "Back" button is not present when the user
is on the first page of an interview, or the [`prevent_going_back()`]
function has been used, or the [`prevent going back`] modifier is in
use.)

Whether this back button is present can be controlled using the
`navigation back button` feature.  This will hide the "Back" button:

{% highlight yaml %}
features:
  navigation back button: False
{% endhighlight %}

You can also place a "Back" button inside the body of a question, next
to the other buttons on the screen, by setting the `question back button`
feature to `True` (the default is `False`).

{% include side-by-side.html demo="question-back-button" %}

You can also place a "Back" button inside the body of a question on
some questions but not others, using the [`back button`] modifier.

## <a name="question help button"></a>Help tab style

When [`interview help`] is available, or the [`help`] modifier is
present on a question, the "Help" tab will be present in the
navigation bar.  When the [`help`] modifier is present, the "Help" tab
is highlighted yellow and marked with a yellow star.  When the user
presses the help tab, the help screen will be shown.

If you set the `question help button` to `True`, users will be able to
access the help screen by pressing a "Help" button located within the
body of the question, to the right of the other buttons on the page.
When `question help button` is `True`, the "Help" tab will not be
highlighted yellow.

Here is an interview in which the `question help button` is not
enabled (which is the default).

{% include side-by-side.html demo="question-help-button-off" %}

Here is the same interview, with the `question help button` feature
enabled:

{% include side-by-side.html demo="question-help-button" %}

Note that when `question help button` is enabled, the label for the
help tab in the navigation bar always defaults to "Help" or to the
`label` of the [`interview help`], and it is not highlighted yellow
when question-specific help is available.

## <a name="labels above fields"></a>Positioning labels above fields

By default, the **docassemble** user interface uses [Bootstrap]'s
[horizontal form] style.  If you want your interview to use the
[Bootstrap]'s [standard] style, set `labels above fields` to `True`:

{% highlight yaml %}
features:
  labels above fields: True
{% endhighlight %}

## <a name="hide standard menu"></a>Hiding the standard menu items

By default, the menu in the corner provides logged-in users with the
ability to edit their "Profile" and the ability to go to "My
Interviews," which is a list of interview sessions they have started.
If you want to disable these links, you can use the `hide standard
menu` specifier:

{% highlight yaml %}
features:
  hide standard menu: True
{% endhighlight %}

If you want to add any of these links manually, or add them with
different names, you can do so with the
[`menu_items` special variable] and the [`url_of()`] function.

{% highlight yaml %}
mandatory: True
code: |
  menu_items = [
    {'label': 'Edit my Profile', 'url': url_of('profile')},
    {'label': 'Saved Sessions', 'url': url_of('interviews')}
  ]
{% endhighlight %}

## <a name="javascript"></a><a name="css"></a>Javascript and CSS files

If you are a web developer and you know how to write [HTML],
[Javascript], and [CSS], you can embed [HTML] in your interview text.
You can also bring [Javascript] and [CSS] files into the user's
browser.

For example, the following interview brings in a [Javascript] file,
[`my-functions.js`], and a [CSS] file, [`my-styles.css`], into the
user's browser.  These files are located in the `data/static` folder
of the same [package] in which the interview is located.

{% include side-by-side.html demo="external_files" %}

The contents of [`my-functions.js`] are:

{% highlight javascript %}
$(document).on('daPageLoad', function(){
  $(".groovy").html("I am purple");
});
{% endhighlight %}

The contents of [`my-styles.css`] are:

{% highlight css %}
.groovy {
  color: purple;
}
{% endhighlight %}

You can write whatever you want in these files; they will simply be
loaded by the user's browser.  Note that your Javascript files will be
loaded after [jQuery] is loaded, so your code can use [jQuery], as
this example does.

If you have Javascript code that you want to run after each screen of
the interview is loaded, attach a [jQuery] event handler to `document`
for the event `daPageLoad`, which is a **docassemble**-specific event
that is triggered after each screen loads.  (Since **docassemble**
uses [Ajax] to load each new screen, if you attach code using
[jQuery]'s [`ready()`] method, the code will run when the browser
first loads, but not every time the user sees a new screen.)  The
example above demonstrates this; every time the page loads, the code
will replace the contents of any element with the class `groovy`.

This example demonstrates bringing in [CSS] and [Javascript] files that
are located in the `data/static` directory of the same package as the
interview.  You can also refer to files in other packages:

{% highlight yaml %}
features:
  css: docassemble.demo:data/static/my.css
{% endhighlight %}

or on the internet at a URL:

{% highlight yaml %}
features:
  javascript: https://example.com/js/my-functions.js
{% endhighlight %}

Also, if you want to bring in multiple files, specify them with a
[YAML] list:

{% highlight yaml %}
features:
  css:
    - my-styles.css
    - https://cdnjs.cloudflare.com/ajax/libs/animate.css/3.5.2/animate.min.css
  javascript:
    - http://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js
    - https://cdnjs.cloudflare.com/ajax/libs/offline-js/0.7.18/offline.min.js
{% endhighlight %}

If you want to include [CSS] or [Javascript] code in a specific
question, rather than in all questions of your interview you can use
the [`script`] and [`css`] modifiers.

<a name="css customization"></a>The HTML of the screen showing a
[`question`] contains a number of placeholder [CSS] classes that are
not used for formatting, but that are available to facilitate
customization:

* If a `question` is tagged with an [`id`], the `<body>` will be given
  a class beginning with `question-` followed by the [`id`], except
  that the [`id`] will be transformed into lowercase and
  non-alphanumeric characters will be converted into hyphens.  For
  example, if the [`id`] is `Intro screen`, the class name will be
  `question-intro-screen`.
* `<fieldset>`s are tagged with classes like `field-yesno` and
  `field-buttons`.
* `<div>`s that contain fields are tagged with classes like
  `field-container`, `field-container-datatype-area`,
  `field-container-inputtype-combobox`, and other classes.

For more information, use the [DOM] inspector in your web browser to
see what the class names are and which elements have the class names.

### <a name="charts"></a>Example use of JavaScript: charting

Here is an example interview that uses a [`javascript`] feature and a
[`script`] modifier to draw a doughnut chart using [chart.js].

{% include side-by-side.html demo="chart" %}

Here is an example interview that draws a pie chart using [Google Charts].

{% include side-by-side.html demo="googlechart" %}

## <a name="disable analytics"></a>Disable analytics

By default, if your [Configuration] enables a [`segment id`], your
interviews will send information to [Segment], and if it enables an
[`analytics id`] in the [`google`] configuration, it will send
information to [Google Analytics].  To turn this off for a particular
interview, set `disable analytics` to `True` in the `features` block.

{% highlight yaml %}
features:
  disable analytics: True
{% endhighlight %}

## <a name="bootstrap theme"></a>Bootstrap theme

Using the `bootstrap theme` feature, you can change the look and feel
of your interview's web interface by instructing your interview to use
a non-standard [CSS] file in place of the standard [CSS] file used by
[Bootstrap].

{% include demo-side-by-side.html demo="bootstrap-theme" %}

The file can be referenced in a number of ways:

* `lumen.min.css`: the file `lumen.min.css` in the "static" folder of
  the current package.
* `docassemble.demo:lumen.min.css`: the file `lumen.min.css` in the
  "static" folder (`data/static/`) of the `docassemble.demo` package.
* `docassemble.demo:data/static/lumen.min.css`: the same.
* `https://bootswatch.com/lumen/bootstrap.min.css`: a file on the internet.

For more information about using custom [Bootstrap] themes, and for
information about applying themes on a global level, see the
documentation for the [`bootstrap theme` configuration directive].

## <a name="inverse navbar"></a>Inverted Bootstrap navbar

By default, **docassemble** uses [Bootstrap]'s "dark" (formerly known
as "inverted") style of navigation bar so that the navigation bar
stands out from the white background.  If you do not want to use the
inverted navbar, set the `inverse navbar` feature to `False`.

{% include side-by-side.html demo="inverse-navbar" %}

To make this change at a global level, see the
[`inverse navbar` configuration directive].

## <a name="hide navbar"></a>Hiding the navbar

By default, **docassemble** shows a navigation bar at the top of the
screen.  To make it disappear, you can set `hide navbar: True`.

## <a name="table width"></a>Width of tables in attachments

As explained more fully in the [tables] section, if you include a
[table] in an [`attachment`] and the table is too wide, or not wide
enough, you can change the default character width of tables from 65
to some other value using the `table width` specifier within the
`features` block.

{% highlight yaml %}
features:
  table width: 75
{% endhighlight %}

## <a name="cache documents"></a>Disabling document caching

By default, **docassemble** caches assembled documents for performance
reasons.  To disable the [document caching feature] for a given
interview, set `cache documents` to `False`.

{% highlight yaml %}
features:
  cache documents: False
{% endhighlight %}

## <a name="pdfa"></a>Producing PDF/A files

If you want the [PDF] files produced by your interview to be in
[PDF/A] format, you can set this as a default:

{% highlight yaml %}
features:
  pdf/a: True
{% endhighlight %}

The default is determined by the [`pdf/a` configuration directive].
The setting can also be made on a per-attachment basis by setting the
[`pdf/a` attachment setting].

<a name="tagged pdf"></a>When using [`docx template file`], you also
have the option of creating a "tagged PDF," which is similar to
[PDF/A].  You can set this as an interview-wide default:

{% highlight yaml %}
features:
  tagged pdf: True
{% endhighlight %}

The default is determined by the [`tagged pdf` configuration directive].
This setting can also be made on a per-attachment basis by setting the
[`tagged pdf` attachment setting].

## <a name="maximum image size"></a>Limiting size of uploaded images

If your users upload digital photos into your interviews, the uploads
may take a long time.  Images can be reduced in size before they are
uploaded.  To require by default for all uploads in your interview,
set `maximum image size` in the `features` block of your interview.

{% include side-by-side.html demo="upload-max-image-size-features" %}

In this example, images will be reduced in size so that they are no
taller than 100 pixels and no wider than 100 pixels.

Note that the image file type of the uploaded file may be changed to
[PNG] during the conversion process.  Different browsers behave
differently.

This is just a default value; you can override it by setting the
[`maximum image size` in a field definition].

If you have an interview-wide default, but you want to override it for
a particular field to allow full-resolution camera uploads, you can
set the [`maximum image size` field modifier] to `None`.

If you want to use a site-side default value, set the
[`maximum image size` in the configuration].

## <a name="image upload type"></a>Converting the format of uploaded images

If you are using `maximum image size`, you can also cause images to be
converted to [PNG], [JPEG], or [BMP] by the browser during the upload
process by setting the `image upload type` to `png`, `jpeg`, or `bmp`.

{% include side-by-side.html demo="upload-max-image-size-type-features" %}

## <a name="go full screen"></a>Going full screen when interview is embedded

It is possible to embed a **docassemble** interview in a web page
using an [iframe].  However, the user experience on mobile is degraded
when an interview is embedded.

If you want the interview to switch to "full screen" after the user
moves to the next screen in the embedded interview, you can do so.
Within a `features` block, include `go full screen: True`.

{% include side-by-side.html demo="exit-url-referer-fullscreen" path="/static/test-iframe.html" %}

For more information about implementing an embedded interview like
this, see the [HTML source of the web page used in this example]({{ site.github.repository_url }}/blob/gh-pages/static/test-iframe.html){:target="_blank"}.

Note that in this example, the user is provided with an [exit button]
at the end of the interview that directs the user back to the page
that originally embedded the interview.  This is accomplished by
setting the `url` of the [exit button] to the result of the
[`referring_url()`] function.

If you only want the interview to go full screen if the user is using
a mobile device, use `go full screen: mobile`.

{% include side-by-side.html demo="exit-url-referer-fullscreen-mobile" path="/static/test-iframe-mobile.html" %}

Note that this example provides a different [ending screen] depending
on whether the user is on a desktop or a mobile device.  If a desktop
user is viewing the interview in an [iframe] on a web site, the
interview should not provide an exit button that takes the user to a
web site, because then the user will see a web site embedded in a web
site.  The interview in this example uses the [`device()`] function to
detect whether the user is using a mobile device.  Note that the
interview logic looks both at `device().is_mobile` as well as
`device().is_tablet`.  This corresponds with the functionality of `go
full screen: mobile`, which will make the interview go full screen if
the user has either a mobile phone or a tablet.

## <a name="loop limit"></a><a name="recursion limit"></a>Infinite loop protection

The [infinite loop protection] section of the [configuration]
documentation explains how you can change the default limits on
recursion and looping for all interviews on the server.

You can also set these limits on a per-interview basis using the `loop
limit` and `recursion limit` features.

{% highlight yaml %}
features:
  loop limit: 600
  recursion limit: 600
{% endhighlight %}

## <a name="review button color"></a><a name="review button icon"></a>Customizing buttons on review pages

By default, when you use a [`review`] screen that includes buttons,
the buttons have the [Bootstrap] "success" color.  You can style these
buttons using the `review button color` and `review button icon`
features.

The `review button color` can be one of `primary`, `secondary`,
`success`, `danger`, `warning`, `info`, `light`, `link`, and `dark`.
The default is `'success'`.  The actual colors depend on the Bootstrap
theme.

The `review button icon` can be set to the name of the [Font Awesome]
icon to use at the start of the button.  The default is
`'pencil-alt'`.  The icon name is assumed to refer to an icon in the
"solid" collection (`fas`).  To use a different collection, specify a
name such as `fab-fa-windows` for the `windows` icon in the "brand"
collection.  The default is `None`, which means no icon is included.

Here is an example that uses the same style as "Edit" buttons within
tables.

{% include side-by-side.html demo="review-edit-list-custom-button" %}

## <a name="use catchall"></a>Enabling catchall blocks

If you set `use catchall` to `True`, then any variables for which no
block is available will be set to a `DACatchAll` object.

{% highlight yaml %}
features:
  use catchall: True
{% endhighlight %}

For more information about this feature, see the [catchall questions]
subsection.

## <a name="default date min"></a><a name="default date max"></a>Default date limits

If you want to set a default [`min`] and/or [`max`] on a [`date`]
field, you can use `default date min` and/or `default date max`.

{% include side-by-side.html demo="default-date-min" %}

[Mako] cannot be used to set these dates inside a `features` block.
If you want to use a computed value, you need to specify a [`min`] or
[`max`] on the field.

[catchall questions]: {{ site.baseurl }}/docs/fields.html#catchall
[infinite loop protection]: {{ site.baseurl }}/docs/config.html#loop limit
[ending screen]: {{ site.baseurl }}/docs/questions.html#ending screens
[`device()`]: {{ site.baseurl }}/docs/functions.html#device
[exit button]: {{ site.baseurl }}/docs/questions.html#special buttons
[`referring_url()`]: {{ site.baseurl }}/docs/functions.html#referring_url
[iframe]: https://www.w3schools.com/TAgs/tag_iframe.asp
[`pdf/a` attachment setting]: {{ site.baseurl }}/docs/documents.html#pdfa
[`tagged pdf` attachment setting]: {{ site.baseurl }}/docs/documents.html#tagged pdf
[`pdf/a` configuration directive]: {{ site.baseurl }}/docs/config.html#pdfa
[`tagged pdf` configuration directive]: {{ site.baseurl }}/docs/config.html#tagged pdf
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
[table]: #table
[tables]: #table
[`ready()`]: https://api.jquery.com/ready/
[Ajax]: https://en.wikipedia.org/wiki/Ajax_(programming)
[jQuery]: https://jquery.com/
[package]: {{ site.baseurl }}/docs/packages.html
[`html`]: {{ site.baseurl }}/docs/fields.html#html
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
[Mako]: http://www.makotemplates.org/
[language support]: {{ site.baseurl }}/docs/language.html
[multiple languages]: {{ site.baseurl }}/docs/language.html
[question modifiers]: {{ site.baseurl }}/docs/modifiers.html
[markup]: {{ site.baseurl }}/docs/markup.html
[setting variables]: {{ site.baseurl }}/docs/fields.html
[objects]: {{ site.baseurl }}/docs/objects.html
[def]: http://docs.makotemplates.org/en/latest/defs.html
[roles]: {{ site.baseurl}}/docs/roles.html
[`progress`]: {{ site.baseurl}}/docs/modifiers.html#progress
[`language` modifier]: {{ site.baseurl}}/docs/modifiers.html#language
[`include`]: #include
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`docassemble.base.legal`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`my-functions.js`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/static/my-functions.js
[`my-styles.css`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/static/my-styles.css
[`set_info()`]: {{ site.baseurl}}/docs/functions.html#set_info
[YAML]: https://en.wikipedia.org/wiki/YAML
[`code` block]: {{ site.baseurl}}/docs/code.html
[`code` blocks]: {{ site.baseurl}}/docs/code.html
[`reconsider` modifier]: {{ site.baseurl}}/docs/logic.html#reconsider
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[HTML]: https://en.wikipedia.org/wiki/HTML
[`css`]: {{ site.baseurl }}/docs/modifiers.html#css
[`script`]: {{ site.baseurl }}/docs/modifiers.html#script
[`objects_from_file()` function]: {{ site.baseurl}}/docs/functions.html#objects_from_file
[sources folder]: {{ site.baseurl }}/docs/playground.html#sources
[machine learning]: {{ site.baseurl }}/docs/ml.html#howtouse
[Training]: {{ site.baseurl }}/docs/ml.html#train
[Sources folder]: {{ site.baseurl }}/docs/playground.html#sources
[Playground]: {{ site.baseurl }}/docs/playground.html
[packaging your training sets]: {{ site.baseurl }}/docs/ml.html#packaging
[`nav.show_sections()`]: {{ site.baseurl}}/docs/functions.html#DANav.show_sections
[`section`]: {{ site.baseurl}}/docs/modifiers.html#section
[`nav.set_section()`]: {{ site.baseurl}}/docs/functions.html#DANav.set_section
[`sections`]: #sections
[`navigation`]: #navigation bar
[Python names]: {{ site.baseurl}}/docs/fields.html#variable names
[`event`]: {{ site.baseurl}}/docs/fields.html#event
[`review`]: {{ site.baseurl}}/docs/fields.html#review
[`navigation bar`]: #navigation bar
[`nav.set_sections()`]: {{ site.baseurl}}/docs/functions.html#DANav.set_sections
[action]: {{ site.baseurl}}/docs/functions.html#actions
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[PDF/A]: https://en.wikipedia.org/wiki/PDF/A
[`dispatch`]: {{ site.baseurl}}/docs/config.html#dispatch
[configuration]: {{ site.baseurl}}/docs/config.html
[`maximum image size` in a field definition]: {{ site.baseurl }}/docs/fields.html#maximum image size
[`maximum image size` in the configuration]: {{ site.baseurl }}/docs/config.html#maximum image size
[`maximum image size` field modifier]: {{ site.baseurl }}/docs/fields.html#maximum image size
[document caching feature]: {{ site.baseurl}}/docs/documents.html#caching
[`id` and `supersedes`]: {{ site.baseurl}}/docs/modifiers.html#precedence
[`id`]: {{ site.baseurl}}/docs/modifiers.html#precedence
[how **docassemble** finds questions for variables]: {{ site.baseurl }}/docs/logic.html#variablesearching
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`code`]: {{ site.baseurl }}/docs/code.html#code
[PNG]: https://en.wikipedia.org/wiki/Portable_Network_Graphics
[JPEG]: https://en.wikipedia.org/wiki/JPEG_File_Interchange_Format
[BMP]: https://en.wikipedia.org/wiki/BMP_file_format
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`using()`]: {{ site.baseurl }}/docs/objects.html#DAObject.using
[Bootstrap]: http://getbootstrap.com/
[`inverse navbar` configuration directive]: {{ site.baseurl }}/docs/config.html#inverse navbar
[`bootstrap theme` configuration directive]: {{ site.baseurl }}/docs/config.html#bootstrap theme
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`objects_from_file()` function]: {{ site.baseurl}}/docs/functions.html#objects_from_file
[`data`]: #data
[`set_parts()` function]: {{ site.baseurl}}/docs/functions.html#set_parts
[`show login` configuration directive]: {{ site.baseurl }}/docs/config.html#show login
[`url_of()`]: {{ site.baseurl}}/docs/functions.html#url_of
[`menu_items` special variable]: {{ site.baseurl}}/docs/special.html#menu_items
[background tasks]: {{ site.baseurl}}/docs/background.html#background
[`word()`]: {{ site.baseurl}}/docs/functions.html#word
[`prevent_going_back()`]: {{ site.baseurl}}/docs/functions.html#prevent_going_back
[`prevent going back`]: {{ site.baseurl}}/docs/modifiers.html#prevent going back
[`interview help`]: #interview help
[`help`]: {{ site.baseurl}}/docs/modifiers.html#help
[`question help button`]: #question help button
[`main page pre`]: {{ site.baseurl }}/docs/config.html#main page pre
[`main page submit`]: {{ site.baseurl }}/docs/config.html#main page submit
[`main page post`]: {{ site.baseurl }}/docs/config.html#main page post
[`metadata`]: #metadata
[`set_parts()`]: {{ site.baseurl}}/docs/functions.html#set_parts
[`set_language()`]: {{ site.baseurl}}/docs/functions.html#set_language
[`set_progress()`]: {{ site.baseurl}}/docs/functions.html#set_progress
[chart.js]: https://www.chartjs.org/
[Google Charts]: https://developers.google.com/chart/
[`javascript`]: #javascript
[`error help`]: {{ site.baseurl}}/docs/config.html#error help
[Configuration]: {{ site.baseurl}}/docs/config.html
[`debug` directive]: {{ site.baseurl}}/docs/config.html#debug
[Markdown]: https://daringfireball.net/projects/markdown/
[`back button`]: {{ site.baseurl}}/docs/modifiers.html#back button
[`show login` metadata specifier]: #show login
[`show login`]: {{ site.baseurl}}/docs/config.html#show login
[`reconsider()`]: {{ site.baseurl}}/docs/functions.html#reconsider
[jQuery Validation Plugin]: http://jqueryvalidation.org
[`words`]: {{ site.baseurl}}/docs/config.html#words
[`yesno`]: {{ site.baseurl }}/docs/fields.html#fields yesno
[`uncheck others`]: {{ site.baseurl }}/docs/fields.html#uncheck others
[`minlength`]: {{ site.baseurl }}/docs/fields.html#minlength
[`maxlength`]: {{ site.baseurl }}/docs/fields.html#maxlength
[`min`]: {{ site.baseurl }}/docs/fields.html#min
[`max`]: {{ site.baseurl }}/docs/fields.html#max
[`email`]: {{ site.baseurl }}/docs/fields.html#email
[`date`]: {{ site.baseurl }}/docs/fields.html#date
[`datetime`]: {{ site.baseurl }}/docs/fields.html#datetime
[`time`]: {{ site.baseurl }}/docs/fields.html#time
[`accept`]: {{ site.baseurl }}/docs/fields.html#accept
[file upload fields]: {{ site.baseurl }}/docs/fields.html#minlength
[`validation messages`]: {{ site.baseurl }}/docs/fields.html#validation messages
[`combobox`]: {{ site.baseurl }}/docs/fields.html#combobox
[`checkboxes`]: {{ site.baseurl }}/docs/fields.html#fields checkboxes
[DOM]: https://en.wikipedia.org/wiki/Document_Object_Model
[privilege]: {{ site.baseurl }}/docs/users.html
[privileges]: {{ site.baseurl }}/docs/users.html
[screen parts]: {{ site.baseurl }}/docs/questions.html#screen parts
[`defined()`]: {{ site.baseurl}}/docs/functions.html#defined
[`docx template file`]: {{ site.baseurl}}/docs/documents.html#docx template file
[`error help`]: #error help
[`verbose error messages`]: {{ site.baseurl}}/docs/config.html#verbose error messages
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`modules`]: #modules
[`imports`]: #imports
[`process_action`]: {{ site.baseurl}}/docs/functions.html#process_action
[`template`]: #template
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`DAFileCollection`]: {{ site.baseurl }}/docs/objects.html#DAFileCollection
[`DAStaticFile`]: {{ site.baseurl }}/docs/objects.html#DAStaticFile
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`Thing`]: {{ site.baseurl }}/docs/objects.html#Thing
[`pandas`]: https://pandas.pydata.org/
[editing an already-gathered list]: {{ site.baseurl }}/docs/groups.html#editing
[groups]: {{ site.baseurl }}/docs/groups.html
[Documents]: {{ site.baseurl }}/docs/documents.html
[Python expression]: http://stackoverflow.com/questions/4782590/what-is-an-expression-in-python
[label and field]: {{ site.baseurl }}/docs/fields.html#label
[variable name]: {{ site.baseurl }}/docs/fields.html#variable names
[`send_email()`]: {{ site.baseurl}}/docs/functions.html#send_email
[`docassemble.demo:data/templates/hello_template.md`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/templates/hello_template.md
[`docassemble.base:data/questions/examples/template-file.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/examples/template-file.yml
[`docassemble.base:data/templates/disclaimer.md`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/disclaimer.md
[`disclaimer.md`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/disclaimer.md
[expression]: http://stackoverflow.com/questions/4782590/what-is-an-expression-in-python
[Pandoc]: http://johnmacfarlane.net/pandoc/
[`table width`]: #table width
[`features`]: #features
[document]: {{ site.baseurl }}/docs/documents.html
[list]: https://docs.python.org/3.6/tutorial/datastructures.html
[dictionary]: https://docs.python.org/3/library/stdtypes.html#dict
[set]: https://docs.python.org/3/library/stdtypes.html#set
[group]: {{ site.baseurl }}/docs/groups.html
[`label` and `field`]: {{ site.baseurl }}/docs/fields.html#label
[question]: {{ site.baseurl }}/docs/questions.html
[multi-lingual interviews]: {{ site.baseurl }}/docs/language.html
[`default language`]: #default language
[sources]: {{ site.baseurl }}/docs/playground.html#sources
[Download an interview phrase translation file]: {{ site.baseurl }}/docs/admin.html#translation file
[Utilities]: {{ site.baseurl }}/docs/admin.html#utilities
[`new markdown to docx`]: {{ site.baseurl}}/docs/config.html#new markdown to docx
[`DAContext`]: {{ site.baseurl }}/docs/objects.html#DAContext
[`DADateTime`]: {{ site.baseurl }}/docs/objects.html#DADateTime
[`.format_date()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_date
[`.format_time()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_time
[`.format_datetime()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_datetime
[`use objects`]: #use objects
[`session_tags()`]: {{ site.baseurl}}/docs/functions.html#session_tags
[interview]: {{ site.baseurl }}/docs/interviews.html
[section on questions]: {{ site.baseurl }}/docs/questions.html
[standard]: https://getbootstrap.com/docs/4.0/components/forms/#form-groups
[horizontal form]: https://getbootstrap.com/docs/4.0/components/forms/#horizontal-form
[`exitpage`]: {{ site.baseurl}}/docs/config.html#exitpage
[special pages]: {{ site.baseurl }}/docs/questions.html#special buttons
[`command()`]: {{ site.baseurl}}/docs/functions.html#command
[`format_date()`]: {{ site.baseurl}}/docs/functions.html#format_date
[`format_datetime()`]: {{ site.baseurl}}/docs/functions.html#format_datetime
[`format_time()`]: {{ site.baseurl}}/docs/functions.html#format_time
[JSON]: https://en.wikipedia.org/wiki/JSON
[Google Analytics]: https://analytics.google.com
[Segment]: https://segment.com/
[`segment id`]: {{ site.baseurl}}/docs/config.html#segment id
[`analytics id`]: {{ site.baseurl}}/docs/config.html#analytics id
[`google`]: {{ site.baseurl}}/docs/config.html#google
[Font Awesome]: https://fontawesome.com
[`depends on`]: {{ site.baseurl }}/docs/logic.html#depends on
[`undefine()`]: {{ site.baseurl}}/docs/functions.html#undefine
[`invalidate()`]: {{ site.baseurl}}/docs/functions.html#invalidate
[meta tags]: https://en.wikipedia.org/wiki/Meta_element
[`social`]: {{ site.baseurl}}/docs/config.html#social
[`brandname`]: {{ site.baseurl}}/docs/config.html#brandname
[`locale`]: {{ site.baseurl}}/docs/config.html#locale
[`allow robots`]: {{ site.baseurl}}/docs/config.html#allow robots
[Jekyll]: https://jekyllrb.com/
[GitHub Pages]: https://pages.github.com/
[GitHub repository]: {{ site.github.repository_url }}
