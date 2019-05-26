---
layout: docs
title: Objects
short_title: Objects
---

# <a name="how"></a>How docassemble uses objects

[Python] allows [object-oriented programming] and so does
**docassemble**.

Object-oriented programming can seem complicated at first, but it
actually makes programming much easier.  For an easy-to-read
introduction to object-oriented programming, see [Object-oriented
Programming for Document Assembly Developers] by [Quinten Steenhuis].

Here is a non-object-oriented way of saying hello to the user by name:

{% include side-by-side.html demo="hello-not-oop" %}

A better way is to define `user` as a **docassemble** object,
[`Individual`].

{% include side-by-side.html demo="hello-oop" %}

As explained in the [fields] section, variable names cannot contain
any punctuation other than the underscore.  So while `user_first_name`
is a valid variable name, `user.name.first` must be referring to
something different.  Periods in [Python] are used to refer to the
"attributes" of "objects."

An object is a special type of variable.  Rather than being a piece of
text, like `user_first_name` is, the variable `user` is an "object"
that is an "instance" of the "class" known as [`Individual`].

Using objects in **docassemble** requires a little bit of setup using
[initial blocks].  The [`objects`] block declares that `user` is an
instance of the class [`Individual`].

Objects have "attributes."  In the above example, `name` is an
attribute of the object `user`.  And `name` is itself an object (it is
an instance of the class [`IndividualName`], though you would need to
look at the [source code] to know that) with attributes `first` and
`last`.  The attributes `first` and `last` are not objects, but rather
pieces of text.  Anything before a `.` is an object, and anything
after the `.` is an attribute of the object.

Objects also have "methods," which are functions that return a value
based on the attributes of the object.  For example,
`user.age_in_years()` will return the current age of the `user` based
on the date defined in the attribute `user.birthdate`:

{% include side-by-side.html demo="age_in_years" %}

Methods are similar to attributes in that they are written with a `.`
before them.  The difference is that they run code to produce a value,
rather than simply accessing a stored value.  You can tell by the
presence of parentheses whether a method is being used.

Using objects in your interviews has a number of advantages over
using plain variables.

<a name="generic"></a>The first advantage is that you can write
[`generic object`] questions.  (See [modifiers] for documentation of
the [`generic object`] feature.)

For example, if you need to collect the phone numbers of three people,
the `grantor`, the `grantee`, and the `trustee`, you don't have to
write separate questions for `grantor.phone_number`,
`grantee.phone_number`, and `trustee.phone_number`.  You can write one
question to collect `x.phone_number`, where `x` is a "generic object"
that acts as a stand-in for any object of type `Individual`.

{% include side-by-side.html demo="generic-object-phone-number" %}

Any time **docassemble** needs to know the phone number of an
[`Individual`], this question will allow it to ask the appropriate question.

In the question text above, [`possessive()`] is a "method" that you can
use on any instance of the [`Individual`] class.  If `trustee`'s name is
Fred Smith, `trustee.possessive('phone number')` returns "Fred Smith's
phone number."  The method is pretty smart; `user.possessive('phone
number')` will return "your phone number."

Using objects also allows you to have different variables that refer
to the exact same thing.  For example, if `user` is already defined as
an object and you run this code:

{% highlight python %}
trustee = user
{% endhighlight %}

then you will define the variable `trustee` as being equivalent to the
`user` object.  `trustee.name.first` will always return the same thing
as `user.name.first`, and `trustee.phone_number` will always return
the same thing as `user.phone_number`.  In addition,
`trustee.possessive('phone number')` will return "your phone number."
You can write code that checks for the equivalence of objects, using
the `is` operator:

{% include side-by-side.html demo="user-is-trustee" %}

Object methods allow you to have a standard way of expressing
information even though the methods used to gather the information may
vary depending on the circumstances.  For example, the
[`age_in_years()`] method, discussed above, first looks to see if the
attribute `age` is defined, and if so will return that instead of
asking for the `birthdate` attribute:

{% include side-by-side.html demo="testage2" %}

Although objects are a fairly complicated concept, as you can see,
they allow you to write code that looks much like plain English.

In part, this is because objects allow you to do complicated things in
an implicit way.  For example, writing `${ grantee }` in a [Mako]
template will return the name of the grantee.  The interview
implicitly calls the method `__str()__` on `grantee`.
`grantee.__str()__` in turn calls `grantee.name.full()`, which strings
together the `grantee`'s full name from its constituent parts
(`name.first`, `name.middle`, `name.last`, and `name.suffix`), all but
the first of which are optional and will not be included if they are
not defined.

Note that object methods may depend upon particular attributes of
objects being defined.  If an attribute is needed but not defined,
**docassemble** will go looking for a `question` or `code` block that
defines the attribute.  For example, if you write this in a question:

{% highlight text %}
Remember that ${ trustee.possessive('phone number') } is
${ trustee.phone_number }.
{% endhighlight %}
    
then in order to ask the question, **docassemble** may ask you for the
trustee's name (so it can say "Remember that John Smith's phone number
is ..."), and then ask for the trustee's `phone_number` if it is not
already defined.

# <a name="stdclasses"></a>Standard docassemble classes

The classes in this section are automatically available for use in
**docassemble** interviews (unless you set [`suppress loading util`]).

To use them within a [Python module], include a line like the
following at the top of your .py file:

{% highlight python %}
from docassemble.base.util import Individual
{% endhighlight %}

When you use objects from non-standard packages, you will need to
include a `modules` block to import the names from the package into
your interview, so that you can use the objects that are available
from that package.

## <a name="DAObject"></a>DAObject

All **docassemble** objects are instances of the `DAObject` class.
`DAObject`s are different from normal [Python objects] because they
have special features that allow their attributes to be set by
**docassemble** questions.  If `fruit` is an ordinary [Python object]
and you refer to `fruit.seeds` when `seeds` is not an existing
attribute of `fruit`, [Python] will generate an [AttributeError].  But
if `fruit` is a `DAObject`, **docassemble** will intercept that error
and look for a [`question`] or [`code`] block that offers to define
`fruit.seeds`.  Or, if that does not work, it will look for a
[`generic object`] block that offers to define `x.seeds` for a `DAObject`.

From the interview developer's perspective, `DAObject`s can be treated
like ordinary [Python objects] in most ways, but there are exceptions.

An important characteristic of all [`DAObject`]s is that they have
intrinsic names.  If you do:

{% highlight yaml %}
objects:
  - foo: DAObject
{% endhighlight %}

then `foo.instanceName` will be `'foo'`.  The object knows its own
name.  This is not a standard feature of [Python] objects, but a
feature added by **docassemble**.

Since `foo` is a [Python] object, you can create other names
for the same object, but the `instanceName` attribute will not change.

{% highlight python %}
>>> from docassemble.base.util import DAObject
>>> foo = DAObject('foo')
>>> foo.instanceName
'foo'
>>> foo.seeds = 4
>>> foo.seeds
4
>>> bar = foo
>>> bar.instanceName
'foo'
>>> bar.seeds += 1
>>> foo.seeds
5
{% endhighlight %}

The fact that each [`DAObject`] has only one intrinsic name can lead
to confusion in interviews if you are not careful.  For example,
suppose you try the following:

{% include side-by-side.html demo="branch-error" %}

This will result in the following error:

> There was a reference to a variable 'long_branch.length' that could
> not be looked up in the question file or in any of the files
> incorporated by reference into the question file.

You might think, "hey, why doesn't my interview ask the question that
sets `tree.branch.length`?"  The reason is that `tree.branch` is just
an alias for `long_branch`, and the object knows itself only as
`long_branch`.  Thus, when the interview needs a definition for the
`.length` attribute of this object, it will look for
`long_branch.length`.

If you had a question that defined `long_branch.length` or a
[`generic object`] question for the `x.length` where `x` is a
[`DAObject`], then the interview would use that question.  However,
the interview is not able to search for the length of the branch using
`tree.branch.length` since the intrinsic name of the object is
`long_branch`, not `tree.branch`.

This will work as intended:

{% include side-by-side.html demo="branch-no-error" %}

You also need to be careful about intrinsic names if you [write your
own functions].  For example, assume you wrote a [Python module]
containing:

{% highlight python %}
from docassemble.base.util import DAList, Thing

def build_list():
    the_list = DAList('the_list', object_type=Thing)
    for indexno in range(4):
        the_list.appendObject()
    return the_list
{% endhighlight %}

Assume you then created some lists in your interview:

{% highlight yaml %}
code: |
  list_of_fruits = build_list()
  list_of_vegetables = build_list()
{% endhighlight %}

The problem here is that the `list_of_fruits` and `list_of_vegetables`
objects, as well as their subobjects, will not have the right
intrinsic names.

In some situations, you can wrote `foo = DAObject()` instead of `foo =
DAObject('foo'), and it will automatically figure out the instance
name, but this is fragile, and under certain circumstances it can
fail, and it will fall back to giving the object a random instrinsic
name.  To avoid this problem, you can always set the intrinsic name of
an object at the time you create it by passing the intrinsic name you
want to use as the first parameter.

Thus, you can do:

{% highlight python %}
def build_list(list_name):
    the_list = DAList(list_name, object_type=Thing)
    for indexno in range(4):
        the_list.appendObject()
    return the_list
{% endhighlight %}

And then this will work:

{% highlight yaml %}
code: |
  list_of_fruits = build_list('list_of_fruits')
  list_of_vegetables = build_list('list_of_vegetables')
{% endhighlight %}

The requirement of making sure your objects are aware of their names
is inconvenient, but necessary.  [Python] has no built-in system by
which a variable can know its own name.  In **docassemble**, it is
necessary for objects to know their own names so that when your
interview logic refers to an undefined object attribute, list element,
or dictionary key, **docassemble** knows what [`question`] or [`code`]
block to use to obtain a definition of the undefined variable.

One of the useful things about `DAObject`s is that you can write
[`generic object`] questions that work in a wide variety of
circumstances because the questions can use the variable name itself
when forming the text of the question to ask the user.

<a name="DAObject.object_name"></a>If you refer to a `DAObject` in a
[Mako] template (or reduce it to text with Python's [str() function]),
this will have the effect of calling the [`object_name()`] method,
which attempts to return a human-friendly name for the object.

For example:

{% include side-by-side.html demo="daobject" %}

Although there is only one question for `x.color`, this question
generates both "What is the color of the turnip?" and "What is the
color of the front gate in the park?"  This is because [`object_name()`]
is implicitly called and it turns `park.front_gate` into "front gate
in the park."

The [`object_name()`] method is multi-lingual-friendly.  By using
`docassemble.base.util.update_word_collection()`, you can provide
non-English translations for words that come from variable names, such
as "turnip," "park," and "front gate."  By using
[`docassemble.base.util.update_language_function()`], you can define a
non-English version of the `a_in_the_b()` function, which
[`object_name()`] uses to convert an attribute name like
`park.front_gate` into "front gate in the park."  (It calls
`a_in_the_b('front gate', 'park')`.)  So in a Spanish interview,
`park.front_gate.object_name()` would return "puerta de entrada en el
parque."  (The Spanish version of `a_in_the_b()` will be more
complicated than the English version because it will need to determine
the gender of the second argument.)

<a name="DAObject.object_possessive"></a>A related method of
`DAObject` is `object_possessive()`.  Calling
`turnip.object_possessive('leaves')` will return `the turnip's
leaves`.  Calling `park.front_gate.object_possessive('latch')` will
return `the latch of the front gate in the park`.

The `DAObject` is the most basic object, and all other **docassemble**
objects inherit from it.  These objects will have different methods
and behaviors.  For example, if `friend` is an [`Individual`], calling
`${ friend }` in a [Mako] template will not return
`friend.object_name()`; rather, it will return `friend.full_name()`,
which may require asking the user for the `friend`'s name.

<a name="DAObject.initializeAttribute"></a>A [`DAObject`] can have any
attributes you want to give it.  When those attributes are objects
themselves, you need to use the `initializeAttribute()` method.

One way to initialize attributes of an object is to use [Python] code:

{% highlight yaml %}
objects:
  - fish: DAObject
---
code: |
  fish.best_friend = DAObject()
{% endhighlight %}

Under many circumstances, this works, and the variable on the left
will be assigned a correct `instanceName`.

However, **docassemble**'s system for setting the `instanceName`
in circumstances like this relies on hacking the internals of
[Python].  It is not guaranteed to work in all circumstances.  A safe
way to define attributes is as follows:

{% highlight yaml %}
objects:
  - fish: DAObject
---
sets: fish.best_friend
code: |
  fish.initializeAttribute('best_friend', DAObject)
{% endhighlight %}

The first argument to `initializeAttribute` is the attribute name, as
quoted text.  The second argument is the name of the object the
attribute should be (not quoted).

It is necessary to modify the [`code`] block with [`sets`] because
**docassemble** needs help figuring out that the code block
offers to define `fish.best_friend`.

The `initializeAttribute()` method returns the object it just
initialized.

<a name="DAObject.reInitializeAttribute"></a>The
[`initializeAttribute()`] method will have no effect if the attribute
is already defined.  If you want to force the setting of an attribute
in situations when the attribute is already defined, use
`reInitializeAttribute()` instead of [`initializeAttribute()`], and it
will overwrite the attribute.  The `reInitializeAttribute()` method
returns the object it just reinitialized.

Another way to define object attributes is to use the [`objects`]
block.

{% highlight yaml %}
objects:
  - fish: DAObject
  - fish.best_friend: DAObject
{% endhighlight %}

You can even use [`objects`] with the [`generic object`] modifier:

{% highlight yaml %}
generic object: Person
objects: |
  - x.principal_place_of_business: City
{% endhighlight %}

This will ensure that the `principal_place_of_business` of an
[`Individual`] or [`Organization`] is always a [`City`].

The [`DAObject`] provides some convenience functions for working with
object attributes.

<a name="DAObject.attribute_defined"></a>The `attribute_defined()`
method will return `True` or `False` depending on whether the given
attribute is defined.  The attribute name must be provided as quoted
text.  For example:

{% highlight yaml %}
objects:
  - client: Individual
---
mandatory: True
question: |
  % if client.address.attribute_defined('city'):
  You live in ${ client.address.city }.
  % else:
  I don't know where you live.
  % endif
{% endhighlight %}

<a name="DAObject.attr"></a>The `attr()` method will return the value
of the given attribute.  The attribute must be provided as text.
(E.g., `client.address.attr('city')`.)  If the attribute is not
defined, `None` will be returned.  This can be useful if you have
several attributes but you want to access them programmatically.  For
example:

{% highlight yaml %}
mandatory: True
question: |
  Your address.
subquestion: |
  % for part in ['address', 'city', 'state', 'zip']:
  Your ${ part } is ${ client.address.attr(part) }.
  
  % endfor
{% endhighlight %}

Note that because `None` is returned when the attribute is not
defined, this method will not trigger a process of retrieving a
definition for the attribute.  If you want to trigger this process,
use the built-in [Python] function [`getattr()`].

{% highlight yaml %}
code: |
  for characteristic in ['eye_color', 'hair_color', 'weight']:
    getattr(client.child[i], characteristic)
  client.child[i].complete = True
{% endhighlight %}

As discussed below, the [`Individual`] object has interesting methods
related to pronouns.  These methods are universal, so you can use them
on any [`DAObject`].

<a name="DAObject.pronoun"></a><a
name="DAObject.pronoun_objective"></a><a
name="DAObject.pronoun_subjective"></a><a
name="DAObject.pronoun_possessive"></a>If the object is a generic
[`DAObject`], or a subclass of [`DAObject`] that does not have any
special pronoun behavior, then the `.pronoun()`,
`.pronoun_subjective()`, and `.pronoun_objective()` methods all return
`'it'`.  The `.pronoun_possessive()` method returns `'its'` followed
by the argument.  For example, `thing.pronoun_possessive('reason')`
returns `'its reason'`.

<a name="DAObject.as_serializable"></a>The `.as_serializable()` method
returns a representation of the object and its attributes.  Objects
are converted to [Python dict]s, so that they can be serialized to
[JSON].  The conversion is not reversible, and much information cannot
be converted.  Nevertheless, this can be a useful way to access
information in your objects in other systems.  See also the
[`all_variables()`] function.

<a name="DAObject.copy_shallow"></a>The `copy_shallow()` method
creates a copy of the object and gives it a new intrinsic name.

{% highlight python %}
new_object = old_object.copy_shallow('new_object')
{% endhighlight %}

The copy is "shallow," which means that while `new_object` will be a
new object with its own separate existence, sub-objects of the new
object will simply be references to corresponding sub-objects of the
original object.

{% highlight python %}
>>> new_object is old_object
False
>>> new_object.sub_object is old_object.sub_object
True
{% endhighlight %}

{% include side-by-side.html demo="copy-shallow" %}

<a name="DAObject.copy_deep"></a>The `copy_deep()` method creates a
copy of the object its sub-objects and gives it, and all of its
sub-objects, new intrinsic names.

{% highlight python %}
new_object = old_object.copy_deep('new_object')
{% endhighlight %}

Because the copy is "deep," each sub-object has a separate existence:

{% highlight python %}
>>> new_object is old_object
False
>>> new_object.sub_object is old_object.sub_object
False
{% endhighlight %}

{% include side-by-side.html demo="copy-deep" %}

## <a name="DAList"></a>DAList

A `DAList` acts like an ordinary [Python list], except that
**docassemble** can ask questions to define items of the list.

Here is a simple "Mad Libs" interview that uses `DAList`s to keep
track of words:

{% include side-by-side.html demo="madlibs" %}

The variable `i` is special.  When the interview encounters
`person[0]` and sees that it is undefined, it will go searching for a
question that offers to define `person[0]`.  If it does not find that,
it will generalize and look for a question that offers to define
`person[i]`.  If that is not found, it will generalize further and
look for a question that offers to define `x[i]`.  Thus, the one
[`generic object`] question, which defines `x[i]` where `x` is a
`DAList`, will ask all of the questions in the interview.

For another example, suppose you want to work with a list of
prospective recipients of an e-mail.  You could define `recipient` as
a `DAList` containing five [`Individual`]s

{% include side-by-side.html demo="testdalist" %}

This will result in the following five questions being asked:

* What is the name of the trustee?
* What is the name of the beneficiary?
* What is the name of the grantor?
* What is the name of the fourth recipient?
* What is the name of the fifth recipient?

<a name="DAList.appendObject"></a>The `DAList` operates like a [list]
in [Python], but it also has some special methods.  When adding a new
item to the list, you should use the **docassemble**-specific 
`appendObject()` method.  This method is similar to the
`initializeAttribute()` method we discussed earlier.  Running
`recipient.appendObject(Individual)` creates a new object of the class
[`Individual`] and adds it to the list.  The `.appendObject()` method
returns the object it creates.  In the example above, the
first such object is the fourth item in the list, which means that the
intrinsic name of the new object is `recipient[3]`.  The result of
[`using()`] can be used in place of the name of a class.used as the
second parameter.

A `DAList` can be given a default object type, so that
`appendObject()` can be called without an argument.  This default
object type is controlled by the `.objectFunction` attribute.  For
example, when a `PartyList` object is created, the `.objectFunction`
attribute is set to [`Person`].

If you want greater control over the way the questions are asked, you
could add a [`generic object`] question that is specific to the
recipients that were added with `appendObject()`.  For example:

{% highlight yaml %}
generic object: Individual
question: |
  The ${ ordinal(i) } ${ x.object_name() } must have a name.  What is it?
fields:
  - First Name: x[i].name.first
  - Last Name: x[i].name.last
{% endhighlight %}

The names of the fourth and fifth recipients are capable of being
asked by this question, since the pattern `x[i]` (where `x[i]` is an
[`Individual`]) matches the intrinsic names `recipient[3]` and
`recipient[4]`.  Since the other [`generic object`] question, which
matches `x` (where `x` is an [`Individual`]) also matches `recipient[3]`
and `recipient[4]`, the order in which you list the questions in the
[YAML] file will determine which one is chosen.  Later-appearing questions
take precedence, so you would need to place the second [`generic
object`] question somewhere after the first [`generic object`] question
in order for it to be chosen.

Other methods available on a `DAList` are:

* <a name="DAList.append"></a>`append(item_to_append)` - adds
  `item_to_append` to the end of the list.  Just like the [Python
  list] method of the same name.  It takes an optional keyword
  argument `set_instance_name`.  If `set_instance_name` is `True`,
  then the object's intrinsic name will be changed to that of a member
  of the list (e.g., `my_list[2]`).  If `set_instance_name` is `False`
  (the default), then the object's instance name will not be changed.
* <a name="DAList.clear"></a><a name="DADict.clear"></a><a
  name="DASet.clear"></a>`clear()` - makes the list empty.
* <a name="DAList.sort"></a>`sort()` - reorders the elements of the
  list, saves the reordered items, and returns the object.  If you
  pass keyword parameters to `sort()`, those parameters will be passed
  directly to Python's [`sorted()`] function.

{% include side-by-side.html demo="sort" %}
  
* <a name="DAList.sort_elements"></a>`sort_elements()` - acts like
  `sort()` but does not cause the list to be gathered.
* <a name="DAList.complete_elements"></a><a
  name="DADict.complete_elements"></a>`complete_elements()` - returns
  the subset of elements in the list that are "complete."  This is
  useful when you have a list of objects, and some objects are still
  in a nascent state, and you only want to use the objects that are
  "complete."  (See the discussion of `.complete_attribute` below.)
* <a name="DAList.gathered_and_complete"></a><a
  name="DADict.gathered_and_complete"></a>`gathered_and_complete()` -
  this effectively re-runs the gathering logic on the list to make
  sure that the list is "complete."  This method is run automatically
  when editing a list item using a [`table`].  If `complete_element`
  is set to `'complete'`, this method will reset the "completeness" of
  each item before re-running the gathering logic.
* <a name="DAList.extend"></a>`extend(extension_list)` - adds the
  items in the `extension_list` to the end of the list.  Just like the
  [Python list] method of the same name.
* <a name="DAList.index"></a>`index()` - given an item that exists
  in the list, returns the index number at which the item can be
  found.
* <a name="DAList.pop"></a>`pop()` - removes an item from the list.
  Just like the [Python list] method of the same name.
* <a name="DAList.first"></a>`first()` - returns the first item of
  the list; error triggered if list is empty.
* <a name="DAList.last"></a>`last()` - returns the last item of the
  list; error triggered if list is empty.
* <a name="DAList.item"></a>`item()` - if `fruit` is a `DAList`,
  `fruit.item(2)` is equivalent to `fruit[2]`, except that if `fruit`
  does not have an item `2`, the result will be empty text.  This is
  a helpful method in some contexts, such as fillable PDF forms.
  Empty text will also result if you try to use attributes on
  the result, so `fruit.item(2).seeds` or
  `fruit.item(2).total_value()` will also result in empty text.
  
{% include side-by-side.html demo="item" %}

* <a name="DAList.does_verb"></a><a name="DADict.does_verb"></a><a
  name="DASet.does_verb"></a>`does_verb(verb)` - like the
  `verb_present()` function, except that it uses the singular or
  plural form depending on whether the list has more than one item or
  not.
* <a name="DAList.did_verb"></a><a name="DADict.did_verb"></a><a
  name="DASet.did_verb"></a>`did_verb(verb)` - like the `verb_past()`
  function, except that it uses the singular or plural form depending
  on whether the list has more than one item or not.
* <a name="DAList.as_singular_noun"></a><a
  name="DADict.as_singular_noun"></a><a
  name="DASet.as_singular_noun"></a>`as_singular_noun()` - if the
  variable name is `case.plaintiff`, returns `plaintiff`; if the
  variable name is `applicant`, returns `applicant`.
* <a name="DAList.as_noun"></a><a name="DADict.as_noun"></a><a
  name="DASet.as_noun"></a>`as_noun()` - if the variable name is
  `case.plaintiff`, returns `plaintiffs` or `plaintiff` depending on
  the number of items in the list; if the variable name is
  `applicant`, returns `applicants` or `applicant` depending on the
  number of items in the list.  You can also give this function any
  arbitrary noun and it will pluralize it or not depending on whether
  the number of items in the list is more than one.  E.g.,
  `client.child.as_noun('kid')` will return `'kid'` or `'kids'`.
* <a name="DAList.number"></a><a name="DADict.number"></a><a
  name="DASet.number"></a>`number()` - returns the total number of
  items in the list.  If necessary it will trigger questions that
  ask for all of the items of the list to be populated.
* <a name="DAList.number_as_word"></a><a
  name="DADict.number_as_word"></a><a
  name="DASet.number_as_word"></a>`number_as_word()` - same as
  `number()`, except that the [`nice_number()`] function is applied to
  the result.
* <a name="DAList.current_index"></a>`current_index()` - similar to
  `number()`, except it returns the index value of the last item in
  the list.  If there is one item in the list, `current_index()`
  returns 0.  If there are two items, it returns 1.  If there are
  no items in the list, it returns 0.  This is useful in questions
  where an iterator `i` is not available, such as question that set
  `.new_object_type`.
* <a name="DAList.remove"></a>`remove()` -
  removes the given items from the list, if they are in the list.
* <a name="DAList.comma_and_list"></a><a
  name="DADict.comma_and_list"></a><a
  name="DASet.comma_and_list"></a>`comma_and_list()` - returns the
  items of the list run through the [`comma_and_list()`] function.
* <a name="DAList.possessive"></a>`possessive()` - if the variable
  name is `plaintiff` and the target is `"fish"`, returns "plaintiff's
  fish" if there is one item in the list and "plaintiffs' fish" if
  there is more than one item in the list.
* <a name="DAList.pronoun"></a><a name="DADict.pronoun"></a><a
  name="DASet.pronoun"></a>`pronoun()` - returns a pronoun like "you,"
  "her," "him," or "them" "it", or "them," as appropriate, depending on the
  number of items in the list.
* <a name="DAList.pronoun_objective"></a><a
  name="DADict.pronoun_objective"></a><a
  name="DASet.pronoun_objective"></a>`pronoun_objective()` - for a
  `DAList`, this is the same as `pronoun()`.
* <a name="DAList.pronoun_possessive"></a><a
  name="DADict.pronoun_possessive"></a><a
  name="DASet.pronoun_possessive"></a>`pronoun_possessive()` - given a
  word like "fish," returns "her fish," "his fish," or "their fish,"
  as appropriate, depending on the number of items in the list.
* <a name="DAList.pronoun_subjective"></a><a
  name="DADict.pronoun_subjective"></a><a
  name="DASet.pronoun_subjective"></a>`pronoun_subjective()` - returns
  a pronoun like "you," "she," "he," or "they" as appropriate,
  depending on the number of items in the list.
* <a name="DAList.union"></a><a
  name="DADict.union"></a>`union(other_set)` - returns a [Python set]
  consisting of the items of current list, considered as a set,
  combined with the items of the `other_set`.
* <a name="DAList.intersection"></a><a
  name="DADict.intersection"></a>`intersection(other_set)` - returns a
  [Python set] consisting of the items of the current list, considered
  as a set, that also exist in the `other_set`.
* <a name="DAList.difference"></a><a
  name="DADict.difference"></a>`difference(other_set)` - returns a
  [Python set] consisting of the items of the current list, considered
  as a set, that do not exist in the `other_set`.
* <a name="DAList.isdisjoint"></a><a
  name="DADict.isdisjoint"></a>`isdisjoint(other_set)` - returns
  `True` if no items overlap between the current list, considered as a
  set, and the `other_set`.  Otherwise, returns `False`.
* <a name="DAList.issubset"></a><a
  name="DADict.issubset"></a>`issubset(other_set)` - returns `True` if
  the current list, considered as a set, is a subset of the
  `other_set`.  Otherwise, returns `False`.
* <a name="DAList.issuperset"></a><a
  name="DADict.issuperset"></a>`issuperset(other_set)` - returns
  `True` if the `other_set` is a subset of the current list,
  considered as a set.  Otherwise, returns `False`.
* <a name="DAList.gather"></a><a name="DADict.gather"></a><a
  name="DASet.gather"></a>`gather()` - causes the items of the list
  to be gathered and named.  Returns `True`.
* <a name="DAList.reset_gathered"></a><a name="DADict.reset_gathered"></a><a
  name="DASet.reset_gathered"></a>`reset_gathered()` - causes the
  list to be considered not-yet-gathered.  This can be used to query
  the user to add items to a list that may already be considered
  complete.  If called with the optional keyword argument `recursive`
  set to `True` (the default is `False`), the lists inside the list
  are also marked as not-yet-gathered.
* <a name="DAList.has_been_gathered"></a><a name="DADict.has_been_gathered"></a>
  <a name="DASet.has_been_gathered"></a>`has_been_gathered()` - returns
  `True` if the group has been gathered yet.  Does not trigger the
  gathering process.
* <a name="DAList.add_action"></a><a
  name="DADict.add_action"></a>`add_action()` - returns HTML for a
  button that adds a new item to the list.  This will set up a queue
  of actions for the user that will ensure that a new item will be
  added and its elements gathered.  See the [groups] section for
  details of how [`DAList`] and [`DADict`] gathering works.  By
  default, the text of the button is "Add an item" if the list is
  empty, and "Add another" if the list is non-empty.  The message can
  be overridden with the optional keyword parameter `message`.  The
  `message` passes through the [`word()`] function, so you can use the
  translation system to handle different languages.  If you set the
  optional keyword parameter `url_only` to `True`, the method will
  return only the URL for the action, not the HTML for a button.
* <a name="DAList.item_actions"></a><a
  name="DADict.item_actions"></a>`item_actions()` - returns HTML for "Edit" and
  "Delete" buttons.  This method is primarily used internally; there
  are specifiers for the [`table`] that control it.  It takes two
  positional parameters: the item itself (`the_group[the_index]`) and
  its index (`the_index`).  It also accepts optional keyword
  parameters.  If `edit` is false, the edit button is not shown.  If
  `delete` is false, the delete button is not shown.  If
  `edit_url_only` is true, a plain URL for the edit action is
  returned, rather than HTML.  If `delete_url_only` is true, a plain
  URL for the delete action is returned, rather than HTML.
* <a name="DAList.filter"></a> - returns a shallow copy of the list
  object where the elements of the list are filtered according to
  criteria specified in keyword arguments.  For example, if `person`
  is a list of [`Individual`]s, and each individual has an attribute
  `is_witness` that is either `True` if the person is a witness and
  `False` otherwise, you can write `person.filter(is_witness=True)` to
  get a list of witnesses.  This only works if the list is a list of
  objects.  By default, the list that is returned will have the same
  instance name as the original list, but you can change this by
  passing a single positional parameter.  Running `witness =
  person.filter('witness', is_witness=True)`, for example, will set
  `witness` to an object with the instance name `witness`.  However,
  note that the instance names of the elements of the list will not be
  changed.  While the `filter()` method can be a useful shorthand, its
  features are very limited.  In most situations, it is probably
  better to use a [list comprehension].

If you refer to a list in a [Mako] template (e.g., `The applicants
include: ${ applicant }`) or convert it to text with the
[str() function] (e.g. (`str(applicant)`) in [Python] code, the result
will be the output of the `comma_and_list()` method.

The `DAList` uses the following attributes:

* <a name="object_type"></a>`object_type`: a class of type
  [`DAObject`] or subclass thereof, or `None`.  Initially, this is set
  to `None`.  If set to an object type, such as `DAObject` or
  `Individual`, then new items will be created as objects of this
  type.  You can also use the result of the [`using()`] method here.
* `gathered`: a boolean value, initially undefined.  It is set to
  `True` when all of the items of the list are defined.
* `elements`: a [Python list] containing the items of the list.  If
  this is set, the list will be considered gathered as soon as it is
  initialized.
* `set_instance_name`: this can be used in combination with
  `elements`.  If set to `True`, then when the `elements` are added to
  the list, their instrinsic names ([see above](#DAObject)) are
  changed to match the intrinsic name of the list.  For example, if
  you initialize `parties` as a `DAList` using `elements=[plaintiff,
  defendant]` and `set_instance_name=True`, then the name of
  `plaintiff` will be changed to `parties[0]` and the name of
  `defendant` will be changed to `parties[0]`.  The variables
  `plaintiff` and `defendant` will still exist, but if your interview
  refers to an undefined attribute `plaintiff.net_worth`, the
  interview will seek a definition of `parties[0].net_worth`.
* `are_there_any`: a boolean value, initially undefined, indicating
  whether any values should be gathered.  The expectation is that the
  interview will define a [question] or [code block] that defines this
  attribute.
* `is_there_another`: a boolean value, initially undefined, indicating
  whether there are any additional values that should be gathered.
* `auto_gather`: a boolean value, set to `True` by default, which
  indicates whether the interview should use the `.gather()` method to
  ask questions to gather the items of the list.
* `complete_attribute`: a text string indicating the name of an
  attribute of a list item.  If you have a [`DAList`] called
  `fruit` and you set `fruit.complete_attribute = 'weight'`, then
  when the `.gather()` method is gathering the items of the list, it
  will seek a definition of `fruit[i].weight` for every item of the
  list, as it is gathering the items of the list.  If you do not set a
  `complete_attribute`, the default behavior is to ask whatever
  questions are necessary to represent the list item as text.  See
  [using `complete_attribute`] for more information.
* `ask_object_type`: a boolean value, initially set to `False`.  This
  is used when you want to build a list of objects of diverse types.
  When `ask_object_type` is `True`, then when items are added to the
  list, **docassemble** will seek out a definition of the
  `new_object_type` attribute before adding an item to the list.  When
  it gets the object type, the object it adds to the list will be of
  this type.
* `new_object_type`: this works like `object_type`, except the
  attribute is undefined and a definition is sought every time an
  object is added to the list.  It is used in conjunction with the
  `ask_object_type` attribute.

For more information about gathering items using [`DAList`] objects,
see the section on [groups].

## <a name="DADict"></a><a name="DADict.initializeObject"></a>DADict

A `DADict` acts like a [Python dictionary] except that dictionary keys
and values can be defined through **docassemble** questions.

To add a value that is a new **docassemble** object, you need to call
the `initializeObject()` method.

For example:

{% include side-by-side.html demo="dadict" %}

The first parameter is the name of the attribute.  The second
parameter is the type of object.  The result of [`using()`] can be
used in place of the class name.

<a name="DADict.new"></a><a name="FinancialList.new"></a><a
name="PeriodicFinancialList.new"></a>The `DADict` also uses a similar
method called `.new()`.  This method initializes a new object and
makes it an entry in the dictionary.  For example, if the dictionary
is called `positions`, calling `positions.new('file clerk',
'supervisor')` will result in the creation of the object
`positions['file clerk']` and the object `positions['supervisor']`.
The type of object is given by the [`object_type`] attribute, or
[`DAObject`] if [`object_type`] is not set.  You can also pass a
[list] and it will unpack the list, initializing dictionary entries
for each value.

`DADict`s use the same attributes that [`DAList`]s use.  It also uses:

* `new_item_name`: a text value, initially undefined, indicating the
key of a new item being gathered into the dictionary.
* `new_item_value`: a value, initially undefined, indicating the value
of a new item being gathered into the dictionary.  This is only used
when the `.object_type` of the [`DADict`] is not set.

`DADict`s use the same methods that [`DAList`]s use, except for
`.appendObject()`, `.append()`, `.remove()`, `.discard()`,
`.extend()`, `.first()`, and `.last()`.

It also uses the following methods, which correspond with the same
methods of the [Python dict].

* <a name="DADict.keys"></a>`keys()`
* <a name="DADict.values"></a>`values()`
* <a name="DADict.update"></a>`update()`
* <a name="DADict.pop"></a>`pop()`
* <a name="DADict.popitem"></a>`popitem()`
* <a name="DADict.setdefault"></a>`setdefault()`
* <a name="DADict.get"></a>`get()`
* <a name="DADict.copy"></a>`copy()`
* <a name="DADict.has_key"></a>`has_key()`
* <a name="DADict.items"></a>`items()`
* <a name="DADict.iteritems"></a>`iteritems()`
* <a name="DADict.iterkeys"></a>`iterkeys()`
* <a name="DADict.itervalues"></a>`itervalues()`

For most purposes, your code can treat a `DADict` object just like a
[Python dictionary].

{% highlight yaml %}
objects:
  things: DADict
---
code: |
  if 'abc' in things:
    gathered_abc = True
  else:
    gathered_abc = False
---
code: |
  if len(things) > 0:
    there_are_things = True
  else:
    there_are_things = False
---
mandatory: True
code: |
  things['abc'] = some_variable
---
code: |
  description = ''
  for key, value in things.iteritems():
    description += "* " + key + ": " + value + "\n"
{% endhighlight %}

<a name="DADict.all_true"></a><a name="DADict.all_false"></a><a name="DADict.any_true"></a><a name="DADict.any_false"></a>The
[`DADict`] object also uses some methods that are unique to it.  The
`all_true()` and `all_false()` methods are useful when working with
[checkbox groups].  If you use `datatype: checkboxes` to set a
variable called `choices`, then `choices` will be a [`DADict`] object.

If you call `choices.all_true()`, the result will be `True` if all of
the checkboxes were selected (i.e., all of the values of the
dictionary are `True`).  If you call `choices.any_false()`, the result
is the opposite of `choices.all_true()`.

If you call `choices.all_false()`, the result will be `True` if none
of the values were selected (i.e., all of the values of the dictionary
are `False`).  If you call `choices.any_true()`, the result is the
opposite of `choices.all_false()`.

You can also call these methods with parameters.  Calling
`choices.all_true('red', 'green')` will return `True` if the user
selected the choices for `'red'` and `'green'`.  Calling
`choices.all_true('red', 'green', exclusive=True)` will return `True`
if `'red'` and `'green'` were selected and these were the only choices
selected.

Here is an example that illustrates uses of `.all_true()`:

{% include side-by-side.html demo="all-true" %}

Here is an example that uses `.all_false()`:

{% include side-by-side.html demo="all-false" %}

<a name="DADict.true_values"></a>The method `.true_values()` will return a
[list] of keys that are `True`.

{% include side-by-side.html demo="true-values" %}

<a name="DADict.false_values"></a>Similarly, `.false_values()` will return a
[list] of keys that are `False`.

{% include side-by-side.html demo="false-values" %}

For more information about using checkboxes, see the documentation for
[checkbox groups].

<a name="DADict.item"></a>Like the [`DAList`], the [`DADict`] supports
the method `item()`.  If `Fruit` is a `DADict`, `fruit.item('apple')`
is equivalent to `fruit['apple']`, except that if `fruit` does not
have an item `'apple'`, the result will be empty text.  This is
a helpful method in some contexts, such as fillable PDF forms.
Empty text will also result if you try to use attributes on the
result, so `fruit.item('apple').seeds` or
`fruit.item('apple').total_value()` will also result in empty text.

{% include side-by-side.html demo="item-dict" %}

For more information about using [`DADict`] objects, see the section
on [groups].

## <a name="DASet"></a>DASet

A `DASet` is like a [`DADict`] and a [`DAList`], except it acts like a
[Python] "[set]."

{% highlight yaml %}
objects:
  issues: DASet
---
code: |
  if user_needs_to_apply:
    issues.add('application')
{% endhighlight %}

`DASet`s use the same methods that [`DAList`]s use, except for
`.appendObject()`, `.append()`, `.extend()`, `.first()`, and
`.last()`.  It also uses the following methods, which correspond with
the methods of the [Python set].

* <a name="DASet.add"></a>`add()`
* <a name="DASet.copy"></a>`copy()`
* <a name="DASet.discard"></a>`discard()`
* <a name="DASet.difference"></a>`difference()`
* <a name="DASet.intersection"></a>`intersection()`
* <a name="DASet.isdisjoint"></a>`isdisjoint()`
* <a name="DASet.issubset">`issubset()`
* <a name="DASet.issuperset"></a>`issuperset()`
* <a name="DASet.pop"></a>`pop()`
* <a name="DASet.remove"></a>`remove()`
* <a name="DASet.union"></a>`union()`

For more information about using [`DASet`] objects, see the section
on [groups].

## <a name="DAFile"></a>DAFile

A `DAFile` object is used to refer to a file, which might be an
uploaded file, an assembled document, or a file generated by code.  It
has the following attributes:

* `filename`: the filename (e.g., `complaint.pdf`).
* `mimetype`: the MIME type of the file.
* `extension`: the file extension (e.g., `pdf` or `rtf`).
* `number`: the internal integer number used by **docassemble** to
  keep track of documents stored on a site.  (You will likely never
  need to use this.)
* `ok`: this is `True` if the `number` has been defined, and is
  otherwise `False`.  (You will likely never need to use this,
  either.)
* `alt_text` (optional): you can set this to a textual description of
  the file.  This can be useful if the file is an image that will be
  displayed in the browser.  The `alt_text` will then be used as the
  [alt text] for the image, which helps users of screen readers.  You
  can also use the [`set_alt_text()`] and [`get_alt_text()`] methods
  to set and get this attribute.

You might work with `DAFile` objects in the following contexts:

* Your interview contains a [document upload field].  The variable
  representing the upload will be set to a [`DAFileList`] object after
  the upload has been done.  If the
  variable name is `pretty_picture`, then `pretty_picture[0]` will be
  a `DAFile` object.
* Your interview assembles a document and the document is assigned to
  a [`variable name`].  If the variable name is
  `motion_to_reconsider`, then `motion_to_reconsider` will be a
  [`DAFileCollection`] object, the attributes of which represent the
  various formats of the document.  For example,
  `motion_to_reconsider.pdf` (the `.pdf` here is an attribute, not a
  file extension) will be a `DAFile` object representing the PDF
  version of the document.
* Your interview contains code that needs to create a file.  You can
  use an [`objects`] block to create a blank [`DAFile`] object.  Then
  you would call [`.initialize()`](#DAFile.initialize) to give the
  file a name and a presence on the file system.
  
You can call [`.path()`](#DAFile.path) on a `DAFile` object to get the
actual file path.  Using the file path, can manipulate the underlying
file directly in whatever way you want.  However, the `DAFile` object
has a number of built-in methods for doing common things with files,
so it is a good idea to use the methods whenever possible.

While the `DAFile` object is saved in your [interview session
dictionary] like any other variable, the content of the file may be
stored on [Amazon S3], [Azure blob storage], or the file system,
depending on the server's configuration.  The path you obtain from
[`.path()`](#DAFile.path) might be different from one screen of your
interview to another.  You should not save the path to a variable and
expect to be able to use that variable across screens of the
interview.  Rather, you should always access the file through the
`DAFile` object, using its built-in methods (such as
[`.path()`](#DAFile.path)).  These methods contain code that
automatically accounts for the fact that the file might be stored in
the cloud.  For example, if you use [Amazon S3], then when you call
[`.path()`](#DAFile.path)), this will cause the file to be retrieved
from [Amazon S3] and placed into a temporary directory.

The methods of `DAFile` are the following:

<a name="DAFile.initialize"></a>The `.initialize()` method transforms
a fresh, uninitialized `DAFile` object (e.g., a `DAFile` object
created by the [`objects`] block) into an object that can actually be
used as a file.  The method takes the optional keyword parameters
`filename` or `extension`.  The `.initialize()` method can be used as
follows (where `myfile` is a `DAFile` object):

* `myfile.initialize(filename='image.jpg')` - `filename` will be
  `image.jpg`, `extension` will be `jpg`, `mimetype` will be
  `image/jpeg`.
* `myfile.initialize(extension='jpg')` - `filename` will be
  `file.jpg`, `extension` will be `jpg`, `mimetype` will be
  `image/jpeg`.
* `myfile.initialize()` - `filename` will be `file.txt`, `extension`
  will be `txt`, `mimetype` will be `text/plain`.

If the object has already been initialized, the `.initialize()` method
can safely be called on it, but this will only have the effect of
calling `.retrieve()` on it, and the `filename` and `extension`
parameters will not overwrite existing values.

The following example uses the [Python Imaging Library] to create a
JPEG image.

{% include side-by-side.html demo="dafile" %}

<a name="DAFile.show"></a>The `.show()` method returns markup that
displays the file as an image.  This method takes an optional keyword
argument, `width`, which can be set to, e.g., `'1in'`, `'44mm'`, or
`'20pt'`.  See [inserting images] for more information about this
markup.

In the context of a [Mako] template, writing `${ myfile }` is
equivalent to writing `${ myfile.show() }` (where `myfile` is a
`DAFile` object).

The method also takes an optional keyword argument `alt_text`, which
can be used to set the [alt text] of images that appear in the web
browser.  If an `alt_text` keyword argument is not supplied, the
`alt_text` attribute of the `DAFile` object itself will be used as the
[alt text].  If that attribute does not exist, no [alt text] will be
used.  (See the [`set_alt_text()`] and [`get_alt_text()`] methods for
more information about this attribute.)

<a name="DAFile.path"></a>The `.path()` method returns a complete file
path that you can use to read the file or write to the file.

<a name="DAFile.num_pages"></a>The `.num_pages()` method returns the
number of pages in a PDF file.  If the file is not a PDF file, it
returns 1.

<a name="DAFile.url_for"></a>The `.url_for()` method returns a URL at
which the file can be accessed.  The URL should only be used in the
context of the user's session and the user's web browser.  For
example, if you are using cloud storage as your form of
[data storage], the URL will link directly to the cloud and will
expire after an hour.  If you are not using cloud storage, the server
will only allow access to the file to the current user.

{% include side-by-side.html demo="dafile-url-for" %}

However, if you have set the `private` attribute to `False` by calling
`.set_attributes(private=False)` on the object, than the URL obtained
from `.url_for()` will be accessible to anyone, regardless of whether
they are logged in.  For more information, see
[`.set_attributes()`](#DAFile.set_attributes).

The `.url_for()` method can also be used to generate a temporary URL
where anyone who knows the URL can access the file, regardless of
whether they are logged in, regardless of whether the server uses
cloud [data storage], and regardless of whether the `private`
attribute is `True` or `False`.  To obtain such a URL, include
`temporary=True` as a keyword parameter.  By default, the URL will
expire after 30 seconds.  To extend this time, include the optional
keyword parameter `seconds`.  This example creates a URL that expires
in 60 seconds.

{% include side-by-side.html demo="dafile-url-for-temporary" %}

If you are using cloud storage, then the URLs will point directly to
the cloud provider rather than to your server.  (This has important
performance benefits.)  The links are long and technical because they
contain access codes.  By default, if a user clicks on a link, the URL
will open as an attachment, and the user may be prompted to download
the file or open it in an application; it will not open in the
browser.  If you would like the links to open in the browser, add
the keyword parameter `inline=True` to `.url_for()`.

<a name="DAFile.retrieve"></a>The `.retrieve()` command ensures that a
stored file is ready for use on the system.  Calling `.retrieve` is
necessary because if **docassemble** is configured to use [Amazon S3]
or [Azure blob storage], documents are stored in the cloud, and the
server accesses them by copying them from the cloud to the server and
then copying them back to the cloud.  If the file does not exist yet,
calling `.retrieve()` will generate an error.

<a name="DAFile.set_attributes"></a>The `.set_attributes()` command
allows you to set two characteristics of the uploaded document:

* `private`: the default value of this attribute is `True`, which
  means that other interviews and other interview sessions cannot
  access the contents of the file, even if they know the `.number`, or
  have the `DAFile` object itself, or have a URL to the file obtained
  from [`.url_for()`](#DAFile.url_for).  You will need to set the
  `private` attribute to `False` if you want other sessions or other
  users to be able to access the file.  For example, you might store
  a [`DAFile`] object in [storage] and retrieve it within other
  interviews at a later time.  The contents of the file will not be
  accessible unless you set `private` to `False`.
* `persistent`: the default value of this attribute is `False`, which
  means that the file will be deleted when the interview session is
  deleted.  Interview sessions are deleted when the user presses an
  [exit button] or an [exit command] is run.  Interview sessions are
  also deleted when the session has been [inactive for a period].  You
  can prevent the deletion of a file by setting the `persistent`
  attribute to `True`.
  
You can set these attributes with code like this:

{% highlight yaml %}
question: |
  Sign your name
signature: user_signature
---
mandatory: True
code: |
  user_signature.set_attributes(persistent=True)
{% endhighlight %}

To read the values of the attributes for a variable like
`user_signature`, refer to `user_signature.private` and
`user_signature.persistent`, which are set by
[`.retrieve()`](#DAFile.retrieve).  Setting these attributes directly
has no effect; you need to use [`.set_attributes()`] to set them.

<a name="DAFile.size_in_bytes"></a>The `.size_in_bytes()` method
returns the number of bytes in the file.

<a name="DAFile.slurp"></a>The `.slurp()` method reads the contents of
the file and returns them as a text value.

{% highlight python %}
contents = the_file.slurp()
{% endhighlight %}

By default, the `.slurp()` method attempts to automatically decode
text files using the `utf-8` encoding.  To turn off this automatic
decoding feature, call it with `.slurp(auto_decode=False)`.

<a name="DAFile.readlines"></a>The `.readlines()` method reads the
contents of the file, line-by-line, and returns the lines as a list.

{% highlight python %}
for line in the_file.readlines():
  if line.startswith('header'):
    header_line = line
{% endhighlight %}

<a name="DAFile.set_mimetype"></a>The `.set_mimetype()` method sets
the `.mimetype` and `.extension` attributes based on the given
[MIME type].

{% highlight python %}
the_file.set_mimetype('image/jpeg')
{% endhighlight %}

<a name="DAFile.write"></a>The `.write()` method takes a variable as
an argument and writes the contents of the variable to the file.

{% highlight python %}
contents = the_file.slurp()
contents = re.sub(r'swords', r'ploughshares', contents)
the_file.write(contents)
{% endhighlight %}

By default, the `.write()` method treats the contents as text and
applies the `utf-8` encoding.  However, if you want to write raw
bytes to the file, include the keyword parameter `binary=True`.

<a name="DAFile.copy_into"></a>The `.copy_into()` method overwrites
any existing contents of the file with the contents of the file given
as an argument.

{% highlight python %}
the_file.copy_into(other_file)
{% endhighlight %}

The `other_file` can be a path to a file on the system.  If
`other_file` is a [`DAFile`], [`DAFileList`], [`DAFileCollection`], or
[`DAStaticFile`], the file at `other_file.path()` will be used.

<a name="DAFile.from_url"></a>The `.from_url()` method overwrites
any existing contents of the file with the contents of the given URL.

{% highlight python %}
the_file.from_url("https://example.com/file.pdf")
{% endhighlight %}

In order to initialize a `DAFile` with contents from a remote source so that
it can be used in an interview, first declare the object:

{% highlight yaml %}
objects:
  - pdf_file: DAFile
{% endhighlight %}

Then use [`code`] to initialize the object and set the contents:

{% highlight yaml %}
code: |
  pdf_file.initialize(extension="pdf")
  pdf_file.from_url("https://example.com/the_file.pdf") 
{% endhighlight %}

<a name="DAFile.commit"></a>The `.commit()` method ensures that
changes to the file are stored permanently.  Under normal
circumstances, **docassemble** will automatically commit changes when
the interview is finished processing (i.e. right before a new screen
appears), but `.commit()` can be called to ensure that changes are
written, just in case there is an error.

{% highlight python %}
the_file.commit()
{% endhighlight %}

<a name="DAFile.make_pngs"></a>The `.make_pngs()` method can be used
on PDF files.  It creates PNG versions of the pages of the document.
In most circumstances, you will not need to use this function, because
when a user uploads a file, a process is started whereby each page of
the PDF file is converted to PNG.  However, if that process is not
started for whatever reason, for example if you are constructing files
manually, you can start the process by running `.make_pngs()`.  This
will launch background processes and wait until they are completed.

<a name="DAFile.set_alt_text"></a><a
name="DAFile.get_alt_text"></a>The `.set_alt_text()` and
`.get_alt_text()` methods can be used to set and retrieve the [alt
text] of the object, which is stored in the `.alt_text` attribute.
The `.alt_text` attribute can be accessed directly, but the methods
are useful because `.get_alt_text()` returns `None` if `.alt_text` is
not defined, and converts the attribute value to unicode if it is not
unicode.  The methods are also useful because they work on file
objects of all types, such as [`DAStaticFile`], [`DAFileList`], and
[`DAFileCollection`] objects.

{% highlight python %}
my_file.set_alt_text("A photograph of the Shanghai skyline")
the_alt_text = my_file.get_alt_text()
{% endhighlight %}

<a name="DAFile.get_pdf_fields"></a>The `.get_pdf_fields()` method
only works on PDF files.  It returns a list of fields that exist in
the PDF file.

The items in the list are tuples with five elements.  The five
elements are:

1. The name of the field.
2. The default value of the field.  If no default value is provided in
   the PDF file, this is the empty string for text fields and `'No'`
   for checkbox fields.
3. The page number on which the field appears.
4. A list of four coordinates indicating the bounding box of the field
   on the page.
5. A code indicating the type of the field.  This can be `'/Tx'`,
   `'/Btn'`, or `None`.

<a name="DAFile.get_docx_variables"></a>The `.get_docx_variables()`
method only works on DOCX files.  It returns a list of variables that
are used in Jinja2 templating in the DOCX file.

## <a name="DAFileCollection"></a>DAFileCollection

`DAFileCollection` objects are created internally by **docassemble**
in order to refer to a document assembled by an
[`attachment`]/[`attachments`] block.  When such a block features a
`variable name`, then a variable by that name will be defined as a
`DAFileCollection` object.  The object is called a "collection"
because an [`attachment`] can have multiple formats: PDF, RTF, etc.

A `DAFileCollection` object has attributes for each file type
generated (e.g., `pdf` or `rtf`), where the attributes are objects of
type [`DAFile`].

For example, if the variable `my_file` is a `DAFileCollection`,
`my_file.pdf` will be a [`DAFile`] containing the PDF version, and
`my_file.rtf` will be a [`DAFile`] containing the RTF version.

In addition, each `DAFileCollection` object also has an attribute
`.info` containing information about the attachment, such as the name,
the filename (before an extension is added), and a description.  The
`.info` attribute is a dictionary containing the following keys:

* `name` is the printable name of the document
* `filename` is the base name used to generate the filename.  If
  `filename` is `custody_complaint`, the PDF file will be `custody_complaint.pdf`.
* `description` is the description of the attachment.

The `DAFileCollection` also has some methods so that you can use it
much as you would use a `DAFile`.

<a name="DAFileCollection.url_for"></a>The `.url_for()` method returns
a URL to the first document type in the collection.  By default, this
is the PDF version, but this can be changed with the [valid formats]
modifier.

<a name="DAFileCollection.path"></a>The `.path()` method returns a
complete file path that you can use to access the first document type
in the collection.

<a name="DAFileCollection.num_pages"></a>The `.num_pages()` method
returns the total number of pages in the PDF file.  If there is no PDF
file, it returns 1.

<a name="DAFileCollection.show"></a>The `.show()` method inserts
markup that displays each file in the collection as an image, or as a
link if the file cannot be displayed as an image.  This
method takes an optional keyword argument, `width`.

The method also takes an optional keyword argument `alt_text`, which
can be used to set the [alt text] of images that appear in the web
browser.  If an `alt_text` keyword argument is not supplied,
[`get_alt_text()`] is called on the underling [`DAFile`] object to
obtain the [alt text].  If no `alt_text` is defined for the file, no
[alt text] is used.

<a name="DAFileCollection.set_alt_text"></a><a
name="DAFileCollection.set_alt_text"></a>The `DAFileCollection` object
supports the `.set_alt_text()` and `.get_alt_text()` methods.  These
work much like the [`set_alt_text()`] and [`get_alt_text()`] methods
of [`DAFile`].  Unlike a `DAFile`, however, a `DAFileCollection` does
not have a `.alt_text` attribute.  If you run `set_alt_text()` on a
[`DAFileCollection`], it is like calling `set_alt_text()` on each of
the files in the collection.  If you run `get_alt_text()` on a
`DAFileCollection`, it is like calling [`get_alt_text()`] on the first
document type in the collection.

<a name="DAFileCollection.get_pdf_fields"></a>The `.get_pdf_fields()`
returns a list of fields that exist in the PDF version of the
`DAFileCollection` object.  See [`get_pdf_fields()`] for more
information.

<a name="DAFileCollection.get_docx_variables"></a>The
`.get_docx_variables()` returns a list of variables that exist in the
Jinja2 templating of the DOCX version of the `DAFileCollection`
object.  See [`get_docx_variables()`] for more information.

## <a name="DAFileList"></a>DAFileList

A `DAFileList` is a [`DAList`], the items of which are expected to be
[`DAFile`] objects.

When a question has a field with a `datatype` for a file upload
([`datatype: file`] and [`datatype: files`]), the variable will be
defined as a `DAFileList` object containing the file or files
uploaded.  These variables can be used in much the same way that
[`DAFile`] variables can be used.

<a name="DAFileList.show"></a>The `.show()` method inserts markup that
displays each file as an image.  This method takes an optional keyword
argument, `width`.

When included in a [Mako] template, a `DAFileList` object will effectively
call `show()` on itself.

The method also takes an optional keyword argument `alt_text`, which
can be used to set the [alt text] of images that appear in the web
browser.  If an `alt_text` keyword argument is not supplied,
[`get_alt_text()`] is called on the underling [`DAFile`] object to
obtain the [alt text].  If no `alt_text` is defined for the file, no
[alt text] is used.

<a name="DAFileList.url_for"></a>The `.url_for()` method returns a URL
at which the first file in the list can be accessed.  This is useful
when working with `DAFileList` objects returned from
[`datatype: file`], when you know that the list will only have one
element in it.

<a name="DAFileList.path"></a>The `.path()` method returns a complete
file path that you can use to access the first file in the collection.

<a name="DAFileList.size_in_bytes"></a>The `.size_in_bytes()` method
returns the number of bytes in the first file in the collection.

<a name="DAFileList.slurp"></a>The `.slurp()` method reads the
contents of the first file in the collection and returns them as a
text value.

<a name="DAFileList.num_pages"></a>The `.num_pages()` method returns
the total number of pages in all PDF files in the list.  If a file is
not a PDF file, it counts as 1 page.

<a name="DAFileList.set_attributes"></a>The `.set_attributes()` method
calls [`.set_attributes()`] on each of the [`DAFile`]s in the list,
applying the same attributes to each file.  For an explanation of how
this method works, see [its documentation](#DAFile.set_attributes).

You would call the method like this:

{% highlight yaml %}
question: |
  Upload a file
fields:
  - File: the_upload
    datatype: file
---
mandatory: True
code: |
  the_upload.set_attributes(private=False)
{% endhighlight %}

<a name="DAFileList.set_alt_text"></a><a
name="DAFileList.set_alt_text"></a>The `DAFileList` object supports
the `.set_alt_text()` and `.get_alt_text()` methods.  These work much
like the [`set_alt_text()`] and [`get_alt_text()`] methods of
[`DAFile`].  Unlike a `DAFile`, however, a `DAFileList` does not have
a `.alt_text` attribute.  If you run `set_alt_text()` on a
[`DAFileList`], it is like calling `set_alt_text()` on each of the
items in the list.  If you run `get_alt_text()` on a `DAFileList`, it
is like calling [`get_alt_text()`] on the first item in the list.

<a name="DAFileList.get_pdf_fields"></a>The `.get_pdf_fields()` method
returns a list of fields that exist in the first file in the list.  If
you run `get_pdf_fields()` on a `DAFileList`, it is like calling
[`get_pdf_fields()`] on the first item in the list.  See
[`get_pdf_fields()`] for more information.

<a name="DAFileList.get_docx_variables"></a>The
`.get_docx_variables()` method returns a list of variables that exist
in the Jinja2 templating of the first file in the list.  If you run
`get_docx_variables()` on a `DAFileList`, it is like calling
[`get_docx_variables()`] on the first item in the list.  See
[`get_docx_variables()`] for more information.

## <a name="DAStaticFile"></a>DAStaticFile

A `DAStaticFile` represents a file in the "static folder" of a
package.  It has some of the same characteristics and methods of a
[`DAFile`].

It depends on one attribute, `filename`, which should be a reference
to a static file, such as:

* `coins.png` - a file in the static folder of the current package
* `docassemble.base:data/static/cow.jpg` - a file in the static folder
  of another package.
* `data/templates/application.pdf` - a file in the templates folder of
  the current package.  (Though template files are not in the static
  folder and are not normally used in the same way as static files, it
  can be useful to use the `DAStaticFile` object to refer to files in
  the templates folder.)

The `DAStaticFile` also uses the `alt_text` attribute.  If you are
using a `DAStaticFile` to insert an image into the browser, you can
set the `alt_text` attribute to the text that you want to use as the
[alt text] for the image.

The `DAStaticFile` object can be used like this:

{% include side-by-side.html demo="static-file" %}

It can also be initialized like this:

{% highlight yaml %}
objects:
  - the_icon: DAStaticFile.using(filename='coins.png')
{% endhighlight %}

It is a best practice to always include [alt text] for every image.
For an image that is purely decorative, set the [alt text] to empty
text:

{% highlight yaml %}
objects:
  - the_icon: DAStaticFile.using(filename='coins.png', alt_text='')
{% endhighlight %}

For an image that conveys substantive information, set the [alt text]
to something descriptive:

{% highlight yaml %}
objects:
  - court_photo: DAStaticFile.using(filename='county_court.jpg', alt_text='Photograph of the Fulton County Courthouse')
{% endhighlight %}

<a name="DAStaticFile.show"></a>The `.show()` method inserts markup that
displays the file as an image.  This method takes an optional keyword
argument, `width`.

The method also takes an optional keyword argument `alt_text`, which
can be used to set the [alt text] of images that appear in the web
browser.  If an `alt_text` keyword argument is not supplied, the
`alt_text` attribute of the `DAStaticFile` object itself will be used
as the [alt text].  If that attribute does not exist, no [alt text]
will be used.

When included in a [Mako] template, a `DAStaticFile` object will effectively
call `show()` on itself.

<a name="DAStaticFile.size_in_bytes"></a>The `.size_in_bytes()` method
returns the number of bytes in the file.

<a name="DAStaticFile.slurp"></a>The `.slurp()` method reads the contents of
the file and returns them as a text value.

{% highlight python %}
contents = the_file.slurp()
{% endhighlight %}

By default, the `.slurp()` method attempts to automatically decode
text files using the `utf8` encoding.  To turn off this automatic
decoding feature, call it with `.slurp(auto_decode=False)`.

<a name="DAStaticFile.url_for"></a>The `.url_for()` method returns a
URL at which the file can be accessed.

<a name="DAStaticFile.path"></a>The `.path()` method returns a complete
file path that you can use to access the file on the server.

<a name="DAStaticFile.set_alt_text"></a><a
name="DAStaticFile.set_alt_text"></a>The `DAStaticFile` object
supports the `.set_alt_text()` and `.get_alt_text()` methods.  These
work much like the [`set_alt_text()`] and [`get_alt_text()`] methods
of [`DAFile`].  Like [`DAFile`] objects, [`DAStaticFile`] objects use
the `alt_text` attribute to store the [alt text] associated with the
file.

Here is an example that shows how [`DAStaticFile`],
[`DAFileCollection`], [`DAFileList`], and [`DAFile`] objects can be
used interchangeably.

{% include side-by-side.html demo="file-types" %}

<a name="DAStaticFile.get_pdf_fields"></a>The `.get_pdf_fields()` method
only works on PDF files.  It returns a list of fields that exist in
the PDF file.  See [`get_pdf_fields()`] for more information.

<a name="DAStaticFile.get_docx_variables"></a>The
`.get_docx_variables()` method only works on DOCX files.  It returns a
list of variables that exist in the Jinja2 templating of the file.
See [`get_docx_variables()`] for more information.

## <a name="DAContext"></a>DAContext

The `DAContext` class is for context-dependent text.  When an instance
of the `DAContext` class is reduced to text, different text will be
used depending on whether the text will appear on the screen or in a
document.

The `DAContext` class is a subclass of [`DADict`].  Possible keys of the
dictionary include:

* `'question'`
* `'document'`
* `'pdf'`
* `'docx'`
* `'pandoc'`

If `favorite_fruit` is a `DAContext`, reducing it to text will return
`favorite_fruit['question']` in the context of the web application,
and `favorite_fruit['document']` in the context of document assembly.

Instead of using `'document'`, you can indicate particular values for
particular types of document assembly.  If you define
`favorite_fruit['pdf']`, its value will be used in a [`pdf template
file`] assembly instead of `favorite_fruit['document']`.

When a `DAContext` object is initialized, the positional and keyword
parameters are used to populate items in the dictionary.  If you
provide two positional parameters, the first parameter will become the
`question` and the second will become the `document`.  If you pass one
positional parameter, the parameter will become the `question`.
Keyword parameters populate items in the dictionary directly
(overriding positional parameters).

{% include demo-side-by-side.html demo="context-manual" %}

If you use a [`data`] block with [`use objects`] enabled, `DAContext`
objects will be created instead of [`DADict`] objects when the [YAML]
includes a dictionary where the keys are a non-empty subset of
`question`, `document`, `'pdf'`, `'docx'`, and `'pandoc'`.

{% include demo-side-by-side.html demo="context" %}

## <a name="DAEmail"></a>DAEmail

The [e-mail receiving] feature converts actual e-mails into objects of
type `DAEmail`.  These objects have the following attributes:

* `short`: the code that was assigned by [`interview_email()`]
  (e.g. `ugjrye`) in order to create the e-mail address to which this
  e-mail was sent (e.g. `ugjrye@help.example.com`).
* `key`: the `key` that was passed to [`interview_email()`], or `None` if no
  `key` was passed.
* `index`: the `index` that was passed to [`interview_email()`], or
  `None` if no index was passed.
* `address_owner`: the e-mail address of the user whose identity and
  privileges were being used when [`interview_email()`] was called.
  If the user was not logged in when [`interview_email()`] was called,
  this will be `None`.
* `to_address`: a [`DAEmailRecipientList`] object representing the
  recipients of the e-mail.
* `cc_address`: a [`DAEmailRecipientList`] object representing the
  "carbon copy" recipients of the e-mail.
* `from_address`: a [`DAEmailRecipient`] object representing the
  sender of the e-mail.
* `reply_to`: a [`DAEmailRecipient`] object representing the
  the [Reply-to] header of the e-mail.
* `return_path`: a [`DAEmailRecipient`] object representing the
  the [Return-path] header of the e-mail.
* `subject`: the subject line of the e-mail.
* `datetime_message`: a [`datetime`] object representing the stated date
  and time of the e-mail message.
* `datetime_received`: a [`datetime`] object representing the actual
  date and time of the message.
* `body_text`: a [`DAFile`] object referring to a file containing the
  plain text version of the e-mail.  If the e-mail did not contain a
  plain text version, `body_text` will be `None`.
* `body_html`: a [`DAFile`] object referring to a file containing the
  [HTML] version of the e-mail.  If the e-mail did not contain a
  [HTML] version, `body_html` will be `None`.
* `attachment`: an object of type [`DAFileList`] containing any
  files that were attached to the e-mail.  Each attachment is a
  [`DAFile`] object.
* `headers`: a [`DAFile`] object referring to a file containing a
  [JSON] representation of the headers of the e-mail.  The format of
  the [JSON] file is a [list], where each item in the [list] is a
  [list] with two items, the first of which is the name of the
  header (e.g., `To`, `From`), and the second item is the value.

## <a name="DAEmailRecipient"></a>DAEmailRecipient

A `DAEmailRecipient` object is used within [`DAEmail`] objects to
represent a single e-mail address and the name associated with the
e-mail address.

It has two attributes:

* `address`: the e-mail address (e.g., `fred1985@yahoo.com`).
* `name`: the name of the owner of the address (e.g., `Fred Smith`).

### <a name="DAEmailRecipient.email_address"></a>`.email_address()`

If `recipient` is a `DAEmailRecipient`, then calling
`recipient.email_address()` will return the person's name followed by
the person's e-mail address, in the standard e-mail format.  E.g.,
`'Fred Smith <fred1985@yahoo.com>'`.  If the name is not defined,
it will simply return the e-mail address (`fred1985@yahoo.com`).

You can suppress the inclusion of the person's name by setting the
optional keyword parameter `include_name` to `False`.

This method is intended to allow you to use `DAEmailRecipient` objects
in much the same way as [`Person`] objects are used when sending
e-mails with [`send_email()`].  (See the
[`.email_address()`] method for [`Person`] objects).

### <a name="DAEmailRecipient.exists"></a>`.exists()`

The `.exists()` method returns `True` if the `.address` attribute has
been defined, and `False` otherwise.

## <a name="DAEmailRecipientList"></a>DAEmailRecipientList

A `DAEmailRecipientList` is a [`DAList`] of [`DAEmailRecipient`] objects.

## <a name="DALazyTemplate"></a>DALazyTemplate

The [`template`] block allows you to store some text to a variable.
The variable will be defined as an object of the `DALazyTemplate`
class.

Objects of this type have two read-only attributes:

* `content`
* `subject`

When **docassemble** shows a [`template`], it assembles any [Mako] in
the `content` and optional `subject` attributes as the resulting text.
Note that the text may have [Markdown]<span></span> [markup] in it.

<a name="DALazyTemplate.show"></a>If a template is a variable
`disclaimer`, the content can be inserted by writing 
`${ disclaimer }`, `${ disclaimer.content }`, or 
`${ disclaimer.show() }`.  The latter method facilitates the use of
[`DALazyTemplate`]s and [`DAFile`]s interchangably. 

<a name="DALazyTemplate.subject_as_html"></a><a
name="DALazyTemplate.content_as_html"></a>If you write Python modules
that generate [HTML], you may wish to use
`disclaimer.subject_as_html()` and `disclaimer.content_as_html()`.
These methods return [HTML] instead of [Markdown].

The `DALazyTemplate` is called a "lazy" object because its `content`
and `subject` attributes are evaluated not when the object is defined,
but whenever it is displayed.  This allows you to define a template,
the content of which depends on whatever the current state of the
interview answers is, and you can re-use the template in a variety of
contexts.

For more information about using [`DALazyTemplate`]s, see the
documentation on the [`template`].  Also, see the documentation for
[`send_email()`] and [`send_sms()`].

## <a name="DATemplate"></a><a name="DATemplate.show"></a>DATemplate

The [`DATemplate`] is like the [`DALazyTemplate`], except that its
`subject` and `content` attributes are static.

## <a name="DAEmpty"></a>DAEmpty

The `DAEmpty` object is designed to stand in place of an object that
might otherwise have important attributes, but it will always return
an empty string whenever the interview tries to access its
attributes.

So if `exemption` is a `DAEmpty` object, `exemption.amount` will
return `''`, as will `exemption[2]`,
`exemption[4].authority.address.unit`, etc.

This object is used internally by the [`item()`](#DAList.item) method.
It can also be useful to use the `DAEmpty` object if you have a
template that refers to variables that you decide you don't actually
want to use.  If your interview simply sets those variables to
`DAEmpty`, your template will not trigger an error.

## <a name="DALink"></a>DALink

The `DALink` class represents a [hyperlink] to a [URL].  It has two
properties:

* `url`: the [URL] to which the link points.
* `anchor_text`: the text of the link that the user sees.

In most circumstances, it is not necessary to use a `DALink` to
represent a [hyperlink] because you can use [Markdown] to indicate a
hyperlink.  However, when you are creating a document from a [`docx
template file`], [Markdown] syntax is not available.  When a `DALink`
object is used within a [`docx template file`], an actual DOCX
hyperlink is inserted into the document.

{% include side-by-side.html demo="dalink" %}

## <a name="DARedis"></a>DARedis

The `DARedis` class facilitates the use of [Redis] for in-memory
storage.

{% include side-by-side.html demo="redis" %}

For the most part, an object of type `DARedis` functions just like an
object created through `redis.StrictRedis()` using the standard
[Python] package called [`redis`].  You can use methods like `.set()`,
`.get()`, `.delete()`, `.incr()`, etc.

However, there are three additional methods that facilitate the use of
[Redis] in the context of **docassemble** interviews.

<a name="DARedis.key"></a>The `key()` method is a convenience function
for obtaining keys that you can use as [Redis] keys in order to avoid
name collisions across interviews.  Given a key like
`'favorite_fruit'`, it returns the key with a prefix based on the
interview, like
`docassemble.food:data/questions/fruit.yml:favorite_fruit`.  You could
use `favorite_fruit` as a key, but if another interview on the system
used the same key, the interviews would interfere with one another.

<a name="DARedis.set_data"></a><a name="DARedis.get_data"></a>The 
`set_data()` and `get_data()` methods act just like the standard
methods `set()` and `get()`, except that they perform [pickling] and
unpickling.  This allows you to store and retrieve **docassemble**
objects or any type of data structure that is able to be [pickled].
The `set_data()` method takes an optional keyword argument `expire`,
which you can set to an integer representing the number of seconds
after which the data should be removed from [Redis].

{% include side-by-side.html demo="redis-data" %}

## <a name="DACloudStorage"></a>DACloudStorage

The `DACloudStorage` object allows you to access low-level
functionality of cloud storage using [Amazon S3] or [Azure blob
storage], using the [boto3] and [azure.storage.blob] libraries,
respectively.

Suppose you include the following in your interview:

{% highlight yaml %}
objects:
  - cloud: DACloudStorage
{% endhighlight %}

If you have enabled [`s3`] in your [Configuration], then:

* `cloud.conn` will return a [`boto3.resource('s3')`] object initialized
  according to the [`s3`] configuration.
* `cloud.client` will return a [`boto3.client('s3')`] object initialized
  according to the [`s3`] configuration.
* `cloud.bucket` will return a [`Bucket`] object for the bucket
  defined in the [`s3`] configuration.
* `cloud.bucket_name` will return the name of the bucket defined in
  the [`s3`] configuration.

If you have enabled [`azure`] in your [Configuration], then:

* `cloud.conn` will return a [`BlockBlobService()`] object initialized
  according to the [`azure`] configuration.
* `cloud.container_name` will return the name of the container defined
  in the [`azure`] configuration.

In some circumstances, you might not be using [`s3`] or [`azure`] for
persistent storage, or you may wish to access a different bucket or
container.  In that case, you can initialize the `DACloudStorage`
object so that it uses a different directive in the [Configuration].

For example, if you have an [S3 bucket] called `mybucket-example-com`,
and your [Configuration] contains the following:

{% highlight yaml %}
mybucket:
  access key id: AGJBRKYM3T4FY7HYWNBQ
  secret access key: BkwEQeg+yeC3EJ2MoCDwY8jbiWrtKdLf4q3++EBd
  bucket: mybucket-example-com
{% endhighlight %}

Then you can initialize a `DACloudStorage` object as follows:

{% highlight yaml %}
objects:
  - cloud: DACloudStorage.using(provider='s3', config='mybucket')
{% endhighlight %}

Then, you can use the `cloud` object to access the contents of the
`mybucket-example-com` bucket in your interview.  For example:

{% highlight yaml %}
question: |
  How to seek help
subquestion: |
  ${ cloud.bucket.Object('markdown_files/help.md').get()['Body'].read().decode('utf-8') }
{% endhighlight %}

In this example, the `subquestion` incorporates the contents of a
file called `help.md` located in the `markdown_files` folder of the
`mybucket-example-com` bucket.

For more information on how to use these objects, see the
documentation for [boto3] and [azure.storage.blob].

The `DACloudStorage` object simply provides a convenient way to obtain
an authenticated API connection to [Amazon S3] or [Azure blob
storage].  If you do not use a `DACloudStorage` object, you can still
use the [boto3] and [azure.storage.blob] packages; the only added
complication is that you have to handle authentication yourself.  You
can use the [`get_config()`] function to retrieve custom values from
your [Configuration].

For example, here is a [Python module] that defines a function that
retrieves a list of object names from an existing [S3 bucket].

{% highlight python %}
import boto3
import docassemble.base.util

s3_config = docassemble.base.util.get_config('manual s3 configuration')

def list_keys(prefix):
    conn = boto3.resource('s3', region_name='us-east-1', aws_access_key_id=s3_config['access key id'], aws_secret_access_key=s3_config['secret access key'])
    client = boto3.client('s3', region_name='us-east-1', aws_access_key_id=s3_config['access key id'], aws_secret_access_key=s3_config['secret access key'])
    bucket = conn.Bucket('example-com-data-bucket')
    output = list()
    for item in bucket.objects.filter(Prefix=prefix, Delimiter='/'):
        output.append(item.key)
    return output
{% endhighlight %}

This assumes you have a custom directive in your [Configuration] that
looks like this:

{% highlight yaml %}
manual s3 configuration:
  access key id: FWIEJFIJIDGISEJFWOEF
  secret access key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
{% endhighlight %}

## <a name="DAOAuth"></a>DAOAuth

The `DAOAuth` objects facilitates using [OAuth2] authentication in the
context of an interview.

{% include demo-side-by-side.html demo="oauth-test" %}

The user needs to be logged in because [OAuth2] credentials are stored
globally using [Redis] and they are tied to the user's e-mail address.

To use a `DAOAuth` object to connect to Google, you need to use the
[Google Developers Console] and enable the "Google Sheets API."  Under
Credentials, create an "OAuth client ID" for a "web application."
Assuming your server is at https://interview.example.com, add
`https://interview.example.com` to the "Authorized JavaScript
origins."  Then, under "Authorized redirect URIs," add
`https://interview.example.com/interview`.  Make a note of the "Client
ID" and the "Client secret" because you will need to plug those values
into the [Configuration]

The module `oauthsheets.py` contains the following:

{% highlight python %}
from docassemble.base.util import DAOAuth
from googleapiclient.discovery import build

__all__ = ['GoogleAuth']

class GoogleAuth(DAOAuth):
    def init(self, *pargs, **kwargs):
        super(GoogleAuth, self).init(*pargs, **kwargs)
        self.appname = 'mygoogle'
        self.token_uri = "https://www.googleapis.com/oauth2/v4/token"
        self.auth_uri = "https://accounts.google.com/o/oauth2/v2/auth"
        self.scope = "https://www.googleapis.com/auth/spreadsheets"
    def test(self):
        service = build('sheets', 'v4', http=self.get_http())
        SAMPLE_SPREADSHEET_ID = '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms'
        SAMPLE_RANGE_NAME = 'Class Data!A2:E'
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=SAMPLE_RANGE_NAME).execute()
        values = result.get('values', [])
        return values
{% endhighlight %}

The `GoogleAuth` class is a subclass of `DAOAuth`.  The following four
attributes must be defined:

* `appname` - This is a name that you choose.  Credentials will be
  stored based on this application name as well as the user's e-mail
  address.  In this example, the application name is `mygoogle`.
* `token_uri` - This is the URL for obtaining the [OAuth2] token.  It
  should be provided in the documentation for the [OAuth2] API.
* `auth_uri` - This is the URL for [OAuth2] authorization.  It
  should be provided in the documentation for the [OAuth2] API.
* `scope` - This is the scope of access you are requesting.  The
  format should be documented in the documentation for the [OAuth2]
  API.

Since the application name is `mygoogle`, you need to edit your
[Configuration] to add the "Client ID" and "Client secret" under the
`oauth` directive as follows:

{% highlight yaml %}
oauth:
  mygoogle:
    id: 18761224589-4t28ji14udf7pa39hd5ssqdttebt959y.apps.googleusercontent.com
    secret: UnDdE_EBOft7wYU8rmCFXTdy
{% endhighlight %}

Note that in the interview, the object was defined with
`.using(url_args=url_args)`, and that the "redirect URI" was
`/interview`.  This is all necessary because after the [OAuth2]
process, the [OAuth2] provider will redirect back to your interview
with the URL parameters `state` and `code`.  The `DAOAuth` object
needs to have a reference to the `url_args` so that it can read these
URL parameters.

If you need to modify the way this works, you can copy and paste the
code for `DAOAuth` out of [`oauth.py`] into your own module.

## <a name="DAGoogleAPI"></a>DAGoogleAPI

The `DAGoogleAPI` object provides convenient access to Google's APIs
through a Google [service account] that you set up in the [Google
Developers Console] and enable in the **docassemble** [Configuration].

The `DAGoogleAPI` object can be used with the low-level [Google API]
and also with higher-level API packages like [gspread] or the [Cloud
Translation API Client Library].

The benefit of the `DAGoogleAPI` object is that it streamlines the
process of authenticating to Google's servers.  It also provides a
standard way to keep [service account] authentication information in
the [Configuration].

### <a name="DAGoogleAPI setup"></a>Setup process

In order for your site to communicate with Google, you will need to
create an account on the [Google Developers Console] and create an
"app."  Within this app, you will need to create a [service account].
Then set the [`service account credentials`] directive in the
[Configuration] to the credentials for this [service account].  For
more information on how to do this, see the documentation for the
[`service account credentials`] directive.

Finally, you need to use the [Google Developers Console] to enable the
APIs that you want to use.  For example, if you want to use the
[Google Drive API], you need to explicitly enable the [Google Drive
API] for your app.

### <a name="DAGoogleAPI usage"></a>Usage

Suppose you define `api` to be a `DAGoogleAPI` object:

{% highlight yaml %}
objects:
  api: DAGoogleAPI
{% endhighlight %}

There are two categories of methods available.  The first is for the
low-level [Google API] available through the
[`google-api-python-client`] package.  This can be used to control any
of the [Google API]s.

* `api.api_credentials(scope)` - this returns a
  [`ServiceAccountCredentials`] object from the
  [oauth2client.service_account] library, initialized for the given `scope`.
* `api.http(scope)` - this returns an [`httplib2.Http()`] object that
  has been modified to send the appropriate credentials to Google.
* `api.drive_service()` - this returns the result
  `apiclient.discovery.build()` with the appropriate parameters for
  the [Google Drive API].

The `scope` can be a single scope like
`'https://www.googleapis.com/auth/drive'`, or it can be a list of
scopes, like `['https://www.googleapis.com/auth/cloud-platform',
'https://www.googleapis.com/auth/cloud-vision']`.  You can browse
Google's [directory of scopes].

Here is an example of a [Python module] that uses the
`.drive_service()` method of the [`DAGoogleAPI`] object to provide
convenience functions for reading and writing to a [Google Drive]
folder:

{% highlight python %}
from docassemble.base.util import DAGoogleAPI, DAFile
import apiclient

api = DAGoogleAPI()

__all__ = ['get_folder_names', 'get_files_in_folder', 'write_file_to_folder', 'download_file']

def get_folder_names():
    service = api.drive_service()
    items = list()
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and sharedWithMe").execute()
        for the_file in response.get('files', []):
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return [item['name'] for item in items]

def get_folder_id(folder_name):
    service = api.drive_service()
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType='application/vnd.google-apps.folder' and sharedWithMe and name='" + unicode(folder_name) + "'").execute()
    folder_id = None
    for item in response.get('files', []):
        folder_id = item['id']
    return folder_id

def get_file_id(filename, folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        raise Exception("The folder was not found")
    service = api.drive_service()
    file_id = None
    response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType!='application/vnd.google-apps.folder' and '" + str(folder_id) + "' in parents and name='" + unicode(filename) + "'").execute()
    for item in response.get('files', []):
        file_id = item['id']
    return file_id

def get_files_in_folder(folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        raise Exception("The folder was not found")
    service = api.drive_service()
    items = list()
    while True:
        response = service.files().list(spaces="drive", fields="nextPageToken, files(id, name)", q="mimeType!='application/vnd.google-apps.folder' and trashed=false and '" + str(folder_id) + "' in parents").execute()
        for the_file in response.get('files', []):
            items.append(the_file)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
    return [item['name'] for item in items]

def write_file_to_folder(path, mimetype, filename, folder_name):
    folder_id = get_folder_id(folder_name)
    if folder_id is None:
        raise Exception("The folder was not found")
    service = api.drive_service()
    file_metadata = { 'name': filename, 'parents': [folder_id] }
    media = apiclient.http.MediaFileUpload(path, mimetype=mimetype)
    the_new_file = service.files().create(body=file_metadata,
                                          media_body=media,
                                          fields='id').execute()
    return the_new_file.get('id')

def download_file(filename, folder_name):
    file_id = get_file_id(filename, folder_name)
    if file_id is None:
        raise Exception("The file was not found")
    the_file = DAFile()
    the_file.set_random_instance_name()
    the_file.initialize(filename=filename)
    service = api.drive_service()
    with open(the_file.path(), 'wb') as fh:
        response = service.files().get_media(fileId=file_id)
        downloader = apiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
    the_file.commit()
    return the_file
{% endhighlight %}

To use this module, log in to [Google Drive] using a normal Google
account and create a folder.  Then share that folder with the e-mail
address of your [service account].  Then, when you call
`get_folder_names()`, the name of this folder will be part of the list
that is returned.

Here is an interview that uses this module to access a [Google Drive]
folder called "DADemo".  It assumes the module is a file called
`google_drive.py` in the same package as the interview.

{% highlight yaml %}
modules:
  - .google_drive
---
mandatory: True
code: |
  first_screen
  files_copied_to_google_drive
  final_screen
---
question: |
  Files in your Google Drive
subquestion: |
  % for item in get_files_in_folder('DADemo'):
  * ${ item } ${ download_file(item, 'DADemo') }
  % endfor
field: first_screen
---
question: |
  Please upload a file.
fields:
  - File: uploaded_files
    datatype: files
---
code: |
  for the_file in uploaded_files:
    (path, mimetype) = path_and_mimetype(the_file)
    write_file_to_folder(path, mimetype, the_file.filename, 'DADemo')
  files_copied_to_google_drive = True
---
event: final_screen
question: Names of files in folder
subquestion: |
  % for item in get_files_in_folder('DADemo'):
  * ${ item }
  % endfor
{% endhighlight %}

You can use any [Google API], not just the [Google Drive API].  The
`.drive_service()` method is provided only as a convenience.  You can
create your own services by running something like:

{% highlight python %}
import apiclient
import docassemble.base.util 

api = docassemble.base.util.DAGoogleAPI()
http = api.http('https://www.googleapis.com/auth/cloud-translation')

service = apiclient.discovery.build('translate', 'v2', http=http)
{% endhighlight %}

Note that while the `api` object can safely persist in your users'
[interview session dictionary], a variable like `service` cannot be
[pickled], so if you store it in your interview file, you will get an
error.  Ideally, you should always use Python modules for functions
that access APIs, so that there is no danger of an error if
**docassemble** tries to pickle an object that cannot be pickled.

The second category of methods is for [Google Cloud packages] like
[`google.cloud.storage`] and [`google.cloud.translate`].  If a Google
service is available both through [`google-api-python-client`] and
through one of the [Google Cloud packages], the [Google Cloud
packages] are probably preferable because they are newer and
easier to use.  Most of these packages are not installed in the
**docassemble** system by default and will need to be installed with
"Package Management" if you want to use them.  Whatever package name
Google tells you to use with `pip`, you can type into the "Package on
PyPI" field in "Package Management."

The methods of the [`DAGoogleAPI`] object that can be used with the
[Google Cloud packages] include the following:

* `api.cloud_credentials(scope)` - this returns a
  [`Credentials`] object from the
  [google.oauth2.service_account] module, initialized for the given
  `scope`.
* `api.project_id()` - this returns the ID of the "app" in which the
  [service account] is configured.  This ID, which is just a text
  string, is required by some API methods.
* `google_cloud_storage_client()` - this returns a
  `google.cloud.storage.Client` object that can be used to access the
  [Google Cloud Storage] API.

Here is an example of a [Python module] that uses the [Google Cloud
Storage] API (the [`google.cloud.storage`] Python package):

{% highlight python %}
import docassemble.base.util

__all__ = ['make_bucket', 'get_bucket', 'make_blob']

api = docassemble.base.util.DAGoogleAPI()
client = api.google_cloud_storage_client()

def make_bucket(bucket_name):
  return client.create_bucket(bucket_name)
  
def get_bucket(bucket_name):
  return client.get_bucket(bucket_name)

def make_blob(bucket_name, blob_name, blob_content):
  bucket = get_bucket(bucket_name)
  blob = bucket.blob(blob_name)
  blob.upload_from_string(blob_content)
  return blob
{% endhighlight %}

# <a name="person classes"></a>Classes for information about people and things

## <a name="Thing"></a>Thing

If `pet_rock` is a `Thing`, it will be an object with one attribute:

* `pet_rock.name` (object of class [`Name`])

If you include `${ pet_rock }` in text, the name of the `Thing` will
be inserted.  **docassemble** will look for a definition of
`pet_rock.name.text`.

If you set the `name` attribute of a `Thing` to text, the
`.name.text` attribute will be set to the text you provided.

## <a name="Event"></a>Event

An `Event` is a type of [`DAObject`] with the following attributes
initialized by default:

* `address`: an [`Address`] object
* `location`: a [`LatitudeLongitude`] object

There may be many other attributes you want to use for an `Event`, but
they are up to you to choose.

## <a name="Person"></a>Person

The `Person` class encompasses [`Individual`]s as well as legal persons,
like companies, government agencies, etc.  If you create an object of
type `Person` by doing:

{% highlight yaml %}
objects:
  - opponent: Person
{% endhighlight %}

then you will create an object with the following built-in attributes:

* `opponent.name` (object of class [`Name`])
* `opponent.address` (object of class [`Address`])
* `opponent.location` (object of class [`LatitudeLongitude`])

Referring to a `Person` in the context of a [Mako] template will
return the output of `.name.full()`.

If you set the `name` attribute of a `Person` to text, the
`.name.text` attribute will be set to the text you provided.

The following attributes are also used, but undefined by default:

* `email` (see [`.email_address()`] and [`send_email()`])
* `phone_number` (see [`.sms_number()`] and [`send_sms()`] )
* `mobile_number` (see [`.sms_number()`] and [`send_sms()`])
* `uses_whatsapp` (see [`.sms_number()`] and [`send_sms()`])

The following methods can be used:

### <a name="Person.possessive"></a>`.possessive()`

Calling `defendant.possessive('fish')` returns "ABC Corporation's fish" or
"your fish" depending on whether `defendant` is the user.
  
### <a name="Person.identified"></a>`.identified()`

Calling `defendant.identified()` returns `True` if `defendant.name.text`
has been defined.  The
[version for `Individual`s](#Individual.identified)
is different.

### <a name="Person.pronoun_objective"></a>`.pronoun_objective()`

Calling `defendant.pronoun_objective()` returns "it," while calling
`defendant.pronoun_objective(capitalize=True)` returns "It."

### <a name="Person.object_possessive"></a>`.object_possessive()`

Calling `defendant.object_possessive('fish')` returns "defendant's
fish."

### <a name="Person.is_are_you"></a>`.is_are_you()`

Calling `defendant.is_are_you()` returns "are you" if `defendant` is
the user, and otherwise returns "is defendant."  Calling
`defendant.is_are_you(capitalize=True)` returns "Are you" or "Is
defendant."

### <a name="Person.is_user"></a>`.is_user()`

Calling `defendant.is_user()` returns `True` if the `defendant` is the
user, and otherwise returns `False`.

### <a name="Person.address_block"></a>`.address_block()`

Calling `defendant.address_block()` will return the name followed by
the address, in a format suitable for inclusion in a document.  For example:

{% highlight text %}
[FLUSHLEFT] ABC Corporation [NEWLINE] 1500 Market Street [NEWLINE] Philadelphia, PA 19102
{% endhighlight %}

See [markup] for more information about how this will appear in documents.

### <a name="Person.do_question"></a>`.do_question()`

Calling `defendant.do_question('testify')` returns "do you testify" if
the defendant is the user, or otherwise it uses the defendant's name,
as in "does ABC Corporation testify."

### <a name="Person.did_question"></a>`.did_question()`

Calling `defendant.did_question('testify')` returns "did you testify" if
the defendant is the user, or otherwise it uses the defendant's name,
as in "did ABC Corporation testify."

### <a name="Person.were_question"></a>`.were_question()`

Calling `defendant.were_question('guilty')` returns "were you guilty" if
the defendant is the user, or otherwise it uses the defendant's name,
as in "was ABC Corporation guilty."

### <a name="Person.have_question"></a>`.have_question()`

Calling `defendant.have_question('lied')` returns "have you lied" if
the defendant is the user, or otherwise it uses the defendant's name,
as in "has ABC Corporation lied."

### <a name="Person.does_verb"></a>`.does_verb()`

Calling `defendant.does_verb('testify')` returns "testify" if the
defendant is the user, but otherwise returns "testifies."  The method
accepts the optional keyword arguments `present` and `past`, which are
expected to be set to `True` or `False`.  For example,
`defendant.does_verb('testify', past=True)` will return "testified."

### <a name="Person.did_verb"></a>`.did_verb()`

The `.did_verb()` method is like the
[`.does_verb()`](#Person.does_verb) method, except that it conjugates
the verb into the past tense.

### <a name="Person.subject"></a>`.subject()`

The `.subject()` method returns "you" if the person is the user, but
otherwise returns the person's name.

### <a name="Person.email_address"></a>`.email_address()`

Calling `defendant.email_address()` will return the person's name
followed by the person's e-mail address, in the standard e-mail
format.  E.g., `'ABC Corporation <info@abc.com>'`.  If the name is not
yet defined, the e-mail address by itself (`info@abc.com`) will be
returned.

If you want to force **docassemble** to ask for the recipient's name,
set the optional keyword parameter `include_name` to `True`.

You can suppress the inclusion of the person's name by setting
`include_name` to `False`.

### <a name="Person.sms_number"></a>`.sms_number()`

Calling `defendant.sms_number()` will return `defendant.mobile_number`
if the `.mobile_number` attribute exists; it will not cause
the question to be asked.  If the `.mobile_number` attribute does not
exist, it will use `defendant.phone_number`.

The method formats the phone number in [E.164] format.  It will make
use of `defendant.country` to format the phone number, since the
[E.164] format contains the international [country calling code] of
the phone number.  If the `.country` attribute is not defined,
`.address.country` will be tried, but if that is not defined either,
the method will call [`get_country()`].  The country is expected to be
a two-letter, capitalized abbreviation of a country ([ISO 3166-1
alpha-2] format).

If a `mobile_number` attribute exists and a `uses_whatsapp` number
also exists and is `True`, then [WhatsApp] will be used to send messages
to the number.

### <a name="Organization"></a>Organization

An `Organization` is a subclass of [`Person`].  It has the attribute
`.office`, which is an object of type [`OfficeList`].

It uses the following attributes, which by default are not defined:

* `handles`: refers to a list of problems the organization handles.
* `serves`: refers to a list of counties the organization serves.

<a name="Organization.will_handle"></a>The `.will_handle()` method
returns `True` or `False` depending on whether the organization serves
a given county or handles a given problem.  It takes two optional
keyword arguments: `problem` and `county`.  For example, you could
call `agency.will_handle(problem='Divorce', county='Hampshire County')`.

### <a name="Individual"></a>Individual

The `Individual` is a subclass of [`Person`].  This class should be used
for persons who you know are human beings.

If you create an object of type `Individual` by doing:

{% highlight yaml %}
objects:
  - president: Individual
{% endhighlight %}

then you will create an object with the following built-in attribute:

* `president.name` (object of class [`IndividualName`])

In addition, the following attributes will be defined by virtue of an
`Individual` being a kind of [`Person`]:

* `president.address` (object of class [`Address`])
* `president.location` (object of class [`LatitudeLongitude`])

The following attributes are also used, but undefined by default:

* <a name="Individual.age"></a>`age` - this can be set to a number.
  It is used by the [`age_in_years()`] method.
* <a name="Individual.birthdate"></a>`birthdate` - this can be the
  result of a [date field], or a [`datetime`] object.  It is used by
  the [`age_in_years()`] method if the [`age`] attribute has not been
  defined.
* <a name="Individual.gender"></a>`gender` - this should be set to
  `'male'`, `'female'`, or `'other'`.  It is used by a variety of
  methods such as [`pronoun()`].

<a name="set_info"></a>A number of useful methods can be applied to
objects of class `Individual`.  Many of them will respond differently
depending on whether the `Individual` is the user or not.  If you use
these methods, be sure to inform **docassemble** who the user is by
inserting the following [initial block]:

{% highlight yaml %}
initial: True
code: |
  set_info(user=client)
{% endhighlight %}

(If you include the [`basic-questions.yml`] file, this is done for
you.) See the documentation for the [`set_info()`] function for more
information.

### <a name="Individual.identified"></a>`.identified()`

Returns `True` if the individual's name has been defined yet,
otherwise it returns `False`.

### <a name="Individual.age_in_years"></a>`.age_in_years()`

`user.age_in_years()` the `user`'s age in years as a whole number.

There are two optional arguments that modify the method's behavior:

* `user.age_in_years(decimals=True)` returns the user's age in years
  with the fractional part included.
* `user.age_in_years(as_of="5/1/2015")` returns the user's age as of a
  particular date.

To determine the user's age, this method first looks to see if there
is an attribute [`age`].  If there is, the value of this attribute is
returned.  However, the `age_in_years()` method will not cause the
interview to seek out this attribute.

If the [`age`] attribute is not defined, this method will calculate
the individual's age based on the [`birthdate`] attribute, which will
be interpreted as a date.  The [`birthdate`] attribute can be a date
expressed in text, as it would be if it was defined by a [date field],
or it can be a [`datetime`] object.

### <a name="Individual.first_name_hint"></a><a name="Individual.last_name_hint"></a>`.first_name_hint()` and `.last_name_hint()`

When you are writing questions in an interview, you may find yourself
in this position:

* You are asking for the name of a person;
* That person whose name you need may be the user;
* The user may be logged in;
* The user, if logged in, may have already provided his or her name on
the user profile page; and
* It would be repetitive for the user to retype his or her
name.

In this situation, it would be convenient for the user if the user's
name was auto-filled on the page.  The `.first_name_hint()` and
`.last_name_hint()` methods accomplish this for you.  You can ask for
an individual's name as follows:

{% highlight yaml %}
generic object: Individual
question: |
  What is ${ x.object_possessive('name') }?
fields:
  - First Name: x.name.first
    default: ${ x.first_name_hint() }
  - Middle Name: x.name.middle
    required: False
  - Last Name: x.name.last
    default: ${ x.last_name_hint() }
  - Suffix: x.name.suffix
    required: False
    code: |
      name_suffix()
{% endhighlight %}

For an explanation of how [`.object_possessive()`] works, see the
[`Person`] class.

### <a name="Individual.possessive"></a>`.possessive()`

If the individual's name is "Adam Smith," this returns "Adam Smith's."
 But if the individual is the current user, this returns "your."  (See
 the [note above].)

### <a name="Individual.salutation"></a>`.salutation()`

Depending on the `gender` attribute, the `.salutation()` method
returns "Mr." or "Ms."  This can be helpful when writing letters.

{% include side-by-side.html demo="salutation" %}

The function takes some optional keyword arguments:

* `client.salutation()` returns `Mr.`
* `client.salutation(with_name=True)` returns `Mr. Jones`
* `client.salutation(with_name_and_punctuation=True)` returns `Mr. Jones:`

This function relies on a few attributes, which it looks for but does
not assume exist:

* <a name="Individual.salutation_to_use"></a>If `.salutation_to_use`
  is set, `.salutation()` uses its value as the salutation instead of
  `'Mr.'` or `'Ms.'`.
* <a name="Individual.is_doctor"></a>If `.is_doctor` is set to a true
  value, the salutation "Dr." is used.
* <a name="Individual.is_judge"></a>If `.is_judge` is set to a true
  value, the salutation "Judge" is used.
* If `.name.suffix` is `'MD'` or `'PhD'`, the salutation "Dr." is used.
* If `.name.suffix` is `'J'`, the salutation "Judge" is used.
* <a name="Individual.is_friendly"></a>If `.is_friendly` is set to a
  true value, a comma will be used in place of a colon when
  `with_name_and_punctuation` is true.

The operation of this function can be customized with
[`docassemble.base.util.update_language_function()`].  Use the
function name `'salutation'` and provide a function that takes an
object of class [`Individual`] as an argument.  For reference, here is
the default function (from [`docassemble.base.functions`]):

{% highlight python %}
def salutation_default(indiv, with_name=False, with_name_and_punctuation=False):
    """Returns Mr., Ms., etc. for an individual."""
    used_gender = False
    if hasattr(indiv, 'salutation_to_use') and indiv.salutation_to_use is not None:
        salut = indiv.salutation_to_use
    elif hasattr(indiv, 'is_doctor') and indiv.is_doctor:
        salut = 'Dr.'
    elif hasattr(indiv, 'is_judge') and indiv.is_judge:
        salut = 'Judge'
    elif hasattr(indiv, 'name') and hasattr(indiv.name, 'suffix') and indiv.name.suffix in ('MD', 'PhD'):
        salut = 'Dr.'
    elif hasattr(indiv, 'name') and hasattr(indiv.name, 'suffix') and indiv.name.suffix == 'J':
        salut = 'Judge'
    elif indiv.gender == 'female':
        used_gender = True
        salut = 'Ms.'
    else:
        used_gender = True
        salut = 'Mr.'
    if with_name_and_punctuation or with_name:
        if used_gender and indiv.gender not in ('male', 'female'):
            salut_and_name = indiv.name.full()
        else:
            salut_and_name = salut + ' ' + indiv.name.last
        if with_name_and_punctuation:
            if hasattr(indiv, 'is_friendly') and indiv.is_friendly:
                punct = ','
            else:
                punct = ':'
            return salut_and_name + punct
        elif with_name:
            return salut_and_name
    return salut
{% endhighlight %}

If you wanted a simpler function, you could include something like
this in a [Python] module that you include in your interview:

{% highlight python %}
def my_salutation(indiv):
    if indiv.is_powerful:
        return "Your excellency"
    else:
        return "Hey you"

docassemble.base.util.update_language_function('*', 'salutation', my_salutation)
{% endhighlight %}

### <a name="Individual.pronoun_possessive"></a>`.pronoun_possessive()`

If the individual is `client`, then
`client.pronoun_possessive('fish')` returns "your fish," "his fish,"
"her fish," or "their fish" depending on whether `client` is the user (see the
[note above]) and depending on the value of `client.gender`.
`client.pronoun_possessive('fish', capitalize=True)` returns "Your
fish," "His fish," "Her fish," or "Their fish."

If you want to refer to the individual in the third person even if the
individual is the user, write `client.pronoun_possessive('fish',
third_person=True)`.

For portability to different languages, this method requires you to
provide the noun you are modifying.  In some languages, the possessive
pronoun may be different depending on what the noun is.

### <a name="Individual.pronoun"></a>`.pronoun()`

Returns "you," "him," "her," or "them," depending on whether the individual is
the user (see the [note above]) and depending on the value of the
`gender` attribute.  If called with `capitalize=True`, the word will
be capitalized (for use at the beginning of a sentence).

### <a name="Individual.pronoun_objective"></a>`.pronoun_objective()`

For the `Individual` class, `pronoun_objective()` does the same thing
as `pronoun`.  (Other classes returns "it.")  If called with
`capitalize=True`, the output will be capitalized.

### <a name="Individual.pronoun_subjective"></a>`.pronoun_subjective()`

Returns "you," "he," "she," or "they," depending on whether the individual is
the user (see the [note above]) and depending on the value of the
`gender` attribute.

You can call this method with the following optional keyword arguments:

* `third_person=True`: will use "he" or "she" even if the individual
is the user.
* `capitalize=True`: the output will be capitalized (for use at the
  beginning of a sentence)

### <a name="Individual.yourself_or_name"></a>`.yourself_or_name()`

Returns "yourself" if the individual is the user (see the [note
above]), but otherwise returns the person's name.  If called with the
optional keyword argument `capitalize=True`, the output will be
capitalized.

## <a name="Name"></a>Name

The `Name` is the base class for names of things, such as [`Person`].
For example, if `plaintiff` is a [`Person`], `plaintiff.name` is an
object of type `Name`.  If `plaintiff` is an [`Individual`],
`plaintiff.name` is an object of type [`IndividualName`], which is a
subtype of `Name`.  (The [`IndividualName`] is defined in the next
section.)

Objects of the basic [`Name`] class have just one attribute, `text`.
To set the name of a [`Person`] called `company`, for example, you can
do something like this:

{% include side-by-side.html demo="name-company-question" %}

There are multiple ways to refer to the name of an object, but the
best way is to write something like this:

{% include side-by-side.html demo="name-company" %}

Multiple ways of referring to the name of a [`Person`] are illustrated
in the following interview:

{% include side-by-side.html demo="name" %}

Note that `${ opponent.name.full() }`, `${ opponent.name }`, and `${
opponent }` all return the same thing.  This is because a [`Person`]
in the context of a [Mako] template returns `.name.full()`, and a
[`Name`] returns `.full()`.

The reason a name is not just a piece of text, but rather an object
with attributes like `text` and methods like `.full()`, is that some
objects have names with multiple parts that you will want to express
in multiple ways.  You might have a list of parties in a case, where
the parties can be companies or individuals.  It helps to have a
common way of referring to the names of these objects.

<a name="Name.full"></a>
<a name="Name.firstlast"></a>
<a name="Name.lastfirst"></a>
The [`Name`] and [`IndividualName`] objects support the following methods:

* `.full()`
* `.firstlast()`
* `.lastfirst()`

Applied to an [`IndividualName`] object, these methods return different
useful expressions of the name.  Applied to a [`Name`] object, these
methods all return the same thing -- the `.text` attribute.  This is
useful because you can write things like this, which lists the names
of the parties in a bullet-point list:

{% include side-by-side.html demo="lastfirst" %}

In this template, the developer does not need to worry about which
parties are companies and which parties are individuals; the name will
be listed in the bullet-point list in an appropriate way.  For
individuals, the last name will come first, but for non-individuals,
the regular name will be printed.

<a name="Name.defined"></a>
The [`Name`] and [`IndividualName`] objects also support the method:

* `.defined()`

This returns `True` if the necessary component of the name (`.text`
for a [`Name`], `first` for an [`IndividualName`]) has been defined yet.
Otherwise it returns `False`.

### <a name="IndividualName"></a>IndividualName

The [`Individual`] class is a subclass of [`Person`].  It defines the
`name` attribute as an `IndividualName` rather than a [`Name`].  An
`IndividualName` uses the following attributes, which are expected to
be text:

* `first`
* `middle`
* `last`
* `suffix`

In the context of a [Mako] template, a reference to an `IndividualName` on
its own will return `.full()`.

The `full()` method attempts to form a full name from these
components.  Only `first` is required, however.  This means that if
you refer to an `IndividualName` in a [Mako] template, e.g., by
writing `${ applicant.name }`, **docassemble** will attempt to return
`applicant.name.full()`, and if `applicant.name.first` has not been
defined yet, **docassemble** will look for a question that defines
`applicant.name.first`.

Here is how `full()` and other methods of the `IndividualName` work:

* <a name="IndividualName.full"></a>`applicant.full()`: "John Q. Adams"
* `applicant.full(middle="full")`: "John Quincy Adams"
* <a name="IndividualName.firstlast"></a>`applicant.firstlast()`: "John Adams"
* <a name="IndividualName.lastfirst"></a>`applicant.lastfirst()`: "Adams, John"
* <a name="IndividualName.defined"></a>`applicant.defined()`: Returns
  `True` if the `.first` attribute has been defined yet. 

The `IndividualName` also uses the attribute `.uses_parts`, which is
`True` by default.  If `.uses_parts` is set to `False`, then the
methods of the object fall back on the methods of [`Name`], and the
individual's name is stored in the attribute `.text`.

If you set the `name` attribute of an `Individual` to text, the
`.uses_parts` attribute will be set to `False` and `.name.text` will
be set to the text you provided.

## <a name="Address"></a>Address

An `Address` has the following text attributes:

* `address`: e.g., "123 Main Street"
* `unit`: e.g., "Suite 100"
* `city`: e.g., "Springfield"
* `state`: e.g., "MA"
* `zip`: e.g. "01199"
* `country`: e.g., 'US' ([ISO 3166-1 alpha-2] format)
* `city_only`: defaults to `False`.  See [`City`], below.

It also has an attribute `location`, which is a [`LatitudeLongitude`]
object representing the GPS coordinates of the address.

If you refer to an address in a [Mako] template, it returns `.block()`.

<a name="Address.block"></a> The `.block()` method returns a formatted
address.  The attribute `city` is needed.

<a name="Address.formatted_unit"></a> The `.formatted_unit()` method
returns the `.unit` attribute (or the `.floor` or `.room`) attributes,
formatted appropriately.  For example, if the `unit` attribute is
`'2000'`, this will return `'Unit 2000'`.  But if the `unit` attribute
is `'Suite 2000'`, this method will return `'Suite 2000'`.  By
default, if the `.unit` attribute is not defined, this method will
return `''`.  However, if it is called as
`.formatted_unit(require=True)` and neither `.unit` nor `.floor` nor
`.room` is defined, it will seek the definition of the `unit`
attribute.

<a name="Address.geolocate"></a> The `.geolocate()` method determines
the latitude and longitude of the address and stores it in the
attribute `location`, which is a [`LatitudeLongitude`] object.  It
uses the [`geopy.geocoders.GoogleV3`] class.  To use this, you will
need an API key for the [Google Maps Geocoding API], which you will
need to add to the [configuration] as the [`api key`] subdirective
under the [`google`] directive.

If you call `.geolocate()` on an [`Address`] object called
`myaddress`, the following attributes will be set:

* `myaddress.geolocated`: this will be set to `True`.  Since the
  `.geolocate()` method uses an API, it is important not to call the
  API repeatedly.  The `.geolocated` attribute keeps track of whether
  the `.geolocate()` method has been called before.  If it has been
  called before, and `.geolocated` is `True`, then calling
  `.geolocate()` again will not call the API again; rather, it will
  immediately return with whatever result was obtained the first time
  `.geolocate()` was called.
* `myaddress.geolocate_success`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to
  `True`; otherwise, this will be set to `False`.
* `myaddress.location.gathered`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to `True`.
* `myaddress.location.known`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to
  `True`.
* `myaddress.location.latitude`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to the
  latitude of the address.
* `myaddress.location.longitude`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to the
  latitude of the address.
* `myaddress.location.description`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to the
  value of `myaddress.block()`.
* `myaddress.geolocate_response`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to the
  raw results returned from the [Google Maps Geocoding API].
* `myaddress.one_line`: if `.geolocate()` was able to
  successfully call the API and get a result, this will be set to the
  address as the geocoder would format it to be expressed on one
  line.
* `myaddress.norm`: if `.geolocate()` was able to successfully call
  the API and get a result, this will be set to an [`Address`] object
  containing normalized names of the address components.
* `myaddress.norm_long`: if `.geolocate()` was able to successfully
  call the API and get a result, this will be set to an [`Address`]
  object containing long-form normalized names of the address
  components.  (E.g., "1234 Main Street" instead of "1234 Main St" and
  "California" instead of "CA.")

In addition, the following attributes will be set if the attribute was
not already set, and if `.geolocate()` was able to successfully
determine the value by calling the API:

* `myaddress.street_number` - the street number (e.g., `123`).
* `myaddress.street` - the street name (e.g., `Main St`).
* `myaddress.city` - the city (known as (`locality`).
* `myaddress.county` - the county (known as `administrative_area_level_2`).
* `myaddress.state` - the state (known as `administrative_area_level_1`).
* `myaddress.zip` - the Zip code (known as `postal_code`).
* `myaddress.country` - the country (e.g., `US`) in [ISO 3166-1 alpha-2] format.

In addition, the following attributes will be set to the "long" form
of the values returned from the [Google Maps Geocoding API], if applicable:

* `myaddress.administrative_area_level_1`
* `myaddress.administrative_area_level_2`
* `myaddress.administrative_area_level_3`
* `myaddress.administrative_area_level_4`
* `myaddress.administrative_area_level_5`
* `myaddress.colloquial_area`
* `myaddress.floor`
* `myaddress.intersection`
* `myaddress.locality`
* `myaddress.neighborhood`
* `myaddress.post_box`
* `myaddress.postal_code`
* `myaddress.postal_code_prefix`
* `myaddress.postal_code_suffix`
* `myaddress.postal_town`
* `myaddress.premise`
* `myaddress.room`
* `myaddress.route`
* `myaddress.sublocality`
* `myaddress.sublocality_level_1`
* `myaddress.sublocality_level_2`
* `myaddress.sublocality_level_3`
* `myaddress.sublocality_level_4`
* `myaddress.sublocality_level_5`
* `myaddress.subpremise`

Here is an example that illustrates how the `.geolocate()` method works:

{% include side-by-side.html demo="geolocate" %}

There is a also a second use of the `geolocate()` method, which is to
populate the attributes of an empty `Address` object using an address
expressed as one line of text:

{% include side-by-side.html demo="geolocate-from-address" %}

If this is used on an `Address` that already has populated attributes,
the attributes of the existing address will be overwritten.

<a name="Address.normalize"></a>
The `.normalize()` method uses the results of `.geolocate()` to
standardize the formatting of the parts of the address.  This will
overwrite the attributes of the object.  This method takes an optional
keyword parameter `long_format`, which defaults to `False`.  If this
parameter is `True`, the address will be normalized using the long
form of the normalization.  (E.g., "California" instead of "CA.")

{% include side-by-side.html demo="normalize" %}

Note that if you want to access a normalized version of the address,
but you don't want to overwrite the original attributes of the object,
you can simply run `.geolocate()` and then, if it is successful,
access the `.norm` attribute or the `.norm_long` attribute, both of
which will be fully populated [`Address`] objects, with normalized
attributes.

<a name="Address.line_one"></a>
The `.line_one()` method returns the first line of the address,
including the unit, if the unit is defined.

<a name="Address.line_two"></a>
The `.line_two()` method returns the second line of the address,
consisting of the city, state, and zip code.

<a name="Address.on_one_line"></a>
The `.on_one_line()` method returns the address, consisting of
the city, state, and zip code, as a single line of text.

It takes two optional keyword parameters:

* `include_unit` - Default value is `False`.  Set to `True` if you want
  the unit number to be included.
* `omit_default_country` - Default value is `True`.  Set to `False` if
  you want the country to be included.  Normally, the country is
  included only if it is different from the default country.

### <a name="address autocomplete"></a>Address autocomplete

If you have defined a [`google maps api key`] in the [Configuration],
you can use the [Place Autocomplete] feature of the [Google Places
API] to help your users enter addresses.  Address suggestions will be
provided as the user begins to type.  To use this feature, modify the
street address (`.address`) field by setting `address autocomplete` to
`True`.  Then, when the user selects an address, the other components
of the address will be filled in with the values obtained from Google.
This will only work if the address components are part of the same
`Address` object.  For example, if the street address field is
`client.address.address`, the other fields must be called
`client.address.city`, `client.address.state`, etc.  You do not need
to include all of these attributes; any attributes not included in the
front end of the page will be ignored.

For this feature to work, your [`google maps api key`] will need to be
associated with an app for which the following APIs are enabled:

* Google Places API Web Service
* Google Maps JavaScript API

Here is an example that illustrates how the address autocomplete
feature works:

{% include side-by-side.html demo="address-autocomplete" %}

### <a name="City"></a>City

A `City` is a type of `Address` for which the attribute `.city_only`
is set to `True`.  Functions that display the address will only
display the city, the state, and (if set) the zip code.

## <a name="LatitudeLongitude"></a>LatitudeLongitude

A `LatitudeLongitude` object represents the GPS coordinates of an
address or location.  `LatitudeLongitude` objects have the following
attributes:

* `latitude`: the latitude of the location.
* `longitude`: the longitude of the location.
* `description`: a textual description of the location.
* `known`: whether the GPS location is known yet.
* `gathered`: whether a determination of the GPS location has been
attempted yet.

One use for the `LatitudeLongitude` object is for mapping the
coordinates of an address.  The [`Address`] object has a method
`.geolocate()` for this purpose.

<a name="LatitudeLongitude.status"></a>
Another use for the `LatitudeLongitude` object is storing the GPS
location of the user's device.  Many web browsers, particularly those
on mobile devices, have a feature for determining the user's GPS
coordinates.  Usually the browser asks the user to consent to the
sharing of the location information.  To support this feature, the
`LatitudeLongitude` object offers the method `.status()`.

The following example shows how to gather the user's latitude and
longitude from the web browser.

{% highlight yaml %}
include:
  - basic-questions.yml
---
initial: True
code: |
  track_location = user.location.status()
{% endhighlight %}

Alternatively, if you do not want to include all of the questions and
code blocks of the [`basic-questions.yml`] file in your interview, you
can do:

{% highlight yaml %}
objects:
  - user: Individual
---
initial: True
code: |
  set_info(user=user, role='user_role')
  track_location = user.location.status()
{% endhighlight %}

If all goes well, the user's latitude and longitude will be gathered
and stored in `user.location.latitude` and `user.location.longitude`.
You can control when this happens in the interview by controlling when
`track_location` is set.  For example, you may wish to prepare the
user for this:

{% highlight yaml %}
initial: True
code: |
  set_info(user=user, role='user_role')
  if user_ok_with_sharing_location:
    track_location = user.location.status()
---
question: |
  We would like to gather information about your current location
  from your mobile device.  Is that ok with you?
yesno: user_ok_with_sharing_location
{% endhighlight %}

[`track_location`] is a [special variable] that tells **docassemble**
whether or not it should ask the browser for the user's GPS
coordinates the next time a question is posed to the user.  If
[`track_location`] is `True`, **docassemble** will ask the browser to
provide the information, and if it receives it, it will make it
available for retrieval through the [`user_lat_lon()`] function.

The `.status()` method looks to see if a latitude and longitude were
provided by the browser, or in the alternative that an error message
was provided, such as "the user refused to share the information," or
"this device cannot determine the user's location."  If the latitude
and longitude information is conveyed, `.status()` stores the
information in `user.location.latitude` and `user.location.longitude`.
The `.status()` method returns `False` in these situations, which
means "we already asked for the latitude and longitude and got a
response, so there is no longer any need for the browser to keep
asking for it."  Otherwise, it returns `True`, which means "the
browser has not yet been asked for the location information, so let's
ask it."

# <a name="currencyclasses"></a>Classes for currency

## <a name="Value"></a>Value

A `Value` is a subclass of [`DAObject`] that is intended to represent a
currency value that may or may not need to be asked for in an interview.

For example, suppose you want to have a variable that represents the
value of the user's real estate holdings.  But before you ask the
value of the user's real estate holdings, you will want to ask if the
user has real estate holdings at all.

A `Value` has two attributes, both of which are initially undefined:

* `.value`: intended to be a number
* `.exists`: a boolean value representing whether the value is applicable

The `.exists` attribute facilitates asking questions about values
using two screens: first, ask whether the value exists at all, then
ask for the value.  For example:

{% include side-by-side.html demo="exists" %}

The [`FinancialList`] object, explained below, represents a list of
`Value`s.  When computing a total of the values (with `.total()`), it
checks the `.exists` attributes of each `Value` to be defined.  This
causes questions to be asked about whether the `Value` is applicable
to the user's situation before the value itself is requested.

<a name="Value.amount"></a>To access the value of a `Value` object,
you can use the `.amount()` method.  If the `.exists` attribute is
`False`, it will return zero without asking for the `.value`.

Referring to a `Value` in a [Mako] template will show the `.amount()`.  The
value of `.amount()` is also returned when you pass a `Value` to the
[`currency()`] function.  For example:

{% highlight yaml %}
question: |
  The value of your real estate holdings is
  ${ currency(real_estate_holdings) }.
  
  An identical way of writing this number is 
  ${ currency(real_estate_holdings.amount()) }.
{% endhighlight %}

### <a name="PeriodicValue"></a>PeriodicValue

A `PeriodicValue` is a [`Value`] that has an additional attribute,
`period`, which is a number representing the number of times per year
the value applies.

{% include side-by-side.html demo="periodic-value" %}

<a name="PeriodicValue.amount"></a>To access the value of a
`PeriodicValue` object, you can use the `.amount()` method.  If the
`.exists` attribute is `False`, it will return zero without asking for
the `.value`.  By default, it returns the value for the period 1
(e.g., in the example above, period of 1 represents a year).  That is,
it will return the `.value` multiplied by the `.period`.

Referring to a `PeriodicValue` in a [Mako] template will show the
`.amount()`.  The value of `.amount()` is also returned when you pass
a `PeriodicValue` to the [`currency()`] function.

# <a name="listclasses"></a>Classes for lists of things

## <a name="PartyList"></a>PartyList

This is a subclass of [`DAList`].

It is indended to contain a list of [`Person`]s (or [`Individual`]s,
which are a type of [`Person`]) who are parties to a case.

## <a name="ChildList"></a>ChildList

This is a subclass of [`DAList`].

It is indended to contain a list of [`Individual`]s who are children.

## <a name="FinancialList"></a>FinancialList

The `FinancialList` is intended to collect a set of financial items,
such as an individual's assets.  It is a [`DADict`] object with an
[`object_type`] of [`Value`].  The `exists` attribute of each
[`Value`] item is set by default to `True`.

The `FinancialList` has three methods:

* <a name="FinancialList.total"></a>`.total()`: tallies up the total
  value of all `Value`s in the list for which the `exists` attribute
  is `True`.  A reference to `.total()` will cause **docassemble** to
  ask the questions necessary to gather the full list of items.
* <a name="FinancialList.existing_items"></a>`.existing_items()`:
  returns a list of types of amounts that exist within the financial
  list.

In the context of a [Mako] template, a `FinancialList` returns the result of
`.total()`.

### <a name="Asset"></a>Asset

This is a subclass of [`FinancialList`] that is intended to be used to
track assets.

Here is some example code that triggers questions that ask about asset
items.

{% include side-by-side.html demo="assets" %}

## <a name="PeriodicFinancialList"></a>PeriodicFinancialList

This is a subclass of [`FinancialList`] intended to collect a set of
financial items that have a periodic nature, such as an individual's
income.  Instead of each item being a [`Value`], each item is a
[`PeriodicValue`].

The `PeriodicFinancialList` has the following method:

* <a name="PeriodicFinancialList.total"></a>`.total()`: tallies up the
  total annual value of all [`PeriodicValue`]s in the list for which the
  `exists` attribute is `True`.

If you have a `PeriodicFinancialList` called `income`, you can have a
single question that asks for the item name for a new item, and also
the value and period of the new item.  Just write a question that sets
these three attributes:

* `income.new_item_name`
* `income.new_item_value`
* `income.new_item_period`

In the context of a [Mako] template, a `PeriodicFinancialList` returns `.total()`.

### <a name="Income"></a>Income

This is a subclass of [`PeriodicFinancialList`] with no special
properties except the name.

### <a name="Expense"></a>Expense

`Expense` is a [`PeriodicFinancialList`] representing a person's
expenses.  It has no special properties except the name.

## <a name="OfficeList"></a>OfficeList

An `OfficeList` object is a type of [`DAList`], the items of which are
expected to be [`Address`] objects.  It is used in [`Organization`]
objects.

# <a name="specialclasses"></a>Classes for special purposes

## <a name="RoleChangeTracker"></a>RoleChangeTracker

The `RoleChangeTracker` class is provided to facilitate [multi-user
interviews] with **docassemble**'s [roles] system.  It facilitates
sending e-mails to the participants to let them know when the
interview needs their attention.  It keeps track of when these e-mails
have been sent to make sure that duplicative e-mails are not sent.

It has one method:

* <a name="RoleChangeTracker.send_email"></a>`role_change.send_email()`
  (not to be confused with the `send_email()` function)

Here is an example that demonstrates its use:

{% highlight yaml %}
objects:
  - client: Individual
  - advocate: Individual
  - role_change: RoleChangeTracker
---
default role: client
code: |
  if user_logged_in() and \
      advocate.attribute_defined('email') and \
      advocate.email == user_info().email:
    user = advocate
    role = 'advocate'
  else:
    user = client
    role = 'client'
  set_info(user=user, role=role)
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
{% endhighlight %}

The `send_email()` method's first argument is the special variable
`role_needed`, a [Python list] that **docassemble** defines internally
whenever there is a mismatch between the current user's role and the
role required by a question that needs to be asked.

The remaining arguments to `send_email()` are [keyword arguments],
where each keyword is the name of a possible role.  Each
[keyword argument] must be a [Python dictionary] containing the
following keys:

* `to`: this needs to be a [`Person`] (or a subclass, like
[`Individual`]).  The person's `email` attribute is expected to be
defined.
* `email`: this needs to a [`DATemplate`] containing the subject and
body of the e-mail that will be sent.

# <a name="DAObject.using"></a>Special object method `using()`

If you wanted to initialize the variable `possession` as a [`DAList`]
of [`Thing`]s, you could write

{% highlight yaml %}
objects:
  - possession: DAList
---
mandatory: True
code: |
  possession.object_type = Thing
{% endhighlight %}

The [`DAObject`] class has a special object method, `using()`, which
can be used to accomplish the same thing in a more compact way, so
that you could instead write:

{% highlight yaml %}
objects:
  - possession: DAList.using(object_type=Thing)
{% endhighlight %}

You can use `using()` when indicating an `object_type`:

{% highlight yaml %}
objects:
  - client: Individual
  - possession: DAList.using(object_type=Thing.using(owner=client))
{% endhighlight %}

The result of this will be that `possession` is a [`DAList`] of
[`Thing`]s, and each item in the list will be initialized so that the
`owner` attribute is set to `client` by default.

The result of `.using()` can be used in a number of contexts,
including [`objects`] initial blocks, as a parameter in the methods
[`initializeAttribute()`], [`reInitializeAttribute()`],
[`appendObject()`], and [`gather()`], or as the [`object_type`]
attribute of a [`DAList`] or [`DADict`].

# <a name="instanceName"></a>How docassemble objects are different

For most purposes, **docassemble** objects behave just like [Python]
objects.  However, they have special properties that facilitate the
automatic asking of questions.  You may need to be mindful of these
special properties if you do anything fancy in your code.

In contrast to [Python objects] in general, **docassemble** objects
are aware of their first-given names.  All **docassemble** objects
have an `.instanceName` attribute.  So if you do:

{% highlight yaml %}
objects:
  - user: Individual
{% endhighlight %}

then `user.instanceName` will be `'user'`, and
`user.name.instanceName` will be `'user.name'`.

You can also initialize `user` in standard [Python] fashion:

{% highlight yaml %}
code: |
  user = Individual()
{% endhighlight %}

In this circumstance, **docassemble** uses some [magic] to set
`.instanceName` to `user`.  However, the magic has its limits.  For
example, the following does not work:

{% highlight yaml %}
code: |
  (user, advocate) = (Individual(), Individual())
{% endhighlight %}

If you ever get an error message in **docassemble** referring to
variables with a name like `qjAMyvGQYnyK`, and you are sure you did
not create such a variable, then you have an object that was unable to
determine its given name.

If you want to initialize objects using expressions more complicated
than `variable_name = ObjectName()`, you can -- you just need to
include the variable name as an argument to the object name.  For
example:

{% highlight yaml %}
code: |
  (user, advocate) = (Individual('user'), Individual('advocate'))
{% endhighlight %}

Attribute initialization does not have this limitation.

Always keep in mind that objects are given `.instanceName` attributes
as early as possible, and once an `.instanceName` is assigned, it will
not be overwritten unless you explicitly overwrite it.  For example,
if you do:

{% highlight yaml %}
code: |
  user.name = IndividualName()
{% endhighlight %}

then `user.name.instanceName` will return `'user.name'`, as you would
expect.  But if you do:

{% highlight yaml %}
code: |
  cool_name = IndividualName()
  cool_name.first = 'Groovy'
  cool_name.last = 'Jones'
---
code: |
  user.name = cool_name()
{% endhighlight %}

then `user.name.instanceName` will be `'cool_name'`, not `'user.name'`.

You can manually correct this:

{% highlight yaml %}
code: |
  user.name = cool_name()
  user.name.instanceName = 'user.name'
{% endhighlight %}

The `.instanceName` is not simply an internal attribute; it is used by
the [`.object_possessive()`] method to refer to the object in
human-readable format.

# <a name="writing"></a>Writing your own classes

If you know how to write your own [Python] code, it is pretty easy
to write your own classes.

For example, you could create your own [package] for interviews
related to cooking.

You would start by using the [package system] to create a
**docassemble** package called `cooking`, the full name of which would
be `docassemble.cooking` (interview packages are subpackages of the
`docassemble` namespace package).

You would create a module file within this package called
`objects.py`.  If you are using the [Playground], you would create
this file in the [Modules folder] of the [Playground].  Otherwise, you
would create this file in the `docassemble/cooking` directory in your
package.  You would set the contents of `objects.py` to the following:

{% highlight python %}
from docassemble.base.util import DAObject

class Recipe(DAObject):
    def summary(self):
        return "#### Ingredients\n\n" + self.ingredients + "\n\n#### Instructions\n\n" + self.instructions
{% endhighlight %}

Your class `Recipe` needs to "inherit" from the basic **docassemble**
object called [`DAObject`].  If you did not do this, **docassemble**
would not be able to ask questions to define attributes of `Recipe`
objects.

The purpose of the `summary()` method is to summarize the contents of
the recipe.  It makes use of the attributes `ingredients` and
`instructions`.

If you are not familiar with [Python], `\n` inside quotation marks
indicates a line break and `+` in the context of text indicates that
the text should be strung together.  In [Markdown], `####` at the
start of a line indicates that the line is a section name.

You can use your class in an interview like this:

{% include demo-side-by-side.html demo="testcooking" %}

Note that the [`modules`] block refers to `.objects`, which is a
[relative module name].  The `.` at the beginning means "in the
current package."  You could also have written
`docassemble.cooking.objects`.  The [relative module name] works so
long as the interview file is in the same package as the module.

By the way, there is way to write the `summary()` method that is more
friendly to other interview developers:

{% highlight python %}
from docassemble.base.util import DAObject, word

class Recipe(DAObject):
    def summary(self):
        return "#### " + word('Ingredients') + "\n\n" + self.ingredients + "\n\n#### " + word('Instructions') + "\n\n" + self.instructions
{% endhighlight %}

If you use the [`word()`] function in this way, interview developers will
be able to translate the "cooking" interview from English to another
language without having to edit your code.  All they would need to do
is include the words `Ingredients` and `Instructions` in a translation
[YAML] file referenced in a [`words`] directive in the **docassemble**
[configuration].

## <a name="ownclassattributes"></a>Initializing object attributes

In the example above, all the attributes of the `Recipe` object were
plain text values.  What if you want attributes of your objects to be
objects themselves?

Suppose you want the `ingredients` attribute to be a [`DAList`].

There are several ways that `ingredients` can be initialized.  In the
interview itself, you can do:

{% highlight yaml %}
modules:
  - docassemble.cooking
---
objects:
  - dinner: Recipe
  - dinner.ingredients: DAList
{% endhighlight %}

Or, you could use [`sets`] in combination with [`initializeAttribute()`]:

{% highlight yaml %}
modules:
  - docassemble.cooking
---
objects:
  - dinner: Recipe
---
generic object: Recipe
sets: x.ingredients
code: |
  x.initializeAttribute('ingredients', DAList)
{% endhighlight %}

However, it is often cleaner to put the object initialization into the
class definition itself:

{% highlight python %}
class Recipe(DAObject):
    def init(self, *pargs, **kwargs):
        self.initializeAttribute('ingredients', DAList)
        super(Recipe, self).init(*pargs, **kwargs)
{% endhighlight %}

Then, you would only need to write this in your interview file:

{% highlight yaml %}
objects:
  - dinner: Recipe
{% endhighlight %}

<a name="DAObject.init"></a>The `init()` function is a special
function that is called on all [`DAObject`] objects at the time they
are initialized.  This is not to be confused with the `__init__()`
function, which is built in to [Python]; you should use `init()`, not
`__init__()`.

When you write your own `init()` function for a class, you should (but
are not required to) include the `super(Recipe, self).init(*pargs,
**kwargs)` line.  This will ensure that `Recipe` objects are
initialized properly.  For example, if you wrote:

{% highlight python %}
dinner.initializeAttribute('recipe', Recipe, oven_temperature=300)
{% endhighlight %}

then `dinner.recipe` would be a `Recipe` object and
`dinner.recipe.oven_temperature` would be `300`.  However, if you
included an `init()` function and failed to include `super(Recipe,
self).init(*pargs, **kwargs)`, then the `oven_temperature` variable
would not be set.  Therefore, it is a good practice to always write
your `init()` methods in this way.

Before you use objects and [inheritance], you should buy a [Python
book] and learn how [Python] handles object orientation.  Object
oriented programming is an advanced topic and **docassemble**
documentation is not a substitute for [Python] documentation.

## <a name="usingglob"></a>Using global variables in your classes

Normally in [Python] you can use global variables to keep track of
information that your methods need to know but that is not passed in
arguments to the methods.  For example, if you wanted to keep track of
whether to use Celsius or Fahrenheit when talking about temperatures,
you might be tempted to write:

{% highlight python %}
from docassemble.base.util import DAObject

temperature_type = 'Celsius'

class Recipe(DAObject):
    def summary(self):
        return "#### Ingredients\n\n" + self.ingredients + "\n\n#### Instructions\n\n" + self.instructions
    def get_oven_temperature(self):
        if temperature_type == 'Celsius':
            return str(self.oven_temperature) + ' °C'
        elif temperature_type == 'Fahrenheit':
            return str(self.oven_temperature) + ' °F'
        elif temperature_type == 'Kelvin': 
            return str(self.oven_temperature) + ' K'
{% endhighlight %}

(The `str()` function is a Python function that converts something to
text.  Here, it is necessary because `self.oven_temperature` may be a
number, and [Python] will complain if you ask it to "add" text to a
number.)

Then to change the `temperature_type` from an interview, you might
write:

{% highlight yaml %}
modules:
  - docassemble.cooking.objects
---
initial: True
code: |
  if user_is_scientist:
    temperature_type = 'Kelvin'
  elif user_country in ['United States', 'Great Britain']:
    temperature_type = 'Fahrenheit'
{% endhighlight %}

This would be effective at changing the `temperature_type` variable
because the `modules` block loads all the names from
`docassemble.cooking.objects` into the [namespace] of the interview,
including `temperature_type`.

However, this is not [thread-safe] and it will not work correctly 100%
of the time.  If your server is under heavy load, users might randomly
be advised to turn their ovens to 350 degrees Celsius, which would
scorch the food.  This is because the variable `temperature_type`
exists at the level of the web server process, and the process might
be supporting several users simultaneously (in different "threads" of
the process).  Between the time one user sets `temperature_type` to
`Fahrenheit` and tries to use it, another user inside the same process
might set `temperature_type` to `Celsius`.

Therefore, it is important that you do not use global variables when
you write your own classes.  The simplest way to get around this
problem is to use the [`set_info()`] and [`get_info()`] functions from
[`docassemble.base.util`]:

{% highlight python %}
from docassemble.base.util import DAObject, get_info

class Recipe(DAObject):
    def summary(self):
        return "#### Ingredients\n\n" + self.ingredients + "\n\n#### Instructions\n\n" + self.instructions
    def get_oven_temperature(self):
        if get_info('temperature_type') == 'Celsius':
            return str(self.oven_temperature) + ' °C'
        elif get_info('temperature_type') == 'Fahrenheit':
            return str(self.oven_temperature) + ' °F'
        elif get_info('temperature_type') == 'Kelvin': 
            return str(self.oven_temperature) + ' K'
{% endhighlight %}

Then from your interview you can run [`set_info()`] in [`initial`]
code:

{% highlight yaml %}
modules:
  - docassemble.cooking.objects
---
initial: True
code: |
  if user_is_scientist:
    set_info(temperature_type='Kelvin')
  elif user_country in ['United States', 'Great Britain']:
    set_info(temperature_type='Fahrenheit')
  else:
    set_info(temperature_type='Celsius')
{% endhighlight %}

The values set by [`set_info()`] are forgotten after the user's screen
is prepared.  Therefore, it is necessary to run [`set_info()`] in an
[`initial`] code block so that values like `temperature_type` are put
in place before they are needed.

If you are an advanced programmer, you can do what
[`docassemble.base.util`] does and use Python's [threading module] to
store global variables.

{% highlight python %}
from docassemble.base.util import DAObject
import threading

__all__ = ['set_temperature_type', 'get_temperature_type', 'Recipe']

this_thread = threading.local

def set_temperature_type(type):
    this_thread.temperature_type = type

def get_temperature_type():
    return this_thread.temperature_type

class Recipe(DAObject):
    def summary(self):
        return "#### Ingredients\n\n" + self.ingredients + "\n\n#### Instructions\n\n" + self.instructions
    def get_oven_temperature(self):
        if this_thread.temperature_type == 'Celsius':
            return str(self.oven_temperature) + ' °C'
        elif this_thread.temperature_type == 'Fahrenheit':
            return str(self.oven_temperature) + ' °F'
        elif this_thread.temperature_type == 'Kelvin': 
            return str(self.oven_temperature) + ' K'
{% endhighlight %}

We added an `__all__` statement so that a `module` block including
`docassemble.cooking.objects` does not clutter the [namespace] with
extraneous names like `threading`.  We also added functions for
setting and retrieving the value of the "temperature type."

The temperature type is now an attribute of the object `this_thread`,
which is an instance of `threading.local`.  This attribute needs to be
set in `initial` code that will run every time a screen refreshes.

Now in your interview you can do:

{% highlight yaml %}
modules:
  - docassemble.cooking.objects
---
initial: True
code: |
  if user_is_scientist:
    set_temperature_type('Kelvin')
  elif user_country in ['United States', 'Great Britain']:
    set_temperature_type('Fahrenheit')
  else:
    set_temperature_type('Celsius')
{% endhighlight %}

Note that you do not need to worry about whether your global variables
are [thread-safe] if they do not change from interview to interview.

For example, if you only wanted to allow people to change the
temperature type from the **docassemble** [configuration], you could
do the following in your [Python module]:

{% highlight python %}
from docassemble.base.util import DAObject

from docassemble.webapp.config import daconfig
temperature_type = daconfig.get('temperature type', 'Celsius')
{% endhighlight %}

Then your interviews would not have to do anything with `temperature_type`.

Also, you could avoid the complication of global variables entirely if
you are willing to pass the temperature type as an argument to
`get_oven_temperature`:

{% highlight python %}
from docassemble.base.util import DAObject

class Recipe(DAObject):
    def get_oven_temperature(self, type):
        if type == 'Celsius':
            return str(self.oven_temperature) + ' °C'
        elif type == 'Fahrenheit':
            return str(self.oven_temperature) + ' °F'
        elif type == 'Kelvin': 
            return str(self.oven_temperature) + ' K'
{% endhighlight %}

Then you could have this in your interview:

{% highlight yaml %}
question: |
  What kind of temperature system do you use?
choices:
  - Celsius
  - Fahrenheit
  - Kelvin
field: temperature_type
{% endhighlight %}

and then in your question text you could write:

{% highlight text %}
Set your oven to ${ apple_pie.get_oven_temperature(temperature_type) }
and let it warm up.
{% endhighlight %}

# <a name="extending"></a>Extending existing classes

If you want to add a method to an existing **docassemble** class, such
as [`Individual`], you do not need to reinvent the wheel or copy and
paste code from anywhere.  Just take advantage of [inheritance].

For example, if your package is `docassemble.missouri_family_law`, you
could create/edit the file
`docassemble/missouri_family_law/objects.py` and add the following:

{% highlight python %}
from docassemble.base.util import Individual

class Attorney(Individual):
    def can_practice_in(self, state):
        if state in self.bar_admissions and self.bar_admissions[state] is True:
            return True
        return False
{% endhighlight %}

Here you are defining the class `Attorney` as a subclass of
[`Individual`].  An object that is an instance of the `Attorney` class
will also be an instance of the [`Individual`] class.  The `Attorney`
class is said to "inherit" from the [`Individual`] class.  All of the
methods that can be used on an [`Individual`] can be used on an
`Attorney`.

This allows you to write an interview like the following:

{% include side-by-side.html demo="attorney" %}

Note that the `lawyer` object works just like an [`Individual`]
object.  The `is_are_you()` method works on the `Attorney` object just
as it works on any [`Individual`].

Note that the `can_practice_in()` method is only available for
`Attorney` objects.  If you added the following to the above
interview:

{% highlight yaml %}
objects:
  - user: Individual
---
mandatory: True
question: |
  % if user.can_practice_in('MA'):
  You can take this case yourself.
  % else:
  You will need to hire a lawyer to take the case.
  % endif
{% endhighlight %}

then you would get an error because `can_practice_in()` is not a valid
method for `user`, which is only an instance of the [`Individual`] class
and not an instance of the `Attorney` class.

# <a name="DADateTime"></a>Special date/time class `DADateTime`

When you set a variable with [`datatype: date`], or use one of the
[date functions] that returns a date, the variable is a special object
of the class `DADateTime`.  This object is special to **docassemble**,
but it is not a [`DAObject`].  You cannot create these with an
[`objects`] block.  (If you want to create one, use
[`as_datetime()`].)

The [`DADateTime`] object is a subclass of [`datetime.datetime`],
which is a standard [Python] class for working with dates and times.
This means that anything that you can do with a [`datetime.datetime`]
object can also be done with a [`DADateTime`] object.

The [`DADateTime`] object also has some additional functionality that
the traditional [`datetime.datetime`] object does not have, such as
the attributes `dow` for day of week and `week` for the week of the
year.

If `birthday` is defined by `as_datetime('4/1/2018')`, then:

* `birthday.day` is 1
* `birthday.month` is 4
* `birthday.year` is 2018
* `birthday.week` is 13
* `birthday.dow` is 7 (Sunday)
* `birthday.hour` is 0
* `birthday.minute` is 0
* `birthday.second` is 0
* `birthday.microsecond` is 0

<a name="DADateTime.plus"></a><a name="DADateTime.minus"></a>The
[`DADateTime`] object also has methods `.plus()` and `.minus()` that
allow you to add or subtract periods of time from a date.

* `birthday.plus(weeks=3)` returns a [`DADateTime`] object representing April 29, 2018.
* `birthday.plus(months=1)` returns a [`DADateTime`] object representing May 1, 2018.
* `birthday.minus(years=2)` returns a [`DADateTime`] object representing April 1, 2020.

The available keyword arguments to `.plus()` and `.minus()` are:

* `years`
* `months`
* `days`
* `weeks`
* `hours`
* `minutes`
* `seconds`
* `microseconds`

The `.plus()` and `.minus()` methods use
[`dateutil.relativedelta.relativedelta`] to calculate dates and times.
The [`date_interval()`] function can be used to do similar
calculations.  For example, `birthday.plus(weeks=1)` is equivalent to
doing `birthday + date_interval(weeks=1)`.

<a name="DADateTime.format"></a><a name="DADateTime.format_date"></a><a name="DADateTime.format_time"></a><a name="DADateTime.format_datetime"></a>The
[`DADateTime`] object also has methods for formatting dates and times.

* `birthday.format()` is `'April 1, 2018'`.
* `birthday.format_date()` is `'April 1, 2018'` (identical to `.format()`)
* `birthday.format_date('MMM')` is `'Apr'`
* `birthday.format_time()` is `'12:00 AM'`
* `birthday.format_time('h:mm a z')` is `'12:00 AM EST'`, or whatever the
  current time zone is.
* `current_datetime().format_time('h:mm')` returns the current time,
  formatted like `'12:00'`.
* `current_datetime().format_datetime()` returns the current time,
  formatted like `'January 1, 2018 at 12:00:00 AM EST'`.

These functions have the same effect as the [`format_date()`],
[`format_time()`], and [`format_datetime()`] functions.  In fact,
`birthday.format_date('long')` simply calls `format_date(birthday,
format='long')`.  See the documentation for the [date functions] for
details.

When a [`DADateTime`] is converted to text, for example when it is
included in a [Mako] template with `${ birthday }`, the text
conversion is done using [`format_date()`].

<a name="DADateTime.replace"></a>The `.replace()` method returns a new
[`DADateTime`] object that is the same as the original object, except
with edited components.  For example, `birthdate.replace(year=2018)`
will return the date of a person's birthday in 2018.  The available
parameters are `year`, `month`, `day`, `hour` (0 to 23), `minute`,
`second`, and `microsecond`.  See [`datetime.datetime.replace()`].

<a name="DADateTime.replace_time"></a>A method that is similar to
`.replace()` is `.replace_time()`, which returns a [`DADateTime`]
object with all of the time-related values set to those of a given
[`datetime.time`] object.  If you ask the user a question and you use
a field with [`datatype: time`], the resulting variable is a
[`datetime.time`] object.  You can combine [`datatype: date`] and
[`datatype: time`] objects using `.replace_time()`:

{% include side-by-side.html demo="date-and-time-fields" %}

<a name="DADateTime.time"></a>If you only want to use the time portion
of a [`DADateTime`], use the `.time()` method, which returns a
[`datetime.time`] object containing only the time-related information
of the original [`DADateTime`] object.  See
[`datetime.datetime.time()`].

[`datetime.time`]: https://docs.python.org/2/library/datetime.html#datetime.time
[`datetime.datetime.time()`]: https://docs.python.org/2/library/datetime.html#datetime.datetime.time
[`datetime.datetime.replace()`]: https://docs.python.org/2/library/datetime.html#datetime.datetime.replace
[`date_interval()`]: {{ site.baseurl }}/docs/functions.html#date_interval
[date functions]: {{ site.baseurl }}/docs/functions.html#date functions
[`dateutil.relativedelta.relativedelta`]: http://dateutil.readthedocs.io/en/stable/relativedelta.html
[`format_date()`]: {{ site.baseurl }}/docs/functions.html#format_date
[`format_time()`]: {{ site.baseurl }}/docs/functions.html#format_time
[`format_datetime()`]: {{ site.baseurl }}/docs/functions.html#format_datetime
[`as_datetime()`]: {{ site.baseurl }}/docs/functions.html#as_datetime
[`datetime.datetime`]: https://docs.python.org/2/library/datetime.html#datetime-objects
[`DADateTime`]: #DADateTime
[`datatype: date`]: {{ site.baseurl }}/docs/fields.html#date
[`datatype: time`]: {{ site.baseurl }}/docs/fields.html#time
[AttributeError]: https://docs.python.org/2/library/exceptions.html#exceptions.AttributeError
[Documents]: {{ site.baseurl }}/docs/documents.html
[Flask-Mail]: https://pythonhosted.org/Flask-Mail/
[HTML]: https://en.wikipedia.org/wiki/HTML
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[Python dict]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[Python module]: https://docs.python.org/2/tutorial/modules.html
[Python object]: https://docs.python.org/2/tutorial/classes.html
[Python objects]: https://docs.python.org/2/tutorial/classes.html
[Python set]: https://docs.python.org/2/library/stdtypes.html#set
[Python]: https://www.python.org/
[YAML]: https://en.wikipedia.org/wiki/YAML
[`Address`]: #Address
[`Asset`]: #Asset
[`ChildList`]: #ChildList
[`DADict`]: #DADict
[`DAEmailRecipientList`]: #DAEmailRecipientList
[`DAEmailRecipient`]: #DAEmailRecipient
[`DAEmail`]: #DAEmail
[`DAFileCollection`]: #DAFileCollection
[`DAFileList`]: #DAFileList
[`DAFile`]: #DAFile
[`DAList`]: #DAList
[`DAObject`]: #DAObject
[`DASet`]: #DASet
[`DAStaticFile`]: #DAStaticFile
[`DATemplate`]: #DATemplate
[`Expense`]: #Expense
[`FinancialList`]: #FinancialList
[`Income`]: #Income
[`IndividualName`]: #IndividualName
[`Individual`]: #Individual
[`LatitudeLongitude`]: #LatitudeLongitude
[`Name`]: #Name
[`Organization`]: #Organization
[`PeriodicFinancialList`]: #PeriodicFinancialList
[`Person`]: #Person
[`Value`]: #Value
[`age_in_years()`]: #Individual.age_in_years
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachments
[`attachments`]: {{ site.baseurl }}/docs/documents.html#attachments
[`basic-questions.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[`code`]: {{ site.baseurl }}/docs/code.html
[`currency()`]: {{ site.baseurl }}/docs/functions.html#currency
[`default role`]: {{ site.baseurl }}/docs/initial.html#default role
[`docassemble.base.legal`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`generic object`]: {{ site.baseurl }}/docs/modifiers.html#generic object
[`get_info()`]: {{ site.baseurl }}/docs/functions.html#get_info
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`interview_url()`]: {{ site.baseurl }}/docs/functions.html#interview_url
[`legal.py`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[`.object_possessive()`]: #DAObject.object_possessive
[`objects`]: {{ site.baseurl }}/docs/initial.html#objects
[`possessive()`]: #Individual.possessive
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`set_info()`]: {{ site.baseurl }}/docs/functions.html#set_info
[`template`]: {{ site.baseurl }}/docs/initial.html
[`table`]: {{ site.baseurl }}/docs/initial.html#table
[`track_location`]:  {{ site.baseurl }}/docs/special.html#track_location
[`word()`]: {{ site.baseurl }}/docs/functions.html#word
[classes]: https://docs.python.org/2/tutorial/classes.html
[Python class]: https://docs.python.org/2/tutorial/classes.html
[configuration]: {{ site.baseurl }}/docs/config.html
[fields]: {{ site.baseurl }}/docs/fields.html
[Python function]: https://docs.python.org/2/tutorial/controlflow.html#defining-functions
[inheritance]: https://docs.python.org/2/tutorial/classes.html#inheritance
[initial block]: {{ site.baseurl }}/docs/initial.html
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[keyword argument]: https://docs.python.org/2/glossary.html#term-argument
[keyword arguments]: https://docs.python.org/2/glossary.html#term-argument
[list]: https://docs.python.org/2/tutorial/datastructures.html
[markup]: {{ site.baseurl }}/docs/markup.html
[methods]: https://docs.python.org/2/tutorial/classes.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[modifiers]: {{ site.baseurl }}/docs/modifiers.html
[multi-user interviews]: {{ site.baseurl }}/docs/roles.html
[object-oriented programming]: https://en.wikipedia.org/wiki/Object-oriented_programming
[package system]: {{ site.baseurl }}/docs/packages.html
[package]: {{ site.baseurl }}/docs/packages.html
[roles]: {{ site.baseurl }}/docs/roles.html
[source code]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[special variable]: {{ site.baseurl }}/docs/special.html
[str() function]: https://docs.python.org/2/library/functions.html#str
[thread-safe]: https://en.wikipedia.org/wiki/Thread_safety
[threading module]: https://docs.python.org/2/library/threading.html
[user login system]: {{ site.baseurl }}/docs/users.html
[`nice_number()`]: {{ site.baseurl }}/docs/functions.html#nice_number
[`comma_and_list()`]: {{ site.baseurl }}/docs/functions.html#comma_and_list
[`user_lat_lon()`]: {{ site.baseurl }}/docs/functions.html#user_lat_lon
[`sets`]: {{ site.baseurl }}/docs/modifiers.html#sets
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[`send_sms()`]: {{ site.baseurl }}/docs/functions.html#send_sms
[E.164]: https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers
[`get_country()`]: {{ site.baseurl }}/docs/functions.html#get_country
[`.sms_number()`]: #Person.sms_number
[`.email_address()`]: #Person.email_address
[`OfficeList`]: #OfficeList
[groups]: {{ site.baseurl }}/docs/groups.html
[question]: {{ site.baseurl }}/docs/questions.html#question
[code block]: {{ site.baseurl }}/docs/code.html#code
[dict]: https://docs.python.org/2/library/stdtypes.html#dict
[set]: https://docs.python.org/2/library/stdtypes.html#set
[magic]: https://docs.python.org/2/library/inspect.html
[Amazon S3]: https://aws.amazon.com/s3/
[Python Imaging Library]: https://en.wikipedia.org/wiki/Python_Imaging_Library
[e-mail receiving]: {{ site.baseurl }}/docs/background.html#email
[`interview_email()`]: {{ site.baseurl }}/docs/functions.html#interview_email
[`datetime`]: https://docs.python.org/2/library/datetime.html#datetime.datetime
[Return-path]: https://en.wikipedia.org/wiki/Bounce_address
[Reply-to]: https://www.ietf.org/rfc/rfc2822.txt
[JSON]: https://en.wikipedia.org/wiki/JSON
[MIME type]: https://en.wikipedia.org/wiki/Media_type
[Azure blob storage]: https://azure.microsoft.com/en-us/services/storage/blobs/
[document upload field]: {{ site.baseurl }}/docs/fields.html#file
[`variable name`]: {{ site.baseurl }}/docs/documents.html#variable name
[inserting images]: {{ site.baseurl }}/docs/markup.html#inserting images
[data storage]: {{ site.baseurl }}/docs/docker.html#data storage
[checkbox groups]: {{ site.baseurl }}/docs/fields.html#fields checkboxes
[storage]: {{ site.baseurl }}/docs/functions.html#storage
[exit button]: {{ site.baseurl }}/docs/questions.html#special buttons
[exit command]: {{ site.baseurl }}/docs/functions.html#command
[inactive for a period]: {{ site.baseurl }}/docs/config.html#interview delete days
[`.set_attributes()`]: #DAFile.set_attributes
[`datatype: file`]: {{ site.baseurl }}/docs/fields.html#file
[`datatype: files`]: {{ site.baseurl }}/docs/fields.html#files
[`City`]: #City
[valid formats]: {{ site.baseurl }}/docs/documents.html#valid formats
["new style" Python objects]: http://realmike.org/blog/2010/07/18/introduction-to-new-style-classes-in-python/
[relative module name]: https://docs.python.org/2.5/whatsnew/pep-328.html
[`words`]: {{ site.baseurl }}/docs/config.html#words
[`object_type`]: #object_type
[`initializeAttribute()`]: #DAObject.initializeAttribute
[`reInitializeAttribute()`]: #DAObject.reInitializeAttribute
[`appendObject()`]: #DAList.appendObject
[`gather()`]: #DAList.gather
[`object_name()`]: #DAObject.object_name
[`getattr()`]: https://docs.python.org/2/library/functions.html#getattr
[`Thing`]: #Thing
[`using()`]: #DAObject.using
[Redis]: https://redis.io/
[in-memory database]: https://en.wikipedia.org/wiki/In-memory_database
[`redis`]: https://github.com/andymccurdy/redis-py
[pickling]: https://docs.python.org/2/library/pickle.html
[pickled]: https://docs.python.org/2/library/pickle.html
[date field]: {{ site.baseurl }}/docs/fields.html#date
[`pronoun()`]: #Individual.pronoun
[`birthdate`]: #Individual.birthdate
[`gender`]: #Individual.gender
[`age`]: #Individual.age
[`geopy.geocoders.GoogleV3`]: https://geopy.readthedocs.io/en/1.11.0/#geopy.geocoders.GoogleV3
[`google`]: {{ site.baseurl }}/docs/config.html#google
[Google Maps Geocoding API]: https://developers.google.com/maps/documentation/geocoding/intro
[`PeriodicValue`]: #PeriodicValue
[Modules folder]: {{ site.baseurl }}/docs/playground.html#modules
[Playground]: {{ site.baseurl }}/docs/playground.html
[Place Autocomplete]: https://developers.google.com/places/web-service/autocomplete
[Google Places API]: https://developers.google.com/places/
[Configuration]: {{ site.baseurl }}/docs/config.html
[`google maps api key`]: {{ site.baseurl }}/docs/config.html#google
[`api key`]: {{ site.baseurl }}/docs/config.html#google
[`all_variables()`]: {{ site.baseurl }}/docs/functions.html#all_variables
[translation system]: {{ site.baseurl }}/docs/functions.html#translation
[`docassemble.base.util.update_language_function()`]: {{ site.baseurl }}/docs/functions.html#linguistic
[`docassemble.base.functions`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/functions.py
[hyperlink]: https://en.wikipedia.org/wiki/Hyperlink
[URL]: https://en.wikipedia.org/wiki/URL
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[boto3]: https://boto3.readthedocs.io/en/latest/
[azure.storage.blob]: https://docs.microsoft.com/en-us/python/api/overview/azure/storage?view=azure-python
[`BlockBlobService()`]: https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python
[`boto3.resource('s3')`]: http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.ServiceResource
[`boto3.client('s3')`]: http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client
[`Bucket`]: http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Bucket
[`s3`]: {{ site.baseurl }}/docs/config.html#s3
[`azure`]: {{ site.baseurl }}/docs/config.html#azure
[Azure blob storage]: {{ site.baseurl }}/docs/docker.html#persistent azure
[Amazon S3]: https://aws.amazon.com/s3/
[Google API]: https://developers.google.com/api-client-library/python/apis/
[Google API for Python]: https://developers.google.com/api-client-library/python/
[service account]: https://cloud.google.com/iam/docs/understanding-service-accounts
[Google Developers Console]: https://console.developers.google.com/
[directory of scopes]: https://developers.google.com/identity/protocols/googlescopes
[Google Drive API]: https://developers.google.com/drive/
[`httplib2.Http()`]: http://httplib2.readthedocs.io/en/latest/libhttplib2.html#httplib2.Http
[`ServiceAccountCredentials`]: http://oauth2client.readthedocs.io/en/latest/source/oauth2client.service_account.html#oauth2client.service_account.ServiceAccountCredentials
[oauth2client.service_account]: http://oauth2client.readthedocs.io/en/latest/source/oauth2client.service_account.html 
[gspread]: https://gspread.readthedocs.io/en/latest/
[Cloud Translation API Client Library]: https://cloud.google.com/translate/docs/reference/libraries#client-libraries-install-python
[`google-api-python-client`]: https://github.com/google/google-api-python-client/
[Google Cloud packages]: https://cloud.google.com/python/references/libraries
[google.oauth2.service_account]: http://google-auth.readthedocs.io/en/latest/reference/google.oauth2.service_account.html
[`Credentials`]: http://google-auth.readthedocs.io/en/latest/reference/google.oauth2.service_account.html#google.oauth2.service_account.Credentials
[`get_config()`]: {{ site.baseurl }}/docs/functions.html#get_config
[`DAGoogleAPI`]: #DAGoogleAPI
[`google.cloud.storage`]: https://cloud.google.com/storage/docs/reference/libraries#client-libraries-install-python
[`google.cloud.translate`]: https://cloud.google.com/translate/docs/reference/libraries#client-libraries-install-python
[data storage]: {{ site.baseurl }}/docs/docker.html#data storage
[S3 bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[Google Drive]: https://www.google.com/drive/
[Google Cloud Storage]: https://cloud.google.com/storage/docs/reference/libraries
[LibreOffice]: https://www.libreoffice.org/
[`service account credentials`]: {{ site.baseurl }}/docs/config.html#service account credentials
[Object-oriented Programming for Document Assembly Developers]: https://www.nonprofittechy.com/2018/09/12/object-oriented-programming-for-document-assembly-developers/
[Quinten Steenhuis]: https://www.nonprofittechy.com/about/
[Python book]: http://shop.oreilly.com/product/0636920028154.do
[list comprehension]: https://docs.python.org/2.7/tutorial/datastructures.html#list-comprehensions
[interview session dictionary]: {{ site.baseurl }}/docs/interviews.html#howstored
[namespace]: https://docs.python.org/2.7/tutorial/classes.html#python-scopes-and-namespaces
[write your own functions]: {{ site.baseurl }}/docs/functions.html#yourown
[`set_alt_text()`]: #DAFile.set_alt_text
[`get_alt_text()`]: #DAFile.get_alt_text
[`get_pdf_fields()`]: #DAFile.get_pdf_fields
[`get_docx_variables()`]: #DAFile.get_docx_variables
[alt text]: https://moz.com/learn/seo/alt-text
[note above]: #set_info
[using `complete_attribute`]: {{ site.baseurl }}/docs/groups.html#complete_attribute
[WhatsApp]: https://www.twilio.com/whatsapp
[`suppress loading util`]: {{ site.baseurl }}/docs/initial.html#suppress loading util
[ISO 3166-1 alpha-2]: https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[country calling code]: https://en.wikipedia.org/wiki/List_of_country_calling_codes
[`pdf template file`]: {{ site.baseurl }}/docs/documents.html#pdf template file
[`data`]: {{ site.baseurl }}/docs/initial.html#data
[`use objects`]: {{ site.baseurl }}/docs/initial.html#use objects
[OAuth2]: https://oauth.net/2/
[Google Developers Console]: https://console.developers.google.com/
[`oauth.py`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/oauth.py
