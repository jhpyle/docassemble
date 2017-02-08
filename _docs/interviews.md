---
layout: docs
title: How to write an interview
short_title: Interviews
---

# What is a **docassemble** interview?

An "interview" in **docassemble** is a [YAML] file that
**docassemble** reads, and on the basis of what it finds, asks
questions of a user.

**docassemble** stores the user's answers in "variables."  The values
of these variables may be incorporated into the the text of [questions],
or into the text of [documents].

The interview can ask different questions of the user depending on
what the answers to earlier questions were.

# The contents of an interview file

The interview file is a series of possible questions that could
potentially be asked, arranged in no particular order.  Which
questions will be asked, and the order in which they are asked, will
be determined by **docassemble**.  All you need to do is give
**docassemble** an end goal.

The end goal might be as simple as "show the exit screen."  This will
instruct **docassemble** to try to show the exit screen.  But
**docassemble** will doubtless find that in order to show the exit
screen, it will need a piece of information.  It will look for a
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
separated by `---`.  For example, this interview has four blocks:

{% highlight yaml %}
---
question: What is your favorite animal?
fields:
  - Animal: favorite_animal
---
question: What is your favorite vegetable?
fields:
  - Animal: favorite_vegetable
---
mandatory: True
question: What a coincidence!
subquestion: |
  My favorite animal is the ${ favorite_animal }, too!
buttons:
  - Exit: exit
---
{% endhighlight %}

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

You can
[try out this interview]({{ site.demourl }}?i=docassemble.demo:data/questions/animal.yml){:target="_blank"}
to see how it looks from the user's perspective.

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

# How you run a **docassemble** interview

You start the interview by going to its URL.  In the case of the
interview linked from the [demonstration page], you can get to the
interview by doing:

[{{ site.demourl }}]({{ site.demourl }}){:target="_blank"}

This URL is simple-looking because it uses the default interview file
that was set in the [configuration].

If you want to link to an interview file by its specific filename,
just set an `i` parameter in the URL:

[{{ site.demourl }}?i=docassemble.demo:data/questions/questions.yml]({{ site.demourl }}?i=docassemble.demo:data/questions/questions.yml){:target="_blank"}

Here, the interview file name is
`docassemble.demo:data/questions/questions.yml`.  This tells
**docassemble** to look for a Python package named `docassemble.demo`
and then within that package, look for the file `questions.yml`
located in the subdirectory `data/questions`.

To make your own Python package, you download a ZIP file from your
**docassemble** server, unpack it on your computer, and you will find
the `data/questions` subdirectory inside.  You can create your own
[YAML] files within that subdirectory.  When you re-ZIP everything and
upload it to your **docassemble** server, you can run the interview by
typing in a URL like:

> http://example.com/interview?i=docassemble.mypackage:data/questions/myinterview.yml

# How answers are stored

When a user starts a new interview, a new "variable store" is created.
A variable store is a [Python dictionary] containing the names of the
variables that get defined during the course of the interview, such as
`favorite_animal` in the example interview above.  The variable store
is saved on the **docassemble** server.

**docassemble** keeps a copy of the variable store for every step of
the interview.  If the user presses the **docassemble** back button
(not the browser back button), **docassemble** will restore the
variable store to the next earliest version.

# Leaving an interview and coming back

If the user is not logged in through **docassemble**'s
[username and password system], then the user's progress through an
interview will be lost if the web browser is closed.

If the user is logged in, however, then when the user logs in again,
the user will resume the interview where he left off.

# How to author your own interviews

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

# Brief introduction to YAML

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
- olive oil
- shortening: for cookies
- flour
{% endhighlight %}

In [Python], this will be interpreted as:

{% highlight python %}
['apples', 'bread', 'olive oil', {'shortening': 'for cookies'}, 'flour']
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


Many punctuation marks, including `"`, `'`, `%`, `?`, `~`, `|`, `#`, `>`, `:`, `!`, `:`, `{`, `}`,
`[`, and `]`, have special meaning in [YAML], so if you use them in
your text, make sure to use quotation marks or block quotes.

For more information about [YAML], see the [YAML specification].

[YAML specification]: http://yaml.org/spec/1.2/spec.html
[if/else statements]: {{ site.baseurl }}/docs/code.html#if
[graphical user interface]: https://en.wikipedia.org/wiki/Graphical_user_interface
[GitHub]: https://github.com/
[package]: {{ site.baseurl }}/docs/packages.html
[playground]: {{ site.baseurl }}/docs/playground.html
[demonstration page]: {{ site.baseurl }}/demo.html
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/config.html
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
