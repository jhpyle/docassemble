---
layout: docs
title: Custom Front Ends
short_title: Custom Front Ends
---

# <a name="interface"></a>Interacting with **docassemble** over HTTP

If you are a software developer, you can develop your own front end
for **docassemble**.  You can use **docassemble**'s [API] to
communicate with **docassemble** sessions.  It is slightly more
complicated, but just as effective, to communicate with
**docassemble** the same way that the web browser does.

You can extract a machine-readable version of any **docassemble**
screen.  If you add `&json=1` to the end of the URL, or include
`json=1` as parameter of a POST request, a [JSON] representation of
the screen will be returned.  (In fact, `json` set to anything will
cause a [JSON] representation to be returned.)

To communicate back with the server, you will need to mimic the way
that the browser communicates with the server.  The easiest way to
figure this out is use your browser's developer tools and inspect the
POST requests that the browser sends to the server.

**docassemble** uses cookies and [302 redirect]s, so if you are using
a library to send HTTP requests to **docassemble**, you need to make
sure that cookies are stored for the life of the session, and make
sure that your library will follow redirects.  If your library does
not store cookies, you will encounter an infinite redirect, because
the first thing that **docassemble** does when a user connects to it
is send a self-referential redirect with a cookie.

In general, you can set any variable in the interview by sending a
POST request with parameters where the keys are [base64]-encoded
variable names and the values are the values you want to assign to the
variables.  In [Javascript], you can use the [`atob()`] and [`btoa()`]
functions to convert between [base64] and text.  However, when using
[`btoa()`], you need to alter the results to remove newline and `=`
characters when working with variable names.  Thus, if your variable
name is `varName`, call `btoa(varName).replace(/[\\n=]/g, '')`.  In
[Python], you can use the [`encode_name()`] and [`decode_name()`]
functions to convert to and from [base64].

For example, if you want to set the variable `favorite_fruit` to
`'apple'`, you would convert `favorite_fruit` to [base64] using
`btoa('favorite_fruit').replace(/[\\n=]/g, '')` or
`encode_name('favorite_fruit')`, to get `'ZmF2b3JpdGVfZnJ1aXQ'`.
Then you would put the following key and value in your POST request:

* `ZmF2b3JpdGVfZnJ1aXQ`: `apple`

The POST request needs to go to the interview URL, which will look like
`https://docassemble.example.com/interview?i=docassemble.yourpackage:data/questions/yourinterview.yml`.

In addition to including keys and values of variables, your requests
should include the parameter `json=1`, so that the server knows to
respond with [JSON].  In addition, your requests should feed back the
following values from the previous [JSON] response you received:

* `csrf_token`.  This token is a security measure that protects against
  cross-site interference.  See [CSRF protection].
* `_question_name`.  This contains the name of the question to which
  you are providing data.  In most cases, this is not used, but there
  are some question types for which it is important.
* `_datatypes`.  This is a way of telling the server the data types of
  the variables being set, so that the server knows which values are
  integers or dates rather than text values.  The value is a
  base64-encoded [JSON] representation of a dictionary where the keys
  are base64-encoded variable names and the values are the names of
  variables' [`datatype`]s.
* `_varnames`.  For certain types of questions, variable aliases are
  used.  This base64-encoded [JSON] representation of a dictionary tells
  the server what this mapping is.

The `_datatypes` field is important if you are setting non-text
values.  For example, to set the variable `likes_fruit` to `True`,
a boolean value, you would run `btoa('likes_fruit').replace(/[\\n=]/g, '')`
to get the key name `bGlrZXNfZnJ1aXQ`, and then you would run
`btoa('{"bGlrZXNfZnJ1aXQ": "boolean"}')` to get
`eyJiR2xyWlhOZlpuSjFhWFEiOiAiYm9vbGVhbiJ9`.  Then you would set
the following keys and values in your POST request:

* `bGlrZXNfZnJ1aXQ`: `True`
* `_datatypes`: `eyJiR2xyWlhOZlpuSjFhWFEiOiAiYm9vbGVhbiJ9`

If you are uploading a file, use the `multipart/form-data` style of
encoding POST parameters, and include one additional parameter:

* `_files`.  This is a [base64]-encoded [JSON] representation of a
  list where each element is a [base64]-encoded variable name for a
  file being uploaded.

The "name" of an uploaded file should simply be the [base64]-encoded
variable name.

For example, if you wanted to upload a file into a variable
`user_picture`, you would run `btoa('user_picture').replace(/[\\n=]/g, '')` to get
`'dXNlcl9waWN0dXJl'`, and then you would run
`btoa('["dXNlcl9waWN0dXJl"]')` to get
`'WyJkWE5sY2w5d2FXTjBkWEpsIl0='`, and you would set the following in
your POST:

* `dXNlcl9waWN0dXJl`: the file you are uploading, using the standard
  method for attaching files to a `multipart/form-data` POST request.
* `_files`: `WyJkWE5sY2w5d2FXTjBkWEpsIl0=`

There is also a second way to upload files, which uses [data URL]s.
To use this method, send a normal POST request, without
`multipart/form-data` and without a traditional uploaded file, in
which there is a key called `_files_inline`, which is set to
[base64]-encoded [JSON] data structure containing the file or files
you want to upload, and some information about them.

For example, suppose you want to upload a file to the variable
`user_picture`.  You would run `btoa('user_picture').replace(/[\\n=]/g, '')`
to get `'dXNlcl9waWN0dXJl'`.  Then you would create a [Javascript] object (a
[Python dictionary]) with two key-value pairs.  In the first key-value
pair, the key will be `keys` and the value will be a list containing
the [base64]-encoded variable names of the variables to which you want
to upload files.  In the second key-value pair, the key will be
`values` and the value will be an object (a [Python dictionary]) with
the following keys:

* `name`: the name of the file being uploaded,
  without a directory specified.
* `size`: the number of bytes in the file.
* `type`: the [MIME type] of the file being uploaded.
* `content`: a [data URL] containing the contents of the file, using
  [base64] encoding.

Here is an example of the data structure you would need to create:

{% highlight json %}
{"keys":["dXNlcl9waWN0dXJl"],"values":{"dXNlcl9waWN0dXJl":[{"name":"the_filename.png","size":8025,"type":"image/png","content":"data:image/png;base64,iVBO...Jggg=="}]}}
{% endhighlight %}

Assuming that this data structure was stored in a [Javascript]
variable `data`, you would set the POST parameter `_files_inline` to
the result of `btoa(JSON.stringify(data))`.

In addition, when sending a POST request, include the parameter `json`
and set it to `1`, so that the response you get back is in [JSON]
format.

The format of the [JSON] representation should be self-explanatory.
Toggle the `json=1` URL parameter to compare the HTML version of the
screen to the [JSON] representation.

# <a name="login"></a>Example of "logging in" with JavaScript

If you want to programmatically "log in" to **docassemble**, you can
use code like the following:

{% highlight js %}
var myHeaders = new Headers();

var myInit = { method: 'GET',
               headers: myHeaders,
               mode: 'cors',
               cache: 'default',
               redirect: 'follow',
               credentials: 'include' };

var myRequest = new Request('https://docassemble.example.com/user/sign-in?json=1', myInit);

fetch(myRequest).then(function(response) {
  var contentType = response.headers.get("content-type");
  if(contentType && contentType.includes("application/json")) {
    return response.json();
  }
  throw new TypeError("Error: JSON not returned from sign-in site");
}).then(function(json) {
  var form = new FormData();
  form.append('next', 'https://docassemble.example.com/interviews?json=1');
  form.append('csrf_token', json.csrf_token);
  form.append('email', 'someuser@example.com');
  form.append('password', 'xxsecretxx');
  var loginInit = { method: 'POST',
                    headers: myHeaders,
                    mode: 'cors',
                    cache: 'default',
                    credentials: 'include',
                    redirect: 'follow',
                    body: form };
  var loginRequest = new Request('https://docassemble.example.com/user/sign-in', loginInit);
  fetch(loginRequest).then(function(response) {
    var contentType = response.headers.get("content-type");
    if(contentType && contentType.includes("application/json")) {
      return response.json();
    }
    throw new TypeError("Error: JSON not returned after signing in");
  }).then(function(json) {
    console.log(json)
  });
});
{% endhighlight %}

# <a name="sessions"></a>Sessions

## <a name="sessionsbackground"></a>Background information

If you are building a front end to **docassemble**, you do not need to
know exactly how **docassemble** works internally, but it may help for
you to know a little about its internal design.

The **docassemble** web application saves state in a two different
ways.

First, there is the state that represents the relationship between the
web browser and the **docassemble** server.  This is controlled by
[Flask], using a standard [Flask] session ID.  [Redis] is used as the
backend for this session tracking system.  (The [`flask_kvsession`]
and [`simplekv.memory.redisstore`] packages are used.)  This session
tracking is necessary for the user login system, which is provided by
the [`flask_user`] package.  It is used on all pages of a
**docassemble** site.  It is necessary for [CSRF protection].  This
session tracking system works through a cookie called `session`.  This
session ID is generated by [Flask] and only lasts for the life of the
web browser session (unless the user chooses the "remember me"
option).  Old session IDs are automatically purged after a time.

Second, there is the state that represents the current step of a
user's **docassemble** interview.  This is not related to [Flask], and
is unique to **docassemble**.  Each step of the interview process
(which is accessible to the user with the "Back" button, which reverts
the interview state to the previous step) is stored as a row in a SQL
table called `userdict`.  A state of the interview is represented as a
[Python dictionary] serialized with [cPickle] and stored in the
`dictionary` column of the `userdict` table.  This [Python] dictionary
is used as the namespace in which interview code is evalutated.  A
stored interview session is uniquely identified by the interview file
name (e.g., `docassemble.eviction:data/questions/complaint.yml`) and a
session ID, which is a unique sequence of 32 random upper and
lowercase characters.  These are the values referred to in the `i` and
`session` parameters produced by [`interview_url()`].  (In the
`userdict` table, the interview file name is in the `filename` column
and the session ID is in the `key` column.)

So, there are two session IDs, based on systems that are independent
from one another.  As a front-end developer, you will probably never
need to worry about the [Flask] session ID, which is stored in the
cookie called `session`; your HTTP library and the **docassemble**
server can work with this session ID without any manual intervention
from you.  The session ID that matters is the **docassemble** session
ID that, along with the filename of the [YAML] interview file,
uniquely identifies an interview session.

By default, server-side encryption is used, which means that interview
answers are stored encrypted on the server, and only a user who
started the interview can access the interview answers.  The
encryption key is stored in a cookie called `secret`, and the value of
the `secret` is not stored on the server anywhere.  For a logged in
user, the `secret` is based on the user's password, and the cookie is
set when the user logs in.  Users who are not logged in have a random
`secret`.  When the user logs in or registers, existing stored
interview states are re-encrypted with the new encryption key.  (The
same happens when a logged-in user changes his or her password.)  If a
user forgets his or her password, there is no way to retrieve the
interview answers.  If a user completes an interview without logging
in, and the cookie containing the `secret` expires (as it will when
the user closes the browser), there is no way for the interview
answers to be retrieved again.  Server-side encryption can be turned
off in the interview by setting [`multi_user`] to `True`.

The **docassemble** web application is designed to use [Ajax] calls as
much as possible.  When a user first visits an interview, the browser
sends a GET request, and the server responds with HTML.  However, when
the user interacts with the screen and moves from step to step in the
interview, the browser sends [Ajax] POST request, and the server
responds with [JSON].  Within this [JSON] is a string representing the
HTML of the `<body>` of the new screen.  The server knows it is
dealing with an [Ajax] request because the browser includes `ajax=1`
among the parameters of every request.

## <a name="sessionsdetail"></a>How sessions work

All interviews take place using the root location `/` (unless the
[`root`] of the whole site is changed in the configuration to
something else).

A new user starts an interview by visiting `/` with an `i` parameter
set to the interview name (e.g.,
`docassemble.eviction:data/questions/complaint.yml`).

If a new user visits `/` without an `i` parameter, the user will be
directed to `/list`.  However, if there is no [`dispatch`] directive
in the configuration, the user will be redirected to the
[`default interview`].

A user can enter an on-going interview by visiting `/` with an `i`
parameter and a `session` parameter.

Once the user enters an interview, the interview filename `i` and the
session ID are cached in the [Flask] session data, so the web browser
does not have to send them to the server with every request; the
`session` cookie is the key that the server uses to know which session
it is dealing with.

The current interview's `session` ID is primarily used internally, out
of sight of the front end, but it can be obtained by:
* Calling [`interview_url()`], which returns a URL that can be used to
  resume the interview, containing both the `i` and `session` parameters.
* Calling `docassemble.base.functions.get_uid()`, which returns the
  session ID.
* Calling [`interview_list()`] to get information about all of the
  sessions of a logged-in user.
* Calling [`get_interview_variables()`] from JavaScript.

The web browser interface tries to make sure that the location bar
always displays the `i` parameter.  Users may bookmark the URL or copy
and paste the URL to share it with other people.  As long as the `i`
parameter is present in the location bar, the link will generally
behave in a way that meets the user's expectations.

However, this is only done out of convenience to the user.  Since the
interview file name is stored in the user's [Flask] session, it is not
necessary to use the `i` parameter; in fact, if you try navigating to
`/` with a web browser while using an interview, this will simply have
the effect of refreshing the screen.

If the browser sends a request with a different `i` parameter than the
one in the [Flask] session data, this has the effect of starting a new
interview session.  The old interview session is not deleted; it is
still there, stored in SQL, and is accessible to a logged-in user on
the `/interviews` page.

If the URL parameter `reset=1` is included along with an `i` parameter
in a GET request, the current interview session is erased from the
server (if there is a current session), and the interview is started
fresh.

If the URL parameter `cache=0` is included in a GET request, the
interview file will be re-read from the disk.  This is how the
[Playground] works; when you click the "Save and Run" button or the
"Run" button, the browser is directed to a link that contains
`cache=0`.  (Parsing an interview YAML file is a computationally
intensive task, so **docassemble** keeps interviews in memory whenever
it can.)

While the web browser sends POST requests with `ajax=1`, a custom
front end would probably not be interested in the information returned
from such requests.  Instead, a custom front end would send POST
requests with `json=1` and get back a [JSON] representation of the
next screen of the interview.

Note that as a technical matter, a user does not need to go through
the [`flask_user`] log-in process in order to resume an existing
interview.  Even if server-side encryption is used, if the appropriate
`secret` cookie is present, the interview answers will be decrypted.
So if you have a mechanism for remembering `i`, `session`, and
`secret`, you can run interviews without logging in.  And if
server-side encryption is turned off in an interview, all you need is
`i` and `session`.  So, if you have such a mechanism for storing these
values, the only benefit to going through the login process would be
that the user of the interview would be that the interview could use
functions like [`user_info()`] to do different things based on who the
user is.

# <a name="cors"></a>Cross-Origin Resource Sharing (CORS)

There are many security issues with sending sensitive data over HTTP.
By default, HTTP libraries implement fairly strict security
restrictions, which you can override by:

1. Changing how you call the library; and
2. Changing the headers returned by the web server.

In addition, **docassemble** uses [Flask]'s [CSRF protection] system.
This is why you need to include a `csrf_token` with every POST
request.  By default, [Flask]'s [CSRF protection] mechanism
scrutinizes the [referer header] of each request, and generates an
error if the [referer header] is not set to an appropriate value.
This security check can be turned off by setting [`require referer`]
to `False` in the [Configuration].  However, [CSRF protection] itself
cannot be turned off.

Depending on how your custom front end calls **docassemble**, you may
need to change the headers that the **docassemble** web server
returns.  By setting the [`cross site domains`] directive in the
[Configuration] to include `https://otherserver.com`, you will
activate the following headers:

{% highlight text %}
Access-Control-Allow-Origin: https://otherserver.com
Access-Control-Allow-Credentials "true"
{% endhighlight %}

In some circumstances you can set [`cross site domains`] to include
`*` in order to allow connections from anywhere.  But when cookies are
used, this is not allowed.  See the "Credentialed requests and
wildcards" section of Mozilla's [Cross-Origin Resource
Sharing](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
documentation.

Using the [API] avoids issues with [CORS].

[API]: {{ site.baseurl }}/docs/api.html
[CORS]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`cross site domains`]: {{ site.baseurl }}/docs/config.html#cross site domains
[Configuration]: {{ site.baseurl }}/docs/config.html
[`require referer`]: {{ site.baseurl }}/docs/config.html#root
[referer header]: https://en.wikipedia.org/wiki/HTTP_referer
[JSON]: https://en.wikipedia.org/wiki/JSON
[`datatype`]: {{ site.baseurl }}/docs/fields.html#datatype
[`atob()`]: https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/atob
[`btoa()`]: https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/btoa
[`encode_name()`]: {{ site.baseurl }}/docs/functions.html#encode_name
[`decode_name()`]: {{ site.baseurl }}/docs/functions.html#decode_name
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[base64]: https://en.wikipedia.org/wiki/Base64
[Python dictionary]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[MIME type]: https://en.wikipedia.org/wiki/Media_type
[data URL]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
[`user_info()`]: {{ site.baseurl }}/docs/functions.html#user_info
[Flask]: http://flask.pocoo.org/
[`flask_kvsession`]: http://pythonhosted.org/Flask-KVSession/
[`simplekv.memory.redisstore`]: http://pythonhosted.org/simplekv/memory.html#redis-backend
[`flask_user`]: http://flask-user.readthedocs.io/en/v0.6/
[CSRF protection]: http://flask-wtf.readthedocs.io/en/stable/csrf.html
[`interview_url()`]: {{ site.baseurl }}/docs/functions.html#interview_url
[`get_interview_variables()`]: {{ site.baseurl }}/docs/functions.html#get_interview_variables
[cPickle]: https://docs.python.org/3/library/pickle.html#module-cPickle
[302 redirect]: https://en.wikipedia.org/wiki/HTTP_302
[`root`]: {{ site.baseurl }}/docs/config.html#root
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[`default interview`]: {{ site.baseurl }}/docs/config.html#default interview
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[Ajax]: https://en.wikipedia.org/wiki/Ajax_(programming)
[`interview_list()`]: {{ site.baseurl }}/docs/functions.html#interview_list
[Redis]: https://redis.io/
[YAML]: https://en.wikipedia.org/wiki/YAML
[Playground]: {{ site.baseurl }}/docs/playground.html
