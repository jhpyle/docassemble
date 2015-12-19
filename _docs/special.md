---
layout: docs
title: Special Variables
short_title: Special Variables
---

# Variables set by **docassemble**.

There are some special variables that **docassemble** sets in every
interview's variable store.

## _internal

`_internal` is a [Python dictionary] that is used by **docassemble**
but that is not intended to be used in interviews.

## url_args

`url_args` is a [Python dictionary] that is used to access parameters
passed via URL.

Users start an interview by going to a URL.  A basic URL would look
like this:

{% highlight text %}
http://example.com/da?i=docassemble.example_inc:data/questions/survey.yml
{% endhighlight %}

Here, the only parameter is `i`, the interview file name.

It is possible to use the URL to pass special parameters to the
interview code.  For example, if the user started the interview by
clicking on the following link:

{% highlight text %}
http://example.com/da?i=docassemble.example_inc:data/questions/survey.yml&from=web
{% endhighlight %}

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

## current_info

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

## role_needed

If you use the [multi-user interview feature] and the user reaches a
point in the interview where input is needed from a different user
before proceeding, **docassemble** will look for a `question` that
offers to sets `role_event`, and ask that question.  **docassemble**
will set the variable `role_needed` to a list of roles capable of
answering the next question in the interview.

# Variables that interviews can set

## role

If you use the [multi-user interview feature], your interview will
need to have a `default role` [initial block] containing code that
sets the variable `role` to the user's role.

## speak_text

If this special variable is set to `True`, **docassemble** will
present the user with an HTML5 audio control at the top of the page.
When the user clicks it, **docassemble** will access the [VoiceRSS]
web service to convert the text of the question to an audio file and
then play that audio back for the user.  This requires enabling the
`voicerss` setting in the [configuration.

Since the [VoiceRSS] service costs money above the free usage tier,
**docassemble** does not send the request to [VoiceRSS] until the user
presses "Play" on the audio control.  It also caches the results and
reuses them whenever possible.

## track_location

[VoiceRSS]: http://www.voicerss.org/
[get]: https://docs.python.org/2/library/stdtypes.html#dict.get
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[initial block]: {{ site.baseurl }}/docs/initial.html
[configuration]: {{ site.baseurl }}/docs/config.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[multi-user interview feature]: {{ site.baseurl }}/docs/roles.html
