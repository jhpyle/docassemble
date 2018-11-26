---
layout: docs
title: Special variables
short_title: Special Variables
---

# Variables set by **docassemble**

There are some special variables that **docassemble** sets in every
interview's variable store.

## <a name="_internal"></a>_internal

`_internal` is a [Python dictionary] that is used by **docassemble**
but that is not intended to be used in interviews.

## <a name="nav"></a>nav

`nav` is an object that is used to keep track of sections in your
interview.  This is relevant if you are using the [navigation bar]
feature.  For information about how to use it, see the documentation
for the [`nav` functions].

## <a name="url_args"></a>url_args

`url_args` is a [Python dictionary] that is used to access parameters
passed via URL.

Users start an interview by going to a URL.  A basic URL would look
like this:

{% highlight text %}
http://example.com/interview?i=docassemble.example_inc:data/questions/survey.yml
{% endhighlight %}

Here, the only parameter is `i`, the interview file name.

It is possible to use the URL to pass special parameters to the
interview code.  For example, if the user started the interview by
clicking on the following link:

{% highlight text %}
http://example.com/interview?i=docassemble.example_inc:data/questions/survey.yml&from=web
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
mandatory: True
question: You came from the ${ origin_of_interviewee }.
---
{% endhighlight %}

Alternatively, you could use [Python]'s [get] method to do the same
thing in less space:

{% highlight yaml %}
---
mandatory: True
question: You came from the ${ url_args.get('from', 'unknown') }.
---
{% endhighlight %}

You can test this out by trying the following links:

* [{{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=web]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=web){:target="_blank"}
* [{{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=moon]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=moon){:target="_blank"}

As soon as the interview loads, the parameters will no longer appear
in the browser's location bar.  Nevertheless, the parameters remain
available in the `url_args` dictionary for the life of the interview.

Moreover, you can set new `url_args` at any time during the course of
the interview.  For example:

{% highlight yaml %}
---
mandatory: True
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
[{{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder){:target="_blank"}.

The following parameter names are not available for use as URL
parameters because they are used for other purposes by
**docassemble**:

* `action`
* `cache`
* `filename`
* `format`
* `from_list`
* `i`
* `index`
* `new_session`
* `question`
* `reset`
* `session`

## <a name="role_needed"></a>role_needed

If you use the [multi-user interview feature] and the user reaches a
point in the interview where input is needed from a different user
before proceeding, **docassemble** will look for a [`question`] that
offers to sets [`role_event`], and ask that question.  **docassemble**
will set the variable `role_needed` to a list of roles capable of
answering the next question in the interview.

# Variables used when finding blocks to set variables

The following variables are set by **docassemble** in the course of
searching for blocks that will define variables.

* `x`
* `i`
* `j`
* `k`
* `l`
* `m`
* `n`

You should never set these variables yourself; they will be set for
you before your blocks are used.

# Variables that interviews can set

## <a name="role"></a>role

If you use the [multi-user interview feature], your interview will
need to have a [`default role` initial block] containing code that
sets the variable `role` to the user's role.

## <a name="speak_text"></a>speak_text

If this special variable is set to `True`, **docassemble** will
present the user with an HTML5 audio control at the top of the page.
When the user clicks it, **docassemble** will access the [VoiceRSS]
web service to convert the text of the question to an audio file and
then play that audio back for the user.  This requires enabling the
[`voicerss`] setting in the [configuration].

Since the [VoiceRSS] service costs money above the free usage tier,
**docassemble** does not send the request to [VoiceRSS] until the user
presses "Play" on the audio control.  It also caches the results and
reuses them whenever possible.

## <a name="track_location"></a>track_location

If set to `True`, the web app will attempt to obtain the user's
position, based on GPS or any other geolocation feature enabled in the
browser.  The [`location_known()`], [`location_returned()`], and
[`user_lat_lon()`] functions can be used to retrieve the information.

The most common way to use this feature is as follows:

{% highlight yaml %}
---
include:
  - basic-questions.yml
---
initial: True
code: |
  track_location = user.location.status()
---
{% endhighlight %}

This will cause `track_location` to be true initially, but once an
attempt has been made to gather the location, it will be set to false.
The user's location can subsequently be obtained by accessing the
`user.location` object.

## <a name="multi_user"></a>multi_user

If you want to use the [multi-user interview feature], you need to set
`multi_user` to `True`.  This is usually done in a "mandatory" or
"initial" code block.

When `multi_user` is set to `True`, **docassemble** will not encrypt
the interview answers (the [interview session dictionary]).  This is
necessary so that different people can access the same interview
session.  When the interview answers are encrypted (which is the
default), only the user who started the interview session can access
the [interview session dictionary].

Setting `multi_user` to `True` will reduce [security] somewhat, but it
is necessary for allowing the [multi-user interview feature] and for
allowing third parties to access the interview answers via the [API].

The `multi_user` variable can be changed dynamically over the course
of an interview.  For example, at a certain point in the interview,
you could ask the user:

{% highlight yaml %}
question: |
  Would you like an attorney to review your answers?
yesno: multi_user
{% endhighlight %}

After `multi_user` is set to `True`, then the next time the interview
answers are saved, encryption will not be used.  Later in the
interview, you can turn encryption back on again by setting
`multi_user` to `False`.

## <a name="menu_items"></a>menu_items

Interviews can add entries to the menu within the web app.

When `menu_items` is set to a [Python list], **docassemble** will add
entries to the menu based on the items in the list.

Each item in the list is expected to be a [Python dictionary] with
keys `label` and `url`.  Typically, these entries are generated using
the [`action_menu_item()` function], which creates a menu item that
runs an "action."  (See the [`url_action()`] and [`process_action()`]
sections of the [functions] page for more information about what
"actions" are in **docassemble**, and for documentation for the
[`action_menu_item()` function].)

{% highlight yaml %}
---
mandatory: True
code: |
  menu_items = [ action_menu_item('Review Answers', 'review_answers') ]
---
{% endhighlight %}

Alternatively, you can set items manually:

{% highlight yaml %}
---
mandatory: True
code: |
  menu_items = [ {'url': 'http://google.com', 'label': 'Go to Google!'} ]
---
{% endhighlight %}

Since menu items are controlled with [`code`] blocks, you can turn them
on and off during the course of the interview as necessary.

## <a name="allow_cron"></a>allow_cron

This variable should be set to `True` if you want to allow the server
to run [scheduled tasks] from your interview.

# Variables that stand in for events

**docassemble** interviews ask questions or run code when required by
[interview logic] and also when caused to do so by [events] and
[actions].  These [events] and [actions] are identified using
variables, which may not ever be defined by an interview.

There are some built-in variable names with special meaning:

* <a name="incoming_email"></a>[`incoming_email`] is used to indicate
  a [`code`] block that should be run when an [e-mail] is received.
* <a name="role_event"></a>[`role_event`] is used to present a special screen when the [roles]
  system requires a change in the interview role.
* <a name="cron_hourly"></a>[`cron_hourly`] is used by the [scheduled tasks] system.  This
  [event] is triggered in the background, every hour, by the server.
  (This requires that [`allow_cron`] be set to `True`.)
* <a name="cron_daily"></a>[`cron_daily`] is similar, except runs on a daily basis.
* <a name="cron_weekly"></a>[`cron_weekly`] is similar, except runs on a weekly basis.
* <a name="cron_monthly"></a>[`cron_monthly`] is similar, except runs on a monthly basis.

[`allow_cron`]: #allow_cron
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[roles]: {{ site.baseurl }}/docs/roles.html
[interview logic]: {{ site.baseurl }}/docs/logic.html
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[events]: {{ site.baseurl }}/docs/fields.html#event
[VoiceRSS]: http://www.voicerss.org/
[get]: https://docs.python.org/2/library/stdtypes.html#dict.get
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[`default role` initial block]: {{ site.baseurl }}/docs/initial.html#default_role
[configuration]: {{ site.baseurl }}/docs/config.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[multi-user interview feature]: {{ site.baseurl }}/docs/roles.html
[security]: {{ site.baseurl }}/docs/security.html
[`action_menu_item()` function]: {{ site.baseurl }}/docs/functions.html#action_menu_item
[functions]: {{ site.baseurl }}/docs/functions.html
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`role_event`]: {{ site.baseurl }}/docs/roles.html
[`voicerss`]: {{ site.baseurl }}/docs/config.html#voicerss
[`code`]: {{ site.baseurl }}/docs/code.html
[`track_location`]: #track_location
[User List]: {{ site.baseurl }}/docs/users.html#user_list
[Profile]: {{ site.baseurl }}/docs/users.html#profile
[`location_known()`]: {{ site.baseurl }}/docs/functions.html#location_known
[`location_returned()`]: {{ site.baseurl }}/docs/functions.html#location_returned
[`user_lat_lon()`]: {{ site.baseurl }}/docs/functions.html#user_lat_lon
[`cron_hourly`]: {{ site.baseurl }}/docs/background.html#cron_hourly
[`cron_daily`]: {{ site.baseurl }}/docs/background.html#cron_daily
[`cron_weekly`]: {{ site.baseurl }}/docs/background.html#cron_weekly
[`cron_monthly`]: {{ site.baseurl }}/docs/background.html#cron_monthly
[e-mail]: {{ site.baseurl }}/docs/background.html#email
[navigation bar]: {{ site.baseurl }}/docs/initial.html#navigation bar
[`nav` functions]: {{ site.baseurl }}/docs/functions.html#get_section
[event]: {{ site.baseurl }}/docs/background.html
[`incoming_email`]: {{ site.baseurl }}/docs/background.html#email
[API]: {{ site.baseurl }}/docs/api.html
[interview session dictionary]: {{ site.baseurl }}/docs/interviews.html#howstored
