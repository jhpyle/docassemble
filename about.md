---
layout: page
short_title: About
title: What is docassemble?
permalink: /about/
---

**docassemble** is a free, open-source expert system for guided
interviews and document assembly.  It provides a web site that
conducts "interviews" with users.  Based on the information gathered,
the interviews can present users with documents in PDF and RTF format,
which users can download or e-mail to themselves.

**docassemble** was created by a lawyer/computer programmer for
purposes of automating the practice of law, but it is a
general-purpose platform that can find applications a variety of
fields.

Though the name emphasizes the document assembly feature,
**docassemble** interviews do not need to assemble a document; they
might submit an application, direct the user to other resources on the
internet, or simply provide the user with information.

## Features

### User-friendly

The user interface is user-friendly.  **docassemble** uses [Bootstrap]
to provide a mobile-friendly and desktop-friendly interface.  In
addition to gathering yes/no answers and fill-in forms,
**docassemble** can collect uploaded documents, pictures taken with a
smartphone, and the user's signature, which the user can write using a
touchscreen or mouse.  The documents created by **docassemble** can
incorporate the user's signature and/or uploaded images.

### Easy to develop

Interviews in **docassemble** are easy to create.  Interviews are
authored as [YAML] files.  Within the [YAML] files, the text of the
interview questions and documents is written in [Markdown], and the
logic of the interview flow is created by writing if/then/else
statements in [Python].

Authors do not need to have any prior experience with [Python] or
computer programming in order to author interviews.  The only [Python]
statements authors will need to write are rudimentary statements that
are very close to plain English.  For example:

	if user.is_citizen or user.is_legal_permanent_resident:
	  user.is_eligible = True
	else:
	  user.is_eligible = False

The [Markdown] language is very simple.  For example, if you write
this [Markdown] text:

    It is *very* important that you obtain your
    [free credit report](https://www.annualcreditreport.com) as soon
    as possible.

then you get text that looks like this:

> It is *very* important that you obtain your
> [free credit report](https://www.annualcreditreport.com) as soon
> as possible.

**docassemble** interviews are especially easy to create because
interview authors do not have to design the "flow" of the interview;
**docassemble** will determine what questions to ask, and the order in
which to ask them, based on what information is necessary to gather.
The system will refrain from asking unnecessary questions.  For
example, if a question or document contains a conditional statement
such as:

    % if user_is_disabled or user.age > 60:
      We have special funding to assist you.
    % endif
	  
then the user will be asked if he is disabled, and will only be asked
for his age if he says he is not disabled.  Authors need to provide a
question for every variable (e.g., there need to be questions that
determine `user_is_disabled` and `user.age`) but **docassemble** will
automatically figure out when and whether to ask those questions.

This allows authors to concentrate on the end result rather than
worrying about how to construct an interview process.  Authors who are
lawyers can "practice at the top of their license" by spending their
time thinking about the law (a lawyer function) rather than thinking
about the interview process (a non-lawyer function).

[YAML] has a very short set of rules, so it is not hard to learn.
**docassemble**'s YAML files are pretty easy to read, and if you forget
the right words to use, you can easily copy, paste, and edit an
example.

There are many text editors that have special features for editing
[YAML] files.  On Windows, the best is [Notepad++].

### The full power of Python

While interview authors do not need to by [Python] experts, authors
who know [Python] (or are willing to learn [Python]) can extend the
functionality of the interviews by writing [Python classes].  This
allows the interviews to do anything [Python] can do (e.g., retrieve
information from web services, interact with databases, send e-mail,
interact with third-party APIs, etc.)

### Reusable content

Interview authors never have to reinvent the wheel because
**docassemble** allows interview questions and logic to be re-used.
By developing one interview, an author effectively creates a "library"
of questions that can be incorporated by reference into future
interviews.

An interview author writes a [YAML] file that is contained within a
[Python package].  Authors can incorporate the work of another author
simply by [installing] the other author's [Python package] on the server
and incorporating the author's interview questions or modules by
reference.  The web interface allows [Python packages] to be installed
either as .zip files or through the cloning of [GitHub] repositories.

### Multilingual

All of the text presented to the user of the **docassemble** web
application can be [translated] to a language other than English.
**docassemble** supports the full use of [Unicode] characters in
interviews.

### Multi-purpose

At its core, **docassemble** is a multi-purpose expert system.  The
logic engine of **docassemble** is the [Python package]
`docassemble-base`, which provides an API.  The web application is a
separate [Python package], `docassemble-webapp`, which uses the API.
This allows for a number of possible applications.  For example, the
[Twilio API](https://www.twilio.com/docs/libraries) could be used
with `docassemble-base` to conduct interviews over the phone (using a
text-to-speech engine) or through text messaging.  A single interview
file (i.e., a [YAML] file) could be used to power both a web-based
interview and a telephone interview.

### Superior to the alternatives

Much of what **docassemble** does can be accomplished with [HotDocs] and
[A2J].  However, **docassemble** has superior features for incorporating
"libraries" of questions.  Since all the authoring is done within a
YAML file, content can easily be reused through incorporation by
reference (the "include" function) or copy-and-paste.

While for some people, **docassemble** may have a steeper learning
curve than [A2J] and [HotDocs], but in the long run, creating forms
and interviews in **docassemble** is more efficient because everything
can be created in a text editor.  **docassemble** was designed to
minimize unnececessary work.  For example, it does not require authors
to give names to every interview question.

In addition, **docassemble** gives authors all the power and
convenience of a general-purpose, object-orientated programming
language.

[HotDocs] is a proprietary system, and its usefulness in a server
environment is limited by licensing requirements.  By contrast,
**docassemble** is free and open source.

## Technical details

The **docassemble** web application is a [WSGI] application written in
[Python] that runs on a server and stores information with a SQL
database.

In the web app, interviews are loaded into the app as Python
subpackages of the **docassemble** package (e.g.,
docassemble.hello-world).  Packages can be loaded directly from
[GitHub] or from a .zip file.  This can be done
entirely [through the web interface].  The [YAML] interview file is a
data file within this package.

To create a new **docassemble** interview, the author logs in through
the web application's [sign-in system] and generates a new [Python]
extension package, which the author downloads as a .zip file and
unpacks on his or her computer.  The author writes interview questions
by editing a file (typically `questions.yml`) that is located within
the `data/questions` subfolder of the [Python package].  If the author
wishes to extend the functionality of the interview with [Python]
code, he or she can edit a [Python module] (typically `objects.py`).

The interview files are written in [YAML].  Within the [YAML] file,
interview questions and document text are represented in [Markdown]
enhanced with the [Mako] templating system.  [Mako] allows the full
power of [Python] to be embedded into interview [questions] and [document
templates].  Documents are converted from [Markdown] into PDF, RTF, and
HTML using [pandoc](http://johnmacfarlane.net/pandoc/).

To test the interview, the author re-packs the [Python] subpackage as
a .zip file and [uploads] it to a **docassemble** server.  Alternatively,
the author can push the [Python package] to a [GitHub] repository and
then tell the web application to install the package directly from
[GitHub].  [GitHub] and Microsoft have developed a user-friendly
[GitHub] application for Windows, which makes this process very easy.

**docassemble** figures out which questions to ask by taking advantage
of the exception-trapping features of [Python].  **docassemble** will
try to assemble a document or process a logic statement, but when it
encounters a variable that is undefined, a [NameError] exception is
triggered.  That exception is trapped and then **docassemble** looks
for an interview question that provides the missing variable.  That
question itself might depend on a variable that is undefined, which
leads to another [NameError] exception, and then **docassemble** will
again look for an interview question that provides the missing
variable, and so on.

The process is repetitive, but it runs quickly because the Python and
[Mako] code within interviews is compiled at the time the interview's
[YAML] file (and its dependencies) are loaded.  In a web server
environment, interviews can be cached in memory, so the compilation
only needs to take place the first time a [WSGI] process sees a given
interview, or any time the interview's underlying [YAML] file is
changed (which in a production environment is very rarely).  As the
user answers questions in the web app, the interview state (containing
the user's answers) is stored in a [Python dictionary] that is
[serialized] and saved to a database.  The next question is obtained
by calling a method on the cached instance of the Interview object
with the [dictionary] as an argument.  All the compiled code
representing the logic of the interview remains in the memory of the
[WSGI] process.

Furthermore, because state is saved as a [serialized object] in a
database, multiple servers in a load-balanced arrangement can be used
to serve the interviews.  Different servers could handle the same
interview for the same user, just as different [WSGI] processes handle
the same interview on a single server.

[Markdown]: https://daringfireball.net/projects/markdown/syntax
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[YAML]: https://en.wikipedia.org/wiki/YAML
[Bootstrap]: https://en.wikipedia.org/wiki/Bootstrap_%28front-end_framework%29
[GitHub]: https://github.com/
[Mako]: http://www.makotemplates.org/
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[serialized]: https://docs.python.org/2/library/pickle.html
[HotDocs]: https://en.wikipedia.org/wiki/HotDocs
[A2J]: https://www.kentlaw.iit.edu/institutes-centers/center-for-access-to-justice-and-technology/a2j-author
[Python package]: https://docs.python.org/2/tutorial/modules.html#packages
[Python packages]: https://docs.python.org/2/tutorial/modules.html#packages
[through the web interface]: {{ site.baseurl }}/docs/packages.html
[installing]: {{ site.baseurl }}/docs/packages.html
[Python classes]: https://docs.python.org/2/tutorial/classes.html
[translated]: {{ site.baseurl }}/docs/language.html
[Unicode]: https://en.wikipedia.org/wiki/Unicode
[sign-in system]: {{ site.baseurl }}/docs/users.html
[Python module]: https://docs.python.org/2/tutorial/modules.html
[questions]: {{ site.baseurl }}/docs/questions.html
[document templates]: {{ site.baseurl }}/docs/documents.html
[uploads]: {{ site.baseurl }}/docs/packages.html
[NameError]: https://docs.python.org/2/library/exceptions.html#exceptions.NameError
[serialized object]: https://docs.python.org/2/library/pickle.html
[Notepad++]: http://notepad-plus-plus.org/
