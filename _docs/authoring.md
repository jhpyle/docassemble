---
layout: docs
title: Documentation overview
short_title: Overview
---

# Sections of the documentation relating to interview authoring

**docassemble** is a platform for creating mobile-friendly web
applications called [Interviews] that ask one question at a time in
order to reach an end point.  This end point may be the presentation
of legal advice, the creation of a signed legal document, the
submission of an application, or something else.  Run the
[Demonstration] to get an idea for what **docassemble** applications
look like.

For a quick introduction to **docassemble** authoring, look at the
[Hello World] tutorial.

Authors write interviews in [YAML] format, a plain-text format that is
human-readable but also machine-readable.

An interview consists of multiple "blocks."  Blocks are pieces of text
separated by `---`, which is a record separator in [YAML].

{% highlight yaml %}
---
question: Do you like turnips?
yesno: likes_turnips
---
question: When did you stop idolizing worms?
fields:
  - Date: worm_idolizing_stop_date
    datatype: date
---
{% endhighlight %}

Some blocks are [Initial Blocks], which set things up in the background.

Other blocks are [Question Blocks] that represent screens that the
user will actually see.  The basic structure of question blocks is
simple, but there are a lot of possible [Question Modifiers] that can
make your screens do different things.

The information gathered from users is stored in Python "variables,"
and the purpose of most question blocks will be [Setting Variables].
You can use whatever variable names you want, as long as they do not
conflict with any [Reserved Names].

[Code] blocks allow you to set variables through computation.  Code is
written in [Python].  To write an interview, you do not need to know
much about [Python] except how to write "if/then/else" statements.

{% highlight yaml %}
code: |
  if plaintiff.county == defendant.county:
    jurisdiction_is_proper = True
{% endhighlight %}

If you want, you can even use "fuzzy logic" with **docassemble**'s
[Machine Learning] feature.

**docassemble** decides which questions to ask, and the order in which
to ask them, according to the [Interview Logic].  You can specify the
order of questions with great specificity if you want, or you can just
specify an end goal and let **docassemble** figure everything out on
its own.

A popular use of interviews is the assembly of [Documents] (hence the
name **docassemble**).  You write documents the same way you write
questions, in plain text with [Markup] to indicate formatting.
You can re-use text in different contexts using [Templates].

When collecting information from users, it is useful to store the
information in a structured way using [Objects].  When you want to
collect one or more pieces of related information, you can structure
information into [Groups].

As your interviews become more sophisticated, you will find it useful
to use [Functions] to do things like conjugate verbs, compute
differences between dates, or offer the user hyperlinks that perform
special [actions].

**docassemble** is a multi-purpose platform, but it is particularly
designed for [Legal Applications], and has special functionality for
that specific purpose.

One of **docassemble**'s most powerful features is its ability to
operate multi-user interviews through the [Roles] feature.

A number of advanced features can be accessed controlled through
[Special Variables], such as pre-populating variables in your
interview by embedding the values in the URL with which the user
accesses the interview.

Interviews do not have to be ephemeral.  There is a [User Login]
system that allows users to create accounts, save their answers, and
resume their interviews at a later date.

Using the [Background Tasks] features, you can have your interviews do
things on the server at times other than times when the user presses a
button to advance to a new page.  Time-intensive tasks can run in the
background; the interview can evaluate user input before the user
submits it; and interviews can do things when the user is not logged
in, like send a reminder e-mail to a user about a deadline as the date
approaches.

If you need to make an interview available in more than one language,
**docassemble**'s [Language Support] features can help you manage
translations.

Authors will invariably make mistakes and encounter [Errors].
**docassemble** tries to provide helpful error messages in the browser
or in logs stored on the server.

**docassemble**'s authoring system was built on the model of the
open-source software development community.  Interviews can be bundled
into [Packages], which can be shared on [GitHub] or moved between
servers as ZIP files.

Authors can prototype and test their interviews in the browser, using
the "interview developers' [Playground]."

The mobile-friendly web interface is the primary way that users will
run interviews, but there is also the option of making interviews
available via [Text Messaging].

When you deploy your interviews, there are a variety of ways you can
provide support to your users.  The [Live Help] features allow
operators to communicate with users using on-line chat.  Operators can
see users' screens and even take control if necessary.  If
communication by phone is necessary, operators can provide users with
a special phone number and code that forwards a call without revealing
the operator's actual phone number.

# Other sections of the documentation

Authors should focus on the creative aspects of interview writing and
not have to worry about how the **docassemble** software is made
available to users on the internet.

The best way to deploy **docassemble** is through [Docker], which
effectively automates the otherwise complicated [Installation] and
[Configuration] process.

System administrators will be pleased to know that **docassemble** has
excellent [Scalability] when deployed in the cloud.

Lawyers will be pleased to know that **docassemble** has a number of
[Security] features, such as server-side encryption.

Financial officers will be pleased to know that **docassemble** is
free software available with a highly permissive open-source
[License].

[Installation]: {{ site.baseurl }}/docs/installation.html
[Configuration]: {{ site.baseurl }}/docs/config.html
[Hello World]: {{ site.baseurl }}/docs/helloworld.html
[Interviews]: {{ site.baseurl }}/docs/interviews.html
[Initial Blocks]: {{ site.baseurl }}/docs/initial.html
[Question Blocks]: {{ site.baseurl }}/docs/questions.html
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[Question Modifiers]: {{ site.baseurl }}/docs/modifiers.html
[Code]: {{ site.baseurl }}/docs/code.html
[Interview Logic]: {{ site.baseurl }}/docs/logic.html
[Templates]: {{ site.baseurl }}/docs/template.html
[Documents]: {{ site.baseurl }}/docs/documents.html
[Markup]: {{ site.baseurl }}/docs/markup.html
[Objects]: {{ site.baseurl }}/docs/objects.html
[Groups]: {{ site.baseurl }}/docs/groups.html
[Functions]: {{ site.baseurl }}/docs/functions.html
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[Legal Applications]: {{ site.baseurl }}/docs/legal.html
[Roles]: {{ site.baseurl }}/docs/roles.html
[Special Variables]: {{ site.baseurl }}/docs/special.html
[Background Tasks]: {{ site.baseurl }}/docs/background.html
[Machine Learning]: {{ site.baseurl }}/docs/ml.html
[Reserved Names]: {{ site.baseurl }}/docs/reserved.html
[Errors]: {{ site.baseurl }}/docs/errors.html
[Language Support]: {{ site.baseurl }}/docs/language.html
[User Login]: {{ site.baseurl }}/docs/users.html
[Packages]: {{ site.baseurl }}/docs/packages.html
[Playground]: {{ site.baseurl }}/docs/playground.html
[Live Help]: {{ site.baseurl }}/docs/livehelp.html
[Text Messaging]: {{ site.baseurl }}/docs/sms.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[Scalability]: {{ site.baseurl }}/docs/scalability.html
[Security]: {{ site.baseurl }}/docs/security.html
[License]: {{ site.baseurl }}/docs/license.html
[Demonstration]: {{ site.baseurl }}/demo.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[GitHub]: https://github.com/
