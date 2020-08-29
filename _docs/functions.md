---
layout: docs
title: Functions
short_title: Functions
---

# <a name="function"></a>What is a function?

A function is a piece of code that takes one or more pieces of input
and returns something as output or does something behind the scenes.
For example:

{% include side-by-side.html demo="function" %}

Functions allow you to do a lot of different things in
**docassemble**.  This section explains the standard **docassemble**
functions.  If you know how to write [Python] code, you can [write your
own functions] and include them in your interview using a [`modules`]
block.

These functions are available automatically in **docassemble**
interviews (unless you set [`suppress loading util`]).  To use them in
a [Python module], put a line like this at the top of your .py file to
indicate which functions you want to import:

{% highlight python %}
from docassemble.base.util import send_email, quote_paragraphs
{% endhighlight %}

All of the functions described in this section are available from the
[`docassemble.base.util`] module.

# <a name="functions"></a>Functions for working with variable values

## <a name="defined"></a>defined()

As explained in [how **docassemble** runs your code], if your code or
templates refer to a variable that is not yet defined, **docassemble**
will stop what it is doing to ask a question or run code in an attempt
to obtain a definition for that variable.

Sometimes, this is not what you want **docassemble** to do.  For
example, you might just want to check to see if a variable has been
defined yet.

The `defined()` function checks to see if a variable has been
defined.  You give it a name of a variable.

{% include side-by-side.html demo="defined" %}

It is essential that you use quotation marks around the name of the
variable.  If you don't, it is as if you are referring to the variable.

## <a name="value"></a>value()

The `value()` function returns the value of a variable, where the name
of the variable is given as a string.

{% include side-by-side.html demo="value" %}

These two code blocks effectively do the exact same thing:

{% highlight yaml %}
---
code: |
  answer = value('meaning_of_life')
---
{% endhighlight %}

{% highlight yaml %}
---
code: |
  answer = meaning_of_life
---
{% endhighlight %}

Note that `value(meaning_of_life)` and `value("meaning_of_life")` are
entirely different.  The first will treat the value of the
`meaning_of_life` variable as a variable name.  So if you set
`meaning_of_life = 'chocolate'`, then `value(meaning_of_life)` will
attempt to find the value of the variable `chocolate`.

## <a name="define"></a>define()

The `define()` function defines a variable.  The first argument is the
name of the variable (as a string) and the second argument is the
value you want the variable to have.  Running
`define('meaning_of_life', 42)` has the same effect as running
`meaning_of_life = 42`.

{% include side-by-side.html demo="define" %}

Note that the second argument is the value itself.  If you wanted to
do the equivalent of `my_favorite_fruit = your_favorite_fruit`, it
would be incorrect to do `define('my_favorite_fruit',
'your_favorite_fruit')`; you should instead do
`define('my_favorite_fruit', your_favorite_fruit)` or
`define('my_favorite_fruit', value('your_favorite_fruit'))`.

## <a name="undefine"></a>undefine()

The `undefine()` function makes a variable undefined.  The name
of the variable must be provided as a string.  If the variable is not
defined to begin with, the function does not do anything.

{% highlight python %}
undefine('favorite_fruit')
{% endhighlight %}

This effectively does the same thing as the [del statement] in
[Python].

{% highlight python %}
del favorite_fruit
{% endhighlight %}

The difference is that when using `del`, the variable must first
exist.

The `undefine()` function can be called with multiple variable names.

{% highlight python %}
undefine('favorite_fruit', 'favorite_vegetable')
{% endhighlight %}

Calling undefine in this way is faster than calling `undefine()`
multiple times.

## <a name="invalidate"></a>invalidate()

The `invalidate()` function does what `undefine()` does, but it also
remembers the previous value and offers it as a default when a
[`question`] is asked again.

## <a name="forget_result_of"></a>forget_result_of()

If you want a [`question`] with [embedded blocks] to be asked again,
or you want a [`mandatory`] block to run again, you need to run
`forget_result_of()` on the [`id`] of the block.

The `forget_result_of()` function takes one or more [`id`]s of blocks
as input and causes the results of those blocks to be forgotten.  If
the [`id`] does not exist, or if the block has not yet been processed,
no error will be raised.

This example illustrates using `forget_result_of()` in conjunction
with `del` to ask a series of questions again, where some of the
questions contained embedded blocks.

{% include side-by-side.html demo="forget-result-of" %}

The `forget_result_of()` function can also be used to reset a
[`mandatory`] block so that it will be run again.

{% include side-by-side.html demo="forget-result-of-mandatory" %}

After resetting a `mandatory` block, you may want to call
[`re_run_logic()`].  Otherwise, the `mandatory` block will not have a
chance to run again until the next time the screen loads.

## <a name="re_run_logic"></a>re_run_logic()

The `re_run_logic()` function causes code to stop executing and causes
the interview logic to be evaluated from the beginning.  You might
want to use this in cases when, after you make changes to variables,
you want the [`initial`] and not-yet-completed [`mandatory`] blocks to
be re-run in light of the changes you made.

If you use this, be careful that you do not create an infinite loop.
When the blocks are re-run, the result should not be encountering the
`re_run_logic()` function again, but should be something else, like
asking the user a question.

For an example of this in action, see the code example in the
[`forget_result_of()`] subsection.

## <a name="reconsider"></a>reconsider()

The `reconsider()` function is similar to the [`reconsider`] modifier
on a [`code`] block.  Each argument to `reconsider()` needs to be a
variable name, as text.  E.g., `reconsider('number_of_fruit',
'number_of_vegetables')`.

When `reconsider()` is run, it will undefine the given variables and
then seek their definitions.  However, it will only do this once
in a given assembly process (i.e., once each time a screen loads).
Thus, even if your [`code`] block executes multiple times in a given
assembly process, each variable will only be recomputed one time.

{% include side-by-side.html demo="reconsider-function" %}

Using this function is computationally more efficient than using the
[`reconsider`] modifier or the [`reset`] initial block because
[`reconsider`] and [`reset`] cause code to run every time the screen
loads.

## <a name="need"></a>need()

The `need()` function takes one or more variables as arguments and
causes **docassemble** to ask questions to define each of the
variables if the variables are not already defined.  Note that with
`need()`, you do _not_ put quotation marks around the variable name.

For example, this [`mandatory`] code block expresses [interview logic]
requiring that the user first be shown a splash screen and then be
asked questions necessary to get to the end of the interview.

{% highlight yaml %}
---
mandatory: True
code: |
  need(user_shown_splash_screen, user_shown_final_screen)
---
{% endhighlight %}

This happens to be 100% equivalent to writing:

{% highlight yaml %}
---
mandatory: True
code: |
  user_shown_splash_screen
  user_shown_final_screen
---
{% endhighlight %}

So the `need()` function does not "do" anything.  However, writing
`need()` functions in your code probably makes your code more readable
because it helps you convey in "natural language" that your interview
"needs" these variables to be defined.

## <a name="force_ask"></a>force_ask()

Usually, **docassemble** only asks a question when it encounters a
variable that is not defined.  However, with the `force_ask` function,
you can cause such a condition to happen manually, even when a
variable is already defined.

In this example, we use `force_ask` to cause **docassemble** to ask a
question that has already been asked.

{% include side-by-side.html demo="force-ask-full" %}

This may be useful in particular circumstances.  However,
`force_ask()` cannot be used with all types of questions.  For
example, it cannot be relied upon to re-ask questions that:

* Use the [`generic object`] modifier (and the special variable `x`)
  or iterators (`i`, `j`, etc.);
* Contain [embedded blocks].

The use of `force_ask()` is discouraged, unless you are an expert and
you know what you are doing.  Usually, there is a more elegant way to
craft your interview logic than by using `force_ask()`.  If the
`question` you want to ask is a single-variable question (`field` with
`choices`, `field` with `buttons`, `yesno`, `noyes`), you can use
[`reconsider()`].  If the `question` has `fields`, you can set a
[`continue button field`].  You might also find it useful to use the
[`undefine()`] and [`re_run_logic()`] functions.

Note that variable names given to force_ask must be in quotes.  If
your variable is `favorite_fruit`, you need to write
`force_ask('favorite_fruit')`.  If you write
`force_ask(favorite_fruit)`, **docassemble** will assume that, for
example, `apples` is a variable in your interview.

Note also that no code that comes after `force_ask()` will ever be
executed.  Once the `force_ask()` function is called, the code stops
running, and the question indicated by the variable name will be
shown.  That is why, in the example above, we set
`user_reconsidering_communism` to False _before_ calling `force_ask`.
The variable `user_reconsidering_communism`, which had been set to
`True` by the "I suggest you reconsider your answer" question, is set
to `False` before the call to `force_ask` so that the [`mandatory`]
code block does not get stuck in an infinite loop.

A different way to reask a question is to use the built-in Python
operator `del`.  This makes the variable undefined.  Instead of
writing:

{% include side-by-side.html demo="force-ask" %}

we could have written:

{% include side-by-side.html demo="del" %}

This will also cause the `user_is_communist` question to be asked
again.  This is more robust than using `force_ask` because the user
cannot get past the question simply by refeshing the screen.

The `force_ask()` function can also be given the names of variables
that refer to [`event`] blocks.  The screen will be shown, but no
variable will be defined.

You can use `force_ask()` to ask a series of questions.  Just list
each variable one after another.

{% include side-by-side.html demo="force-ask-multiple" %}

The second and subsequent arguments to `force_ask()` can specify
[actions] with arguments.  If an argument to `force_ask()` is a
[Python dictionary] with keys `action` and `arguments`, the specified
action will be run.  (Internally, **docassemble** uses the [actions]
mechanism to force the interview to ask these questions.)

If you give `force_ask()` the name of a variable that no [`question`]
can define, then `force_ask()` will quietly ignore it.  Thus you can
use conditional logic within a `force_ask()` sequence by adding [`if`]
modifiers to each [`question`] that specify under what conditions the
[`question`] should be asked.

In addition to giving `force_ask()` variables and actions, you can
give it a dictionary containing a special command.

* `force_ask('favorite_fruit', {'recompute': 'dessert_cost'}, 'favorite_vegetable')`
* `force_ask('favorite_fruit', {'recompute': ['dessert_cost', 'breakfast_cost']}, 'favorite_vegetable')`
* `force_ask('favorite_fruit', {'recompute': ['dessert_cost', 'breakfast_cost']}, 'favorite_vegetable')`
* `force_ask('favorite_fruit', {'set': {'fruit_known': True}}, 'favorite_vegetable')`
* `force_ask('favorite_fruit', 'favorite_vegetable', {'set': [{'fruit_known': True}, {'vegetable_known': True}]})`

For more information on how these data structures work, see the
subsection on [customizing the display of `review` options].

A function that is related to `force_ask()` is [`force_gather()`].
[`force_gather()`] cannot force the-reasking of a question to define a
variable that has already been defined, but it does not have the
limitations on question types that `force_ask()` has.

## <a name="force_gather"></a>force_gather()

The `force_gather()` function is very similar to [`force_ask()`],
except it affects the interview logic for all users of the interview,
not just the current user.

{% include side-by-side.html demo="force-gather" %}

Calling `force_gather('favorite_food')` means "until `favorite_food`
is defined, keep asking questions that offer to define
`favorite_food`, and satisfy any prerequisites that these questions
require."

Normally, you will not need to use either [`force_ask()`] or
[`force_gather()`]; you can just mention the name of a variable in
your [`question`]s or [`code`] blocks, as part of your [interview
logic], and **docassemble** will make sure that the variables get
defined.  The [`force_ask()`] and [`force_gather()`] functions are
primarily useful when you are using [actions] to do things that are
outside the normal course of the [interview logic].

## <a name="dispatch"></a>dispatch()

The `dispatch()` function provides logic so that an interview can
present a menu system within a screen.  For example:

{% include side-by-side.html demo="dispatch" %}

To make a menu, you need to add a few components to your interview:

* Some code that runs `dispatch()` in order to launch the menu at a
  particular place in your interview logic.
* A screen that shows the menu.  This is typically a
  [multiple-choice question] in which each choice represents a screen
  that the user can visit.
* Screens corresponding to each choice.  These can be standalone
  screens, or they can be sub-menus.

In the example above, the main menu is a [multiple-choice question]
that sets the variable `main_menu_selection`.

When the interview logic calls `dispatch('main_menu_selection')`, it
looks for a definition of the variable `main_menu_selection`.  It
finds a [multiple-choice question] that offers to define
`main_menu_selection`.  This question will set the variable
to one of four values:

* `fruit_menu`
* `vegetable_menu`
* `rocks_page`
* `Null`

The first three values are the names of other variables in the
interview.  Note that in the interview, `fruit_menu` and
`vegetable_menu` are variables defined by [`code`] blocks, and
`rocks_page` is defined by a [`question`] block.  If the user selects
one of these choices, the interview will look for a definition of the
selected variable.  This all done by the `dispatch()` function.

The last value, `Null`, is special; it ends the menu.  (Note that
`Null` or `null` is a special value in [YAML]; it becomes `None` in
[Python].)  When the user selects "Continue," the `dispatch()`
function will end.  In this sample interview, the next step after the
menu is to show the `final_screen`.  Thus, when the user selects
"Continue," the user sees the `final_screen` question.  If you want
the interview logic to be able to move past the `dispatch()` function,
you must include a `Null` option.

This sample interview features two sub-menus.  You can tell this
because the variable `fruit_menu` is defined with:

{% highlight python %}
fruit_menu = dispatch('fruit_menu_selection')
{% endhighlight %}

and the variable `vegetable_menu` is defined with:

{% highlight python %}
vegetable_menu = dispatch('vegetable_menu_selection')
{% endhighlight %}

If the user selects "Fruit" from the main menu, the interview will
seek a definition of `fruit_menu`.  This in turn leads to calling the
`dispatch()` function on `'fruit_menu_selection'`.  This leads to
seeking a definition of the variable `fruit_menu_selection`.  If the
user selects the `Null` option on this menu, the user will go back to
the main menu.

If the user selects "Rocks" from the main menu, the interview will
seek a definition of `rocks_page`.  In this case, the block that
offers to define `rocks_page` is a [`question`] with a "Continue"
button.  When the user presses "Continue" on the "Rocks screen," the
user will return to the menu.

Note that when the interview seeks definitions of variables and
displays screens, it will ask questions to satisfy prerequisites.  For
example, when the user selects "Apple" from the "Fruit menu," the
interview will seek the definition of `apple`, but in order to pose
the `question` that defines `apple`, it needs the definition of
`likes_apples`.  So it will stop and ask "Do you like apples?" before
proceeding to the `question` that defines `apple`.

One very important thing to know about the `dispatch()` function is
that the variables it uses to navigate among the screens are
temporary.  After the call to `dispatch('main_menu_selection')`, the
variables `main_menu_selection`, `fruit_menu`, `fruit_menu_selection`,
`apple`, `rocks_page`, etc., will all be undefined.  However,
questions _will_ be able to access these variables from within the
`dispatch()` function.  For example, the "Peaches screen" successfully
accesses the values of `main_menu_selection` and
`fruit_menu_selection`.

If you want to gather information about what screens your user visited
or did not visit, you can use prerequisites to do so.  Here is an
example that uses the [`need` specifier] to run a code block when a
user selects a menu item.

{% include side-by-side.html demo="dispatch-track" %}

Or, if you want to keep a count of the number of times a user has
visited a page, you could do:

{% include side-by-side.html demo="dispatch-count" %}

## <a name="all_variables"></a>all_variables()

The `all_variables()` function returns all of the variables defined in
the interview session as a simplified [Python dictionary].

{% include side-by-side.html demo="all_variables" %}

The resulting [Python dictionary] is suitable for conversion to [JSON]
or other formats.  Each [object] is converted to a [Python
dictionary].  Each [`datetime`] or [`DADateTime`] object is converted
to its `isoformat()`.  Other objects are converted to `None`.

If you want the raw [Python] dictionary representing the variables
defined in the interview session, you can call
`all_variables(simplify=False)`.  The result is not suitable for
conversion to [JSON].  This raw [Python] dictionary will be linked to
the current interview answers, so that if you use the [Python] `is`
operator to test for equivalence between objects, you will see that
they are equivalent.  Therefore, if you try to edit the output of
`all_variables(simplify=False)`, you may be affecting the interview
variables in unwanted ways.  If you want the result of
`all_variables(simplify=False)` to be a distinct copy of the interview
answers, call it using `all_variables(simplify=False,
make_copy=True)`.

**docassemble** keeps a dictionary called `_internal` in the interview
variables and uses it for a variety of internal purposes.  By default,
it is not included in the output of [`all_variables()`].  If you want
`_internal` to be included, set the optional keyword parameter
`include_internal` to `True`.  This parameter has no effect when
`simplify` is `False`.

The [`all_variables()`] function also has three special behaviors:

* `all_variables(special='titles')` will return a [Python dictionary]
  containing information set by the [`metadata` initial block] and the
  [`set_parts()`] function.
* `all_variables(special='metadata')` will return a dictionary
  representing the "metadata" indicated in the [`metadata` initial
  block]s of the interview.  (If multiple blocks exist, information is
  "layered" so that keys in later blocks overwrite keys in earlier
  blocks.)  Unlike the `'titles'` option, the information returned
  here is not updated to take into account changes made
  programmatically by the [`set_parts()`] function.
* `all_variables(special='tags')` will return a [Python set]
  containing the current set of [tags] defined for the interview
  session.

# <a name="special responses"></a>Functions for special responses

## <a name="message"></a>message()

{% include side-by-side.html demo="message" %}

The `message()` function causes **docassemble** to stop what it is
doing and present a screen to the user that contains a given message.

By default, the user will be offered an "exit" button and a "restart"
button, but these choices can be configured.

The first argument is the title of the screen the user will see (the
[`question`]).  The second argument, which is optional, indicates the
text that will follow the title (the [`subquestion`]).

The `message()` function also takes keyword arguments.  The following
do the same thing:

* `message("This is the big part of the question", "This is the
  smaller part of the question")`
* `message(question="This is the big part of the question", subquestion="This is the
  smaller part of the question")`

The optional keyword arguments influence the appearance of the screen:

* `message("Bye!", "See ya later", show_restart=False)` will show the
  Exit button but not the Restart button.
* `message("Bye!", "See ya later", show_exit=False)` will show the
  Restart button but not the Exit button.
* `message("Bye!", "See ya later", url="https://www.google.com")`:
  clicking the Exit button will take the user to Google.
* `message("Bye!", "See ya later", show_leave=True)` will show a
  Leave button instead of the Exit button.
* `message("Bye!", "See ya later", show_leave=True, show_exit=True,
  show_restart=False)` will show a Leave button and an Exit button.
* `message("Bye!", "See ya later",
  buttons=[{"Learn More": "exit", "url": "https://en.wikipedia.org/wiki/Spinning_wheel"}])`
  will show a "Learn More" button that exits to Wikipedia.

## <a name="response"></a>response()

The `response()` command allows the interview developer to use code to
send a special HTTP response.  Instead of seeing a new **docassemble**
screen, the user will see raw content as an HTTP response, or be
redirected to another web site.  As soon as **docassemble** runs the
`response()` command, it stops what it is doing and returns the
response.

There are four different types of responses, which you can invoke by
using one of four keyword arguments: `response`, `binaryresponse`,
`file`, and `url`.  There is also an optional keyword argument
`content_type`, which determines the setting of the [Content-Type
header].  (This is not used for `url` responses, though.)  The
`response()` function accepts the optional keyword parameter
`response_code`.  The default HTTP response code is 200 but you can
use `response_code` to set it to a different value.

The four response types are:

* `response`: This is treated as text and encoded to UTF-8.  For
  example, if you have some data in a dictionary `info` and you want
  to return it in [JSON] format, you could do
  `response(response=json.dumps(info),
  content_type='application/json')`.  If the `content_type` keyword
  argument is omitted, the [Content-Type header] defaults to
  `text/plain; charset=utf-8`.
* `binaryresponse`: This is like `response`, except that the data
  provided as the `binaryresponse` is treated as binary bytes rather
  than text, and it is passed directly without any modification.  You
  could use this to transmit images that are created using a software
  library like the [Python Imaging Library].  If the `content_type`
  keyword argument is omitted, the [Content-Type header] defaults to
  `text/plain; charset=utf-8`.
* `file`: The contents of the specified file will be delivered in
  response to the HTTP request.  You can supply one of two types of
  file designators: a [`DAFile`] object (e.g., an assembled document
  or an uploaded file), or a reference to a file in a **docassemble**
  package (e.g., `'moon_stars.jpg'` for a file in the static files
  folder of the current package, or
  `'docassemble.demo:data/static/orange_picture.jpg'` to refer to a
  file in another package).
* `url`: If you provide a URL, the web server will redirect the user's
  browser to the provided URL.

Here is an example that demonstrates `response`:

{% include side-by-side.html demo="response" %}

Here is an example that demonstrates the `binaryresponse`:

{% include side-by-side.html demo="response-svg" %}

The following example shows how you can make information entered into
an interview available to a third-party application through a URL that
returns data in [JSON] format.

{% include side-by-side.html demo="response-json" %}

Note the following about this interview.

1. We set [`multi_user`] to `True` in order to disable server-side
   encrpytion.  This allows an external application to access the
   interview without logging in as the user.
2. The `query_fruit` [`event`] code will be run as an [action] when
   someone accesses the link created by [`interview_url_action()`].

The `response()` command can be used to integrate a **docassemble**
interview with another application.  For example, the other
application could call **docassemble** with a URL that includes an
interview file name (argument `i`) along with a number of
[URL arguments].  The interview would process the information passed
through the URLs, but would not ask any questions.  It would instead
return an assembled document using `response()`.

{% highlight yaml %}
attachment:
  name: A file
  file: test_file
  variable name: the_file
  valid formats:
    - pdf
  content: |
    Hello, ${ url_args.get('name', 'you') }!
---
mandatory: True
code: |
  response(file=the_file.pdf)
---
{% endhighlight %}

Here is a link that runs this interview.  Notice how the name "Fred" is
embedded in the URL.  The result is an immediate PDF document.

> [{{ site.demourl }}/interview?i=docassemble.base:data/questions/examples/immediate_file.yml&name=Fred]({{ site.demourl }}/interview?i=docassemble.base:data/questions/examples/immediate_file.yml&name=Fred){:target="_blank"}

When you write code that runs in a [scheduled task], you can use
`response()` to finish the scheduled task.  In this context, you can
pass the optional keyword argument `sleep` with a number of seconds
that you want to pause after the task is finished.  This can be useful
when your [scheduled tasks] would overwhelm your SQL server if
executed one after another without pauses.

## <a name="json_response"></a>json_response()

Calling `json_response(data)` is a shorthand for
`response(json.dumps(data), content_type="application/json")`.

In other words, it takes a single argument and returns it as an HTTP
response in [JSON] format.

The `json_response()` function accepts the optional keyword parameter
`response_code`.  The default response code is 200 but you can use
`response_code` to set it to a different value.

Another way to get [JSON] output from **docassemble** is to use the
[JSON interface], which provides a [JSON] representation of a
**docassemble** screen.  This can be useful if you are developing your
own front end to **docassemble**.

## <a name="variables_as_json"></a>variables_as_json()

The `variables_as_json()` function acts like [`response()`] in the
example above, except that is returns all of the variables in the
[interview session dictionary] in [JSON] format.

{% include side-by-side.html demo="variables_as_json" %}

The `variables_as_json()` function simplifies the interview variables
in the same way that the [`all_variables()`] function does.  Like
[`all_variables()`], it takes an optional keyword argument
`include_internal`, which is `False` by default, but when `True`,
includes internal variables in the output.

## <a name="command"></a>command()

{% include side-by-side.html demo="exit" %}

The `command()` function allows the interview developer to trigger an
exit from the interview using code, rather than having the user click
an `exit`, `restart`, `leave` or `signin` button.

The first argument to `command()` is one of the following:

* `'restart'`: deletes the user's answers and puts them back at the
  start of the interview.
* `'new_session'`: starts a new session for the same interview without
  deleting the user's answers.
* `'exit'`: deletes the user's answers and redirects them to a web site
* `'logout'`: logs the user out and redirects them to a web site.
* `'exit_logout'`: deletes the user's answers, logs the user out (if
  logged in) and redirects them to a web site.
* `'leave'`: redirects the user to a web site without deleting the
  user's answers.
* `'signin'`: redirects the user to the sign-in screen.

The optional keyword argument `url` provides a URL to which the user
should be redirected.  The value of [`exitpage`] will be used if no
`url` is provided.

Note that the [special buttons] perform a similar function to
`command()`.  See also the [starting an interview from the beginning]
subsection for URL parameters that reset interview sessions.

One use of `command()` is to delete interviews after a period of
inactivity.  See [scheduled tasks] for more information.  In the
context of [scheduled tasks], you can pass the optional keyword
argument `sleep` with a number of seconds that you want to pause after
the session is deleted.  This can be useful when your [scheduled
tasks] would overwhelm your SQL server if executed one after another
without pauses.

# <a name="texttransformation"></a>Text transformation functions

## <a name="from_b64_json"></a>from_b64_json()

Takes a string as input, converts the string from base-64, then parses
the string as [JSON], and returns the object represented by the
[JSON].

This is an advanced function that is used by software developers to
integrate other systems with **docassemble**.

## <a name="plain"></a><a name="bold"></a><a name="italic"></a>plain(), bold(), and italic()

The functions `plain()`, `bold()`, and `italic()` are useful when
including variables in a template.

For example, if you write:

{% highlight yaml %}
subquestion: |
  * Your phone number: **${ phone_number }**
  * Your fax number: **${ fax_number }**
{% endhighlight %}

Then the values of the two variables will have bold face [markup],
but if one of them is empty, you will get asterisks instead of what
you presumably wanted, which was no text at all.

> * Your phone number: **202-555-2030**
> * Your fax number: &#42;&#42;&#42;&#42;

Instead, you can write:

{% highlight yaml %}
subquestion: |
  * Your phone number: ${ bold(phone_number) }
  * Your fax number: ${ bold(fax_number) }
{% endhighlight %}

This leads to:

> * Your phone number: **202-555-2030**
> * Your fax number:

Alternatively, you can pass an optional keyword argument, `default`,
if it should plug in something different when empty.

{% highlight yaml %}
subquestion: |
  * Your phone number: ${ bold(phone_number, default='Not available') }
  * Your fax number: ${ bold(fax_number, default='Not available') }
{% endhighlight %}

This leads to:

> * Your phone number: **202-555-2030**
> * Your fax number: **Not available**

Calling `italic('apple')` function returns `_apple`.

The `plain()` function does not supply any formatting, but it
will substitute the `default` keyword argument.

## <a name="space_to_underscore"></a>space_to_underscore()

If `user_name` is `John Wilkes Booth`,
`space_to_underscore(user_name)` will return `John_Wilkes_Booth`.
This is useful if you do not want spaces in the filenames of your
[attachments]. This function will also do [basic filename sanitization](https://werkzeug.palletsprojects.com/en/0.16.x/utils/#werkzeug.utils.secure_filename)
to remove dangerous characters and command injection.

{% highlight yaml %}
---
sets: user_done
question: Thanks!
subquestion: Here is your letter.
attachment:
  - name: A letter for ${ user_name }
    filename: Letter_for_${ space_to_underscore(user_name) }
    content file: letter.md
---
{% endhighlight %}

## <a name="single_to_double_newlines"></a>single_to_double_newlines()

Under the rules of [Markdown], you need to insert two newlines to
break a paragraph.  Sometimes you have text where one newline
represents a paragraph, but you want the single newlines to count as
paragraph breaks.  The function `single_to_double_newlines()` will
convert the text for you.

{% include side-by-side.html demo="single_to_double_newlines" %}

## <a name="single_paragraph"></a>single_paragraph()

`single_paragraph(user_supplied_text)` will replace any linebreaks in
`user_supplied_text` with spaces.  This allows you to do things like:

{% highlight yaml %}
---
question: Summary of your answers
subquestion: |
  When I asked you the meaning of life, you said:

  > ${ single_paragraph(meaning_of_life) }

field: ok_to_proceed
---
{% endhighlight %}

If you did not remove line breaks from the text, then if the
`meaning_of_life` contained two consecutive line breaks, only the
first paragraph of the answer would be indented.

## <a name="verbatim"></a>verbatim()

If you are inserting user-supplied input into a document or onto the
screen, it is possible that the text may contain characters that will
result in undesired formatting changes.  For example, the input may
contain Markdown codes, HTML codes, or LaTeX codes.  To avoid the
effects of such characters, wrap the text with the `verbatim()`
function.

{% include side-by-side.html demo="verbatim" %}

## <a name="quote_paragraphs"></a>quote_paragraphs()

The `quote_paragraphs()` function adds [Markdown] to text so that it
appears as a quotation.

{% include side-by-side.html demo="quote_paragraphs" %}

## <a name="indent"></a>indent()

The `indent()` function adds four spaces to the beginning of each line
of the given [Markdown] to text.  This needs to be used if you are
inserting a [table] or a paragraph of user text into the context of a
[Markdown] bullet-point or itemized list, and you want the text to be
part of an item.  If you do not indent the text, the text will be
treated as a new paragraph that ends the list.

{% include side-by-side.html demo="indent" %}

## <a name="fix_punctuation"></a>fix_punctuation()

The `fix_punctuation()` function ensures that the given text ends with
a punctuation mark.  It will add a `.` to the end of the text if no
punctuation is present at the end.  To use a different punctuation
mark, set the optional keyword argument `mark` to the text you want to
use.

A call to `fix_punctuation(reason)` will return:

* `I have a valid claim.` if `reason` is `I have a valid claim`
* `I have a valid claim.` if `reason` is `I have a valid claim.`
* `I have a valid claim!` if `reason` is `I have a valid claim!`
* `I have a valid claim?` if `reason` is `I have a valid claim?`

{% include side-by-side.html demo="fix-punctuation" %}

## <a name="redact"></a>redact()

The `redact()` function is used when preparing redacted and unredacted
versions of a document.  For example, instead of referring to
`client.ssn` in a document, you can refer to `redact(client.ssn)`.
Then, in the final document, a redaction mark will be included instead
of the client's Social Security number.  However, if the document is
assembled with [`redact: False`], the Social Security number will be
included.

Here is an example of `redact()` being used when generating a PDF and
RTF file from [Markdown]:

{% include side-by-side.html demo="redact" %}

Here is the same example, but with a [`docx template file`] named
[redact_demo.docx]:

{% include demo-side-by-side.html demo="redact-docx" %}

Here is the same example, but with a [`pdf template file`] named
[redact_demo.pdf]:

{% include demo-side-by-side.html demo="redact-pdf" %}

The `redact()` function is intended to be called the markup of
documents, as demonstrated in the various examples above.  It is only
in this context that the `redact()` function knows whether you have
set `redact: False` or not.  The `redact()` function can be from other
contexts, but the result may not be what you want; for example, you
may see redactions even though you set `redact: False`.  If you define
a variable `ssn_text = redact(user.ssn)`, and the `ssn_text` variable
is already defined by the time **docassemble** gets around to
assembling a document with the `redact` option set to `False`, then
your "unredacted" document will contain a redacted Social Security
number.

# <a name="actions"></a>Functions for interacting with the interview using URLs

Normally, when **docassemble** figures out what [`question`] to ask,
it simply evaluates the [interview logic]: it goes through the [YAML]
from top to bottom, and runs anything marked as [`initial`] or
[`mandatory`] (skipping over [`mandatory`] blocks that have already
been processed), and if it encounters an undefined variable, it seeks
a definition of that undefined variable by running blocks that offer
definitions of those variables.

Sometimes, however, you may want to direct **docassemble** to perform
a specific task other than evaluating the current state of the
[interview logic].  The mechanism for doing that is called the
"actions" mechanism.

An "action" is similar to a function call in computer programming.
When you call a function, you might call `cancel_application()` or
`submit_application(user, details)`.  Running `cancel_application()`
just runs a function called `cancel_application`.  Running
`submit_application(user, details)` runs a function called
`submit_application`, and passes `user` and `details` to the function;
these are referred to as the "arguments" of the function.

Here is some made-up code that illustrates how traditional functions work:

{% highlight python %}

def cancel_application():
  central_authority = CentralAuth(hostname='central-authority.example.com')
  payload = {'type': 'cancel'}
  send(payload, central_authority)

def submit_application(user, details):
  central_authority = CentralAuth(hostname='central-authority.example.com')
  payload = {'type': 'submit', 'user': user, 'details': details}
  send(payload, central_authority)
{% endhighlight %}

In **docassemble**, an "action" consists of an action name and an
optional [dictionary] of arguments.  When you call the action
`cancel_application`, **docassemble** will seek out a block in your
[YAML] that offers to define `cancel_application`, and will run that
`block`.  To locate this block, it uses the same process that it uses
when it seeks a block that defines an undefined variable.

Here is how you would implement the functions above as "actions" in
your interview [YAML]:

{% highlight yaml %}
event: cancel_application
code: |
  send({'type': 'cancel'}, CentralAuth(hostname='central-authority.example.com'))
---
event: submit_application
code: |
  send({'type': 'submit', 'user': action_argument('user'), 'details': action_argument('details')}, CentralAuth(hostname='central-authority.example.com'))
{% endhighlight %}

Writing `event: cancel_application` means "this block advertises that
it defines `cancel_application`.  You may have seen [`event`] used
before in a context like this:

{% highlight yaml %}
mandatory: True
code: |
  intro_screen
  favorite_fruit
  final_screen
---
event: final_screen
question: Thank you for answering my questions today.
subquestion: |
  I like ${ favorite_fruit } as well.
{% endhighlight %}

When a variable name is referenced, its definition will be sought if
the variable is undefined, but if the variable is defined, it will
continue running the Python code.  The `final_screen` [`question`] is
different, though, because it is a dead end; `final_screen` is a
variable name that will never actually get defined.


The arguments to the action

## <a name="url_action"></a><a name="process_action"></a>url_action() and process_action()

The `url_action()` function allows users to interact with
**docassemble** using hyperlinks embedded in questions.

`url_action()` returns a URL that, when clicked, will perform an
"action" within **docassemble**, such as running some code or asking a
question.  Typically the URL will be part of a [Markdown] link inside
of a [question], or in a `note` within a set of [fields].

The [`process_action()`] function triggers the processing of the
"action."  It is typically called for you, behind-the-scenes, but you
can call it explicitly if you want to control exactly when (and if) it
is called.  For more information about calling [`process_action()`]
explicitly, see the section on the [interaction of user roles and
actions].

Here is an example:

{% include side-by-side.html demo="lucky-number" %}

When the user clicks one of the links, the interview will load as
usual (much as if the user refreshed the web browser page).  The only
difference is that **docassemble** sees the additional information
stored in the URL and makes that information available to the
interview logic.

In the above example, when the user clicks on the link generated by
`url_action('lucky_color')`, the interview will load as normal.
Before [`initial`] and [`mandatory`] blocks are processed,
**docassemble** will run the function `process_action()`.  The
`process_action` function will check to see if any "actions" have been
requested.  In this case, it will find that the `'lucky_color'` action
was requested.  As a result, **docassemble** will look for a
`question` or `code` block that defines `lucky_color`.  (Internally,
it calls [`force_ask()`].)  Since there is a question in the interview
that offers to define `lucky_color`, that question will be asked.

When the user clicks on the link generated by
`url_action('set_number_event', increment=1)`, the `process_action()`
function will look for a `question` or `code` block that defines
`set_number_event`.  It will find the `code` block that was labeled
with `event: set_number_event`.  (See [Setting Variables] for more
information about [`event`]s.)  It will then run that code block.
Note how the [Python] code within that block knows the value of
`increment` which had been specified in the `url_action` function: it
retrieves it with [`action_argument()`].

The `process_action` function runs every time the screen loads, but it
will do nothing if the user did not click on a link generated by
`url_action`.

You can pass as many named parameters as you like to an "action."  For
example:

{% highlight yaml %}
---
question: Hello
subquestion: |
  You can set lots of information by [clicking this link](${
  url_action('set_stuff', fish='trout', berry='strawberry',
  money=65433, actor='Will Smith')}).
---
event: set_stuff
code: |
  info = action_arguments()
  user_favorite_fish = info['fish']
  user_favorite_fruit = info['berry']
  if info['money'] > 300000:
    user_is_rich = True
  actor_to_hire = info['actor']
---
{% endhighlight %}

In this example, we use [`action_arguments()`] to retrieve all of the
arguments to [`url_action()`] as a [Python dictionary].

You can control whether and when the "action" will be performed by
placing the `process_action()` statement in a particular place in your
[`initial`] code.  For example, you might want to ensure that actions
can only be carried out if the user is logged in:

{% highlight yaml %}
---
initial: True
code: |
  if user_logged_in():
    process_action()
---
{% endhighlight %}

Note that these links will only work for the current user, whose
access credentials are stored in a cookie in his or her browser.  It
is possible for actions to be run by a "third party."  For information
on how to do this, see [`interview_url_action()`] and [scheduled
tasks].

## <a name="action_menu_item"></a>action_menu_item()

One way to let the user trigger "[actions]" is to provide a selection in
the menu of the web app.  You can do this by setting the `menu_items`
list.  See [special variables] section for more information about
setting menu items.

{% highlight yaml %}
---
mandatory: True
code: |
  menu_items = [ action_menu_item('Review Answers', 'review_answers') ]
---
{% endhighlight %}

In this example, a menu item labeled "Review Answers" is added, which
when run triggers the action "review_answers."

The `action_menu_item(a, b)` function returns a [Python dictionary] with
keys `label` and `url`, where `label` is set to the value of `a` and
`url` is set to the value of `url_action(b)`.

## <a name="interview_url"></a>interview_url()

The `interview_url()` function returns a URL to the interview that
provides a direct link to the interview and the current variable
store.  This is used in [multi-user interviews] to invite additional
users to participate.

{% include side-by-side.html demo="interview-url" %}

People who click on the link (other than the current user) will not be
able to access the interview answers unless [`multi_user`] is set to
`True`.  This is because interviews are encrypted on the server by
default.  Setting [`multi_user`] to `True` disables this encryption.
Note that the communication between **docassemble** and the browser
will always be encrypted if the site is configured to use [HTTPS].
The server-side encryption merely protects against the scenario in
which the server running **docassemble** is compromised.

You can include keyword arguments to `interview_url()`.  These will be
passed to the interview as [`url_args`].

The keyword argument `i` is special, however: you can set this to the
name of an interview (e.g.,
`docassemble.demo:data/questions/questions.yml`) and this interview
will be used instead of the current interview.  In this case, the URL
functions as a referral to a different interview, with a fresh
variable store.

The keyword argument `session` is also special: set this to the
session ID of an interview (e.g., obtained from [`interview_list()`]),
and also set `i` to the filename of the interview corresponding with
the session.  Then the link will point not to the current session, but
to the session indicated by the session ID.

The keyword argument `local` is also special: set this to `True` if
you want the URL to be relative (i.e., it will start with `?`).  Note
that for purposes of the "copy link" feature of web browsers, this
does not matter; the web browser will provide a full URL even if the
underlying URL is relative.  However, **docassemble** treats URLs
differently if they begin with `http:`/`https:` or `?`: links that
begin with `http` will open in another tab.

The keyword argument `style` is also special: set this to `'short'` if
you want the URL to begin with `/run` instead of `/interview`.  This
will use `/run/shortcutname` format if the interview is listed in
[`dispatch`], and otherwise will use `/run/packagename/filename`
format.  In the absence of a `style` argument, the URL returned by
`interview_url()` in the context of the web application will use the
style of the URL that is in the location bar of the web browser.  If
the URL in the location bar is `/run/packagename/filename`, the URL
returned by `interview_url()` will be `/run/packagename/filename`.
However, if `interview_url()` is called by a background process or a
call to the API, `interview_url()` will return
`/interview?i=docassemble.packagename:data/questions/filename.yml` by
default, unless a `style` is specified.

There are security risks with URLs created using `interview_url()`.
The URLs contain a `session` key, and if `multi_user` is `True`,
anyone with that `session` key can access the interview session.  If
you e-mail the result of `interview_url()`, the `session` key may be
stored permanently in the person's e-mail account, where a third party
may see it.

One way around this potential security risk is to set the keyword argument
`temporary`.  Then a special URL will be returned, which will contain
a code that will expire after a certain number of hours.  For example,
if you add `temporary=48` to the keyword arguments, the link will
expire after 48 hours.  When the user clicks visits the link, the user
will be redirected to the location that `interview_url()` would return
if `temporary` was not set.  By using a temporary URL, you will avoid
sharing the actual session ID, and you will protect against any
unauthorized access that would take place after 48 hours have expired.

{% include side-by-side.html demo="interview-url-temp" %}

If you set `temporary` to `0` or to a non-number, the expiration
period will default to 24 hours.

You can add additional security by using the keyword argument
`once_temporary` instead of the keyword argument `temporary`.  This
works the same way as `temporary`, except the link will also expire
immediately after it is used for the first time.

## <a name="interview_url_as_qr"></a>interview_url_as_qr()

`interview_url_as_qr()` is like `interview_url()`, except it inserts
into the markup a [QR code] linking to the interview.  The resulting
[QR code] can be used to pass control from a web browser or a paper
handout to a mobile device.

## <a name="interview_url_action"></a>interview_url_action()

`interview_url_action()` is like [`interview_url()`], except that it
also has the effect of running [`url_action()`].  You will want to use
this instead of [`url_action()`] if you want the user to be able to
share the URL with other people, or run it unattended.

{% include side-by-side.html demo="interview_url_action" %}

Note that in this example, [`multi_user`] is set to `True`.  This
disables server-side encryption of answers.  This is necessary because
the encryption uses an decryption key, and a decryption key should not
be embedded in a URL.

The first argument to `interview_url_action()` is the name of the
action.  The keyword arguments are the arguments of the action.  In
this respect, `interview_url_action()` is similar to
[`url_action()`].  However, the following keyword arguments have
special meaning:

* `i` - if you set an `i` parameter, `interview_url_action()` will
  form a URL for an interview other than the current interview.  The
  current session ID will not be included by default in the URL.
* `session`: if you set a `session` parameter, the value of `session`
  will be used as the session ID.  This will allow the user of the URL
  to resume an existing interview session other than the current
  interview session.  By default, if `i` is not set, the session ID of
  the current session is included in the URL, which allows the user of
  the URL to resume the current interview session
* `local`: if you set the `local` parameter to a true value, then a
  relative URL will be returned.  By default, `interview_url_action()`
  returns a complete URL.
* `new_session`: if you set the `new_session` parameter to a true
  value, then `new_session=1` will be included in the URL.  Set this
  if you are providing an `i` parameter and you want to make sure that the
  user of the URL starts a new session rather than resuming an
  existing one.
* `reset`: if you set the `reset` parameter to a true value, then
  `reset=1` will be included in the URL.  Set this if you are
  providing an `i` parameter and you want the user of the URL to
  restart any existing session they may be using in the interview
  indicated by `i`.

## <a name="interview_url_action_as_qr"></a>interview_url_action_as_qr()

`interview_url_action_as_qr()` is like `interview_url_action()`,
except it inserts into the markup a [QR code] linking to the
interview, with the specified actions.

Note that there is a limit to the number of characters a [QR code] can
hold, and you might run up against this limit if you try to add too
many arguments to the URL.  Using the `temporary` keyword parameter is
one way around this limitation.

## <a name="action_arguments"></a>action_arguments()

The `action_arguments()` function returns a dictionary with any
arguments that were passed when the user clicked on a link generated
by [`url_action()`] or [`interview_url_action()`].

## <a name="action_argument"></a>action_argument()

The `action_argument()` function is like [`action_arguments()`],
except that it returns the value of a given argument.

For example, if you formed a URL with:

{% highlight yaml %}
---
question: |
  The total amount of your bill is ${ currency(bill + tip) }.
subquestion: |
  [Tip your waiter $10](${ url_action('tip', amount=10)}).

  [Tip your waiter $20](${ url_action('tip', amount=20)}).
---
{% endhighlight %}

Then you could retrieve the value of `amount` by doing:

{% highlight yaml %}
---
event: tip
code: |
  tip = action_argument('amount')
---
{% endhighlight %}

If you are writing an [`initial`] block that calls `process_action()`
and you want to know the name of the action itself before you call
`process_action()`, you can retrieve the name of the action by calling
`action_argument()` without an argument.  This will return the name of
the action itself.  If the result is `None`, then no action was called
for the current request (and `process_action()` will not do anything).

You can only retrieve the action name with `action_argument()` before
you call `process_action()`.  During the processing of the action, and
after `process_action()` returns, `action_argument()` will always
return `None`.

## <a name="url_of"></a>url_of()

This function returns a URL to a file within a **docassemble**
package's `static` folder.

For example, you might have PDF files associated with your interview.
You would keep these in the `data/static` directory of your package,
and you would refer to them by writing something like:

{% highlight yaml %}
---
mandatory: True
question: You are done.
subquestion: |
  To learn more about this topic, read
  [this brochure](${ url_of('docassemble.mycompany:data/static/brochure.pdf') }).
---
{% endhighlight %}

You can also refer to files in the current package by leaving off the
package part of the file name:

{% highlight yaml %}
---
mandatory: True
question: You are done.
subquestion: |
  To learn more about this topic, read
  [this brochure](${ url_of('brochure.pdf') }).
---
{% endhighlight %}

If you do not specify a package, **docassemble** will look for the
file in the `static` folder of the package in which the current
[`question`] or current [`code`] block resides.

### Special uses

The `url_of()` function also has a few special uses.

* If applied to a [`DAFile`] object, it will return a URL to the file.
* `url_of('help')` returns a URL that causes the help tab to be shown,
  if there is a help tab.
* `url_of('login')` returns a URL to the sign-in page.  It takes an
  optional keyword parameter `next`, which you can set to a URL if you
  want the user to be directed to a particular URL after they log in.
* `url_of('signin')` does the same thing as `url_of('login')`.
* `url_of('restart')` returns a URL that will delete the current
  session and restart it with the same URL parameters.
* `url_of('new_session')` returns a URL that starts a new session of
  the current interview, preserving the existing session.
* `url_of('exit')` returns a URL that deletes the interview session
  and redirects to the URL at the `next` parameter, or to the
  [`exitpage`] if there is no `next` parameter.
* `url_of('interview')` returns a URL to the interview page.  (See
  also [`interview_url()`].)
* `url_of('logout')` returns a URL that logs the user out.  It accepts
  a `next` parameter.
* `url_of('exit_logout')` returns a URL that deletes the interview session,
  logs the user out (if the user is logged in), and redirects to the
  URL at the `next` parameter, or to the [`exitpage`] if there is no
  `next` parameter.
* `url_of('leave')` redirects to the URL at the `next` parameter, or to the
  [`exitpage`] if there is no `next` parameter.  It does not log the
  user out or delete the interview session.
* `url_of('register')` returns a URL to the user registration page.
  It accepts a `next` parameter.
* `url_of('profile')` returns a URL to the logged-in user's profile page.
* `url_of('change_password')` returns a URL to a page where a logged-in user
  can change his or her password.
* `url_of('interviews')` returns a URL to the page listing the
  on-going interviews of a signed-in user.
* `url_of('dispatch')` returns a URL to the page listing the
  interviews defined in the [`dispatch`] directive of the [Configuration].
* `url_of('manage') returns a URL to a page where the user can delete
  his or her account data.
* `url_of('config')` returns a URL to the [Configuration] page.
* `url_of('playground')` returns a URL to the [Playground].
* `url_of('playgroundtemplate')` returns a URL to the Templates folder
  of the [Playground].
* `url_of('playgroundstatic')` returns a URL to the Static folder of
  the [Playground].
* `url_of('playgroundsources')` returns a URL to the Sources folder of
  the [Playground].
* `url_of('playgroundmodules')` returns a URL to the Modules folder of
  the [Playground].
* `url_of('playgroundpackages')` returns a URL to the Packages folder
  of the [Playground].
* `url_of('configuration')` returns a URL to the [Configuration] page.
* `url_of('root')` returns the root URL of your server.

By default, `url_of()` returns relative URLs, which begin with `/`.
However, if you want a full URL, you can call, e.g., `url_of('root',
_external=True)`.

You can set `_attachment=True` if you want the user to download the
file.  This only works when `url_of()` refers to a file.

The `url_of()` function can also be used to format URLs with
parameters.  For example, `url_of('https://example.com', query="Hello, world!")`
becomes `https://example.com?query=Hello%2C+world%21`.

You can also use this feature to format `mailto:` URLs:

{% highlight yaml %}
question: |
  What e-mail would you like to send?
fields:
  - To: addressee
    datatype: email
  - Subject: subject
  - Body: body
    input type: area
---
mandatory: True
question: |
  Draft e-mail
subquestion: |
  [Your draft e-mail](${ url_of('mailto:' + addressee, subject=subject, body=body) })
  is ready.
{% endhighlight %}

## <a name="url_ask"></a>url_ask()

The `url_ask()` function is like [`url_action()`], except instead
of accepting a single action name and optional arguments, it accepts a
single data structure, which is treated like the `fields` specifier
inside an item of a [`review`] block.  It returns a URL that will
result in the asking of certain [`question`]s when the user visits it.

* `url_ask('favorite_fruit')` - Ask the [`question`] that defines `favorite_fruit`.
* `url_ask(['favorite_fruit', 'favorite_vegetable'])` - Ask the
  [`question`] that defines `favorite_fruit`, then ask the [`question`] that defines `favorite_vegetable`.
* `url_ask(['favorite_fruit', {'follow up': ['favorite_apple']},
  'favorite_vegetable'])` - Ask the
  [`question`] that defines `favorite_fruit`; then ask the [`question`]
  that defines `favorite_apple`, if such a [`question`] can be found;
  then ask the [`question`] that defines `favorite_vegetable`.
* `url_ask(['favorite_fruit', {'recompute': ['fruit_to_offer']},
  'favorite_vegetable'])` - Ask the [`question`] that defines
  `favorite_fruit`; then undefine the variable `fruit_to_offer` if it
  is defined; then compute the value of `fruit_to_offer`; then ask the
  [`question`] that defines `favorite_vegetable`.

For more information on how these data structures work, see the
subsection on [customizing the display of `review` options].

## <a name="action_button_html"></a>action_button_html()

The `action_button_html()` function returns the HTML of a
Bootstrap-formatted button (an `<a>` tag styled as a button) that
visits a given URL.  It is often given the output of [`url_ask()`] or
[`url_action()`], but you can give it any URL.

{% include side-by-side.html demo="action-button-html" %}

It accepts the following optional keyword arguments:

* `icon` - this is the name of the [Font Awesome] icon to use at the
  start of the button.  It can take a value like `'pencil-alt'`.  By
  default, the icon is assumed to be in the "solid" collection
  (`fas`).  To use a different collection, specify a name such as
  `fab-fa-windows` for the `windows` icon in the "brand" collection.
  If you do not want any icon, set `icon` to `None`.  The default is
  `None`.
* `color` - this is the Bootstrap color of the button.  The options
  are `primary`, `secondary`, `success`, `danger`, `warning`, `info`,
  `light`, `link`, and `dark`.  The default is `'dark'`.  The actual
  colors depend on the Bootstrap theme.
* `size` - this is the Bootstrap size of the button.  The options are
  `'sm'`, `'md'`, and `'lg'`.  The default is `'sm'`.
* `block` - if set to `True`, the button will fill the width of the
  question area.
* `label` - this is the text on the button.  It passes through the
  [`word()`]  function, so you can use the translation system to
  handle different languages.
* `classname` - set this to one or more class names (separated by a
  space) if you want to add additional [CSS] classes to the button.
* `new_window` - set this to `False` if you don't want the button to
  open a new tab.  The default value is `True`, which means external
  links will open in a new tab.  If you use a value other than `True`
  or `False`, it will be used as the `target` of the hyperlink.
* `id_tag` - if you want your button to have an `id` so that you can
  manipulate it with [JavaScript], set `id_tag` to the `id` you want
  to use.  For example, if you don't want the button to actually visit
  a link, you can do `action_button_html('#', label="Click me",
  id_tag="mybutton")` and then write [JavaScript] code that does something
  like `$("#mybutton").click(function(e){e.preventDefault();
  console.log("Hello"); return false;})`.

# <a name="qrfunctions"></a>QR code functions

## <a name="qr_code"></a>qr_code()

The `qr_code()` function allows you to include the `[QR ...]` [markup] statement
using [Python].

{% include side-by-side.html demo="qr-code" %}

These two questions are equivalent:

{% highlight yaml %}
question: |
  Here is a QR code.
subquestion: |
  Go to Google:

  ${ qr_code('http://google.com', width='200px') }

  Or go to Yahoo:

  ${ qr_code('http://yahoo.com') }
{% endhighlight %}

{% highlight yaml %}
question: |
  Here is a QR code.
subquestion: |
  Go to Google:

  [QR http://google.com, 200px]

  Or go to Yahoo:

  [QR http://yahoo.com]
{% endhighlight %}

For more information about what the `[QR ...]` [markup] statement
does, see the [QR markup documentation].

Note that if you want to include a QR code that points to an interview
or an interview action, there are shorthand functions for that.  See
[`interview_url_as_qr()`](#interview_url_as_qr) and
[`interview_url_action_as_qr()`](#interview_url_action_as_qr).

## <a name="read_qr"></a>read_qr()

This function reads QR codes from one or more image files and returns
a [Python list] with the encoded text string or strings.

{% include side-by-side.html demo="read-qr" %}

The first argument must be a [`DAFile`] or [`DAFileList`] object.  If
the argument is a [`DAFileList`] with more than one file, all files
(and all pages within all files) will be scanned for QR codes.

The function accepts image files (JPEG, PNG, etc.) as well as PDF
files.  If you provide PDF files, the following optional parameters
customize the reading of the PDF files (they are passed directly to
[pdftoppm]).

* `f` indicates the first page of the PDF file to read.  By
  default, all pages are read.
* `l` indicates the last page of the PDF file to read.  By
  default, all pages are read.
* `x`: for cropping PDF pages.  Indicates the x-coordinate of the crop
  area's top left corner, in pixels.  (By default, PDF files are
  converted at 300 dpi unless another value is given by the
  [`ocr dpi`] configuration directive.)
* `y`: for cropping PDF pages.  Indicates the y-coordinate of the crop
  area's top left corner, in pixels.
* `W`: for cropping PDF pages.  Indicates the width of the crop area
  in pixels (default is 0).
* `H`: for cropping PDF pages.  Indicates the height of the crop area
  in pixels (default is 0).

The function returns a [Python list] with the codes found, in the
order in which they were found.

# <a name="emailfunctions"></a>E-mail functions

## <a name="send_email"></a>send_email()

The `send_email()` function sends an e-mail using [Flask-Mail].

{% include side-by-side.html demo="send-email" %}

All of the arguments to `send_email()` are [keyword arguments]:

* `to` expects a list of [`Individual`]s, or [`Person`]s,
  [`DAEmailRecipient`]s, or plain e-mail addresses.  It also accepts a
  single item of any of these.
* `sender` expects a single [`Individual`].  If not set, the
  `default_sender` information from the [configuration] is used.
* `cc` expects a [list] of [`Individual`]s, or `None`.
* `bcc` expects a [list] of [`Individual`]s, or `None`.
* `body` expects text, or `None`.  Will set the plain text content of
  the e-mail.
* `html` expects text, or `None`.  Will set the (optional) [HTML]
  content of the e-mail.
* `subject` expects text, or `None`.  Will set the subject of the
  e-mail.  The default is `""`.
* `template` expects a [`template`] object, or `None`.  These
  templates can be created in an interview file using the `template`
  specifier.  If this [keyword argument] is supplied, both the plain
  text and [HTML] contents of the e-mail will be set by converting the
  [Markdown] text of the template into [HTML] and by converting the
  [HTML] to plain text (using [html2text]).  In addition, the subject
  of the e-mail will be set to the subject of the template.  You can
  override any of these behaviors by manually specifying `body`,
  `html`, or `subject`.
* `task` expects the name of a [task].  If this argument is provided,
  and if sending the e-mail is successful, the task will be marked as
  having been performed (i.e., [`mark_task_as_performed()`] will be
  called).  Alternatively, you can handle this in your own code, but
  you might find it convenient to let the `send_email()` function
  handle it for you.
* `task_persistent`: if you set a `task`, you can optionally set
  the "persistence" of the task by setting this to `True` or a value
  like `'user'`.  For more information, see the documentation for the
  [task-related functions](#tasks).
* `attachments` expects a [list] of [`DAFile`], [`DAFileList`], or
  [`DAFileCollection`] objects.  You can include:
  * Images generated by `signature` blocks (objects of class
  [`DAFile`]);
  * File uploads generated by including [fields] of [`datatype: file`] or
  [`datatype: files`] in a [`question`] (objects of class [`DAFileList`]);
  * [Documents] generated by [`attachments`] to a [`question`] for which a
  `variable` was provided (objects of class [`DAFileCollection`]).
* `mailgun_variables` expects a [dictionary] of [user variables] that
  should be passed to the [Mailgun API].  This is only applicable if
  you are using the [Mailgun API] for [e-mail sending].
* `dry_run` can be set to `True` if you want to do a "dry run" of the
  e-mail sending process.  You would use this if you wanted to make
  sure that all of the variables `send_email()` needs are defined
  before you actually send the e-mail.  The default is `False`.

It uses the `name` and `email` attributes of the listed [`Individual`]s
to form e-mail addresses.

`send_email()` returns `False` if an error prevented the e-mail from
being delivered to the mail server; otherwise it returns `True`.  Note
that this function might return `True` even though no e-mail is
actually delivered to the recipient; the return value indicates only
whether there was a problem sending the e-mail with [Flask-Mail].

See [configuration] for information about how to configure the mail
server that `send_email()` will use.

Here is an example of sending an attachment via e-mail:

{% include side-by-side.html demo="send-email-with-attachment" %}

Sending e-mail can be slow.  If you call `send_email()` from within
your interview logic, the user might have to look at a spinner.  In
order to provide a better experience to users, you may wish to call
`send_email()` from within a [background process].

## <a name="interview_email"></a>interview_email()

The `interview_email()` function returns an e-mail address that the
user can use to send a message to the interview.  For more information
about how users can send e-mails to interview sessions, see the
documentation for the [e-mail to interview] feature.

If the [`incoming mail domain`] directive in your [configuration] is
`help.example.com`, then `interview_email()` will return something
like `kgjeir@help.example.com`.

The address returned by `interview_email()` is a unique random
sequence of six lowercase letters.  If any e-mails are received at
this e-mail address, **docassemble** will associate them with the
user's session and the e-mails can be retrieved with [`get_emails()`].

The result returned by `interview_email()` will be unique to the
session.  Every time your interview calls `interview_email()`, the
same e-mail address will be returned.

You can also associate more than one e-mail address with the session,
if you wish.  For example, in a litigation application, you may want
to have one e-mail address for receiving evidence from the client and
another address for corresponding with opposing counsel.  You can
obtain these different e-mail addresses using the optional keyword
argument `key`.  For example, `interview_email(key='evidence')` and
`interview_email(key='opposing counsel')` will return different unique
addresses.

If you are using a `key` to get an e-mail address, you can also
set the optional keyword argument `index` to an integer.  For example,
if there are multiple opposing counsel and you want a separate e-mail
address for each one, you can use `interview_email(key='opposing
counsel', index=1)`, `interview_email(key='opposing
counsel', index=2)`, etc.

## <a name="get_emails"></a>get_emails()

The `get_emails()` function returns a [list] of objects representing
e-mail addresses generated with [`interview_email()`].  For more
information about how users can send e-mails to interview sessions,
see the documentation for the [e-mail to interview] feature.

Each object in the [list] returned by `get_emails()` has the following
attributes:

* `address`: the part of the e-mail address before the `@`.
* `emails`: a [list] of [`DAEmail`] objects representing e-mails that
  have been sent to the e-mail address.
* `key`: the `key` associated with the e-mail address, which is `None`
  if you did not supply a `key` to [`interview_email()`]
* `index`: the `index` associated with the e-mail address, which is
  `None` if you did not supply an `index` to [`interview_email()`].

If you used `key` with [`interview_email()`], you can use the optional
`key` and `index` keyword arguments to `get_emails()` in order to
filter the results.  For example, `get_emails(key='evidence')` will
only return information about e-mail addresses created with
`interview_email(key='evidence')`.  Calling
`get_emails(key='evidence', index=2)` will limit the [list] even further
to the e-mail address created by `interview_email(key='evidence',
index=2)`.

# <a name="faxfunctions"></a>Fax functions

## <a name="send_fax"></a>send_fax()

The `send_fax()` function sends a PDF document as a fax.  It requires
a [`twilio`] configuration in which `fax` is set to `True`.

`send_fax()` takes two arguments, a destination and a file.

{% highlight yaml %}
objects:
  - user: Individual
---
question: |
  What is your fax number?
fields:
  - Fax: user.fax_number
---
question: |
  What file would you like
  me to fax?
fields:
  - File: document
    datatype: file
---
code: |
  fax_result = send_fax(user, document)
---
mandatory: True
question: |
  % if fax_result.received():
  The fax was received.
  % else:
  The status of the fax is
  ${ fax_result.status() }.
  % endif
reload: True
{% endhighlight %}

The destination can be a [`Person`] or a fax number.  If it is a
[`Person`], the fax number will be obtained from the `fax_number`
attribute of the object.  The `send_fax()` function will convert the
fax number to [E.164] format.  To do so, it will need to determine the
appropriate [country calling code] for the phone number.  This country
code will be based on the `country` attribute of the object, or the
`address.country` attribute, but if neither of these attributes is
already defined, the value of [`get_country()`] will be used.  If you
want to use a specific country, you can call `send_fax()` with the
optional keyword parameter `country`.  The format of the `country`
attribute and the keyword parameter is expected to be [ISO 3166-1
alpha-2] format.

The second argument, the file, must be a file object such as a
[`DAFile`], [`DAFileList`], [`DAFileCollection`], or [`DAStaticFile`]
object.

The `send_fax()` function returns an object that represents the status
of the fax sending.  The object has the following methods:

* `.status()` - this will be one of [Twilio]'s [fax status values].
  However, if there is a [Twilio] configuration error, it will be
  `'not-configured'`, and if no result is available, it will be
  `'no-information'`.
* `.pages()` - this will be one of [Twilio]'s [fax status values].
* `.info()` - this will be a [dictionary] containing the
  [status callback values] returned from [Twilio] (excluding the
  `AccountSid`).  If no result is available, this will be a
  [dictionary] with the `FaxStatus` set to `'not-configured'` or
  `'no-information'`.
* `.received()` - this will be `True` or `False` depending on whether
  the fax has been received yet.  It will be `None` if no result is
  available.

Immediately after `send_fax()` is called, the result will likely be
unavailable, because [Twilio] will not have had time to start
processing the request.

In addition, the result will expire 24 hours after the last time
[Twilio] reported a change in the status of the fax sending.  Thus, if
you want to ensure that the outcome of a fax sending gets recorded in
the [interview session dictionary], you should launch a
[`background_action()`] that polls the status, or set up a [scheduled
task] that checks in hourly.

# <a name="geofunctions"></a>Geographic functions

## <a name="map_of"></a>map_of()

The `map_of()` function inserts a Google Map into question text.  (It
does not work within documents.)  The arguments are expected to be
**docassemble** [objects].  Different objects are mapped differently:

* [`Address`] objects: if an [`Address`] object is provided as an argument
  to `map_of()`, a map marker will be placed at the geolocated
  coordinates of the address.  The description of the address will be
  the address itself.
  * _Technical details_: if the object is called `address`, the marker
    will be placed at the coordinates `address.location.latitude` and
    `address.location.longitude`.  (The attribute `address.location`
    is a [`LatitudeLongitude`] object.)  The description of the marker
    will be set to `address.location.description`.  These fields are
    set automatically during the geolocation process, which will take
    place the first time **docassemble** runs `map_of()`, if it has
    not taken place already.  The marker icon can be customized by
    setting `address.icon`.
* [`Organization`] objects: map markers will be placed at the
  locations of each of the organization's offices.  For example, if
  the object name is `company`, markers will be placed on the map for
  each address in `company.office` (which is a list of [`Address`]es).
  The icon for the `i`th office will be `company.office[i].icon`, or,
  if that is not defined, it will be `company.icon` if that is
  defined.  The description of each marker will be the organization's
  name (`company.name.full()`) followed by
  `company.office[i].location.description`.
* [`Person`] objects: a map marker will be placed at the person's
  address.  The description will be the person's name, followed by the
  address.  The marker icon can be customized by setting `person.icon`
  (for a [`Person`] object called `person`).  If the [`Person`] object
  is the user, the default icon is a blue circle.

{% include demo-side-by-side.html demo="testgeolocate" %}

In order for maps to appear, you will need to configure a
[Google API key].  From the [`google`] section of the [configuration],
the `google maps api key` will be used if it exists.  If a
`google maps api key` is not present, the `api key` will be used.

## <a name="location_known"></a>location_known()

Returns `True` or `False` depending on whether **docassemble** was
able to learn the user's GPS location through the web browser.

See [`track_location`] and [`LatitudeLongitude`] for more information
about how **docassemble** collects information about the user's
location.

## <a name="location_returned"></a>location_returned()

Returns `True` or `False` depending on whether an attempt has yet been
made to transmit the user's GPS location from the browser to
docassemble.  Will return true even if the attempt was not successful
or the user refused to consent to the transfer.

See [`track_location`] and [`LatitudeLongitude`] for
more information about how **docassemble** collects information about
the user's location.

## <a name="user_lat_lon"></a>user_lat_lon()

Returns the user's latitude and longitude as a tuple.

See [`track_location`] and [`LatitudeLongitude`] for more information
about how **docassemble** collects information about the user's
location.

## <a name="iso_country"></a>iso_country()

The `iso_country()` function takes a country name or abbreviation as
input and returns a two-character [ISO 3166-1 alpha-2] code or other
[ISO 3166-1] information about a country.

{% include side-by-side.html demo="iso-country" %}

By default, it returns the [ISO 3166-1 alpha-2] country code, but it
can return other things depending on the optional keyword parameter
`part`, which can be set to one of the following values:

* `'alpha_2'` (the default): returns the two-letter country code
  (e.g., `US`).
* `'alpha_3'`: Returns the three-letter country code (e.g., `'USA'`).
* `'name'`: Returns the name of the country (e.g., `'United States'`).
* `'numeric'`: Returns the three-digit country code, as text (e.g., `'840'`).
* `'official_name'`: Returns a long-form name of the country (e.g.,
  `'United States of America'`).

## <a name="countries_list"></a><a name="country_name"></a>countries_list() and country_name()

The `countries_list()` function returns a list of dictionaries, where
each dictionary contains a single key-value pair mapping a two-letter,
capitalized country abbreviation to the name of the country (in
English).  This function is primarily useful when asking a user to
specify his or her country.

The `country_name()` function returns the name of a country (in
English) based on the two-letter, capitalized country abbreviation.

{% include side-by-side.html demo="country" %}

When working with countries, it is a good idea to store country names
in this two-letter, capitalized format ([ISO 3166-1 alpha-2] format).
The country code is used by the [`send_sms()`] function to determine
the appropriate universal formatting of phone numbers.

The data come from the [`pycountry` package].

## <a name="states_list"></a><a name="state_name"></a>states_list() and state_name()

The `states_list()` function returns a list of dictionaries, where
each dictionary contains a single key-value pair mapping a state
abbreviation to the name of a state.  This function is primarily
useful when asking a user to specify his or her state.

The function takes an optional keyword argument `country`, which is
expected to be a country abbreviation ([ISO 3166-1 alpha-2], e.g.,
`'SE'` for Sweden).  If the `country` is not provided, it is assumed
to be the default country (the value returned by [`get_country()`]).
For countries other than the United States, the geographic areas
returned are the first-level subdivisions within the country.  The
name of these subdivisions varies.  The [`subdivision_type()`]
function can be used to find the name of the major subdivision, and
also to find if the country has any subdivisions at all.

The `state_name()` function returns the name of a state based on the
state abbreviation provided.

{% include side-by-side.html demo="state" %}

When working with states, it is a good idea to store state names in
this abbreviated format.

The data come from the [`pycountry` package].

## <a name="subdivision_type"></a>subdivision_type()

Given a country code ([ISO 3166-1 alpha-2]), `subdivision_type()`
returns the name of the primary subdivision within that country.

{% include side-by-side.html demo="subdivision-type" %}

Note that some countries have no subdivisions at all.  In that case,
this function will return `None`.

The data come from the [`pycountry` package].

# <a name="navigation"></a>Navigation and progress bar functions

For more information about the progress bar, see the documentation for
the [progress bar] initial block and the [`progress`] modifier.

For more information about the navigation bar, see the documentation
for the [navigation bar] feature.

## <a name="get_progress"></a>get_progress()

You can retrieve the current numeric value of the progress bar by
calling `get_progress()`.

## <a name="set_progress"></a>set_progress()

You can set the numeric value of the progress bar by calling, e.g.,
`set_progress(20)`.  If you run `set_progress(None)`, the progress
meter will be hidden.  You can also use the [`progress`] modifier on a
[`question`] to set the progress meter to a particular value.

## <a name="DANav.get_section"></a>nav.get_section()

The [navigation bar] is controlled by a [special variable] called
`nav`.  This is a special [Python object] of type [`DANav`].  Access
to the [navigation bar] is achieved by [methods] that act upon this
object.

{% include side-by-side.html demo="sections" %}

You can retrieve the current section by calling `nav.get_section()`.
This will return the keyword corresponding to the current section.
To get the displayed name of the section, call it using
`nav.get_section(display=True)`.  When you call it with
`display=True`, you can also use the optional keyword parameter
`language` to indicate a language to use, if you want the display name
for a language other than the current language.

## <a name="DANav.set_section"></a>nav.set_section()

You can change the current section by calling `nav.set_section()` with
the keyword of the section you want to be the current section.

{% include side-by-side.html demo="sections-keywords-code" %}

## <a name="DANav.get_sections"></a>nav.get_sections()

Calling `nav.get_sections()` returns a [Python list] with the sections
defined using the [`sections`] initial block or the
[`nav.set_sections()`] method.

{% include side-by-side.html demo="sections-keywords-get-sections" %}

## <a name="DANav.set_sections"></a>nav.set_sections()

You can programmatically set the list of sections using
`nav.set_sections()`.  It takes one argument, the [Python list]
containing the sections defintion.  The list should have the same
structure as a sections definition using the [`sections`] initial
block (except it should be a [Python] data structure rather than
[YAML] text).  This method takes an optional keyword argument
`language` that you can specify if you want to define the section
names for a language other than the current language.

{% include side-by-side.html demo="sections-keywords-set-sections" %}

## <a name="DANav.show_sections"></a>nav.show_sections()

To display the section list to the user in the body of a question, you
can include the `nav` variable in a [Mako] template like so:
`${ nav }`.  This has the effect of doing
`${ nav.show_sections(style='inline') }`.  This method takes the optional
keyword arguments `style`, the options for which are `None` or
`'inline'`, and `show_links`, which you can set to `True` if you want
users to be able to click on section names.

## <a name="DANav.hide"></a>nav.hide()

If you want to hide the main navigation bar, run `nav.hide()`.  The
sections system will still work, and you can still insert `nav` into
the body of a question, but the main navigation bar will not be shown
on the screen.  The navigation bar is shown by default if sections are
defined.

## <a name="DANav.unhide"></a>nav.unhide()

Calling `nav.unhide()` will undo the effect of `nav.hide()`.

## <a name="DANav.visible"></a>nav.visible()

The result of `nav.visible()` will be `False` if the navigation bar
has been hidden with `nav.hide()`, and it will return `False` if no
sections have been defined.  `nav.visible()` takes an optional keyword
argument `language`, and when determining whether no sections have
been defined, it will look to that language.  If sections are defined
and the navigation bar has not been hidden with `nav.hide()`,
`nav.visible()` will return `True`.

# <a name="globalvars"></a>Functions for managing global variables

If you try writing your own functions, you will learn that functions
do not have access to all of the variables in your interview.
Functions only know the variables you pass to them.

If your functions need to know background information about the
interview, but you do not want to have to pass a lot of variables to
every function you call, you can use "global" variables.

You set "global" variables in **docassemble** by calling [`set_info()`]
and you retrieve them by calling [`get_info()`].  Note that
**docassemble** will forget the values of these variables every time
the screen loads, so you will have to make sure they are set by
setting them in [`initial`] code, which runs every time the screen
loads.

## <a name="set_info"></a>set_info()

This function is used to store information for later retrieval by
`get_info()`.  You pass it one or more [keyword arguments]:

{% highlight yaml %}
---
initial: True
code: |
  set_info(interview_type='standard')
---
{% endhighlight %}

Some of the [functions] and [methods] will behave differently
depending on who the interviewee is and what the interviewee's role
is.  For example, if `trustee` is an object of the class
[`Individual`], and you call `trustee.do_question('have')`, the result
will be "do you have" if if the interviewee is the trustee, but
otherwise the result will be "does Fred Jones have" (or whatever the
trustee's name is).

In order for **docassemble** to know this background information, you
need to include an [`initial`] code block (or a [`default role`] block
containing [`code`]) that:

1. Defines `user` as an object of the class [`Individual`];
2. Defines `role` as a text value (e.g., `'advocate'`); and
3. Calls `set_info(user=user, role=role)`.

For example, this is how [`basic-questions.yml`] does it:

{% highlight yaml %}
---
objects:
  - client: Individual
  - advocate: Individual
  # etc.
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

(See [initial blocks] for an explanation of [`objects`] and [`default
role`].  See the [roles] section for an explanation of how user roles
work in **docassemble**.)

## <a name="get_info"></a>get_info()

This function is used to retrieve information passed to
`set_info()`.

For example, if you passed `interview_type` as a [keyword argument] to
`set_info()`, you can retrieve the value in your [Python module] by
doing:

{% highlight python %}
from docassemble.base.util import *

class Recipe(DAObject):
    def difficulty_level(self):
        if get_info('interview_type') == 'standard':
            #etc.
{% endhighlight %}

If the item was never set, `get_info()` will return `None`.

## <a name="interface"></a>interface()

The `interface()` function returns `'web'` if the user is accessing
the interview through a web browser and `'sms'` if the user is using
[SMS].  If the web interface is used, but `&json=1` is added to the
URL, then `interface()` will return `'json'`.  If the API is being
used, `interface()` will return `'api'`.

{% include side-by-side.html demo="interface" %}

Sometimes interviews are accessed by [background processes].
`interface()` will return `'cron'` if the interview is being accessed
by a [scheduled task], and will return `'worker'` if it is being
accessed by a [background process].

You might want to use this function to provide special instructions to
users depending on the way they access the interview.  For example,
the following will show a special instruction screen to users who are
accessing the interview through [SMS].

{% highlight yaml %}
---
mandatory: True
code: |
  if interface() == 'sms':
    sms_instructions
---
question: |
  Instructions
subquestion: |
  To leave the interview, type exit.
field: sms_instructions
---
{% endhighlight %}

You can also use `interface()` to distinguish between actual user
requests and requests that originate from [background processes].

{% highlight yaml %}
---
code: |
  request_counter = 0
---
initial: True
code: |
  if interface() in ['sms', 'web']:
    request_counter += 1
---
{% endhighlight %}

## <a name="user_logged_in"></a>user_logged_in()

The `user_logged_in()` function returns `True` if the user is logged
in, and otherwise returns `False`.

You can use this function to ensure that the user is logged in before
the user can finish your interview:

{% include side-by-side.html demo="user-logged-in" %}

This function uses the [`url_of()`] function and the
[`interview_url()`] function.  The `next` parameter is set to a URL
for the session.  The URL returned by [`interview_url()`] takes the
user back to the original session.

## <a name="user_privileges"></a>user_privileges()

The `user_privileges()` function returns the user's [privileges] as a
list.  If the user is not logged in, the result is `['user']`.  If the
user is a "user" as well as a "customer," the result is
`['user', 'customer']`.  If the interview is running a
[scheduled task], the result is `['cron']`.

## <a name="user_has_privilege"></a>user_has_privilege()

The `user_has_privilege()` function returns `True` if the user has any
of the given [privileges], and `False` otherwise.  For example, if the
user has the [privilege] of "customer," `user_has_privilege('customer')`
will return `True`.  A list can also be provided, in which case `True`
will be returned if the user has any of the given [privileges].  For
example, if the user has the [privilege] of "developer",
`user_has_privilege(['developer', 'admin'])` will return `True`.

## <a name="user_info"></a>user_info()

The `user_info()` function will return an object with the following
attributes describing the current user:

* `first_name`
* `last_name`
* `email`
* `country` (will be an official [ISO 3166-1 alpha-2] country code like `US`)
* `subdivision_first` (e.g., state)
* `subdivision_second` (e.g., county)
* `subdivision_third` (e.g., municipality)
* `organization` (e.g., company or non-profit organization)
* `session` the session ID of the current interview session
* `filename` the filename of the current interview session
* `package` the package of the current filename
* `language` the user's language, if set (an [ISO-639-1] or
  [ISO-639-3] code)
* `timezone` the user's time zone, in a format like `America/New_York`

All of these attributes, with the exception of `session` and
`filename`, are set by the user on the [Profile page].  They can also
be set by the [`set_user_info()`] function.

For example:

{% highlight yaml %}
---
question: |
  Your e-mail address is ${ user_info().email }.  Is that
  the best way to reach you?
yesno: email_is_best
---
{% endhighlight %}

## <a name="set_save_status"></a>set_save_status()

The `set_save_status()` function is useful in `code` that replies to
[actions].  By default, running an [action] will create a new step in
the interview history (which the user can undo by clicking the Back
button).  However, sometimes this can be a source of confusion.  When
the user undoes something, the user will expect to see something
different; but if you are using [actions], undoing an [action] might
not change anything visibly on the screen.  You can use
`set_save_status()` to tell the interview to save the result of the
action, but not create a new step.  Or, if you want to run a "read
only" action that does not change the interview answers at all, you
can use `set_save_status()` for that.  This can be useful for
actions that return a JSON response.

The function takes one of three parameters:

* `set_save_status('new')` - the changes made during the processing of
  the interview logic are saved, and a new step is created in the
  interview history.  This is the default.
* `set_save_status('overwrite')` - the changes made during the
  processing of the interview logic are saved, but the
  current step is overwritten.
* `set_save_status('ignore')` - the changes made during the processing
  of the interview logic are not saved.

## <a name="set_parts"></a>set_parts()

The `set_parts()` function allows you to configure text on various
parts of the screen, which is displayed in the "My Interviews" list
and in the navigation bar.  It is also used to set certain
interview-level default values.

It accepts any of the following optional keyword arguments:

* `title` - this is the main title of the interview.  It should be
  plain text.  It is displayed in the navigation bar if there is no `logo`.
* `logo` - this can be used for raw HTML that you want to go into the
  navigation bar in place of the plain text title of the interview.
  If you include an image, you should size it to be about 20 pixels in
  height.
* `short` - for the mobile-friendly version of the interview title,
  which is displayed in the navigation bar when the screen is small.
* `short_title` does the same thing as `short`.
* `subtitle` - for the subtitle of the interview, which is displayed
  in the "Interviews" list.  The subtitle is not visible on the screen
  of the interview itself.
* `tab` - for the [HTML] title of the web page.  This is typically
  displayed in the browser tab.
* `tab_title` does the same thing as `tab`.
* `exit_link` - can be set to `'exit'` or `'leave'` in order to
  control the behavior of the "Exit" menu option, which is displayed
  when [`show login`] is `False`.  If set to `'exit'`, then clicking
  "Exit" will delete the user's answers.  If set to `'leave'`, the
  user's answers will not be deleted.  The default behavior is `'exit'`.
* `exit_label` - can be used to change the appearance of the "Exit"
  menu option.
* `pre` - can be set to HTML that will be inserted before
  the `question` part of a screen.
* `submit` - can be set to HTML that will be inserted before the
  buttons.
* `continue_button_label` - will change the text in the Continue
  button.
* `resume_button_label` - will change the text in the Resume
  button on [`review`] screens.
* `back button label` - will change the text of the back button that
  appears inside
* `help_label` - will change the default label of the help tab and the
  help button
* `under` - can be set to HTML that will be inserted after the buttons.
* `right` - can be set to HTML that will be inserted to the right of
  the question, or below the `under` content on small screens.
* `post` - can be set to HTML that will be inserted at the bottom of
  the screen, after the buttons.
* `date format` - this can be set to a default date format string used
  by the [`format_date()`] function and the [`.format_date()`] method
  of the [`DADateTime`] object (which is called when a [`DADateTime`]
  object is reduced to text).
* `datetime format` - this can be set to a default date/time format
  string used by the [`format_datetime()`] function and the
  [`.format_datetime()`] method of the [`DADateTime`] object.
* `time format` - this can be set to a default time format string used
  by the [`format_time()`] function and the [`.format_time()`]
  method of the [`DADateTime`] object.

In the following interview, note that the screen parts that were
initially set by [`metadata`] are overridden when `set_parts()` is
run.

{% include side-by-side.html demo="set-parts" %}

The following example shows how you can use a [`DAStaticFile`] to
display a logo from your "static" folder in the navigation bar.

{% include side-by-side.html demo="set-logo-title" %}

For information about other ways to set defaults for different parts
of the screens during interviews, see the [screen parts] section.

## <a name="session_tags"></a>session_tags()

Every interview and interview session can be "tagged" with "tags."  If
you include a `tags` specifier in your interview's [`metadata`], and
the `tags` specifier is a [list], then you will define the tags for
the interview itself.  These tags can be seen on the
[list of available interviews] that can be started (`/list`) and on
the list of saved interviews that can be resumed (`/interviews`).

The tags associated with an interview session can be edited using
[Python] code.  The function `session_tags()` returns a [Python set]
representing the tags.  It isn't technically a [Python set], but it
works just like one, and it allows you to read and write the
tags associated with the interview session.

{% include side-by-side.html demo="tags" %}

## <a name="set_status"></a>set_status()

The `set_status()` function allows you to configure global settings
for the interview session.  You give it keyword arguments for one or
more settings, and it will save the values for the session.

Currently, there is only one setting available, `variable_access`,
which turns off the [`get_interview_variables()`] feature on a
production server.  By default, the [`get_interview_variables()`]
function can be called from [JavaScript] and all of the variables in
the interview answers will be returned in [JSON] format.  While this
function is useful for many applications, it also poses a risk of
revealing confidential information, particularly in [multi-user
interviews] where users should not be able to find out other users'
answers.  Setting `variable_access` to `False` with `set_status()`
will disable this feature.

{% highlight yaml %}
mandatory: True
code: |
  set_status(variable_access=False)
{% endhighlight %}

However, if your server is a development server (the [`debug`]
directive in the [Configuration] is set to `True`), then this has no
effect.

## <a name="get_status"></a>get_status()

If you set a value using `set_status()`, you can retrieve the value
using `get_status()`.  For example:

{% highlight yaml %}
field: variable_access_shown
question: |
  % if get_status('variable_access') is False:
  The `get_interview_variables()` function is
  disabled.
  % else:
  The `get_interview_variables()` function is
  enabled.
  % endif
{% endhighlight %}

If a setting has not been set, the function returns `None`.

# <a name="browser"></a>Functions for determining information about the browser

## <a name="language_from_browser"></a>language_from_browser()

The `language_from_browser()` function returns a language code
representing the preferred language of the user.  Most browsers allow
users to select one or more preferred languages.  These languages are
transmitted to web sites using the [Accept-Language header].  The
`language_from_browser()` function reads this header and extracts the
language from it.

The code will be in [ISO-639-1], [ISO-639-2], or [ISO-639-3] format
and will be in lower case.  If multiple languages are listed in the
[Accept-Language header], the first recogized language will be
returned.

{% include side-by-side.html demo="language_from_browser" %}

That this function will return `None` if the [`interface()`] is `sms`,
if the [Accept-Language header] is missing, or if no valid
[ISO-639-1], [ISO-639-2], or [ISO-639-3] code can be found in the
[Accept-Language header].

Optionally, you can call `language_from_browser()` with arguments,
where the arguments are valid languages.  The first valid language
will be returned.  If none of the languages in the
[Accept-Language header] is in the list, `None` will be returned.

{% include side-by-side.html demo="language_from_browser_restricted" %}

## <a name="device"></a>device()

The `device()` function returns an object containing
information about the user's browser, derived from the [User-Agent header].

{% include side-by-side.html demo="device" %}

For more information about the properties of this object, see the
documentation for the [user-agents] library.

If **docassemble** cannot determine information about the user's
browser, this function will return `None`.

You can also use this function to obtain the user's IP address.  If
you call the function using `device(ip=True)`, the IP address is
returned:

{% include side-by-side.html demo="device-ip" %}

# <a name="langlocale"></a>Language and locale functions()

These functions access and change the active language and locale.  See
[language support] for more information about these features.

## <a name="get_language"></a>get_language()

If the language is set to English, `get_language()` returns `en`.

## <a name="set_language"></a>set_language()

This sets the language that will be used in the web application and in
[language-specific functions] of **docassemble**.  It does not change
the active [Python locale].  See `update_locale()` for information on
changing the [Python locale].

If you need to set the language to something other than the language
set in the [configuration], you need to call `set_language()` within
[`initial`] code.  For example:

{% highlight yaml %}
initial: True
code: |
  set_language(user_language)
---
question: |
  What language do you speak? (¿Qué idioma habla?)
field: user_language
choices:
  - English: en
  - Español: es
---
{% endhighlight %}

The value given to `set_language()` must be a lowercase [ISO-639-1] or
[ISO-639-3] code.  For example in [ISO-639-1], Spanish is `es`, French
is `fr`, and Arabic is `ar`.

Using the optional `dialect` keyword argument, you can also set the
dialect of the language.  The dialect is relevant only for the
text-to-speech engine.  For example:

{% highlight yaml %}
---
initial: True
code: |
  set_language('en', dialect='au')
---
{% endhighlight %}

This will set the language to English, and will instruct the
text-to-speech engine to use an Australian dialect.  (The dialect is
relevant only for the text-to-speech engine, which is controlled by
the [special variable `speak_text`].)

For more information about languages in **docassemble**, see
[language support].

If your interview uses [actions], and your [actions] need to know what
language to use, you will need to manually include
[`process_action()`] in an [`initial`] block, as follows:

{% highlight yaml %}
initial: True
code: |
  set_language(user_language)
  process_action()
{% endhighlight %}

By default, [`process_action()`] is called automatically, prior to the
execution of any [`mandatory`] or [`initial`] blocks.  However, in
cases where your [actions] have a prerequisite, you need to indicate
exactly where in the interview logic [actions] should be executed.

Note that in the above example, [actions] will not be able to be run
until `user_language` is defined, so if your interview uses [actions]
very early on in the interview, you may need to set a default value
for `user_language` before asking the user what `user_language` should
be.

## <a name="get_dialect"></a>get_dialect()

Returns the current dialect, as set by the `dialect` keyword argument
to the [`set_language()`] function.

## <a name="get_country"></a>get_country()

Returns the current country as a two-digit [ISO 3166-1 alpha-2]
country code.  The default country is `'US'`, unless a different
default is set using the [`country` configuration setting].

## <a name="set_country"></a>set_country()

Sets the current country.  Expects a two-digit, uppercase country code
([ISO 3166-1 alpha-2] format) such as `'US'`, `'GB'`, or `'DE'`.

## <a name="set_locale"></a>set_locale()

If you run `set_locale('FR.utf8')`, then [`get_locale()`] will return
`FR.utf8`.  The only effect is to remember the value; there are no
side effects.

The actual [Python locale] will not change unless you run
`update_locale()`, which will use the value you set with
`set_locale('FR.utf8')`.

The information you set with `set_locale()`, like the language you set
with [`set_language()`], is only remembered for the duration of a page
load.  Thus, you can use `set_locale()` and [`get_locale()`], without
[`update_locale()`], for your own purposes, as a way of passing a
locale identifier to custom functions and methods without having to
pass the locale identifier as an argument or setting an object
attribute.

A second use of `set_locale()` is to set a default currency symbol for
use in an interview session, if the default currency symbol associated
with the locale is not appropriate.  To indicate what currency symbol
should be used, you can call `set_locale()` with a `currency_symbol`
keyword parameter.  You need to call this in an [`initial`] block, in
much the same way as you use [`set_language()`] to indicate what
language to use.

{% highlight yaml %}
---
initial: True
code: |
  if user.address.country == 'US':
    set_locale(currency_symbol='$')
  else:
    set_locale(currency_symbol='€')
{% endhighlight %}

It is important that an [`initial`] code block is used, because the
code needs to run every time the screen loads.

If you want to undo the effect of `set_locale()` with a
`currency_symbol`, call `set_locale(currency_symbol=None)` and the
default behavior will be used instead.

Another way to change the currency symbol that users see is to set the
[`currency symbol` field specifier] on the [`datatype: currency`]
fields you use to collect currency values.  You can also provide a
`symbol` keyword parameter to the [`currency()`] function.

## <a name="get_locale"></a>get_locale()

If the locale is set to `US.utf8`, `get_locale()` returns `US.utf8`.

To obtain the currency symbol, call `get_locale('currency_symbol')`.
This will return `None` if there is no currency symbol set.

## <a name="update_locale"></a>update_locale()

Running `update_locale` will change the [Python locale] based on the
current language and locale settings.

For example, if you run:

{% highlight python %}
import docassemble.base.util
docassemble.base.util.set_language('fr')
docassemble.base.util.set_locale('FR.utf8')
docassemble.base.util.update_locale()
{% endhighlight %}

then the [Python locale] will be changed to `fr_FR.utf8`.

Running `update_locale()` is necessary in order to affect the behavior
of functions like [`currency()`] and [`currency_symbol()`].

Note that changes to the locale are not [thread-safe].  This means that
there is a risk that between the time **docassemble** runs
`update_locale()` and the time it runs [`currency_symbol()`], another
user on the same server may cause **docassemble** to run
`update_locale()` and change it to the wrong setting.

If you want to host different interviews that use different locale
settings on the same server (e.g., to format a numbers as 1,000,000 in
one interview, but 1.000.000 in another), you will need to make sure
you run the **docassemble** web server in a multi-process, single-thread
configuration.  (See [installation] for instructions on how to do
that.)  Then you would need to begin each interview with [`initial`]
code such as:

{% highlight yaml %}
---
initial: True
code: |
  import docassemble.base.util
  docassemble.base.util.set_language('fr')
  docassemble.base.util.set_locale('FR.utf8')
  docassemble.base.util.update_locale()
---
{% endhighlight %}

# <a name="time"></a>Access time functions

Internally, **docassemble** keeps track of the last time the interview
session was accessed.  The following functions retrieve information
about access times.  These functions are particularly useful in
[scheduled tasks].

## <a name="start_time"></a>start_time()

`start_time()` returns a [`DADateTime`] object representing the time
the interview session was started.

The time is expressed in the [UTC] time zone.  If you would
like to localize the time to a particular time zone, you can set the
optional keyword parameter `timezone` (e.g., to `'America/New_York'`).

## <a name="last_access_time"></a>last_access_time()

`last_access_time()` returns a [`DADateTime`] object containing the
last time the interview session was accessed by a user other than the
special [cron user].

The time is expressed in the [UTC] time zone.  (Note: before version
0.2.27, the object returned was a [UTC] datetime without a time zone;
as of 0.2.27, the object returned is [UTC] with a time zone).  If you
would like to localize the time to a particular time zone, you can set
the optional keyword parameter `timezone` (e.g., to
`'America/New_York'`).

Optionally, a [privilege] name or a list of [privilege] names can be provided.  In
this case, the function will return the latest access time by any user
holding one of the [privileges].

* `last_access_time('client')`: returns the last time a user with the
  privilege of `client` accessed the interview session.
* `last_access_time('advocate')`: returns the last time a user with
  the privilege of `advocate` accessed the interview session.
* `last_access_time(['advocate', 'admin'])`: returns the last time a
  user with the privilege of `advocate` or `admin` accessed the interview session.

The first argument can also be written as a keyword parameter
`include_privileges`:

* `last_access_time(include_privileges='client')`: same as `last_access_time('client')`.

By default, `last_access_time()` will ignore session access by the
[cron user].  However, if you do not wish to ignore access by the
[cron user], you can call `last_access_time()` with the optional
keyword argument `include_cron` equal to `True`:

* `last_access_time(include_cron=True)`: returns the last time any
  user, including the [cron user] if applicable, accessed the
  session.

You can also provide a list of [privileges] you want the method to ignore,
using the `exclude_privileges` keyword parameter.  This can be useful
because users can have multiple [privileges].

* `last_access_time(include_privileges='advocate',
  exclude_privileges=['developer'])`: returns the last time a user who is
  an `advocate` but not a `developer` accessed the interview.

The `last_access_time()` function takes an optional keyword argument
`timezone`.  If `timezone` is provided (e.g.,
`timezone='America/New_York'`), the [`DADateTime`] object will be
expressed in the given time zone.

## <a name="last_access_days"></a>last_access_days()

The function `last_access_days()` works just like
[`last_access_time()`], except that it returns the number of days
(including fractional days) between the current time and the last
access time.

## <a name="last_access_hours"></a>last_access_hours()

Like [`last_access_days()`], except returns hours.

## <a name="last_access_minutes"></a>last_access_minutes()

Like [`last_access_days()`], except returns minutes.

## <a name="last_access_delta"></a>last_access_delta()

The function `last_access_delta()` works just like
[`last_access_time()`], except that it returns a
[`datetime.timedelta`] object giving the difference between the
current time and the last access time.

## <a name="returning_user"></a>returning_user()

The function [`returning_user()`] returns `True` if the user has not
accessed the interview session in at least six hours, and otherwise
returns `False`.  To use a different time limit, you can set one of
the optional keyword arguments.

* `returning_user(minutes=5)`
* `returning_user(hours=1)`
* `returning_user(days=30)`

# <a name="date functions"></a>Functions for working with dates and times

## <a name="month_of"></a><a name="day_of"></a><a name="year_of"></a><a name="dow_of"></a>month_of(), day_of(), year_of(), and dow_of()

These functions read a date and provide the parts of the date.

{% include side-by-side.html demo="date-parts" %}

The `month_of()` and `dow_of()` functions have an optional setting: if
called with the optional parameter `as_word=True`, they will return the result as a
word (according to the current language and locale) rather than as a
number.

## <a name="format_date"></a>format_date()

The `format_date()` function takes as input a date and returns the
date formatted appropriately for the current language.  It can be
given a piece of text containing a time, a [`DADateTime`] object, a
[`datetime.datetime`] object, or a [`datetime.time`] object.

For example:

* `format_date(today())` returns the current date, formatted like `January 1, 2018`.
* `format_date("10/31/2016")` returns `October 31, 2016`.
* `format_date("2016-04-01")` returns `April 1, 2016`.
* `format_date('April 5, 2014')` returns `April 5, 2014`.
* `format_date('April 5, 2014', format='long')` returns `April 5, 2014`.
* `format_date('April 5, 2014', format='full')` returns `Saturday, April 5, 2014`.
* `format_date('April 5, 2014', format='EEEE')` returns `Saturday`.
* `format_date('April 5, 2014', format='yyyy')` returns `2014`.
* `format_date('April 5, 2014', format='yy')` returns `14`.
* `format_date('April 5, 2014', format='MMMM')` returns `April`.
* `format_date('April 5, 2014', format='MMM')` returns `Apr`.
* `format_date('April 5, 2014', format='d')` returns `5`.
* `format_date('April 5, 2014', format='dd')` returns `05`.
* `format_date('April 5, 2014', format='E')` returns `Sat`.
* `format_date('April 5, 2014', format='e')` returns `6` (numbers
  range from 1 to 7).
* `format_date('April 5, 2014', format='EEEE, MMMM d, yyyy')` returns
  `Saturday, April 5, 2014`.
* `format_date('April 5, 2014', format='short')` returns `4/5/14`.
* `format_date('April 5, 2014', format='M/d/yyyy')` returns `4/5/2014`.
* `format_date('April 5, 2014', format='MM/dd/yyyy')` returns
  `04/05/2014`.
* `format_date('April 5, 2014', format='yyyy-MM-dd')` returns
  `2014-04-05`.

The date formatting is provided by the
[babel.dates](http://babel.pocoo.org/en/latest/api/dates.html#date-fields)
package, which has good support for language and locale variation.
The `format` argument, is passed directly to the
`babel.dates.format_date()` function.

The
[patterns](http://babel.pocoo.org/en/latest/dates.html#date-fields)
used in date formatting by `babel.dates.format_date()` are based on
[Unicode Technical Standard #35].

If you do not provide a `format` argument, the default `date format`
will be used.  This default can be set in the interview [`metadata`]
or overridden using [`set_parts()`].  If no default is set, `'long'`
is used.

The date formatting will be different depending on the current
language.  For example, if you run `set_language('es')`, then
`format_date('4/5/2014')` returns `5 de abril de 2014`.  If you run
`set_language('fr')`, then `format_date('4/5/2014')` returns `5 avril
2014`.

## <a name="format_time"></a>format_time()

The `format_time()` function works just like [`format_date()`], except
it returns a time, rather than a date.  It can be given a piece of
text containing a time, a [`DADateTime`] object, a
[`datetime.datetime`] object, or a [`datetime.time`] object.

For example:

* `format_time(current_datetime())` returns the current time,
  formatted like `12:00 AM`.
* `format_time("04:01:23")` returns `4:00 AM`.
* `format_time("04:01:23", format='h')` returns `4`.
* `format_time("04:01:23", format='hh')` returns `04`.
* `format_time("04:01:23", format='m')` returns `1`.
* `format_time("04:01:23", format='mm')` returns `01`.
* `format_time("04:01:23", format='ss')` returns `23`.
* `format_time("04:01:23", format='a')` returns `AM`.
* `format_time("04:01:23", format='z')` returns `EST`, or whatever the
  current time zone is.
* `format_time("04:01:23", format='zzzz')` returns `Eastern Standard
  time`, or whatever the current time zone is.
* `format_time("04:01:23", format='h:mm a')` returns `4:01 AM`.

The time formatting is provided by the
[babel.dates](http://babel.pocoo.org/en/latest/api/dates.html#time-fields)
package.

The `format` argument is passed directly
to the `babel.dates.format_time()` function.  The
[patterns](http://babel.pocoo.org/en/latest/dates.html#time-fields)
used in time formatting are based on [Unicode Technical Standard #35].

If you do not provide a `format` argument, the default `time format`
will be used.  This default can be set in the interview [`metadata`]
or overridden using [`set_parts()`].  If no default is set, `'short'`
is used.

## <a name="format_datetime"></a>format_datetime()

The `format_datetime()` function works like a combination of
[`format_date()`] and [`format_time()`].  It is different only in that
it allows date and time to be joined in the same output.

* `format_datetime('4/5/2014 07:30')` returns `April 5, 2014 at
  07:30:00 AM EST`.
* `format_datetime('4/5/2014 07:30', 'h:mm in MMMM')` returns `'7:30 in
  April'`.

If you do not provide a `format` argument, the default `datetime
format` will be used.  This default can be set in the interview
[`metadata`] or overridden using [`set_parts()`].  If no default is
set, `'long'` is used.

## <a name="today"></a>today()

{% include side-by-side.html demo="today" %}

Returns a [`DADateTime`] object representing today's date at midnight.
It takes an optional keyword argument `timezone`, which refers to one
of the time zone names in [`timezone_list()`] (e.g.,
`'America/New_York'`).  If the `timezone` is not supplied, the default
time zone will be used.

Since the result is a [`DADateTime`] object, if `today()` is included
in a [Mako] template, the result will be equivalent to calling
[`format_date()`] on the object.

So this:

{% highlight text %}
Today's date is ${ today() }.
{% endhighlight %}

becomes, for example:

> Today's date is August 1, 2018.

The fact that the object is a [`DADateTime`] object means you can use
methods on it.  For example, you can write things like `Your term
paper is due in a week, so make sure you give it to me by ${
today().plus(weeks=1) }!`

The `today()` function also takes an optional keyword parameter
`format`.  If a `format` is provided, then `today()` returns text, not
an object.  So this:

{% highlight text %}
Today's date is ${ today(format='M/d/YYYY') }.
{% endhighlight %}

becomes, for example:

> Today's date is 8/1/2018.

## <a name="timezone_list"></a>timezone_list()

{% include side-by-side.html demo="timezone-list" %}

The `timezone_list()` function returns a list of time zones that the
other date-related functions in **docassemble** understand.  The list
is generated from the [`pytz`] module.  The primary purpose of this
function is to include in a multiple choice question.

Note that the items in this list are strings, like `America/New_York`.

## <a name="get_default_timezone"></a>get_default_timezone()

{% include side-by-side.html demo="get-default-timezone" %}

The `get_default_timezone()` function returns the default timezone
(e.g., `'America/New_York'`).  This is the time zone of the server,
unless the default timezone is set using the [`timezone`
configuration].

## <a name="as_datetime"></a>as_datetime()

{% include side-by-side.html demo="as-datetime" %}

The `as_datetime()` function expresses a date as a [`DADateTime`]
object with a time zone.  It takes an optional keyword argument,
`timezone`, which will override the default time zone.

* `as_datetime('12/25/2018')` returns midnight on Christmas.
* `as_datetime('12/25/2018 07:30 AM')` returns 7:30 a.m. on Christmas.
* `as_datetime('07:30 AM')` returns 7:30 a.m. on the current day.
* `as_datetime('07:30 AM', timezone='America/New_York')` returns 7:30
  a.m. on the east coast.

In combination with the [`.time()`] method of [`DADateTime`], this
function can be used to create objects of type [`datetime.time`].

* `as_datetime('07:30 AM').time()` returns a [`datetime.time`] object
  representing 7:30 a.m.

## <a name="current_datetime"></a>current_datetime()

{% include side-by-side.html demo="current-datetime" %}

The `current_datetime()` function returns the current date and time as
a [`DADateTime`] object.  It takes an optional keyword argument,
`timezone` (e.g., `'America/New_York'`), which will override the
default time zone.

## <a name="date_difference"></a>date_difference()

{% include side-by-side.html demo="date-difference" %}

The `date_difference()` function returns the difference between two
dates as an object with attributes that express the difference using
different units.  The function takes two keyword arguments: `starting`
and `ending`.  If either is omitted, the `current_datetime()` is used
in its place.

If you do `date_difference(starting=a, ending=b)`, then if date `a` comes
before date `b`, the resulting values will be positive.  But if date
`b` comes before date `a`, the values will be negative.

For example, if you set `z = date_difference(starting='1/1/2015',
ending='1/3/2015')`, then:

* `z.years` returns `0.005475814013977016`.
* `z.weeks` returns `0.2857142857142857`.
* `z.days` returns `2.0`.
* `z.hours` returns `48.0`.
* `z.minutes` returns `2880.0`.
* `z.seconds` returns `172800`.
* `z.delta` returns a [`datetime.timedelta`] object representing the
  difference between the times.

Dates without time zones are localized into the default time zone
before the calculation takes place.  You can supply the optional
keyword argument `timezone` (e.g., `'America/New_York'`) to use a
different time zone.

The object returned by `date_difference()` has a method
`.describe()`.  If you set
`z = date_difference(starting='1/1/2014', ending='4/3/2015')`, then:

* `z.describe()` returns `one year, three months, and one day`.
* `z.describe(capitalize=True)` returns `One year, three months, and one day`.
* `z.describe(specificity='year')` returns `one year`.
* `z.describe(specificity='month')` returns `one year and three months`.
* `z.describe(nice=False)` returns `1 year, 3 months, and 1 day`

If you reduce the resulting object to text, this has the effect of
running `.describe()` on the object.

## <a name="date_interval"></a>date_interval()

{% include side-by-side.html demo="date-interval" %}

The `date_interval()` function can be used to perform calculations on
a date.  For example,

* `current_datetime() + date_interval(days=1)` represents 24 hours in
  the future.
* `current_datetime() - date_interval(years=1)` represents one year in
  the past.

The available keyword arguments are:

* `years`
* `months`
* `days`
* `weeks`
* `hours`
* `minutes`
* `seconds`
* `microseconds`

This function is a direct wrapper around
[`dateutil.relativedelta.relativedelta`].

# <a name="phone"></a>Functions for working with phone numbers

The following functions help with mangaging phone numbers.  They rely
on the [`phonenumbers`] package in [Python].

## <a name="phone_number_in_e164"></a>phone_number_in_e164()

The `phone_number_in_e164()` function takes a phone number and formats
it into [E.164] format.  It takes an optional keyword argument
`country`, which is expected to be a country abbreviation ([ISO 3166-1
alpha-2] format, e.g., `'SE'` for Sweden).  (See the [`pycountry`
package] for the list of codes.)  The `country` code is used to
determine the country code for the phone number.  If `country` is not
provided, the [`get_country()`] function is used to determine the
applicable country.

## <a name="phone_number_formatted"></a>phone_number_formatted()

The `phone_number_formatted()` function is use to rewrite a number in
a standard phone number format according to national conventions.  It
works like `phone_number_in_e164()`, except that it returns the format
in the national format for the country, rather than [E.164].

## <a name="phone_number_is_valid"></a>phone_number_is_valid()

The `phone_number_is_valid()` function takes a phone number and
returns `True` or `False` depending on whether the phone number is
valid.  It takes an optional keyword argument `country` that is used
to determine the country whose phone number standards should be used
to determine the validity of the phone number.  The `country` must be
expressed in [ISO 3166-1 alpha-2] format.  If `country` is not
provided, the [`get_country()`] function is used to determine the
applicable country.

## <a name="phone_number_part"></a>phone_number_part()

The `phone_number_part()` function is use to extract individual parts
of a phone number.

* `phone_number_part("555-212-5623", 0)` returns `'555'`.
* `phone_number_part("555-212-5623", 1)` returns `'212'`.
* `phone_number_part("555-212-5623", 2)` returns `'5623'`.

The function takes an optional keyword argument `country`, a [ISO
3166-1 alpha-2] country code, that is used to format the phone number
according to the national conventions.  If `country` is not provided,
the [`get_country()`] function is used to determine the applicable
country.

# <a name="tasks"></a>Functions for tracking tasks

These are helpful functions for keeping track of whether certain tasks
have been performed.  For example, if your interview logic sends an
e-mail to the user about something, but you want to avoid sending the
e-mail more than once, you can give the "task" a name and use these
functions in your code to make sure your interview logic only sends
the e-mail if it has never been successfuly sent before.

Instead of using these functions, you could use your own variables to
keep track of whether tasks have been carried out or not.  These
functions do not do anything besides keep track of information.  A
good reason to use these functions is to increase the readability of
your code.

## <a name="task_performed"></a>task_performed():

The `task_performed()` function returns `True` if the task has been
performed at least once, otherwise `False`.

For example, `task_performed('application_for_assistance')` will
return `False` until
`mark_task_as_performed('application_for_assistance')` is called.

## <a name="task_not_yet_performed"></a>task_not_yet_performed():

The `task_not_yet_performed()` function returns `True` if the task has
never been performed, otherwise `False`.  It is simply the opposite of
[`task_performed()`].

## <a name="mark_task_as_performed"></a>mark_task_as_performed():

The `mark_task_as_performed()` function increases by 1 the number of
times the task has been performed.

For example, if `task_performed('send_reminder')` is `False`, and then
you call `mark_task_as_performed('remind_user')`, then
`task_performed('send_reminder')` will now return `True`, and
`times_task_performed('remind_user')` will return `1`.

If you call `mark_task_as_performed('remind_user')` again,
`task_performed('send_reminder')` will still return `True`, and
`times_task_performed('remind_user`) will now return `2`.

## <a name="times_task_performed"></a>times_task_performed():

The `times_task_performed()` function returns the number of times the
task has been performed (i.e., the number of times
[`mark_task_as_performed()`] is called).  If the task has never been
performed, `0` is returned.

## <a name="set_task_counter"></a>set_task_counter():

The `set_task_counter()` function allows you to manually set the
number of times the task has been performed.
`set_task_counter('remind_user', 0)` sets the counter of the
`remind_user` task to zero, which means that
`task_performed('remind_user')` would subsequently return `False`.

## <a name="persistent tasks"></a>Persistent task results

The above functions for tracking "tasks" store data in the interview
answers.  When the user presses the "Back" button to undo the results
of answering questions, the record of a task being completed will also
be undone.  Thus, if the user goes back and changes a variable on
which the task depends, the task will be re-run.  If you do not want a
task to be re-run, you can set the optional keyword parameter
`persistent` on your functions.

The example below demonstrates how this works; after the user answers
the `favorite_fruit` question, the task is marked as completed, but if
the user clicks the "Back" button, the fact that the the task was
completed will "persist."  Without `persistent=True`, the memory of
the task completion would be forgotten along with the value of
`favorite_fruit`.

{% include side-by-side.html demo="persistent-task" %}

When `persistent` is true, the task functions use a `DAStore` instead
of the interview answers to store information about whether tasks have
been completed.  Specifically, the functions use a `DAStore` with a
`base` of `'session'` within that `DAStore`, they use a value called
`tasks`.  If you set `persistent` to something other than `True`, the
`DAStore` will use this value as the `base`.  Thus, if you call
`mark_task_as_performed('fruit_gathered', persistent='interview')`,
then the result of task completion will apply across all sessions in
the same interview.  If you set `persistent` to `'user'`, the results
will apply across all sessions of the user.  If you set `persistent`
to `'global'`, the results will apply across all sessions of the
server.

# <a name="explaining"></a>Tracking reasoning

It may be important that the logic of your interview be explainable.
There are many ways to write your interviews in such a way you can
explain to the user the reasoning you are applying, and there is no
one right way to do this; nor is there a way that this process can be
feasibly automated.

The functions in this subsection may be of use for explaining
reasoning.  They allow you to write "comment"-like phrases in your
code that are saved into a list as the user goes through the
interview.  Then you can present the user with the list of phrases.

Here is an illustrative example:

{% include demo-side-by-side.html demo="explain" %}

The contents of the referenced module, [`somefuncs.py`], are:

{% highlight python %}
from docassemble.base.util import explain

__all__ = ['wrong_vegetable']

def wrong_vegetable(vegetable):
    if vegetable == 'turnip':
        explain("You also said your favorite vegetable was turnip.")
        return True
    else:
        explain("You also said your favorite vegetable was " + vegetable + ".")
        return False
{% endhighlight %}

Note that even though the call to `explain` takes place in a module,
and even though it references no variables in your interview answers,
the phrase is tracked in the list of explanations.

## <a name="explain"></a>explain()

The `explain()` function stores a phrase in the list of explanations.
If the same phrase, verbatim, already exists in the list, the phrase
is not added.

The `explain()` function takes an optional keyword argument,
`category`.  This allows you to keep track of more than one list of
explanations.  By default, the `category` is `'default'`.  The two
category names that are reserved are `'default'` and `'all'`.

## <a name="clear_explanations"></a>clear_explanations()

The `clear_explanations()` function resets the explanation list.  It
takes an optional keyword argument `category`, which resets the given
list.  If you set `category` to `'all'`, every list is reset.

It is a good idea to call `clear_explanations()` every time the screen
loads.  If your users can edit their answers, then reasoning that has
been made obsolete by changes to the variables may persist in the
explanations list.  Clearing the history and running through all of
the logic every time the screen loads will help make sure that the
explanations are corrected.

## <a name="explanation"></a>explanation()

The `explanation()` function returns the explanation list as a [Python
list].  If the list does not exist, an empty list is returned.  This
function takes an optional keyword argument `category`, which
indicates the category of explanation list you would like to be
returned.

# <a name="translation"></a>Simple translation of words

## <a name="word"></a>word()

`word()` is a general-purpose translation function that is used in the
code of the web application to ensure that the text the user sees is
translated into the user's language.  It is also available for use
inside interviews.  It is not the only mechanism for [translating]
your interviews into different languages, but it is one of the
essential components of [language support] in **docassemble**.

Suppose the following [`words`] directive appears in the
[Configuration].

{% highlight yaml %}
words:
  - docassemble.missouri:data/sources/words.yml
{% endhighlight %}

Suppose that the `words.yml` file contains the following:

{% highlight yaml %}
es:
  "fish": "pez"
  "cow": "vaca"
{% endhighlight %}

Suppose further that your interview has an
[`initial`]<span></span>[`code`] block that sets the language to
`'en'` or `'es'`:

{% highlight yaml %}
initial: True
code: |
  set_language(user_language)
---
question: |
  Please select your language.
field: user_language
choices:
  - English: en
  - Español: es
{% endhighlight %}

Finally, suppose that the user selected "Español" as their language.

Thereafter, if code in your interview runs `word("fish")`, the
returned value will be `'vaca'`.  However, if the user had selected
"English" as their language, the returned value would have been
`'fish'`.

When you call `word("fish")`, the `word()` function looks through all
the data in the [YAML] files listed under `words` and checks to see if
there is an entry for the phrase `fish` under the current language
(which is controlled by [`set_language()`] and [`get_language()`]).
If, among the key/value pairs listed under the language in question,
there is a key matching the word `'fish'`, the corresponding value is
returned.

<a name="update_word_collection"></a>In addition to using the
[`words`] directive in the [Configuration], you can a [Python module]
to change the translations.  The function
`docassemble.base.util.update_word_collection()` takes a language and
a [Python dictionary] as parameters and updates the translation
tables, which are kept in memory.

{% highlight python %}
import docassemble.base.util
definitions = {'Continue': 'Continuar', 'Help': 'Ayuda'}
docassemble.base.util.update_word_collection('es', definitions)
{% endhighlight %}

Since this function is not thread-safe, you should only run it from
code that runs when the module loads.

# <a name="linguistic"></a>Language-specific functions

These functions behave differently according to the language and
locale.  You can write functions for different languages, or reprogram
the default functions, by
using `import docassemble.base.util` and
then running
`docassemble.base.util.update_language_function()`.

For example, suppose you had a Spanish linguistic package that you
wanted to use for writing possessives.  You could include the
following in a [Python module] that you include in your interview:

{% highlight python %}
import docassemble.base.util
from special.spanish.package import spanish_possessify

def possessify_es(a, b, **kwargs):
    return spanish_possessify(a, b)

docassemble.base.util.update_language_function('es', 'possessify', possessify_es)
{% endhighlight %}

This means that whenever the current language is Spanish, the function
`possessify_es` should be substituted for the default function.  The
first argument is the name of the language, the second argument is the
name of the standard language function, and the third argument is a
reference to your function.

If you want to override the default function, use `'*'` as the
language.  This will be used if no language-specific function exists.

If you want to create a new language function that does not already
exist in **docassemble**, you can use the
`language_function_constructor()` function from
`docassemble.base.util`.

{% highlight python %}
import docassemble.base.util

__all__ = ['closing']

closing = docassemble.base.util.language_function_constructor('closing')

def closing_default(indiv, **kwargs):
    return "Goodbye, " + indiv.name.first + "!"

def closing_fr(indiv, **kwargs):
    return "Au revoir, " + indiv.name.first + "."

docassemble.base.util.update_language_function('*', 'closing', closing_default)
docassemble.base.util.update_language_function('fr', 'closing', closing_fr)
{% endhighlight %}

When writing a language function, do not use named keyword parameters.
Instead, using `**kwargs` so that the function accepts any combination
of keyword parameters.  This is necessary because language functions
can be called with an optional parameter `language`, which forces the
use of a language other than the default language.  It is also helpful
so that other developers can extend your language function.  For
example, suppose someone wants to add a Japanese version of
`closing()`, but in Japanese there are formal and informal ways of
saying goodbye.  In interviews, the developer will want to write
things like `closing(client, formal=False)` or `closing(judge,
formal=True)` to use these different forms.  The developer would
create a module that imports your module.  Then they would write a
function called `closing_ja` and call
`docassemble.base.util.update_language_function('ja', 'closing',
closing_ja)`.  Unless `**kwargs` is used, the keyword parameter
`formal` would trigger an error when used outside of a Japanese context.

Note that updates to language functions are not [thread-safe]; they
have a server-wide effect.  The best practice for calling
`update_language_function()` is to call it in main body of a module.
The code will be run once, when the server starts.

Listed below are some of the existing language functions that can be customized.

## <a name="capitalize"></a>capitalize()

{% include side-by-side.html demo="capitalize" %}

If `favorite_food` is defined as "spaghetti marinara," then
`capitalize(favorite_food)` will return `Spaghetti marinara`.
This is often used when a variable value begins a sentence.  For example:

{% highlight yaml %}
question: |
  ${ capitalize(favorite_food) } is being served for dinner.  Will you
  eat it?
yesno: user_will_eat_dinner
{% endhighlight %}

There is also the [`title_case()`] function, which is described below.

## <a name="comma_and_list"></a>comma_and_list()

If `things` is a [Python list] with the elements
`['lions', 'tigers', 'bears']`, then:

* `comma_and_list(things)` returns `lions, tigers, and bears`.
* `comma_and_list(things, oxford=False)` returns `lions, tigers and
  bears`.
* `comma_and_list('fish', 'toads', 'frogs')` returns `fish, toads, and
  frogs`.
* `comma_and_list('fish', 'toads')` returns `fish and toads`
* `comma_and_list('fish')` returns `fish`.
* `comma_and_list('fish', 'toads', 'frogs', and_string='or')` returns
  `fish, toads, or frogs`.
* `comma_and_list('fish', 'toads', 'frogs', comma_string='; ')`
  returns `fish; toads; and frogs`.
* `comma_and_list('fish', 'toads', 'frogs', before_and='---')` returns
  `fish; toads;---and frogs`.
* `comma_and_list('fish', 'toads', 'frogs', after_and=' (last but not
  least) ')` returns `fish, toads, and (last but not least) frogs`.

## <a name="comma_list"></a>comma_list()

If `things` is a [Python list] with the elements
`['lions', 'tigers', 'bears']`, then:

* `comma_list(things)` returns `lions, tigers, bears`.
* `comma_list(things, comma_string='; ')` returns `lions; tigers; bears`.
* `comma_list('fish', 'toads', 'frogs')` returns `fish, toads, and
  frogs`.
* `comma_list('fish')` returns `fish`.

## <a name="add_separators"></a>add_separators()

The `add_separators()` functions takes a list as input and returns a
list in which each item is reduced to text, a period is appended to
the last item, `; and` is appended to the penultimate item, and `;` is
appended to all other items.

{% include side-by-side.html demo="add-separators" %}

`add_separators()` takes three optional keyword parameters:

* `separator`: default is `';'`
* `last_separator`: default is `'; and'`
* `end_mark`: default is `'.'`

The function is also available as a [Jinja2] filter called
`add_separators`.  In the above example, the [`add-separators.docx`]
file contains:

> You like:<br>
> {% raw %}{%p for item in fruit | add_separators %}{% endraw %}<br>
>     1. {% raw %}{{ item }}{% endraw %}<br>
> {% raw %}{%p endfor %}{% endraw %}

## <a name="currency"></a>currency()

If the locale is `US.utf8`, `currency(45.2)` returns `$45.20`.

{% include side-by-side.html demo="currency" %}

`currency(45)` returns `$45.00`, but `currency(45, decimals=False)`
returns `$45`.

With `decimals` unset or equal to `True`, this function uses the
[`locale`] module to express the currency.  However, `currency(x,
decimals=False)` will simply return [`currency_symbol()`] followed by
`x` formatted as an integer, which might not be correct in your
locale.  This is due to a limitation in the [locale module].  If the
`currency` function does not meet your currency formatting needs, you
may want to define your own.

If you defined a currency symbol in an [`initial`] block by calling
[`set_locale()`] with a `currency_symbol` keyword parameter, then the
locale-specific currency formatting function is not used.

The `currency()` function accepts an optional keyword parameter
`symbol`.  If this is set, then the [`locale`]-specific currency formatter
function is not used, and instead the provided symbol is used,
followed by the number.

{% include side-by-side.html demo="money-field-euro" %}

## <a name="currency_symbol"></a>currency_symbol()

If the locale is `US.utf8`, `currency_symbol()` returns `$`.

The locale can be set in the [configuration] or through the
[`set_locale()`] function.

If you set [`currency symbol`] in the [configuration], then
`currency_symbol()` returns the symbol specified there, and does not
use the locale to determine the symbol.

## <a name="indefinite_article"></a>indefinite_article()

{% include side-by-side.html demo="indefinite-article" %}

The English language version of this function uses the `article()`
function of [pattern.en].

`indefinite_article('bean')` returns `a bean` and
`indefinite_article('apple')` returns `an apple`.

## <a name="nice_number"></a>nice_number()

{% include side-by-side.html demo="nice-number" %}

* `nice_number(4)` returns `four`
* `nice_number(10)` returns `ten`
* `nice_number(11)` returns `11`
* `nice_number(-1)` returns `-1`
* `nice_number(5.0)` returns `five`
* `nice_number(5.1)` returns `5.1`
* `nice_number(23423)` returns `23,423` (this depends on the [locale])
* `nice_number(12873818.27774)` returns `12,873,818.28` (this depends on the [locale])

This function can be customized by calling
`docassemble.base.util.update_nice_numbers()` with a [language] as the
first parameter and a [dictionary] as the second parameter, where the
dictionary maps numbers to their textual representation. Since this
function is not thread-safe, you should only run it from a [Python
module] in code that runs when the module loads.

## <a name="noun_plural"></a>noun_plural()

{% include side-by-side.html demo="noun-plural" %}

The English language version of this function passes all arguments
through to the `pluralize()` function of [pattern.en].

* `noun_plural('friend')` returns `friends`
* `noun_plural('fish')` returns `fish`
* `noun_plural('moose')` returns `mooses`

You can also pass a number as a second argument to the function.  If
the number is 1, the first argument will be returned as a singular noun;
otherwise, the pluralized version of the first argument will be returned.

* `noun_plural('friend', number_friends)` returns `friend` if
  `number_friends` is `1`, otherwise it returns `friends`.

## <a name="quantity_noun"></a>quantity_noun()

{% include side-by-side.html demo="quantity-noun" %}

This function combines [`nice_number()`] and [`noun_plural()`] into a
single function.  It will round the number to the nearest integer unless
you add the optional keyword argument `as_integer=False`.

* `quantity_noun(2, "apple")` returns `two apples`.
* `quantity_noun(1, "apple")` returns `one apple`.
* `quantity_noun(144, "apple")` returns `144 apples`.
* `quantity_noun(1.5, "apple")` returns `2 apples`.
* `quantity_noun(1.5, "apple", as_integer=False)` returns `1.5 apples`.

## <a name="noun_singular"></a>noun_singular()

The English language version of this function passes all arguments
through to the `singularize()` function of [pattern.en].

* `noun_singular('friends')` returns `friend`
* `noun_singular('fishes')` returns `fish`
* `noun_singular('mooses')` returns `moose`

You can also pass a number as a second argument to the function.  If
the number is 1, the singularized version of the first argument will
be returned.  Otherwise, the first argument will be returned,
untouched.

* `noun_singular('friends', number_friends)` return `friend` if
  `number_friends` is `1`, otherwise it returns `friends`.

## <a name="ordinal_number"></a>ordinal_number()

* `ordinal_number(8)` returns `eighth`.
* `ordinal_number(8, capitalize=True)` returns `Eighth`.
* `ordinal_number(11)` returns `11th`.
* `ordinal_number(8, use_word=False)` returns `8th`.

{% include side-by-side.html demo="ordinal-number" %}

This function can be customized with
`docassemble.base.util.update_ordinal_numbers()` and
`docassemble.base.util.update_ordinal_function()`.

{% highlight python %}
import docassemble.base.util

es_ordinal_nums = {
  '0': 'zeroth',
  '1': 'primero',
  '2': 'segundo',
  '3': 'tercero',
  '4': 'cuarto',
  '5': 'quinto',
  '6': 'sexto',
  '7': 'séptimo',
  '8': 'octavo',
  '9': 'noveno',
  '10': 'décimo'
}

docassemble.base.util.update_ordinal_numbers('es', es_ordinal_nums)
docassemble.base.util.update_ordinal_function()
{% endhighlight %}

Since these functions are not thread-safe, you should only run them
from a [Python module] in code that runs when the module loads.

## <a name="ordinal"></a>ordinal()

`ordinal(x)` returns `ordinal_number(x + 1)`.  This is useful when
working with indexes that start at zero.

## <a name="alpha"></a>alpha()

`alpha(x)` returns `x + 1` as an alphabetical character.  This is
intended to be used with indexes that start at zero.

* `alpha(0)` returns `A`.
* `alpha(25)` returns `Z`.
* `alpha(26)` returns `AA`.
* `alpha(26)` returns `AB`.
* `alpha(0, case='lower')` returns `a`.

## <a name="roman"></a>roman()

`roman(x)` returns `x + 1` as a Roman numeral.  This is intended to be
used with indexes that start at zero.

* `roman(0)` returns `I`.
* `roman(65)` returns `LXVI`.
* `roman(65, case='lower')` returns `lxvi`.

## <a name="item_label"></a>item_label()

`item_label(x)` returns `x + 1` as a label for a list item.  This is
intended to be used with indexes that start at zero.  It takes an
optional second argument indicating a level between 0 and 6.  It takes
an optional keyword argument `punctuation` indicating whether
punctuation should be provided or not.

* `item_label(0)` returns `I.`.
* `item_label(1)` returns `II.`.
* `item_label(0, 0)` returns `I.`.
* `item_label(0, 1)` returns `A.`.
* `item_label(0, 2)` returns `1.`.
* `item_label(0, 3)` returns `a)`.
* `item_label(0, 4)` returns `(1)`.
* `item_label(0, 5)` returns `(a)`.
* `item_label(0, 6)` returns `i)`.
* `item_label(0, 6, punctuation=False)` returns `i`.

## <a name="period_list"></a>period_list()

`period_list` returns a list within a list:

{% highlight python %}
[[12, "Per Month"], [1, "Per Year"], [52, "Per Week"],
[24, "Twice Per Month"], [26, "Every Two Weeks"]]
{% endhighlight %}

This is useful for using in `code` associated with periodic currency
amounts.

{% include side-by-side.html demo="income" %}

The text in the default `period_list()` function can be translated to
different languages using the
[`docassemble.base.util.update_word_collection()`] function.  If you
want to customizes the choices available, you can override the default
function by including something like the following in your
[Python module]:

{% highlight python %}
def my_period_list():
  return [[365, word("Per Day")], [52, word("Per Week")]]

docassemble.base.util.update_language_function('*', 'period_list', my_period_list)
{% endhighlight %}

## <a name="name_suffix"></a>name_suffix()

Like `period_list()`, except it represents common suffixes of
individual names.

Returns the following list:
{% highlight python %}
['Jr', 'Sr', 'II', 'III', 'IV', 'V', 'VI']
{% endhighlight %}

Here is a question that asks for the user's name with an optional
suffix:

{% highlight yaml %}
question: |
  What is your name?
fields:
  - First Name: user.name.first
  - Middle Name: user.name.middle
    required: False
  - Last Name: user.name.last
  - Suffix: user.name.suffix
    required: False
    code: |
      name_suffix()
---
{% endhighlight %}

## <a name="title_case"></a>title_case()

{% include side-by-side.html demo="title-case" %}

`title_case("the importance of being ernest")` returns `The Importance
of Being Ernest`.

The default version of this function passes through all arguments to
the `titlecase()` function of the [titlecase] module.

There is also the `capitalize()` function, which is described above.

## <a name="verb_past"></a>verb_past()

{% include side-by-side.html demo="past-tense" %}

The English-language version of this function passes all arguments
through to the `conjugate()` function of [pattern.en].

* `verb_past('help', '3gp')` returns `helped` (third person past tense).
* `verb_past('help', 'ppl')` returns `helped` (plural past tense).

## <a name="verb_present"></a>verb_present()

The English-language version of this function passes through all
arguments to the `conjugate()` function of the [pattern.en].

* `verb_present('helped', '3sg')` returns `helps` (third person singular).
* `verb_present('helps', '1sg')` returns `help` (first person singular).
* `verb_present('helps', 'pl')` returns `help` (plural).

# <a name="simplelang"></a>Simple language functions

The following simple language functions all have the property that if
the optional argument `capitalize=True` is added, the resulting phrase
will be capitalized.

* `her('turtle')` returns `her turtle`.
* `her('turtle', capitalize=True)` returns `Her turtle`.
* `his('turtle')` returns `his turtle`.
* `a_in_the_b('cat', 'hat')` returns `cat in the hat`.
* `do_you('smoke')` returns `do you smoke`.
* `does_a_b('Fred', 'smoke')` returns `does Fred smoke`.
* `in_the('house')` returns `in the house`.
* `of_the('world')` returns `of the world`.
* `possessify('Fred', 'cat')` returns `Fred's cat`.
* `possessify_long('Fred', 'cat')` returns `the cat of Fred`.
* `the('apple')` returns `the apple`.

Note that unlike other functions, these functions are *not* available
for use within interviews.

These functions are intended to be used from within [Python modules],
where you can import them by doing:

{% highlight python %}
from docassemble.base.util import his, her
{% endhighlight %}

Note that doing `from docassemble.base.util import *` will not work,
because these functions are not automatically exported by
[`docassemble.base.util`].

You can customize the functions for different languages:

{% highlight python %}
def her_fr(word, capitalize=False):
  if capitalize:
    return 'Sa ' + word
  else:
    return 'sa ' + word
docassemble.base.util.update_language_function('fr', 'her', her_fr)
{% endhighlight %}

Or, you can accomplish the same result with a handy function generator
from [`docassemble.base.util`]:

{% highlight python %}
docassemble.base.util.update_language_function('fr', 'her', docassemble.base.util.prefix_constructor('sa '))
{% endhighlight %}

# <a name="formfilling"></a>Helper functions for form filling

## <a name="yesno"></a>yesno()

The `yesno()` function returns `'Yes'` or `'No'` depending on the
truth value of the argument.  This is useful for filling in checkboxes
in [PDF templates].  It takes an optional keyword argument `invert`,
which, if set to true, returns `'No'` in place of `'Yes'` and
vice-versa.

## <a name="noyes"></a>noyes()

The `noyes()` function does the opposite of [`yesno()`], or the same
thing as `yesno(some_fact, invert=True)`.

## <a name="split"></a>split()

The `split()` function splits a phrase into parts that are a certain
number of characters long.  It splits on word breaks when it can.
This is useful for filling in [PDF templates] when a single phrase
must be typed into more than one field.

The first argument is the phrase.  The second argument is a list of
maximum character lengths of each part.  If there are two numbers,
there will be at most three parts.  The third argument is the index of
the part you want.  The first index is `0`.

In this example, the first part should be no more than 12 characters
and the second part should be no more than 20 characters.

* `split("The quick brown fox jumped over the lazy dog", [12, 20], 0)`
returns `'The quick'`.
* `split("The quick brown fox jumped over the lazy dog", [12, 20], 1)`
returns `'brown fox jumped over'`.
* `split("The quick brown fox jumped over the lazy dog", [12, 20], 2)`
returns `'the lazy dog'`.

If you only want to split in two parts, and you do not wish to limit
the length of the second part, you can pass a single number instead of
a list of numbers as the second argument.

* `split("The quick brown fox jumped over the lazy dog", 12, 0)`
returns `'The quick'`.
* `split("The quick brown fox jumped over the lazy dog", 12, 1)`
returns `'brown fox jumped over the lazy dog'`.

If you refer to an index for a part that does not exist because the
phrase was too short, empty text (`''`) is returned.

To figure out what character lengths you should use, one method is to
test the PDF file to see how many letter `M`s you can fit into a
field.  If you can fit 10 `M`s into the first field and 22 `M`s in
into the second field, the second argument to `split()` would be
`[10, 22]`.

## <a name="showif"></a>showif()

The `showif()` function returns the value of variable if the given
condition is true, and otherwise returns empty text (`''`).

* `showif('favorite_fruit', likes_fruit)` returns the value of the
  variable `favorite_fruit`, but only if the variable `likes_fruit` is
  true.

Note that the first argument must be a variable name in quotes.  This
ensures that a definition of the variable will not be sought unless
the condition is true.

If you want the function to return something other than the empty
string (`''`), supply a third argument:

* `showif('favorite_fruit', likes_fruit, 'no fruit')` returns the value of the
  variable `favorite_fruit` if the variable `likes_fruit` is true, and
  otherwise returns the text `no fruit`.

## <a name="showifdef"></a>showifdef()

The `showifdef()` function is like `showif()`, except that the value
of the variable is only returned if the variable is defined.

* `showifdef('favorite_fruit')` returns the value of the
  variable `favorite_fruit` if the variable `favorite_fruit` is
  defined, and otherwise returns empty text.
* `showifdef('favorite_fruit', 'no fruit')` returns the value of the
  variable `favorite_fruit` if the variable `favorite_fruit` is
  defined, and otherwise returns the text `no fruit`.

# <a name="admin"></a>Administrative functions

## <a name="interview_list"></a>interview_list()

If the current user is logged in, [`interview_list()`] returns a list
of dictionaries indicating information about the user's interview
sessions.  This function provides a programmatic version of the screen
available at `/interviews`.  In addition, the optional keyword
parameter `user_id` can be used (by a user with `admin` [privileges]) to
get information about sessions owned by other people.

The function returns a two-item tuple.  The first item in the tuple is
a [Python list] of [Python dictionaries], where the items in each
dictionary are:

* `dict`: the [interview session dictionary] for the session.
* `email`: the e-mail address of the logged-in user associated with the
  session, if any.
* `user_id`: the user ID of the logged-in user associated with the
  session, if any.
* `temp_user_id`: the temporary user ID of the anonymous user
  associated with the session, if the user was not logged
  in.  (Note that these IDs do not correspond in any way with the IDs
  of logged-in users.)
* `filename`: the filename of the interview, e.g.,
  `docassemble.demo:data/questions/questions.yml`
* `metadata`: the metadata of the interview as a dictionary.
* `modtime`: the modification time of the session, in text format,
  formatted to the user's time zone.
* `session`: the ID of the session.
* `starttime`: the start time of the session, in text
  format, formatted to the user's time zone.
* `title`: the [title](#get_title) of the session.
* `subtitle`: the [subtitle](#get_title) of the session.
* `utc_modtime`: the modification time of the session, in [UTC].
* `utc_starttime`: the start time of the session, in [UTC].
* `valid`: whether the interview session can be resumed.  This will be
  `False` if there is an error with the interview that prevents it
  from being resumed, or the [interview session dictionary] is not able
  to be decrypted.

The second item in the tuple is a code that is used for pagination.
Since the list of users may be very long, `interview_list()` uses
pagination.  When you first call `interview_list()`, up to 100 records
are returned in the first item in the tuple (configurable using the
[`pagination limit`] Configuration directive).  If additional records
exist, the second item in the tuple will be a code.  To obtain the
next page of records, call `interview_list()` again, this time with the
`next_id` optional keyword parameter set to the second item in the
tuple.  By making multiple calls to `interview_list()`, you can obtain
the complete list of user records.  For example:

{% highlight python %}
from docassemble.base.util import interview_list

sessions_list = []
next_id = None
while True:
    (items, next_id) = interview_list(next_id=next_id)
    sessions_list.extend(items)
    if not next_id:
        break
{% endhighlight %}

The following question will display a list of the titles of each
session associated with the current user (or the first 100):

{% highlight yaml %}
question: Sessions
subquestion: |
  % for info in interview_list()[0]:
  * ${ info['title'] }
  % endfor
{% endhighlight %}

To limit the results to sessions involving specific interviews, you
can provide the optional keyword argument `filename`:

{% highlight yaml %}
question: Session start times
subquestion: |
  % for info in interview_list(filename='docassemble.demo:data/questions/questions.yml')[0]:
  * ${ info['starttime'] }
  % endfor
{% endhighlight %}

If the current user has `admin` [privileges], the optional keyword
argument `user_id` can be used to retrieve a list of sessions
belonging to another user:

{% highlight yaml %}
question: Sessions John has started
subquestion: |
  % for info in interview_list(user_id=22)[0]:
  * ${ info['title'] }
  % endfor
{% endhighlight %}

Or, if you want to list sessions belonging to any user, you can set
`user_id` to `'all'`.

{% highlight yaml %}
question: Who has what session
subquestion: |
  % for info in interview_list(filename='docassemble.demo:data/questions/questions.yml', user_id='all')[0]:
  * ${ info['email'] } started at ${ info['starttime'] }.
  % endfor
{% endhighlight %}

Since the information about each session could include the interview
session dictionary, to avoid storing all of this information in your
own dictionary, it is a good idea to avoid keeping interview
information around when you are done using it.  For example, this
interview runs `del` to ensure that the variable `info` is not left
over when the for loop completes its work:

{% highlight yaml %}
code: |
  users = set()
  for info in interview_list()[0]:
    users.add(info['email'])
    del info
{% endhighlight %}

You can also refrain from obtaining the interview session dictionary
by setting the optional keyword parameter `include_dict` to `False`.

The [`interview_list()`] function takes an optional keyword argument
`exclude_invalid`.  If this is set to `False`, a session will be
included even if there is an error that would prevent the session from
being resumed.  By default, `exclude_invalid` is `True`, meaning that
sessions will only be included if they can be resumed.  You can check
whether a session can be resumed by checking the value of the `valid`
key.  The most common reason for a session not to be `valid` is that
the current user does not have an encryption key that decrypts the
interview answers; so a session belonging to someone else might be not
`valid` for you, but it would be `valid` for the user who started that
session.

The [`interview_list()`] function can be useful in interviews that
replace the standard list of sessions.  See the [`session list
interview`] configuration directive for more information.

Note that more than one user can be associated with any given session.
Unless server-side encryption prevents it, any user who has the
session ID of a session can join that interview by visiting a URL with
the `i` and `session` parameters set.  This will associate the user
with the session.  Thus, if a session has been joined by more than one
user, it will show up multiple times in the list returned by
`interview_list(user_id='all')`.

You can use [`interview_list()`] to delete sessions.  If you set the
optional keyword parameter `action` to `'delete_all'`, all of the
user's sessions will be deleted.  Or, if you want to delete all of the
sessions belonging to any user, you can set `user_id` to `'all'` and
set `action` to `'delete_all'`.  You can delete a particular session
by setting `action` to `'delete'`, with optional keyword parameter
`filename` set to the filename of the session's interview, and
optional keyword parameter `session` set to the ID of the session.  By
default, the underlying session data associated with a particular user
will not be deleted if it is shared by another user.  For example, if
there was an interview with [`multi_user`] set to `True`, and two
users accessed a session of this interview, and then one user deletes
the session, the other user will still be able to access the session
and all of its data.  However, if you set the optional keyword
parameter `delete_shared` to `True`, then the session and its data
will be deleted regardless of whether it is shared by one or more
other users.

For [API] versions of this function, see [`/api/interviews`],
[`/api/user/interviews`], and [`/api/user/<user_id>/interviews`].

## <a name="interview_menu"></a>interview_menu()

The `interview_menu()` function returns a list of dictionaries
indicating information about interviews available on the web site.
See the [`dispatch`] configuration directive for information about
setting up this menu.  This function provides a programmatic version
of the screen available at `/list`.

The keys in each dictionary are:

* `title`: the [title](#set_parts) of the interview
* `subtitle`: the [subtitle](#set_parts) of the interview
* `filename`: e.g., `docassemble.demo:data/questions/questions.yml`
* `link`: a hyperlink to the interview on your server
* `metadata`: a dictionary representing the metadata of the interview
  (minus the `tags`, which are provided separately).
* `package`: the package in which the interview is located, e.g., `docassemble.demo`
* `status_class`: this is set to `dainterviewhaserror` if there is a
  problem with the interview.
* `subtitle_class`: this is set to `invisible` if there is a problem
  with the interview.
* `tags`: a list of tags specified in the interview metadata.

The `interview_menu()` function takes three optional keyword arguments,
`absolute_urls`, `start_new`, and `tag`.

If `absolute_urls` is set to `True`, then the URLs will be absolute
rather than relative, so that the HTML can be used from a web site on
another server.

If `start_new` is set to `True`, then the URLs will have `&reset=1` at
the end.  Thus, even if the user has already started an interview,
clicking the link will start the interview at the beginning again.

If `tag` is set to `'estates'` (for example), then `interview_menu()`
will only return interviews that have `'estates'` defined as a `tag`
in the interview [`metadata`].

This function can be useful in interviews that replace the standard
list of available interviews.  See the [`dispatch interview`]
configuration directive for more information.

For an [API] version of this function, see [`/api/list`].

## <a name="create_user"></a>create_user()

The [`create_user()`] function creates a new user account on the
system.

{% highlight python %}
new_user_id = create_user('testuser@example.com', 'xxxsecretxxx')
{% endhighlight %}

This will create an account with the e-mail address `testuser@example.com`
and the password `xxxsecretxxx`.  The variable `new_user_id` will be
set to the user ID of the newly-created account.

Only users with [privileges] of `admin` can use this function.

The [`create_user()`] function also accepts an optional keyword
parameter `privileges`, which can be set to the name of a [privilege]
(e.g., `'advocate'`) or a list of [privileges] (e.g., `['advocate',
'trainer']`).

The function also accepts an optional keyword parameter `info`, which
is expected to be a dictionary containing information about the new
user.  The `info` dictionary can contain any of the following keys:

 - `country`: user's country code ([ISO 3166-1 alpha-2] format).
 - `first_name`: user's first name.
 - `language`: user's language code.
 - `last_name`: user's last name.
 - `organization`: user's organization
 - `subdivisionfirst`: user's state.
 - `subdivisionsecond`: user's county.
 - `subdivisionthird`: user's municipality.
 - `language` the user's language (an [ISO-639-1] or [ISO-639-3]
   code).
 - `timezone`: user's time zone (e.g. `'America/New_York'`).

To set this information after the user account is created, use
[`set_user_info()`].

For an [API] version of this function, see [`/api/user/new`].

## <a name="get_user_list"></a>get_user_list()

The [`get_user_list()`] function returns a list of registered users on
the server.  If the optional keyword parameter `include_inactive` is
set to `True`, then any inactive users are included in the results;
otherwise they are excluded.

The function returns a two-item tuple. The first item in the tuple is
a [Python list] of [Python dictionaries], where each dictionary has
the following keys:

 - `active`: whether the user is active.  This is only included if the
   `include_inactive` parameter is set.
 - `country`: user's country code ([ISO 3166-1 alpha-2] format).
 - `email`: user's e-mail address.
 - `first_name`: user's first name.
 - `id`: the integer ID of the user.
 - `language`: user's language code.
 - `last_name`: user's last name.
 - `organization`: user's organization
 - `privileges`: a [Python list] of the user's [privileges] (e.g., `'admin'`,
   `'developer'`).
 - `subdivisionfirst`: user's state.
 - `subdivisionsecond`: user's county.
 - `subdivisionthird`: user's municipality.
 - `language` the user's language (an [ISO-639-1] or [ISO-639-3]
   code).
 - `timezone`: user's time zone (e.g. `'America/New_York'`).

The second item in the tuple is a code that is used for pagination.
Since the list of users may be very long, `get_user_list()` uses
pagination.  When you first call `get_user_list()`, up to 100 records
are returned in the first item in the tuple (configurable using the
[`pagination limit`] Configuration directive).  If additional records
exist, the second item in the tuple will be a code.  To obtain the
next page of records, call `get_user_list()` again, this time with the
`next_id` optional keyword parameter set to the second item in the
tuple.  By making multiple calls to `get_user_list()`, you can obtain
the complete list of user records.  For example:

{% highlight python %}
from docassemble.base.util import get_user_list

user_list = []
next_id = None
while True:
    (items, next_id) = get_user_list(next_id=next_id)
    user_list.extend(items)
    if not next_id:
        break
{% endhighlight %}

For an [API] version of this function, see [`/api/user_list`].

## <a name="get_user_info"></a>get_user_info()

The [`get_user_info()`] function is like [`get_user_list()`], except
it only returns information about one user at a time.  If called
without arguments, it returns a [Python dictionary] of information
about the current user.  The function can also take a user ID as an
argument (e.g., `get_user_info(user_id=22)`), or an e-mail address as
an argument (e.g., `get_user_info(email='jsmith@example.com')`, in
which case it returns information about the user with that user ID or
e-mail address.  If no user is found, `None` is returned.

Only users with `admin` [privileges] can see information about other
users.

This function will only work if the user running the interview that
calls the function is logged in.

For [API] versions of this function, see [`/api/user`] and
[`/api/user/<user_id>`].  (Searching by e-mail address is not
supported in the [API].)

## <a name="set_user_info"></a>set_user_info()

The [`set_user_info()`] function writes information to user profiles.

It accepts the following keyword parameters, all of which
are optional:

 - `country`: user's country code ([ISO 3166-1 alpha-2] format).
 - `first_name`: user's first name.
 - `language`: user's language code.
 - `last_name`: user's last name.
 - `organization`: user's organization
 - `subdivisionfirst`: user's state.
 - `subdivisionsecond`: user's county.
 - `subdivisionthird`: user's municipality.
 - `language` the user's language (an [ISO-639-1] or [ISO-639-3]
   code).
 - `timezone`: user's time zone (e.g. `'America/New_York'`).
 - `password`: user's password.
 - `account_type`: the type of login the user used.  This is `local`
   for the username/password system, `auth0` for Auth0, `google` for
   Google, etc.

The current user's profile will be updated with the values of the
parameters.  Note that the `user_id` and `email` attributes cannot be
changed using this function; these attributes are used only for
selecting the user whose information is going to be changed.

This function will only work if the user running the interview that
calls the function is logged in.  Only users with `admin` [privileges]
can change passwords with this function.

Here is an example of a code block that updates the name of the user:

{% highlight yaml %}
mandatory: True
code: |
  set_user_info(first_name=user.name.first, last_name=user.name.last)
{% endhighlight %}

If the user running the interview that calls the function has `admin`
[privileges], then the function can be used to change the profiles of
other users.  A user account can be indicated by the inclusion of an
additional keyword parameter, `user_id` or `email`, that identifies
the user whose profile should be changed.

For example, the following [Python] code, when run by a user with
`admin` [privileges], will change the "organization" setting of the user
`jsmith@example.com`:

{% highlight python %}
set_user_info(email='jsmith@example.com', organization='Example, Inc.')
{% endhighlight %}

Users with `admin` [privileges] can disable user accounts by setting the
`active` keyword parameter to `False` (or enable a disabled account by
setting `active` to `True`).

In addition, users with `admin` [privileges] can change the [privileges]
of a user by setting the `privileges` keyword parameter to the list of
[privilege] names that the user should have.

{% highlight python %}
set_user_info(user_id=22, privileges=['user', 'trainer'])
{% endhighlight %}

For an [API] version of this function, see the [POST method of
`/api/user/<user_id>`], the [DELETE method of
`/api/user/<user_id>`], the [POST method of
`/api/user/<user_id>/privileges`], and the [DELETE method of
`/api/user/<user_id>/privileges`]  (Changing accounts by e-mail address is
not supported in the [API].)

## <a name="get_user_secret"></a>get_user_secret()

The [`get_user_secret()`] function takes an e-mail address and a
password as arguments and returns a decryption key if the e-mail
address/password combination is valid.  You will need this decryption
key in order to use [`get_session_variables()`] and
[`set_session_variables()`] with interview answers that are encrypted.

{% highlight python %}
secret = get_user_secret('jsmith@example.com', 'xx_Secr3t_xx')
{% endhighlight %}

Note that you need to keep decryption keys secret, or else you defeat
the purpose of server-side encryption.  The idea behind server-side
encryption is that if a system's security is breached, and all the
data on the server is revealed, the information would still be
protected because it is encrypted.  But if the decryption key is
stored on the server in an accessible place, then the information
would no longer be protected, since someone who found the decryption
key could decrypt the data.  Thus, you would not want to store the
result of [`get_user_secret()`] in the [interview session dictionary] of
an interview that sets [`multi_user`] to `True`.  Also, even if your
interview answers are encrypted, it is still a good idea to
avoid storing passwords or decryption keys in an interview session
dictionary.

For an [API] version of this function, see [`/api/secret`].

## <a name="get_session_variables"></a>get_session_variables()

The [`get_session_variables()`] function retrieves the dictionary for
an interview session.  It has two required arguments: an interview
filename (e.g., `'docassemble.demo:data/questions/questions.yml'`), a
session ID (e.g., `'iSqmBovRpMeTcUBqBvPkyaKGiARLswDv'`).  In addition,
it can take a third argument, an encryption key for decrypting the
interview answers.  If the interview answers are encrypted, the third
argument is required.

If the third argument is omitted, but the interview answers are
encrypted, the current user's decryption key will be tried.  To obtain
an encryption key for a different user, you can use
[`get_user_secret()`].

To get the interview filename for the current interview, and the
session ID for the current interview session, you can use the
[`user_info()`] function.

However, note that if you want to get the dictionary for the current
interview session, you can simply use the [`all_variables()`]
function.

Like the [`all_variables()`] function, [`get_session_variables()`]
simplifies the dictionary (converting objects to dictionaries, for
example), so that it is safe to convert the result to a format like
[JSON].  If you want the raw [Python dictionary], you can call
[`get_session_variables()`] with the optional keyword parameter
`simplify` set to `False`.

{% highlight python %}
vars = get_session_variables(filename, session_id, secret, simplify=False)
{% endhighlight %}

For an [API] version of this function, see the [GET method of `/api/session`].

## <a name="create_session"></a>create_session()

The [`create_session()`] function allows you to initiate a session in
an interview.

{% highlight python %}
yaml_filename = 'docassemble.demo:data/questions/questions.yml'
secret = get_user_secret(username, password)
session_id = create_session(yaml_filename, secret=secret, url_args={'foo': 'bar'})
{% endhighlight %}

The `session_id` that is returned can then be passed to functions like
[`set_session_variables()`].

The first and only required parameter is the file name of the YAML
interview for which you want to create a session.

The optional keyword parameter `secret` can be set to the output of
`get_user_secret()`.  If the target interview does not use server-side
encryption ([`multi_user`] is set to `False`), then the `secret`
parameter is not important.  If you do not provide a `secret`
parameter and the target interview uses server-side encryption, then
the current user's decryption key will be used, and only the current
user will be able to access the session.

The optional keyword parameter `url_args` can be set to a [Python
dictionary] representing the [`url_args`] you want to be present in
the session when it starts.

After setting the `url_args` (if any), `create_session()` will
evaluate the interview logic in the session and save the interview
answers for the session.  Thus, if `mandatory` or `initial` blocks in
the interview cause side effects, these side effects will be triggered
by the call to `create_session()`.  Also, note that when this code
executes, the user for purposes of this code execution will be the
same as the user who ran `create_session()`.

## <a name="set_session_variables"></a>set_session_variables()

The [`set_session_variables()`] function allows you to write changes
to any [interview session dictionary].  It has three required
parameters: an interview filename (e.g.,
`'docassemble.demo:data/questions/questions.yml'`), a session ID
(e.g., `'iSqmBovRpMeTcUBqBvPkyaKGiARLswDv'`), and a [Python
dictionary] containing the variables you want to set.

If you run this:

{% highlight python %}
vars = {"defense['latches']": False, "client.phone_number": "202-555-3434"}
set_session_variables(filename, session_id, vars)
{% endhighlight %}

Then the following statements will be executed in the interview
session dictionary:

{% highlight python %}
defense['latches'] = False
client.phone_number = '202-555-3434'
{% endhighlight %}

Note that if you pass [`DAFile`], [`DAFileList`], or
[`DAFileCollection`] objects from one interview session to another,
the other interview will not be able to read the files unless the
[`.set_attributes()`] method has been used to either change the
`session` and `filename` to match the destination interview session,
or the `private` attribute has been set to `False`.  Note that if the
`session` and `filename` are changed, then the first interview session
will no longer be able to access the file.  Note also that if
`private` is set to `False`, then the file will be accessible on the
internet from a URL.

This function has an optional keyword parameter `question_name`.  If
you set `question_name` to the ID of a question in the interview, the
question will be marked as answered.  You can obtain the ID of a
question from the `questionName` attribute in the question data using
[`get_question_data()`] or the [`/api/session/question`] API method.
It is only necessary to specify a `question_name` when you are setting
a variable for purposes of answering a [`mandatory`] question.  You
can tell if a question is [`mandatory`] by checking for the presence
of the attribute `mandatory` in the question data.

The [`set_session_variables()`] function accepts the optional keyword
parameter `secret`, an encryption key for decrypting the interview
answers.  If no `secret` is provided, the encryption key of the
current user is used.

It also accepts the optional keyword parameter `question_name`, which
you can set to the name of a question, if you are calling the function
to answer a specific question.  Typically, you would take the
`question_name` value from [`get_question_data()`] and pass it to
[`set_session_variables()`].  Using this parameter is necessary in
order to ensure that the interview logic moves past [`mandatory`]
questions when the variables are defined.

It also accepts the optional keyword parameter `overwrite`, which can
be set to `True` if you do not want to create a new step in the
interview when the function runs.

For an [API] version of this function, see the [POST method of
`/api/session`].

## <a name="get_question_data"></a>get_question_data()

The `get_question_data()` function returns data about the current
question of an interview session.  It has two required parameters: an
interview filename (e.g.,
`'docassemble.demo:data/questions/questions.yml'`) and a session ID
(e.g., `'iSqmBovRpMeTcUBqBvPkyaKGiARLswDv'`).  If the interview
session is encrypted, you must supply a third parameter (or the
keyword parameter `secret`) containing the encryption key for
decrypting the interview answers.

The function returns a [Python dictionary] containing information
about the question.  The format of the dictionary varies by question
type.

You should only use this function to access the question data for an
interview other than the current interview.  If you try to access the
current question in a session from within that session, there may be
an error or a long delay.

For an [API] version of this function, see the [`/api/session/question`].

## <a name="go_back_in_session"></a>go_back_in_session()

The [`go_back_in_session()`] function causes the effect of clicking
the "back" button in an interview session.  It has two required
parameters: the interview filename and the session ID.  It also accepts
an optional keyword parameter `secret`, which is the encryption key to
use to decrypt the [interview session dictionary], if it is encrypted.

{% highlight python %}
go_back_in_session(filename, session_id, secret)
{% endhighlight %}

For an [API] version of this function, see the [POST method of `/api/session/back`].

## <a name="manage_privileges"></a>manage_privileges()

The [`manage_privileges()`] function allows a user with `admin`
[privileges] to list, add, or remove [privilege] types from the list of
existing [privileges].

* `manage_privileges('list')` returns the list of existing [privilege]
  types as an alphabetically sorted list.
* `manage_privileges('add', 'supervisor')` adds a [privilege] called
  `supervisor` to the list of existing [privilege] types.
* `manage_privileges('remove', 'supervisor')` removes the [privilege] called
  `supervisor` from the list of existing [privilege] types.  Moreover,
  if any users have the [privilege], the [privilege] is taken away from
  the users.

For an [API] version of this function, see [`/api/privileges`].

# <a name="functions"></a>Miscellaneous functions

## <a name="validation_error"></a>validation_error()

<a name="DAValidationError"></a>The `validation_error()` function
takes an error message as a parameter and [`raise`]s a
`DAValidationError` exception with that error message.  This means
that any code that follows the call to `validation_error()` will not
be executed.

This is primarily useful inside [`validate`] code and [`validation
code`] when you want to indicate that the validation did not succeed.
The `validation_error()` function requires a single argument, which is
the error message the user should see.

For more information, see the documentation for [`validate`] and
[`validation code`].

The `validation_error()` function can be used to raise an error
message from inside a [lambda function] that is used as the argument
for [`validate`]:

{% include side-by-side.html demo="validation-error" %}

However, note that [lambda functions] can be confusing to people who
don't have a good knowledge of [Python], so you might want to keep
them out of your interview files.

`validation_error()` accepts an optional keyword argument `field`,
which should refer to a variable name on the screen.  If you call
`validation_error()` from [`validation code`] and reference a `field`,
the error message will be placed next to the indicated field.

## <a name="server_capabilities"></a>server_capabilities()

The `server_capabilities()` function returns a dictionary indicating
whether the server has particular features enabled.

{% include side-by-side.html demo="server-capabilities" %}

The keys are:

* `sms` - whether SMS messaging is available.  See the [`twilio`]
  configuration.
* `fax` - whether fax sending is available.  See the [`twilio`]
  configuration.
* `google_login` - whether logging in with Google is available.  See
  the [`oauth`] configuration.
* `facebook_login` - whether logging in with Facebook is available.
  See the [`oauth`] configuration.
* `twitter_login` - whether logging in with Twitter is available.
  See the [`oauth`] configuration.
* `phone_login` - whether logging in with an [SMS] security code is
  available.  See the [`phone login`] configuration.
* `voicerss` - whether the text-to-speech feature is available.  See
  the [`voicerss`] configuration.
* `s3` - whether [Amazon S3] is enabled.  See the [`s3`]
  configuration.
* `azure` - whether [Azure blob storage] is enabled.  See the [`azure`]
  configuration.
* `googledrive` - whether [Google Drive synchronization] is
  available.  See the [`googledrive`] configuration.
* `github` - whether developers have the option of integrating their
  [Playground]s with [GitHub].  See the [`github`] configuration.
* `pypi` - whether developers have the option of integrating their
  [Playground]s with [PyPI].  See the [`pypi`] configuration.
* `google_maps` - whether the Google Maps API (used in the [`map_of()`]
  function and the [`geolocate()`] method) is available.  See the
  [`google`] configuration.

## <a name="referring_url"></a>referring_url()

Returns the URL that the user was visiting when the user clicked on a
link to go to the interview.

Under some circumstances, this URL cannot be obtained.  For example,
if the user started the interview by typing a URL directly into the
location bar of the browser, or if the user has a browser setting that
blocks the [referer header], then the URL will not be available.

If the URL cannot be obtained, then the URL indicated by the optional
keyword parameter `default` will be returned.  If no `default` URL is
provided, or `default` is `None`, then the value of the configuration
directive [`exitpage`] will be used.

This function is useful when you want to bring the user back to where
they started at the end of the interview.

{% include side-by-side.html demo="exit-url-referer" %}

If you just want to find out the referring URL, make sure to set the
`default` parameter to something you can test.  For example, the
following blocks will set the variable `how_user_heard_of_us` either
by obtaining the referring URL or, if the URL is not available, by
asking the user "How did you hear about us?"

{% highlight yaml %}
question: |
  How did you hear about us?
fields:
  no label: how_user_heard_of_us
---
code: |
  if referring_url(default=False) is not False:
    how_user_heard_of_us = referring_url()
{% endhighlight %}

## <a name="static_image"></a>static_image()

{% include side-by-side.html demo="static_image" %}

Returns appropriate markup to include a static image.  If you know the
image path, you can just use the `[FILE ...]` [markup] statement.  The
`static_image()` function is primarily useful when you want to
assemble the image path using code.

The function takes an optional keyword argument "width" that will
affect the width of the image on the screen or page:

{% highlight python %}
static_image('docassemble.demo:crawling.png', width='2in'))
{% endhighlight %}

## <a name="get_config"></a>get_config()

Returns a value from the **docassemble** configuration file.  If the
value is not defined, returns None.

See the explanation of this function in the
[configuration section]({{ site.baseurl }}/docs/config.html#get_config")
for more information.

## <a name="prevent_going_back"></a>prevent_going_back()

**docassemble**'s back button helps users when they make a mistake and
want to go back and correct it.  But sometimes, we want to prevent
users from going back.  For example, if the interview code causes an
e-mail to be sent, or data to be written to a database, allowing the
user to go back and do the process again would create confusion.

You can call `prevent_going_back()` to instruct the web application to
prevent the user from going back past that point.  See also the
[modifier] of the same name.

{% include side-by-side.html demo="prevent-back" %}

## <a name="selections"></a>selections()

This is used in multiple choice questions in `fields` lists where the
`datatype` is `object`, `object_radio`, or `object_list` and the list
of selections is created by embedded `code`.  The function takes one
or more arguments and outputs an appropriately formatted list of
objects.  If any of the arguments is a list, the list is unpacked and
its elements are added to the list of selections.

## <a name="objects_from_file"></a>objects_from_file()

`objects_from_file()` imports data from a [YAML] or [JSON] file,
including objects.

The import acts like a standard [YAML] import, except that when an
[associative array] (dictionary) is encountered that has the keys
`object` and `items`, then the [associative array] is converted into a
list of objects (specifically, a [`DAList`]).  In addition, if an
[associative array] is encountered that has the keys `object` and
`item`, then the [associative array] is converted into a single
object.

{% include demo-side-by-side.html demo="objects-from-file" %}

In the above example, the file [`contacts.yml`] file has the following contents:

{% highlight yaml %}
object: Individual
module: docassemble.base.util
items:
  - name:
      object: IndividualName
      item:
        first: Fred
        last: Smith
    email: fred@example.com
    allergies:
      - peanuts
      - subway tokens
  - name:
      object: IndividualName
      item:
        first: Larry
        last: Jones
    email: larry@example.com
    skills:
      - stapling
      - making coffee
{% endhighlight %}

This example uses two standard **docassemble** [objects],
[`Individual`] and [`IndividualName`].

A [JSON] file can also be used.

{% include demo-side-by-side.html demo="objects-from-file-json" %}

In the above example, the file [`contacts.json`] file has the following contents:

{% highlight yaml %}
{
    "object": "Individual",
    "module": "docassemble.base.util",
    "items": [
        {
            "name": {
                "object": "IndividualName",
                "module": "docassemble.base.util",
                "item": {
                    "first": "Fred",
                    "last": "Smith"
                }
            },
            "email": "fred@example.com",
            "allergies": [
                "peanuts",
                "subway tokens"
            ]
        },
        {
            "name": {
                "object": "IndividualName",
                "module": "docassemble.base.util",
                "item": {
                    "first": "Larry",
                    "last": "Jönes"
                }
            },
            "email": "larry@example.com",
            "skills": [
                "stapling",
                "making coffee"
            ]
        }
    ]
}
{% endhighlight %}

### What gets returned

The `objects_from_file()` function will return a [`DAList`] object if:

* There is more than one [YAML] "[document]" (separated by `---`).
* There is one [YAML] "[document]" and it is an [associative array] with
  the keys `object` and `items`.

If there is one [YAML] "[document]" and it is an [associative array]
with the keys `object` and `item`, then the object itself will be
returned.

If there is one [YAML] "[document]" and it is something other than an
[associative array] with the keys `object` and `items` or `object` and
`item`, then the data structure will be returned.

There is an optional keyword argument `name` that will be used to set
the [`.instanceName`] attribute of the resulting object.  If you do
not pass a `name` parameter, the object/data structure returned by
`objects_from_file()` will still be readable, but it will not be
writable by **docassemble** questions.

There is also an optional keyword argument `use_objects`, which, if
`True`, will cause lists to become gathered [`DAList`]s, and
dictionaries to become gathered [`DADict`]s.

Note that there is an [initial block] called [`objects from file`]
that can be used as a shorthand way of calling `objects_from_file()`.
Instead of writing:

{% highlight yaml %}
---
mandatory: True
code: |
  claims = objects_from_file('claim_list.yml', name='claims')
---
{% endhighlight %}

you can instead write:

{% highlight yaml %}
---
objects from file:
  - claims: claim_list.yml
---
{% endhighlight %}

### Using your own object types

If you want to import objects that are not standard **docassemble**
[objects], you need to specify a `module` that defines the object's
class so that **docassemble** knows where to get the class definition.

For example, suppose you defined some classes with a [Python module]
called [`fish.py`]:

{% highlight python %}
from docassemble.base.util import DAObject

class Halibut(DAObject):
    pass

class Food(DAObject):
    pass
{% endhighlight %}

Suppose you want to import some objects of type `Halibut`.  You can
create a [YAML] file called [`fishes.yml`] with the following
contents:

{% highlight yaml %}
object: Halibut
module: .fish
items:
  - name: Fred Halibut
    scales: 500
    food:
      object: Food
      module: .fish
      items:
        - name: plankton
          calories: 5
  - name: Larry Halibut
    scales: 600
    food:
      object: Food
      module: .fish
      items:
        - name: seaweed
          calories: 2
{% endhighlight %}

Note the inclusion of `module: .fish` along with each `object`
specifier.  This indicates that the `Halibut` and `Food` classes are
defined in the module `.fish`.

The following interview will import these two `Halibut` objects into
the interview:

{% include demo-side-by-side.html demo="fish-example" %}

Note that the `.` in front of the module name (`.fish`) is
[standard Python notation] for indicating that the module is part of
the current package.  In this example, the interview lives in the
[`docassemble.demo`] package, so we could have written the full module
name, `docassemble.demo.fish`, instead of `.fish`.

To see how these separate files are able to find one another, check
out the [`docassemble.demo` package on GitHub] and look for the
following files:

* The interview file, `data/questions/examples/fish-example.yml`
* The [Python module], `fish.py`
* The [YAML] data file, `data/sources/fishes.yml`

### How YAML files are located

When the interview calls `objects_from_file('fishes.yml')`, the
`objects_from_file()` function looks for the file `fishes.yml` in the
`data/sources` folder of the current package (or the [sources folder]
if your interview is running in the [Playground]).

The `objects_from_file()` function can also be given explicit
references.  For example, calling
`objects_from_file('docassemble.demo:data/sources/fishes.yml')` would
have the same effect.

### Preventing recursive object conversion

By default, `objects_from_file()` will comb through the data structure
looking for objects to convert.  If you only want it to convert
objects that are specified in an [associative array] at the very top
level, you can set the keyword parameter `recursive` to `False`.

{% include demo-side-by-side.html demo="raw-data-example" %}

### How objects are created

The `objects_from_file()` creates objects by passing keyword arguments
to the object constructor.  In the "fishes" example above, the first
object was effectively created by calling:

{% highlight python %}
Halibut(name='Fred Halibut', scales=500, food=[Food(name='plankton', calories=5)])
{% endhighlight %}

The second object was effectively created by calling:

{% highlight python %}
Halibut(name='Larry Halibut', scales=600, food=[Food(name='seaweed', calories=2)])
{% endhighlight %}

Therefore, object attributes will only be initialized if the object
supports initialization of attributes through keyword arguments passed
to the constructor.  All objects that are instances of the
[`DAObject`] class have this property.

However, if you are using objects that are not [`DAObject`]s, but you
want to make them compatible with `objects_from_file()`, you can
include an [`__init__()`] method in your class that does the following:

{% highlight python %}
class SwordFish:
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
{% endhighlight %}

You could also write your own custom code in [`__init__()`] that
initiates the object attributes in special ways in response to keyword
parameters.

You can use `objects_from_file()` to import other kinds of objects
that allow initialization through keyword parameters.  For example,
[`datetime.datetime`] objects can be created by doing:

{% highlight python %}
datetime.datetime(year=2017, month=4, day=1)
{% endhighlight %}

Thus, you could import a [`datetime.datetime`] object with the following [YAML]:

{% highlight yaml %}
object: datetime
module: datetime
item:
  year: 2017
  month: 4
  day: 1
{% endhighlight %}

### Importing group objects

To import a [`DAList`], [`DADict`], or [`DASet`] objects that contain
items, set the `elements` attribute to a [YAML] list (in the case of a
[`DAList`] or [`DASet`] or a [YAML] dictionary (in the case of a
[`DADict`]).

Here is a sample [YAML] file that defines a [`DADict`]:

{% highlight yaml %}
object: DADict
item:
  elements:
    apple: 4
    peach: 5
    orange: 10
{% endhighlight %}

Here is an interview that imports this file:

{% include demo-side-by-side.html demo="objects-from-file-dadict" %}

By default, any groups that are populated by importing will be marked
as [gathered].  If you want **docassemble** to ask the user if more
elements should be added, you can set the optional keyword argument
`gathered` to `False`:

{% include demo-side-by-side.html demo="objects-from-file-gather" %}

### Avoiding problems with whitespace

If you include text in your [YAML] file and you wish to use this text
within documents, you should understand a few rules about [YAML].

This in [YAML]:

{% highlight yaml %}
claim: |
  The landlord is not entitled
  to collect back rent.
{% endhighlight %}

becomes this in [Python]:

{% highlight python %}
{'claim': 'The landlord is not entitled\nto collect back rent.\n'}
{% endhighlight %}

Note that the newline after the word "entitled" was treated
literally (`\n`), and a newline was added at the end.  This is not a problem
when your text is treated as [Markdown], because [Markdown] treats
single newlines as though they were spaces and only breaks a line when
it sees two newlines together.  However, if you are inserting text
into a [`docx template file`], the newlines will cause paragraph
breaks, which may be what you want, or it may not be what you want.

Here are some [YAML] tips that can help you out in situations like
this.

This in [YAML]:

{% highlight yaml %}
claim: |-
  The landlord is not entitled
  to collect back rent.
{% endhighlight %}

becomes this in [Python]:

{% highlight python %}
{'claim': 'The landlord is not entitled\nto collect back rent.'}
{% endhighlight %}

Changing the quote mark from `|` to `|-` gets rid of the newline at the
end, but not the one in the middle.

This in [YAML]:

{% highlight yaml %}
claim: >
  The landlord is not entitled
  to collect back rent.
{% endhighlight %}

becomes this in [Python]:

{% highlight python %}
{'claim': 'The landlord is not entitled to collect back rent.\n'}
{% endhighlight %}

The `>` treats newlines as spaces, but adds a newline at the end.

{% highlight yaml %}
claim: >-
  The landlord is not entitled
  to collect back rent.
{% endhighlight %}

becomes this in [Python]:

{% highlight python %}
{'claim': 'The landlord is not entitled to collect back rent.'}
{% endhighlight %}

The `>-` quote mark treats newlines as spaces and refrains from adding
a newline at the end.

This in [YAML]:

{% highlight yaml %}
claim: The landlord is not entitled to collect back rent.
{% endhighlight %}

becomes this in [Python]:

{% highlight python %}
{'claim': 'The landlord is not entitled to collect back rent.'}
{% endhighlight %}

Similarly, this in [YAML]:

{% highlight yaml %}
claim: "The landlord is not entitled to collect back rent."
{% endhighlight %}

also becomes:

{% highlight python %}
{'claim': 'The landlord is not entitled to collect back rent.'}
{% endhighlight %}

The quotation marks do not change the text in this case.  Quotation
marks can still be useful, however, if your text contains any
punctuation marks that have special meaning in [YAML].

If you want literal quotation marks, you could use quotes within
quotes:

This in [YAML]:

{% highlight yaml %}
quotation: '"It was the best of times, it was the worst of times."'
{% endhighlight %}

becomes this in [Python]:

{% highlight python %}
{'quotation': '"It was the best of times, it was the worst of times."'}
{% endhighlight %}

Similarly, this in [YAML]:

{% highlight yaml %}
quotation: >-
  "It was the best of times, it was the worst of times."
{% endhighlight %}

also becomes:

{% highlight python %}
{'quotation': '"It was the best of times, it was the worst of times."'}
{% endhighlight %}

For more information, see [The YAML Format].

## <a name="ocr_file"></a>ocr_file()

Given a PDF file, `ocr_file()` uses [optical character recognition] (OCR) to
read the text of the file.  In the text returned, pages are
separated by the [form feed character].

{% include side-by-side.html demo="ocr" %}

The first argument must be a [`DAFile`] or [`DAFileList`] object.  If
the argument is a [`DAFileList`] with more than one file, all files
will be OCRed, and the text of all the pages will be returned.

The following optional keyword arguments affect the way OCR is
performed.

* `language` indicates the language of the document.  If not
  specified, the language returned by `get_language()` is used.  The
  language must be a lowercase [ISO-639-1]/[ISO-639-3] code or a
  language code that [Tesseract] uses.
* `psm` indicates the [Tesseract] page segmentation mode.  The default
is 6 ("assume a uniform block of text").  The choices are:
    * 0: Orientation and script detection (OSD) only.
    * 1: Automatic page segmentation with OSD.
    * 2: Automatic page segmentation, but no OSD, or OCR.
    * 3: Fully automatic page segmentation, but no OSD. (Default)
    * 4: Assume a single column of text of variable sizes.
    * 5: Assume a single uniform block of vertically aligned text.
    * 6: Assume a single uniform block of text.
    * 7: Treat the image as a single text line.
    * 8: Treat the image as a single word.
    * 9: Treat the image as a single word in a circle.
    * 10: Treat the image as a single character.

In addition, the following optional parameters, which are passed to
[pdftoppm], customize the conversion of PDF files:

* `f` indicates the first page of the PDF file to read.  By
  default, all pages are read.
* `l` indicates the last page of the PDF file to read.  By
  default, all pages are read.
* `x`: for cropping PDF pages.  Indicates the x-coordinate of the crop
  area's top left corner, in pixels.  (By default, PDF files are
  converted at 300 dpi unless another value is given by the
  [`ocr dpi`] configuration directive.)
* `y`: for cropping PDF pages.  Indicates the y-coordinate of the crop
  area's top left corner, in pixels.
* `W`: for cropping PDF pages.  Indicates the width of the crop area
  in pixels (default is 0).
* `H`: for cropping PDF pages.  Indicates the height of the crop area
  in pixels (default is 0).

## <a name="ocr_file_in_background"></a>ocr_file_in_background()

Note that the OCR process usually takes a long time; it takes a lot of
computational power to recognize characters from a graphical image.
Unless the document is only one page long, the user will have to wait,
looking at a spinner, for what may be an inconvenient period of time.
The user may think that the application has crashed.

The best practice is to run OCR tasks in the background, using the
[`ocr_file_in_background()`] function.  This function is a cross
between [`ocr_file()`] and [`background_action()`].

To control the details of the OCR process, you can set optional
keyword parameters `language`, `psm`, `x`, `y`, `W`, and `H`.  (See
[`ocr_file()`] for information about what these do.)

Like [`background_action()`], it immediately returns an object
representing a background task.  You can call `.ready()` on this
object to see if the task is still running in the background, and you
can call `.get()` to obtain the result of the OCR task.  (See
[`background_action()`] for more information about these methods.)

Here is an example of how [`ocr_file_in_background()`] can be used.

{% include side-by-side.html demo="ocr-chord" %}

This example demonstrates a technique for avoiding making the user
wait.  First, the user uploads a document.  Then,
[`ocr_file_in_background()`] is called on the uploaded file, which
starts the OCR process in the background.  Then, the user is asked a
question ("What is your nickname?").  Then is the user sent to a
screen that displays the text obtained through OCR.  Hopefully, the
question about the nickname took enough time that the results of the
OCR are ready by the time this screen appears in the interview.  Just
in case there wasn't enough time, the interview question calls
`.ready()` to check to see if the task is done.  If it is not done,
the user is asked to wait, and to press "Refresh."  If the process has
completed by then, `.ready()` will be `True`, and the user can see the
text obtained through OCR.

It is safe to call `.get()` without first ensuring that `.ready()` is
`True`.  The `.get()` method will cause the system to wait until the
OCR text is available.  The user will see a spinner in the meantime.

Other questions could be asked, in addition to the nickname question,
in order to give the computer more time to finish the OCR process.

If you do not want to stall for time by asking questions, but you want
to give the user a user-friendly screen to look at while they wait and
you don't want to make the user press a Refresh button, you can use
the optional second argument to the [`ocr_file_in_background()`]
function.  This second argument acts like the second argument to
[`background_action()`].  In this example, we set it to `refresh`:

{% include side-by-side.html demo="ocr-chord-refresh" %}

Be careful about combining the use of `refresh` with the method of
asking questions of the user to pass the time.  If any of the
questions call for the user to type something in, the user will be
very annoyed if the screen refreshes while they are typing; they will
lose what they have typed.  However, if you are only asking questions
that require buttons to be pressed, then the user will not notice if
the screen refreshes.

You can also use other notification methods, such as:

* `ocr_file_in_background(the_file, 'javascript', message='all done')`
* `ocr_file_in_background(the_file, 'flash', message='All done')`

These notification methods show a Javascript alert or a message
"flashed" at the top of the screen when the background task is
complete.  The message is "OCR succeeded" unless you override the
message using the optional keyword argument `message`.

See the documentation of [`background_action()`] for more information
about notification methods.

The value returned by `.get()` is an object, not a piece of text.  If
the attribute `.ok` is `True`, the text can be found in the `.content`
attribute of this object.  If the attribute `.ok` is `False`, then
there was an error during the OCR process, and the error message can
be found in the attribute `.error_message`.  When you put the output
of `.get()` inside of a `${ ... }` [Mako] tag, the object is forced to
be text, in which case either `.content` or `.error_message` is used,
depending on the success of the OCR process.

### Advantages of [`ocr_file_in_background()`] over [`ocr_file()`]

Note that it is also possible to use [`ocr_file()`] within
[`background_action()`]:

{% include side-by-side.html demo="ocr-background" %}

However, the advantage of [`ocr_file_in_background()`] is that it can
be a lot faster if there is more than one page image.  The
[`ocr_file()`] function OCRs one page at a time, using a single CPU
core.  The [`ocr_file_in_background()`] function, by constrast,
assigns each page image to a separate background task, and these tasks
are then distributed across all the CPU cores in your system.  If your
**docassemble** installation has two application servers, each with
four CPU cores, the system will process the OCR job eight pages at a
time rather than one page at a time.  For a large document,
[`ocr_file_in_background()`] will get the whole job done much faster.

### Running OCR with languages other than English

[Tesseract] supports the following languages.

|------------+---------------------|
| Code       | Language            |
|------------+---------------------|
| `afr`      | Afrikaans           |
| `ara`      | Arabic              |
| `aze`      | Azerbaijani         |
| `bel`      | Belarusian          |
| `ben`      | Bengali             |
| `bul`      | Bulgarian           |
| `cat`      | Catalan             |
| `ces`      | Czech               |
| `chi-sim`  | Simplified Chinese  |
| `chi-tra`  | Traditional Chinese |
| `chr`      | Cherokee            |
| `dan`      | Danish              |
| `deu`      | German              |
| `deu-frak` | German Fraktur      |
| `ell`      | Greek               |
| `eng`      | English             |
| `enm`      | Middle English      |
| `epo`      | Esperanto           |
| `est`      | Estonian            |
| `eus`      | Basque              |
| `fin`      | Finnish             |
| `fra`      | French              |
| `frk`      | Frankish            |
| `frm`      | Middle French       |
| `glg`      | Galician            |
| `grc`      | ancient Greek       |
| `heb`      | Hebrew              |
| `hin`      | Hindi               |
| `hrv`      | Croatian            |
| `hun`      | Hungarian           |
| `ind`      | Indonesian          |
| `isl`      | Icelandic           |
| `ita`      | Italian             |
| `ita-old`  | Old Italian         |
| `jpn`      | Japanese            |
| `kan`      | Kannada             |
| `kor`      | Korean              |
| `lav`      | Latvian             |
| `lit`      | Lithuanian          |
| `mal`      | Malayalam           |
| `mkd`      | Macedonian          |
| `mlt`      | Maltese             |
| `msa`      | Malay               |
| `nld`      | Dutch               |
| `nor`      | Norwegian           |
| `pol`      | Polish              |
| `por`      | Portuguese          |
| `ron`      | Romanain            |
| `rus`      | Russian             |
| `slk`      | Slovak              |
| `slk-frak` | Slovak Fractur      |
| `slv`      | Slovenian           |
| `spa`      | Spanish             |
| `spa-old`  | Old Spanish         |
| `sqi`      | Albanian            |
| `srp`      | Serbian             |
| `swa`      | Swahili             |
| `swe`      | Swedish             |
| `tam`      | Tamil               |
| `tel`      | Telugu              |
| `tgl`      | Tagalog             |
| `tha`      | Thai                |
| `tur`      | Turkish             |
| `ukr`      | Ukranian            |
| `vie`      | Vietnamese          |
|------------|---------------------|
{: .table }

The `language` parameter is flexible; you can set it to a language
code that [Tesseract] supports (e.g., `eng`, `chi-sim`, `chi-tra`,
`slk-frak`), or you can give it a two-character [ISO-639-1] code, in
which case **docassemble** will convert it to the corresponding
[Tesseract] code.  If [Tesseract] does not support the language,
English will be used.  If the `language` parameter is not supplied,
**docassemble** will use the default language (the result of
`get_language()`).

For some languages, there is more than one variant.  For example, if
you specify Chinese, `zh`, **docassemble** will use `chi-tra`
(traditional Chinese).  If this is not what you want, you can specify
an explicit `language` parameter, such as `chi-sim` (simplified
Chinese).  Alternatively, you can override the mapping between
[ISO-639-1] codes and [Tesseract] codes by editing the
[`ocr languages`] directive in the [configuration].  For example, if
you wanted all Chinese to be interpreted as Simplified Chinese, and
all Uzbek to be interpreted as the Cyrillic form, you could set the
following:

{% highlight yaml %}
ocr languages:
  zh: chi-sim
  uz: uzb-cyrl
{% endhighlight %}

## <a name="path_and_mimetype"></a>path_and_mimetype()

The `path_and_mimetype()` function returns a [tuple] consisting of a
file path and [MIME type] for a given reference to a file.

The function works with a variety of file references, including:

* A `DAFile` object;
* A file number (see [`DAFile`]);
* A reference to a file in the current package (e.g.,
`data/sources/training-data.json`);
* A reference to a file in a particular package (e.g.,
`docassemble.demo:data/static/crown.png`); or
* A URL to a file on the Internet.

If the reference is to a file on the Internet, the file will be
downloaded to a temporary file.

{% include side-by-side.html demo="path-and-mimetype" %}

Paths retrieved through `path_and_mimetype()` can be used by [Python]
functions right away.

Note, however, that paths obtained from [`DAFile`] objects, file
numbers, and URLs, will not necessarily be stable from request to
request.  If you save a path to a variable at one time, and expect to
use it later in a subsequent question, you may find that the path does
not exist.  This is because temporary files can be deleted, and
subsequent user screens may be handled by different servers.

If you want a file that persists from request to request, you should
store its contents to a [`DAFile`] object.  When a [`DAFile`] object
is assigned to a variable, you can reliably obtain the file path by
calling the [`.path()`] method on the variable.

The `path_and_mimetype()` function can be used along with the
[`.set_mimetype()`] and [`.copy_into()`] methods of the [`DAFile`]
class in order to save files to [`DAFile`] objects.

The following interview retrieves an image from the Internet and saves
it to a variable `logo`, which is a [`DAFile`] object.

{% include side-by-side.html demo="save-url-to-file" %}

## <a name="run_python_module"></a>run_python_module()

The `run_python_module()` runs a [Python module] as though it were
being run from the command line, and returns the output of the command
(standard output as well as standard error) along with the return code
from running the command.

The first argument, which is required, is the name of the module.
This can be expressed in a few ways.  If it is the name of a file
ending in .py, it is assumed to be a module in the same package as the
interview file.  Or, if you are using the [Playground], it is assumed
to be a file in the [modules folder].  The module file is executed as
you would execute a module file by using `python modulename.py` from
the command line.  If the first argument is the name of a module, that
module will be run, much as you would execute a module by using `python
-m modulename` from the command line.

The function returns a tuple of two variables: the output of the
command (text) and the return value (an integer).  If the command
was successful, the return value will be zero.

The following three example interviews refer to a very simple
[Python module] file, [`hello.py`].  The contents of this file are:

{% highlight python %}
print "Hello, world!"
{% endhighlight %}

The interviews and the [`hello.py`] module are all in the
[`docassemble.demo`] package.

The first example refers to the .py file:

{% include demo-side-by-side.html demo="run-python-module" %}

The second example refers to the same [Python module], but by its full
module name:

{% include demo-side-by-side.html demo="run-python-module-2" %}

The third example refers to the same [Python module], but using a
[relative module name] instead of a full module name:

{% include demo-side-by-side.html demo="run-python-module-3" %}

Note that the first example and the third example only work because
the interviews and the module are in the same package.

When calling `run_python_module()`, you can also include an optional
second argument, which must be a list of command line arguments to be
passed to the module.

The following example demonstrates how you can use
`run_python_module()` to run unit tests using the standard
[`unittest` framework].  The interview, the [`tests.py`] file it
refers to, and the [`my_name_suffix`] module that is being tested in
[`tests.py`], are all in [`docassemble.demo`] package.

The command line argument `-v` results in "verbose" output.

{% include demo-side-by-side.html demo="run-python-module-tests" %}

The [`indent()`] function is used here because it indents each line in
the output by four spaces.  In [Markdown], this causes the text to be
displayed in a monospace font.

## <a name="pdf_concatenate"></a>pdf_concatenate()

The `pdf_concatenate()` function accepts one or more file objects
([`DAFile`], [`DAStaticFile`], [`DAFileList`], or
[`DAFileCollection`]) as input (raw file paths are also accepted) and
returns a [`DAFile`] containing the files concatenated into a single
[PDF] file.  Image files and word processing files (.doc, .docx, .rtf,
and .odt) will be converted to [PDF].  If any of the arguments is a
list, it will be unpacked.

{% include side-by-side.html demo="pdf-concatenate" %}

`pdf_concatenate()` has three optional keyword parameters:

* `filename`: if provided, this will be the name of the resulting
  file.  If not provided, the file will be named `file.pdf`.
* `pdfa`: if `True`, the [PDF] file will be converted to [PDF/A]
  format.  The default is `False`.
* `password`: if provided, the [PDF] file will be protected.  See the
  documentation for the [`password`] document modifier.

## <a name="docx_concatenate"></a>docx_concatenate()

The `docx_concatenate()` function accepts one or more file objects
([`DAFile`], [`DAStaticFile`], [`DAFileList`], or
[`DAFileCollection`]) as input (raw file paths are also accepted) and
returns a [`DAFile`] containing the files concatenated into a single
[DOCX] file.  Only word processing files (.doc, .docx, .rtf, and .odt)
are accepted.  If any of the arguments is a list, it will be unpacked.

`docx_concatenate()` takes an optional keyword parameter `filename`,
which, if provided, will be used as the name of the resulting file.
If no `filename` is provided, the file will be named `file.docx`.

## <a name="overlay_pdf"></a>overlay_pdf()

The `overlay_pdf()` function overlays a single page from a PDF file on
top of the pages of another PDF file.

It has two mandatory parameters: a main document, and an overlay
document.  The parameters can be [`DAFileCollection`], [`DAFileList`],
or [`DAFile`] objects.  They can also be file paths for files on the
file system.

The function returns a [`DAFile`] containing a PDF file where the
first page of the overlay document has been superimposed on top of the
main document.

{% include demo-side-by-side.html demo="overlay-pdf" %}

The `overlay_pdf()` function accepts several optional keyword
parameters.  If you only want to overlay on top of some of the pages
of the main document, you can indicate a `first_page` and/or a
`last_page`, which will instruct `overlay_pdf()` to start at a given
page number and/or end at a given page number.  By default,
`overlay_pdf()` starts on the first page and ends on the last page.
If you only want to overlay over even-numbered pages, set `only` to
`'even'`.  If you only want to overlay over odd-numbered pages, set
`only` to `'odd'`.

If your document containing the logo has more than one page, you can
specify which page to use by setting `logo_page` to the page number of
the page you want to use.

## <a name="zip_file"></a>zip_file()

The `zip_file()` function is like the [`pdf_concatenate()`] function,
except it returns a [ZIP file] archive of the files.

`zip_file()` has one optional keyword parameter:

* `filename`: if provided, this will be the name of the resulting
  file.  If not provided, the file will be named `file.zip`.

If you want your zip file to include file structure, you can pass a
[Python dictionary] as a parameter, and they keys of the dictionary
will be folder names.

The following example results in a [ZIP file] called "Image files.zip"
that contains an uploaded file and a folder called `assets` that
contains two files from the "static" folder of the interview's
[package].

{% include side-by-side.html demo="zip-file" %}

## <a name="log"></a>log()

The `log()` function allows you to log a message to the server log, to
the browser console, or to the user's screen.

The first parameter is the message you want to send.  The second
parameter, which is optional, is the "priority" of the message.  The
default priority is `'log'`.

{% include side-by-side.html demo="log" %}

The options for the `priority` are:

* `'log'` - a message is immediately logged to the server logs.
* `'console'` - when the next screen loads in the user's browser, the
  message will appear in the browser log.  (This uses the
  [`console.log` JavaScript function].)
* `'javascript'` - like `'console'`, except that the contents of the
  "message" will be passed to the [`eval` JavaScript function] instead
  of the [`console.log` JavaScript function].  This allows you to log
  a message in the front end in your own custom fashion.  It can also
  be used for tasks other than logging messages.
* `'success'` - when the next screen loads in the user's browser, a
  popup message (a [Bootstrap alert]) will appear at the top of the
  page, using the [Bootstrap] color associated with "success"
  (typically green).  The message will disappear after a few seconds.
* `'info'` - like `'success'`, except it uses the "info" [Bootstrap]
  color.  The message will not disappear.
* Other [Bootstrap] color names besides `'info'` and `'success'`.

The [Bootstrap] color names are as follows:

<div class="card">
<div class="card-body">
<div class="alert alert-primary">primary</div>
<div class="alert alert-secondary">secondary</div>
<div class="alert alert-success">success</div>
<div class="alert alert-danger">danger</div>
<div class="alert alert-warning">warning</div>
<div class="alert alert-info">info</div>
<div class="alert alert-light">light</div>
<div class="alert alert-dark">dark</div>
</div>
</div>

You can also use the [JavaScript] function [`flash()`] to display
notifications like this.

## <a name="encode_name"></a>encode_name()

In the [HTML] of the web interface, input elements for variables are
base64-encoded versions of the [Python] variable names.

The `encode_name()` function converts a variable name to base64
encoding.

{% highlight python %}
>>> encode_name('favorite_fruit')
'ZmF2b3JpdGVfZnJ1aXQ'
{% endhighlight %}

For more information about the relationship between [HTML] and the
setting of variables, see the discussion in the
[section on custom front ends].

## <a name="decode_name"></a>decode_name()

The `decode_name()` function does the opposite of [`encode_name()`]:
it converts a variable name from base64 encoding to plain text.

{% highlight python %}
>>> decode_name('ZmF2b3JpdGVfZnJ1aXQ')
'favorite_fruit'
{% endhighlight %}

## <a name="mmdc"></a>mmdc()

Using the `mmdc()` function, you can use the [mermaid] diagram-drawing
system to produce a [`DAFile`] containing a completed diagram.

The `mmdc()` function is defined in the `docassemble.base.mermaid`
package.  To use it, you will need to include the
`docassemble.base.mermaid` module in your interview:

{% highlight yaml %}
modules:
  - docassemble.base.mermaid
{% endhighlight %}

Then you can call the `mmdc()` function on a text string or a
[`template`] object.

{% include side-by-side.html demo="mermaid" %}

If you installed **docassemble** with the standard [Docker]
installation, then the [mermaid] executable (`mmdc`) should be
available on the standard system path.  You can set a precise location
by setting the `mmdc path` directive in the [Configuration].

{% highlight yaml %}
mmdc path: /var/www/node_modules/.bin/mmdc
{% endhighlight %}

# <a name="sms"></a>Functions for working with SMS messages

## <a name="send_sms"></a>send_sms()

The `send_sms()` function is similar to `send_email()`, except it
sends a text message (also known as an [SMS] message).  This requires
a [Twilio] account.

All of its arguments are [keyword arguments], the defaults of which
are:

{% highlight python %}
send_sms(to=None, body=None, template=None, task=None, attachments=None, config='default')
{% endhighlight %}

* `to` expects a [list] of recipients.  The list can consist of
  [`Individual`]s (or any other [`Person`]s), objects of type
  [`phonenumbers.PhoneNumber`], or a simple string containing a phone
  number.  If the number begins with `whatsapp:`, then [WhatsApp] will
  be used to send the message.  If the recipient is a [`Person`], then
  the [`sms_number()`] method will be used to obtain the person's number.
* `body` expects text, or `None`.  If provided, it will be the content
  of the message.  Markdown will be converted to plain text.
* `template` expects a [`template`] object, or `None`.  These
  templates can be created in an interview file using the `template`
  specifier.  The "subject" of the template, if provided, will be the first
  line of the message.
* `task` expects the name of a [task].  If this argument is provided,
  and if sending the text message is successful, the task will be
  marked as having been performed (i.e., [`mark_task_as_performed()`]
  will be called).  Alternatively, you can handle this in your own
  code, but you might find it convenient to let the `send_email()`
  function handle it for you.
* `task_persistent`: if you set a `task`, you can optionally set
  the "persistence" of the task by setting this to `True` or a value
  like `'user'`.  For more information, see the documentation for the
  [task-related functions](#tasks).
* `attachments` expects a [list] of [`DAFile`] objects, [`DAFileList`]
  objects, [`DAFileCollection`] objects, or ordinary URLs.  If
  provided, the message will be an [MMS] message containing the
  attached files.  No more than 10 attachments may be added.  You can
  include:
  * Images generated by `signature` blocks (objects of class
  [`DAFile`]);
  * File uploads generated by including [fields] of `datatype: file` or
  `datatype: files` in a [`question`] (objects of class [`DAFileList`]);
  * [Documents] generated by [`attachments`] to a [`question`] for which a
  `variable` was provided (objects of class [`DAFileCollection`]).
* `config` indicates the section of the [`twilio`] configuration that
  should be used when sending the text message.  If you only have one
  [Twilio] phone number, you do not need to set this parameter.  This
  will determine which [Twilio] phone number will be used to send the
  text.
* `dry_run` can be set to `True` if you want to do a "dry run" of the
  SMS sending process.  You would use this if you wanted to make
  sure that all of the variables `send_sms()` needs are defined
  before you actually send the SMS message.  The default is `False`.

When the recipients are [`Individual`]s or [`Person`]s, the
`mobile_number` attribute will be used, but only if it already exists.
Otherwise, the `phone_number` attribute will be used, and sought if it
is not already defined.

Note that [Twilio] expects the phone number to be expressed in [E.164]
format, which includes the [country calling code] (e.g., 1 for the
United States).  However, users do not typically write phone numbers
in such a way.  Therefore, the [`phonenumbers`] package is used to
convert phone numbers to [E.164] based on the applicable country.  If
an [`Individual`] or [`Person`] is the recipient, the `country`
attribute, if it exists, will be used to determine the country.
Otherwise, the [`get_country()`] function is used to determine the
applicable country.  Your interview can use [`set_country()`] in
[`initial`] code to set a default country, or you can set a default on
a server level by setting the [`country` configuration directive].
The country must be specified as a two-letter, capitalized
abbreviation ([ISO 3166-1 alpha-2] format).

`send_sms()` returns `False` if an error prevented the message from
being sent; otherwise it returns `True`.

See the [`twilio` configuration directive] for information about how to configure that `send_sms()` will use.

## <a name="get_sms_session"></a>get_sms_session()

When someone sends a text message to one of your [Twilio] numbers, the
[SMS interface] is invoked.  The interview session is tracked based on
the user's phone number and the [Twilio] number with which the user
interacts.

The function `get_sms_session()` retrieves session information and
returns it in the form of a [Python dictionary] with the following
keys:

* `yaml_filename` - the name of the interview; e.g.,
  `docassemble.demo:data/questions/questions.yml`.
* `uid` - the session ID
* `secret` - the encryption key for decrypting the interview answers
* `encrypted` - a `True` or `False` value indicating whether the
interview answers are encrypted.
* `email` - the e-mail address of the user.  If the user is not
  authenticated, this is `None`.  Note that authentication of [SMS]
  users is only possible if the interview session is started with
  [`initiate_sms_session()`].

The `get_sms_session()` functions takes an optional keyword argument
`config`, which indicates a section of the [`twilio`] configuration
that should be used.  A single [SMS] user can have multiple sessions
with the [SMS interface] if there is
[more than one `twilio` configuration directive].

## <a name="initiate_sms_session"></a>initiate_sms_session()

The `initiate_sms_session()` function is used to bring someone into an
interview using the [SMS interface].

In its simplest form, `initiate_sms_session("202-555-1212")` will send
an [SMS] message to 202-555-1212, where the body of the message is the
current question in the interview.

The following optional keyword arguments alter the way the function
works:

* `yaml_filename` - this controls which interview the [SMS] user will
  be placed into.  If `yaml_filename` is not specified, the current
  interview will be used.
* `email` - this controls the identity of the [SMS] user in
  [user login system], which may affect the interview questions that
  the [SMS] user sees.  If `email` is not specified, the [SMS] user
  will have the same identity as the user who was using the interview
  when the call to `initiate_sms_session()` was made.
* `new` - this controls whether the [SMS] user will join an ongoing
  interview session or start a fresh session.  Set this to `True` if
  you want the [SMS] user to start a fresh session.  If `new` is not
  specified, the [SMS] user will join the session that was ongoing
  when the call to `initiate_sms_session()` was made.
* `send` - this controls whether the invitation message should be sent
  or not.  If `send` is not specified, the message will be sent.  Set
  this to `False` to suppress sending the message.  If `send` is
  `False`, the [SMS] session will still be created.  The fact that the
  session is created means that if an [SMS] message is received from
  the given phone number, the [SMS] user will receive a response as if
  the interview session had already been started.  The user's initial
  message will not be interpreted as a choice of an interview from the
  `dispatch` section of the [`twilio`] configuration.
* `config` - this controls which [Twilio] phone number is used for
  communication.  You would only need to use this if you have more
  than [more than one `twilio` configuration directive] set up in your
  [configuration].

If you are not using `new=True`, note that there may be a delay
between the time the message is sent to the [SMS] user and the time
the [SMS] user sees the message and responds.  The [SMS] user will
join the interview at whatever state the interview session is in at
the time the [SMS] user responds.  **docassemble** does not make a
copy of the interview state when the call to `initiate_sms_session()`
is made.

Here is an example interview that solicits input through [SMS].

{% highlight yaml %}
mandatory: True
code: |
  if interface() == 'sms':
    how_many_apples
    all_done_sms
  if ok_to_initiate and session_initiated:
    all_done_web
---
question: |
  How many apples are there?
fields:
  - no label: how_many_apples
    datatype: integer
---
sets: all_done_sms
question: |
  Thank you!
---
question: |
  What phone number should be used?
fields:
  Phone Number: phone_number
---
question: |
  Ready to send a message to
  ${ phone_number }.
field: ok_to_initiate
---
code: |
  initiate_sms_session(phone_number)
  session_initiated = True
---
sets: all_done_web
question: |
  All done.
subquestion: |
  % if defined('how_many_apples'):
  Visitor said there are ${ how_many_apples } apples.
  % else:
  We have not heard from the visitor yet.
  % endif
buttons:
  - Check: refresh
{% endhighlight %}

## <a name="terminate_sms_session"></a>terminate_sms_session()

The `terminate_sms_session()` function will terminate the current
session, if any, for a given phone number.

{% highlight python %}
terminate_sms_session("202-555-1212")
{% endhighlight %}

After the above code executes, then if a message is received from
202-555-1212, it will be treated as a selection of an interview from
the `dispatch` section of the [`twilio`] configuration.  If the [SMS]
user had been in the middle of an interview session, the user will not
be able to get back to that session again.

# <a name="storage"></a>Storing data

## <a name="redis"></a>With Redis

If you do not know what a [Redis] server is, skip this section!

The [background processes] feature of **docassemble** depends on a
[Redis] server being available.  The server is also used to facilitate
[live chat].

Interview developers may want to make use of the [Redis] server for
purposes of storing information across users of a particular
interview, keeping usage statistics, or other purposes.

{% include side-by-side.html demo="redis" %}

To use the [Redis] server, use an [`objects`] section to create an
object of type [`DARedis`].  This object can now be used to
communicate with the redis server, much as though it had been created
by calling `redis.StrictRedis()`.

## <a name="dastore"></a>With SQL

Since [Redis] is an [in-memory database], it is not appropriate for
long-term storage or for the storage of large amounts of data.

An alternative is to store data in SQL.  **docassemble** provides
an object called [`DAStore`] that is similar to [`DARedis`], except it
uses SQL instead of [Redis], and it supports encryption.

{% include side-by-side.html demo="dastore" %}

In the above example, the user's preferences are stored in the
database using a key that is specific to the user.  The first time the
user uses the interview, the user is asked for their favorite fruit.
If the user restarts the interview (which permanently erases the
interview answers), the user's favorite fruit will be retrieved from
the `DAStore`, and it will not need to be asked of the user.  The
object stored in the database is a [`DAObject`], and the favorite
fruit is an attribute of that object.  In the database, the object is
stored under key called `prefs`.  This key is specific to the user, so
that each user will have their own personal `prefs` entry in the
database.

For more information, see the [`DAStore`] documentation.

### <a name="sql">write_record(), read_records(), and delete_record()</a>

There are also three functions, `write_record()`, `read_records()`, and
`delete_record()`, for managing data in SQL.  These functions are
useful when you want to store a list of one or more "records" under a
single "key."  Encryption is not used.

{% include side-by-side.html demo="database_storage" %}

<a name="write_record"></a>When you call `write_record(key, data)`,
the variable `data` is stored in a SQL database.  The function returns
the integer unique ID for the record.  The `data` variable can be any
type of data, such as a number, some text, an [object], a
[Python dictionary], or something else.  The only limitation is that
the information in the variable needs to be able to be [pickled].

<a name="read_records"></a>When you call `read_records(key)`, you will
retrieve all of the records that had been stored using that `key`.
The function returns a [Python dictionary] where the keys are integers
representing the unique ID of the record.

<a name="delete_record"></a>You can delete records by calling
`delete_record(key, id)` where `key` is the key under which the record
was saved and `id` is the unique ID integer of the record.

Note that all interviews on the server will have access to the data
stored with `write_record()`, and the data are not encrypted on the
server.  It is important to choose your `key` names wisely because if
you use a simple name like `mydata`, another interview developer might
have chosen the same key, and then your data will become intermingled.
It is a good idea to include your interview package name in the `key`
names you choose.

**docassemble** will attempt to sanitize data you pass to
`write_record()` by converting any item that cannot be [pickled] to
`None`.

### <a name="sql example"></a>Example of using stored objects with write_record()

Suppose you have an interview that your user might complete several
times for different situations, but you do not want the user to have
to re-enter the same information more than once.  You can use
[`read_records()`] and [`write_record()`] to accomplish this.

Here is an example:

{% highlight yaml %}
metadata:
  title: Side of the bed
---
code: |
  user_key = 'workers_comp_user:' + user_info().email
---
objects:
  - user: Individual
---
code: |
  saved_records = read_records(user_key)
  for id in saved_records:
    user = saved_records[id]
---
mandatory: True
code: |
  if not user_logged_in():
    command('leave', url=url_of('login', next=interview_url()))
  first_part_finished
  user_info_saved
  interview_finished
---
question: |
  Thanks for all that information!
subquestion: |
  We now know that your name is
  ${ user },
  your favorite fruit is
  ${ user.favorite_fruit },
  and you woke up on the
  ${ side_of_bed }
  side of the bed this morning.
field: first_part_finished
---
question: |
  What is your name?
fields:
  - First name: user.name.first
  - Last name: user.name.last
---
question: |
  What is your favorite fruit?
fields:
  - Fruit: user.favorite_fruit
---
question: |
  On which side of the bed did you
  wake up this morning, ${ user }?
field: side_of_bed
choices:
  Right side: right
  Wrong side: wrong
---
event: interview_finished
question: |
  Ok, go eat some
  ${ user.favorite_fruit },
  ${ user }.
subquestion: |
  Perhaps you will wake up on
  the ${ side_of_bed } side of
  the bed tomorrow, too.
buttons:
  - Exit: leave
    url: ${ url_of('dispatch') }
---
code: |
  for id in read_records(user_key):
    delete_record(user_key, id)
  write_record(user_key, user)
  set_parts(title=capitalize(side_of_bed) + " side of the bed")
  session_tags().add(side_of_bed)
  user_info_saved = True
{% endhighlight %}

The first time the user goes through the interview, the interview will
ask for the user's name and favorite fruit.  The second time the user
goes through the interview, the interview does not ask for the name
and favorite fruit, because it already knows the information -- even
though the user's second interview is a separate session with a
separate, isolated set of interview answers.

The interview accomplishes this using [`write_record()`] and
[`read_records()`].

When the interview is done asking questions, it calls
[`write_record()`] to store the object `user` to SQL.  It records this
information using a unique "key" that is based on the e-mail address
of the user (e.g., `workers_comp_user:fred@example.com`).  To get the
e-mail address of the user, the interview requires the user to log in,
and uses `user_info().email` to get the e-mail address.

Whenever the interview starts, the interview first checks to see if
anything has been stored under the unique "key."  If there is
something stored, then the `user` object is retrieved from storage.
If there is nothing stored, `user` is initialized as an object of type
[`Individual`].

Note that the timing of when `user` is stored is important.  The
[`write_record()`] function will store a "snapshot" of the object, so
if `user` is stored before the necessary information (name and
favorite fruit) have been gathered, then the interview will not work
as intended.

Here is the code that initializes the `user` object:

{% highlight yaml %}
objects:
  - user: Individual
---
code: |
  saved_records = read_records(user_key)
  for id in saved_records:
    user = saved_records[id]
{% endhighlight %}

Note that neither of these blocks is [`mandatory`]; when the interview
needs to know the definition of `user`, it will try the [`code`] block
first (because it is later in the [YAML]).  If `user` is still
undefined, the interview will "fall back" to trying the `objects`
block, which will initialize a fresh object of class [`Individual`].

The [`read_records()`] function always returns a [Python dictionary],
because you can store more than one record under a single key.  But in
this interview, we are only storing one record under the key
`user_key`.

The interview logic starts with forcing the user to log in:

{% highlight yaml %}
mandatory: True
code: |
  if not user_logged_in():
    command('leave', url=url_of('login', next=interview_url()))
  first_part_finished
  user_info_saved
  interview_finished
{% endhighlight %}

The [`command()`] line redirects the user to the sign-in page, but
tells the sign-in page that when the user logs in, the user
should be directed back to the same interview.

The reference to `user_info_saved` before `interview_finished` ensures
that before the user sees the last screen of the interview, some code
is run that saves the `user` object to storage.

The [`code`] block that defines `user_info_saved` looks like this:

{% highlight yaml %}
code: |
  for id in read_records(user_key):
    delete_record(user_key, id)
  write_record(user_key, user)
  set_parts(title=capitalize(side_of_bed) + " side of the bed")
  session_tags().add(side_of_bed)
  user_info_saved = True
{% endhighlight %}

First, the code deletes any existing records under `user_key`, and
then stores the `user` object.  This means that even if the interview
session started off by retrieving `user` from storage, it will save a
new copy of the `user` object to storage.  Thus, the interview can
make changes to the `user` object if necessary, and those changes will
be saved.

This interview also uses [`set_parts()`] and [`session_tags()`] to
change the title and tags of the interview, so that when the user goes
to "My Interviews," the user will see a different title and different
tags based on their interview answers.  Using a technique like this
might help your users in case your users want to resume their
interview session.

Now, suppose you have a variety of interviews, all of which relate to
the same topic (e.g., workers compensation).  If any one of these
interviews is the first interview that the user uses, you want the
basic questions (name, favorite fruit) to be asked.  And if the user
launches another interview, you don't want to re-ask those basic
questions.

You can do this using interviews like the above, but each interview
would need to contain the same blocks that force the user to log in,
retrieves `user` from storage, saves `user` to storage at the end,
etc.  It is inconvenient to maintain the same code in several
different files.

You can avoid this problem by using [`include`].  You can create a
"common" [YAML] file called [`wc_common.yml`], which contains the
following:

{% highlight yaml %}
objects:
  - user: Individual
---
code: |
  user_key = 'workers_comp_user:' + user_info().email
---
code: |
  saved_records = read_records(user_key)
  for id in saved_records:
    user = saved_records[id]
---
initial: True
code: |
  if not user_logged_in():
    command('leave', url=url_of('login', next=interview_url()))
---
question: |
  What is your name?
fields:
  - First name: user.name.first
  - Last name: user.name.last
---
question: |
  What is your favorite fruit?
fields:
  - Fruit: user.favorite_fruit
---
code: |
  for id in read_records(user_key):
    delete_record(user_key, id)
  write_record(user_key, user)
  user_info_saved = True
{% endhighlight %}

Then your actual interview file will just incorporate this by
reference.  For example, you could have a file called
[`wc_side_of_bed.yml`], which looks like this:

{% highlight yaml %}
metadata:
  title: Side of the bed
---
include:
  - wc_common.yml
---
mandatory: True
code: |
  first_part_finished
  user_info_saved
  interview_tagged
  interview_finished
---
question: |
  Thanks for all that information!
subquestion: |
  We now know that your name is
  ${ user },
  your favorite fruit is
  ${ user.favorite_fruit },
  and you woke up on the
  ${ side_of_bed }
  side of the bed this morning.
field: first_part_finished
---
question: |
  On which side of the bed did you
  wake up this morning, ${ user }?
field: side_of_bed
choices:
  Right side: right
  Wrong side: wrong
---
event: interview_finished
question: |
  Ok, go eat some
  ${ user.favorite_fruit },
  ${ user }.
subquestion: |
  Perhaps you will wake up on
  the ${ side_of_bed } side of
  the bed tomorrow, too.
buttons:
  - Exit: leave
    url: ${ url_of('dispatch') }
---
code: |
  set_parts(title=capitalize(side_of_bed) + " side of the bed")
  session_tags().add(side_of_bed)
  interview_tagged = True
{% endhighlight %}

You could then create other [YAML] files that follow the same pattern,
all of which [`include`] the [`wc_common.yml`] file.  Any time you
wanted to change a "common" question, you would only need to make the
change in one place.

## <a name="store_variables_snapshot"></a>Storing interview answer snapshots in unencrypted JSON format in SQL

If you want to "run reports" on the interview answers of multiple
sessions, you can use `store_variables_snapshot()` in your interview
logic to save an unencrypted copy of the interview answers in [JSON]
format to a SQL table.  If you use [PostgreSQL], you can
conveniently run SQL queries on the contents of interview answers.
Using [PostgreSQL] syntax for working with [JSON] data, you can
extract, filter, and order by specific variables embedded in the
interview answers of sessions.

Here is an example of an interview that asks the user a question and
then saves the interview answers in [JSON] format to a SQL table.  Then,
using a function `analyze()` that was defined in the
[`read_snapshot.py`] module, the final question of the interview reads
the interview answers of all sessions that have been completed on this
interview on the server and summarizes the results.

{% include demo-side-by-side.html demo="snapshot" %}

The contents of the [`read_snapshot.py`] module are as follows.

{% highlight python %}
from docassemble.base.util import variables_snapshot_connection, user_info

__all__ = ['analyze']

def analyze():
  conn = variables_snapshot_connection()
  cur = conn.cursor()
  cur.execute("select data->>'favorite_fruit' from jsonstorage where filename='" + user_info().filename + "'")
  counts = dict()
  for record in cur.fetchall():
    fruit = record[0].lower()
    if fruit not in counts:
      counts[fruit] = 0
    counts[fruit] += 1
  conn.close()
  return counts
{% endhighlight %}

The `analyze()` function imports the `variables_snapshot_connection()`
function from [`docassemble.base.util`] and calls it in order to get a
SQL connection object.  If your database is [PostgreSQL], this will be
a [`psycopg2`] connection object.  Note that
`variables_snapshot_connection()` is not available for use inside
interview [YAML] the way `store_variables_snapshot()` is.  If you
tried to call `variables_snapshot_connection()` from inside of a
[`code`] block, you would get an error.  Always call
`variables_snapshot_connection()` from a function or method defined in
a [Python module].

When using [PostgreSQL], the data type used for the [JSON] `data` is
[JSONB].  This allows for the use of the special [PostgreSQL]
operators `->` and `->>` to efficiently probe inside the data
structure.  For more information on how these operators work, see the
documentation for the [JSONB] data type.

Note that the [JSON] snapshots created by `store_variables_snapshot()`
are tied to the underlying interview session.  When the session is
deleted, the snapshot is deleted.  (However, see the discussion of
`persistent` below.)

If you call `store_variables_snapshot()` multiple times, each time you
will overwrite the stored [JSON] snapshot of the interview answers.
(However, see the discussion of `key` below.)

Note that the snapshot is a copy of the interview answers, not the
interview answers themselves.  The [JSON] snapshot does not
automatically synchronize with the current state of the interview
answers.  In **docassemble**, the interview answers are stored in a
Python-specific object format, not [JSON]; it is not possible for
[JSON] to serve as the format for **docassemble** interview answers
because **docassemble** allows interview answers to contain complex
data structures containing [Python] objects and object references.
The conversion from Python objects to [JSON] is one-way, and is a
simplification; Python objects cannot be recreated from [JSON].

Because of this, the `store_variables_snapshot()` is not as useful as
other data storage options for many applications.  You should use
`store_variables_snapshot()` if you want to run SQL queries on
multiple sessions belonging to different users.  You should use other
methods, such as [`DAStore`], for storing reusable global data.

The `store_variables_snapshot()` accepts the optional keyword
parameters, `key`, `persistent`, `include_internal`, and `data`.

If you want to save multiple snapshots during the course of the
interview, you can set `key` when you call
`store_variables_snapshot()`.  For example, you might want to save a
snapshot after the user completes an initial section of an interview,
and save another snapshot after the user completes the entire
interview.  You could write:

{% highlight yaml %}
mandatory: True
code: |
  intro_section_completed
  store_variables_snapshot(key='intro')
---
mandatory: True
code: |
  final_section_completed
  store_variables_snapshot(key='final')
{% endhighlight %}

This will allow you to run queries on two populations of users: a
large population of users who started but may not have finished, and a
smaller population of users who finished.  The `key` is similar to a
key in [Redis]; it uniquely identifies a snapshot within the interview
session.

If you do not want the interview snapshot (or snapshots) to be deleted
when the session is deleted, call
`store_variables_snapshot(persistent=True)`.  Note that this means
that if a user restarts an interview session, the user may have
multiple sessions in [JSON] data table.

By default, `store_variables_snapshot()` does not save the "internal"
portion of the interview answers; this is a data structure under the
`_internal` key that **docassemble** uses internally.  (The data
structure is not documented and the design may change at any time, but
you are welcome to use it at your own risk.)  If you want to include
the `_internal` data in the [JSON] snapshot, call
`store_variables_snapshot()` with `include_internal=True`.

`store_variables_snapshot()` can store something other than the
interview answers if you set the optional keyword parameter `data`.
You can set `data` to any Python data structure, and it will be
serialized to [JSON] and stored in place of the data structure
representing the interview answers.

While the example above shows how the [JSON] data table can be queried
from within an interview, you will probably find that it is easiest to
query the data tables from outside of **docassemble**.  You can set up
your server's [`db`] configuration to use an external SQL database,
and then query the `jsonstorage` table in that database using the
credentials for the **docassemble** SQL database.  However, there are
many other tables in this database, and it may be preferable to use a
separate database for [JSON] snapshots.  If you define a [`variables
snapshot db`] in your [Configuration], a `jsonstorage` table will be
created in the referenced database, and `store_variables_snapshot()`
and `variables_snapshot_connection()` will use this database instead
of the default **docassemble** database.

The columns in the `jsonstorage` table are as follows.

* `id` - a unique integer ID for the row
* `filename` - the YAML filename of the interview
* `key` - the session ID of the session
* `data` - the JSON data
* `tags` - the value of the `key` you passed to
  `store_variables_snapshot()` (not to be confused with the column
  `key`)
* `modtime` - the last time the row was modified
* `persistent` - whether the row should be preserved when the session
  is deleted.

Note that there is no [API] for querying the [JSON] data.  The best
way to access the data is by using a [PostgreSQL] client because it
provides an extremely powerful and flexible query language.

Note that unlike [`DAStore`], `store_variables_snapshot()` cannot use
server-side encryption.  If the interview itself uses server-side
encryption, calling `store_variables_snapshot()` will effectively
defeat the purpose of server-side encryption by storing user data in a
way that would allow anyone with shell access on the server to read
the data.

### Advanced SQL storage

Though the data are stored on a SQL server, you cannot use SQL queries
to retrieve data stored by [`write_record()`]; you can only use
[`read_records()`] to retrieve data.

If you want to use the full power of SQL in your interviews, you can
write a module that does something like this:

{% highlight python %}
from docassemble.base.util import get_config
import psycopg2

def get_conn():
    dbconfig = get_config('db')
    return psycopg2.connect(database=dbconfig.get('name'),
                            user=dbconfig.get('user'),
                            password=dbconfig.get('password'),
                            host=dbconfig.get('host'),
                            port=dbconfig.get('port'))
def some_function(id, thing):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("update foo set bar=%s where id=%s", (thing, id))
    conn.commit()
    cur.close()
{% endhighlight %}

This assumes the [`db`] configuration refers to a [PostgreSQL]
database.  If you connect to the database with the credentials from
[`db`], you have the power to create and drop tables.

# <a name="docx"></a>Functions for working with DOCX templates

## <a name="include_docx_template"></a>include_docx_template()

The `include_docx_template()` function can be called from within a
[DOCX template file] in order to include the contents of another
DOCX file within the template being assembled.

{% include demo-side-by-side.html demo="subdocument" %}

The file [`main_document.docx`] looks like this:

![include_docx_template]({{ site.baseurl }}/img/include_docx_template.png)

The file [`sub_document.docx`] looks like this:

![include_docx_template_sub]({{ site.baseurl }}/img/include_docx_template_sub.png)

Note that it is important to use the `p` form of [Jinja2] markup, or
else the contents of the included document will not be visible.  The
template text must also be by itself on a line, and the
`include_docx_template()` function must be by itself within a [Jinja2]
`p` tag, and not combined with the `+` operator with any other text.

The filename that you give to `include_docx_template()` must be a file
that exists in the templates folder of the current package.  You can
also refer to templates in other packages using a full package
filename reference, such as
`docassemble.demo:data/templates/sub_document.docx`.  You can also
give the function a [`DAFile`] or a [`DAFileList`] object.

The `include_docx_template()` function also accepts optional keyword
parameters.  These values become variables that you can use in
[Jinja2] inside the DOCX file you are including.  This can be useful
if you have a "sub-document" that you want to include multiple times,
but you want to use different variable values each time you include
the "sub-document."

Here is an example:

{% include demo-side-by-side.html demo="subdoc-params" %}

The file [`main_doc_params.docx`] looks like this:

![include_docx_template_param]({{ site.baseurl }}/img/include_docx_template_param.png)

The file [`sub_doc_params.docx`] looks like this:

![include_docx_template_param_sub]({{ site.baseurl }}/img/include_docx_template_param_sub.png)

In this example, the variables `grantor`, `grantee`, and `stuff` are
set by the keyword parameters of the `include_docx_template()`
function.  Note that in your sub-document you can still refer to
ordinary interview variables in addition to variables created by
keyword parameters; in this example, the sub-document references the
variable `planet`, which is set by the interview.

The effect of including keyword parameters is to insert [Jinja2] `set`
commands at the start of the included document.  For example, the
first call to `include_docx_template()` might result in the following:

{% highlight text %}
{% raw %}{%p set grantor = father %}{% endraw %}
{% raw %}{%p set grantee = mother %}{% endraw %}
{% raw %}{%p set stuff = 'toadstools' %}{% endraw %}
{% endhighlight %}

Nobody ever actually sees these `set` statements; they are inserted
and evaluated behind the scenes.

Note that if the values of any of your keyword arguments are objects
other than [`DAObject`]s, they will be converted to their [`repr()`]
representation _before being included_.  This means that there may be
some objects that you cannot pass through to your sub-documents.

When a `docx template file` document contains a call to
`include_docx_template()`, the document is assembled in multiple
"passes."  On the first pass, all of the [Jinja2] is evaluated.  The
effect of `include_docx_template()` is to insert any `set` statements
based on keyword parameters, along the verbatim contents of the file.
Then, on the second pass, any remaining [Jinja2] code is evaluated;
this would be any [Jinja2] code contained in sub-documents, as well as
the `set` statements included by `include_docx_template()`.  If any of
the sub-documents contain calls to `include_docx_template()`, a third
pass will be done, and so on, until the document is fully assembled.
(The number of passes is limited to 10 in order to protect against
accidentally creating an infinite loop of document inclusion.)

## <a name="raw"></a>raw()

This function is only used in the context of an [`attachments`] block
that uses a [`docx template file`] and values are passed to the DOCX
template using the `code` or `field code` methods.

Normally, all values that you transfer to a DOCX template with `code`
or `field code` are converted so that they display appropriately in
your DOCX file.  For example, if the value is a [`DAFile`] graphics
image, it will be displayed in the DOCX file as an image.  Or, if the
value contains [document markup] codes that indicate line breaks,
these will display as actual line breaks in the DOCX file, rather
than as codes like `[BR]`.

However, if your DOCX file uses advanced template features, such as
for loops, this conversion might cause problems for you.  By passing a
value `val` as `raw(val)`, you will ensure that the template sees the
original value of `val`, not a converted value.

For example, suppose you have a variable `fruit_list` that is defined
as a [`DAList`] with items `['apples', 'oranges']`, and you pass it to
a DOCX template as follows.

{% highlight yaml %}
event: document_shown
question: |
  Here is the document.
attachment:
  docx template file: letter_template.docx
  field code:
    list_of_fruit: fruit_list
{% endhighlight %}

This will work as intended if your template uses `list_of_fruit` in a
context like:

{% highlight text %}
make sure to bring {% raw %}{{ list_of_fruit }}{% endraw %} to the party
{% endhighlight %}

This will result in:

> make sure to bring apples and oranges to the party

When the [`DAList`] is converted to text, the [`.comma_and_list()`]
method is automatically applied to make the data structure
"presentable."

However, suppose you wanted to write:

{% highlight text %}
{% raw %}{%p for fruit in list_of_fruit: %}
Don't forget to bring {{ fruit }}!
{%p endfor %}{% endraw %}
{% endhighlight %}

In this case, the variable `list_of_fruit` is a literal piece of text,
`apples and oranges`.  The `for` loop will loop over each character,
and you will get:

> Don't forget to bring a!
> Don't forget to bring p!
> Don't forget to bring p!
> Don't forget to bring l!

and so on.  That is certainly not what you want!

You can prevent the conversion of `fruit_list` into text by wrapping
it in the `raw()` function, as follows:

{% highlight yaml %}
event: document_shown
question: |
  Here is the document.
attachment:
  docx template file: letter_template.docx
  field code:
    list_of_fruit: raw(fruit_list)
{% endhighlight %}

Now, the resulting DOCX file will contain:

> Don't forget to bring apples!
> Don't forget to bring oranges!

Note that another way to pass "raw" values to a DOCX template is to
use a list of [`raw field variables`].

Moreover, the easiest way to pass "raw" values is to omit `field`,
`field code`, `field variables`, `code`, and `raw field variables`
entirely, so that your DOCX file is [assembled] using your full set
of interview variables.

## <a name="assemble_docx"></a>assemble_docx()

The `assemble_docx()` function does what an `attachment` does, except
it is triggered by Python code and it does not create a `DAFile` in
the document storage.

This is an advanced function, so in the vast majority of
circumstances, you should instead use an [`attachments`] block.

The `assemble_docx()` takes a single positional parameter, which needs
to be a file.  The format is flexible; it can be a [`DAFile`] or
related object, or a template reference like
`'data/templates/mytemplate.docx'`.

The function returns a path to a temporary file in DOCX format,
representing the assembled document.  This file needs to be processed
right away, because it is not guaranteed to persist across HTTP
requests.

It also takes the following optional keyword parameters:

* `fields`: this can be set to a [Python dictionary] in which the keys
  are variable names and the values are the values of those variables.
  This allows you to superimpose particular variables on top of the
  interview answers for purposes of document assembly.  The values are
  not saved in the interview answers.  The keys can only be simple
  [Python] variable names (`favorite_fruit`, `type_of_document`),
  not indices (`fruits[0]`, `favorite['fruit']`) or attributes
  (`favorite_vegetable.color`, `apple.seeds`).
* `output_path`: if you want the function to save a file to a
  particular path instead of returning a path to a temporary file, set
  `output_path` to the path to which you want `assemble_docx` to
  write.
* `output_format`: if you want the assembled document to be converted
  to PDF, set `output_format` to `'pdf'`.  If you want it assembled to
  [Markdown], set `output_format` to `'md'`.
* `pdf_options`: if you are setting `output_format` to `'pdf'`, you
  can also set options for the way the PDF conversion is conducted by
  setting `pdf_options` to a [Python dictionary] with one or more of
  the following keys: `pdfa` (boolean for whether PDF/A should be
  created, `password` (a password for securing the PDF), `update_refs`
  (if you want references to be updated in the DOCX file before
  conversion), `tagged` (if you want LibreOffice to produce a tagged
  PDF).  For more information about these options, see the [Documents]
  section.
* `return_content`: if you want the contents of the file to be
  returned, instead of a file path, set `return_content` to `True`.

Here is an example of an interview that uses `assembled_docx()` in a
contract assembly interview.  All of the clauses of the contract are
in the [`contract.docx`] DOCX template file, but they are written in
such a way that they can be extracted from the DOCX file using
`assembled_docx()` and converted into [Markdown].  Extracting clauses
in [Markdown] format is useful because:

* It allows you to manage your contract clauses as a list of
  paragraphs, separated from the logic about whether the clauses
  should be included in the contract or not.
* It allows you to draft your contract clauses in a DOCX file, which
  is the ideal format for writing, especially when formatting is used.
* It allows you to show the text of the contract clauses in the web
  browser, without needing to maintain the content for the contract
  clauses in more than one place.
* It allows you to give the user an opportunity to edit contract
  clauses during the interview and then insert the clauses into the
  DOCX file with formatting preserved (at least as far as the
  formatting translates to and from [Markdown]).

{% include demo-side-by-side.html demo="clauses" %}

The [`contract.docx`] DOCX template is used for two very different
purposes:

1. Assembling a document containing a single clause.
2. Assembling the contract itself.

The template uses the variable `clause` to determine which clause to
assemble, or whether to assemble the contract itself.  In the
interview answers, `clause` is set to `None`, but the `fields`
parameter passed to `assemble_docx()` will override that value for
purposes of assembling a single clause.

The DOCX file uses the `macro` feature of [Jinja2].  The DOCX template
could be written without the use of `macro` definitions, but they are
useful so that if you want, you can insert clauses into the contract
without converting them to [Markdown] and back again.

# <a name="yourown"></a>Writing your own functions

There are two ways that you can write your own functions in
**docassemble**.

The first way is to use the `<%def></%def>` feature of [Mako] in order
to use "functions" in your templates.  These are not true
[Python functions] because they are based around [Mako] templates, but
they are similar to [Python functions].  The `<%def></%def>` feature
is documented on the [Mako web site].  **docassemble**'s [`def` block]
makes it easy to re-use [`def` blocks] in your interviews.

The second way, which is usually more elegant, is to write a
[Python module] containing a definition of a [Python function], and
then include that module in your interview using the
[`modules` block].  This allows you to use your function both in
[Mako] templates and in [`code`] blocks.

Here is a brief tutorial on how to write a function `plus_one()` that
takes a number and returns the number plus one.  For example,
`plus_one(3)` should return `4`.

First, go to the [Playground].  (This requires that you have a
developer account on the server.)

Then, go to the [modules folder] of the [Playground].

![modules folder]({{ site.baseurl }}/img/docassemble-modules.png)

Then, type the following [Python] code into the text box:

{% highlight python %}
def plus_one(number):
  return number + 1
{% endhighlight %}

The screen should look like this:

![sample function]({{ site.baseurl }}/img/docassemble-sample-function.png)

Then, press the "Save" button at the bottom of the screen.  This will
create a [Python module] called `test`.  (The text file is called
`test.py` in the [modules folder] because files containing Python code
have the extension `.py` in their file names.  Within [Python], you
refer to modules using the file name without the file extension.)

Then click the "Back to Playground" button to leave the "Modules"
folder.

Now, you can use the `plus_one()` function in your interviews by
doing something like:

{% include side-by-side.html demo="sample-function" %}

The `.` in front of the module name is [Python]'s way of referring to
modules that are in the current package.  If you put your module
within a [package] called `docassemble.simplemath`, then you could
write, instead:

{% highlight yaml %}
---
modules:
  - docassemble.simplemath.test
---
{% endhighlight %}

## <a name="jinja2"></a>A caveat regarding functions called from docx templates

If you write your own functions and they are called from markup inside
`docx template file` functions, beware that [Jinja2] will send your
functions objects in place of arguments when the arguments are
undefined.  For example, consider a a template that contains:

{% highlight text %}
{% raw %}
{%p if claiming_damages %}
You owe me {{ currency(compute_damages(amount_owed, demand_interest)) }}.
{% endif %}
{% endraw %}
{% endhighlight %}

If `demand_interest` is undefined, and `claiming_damages` is true,
**docassemble** should seek out a block that defines `amount_owed`.
However, when [Jinja2] sees that `demand_interest` is undefined, it
creates an object `amount_owed` of the class
`jinja2.runtime.Undefined`.  If the only way `compute_damages()` acts
upon `demand_interest` is by evaluating the conditional expression
`demand_interest is True`, the expression will evaluate to `False`,
even though your interview has not actually defined
`demand_interest`.

This is different to how [Python] normally works.  Normally, if the
code is `compute_damages(amount_owed, demand_interest)` and
`demand_interest` is undefined, a [`NameError`] is raised before
`compute_damages()` is even called.

The behavior of [Jinja2] might not be a problem if your function does
arithmetic with the variable, calls `unicode()` on the variable or
does other things with the variable that access its "value"; in those
situations, an exception will be raised and **docassemble** will seek
out a definition of the undefined variable.  However, if your function
uses [`try`/`except`] on the operations, this exception may not be
passed on to **docassemble**.

To get around this problem, you can include the following in your
module file:

{% highlight python %}
from docassemble.base.util import ensure_definition
{% endhighlight %}

Then at the start of every function that might be called from
[Jinja2], run the function's parameters through `ensure_definition`:

{% highlight python %}
def compute_damages(amount_owed, demand_interest):
    ensure_definition(amount_owed, demand_interest)
    ...
{% endhighlight %}

The `ensure_definition()` function checks to see if each of its
arguments (both positional and named) are `Undefined`, and if so, it
raises an exception that will cause **docassemble** to seek out the
appropriate definition.

# <a name="google sheets example"></a>Example module: using Google Sheets

This section explains an example of something you might do with a
module: integrate with [Google Sheets].

In order for your site to communicate with [Google Sheets], you will
need to create an account on the [Google Developers Console] and
create an "app."  Within this app, you will need to create a "service
account."  (More information is available on the internet about what a
"service account" is and how you create one.)  When you create the
service account, you will be provided with "credentials."  Download
the [JSON] (not p12) credential file for the service account.  Also
make a note of the e-mail address of the service account.

Within the [Google Developers Console], enable the [Google Drive API]
and the [Google Sheets API].

Go to [Google Sheets], pick a spreadsheet that you want to use, and
share it with the e-mail address of the service account, just like you
were sharing it with a real person.  (When you share the spreadsheet
with this e-mail address, you will get an e-mail notification from
Google about an undeliverable e-mail.  This is because Google will try
to e-mail the service account, but the service account does not
actually have an e-mail account.  To avoid getting this e-mail, click
the "Advanced" link on the sharing screen and uncheck "Notify people.")

Go to the [Configuration] and set the [`service account credentials`]
subdirective under the [`google`] directive.  Set it to the contents of
the [JSON] file you downloaded.  The directive will look something
like this:

{% highlight yaml %}
google:
  service account credentials: |
    {
      "type": "service_account",
      "project_id": "redacted",
      "private_key_id": "redacted",
      "private_key": "-----BEGIN PRIVATE KEY-----REDACTED-----END PRIVATE KEY-----\n",
      "client_email": "googledocs@redacted.iam.gserviceaccount.com",
      "client_id": "redacted",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://accounts.google.com/o/oauth2/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/googledocs%40redacted.iam.gserviceaccount.com"
    }
{% endhighlight %}

Next, go to the [modules folder] of the [Playground] and add a new
module called `google_sheets.py`.  Set the contents to:

{% highlight python %}
import gspread
import json
from docassemble.base.util import get_config
from oauth2client.service_account import ServiceAccountCredentials
credential_info = json.loads(get_config('google').get('service account credentials'), strict=False)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
__all__ = ['read_sheet']

def read_sheet(sheet_name, worksheet_index):
  creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
  client = gspread.authorize(creds)
  sheet = client.open(sheet_name).get_worksheet(worksheet_index)
  return sheet.get_all_records()
{% endhighlight %}

You might need to change the reference to `'google'` and `'service account credentials'`
to something else if you used a different name for the [JSON] crededials
in your [Configuration].

Go to the [Playground] and create an interview that references the
`google_sheets` module and the `read_sheet` function.

{% highlight yaml %}
modules:
  - .google_sheets
---
mandatory: True
question: |
  List of countries
subquestion: |
  % for row in read_sheet("Country Data", 0):
  * ${ row['name'] } is at ${ row['longitude'] } longitude.
  % endfor
{% endhighlight %}

In this example, a [Google Sheet] called "Country Data" has been
shared with the "service account" that owns the credentials in the
`service account credentials` subdirective under the `google`
directive.  The first worksheet in the spreadsheet (index 0) contains
a table with headings for `name` and `longitude`, among other columns.
The `read_sheet` function returns a list of dictionaries representing
the contents of the table.

For more information on using [Google Sheets] from [Python], see the
documentation for the [gspread] module.

# <a name="google sheets example two"></a>Example module: storing data in a Google Sheet

The following example interview extends the system developed in the
previous section by adding functionality for writing data to the
worksheet.  This interview asks the interviewee some questions
and then stores the results in a [Google Sheet], much like [Google
Forms] would.

{% include demo-side-by-side.html demo="google-sheet" %}

This interview uses a [Google Sheet] called [Fruits and veggies] (you
can view it at that link), which has been shared with the "service
account" referenced in the `service account credentials` subdirective
under the `google` directive in the [Configuration] on the
demo.docassemble.org server.

You can [try out this interview] and then look at the [Fruits and
veggies] spreadsheet to see your answers along with the answers of
other people who have tested the interview.

There is a single [`mandatory`] block in this interview: a [`code`]
block that first requires a definition of
`data_stored_in_google_sheet`, and then seeks a definition of
`final_screen_shown`.

The variable `data_stored_in_google_sheet` is defined by a [`code`]
block that calls `append_to_sheet()`, which is a function defined in
the [`google_sheets` module].  This module is in the same [Python]
package as the interview (`docassemble.demo`).  (The [`google_sheets`
module] is based on the [Python] module described in the previous
section.)

The `append_to_sheet()` function is very similar to the `read_sheet()`
function described in the previous section.

{% highlight python %}
def append_to_sheet(sheet_name, vals, worksheet_index=0):
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).get_worksheet(worksheet_index)
    sheet.append_row(vals)
{% endhighlight %}

There is a handy method in [gspread] called `append_row()`, which adds
a row to the end of a spreadsheet.  If you use a method like this
yourself, please note in [Google Sheets], spreadsheets by default have
several hundred rows, so if you append data to them, you might not see
the data that you have appended unless you scroll all the way down.
It is recommended that you delete all of these extraneous rows before
you use [gspread]'s `append_row()` method to write to a spreadsheet.

# <a name="javascript"></a>Javascript functions

If you know how to program in [JavaScript], you can include
browser-side code in your interviews using [`script`], [`html`], and
[`css`] elements within a [`fields`] block, or you can put
[JavaScript] and [CSS]<span></span> [static files] in your [packages]
and bring them into your interview using the [`javascript`] and
[`css`]({{ site.baseurl }}/docs/initial.html) specifiers within a
[`features`] block.

The following [JavaScript] functions are available for your use in
your [JavaScript] code.

## <a name="flash"></a>flash() JavaScript function

The `flash()` function displays a notification at the top of the
screen, using the standard [Bootstrap] notification style.

{% include side-by-side.html demo="flash" %}

The first parameter is the message itself, the second parameter is the
optional priority, and the third parameter is an optional true/false
value indicating whether the existing messages should be removed
before the new message is displayed.

The available priorities are:

<div class="card">
<div class="card-body">
<div class="alert alert-primary">primary</div>
<div class="alert alert-secondary">secondary</div>
<div class="alert alert-success">success</div>
<div class="alert alert-danger">danger</div>
<div class="alert alert-warning">warning</div>
<div class="alert alert-info">info</div>
<div class="alert alert-light">light</div>
<div class="alert alert-dark">dark</div>
</div>
</div>

If no priority is supplied, `'info'` is used.

The `success` message is special because it automatically disappears
after three seconds.

If you only want to clear the messages, you can run
`flash(null, null, true)`.

You can also access this function under the name `da_flash()`, which
can be useful if you are embedding **docassemble** and there is a name
conflict.

## <a name="js_val"></a>val() JavaScript function

If you need the value of one of the HTML inputs on the screen, you can
call `val()`, passing as the sole parameter the variable name of the
field as a string.  The variable name must be written exactly as it
appears in the underlying [`question`].

{% include side-by-side.html demo="val" %}

This function is essential for using the [`js show if`] feature.

Note that `val()` only works with fields that exist on the screen; the
[JavaScript] environment is not aware of the Python environment.  If
you want to pass variable values from Python to JavaScript, see the
[recipe on the topic].

You can also access this function under the name `da_val()`, which can
be useful if you are embedding **docassemble** and there is a name
conflict.

## <a name="js_getField"></a>getField() JavaScript function

The `getField()` function is similar to `val()`, except that instead
of returning the value of the input element, it returns the element
itself.

{% include side-by-side.html demo="getField" %}

You can also access this function under the name `daGetField()`, which
can be useful if you are embedding **docassemble** and there is a name
conflict.

## <a name="js_setField"></a>setField() JavaScript function

The `setField()` function sets the value of a field.  The first
parameter is the the variable name of the field, as a string.  The
second parameter is the value that the variable should have.  The
variable name must be written exactly as it appears in the underlying
[`question`].

{% include side-by-side.html demo="setField" %}

You can also access this function under the name `daSetField()`, which
can be useful if you are embedding **docassemble** and there is a name
conflict.

## <a name="js_getFields"></a>getFields() JavaScript function

The `getFields()` function returns an array of names of the fields on
the screen that can be used with `val()`, `getField()`, and
`setField()`.

{% include side-by-side.html demo="getFields" %}

You can also access this function under the name `daGetFields()`, which
can be useful if you are embedding **docassemble** and there is a name
conflict.

## <a name="js_url_action"></a>url_action() JavaScript function

The `url_action()` function, like its [Python namesake](#url_action),
returns a URL that will run a particular action in the interview.  The
first parameter is the [action] to run, and the second
parameter is an object containing the arguments to provide to the
action (to be read with [`action_argument()`]).

{% include side-by-side.html demo="js_url_action" %}

You can also access this function under the name `da_url_action()`,
which can be useful if you are embedding **docassemble** and there is
a name conflict.

## <a name="js_url_action_perform"></a><a name="js_action_perform"></a>action_perform() JavaScript function

The `action_perform()` function is like
[`url_action()`](#js_url_action), except that instead of returning a
URL that would run the action if accessed, it actually causes the
user's web browser to run the action.

The [JavaScript] function takes two arguments:

1. The [action] to take.  This corresponds with the name of an
   [`event`] in your interview.
2. An object containing arguments to pass to the [action].  In your
   interview, you can use the [`action_argument()`] function to read
   these values.

You can also access this function under the name
`da_action_perform()`, which can be useful if you are embedding
**docassemble** and there is a name conflict.

## <a name="js_url_action_call"></a><a name="js_action_call"></a>action_call() JavaScript function

The `action_call()` function is like
[`url_action()`](#js_url_action), except it makes an [Ajax] call to
the URL and runs a callback function when the server responds to the
request.  In combination with [`json_response()`], this can allow you
to write [JavaScript] code that interacts with "APIs" with your interview.

The [JavaScript] function takes three arguments:

1. The [action] to take.  This corresponds with the name of an
   [`event`] in your interview.
2. An object containing arguments to pass to the [action].  In your
   interview, you can use the [`action_argument()`] function to read
   these values.
3. A callback function that will be run when the [Ajax] call returns.
   This function takes a single argument (`data` in this example),
   which is the return value of `json_response()`.

{% include side-by-side.html demo="js_action_call" %}

This example takes advantage of the [CSS] classes `btn` and
`btn-primary` that are available in [Bootstrap].  See the
[Bootstrap documentation] for more information about using these
classes.

Note that [Ajax] interactions with the interview are possible without
writing any [JavaScript] code; see the [`check in` feature].

You can also access this function under the name `da_action_call()`,
which can be useful if you are embedding **docassemble** and there is
a name conflict.

## <a name="js_get_interview_variables"></a>get_interview_variables() JavaScript function

If you would like to work with all of the variables in the interview
in your [JavaScript] code, you can do so with the
`get_interview_variables()` function, which sends an [Ajax] call to
the server to retrieve the contents of the [interview session dictionary].

The function takes a single argument, which is the callback function.
The callback function is given one parameter, which is an object
having the following attributes:

* `success`: this will be `True` if the call succeeds, `False`
otherwise.
* `variables`: this will be an object containing the interview
  variables in the format produced by [`all_variables()`].
* `i`: the current interview [YAML] file.
* `uid`: the current session ID.
* `encrypted`: whether the [interview session dictionary] is encrypted.
* `steps`: the number of steps taken so far in the interview.

{% highlight javascript %}
var the_vars;
get_interview_variables(function(data){
  if (data.success){
    the_vars = data.variables;
    console.log("The current role is " + the_vars['role']);
  }
});
{% endhighlight %}

You can also access this function under the name
`da_get_interview_variables()`, which can be useful if you are
embedding **docassemble** and there is a name conflict.

## <a name="js_daPageLoad"></a>Running Javascript at page load time

When your [JavaScript] code is imported through the [`javascript`]
feature, it is necessary to wrap the code in a `daPageLoad` trigger.
Otherwise, the code will only be executed on the first page load, not
when the user navigates from screen to screen.

{% highlight javascript %}
$(document).on('daPageLoad', function(){
  console.log("The screen is loaded");
});
{% endhighlight %}

[`json_response()`]: #json_response
[Ajax]: https://en.wikipedia.org/wiki/Ajax_(programming)
[package]: {{ site.baseurl }}/docs/playground.html#packages
[packages]: {{ site.baseurl }}/docs/packages.html
[modules folder]: {{ site.baseurl }}/docs/playground.html#modules
[Playground]: {{ site.baseurl }}/docs/playground.html
[Mako web site]: http://docs.makotemplates.org/en/latest/defs.html
[Mako]: http://www.makotemplates.org/
[Content-Type header]: https://en.wikipedia.org/wiki/List_of_HTTP_header_fields
[Documents]: {{ site.baseurl }}/docs/documents.html
[documents]: {{ site.baseurl }}/docs/documents.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[Flask-Mail]: https://pythonhosted.org/Flask-Mail/
[HTML]: https://en.wikipedia.org/wiki/HTML
[JSON]: https://en.wikipedia.org/wiki/JSON
[Markdown]: https://daringfireball.net/projects/markdown/
[Python dictionary]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[Python dictionaries]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[Python function]: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
[Python functions]: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
[Python interpreter]: https://docs.python.org/3/tutorial/interpreter.html
[Python list]: https://docs.python.org/3/tutorial/datastructures.html
[Python locale]: https://docs.python.org/3/library/locale.html
[Python module]: https://docs.python.org/3/tutorial/modules.html
[Python modules]: https://docs.python.org/3/tutorial/modules.html
[Python set]: https://docs.python.org/3/library/stdtypes.html#set
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[YAML]: https://en.wikipedia.org/wiki/YAML
[`Address`]: {{ site.baseurl }}/docs/objects.html#Address
[`DAFileCollection`]: {{ site.baseurl }}/docs/objects.html#DAFileCollection
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`DAStaticFile`]: {{ site.baseurl }}/docs/objects.html#DAStaticFile
[`.path()`]: {{ site.baseurl }}/docs/objects.html#DAFile.path
[`.set_mimetype()`]: {{ site.baseurl }}/docs/objects.html#DAFile.set_mimetype
[`.copy_into()`]: {{ site.baseurl }}/docs/objects.html#DAFile.copy_into
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`DASet`]: {{ site.baseurl }}/docs/objects.html#DASet
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`DAEmail`]: {{ site.baseurl }}/docs/objects.html#DAEmail
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`IndividualName`]: {{ site.baseurl }}/docs/objects.html#IndividualName
[`LatitudeLongitude`]: {{ site.baseurl }}/docs/objects.html#LatitudeLongitude
[`Organization`]: {{ site.baseurl }}/docs/objects.html#Organization
[`Person`]: {{ site.baseurl }}/docs/objects.html#Person
[`attachments`]: {{ site.baseurl }}/docs/documents.html#attachments
[`basic-questions.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[`code`]: {{ site.baseurl }}/docs/code.html
[`currency()`]: #currency
[`currency_symbol()`]: #currency_symbol
[`currency symbol`]: {{ site.baseurl }}/docs/config.html#currency symbol
[`currency symbol` field specifier]: {{ site.baseurl }}/docs/fields.html#currency
[`datatype: currency`]: {{ site.baseurl }}/docs/fields.html#currency
[`default role`]: {{ site.baseurl }}/docs/initial.html#default role
[`docassemble.base.legal`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[static files]: {{ site.baseurl }}/docs/playground.html#static
[`event`]: {{ site.baseurl }}/docs/fields.html#event
[`force_ask()`]: #force_ask
[`force_gather()`]: #force_gather
[`get_info()`]: #get_info
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`interface()`]: #interface
[`interview_url()`]: #interview_url
[`interview_url_action()`]: #interview_url_action
[`legal.py`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`modules` block]: {{ site.baseurl }}/docs/initial.html#modules
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[`need()`]: #need
[`nice_number()`]: #nice_number
[`noun_plural()`]: #noun_plural
[`object_possessive`]: {{ site.baseurl }}/docs/objects.html#DAObject.object_possessive
[`objects`]: {{ site.baseurl }}/docs/initial.html#objects
[`process_action()`]: #process_action
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`set_info()`]: #set_info
[`set_locale()`]: #set_locale
[`subquestion`]: {{ site.baseurl }}/docs/questions.html#subquestion
[`title_case()`]: #title_case
[`track_location`]:  {{ site.baseurl }}/docs/special.html#track_location
[`url_action()`]: #url_action
[`url_ask()`]: #url_ask
[`words`]: {{ site.baseurl }}/docs/config.html#words
[action]: #url_action
[`attachment`]: {{ site.baseurl }}/docs/documents.html
[`attachments`]: {{ site.baseurl }}/docs/documents.html
[attachments]: {{ site.baseurl }}/docs/documents.html
[classes]: https://docs.python.org/3/tutorial/classes.html
[configuration]: {{ site.baseurl }}/docs/config.html
[dictionary]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[fields]: {{ site.baseurl }}/docs/fields.html
[function]: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
[functions]: #functions
[how **docassemble** runs your code]: {{ site.baseurl }}/docs/logic.html#howitworks
[html2text]: https://pypi.python.org/pypi/html2text
[initial block]: {{ site.baseurl }}/docs/initial.html
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[installation]: {{ site.baseurl }}/docs/installation.html
[interview logic]: {{ site.baseurl }}/docs/logic.html
[keyword argument]: https://docs.python.org/3/glossary.html#term-argument
[keyword arguments]: https://docs.python.org/3/glossary.html#term-argument
[language support]: {{ site.baseurl }}/docs/language.html
[language]: {{ site.baseurl }}/docs/language.html
[list]: https://docs.python.org/3/tutorial/datastructures.html
[locale module]: https://docs.python.org/3/library/locale.html
[markup]: {{ site.baseurl }}/docs/markup.html
[document markup]: {{ site.baseurl }}/docs/documents.html#markup
[methods]: {{ site.baseurl }}/docs/objects.html#person classes
[modifier]: {{ site.baseurl }}/docs/modifiers.html#prevent_going_back
[multi-user interviews]: {{ site.baseurl }}/docs/roles.html
[objects]: {{ site.baseurl }}/docs/objects.html
[pattern.en]: http://www.clips.ua.ac.be/pages/pattern-en
[question]: {{ site.baseurl }}/docs/questions.html
[roles]: {{ site.baseurl }}/docs/roles.html
[scheduled task]: {{ site.baseurl }}/docs/background.html#scheduled
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[special variable]: {{ site.baseurl }}/docs/special.html
[special variables]: {{ site.baseurl }}/docs/special.html
[titlecase]: https://pypi.python.org/pypi/titlecase
[user login system]: {{ site.baseurl }}/docs/users.html
[cron user]: {{ site.baseurl }}/docs/background.html#cron user
[`last_access_time()`]: #last_access_time
[`last_access_days()`]: #last_access_days
[`last_access_hours()`]: #last_access_hours
[`last_access_minutes()`]: #last_access_minutes
[`last_access_delta()`]: #last_access_delta
[`returning_user()`]: #returning_user
[UTC time]: https://en.wikipedia.org/wiki/Coordinated_Universal_Time
[`timezone_list()`]: #timezone_list
[`pytz`]: http://pytz.sourceforge.net/
[`timezone` configuration]: {{ site.baseurl }}/docs/config.html#timezone
[`datetime.timedelta`]: https://docs.python.org/3/library/datetime.html#datetime.timedelta
[`dateutil.relativedelta.relativedelta`]: http://dateutil.readthedocs.io/en/stable/relativedelta.html
[`datetime`]: https://docs.python.org/3/library/datetime.html#datetime.datetime
[`action_argument()`]: #action_argument
[`action_arguments()`]: #action_arguments
[HTTPS]: {{ site.baseurl }}/docs/docker.html#https
[QR code]: https://en.wikipedia.org/wiki/QR_code
[Profile page]: {{ site.baseurl }}/docs/users.html#profile
[`task_performed()`]: #task_performed
[`task_not_yet_performed()`]: #task_not_yet_performed
[`mark_task_as_performed()`]: #mark_task_as_performed
[`times_task_performed()`]: #times_task_performed
[`set_task_counter()`]: #set_task_counter
[task]: #tasks
[actions]: #actions
[`format_date()`]: #format_date
[`format_datetime()`]: #format_datetime
[`format_time()`]: #format_time
[`user_info()`]: #user_info
[`user_logged_in()`]: #user_logged_in
[`user_has_privilege()`]: #user_logged_in
[`def` block]: {{ site.baseurl }}/docs/initial.html#def
[`def` blocks]: {{ site.baseurl }}/docs/initial.html#def
[`response()`]: #response
[`command()`]: #command
[`message()`]: #message
[`url_of()`]: #url_of
[Python Imaging Library]: http://www.pythonware.com/products/pil/
[URL arguments]: {{ site.baseurl }}/docs/special.html#url_args
[Celery]: http://www.celeryproject.org/
[`background_action()`]: {{ site.baseurl }}/docs/background.html#background_action
[`background_response()`]: {{ site.baseurl }}/docs/background.html#background_response
[`background_response_action()`]: {{ site.baseurl }}/docs/background.html#background_response_action
[callback function]: https://en.wikipedia.org/wiki/Callback_(computer_programming)
[background processes]: {{ site.baseurl }}/docs/background.html#background
[background process]: {{ site.baseurl }}/docs/background.html#background
[live chat]: {{ site.baseurl }}/docs/livehelp.html
[special variable `speak_text`]: {{ site.baseurl }}/docs/special.html#speak_text
[`country` configuration setting]: {{ site.baseurl }}/docs/config.html#country
[SMS]: https://en.wikipedia.org/wiki/Short_Message_Service
[MMS]: https://en.wikipedia.org/wiki/Multimedia_Messaging_Service
[Twilio]: https://twilio.com
[E.164]: https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers
[`phonenumbers.PhoneNumber`]: https://github.com/daviddrysdale/python-phonenumbers
[`twilio`]: {{ site.baseurl }}/docs/config.html#twilio
[`twilio` configuration directive]: {{ site.baseurl }}/docs/config.html#twilio
[`phonenumbers`]: https://github.com/daviddrysdale/python-phonenumbers
[`get_country()`]: #get_country
[`set_country()`]: #set_country
[`country` configuration directive]: {{ site.baseurl }}/docs/config.html#country
[`pycountry` package]: https://pypi.python.org/pypi/pycountry
[`send_sms()`]: #send_sms
[flash]: http://flask.pocoo.org/docs/0.11/patterns/flashing/
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[`features`]: {{ site.baseurl }}/docs/initial.html#features
[`javascript`]: {{ site.baseurl }}/docs/initial.html#javascript
[`script`]: {{ site.baseurl }}/docs/fields.html#script
[`html`]: {{ site.baseurl }}/docs/fields.html#html
[`css`]: {{ site.baseurl }}/docs/fields.html#css
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
[`alert()`]: http://www.w3schools.com/jsref/met_win_alert.asp
[multiple servers]: {{ site.baseurl }}/docs/scalability.html
[special user]: {{ site.baseurl }}/docs/background.html#cron user
[Redis]: https://redis.io/
[in-memory database]: https://en.wikipedia.org/wiki/In-memory_database
[object]: {{ site.baseurl }}/docs/objects.html
[pickled]: https://docs.python.org/3/library/pickle.html
[`db`]: {{ site.baseurl }}/docs/config.html#db
[PostgreSQL]: http://www.postgresql.org/
[`checkin interval`]: {{ site.baseurl }}/docs/config.html#checkin interval
[`all_variables()`]: #all_variables
[form feed character]: https://en.wikipedia.org/wiki/Page_break#Form_feed
[optical character recognition]: https://en.wikipedia.org/wiki/Optical_character_recognition
[`get_language()`]: #get_language
[`set_language()`]: #set_language
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[ISO-639-2]: https://en.wikipedia.org/wiki/List_of_ISO_639-2_codes
[ISO-639-3]: https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
[Tesseract]: https://en.wikipedia.org/wiki/Tesseract_(software)
[`ocr languages`]: {{ site.baseurl }}/docs/config.html#ocr languages
[`debian packages`]: {{ site.baseurl }}/docs/config.html#debian packages
[`ocr dpi`]: {{ site.baseurl }}/docs/config.html#ocr dpi
[pdftoppm]: http://www.foolabs.com/xpdf/download.html
[`s3`]: {{ site.baseurl }}/docs/config.html#s3
[`azure`]: {{ site.baseurl }}/docs/config.html#azure
[`voicerss`]: {{ site.baseurl }}/docs/config.html#voicerss
[`oauth`]: {{ site.baseurl }}/docs/config.html#oauth
[SMS interface]: {{ site.baseurl }}/docs/sms.html
[more than one `twilio` configuration directive]: {{ site.baseurl }}/docs/config.html#multiple twilio
[`initiate_sms_session()`]: #initiate_sms_session
[user-agents]: https://pypi.python.org/pypi/user-agents
[User-Agent header]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent
[Accept-Language header]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Language
[Bootstrap]: https://en.wikipedia.org/wiki/Bootstrap_%28front-end_framework%29
[Bootstrap documentation]: https://getbootstrap.com/docs/4.0/getting-started/introduction/
[`check in` feature]: {{ site.baseurl }}/docs/background.html#check in
[Amazon S3]: https://aws.amazon.com/s3/
[e-mail to interview]: {{ site.baseurl }}/docs/background.html#email
[`interview_email()`]: #interview_email
[`get_emails()`]: #get_emails
[`subdivision_type()`]: #subdivision_type
[`incoming mail domain`]: {{ site.baseurl }}/docs/config.html#incoming mail domain
[interaction of user roles and actions]: {{ site.baseurl }}/docs/users.html#users and actions
[`contacts.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/sources/contacts.yml
[`contacts.json`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/sources/contacts.json
[associative array]: https://en.wikipedia.org/wiki/Associative_array
[`fish.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/fish.py
[`fishes.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/sources/fishes.yml
[standard Python notation]: https://docs.python.org/3/tutorial/modules.html#intra-package-references
[`docassemble.demo`]: https://github.com/jhpyle/docassemble/tree/master/docassemble_demo/docassemble/demo
[`docassemble.demo` package on GitHub]: https://github.com/jhpyle/docassemble/tree/master/docassemble_demo/docassemble/demo
[GitHub]: https://github.com/
[sources folder]: {{ site.baseurl }}/docs/playground.html#sources
[`datetime.datetime`]: https://docs.python.org/3/library/datetime.html#datetime-objects
[`__init__()`]: https://docs.python.org/3/reference/datamodel.html#object.__init__
[document]: http://yaml.org/spec/1.2/spec.html#id2760395
[MIME type]: https://en.wikipedia.org/wiki/Media_type
[tuple]: https://en.wikibooks.org/wiki/Python_Programming/Tuples
[Azure blob storage]: https://azure.microsoft.com/en-us/services/storage/blobs/
[`url_args`]: {{ site.baseurl }}/docs/special.html#url_args
[`ocr_file()`]: #ocr_file
[`ocr_file_in_background()`]: #ocr_file_in_background
[tesseract-ocr-all]: https://packages.debian.org/stretch/tesseract-ocr-all
[`raw field variables`]: {{ site.baseurl }}/docs/documents.html#raw field variables
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[`pdf template file`]: {{ site.baseurl }}/docs/documents.html#pdf template file
[assembled]: {{ site.baseurl }}/docs/documents.html#docx template file
[`.comma_and_list()`]: {{ site.baseurl }}/docs/objects.html#DAList.comma_and_list
[gathered]: {{ site.baseurl }}/docs/groups.html#gathering
[`.instanceName`]: {{ site.baseurl }}/docs/objects.html#instanceName
[`objects from file`]: {{ site.baseurl }}/docs/initial.html#objects from file
[The YAML Format]: http://symfony.com/doc/current/components/yaml/yaml_format.html
[QR markup documentation]: {{ site.baseurl }}/docs/markup.html#qr
[progress bar]: {{ site.baseurl }}/docs/initial.html#features
[`progress`]: {{ site.baseurl}}/docs/modifiers.html#progress
[navigation bar]: {{ site.baseurl }}/docs/initial.html#navigation bar
[Python object]: https://docs.python.org/3/tutorial/classes.html
[methods]: https://docs.python.org/3/tutorial/classes.html
[`sections`]: {{ site.baseurl }}/docs/initial.html#sections
[`nav.set_sections()`]: #DANav.set_sections
[`DANav`]: #DANav.set_sections
[table]: {{ site.baseurl }}/docs/initial.html#table
[referer header]: https://en.wikipedia.org/wiki/HTTP_referer
[`exitpage`]: {{ site.baseurl }}/docs/config.html#exitpage
[JSON interface]: {{ site.baseurl }}/docs/frontend.html
[`hello.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/hello.py
[relative module name]: https://docs.python.org/2.5/whatsnew/pep-328.html
[`unittest` framework]: https://docs.python.org/3/library/unittest.html
[`tests.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/tests.py
[`my_name_suffix`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/my_name_suffix.py
[`indent()`]: #indent
[del statement]: https://docs.python.org/3/tutorial/datastructures.html#the-del-statement
[multiple-choice question]: {{ site.baseurl }}/docs/fields.html#field with buttons
[`need` specifier]: {{ site.baseurl }}/docs/logic.html#need
[PDF templates]: {{ site.baseurl }}/docs/documents.html#pdf template file
[`yesno()`]: #yesno
[Unicode Technical Standard #35]: https://unicode.org/reports/tr35/tr35-dates.html#Date_Field_Symbol_Table
[`DARedis`]: {{ site.baseurl }}/docs/objects.html#DARedis
[`DADateTime`]: {{ site.baseurl }}/docs/objects.html#DADateTime
[`.time()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.time
[`.format_date()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_date
[`.format_time()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_time
[`.format_datetime()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_datetime
[locale]: #langlocale
[`metadata` initial block]: {{ site.baseurl }}/docs/initial.html#metadata
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[PDF/A]: https://en.wikipedia.org/wiki/PDF/A
[`console.log` JavaScript function]: https://developer.mozilla.org/en-US/docs/Web/API/Console/log
[`eval` JavaScript function]: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval
[Bootstrap alert]: https://getbootstrap.com/docs/4.0/components/alerts/
[`flash()`]: #flash
[Google API key]: {{ site.baseurl }}/docs/config.html#google
[`google`]: {{ site.baseurl }}/docs/config.html#google
[`service account credentials`]: {{ site.baseurl }}/docs/config.html#service account credentials
[configuration]: {{ site.baseurl }}/docs/config.html
[`encode_name()`]: #encode_name
[`decode_name()`]: #decode_name
[section on custom front ends]: {{ site.baseurl }}/docs/frontend.html
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[UTC]: https://en.wikipedia.org/wiki/Coordinated_Universal_Time
[`dispatch interview`]: {{ site.baseurl }}/docs/config.html#dispatch interview
[`session list interview`]: {{ site.baseurl }}/docs/config.html#session list interview
[`generic object`]: {{ site.baseurl}}/docs/modifiers.html#generic object
[`googledrive`]: {{ site.baseurl }}/docs/config.html#googledrive
[`phone login`]: {{ site.baseurl }}/docs/config.html#phone login
[PyPI]: https://pypi.python.org/pypi
[GitHub]: https://github.com/
[`github`]: {{ site.baseurl }}/docs/config.html#github
[`pypi`]: {{ site.baseurl }}/docs/config.html#pypi
[`map_of()`]: #map_of
[`geolocate()`]: {{ site.baseurl }}/docs/objects.html#Address.geolocate
[`google`]: {{ site.baseurl }}/docs/config.html#google
[list of available interviews]: {{ site.baseurl }}/docs/config.html#dispatch
[`show login`]: {{ site.baseurl }}/docs/config.html#show login
[`password`]: {{ site.baseurl }}/docs/documents.html#password
[status callback values]: https://www.twilio.com/docs/api/fax/rest/faxes#fax-status-callback
[fax status values]: https://www.twilio.com/docs/api/fax/rest/faxes#fax-status-values
[DOCX template file]: {{ site.baseurl }}/docs/documents.html#docx template file
[Jinja2]: http://jinja.pocoo.org/docs/2.9/
[`/api/list`]: {{ site.baseurl }}/docs/api.html#list
[`/api/interviews`]: {{ site.baseurl }}/docs/api.html#interviews
[`/api/user/interviews`]: {{ site.baseurl }}/docs/api.html#user_interviews
[`/api/user/<user_id>/interviews`]: {{ site.baseurl }}/docs/api.html#user_user_id_interviews
[`/api/user_list`]: {{ site.baseurl }}/docs/api.html#user_list
[`/api/user`]: {{ site.baseurl }}/docs/api.html#user
[`/api/user/new`]: {{ site.baseurl }}/docs/api.html#user_new
[`/api/user/<user_id>`]: {{ site.baseurl }}/docs/api.html#user_user_id
[POST method of `/api/user/<user_id>`]: {{ site.baseurl }}/docs/api.html#user_user_id_post
[DELETE method of `/api/user/<user_id>`]: {{ site.baseurl }}/docs/api.html#user_user_id_delete
[`/api/secret`]: {{ site.baseurl }}/docs/api.html#secret
[GET method of `/api/session`]: {{ site.baseurl }}/docs/api.html#session_get
[POST method of `/api/session`]: {{ site.baseurl }}/docs/api.html#session_post
[POST method of `/api/session/back`]: {{ site.baseurl }}/docs/api.html#session_back
[POST method of `/api/user/<user_id>/privileges`]: {{ site.baseurl }}/docs/api.html#user_privilege_add
[DELETE method of `/api/user/<user_id>/privileges`]: {{ site.baseurl }}/docs/api.html#user_privilege_remove
[`get_user_list()`]: #get_user_list
[`get_user_secret()`]: #get_user_secret
[`create_session()`]: #create_session
[`get_session_variables()`]: #get_session_variables
[`get_question_data()`]: #get_question_data
[`set_session_variables()`]: #set_session_variables
[API]: {{ site.baseurl }}/docs/api.html
[`get_user_info()`]: #get_user_info
[`set_user_info()`]: #set_user_info
[`go_back_in_session()`]: #go_back_in_session
[`manage_privileges()`]: #manage_privileges
[Google Drive synchronization]: {{ site.baseurl }}/docs/playground.html#google drive
[`/api/privileges`]: {{ site.baseurl }}/docs/api.html#privileges
[`/api/session/question`]: {{ site.baseurl }}/docs/api.html#session_question
[`.set_attributes()`]: {{ site.baseurl }}/docs/objects.html#DAFile.set_attributes
[`datetime.time`]: https://docs.python.org/3/library/datetime.html#datetime.time
[thread-safe]: https://en.wikipedia.org/wiki/Thread_safety
[gspread]: https://gspread.readthedocs.io/en/latest/
[Google Developers Console]: https://console.developers.google.com/
[Google Sheets]: https://sheets.google.com
[Google Forms]: https://docs.google.com/forms
[Google Sheet]: https://sheets.google.com
[Fruits and veggies]: https://docs.google.com/spreadsheets/d/1Lrm75Rq-C4wrftZnmwLJaKh_VPP3xe1iYfDP95e-UMs/edit?usp=sharing
[`google_sheets` module]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/google_sheets.py
[try out this interview]: https://demo.docassemble.org/interview?i=docassemble.demo:data/questions/examples/google-sheet.yml
[`main_document.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/main_document.docx
[`sub_document.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/sub_document.docx
[`main_doc_params.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/main_doc_params.docx
[`sub_doc_params.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/sub_doc_params.docx
[`repr()`]: https://docs.python.org/3/library/functions.html#repr
[`pdf_concatenate()`]: #pdf_concatenate
[ZIP file]: https://en.wikipedia.org/wiki/Zip_(file_format)
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[`interview_list()`]: #interview_list
[Google Drive API]: https://developers.google.com/drive/
[`set_parts()`]: #set_parts
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[`session_tags()`]: #session_tags
[`read_records()`]: #read_records
[`write_record()`]: #write_record
[`validate`]: {{ site.baseurl }}/docs/fields.html#validate
[`wc_side_of_bed.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/examples/wc_side_of_bed.yml
[`wc_common.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/examples/wc_common.yml
[lambda function]: https://docs.python.org/3.6/tutorial/controlflow.html#lambda-expressions
[lambda functions]: https://docs.python.org/3.6/tutorial/controlflow.html#lambda-expressions
[`raise`]: https://docs.python.org/3.6/tutorial/errors.html#raising-exceptions
[`validation code`]: {{ site.baseurl }}/docs/fields.html#validation code
[Google Sheets API]: https://developers.google.com/sheets/api/
[`js show if`]: {{ site.baseurl }}/docs/fields.html#js show if
[redact_demo.docx]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/redact_demo.docx
[redact_demo.pdf]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/redact_demo.pdf
[`somefuncs.py`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/somefuncs.py
[`NameError`]: https://docs.python.org/3/library/exceptions.html#exceptions.NameError
[`try`/`except`]: https://docs.python.org/3.6/tutorial/errors.html#handling-exceptions
[`redact: False`]: {{ site.baseurl }}/docs/documents.html#redact
[`forget_result_of()`]: #forget_result_of
[`re_run_logic()`]: #re_run_logic
[`id`]: {{ site.baseurl }}/docs/modifiers.html#id
[embedded blocks]: {{ site.baseurl }}/docs/fields.html#code button
[special buttons]: {{ site.baseurl }}/docs/questions.html#special buttons
[starting an interview from the beginning]: {{ site.baseurl }}/docs/interviews.html#reset
[tags]: #session_tags
[`reconsider`]: {{ site.baseurl }}/docs/logic.html#reconsider
[`reset`]: {{ site.baseurl }}/docs/initial.html#reset
[`review`]: {{ site.baseurl }}/docs/fields.html#review
[customizing the display of `review` options]: {{ site.baseurl }}/docs/fields.html#review customization
[`word()`]: #word
[Font Awesome]: https://fontawesome.com
[mermaid]: https://github.com/mermaidjs/mermaid.cli
[`template`]: {{ site.baseurl }}/docs/initial.html#template
[interview session dictionary]: {{ site.baseurl }}/docs/interviews.html#howstored
[write your own functions]: #yourown
[`create_user()`]: #create_user
[privileges]: {{ site.baseurl }}/docs/users.html
[privilege]: {{ site.baseurl }}/docs/users.html
[upgrade to Python 3]: {{ site.baseurl }}/docs/twotothree.html
[six]: https://pypi.org/project/six/
[screen parts]: {{ site.baseurl }}/docs/questions.html#screen parts
[`sms_number()`]: {{ site.baseurl }}/docs/objects.html#Person.sms_number
[WhatsApp]: https://www.twilio.com/whatsapp
[`suppress loading util`]: {{ site.baseurl }}/docs/initial.html#suppress loading util
[country calling code]: https://en.wikipedia.org/wiki/List_of_country_calling_codes
[`get_interview_variables()`]: #js_get_interview_variables
[`debug`]: {{ site.baseurl }}/docs/config.html#debug
[`DAStore`]: {{ site.baseurl }}/docs/objects.html#DAStore
[translating]: {{ site.baseurl }}/docs/initial.html#translations
[`continue button field`]: {{ site.baseurl }}/docs/fields.html#continue button field
[`undefine()`]: #undefine
[`get_locale()`]: #get_locale
[`set_locale()`]: #set_locale
[`update_locale()`]: #update_locale
[`datatype: file`]: {{ site.baseurl }}/docs/fields.html#file
[`datatype: files`]: {{ site.baseurl }}/docs/fields.html#files
[`locale`]: https://docs.python.org/3.6/library/locale.html
[language-specific functions]: #linguistic
[`docassemble.base.util.update_word_collection()`]: #update_word_collection
[`add-separators.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_base/docassemble/base/data/templates/add-separators.docx
[`reconsider()`]: #reconsider
[`contract.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/contract.docx
[ISO 3166-1 alpha-2]: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[ISO 3166-1]: https://en.wikipedia.org/wiki/ISO_3166-1
[Mailgun API]: {{ site.baseurl }}/docs/config.html#mailgun api
[e-mail sending]: {{ site.baseurl }}/docs/config.html#mail
[user variables]: https://documentation.mailgun.com/en/latest/user_manual.html#attaching-data-to-messages
[`if`]: {{ site.baseurl }}/docs/modifiers.html#if
[`pagination limit`]: {{ site.baseurl }}/docs/config.html#pagination limit
[`read_snapshot.py`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/read_snapshot.py
[JSONB]: https://www.postgresql.org/docs/current/functions-json.html
[`psycopg2`]: https://www.psycopg.org/docs/
[`variables snapshot db`]: {{ site.baseurl }}/docs/config.html#variables snapshot db
[`DAEmailRecipient`]: {{ site.baseurl }}/docs/objects.html#DAEmailRecipient
[recipe on the topic]: {{ site.baseurl }}/docs/recipes.html#python to javascript
