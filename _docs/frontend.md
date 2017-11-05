---
layout: docs
title: Custom Front Ends
short_title: Custom Front Ends
---

If you are a software developer, you can develop your own front end
for **docassemble**.  If you add `&json=1` to the end of the URL, or
include `json=1` as parameter of a POST request, a [JSON]
representation of the screen will be returned.  (In fact, `json` set
to anything will cause a [JSON] representation to be returned.)

To communicate back with the server, you will need to mimic the way
that the browser communicates with the server.  The easiest way to
figure this out is use your browser's developer tools and inspect the
POST requests that the browser sends to the server.

In general, you can set any variable in the interview by sending a
POST request with parameters where the keys are [base64]-encoded
variable names and the values are the values you want to assign to the
variables.  In [Javascript], you can use the [`atob()`] and [`btoa()`]
functions to convert between [base64] and text.  In [Python], you can use
the [`encode_name()`] and [`decode_name()`] functions from
[`docassemble.base.util`].

For example, if you want to set the variable `favorite_fruit` to
`'apple'`, you would convert `favorite_fruit` to [base64] using
`btoa('favorite_fruit')` or `encode_name('favorite_fruit')`, to get
`'ZmF2b3JpdGVfZnJ1aXQ='`.  Then you would put the following key and
value in your POST request:

* `ZmF2b3JpdGVfZnJ1aXQ=`: `apple`

The POST request needs to go to the interview URL, which will look like
`https://docassemble.example.com/?i=docassemble.yourpackage:data/questions/yourinterview.yml`.

In addition to including keys and values of variables, your requests
should feed back the following values from the last [JSON] response
you received:

* `csrf_token`.  This token is a security measure that protects against
  cross-site interference.
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
a boolean value, you would run `btoa('likes_fruit')` to get the key
name `bGlrZXNfZnJ1aXQ=`, and then you would run
`btoa('{"bGlrZXNfZnJ1aXQ=": "boolean"}')` to get
`eyJiR2xyWlhOZlpuSjFhWFE9IjogImJvb2xlYW4ifQ==`.  Then you would set
the following keys and values in your POST request:

* `bGlrZXNfZnJ1aXQ=`: `True`
* `_datatypes`: `eyJiR2xyWlhOZlpuSjFhWFE9IjogImJvb2xlYW4ifQ==`

If you are uploading a file, use the `multipart/form-data` style of
encoding POST parameters, and include one additional parameter:

* `_files`.  This is a [base64]-encoded [JSON] representation of a
  list where each element is a [base64]-encoded variable name for a
  file being uploaded.
  
The "name" of an uploaded file should simply be the [base64]-encoded
variable name.

For example, if you wanted to upload a file into a variable
`user_picture`, you would run `btoa('user_picture')` to get
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
`user_picture`.  You would run `btoa('user_picture')` to get
`'dXNlcl9waWN0dXJl'`.  Then you would create a [Javascript] object (a
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

[JSON]: https://en.wikipedia.org/wiki/JSON
[`datatype`]: {{ site.baseurl }}/docs/fields.html#datatype
[`atob()`]: https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/atob
[`btoa()`]: https://developer.mozilla.org/en-US/docs/Web/API/WindowOrWorkerGlobalScope/btoa
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`encode_name()`]: {{ site.baseurl }}/docs/functions.html#encode_name
[`decode_name()`]: {{ site.baseurl }}/docs/functions.html#decode_name
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[base64]: https://en.wikipedia.org/wiki/Base64
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[MIME type]: https://en.wikipedia.org/wiki/Media_type
[data URL]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/Data_URIs
