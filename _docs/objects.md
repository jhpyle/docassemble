---
layout: docs
title: Objects
short_title: Objects
---

# How docassemble uses objects

[Python] allows [object-oriented programming] and so does
**docassemble**.

Here is a non-object-oriented way of saying hello to the user by name:

{% highlight yaml %}
---
question: What is your name?
fields:
  - First: user_first_name
  - Last: user_last_name
---
question: |
  Hello, ${ user_first_name } ${ user_last_name }!
mandatory: true
{% endhighlight %}

A better way is to define `user` as a **docassemble** object,
`Individual`.

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - user: Individual
---
question: |
  What's your name?
fields:
  - First: user.name.first
  - Last: user.name.last
---
question: |
  Hello, ${ user }!
mandatory: true
---
{% endhighlight %}

As explained in the [fields] section, variable names cannot contain
any punctuation other than the underscore.  So while `user_first_name`
is a valid variable name, `user.name.first` must be something
different.  Periods in [Python] are used to refer to the "attributes"
of "objects."

An object is a special type of variable.  Rather than being a piece of
text, like `user_first_name` is, the variable `user` is an "object"
that is an "instance" of the "class" known as `Individual`.

Using objects in **docassemble** requires a little bit of setup in
[initial blocks].  `Individual` is defined in the
`docassemble.base.legal` [Python module], so it was necessary to bring
that module into the interview with a `modules` block.  It was also
necessary to use an `objects` block to declare that `user` is an
instance of the class `Individual`.

Objects have "attributes."  In the above example, `name` is an
attribute of the object `user`.  And `name` is itself an object (it is
an instance of the class `IndividualName`, though you would need to
look at the [source code] to know that) with attributes `first` and
`last`.  The attributes `first` and `last` are not objects, but rather
pieces of text.  Anything before a `.` is an object, and anything
after the `.` is an attribute of the object.

Objects have "methods," which are functions that return a value based
on the attributes of the object.  For example, `user.age_in_years()`
will return the current age of the `user` based on the date defined in
the attribute `user.birthdate`:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - user: Individual
---
question: |
  What is your date of birth?
fields:
  - no label: user.birthdate
    datatype: date
---
mandatory: true
question: |
  You are ${ user.age_in_years() } years old.
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testage.yml){:target="_blank"}.)

Using objects in your interviews has a number of advantages over
using plain variables.

The first advantage is that you can write `generic object` questions.
(See [modifiers] for documentation of the `generic object` feature.)
For example, if you need to collect the phone numbers of three people,
the `grantor`, the `grantee`, and the `trustee`, you don't have to
write separate questions for `grantor.phone_number`,
`grantee.phone_number`, and `trustee.phone_number`.  You can write one
question to collect `x.phone_number`:

{% highlight yaml %}
---
generic object: Individual
question: |
  What is ${ x.possessive('phone number') }?
fields:
  Phone Number: x.phone_number
---
{% endhighlight %}

Any time **docassemble** needs to know the phone number of an
`Individual` object, it will ask this question.

In the question text above, `possessive()` is a "method" that you can
use on any instance of the `Individual` class.  If `trustee`'s name is
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
You can write code that checks for the equivalence of objects:

{% highlight yaml %}
---
question: |
  % if user is trustee:
  As the trustee of the estate, you need to understand that it is
  your fiduciary duty to safeguard the assets of the estate.
  % elif user is grantee:
  You are the grantee, which means that ${ trustee } is required to
  safeguard the assets of the estate on your behalf.
  % else:
  ${ trustee } will safeguard the assets of the estate on behalf of
  ${ grantee }.
  % endif
---
{% endhighlight %}

Object methods allow you to have a standard way of expressing
information even though the methods used to gather the information may
vary depending on the circumstances.  For example, the
`age_in_years()` function, discussed above, first looks to see if the
attribute `age` is defined, and if so will return that instead of
asking for the `birthdate` attribute:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - user: Individual
---
question: |
  How old are you?
fields:
  - Age in years: user.age
    datatype: number
---
mandatory: true
code: |
  need(user.age)
---
mandatory: true
question: |
  You are ${ user.age_in_years() } years old.
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testage2.yml){:target="_blank"}.)

Although objects are a fairly complicated concept, as you can see,
they allow you to write code that looks much like plain English.

In part, this is because objects allow you to do complicated things in
an implicit way.  For example, writing `${ grantee }` in a [Mako]
template implicitly calls the method `__str()__` on `grantee`.
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

# Writing your own classes

If you are prepared to write your own [Python] code, it is pretty easy
to write your own classes.

For example, you could create your own [package] for interviews
related to cooking.

You would start by using the [package system] to create a
**docassemble** package called `cooking`, which would be given the
name `docassemble.cooking` (interview packages are subpackages of the
`docassemble` namespace package).

You would go into the package and edit the file
`docassemble/cooking/objects.py` and set the contents to the
following:

{% highlight python %}
from docassemble.base.core import DAObject

class Recipe(DAObject):
    def summary(self):
        return "#### Ingredients\n\n" + self.ingredients + "\n\n#### Instructions\n\n" + self.instructions
{% endhighlight %}

Your class `Recipe` needs to "inherit" from the basic **docassemble**
object called `DAObject`.  If you did not do this, **docassemble**
would not be able to ask questions to define attributes of `Recipe` objects.

The purpose of the `summary()` method is to summarize the contents of
the recipe.  It makes use of the attributes `ingredients` and
`instructions`.

If you are not familiar with [Python], `\n` inside quotation marks
indicates a line break and `+` in the context of text indicates that
the text should be strung together.  In [Markdown], `####` at the
start of a line indicates that the line is a section name.

Once you install the package on your server, you can use your class in
an interview:

{% highlight yaml %}
---
modules:
  - docassemble.cooking.objects
---
objects:
  - submission: Recipe
---
generic object: Recipe
question: |
  What do you want to cook?
fields:
  - Food: x.name
---
generic object: Recipe
question: |
  What are the ingredients of ${ x.name }?
fields:
  - no label: x.ingredients
    datatype: area
---
generic object: Recipe
question: |
  What are the cooking instructions for making ${ x.name }?
fields:
  - no label: x.instructions
    datatype: area
---
mandatory: true
question: |
  Recipe for ${ submission.name }
subquestion: |
  ${ submission.summary() }
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testcooking.yml){:target="_blank"}.)

By the way, there is way to write the `summary()` method that is more
friendly to other interview authors:

{% highlight python %}
return "#### " + word('Ingredients') + "\n\n" + self.ingredients + "\n\n#### " + word('Instructions') + "\n\n" + self.instructions
{% endhighlight %}

If you use the `word()` function in this way, other people will be
able to use `docassemble.cooking.objects` in non-English interviews
without having to edit your code.  All they would have to do is
include the words `Ingredients` and `Instructions` in a translation
[YAML] file referenced in a `words` directive in the **docassemble**
[configuration].

## Using global variables in your classes

Normally in [Python] you can use global variables to keep track of
information that your methods need to know but that is not passed in
arguments to the methods.  For example, if you wanted to keep track of
whether to use Celsius or Fahrenheit when talking about temperatures,
you could do:

{% highlight python %}
from docassemble.base.core import DAObject

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

Then you could change the `temperature_type` from an interview:

{% highlight yaml %}
---
modules:
  - docassemble.cooking.objects
---
initial: true
code: |
  if user_is_scientist:
    temperature_type = 'Kelvin'
  elif user_country in ['United States', 'Great Britain']:
    temperature_type = 'Fahrenheit'
...
{% endhighlight %}

This works because the `modules` block loads all the names from
`docassemble.cooking.objects` into the variable store of the
interview, including `temperature_type`.

However, this is not [thread-safe] and it will not work correctly 100%
of the time.  If your server is under heavy load, users might randomly
be advised to turn their ovens to 350 degrees Celsius, which would
scorch the food.  This is because the variable `temperature_type`
exists at the level of the web server process, and the process might
be supporting several users simultaneously (in different "threads" of
the process).  Between the time one thread sets `temperature_type` to
`Fahrenheit` and tries to use it, another user inside the same process
might set `temperature_type` to `Celsius`.

The simplest way to get around this problem is to use the `set_info()`
and `get_info()` functions from `docassemble.base.util`:

{% highlight python %}
from docassemble.base.core import DAObject
from docassemble.base.util import get_info

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

Then from your interview you can bring in `docassemble.base.util` and run `set_info()`:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
  - docassemble.cooking.objects
---
initial: true
code: |
  if user_is_scientist:
    set_info(temperature_type='Kelvin')
  elif user_country in ['United States', 'Great Britain']:
    set_info(temperature_type='Fahrenheit')
  else:
    set_info(temperature_type='Celsius')
...
{% endhighlight %}

Alternatively, you can do what `docassemble.base.util` does and use
Python's [threading module] to store global variables.

{% highlight python %}
from docassemble.base.core import DAObject
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

We added an `__all__` statement so that interviews can a `module`
block including `docassemble.cooking.objects` does not clutter the
variable store with extraneous names like `threading`.  We also added
functions for setting and retrieving the value of the "temperature
type."

The temperature type is now an attribute of the object `this_thread`,
which is an instance of `threading.local`.  This attribute needs to be
set in `initial` code that will run every time a screen refreshes.

Now in your interview you can do:

{% highlight yaml %}
---
modules:
  - docassemble.cooking.objects
---
initial: true
code: |
  if user_is_scientist:
    set_temperature_type('Kelvin')
  elif user_country in ['United States', 'Great Britain']:
    set_temperature_type('Fahrenheit')
  else:
    set_temperature_type('Celsius')
...
{% endhighlight %}

Note that you do not need to worry about whether your global variables
are [thread-safe] if they do not change from interview to interview.

For example, if you only wanted to allow people to change the
temperature type from the **docassemble** [configuration], you could
do the following in your [Python module]:

{% highlight python %}
from docassemble.base.core import DAObject

from docassemble.webapp.config import daconfig
temperature_type = daconfig.get('temperature type', 'Celsius')
{% endhighlight %}

Then your interviews would not have to do anything with `temperature_type`.

Also, you could avoid the complication of global variables entirely if
you are willing to pass the temperature type as an argument to
`get_oven_temperature`:

{% highlight python %}
from docassemble.base.core import DAObject

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
---
question: |
  What kind of temperature system do you use?
choices:
  - Celsius
  - Fahrenheit
  - Kelvin
field: temperature_type
---
{% endhighlight %}

and then in your question text you could write:

{% highlight text %}
Set your oven to ${ apple_pie.get_oven_temperature(temperature_type) }
and let it warm up.
{% endhighlight %}
    
# Standard docassemble classes

## <a name="DAObject"></a>DAObject

All **docassemble** objects are instances of the `DAObject` class.
`DAObject`s are different from normal [Python objects] because they
have special attributes that allow their attributes to be set by
**docassemble** questions.  If `fruit` is an ordinary [Python object]
and you refer to `fruit.seeds` when `seeds` is not an existing
attribute of `fruit`, [Python] will generate an [AttributeError].  But
if `fruit` is a `DAObject`, **docassemble** will ask a question that
offers to define `fruit.seeds`, or ask a `generic object` question for
object `DAObject` that offers to define `x.seeds`.

If you wish to add an attribute to a `DAObject` that is an instance
`DAObject`, you may need to use the `initializeAttribute()` method.

Suppose you try the following:

{% highlight yaml %}
---
modules:
  - docassemble.base.core
---
objects:
  - tree: DAObject
  - long_branch: DAObject
---
mandatory: true
question: |
  The length of the branch is ${ tree.branch.length }.
---
code: |
  tree.branch = long_branch
---
question: |
  What is the length of the branch on the tree?
fields:
  - Length: tree.branch.length
---
{% endhighlight %}

This will result in the following error:

> Found a reference to a variable 'long_branch.length' that could not
> be looked up in the question file or in any of the files
> incorporated by reference into the question file, despite reaching
> the very end of the file.

If you had a question that defined `long_branch.length` or a `generic
object` question for the `x.length` where `x` is a `DAObject`, then
**docassemble** would use that question, but it is not able to ask for
the length of the branch with `tree.branch.length` since the intrinsic
name of the branch is `long_branch`, not `tree.branch`.

However, this will work as intended:

{% highlight yaml %}
---
modules:
  - docassemble.base.core
---
objects:
  - tree: DAObject
---
sets: tree.branch
code: |
  tree.initializeAttribute('branch', DAObject)
---
mandatory: true
question: |
  The length of the branch is ${ tree.branch.length }.
---
question: |
  What is the length of the branch on the tree?
fields:
  - Length: tree.branch.length
---
{% endhighlight %}

The `initializeAttribute` section here creates a new `DAObject` with
the intrinsic name of `tree.branch`, and adds the `branch` attribute
to the object `tree`.

Note that we had to add `sets: tree.branch` to the `code` section with
`tree.initializeAttribute('branch', DAObject)`, but this was not
necessary when the code was `tree.branch = long_branch`.  This is
because **docassemble** reads the code in `code` sections and looks
for assignments with the `=` operator, and keeps track of which code
sections define which variables.  But sometimes variables are assigned
by functions, and **docassemble** does not realize that.  The
`sets: tree.branch` line tells **docassemble** that the code promises
to define `tree.branch`.

One of the useful things about `DAObject`s is that you can write
`generic object` questions that work in a wide variety of
circumstances because the questions can use the variable name itself
when forming the text of the question to ask the user.

If you refer to a `DAObject` in a [Mako] template (or reduce it to
text with Python's [str function]), this will have the effect of
calling the `object_name()` method, which attempts to return a
human-friendly name for the object.

For example:

{% highlight yaml %}
---
modules:
  - docassemble.base.core
---
objects:
  - park: DAObject
  - turnip: DAObject
---
mandatory: true
code: |
  park.initializeAttribute('front_gate', DAObject)
---
mandatory: true
question: |
  The ${ turnip.color } turnip sat before the
  ${ park.front_gate.color } gate.
---
generic object: DAObject
question: |
  What is the color of the ${ x }?
fields:
  - Color: x.color
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testdaobject.yml){:target="_blank"}.)

Although there is only one question for `x.color`, this question
generates both "What is the color of the turnip?" and "What is the
color of the front gate in the park?"  This is because `object_name()`
is implicitly called and it turns `park.front_gate` into "front gate
in the park."

The `object_name()` method is multi-lingual-friendly.  By using
`docassemble.base.util.update_word_collection()`, you can provide
non-English translations for words that come from variable names, such
as "turnip," "park," and "front gate."  By using
`docassemble.base.util.update_language_function()`, you can define a
non-English version of the `a_in_the_b()` function, which
`object_name()` uses to convert an attribute name like
`park.front_gate` into "front gate in the park."  (It calls
`a_in_the_b('front gate', 'park')`.)  So in a Spanish interview,
`park.front_gate.object_name()` would return "puerta de entrada en el
parque."  (The Spanish version of `a_in_the_b()` will be more
complicated than the English version because it will need to determine
the gender of the second argument.)

A related method of `DAObject` is `object_possessive()`.  Calling
`turnip.object_possessive('leaves')` will return `the turnip's
leaves`.  Calling `park.front_gate.object_possessive('latch')` will
return `the latch of the front gate in the park`.

The `DAObject` is the most basic object, and all other **docassemble**
objects inherit from it.  These objects will have different methods
and behaviors.  For example, if `friend` is an `Individual` (from
`docassemble.base.legal`), calling `${ friend }` in a [Mako] template
will not return `friend.object_name()`; rather, it will return
`friend.full_name()`, which may require asking the user for the
`friend`'s name.

## <a name="DAList"></a>DAList

A `DAList` acts like an ordinary [Python list], except that
**docassemble** can ask questions to define elements of the list.  For
example, you could define `recipient` as a `DAList` containing five
`Individual`s:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - recipient: DAList
  - trustee: Individual
  - beneficiary: Individual
  - grantor: Individual
---
mandatory: true
code: |
  recipient.append(trustee)
  recipient.append(beneficiary)
  recipient.append(grantor)
  recipient.appendObject(Individual)
  recipient.appendObject(Individual)
---
mandatory: true
question: The recipients
subquestion: |
  % for person in recipient:
  ${ person } is a recipient.
  % endfor
---
generic object: Individual
question: |
  What is the name of the ${ x.object_name() }?
fields:
  - First Name: x.name.first
  - Last Name: x.name.last
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testdalist.yml){:target="_blank"}.)

This will result in the following five questions being asked:

* What is the name of the trustee?
* What is the name of the beneficiary?
* What is the name of the grantor?
* What is the name of the fourth recipient?
* What is the name of the fifth recipient?

<a name="DAList.appendObject"></a>
The `appendObject()` method is similar to the `initializeAttribute()`
method we discussed earlier.  Running
`recipient.appendObject(Individual)` creates a new object of the class
`Individual` and adds it to the list.  In the example above, the first
such object is the fourth element in the list, which means that the
intrinsic name of the new object is `recipient[3]`.

A `DAList` can be given a default object type, so that
`appendObject()` can be called without an argument.  This default
object type is controlled by the `.objectFunction` attribute.  For
example, when a `PartyList` object is created, the `.objectFunction`
attribute is set to `Person`.

If you want greater control over the way the questions are asked, you
could add a `generic object` question that is specific to the
recipients that were added with `appendObject()`.  For example:

{% highlight yaml %}
---
generic object: Individual
question: |
  The ${ ordinal(i) } ${ x.object_name() } must have a name.  What is it?
fields:
  - First Name: x[i].name.first
  - Last Name: x[i].name.last
---
{% endhighlight %}

The names of the fourth and fifth recipients are capable of being
asked by this question, since the pattern `x[i]` (where `x[i]` is an
`Individual`) matches the intrinsic names `recipient[3]` and
`recipient[4]`.  Since the other `generic object` question, which
matches `x` (where `x` is an `Individual`) also matches `recipient[3]`
and `recipient[4]`, the order in which you list the questions in the
[YAML] file will determine which one is chosen.  Later-appearing questions
take precedence, so you would need to place the second `generic
object` question somewhere after the first `generic object` question
in order for it to be chosen.

Other methods available on a DAList are:

* <a name="DAList.append"></a>`append(item_to_append)` - adds `item_to_append` to the end of the
  list.  Just like the [Python list] method of the same name.
* <a name="DAList.extend"></a>`extend(extension_list)` - adds the items in the `extension_list` to
  the end of the list.  Just like the [Python list] method of the same name.
* <a name="DAList.first"></a>`first()` - returns the first element of the list; error triggered
  if list is empty 
* <a name="DAList.last"></a>`last()` - returns the last element of the list; error triggered if list is empty
* <a name="DAList.does_verb"></a>`does_verb(verb)` - like the `verb_present()` function from
  `docassemble.base.util`, except that it uses the singular or plural
  form depending on whether the list has more than one element or not.
* <a name="DAList.did_verb"></a>`did_verb(verb)` - like the `verb_past()` function from
  `docassemble.base.util`, except that it uses the singular or plural
  form depending on whether the list has more than one element or not.
* <a name="DAList.as_singular_noun"></a>`as_singular_noun()` - if the variable name is `case.plaintiff`,
  returns `plaintiff`; if the variable name is `applicant`, returns `applicant`.
* <a name="DAList.as_noun"></a>`as_noun()` - if the variable name is `case.plaintiff`, returns
  `plaintiffs` or `plaintiff` depending on the number of elements in
  the list; if the variable name is `applicant`, returns `applicants`
  or `applicant` depending on the number of elements in the list.
* <a name="DAList.number"></a>`number()` - returns the total number of elements in the list, with
  the side effect of checking on the value of the `gathered`
  attribute, which might trigger questions that ask for all of the
  elements of the list to be populated.
* <a name="DAList.number_as_word"></a>`number_as_word()` - same as `number()`, except that the
  `nice_number()` [function] is applied to the result.
* <a name="DAList.number_gathered"></a>`number_gathered()` - like `number()` except that it does not have
  the side effect of checking on the value of the `gathered`
  attribute.
* <a name="DAList.number_gathered_as_word"></a>`number_gathered_as_word()` - same as `number_gathered()`, except that the
  `nice_number()` [function] is applied to the result.
* <a name="DAList.remove"></a>`remove()` - removes the given elements
  from the list, if they are in the list.
* <a name="DAList.comma_and_list"></a>`comma_and_list()` - returns the elements of the list run through
  the `comma_and_list()` [function].

If you refer to a list in a [Mako] template (e.g., `The applicants
include: ${ applicant }`) or convert it to text with the
[str function] (e.g. (`str(applicant)`) in [Python] code, the result
will be the output of the `comma_and_list()` method.

The `DAList` uses the following attributes:

* `gathering`: a boolean value, initialized to `False`.  Set this to
`True` when the interview is in the process of asking questions to
define all the elements of the list.
* `gathered`: a boolean value, initially undefined.  Set this to
`True` when then all of the elements of the list are defined.
* `elements`: a [Python list] containing the elements of the list.

By checking the value of the `gathered` attribute, you can trigger
asking the necessary questions to define all of the elements of the
list.  The methods of `DAList` behave differently depending on whether
or not the interview is in the process of gathering the elements of
the list.

## <a name="DADict"></a>DADict

A `DADict` acts like a [Python dictionary] except that dictionary
elements can be defined through **docassemble** questions.  To add an
element that is a new **docassemble** object, you need to call the
`initializeObject()` method.

For example:

{% highlight yaml %}
---
modules:
  - docassemble.base.core
---
objects:
  - player: DADict
---
mandatory: true
code: |
  player.initializeObject('trustee', DAObject)
  player.initializeObject('beneficiary', DAObject)
  player.initializeObject('grantor', DAObject)
---
mandatory: true
question: The players
subquestion: |
  % for type in player:
  ${ player[type].firstname } ${ player[type].lastname } is here.

  % endfor
---
generic object: DAObject
question: |
  What is ${ x[i].object_possessive('name') }?
fields:
  - First Name: x[i].firstname
  - Last Name: x[i].lastname
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testdadict.yml){:target="_blank"}.)

The `DADict` uses the following attributes:

* `elements`: a [Python dictionary] containing the items of the dictionary.

## <a name="DAFile"></a>DAFile

A `DAFile` object is used to refer to a file, which might be an
uploaded file, an assembled document, or a static document.  It has
the following attributes:

* `filename`: the path to the file on the filesystem;
* `mimetype`: the MIME type of the file;
* `extension`: the file extension (e.g., `pdf` or `rtf`); and
* `number`: the internal integer number used by **docassemble** to
  keep track of documents stored in the system

<a name="DAFile.show"></a>It has one method, `.show()`, which inserts
markup that displays the file as an image.  This method takes an
optional keyword argument, `width`.

When included in a template, a `DAFile` object will effectively
call `show()` on itself.

## <a name="DAFileCollection"></a>DAFileCollection

`DAFileCollection` objects are created internally by **docassemble**
in order to refer to a document assembled using the `attachments`
[modifier] in combination with a `variable name`.  It has attributes
for each file type generated (e.g., `pdf` or `rtf`), where the
attributes are objects of type `DAFile`.

For example, if the variable `my_file` is a `DAFileCollection`,
`my_file.pdf` will be a `DAFile` containing the PDF version, and
`my_file.rtf` will be a `DAFile` containing the RTF version.

## <a name="DAFileList"></a>DAFileList

A `DAFileList` is a `DAList`, the elements of which are expected to be
`DAFile` objects.

When a question has a field with a `datatype` for a file upload (see
[fields]), the variable will be defined as a `DAFileList` object
containing the file or files uploaded.

<a name="DAFileList.show"></a>It has one method, `.show()`, which
inserts markup that displays each file as an image.  This method takes
an optional keyword argument, `width`.

When included in a template, a `DAFileList` object will effectively
call `show()` on itself.

## <a name="DATemplate"></a>DATemplate

The `template` block allows you to store some text to a variable.  See
[template].  The variable will be defined as an object of the
`DATemplate` class.

Objects of this type have two attributes:

* `content`
* `subject`

When **docassemble** defines a [template], it assembles any [Mako] in
the `content` and option `subject` sets defines these attributes as
the resulting text.  Note that the text may have [Markdown] [markup]
in it.

# Extending existing classes

If you want to add a method to an existing **docassemble** class, such
as `Individual`, you do not need to reinvent the wheel or copy and
paste code from anywhere.  Just take advantage of [inheritance].

For example, if your package is `docassemble.missouri_family_law`, you
could create/edit the file
`docassemble/missouri_family_law/objects.py` and add the following:

{% highlight python %}
from docassemble.base.legal import Individual

class Attorney(Individual):
    def can_practice_in(self, state):
        if state in self.bar_admissions and self.bar_admissions[state] is True:
            return True
        return False
{% endhighlight %}

Here you are defining the class `Attorney` as a subclass of
`Individual`.  An object that is an instance of the `Attorney` class
will also be an instance of the `Individual` class.  The `Attorney`
class is said to "inherit" from the `Individual` class.  All of the
methods that can be used on an `Individual` can be used on an `Attorney`.

This allows you to write an interview like the following:

{% highlight yaml %}
---
modules:
  - docassemble.missouri_family_law.objects
---
imports:
  - us
---
objects:
  - lawyer: Attorney
---
mandatory: true
question: |
  % if lawyer.can_practice_in('MA'):
  ${ lawyer } can practice in Massachusetts.
  % else:
  Sorry, ${ lawyer } cannot practice in Massachusetts.
  % endif
---
generic object: Attorney
question: |
  In what state(s) ${ x.is_are_you() } admitted to practice?
fields:
  - no label: x.bar_admissions
    datatype: checkboxes
    code: |
      us.states.mapping('abbr', 'name')
---
generic object: Attorney
question: |
  What is the attorney's name?
fields:
  - First Name: x.name.first
  - Last Name: x.name.last
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testattorney.yml){:target="_blank"}.)

Note that the `lawyer` object works just like an `Individual` object.
The `is_are_you()` method, which is defined in
`docassemble.base.legal`, works on the `Attorney` object, despite the
fact that the interview does not explicitly refer to
`docassemble.base.legal` anywhere.  (The module
`docassemble.missouri_family_law.objects` imports
`docassemble.base.legal`.)

Note that the `can_practice_in()` method is only available for
`Attorney` objects.  If you added the following to the above
interview:

{% highlight yaml %}
---
objects:
  - user: Individual
---
mandatory: true
question: |
  % if user.can_practice_in('MA'):
  You can take this case yourself.
  % else:
  You will need to hire a lawyer to take the case.
  % endif
---
{% endhighlight %}

then you would get an error because `can_practice_in()` is not a valid
method for `user`, which is only an instance of the `Individual` class
and not an instance of the `Attorney` class.

[YAML]: https://en.wikipedia.org/wiki/YAML
[inheritance]: https://docs.python.org/2/tutorial/classes.html#inheritance
[threading module]: https://docs.python.org/2/library/threading.html
[thread-safe]: https://en.wikipedia.org/wiki/Thread_safety
[object-oriented programming]: https://en.wikipedia.org/wiki/Object-oriented_programming
[modifiers]: {{ site.baseurl }}/docs/modifiers.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[Mako]: http://www.makotemplates.org/
[Python module]: https://docs.python.org/2/tutorial/modules.html
[Python]: https://www.python.org/
[fields]: {{ site.baseurl }}/docs/fields.html
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[source code]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[package]: {{ site.baseurl }}/docs/packages.html
[package system]: {{ site.baseurl }}/docs/packages.html
[configuration]: {{ site.baseurl }}/docs/config.html
[Markdown]: https://daringfireball.net/projects/markdown/syntax
[AttributeError]: https://docs.python.org/2/library/exceptions.html#exceptions.AttributeError
[Python objects]: https://docs.python.org/2/tutorial/classes.html
[Python object]: https://docs.python.org/2/tutorial/classes.html
[str function]: https://docs.python.org/2/library/functions.html#str
[function]: {{ site.baseurl }}/docs/functions.html
[template]: {{ site.baseurl }}/docs/template.html
[markup]: {{ site.baseurl }}/docs/markup.html
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
