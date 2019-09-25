---
layout: docs
title: The "legal" module and basic-questions.yml
short_title: Legal Applications
---

# Using **docassemble** in legal applications

One "use case" for **docassemble** is the creation of web applications
that help people with legal problems.  The [`docassemble.base`] package
contains a [Python module]<span></span> [`docassemble.base.legal`] that defines some
helpful Python [classes] and [function]s.  It also contains a helpful
set of [`question`]s and [`code`] blocks,
`docassemble.base:data/questions/basic-questions.yml`.

To gain access to the functionality of [`docassemble.base.legal`],
include the following in your interview file:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
{% endhighlight %}

Or, if you want the functionality of [`docassemble.base.legal`] as well
as access to the [`basic-questions.yml`] questions, do this instead:

{% highlight yaml %}
---
include:
  - basic-questions.yml
---
{% endhighlight %}

The best way to understand what these resources offer is to read the
source code of [`legal.py`] and [`basic-questions.yml`].

# Classes for information about things in a court case

The classes that are available in `docassemble.base.legal` are very
basic, and the built-in functionality they currently provide might not
be useful in your interviews.  However, it is still worthwhile for you
to use these classes.  For example, if you write your own class that
represents the courts of your jurisdiction, make the class a subclass
of `Court`.  By subclassing and sharing code, the community of
**docassemble** developers can develop a powerful set of object
types.  Perhaps you can contribute your code to this project.

## <a name="Court"></a>Court

A `Court` has one attribute:

* `name`: e.g., "Court of Common Pleas of Butler County"

If you refer to a `Court` in a template, it returns `.name`.

The `Court` class has the following methods:

* <a name="Court.in_the_court"></a>`in_the_court()`: returns the top
  line of the first page of a pleading filed in this court.  It takes
  two optional keyword arguments: `legalfiling` and `case`,
  representing the relevant [`LegalFiling`] and the [`Case`] that
  might be relevant for determining the content of the "In the Court" line.

## <a name="Case"></a>Case

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

The idea here is that `plaintiff` and `defendant` are the default
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
mandatory: True
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

* <a name="Case.parties"></a>`parties()`: returns a list of all
  parties to the case (namely, all elements of any attributes of the
  `Case` that are `PartyList`s.  Calling this method will trigger
  "gathering" the elements of each `PartyList`.
* <a name="Case.all_known_people"></a>`all_known_people()`: this is
  like `parties()`, except that it includes children of each
  individual, and does not trigger the gathering of the `PartyList`s.
* <a name="Case.role_of"></a>`role_of(party)`: Looks for `party`
  within the `PartyList` attributes of the case and returns the
  attribute name of the `PartyList` in which `party` was found (e.g.,
  `plaintiff`, `defendant`, etc.), or `third party` if `party` was not
  found in any of the lists.
* <a name="Case.set_action_type"></a>`set_action_type(action_type)`:
  Possibilities are `'solo petition'`, `'in re'`, `'petition'`, and
  `'plaintiff defendant'`.  The default is `'plaintiff defendant'`.
  This will determine the types of `PartyList` attributes.
* <a name="Case.case_id_in_caption"></a>`case_id_in_caption()`:
  returns the [Markdown] text for the case ID that will appear in the
  case caption.
* <a name="Case.determine_court"></a>`determine_court()`: runs code,
  if any exists, to determine what court has jurisdiction over the case.

## <a name="Jurisdiction"></a>Jurisdiction

A `Jurisdiction` has the following attributes:

* `state`
* `county`

## <a name="Document"></a>Document

A `Document` has the following attributes:

* `title`

### <a name="LegalFiling"></a>LegalFiling

`LegalFiling` is a subclass of `Document`.

It has the following attributes (in addition to `title`):

* `case`: the `Case` object in which the document is filed.

It has one method:

<a name="LegalFiling.caption"></a>

* `caption()`: returns a case caption suitable for inclusion in a
**docassemble** document.  If `pleading` is a `LegalFiling`, then
including `pleading.caption()` will require the following:
    * `pleading.case`
    * `pleading.case.firstParty.gathered`
    * `pleading.case.secondParty.gathered`
    * `pleading.case.court.name`
    * `pleading.title`

# <a name="jurisdictional"></a>Adjusting for jurisdictional variation

**docassemble** is an ideal platform for legal interviews that are
applicable in multiple jurisdictions.  The features of object-oriented
programming are well-adapted to representing general rules that can be
overridden by special cases, state rules that can be overriden by
local rules, old law that is partially superseded by new law.

The features of software packaging and the nested importation of
software libraries enable collaboration among legal experts.  For
example, suppose Lawyer A is an expert in the general family law of
the state of California.  Lawyer B is an expert in how that law is
applied in the city of Los Angeles, California.  Lawyer C is an expert
in how that law is applied in the city of San Francisco, California.
Lawyer A can develop the package `docassemble.us-ca-family` containing
classes and methods for applying California Family Law to the facts of
cases.  Lawyer B can develop the package `docassemble.us-ca-la-family`,
which imports `docassemble.us-ca-family` and makes modifications to the
classes as necessary to express the local variations in Los Angeles.
Lawyer C can develop the package `docassemble.us-ca-sf-family`, which
does the same for San Francisco.  All three lawyers will take
responsibility for maintaining their code.

Then, Lawyer D could develop a statewide interview for a family law
pleading, using the packages `docassemble.us-ca-family`,
`docassemble.family-us-ca-la`, `docassemble.family-us-ca-sf`, and any other
packages that might exist.  Lawyer D would not need to research the
special variations of law in San Francisco and Los Angeles because
Lawyers B and C will do all that work; Lawyer D would just need to put
the pieces together.

Lawyers A, B and C will not need to become experts in each others'
areas of law, or understand each others' code, but they will need to
cooperate around using a "common language."  For example, if Lawyer B
thinks about using an attribute `.driver_license_number`, but Lawyer C
has already used `.drivers_license_id` to represent the same concept,
Lawyer B should notice that Lawyer C has started to use
`.drivers_license_id` and should use the same naming convention.  In
order to facilitate collaboration, Lawyers B and C will need to
document their work clearly and concisely.  The `README.md` file in
each **docassemble** package is a good place for this documentation to
be located.  They may also need to communicate with one another.  This
communication could take place formally, for example through a
committee that has regular conference calls or in-person meetings, or
it could take place informally, through an e-mail distribution list or
a channel on the [**docassemble** Slack group].

In an area like family law where each state's law is relatively
similar, it may be worthwhile for a developer to work on a
`docassemble.us-family` package, which would contain resources useful
across many states.  For example, the task of asking clients about the
members of their family is not particularly state-specific.  The
`docassemble.us-family` package could contain "best practices" and
carefully written plain language.  Once lawyers in California develop
a robust set of family law applications, lawyers in Texas could take
their work, adapt it for Texas, note what did not change, and put the
code that did not change into the `docassemble.us-family` package.
Then lawyers in New York would be able to follow a roadmap for
developing family law applications for New York.

The goal of **docassemble** is to enable a development environment
similar to Drupal and Wordpress, in which a small number of developers
work on the "core," while a large number of developers work on
"modules."  Modules depend on other modules.

[**docassemble** Slack group]: https://join.slack.com/t/docassemble/shared_invite/enQtMjQ0Njc1NDk0NjU2LTUyOGIxMDcxYzg1NGZhNDY5NDI2ZTVkMDhlOGJlNTgzZTUwYzNhYTJiMTJmMDYzYjQ0YWNmNjFiOTE5NmQzMjc
[Python list]: https://docs.python.org/3/tutorial/datastructures.html
[Python dictionary]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[`legal.py`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`basic-questions.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[Python module]: https://docs.python.org/3/tutorial/modules.html
[classes]: https://docs.python.org/3/tutorial/classes.html
[function]: https://docs.python.org/3/tutorial/controlflow.html#defining-functions
[methods]: https://docs.python.org/3/tutorial/classes.html
[roles]: {{ site.baseurl }}/docs/roles.html
[functions]: {{ site.baseurl }}/docs/functions.html
[initial block]: {{ site.baseurl }}/docs/initial.html
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[user login system]: {{ site.baseurl }}/docs/users.html
[configuration]: {{ site.baseurl }}/docs/config.html
[keyword arguments]: https://docs.python.org/3/glossary.html#term-argument
[keyword argument]: https://docs.python.org/3/glossary.html#term-argument
[html2text]: https://pypi.python.org/pypi/html2text
[HTML]: https://en.wikipedia.org/wiki/HTML
[Flask-Mail]: https://pythonhosted.org/Flask-Mail/
[Documents]: {{ site.baseurl }}/docs/documents.html
[fields]: {{ site.baseurl }}/docs/fields.html
[list]: https://docs.python.org/3/tutorial/datastructures.html
[objects]: {{ site.baseurl }}/docs/objects.html
[Markdown]: https://daringfireball.net/projects/markdown/
[multi-user interviews]: {{ site.baseurl }}/docs/roles.html
[special variable]: {{ site.baseurl }}/docs/special.html
[`track_location`]:  {{ site.baseurl }}/docs/special.html#track_location
[YAML]: https://en.wikipedia.org/wiki/YAML
[Python set]: https://docs.python.org/3/library/stdtypes.html#set
[`object_possessive`]: {{ site.baseurl }}/docs/objects.html#DAObject.object_possessive
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`code`]: {{ site.baseurl }}/docs/code.html
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`DAFileCollection`]: {{ site.baseurl }}/docs/objects.html#DAFileCollection
[`attachments`]: {{ site.baseurl }}/docs/documents.html#attachments
[`objects`]: {{ site.baseurl }}/docs/initial.html#objects
[`default role`]: {{ site.baseurl }}/docs/initial.html#default role
[`Individual`]: #Individual
[`Person`]: #Person
[`LatitudeLongitude`]: #LatitudeLongitude
[`Address`]: #Address
[`Name`]: #Name
[`IndividualName`]: #IndividualName
[`ChildList`]: #ChildList
[`Income`]: #Income
[`Asset`]: #Asset
[`Expense`]: #Expense
[`PeriodicFinancialList`]: #PeriodicFinancialList
[`Value`]: #Value
[`FinancialList`]: #FinancialList
[`currency()`]: {{ site.baseurl }}/docs/functions.html#currency
[`Organization`]: #Organization
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`docassemble.base.legal`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[`interview_url()`]: #interview_url
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`LegalFiling`]: #LegalFiling
[`Case`]: #Case
