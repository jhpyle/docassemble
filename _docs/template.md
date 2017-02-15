---
layout: docs
title: Templates
short_title: Templates
---

This section explains how the `template` block is used in
**docassemble** interviews.  If you are interested in document
templates, see [documents].  If you are interested in how to insert
variables into the text of your questions or documents, see [markup].

A `template` allows you assign text to a variable and then re-use the
text by referring to a variable.

{% include side-by-side.html demo="template" %}

The `content` of a `template` may contain [Mako] and [Markdown].

The name after `template:` is a [variable name] that you can refer to
elsewhere.

The `template` block, like [`question`] and [`code`] blocks, offers to
define a variable.  So when **docassemble** needs to know the
definition of `disclaimer` and finds that `disclaimer` is not defined,
it will look for a [`question`], [`code`], or `template` block that offers
to define `disclaimer`.  If it finds the `template` block above, it
will define the `disclaimer` variable.

A template, once defined, is a variable of type [`DATemplate`].
However, this variable will be undefined each time the screen loads.
Therefore, if the variables that the template depends on are
redefined, the template will change accordingly.

Optionally, a `template` can have a `subject`:

{% include side-by-side.html demo="template-subject" %}

You can refer to the two parts of the template by writing, e.g.,
`disclaimer.subject` and `disclaimer.content`.

Note that writing `${ disclaimer }` has the same effect as writing `${
disclaimer.content }`.

Templates are also useful for defining the content of e-mails.  See
[`send_email()`] for more information on using templates with e-mails.

You might prefer to write text in [Markdown] files, rather than in
[Markdown] embedded within [YAML].  To facilitate this,
**docassemble** allows you to create a `template` that references a
separate [Markdown] file.

{% include side-by-side.html demo="template-file" %}

The file [`disclaimer.md`] is a simple [Markdown] file containing the
disclaimer from the previous example.

The `source file` is assumed to refer to a file in the "templates"
folder of the same package as the interview source, unless a specific
package name is indicated.  (e.g., `source file:`
[`docassemble.demo:data/templates/hello_template.md`])

In the example above, the sample interview is in the file
[`docassemble.base:data/questions/examples/template-file.yml`], while
the [Markdown] file is located at
[`docassemble.base:data/templates/disclaimer.md`].

[`docassemble.demo:data/templates/hello_template.md`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/templates/hello_template.md
[`docassemble.base:data/questions/examples/template-file.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/examples/template-file.yml
[`docassemble.base:data/templates/disclaimer.md`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/disclaimer.md
[`disclaimer.md`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/disclaimer.md
[markup]: {{ site.baseurl }}/docs/markup.html
[documents]: {{ site.baseurl }}/docs/documents.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[Python]: https://www.python.org/
[`DATemplate`]: {{ site.baseurl }}/docs/objects.html#DATemplate
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`code`]: {{ site.baseurl }}/docs/code.html#code
[variable name]: {{ site.baseurl }}/docs/fields.html#variable names
[YAML]: https://en.wikipedia.org/wiki/YAML
