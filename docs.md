---
layout: docs
title: Overview of docassemble
short_title: Documentation
order: 20
---

**docassemble** is a platform for creating mobile-friendly web
applications called [Interviews] that ask one question at a time in
order to reach an end point.  This end point may be the presentation
of advice, the creation of a signed document, the submission of an
application, or something else.  Run the [Demonstration] to get an
idea for what **docassemble** applications look like.

You can run **docassemble** on your laptop, but most people run it "in
the cloud" on [Amazon Web Services], [Digital Ocean], or another
hosting service.  The [Deploy] page describes a variety of ways you
can get your own **docassemble** instance up and running.  You can
install **docassemble** on a server using [Docker] or (if you are an
expert) follow the detailed [Installation] instructions.  For the most
part, the [Administration] and [Configuration] of **docassemble** can
be handled through the web interface.

# <a name="intro"></a>Introduction to **docassemble**

Interview developers write interviews in [YAML] format, a plain-text
format that is human-readable but also machine-readable.

An interview consists of multiple "blocks."  Blocks are pieces of text
separated by `---`, which is a record separator in [YAML].  For
example:

{% include demo-side-by-side.html demo="turnips-worms" %}

You can click the screenshot above to see this interview in action.
If you hover over the source code, three dots will appear in the
lower-right corner; if you click the three dots, you can see full
interview [YAML] behind the sample interview.

Some blocks are [Question Blocks] that represent screens that the user
will actually see.  (Two examples are above.)  The basic structure of
question blocks is simple, but there are a lot of possible [Question
Modifiers] that can make your screens do different things.

The information gathered from users is stored in "variables," and the
purpose of most question blocks will be [Setting Variables].  You can
use whatever variable names you want, except you can't use the names
of [Special Variables] that already have their own meaning.

**docassemble** supports [many different types] of variables -- even
[file uploads] and [touchscreen signatures].  One of the most powerful
features is the ability to store information in a structured way using
[Objects].  When you want to collect one or more pieces of related
information, you can collect the information into [Groups] such as
[lists] and [dictionaries].

There are other types of blocks besides [`question`] blocks.

[Initial Blocks] set interview-wide options, like the special
[features] of an interview, or the default [screen parts].

[Code] blocks allow you to set variables through computation.  Code is
written in [Python].  To write an interview, you do not need to know
much about [Python] except how to write "if/then/else" statements.

{% highlight yaml %}
code: |
  if plaintiff.county == defendant.county:
    jurisdiction_is_proper = True
{% endhighlight %}

You can even use "fuzzy logic" with **docassemble**'s [Machine
Learning] feature.

**docassemble** decides which questions to ask, and the order in which
to ask them, according to the [Interview Logic].  You can specify the
order of questions with great specificity if you want, or you can just
specify an end goal and let **docassemble** figure everything out on
its own.

A popular use of interviews is the assembly of [Documents] (hence the
name **docassemble**).  You can write document templates in [DOCX] or
[PDF] formats.  You can also write documents the same way you write
questions, in plain text using [Markup] to indicate formatting.

As your interviews become more sophisticated, you will find it useful
to invoke [Functions] to do things like conjugate verbs, compute
differences between dates, or offer the user hyperlinks that perform
special [actions].

**docassemble** uses a [User Login] system that allows users to create
accounts, save their answers, and resume their interviews at a later
date.

Since **docassemble** is a free and open-source application, it is
designed to be interoperable with other applications.  There are a
variety of ways to work with [External Data]; you can move information
easily into and out of a **docassemble** interview session.  There is
also a full-featured [API] for interacting with **docassemble**
programmatically.  You can also design your own [Custom Front Ends].

Developers can prototype and test their interviews in the browser, using
the interview developers' [Playground].

Once you get a **docassemble** server [up and running], go through the
[Hello World] tutorial to learn more about how interviews work.  As
you become more experienced using the system, you may want to explore
using other [Development Workflows] than just the [Playground].

One of **docassemble**'s most powerful features is its ability to
operate multi-user interviews through the [Roles] feature.  For
example, a user could fill out an interview and then an attorney could
enter the interview to evaluate the information and provide legal
advice, which the user would see the next time they log in.

Using the [Background Tasks] features, you can have your interviews do
things on the server at times other than when the user presses a
button to advance to a new page.  Time-intensive tasks can run in the
[background].  The interview can [evaluate user input] before the user
clicks the Continue button.  Interviews can do things [when the user
is not logged in], like send a reminder [e-mail] to a user about a
deadline as the date approaches.

**docassemble** is a multi-purpose platform, but it is particularly
designed for [Legal Applications], and has special functionality for
that specific purpose.

If you need to make an interview available in more than one language,
**docassemble**'s [Language Support] features can help you manage
translations.  **docassemble** also has a number of features for
[Accessibility] by persons with disabilities.

**docassemble** was built on the model of the open-source software
development world.  Interviews can be bundled into [Packages], which
can be shared on [GitHub] or moved between servers as ZIP files.

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

**docassemble** has excellent [Scalability] when deployed in the
cloud, so you don't have to worry about what will happen if your
interviews get a lot of traffic.

If your interviews will process sensitive information, **docassemble**
has a number of [Security] features to keep that information safe,
such as server-side encryption.

Developers will invariably make mistakes and encounter [Errors].
**docassemble** tries to provide helpful error messages in the browser
or in logs stored on the server.

If you get stuck, you can seek out [Support] from the **docassemble**
community, in particular by posting a question on the **docassemble**
[Slack].  You might also find that there is an example interview in
the [Recipes] that will help you solve your problem.

**docassemble** is free software available with a highly permissive
open-source [License].  The software is updated frequently, and you
can see what new features are available by reading the [Change Log].

Note that if you have been using **docassemble** for a long time, you
need learn about the necessity of doing a [Python Upgrade].

# <a name="using documentation"></a>Using the documentation

The **docassemble** documentation is intended more as a reference
guide than as a manual that you have to read before getting started.

The best way to learn about **docassemble** is to start creating your
own interview.  Start by following along with the "Hello, world"
[tutorial] that explains how to create a simple interview.  Once you
get that working, you can experiment with adding more questions to it.

The best way to learn about more advanced **docassemble** features is
to study working examples.  The sections of this documentation site
contain a number of side-by-side examples comparing source code to
screenshots.  You can click on the screenshots to run the interviews.
The code next to the screenshots is often only an excerpt of the full
interview.  To see the full source code of the interview, hover over
the source code and click the button that appears in the lower right
corner.  In addition, while you are developing interviews in the
[Playground], you can browse working examples of many of
**docassemble**'s features.

There is also a full-featured sample interview linked from the
[demonstration page].  While you are using the interview you can click
"Source" in the navigation bar to toggle display of the source code
for the question and an explanation of the path **docassemble** took
to decide to ask that question.

# <a name="toc"></a>Sections of the documentation

<ul class="interiortoc">
{% for section in site.data.docs %}
<li>{{ section.title }}</li>
<ul>
{% include docs_section.html items=section.docs %}
</ul>
{% endfor %}
</ul>

[Hello World]: {{ site.baseurl }}/docs/helloworld.html
[Interviews]: {{ site.baseurl }}/docs/interviews.html
[Initial Blocks]: {{ site.baseurl }}/docs/initial.html
[Question Blocks]: {{ site.baseurl }}/docs/questions.html
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[Question Modifiers]: {{ site.baseurl }}/docs/modifiers.html
[Code]: {{ site.baseurl }}/docs/code.html
[Interview Logic]: {{ site.baseurl }}/docs/logic.html
[Markup]: {{ site.baseurl }}/docs/markup.html
[Documents]: {{ site.baseurl }}/docs/documents.html
[Objects]: {{ site.baseurl }}/docs/objects.html
[Groups]: {{ site.baseurl }}/docs/groups.html
[Functions]: {{ site.baseurl }}/docs/functions.html
[External Data]: {{ site.baseurl}}/docs/external.html
[Legal Applications]: {{ site.baseurl }}/docs/legal.html
[Special Variables]: {{ site.baseurl }}/docs/special.html
[Language Support]: {{ site.baseurl }}/docs/language.html
[Accessibility]: {{ site.baseurl }}/docs/accessibility.html
[Roles]: {{ site.baseurl }}/docs/roles.html
[background tasks]: {{ site.baseurl }}/docs/background.html
[Background Tasks]: {{ site.baseurl }}/docs/background.html
[Machine Learning]: {{ site.baseurl }}/docs/ml.html
[Text Messaging]: {{ site.baseurl }}/docs/sms.html
[API]: {{ site.baseurl}}/docs/api.html
[Custom Front Ends]: {{ site.baseurl }}/docs/frontend.html
[User Login]: {{ site.baseurl }}/docs/users.html
[Live Help]: {{ site.baseurl }}/docs/livehelp.html
[Development Workflows]: {{ site.baseurl }}/docs/development.html
[Playground]: {{ site.baseurl }}/docs/playground.html
[Packages]: {{ site.baseurl }}/docs/packages.html
[Errors]: {{ site.baseurl }}/docs/errors.html
[Support]: {{ site.baseurl }}/docs/support.html
[Recipes]: {{ site.baseurl }}/docs/recipes.html
[Administration]: {{ site.baseurl }}/docs/admin.html
[Installation]: {{ site.baseurl }}/docs/installation.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[Configuration]: {{ site.baseurl }}/docs/config.html
[Scalability]: {{ site.baseurl }}/docs/scalability.html
[Security]: {{ site.baseurl }}/docs/security.html
[Change Log]: {{ site.baseurl }}/docs/changelog.html
[Python Upgrade]: {{ site.baseurl }}/docs/twotothree.html
[License]: {{ site.baseurl }}/docs/license.html
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[Demonstration]: {{ site.baseurl }}/demo.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[GitHub]: https://github.com/
[Reserved Names]: {{ site.baseurl }}/docs/special.html#reserved
[demonstration]: {{ site.baseurl }}/demo.html
[demonstration page]: {{ site.baseurl}}/demo.html
[tutorial]: {{ site.baseurl}}/docs/helloworld.html
[Playground]: {{ site.baseurl}}/docs/playground.html
[Digital Ocean]: https://www.digitalocean.com/
[Amazon Web Services]: https://aws.amazon.com/ec2/
[many different types]: {{ site.baseurl }}/docs/fields.html#data types
[file uploads]: {{ site.baseurl }}/docs/fields.html#file
[touchscreen signatures]: {{ site.baseurl }}/docs/fields.html#signature
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[Deploy]: {{ site.baseurl }}/deploy.html
[DOCX]: {{ site.baseurl }}/docs/documents.html#docx template file
[PDF]: {{ site.baseurl }}/docs/documents.html#pdf template file
[lists]: {{ site.baseurl }}/docs/groups.html#gather list
[dictionaries]: {{ site.baseurl }}/docs/groups.html#gather dictionary
[features]: {{ site.baseurl }}/docs/initial.html#features
[screen parts]: {{ site.baseurl }}/docs/questions.html#screen parts
[up and running]: {{ site.baseurl }}/deploy.html
[background]: {{ site.baseurl }}/docs/background.html#background
[evaluate user input]: {{ site.baseurl }}/docs/background.html#check in
[when the user is not logged in]: {{ site.baseurl }}/docs/background.html#scheduled
[e-mail]: {{ site.baseurl }}/docs/functions.html#send_email
[Slack]: {{ site.slackurl }}
