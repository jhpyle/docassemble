---
layout: docs
title: Initial Blocks
short_title: Initial Blocks
---

# <a name="metadata"></a>Interview Title and Other `Metadata`

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

If a `title` is defined, it will be displayed in the navigation bar in
the web app.  If a `short title` is provided, it will be displayed
in place of the `title` when the size of the screen is small.

If a `logo` is defined, it will be displayed in the navigation bar in
the web app in place of the `title` and `short title`.  The content of
the `logo` should be raw [HTML].  If you include an image, you should
size it to be about 20 pixels in height.

If a `tab title` is provided, it will be displayed as the title
of the browser tab.  Otherwise, the `title` will be used.

If a `subtitle` is provided, it will be displayed as the subtitle of
the interview in the "Interview Sessions" list available to a logged-in user
at `/interviews`.

These titles can be overridden using the [`set_title()` function].

The `metadata` block and the [`set_title()` function] can be used to
modify other aspects of the navigation bar.

<a name="exit link"></a>If an `exit link` is provided, the behavior of
the "Exit" link can be altered.  (The "Exit" menu option is displayed
when the [`show login` configuration directive] is set to `False` or
the [`show login` metadata component] for an interview is set to
`False`.)  The value can be either `exit` or `leave.` If it is `exit`,
then when the user clicks the link, they will be logged out (if they
are logged in) and their interview session answers will be deleted from the
server.  If it is `leave`, the user will be logged out (if they are
logged in), but the interview session answers will not be deleted from the
server.  It can be important to keep the interview session answers on the
server if [background tasks] are still running.

<a name="exit label"></a>If `exit label` is provided, the given text
will be used in place of the word "Exit" on the "Exit" menu option.
This text is passed through the [`word()`] function, so that it can be
translated into different languages.

If you set `unlisted: True` for an interview that has an entry in the
[`dispatch`] list in your [configuration], the interview will be
exempted from display in the list of interview available at `/list`.  For
more information about this, see the documentation for the
[`dispatch`] configuration directive.

<a name="pre"></a><a name="submit"></a><a name="post"></a>The
[`metadata`] block also accepts the components `pre`, `submit`, and
`post`.  You can use these to provide raw [HTML] that will be inserted
into the page before the [`question`] heading, before the buttons, and
after the buttons, respectively.  You can also set server-wide
defaults for these values using the [`main page pre`], [`main page
submit`], and [`main page post`] directives in the [Configuration].
You can also customize these values with the [`set_title()`] function.

<a name="error help">The [`metadata`] block also accepts the component
`error help`.  This is [Markdown]-formatted text that will be included
on any error screen that appears to the user during the interview session.
You can also provide this text on a server-wide basis using the
[`error help`] directive in the [Configuration].

{% include side-by-side.html demo="error-help" %}

<a name="show login">The [`metadata`] block also accepts the component
`show login`, which can be `true` or `false`.  This controls whether
the user sees a "Sign in or sign up to save answers" link in the upper
right-hand corner during the interview session.  If `show login` is not
specified in the [`metadata`] block, the [Configuration] directive [`show
login`] determines whether this link is available.

{% include side-by-side.html demo="show-login" %}

# <a name="objects"></a>Creating `objects`

{% highlight yaml %}
---
objects:
  - spouse: Individual
  - user.case: Case
---
{% endhighlight %}

An `objects` block creates objects that may be referenced by your
DALang.  See [objects] for more information about objects in
[DALang].

If your DALang references the variable `spouse`, it
will find the above `objects` block and process it.  It will define
`spouse` as an instance of the object class `Individual` and define
`user.case` as an instance of the object class `Case`.

The use of objects when building your interviews is highly encouraged.
However, the objects you use as variables in your [DALang] files
need to inherit from the class `DAObject`.  Otherwise, your Steward
might not be able to find the appopriate [`code` blocks] or questions
necessary to define them.  This is because of the way Stewards
keep track of the names of variables.

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
that you define in a separate [DALang] data file located in the
[sources folder] of the current Steward.  If the DALang file
containing the `objects from file` block is
`data/questions/manage_claims.yml`, the Steward will expect the
data file to be located at `data/sources/claim_list.yml`.

For more information about how this works, and about how to format the
data file, see the documentation for the
[`objects_from_file()` function].  The example above is equivalent to
running `claims = objects_from_file('claim_list.yml', name='claims')`.

# <a name="include"></a>Incorporation by Reference: `include`

{% highlight yaml %}
---
include:
  - basic-questions.yml
  - docassemble.helloworld:questions.yml
---
{% endhighlight %}

The `include` block incorporates the questions in another [DALang]
file, almost as if the contents of the other DALang file appeared in
place of the `include` block.  When the `include`d file is parsed,
files referenced within it will be assumed to be part of the Steward containing the
`include`d file.

When a filename is provided without specifying a Steward, the Steward conducting the interview session
will look first in its own `data/questions` directory
(i.e., the package within which the [DALang] file being read is
located), and then in the `data/questions` directory of
[`docassemble.base`].

You can include [DALang] files from other Stewards by explicitly
referring to that Steward's name.  E.g.,
`docassemble.helloworld:questions.yml` refers to the DALang file
`questions.yml` in the `docassemble/helloworld/data/questions`
directory of the Steward named [helloworld].

# <a name="im"></a>Images

## <a name="image sets"></a>With Attribution: `image sets`

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
of the Steward in which the [DALang] file is located.

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
sets` block, see `decoration` in the [modifier components] section, `buttons`
in the [setting variables] section, and "Inserting inline icons" in
the [markup] section.

## <a name="images"></a>Without Attribution: `images`

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

# <a name="mods"></a>Python Modules

## <a name="imports"></a>Importing Modules: `imports`

{% highlight yaml %}
---
imports:
  - datetime
  - us
---
{% endhighlight %}

`imports` loads a [Python module] name into the namespace in which your
code and question templates are evaluated.  The example above is
equivalent to running the following Python code:

{% highlight python %}
import datetime
import us
{% endhighlight %}

## <a name="modules"></a>Importing All Names: `modules`

{% highlight yaml %}
---
modules:
  - datetime
---
{% endhighlight %}

Like `imports`, `modules` loads [Python modules] into the namespace in
which your code and question templates are evaluated, except that it
imports all of the names that the module exports.  The example above
is equivalent to running the following Python code:

{% highlight python %}
from datetime import *
{% endhighlight %}

# <a name="data"></a>Storing Structured `data` in a Variable

The `data` block allows you to specify a data structure in [YAML] in a
block and have it available as a [Python] data structure.

For example, in this Steward we create a [Python] list and then
re-use it in two questions to offer a multiple-choice list.

{% include side-by-side.html demo="data-simple" %}

In [Python], the variable `fruits` is this:

{% highlight python %}
[u'Apple', u'Orange', u'Peach', u'Pear']
{% endhighlight %}

You can also use the `data` block to create more complex data
structures.  You can also use [Mako] in the data structure.

{% include side-by-side.html demo="data" %}

You can also import data from [DALang] files using the
[`objects_from_file()` function].

# <a name="data from code"></a>Storing Structured `data` in a Variable using Code

The `data from code` block works just like the [`data`] block, except
that [Python] code is used instead of text or [Mako] markup.

{% include side-by-side.html demo="data-code" %}

# <a name="reset"></a>Keeping Variables Fresh: `reset`

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

# <a name="order"></a>Changing Order of Precedence

As explained in [how a Steward finds questions for variables],
if there is more than one [`question`] or [`code`] block that offers
to define a particular variable, blocks that are later in the [DALang]
file will be tried first.

If you would like to specify the order of precedence of blocks in a
more explicit way, so that you can order the blocks in the [DALang] file
in whatever way you want, you can tag two or more blocks with [`id`]s
and insert an `order` block indicating the order of precedence of the
blocks.

For example, suppose you have a Steward with two blocks that could
define the variable `favorite_fruit`.  Normally, the Steward will
try the the second block first because it appears later in the [DALang]
file; the second block will "override" the first.

{% include side-by-side.html demo="supersede-regular" %}

However, if you actually want the first block to be tried first, you
can manually specify the order of blocks:

{% include side-by-side.html demo="supersede-order" %}

Another way to override the order in which blocks will be tried is by
using the [`id` and `supersedes`] components.

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
term, you can define certain vocabulary words, and the Steward
will turn them into hyperlinks wherever they appear in curly brackets.
When the user clicks on the hyperlink, a popup appears with the word's
definition.

{% include side-by-side.html demo="terms" %}

If you want the terms to be highlighted every time they are used,
whether in curly brackets or not, use `auto terms`.

{% include side-by-side.html demo="auto-terms" %}

You can also use `terms` and `auto terms` as [modifier components], in which
case the terms will apply only to the question, not to the Steward
as a whole.

# <a name="sections"></a>Defining the Sections for the Navigation Bar

You can use the [`navigation bar`] feature or the
[`nav.show_sections()`] function to show your users the "sections" of
the interview session and what the current section of the interview session is.

Here is a complete example.

{% include side-by-side.html demo="sections" %}

Subsections are supported, but only one level of nesting is allowed.

If your Steward is [multilingual], you can specify more than
one `sections` block and modify each one with a `language` component:

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

In the example above, the [`section`] component referred to sections
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

# <a name="interview help"></a>Assisting Users with `interview help`

{% highlight yaml %}
---
interview help:
  heading: How to use this web site
  content: |
    Answer each question.  At the end, you will get a prize.
---
{% endhighlight %}

An `interview help` block adds text to the "Help" page of every
question in the interview session.  If the question has `help` text of its
own, the `interview help` will appear after the question-specific
help.

You can also add audio to your Steward's interview help:

{% highlight yaml %}
---
interview help:
  heading: How to use this web site
  audio: answer_each_question.mp3
  content: |
    Answer each question.  At the end, you will get a prize.
---
{% endhighlight %}

You can also add video to your Steward's help text using the `video` component.

See the [modifier components] section for an explanation of how audio and video
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

# <a name="def"></a>Mako Functions: `def`

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

Due to the way Stewards operate, the `def` block
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

If your Steward uses the [roles] feature for multi-user interviews,
the `default role` component will define what role or roles will be
required for any question that does not contain an explicit `role`
component.

When you use the [roles] feature, you need to have some way of telling
your Steward what the role of the interviewee is.

If you include a `default role` component within a `code` block or within a block with a `code` component,
that code will be executed every time the Steward
is accessed, as if it was marked as `initial`.  For this reason, any
block with the `default role` component that also contains `code` should be placed earlier
in the DALang file than and `mandatory` questions or [`code` blocks].

In the example above, there are two roles: "client" and
"advocate".  The special variables `user` and `role` are set in the
`code` block, which is executed every time the Steward is accessed.

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
the file for which the [`language` component] is not specified.  The
purpose of this is to save typing; otherwise you would have to set the
[`language` component] for each question.  Note that this does not extend to
questions in [`include`]d files.

If your Steward only speaks one language, it is not necessary to
(and probably not a good idea to) set a `default language`.

See [language support] for more information about how to create
multilingual Steward.  See [modifier components] for information about the
`language` setting of a question.

# <a name="machine learning storage"></a>Machine Learning Training Data
 
If you use the Docassemble Framework's [machine learning] features, then by default,
your Steward will use training data associated with its own [package].

If you would like a Steward to share training data accross its
interviews, you can use the `machine learning storage` configuration directive to
point to the training data of another interview that Steward offers.

For example, suppose you have developed a Steward with the [DALang] file
`child_custody.yml` that uses [machine learning], and you have built
rich training sets for variables within this interview.  Then you
decide to develop another interview for this same Steward, called
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
directory of the Steward's [package].  This file contains the training data for
the `child-custody.yml` interview.  The naming convention for these
data files is to add `ml-` to the beginning of the interview's [DALang] file
and replace `.yml` with `.json` at the end.

Now, both the Steward's interview files, `child-custody.yml` and `child-support.yml`,
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
corresponds with the Steward conducting both interviews, such as a Family Law Steward. You could
include `machine learning storage: ml-family-law.json` in both the
`child-custody.yml` and `child-support.yml` interviews.  Even though
there is no [DALang] file named `family-law.yml` for your Family Law Steward, this will still work.
If you are using the [Playground], a file called `ml-family-law.json`
will automatically be created in the `Sources folder`.

You can also share "storage" areas between Stewards.  Suppose you are
working within a Steward named `docassemble.missourifamilylaw`, but
you want to take advantage of training sets in a Steward named
`docassemble.generalfamilylaw`.  You can write:

{% highlight yaml %}
---
machine learning storage: docassemble.generalfamilylaw:data/sources/ml-family.json
---
{% endhighlight %}

For more information about managing training data, see the
[machine learning] section on [packaging your training sets]

# <a name="features"></a>Optional `features`

The `features` block sets some optional features for your Stewards.

## <a name="debug"></a>Whether Debugging Features are Available

If the [`debug` directive] in the [Configuration] is `True`, then by
default, the navigation bar will contain a "Source" link that shows
information about how the Steward arrived at the question being
shown.  If the [`debug` directive] is `False`, then this will not be
shown.

This can be overridden in the `features` by setting `debug` to `True`
or `False` depending on the behavior you want.

The following example demonstrates turning the `debug` feature off.

{% include side-by-side.html demo="debug-mode" %}

On the [server] that hosts the demonstration Stewards, the [`debug`
directive] is `True`, so the "Source" link is normally shown.  Setting
`debug: False` makes the "Source" link disappear.

## <a name="centered"></a>Whether Interview Questions are Centered

If you do not want your interview questions to be centered on the screen, set
`centered` to `False`.

{% include side-by-side.html demo="centered" %}

## <a name="progress bar"></a>Progress Bar

The `progress bar` feature controls whether a progress bar is shown
during the interview session.  You can use the [`progress`] component or the
[`set_progress()`] function to indicate the setting of the progress
bar.

{% include side-by-side.html demo="progress-features" %}

If you want the progress bar to display the percentage, include `show
progress bar percentage: True`:

{% include side-by-side.html demo="progress-features-percentage" %}

## <a name="navigation bar"></a>Navigation Bar

The `navigation` feature controls whether a navigation bar is
shown during the interview session.  You can use the [`sections`] initial
block or the [`nav.set_sections()`] function to define the sections of
your interview.  The [`section`] component or the [`nav.set_section()`]
function can be used to change the current section.

{% include side-by-side.html demo="sections" %}

Note that the section list is not shown on small devices, such as
smartphones.  To show a smartphone user a list of sections, you can
use the [`nav.show_sections()`] function.

If you want the navigation bar to be horizontal across the top of the
page, set `navigation` to `horizontal`:

{% include side-by-side.html demo="sections-horizontal" %}

## <a name="question back button"></a><a name="navigation back button"></a>Back Button Style

By default, there is a "Back" button located in the upper-left corner
of the page.  (However, the "Back" button is not present when the user
is on the first page of an interview session, or the [`prevent_going_back()`]
function has been used, or the [`prevent going back`] component is in
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
some questions but not others, using the [`back button`] component.

## <a name="question help button"></a>Help Tab Style

When [`interview help`] is available, or the [`help`] component is
present on a question, the "Help" tab will be present in the
navigation bar.  When the [`help`] component is present, the "Help" tab
is highlighted yellow and marked with a yellow star.  When the user
presses the help tab, the help screen will be shown.

If you set the `question help button` to `True`, users will be able to
access the help screen by pressing a "Help" button located within the
body of the question, to the right of the other buttons on the page.
When `question help button` is `True`, the "Help" tab will not be
highlighted yellow.

Here is a Steward in which the `question help button` is not
enabled (which is the default).

{% include side-by-side.html demo="question-help-button-off" %}

Here is the same Steward, with the `question help button` feature
enabled:

{% include side-by-side.html demo="question-help-button" %}

Note that when `question help button` is enabled, the label for the
help tab in the navigation bar always defaults to "Help" or to the
`label` of the [`interview help`], and it is not highlighted yellow
when question-specific help is available.

## <a name="hide standard menu"></a>Hiding the Standard Menu Items

By default, the menu in the corner provides logged-in users with the
ability to edit their "Profile" and the ability to go to "My
Interviews," which is a list of interview sessions that have been
started with Stewards on that [server].  If you want to disable these links, you can use the `hide
standard menu` component:

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

## <a name="javascript"></a><a name="css"></a>Javascript and CSS Files

If you are a web developer and you know how to write [HTML],
[Javascript], and [CSS], you can embed [HTML] in your interview text.
You can also bring [Javascript] and [CSS] files into the user's
browser.

For example, the following Steward brings in a [Javascript] file,
[`my-functions.js`], and a [CSS] file, [`my-styles.css`], into the
user's browser.  These files are located in the `data/static` folder
of the Steward's [package].

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
the interview session is loaded, attach a [jQuery] event handler to `document`
for the event `daPageLoad`, which is a Docassemble Framework specific event
that is triggered after each screen loads.  (Since Stewards
use [Ajax] to load each new screen, if you attach code using
[jQuery]'s [`ready()`] method, the code will run when the browser
first loads, but not every time the user sees a new screen.)  The
example above demonstrates this; every time the page loads, the code
will replace the contents of any element with the class `groovy`.

This example demonstrates bringing in [CSS] and [Javascript] files that
are located in the `data/static` directory of the Steward conducting the
interview session.  However, you can also refer to files in another Steward's package:

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
question, rather than in all questions of an interview you can use
the [`script`] and [`css`] component.

### <a name="charts"></a>Example use of JavaScript: Charting

Here is an example Steward that uses a [`javascript`] feature and a
[`script`] component to draw a doughnut chart using [chart.js].

{% include side-by-side.html demo="chart" %}

Here is an example Steward that draws a pie chart using [Google Charts].

{% include side-by-side.html demo="googlechart" %}

## <a name="bootstrap theme"></a>Bootstrap Theme

Using the `bootstrap theme` feature, you can change the look and feel
of your Steward's web interface by instructing your Steward to use
a non-standard [CSS] file in place of the standard [CSS] file used by
[Bootstrap].

{% include demo-side-by-side.html demo="bootstrap-theme" %}

The file can be referenced in a number of ways:

* `lumen.min.css`: the file `lumen.min.css` in the "static" folder of
  the current Steward.
* `docassemble.demo:lumen.min.css`: the file `lumen.min.css` in the
  "static" folder (`data/static/`) of the Steward `docassemble.demo`.
* `docassemble.demo:data/static/lumen.min.css`: the same as above.
* `https://bootswatch.com/lumen/bootstrap.min.css`: a file on the internet.

For more information about using custom [Bootstrap] themes, and for
information about applying themese on a global level, see the
documentation for the [`bootstrap theme` configuration directive].

## <a name="inverse navbar"></a>Inverted Bootstrap Navbar

By default, the Docassemble Framework uses [Bootstrap]'s "dark" (formerly known
as "inverted") style of navigation bar so that the navigation bar
stands out from the white background.  If you do not want to use the
inverted navbar, set the `inverse navbar` feature to `False`.

{% include side-by-side.html demo="inverse-navbar" %}

To make this change at a global level, see the
[`inverse navbar` configuration directive].

## <a name="table width"></a>Width of Tables in Attachments

As explained more fully in the [tables] section, if you include a
[table] in an [`attachment`] and the table is too wide, or not wide
enough, you can change the default character width of tables from 65
to some other value using the `table width` component within the
`features` block.

{% highlight yaml %}
features:
  table width: 75
{% endhighlight %}

## <a name="cache documents"></a>Disabling Document Caching

By default, Stewards cache assembled documents for performance
reasons.  To disable the [document caching feature] for a given
interview, set `cache documents` to `False`.

{% highlight yaml %}
features:
  cache documents: False
{% endhighlight %}

## <a name="pdfa"></a>Producing PDF/A Files

If you want the [PDF] files produced by your Steward to be in
[PDF/A] format, you can set this as a default:

{% highlight yaml %}
features:
  pdf/a: True
{% endhighlight %}

The default is determined by the [`pdf/a` configuration directive].
The setting can also be made on a per-attachment basis by setting the
[`pdf/a` attachment setting].

## <a name="maximum image size"></a>Limiting size of Uploaded Images

If your users upload digital photos to a Steward, the uploads
may take a long time.  Images can be reduced in size before they are
uploaded.  To require by default for all uploads in an interview,
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
set the [`maximum image size` field component] to `None`.

If you want to use a [server]-wide default value, set the
[`maximum image size` in the configuration].

## <a name="go full screen"></a>Going Full Screen when Steward is Embedded

It is possible to embed a Steward in a web page
using an [iframe].  However, the user experience on mobile is degraded
when a Steward is embedded.

If you want the Steward to switch to "full screen" after the user
moves to the next screen in the embedded interview session, you can do so.
Within a `features` block, include `go full screen: True`.

{% include side-by-side.html demo="exit-url-referer-fullscreen" path="/static/test-iframe.html" %}

For more information about implementing an embedded Stewards like
this, see the [HTML source of the web page used in this example]({{ site.github.repository_url }}/blob/gh-pages/static/test-iframe.html){:target="_blank"}.

Note that in this example, the user is provided with an [exit button]
at the end of the interview session that directs the user back to the page
that originally embedded the Steward.  This is accomplished by
setting the `url` of the [exit button] to the result of the
[`referring_url()`] function.

If you only want the Steward to go full screen if the user is using
a mobile device, use `go full screen: mobile`.

{% include side-by-side.html demo="exit-url-referer-fullscreen-mobile" path="/static/test-iframe-mobile.html" %}

Note that this example provides a different [ending screen] depending
on whether the user is on a desktop or a mobile device.  If a desktop
user is viewing the Steward in an [iframe] on a web site, the
Steward should not provide an exit button that takes the user to a
web site, because then the user will see a web site embedded in a web
site.  The Steward in this example uses the [`device()`] function to
detect whether the user is using a mobile device.  Note that the
Steward looks both at `device().is_mobile` as well as
`device().is_tablet`.  This corresponds with the functionality of `go
full screen: mobile`, which will make the Steward go full screen if
the user has either a mobile phone or a tablet.

## <a name="loop limit"></a><a name="recursion limit"></a>Infinite Loop Protection

The [infinite loop protection] section of the [configuration]
documentation explains how you can change the default limits on
recursion and looping for all Stewards on the [server].

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
[`pdf/a` attachment setting]: {{ site.baseurl }}/docs/documents.html#pdfa
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
[multilingual]: {{ site.baseurl }}/docs/language.html
[modifier components]: {{ site.baseurl }}/docs/modifiers.html
[markup]: {{ site.baseurl }}/docs/markup.html
[setting variables]: {{ site.baseurl }}/docs/fields.html
[objects]: {{ site.baseurl }}/docs/objects.html
[def]: http://docs.makotemplates.org/en/latest/defs.html
[roles]: {{ site.baseurl}}/docs/roles.html
[`progress`]: {{ site.baseurl}}/docs/modifiers.html#progress
[`language` component]: {{ site.baseurl}}/docs/modifiers.html#language
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
[`reconsider` component]: {{ site.baseurl}}/docs/logic.html#reconsider
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
[how a Steward finds questions for variables]: {{ site.baseurl }}/docs/logic.html#variablesearching
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`code`]: {{ site.baseurl }}/docs/code.html#code
[PNG]: https://en.wikipedia.org/wiki/Portable_Network_Graphics
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`using()`]: {{ site.baseurl }}/docs/objects.html#DAObject.using
[Bootstrap]: http://getbootstrap.com/
[`inverse navbar` configuration directive]: {{ site.baseurl }}/docs/config.html#inverse navbar
[`bootstrap theme` configuration directive]: {{ site.baseurl }}/docs/config.html#bootstrap theme
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`objects_from_file()` function]: {{ site.baseurl}}/docs/functions.html#objects_from_file
[`data`]: #data
[`set_title()` function]: {{ site.baseurl}}/docs/functions.html#set_title
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
[`set_title()`]: {{ site.baseurl}}/docs/functions.html#set_title
[`set_progress()`]: {{ site.baseurl}}/docs/functions.html#set_progress
[chart.js]: https://www.chartjs.org/
[Google Charts]: https://developers.google.com/chart/
[`javascript`]: #javascript
[`error help`]: {{ site.baseurl}}/docs/config.html#error help
[Configuration]: {{ site.baseurl}}/docs/config.html
[`debug` directive]: {{ site.baseurl}}/docs/config.html#debug
[Markdown]: https://daringfireball.net/projects/markdown/
[`back button`]: {{ site.baseurl}}/docs/modifiers.html#back button
[`show login` metadata component]: #show login
[`show login`]: {{ site.baseurl}}/docs/config.html#show login
[`reconsider()`]: {{ site.baseurl}}/docs/functions.html#reconsider
[Python module]: https://docs.python.org/2/tutorial/modules.html
[Python modules]: https://docs.python.org/2/tutorial/modules.html
[DALang]: {{ site.baseurl }}/docs/interviews.html#yaml
[server]: {{ site.baseurl }}/docs/installation.html
[helloworld]: {{ site.baseurl }}/docs/helloworld.md