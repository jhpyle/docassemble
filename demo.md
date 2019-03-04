---
layout: docs
title: A demonstration of docassemble
short_title: Demo
order: 10
---

You can 
[run a simple demonstration](https://demo.docassemble.org?i=docassemble.demo:data/questions/questions.yml){:target="_blank"}
to see **docassemble** in action.

<a class="btn btn-primary btn-lg" href="https://demo.docassemble.org?i=docassemble.demo:data/questions/questions.yml" target="_blank">Run the demo</a>

Note that the example interview is not intended to make logical sense
as an interview (in fact it is rather silly); it is simply intended to
demonstrate the features of **docassemble**.

The interface is based on [Bootstrap], which is both mobile-friendly
and desktop-friendly.  Try it out on a mobile device.

While you are using the demonstration, you can click "Source" to see
the [YAML] source code that generated the question, along with a
review of the conditions that led to the question being asked.  You
can learn a lot about how to do things in **docassemble** by clicking
"Source" and comparing the [YAML] source to the end result.  The
"Source" tab is only available because the demo server is configured
as a development server (by setting `debug: True` in the
[configuration file]).  End users will not see a "Source" tab.

The two documents are generated from [Markdown] templates that are
written in the [YAML], but **docassemble** also supports generating
documents from [Microsoft Word templates].

The full source code for the interview is available in the
[`questions.yml`] file.  This file incorporates by reference the
[`basic-questions.yml`] file, where much of the interview's
functionality is defined.

To see other functionality of **docassemble**, you can explore the
[documentation].  Whenever there is a side-by-side example of code and
a screenshot, you can click the screenshot to run the example interview.

[Markdown]: https://daringfireball.net/projects/markdown/
[Microsoft Word templates]: {{ site.baseurl}}/docs/documents.html#docx template file
[`questions.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/questions.yml
[`basic-questions.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[Bootstrap]: https://en.wikipedia.org/wiki/Bootstrap_%28front-end_framework%29
[YAML]: https://en.wikipedia.org/wiki/YAML
[configuration file]: {{ site.baseurl }}/docs/config.html#debug
[documentation]: {{ site.baseurl }}/docs.html
