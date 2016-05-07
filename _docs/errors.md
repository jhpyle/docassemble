---
layout: docs
title: Error messages
short_title: Errors
---

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
mandatory: true
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

[Flask]: http://flask.pocoo.org/
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[Mako]: http://www.makotemplates.org/
[exec]: https://docs.python.org/2.0/ref/exec.html
[pickle]: https://docs.python.org/2/library/pickle.html
[pickleable]: https://docs.python.org/2/library/pickle.html#what-can-be-pickled-and-unpickled
[import]: https://docs.python.org/2/tutorial/modules.html
[`code`]: {{ site.baseurl }}/docs/code.html
