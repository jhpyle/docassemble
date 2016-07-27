---
layout: docs
title: "Groups of things: lists, dictionaries, and sets"
short_title: Groups
---

To help you organize groups of things, **docassemble** offers three
data structures: lists, dictionaries, and sets.  These mirror the data
types of the same name that exist in Python.

# Overview of types of data structures

## <a name="list"></a>List

A **list** is a **group that has a defined order**.  Elements are
numbered with an index that starts from zero.  In Python, if a list is
defined as `fruit = ['apple', 'orange', 'pear']`, then `fruit[0]` will
return `apple`, `fruit[1]` will return `orange`, and `fruit[2]` will
return `pear`.  Adding a new element to the list is called "appending"
to the list.  In **docassemble**, lists are objects of type [`DAList`],
but they behave much like Python lists.

## <a name="dictionary"></a>Dictionary

A dictionary, or **dict**, is a **group of key/value pairs**.  By
analogy with a dictionary, the "key" represents the word and the
"value" represents the definition.  In Python, if a list is defined as
`feet = {'dog': 4, 'human': 2, 'bird': 2}`, then `feet['dog']` will
return `4`, `feet['human']` will return `2`, and `feet['bird']` will
return `2`.  The keys are `dog`, `human`, and `bird`, and the values
are `4`, `2`, and `2`, respectively.  The keys of a dictionary are
unique.  Doing `feet['rabbit'] = 2` will add a new entry to the
dictionary, whereas doing `feet['dog'] = 3` will change the entry for
`dog`.  The elements in a dictionary are stored in no particular
order; the order in which you add them is not remembered.

## <a name="set"></a>Set

A **set** is a **group of unique elements with no order**.  There is
no index or key that allows you to refer to a particular entry; an
element is either in the set or is not.  In Python, a set can be
defined with a statement like `colors = set(['blue', 'red'])`. Adding
a new element to the set is called "adding," not "appending."  E.g.,
`colors.add('green')`.  If you add an element to a set when the
element is already in the set, this will have no effect on the set.

# Lists, dictionaries, and sets in **docassemble**

In **docassemble**, you can track groups of things using objects of
types [`DAList`], [`DADict`], or [`DASet`].  These are defined in the
[`docassemble.base.core`] module, but are also available if you use
[`docassemble.base.util`] or [`docassemble.base.legal`].

In your **docassemble** interviews, you will typically not use these
object types directly, but rather subtypes of these basic objects.
For example, if you include the [`basic-questions.yml`] file (see
[legal applications]), an object of type [`Case`] will be created
(called `case`), which allows you to refer to the plaintiffs and
defendants in the case as `case.plaintiff` or `case.defendant`,
respectively.  Both of these objects are objects of type [`PartyList`],
which is a subtype of [`DAList`].  The first plaintiff is
`case.plaintiff[0]` and the second plaintiff, if there is one, will be
`case.plaintiff[1]`.

# For loop

In computer programming, a "for loop" allows you to do something
repeatedly, such as iterating through each item in a list.

For example, here is an example in [Python]:

{% highlight python %}
---
numbers = [5, 7, 2]
total = 0
for n in numbers:
    total = total + n
print total
---
{% endhighlight %}

This code "loops" through the elements of `numbers` and computes the
total amount.  At the end, `14` is printed.

For loops can be included in **docassemble** templates using the
`for`/`endfor` [Mako] statement:

{% include side-by-side.html demo="for_fruit" %}

[Mako] "for" loops work just like [Python] for loops, except that they
need to be ended with "endfor."

{% highlight yaml %}
---
question: |
  Summary of the case
subquestion: |
  % for person in case.plaintiff:
  ${ person } is a plaintiff.
  % endfor
---
{% endhighlight %}

This results in a sentence like:

> John Smith is a plaintiff. Jane Doe is a plaintiff. Robert Jones is
> a plaintiff.

If the list might be empty, you can check its [`.number()`] first using
an `if`/`else`/`endif` [Mako] statement:

{% highlight yaml %}
---
question: |
  Summary of the case
subquestion: |
  % if case.plaintiff.number() > 0:
  % for person in case.plaintiff:
  ${ person } is a plaintiff.
  % endfor
  % else:
  There are no plaintiffs.
  % endif
---
{% endhighlight %}

You can check if something is in a list using a statement of the form
`if` ... `in`:

{% highlight yaml %}
---
question: |
  % if client in case.plaintiff:
  Since you are bringing the case, it will be your responsibility to
  prove that you were harmed.
  % else:
  The responsibility to prove this case belongs to
  ${ case.plaintiff }.  You do not have to testify in your defense.
  % endif
---
{% endhighlight %}

**docassemble** lets you ask generic questions to fill in information
about each object in a list:

{% highlight yaml %}
---
question: |
  Does ${ case.plaintiff[i] } agree to accept service?
yesno: case.plaintiff[i].agrees_to_accept_service
---
{% endhighlight %}

<a name="i"></a>The special variable `i` will stand in for the index
of whichever list member your interview asks about.

You can also make use of the special variable `i`:

{% highlight yaml %}
---
question: |
  Does ${ case.plaintiff[i] }, the ${ ordinal(i) } plaintiff,
  agree to accept service?
yesno: case.plaintiff[i].agrees_to_accept_service
---
{% endhighlight %}

[legal applications]: {{ site.baseurl }}/docs/legal.html
[Mako]: http://www.makotemplates.org/
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`docassemble.base.core`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/core.py
[`docassemble.base.legal`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`DASet`]: {{ site.baseurl }}/docs/objects.html#DASet
[`Case`]: {{ site.baseurl }}/docs/legal.html#Case
[`PartyList`]: {{ site.baseurl }}/docs/legal.html#PartyList
[`basic-questions.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[`.number()`]: {{ site.baseurl }}/docs/objects.html#DAList.number
