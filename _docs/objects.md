---
layout: docs
title: Objects
short_title: Objects
---

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
question: >-
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

([Try it out here](https://docassemble.org/demo?i=docassemble.demo:data/questions/testage.yml){:target="_blank"}.)

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
question: >-
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

([Try it out here](https://docassemble.org/demo?i=docassemble.demo:data/questions/testage2.yml){:target="_blank"}.)

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

    Remember that ${ trustee.possessive('phone number') } is
    ${ trustee.phone_number }.

then in order to ask the question, **docassemble** may ask you for the
trustee's name (so it can say "Remember that John Smith's phone number
is ..."), and then ask for the trustee's `phone_number` if it is not
already defined.

## Writing your own classes

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
---
from docassemble.base.core import DAObject

class Recipe(DAObject):
    def summary(self):
        return "#### Ingredients\n\n" + self.ingredients + "\n\n#### Instructions\n\n" + self.instructions
---
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

([Try it out here](https://docassemble.org/demo?i=docassemble.demo:data/questions/cooking.yml){:target="_blank"}.)

By the way, there is way to write the `summary()` method that is more
friendly to other interview authors:

{% highlight python %}
---
return "#### " + word('Ingredients') + "\n\n" + self.ingredients + "\n\n#### " + word('Instructions') + "\n\n" + self.instructions
---
{% endhighlight %}

This way, other people will be able to use
`docassemble.cooking.objects` in non-English interviews without having
to edit your code.  All they would have to do is include the words
`Ingredients` and `Instructions` in a translation [YAML] file
referenced in a `words` directive in the **docassemble**
[configuration].

### Using global variables in your classes

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

The `str()` function is a Python function that converts something to
text.  Here, it is necessary because `self.oven_temperature` may be a
number, and [Python] will complain if you ask it to "add"
text to a number.

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

This will work correctly 99% of the time.  However, it is not
[thread-safe].  If your server is under heavy load, users might
randomly be advised to turn their ovens to 350 degrees Celsius, which
would scorch the food.  This is because the variable
`temperature_type` is defined at the level of the web server process,
and the process might be supporting several users simultaneously (in
different "threads" of the process).  Between the time one thread sets
`temperature_type` to `Fahrenheit` and tries to use it, another thread
might set `temperature_type` to `Celsius`.

To get around this problem, use Python's [threading module] to store
global variables.

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

We added an `__all__` statement so that interviews can include names
from `docassemble.cooking.objects` without including extraneous names
like `threading`.  We also added functions for setting and retrieving
the value of the "temperature type."

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
temperature type from the **docassemble** [configuration], you could do:

{% highlight python %}
from docassemble.base.core import DAObject

from docassemble.webapp.config import daconfig
temperature_type = daconfig.get('temperature type', 'Celsius')
{% endhighlight %}

Then your interviews would not have to do anything with `temperature_type`.

Also, you could avoid the complication of global variables entirely if
you always pass the temperature type as an argument to `get_oven_temperature`:

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

    Set your oven to ${ apple_pie.get_oven_temperature(temperature_type) }
    and let it warm up.

### Extending existing classes

If you want to add a method to an existing **docassemble** class, such
as `Individual`, you do not need to reinvent the wheel.  Just take
advantage of [inheritance].

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

([Try it out here](https://docassemble.org/demo?i=docassemble.demo:data/questions/testattorney.yml){:target="_blank"}.)

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
