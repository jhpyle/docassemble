---
layout: docs
title: The "legal" module and basic-questions.yml
short_title: Legal applications
---

One "use case" for **docassemble** is the creation of web applications
that help people with legal problems.  The `docassemble.base` package
contains a [Python module] `docassemble.base.legal` that defines some
helpful Python [classes] and [functions].  It also contains a helpful
set of `question`s and `code` blocks,
`docassemble.base:data/questions/basic-questions.yml`.

To gain access to the functionality of `docassemble.base.legal`,
include the following in your interview file:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
{% endhighlight %}

Or, if you want the functionality of `docassemble.base.legal` as well
as access to the `basic-questions.yml` questions, do this instead:

{% highlight yaml %}
---
include:
  - basic-questions.yml
---
{% endhighlight %}

The best way to understand what these resources offer is to read the
source code of [legal.py] and [basic-questions.yml].

## Functions

### update_info()

Some of the [functions] and [methods] of `docassemble.base.legal` will
behave differently depending on background information about the
interview, such as who the interviewee is and what the interviewee's
role is.  For example, if `trustee` is an object of the class
`Individual`, and you call `trustee.do_question('have')`, the result
will be "do you have" if if the interviewee is the trustee, but
otherwise the result will be "does Fred Jones have" (or whatever the
trustee's name is).

In order for the `docassemble.base.legal` module to know this
background information, you need to include an `initial` code block
(or a `default role` block containing `code`) that:

1. Defines `user` as an object of the class `Individual`;
2. Defines `role` as a text variable (e.g., `'advocate'`); and
3. Calls `update_info(user, role, current_info)`.  (The `current_info`
dictionary is already defined by **docassemble**.)

For example, this is how [basic-questions.yml] does it:

{% highlight yaml %}
---
objects:
  - client: Individual
  - advocate: Individual
  # etc.
---
default role: client
code: |
  if current_info['user']['is_authenticated'] and \
     'advocate' in current_info['user']['roles']:
    user = advocate
    role = 'advocate'
  else:
    user = client
    role = 'client'
  update_info(user, role, current_info)
---
{% endhighlight %}

(See [initial blocks] for an explanation of `objects` and `default
role`.  See the [roles] section for an explanation of how user roles
work in **docassemble**.)

If you wish to retrieve the values that were passed to
`update_info()`, you can call:

* `get_info('user')`
* `get_info('role')`
* `get_info('current_info')`

Also, you can add [keyword arguments] to `update_info()` to set your
own variables and retrieve the values later with `get_info()`.  For
example, your `initial` block could be:

{% highlight yaml %}
---
initial: true
code: |
  update_info(user, 'interviewee', current_info,
    interview_type=url_args.get('type', 'standard'))
---
{% endhighlight %}

This is equivalent to doing:

{% highlight yaml %}
---
initial: true
code: |
  update_info(user, 'interviewee', current_info)
  set_info(interview_type=url_args.get('type', 'standard'))
---
{% endhighlight %}

For more information about `get_info()` and `set_info()`, see
[functions].

### interview_url()

The `interview_url()` function returns a URL to the interview that
provides a direct link to the interview and the current variable
store.  This is used in multi-user interviews to invite additional
users to participate.

### send_email()

The `send_email()` function sends an e-mail using [Flask-Mail].  All
of its arguments are [keyword arguments], the defaults of which are:

    send_email(to=None, sender=None, cc=None, bcc=None, body=None, html=None, subject="", attachments=[])

This function is integrated with other classes in
`docassemble.base.legal`.

* `to` expects a [list] of `Individual`s.
* `sender` expects a single `Individual`.  If not set, the
  `default_sender` information from the [configuration] is used.
* `cc` expects a [list] of `Individual`s, or `None`.
* `bcc` expects a [list] of `Individual`s, or `None`.
* `body` expects text, or `None`.  Will set the plain text content of
  the e-mail.
* `html` expects text, or `None`.  Will set the (optional) [HTML]
  content of the e-mail.
* `subject` expects text, or `None`.  Will set the subject of the e-mail.
* `template` expects a `DATemplate` object, or `None`.  These
  templates can be created in an interview file using the `template`
  directive.  If this [keyword argument] is supplied, both the plain
  text and [HTML] contents of the e-mail will be set by converting the
  [Markdown] text of the template into [HTML] and by converting the
  [HTML] to plain text (using [html2text]).  In addition, the subject
  of the e-mail will be set to the subject of the template.  You can
  override any of these behaviors by manually specifying `body`,
  `html`, or `subject`.
* `attachments` expects a [list] of `DAFile`, `DAFileList`, or
`DAFileCollection` objects.  You can include:
  * Images generated by `signature` blocks (objects of class
  `DAFile`);
  * File uploads generated by including [fields] of `datatype: file` or
  `datatype: files` in a `question` (objects of class `DAFileList`);
  * [Documents] generated by `attachments` to a `question` for which a
  `variable` was provided (objects of class `DAFileCollection`).

It uses the `name` and `email` attributes of the listed `Individuals`
to form e-mail addresses.

`send_email()` returns `False` if an error prevented the e-mail from
being sent; otherwise it returns `True`.

See [configuration] for information about how to configure the mail
server that `send_email()` will use.

Here is an example:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - user: Individual
---
mandatory: true
question: |
  So long, ${ user }!
subquestion: |
  % if success_sending_email:
  We sent an e-mail to your e-mail address.
  % else:
  Oops, for some reason we could not send an e-mail to you.
  % endif
---
question: |
  Please fill in the following information.
fields:
  - Your First Name: user.name.first
  - Your Last Name: user.name.last
  - Your E-mail: user.email
    datatype: email
  - A Picture: the_file
    datatype: file
---
code: |
  success_sending_email = send_email(to=[user], template=hello_email, attachments=[the_file])
---
template: hello_email
subject: |
  A picture for ${ user }
content: |
  Hello, ${ user }!

  Attached please find an incredibly *cool* picture.

  From,

  Your friend
---
{% endhighlight %}


## Classes for information about persons

### Person

#### Individual

### Name

#### IndividualName

### Address

## Classes for information about things in a court case

### Court

### Case

### Jurisdiction

### Document

#### LegalFiling

### RoleChangeTracker

## Classes for lists of things

### PartyList

### ChildList

### FinancialList

#### Asset

### PeriodicFinancialList

#### Income

### Value

#### PeriodicValue





[legal.py]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[basic-questions.yml]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[Python module]: https://docs.python.org/2/tutorial/modules.html
[classes]: https://docs.python.org/2/tutorial/classes.html
[functions]: https://docs.python.org/2/tutorial/controlflow.html#defining-functions
[methods]: https://docs.python.org/2/tutorial/classes.html
[roles]: {{ site.baseurl }}/docs/roles.html
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[user login system]: {{ site.baseurl }}/docs/users.html
[configuration]: {{ site.baseurl }}/docs/config.html
[keyword arguments]: https://docs.python.org/2/glossary.html#term-argument
[keyword argument]: https://docs.python.org/2/glossary.html#term-argument
[html2text]: https://pypi.python.org/pypi/html2text
[HTML]: https://en.wikipedia.org/wiki/HTML
[Flask-Mail]: https://pythonhosted.org/Flask-Mail/
[Documents]: {{ site.baseurl }}/docs/documents.html
[fields]: {{ site.baseurl }}/docs/fields.html
[list]: https://docs.python.org/2/tutorial/datastructures.html
