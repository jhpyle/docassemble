---
layout: docs
title: Templates
short_title: Templates
---

This section explains how the `template` block is used in
**docassemble** interviews.  If you are interested in document
templates, see [documents].  If you are interested in how to insert
variables into the text of your questions or documents, see [markup].

## `template`

A `template` allows you assign text to a variable and then re-use the
text by referring to a variable.

{% highlight yaml %}
---
template: disclaimer
content: |
  The opinions expressed herein do not *necessarily* reflect the views
  of ${ company }.
---
{% endhighlight %}

The `content` of a `template` may contain [Mako] and [Markdown].

The name after `template:` is a variable name that you can refer to
elsewhere.  For example:

{% highlight yaml %}
---
field: intro_screen
question: Welcome to the interview!
subquestion: |
  Greetings.  We hope you learn something from this guided interview.

  ${ disclaimer }

  To get started, press **Continue**.
---
{% endhighlight %}

The `template` block, like `question` and `code` blocks, offers to
define a variable.  So when **docassemble** needs to know the
definition of `disclaimer` and finds that `disclaimer` is not defined,
it will look for a `question`, `code`, or `template` block that offers
to define `disclaimer`.  If it finds the `template` block above, it
will define the `disclaimer` variable.  Note that once the variable is
defined, it will always return the same text, even if underlying
variables like `company` may have changed in the interim.  If you want
a template that returns something different every time, you can use
code to make `disclaimer` undefined again (`del disclaimer`), write a
[Mako] `def` function, or write a custom [Python] function.

Optionally, a `template` can have a `subject`:

{% highlight yaml %}
---
template: disclaimer
subject: Please be advised
content: |
  The opinions expressed herein do not *necessarily* reflect the views
  of ${ company }.
---
{% endhighlight %}

Then you can write:

{% highlight yaml %}
---
field: intro_screen
question: Welcome to the interview!
subquestion: |
  Greetings.  We hope you learn something from this guided interview.

  To get started, press **Continue**.

  ### ${ disclaimer.subject }

  ${ disclaimer.content }
---
{% endhighlight %}

Writing `${ disclaimer }` has the same effect as writing
`${ disclaimer.content }`.

Templates are also useful for defining the content of e-mails.  See
[Legal Applications].

[markup]: {{ site.baseurl }}/docs/markup.html
[documents]: {{ site.baseurl }}/docs/documents.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[Python]: https://www.python.org/
[Legal Applications]: {{ site.baseurl }}/docs/legal.html
