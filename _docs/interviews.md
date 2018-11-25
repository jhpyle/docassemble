---
layout: docs
title: Steward Web Apps
short_title: Stewards
---

# <a name="whatis"></a>What is a Steward?

A Steward is a web application on the Docassemble Framework. It is written in a
[domain specific language] called [DALang] that is based on [Python].
The Steward reads this DALang and based on what it finds,
it asks questions of the user(s) during an interview session.

Stewards store users' answers in [variables].  The values
of these variables can be incorporated into future [questions]
and into deliverables, such as [generated documents] or an API call to
another web application like [Zapier].

The Steward can ask users different questions based on the answers
a user gave to previous questions. Therefore, not every interview session with a Steward is identical.

# <a name="simple interview"></a>Example of a Steward

A Steward is fundamentally comprised of a series of possible questions that could
potentially be asked, arranged in no particular order.  Which
questions will be asked, and the order in which they are asked, will
be determined by the Steward.  All you need to do is give
the Steward an objective. Both of which are accomplished in [DALang]. 

The objective might be as simple as "show the exit screen."  This will
instruct the Steward to try to show the exit screen.  But
the Steward will doubtless find that in order to show the exit
screen, it will need some other pieces of information.  It will look for a
question in the [DALang] that will provide that information, and it
will try to ask that question.  But it may find that in order to ask
that question, it needs to know another piece of information, and it
will look for a question that provides that information, and so forth
and so on.  The first question will turn out to be something basic,
like "What is your name?" and the Steward might not reach the exit
screen until 20 questions have been asked and answered.
This is called [backward chaining].

In addition to questions, [DALang] can contain bits of logic,
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

If the Steward ever needs to know the recommended health insurance, it will
need to run this code.  If it does not know the user's age, it will need to ask.
If the user is under 65, the Steward will need to ask questions to determine
whether the household is low income.

[DALang] is stored in the [YAML] file format, and a Steward is made up of 
multiple "blocks" each separated by `---`.  For example, this Steward has three blocks:

{% include side-by-side.html demo="animal" %}

The first block is a "question" that defines the variable `favorite_animal`.

The second block is a "question" that defines the variable `favorite_vegetable`.

The third block is a "question" that is marked as `mandatory`.  This
is not really a question, since it offers the user no option except
clicking the "Exit" button.  It refers to the variable `favorite_animal`.

When the Steward is run by a user, it does the following steps: 

1. It scans the DALang file and processes everything that is "[`mandatory`]."
  It treats everything else as optional.
2. It finds a [`mandatory`] question in the third block and tries to
   ask the question.
3. It can't assemble the question because `favorite_animal` is not defined,
so it looks for a question that defines `favorite_animal`.
4. It looks through the other blocks for a question that defines
`favorite_animal`, and finds it in the first block.
5. It asks the user for his or her favorite animal, and goes back to
step 1.  This time around, it is able to ask the `mandatory` question,
and the Steward stops there because the only thing the user can do
is press the "Exit" button.

The order of the blocks in the file is irrelevant; the Steward
would follow the same steps regardless of the order of the blocks.

Note that the second block, containing the question about the user's
favorite vegetable, was never used because it was never needed.

This is a very simple Steward; there are more types of blocks that
you can write.  These blocks are explained in the following sections:

* [Initial Blocks] - Explains special blocks you can write that make the Steward
  behave in certain ways.
* [Question Blocks] - Explains the basics of the [`question`] blocks, which presents a
  screen to the user (which usually asks a question but does not need to).
* [Question Blocks: Fields] - Explains how to collect information from users
  interacting with `question` blocks.
* [Question Blocks: Modifiers] - Explains ways you can enhance questions with
special features, for example by adding help text or icons.
* [Code Blocks] - Explains `code` blocks, which are like `question`s except
  that instead of presenting something to the user, they run [Python]
  code that defines variables or does other things that computer code
  can do.
* [Interview Flow] - Explains [`mandatory`] and [`initial`] blocks and how
  a Steward will process your [DALang].
* [Objects] - Explains the use of Python objects to simplify the way
  information is organized.
* [Markup] - Explains how to format text in DALang.
* [Template Blocks] - Explains `template` blocks, which allow you to assign
  data to a variable and then include that variable into future question
  or in document generation.
* [Functions] - Explains how to use special [Python] functions to
  simplify and generalize the way questions are asked.
* [Documents] - Explains how to generate documents for users and/or counsel
  in PDF, DOCX, and RTF format, based on the answers provided to the Steward.
* [Roles] - Explains features for interviews involving multi-users.
* [Reserved Names] - Lists the variable names you aren't allowed to use
  because they would conflict with the functionality of
  the Docassemble Framework and [Python].
* [Special Variables] - Describes variables that have special properties.
* [Errors] - Explains some common error messages and how to avoid them.

# <a name="invocation"></a>How to Run a Steward

A Steward must be hosted on a [server]; a server is a single instance of
the Docassemble Framework, running locally or in the cloud.
In either case, a server can host many Stewards at once, a Steward can perform multiple different interviews, and a Steward can conduct many interview sessions for any particular interview simultaniously.
Users can begin an interview session with a Steward by going to the URL for that particular interview.
This is the URL of the Steward's host server appended with the `/interview` path and the
`i` URL parameter set to the path for the DALang file of that interview.

For example, the [demo Steward], which is hosted on the [server] at
`demo.docassemble.org`, can be accessed with this URL.

[{{ site.demourl }}/interview?i=docassemble.demo:data/questions/questions.yml]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/questions.yml){:target="_blank"}

The file path is
`docassemble.demo:data/questions/questions.yml`.  This tells
the Docassemble Framework to look for a Steward named `demo`
and then within it, look for the interview file `questions.yml`
located in the subdirectory `data/questions`.

Stewards are simply Python [packages]. You can make your own Stewards
and then install them on any [server].
If the URL of your server is `Steward.example.com`, the name of
your Steward is `mySteward`, and the name of the interview
file is `myDALang.yml`, your users can access the
Steward at:

> https://interview.example.com/interview?i=docassemble.mySteward:data/questions/myDALang.yml

Note that the naming convention for Python namespace [packages] is such that the full name
for your Steward, `mySteward`, is actually `docassemble.mySteward`.  Likewise all Stewards' full names
will have `docassemble.` prepended to them.

While you are interacting with a Steward, the URL in the location
bar will change.  It will end with `#page1`, then `#page2`, then
`#page3`, etc., as the Steward progresses.  These tags have no
effect except to allow the user to click the browser's back button in
order to go back one screen. They aren't specifically linked to any particular block for that Steward.

If you want to give users a list of interviews avaliable on the [server],
there is a special page located at `/list`, which displays a [list of interviews].

> https://interview.example.com/list

This list is not automatically-generated.  You need to configure the
list using the [`dispatch`] configuration directive.  The list of
interviews can also be [embedded] into a page of another web site.
This page is highly [configurable].  You can also replace the default
`/list` page with your own Steward using the [`dispatch interview`]
configuration directive.  Within that Steward, you can use the
[`interview_menu()`] function to present a list of interviews
in whatever way you want.

The [`dispatch`] configuration directive also allows your users to
access specific interviews at human-readable URLs like:

> https://interview.example.com/start/eviction<br>
> https://interview.example.com/start/namechange

If the user visits the main (or "root") URL for the site, e.g.,
`https://interview.example.com`, the user will be redirected to the
URL indicated by the [`root redirect url`] configuration directive.
A typical way to use this feature is to direct users to a web site
outside of the Docassemble Framework where they can find out information about
the services you offer.

If you don't have a [`root redirect url`] set, the user will be
redirected to `/interview` and will start the interview indicated by
the [`default interview`] configuration directive.

This can be useful when you have one primary interview on your server
and you want users to be able to start it by visiting an easy-to-type
URL such as:

> https://interview.example.com

If you have set [`root redirect url`], your
[`default interview`] will still be accessible at:

> https://interview.example.com/interview

If you do not have a [`default interview`], but you have configured a
`/list` page using the [`dispatch`] configuration directive, then the
user who visits the "root" URL of your site will be redirected to
`/list`.

However, if the user had previously been in another interview session
during the same browser session, going to
`https://interview.example.com/` (without a [`root redirect url`]) or
`https://interview.example.com/interview` will resume the original
interview session.

If you want your users who are in the middle of an interview session with a Steward
to be able to begin a different interview session with the same or a different Steward,
you can enable [`show dispatch link`] in the [configuration],
and then in the menu, the user will see
a link called "Available Interviews," which directs to your `/list`
page.  You can also use the [`menu_items` special variable] within an
interview session to provide options on the pull-down menu for starting a different interview.

Or if you want a single Steward to perform multiple different interviews,
within the body of an interview question you can insert
a link to another interview using the [`interview_url()`] function
with an `i` parameter indicating the interview.

## <a name="iframe"></a>Embedding a Steward into a Web Page

You can embed a Steward into a web page by inserting an [iframe]
into the [HTML] of the page.

{% highlight html %}
<iframe style="width: 500px; height: 700px;" src="https://demo.docassemble.org/interview?i=docassemble.demo:data/questions/questions.yml&reset=1"></iframe>
{% endhighlight %}

You should adjust the width and height of the [iframe] based on what
makes sense for the web page.  The Docassemble Framework can handle a variety of
sizes, but make sure you test the user experience both on desktop
and on mobile.  Since embedded Stewards are often less than ideal for
mobile users, you can use the [`go full screen`] feature to cause the
Steward to "go full screen" on the user's device once the user
starts interacting with it.

## <a name="reset"></a>Restarting an Interview Session

Stewards use browser cookies to keep track
of the user's current interview session.  If the user starts an
interview session with a Steward, then navigates to a different page, and then navigates to
`/interview` on the [server] with no URL parameters, or
with an `i` parameter that is the same as the `i` parameter of the
current interview session, the user will be redirected to where they left
off in the previous interview session.

<a name="new_session"></a>If you want to be able to provide your users
with a URL that always starts a fresh interview session with the Steward, and will not
resume an existing session, include `&new_session=1` in the URL.
Whenever this link is clicked (or the [iframe] is drawn), the
Steward will start the interview session at the beginning, even if the user had just been
in a session of the same interview.  The prior interview session, if any, is
preserved.

If you add `&reset=1` to the end of a interview's URL, this will have
the same effect as `&new_session=1`, but if the user had just been in
a session with the same interview, that session will be deleted.
In this cirumstance, adding `&reset=1` is like a "restart" operation.

If the user is in an interview session, and then clicks a link
with a different `i` parameter, this has the same effect as
if `&new_session=1` had been added; a fresh interview session will always be
started.

For other session restarting options, see the `'restart'` and
`'new_session'` options for the [`url_of()`] and [`command()`]
functions, and the `restart` and `new_session` [special buttons].

# <a name="howstored"></a>How Answers are Stored

When a user starts a new interview session with a Steward, a new "variable store" is created.
A variable store is a [Python dictionary] containing the names of the
variables that get defined during the course of the interview session, such as
`favorite_animal` in the example Steward above.  The variable store
is then saved in the [server]'s [database].

The Steward keeps a copy of the variable store in the server's database for every step of an
interview session.  If the user presses the Steward's back button
(not the browser back button), the Steward will restore the
variable store to the next earliest version.

# <a name="comingback"></a>Leaving an Interview Session and Coming Back

If the user is not logged in through the Docassemble Framework's
[username and password system], then the user's progress through an
interview session with a Steward will be lost if the web browser is closed.

If the user is logged in, however, then when the user logs in again,
the user will be able to resume the interview session where one left off.

If a new user starts an interview session without being logged in, and then
clicks the link to log in, and then clicks the link to register, the
user will be logged in and will immediately be directed back to the
Steward and the interview session they had been using, and they will immediately pick up where
they left off.

If a logged-in user leaves an interview session without completing it, closes
their browser, then opens their browser at a later time, and visits
the interview's link again, they will start a new interview session with that Steward.  If
they then log in using the menu in the corner, they will be directed
to the `/interviews` page, where they will see two interview sessions with that Steward
listed, including their original session and the session they just
started.

If your users will only ever need to use a single interview session with a
Steward, you might want to change the [DALang] code of your Steward so that
they have a different experience.  For example, you might want to
start your Steward with a multiple-choice question that asks the
user if they are a new user or a returning user.  If they are a
returning user.

{% highlight yaml %}
modules:
  - docassemble.base.util
---
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
`'login'` returns the URL for the Docassemble Framework login page.

For other exiting options, see the `'exit'`, `'leave'`, `'logout'`, and
`'exit_logout'` options for the [`url_of()`] and [`command()`]
functions.

# <a name="htauthor"></a>How to Build Your Own Stewards

To write and test your own Stewards, you will need:

1. A Docassemble Framework server (see [installation]);
2. An account on the [username and password system] of that server,
   where the privileges of the account have been upgraded to
   "developer" or "admin."

There are three ways to build your own Stewards:

1. When logged in, go to the "Playground" from the menu in the upper
   right hand corner.  The [playground] allows you to quickly edit and
   run [DALang].
2. Create a Steward on your local computer and then install it on
   your [server] either through [GitHub] or by uploading a ZIP
   file of the [package] containing the Steward.
3. Create a Steward, push it to [GitHub], and then edit your
   Steward using [GitHub]'s web interface.  (You can also upload
   static files using [GitHub].)  To run your Steward, update your
   Steward on your [server] (which will retrieve your code from
   [GitHub]).

# <a name="yaml"></a>Brief Introduction to DALang

Stewards are written in DALang using [YAML] formating, rather than being
assembled using a [graphical user interface], because once authors
have climbed the learning curve, the text format is
ideal for managing the complexity of advanced Stewards, since it
allows authors to copy-and-paste, search-and-replace, and organize
text into multiple files.  [YAML] was chosen as the format because it
is the cleanest-looking of data formats that are both machine-readable
and human-readable.

The hardest part about learning DALang is not writing
Python [code], since sophisticated Stewards can be built using
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
it sees a color, it thinks you are talking about a dictionary.

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
your Stewards, so if you ever use "True" and "False" as a label or
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
your labels in a [`fields`] component are long.  For example, instead
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

Note that many punctuation marks, including `"`, `'`, `%`, `?`, `~`, `|`, `#`, `>`, `:`, `!`, `:`, `{`, `}`,
`[`, and `]`, have special meaning in [YAML], so if you use them in
your text, make sure to use quotation marks or block quotes.

For more information about [YAML], see the [YAML specification].

[YAML specification]: http://yaml.org/spec/1.2/spec.html
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
[Question Blocks: Fields]: {{ site.baseurl }}/docs/fields.html
[Question Blocks: Modifiers]: {{ site.baseurl }}/docs/modifiers.html
[Template Blocks]: {{ site.baseurl }}/docs/template.html
[Code Blocks]: {{ site.baseurl }}/docs/code.html
[Interview Flow]: {{ site.baseurl }}/docs/logic.html
[Objects]: {{ site.baseurl }}/docs/objects.html
[Markup]: {{ site.baseurl }}/docs/markup.html
[Functions]: {{ site.baseurl }}/docs/functions.html
[Documents]: {{ site.baseurl }}/docs/documents.html
[Roles]: {{ site.baseurl }}/docs/roles.html
[Reserved Names]: {{ site.baseurl }}/docs/reserved.html
[Errors]: {{ site.baseurl }}/docs/errors.html
[username and password system]: {{ site.baseurl }}/docs/users.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[JSON]: https://en.wikipedia.org/wiki/JSON
[Special Variables]: {{ site.baseurl }}/docs/special.html
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[`default interview`]: {{ site.baseurl }}/docs/config.html#default interview
[embedded]: {{ site.baseurl }}/docs/config.html#dispatch
[list of interviews]: {{ site.baseurl }}/docs/config.html#dispatch
[demo Steward]: {{ site.baseurl }}/demo.html
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
[domain specific language]: https://en.wikipedia.org/wiki/Domain-specific_language
[backward chaining]: https://en.wikipedia.org/wiki/Backward_chaining
[variables]: {{ site.baseurl }}/docs/fields.html
[DALang]: {{ site.baseurl }}/docs/interviews.html#yaml
[Zapier]: https://zapier.com
[generated documents]: {{ site.baseurl }}/docs/documents.html
[server]: {{ site.baseurl }}/docs/installation.html
[database]: {{ site.baseurl }}/docs/schema.html