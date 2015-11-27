---
layout: docs
title: The "legal" module and basic-questions.yml
short_title: Legal applications
---

# Using **docassemble** in legal applications

One "use case" for **docassemble** is the creation of web applications
that help people with legal problems.  The `docassemble.base` package
contains a [Python module] `docassemble.base.legal` that defines some
helpful Python [classes] and [function]s.  It also contains a helpful
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

# Functions

## update_info

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
2. Defines `role` as a text value (e.g., `'advocate'`); and
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

## interview_url

The `interview_url()` function returns a URL to the interview that
provides a direct link to the interview and the current variable
store.  This is used in multi-user interviews to invite additional
users to participate.

## send_email

The `send_email()` function sends an e-mail using [Flask-Mail].  All
of its arguments are [keyword arguments], the defaults of which are:

{% highlight python %}
send_email(to=None, sender=None, cc=None, bcc=None, body=None, html=None, subject="", attachments=[])
{% endhighlight %}

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

# Classes for information about persons

## Person

The `Person` class encompasses `Individual`s as well as legal persons,
like companies, government agencies, etc.  If you create an object of
type `Person` by doing:

{% highlight yaml %}
---
objects:
  - opponent: Person
---
{% endhighlight %}

then you will create an object with the following built-in attributes:

* `opponent.name` (object of class `Name`)
* `opponent.address` (object of class `Address`)
* `opponent.location` (object of class `LatitudeLongitude`)

Referring to a `Person` in the context of a template will return the
output of `.name.full()`.

The following attributes are also used, but undefined by default:

* `email`

### Individual

The `Individual` is a subclass of `Person`.  This class should be used
for persons who you know are human beings.

If you create an object of type `Individual` by doing:

{% highlight yaml %}
---
objects:
  - president: Individual
---
{% endhighlight %}

then you will create an object with the following built-in attributes:

* `president.name` (object of class `IndividualName`)
* `president.child` (object of class `ChildList`)
* `president.income` (object of class `Income`)
* `president.asset` (object of class `Asset`)
* `president.expense` (object of class `Expense`)

In addition, the following attributes will be defined by virtue of an
`Individual` being a kind of `Person`:

* `president.address` (object of class `Address`)
* `president.location` (object of class `LatitudeLongitude`)

## Name

The `Name` is a general class for names of persons and other things.
Its only expected attribute is `text`, and its only method is
`full()`, which simply returns the value of the `text` attribute.  In
the context of a template, a `Name` object returns the value of `.full()`.

For example, this interview sets the name of a `Person`:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - opponent: Person
---
question: |
  What are you fighting?
field: opponent.name.text
choices:
  - the Empire
  - the Rebel Alliance
---
mandatory: true
question: |
  You are fighting ${ opponent.name.full() }.
subquestion: |
  Your enemy is ${ opponent.name }.

  Your opponent is ${ opponent }.
---
{% endhighlight %}

([Try it out here](https://docassemble.org/demo?i=docassemble.demo:data/questions/testperson.yml){:target="_blank"}.)

Note that `${ opponent.name.full() }`, `${ opponent.name }`, and `${
opponent }` all return the same thing.  This is because a `Person` in
the context of a template returns `.name.full()`, and a `Name` returns
`.full()`.

### IndividualName

The `Individual` class is a subclass of `Person`, but it defines the
`name` attribute as an `IndividualName` rather than a `Name`.  An
`IndividualName` uses the following attributes, which are expected to
be text:

* `first`
* `middle`
* `last`
* `suffix`

In the context of a template, a reference to an `IndividualName` on
its own will return `.full()`

The `full()` method attempts to form a full name from these
components.  Only `first` is required, however.  This means that if
you refer to an `IndividualName` in a template, e.g., by writing
`${ applicant.name }`, **docassemble** will attempt to return
`applicant.name.full()`, and if `applicant.name.first` is not defined,
**docassemble** will look for a question that defines
`applicant.name.first`.

Here is how `full()` and other methods of the `IndividualName` work:

* `applicant.full()`: "John Q. Adams"
* `applicant.full(middle="full")`: "John Quincy Adams"
* `applicant.firstlast()`: "John Adams"
* `applicant.lastfirst()`: "Adams, John"

## Address

An `Address` has the following text attributes:

* `address`: e.g., "123 Main Street"
* `unit`: e.g., "Suite 100"
* `city`: e.g., "Springfield"
* `state`: e.g., "MA"
* `zip`: e.g. "01199"

If you refer to an address in a template, it returns `.block()`.

The `.block()` method returns a formatted address.  All attributes
except `unit` are required.

# Classes for information about things in a court case

## Court

A `Court` has one attribute:

* `name`: e.g., "Court of Common Pleas of Butler County"

If you refer to an address in a template, it returns `.name`.

## Case

If you create an object of type `Case` by doing:

{% highlight yaml %}
---
objects:
  - case: Case
---
{% endhighlight %}

then you will create an object with the following built-in attributes:

* `case.plaintiff` (object of class `PartyList`)
* `case.defendant` (object of class `PartyList`)
* `case.case_id` (text initialized to "")

In addition, the following attributes will be created:

* `case.firstParty`: set equal to `case.plaintiff`
* `case.secondParty`: set equal to `case.defendant`

The idea is that `plaintiff` and `defendant` are the default
parties to the case, but you can change this if you want.  For
example, you could do:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects: 
  - case: Case
---
mandatory: true
code: |
  del case.plaintiff
  del case.defendant
  case.initializeAttribute(name='petitioner', objectType=PartyList)
  case.initializeAttribute(name='respondent', objectType=PartyList)
  case.firstParty = case.petitioner
  case.secondParty = case.respondent
---
{% endhighlight %}

The `Case` class also has the following attribute, which is undefined
at first:

* `court`: the `Court` in which the case is filed.

The `Case` class has the following methods:

* `parties()`: returns a list of all parties to the case (namely, all
elements of any attributes of the `Case` that are `PartyList`s.
Calling this method will trigger "gathering" the elements of each
`PartyList`.
* `all_known_people()`: this is like `parties()`, except that it
includes children of each individual, and does not trigger the
gathering of the `PartyList`s.
* `role_of(party)`: Looks for `party` within the `PartyList`
attributes of the case and returns the attribute name of the
`PartyList` in which `party` was found (e.g., `plaintiff`,
`defendant`, etc.), or `third party` if `party` was not found in any
of the lists.

## Jurisdiction

A `Jurisdiction` has the following attributes:

* `state`
* `county`

## Document

A `Document` has the following attributes:

* `title`

### LegalFiling

`LegalFiling` is a subclass of `Document`.

It has the following attributes (in addition to `title`):

* `case`: the `Case` object in which the document is filed.

It has one method:

* `caption()`: returns a case caption suitable for inclusion in a
**docassemble** document.  If `pleading` is a `LegalFiling`, then
including `pleading.caption()` will require the following:

* pleading.case
* pleading.case.firstParty.gathered
* pleading.case.secondParty.gathered
* pleading.case.court.name
* pleading.title

## Value

A `Value` is a subclass of `DAObject` that is intended to represent a
currency value.  It has two attributes, both of which are initially
undefined:

* `value`: intended to be a number
* `exists`: a boolean value representing whether the value is applicable

### PeriodicValue

A `PeriodicValue` is a `Value` that has an additional attribute,
`period`, a number representing the number of times per year that the
period value is applicable.

# Classes for lists of things

## PartyList

This is a subclass of `DAList`.  (See [objects] for an explanation of the
`DAList` class.)

It is indended to contain a list of `Person`s who are parties.

## ChildList

This is a subclass of `DAList`.  (See [objects] for an explanation of the
`DAList` class.)

It is indended to contain a list of `Individuals`s who are children.

## FinancialList

This is a class intended to collect a set of financial items, such as
an individual's assets.

The `FinancialList` uses the following attributes:

* `gathering`: a boolean value that is initialized to `False`.  Set
this to `True` when your process of collecting the elements of the
list is ongoing and will span multiple questions.
* `gathered`: a boolean value that is initially undefined.  Set this
to `True` when you have finished gathering all of the elements.
* `elements`: a [Python set] containing the names of the financial
  items.

The `FinancialList` has two methods:

* `.new(item_name)`: gives the `FinancialList` a new attribute with
  the name `item_name` and the object type `Value`.
* `.total()`: tallies up the total value of all `Value`s in the list
  for which the `exists` attribute is `True`.  It requires `.gathered`
  to be True.

In the context of a template, a `FinancialList` returns the result of
`.total()`.

Note that a `FinancialList` is a `DAObject` but not a `DAList`.  It
tracks the items in the list using the attribute `elements`, which is
a [Python set].

### Asset

This is a subclass of `FinancialList` that is intended to be used to
track assets.

Here is some example code that triggers questions that ask about asset
items.  Note that every `Individual` is initialized with an attribute
called `asset` that is an object of type `Asset`.

{% highlight yaml %}
---
mandatory: true
question: |
  Your total assets are ${ user.asset }.
---
generic object: Individual
code: |
  for asset_item in ['checking', 'savings', 'stocksbonds']:
    x.asset.new(asset_item)
  x.asset.gathered = True
---
generic object: Individual
question: |
  What kinds of assets ${ x.do_question("own") }?
fields:
  - Checking Account: x.asset.checking.exists
    datatype: yesnowide
  - Savings Account: x.asset.savings.exists
    datatype: yesnowide
  - Stocks and Bonds: x.asset.stocksbonds.exists
    datatype: yesnowide
---
generic object: Individual
question: |
  How much ${ x.do_question("have") } in 
  ${ x.pronoun_possessive("checking account") }?
fields:
  - Amount in Checking Account: x.asset.checking.value
    datatype: currency
---
{% endhighlight %}

(Additional questions asking about the value of asset items are
omitted.)

1. The inclusion of `user.asset` in a template returns the value of
`user.asset.total()`.
2. The `.total()` method checks to see if `user.asset.gathered` is
`True`.  Since `user.asset.gathered` is initially undefined, this
triggers the code block that defines the elements of `user.asset`.
Note that we say the elements are "gathered" even though the
attributes of each element, `exists` and `value`, are still undefined.
3. The `.total()` method then goes through each element and checks to
see if the element `exists`.  This triggers the question that will
define `user.asset.checking.exists` and the other values.
4. If the `.total()` method finds that an element exists, it adds its
`value` to a subtotal.  This triggers the question that will
define `user.asset.checking.value`.
5. The `.total()` method does this for every element in `user.asset`
and finally returns a total.

Note that in this example, we did not have to worry about setting
`user.asset.gathering` because the process of populating the elements
of the asset list did not span multiple questions.

## PeriodicFinancialList

This is a class intended to collect a set of financial items that have
a periodic nature, such as an individual's income.

The `PeriodicFinancialList` uses the following attributes:

* `gathering`: a boolean value that is initialized to `False`.  Set
this to `True` when your process of collecting the elements of the
list is ongoing and will span multiple questions.
* `gathered`: a boolean value that is initially undefined.  Set this
to `True` when you have finished gathering all of the elements.
* `elements`: a [Python set] containing the names of the periodic financial
  items.

The `PeriodicFinancialList` has two methods:

* `.new(item_name)`: gives the `PeriodicFinancialList` a new attribute with
  the name `item_name` and the object type `PeriodicValue`.
* `.total()`: tallies up the total annual value of all `PeriodicValue`s in the list
  for which the `exists` attribute is `True`.

In the context of a template, a `PeriodicFinancialList` returns `.total()`.

### Income

This is a subclass of `PeriodicFinancialList`.

Here is some example code that triggers questions that ask about
income items.  Note that ever `Individual` has an attribute `income`
that is an object of type `Income`.

{% highlight yaml %}
---
mandatory: true
question: |
  Your total annual income is ${ user.income }.
---
generic object: Individual
code: |
  for income_item in ['employment', 'selfemployment']:
    x.income.new(income_item, period=12)
  x.income.gathered = True
---
generic object: Individual
question: |
  What kinds of income ${ x.do_question("have") }?
fields:
  - Employment: x.income.employment.exists
    datatype: yesnowide
  - Self-employment: x.income.selfemployment.exists
    datatype: yesnowide
---
generic object: Individual
question: |
  How much ${ x.do_question("make") } from employment?
fields:
  - Employment Income: x.income.employment.value
    datatype: currency
  - "": x.income.employment.period
    datatype: number
    code: |
      period_list()
---
{% endhighlight %}

(Not all necessary questions shown.)

# Classes for special purposes

## RoleChangeTracker

The `RoleChangeTracker` class is provided to facilitate multi-user
interviews with **docassemble**'s [roles] system.  It facilitates
sending e-mails to the participants to let them know when the
interview needs their attention.  It keeps track of when these e-mails
have been sent to make sure that duplicative e-mails are not sent.

It has one method:

* `role_change.send_email()` (not to be confused with the `send_email()`
  function)

Here is an example that demonstrates its use:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - client: Individual
  - advocate: Individual
  - role_change: RoleChangeTracker
---
default role: client
code: |
  if current_info['user']['is_authenticated'] and \
     advocate.attribute_defined('email') and \
     advocate.email == current_info['user']['email']:
    user = advocate
    role = 'advocate'
  else:
    user = client
    role = 'client'
  update_info(user, role, current_info)
---
event: role_event
question: You are done for now.
subquestion: |
  % if 'advocate' in role_needed:
  An advocate needs to review your answers before you can proceed.

  Please remember the following link and come back to it when you
  receive notice to do so:

  [${ interview_url() }](${ interview_url() })
  % else:
  Thanks, the client needs to resume the interview now.
  % endif

  % if role_change.send_email(role_needed, advocate={'to': advocate, 'email': role_event_email_to_advocate}, client={'to': client, 'email': role_event_email_to_client}):
  An e-mail has been sent.
  % endif
decoration: exit
buttons:
  - Exit: leave
---
template: role_event_email_to_advocate
subject: |
  Client interview waiting for your attention: ${ client }
content: |
  A client, ${ client }, has partly finished an interview.

  Please go to [the interview](${ interview_url() }) as soon as
  possible to review the client's answers.
---
template: role_event_email_to_client
subject: |
  Your interview answers have been reviewed
content: |
  An advocate has finished reviewing your answers.

  Please go to [${ interview_url() }](${ interview_url() })
  to resume the interview.
---
{% endhighlight %}

The `send_email()` method's first argument is the special variable
`role_needed`, a [Python list] that **docassemble** defines internally
whenever there is a mismatch between the current user's role and the
role required by a question that needs to be asked.

The remaining arguments to `send_email()` are [keyword arguments],
where each keyword is the name of a possible role.  Each
[keyword argument] must be a [Python dictionary] containing the
following keys:

* `to`: this needs to be a `Person` (or a subclass, like
`Individual`).  The person's `email` attribute is expected to be
defined.
* `email`: this needs to a `DATemplate` containing the subject and
body of the e-mail that will be sent.  See [objects] for an
explanation of `DATemplate`.

[Python set]: https://docs.python.org/2/library/stdtypes.html#set
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[legal.py]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[basic-questions.yml]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[Python module]: https://docs.python.org/2/tutorial/modules.html
[classes]: https://docs.python.org/2/tutorial/classes.html
[function]: https://docs.python.org/2/tutorial/controlflow.html#defining-functions
[methods]: https://docs.python.org/2/tutorial/classes.html
[roles]: {{ site.baseurl }}/docs/roles.html
[functions]: {{ site.baseurl }}/docs/functions.html
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
[objects]: {{ site.baseurl }}/docs/objects.html
[Markdown]: https://daringfireball.net/projects/markdown/
