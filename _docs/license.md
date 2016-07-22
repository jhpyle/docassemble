---
layout: docs
title: License
short_title: License
---

**Docassemble** is licensed under the [MIT License].  This means that
a fork of the project could be distributed as non-free software.

Note that **docassemble** has a number of dependencies, which have
various licenses of their own.

Some of these dependencies are [Python] packages that are installed
automatically when the **docassemble** packages are installed using
[pip].  Licenses used by [Python] libraries include the BSD License,
Apache License, [MIT License], Standard PIL License, Python Software
Foundation License, ISC License, the LGPL, and the Zope Public
License, among others, including variations on these standard
licenses.  To the best of the developer's knowledge, none of the
libraries on which **docassemble** depends is licensed under the GPL
or any other license that would impair the licensing of
**docassemble** under the [MIT License].

Other dependencies are [requirements] that are expected to be
available on the system.  These dependencies include C libraries that
are needed by some [Python] packages on which **docassemble** relies.
To the best of the developer's knowledge, none of these libraries is
licensed under the GPL or any other license that would impair the
licensing of **docassemble** under the [MIT License].

In addition to depending on libraries, **docassemble** depends on
certain applications that it calls using [subprocess] calls, including
[Pandoc], [LaTeX], [PDFtk], and [ImageMagick].  Some of these
dependencies are licensed under the GNU Public License.  The use of
GPL-licensed software by **docassemble** using [subprocess] calls does
not impair the licensing of **docassemble** under the [MIT License].
The Free Software Foundation explains that [mere aggregation] of GPL
software with other software does not mean that the non-GPL software
is covered by the GPL.

While the code of **docassemble** itself is licensed under the
[MIT License], note that this does not mean that a [Docker] image
containing **docassemble**, its dependencies, and Linux support files,
is a product wholly licensed under the [MIT License].  Each component
of the image has its own license.  The building of a [Docker] image is
[mere aggregation], so that the bundling of non-GPL software in a
[Docker] image along with GPL software will not bring the non-GPL
software under the GPL.

The **docassemble** interviews that you develop are "code" that you
can license as you wish.  **Docassemble** interprets that code as
data.  The [`code`] blocks in your **docassemble** interviews are
evaluated using Python's [`eval()`] and [`exec()`] statements.  These
[`code`] blocks, and any [Python] modules that you create and bundle
with your interviews, could potentially link to GPL-licensed [Python]
modules if you [`import`] them.  These modules would load into the
[WSGI] process and become dynamically linked with your code.
Therefore, your [`import`]ation of GPL-licensed software into your
**docassemble** interviews may bring your interview source code under
the GPL, which may not be what you want.  As explained above,
**docassemble** does not depend on any GPL-licensed [Python] modules,
so this danger will only arise if you install additional modules.

[`import`]: https://docs.python.org/3/reference/import.html
[Docker]: https://www.docker.com/
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[requirements]: {{ site.baseurl }}/docs/requirements.html
[MIT License]: https://en.wikipedia.org/wiki/MIT_License
[subprocess]: https://docs.python.org/2/library/subprocess.html
[`eval()`]: https://docs.python.org/2/library/functions.html#eval
[`exec()`]: https://docs.python.org/2/reference/simple_stmts.html#exec
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[`code`]: {{ site.baseurl }}/docs/code.html#code
[mere aggregation]: https://www.gnu.org/licenses/gpl-faq.en.html#MereAggregation
[pip]: https://en.wikipedia.org/wiki/Pip_(package_manager)
[Pandoc]: http://johnmacfarlane.net/pandoc/
[LaTeX]: http://www.latex-project.org/
[PDFtk]: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/
[ImageMagick]: http://http://www.imagemagick.org/
