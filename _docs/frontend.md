---
layout: docs
title: Custom Front Ends
short_title: Custom Front Ends
---

If you are a software developer, you can develop your own front end
for **docassemble**.  If you add `&json=1` to the end of the URL, or
include `json=1` as parameter of a POST request, a [JSON]
representation of the screen will be returned.

To communicate back with the server, you will need to mimic the way
that the browser communicates with the server.  The easiest way to
figure this out is use your browser's developer tools and inspect the
POST requests that the browser sends to the server.

In general, you can set any variable in the interview by sending a
POST request with parameters where the keys are base64-encoded
variable names and the values are the values you want to assign to the
variables.  In Javascript, you can use the [`atob()`] and [`btoa()`]
functions to convert between base64 and text.

The POST request needs to go to the interview URL, which will look like
`https://docassemble.example.com/?i=docassemble.yourpackage:data/questions/yourinterview.yml`.

Your requests should feed back the following values from the last
[JSON] response you received:

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
