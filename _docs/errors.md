---
layout: docs
title: Debugging
short_title: Debugging
---

# Debugging interviews

Errors are a natural part of developing an interview.

There are a variety of tools to help you figure out what went wrong
and fix it.

Make sure your [Configuration] is set up with the [`debug`] directive
set to `True`.

If your interview is showing a screen that it shouldn't, try opening
the "Source" tab.  This will provide you with a report about how
**docassemble** reached the screen it is showing.  (You may need to
scroll down to see the report.)  At the bottom of the page is a link
called "Show variables and values."  If you click this, a browser tab
will open and you will see a [JSON] representation of the variables
that had been defined before the error occurred.  (If your interview
generated an error on the very first screen, however, the variables
will not be available.)  The location of this screen is simply
`/vars`.

A common debugging technique is to print messages at various points in
your code.  You can use the [`log()`] function to do this.  The
messages will be available in the file called `docassemble.log` in the
"Logs" interface from the main menu.  You can also use [`log()`] to
log the messages to the browser console or to the screen.

# Errors in docx templates

If you are using the [`docx template file`] feature and you get an
error that relates to your template, it can be difficult to figure out
exactly where your error is located.  Some tips:

* Review your interview carefully to make sure that each `if`
  statement is matched with an `endif` statement, and every `for` statement is
  matched with an `endfor` statement.  Make sure that every `{% raw %}{{{% endraw %}` is
  matched with a `{% raw %}}}{% endraw %}`.
* Make sure you are using `{% raw %}{%p ... %}{% endraw %}` tags only in
  contexts where you want the entire current paragraph in Word to be
  replaced with the contents of the tag.  If you are using an inline
  tag, use `{% raw %}{% ... %}{% endraw %}` instead.

# I have a question that defines my variable, why isn't it being used?

Note that **docassemble** objects can go by different names, but they
are only "self-aware" about having one intrinsic identity.

For example, suppose that you do the following: 

{% highlight yaml %}
objects:
  - user.coworkers: DAList
  - user.friends: DAList
---
mandatory
code: |
  if user.works_all_the_time:
    user.friends = user.coworkers
---
question: |
  What is 
  ${ user.friends[i].possessive('birthdate') }?
fields:
  - Birthdate: user.friends[i].birthdate
    datatype: date
{% endhighlight %}

You might expect that if the interview needs to know the birthday of
one of the user's friends, it will ask the last question.  However,
the list `user.friends` was initialized as `user.coworkers`.  This
means that if you refer to `user.friends[1].birthdate`, your interview
will actually look for `user.coworkers[1].birthdate`.

For more information about this issue, see the documentation for the
base class of all **docassemble** objects, [`DAObject`].

# Common error messages

Here are some error messages you might encounter in **docassemble**
and how to avoid them.

> can't pickle module objects

Interview variables are stored in a Python dictionary.  This
dictionary is passed to [Mako] and [exec] and becomes the environment
of global variables in which templates are assembled and [`code`] blocks
are executed.  The web app uses [pickle] to serialize this dictionary
for storage in a SQL database.  Many different types of data are
[pickleable], but not all are.

If a variable is added to the user dictionary that cannot be pickled,
this error will result.

Before pickling a user dictionary, **docassemble** loops through the
keys in the dictionary and removes modules, functions, types, and
builtins.  For this reason, it is safe (and normal) to [import]
modules and function names into the namespace of the user dictionary.

However, **docassemble** does not recurse through all of the list
items and object attributes of every object it stores, so it is up to
you to avoid setting list items or object attributes to values that
are not [pickleable].

> Docassemble has finished executing all code blocks marked as initial
> or mandatory, and finished asking all questions marked as mandatory
> (if any).  It is a best practice to end your interview with a
> question that says goodbye and offers an Exit button.

If you see this message, it is because **docassemble** was able to go
through all the questions of your interview and reach the end without
encountering any questions to ask of the user.

Perhaps you forgot to mark any questions or code blocks as mandatory.
Or perhaps you forgot to create a user-friendly question for the end
of the interview.

You can prevent this error from appearing by adding a question such as
the following:

{% highlight yaml %}
---
question: Goodbye, world!
mandatory: True
buttons
  - Exit: exit
---
{% endhighlight %}

> AssertionError: A blueprint's name collision occurred between
> <flask.blueprints.Blueprint object at 0x7fab5a780850> and
> <flask.blueprints.Blueprint object at 0x7fab59da1b90>.  Both
> share the same name "flask_user".  Blueprints that are created
> on the fly need unique names.

If you get this error, try restarting the web server.  Normally,
"touch"ing the [WSGI] file succeeds at restarting the server, but
sometimes it does not, and this error appears.

If that does not solve the problem, try reinstalling the [Flask]
packages.  Also make sure that you do not have multiple versions of
[Flask] installed at the same time (e.g., one version in `/usr/lib`
and another in `/usr/local/lib`).

# Unexplained errors

If you run into a problem where you think you did everything right,
but you are getting a strange error, the problem might be that your
interview uses a [variable name] that is being used for some other
purpose.  See [reserved variable names] for a list of variable names
that you cannot use.  If this is the problem, the solution is simply
to change the name of your variable to something else.

# Get help

To get help from the community of developers and other users, you can
submit questions to the [docassemble mailing list] or chat in real
time with other users on the [**docassemble** Slack group].

# Report an issue

If you encounter an error that you think is a problem with
**docassemble** rather than with your interview, please create an
"issue" on the [issues page].  The developers will be happy to sort
out the problem.

[docassemble mailing list]: https://mail.python.org/mm3/mailman3/lists/docassemble.python.org/
[**docassemble** Slack group]: https://join.slack.com/t/docassemble/shared_invite/enQtMjQ0Njc1NDk0NjU2LTAzYzY5NWExMzUxNTNhNjUyZjRkMDg0NGE2Yjc2YjI0OGNlMTcwNjhjYzRhMjljZWU0MTI2N2U0MTFlM2ZjNzg
[issues page]: {{ site.github.repository_url }}/issues
[variable name]: {{ site.baseurl }}/docs/fields.html#variable names
[reserved variable names]: {{ site.baseurl }}/docs/special.html#reserved
[Flask]: http://flask.pocoo.org/
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[Mako]: http://www.makotemplates.org/
[exec]: https://docs.python.org/2.0/ref/exec.html
[pickle]: https://docs.python.org/2/library/pickle.html
[pickleable]: https://docs.python.org/2/library/pickle.html#what-can-be-pickled-and-unpickled
[import]: https://docs.python.org/2/tutorial/modules.html
[`code`]: {{ site.baseurl }}/docs/code.html
[Configuration]: {{ site.baseurl }}/docs/config.html
[`debug`]: {{ site.baseurl }}/docs/config.html#debug
[`log()`]: {{ site.baseurl }}/docs/functions.html#log
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[JSON]: https://en.wikipedia.org/wiki/JSON
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
