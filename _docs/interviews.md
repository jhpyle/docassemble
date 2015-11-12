---
layout: docs
title: How to write an interview
short_title: Interviews
---

## What is a **docassemble** interview?

An "interview" in **docassemble** is a [YAML] file that
**docassemble** reads, and on the basis of what it finds, asks
questions of a user.

## The contents of an interview file

The interview file is a series of possible questions that could
potentially be asked, arranged in no particular order.  The order of
the questions is determined by the interview logic, which tells
**docassemble** an end goal.

The interview logic could be as simple as "show the exit screen."
This will instruct **docassemble** to try to show the exit screen.
But **docassemble** will doubtless find that in order to show the exit
screen, it will need a piece of information.  It will look for a
question in the [YAML] file that will provide that information, and it
will try to ask that question.  But it may find that in order to even
ask that question, it needs to know another piece of information, and
it will look for a question that provides it, and so forth and so on.
The first question will turn out to be something basic, like "What is
your name?"

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
separated by `---`.  For example, this [YAML] interview has four blocks:

{% highlight yaml %}
---
mandatory: true
code: |
  exit_page
---
sets: exit_page
question: What a coincidence!
subquestion: |
  My favorite animal is the ${ favorite_animal }, too!
buttons:
  - Exit: exit
---
question: What is your favorite animal?
fields:
  - Animal: favorite_animal
---
question: What is your favorite vegetable?
fields:
  - Animal: favorite_vegetable
---
{% endhighlight %}

The first block is the interview logic.  It tells **docassemble** that
the goal is to get to the `exit_page`.

The second block is a "question" that presents the `exit_page`.  It
refers to the variable `favorite_animal`.

The third block is a "question" that defines the `favorite_animal`.

The fourth block is a "question" that defines the `favorite_vegetable`.

When **docassemble** presents this interview to the user, it follows
these steps:

1. It scans the file and processes everything that is "mandatory."  It
  treats everything else as optional.
2. It finds `mandatory` code in the first block and tries to run it.
3. It can't run the code because it doesn't know what `exit_page` is,
so it looks for a question that defines `exit_page`.
4. It looks through the blocks for a question that defines
`exit_page`, and finds it in the second block.
5. It tries to ask the `exit_page` question, but runs into a variable
it doesn't know: `favorite_animal`.
6. It looks through the blocks for a question that defines
`favorite_animal`, and finds it in the third block.
7. It asks the user for his or her favorite animal, and goes back to
step 1.  This time around, it is able to ask the `exit_page` question,
and the interview stops there because the only thing the user can do
is press the "Exit" button.

The order of the blocks in the file is irrelevant; **docassemble**
would do the same thing regardless of the order of the blocks.

Note that the fourth block, containing the question about the user's
favorite vegetable, was never used because the interview logic did not
need it.

This is a very simple interview; there are more types of blocks that
you can write.  These blocks are explained in the following sections:

* [Initial Blocks] - Explains special blocks you can write that have
  an effect on whole interview.
* [Question Blocks] - Explains the basics of the `question` block, which presents a
  screen to the user (which usually asks a question but does not need to).
* [Setting Variables] - Explains how to use collect information from users
  using `question` blocks.
* [Question Modifiers] - Explains ways you can enhance questions with
  special features, for example by adding help text or icons.
* [Code] - Explains `code` blocks, which are like `question`s except
  that instead of presenting something to the user, they run [Python]
  code that defines variables or does other things that computer code
  can do.
* [Interview Logic] - Explains `mandatory` and `initial` blocks and how
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

## How you run a **docassemble** interview

You start the interview by going to its URL.  In the case of the
interview linked from the [demonstration page], you can get to the
interview by doing:

[https://docassemble.org/demo](https://docassemble.org/demo){:target="_blank"}

This URL is simple-looking because it uses the default interview file
that was set in the [configuration].

If you want to link to an interview file by its specific filename,
just set an `i` parameter in the URL:

[https://docassemble.org/demo?i=docassemble.demo:data/questions/questions.yml](https://docassemble.org/demo?i=docassemble.demo:data/questions/questions.yml){:target="_blank"}

Here, the interview file name is
`docassemble.demo:data/questions/questions.yml`.  This tells
**docassemble** to look for a Python package named `docassemble.demo`
and then within that package, look for the file `questions.yml`
located in the subdirectory `data/questions`.

As you will learn if you follow the [tutorial], it is easy to make
your own Python package: you just download a ZIP file from your
**docassemble** server, unpack it on your computer, and you will find
the `data/questions` subdirectory inside.  You can create your own
[YAML] files within that subdirectory.  When you re-ZIP everything and
upload it to your **docassemble** server, you can run the interview by
typing in a URL like:

> http://example.com/interview?i=docassemble.mypackage:data/questions/myinterview.yml

## Leaving an interview and coming back

If the user is not logged in through **docassemble**'s
[username and password system], then the user's progress through an
interview will be lost if the web browser is closed.

If the user is logged in, however, then when the user logs in again,
the user will resume the interview where he left off.

When a user starts a new interview, a new "variable store" is created.
A variable store is a [Python dictionary] containing the names of the
variables that get defined during the course of the interview, such as
`favorite_animal` in the example interview above.  The variable store
is saved on the **docassemble** server.

[demonstration page]: {{ site.baseurl }}/demo.html
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[configuration]: {{ site.baseurl }}/docs/config.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[Python]: https://www.python.org/
[Initial Blocks]: {{ site.baseurl }}/docs/initial.html
[Question Blocks]: {{ site.baseurl }}/docs/questions.html
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[Question Modifiers]: {{ site.baseurl }}/docs/modifiers.html
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
