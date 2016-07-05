---
layout: page
short_title: About
title: What is docassemble?
permalink: /about/
---

**docassemble** is a free, open-source expert system for guided
interviews and document assembly.  It provides a web site that
conducts interviews with users.  Based on the information gathered,
the interviews can present users with documents in PDF and RTF format,
which users can download or e-mail.

**docassemble** was created by a lawyer/computer programmer for
purposes of automating the practice of law, but it is a
general-purpose platform that can find applications in a variety of
fields.

Though the name emphasizes the document assembly feature,
**docassemble** interviews do not need to assemble a document; they
might submit an application, direct the user to other resources on the
internet, or simply provide the user with information.

## Features

### User-friendly

The interface is user-friendly.  **docassemble** uses [Bootstrap] to
provide a mobile-friendly and desktop-friendly interface.  In addition
to gathering yes/no answers and fill-in forms, **docassemble** can
collect uploaded documents, pictures taken with a smartphone, and the
user's signature, which the user can write using a touchscreen or
mouse.  The documents created by **docassemble** can incorporate the
user's signature and uploaded images.  Audio and video can be easily
integrated into questions; in particular, **docassemble** integrates
with [Voice RSS] to provide on-the-fly text-to-speech generation.
Interviews can provide the user with information relevant to their
current physical location by accessing the geolocation feature of the
user's browser, and present Google Maps to the user on the basis of
addresses geocoded with [Google's geocoding API].

### Easy to develop

Interviews in **docassemble** are easy to create.  Interviews are
authored as [YAML] files.  Within the [YAML] files, the text of the
interview questions and documents is formatted with [Markdown], and
the logic of the interview flow is created by writing if/then/else
statements in [Python].

Authors do not need to have any prior experience with [Python] or
computer programming in order to create **docassemble** interviews.
The only [Python] statements authors will need to write are
rudimentary statements that are very close to plain English.  For
example:

{% highlight python %}
if user.is_citizen or user.is_legal_permanent_resident:
  user.is_eligible = True
else:
  user.is_eligible = False
{% endhighlight %}
      
The [Markdown] language is very simple.  For example, if you write
this [Markdown] text:

{% highlight text %}
It is *very* important that you obtain your
[free credit report](https://www.annualcreditreport.com) as soon
as possible.
{% endhighlight %}

then you get text that looks like this:

> It is *very* important that you obtain your
> [free credit report](https://www.annualcreditreport.com) as soon
> as possible.

**docassemble** interviews are especially easy to create because
interview authors do not have to design the "flow" of the interview;
**docassemble** will determine what questions to ask, and the order in
which to ask them, based on what information is necessary to gather.
The system will refrain from asking unnecessary questions.  For
example, if the interview contains a conditional statement such as:

{% highlight python %}
if user.is_disabled or user.age > 60:
  special_funding_exists = True
else:
  special_funding_exists = False
{% endhighlight %}
	  
then the user will be asked if he is disabled, and will only be asked
for his age if he says he is not disabled.  Authors need to provide a
question for every variable (e.g., there need to be questions that
determine `user.is_disabled` and `user.age`) but **docassemble** will
automatically figure out when and whether to ask those questions.

This allows authors to concentrate on the end result rather than
worrying about how to construct the interview process.  Authors who
are lawyers can "practice at the top of their license" by spending
their time thinking about the law (a lawyer function) rather than
thinking about the interview process (a non-lawyer function).

[YAML] has a very short set of rules, so it is not hard to learn.
**docassemble**'s [YAML] files are pretty easy to read, and if you
forget the right words to use, you can easily copy, paste, and edit an
example.

There are many text editors that have special features for editing
[YAML] files.  On Windows, the best is [Notepad++], and [Sublime Text]
works pretty well, too.

### The full power of Python

While interview authors do not need to be [Python] experts, authors
who know [Python] (or are willing to learn [Python]) can extend the
functionality of the interviews by writing [Python classes].  This
allows the interviews to do anything [Python] can do (e.g., retrieve
information from web services, interact with databases, interact with
third-party APIs, etc.)

**docassemble** contains [built-in support] for interview authors to
accomplish common tasks that would otherwise require significant
coding.  For example, sending an HTML e-mail with documents attached
to it can be accomplished in one line of code.

### Reusable content

Interview authors never have to reinvent the wheel because
**docassemble** allows interview questions and logic to be re-used.
By developing one interview, an author effectively creates a "library"
of questions that can be incorporated by reference into future
interviews.

Interviews are written as [YAML] files that are contained within a
[Python package].  This allows the **docassemble** authoring community
to take advantage of the [Python] package distribution and
installation system.  Authors can incorporate the work of another
author simply by [installing] the other author's [Python package] on
the server and incorporating the author's interview questions or
modules by reference.  The web interface allows [Python packages] to
be installed either as .zip files, through the cloning of [GitHub]
repositories, or through installation from [PyPI].

### Secure

User answers are stored on a server in an encrypted format, so that
even if someone were to gain access to the server, they would need to
somehow figure out a user's password in order to decrypt the user's
answers.  (Users who are not logged in yet are given a random key,
which is stored as a cookie.)  User passwords are stored in hashed
format, not in plain text, so that they cannot be discovered.

**docassemble** deletes user information whenever possible.  For
example, if a user finishes an interview and exits, the user's answers
and any uploaded documents are deleted from the database.

**docassemble** can easily be [set up] to run on [HTTPS] rather than
[HTTP] in order to encrypt the traffic between the browser and the
server.  SSL certificates are available at no cost from companies like
[StartCom].  In addition, **docassemble** has built-in support for
using [Let's Encrypt].

### Multilingual

All of the text presented to the user of the **docassemble** web
application can be [translated] to a language other than English.
**docassemble** supports the full use of [Unicode] characters in
interviews.

### Multi-purpose

At its core, **docassemble** is a multi-purpose expert system.  The
logic engine of **docassemble** is the [Python package]
`docassemble.base`, which provides an API.  The web application is a
separate [Python package], `docassemble.webapp`, which uses the API.
This allows for a number of possible applications.  For example, the
[Twilio API](https://www.twilio.com/docs/libraries) could be used with
`docassemble.base` to conduct interviews over the phone (using a
text-to-speech engine) or through text messaging.  A single interview
file (i.e., a [YAML] file) could be used to power both a web-based
interview and a telephone interview.

### Superior to the alternatives

Much of what **docassemble** does can be accomplished with [HotDocs]
and [A2J].  If the logic behind an interview is easy to flowchart, or
being able to create the document template in Microsoft Word is
important so as to have fine-grained control over document formatting,
then the [A2J]/[HotDocs] platform may be preferable.

However, many of **docassemble**'s features are not available yet in
the [A2J]/[HotDocs] platform, such as electronic signatures, document
uploads, text-to-speech, ability to generate documents in the middle
of interviews as opposed to only at the end, and multi-user
interviews.

In addition, **docassemble** does many things that [A2J] and [HotDocs]
can do, but does them better.  For example, **docassemble** has
superior features for incorporating "libraries" of questions (which
might reference other "libraries," which in turn reference other
"libraries," etc.).  Since all the authoring is done within a [YAML]
file, content can easily be reused through incorporation by reference
(using the [include] function) or copy-and-paste.  By contrast,
[HotDocs] allows one component file to be imported, but does not allow
such inclusions to be nested.  All of the content of an [A2J] or
[HotDocs] interview is effectively locked inside the
graphical user interface.

For some people, **docassemble** may have a steeper learning curve
than [A2J] and [HotDocs].  [A2J] is optimized for legal professionals
without a technical background.  **docassemble**, by contrast, makes
no compromises that would impede professional coders from working as
efficiently as possible.

While [A2J] and [HotDocs] may be easier for the uninitiated, authors
who try to go beyond the specific use cases that the developers of
[A2J] and [HotDocs] had in mind will find themselves devising
complicated workarounds in order to achieve their goals.  In
**docassemble**, it will never be necessary to create such
workarounds.  Most features that an author might want to add can be
implemented in a simple and straightforward fashion by writing a
[Python] class or inserting [Javascript] into a question, all of which
can be done without changing **docassemble**'s code.  And if that is
not enough, authors can modify the **docassemble** code and submit a
[pull request] to include the changes in the latest version of
**docassemble**.

In general, tools that offer users the ability to develop software
"without writing code" actually do make users write code, just in an
indirect way using a graphical user interface.  This makes the
learning curve less steep at the expense of limiting the user's
freedom once they have climbed the learning curve.  **docassemble**
takes a different approach.  It does not hide the code from the
author.  It tries to make writing code as easy as possible, but it
does not limit what the author can do.

In the long term, creating forms and interviews in **docassemble** is
more efficient than creating them in [A2J] and [HotDocs] because:

1. Authors do not have to plan out every last detail of the interview
flow;
2. Authors have the power of "copy and paste" and "search and
replace" at their fingertips;
3. The ability to share common questions across multiple interviews
and incorporate libraries of questions means that authors can easily
re-use their own past work and the work of other authors in the
community; and
4. **docassemble** uses objects as variables, not just boolean and
text values.  The features of object-oriented programming, including
object methods and inheritance, save the developer a great deal of
time and greatly simplify the appearance of code.

Perhaps most importantly, **docassemble** gives authors all the power
and convenience of a general-purpose, object-orientated programming
language.  While the programming language within [HotDocs] is
proprietary and fixed, [Python] is fully extensible.  **docassemble**
authors can include any of the more than 70,000 [Python] packages
available on [PyPI], [Github], and other sites.  Code written by
**docassemble** authors can easily be shared and re-used by others in
the authoring community.

**docassemble** is also a superior system because it is free and
open-source.  [HotDocs] is a proprietary system, and its usefulness in
a web server environment is limited by licensing requirements.  By
contrast, **docassemble** is free and open source, and can easily be
[set up in a multi-server environment] by anyone.

#### **docassemble** vs. rules engines

In addition to [A2J] and [HotDocs], there are other existing expert
systems.  Many of these, like [Drools], are based on "rules engines."
If a rules-based approach to expressing logic is appropriate for an
application, **docassemble** may not be the best system.

However, **docassemble**'s approach, which is to express logic using
code, is likely to be better suited for legal applications.
Developers of legal expert systems have observed that when they ask
lawyers to express their expertise in the form of rules, the lawyers
first express the knowledge in the form of sequential logical
statements (i.e., [pseudocode]) and then attempt to translate that
"code" into "rules."  **docassemble** cuts out the extra step by
allowing legal experts to express legal knowledge in the form that
comes naturally.  Among general purpose programming languages,
[Python] is very close to plain English.  As a result, **docassemble**
code that embodies legal knowledge will look similar to the language
of statutes and regulations, which is familiar to legal professionals.

While **docassemble** is different from a "rules engine" because it
allows authors to express knowledge as code, it also has some of the
features of a "rules engine."  Authors can express knowledge in the
form of multiple discrete chunks of code, and **docassemble** will
automatically decide whether and when those discrete chunks need to be
used.  When the author references information (i.e. a variable), the
author does not need to worry about whether the information has been
gathered yet (i.e. whether the variable is defined); if the
information has not been gathered yet, **docassemble** will gather
it.

## Technical details

The **docassemble** web application is a [WSGI] application written in
[Python] that runs on a server and stores information with a SQL
database.

In the web app, interviews are loaded into the app as Python
subpackages of the **docassemble** package (e.g.,
docassemble.hello-world).  Packages can be loaded directly from
[GitHub] or from a .zip file.  This can be done entirely
[through the web interface].  The [YAML] interview file is a data file
within this package.

To create a new **docassemble** interview, the author logs in through
the web application's [sign-in system] and generates a new [Python]
extension package, which the author downloads as a .zip file and
unpacks on his or her computer.  The author writes interview questions
by editing a file (e.g., `questions.yml`) that is located within the
`data/questions` subfolder of the [Python package].  If the author
wishes to extend the functionality of the interview with [Python]
code, he or she can edit a [Python module] (typically `objects.py`).

The interview files are written in [YAML].  Within the [YAML] file,
interview questions and document text are represented in [Markdown]
enhanced with the [Mako] templating system.  [Mako] allows the full
power of [Python] to be embedded into interview [questions] and
[document templates].  Documents are converted from [Markdown] into
PDF, RTF, and HTML using [Pandoc].

To test the interview, the author re-packs the [Python] subpackage as
a .zip file and [uploads] it to a **docassemble** server.  Alternatively,
the author can push the [Python package] to a [GitHub] repository and
then tell the web application to install the package directly from
[GitHub].  [GitHub] and Microsoft have developed a user-friendly
[GitHub] application for Windows, which makes this process very easy.

For quicker testing of interview questions, the developer can test
**docassemble** interviews in the [Playground] area, which allows
[YAML] code to be entered and tested in the web browser.

**docassemble** figures out which questions to ask by taking advantage
of the exception-trapping features of [Python].  **docassemble** will
try to assemble a document or process a logic statement, but when it
encounters a variable that is undefined, a [NameError] exception is
triggered.  That exception is trapped and **docassemble** looks for an
interview question that provides the missing variable.  That question
itself might depend on a variable that is undefined, which leads to
another [NameError] exception, and then **docassemble** will again
look for an interview question that provides the missing variable, and
so on.

The process is repetitive, but it runs quickly because the [Python]
and [Mako] code within interviews is compiled at the time the
interview's [YAML] file (and its dependencies) are loaded.  Interviews
are cached in memory, so the compilation only needs to take place the
first time a [WSGI] process sees a given interview, or any time the
interview's underlying [YAML] file is changed (which in a production
environment is very rarely).  As the user answers questions in the web
app, the interview state (containing the user's answers) is stored in
a [Python dictionary] that is [serialized] and saved to a database.
The next question is obtained by calling a method on the cached
instance of the Interview object with the [dictionary] as an argument.
All the compiled code representing the logic of the interview remains
in the memory of the [WSGI] process.

Furthermore, because state is saved as a [serialized object] in a
database, [multiple servers] in a load-balanced arrangement can be
used to serve the interviews.  Different servers can handle the same
interview for the same user, just as different [WSGI] threads handle
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
[Sublime Text]: http://www.sublimetext.com/
[include]: {{ site.baseurl }}/docs/initial.html
[Playground]: {{ site.baseurl }}/docs/playground.html
[multiple servers]: {{ site.baseurl }}/docs/scalability.html
[Voice RSS]: http://www.voicerss.org/
[built-in support]: {{ site.baseurl }}/docs/legal.html
[Google's geocoding API]: https://developers.google.com/maps/documentation/geocoding/intro
[PyPI]: https://pypi.python.org/pypi
[set up in a multi-server environment]: {{ site.baseurl }}/docs/scalability.html
[pull request]: https://help.github.com/articles/using-pull-requests/
[Drools]: http://www.drools.org/
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
[pseudocode]: https://en.wikipedia.org/wiki/Pseudocode
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
[HTTPS]: https://en.wikipedia.org/wiki/HTTPS
[set up]: {{ site.baseurl }}/docs/config.html
[StartCom]: https://www.startssl.com/
[Pandoc]: http://johnmacfarlane.net/pandoc/
[Let's Encrypt]: https://letsencrypt.org/
