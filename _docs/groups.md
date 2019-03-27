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
arranges a list in order.

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
and `feet['bird']` will return `2`.  The keys are `'dog'`, `'human'`, and
`'bird'`, and the values are `4`, `2`, and `2`, respectively.

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

The keys of a dictionary are unique.  Setting `feet['rabbit'] = 4`
will add a new entry to the above dictionary, whereas setting
`feet['dog'] = 3` will change the existing entry for `'dog'`.  The
items in a dictionary are stored in no particular order; [Python] will
not remember the order in which you add them.  (See the
[`DAOrderedDict`] for an alternative to this.)

In **docassemble**, dictionaries are objects of type [`DADict`], which
behave much like [Python dict]s.

## <a name="set"></a>Set

A **set** is a **group of unique items with no order**.  There is no
index or key that allows you to refer to a particular item; an item is
either in the set or is not.  (A set in Python behaves much like a set
in mathematical [set theory].)  In [Python], a set can be defined with a
statement like `colors = set(['blue', 'red'])`. Adding a new item to
the set is called "adding," not "appending."  For example:
`colors.add('green')`.  If you add an item to a set when the item is
already in the set, this will have no effect on the set.

{% highlight python %}
>>> colors = set(['blue', 'green', 'red'])
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

# <a name="gathering"></a>Lists, dictionaries, and sets in **docassemble**

In **docassemble**, you can track groups of things using objects of
types [`DAList`], [`DADict`], or [`DASet`].

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

When you want to gather information from the user into a list,
dictionary, or set, you should use the objects [`DAList`], [`DADict`],
and [`DASet`] (or subtypes thereof) instead of [Python]'s basic
[list], [dict], and [set] data types.  These objects have special
attributes that help interviews find the right questions to ask the
user in order to populate the items of the group.  (If you want to,
you can use [Python]'s basic [list], [dict], and [set] data types in
your interviews; nothing will stop you -- but there are no special
features to help you populate these objects with user input.)

# <a name="gather list"></a>Gathering information into lists

The following interview populates a list of fruits.

{% include side-by-side.html demo="gather-fruit" %}

The variable `fruit` is defined as a [`DAList`] <span></span>
[object].

{% highlight yaml %}
objects:
  - fruit: DAList
{% endhighlight %}

The next block contains the end point of the interview, a screen that
says how many fruits are in the list and lists them.

{% highlight yaml %}
mandatory: True
question: |
  There are ${ fruit.number_as_word() }
  fruits in all.
subquestion: |
  The fruits are ${ fruit }.
{% endhighlight %}

Since this [`question`] is [`mandatory`], **docassemble** tries to ask
it.  However, it encounters `fruit.number_as_word()`, which returns
the number of items in the list.  But in order to know how many items
are in the list, **docassemble** needs to ask the user what those
items are.  So the reference to `fruit.number_as_word()` will
implicitly trigger the process of asking these questions.  (The
reference to `${ fruit }` would also trigger the same process, but
**docassemble** will encounter `fruit.number_as_word()` first.)

Behind the scenes, when `fruit.number_as_word()` is run,
**docassemble** runs `fruit.gather()`, which is an auto-gathering
algorithm.  The `.gather()` method orchestrates the gathering process
by triggering the seeking of variables necessary to gather the list.

The auto-gathering algorithm behaves like a lawyer interrogating a
witness.

"Do you have any children?" asks the lawyer.

"Yes," answers the witness.

"What is the name of your first child?"

"James."

"Besides James, do you have any other children?"

"Yes"

"What is the name of your second child?"

"Charlotte."

"Besides James and Charlotte, do you have any other children?"

"No"

The `.gather()` method asks questions like these by seeking the values
of various variables:

* `fruit.there_are_any`: should there be any items in the list at all?
* `fruit[i]`: the name of the `i`th fruit in the list.
* `fruit.there_is_another`: are there any more fruits that still need
  to be added?

First, the interview will want to know whether there are any items in
the list at all.  It will seek a definition for `fruit.there_are_any`.
Thus, it will ask the question, "Are there any fruit that you would
like to add to the list?"

{% highlight yaml %}
question: |
  Are there any fruit that you would like
  to add to the list?
yesno: fruit.there_are_any
{% endhighlight %}

If the answer to this is `True`, the interview will seek a definition
for `fruit[0]` to gather the first element.  Thus, it will ask the
question "What fruit should be added to the list?"

{% highlight yaml %}
question: |
  What fruit should be added to the list?
fields:
  - Fruit: fruit[i]
{% endhighlight %}

Assume the user enters "apples."

Now **docassemble** knows the first item in the list, but it does not
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
the `fruit.gather()` method will return without asking any questions,
and `fruit.number_as_word()` will respond with the the number of items
in `fruit` (in this case, 2).  When **docassemble** later encounters
`The fruits are ${ fruit }.`, it will attempt to reduce the variable
`fruit` to text.  Since the interview knows that there are no more
elements in the list, it does not need to ask any further questions.
`${ fruit }` will result in `apples and oranges`.

<a name="i"></a>Note that the variable `i` is special in
**docassemble**.  When the interview seeks a definition for
`fruit[0]`, the interview will first look for a question that offers
to define `fruit[0]`.  If it does not find one, it will take a more
general approach and look for a question that offers to define
`fruit[i]`.  The question that offers to define `fruit[i]` will be
reused as many times as necessary.

## Customizing the way information is gathered

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
are there?" and use `fruit.target_number` as the variable set by the
question.  (The `.target_number` attribute is a special attribute,
like `.there_is_another`.)

{% include side-by-side.html demo="gather-fruit-number" %}

<a name="minimum_number"></a>You can avoid the `.there_are_any`
question by setting the `.minimum_number` to a value:

{% include side-by-side.html demo="gather-fruit-at-least-two" %}

## <a name="list of objects"></a>Gathering a list of objects

The examples above have gathered simple variables (e.g., `'apple'`,
`'orange'`) into a list.  You can also gather [objects] into a list.
You can do this by setting the `.object_type` of a [`DAList`] (or
subtype thereof) to the type of object you want the items of the list
to be.

In this example, we gather [`Address`] objects into a [`DAList`] by
setting the `.object_type` attribute to `Address`.

{% include side-by-side.html demo="gather-list-objects" %}

There are some list types that have an `.object_type` by default.  For
example, [`DAEmailRecipientList`] lists have an `.object_type` of
[`DAEmailRecipient`].

{% include side-by-side.html demo="gather-list-email-recipients" %}

During the gathering process, **docassemble** only gathers the
attributes necessary to display each object as text.  So if you do:

{% highlight yaml %}
objects:
  - friend: DAList
---
mandatory: True
code: |
  friend.object_type = Individual
{% endhighlight %}

then the list will consist of [`Individual`]s, and **docassemble**
will gather `friend[i].name.first` for each item in the list.  This is
because of the way that the [`Individual`] object works: if `y` is an
[`Individual`], then its textual representation (e.g., including 
`${ y }` in a [Mako] template, or calling `str(y)` in [Python] code) will
run `y.name.full()`, which, at a minimum, requires a definition for
`y.name.first`.  (See the documentation for [`Individual`] for more
details.)  Other object types behave differently.  For example,
if `y` is an [`Address`], including `${ y }` in a [Mako] template will
result in `y.block()`, which depends on the `address`, `city`, and
`state` attributes.  If you use a plain [`DAObject`] as the
`object_type`, then **no** questions will be asked; this is because
the [`DAObject`] is meant to be a "base class," with no meaningful
attributes of its own.  Thus, calling `str(y)` on a plain [`DAObject`]
will simply return a name based on the variable name; no questions
will be asked.  Thus, it is not recommended that you set `object_type`
to `DAObject`.

If your interview has a list of [`Individual`]s and uses attributes of
the [`Individual`]s besides the name, **docassemble** will eventually
gather those additional attributes, but it will ask for the names
first and only when it is done asking for the names of each individual
in the list will it start asking about the other attributes.  Here is
an interview that does this:

{% include side-by-side.html demo="gather-list-friend-bad-order" %}

<a name="complete_attribute"></a>If you would prefer that all of the
questions about each individual be asked together, you can use the
`.complete_attribute` attribute to tell **docassemble** that an item
is not completely gathered until a particular attribute of that item
is defined.  You can then write a [`code` block] that defines this
attribute.  You can use this [`code` block] to ensure that all the
questions you want to be asked are asked during the gathering process.

In the above example, we can accomplish this by doing
`friend.complete_attribute = 'complete'`.  Then we include a `code`
block that sets `friend[i].complete = True`.  This tells
**docassemble** that an item `friend[i]` is not fully gathered until
`friend[i].complete` is defined.  Thus, before **docassemble** moves
on to the next item in a list, it will run this code block.  This
`code` block will cause other attributes of `friend[i]` to be defined,
including `.birthdate` and `.favorite_animal`.  Here is what the
revised interview looks like:

{% include side-by-side.html demo="gather-list-friend-good-order" %}

You can use any attribute you want as the `complete_attribute`.
Defining a `complete_attribute` simply means that in addition to
ensuring that a list item is displayable (i.e., gathering the name of
an `Individual`), **docassemble** will also seek a definition of the
attribute indicated by `complete_attribute`.  If `.birthdate` was the
only other element we wanted to define during the gathering process,
we could have written `friend.complete_attribute = 'birthdate'` and
skipped the [`code` block] entirely.

When you write your own class definitions, you can set a
default `complete_attribute` that is not really an attribute, but a method
that behaves like an attribute.

In the following example, `FishList` is a list of `Fish`, where a
`Fish` is considered "complete" for purposes of auto-gathering when
the `common_name`, `scales`, and `species` attributes have been
defined.

{% highlight python %}
from docassemble.base.util import DAList, DAObject

__all__ = ['FishList', 'Fish']

class FishList(DAList):
    def init(self, *pargs, **kwargs):
        self.object_type = Fish
        self.complete_attribute = 'fish_complete'
        super(FishList, self).init(*pargs, **kwargs)

class Fish(DAObject):
    @property
    def fish_complete(self):
        self.common_name
        self.scales
        self.species

    def __unicode__(self):
        return self.common_name
{% endhighlight %}

Here is an interview that uses this class definition.

{% include demo-side-by-side.html demo="complete-attribute-method" %}

## <a name="mixed object types"></a>Mixed object types

If you want to gather a list of objects that are not all the same
object type, you can do so by setting the `.ask_object_type` attribute
of the list to `True` providing a block that defines the
`.new_object_type` attribute of the list.

{% include side-by-side.html demo="mixed-list" %}

In this example, we have a list called `location`, which is a type of
[`DAList`].  We have a [`mandatory`] <span></span> [`code` block] that
sets `location.ask_object_type` to `True`.  This instructs
**docassemble** that `location` is a list of objects, and that when a
new item is added to the list, **docassemble** should to look for the
value of `location.new_object_type` to figure out what type of object
the new item should be.  By contrast, the `.object_type` attribute
instructs **docassemble** that the object type for every new object
should be the value of `.object_type`.

Thus, before **docassemble** adds a new item to the list, it will seek
a definition of `location.new_object_type` and then the item it adds
to the list will be an object of the type indicated by the value of
`location.new_object_type`.  After each item is added, **docassemble**
forgets about the value of `location.new_object_type`, so the
question will be asked again for each item in the list.

There are a few things to note about the [`question`] that defines
`location.new_object_type`.

{% highlight yaml %}
question: |
  Do you know the full address of the
  ${ ordinal(location.current_index()) }
  location?
buttons:
  - Yes:
      code: |
        location.new_object_type = Address
  - No:
      code: |
        location.new_object_type = City
{% endhighlight %}

This a question about an item in a list, but note that we do not have
a variable `i` to indicate which item it is, since `.new_object_type`
is an attribute of the list `location`, not an attribute of the new
object (`location[i]`).  Thus, we have to use the
[`.current_index()` method] to obtain the number.

Note also that we are using the method of
[embedding a code block within a multiple choice question] in order to
set the value of `location.new_object_type` based on user input.  You
might think it would be simpler to just write the following:

{% highlight yaml %}
question: |
  Do you know the full address of the
  ${ ordinal(location.current_index()) }
  location?
field: location.new_object_type
buttons:
  - Yes: Address
  - No: City
{% endhighlight %}

However, this would set `location.new_object_type` to a piece of text
(`'Address'` or `'City'`), instead of the object type (`Address` or
`City`).  Thus, when setting `.new_object_type` (or `.object_type`),
make sure to use [Python] code.

Note that there are two questions that ask about attributes of the
list items:

{% highlight yaml %}
---
question: |
  What is the address of the
  ${ ordinal(i) } location?
fields:
  - Address: location[i].address
  - Unit: location[i].unit
    required: False
  - City: location[i].city
  - State: location[i].state
    code: |
      states_list()
  - Zip: location[i].zip
    required: False
---
question: |
  What is the city of the
  ${ ordinal(i) } location?
fields:
  - City: location[i].city
  - State: location[i].state
    code: |
      states_list()
---
{% endhighlight %}

You might be wondering how **docassemble** knows which of these two
questions to ask for a given item in the `location` list.  If the
object is a `City`, a textual representation of the object will first
ask for `.city` and then `.state`.  If the object is an `Address`, a
textual representation of the object will first ask for `.address`.
When **docassemble** gathers items into a list, it asks whatever
questions are necessary to construct a textual representation of the
item.  So if the attribute **docassemble** needs is `.city`, both
questions are capable of defining that attribute.  The "What is the
city" question comes last in the [YAML] file, so it takes precedence
over the "What is the address" question, and it will be asked.  If the
attribute **docassemble** needs is `.address`, only the "What is the
address" question is capable of defining that, so only that question
will be asked.

# <a name="gather dictionary"></a>Gathering information into dictionaries

The process of gathering the items in a [`DADict`] dictionary is
slightly different from the process of gathering the items of a
[`DAList`].  Like the gathering process for [`DAList`] objects, the
gathering process for [`DADict`] objects will call upon the attributes
`.there_are_any` and `.there_is_another`.

In addition, the process will look for the attribute `.new_item_name`
to get the key to be added to the dictionary.  In the example below,
we build a [`DADict`] in which the keys are the names of fruits and
the values are the number of seeds that fruit contains.  There is one
question that asks for the fruit name (`fruit.new_item_name`) and a
separate question that asks for the number of seeds (`fruit[i]`).
(When populating a [`DADict`], `i` refers to the key, whereas when
populating a [`DAList`], `i` refers to a number like 0, 1, 2, etc.)

{% include side-by-side.html demo="gather-dict" %}

Alternatively, you can use the attribute `.new_item_value` to set the
value of a new item.

{% include side-by-side.html demo="gather-dict-value" %}

The value of the `.new_item_value` attribute will never be sought by
the gathering process; only the value of the
`.new_item_name` attribute will be sought.  So if you want to use
`.new_item_value`, you need to set it using a question that
simultaneously sets `.new_item_name`, as in the example above.

## <a name="dict of objects"></a>Gathering a dictionary of objects

You can also populate the contents of a [`DADict`] in which each value
is itself an object.

{% include side-by-side.html demo="gather-dict-object" %}

In the example above, we populate a [`DADict`] called `pet`, in which
the keys are a type of pet (e.g., `'cat'`, `'dog'`), and the values
are objects of type [`DAObject`] with attributes `.name` (e.g.,
`'Mittens'`, `'Spot'`) and `.feet` (e.g., `4`).  We need to start by
telling **docassemble** that the [`DADict`] is a dictionary of
objects.  We do this by setting the `.object_type` attribute of the
[`DADict`] to [`DAObject`], using some [`mandatory`] code.
(Alternatively, the [`objects`] block could have included the line
`pet: DADict.using(object_type=DAObject)`) Then we provide a question 
that sets the `.new_item_name` attribute.

When a `.object_type` is provided, **docassemble** will take care of
initializing the value of each entry as an object of this type.  It
will also automatically gather whatever attributes, if any, are
necessary to represent the object as text.  The representation of the 
object as text is what you see if you include the object in a [Mako] template:
`${ pet['cat'] }`.  (Or, if you know [Python], it is the result of
`str(pet['cat'])`.)  The attributes necessary to represent the object
as text depend on the type of object.  In the case of a [`DAObject`],
no attributes are required to represent the object as text.  In the
case of an [`Individual`], the individual's name is required
(`.name.first` at a minimum).

Since a [`DAObject`] does not have any necessary attributes, then in
the example above, the `pet` object is considered "gathered"
(i.e. `pet.gathered` is `True`) after all the types of pet (e.g.,
`'cat'`, `'dog'`) have been provided.  At this point, the values of
the [`DADict`] are simply empty [`DAObject`]s.  The `.name` and
`.feet` attributes are still not defined.  The final screen of the
interview, which contains a "for" loop that describes the number of
feet of each pet, causes the asking of questions to obtain the `.feet`
and `.name` attributes.

# <a name="gather set"></a>Gathering information into sets

The gathering of items into a [`DASet`] is much like the gathering of
items into a [`DADict`].  The difference is that instead of using the
attributes `.new_item_name` and `.new_item_value`, you use a single
attribute, `.new_item`.

Here is an example that gathers a set of text items (e.g., `'apple'`,
`'orange'`, `'banana'`) into a [`DASet`].

{% include side-by-side.html demo="gather-set" %}

You can also gather objects into a [`DASet`].  However, the [`DASet`]
does not use the `.object_type` attribute, as [`DAList`] and
[`DADict`] groups do.  The objects that you gather into a [`DASet`]
need to exist already.

In the example below, we create several [`DAObject`]s, each
representing a fruit, and we use a multiple choice question with
`datatype` set to `object` to ask which fruits the user likes.  (See
[selecting objects] for more information about these types of
questions.)

{% include side-by-side.html demo="gather-set-object" %}

# <a name="manual"></a>Manually triggering the gathering process

In the examples above, the process of asking questions that populate
the list is triggered implicitly by code like `${ fruit.number() }`,
`${ fruit }` or `% for item in fruit:`.

If you want to ask the questions at a particular time, you can do so
by referring to `fruit.gather()`.  (Behind the scenes, this is the
same method used when the process is implicitly triggered.)

{% include side-by-side.html demo="gather-fruit-gather" %}

The `.gather()` method accepts some optional keyword arguments:

* `minimum` can be set to the minimum number of items you want to
  gather.  The `.there_are_any` attribute will not be sought.  The
  `.there_is_another` attribute will be sought after this minimum
  number is reached.
* `number` can be set to the total number of items you want to
  gather.  The `.there_is_another` attribute will not be sought.
* `item_object_type` can be set to the type of object each element of
  the group should be.  (This is not available for [`DASet`] objects.)
* `complete_attribute` can be set to the name of an attribute that
  should be sought for each item during the gathering process.  You
  can also set the [`complete_attribute`] attribute of the group object
  itself.

The `.gather()` method is not the only way that a gathering process
can be triggered.  The `.auto_gather` attribute controls whether the
`.gather()` method is invoked.  If `.auto_gather` is `True` (which is
the default), then the gathering process will be triggered using
`.gather()`.  If `.auto_gather` is `False`, the gathering process will
be triggered in a simpler way: by seeking the value of `.gathered`.
Thus, you can provide a [`code` block] that sets `.gathered` to
`True`.  For example:

{% include side-by-side.html demo="gather-manual-gathered" %}

Setting `.gathered` to `True` means that when you try to get the
length of the group or iterate through it, **docassemble** will assume
that nothing more needs to be done to populate the items in the group.
You can still add more items to the list if you want to, using
[`code` block]s.

# Detailed explanation of gathering process

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

To gather the list manually, it is necessary to [disable the automatic
gathering system]:

{% highlight python %}
fruit.auto_gather = False
fruit.gathered = True
{% endhighlight %}

This example uses a little bit of [Python] code to ask the appropriate
questions.

Some variables are initialized:

{% highlight python %}
num_fruits = 0
more_fruits = True
{% endhighlight %}

Then the main algorithm is:

{% highlight python %}
while more_fruits:
  fruit[num_fruits]
  num_fruits += 1
  del more_fruits
{% endhighlight %}

Since `more_fruits` is initialized as `0`, the first undefined
variable that this code encounters is `fruit[0]`.  When the code
encounters `fruit[0]`, it will go looking for the value of `fruit[0]`,
and the question "What's the first fruit?" will be asked.  Once
`fruit[0]` is defined, the interview undefines `more_fruits`, but then
when the `while` loop loops around, the definition of `more_fruits` is
needed.  Since `more_fruits` is undefined, the interview presents the
user with the `more_fruit` question, which asks "Are there more
fruits?"  If `more_fruits` is `True`, the loop repeats, and the
definition of `fruit[1]` is sought.

This is starting to get complicated.  And things get even more
complicated when you want to say things like "There are three fruits
in all" and "You have told me about three fruits so far" in your
interview questions.  In the case of "There are three fruits in all,"
a prerequisite to saying this is to make sure that the user has
supplied the full list.  But in the case of "You have told me about
three fruits so far," you would not want this prerequisite.

Since asking users for lists of things can get complicated,
**docassemble** has a feature for automating the process of asking the
necessary questions to fully populate the list.

If your list is `fruit`, there are three special attributes:
`fruit.gathered`, `fruit.there_are_any`, and `fruit.there_is_another`.
The `fruit.gathered` attribute is initially undefined, but is set to
`True` when the list is completely populated.  The
`fruit.there_are_any` attribute is used to ask the user whether the
list is empty.  The `fruit.there_is_another` attribute is used to ask
the user questions like "You have told me about three fruits so far:
apples, peaches, and pears.  Are there any additional fruits?"

In addition to these two attributes, there is special method,
`fruit.gather()`, which will cause appropriate questions to be asked
and will return `True` when the list has been fully populated.  The
`.gather()` method looks for definitions for `fruit.there_are any`,
`fruit[i]`, and `fruit.there_is_another`.  It makes
`fruit.there_is_another` undefined as necessary.

Here is a complete example:

{% include side-by-side.html demo="gather-fruit" %}

# <a name="for loop"></a>Using "for loops"

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

For loops based on [`DAList`], [`DADict`], and [`DASet`] objects can
be included in textual content using the `for`/`endfor` [Mako] statement:

{% include side-by-side.html demo="for_fruit" %}

[Mako] "for" loops work just like [Python] for loops, except that they
need to be ended with "endfor."

If the list might be empty, you can check its length using an
`if`/`else`/`endif` [Mako] statement:

{% highlight yaml %}
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
mandatory: True
{% endhighlight %}

You can also use the [`.number()`] method:

{% highlight yaml %}
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

For more information about "for loops" in [Mako], see the
[markup section].

# <a name="editing"></a>Edit an already-gathered list

It is possible to allow your users to edit a [`DAList`] list that has
already been gathered.  Here is an example.

{% include side-by-side.html demo="edit-list" %}

This works using two features:

1. The `edit` specifier on the [`table`] block, which adds an
   "Actions" column to the table and indicates which screens should be
   shown when the user clicks the "Edit" button.  First a screen will
   be shown that asks for the the attribute `.name.first`.  Then a
   screen will be shown that asks for the attribute `.favorite_fruit`.
2. The `.add_action()` method on the [`DAList`] inserts HTML for a
   button that the user can press in order to add an entry to an
   already-gathered list.

You can allow your users to edit a [`DAList`] from an edit button in a
[`review`] page.

{% include side-by-side.html demo="review-edit-list" %}

The attribute `.revisit` of a [`DAList`] is special; it is undefined
by default and is set to `True` by the auto-gathering process at the
same time that `.gathered` is set to `True`.  Because `.revisit` is
undefined at first, the [`review`] block will not show the "Edit"
button for the list until the list is gathered.  When the list has
been gathered, and the user clicks the "Edit" button associated with
`.revisit`, the user is taken to the block with `field:
person.revisit`.  On this screen, you can show the list as a table
and provide the `.add_action()` button if you want users to be able to
add entries.

Putting an editable table directly into a review page is also
possible.

{% include side-by-side.html demo="review-edit-list-table" %}

The line `need: person.table` is important here.  An item in a
`review` list will not be shown if it contains any undefined
variables.  The presence of an undefined variable in a `review` list
item will not cause **docassemble** to seek a definition of that
variable (unless the specifier `skip undefined: False` is used).
Therefore, if you want a `review` item containing a `table` to be
displayed, you need to make sure that the variable representing the
`table` gets defined by the time that you want the table to be
editable.  In this example, `need: person.table` ensures that the
variable representing the table is defined before the user is given
the opportunity to review his or her answers.

While the above examples have all featured tables for editing `DAList`
objects, the `edit` feature can also be used when the `rows` of the
[`table`] refer to a [`DADict`]:

{% include side-by-side.html demo="table-dict-edit" %}

## <a name="custom editing"></a>Customizing the editing interface

If you do not want your users to be able to delete items, you can add
`delete buttons: False` to the [`table`].

{% include side-by-side.html demo="table-dict-edit-delete-buttons" %}

Or, if you want your users to be able to delete items, but not edit
items, you can include `delete buttons: True` and do not include
`edit`:

{% include side-by-side.html demo="table-dict-delete-buttons" %}

If you want to allow your users to delete items, but only if the group
is longer than a certain length, you can give the [`DAList`] or
[`DADict`] a [`minimum_number`] attribute.

{% include side-by-side.html demo="table-dict-edit-minimum-number" %}

<a name="read only"></a>If you want specific items to be protected
against editing and/or deletion, you can set a `read only` specifier:

{% include side-by-side.html demo="table-read-only" %}

In this example, the attribute `important` of the table `fruit`
determines whether the item is "read only" or not.  The first two
items in the `DAList`, which are added to the list in a `code` block,
have the `important` attribute set to `True`, while items that are
added by the user have the `important` attribute set to `False`.
Since `read only` is set to `important`, the `Edit` and `Delete`
buttons are not available for the items that have the `important`
attribute set to `True`.

If you want to allow editing but not deletion, or vice versa, the
value of the attribute can be set to a [Python] dictionary rather than
the value `True` or `False`.  If the value of the key `edit` is false,
the "Edit" button will not be shown.  If the value of the key
`delete` is false, the "Delete" button will not be shown.

{% include side-by-side.html demo="table-read-only-2" %}

<a name="editable"></a>If you have a `table` definition that includes
editable elements (i.e. `edit`, `delete buttons`), but you want to
present the table with the editing features in some contexts, but
without the editing features in other contexts, you can include the
table by calling the method `.show()` with `editable=False` to hide
the editing features.

{% include side-by-side.html demo="edit-list-non-editable" %}

# <a name="reordering"></a>Reorder an already-gathered list

If you have a [`DAList`] and you want to allow the user to change the
order of items in the list, you can set `allow reordering` to `True`:

{% include side-by-side.html demo="table-reorder" %}

The changes to the order of elements will be saved when the user
presses Continue.

# <a name="list collect"></a>Collect all items on one page

By default, when gathering or editing a list item, **docassemble**
asks about only one list item at a time.  If you have a [`question`]
that contains a [`fields`] specifier and that uses iterator variables
(`i`, `j`, `k` etc.) in the variable names, you can use `list collect`
to expand this [`question`] on the screen so that the user can enter
answers for multiple list items on one screen.

{% include side-by-side.html demo="list-collect" %}

The `list collect` specifier can be set to `True`, `False`, or
[Python] code that evaluates to a true or false value.  If the value
is true, the [`question`] will be expanded; if it is false, the
[`question`] will not be expanded.

You can customize the behavior of the [`question`] by setting `list
collect` to a dictionary.

The available keys for the dictionary are:

* `enable`: this can be `True`, `False`, or [Python] code that
  evaluates to a true or false value.  If the value is true, the
  [`question`] will be expanded; if it is false, the [`question`] will
  not be expanded.  (This is the same as the value for the shorthand
  version of `list collect` discussed above.)  If `list collect` is a
  dictionary and `enable` is omitted, the default value is `True`.
* `label`: this can be set to a text label for each item on the
  screen.  If it is "Fruit," the items will be labeled "Fruit 1,"
  "Fruit 2," etc.  [Mako] templating can be used.
* `is final`: this can be `True`, `False`, or [Python] code that
  evaluates to a true or false value.  If the value is true, then the
  `there_is_another` attribute will be set to `True` when the user
  presses the Continue button.  The default value is `True`.
* `allow append`: this can be `True`, `False`, or [Python] code that
  evaluates to a true or false value.  If the value is true, then the
  user is allowed to add additional items to the list.  If the value
  is false, the user can only edit the existing items.  The default
  value is `True`.
* `allow delete`: this can be `True`, `False`, or [Python] code that
  evaluates to a true or false value.  If the value is true, then the
  user is allowed to delete existing items from the list.  If it is
  false, the user will not see any "Delete" buttons except on items
  that appear because the user clicked the "Add another" button.

Here is an example:

{% include side-by-side.html demo="list-collect-options" %}

This example demonstrates how you can use the `enable` attribute to
indicate that the multiple-item collection method should be used to
gather the list initially, but that the ordinary one-item-per-screen
method should be used for editing list elements or adding new list
elements after the list is initially gathered.

If you set a the `minimum_number` attribute on the [`DAList`] to 3,
the first three items in the list will not have Delete buttons.

The `list collect` specifier only works on [`DAList`] variables, not
on [`DADict`] or [`DASet`] variables.

# <a name="examples"></a>Examples

## <a name="nested objects"></a>List of dictionaries from checkbox

Here is an example of an interview that uses a checkbox to determine
which items to use in a dictionary.

{% include side-by-side.html demo="nested-objects" %}

## <a name="prepopulate"></a>Prepopulate a list

Here is an example of an interview that populates a list with two
entries before allowing the user to add other entries.

{% include side-by-side.html demo="prepopulate-list" %}

This interview takes advantage of the fact that the automatic
gathering process will seek a definition of the `.there_are_any`
attribute.  It uses the code block that defines `.there_are_any` to
populate the list of objects.

Note that `user.favorite_things.clear()` is called.  This line happens
to be unnecessary in this interview, but it illustrates a good
practice.  Code blocks in **docassemble** often need to be
[idempotent]; they should be able to be run from the beginning more
than once without causing unwanted side effects.  Code blocks often
restart because when an undefined variable is encountered and the
definition is retrieved from the user or from another code block, the
original code block does not pick up where it left off, but rather
starts at the beginning again.

Alternatively, you could prepopulate a list by using [`mandatory`]
code at the beginning of an interview to append items to the list.
Then the interview will never even seek a definition of the
`.there_are_any` attribute.  The method described above is helpful,
however, in cases where the list being initialized does not exist at
the start of the interview, as would be the case if the list was
`user.sibling[i].favorite_things`.

## <a name="postpopulate"></a>Postpopulate a list

Here is an example of an interview that populates a list with two
entries after the user is done adding entries.

{% include side-by-side.html demo="postpopulate-list" %}

This interview uses code blocks to determine
`user.favorite_things.there_are_any` and
`user.favorite_things.there_is_another`.  Instead of asking the user
questions that define these variables directly, the interview asks
questions that set the variables `user.likes_something` and
`user.likes_another_thing`.  It can then use code to do things
depending on what the answers are.

If the user says he has no favorite things, the interview adds Mom and
apple pie to `user.favorite_things`.  If the user does describe some
favorite things, and then says that he has no other favorite things,
the interview will then add Mom and apple pie to the list.

Note that if the user says he has no favorite things, the interview
sets `.there_is_another` to `False`.  This is necessary to persuade the
automatic gathering feature that the list is fully gathered.

Note the use of [`del`] to undefine `user.likes_another_thing` as soon
as it is set to `True`.  This is because the automatic gathering
system will need to ask the question again, and if
`user.likes_another_thing` is already set to `True`, the list of the
user's favorite things will be infinite!  Similarly, behind the
scenes, the automatic gathering process undefines `.there_is_another`
after it is defined.

[markup section]: {{ site.baseurl }}/docs/markup.html#for
[legal applications]: {{ site.baseurl }}/docs/legal.html
[Mako]: http://www.makotemplates.org/
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
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
[objects]: {{ site.baseurl }}/docs/objects.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[selecting objects]: {{ site.baseurl }}/docs/fields.html#objects
[disable the automatic gathering system]: #manual
[`generic object`]: {{ site.baseurl }}/docs/modifiers.html#generic object
[`Address`]: {{ site.baseurl }}/docs/objects.html#Address
[`DAEmailRecipientList`]: {{ site.baseurl }}/docs/objects.html#DAEmailRecipientList
[`DAEmailRecipient`]: {{ site.baseurl }}/docs/objects.html#DAEmailRecipient
[`.current_index()` method]: {{ site.baseurl }}/docs/objects.html#DAList.current_index
[embedding a code block within a multiple choice question]: {{ site.baseurl }}/docs/fields.html#code%20button
[expression]: http://stackoverflow.com/questions/4782590/what-is-an-expression-in-python
[`objects`]: {{ site.baseurl }}/docs/initial.html#objects
[idempotent]: https://en.wikipedia.org/wiki/Idempotence#Computer_science_meaning
[`del`]: https://docs.python.org/2/tutorial/datastructures.html#the-del-statement
[YAML]: https://en.wikipedia.org/wiki/YAML
[`table`]: {{ site.baseurl }}/docs/initial.html#table
[`review`]: {{ site.baseurl }}/docs/fields.html#review
[`minimum_number`]: #minimum_number
[`complete_attribute`]: #complete_attribute
[`DAOrderedDict`]: {{ site.baseurl }}/docs/objects.html#DAOrderedDict
[set theory]: https://en.wikipedia.org/wiki/Set_theory
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
