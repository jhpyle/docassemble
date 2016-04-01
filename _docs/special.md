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

* [https://demo.docassemble.org?i=docassemble.demo:data/questions/testurlarg.yml&from=web](https://demo.docassemble.org?i=docassemble.demo:data/questions/testurlarg.yml&from=web){:target="_blank"}
* [https://demo.docassemble.org?i=docassemble.demo:data/questions/testurlarg.yml&from=moon](https://demo.docassemble.org?i=docassemble.demo:data/questions/testurlarg.yml&from=moon){:target="_blank"}

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
[https://demo.docassemble.org?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder](https://demo.docassemble.org?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder){:target="_blank"}.

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
  `http://demo.docassemble.org`).
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
  * `location` - if `track_location` (see below) is set to true, and
    the user's location is successfully obtained, this entry will
    contain a dictionary with the keys `latitude` and `longitude`,
    indicating the user's location.
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
`voicerss` setting in the [configuration].

Since the [VoiceRSS] service costs money above the free usage tier,
**docassemble** does not send the request to [VoiceRSS] until the user
presses "Play" on the audio control.  It also caches the results and
reuses them whenever possible.

## track_location

If set to `True`, the web app will attempt to obtain the user's
position, based on GPS or any other geolocation feature enabled in the
browser.  The result is stored in the `current_info` dictionary (see
above).

The most common way to use this feature is as follows:

{% highlight yaml %}
---
include:
  - basic-questions.yml
---
initial: true
code: |
  track_location = user.location.status()
---
{% endhighlight %}

This will cause `track_location` to be true initially, but once an
attempt has been made to gather the location, it will be set to false.
The user's location can subsequently be obtained by accessing the
`user.location` object.

## multi_user

If you want to use the [multi-user interview feature], you need to set
`multi_user` to `True`.  This is usually done in a "mandatory" or
"initial" code block.

When `multi_user` is set to `True`, **docassemble** will not encrypt
the interview answers on the server.  This is necessary so that
different people can access the same interview.  When interview
answers are encrypted, only the user who started the interview can
access the interview answers.

Setting `multi_user` to `True` will reduce [security] somewhat, but it
is necessary for allowing the [multi-user interview feature].

## menu_items

Interviews can add entries to the menu within the web app.

When `menu_items` is set to a [Python list], **docassemble** will add
entries to the menu based on the items in the list.

Each item in the list is expected to be a [Python dictionary] with
keys `label` and `url`.  Typically, these entries are generated using
the `action_menu_item()` [function], which creates a menu item that
runs an "action."  (See the "url_action and process_action" section of
the [functions] page for more information about what "actions" are in
**docassemble**, and for documentation for the `action_menu_item()`
function.)

{% highlight yaml %}
---
mandatory: true
code: |
  menu_items = [ action_menu_item('Review Answers', 'review_answers') ]
---
{% endhighlight %}

Alternatively, you can set items manually:

{% highlight yaml %}
---
mandatory: true
code: |
  menu_items = [ {'url': 'http://google.com', 'label': 'Go to Google!'} ]
---
{% endhighlight %}

Since menu items are controlled with `code` blocks, you can turn them
on and off during the course of the interview as necessary.

[VoiceRSS]: http://www.voicerss.org/
[get]: https://docs.python.org/2/library/stdtypes.html#dict.get
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[initial block]: {{ site.baseurl }}/docs/initial.html
[configuration]: {{ site.baseurl }}/docs/config.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[multi-user interview feature]: {{ site.baseurl }}/docs/roles.html
[security]: {{ site.baseurl }}/docs/security.html
