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

If a "title" is defined, it will be displayed in the navigation bar in
the web app.  If a "short title" is provided, it will be displayed
in place of the "title" when the size of the screen is small.

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
  user.initializeAttribue(name='case', objectType=Case)
---
{% endhighlight %}

This code is more complicated than normal Python code for object
initialization because the full name of the variable needs to be
supplied to the function that creates and initializes the object.  The
base class `DAObject` keeps track of variable names.

Whenever possible, you should use `objects` blocks rather than code to
initialize your objects.  `objects` blocks are clean and readable.

# <a name="objects from file"></a>Importing `objects from file`

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

# Images

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

# Python modules

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

# <a name="features"></a>Optional `features`

The `features` block sets some optional features of the interview.

## <a name="progress bar"></a>Progress bar

The `progress bar` feature controls whether a progress bar is shown
during the interview.  You can use the [progress] modifier to indicate
the setting of the progress bar.

{% include side-by-side.html demo="progress-features" %}

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
[modifiers]: {{ site.baseurl }}/docs/modifiers.html
[markup]: {{ site.baseurl }}/docs/markup.html
[setting variables]: {{ site.baseurl }}/docs/fields.html
[objects]: {{ site.baseurl }}/docs/objects.html
[def]: http://docs.makotemplates.org/en/latest/defs.html
[roles]: {{ site.baseurl}}/docs/roles.html
[progress]: {{ site.baseurl}}/docs/modifiers.html#progress
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
