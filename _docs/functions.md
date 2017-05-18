---
layout: docs
title: Functions
short_title: Functions
---

# What is a function?

A function is a piece of code that takes one or more pieces of input
and returns something as output.  For example:

{% include side-by-side.html demo="function" %}

Functions allow you to do a lot of different things in
**docassemble**.  This section explains the standard **docassemble**
functions.  If you know how to write [Python] code, you can write your
own functions and include them in your interview using a [`modules`]
block.

# <a name="howtouse"></a>How to use functions

To use the functions described in this section in your interviews, you
need to include them from the [`docassemble.base.util`] module by
writing the following somewhere in your interview:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
{% endhighlight %}

Unless otherwise instructed, you can assume that all of the functions
discussed in this section are available in interviews when you include
this [`modules`] block.

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
`meaning_of_life` variable as a variable name.  So if
`meaning_of_life` is "chocolate," `value(meaning_of_life)` will
attempt to find the value of the variable `chocolate`.

## <a name="need"></a>need()

The `need()` function takes one or more variables as arguments and
causes **docassemble** to ask questions to define each of the
variables if the variables are not already defined.  Note that with
`need()`, you do _not_ put quotation marks around the variable name.

For example, this [`mandatory`] code block expresses [interview logic]
requiring that the user first be shown a splash screen and then be
asked questions necessary to get to the end of the intererview.

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

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
question: |
  Are you a communist?
yesno: user_is_communist
---
mandatory: True
code: |
  if user_is_communist and user_reconsidering_communism:
    user_reconsidering_communism = False
    force_ask('user_is_communist')
---
question: |
  I suggest you reconsider your answer.
field: user_reconsidering_communism
---
mandatory: True
question: |
  % if user_is_communist:
  I am referring your case to Mr. McCarthy.
  % else:
  I am glad you are a true American.
  % endif
{% endhighlight %}

This may be useful in particular circumstances.  Note, however, that
the effect of `force_ask()` is temporary.  If the user refreshes the
screen while looking at the `user_is_communist` question a second
time, it will be as though `force_ask` never happened.

Note also that no code that comes after `force_ask()` will ever be
executed.  Once the `force_ask()` function is called, the code stops
running, and the question indicated by the variable name will be
shown.  That is why, in the example above, we set
`user_reconsidering_communism` to False before calling `force_ask`.
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

## <a name="force_gather"></a>force_gather()

The `force_gather()` function is similar to [`force_ask()`], except it
is not only asks a question, but insists that a variable be defined.

In addition to doing what [`force_ask()`] does, `force_gather()`
engages the assistance of the [`process_action()`] function to make
sure that the variable is defined.  The [`process_action()`] function
will not finish until the variable is defined.

{% include side-by-side.html demo="force-gather" %}

In this example, [`force_ask()`] would not have worked in place of
`force_gather()`, because if the user selects "Something else," the
interview would not continue on to the next question that offers to
define `favorite_food`.  Calling `force_ask('favorite_food')` means
"look for a question that offers to define `favorite_food`, and
present it to the user, whereas calling
`force_gather('favorite_food')` means "until `favorite_food` is
defined, keep asking questions that offer to define `favorite_food`."

Normally, you will not need to use either [`force_ask()`] or
[`force_gather()`]; you can just mention the name of a variable in
your [`question`]s or [`code`] blocks, and **docassemble** will make
sure that the variables get defined.  The [`force_ask()`] and
[`force_gather()`] functions are primarily useful when you are using
[actions] to do things that are outside the normal course of the
[interview logic].

## <a name="all_variables"></a>all_variables()

The `all_variables()` function returns all of the variables in the
interview in the form of a simplified [Python dictionary].

{% include side-by-side.html demo="all_variables" %}

The resulting [Python dictionary] is suitable for conversion to [JSON]
or other formats.  Each [object] is converted to a
[Python dictionary].  Each [`datetime`] object is converted to its
`isoformat()`.  Other objects are converted to `None`.

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

The `response()` command allows the interview author to use code to
send a special HTTP response.  Instead of seeing a new **docassemble**
screen, the user will see raw content as an HTTP response, or be
redirected to another web site.  As soon as **docassemble** runs the
`response()` command, it stops what it is doing and returns the
response.

There are four different types of responses, which you can invoke by
using one of four keyword arguments: `response`, `binaryresponse`,
`file`, and `url`.  There is also an optional keyword argument
`content_type`, which determines the setting of the
[Content-Type header].  (This is not used for `url` responses,
though.)

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

1. We load [`docassemble.base.util`] so that the
   [`interview_url_action()`], [`process_action()`], and
   [`url_action()`] functions are available.
2. We set [`multi_user`] to `True` in order to disable server-side
   encrpytion.  This allows an external application to access the
   interview without logging in as the user.
3. The `query_fruit` [`event`] code will be run as an [action] when
   someone accesses the link created by [`interview_url_action()`].

The `response()` command can be used to integrate a **docassemble**
interview with another application.  For example, the other
application could call **docassemble** with a URL that includes an
interview file name (argument `i`) along with a number of
[URL arguments].  The interview would process the information passed
through the URLs, but would not ask any questions.  It would instead
return an assembled document using `response()`.

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
attachment:
  name: A file
  file: test_file
  variable name: the_file
  valid formats:
    - pdf
  content: |
    Hello, world!
---
mandatory: True
code: |
  response(file=the_file.pdf)
---
{% endhighlight %}

Here is a link that runs this interview.  Notice how the name "Fred" is
embedded in the URL.  The result is an immediate PDF document.

> [{{ site.demourl }}?i=docassemble.base:data/questions/examples/immediate_file.yml&name=Fred]({{ site.demourl }}?i=docassemble.base:data/questions/examples/immediate_file.yml&name=Fred){:target="_blank"}

## <a name="json_response"></a>json_response()

The function `json_response(data)` is a shorthand for
`response(json.dumps(data), content_type="application/json")`.

In other words, it takes a single argument and returns it as an HTTP
response in [JSON] format.

## <a name="variables_as_json"></a>variables_as_json()

The `variables_as_json()` function acts like [`response()`] in the
example above, except that is returns all of the variables in the
interview dictionary in [JSON] format.

{% include side-by-side.html demo="variables_as_json" %}

The `variables_as_json()` function simplifies the interview variables
in the same way that the [`all_variables()`] function does.

## <a name="command"></a>command()

{% include side-by-side.html demo="exit" %}

The `command()` function allows the interview author to trigger an
exit from the interview using code, rather than having the user click
an `exit`, `restart`, `leave` or `signin` button.

The first argument to `command()` is one of the following:

* `restart`: deletes the user's answers and puts them back at the
  start of the interview.
* `exit`: deletes the user's answers and redirects them to a web site
* `leave`: redirects the user to a web site without deleting the
  user's answers.
* `signin`: redirects the user to the sign-in screen.

The optional keyword argument `url` provides a URL to which the user
should be redirected.

One use of `command()` is to delete interviews after a period of
inactivity.  See [scheduled tasks] for more information.

# Text transformation functions

## <a name="from_b64_json"></a>from_b64_json()

Takes a string as input, converts the string from base-64, then parses
the string as [JSON], and returns the object represented by the
[JSON].

This is an advanced function that is used by software developers to
integrate other systems with docassemble.

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
[attachments].

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

# <a name="actions"></a>Functions for interacting with the interview using URLs

## <a name="url_action"></a><a name="process_action"></a>url_action() and process_action()

The `url_action()` function allows users to interact with
**docassemble** using hyperlinks embedded in questions.

`url_action()` returns a URL that, when clicked, will perform an
action within **docassemble**, such as running some code or asking a
question.  Typically the URL will be part of a [Markdown] link inside
of a [question], or in a `note` within a set of [fields].

The [`process_action()`] function triggers the processing of the
action.  It is typically called behind-the-scenes, but you can call it
explicitly if you want to control exactly when (and if) it is called.
For more information about calling [`process_action()`] explicitly,
see the section on the [interaction of user roles and actions].

Here is an example:

{% include side-by-side.html demo="lucky-number" %}

When the user clicks one of the links, the interview will load as
usual (much as if the user refreshed the web browser page).  The only
difference is that **docassemble** sees the additional information
stored in the URL and makes that information available to the
interview.

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
is possible for actions on the interview to be run by a "third party."
For information on how to do this, see [`interview_url_action()`] and
[scheduled tasks].

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

The keyword argument `i` is special: you can set this to the name of
an interview (e.g., `docassemble.demo:data/questions/questions.yml`)
and this interview will be used instead of the current interview.

## <a name="interview_url_as_qr"></a>interview_url_as_qr()

Like `interview_url()`, except it inserts into the markup a [QR code]
linking to the interview.  The resulting [QR code] can be used to pass
control from a web browser or a paper handout to a mobile device.

## <a name="interview_url_action"></a>interview_url_action()

`interview_url_action()` is like [`interview_url()`], except that it
also has the effect of running [`url_action()`].  You will want to use
this instead of [`url_action()`] if you want the user to be able to
share the URL with other people, or run it unattended.

{% include side-by-side.html demo="interview_url_action" %}

Note the following about this example:

* [`multi_user`] must be set to `True`.  This disables server-side
  encryption of answers.  This is necessary because the encryption
  uses the user's password, and the password should not be embedded in
  a URL.
* [`initial`] code also runs [`process_action()`], which indicates when
  the action (in this case, `check_update_status`) should be done
  relative to other [`initial`] and [`mandatory`] code.

## <a name="interview_url_action_as_qr"></a>interview_url_action_as_qr()

Like `interview_url_action()`, except it inserts into the markup a
[QR code] linking to the interview, with the specified actions.

Note that there is a limit to the number of characters a [QR code] can
hold, and you might run up against this limit if you try to add too
many arguments to the URL.

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

## <a name="qr_code"></a>qr_code()

The `qr_code()` function allows you to include the `[QR ...]` [markup] statement
using [Python].

These two questions are equivalent:

{% highlight yaml %}
---
question: |
  Here is a QR code.
subquestion: |
  Go to Google:

  ${ qr_code('http://google.com', width='200px') }

  Or go to Yahoo:

  ${ qr_code('http://yahoo.com') }
sets: qr_example
---
{% endhighlight %}

{% highlight yaml %}
---
question: |
  Here is a QR code.
subquestion: |
  Go to Google:

  [QR http://google.com, 200px]

  Or go to Yahoo:

  [QR http://yahoo.com]
sets: qr_example
---
{% endhighlight %}

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
* `url_of('login')` returns a URL to the sign-in page.
* `url_of('signin')` does the same thing as `url_of('login')`.
* `url_of('interviews')` returns a URL to the page listing the
  on-going interviews of a signed-in user.
* `url_of('playground')` returns a URL to the [Playground].

# E-mail functions

## <a name="send_email"></a>send_email()

The `send_email()` function sends an e-mail using [Flask-Mail].

{% include side-by-side.html demo="send-email" %}

All of the arguments to `send_email()` are [keyword arguments], the
defaults of which are:

{% highlight python %}
send_email(to=None, sender=None, cc=None, bcc=None, body=None, html=None, subject="", template=None, task=None, attachments=None)
{% endhighlight %}

This function is integrated with other classes in
[`docassemble.base.util`] and [`docassemble.base.core`].

* `to` expects a [list] of [`Individual`]s.
* `sender` expects a single [`Individual`].  If not set, the
  `default_sender` information from the [configuration] is used.
* `cc` expects a [list] of [`Individual`]s, or `None`.
* `bcc` expects a [list] of [`Individual`]s, or `None`.
* `body` expects text, or `None`.  Will set the plain text content of
  the e-mail.
* `html` expects text, or `None`.  Will set the (optional) [HTML]
  content of the e-mail.
* `subject` expects text, or `None`.  Will set the subject of the e-mail.
* `template` expects a [`DATemplate`] object, or `None`.  These
  templates can be created in an interview file using the `template`
  directive.  If this [keyword argument] is supplied, both the plain
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
* `attachments` expects a [list] of [`DAFile`], [`DAFileList`], or
  [`DAFileCollection`] objects.  You can include:
  * Images generated by `signature` blocks (objects of class
  [`DAFile`]);
  * File uploads generated by including [fields] of `datatype: file` or
  `datatype: files` in a [`question`] (objects of class [`DAFileList`]);
  * [Documents] generated by [`attachments`] to a [`question`] for which a
  `variable` was provided (objects of class [`DAFileCollection`]).

It uses the `name` and `email` attributes of the listed [`Individual`]s
to form e-mail addresses.

`send_email()` returns `False` if an error prevented the e-mail from
being sent; otherwise it returns `True`.

See [configuration] for information about how to configure the mail
server that `send_email()` will use.

Here is an example of sending an attachment via e-mail:

{% include side-by-side.html demo="send-email-with-attachment" %}

## <a name="interview_email"></a>interview_email()

The `interview_email()` function returns an e-mail address that the
user can use to send a message to the interview.  For more information
about how users can send e-mails to interviews, see the documentation
for the [e-mail to interview] feature.

If the [`incoming mail domain`] directive in your [configuration] is
`help.example.com`, then `interview_email()` will return something
like `kgjeir@help.example.com`.

The address returned by `interview_email()` is a unique random
sequence of six lowercase letters.  If any e-mails are received at
this e-mail address, **docassemble** will associate them with the
user's interview session and the e-mails can be retrieved with
[`get_emails()`].

The result returned by `interview_email()` will be unique to the
interview session.  Every time your interview calls
`interview_email()`, the same e-mail address will be returned.

You can also associate more than one e-mail address with the interview
session, if you wish.  For example, in a litigation application, you
may want to have one e-mail address for receiving evidence from the
client and another address for corresponding with opposing counsel.
You can obtain these different e-mail addresses using the optional
keyword argument `key`.  For example,
`interview_email(key='evidence')` and `interview_email(key='opposing
counsel')` will return different unique addresses.

If you are using a `key` to get an e-mail address, you can also
set the optional keyword argument `index` to an integer.  For example,
if there are multiple opposing counsel and you want a separate e-mail
address for each one, you can use `interview_email(key='opposing
counsel', index=1)`, `interview_email(key='opposing
counsel', index=2)`, etc.

## <a name="get_emails"></a>get_emails()

The `get_emails()` function returns a [list] of objects representing
e-mail addresses generated with [`interview_email()`].  For more
information about how users can send e-mails to interviews, see the
documentation for the [e-mail to interview] feature.

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

# Geographic functions

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
in this two-letter, capitalized format.  The country code is used by
the [`send_sms()`] function to determine the appropriate universal
formatting of phone numbers.

The data come from the [`pycountry` package].

## <a name="states_list"></a><a name="state_name"></a>states_list() and state_name()

The `states_list()` function returns a list of dictionaries, where
each dictionary contains a single key-value pair mapping a state
abbreviation to the name of a state.  This function is primarily
useful when asking a user to specify his or her state.

The function takes an optional keyword argument `country`, which is
expected to be a country abbreviation (e.g., `'SE'` for Sweden).  If
the `country` is not provided, it is assumed to be the default country
(the value returned by [`get_country()`]).  For countries other than
the United States, the geographic areas returned are the first-level
subdivisions within the country.  The name of these subdivisions
varies.  The [`subdivision_type()`] function can be used to find the
name of the major subdivision, and also to find if the
country has any subdivisions at all.

The `state_name()` function returns the name of a state based on the
state abbreviation provided.

{% include side-by-side.html demo="state" %}

When working with states, it is a good idea to store state names in
this abbreviated format.

The data come from the [`pycountry` package].

## <a name="subdivision_type"></a>subdivision_type()

Given a country code, `subdivision_type()` returns the name of the
primary subdivision within that country.

{% include side-by-side.html demo="subdivision-type" %}

Note that some countries have no subdivisions at all.  In that case,
this function will return `None`.

The data come from the [`pycountry` package].

# Functions for managing global variables

If you try writing your own functions, you will learn that functions
do not have access to all of the variables in your interview.
Functions only know the variables you pass to them.

If your functions need to know background information about the
interview, but you do not want to have to pass a lot of variables to
every function you call, you can use "global" variables.

You set "global" variables in **docassemble** by calling [`set_info()`]
and your retrieve them by calling [`get_info()`].  Note that
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

Some of the [functions] and [methods] of [`docassemble.base.util`]
will behave differently depending on who the interviewee is and what
the interviewee's role is.  For example, if `trustee` is an object of
the class [`Individual`], and you call `trustee.do_question('have')`,
the result will be "do you have" if if the interviewee is the trustee,
but otherwise the result will be "does Fred Jones have" (or whatever
the trustee's name is).

In order for the [`docassemble.base.util`] module to know this
background information, you need to include an [`initial`] code block
(or a [`default role`] block containing [`code`]) that:

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
[SMS].

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

## <a name="user_privileges"></a>user_privileges()

The `user_privileges()` function returns the user's privileges as a
list.  If the user is not logged in, the result is `['user']`.  If the
user is a "user" as well as a "customer," the result is
`['user', 'customer']`.  If the interview is running a
[scheduled task], the result is `['cron']`.

## <a name="user_has_privilege"></a>user_has_privilege()

The `user_has_privilege()` function returns `True` if the user has any
of the given privileges, and `False` otherwise.  For example, if the
user has the privilege of "customer," `user_has_privilege('customer')`
will return `True`.  A list can also be provided, in which case `True`
will be returned if the user has any of the given privileges.  For
example, if the user has the privilege of "developer",
`user_has_privilege(['developer', 'admin'])` will return `True`.

## <a name="user_info"></a>user_info()

The `user_info()` function will return an object with the following
attributes describing the current user:

* `first_name`
* `last_name`
* `email`
* `country` (will be an official [country code] like `us`)
* `subdivision_first` (e.g., state)
* `subdivision_second` (e.g., county)
* `subdivision_third` (e.g., municipality)
* `organization` (e.g., company or non-profit organization)

These attributes are set by the user on the [Profile page].

For example:

{% highlight yaml %}
---
question: |
  Your e-mail address is ${ user_info().email }.  Is that
  the best way to reach you?
yesno: email_is_best
---
{% endhighlight %}

# Functions for determining information about the browser

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

# Language and locale functions()

These functions access and change the active language and locale.  See
[language support] for more information about these features of
**docassemble**.

## <a name="get_language"></a>get_language()

If the language is set to English, `get_language()` returns `en`.

## <a name="set_language"></a>set_language()

This sets the language that will be used in the web application and in
language-specific functions of **docassemble**.  It does not change
the active [Python locale].  See `update_locale()` for information on
changing the [Python locale].

If you need to set the language to something other than the language
set in the [configuration], you need to call `set_language()` within
[`initial`] code.  For example:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
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

The value given to `set_language()` must be a two-character lowercase
[ISO-639-1] code.  For example, Spanish is `es`, French is `fr`, and
Arabic is `ar`.

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

## <a name="get_dialect"></a>get_dialect()

Returns the current dialect, as set by the `dialect` keyword argument
to the [`set_language()`] function.

## <a name="get_country"></a>get_country()

Returns the current country as a two-digit country code.  The default
country is `'US'`, unless a different default is set using the
[`country` configuration setting].

## <a name="set_country"></a>set_country()

Sets the current country.  Expects a two-digit, uppercase country code
such as `'US'`, `'GB'`, or `'DE'`.

## <a name="get_locale"></a>get_locale()

If the locale is set to `US.utf8`, `get_locale()` returns `US.utf8`.

## <a name="set_locale"></a>set_locale()

If you run `set_locale('FR.utf8')`, then `get_locale()` will return
`FR.utf8`, but the actual [Python locale] will not change
unless you run `update_locale()`.

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

Note that changes to the locale are not thread-safe.  This means that
there is a risk that between the time **docassemble** runs
`update_locale()` and the time it runs [`currency_symbol()`], another
user on the same server may cause **docassemble** to run
`update_locale()` and change it to the wrong setting.

If you want to host different interviews that use different locale
settings on the same server (e.g., to format a numbers as 1,000,000 in
one interview, but 1.000.000 in another), you will need to make sure
you run the **docassemble** web server in a multi-process,
single-thread configuration.  (See [installation] for instructions on
how to do that.)  Then you would need to begin each interview with
[`initial`] code such as:

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

# Access time functions

Internally, **docassemble** keeps track of the last time the interview
was accessed.  The following functions retrieve information about
access times.  These functions are particularly useful in
[scheduled tasks].

## <a name="last_access_time"></a>last_access_time()

`last_access_time()` returns a [`datetime`] object containing the last
time the interview was accessed by a user other than the special
[cron user].  The time is expressed in [UTC time] without a time zone.

Optionally, a role name or a list of role names can be provided.  In
this case, the function will return the latest access time by any user
holding one of the [roles].

* `last_access_time('client')`: returns the last time a user with the
  role of `client` accessed the interview.
* `last_access_time('advocate')`: returns the last time a user with
  the role of `advocate` accessed the interview.
* `last_access_time(['advocate', 'admin'])`: returns the last time a
  user with the role of `advocate` or `admin` accessed the interview.

By default, `last_access_time()` will ignore interview access by the
[cron user].  However, if you do not wish to ignore access by the
[cron user], you can call `last_access_time()` with the optional
keyword argument `include_cron` equal to `True`:

* `last_access_time(include_cron=True)`: returns the last time any
  user, including the [cron user] if applicable, accessed the
  interview.

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

# Functions for working with dates and times

## <a name="month_of"></a><a name="day_of"></a><a name="year_of"></a>month_of(), day_of(), and year_of()

These functions read a date and provide the parts of the date.

{% include side-by-side.html demo="date-parts" %}

The `month_of` function has an optional setting: if called as, e.g.,
`month_of(some_date, as_word=True)`, it will return the month as a
word (according to the current language and locale).

## <a name="format_date"></a>format_date()

The `format_date()` function takes as input a date, which could be
written in any format, and returns the date formatted appropriately
for the current language.

For example:

* `format_date("10/31/2016")` returns `October 31, 2016`.
* `format_date("2016-04-01")` returns `April 1, 2016`.
* `format_date("March 3, 2016")` returns `March 3, 2016`.
* `format_date('April 5, 2014', format='full')` returns `Saturday, April 5, 2014`.
* `format_date('April 5, 2014', format='short')` returns `4/5/14`.
* `format_date('April 5, 2014', format='M/d/yyyy')` returns `4/5/2014`.
* `format_date('April 5, 2014', format='MM/dd/yyyy')` returns
  `04/05/2014`.

For more information about how to specify date formats, see the
documentation for
[babel.dates](http://babel.pocoo.org/en/latest/api/dates.html).  The
`format` argument, which defaults to `long`, is passed directly to the
`babel.dates.format_date()` function.

## <a name="format_time"></a>format_time()

The `format_time()` function works just like [`format_date()`], except
it returns a time, rather than a date.

For example:

* `format_time("04:01:23")` returns `4:00 AM`.

For more information about how to specify time formats, see the
documentation for
[babel.dates](http://babel.pocoo.org/en/latest/api/dates.html).  The
`format` argument, which defaults to `short`, is passed directly to
the `babel.dates.format_time()` function.

## <a name="today"></a>today()

{% include side-by-side.html demo="today" %}

Returns today's date in long form according to the current locale
(e.g., `March 31, 2016`).  It is like `format_date()` in that it
accepts the optional keyword argument `format`.  It also takes an
optional keyword argument `timezone`, which refers to one of the time
zone names in [`timezone_list()`].

For example:

* `today(format='M/d/yyyy')`
* `today(timezone='US/Eastern')`

If the `timezone` is not supplied, the default time zone will be
used.

## <a name="timezone_list"></a>timezone_list()

{% include side-by-side.html demo="timezone-list" %}

The `timezone_list()` function returns a list of time zones that the
other date-related functions in **docassemble** understand.  The list
is generated from the [`pytz`] module.  The primary purpose of this
function is to include in a multiple choice question.

Note that the items in this list are strings, like `America/New_York`.

## <a name="get_default_timezone"></a>get_default_timezone()

{% include side-by-side.html demo="get-default-timezone" %}

The `get_default_timezone()` function returns the default timezone.
This is the time zone of the server, unless the default timezone is
set using the [`timezone` configuration].

## <a name="as_datetime"></a>as_datetime()

{% include side-by-side.html demo="as-datetime" %}

The `as_datetime()` function expresses a date as a [`datetime`]
object with a time zone.  It takes an optional keyword argument,
`timezone`, which will override the default time zone.

## <a name="current_datetime"></a>current_datetime()

{% include side-by-side.html demo="current-datetime" %}

The `current_datetime()` function returns the current date and time as
a [`datetime`] object.  It takes an optional keyword argument,
`timezone`, which will override the default time zone.

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
keyword argument `timezone` to use a different time zone.

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

## <a name="phone_number_in_e164"></a>phone_number_in_e164()

The `phone_number_in_e164()` function takes a phone number and formats
it into [E.164] format.  It takes an optional keyword argument
`country` that is used to determine the country code for the phone
number.  If `country` is not provided, the [`get_country()`] function
is used to determine the applicable country.

## <a name="phone_number_is_valid"></a>phone_number_is_valid()

The `phone_number_is_valid()` function takes a phone number and
returns `True` or `False` depending on whether the phone number is
valid.  It takes an optional keyword argument `country` that is used
to determine the country whose phone number standards should be used
to determine the validity of the phone number.  If `country` is not
provided, the [`get_country()`] function is used to determine the
applicable country.

# <a name="tasks"></a>Functions for tracking tasks

These are helpful functions for keeping track of whether certain tasks
have been performed.  For example, if your interview sends an e-mail
to the user about something, but you want to avoid sending the e-mail
more than once, you can give the "task" a name and use these functions
in your code to make sure your interview only sends the e-mail if it
has never been successfuly sent before.

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

# Simple translation of words

## <a name="word"></a>word()

`word()` is a general-purpose translation function that is used in the
code of the web application to ensure that the text the user sees is
translated into the user's language.

`word("fish")` will return `fish` unless
`docassemble.base.util.update_word_collection()` has been used to
define a different translation for the current language.

The following [Python interpreter] session demonstrates how it works:

{% highlight python %}
>>> from docassemble.base.util import *
>>> set_language('es')
>>> word("fish")
u'fish'
>>> import docassemble.base.util
>>> docassemble.base.util.update_word_collection('es', {'fish': 'pescado'})
>>> word("fish")
u'pescado'
>>> set_language('en')
>>> word("fish")
u'fish'
{% endhighlight %}

In your own [Python] code you may wish to use `word()` to help make
your code multi-lingual.

It is not a good idea to call
`docassemble.base.util.update_word_collection()` in interviews.  You
can use it in [Python] modules, but keep in mind that the changes you
make will have global effect within the [WSGI] process.  If other
interviews on the server define the same word translations for the
same language using `docassemble.base.util.update_word_collection()`,
the module that happened to load last will win, and the results could
be unpredictable.

The best practice is to load translations at the server level by using
the [`words`]<span></span> [configuration] directive to load translations from one or
more [YAML] files.  This causes **docassemble** to call
`docassemble.base.util.update_word_collection()` at the time the
server is initialized.

# <a name="linguistic"></a>Language-specific functions

These functions behave differently according to the language and
locale.  You can write functions for different languages, or reprogram
the default functions, by calling
`docassemble.base.util.update_language_function()`.

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
* `comma_and_list(things, oxford=False)` returns `lions, tigers and bears`.
* `comma_and_list('fish', 'toads', 'frogs')` returns `fish,
toads, and frogs`.
* `comma_and_list('fish', 'toads')` returns `fish and toads`
* `comma_and_list('fish')` returns `fish`.

## <a name="comma_list"></a>comma_list()

If `things` is a [Python list] with the elements
`['lions', 'tigers', 'bears']`, then `comma_list(things)` will return
`lions, tigers, bears`.

## <a name="currency"></a>currency()

If the locale is `US.utf8`, `currency(45.2)` returns `$45.20`.

`currency(45)` returns `$45.00`, but `currency(45, decimals=False)`
returns `$45`.

With `decimals` unset or equal to `True`, this function uses the
`locale` module to express the currency.  However, `currency(x,
decimals=False)` will simply return [`currency_symbol()`] followed by
`x` formatted as an integer, which might not be correct in your
locale.  This is due to a limitation in the [locale module].  If the
`currency` function does not meet your currency formatting needs, you
may want to define your own.

## <a name="currency_symbol"></a>currency_symbol()

If the locale is `US.utf8`, `currency_symbol()` returns `$`.

The locale can be set in the [configuration] or through the
[`set_locale()`] function.

If you set [`currency symbol`] in the [configuration], then
`currency_symbol()` returns the symbol specified there, and does not
use the locale to determine the symbol.

## <a name="indefinite_article"></a>indefinite_article()

{% include side-by-side.html demo="indefinite-article" %}

The English language version of this function passes all arguments
through to the `article()` function of [pattern.en].

`indefinite_article('bean')` returns `a bean` and
`indefinite_article('apple')` returns `an apple`.

## <a name="nice_number"></a>nice_number()

{% include side-by-side.html demo="nice-number" %}

* `nice_number(4)` returns `four`
* `nice_number(10)` returns `ten`
* `nice_number(11)` returns `11`
* `nice_number(-1)` returns `-1`

This function can be customized by calling
`docassemble.base.util.update_nice_numbers()`.

## <a name="noun_plural"></a>noun_plural()

{% include side-by-side.html demo="noun-plural" %}

The English language version of this function passes all arguments
through to the `pluralize()` function of [pattern.en].

* `noun_plural('friend')` returns `friends`
* `noun_plural('fish')` returns `fish`
* `noun_plural('moose')` returns `mooses`

You can also pass a number as a second argument to the function.  If
the number is 1, the first argument will be returned, untouched;
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
* `ordinal_number(11)` returns `11th`.

This function can be customized with
`docassemble.base.util.update_ordinal_numbers()` and
`docassemble.base.util.update_ordinal_function()`.

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
`docassemble.base.util.update_word_collection()` function.  If you
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
---
modules:
  - docassemble.base.util
---
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

# Simple language functions

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

Note that unlike other functions in [`docassemble.base.util`], these
functions are *not* available for use within interviews.  If you do:

{% highlight yaml %}
modules:
  - docassemble.base.util
{% endhighlight %}

you will *not* be able to write things like `${ her('dog') }`.

These functions are intended to be used from within [Python modules], where you
can import them by doing:

{% highlight python %}
from docassemble.base.util import his, her
{% endhighlight %}

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

# <a name="functions"></a>Miscellaneous functions

## <a name="server_capabilities"></a>server_capabilities()

The `server_capabilities()` function returns a dictionary indicating
whether the server has particular features enabled.  The keys are:

* `sms` - whether SMS messaging is available.  See the [`twilio`]
  configuration.
* `google_login` - whether logging in with Google is available.  See
  the [`oauth`] configuration.
* `facebook_login` - whether logging in with Facebook is available.
  See the [`oauth`] configuration.
* `voicerss` - whether the text-to-speech feature is available.  See
  the [`voicerss`] configuration.
* `s3` - whether [Amazon S3] is enabled.  See the [`s3`]
  configuration.
* `azure` - whether [Azure blob storage] is enabled.  See the [`azure`]
  configuration.

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
value is defined, returns None.

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

`objects_from_file()` imports data from a [YAML] file, including
objects.

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

### Using your own object types

If you want to import objects that are not standard **docassemble**
[objects], you need to specify a `module` that defines the object's
class so that **docassemble** knows where to get the class definition.

For example, suppose you defined some classes with a [Python module]
called [`fish.py`]:

{% highlight python %}
from docassemble.base.core import DAObject

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
directive.  This indicates that the `Halibut` and `Food` classes are
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
  language must be either a two-character lowercase [ISO-639-1] code
  or a language code that [Tesseract] uses.
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

The `language` parameter is flexible; you can set it to a language
code that [Tesseract] supports (e.g., `eng`, `chi-sim`, `chi-tra`,
`slk-frak`), or you can give it a two-character [ISO-639-1] code, in
which case **docassemble** will convert it to the corresponding
[Tesseract] code.  If [Tesseract] does not support the language,
English will be used.  If the `language` parameter is not supplied,
**docassemble** will use the default language (the result of
`get_language()`), which is always a two-character [ISO-639-1] code.

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
is assigned to an interview variable, you can reliably obtain the file
path by calling the [`.path()`] method on the variable.

The `path_and_mimetype()` function can be used along with the
[`.set_mimetype()`] and [`.copy_into()`] methods of the [`DAFile`]
class in order to save files to [`DAFile`] objects.

The following interview retrieves an image from the Internet and saves
it to a variable `logo`, which is a [`DAFile`] object.

{% include side-by-side.html demo="save-url-to-file" %}

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

This function is integrated with other classes in
[`docassemble.base.util`] and [`docassemble.base.core`].

* `to` expects a [list] of recipients.  The list can consist of
  [`Individual`]s (or any other [`Person`]s), objects of type
  [`phonenumbers.PhoneNumber`], or a simple string containing a phone number.
* `body` expects text, or `None`.  If provided, it will be the content
  of the message.  Markdown will be converted to plain text.
* `template` expects a [`DATemplate`] object, or `None`.  These
  templates can be created in an interview file using the `template`
  directive.  The "subject" of the template, if provided, will be the first
  line of the message.
* `task` expects the name of a [task].  If this argument is provided,
  and if sending the text message is successful, the task will be
  marked as having been performed (i.e., [`mark_task_as_performed()`]
  will be called).  Alternatively, you can handle this in your own
  code, but you might find it convenient to let the `send_email()`
  function handle it for you.
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

When the recipients are [`Individual`]s or [`Person`]s, the
`mobile_number` attribute will be used, but only if it already exists.
Otherwise, the `phone_number` attribute will be used, and sought if it
is not already defined.

Note that [Twilio] expects the phone number to be expressed in [E.164]
format, which includes the country code (e.g., 1 for the United
States).  However, users do not typically write phone numbers in such
a way.  Therefore, the [`phonenumbers`] package is used to convert
phone numbers to [E.164] based on the applicable country.  If an
[`Individual`] or [`Person`] is the recipient, the `country`
attribute, if it exists, will be used to determine the country.
Otherwise, the [`get_country()`] function is used to determine the
applicable country.  Your interview can use [`set_country()`] in
[`initial`] code to set a default country, or you can set a default on
a server level by setting the [`country` configuration directive].
The country must be specified as a two-letter, capitalized
abbreviation.

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
  interview or start a fresh interview.  Set this to `True` if you
  want the [SMS] user to start a fresh interview.  If `new` is not
  specified, the [SMS] user will join the interview that was ongoing
  when the call to `initiate_sms_session()` was made.
* `send` - this controls whether the invitation message should be sent
  or not.  If `send` is not specified, the message will be sent.  Set
  this to `False` to suppress sending the message.  If `send` is
  `False`, the [SMS] session will still be created.  The fact that the
  session is created means that if an [SMS] message is received from
  the given phone number, the [SMS] user will receive a response as if
  the interview had already been started.  The user's initial message
  will not be interpreted as a choice of an interview from the
  `dispatch` section of the [`twilio`] configuration.
* `config` - this controls which [Twilio] phone number is used for
  communication.  You would only need to use this if you have more
  than [more than one `twilio` configuration directive] set up in your
  [configuration].

If you are not using `new=True`, note that there may be a delay
between the time the message is sent to the [SMS] user and the time
the [SMS] user sees the message and responds.  The [SMS] user will
join the interview at whatever state the interview is in at the time
the [SMS] user responds.  **docassemble** does not make a
copy of the interview state when the call to `initiate_sms_session()`
is made.

Here is an example interview that solicits input into the interview
through [SMS].

{% highlight yaml %}
modules:
  - docassemble.base.util
---
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
user had been in the middle of an interview, the user will not be able
to get back to the interview.

# <a name="storage"></a>Storing data

## <a name="redis"></a>With Redis

If you do not know what a [Redis] server is, skip this section!

The [background processes] feature of **docassemble** depends on a
[Redis] server being available.  The server is also used to facilitate
[live chat].

Interview authors may want to make use of the [Redis] server for
purposes of storing information across users of a particular
interview, keeping usage statistics, or other purposes.

{% include side-by-side.html demo="redis" %}

To use the [Redis] server, use an [`objects`] section to create an
object of type `DARedis`.  This object can now be used to
communicate with the redis server, much as though it had been created
by calling `redis.StrictRedis()`.

## <a name="sql"></a>With SQL

Since [Redis] is an [in-memory database], it is not appropriate for
long-term storage or for the storage of large amounts of data.

An alternative is to store data in SQL.  **docassemble** provides three
functions that allow you to store, retrieve, and delete data.

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

### Advanced SQL storage

Though the data are stored on a SQL server, you cannot use SQL queries
to retrieve data stored by `write_record()`; you can only use
`read_records()` to retrieve data.

If you want to use the full power of SQL in your interviews, you can
write a module that does something like this:

{% highlight python %}
from docassemble.base.util import get_config
import psycopg2

def get_conn():
    dbconfig = get_config('db')
    return psycopg2.connect(database=dbconfig.get('name'),
                            user=dbconfig.get('user'),
                            password=dbconfig.get('password')
                            host=dbconfig.get('host')
                            port=dbconfig.get('port'))
def some_function(id, thing):
    conn = get_conn()
    cur = conn.get_cursor()
    cur.execute("update foo set bar=%s where id=%s", (thing, id))
    conn.commit()
    cur.close()
{% endhighlight %}

This assumes the [`db`] configuration refers to a [PostgreSQL]
database.  If you connect to the database with the credentials from
[`db`], you have the power to create and drop tables.

# <a name="docx"></a>Functions for working with .docx templates

## <a name="raw"></a>raw()

This function is only used in the context of an [`attachments`] block
that uses a [`docx template file`] and values are passed to the .docx
template using the `code` or `field code` methods.

Normally, all values that you transfer to a .docx template with `code`
or `field code` are converted so that they display appropriately in
your .docx file.  For example, if the value is a [`DAFile`] graphics
image, it will be displayed in the .docx file as an image.  Or, if the
value contains [document markup] codes that indicate line breaks,
these will display as actual line breaks in the .docx file, rather
than as codes like `[BR]`.

However, if your .docx file uses advanced template features, such as
for loops, this conversion might cause problems for you.  By passing a
value `val` as `raw(val)`, you will ensure that the template sees the
original value of `val`, not a converted value.

For example, suppose you have a variable `fruit_list` that is defined
as a [`DAList`] with items `['apples', 'oranges']`, and you pass it to
a .docx template as follows.

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

Now, the resulting .docx file will contain:

> Don't forget to bring apples!
> Don't forget to bring oranges!

Note that another way to pass "raw" values to a .docx template is to
use a list of [`raw field variables`].

Moreover, the easiest way to pass "raw" values is to omit `field`,
`field code`, `field variables`, `code`, and `raw field variables`
entirely, so that your .docx file is [assembled] using your full set
of interview variables.

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

# <a name="javascript"></a>Javascript functions

If you know how to program in [Javascript], you can include
browser-side code in your interviews using [`script`], [`html`], and
[`css`] elements within a [`fields`] block, or you can put
[Javascript] and [CSS]<span></span> [static files] in your [packages]
and bring them into your interview using the [`javascript`] and
[`css`]({{ site.baseurl }}/docs/initial.html) directives within a
[`features`] block.

The following [Javascript] functions are available for your use in
your [Javascript] code.

## <a name="js_url_action"></a>url_action()

The `url_action()` function, like its [Python namesake](#url_action),
returns a URL that will run a particular action in the interview.  The
first parameter is the [action] to run, and the second
parameter is an object containing the arguments to provide to the
action (to be read with [`action_argument()`]).

{% include side-by-side.html demo="js_url_action" %}

## <a name="js_url_action_call"></a>url_action_call()

The `url_action_call()` function is like
[`url_action()`](#js_url_action), except it makes an [Ajax] call to
the URL and runs a callback function when the server responds to the
request.  In combination with [`json_response()`], this can allow you
to write [Javascript] code that interacts with the server.

The [Javascript] function takes three arguments:

1. The [action] to take.  This corresponds with the name of an
   [`event`] in your interview.
2. An object containing arguments to pass to the [action].  In your
   interview, you can use the [`action_argument()`] function to read
   these values.
3. A callback function that will be run when the [Ajax] call returns.
   This function takes a single argument (`data` in this example),
   which is the return value of `json_response()`.

{% include side-by-side.html demo="js_url_action_call" %}

This example takes advantage of the [CSS] classes `btn` and
`btn-primary` that are available in [Bootstrap].  See the
[Bootstrap documentation] for more information about using these
classes.

Note that [Ajax] interactions with the interview are possible without
writing any [Javascript] code; see the [`check in` feature].

## <a name="js_get_interview_variables"></a>get_interview_variables()

If you would like to work with all of the variables in the interview
in your [Javascript] code, you can do so with the
`get_interview_variables()` function, which sends an [Ajax] call to
the server to retrieve the contents of the interview dictionary.

The function takes a single argument, which is the callback function.
The callback function is given one parameter, which is an object
having the following attributes:

* `success`: this will be `True` if the call succeeds, `False`
otherwise.
* `variables`: this will be an object containing the interview
  variables in the format produced by [`all_variables()`].
* `i`: the current interview [YAML] file.
* `uid`: the current session ID.
* `encrypted`: whether the interview dictionary is encrypted.
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

## <a name="js_daPageLoad"></a>Running Javascript at page load time

When your [Javascript] code is imported through the [`javascript`]
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
[Docker]: {{ site.baseurl }}/docs/docker.html
[Flask-Mail]: https://pythonhosted.org/Flask-Mail/
[HTML]: https://en.wikipedia.org/wiki/HTML
[JSON]: https://en.wikipedia.org/wiki/JSON
[Markdown]: https://daringfireball.net/projects/markdown/
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python function]: https://docs.python.org/2/tutorial/controlflow.html#defining-functions
[Python functions]: https://docs.python.org/2/tutorial/controlflow.html#defining-functions
[Python interpreter]: https://docs.python.org/2/tutorial/interpreter.html
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[Python locale]: https://docs.python.org/2/library/locale.html
[Python module]: https://docs.python.org/2/tutorial/modules.html
[Python modules]: https://docs.python.org/2/tutorial/modules.html
[Python set]: https://docs.python.org/2/library/stdtypes.html#set
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[YAML]: https://en.wikipedia.org/wiki/YAML
[`Address`]: {{ site.baseurl }}/docs/objects.html#Address
[`DAFileCollection`]: {{ site.baseurl }}/docs/objects.html#DAFileCollection
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`.path()`]: {{ site.baseurl }}/docs/objects.html#DAFile.path
[`.set_mimetype()`]: {{ site.baseurl }}/docs/objects.html#DAFile.set_mimetype
[`.copy_into()`]: {{ site.baseurl }}/docs/objects.html#DAFile.copy_into
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`DATemplate`]: {{ site.baseurl }}/docs/objects.html#DATemplate
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
[`default role`]: {{ site.baseurl }}/docs/initial.html#default role
[`docassemble.base.core`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/core.py
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
[`words`]: {{ site.baseurl }}/docs/config.html#words
[action]: #url_action
[`attachment`]: {{ site.baseurl }}/docs/documents.html
[`attachments`]: {{ site.baseurl }}/docs/documents.html
[attachments]: {{ site.baseurl }}/docs/documents.html
[classes]: https://docs.python.org/2/tutorial/classes.html
[configuration]: {{ site.baseurl }}/docs/config.html
[dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[fields]: {{ site.baseurl }}/docs/fields.html
[function]: https://docs.python.org/2/tutorial/controlflow.html#defining-functions
[functions]: #functions
[how **docassemble** runs your code]: {{ site.baseurl }}/docs/logic.html#howitworks
[html2text]: https://pypi.python.org/pypi/html2text
[initial block]: {{ site.baseurl }}/docs/initial.html
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[installation]: {{ site.baseurl }}/docs/installation.html
[interview logic]: {{ site.baseurl }}/docs/logic.html
[keyword argument]: https://docs.python.org/2/glossary.html#term-argument
[keyword arguments]: https://docs.python.org/2/glossary.html#term-argument
[language support]: {{ site.baseurl }}/docs/language.html
[list]: https://docs.python.org/2/tutorial/datastructures.html
[locale module]: https://docs.python.org/2/library/locale.html
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
[UTC time]: https://en.wikipedia.org/wiki/Coordinated_Universal_Time
[`timezone_list()`]: #timezone_list
[`pytz`]: http://pytz.sourceforge.net/
[`timezone` configuration]: {{ site.baseurl }}/docs/config.html#timezone
[`datetime.timedelta`]: https://docs.python.org/2/library/datetime.html#datetime.timedelta
[`dateutil.relativedelta.relativedelta`]: http://dateutil.readthedocs.io/en/stable/relativedelta.html
[`datetime`]: https://docs.python.org/2/library/datetime.html#datetime.datetime
[`action_argument()`]: #action_argument
[`action_arguments()`]: #action_arguments
[HTTPS]: {{ site.baseurl }}/docs/docker.html#https
[QR code]: https://en.wikipedia.org/wiki/QR_code
[Profile page]: {{ site.baseurl }}/docs/users.html#profile
[country code]: http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[`task_performed()`]: {{ site.baseurl }}/docs/functions.html#task_performed
[`task_not_yet_performed()`]: #task_not_yet_performed
[`mark_task_as_performed()`]: #mark_task_as_performed
[`times_task_performed()`]: #times_task_performed
[`set_task_counter()`]: #set_task_counter
[task]: #tasks
[actions]: #actions
[`format_date()`]: #format_date
[`format_time()`]: #format_time
[`user_info()`]: #user_info
[`user_logged_in()`]: #user_logged_in
[`user_has_privilege()`]: #user_logged_in
[`def` block]: {{ site.baseurl }}/docs/initial.html#def
[`def` blocks]: {{ site.baseurl }}/docs/initial.html#def
[`response()`]: #response
[`command()`]: #command
[`message()`]: #message
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
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
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
[pickled]: https://docs.python.org/2/library/pickle.html
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
[Bootstrap documentation]: http://getbootstrap.com/css/
[`check in` feature]: {{ site.baseurl }}/docs/background.html#check in
[Amazon S3]: https://aws.amazon.com/s3/
[e-mail to interview]: {{ site.baseurl }}/docs/background.html#email
[`interview_email()`]: #interview_email
[`get_emails()`]: #get_emails
[`subdivision_type()`]: #subdivision_type
[`incoming mail domain`]: {{ site.baseurl }}/docs/config.html#incoming mail domain
[interaction of user roles and actions]: {{ site.baseurl }}/docs/users.html#users and actions
[`contacts.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/sources/contacts.yml
[associative array]: https://en.wikipedia.org/wiki/Associative_array
[`fish.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/fish.py
[`fishes.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/sources/fishes.yml
[standard Python notation]: https://docs.python.org/2/tutorial/modules.html#intra-package-references
[`docassemble.demo`]: https://github.com/jhpyle/docassemble/tree/master/docassemble_demo/docassemble/demo
[`docassemble.demo` package on GitHub]: https://github.com/jhpyle/docassemble/tree/master/docassemble_demo/docassemble/demo
[GitHub]: https://github.com/
[sources folder]: {{ site.baseurl }}/docs/playground.html#sources
[`datetime.datetime`]: https://docs.python.org/2/library/datetime.html#datetime-objects
[`__init__()`]: https://docs.python.org/2/reference/datamodel.html#object.__init__
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
[assembled]: {{ site.baseurl }}/docs/documents.html#docx template file
[`.comma_and_list()`]: {{ site.baseurl }}/docs/objects.html#DAList.comma_and_list
