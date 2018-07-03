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

The interview can ask different questions of the user depending on
what the answers to earlier questions were.

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
whether the household is low income.

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
* [Setting Variables] - Explains how to use collect information from users
  using `question` blocks.
* [Question Modifiers] - Explains ways you can enhance questions with
special features, for example by adding help text or icons.
* [Templates] - Explains `template` blocks, which allow you to assign
  text to a variable and then include it by reference in a question or
  document.
* [Code] - Explains `code` blocks, which are like `question`s except
  that instead of presenting something to the user, they run [Python]
  code that defines variables or does other things that computer code
  can do.
* [Interview Logic] - Explains [`mandatory`] and [`initial`] blocks and how
  **docassemble** processes your interview.
* [Objects] - Explains the use of Python objects to simplify the way
  information is organized.
* [Markup] - Explains how to change the formatting of text in **docassemble**.
* [Functions] - Explains how to use special [Python] functions to
  simplify and generalize the way questions are asked.
* [Documents] - Explains how to offer your users documents in PDF and
  RTF format based on the user's answers to the interview questions.
* [Roles] - Explains **docassemble**'s features for multi-user interviews.
* [Reserved Names] - Lists the variable names you aren't allowed to use
  because they would conflict with the functionality of
  **docassemble** and [Python].
* [Special Variables] - Describes variables that have special properties
* [Errors] - Explains some common error messages and how to avoid them.

# <a name="invocation"></a>How you run a **docassemble** interview

Users start an interview by going to its URL, which is the URL of your
server with the `i` parameter set to the name of the interview.

For example, the [demo interview], which is hosted on the server
`demo.docassemble.org`, can be accessed with this URL.

[{{ site.demourl }}?i=docassemble.demo:data/questions/questions.yml]({{ site.demourl }}?i=docassemble.demo:data/questions/questions.yml){:target="_blank"}

Here, the interview file name is
`docassemble.demo:data/questions/questions.yml`.  This tells
**docassemble** to look for a Python package named `docassemble.demo`
and then within that package, look for the file `questions.yml`
located in the subdirectory `data/questions`.

You can make your own [packages] in the [Playground] and then install
them on the same server or a different server.  If the name of your
server is `interview.example.com`, the name of your package is
`docassemble.mypackage`, and the name of your interview file is
`myinterview.yml`, your users can access the interview at:

> https://interview.example.com/?i=docassemble.mypackage:data/questions/myinterview.yml

Note that while you are using an interview, the URL in the location
bar will change.  It will end with `#page1`, then `#page2`, then
`#page3`, etc., as the interview progresses.  These tags have no
effect except to allow the user to click the browser's back button in
order to go back one screen.

There is also a special page of the site, located at `/list`, which
displays a [list of interviews] available on your server.

> https://interview.example.com/list

You can configure this list using the [`dispatch`] configuration
directive.  The list of interviews can also be [embedded] into a page
of another web site.  You can also replace the default `/list` page
with an interview using the [`dispatch interview`] configuration
directive.  Within that interview, you can use the
[`interview_menu()`] function within that interview to present the
list of interviews in whatever way you want.

The [`dispatch`] configuration directive also allows your users to
access specific interviews at human-readable URLs like:

> https://interview.example.com/start/eviction<br>
> https://interview.example.com/start/namechange

By default, if the user visits the main URL for the site, e.g.,
`https://interview.example.com`, the user will be redirected to the
`/list` page.  You can change this if you want.  If you set set the
[`default interview`] configuration directive, and then the interview
will be accessible at:

> https://interview.example.com

However, if the user had previously been using another interview
during the same browser session, going to
`https://interview.example.com/` will resume the original session.  If
you want to provide a way for users to access other interviews, you
can use the [`menu_items` special variable] within an interview to
provide options on the pull-down menu for visiting other parts of the
site.

You can embed an interview into a web page by inserting an [iframe]
into the [HTML] of the page.

{% highlight html %}
<iframe style="width: 500px; height: 700px;" src="https://demo.docassemble.org/?i=docassemble.demo:data/questions/questions.yml&reset=1"></iframe>
{% endhighlight %}

You should adjust the width and height of the [iframe] based on what
makes sense for the web page.  **docassemble** can handle a variety of
sizes, but make sure you test the user experience both on desktop
and on mobile.  Since embedded interviews are often less than ideal for
mobile users, you can use the [`go full screen`] feature to cause the
interview to "go full screen" on the user's device once the user
starts interacting with it.

If you add `&reset=1` to the end of an interview URL, this means that
whenever the link is clicked (or the [iframe] is drawn), the interview
will start at the beginning.  If `&reset=1` is omitted from the URL,
then if the user clicks on the link after having already visited the
same interview during the same browser session, then the user will be
taken back to the "current" screen of the interview.

If the user has started using one interview, and then clicks a link to
start an interview with a different `i` parameter, this has the same
effect as if `&reset=1` had been added; a fresh interview will be
started.

# <a name="howstored"></a>How answers are stored

When a user starts a new interview, a new "variable store" is created.
A variable store is a [Python dictionary] containing the names of the
variables that get defined during the course of the interview, such as
`favorite_animal` in the example interview above.  The variable store
is saved on the **docassemble** server.

**docassemble** keeps a copy of the variable store for every step of
the interview.  If the user presses the **docassemble** back button
(not the browser back button), **docassemble** will restore the
variable store to the next earliest version.

# <a name="comingback"></a>Leaving an interview and coming back

If the user is not logged in through **docassemble**'s
[username and password system], then the user's progress through an
interview will be lost if the web browser is closed.

If the user is logged in, however, then when the user logs in again,
the user will be able to resume the interview where he left off.

If a new user starts an interview without being logged in, and then
clicks the link to log in, and then clicks the link to register, the
user will be logged in and will immediately be directed back to the
interview they had been using, and they will immediately pick up where
they left off.

If a logged-inuser leaves an interview without completing it, closes
their browser, then opens their browser at a later time, and visits
the interview link again, they will start a new interview session.  If
they then log in using the menu in the corner, they will be directed
to the `/interviews` page, where they will see two interview sessions
listed, including their original session and the session they just
started.

If your users will only ever need to use a single session of an
interview, you might want to change the code of your interview so that
they have a different experience.  For example, you might want to
start your interview with a multiple-choice question that asks the
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
`'login'` returns the URL for the **docassemble** login page.

# <a name="htauthor"></a>How to author your own interviews

To write and test your own interviews, you will need:

1. A **docassemble** server (see [installation]);
2. An account on the [username and password system] of that server,
   where the privileges of the account have been upgraded to
   "developer" or "admin."

There are three ways to author your own interviews:

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

# <a name="yaml"></a>Brief introduction to YAML

**docassemble** interviews are written in [YAML] format, rather than
assembled using a [graphical user interface], because once authors
have climbed the **docassemble** learning curve, the text format is
ideal for managing the complexity of advanced interviews, since it
allows authors to copy-and-paste, search-and-replace, and organize
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
it sees a color, it things you are talking about a dictionary.

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
* `True`, `True`, `TRUE` -- these become `True` in [Python]
* `False`, `False`, `FALSE` -- these become `False` in [Python]
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
your labels in a [`fields`] directive are long.  For example, instead
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
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[Question Modifiers]: {{ site.baseurl }}/docs/modifiers.html
[Templates]: {{ site.baseurl }}/docs/template.html
[Code]: {{ site.baseurl }}/docs/code.html
[Interview Logic]: {{ site.baseurl }}/docs/logic.html
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
[demo interview]: {{ site.baseurl }}/demo.html
[iframe]: https://www.w3schools.com/TAgs/tag_iframe.asp
[HTML]: https://en.wikipedia.org/wiki/HTML
[`go full screen`]: {{ site.baseurl }}/docs/initial.html#go full screen
[`dispatch interview`]: {{ site.baseurl }}/docs/config.html#dispatch interview
[`interview_menu()`]: {{ site.baseurl }}/docs/functions.html#interview_menu
[`menu_items` special variable]: {{ site.baseurl }}/docs/special.html#menu_items
[configured otherwise]: {{ site.baseurl }}/docs/config.html#session list interview
[`command()`]: {{ site.baseurl }}/docs/functions.html#command
[`url_of()`]: {{ site.baseurl }}/docs/functions.html#url_of
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
