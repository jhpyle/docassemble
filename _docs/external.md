---
layout: docs
title: External data
short_title: External data
---

# <a name="url_args"></a>URL arguments

As explained in the [invocation] section, when a user starts an
interview, the user visits a URL.  This URL can contains parameters of
your own choosing (as long as the names do not conflict with any of
the [reserved URL parameters]).  Data passed using these parameters is
available inside the interview session using the [`url_args` special
variable].

You can also change the [`url_args`] during an active interview
session.  If the user's browser is logged into a session, and the user
clicks on a hyperlink to the same interview with URL parameters set,
the [`url_args`] will be updated.

[`url_args`]: {{ site.baseurl }}/docs/special.html#url_args
[`url_args` special variable]: {{ site.baseurl }}/docs/special.html#url_args
[reserved URL parameters]: {{ site.baseurl }}/docs/special.html#reserved url parameters
[invocation]: {{ site.baseurl }}/docs/interviews.html#invocation

# <a name="actions"></a>Using the "actions" system

The normal flow of an interview in **docassemble** is as follows:

1. The screen loads, and the user sees whatever [`question`] is the
   next step in the [interview logic], given the current state of the
   interview answers.
2. The user enters some information (if the screen asks for
   information) and then presses a button.
3. The interview answers are updated with the new information.
4. Go back to step 1.

Eventually, the interview will reach a logical endpoint.  This flow
makes sense for the main path of the interview, but sometimes the user
needs to deviate from the main path.  For example, they might want to
adjust their answers to previous questions.

In **docassemble**, "actions" are used to trigger deviations from the
main path of the [interview logic].  For example, suppose that under
the [main path] of the [interview logic], the next piece of
information that is necessary to gather is `favorite_legume`.  The
interview will show a [`question`] that offers to define
`favorite_legume`.  But suppose you want the user to be able to go
back to the `favorite_vegetable` question.  (Perhaps a common mistake
is for users to list a legume as their favorite vegetable).  You can
allow the user to launch an "action" that causes the interview to seek
(or in this case, re-seeks) the variable `favorite_vegetable` instead of
the variable `favorite_legume`.

{% highlight text %}
question: |
  What is your favorite legume?
subquestion: |
  You said your
  [favorite vegetable](${ url_action('favorite_vegetable') })
  was
  ${ favorite_vegetable }.
fields:
  Legume: favorite_legume
{% endhighlight %}

For more information about "actions," see the documentation for
[`url_action()`] and [`url_ask()`].

Another type of deviation from the main interview logic is a
[background action].  This is where some code runs on the server,
in the background, where the user can't see anything.  This is
typically used for code that takes a long time to run, where you don't
want the user to have to wait for the result, or there is a danger
that the user's browser will time out if the server does not respond
quickly enough.

[background action]: {{ site.baseurl }}/docs/background.html#background
[`url_ask()`]: {{ site.baseurl }}/docs/functions.html#url_ask
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[interview logic]: {{ site.baseurl }}/docs/logic.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question

## <a name="push"></a>Pushing information into a session

Typically, users launch actions by clicking hyperlinks


## <a name="pull"></a>Pulling information out of a session

# <a name="email from"></a>E-mail

## <a name="email from"></a>Sending e-mail from a session

## <a name="email to"></a>Sending e-mail to a session

# <a name="sms"></a>Sending text messages from a session

# <a name="persist data"></a>Persisting data

## <a name="sql"></a>Saving to SQL

## <a name="redis"></a>Saving to Redis

## <a name="persist files"></a>Persistent files

# <a name="api"></a>Using the API

# <a name="third party api"></a>Using third-party APIs

