---
layout: page
title: About
permalink: /about/
---

## How does it work?

docassemble uses the [Mako](http://www.makotemplates.org/) templating
system, which allows the full power of the
[Python programming language](https://www.python.org/) to be embedded
into interview questions and document templates.  Documents are
composed in [Markdown](http://daringfireball.net/projects/markdown/)
and then converted using [pandoc](http://johnmacfarlane.net/pandoc/)
into other formats, such as HTML, RTF, and PDF.

It is meant to be as flexible as possible, so that Python programs can
present the interview questions and the resulting documents to the
user in any number of ways.  The most common method will be through
the web.  The package includes a web application for presenting
interview questions in mobile-responsive HTML format and saving
interview state to a database (see below for a demonstration), but
this is just one of many possible applications.  The docassemble API
could be used for conducting interviews over the phone (using a
text-to-speech engine) or through text messaging (e.g., using the
[Twilio API](https://www.twilio.com/docs/libraries)).

To create a docassemble interview, the author writes a
[YAML](http://yaml.org) file that containing the interview questions,
logic, and the
[Markdown](http://daringfireball.net/projects/markdown/) source of any
documents to be assembled on the basis of the answers to the
questions.

While conducting an interview, docassemble will determine what
questions to ask, and the order in which to ask them, based on the
specified logic; the author does not need to specify the path of the
questions.  The system will refrain from asking the user unnecessary
questions.  For example, if a question or document contains a
conditional statement such as:

    % if user_is_disabled or user.age > 60:
      We have special funding to assist you.
    % endif
	  
then the user will be asked if he is disabled, and will only be asked
for his age if he says he is not disabled.  Authors need to provide a
question for every variable (e.g., ~user_is_disabled~ and ~user.age~)
but docassemble will figure out when and whether to ask those
questions.

This allows authors to concentrate on the end result rather than
worrying about how to construct an interview process.  Authors who are
lawyers can "practice at the top of their license" by spending their
time thinking about the law (a lawyer function) rather than thinking
about the interview process (a paralegal function).

In addition, there are many common questions that authors do not need
to think about at all; authors can incorporate by reference the
questions that other authors have written (in the form of one or more
[YAML](http://yaml.org) files), and thereby devote all of their
attention the special aspects of their interviews and documents.  ##
Has it been released yet?  docassemble is still in development, but it
is usable.

## Can I run a demo?

The [demonstration page](file:demo.org) contains a demo interview that
asks questions and assembles a document at the end.  It also contains
a complete annotated YAML source listing of the code used to generate
the interview.

## How does it compare with the alternatives?

Much of what docassemble does can be accomplished with HotDocs and
A2J.  However, docassemble has superior features for incorporating
"libraries" of questions.  Since all the authoring is done within a
YAML file, content can easily be reused through incorporation by
reference (the "include" function) or copy-and-paste.

While for some people, docassemble may have a steeper learning curve
than A2J and HotDocs, but in the long run, creating forms and
interviews in docassemble is probably more efficient because
everything can be created in a text editor.  docassemble was designed
to minimize unnececessary work.  For example, it does not require
authors to give names to every interview question.

In addition, docassemble gives authors all the power and convenience
of a general-purpose, object-orientated programming language.

HotDocs is a proprietary system, and its usefulness in a server
environment is limited by licensing requirements.  By contrast,
docassemble is free and open source.

Features of the docassemble web application include:

* Sign-in system with web-based registration, forgot-my-password
  support, and sign-in through Google and Facebook.
* File upload, so that users can include their own photographs and
  documents in the documents they assemble.
* Extension packages through [GitHub](http://github.com).  Interviews,
  code, and images can easily be shared among developers so that
  nobody ever has to reinvent the wheel.

## Is writing a YAML file too difficult?

[YAML](http://yaml.org) has a very short set of rules, so it is not
hard to learn.  docassemble's YAML files are pretty easy to read, and
if you forget the right words to use, you can easily copy, paste, and
edit an example.  There are many text editors that have special
features for editing YAML files.  On Windows, the best is
[Notepad++](http://notepad-plus-plus.org/).

## Do I need to know Python in order to write docassemble interviews?

Prior experience coding in Python is not required.  The Python code
typically used in interviews is rudimentary.

## How can I run my interviews in the web app?

In the web app, interviews are loaded into the app as Python
subpackages of the docassemble package (e.g.,
docassemble.hello_world).  These packages can be loaded directly from
[GitHub](http://github.com) or from a .zip file.  The YAML interview
file is a data file within this package.

The web application provides a downloadable template (in the form of a
.zip file) of a Python package that you can use as a starting point
for writing an interview.  This provides an easy way for interview
authors to bundle docassemble interviews with supporting Python
modules.

## Is it fast?

Yes.

In some ways, the code is repetitive, so you might expect it to be
slow.  It goes along trying to assemble a document or calculate a
mandatory value, until it finds a variable that is undefined, and then
it generates a NameError exception, and that exception is trapped and
docassemble looks for an interview question that provides the missing
variable, and that question might depend on a variable that is
undefined, which leads to another NameError exception, and so on.

However, the process runs quickly because the Python and
[Mako](http://www.makotemplates.org/) code within interviews is
compiled at the time the interview's [YAML](http://yaml.org) file (and
its dependencies) are loaded and an instance of an Interview object is
created.  In a web server environment, these Interview instances can
be cached in memory, so the compilation only needs to take place the
first time a
[WSGI](http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface)
process sees a given interview, or any time the interview's underlying
[YAML](http://yaml.org) file is changed (which in a production
environment is very rarely).  As the user answers questions in the web
app, the interview state (containing the user's answers) is stored in
a Python
[dictionary](https://docs.python.org/2/tutorial/datastructures.html#dictionaries)
that is [serialized](https://docs.python.org/2/library/pickle.html)
and saved to a database.  The next question is obtained by calling a
method on the cached instance of the Interview object with the
dictionary as an argument.  So all the compiled code representing the
logic of the interview remains in the memory of the process.

Furthermore, because state is saved as a serialized object in a
database, multiple servers in a load-balanced arrangement could be
used to serve the interviews.  Different servers could handle the same
interview for the same user.

## Who wrote it?

Jonathan Pyle, jhpyle@gmail.com

## How do I get it?

The source code is
[available on GitHub](https://github.com/jhpyle/docassemble), where
the
[README](https://github.com/jhpyle/docassemble/blob/master/README.md)
explains how to install the software.

docassemble is free, open-source software.
