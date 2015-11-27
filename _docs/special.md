---
layout: docs
title: Special Variables
short_title: Special Variables
---

There are some special variables that **docassemble** sets in every
interview's variable store.

# _internal

`_internal` is a [Python dictionary] that is used by **docassemble**
but that is not intended to be used in interviews.

# url_args

`url_args` is a [Python dictionary] that is used to access parameters
passed via URL.

Users start an interview by going to a URL.  A basic URL would look
like this:

    http://example.com/da?i=docassemble.example_inc:data/questions/survey.yml

Here, the only parameter is `i`, the interview file name.

It is possible to use the URL to pass special parameters to the
interview code.  For example, if the user started the interview by
clicking on the following link:

    http://example.com/da?i=docassemble.example_inc:data/questions/survey.yml&from=web

then the interview would load as usual, and the interview code could
access the value of the `from` parameter by looking in the `url_args`
variable in the variable store.  For example, the interview could
contain the following code:

{% highlight yaml %}
---
code: |
  if 'from' in url_args:
    origin_of_interviewee = url_args['from']
  else:
    origin_of_interviewee = 'unknown'
---
mandatory: true
question: You came from the ${ origin_of_interviewee }.
---
{% endhighlight %}

Alternatively, you could use [Python]'s [get] method to do the same
thing in less space:

{% highlight yaml %}
---
mandatory: true
question: You came from the ${ url_args.get('from', 'unknown') }.
---
{% endhighlight %}

You can test this out by trying the following links:

* [https://docassemble.org/demo?i=docassemble.demo:data/questions/testurlarg.yml&from=web](https://docassemble.org/demo?i=docassemble.demo:data/questions/testurlarg.yml&from=web){:target="_blank"}
* [https://docassemble.org/demo?i=docassemble.demo:data/questions/testurlarg.yml&from=moon](https://docassemble.org/demo?i=docassemble.demo:data/questions/testurlarg.yml&from=moon){:target="_blank"}

As soon as the interview loads, the parameters will no longer appear
in the browser's location bar.  Nevertheless, the parameters remain
available in the `url_args` dictionary for the life of the interview.

Moreover, you can set new `url_args` at any time during the course of
the interview.  For example:

{% highlight yaml %}
---
mandatory: true
question: You came from the ${ url_args.get('from', 'unknown') }.
subquestion: |
  % if url_args.get('fruit', 'apple') == 'apple':
  I think your favorite fruit is an apple, but [click here](?fruit=orange)
  if you disagree.
  % else:
  I see that your favorite fruit is not an apple.
  % endif
---
{% endhighlight %}

You can test this out by trying the following link:
[https://docassemble.org/demo?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder](https://docassemble.org/demo?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder){:target="_blank"}.

# current_info

`current_info` is a [Python dictionary] that is defined by
**docassemble** every time a screen loads.  It allows interviews to
access certain information from **docassemble**, such as the identity
of the person logged in and other information.

`current_info` contains the following keys:

* `default_role` - the default role for the interview, as defined by
  the `default role` [initial block];
* `session` - the session key, which is a secret identifier that
  unlocks access to the variable store of the user's interview.  If
  passed as the `session` parameter of a URL, the interview will load
  using the variable store for that session key.
* `url` - the base URL of the docassemble application (e.g.,
  `http://docassemble.org/demo`).
* `user` - a [Python dictionary] containing the following keys:
  * `is_authenticated` - whether the user is logged in (True or False)
  * `is_anonymous` - whether the user is not logged in (True or False)
  * `email` - the user's e-mail address
  * `theid` - the unique ID of the user
  * `roles` - a [Python list] containing the user's roles, as defined
    by a site administrator.  (Administrators can change user roles on
    the User List page.)
  * `firstname` - the user's first name.  This and the following can
    all be set by the user on the User Profile page.
  * `lastname` - the user's last name.
  * `country` - the user's country.
  * `subdivisionfirst` - in the U.S., the state.
  * `subdivisionsecond` - in the U.S., the county.
  * `subdivisionthird` - in the U.S., the municipality.
  * `organization` - the user's organization.
* `yaml_filename` - the filename of the current interview, in the
  package:path form (e.g., `docassemble.demo:data/questions/questions.yml`)

[get]: https://docs.python.org/2/library/stdtypes.html#dict.get
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[initial block]: {{ site.baseurl }}/docs/initial.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
