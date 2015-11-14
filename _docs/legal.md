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

Or, if you also want the functionality of the `basic-questions.yml`
file, you can do this instead:

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
interview, such as who the interviewee is.  For example, if `trustee`
is an object of the class `Individual`, and you call
`trustee.do_question('have')`, the result will be "do you have" if
if the interviewee is the trustee, but otherwise the result will be
something like "does Fred Jones have."

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
  # (other objects omitted)
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

### interview_url()

### send_email()

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
