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

{% highlight python %}
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
mandatory: true
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

[GitHub]: https://github.com/
[package]: {{ site.baseurl }}/packages.html
[playground]: {{ site.baseurl }}/playground.html
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
