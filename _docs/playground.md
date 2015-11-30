---
layout: docs
title: Interview developers' playground
short_title: Playground
---

The "Playground" within the **docassemble** web application is a
testing ground for interviews.  It allows you to write [YAML] in one
or more "files" and then run an interview with one click.

Each "tab" on the Playground page is a [YAML] file.  If you have a tab
called "test" and a tab called "questions," you can incorporate one
into the other by reference.

For example, suppose your "test" tab contains:

{% highlight yaml %}
---
include:
  - questions
---
mandatory: true
code:
  say_hello
---
{% endhighlight %}

and suppose your "questions" tab contains:

{% highlight yaml %}
---
sets: say_hello
question: |
  Hello, world!
---
{% endhighlight %}

If you run the "test" tab, you will go to an interview that says
"Hello, world!"  The "test" interview knew how to ask `say_hello`
because it incorporated the "questions" tab by reference.

Notes:

* The "run" function will open an interview in another window.  Your
  browser might block this as an unwanted pop-up window.  Make sure to
  tell your browser to allow pop-ups from **docassemble**.
* Once you are running the interview in another tab, changes that you
  make to the interview you ran will be visible if you refresh the
  screen.  However, these changes will only re-appear if you "Save"
  the same file that you ran; you will not see changes to files
  included by reference unless you re-save the file you ran.
* Interviews you create in the "Playground" cannot directly be run by
  the general public or by other developers; to share an interview
  with others, you need to prepare a [package].
* The "Playground" does not offer a full range of authoring
  functionality.  For example, it does not allow you to upload images,
  templates, or static documents.  It does not allow you to edit
  [Python modules].  It is a place to test interview code quickly, not
  a development platform.  To learn how to access the full range of
  authoring functionality, see the [tutorial] and the [packages]
  sections.

[packages]: {{ site.baseurl }}/docs/packages.html
[Python package]: {{ site.baseurl }}/docs/packages.html
[Python modules]: https://docs.python.org/2/tutorial/modules.html
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
