---
layout: docs
title: External data
short_title: External Data
---

There are a variety of ways that you can move information into and out
of interview sessions, besides obtaining information from the user.

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
the main path of the [interview logic], the next piece of
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

## <a name="push"></a>Pushing information into a session

Typically, users launch actions by clicking hyperlinks within the
**docassemble** application.  However, it is also possible to click
hyperlinks outside of the application that run actions inside the
session.

For more information about this feature, see the
[`interview_url_action()`] function.  This function creates a URL that
embeds the session ID.

## <a name="pull"></a>Pulling information out of a session

The [`interview_url_action()`] function also allows the extraction of
information from an interview.  You can call
[`interview_url_action()`] with a reference to an [`event`] that runs
[`json_response()`] to return selected information in a
machine-readable format.  This allows you to create a customizable
"API" for your interview.

{% include side-by-side.html demo="response-json" %}

If you go through the interview and obtain the URL, you can try
loading it in a different browser to verify that another application
(not having the same browser cookies) can access the information in
[JSON] format.

# <a name="api"></a>Using the API

You can also manipulate interview sessions using the **docassemble** [API].

# <a name="email from"></a>E-mail

## <a name="email from"></a>Sending e-mail from a session

You can use the [`send_email()`] function to send e-mails from an
interview session to the outside world.  You will first need to
[configure your server]({{ site.baseurl }}/docs/config.html#mail) to
send e-mail.

## <a name="email to"></a>Sending e-mail to a session

If you are using [Docker] to deploy your server, and you have
[configured your server to receive e-mail]({{ site.baseurl }}/docs/config.html#setup_email),
you can use **docassemble**'s e-mail-to-session feature.

This involves generating a special e-mail address using
[`interview_email()`].  Any e-mails sent to that address and received
by the server will be processed and made available in the interview
session for retrieval using [`get_emails()`].

# <a name="sms"></a>Sending text messages from a session

You can use the [`send_sms()`] function to send text messages from an
interview session to the outside world.  You will first need to
[configure your server]({{ site.baseurl }}/docs/config.html#twilio) to
send text messages.  Despite the function name ("SMS"), this function
can be used to send messages through [Twilio]'s [WhatsApp API].

# <a name="persist data"></a>Persisting data

## <a name="persist sessions"></a>Persistent interview sessions

The interview answers in an interview session are stored in encrypted
form inside of rows in a [SQL] table.  Documents are stored on the
server or in a cloud storage system.  If a user who is not logged in
completes an interview, they will not be able to access their
interview session again after closing their browser, because the
encryption key will be lost.  However, if they log in, their interview
session will be tied to their account, and their password will become
the decryption key for the session.

The encryption of interview answers makes it impossible for someone
other than the original user to access the data in the interview
session, unless the decryption key (the user's password) is known.
However, if the interview sets [`multi_user`] to `False`, then
functions like [`interview_url_action()`] can be used to access the data
in the interview as long as the interview session exists.

By default, interview sessions are deleted after 90 days of
inactivity.  This feature can be modified or turned off using the
[`interview delete days`] configuration directive.

## <a name="persist files"></a>Persistent files

When an interview session is deleted, the files associated with the
interview session are also deleted.

If you want a file to continue exist after its associated interview
session has been deleted, you can use the [`.set_attributes()`] method
of the [`DAFile`] object in order to indicate that the file should not
be deleted when the interview session is deleted.

## <a name="sql"></a>Saving to SQL

A session's interview answers are stored in a [SQL] server, but not in a
way that is easily accessible across interview sessions.  Interview
sessions are not persistent; the user can delete a session, and a
session may be deleted due to inactivity (unless the [`interview
delete days`] configuration directive is set to disable automatic
deletion).

If you want to save information in [SQL] in a way that will persist
indefinitely and that will not be encrypted, you can use the
[`store_variables_snapshot()`] function to store the interview answers
to a special [SQL] table in a [JSON] format that allows you to write [SQL]
queries that access individual variables inside the data structure.
You can also use [`write_record()`], [`delete_record()`] and
[`read_records()`] functions to store data (including Python objects)
in [SQL] records.  These methods do not preserve server-side encryption,
however.

You can save information in encrypted form in [SQL] in a [Redis]-like
fashion using a [`DAStore`] object.

It is also possible for [`DAObject`]s to "mirror" rows in a [SQL]
database.  To do this, you need to write custom classes that are
subclasses of [`DAObject`] and the special object [`SQLObject`].  For
more information, see the documentation for [`SQLObject`].

## <a name="redis"></a>Saving to Redis

Instead of saving to the [SQL] database, you can write persistent data
to [Redis] using an instance of the [`DARedis`] object.

# <a name="third party api"></a>Using third-party APIs

Your interview can also communicate with the outside world using any
[Python] module that provides the functionality you want.

Here is a simple example that calls the [World Clock API] to obtain
the current time (which you don't really need an API to do).

The API call is in a [Python module] called [`gettime.py`] in the
[`docassemble.demo`] package.  The contents of this file are:

{% highlight python %}
import requests

def get_time():
    r = requests.get('http://worldclockapi.com/api/json/est/now')
    if r.status_code != 200:
        raise Exception("Could not obtain the time")
    return r.json()['currentDateTime']
{% endhighlight %}

The [World Clock API] returns output in [JSON] format, such as:

{% highlight javascript %}
{"$id":"1","currentDateTime":"2019-03-04T22:43-05:00","utcOffset":"-05:00:00","isDayLightSavingsTime":false,"dayOfTheWeek":"Monday","timeZoneName":"Eastern Standard Time","currentFileTime":131962129911877536,"ordinalDate":"2019-63","serviceResponse":null}
{% endhighlight %}

The `get_time()` function uses the [`requests`] library.  The variable
`r` represents the response of the [World Clock API]'s server to the
attempt to your code's attempt to obtain the contents of the given
URL.  This object has a handy method `.json()` that converts the
output of the request to a data structure, assuming that the request
returns [JSON].  The `get_time()` function returns the
`currentDateTime` part of the [World Clock API]'s response.

Here is an interview that calls the `get_time()` function:

{% include demo-side-by-side.html demo="get-time" %}

For more complex examples, see the [sample interviews in the
documentation] that read data from a [Google Sheet] and write data to
a [Google Sheet].

# <a name="across sessions"></a>Sharing information across sessions

Users' answers to questions in an interview are stored in the
"interview answers," which is a pickled Python dictionary stored on
the [SQL] server.  Each set of "interview answers" is specific to a
particular interview (e.g.,
`docassemble.demo:data/questions/questions.yml`) and specific to a
particular session in that interview (e.g., session ID
`BoJSwJHppIPFYtFEOeBU1y4koaM3L9zP`).

Every time the user proceeds from one screen to another, the interview
answers are changed, the interview logic is evaluated (which may
change the interview answers further) and a new set of interview
answers is saved. The user can incrementally "undo" changes to the
interview answers by pressing the "back" button, which restores an
earlier saved state of the interview answers.

**docassemble**'s interview logic system is based on this system of
the "interview answers."  If the interview logic calls for a value of
a variable that is undefined, **docassemble** will ask a `question` or
run `code` to obtain a definition of that variable.  **docassemble**
asks for information that is missing in the interview answers.

By default, the interview answers are encrypted on the server and can
only be accessed when the user provides the decryption key via a web
browser cookie.  This gives the user control over their information.

The way that **docassemble** works with interview answers is very
different from the way that a typical web-based database works with
data. A web-based database will typically use a [SQL] backend, where the
front end allows the user to populate fields of data records, where
the fields are columns and the data records are rows in [SQL]
tables. These applications are known as "[CRUD]" applications, because
the front end facilitates creating, retrieving, updating, and deleting
rows in tables. In **docassemble**, by contrast, the interview answers
are not values in two-dimensional data tables, but rather Python data
structures that at any point in time may be only be partially
populated.

If you want to share information across sessions, you can do so, but
the methods for doing so are not going to be the same as the methods
for accessing data in a [CRUD] application.

There are multiple ways that you can share information across
sessions:

* Push data: from session A, you can populate variables in session B
  by calling [`set_session_variables()`]. If session B does not exist
  yet, you can first initiate it by calling [`create_session()`].
* Pull data: from session B, you can retrieve variables from session A
  by calling [`get_session_variables()`].
* Share data in a common storage area: from session A, you can use a
  [`DAStore`] object to save data to a storage area that is specific
  to the user but can be accessed from any session. In session B, you
  can write `code` blocks that initialize variables to values that are
  stored in that storage area, if the storage area exists. By default,
  data are encrypted using the same encryption system as interview
  answers, and encryption can be turned off.
* Share data using [Redis]: [`DARedis`] can also be used as a storage
  area. From session A, you can use the [`.set_data()`] method of
  [`DARedis`] to save a Python data structure to [Redis], and then
  inside of session B, you can call the [`.get_data()`] method of
  [`DARedis`] to retrieve the data structure. [Redis] is a fast,
  in-memory data storage area, so it is best used with information
  that only needs to be stored temporarily. Encryption is not
  available.
* Share data in a list of records: the [`write_record()`] and
  [`read_records()`] functions are useful for storing lists of data
  records, where each list is identified by a key that is global to
  the server. Inside of session A, you can call [`write_record()`] to
  store a row in a list. Inside of session B, you can call
  [`read_records()`] to retrieve all of the records in that
  list. Encryption is not available.
* Sync data to a SQL database: if you would like to use a traditional
  [SQL] database as a "single source of truth" for variables in your
  interview, you can use the [`SQLObject`] system. This allows you to
  "sync" variables in your interview answers with a [SQL]
  database. Encryption is not supported.
* Stash data temporarily in an encrypted data store: from session A,
  you can call [`stash_data()`] to store particular interview answers
  in an encrypted location. [`stash_data()`] returns tokens that can
  be used to access the stashed data. Session A can offer the user
  URLs to other interviews, in which the tokens are URL parameters. If
  the user clicks one of these URLs and starts session B, the
  interview logic in session B can get look for the tokens in
  `url_args` and call [`retrieve_stashed_data()`] to retrieve the
  interview answers that had been stored by session A. The stored data
  can be deleted once they are retrieved, and can automatically expire
  after a period of time. This is a secure way to pass data from one
  session to another. It avoids storing human-readable information in
  the URL parameters when passing data from one session to a
  prospective session. It avoids the unnecessary creation of a new
  session if the user does not want to proceed to start a new
  session. The encryption system is independent of the encryption
  system for interview answers, so that knowledge of the tokens does
  not lead to knowledge of any interview answers. There are [API
  interfaces] for stashing data and retrieving stashed data.

[JSON]: https://en.wikipedia.org/wiki/JSON
[`requests`]: https://requests.readthedocs.io/en/master/
[`gettime.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/gettime.py
[`docassemble.demo`]: https://github.com/jhpyle/docassemble/tree/master/docassemble_demo/docassemble/demo
[Python module]: https://docs.python.org/3/tutorial/modules.html
[World Clock API]: http://worldclockapi.com/
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[sample interviews in the documentation]: {{ site.baseurl }}/docs/functions.html#google sheets example
[Google Sheets]: https://sheets.google.com
[Google Sheet]: https://sheets.google.com
[`DAStore`]: {{ site.baseurl }}/docs/objects.html#DAStore
[`write_record()`]: {{ site.baseurl }}/docs/functions.html#write_record
[`delete_record()`]: {{ site.baseurl }}/docs/functions.html#delete_record
[`read_records()`]: {{ site.baseurl }}/docs/functions.html#read_records
[`url_args`]: {{ site.baseurl }}/docs/special.html#url_args
[`url_args` special variable]: {{ site.baseurl }}/docs/special.html#url_args
[reserved URL parameters]: {{ site.baseurl }}/docs/special.html#reserved url parameters
[invocation]: {{ site.baseurl }}/docs/interviews.html#invocation
[background action]: {{ site.baseurl }}/docs/background.html#background
[`url_ask()`]: {{ site.baseurl }}/docs/functions.html#url_ask
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[interview logic]: {{ site.baseurl }}/docs/logic.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`interview_url_action()`]: {{ site.baseurl }}/docs/functions.html#interview_url_action
[`json_response()`]: {{ site.baseurl }}/docs/functions.html#json_response
[`event`]: {{ site.baseurl }}/docs/fields.html#event
[API]: {{ site.baseurl }}/docs/api.html
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[Docker]: {{ site.baseurl }}/docs/docker.html
[`interview_email()`]: {{ site.baseurl }}/docs/functions.html#interview_email
[`get_emails()`]: {{ site.baseurl }}/docs/functions.html#get_emails
[`send_sms()`]: {{ site.baseurl }}/docs/functions.html#send_sms
[Twilio]: https://twilio.com
[WhatsApp API]: https://www.twilio.com/whatsapp
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[`interview delete days`]: {{ site.baseurl }}/docs/config.html#interview delete days
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`.set_attributes()`]: {{ site.baseurl }}/docs/objects.html#DAFile.set_attributes
[`DARedis`]: {{ site.baseurl }}/docs/objects.html#DARedis
[`.set_data()`]: {{ site.baseurl }}/docs/objects.html#DARedis.set_data
[`.get_data()`]: {{ site.baseurl }}/docs/objects.html#DARedis.get_data
[Redis]: https://redis.io/
[`SQLObject`]: {{ site.baseurl }}/docs/objects.html#SQLObject
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`store_variables_snapshot()`]: {{ site.baseurl }}/docs/functions.html#store_variables_snapshot
[CRUD]: https://en.wikipedia.org/wiki/Create,_read,_update_and_delete
[`create_session()`]: {{ site.baseurl }}/docs/functions.html#create_session
[`set_session_variables()`]: {{ site.baseurl }}/docs/functions.html#set_session_variables
[`get_session_variables()`]: {{ site.baseurl }}/docs/functions.html#get_session_variables
[`stash_data()`]: {{ site.baseurl }}/docs/functions.html#stash_data
[`retrieve_stashed_data()`]: {{ site.baseurl }}/docs/functions.html#retrieve_stashed_data
[SQL]: https://en.wikipedia.org/wiki/SQL
[API interfaces]: {{ site.baseurl }}/docs/api.html#stash_data
