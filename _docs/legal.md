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

## <a name="Court"></a>Court

A `Court` has one attribute:

* `name`: e.g., "Court of Common Pleas of Butler County"

If you refer to an address in a template, it returns `.name`.

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

[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[`legal.py`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`basic-questions.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[Python module]: https://docs.python.org/2/tutorial/modules.html
[classes]: https://docs.python.org/2/tutorial/classes.html
[function]: https://docs.python.org/2/tutorial/controlflow.html#defining-functions
[methods]: https://docs.python.org/2/tutorial/classes.html
[roles]: {{ site.baseurl }}/docs/roles.html
[functions]: {{ site.baseurl }}/docs/functions.html
[initial block]: {{ site.baseurl }}/docs/initial.html
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
[multi-user interviews]: {{ site.baseurl }}/docs/roles.html
[special variable]: {{ site.baseurl }}/docs/special.html
[`track_location`]:  {{ site.baseurl }}/docs/special.html#track_location
[YAML]: https://en.wikipedia.org/wiki/YAML
[Python set]: https://docs.python.org/2/library/stdtypes.html#set
[`object_possessive`]: {{ site.baseurl }}/docs/objects.html#DAObject.object_possessive
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`code`]: {{ site.baseurl }}/docs/code.html
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`DATemplate`]: {{ site.baseurl }}/docs/objects.html#DATemplate
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
