---
layout: docs
title: Code questions
short_title: Code
---

**docassemble** allows interview developers to use [Python], a general
purpose programming language, to control the direction of interviews
and do things with user input.  It is not necessary to use [Python]
code when developing an interview, but it is an extremely powerful tool.

[Python] appears in **docassemble** interviews in a number of ways:

* Every [variable name] in an interview is a [Python] variable,
  whether developers realize it or not.  The value of the variable
  might be text (e.g., `"123 Main Street"`), a number (e.g., `42`), a
  special value that has meaning in [Python] (e.g. `True`, `False`,
  and `None`), a [group] (e.g., a [list], [dictionary], or [set]), an
  [object], or an attribute of an [object].
* Developers can use [`code`] blocks to set variables using [Python]
  code, which may act upon user input.
* [Python] code can be embedded within [`question`]s, for example to
  generate a list of choices in a multiple-choice list.
* The [Mako] templating system, which developers can use to format
  [questions] and [documents], is based on [Python], and allows
  developers to embed [Python] statements within templates.  There are
  slight syntax differences between [Mako] and [Python].  For example,
  [Mako] requires that if/then/else logic statements be closed with an
  `endif` statement.

# <a name="python"></a>An introduction to coding in Python

As general purpose programming languages go, [Python] is relatively
user-friendly and readable.  Python programmers don't need to worry
that their code will fail because of a missing semicolon.

## <a name="simpleexamples"></a>Simple examples: arithmetic

Here is some very simple [Python] code:

{% include side-by-side.html demo="code-example-01" %}

This code sets the variable `answer` to 2 + 2.  The code is contained
in a [`code`] block, which is explained [below](#code).

Here is a more complicated example:

{% include side-by-side.html demo="code-example-02" %}

This code first sets the variable `a` to the number 2.  Then it sets
the variable `b` to the number 3.  Then it sets the variable `answer`
to the sum of `a` and `b`, which is 5.

Note that once a variable is set, its value does not change.  In the
code below, the `answer` is still 5, even though `b` is changed to
`1`.

{% include side-by-side.html demo="code-example-03" %}

The `code` blocks can contain multiple lines of code, which are
processed one at a time.

It is also possible to run Python code in a more limited way within a
[Mako] template, using [Mako]'s `${}` syntax.

{% include side-by-side.html demo="code-example-04" %}

The contents of `${ ... }` are processed as [Python] code.  The code
that can be placed inside `${ ... }` is limited to one line of code,
the result of which is then placed into the text of the question.  So
you could not include multiple lines of code within a `${ ... }`
expression.

You can do complicated arithmetic with [Python]:

{% include side-by-side.html demo="code-example-05" %}

Note that the spaces within this code are purely aesthetic; the code
will still function without them:

{% include side-by-side.html demo="code-example-06" %}

However, using spaces in your code is highly recommended, because they
make the code much more readable!

## <a name="if"></a>Conditional actions: if/then/else statements

Sometimes you want different code to run differently depending on
certain conditions.  In computer programming, the simplest form of a
"conditional statement" is the if/then/else statement, where you tell
the computer that _if_ a certain condition is true, _then_ do
something, or do something _else_ if the condition is false.

For example:

{% include side-by-side.html demo="code-example-07" %}

Here, the condition to be evaluated is `b > a`.  The `>` symbol means
"greater than."  (The `<` symbol means "less than.")  Since `b` is 5
and `a` is 4, and 5 is greater than 4, the condition is true.
Therefore, the lines `b = 62 ` and `answer = 20` will be run, and the
code `answer = 40` will be ignored.

There are several important things to note in this example because
they illustrate the syntax of the [Python] language:

* The `if` and `else` statements end in a colon `:`, after which the
  line ends.
  * Rule: This colon must be there.  If you forget the colon, you will
    get an "invalid syntax" error.
* The lines after the `if` and `else` lines are indented.  The
  indentation indicates which lines are referred to by the colon, and
  which are not.
  * Rule: There must be at least one indented line following the
    colon.  If you don't have an indented line following a colon, you
    will see the error "IndentationError: expected an indented block."
* At the end, `b` will be set to 0.  Although the line follows
  `else:`, it is not indented relative to the `else:` line.
* The lines `b = 62` and `answer = 20` are both indented by two
  spaces.
  * Rule: While the number of spaces is not important (1, 2, 3, 4, or
  more spaces would all be valid) the indentation following the colon
  must be consistent.  If you use inconsistent indentation, you will
  see the error "IndentationError: unindent does not match any outer
  indentation level."

These are important rules in [Python].  In other programming
languages, line breaks and spaces do not matter, and punctuation marks
like `{`, `}`, and `;` are used to separate different pieces of code.
In [Python], however, line breaks and spaces are important; they serve
the same purposes that `{`, `}`, and `;` serve in other languages.

You can have multiple layers of indentation.  For example:

{% include side-by-side.html demo="code-example-08" %}

In addition to greater than (`>`) and less than (`<`), the following
conditional operators are available in [Python]:

* `a == b` is true if `a` equals `b`.  There are two equal signs to
  distinguish this from `a = b`, which sets the value of `a` to the
  value of `b`.  This works with numbers as well as with text.
* `a is b` is essentially synonomous with `a == b`.
* `a >= b` is true if `a` is greater than or equal to `b`.
* `a <= b` is true if `a` is less than or equal to `b`.
* `a in b` is true if `b` is a [list], [dictionary], or [set], and `a`
  is contained within `b`.  For example, `42 in [13, 42, 62]` is true.
  This also works with text.  If you do `a = "Fred"`, then `a in
  ["Mary", "Fred", "Scott"]` will be true, while `a in
  ["Harold", "Anthony", "Norman"]` will be false.  In the case where
  `b` is a [dictionary], `a in b` will return true if `a` is a key
  within `b`.

The following conditions apply when the variables are text.

* `a.rfind(b) >= 0` will return true if `a` and `b` are both text
  strings and `b` is contained within `a`.
* `a.startswith(b)` returns true if the text in `b` is the start of
  the text in `a`.
* `a.endswith(b)` returns true if the text in `b` is at the tail end
  of the text in `a`.

## <a name="looping"></a>Going through the items in a group

There are special types of variables in [Python] that help you manage
collections of things.  For more information about this, see the
[groups] section.

# <a name="code"></a>The `code` block

In a **docassemble** interview, a [`question`] block tells
**docassemble** that if the interview logic wants to know the value of
a particular variable, such as `best_fruit_ever`, and that variable
has not been defined yet, **docassemble** can pose the question to the
user and the user's answer to the question may provide a definition
for that variable.

For example:

{% highlight yaml %}
---
question: What is the best fruit ever?
fields:
  - Fruit: best_fruit_ever
---
{% endhighlight %}

This [`question`] asks the user to type in the name of the best fruit
ever.

The value of variables like `best_fruit_ever` can also be retrieved by
running Python code contained within `code` blocks:

{% highlight yaml %}
---
code: |
  best_fruit_ever = "Apple"
---
{% endhighlight %}

This `code` "question" is "asked" in much the same way that the
previous [`question`] question is asked: if and when it needs to be
asked.  **docassemble** "asks" `code` questions not by asking for the
user's input and then processing the user's input, but by running the
Python code contained in the `code` statement.

As with user [`question`]s, **docassemble** might find that "asking" the
`code` question did not actually define the needed variable.  In that
case, it goes looking for another question (which could be of the
[`question`] or `code` variety) that will provide a definition.

Once `best_fruit_ever` is defined, **docassemble** will not need to
run the `code` again if the interview logic calls for
`best_fruit_ever` at a later point.  In the same way, **docassemble**
does not need to ask the user for the user's name every time it needs
to know the user's name.

The `code` can do anything Python can do, such as retrieve information
from the web:

{% highlight yaml %}
---
import:
  - urllib2
---
code:
  response = urllib2.urlopen('http://worldsbestfruit.com/')
  best_fruit_ever = response.read()
---
{% endhighlight %}

or pick a random value from a list:

{% highlight yaml %}
---
imports:
  - random
---
code:
  best_fruit_ever = random.choice(['Apple', 'Orange', 'Pear'])
---
{% endhighlight %}

(If you don't remember what an [`imports`] block does, see
[initial blocks].)

All of the variables you set with [`question`] blocks are available to
your Python code.  If your code uses a variable that is not defined
yet, **docassemble** will "ask" [`question`] blocks and `code` blocks in
order to define the variables.

Consider the following example:

{% highlight yaml %}
---
code: |
  if user_age > 60:
    product_recommendation = 'Oldsmobile'
  else:
    product_recommendation = 'Mustang'
---
question: What is your age?
fields:
  - Age in Years: user_age
    datatype: number
---
{% endhighlight %}

If **docassemble** needs to know `product_recommendation`, it will
execute the code block, but the code block will fail to execute
because `user_age` is undefined.  **docassemble** will then go looking
for a question that answers `user_age`, and it will ask the user "What
is your age?"  Upon receiving a response, **docassemble** will
continue in its effort to find a definition for
`product_recommendation` and will complete the execution of the `code`
block.

# <a name="modifiers"></a>`code` block modifiers

You can change the way `code` blocks work by adding modifiers:

* <span></span>[`reconsider`]: If `reconsider` is set to `True`, then
  **docassemble** will always "reconsider" the values of any of the
  variables set by the `code` block.  That is, every time the
  interview logic is evaluated (every time the screen loads) **docassemble**
  will forget about the value of any of the variables set by the
  `code` block.
* <span></span>[`initial`]: If `initial` is set to `True`, then **docassemble**
  will run the code every time the interview logic is evaluated (every time
  the screen loads).
* <span></span>[`mandatory`]: If `mandatory` is set to `True`, then
  **docassemble** will run the code when the interview logic is evaluated,
  except that once the code runs through all the way, **docassemble**
  will remember that the `code` block was successfully run, and it will
  not re-run it again, as it does with `initial` code.

For more information about these modifiers and how they are used, see
the [Interview Logic] section.

# <a name="limitations"></a>Limitations

You can run any [Python] code within [`code`] blocks, but there are
some constraints based on the way **docassemble** works:

* After each screen loads, the variables are serialized with [pickle].
  Any name in the global namespace that refers to something
  non-pickleable will be omitted from this serialization.  So, you can
  define a function `foo()` with some code, but when the next screen
  loads, the name `foo` will be undefined (as though `reconsider` is
  set to `True`).  Thus, **docassemble** will need to seek out the
  definition of `foo`, and will re-run the [`code`] block that defines
  the function `foo`.
* You can include a `class` definition in [`code`], but any instances
  of objects of that class will not be serializable, and an exception
  will be raised.  So if you want to use [custom classes], write a
  [module], use [`modules`] to import all the names from the module, and
  use [`objects`] to instantiate objects of your custom class.
* You can use the standard [Python] statements `import` and `from
  ... import` to import names, but if the names you are importing
  refer to classes of objects that you will create and expect to be
  serialized, put your `import` and `from ... import` statements in
  [`initial`] code.  Otherwise, the serialization process may raise an
  exception.  Better yet, stick with using [`modules`] and [`imports`]
  to bring in names from other packages, and then you don't have to
  worry about this.
* When **docassemble** prepares the variables for serialization, it
  will discard non-serializable names in the global namespace, but it
  **does not do this recursively**.  So you can feel free to use
  non-serializable types in the global namespace, but if you use
  non-serializable types within lists, dictionaries, or attributes, an
  exception will be raised.

While **docassemble** will allow you to do many things with code in
[`code`] blocks, it is a best practice to put complicated code into
modules, and only use rudimentary [Python] code in your interviews.
Ideally, non-programmers should at least be able to read and edit
interview files, because subject matter experts are often not adept at
coding.  The more [Python] code you put into an interview file, the
more non-programmers will be intimidated by the interview file and be
unwilling to work with it.  If you can hide complexity behind a simple
functional interface, you should do so.

[pickle]: https://docs.python.org/2/library/pickle.html
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`imports`]: {{ site.baseurl }}/docs/initial.html#imports
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`reconsider`]: {{ site.baseurl }}/docs/logic.html#reconsider
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[Interview Logic]: {{ site.baseurl }}/docs/logic.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`code`]: #code
[variable name]: {{ site.baseurl }}/docs/fields.html#variable names
[object]: {{ site.baseurl }}/docs/objects.html
[group]: {{ site.baseurl }}/docs/groups.html
[list]: {{ site.baseurl }}/docs/groups.html#list
[dictionary]: {{ site.baseurl }}/docs/groups.html#dictionary
[set]: {{ site.baseurl }}/docs/groups.html#set
[Mako]: http://www.makotemplates.org/
[questions]: {{ site.baseurl }}/docs/questions.html
[documents]: {{ site.baseurl }}/docs/documents.html
[groups]: {{ site.baseurl }}/docs/groups.html
[custom classes]: {{ site.baseurl }}/docs/objects.html#writing
[module]: {{ site.baseurl }}/docs/packages.html
[`objects`]: {{ site.baseurl }}/docs/initial.html#objects
