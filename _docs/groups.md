---
layout: docs
title: "Groups of things: lists, dictionaries, and sets"
short_title: Groups
---

To help you organize groups of things, **docassemble** offers three
data structures: lists, dictionaries, and sets.  These mirror the
[list], [dict], and [set] data types that exist in [Python].

# Overview of types of data structures

## <a name="list"></a>List

A **list** is a **group that has a defined order**.  Elements are
numbered with an index that starts from zero.  In [Python], if a list is
defined as:

{% highlight python %}
fruit = ['apple', 'orange', 'pear']
{% endhighlight %}

then `fruit[0]` will return `apple`, `fruit[1]` will return `orange`,
and `fruit[2]` will return `pear`.  You can try this out in a
[Python interpreter]:

{% highlight python %}
>>> fruit = ['apple', 'orange', 'pear']
>>> fruit[0]
'apple'
>>> fruit[1]
'orange'
>>> fruit[2]
'pear'
{% endhighlight %}

Adding a new element to the list is called "appending" to the list.

{% highlight python %}
>>> fruit = ['apple', 'orange', 'pear']
>>> fruit.append('grape')
>>> fruit
['apple', 'orange', 'pear', 'grape']
>>> sorted(fruit)
['apple', 'grape', 'orange', 'pear']
{% endhighlight %}

The [`sorted()` function] is a built-in [Python] function that
arranges a list in alphabetical order.

In **docassemble**, lists are objects of type [`DAList`], which behave
much like [Python lists].

## <a name="dictionary"></a>Dictionary

A dictionary, or **dict**, is a **group of key/value pairs**.  By
analogy with a dictionary, the "key" represents the word and the
"value" represents the definition.  In [Python], if a dictionary is
defined as:

{% highlight python %}
feet = {'dog': 4, 'human': 2, 'bird': 2}
{% endhighlight %}

then `feet['dog']` will return `4`, `feet['human']` will return `2`,
and `feet['bird']` will return `2`.  The keys are `dog`, `human`, and
`bird`, and the values are `4`, `2`, and `2`, respectively.

{% highlight python %}
>>> feet = {'dog': 4, 'human': 2, 'bird': 2}
>>> feet['dog']
4
>>> feet['human']
2
>>> feet['bird']
2
>>> feet.keys()
['dog', 'human', 'bird']
>>> feet.values()
[4, 2, 2]
{% endhighlight %}

The keys of a dictionary are unique.  Doing `feet['rabbit'] = 2` will
add a new entry to the above dictionary, whereas doing `feet['dog'] =
3` will change the existing entry for `dog`.  The items in a
dictionary are stored in no particular order; [Python] will not
remember the order in which you add them.

In **docassemble**, dictionaries are objects of type [`DADict`], which
behave much like [Python dict]s.

## <a name="set"></a>Set

A **set** is a **group of unique items with no order**.  There is no
index or key that allows you to refer to a particular item; an item is
either in the set or is not.  In Python, a set can be defined with a
statement like `colors = set(['blue', 'red'])`. Adding a new item to
the set is called "adding," not "appending."  E.g.,
`colors.add('green')`.  If you add an item to a set when the item is
already in the set, this will have no effect on the set.

{% highlight python %}
>>> colors = set(['blue', 'red'])
>>> colors
set(['blue', 'green', 'red'])
>>> colors.add('blue')
>>> colors
set(['blue', 'green', 'red'])
>>> colors.remove('red')
>>> colors
set(['blue', 'green'])
{% endhighlight %}

In **docassemble**, sets are objects of type [`DASet`], which behave
much like [Python set]s.

# Lists, dictionaries, and sets in **docassemble**

In **docassemble**, you can track groups of things using objects of
types [`DAList`], [`DADict`], or [`DASet`].  These are defined in the
[`docassemble.base.core`] module.  They are also available if you use
[`docassemble.base.util`] or [`docassemble.base.legal`] as
[`modules`], or if you [`include`] the file [`basic-questions.yml`].

{% include side-by-side.html demo="object-demo" %}

In your **docassemble** interviews, you will typically not use these
object types directly, but rather you will use subtypes of these basic
objects.  For example, if you include the [`basic-questions.yml`] file
(see [legal applications]), an object of type [`Case`] will be created
(called `case`), which allows you to refer to the plaintiffs and
defendants in the case as `case.plaintiff` or `case.defendant`,
respectively.  Both of these objects are objects of type
[`PartyList`], which is a subtype of [`DAList`].  The first plaintiff
is `case.plaintiff[0]` and the second plaintiff, if there is one, will
be `case.plaintiff[1]`.

## <a name="gathering"></a>Gathering information from the user

When you want to gather information from the user into a list,
dictionary, or set, you should use the objects [`DAList`], [`DADict`],
and [`DASet`] instead of [Python]'s basic [list], [dict], and [set]
data types.  These objects have special attributes that help
interviews find the right questions to ask the user in order to
populate the items of the group.

### <a name="gather list"></a>Lists

The following interview populates a list of fruits.

{% include side-by-side.html demo="gather-fruit" %}

First, the module [`docassemble.base.core`] is brought in, because it
contains the definition of the [`DAList`] object.

{% highlight yaml %}
modules:
  - docassemble.base.core
{% endhighlight %}

Second, the variable `fruit` is defined as a [`DAList`] <span></span>
[object].

{% highlight yaml %}
objects:
  - fruit: DAList
{% endhighlight %}

The next block contains the end point of the interview, a screen that
says how many fruits are in the list and lists them.

{% highlight yaml %}
mandatory: true
question: |
  There are ${ fruit.number_as_word() }
  fruits in all.
subquestion: |
  The fruits are ${ fruit }.
{% endhighlight %}

The interview encounters `fruit.number_as_word()`, which will return
the number of items in the list.  But in order to know how many items
are in the list, the interview first needs to ask the user what those
items are.  So the reference to `fruit.number_as_word()` will trigger
the process of asking these questions.  (The reference to ${ fruit }
would trigger the same process, but the interview will encounter
`fruit.number_as_word()` first.)

The text of these questions is provided in [`question`] blocks that
define the following variables:

* `fruit.there_are_any`: should there be any items in the list at all?
* `fruit[i]`: the name of the `i`th fruit in the list.
* `fruit.there_is_another`: are there any more fruits that still need
  to be added?

First, the interview will want to know whether there are any items in
the list at all.  It will seek a definition for `fruit.there_are_any`.
It will ask the question, "Are there any fruit that you would like to
add to the list?"

{% highlight yaml %}
question: |
  Are there any fruit that you would like
  to add to the list?
yesno: fruit.there_are_any
{% endhighlight %}

If the answer to this is `True`, the interview will seek a definition
for `fruit[0]` to gather the first element.  It will ask the question
"What fruit should be added to the list?"

{% highlight yaml %}
question: |
  What fruit should be added to the list?
fields:
  - Fruit: fruit[i]
{% endhighlight %}

Assume the user enters "apples."

Now the interview knows the first item in the list, but it does not
know if the list is complete yet.  Therefore, it will seek a
definition for `fruit.there_is_another`.  It will ask the question "So
far, the fruits include apples.  Are there any others?"

{% highlight yaml %}
question: |
  So far, the fruits include ${ fruit }.
  Are there any others?
yesno: fruit.there_is_another
{% endhighlight %}

If the answer to this is `True`, the interview will seek a definition
of `fruit[1]` to gather the second item in the list.  It will ask,
again, "What fruit should be added to the list?"  Assume the user
enters "oranges."

Then the interview will again seek the definition of
`fruit.there_is_another`.  This time, if the answer is `False`, then
`fruit.number_as_word()` has all the information it needs, and it will
return the number of items in `fruit` (in this case, 2).  When the interview later
encounters `The fruits are ${ fruit }.`, it will attempt to reduce the
variable `fruit` to text.  Since the interview knows that there are no
more elements in the list, it does not need to ask any further
questions.  `${ fruit }` will result in `apples and oranges`.

Note that the variable `i` is special in **docassemble**.  When the
interview seeks a definition for `fruit[0]`, the interview will first
look for a question that offers to define `fruit[0]`.  If it does not
find one, it will take a more general approach and look for a question
that offers to define `fruit[i]`.  It finds just such a question.  As
a result, the single question that offers to define `fruit[i]` can be
reused as many times as necessary.

#### Customizing the way information is gathered

The way that **docassemble** asks questions to populate the list can
be customized by setting attributes of `fruit`.  For example, perhaps
you would prefer that the questions in the interview go like this:

1. How many fruits are there?
2. What is the name of the first fruit?
3. What is the name of the second fruit?
4. etc.

To ask questions this way, include a [`mandatory`]<span></span>
[`code` block] up front that sets the `.ask_number` attribute of
`fruit` to `True`.  Also include a question that asks "How many fruits
are there?" and use `fruit.target_number` as the true/false variable.
(The `.target_number` attribute is a special attribute, like
`.there_is_another`.)

{% include side-by-side.html demo="gather-fruit-number" %}

You can avoid the `.there_are_any` question by setting the
`.minimum_number` to a value:

{% include side-by-side.html demo="gather-fruit-at-least-two" %}

### <a name="gather dictionary"></a>Dictionaries

The process of gathering the items in a [`DADict`] dictionary is
slightly different.  Like the gathering process for [`DAList`]
objects, the gathering process for [`DADict`] objects will call upon
the attributes `.there_are_any` and `.there_is_another`.

In addition, the process will look for the attribute `.new_item_name`
to get the key to be added to the dictionary.

If you use a plain [`DADict`] object, the process will look for the
attribute `.new_item_value` to get the value of the 

{% include side-by-side.html demo="gather-dict" %}

{% include side-by-side.html demo="gather-dict-object" %}

{% include side-by-side.html demo="gather-dict-value" %}


### <a name="gather set"></a>Sets

{% include side-by-side.html demo="gather-set" %}

{% include side-by-side.html demo="gather-set-object" %}

## Manually triggering the gathering process

In the examples above, the process of asking questions that populate
the list was triggered implicitly by code like `${ fruit.number() }` or
`${ fruit }` or `% for item in fruit:`.

If you want to ask the questions at a particular time, you can do so
by referring to `fruit.gather()`.  (Behind the scenes, this is the
same method used when the process is implicitly triggered.)

{% include side-by-side.html demo="gather-fruit-gather" %}

## Asking additional questions about each item

The `.gather()` method only asks enough questions about each item in
order to display it.  For example, if you have a `PartyList` called
`witness`, the items will be `Individual`s, and the bare minimum
information needed to display an `Individual` is the `Individual`'s `.name.first`.

## Manually gathering items

At a very basic level, it is not complicated to gather a list of
things from a user.  For example, you can do this:

{% include side-by-side.html demo="gather-simple" %}

This example uses [Python]'s built-in [`range()` function], which
returns a list of integers starting with the first argument and less
than the second argument.  For example:

{% highlight python %}
>>> range(0, 5)
[0, 1, 2, 3, 4]
{% endhighlight %}

The [`for` loop] iterates through all the numbers using the variable
`index`, looking for `fruit[index]`.  The first item it looks for is
`fruit[0]`.  Since this is not defined yet, the interview looks for a
question that offers to define `fruit[0]`.  It does not find any
questions that define `fruit[0]`, so it then looks for a question that
offers to defined `fruit[i]`.  It finds this question, and asks it of
the user.  After the user provides an answer, the [`for` loop] runs
again.  This time, `fruit[0]` is already defined.  But on the next
iteration of the [`for` loop], the interview looks for `fruit[1]` and
finds it is not defined.  So the interview repeats the process with
`fruit[1]`.  When all of the `fruit[index]` are defined, the
`mandatory` question is able to be shown to the user, and the
interview ends.

Another way to ask questions is to ask for one item at a time, and
after each item, ask if any additional items exist.

{% include side-by-side.html demo="gather-another" %}

This example uses a little bit of [Python] code to ask the appropriate
questions.  The code is:

{% highlight python %}
fruit[0]
if more_fruits:
  del more_fruits
  fruit[len(fruit)]
{% endhighlight %}

The first line makes sure that the first fruit, `fruit[0]`, is
defined.  Initially, this initially undefined, but when the code
encounters `fruit[0]` it will go looking for the value of `fruit[0]`,
and the question "What's the first fruit?" will be asked.  Once
`fruit[0]` is defined, the interview considers whether `more_fruits`
is true.  If `more_fruits` is undefined, the interview presents the
user with the `more_fruit` question, which asks "Are there more
fruits?"  If `more_fruits` is `True`, however, the interview deletes
the definition of `more_fruit` (making the variable undefined again),
and then makes sure that `fruit[len(fruit)]` is defined.  The
expression `len(fruit)` returns the number of items in the `fruit`
list.  If there is only one item in the list (i.e., `fruit[0]`), then
`len(fruit)` will be return `1`, and the interview will look for the
second element in the list, `fruit[1]`.

This is starting to get complicated.  And things get even more
complicated when you want to say things like "There are three fruits
in all" and "You have told me about three fruits so far" in your
interview questions.  In the case of "There are three fruits in all,"
a prerequisite to saying this is to make sure that the user has
supplied the full list.  But in the case of "You have told me about
three fruits so far," you would not want this prerequisite.

Since asking users for lists of things can get complicated,
**docassemble** automates the process of asking the necessary
questions to fully populate the list

If your list is `fruit`, there are two special attributes:
`fruit.gathered` and `fruit.there_is_another`.  The `fruit.gathered`
attribute is initially undefined, but is set to `True` when the list
is completely populated.  The `fruit.there_is_another` attribute is
used to ask the user questions like "You have told me about three
fruits so far: apples, peaches, and pears.  Are there any additional
fruits?"

In addition to these two attributes, there is special method,
`fruit.gather()`, which will cause appropriate questions to be asked
and will return `True` when the list has been fully populated.  The
`.gather()` method looks for definitions for `fruit[i]` and
`fruit.there_is_another`, and makes `fruit.there_is_another`
undefined, as necessary.

Here is a complete example:

{% include side-by-side.html demo="gather-fruit" %}

# For loop

In computer programming, a "for loop" allows you to do something
repeatedly, such as iterating through each item in a list.

For example, here is an example in [Python]:

{% highlight python %}
numbers = [5, 7, 2]
total = 0
for n in numbers:
    total = total + n
print total
{% endhighlight %}

This code "loops" through the elements of `numbers` and computes the
total amount.  At the end, `14` is printed.

For loops based on [`DAList`], [`DADict`], and [`DASet`] objects can be included in
**docassemble** templates using the `for`/`endfor` [Mako] statement:

{% include side-by-side.html demo="for_fruit" %}

[Mako] "for" loops work just like [Python] for loops, except that they
need to be ended with "endfor."

If the list might be empty, you can check its length using an
`if`/`else`/`endif` [Mako] statement:

{% highlight yaml %}
---
question: |
  Summary of fruit
subquestion: |
  % if len(fruit_list) > 0:
    % for fruit in fruit_list:
  I assume you like ${ fruit }.
    % endfor
  % else:
  There are no fruits to discuss.
  % endif
mandatory: true
---
{% endhighlight %}

You can do the same with a [`DAList`], but you can check its
[`.number()`], which has the effect of causing the list to be
gathered.

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

The `len()` function, by contrast, only returns the number of elements
gathered so far, or `0` if no elements have been gathered.
  
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
[Python interpreter]: https://docs.python.org/2.7/tutorial/interpreter.html
[Python list]: https://docs.python.org/2.7/tutorial/datastructures.html
[Python lists]: https://docs.python.org/2.7/tutorial/datastructures.html
[Python dict]: https://docs.python.org/2/library/stdtypes.html#dict
[Python set]: https://docs.python.org/2/library/stdtypes.html#set
[`sorted()` function]: https://docs.python.org/2/library/functions.html#sorted
[`range()` function]: https://docs.python.org/2/library/functions.html#sorted
[`for` loop]: {{ site.baseurl }}/docs/markup.html#for
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`code` block]: {{ site.baseurl }}/docs/code.html#code
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[list]: https://docs.python.org/2.7/tutorial/datastructures.html
[dict]: https://docs.python.org/2/library/stdtypes.html#dict
[set]: https://docs.python.org/2/library/stdtypes.html#set
[object]: {{ site.baseurl }}/docs/objects.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
