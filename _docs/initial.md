---
layout: docs
title: Initial blocks
short_title: Initial Blocks
---

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

A `metadata` block contains information about the [YAML] file, such as
the name of the author.  It must be a [YAML] dictionary, but each the
dictionary items can contain any arbitrary [YAML] structure.

If a `title` is defined, it will be displayed in the navigation bar in
the web app.  If a `short title` is provided, it will be displayed
in place of the `title` when the size of the screen is small.

If you set `unlisted: True` for an interview that has an entry in the
[`dispatch`] list in your [configuration], the interview will be
exempted from display in the interview list available at `/list`.  For
more information about this, see the documentation for the
[`dispatch`] configuration directive.

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
However, the objects you use as variables in your interview [YAML] files
need to inherit from the class `DAObject`.  Otherwise, **docassemble**
might not be able to find the appopriate [`code` blocks] or questions
necessary to define them.  This is because of the way **docassemble**
keeps track of the names of variables.

A code block like this would effectively do the same thing as the
`objects` block above:

{% highlight yaml %}
---
code: |
  spouse = Individual('spouse')
  user.initializeAttribute(name='case', objectType=Case)
---
{% endhighlight %}

This code is more complicated than normal Python code for object
initialization because the full name of the variable needs to be
supplied to the function that creates and initializes the object.  The
base class `DAObject` keeps track of variable names.

In some situations, running `spouse = Individual()` will correctly
detect the variable name `spouse`, but in other situations, the name
cannot be detected.  Running `spouse = Individual('spouse')` will
always set the name correctly.

Whenever possible, you should use `objects` blocks rather than code to
initialize your objects because `objects` blocks are clean and
readable.

<a name="objects from file"></a>Importing `objects from file`

{% highlight yaml %}
---
objects from file:
  - claims: claim_list.yml
---
{% endhighlight %}

An `objects from file` block imports objects or other data elements
that you define in a separate [YAML] data file located in the
[sources folder] of the current package.  If the interview file
containing the `objects from file` block is
`data/questions/manage_claims.yml`, **docassemble** will expect the
data file to be located at `data/sources/claim_list.yml`.

For more information about how this works, and about how to format the
data file, see the documentation for the
[`objects_from_file()` function].  The example above is equivalent to
running `claims = objects_from_file('claim_list.yml', name='claims')`.

# <a name="include"></a>Incorporation by reference: `include`

{% highlight yaml %}
---
include:
  - basic-questions.yml
  - docassemble.helloworld:questions.yml
---
{% endhighlight %}

The `include` statement incorporates the questions in another [YAML]
file, almost as if the contents of the other [YAML] file appeared in
place of the `include` statement.  When the `include`d file is parsed,
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
sets` block, see `decoration` in the [modifiers] section, `buttons`
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

## <a name="imports"></a>Importing module itself: `imports`

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

## <a name="modules"></a>Importing all names: `modules`

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

For information about how to cause **docassemble** to reset variables
set by [`code` blocks], see the [`reconsider` modifier].

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
using the [`id` and `supersedes`] modifiers.

# <a name="terms"></a><a name="auto terms"></a>Vocabulary `terms` and `auto terms`

{% highlight yaml %}
---
terms:
  enderman: |
    A slender fellow from The End who carries enderpearls and picks up
    blocks.
  fusilli: |
    A pasta shape that looks like a corkscrew.
---
{% endhighlight %}

Sometimes you will use vocabulary that the user may or may not know.
Instead of interrupting the flow of your questions to define every
term, you can define certain vocabulary words, and **docassemble**
will turn them into hyperlinks wherever they appear in curly brackets.
When the user clicks on the hyperlink, a popup appears with the word's
definition.

{% include side-by-side.html demo="terms" %}

If you want the terms to be highlighted every time they are used,
whether in curly brackets or not, use `auto terms`.

{% include side-by-side.html demo="auto-terms" %}

You can also use `terms` and `auto terms` as [modifiers], in which
case the terms will apply only to the question, not to the interview
as a whole.

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

You can also add video to help text using the `video` declaration.

See the [modifiers] section for an explanation of how audio and video
file references work.

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
---
modules:
  - docassemble.base.util
---
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
the `default role` statement will define what role or roles will be
required for any question that does not contain an explicit `role`
statement.

When you use the [roles] feature, you need to have some way of telling
your interview logic what the role of the interviewee is.

If you include `code` within the same block as your `default role`
statement, that code will be executed every time the interview logic
is processed, as if it was marked as `initial`.  For this reason, any
`default role` statement that contains code should be placed earlier
in the interview file than and `mandatory` questions or [`code` blocks].

In the example above, the interview has two roles: "client" and
"advocate".  The special variables `user` and `role` are set in the
`code` block, which is executed every time the interview logic is
processed.

In addition, the [`set_info()`] function from
[`docassemble.base.util`] is called.  This lets the linguistic
functions in [`docassemble.base.util`] know who the user is, so that
questions can ask "What is your date of birth?" or "What is John
Smith's date of birth" depending on whether the current user is John
Smith or not.

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

If your interview only supports one language, it is not necessary to
(and probably not a good idea to) set a `default language`.

See [language support] for more information about how to create
multi-lingual interviews.  See [modifiers] for information about the
`language` setting of a question.

# <a name="machine learning storage"></a>Machine learning training data
 
If you use [machine learning] in your interviews, then by default,
**docassemble** will use training data associated with the
particular interview in the particular [package] in which the
interview resides.

If you would like your interview to share training data with another
interview, you can use the `machine learning storage` directive to
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

## <a name="progress bar"></a>Progress bar

The `progress bar` feature controls whether a progress bar is shown
during the interview.  You can use the [`progress`] modifier to indicate
the setting of the progress bar.

{% include side-by-side.html demo="progress-features" %}

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

## <a name="table width"></a>Width of tables in attachments

As explained more fully in the [tables] section, if you include a
[table] in an [`attachment`] and the table is too wide, or not wide
enough, you can change the default character width of tables from 65
to some other value using the `table width` directive within the
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

## <a name="maximum image size"></a>Limiting size of uploaded images

If your users upload digital photos into your interviews, the uploads
may take a long time.  Images can be reduced in size before they are
uploaded.  To require by default for all uploads in your interview,
set `maximum image size` in the `features` block for your interview.

{% include side-by-side.html demo="upload-max-image-size-features" %}

In this example, images will be reduced in size so that they are no
taller than 100 pixels and no wider than 100 pixels.

This is just a default value; you can override it by setting the
[`maximum image size` in a field definition].

If you have an interview-wide default, but you want to override it for
a particular field to allow full-resolution camera uploads, you can
set the [`maximum image size` field modifier] to `None`.

If you want to use a site-side default value, set the
[`maximum image size` in the configuration].

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
   
[infinite loop protection]: {{ site.baseurl }}/docs/config.html#loop limit
[ending screen]: {{ site.baseurl }}/docs/questions.html#ending screens
[`device()`]: {{ site.baseurl }}/docs/functions.html#device
[exit button]: {{ site.baseurl }}/docs/questions.html#special buttons
[`referring_url()`]: {{ site.baseurl }}/docs/functions.html#referring_url
[iframe]: https://www.w3schools.com/TAgs/tag_iframe.asp
[`pdf/a` attachment setting]: {{ site.baseurl }}/docs/document.html#pdfa
[`pdf/a` configuration directive]: {{ site.baseurl }}/docs/config.html#pdfa
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
[table]: {{ site.baseurl }}/docs/template.html#table
[tables]: {{ site.baseurl }}/docs/template.html#table
[`ready()`]: https://api.jquery.com/ready/
[Ajax]: https://en.wikipedia.org/wiki/Ajax_(programming)
[jQuery]: https://jquery.com/
[package]: {{ site.baseurl }}/docs/packages.html
[`html`]: {{ site.baseurl }}/docs/fields.html#html
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
[Mako]: http://www.makotemplates.org/
[language support]: {{ site.baseurl }}/docs/language.html
[multiple languages]: {{ site.baseurl }}/docs/language.html
[modifiers]: {{ site.baseurl }}/docs/modifiers.html
[markup]: {{ site.baseurl }}/docs/markup.html
[setting variables]: {{ site.baseurl }}/docs/fields.html
[objects]: {{ site.baseurl }}/docs/objects.html
[def]: http://docs.makotemplates.org/en/latest/defs.html
[roles]: {{ site.baseurl}}/docs/roles.html
[`progress`]: {{ site.baseurl}}/docs/modifiers.html#progress
[`language` modifier]: {{ site.baseurl}}/docs/modifiers.html#language
[`include`]: {{ site.baseurl}}/docs/initial.html#include
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`docassemble.base.legal`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
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
