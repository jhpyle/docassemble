---
layout: docs
title: Functions
short_title: Functions
---

# How to use functions

To use the functions described in this section in your interviews, you
need to include them from the `docassemble.base.util` module by
writing the following somewhere in your interview:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
{% endhighlight %}

Unless otherwise instructed, you can assume that all of the functions
discussed in this section are available in interviews when you include
this `modules` block.

# Miscellaneous functions

## need

The `need()` function takes one or more variables as arguments and
causes **docassemble** to ask questions to define each of the
variables if the variables are not already defined.

For example, this `mandatory` code block expresses [interview logic]
requiring that the user first be shown a splash screen and then be
asked questions necessary to get to the end of the intererview.

{% highlight yaml %}
---
mandatory: true
code: |
  need(user_shown_splash_screen, user_shown_final_screen)
---
{% endhighlight %}

This happens to be 100% equivalent to writing:

{% highlight yaml %}
---
mandatory: true
code: |
  user_shown_splash_screen
  user_shown_final_screen
---
{% endhighlight %}

So the `need()` function does not "do" anything.  However, writing
`need()` functions in your code probably makes your code more readable
because it helps you convey in "natural language" that your interview
"needs" these variables to be defined.

## force_ask 

Usually, **docassemble** only asks a question when it encounters a
variable that is not defined.  However, with the `force_ask` function
from `docassemble.base.util`, you can cause such a condition to happen
manually, even when a variable is already defined.

In this example, we use `force_ask` to cause **docassemble** to ask a
question that has already been asked.

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
question: |
  Are you a communist?
yesno: user_is_communist
---
mandatory: true
code: |
  if user_is_communist and user_reconsidering_communism:
    user_reconsidering_communism = False
    force_ask('user_is_communist')
---
question: |
  I suggest you reconsider your answer.
field: user_reconsidering_communism
---
mandatory: true
question: |
  % if user_is_communist:
  I am referring your case to Mr. McCarthy.
  % else:
  I am glad you are a true American.
  % endif
{% endhighlight %}

This may be useful in particular circumstances.  Note, however, that
it does not make any change to the variables that are defined.  If the
user refreshes the screen while looking at the `user_is_communist`
question a second time, it will be as though `force_ask` never
happened.

Note also that no code that comes after `force_ask` will ever be
executed.  That is why, in the example above, we set
`user_reconsidering_communism` to False before calling `force_ask`.
The variable `user_reconsidering_communism`, which had been set to
True by the "I suggest you reconsider your answer" question, is set to
False before the call to `force_ask` so that the `mandatory` code
block does not get stuck in an infinite loop.

A different way to reask a question is to use the built-in Python
operator `del`.  This makes the variable undefined.  Instead of
writing:

{% highlight python %}
if user_is_communist and user_reconsidering_communism:
  user_reconsidering_communism = False
  force_ask('user_is_communist')
{% endhighlight %}

we could have written:

{% highlight python %}
if user_is_communist and user_reconsidering_communism:
  user_reconsidering_communism = False
  del user_is_communist
  need(user_is_communist)
{% endhighlight %}

This will also cause the `user_is_communist` question to be asked
again.  This is more robust than using `force_ask` because the user
cannot get past the question simply by refeshing the screen.  (By the
way, `need(user_is_communist)` could be left out here because the
second mandatory code block would cause the question to be asked
again.  But you make your intentions more clear to readers of your
code by calling `need()`.)

## space_to_underscore

If `user_name` is `John Wilkes Booth`,
`space_to_underscore(user_name)` will return `John_Wilkes_Booth`.
This is useful if you do not want spaces in the filenames of your
[attachments]\:

{% highlight yaml %}
---
sets: user_done
question: Thanks!
subquestion: Here is your letter.
attachment:
  - name: A letter for ${ user_name }
    filename: Letter_for_${ space_to_underscore(user_name) }
    content file: letter.md
---
{% endhighlight %}

## url_of

This function returns a URL to a file within a **docassemble**
package.

For example, you might have PDF files associated with your interview.
You would keep these in the `data/static` directory of your package,
and you would refer to them by writing something like:

{% highlight yaml %}
---
sets: user_done
question: You are done.
subquestion: |
  To learn more about this topic, read
  [this brochure](${ url_of('docassemble.mycompany:data/static/brochure.pdf') }).
---
{% endhighlight %}

## url_action and process_action

The `url_action()` and `process_action()` functions allow users to
interact with **docassemble** using hyperlinks embedded in questions.

`url_action()` returns a URL that, when clicked, will perform an
action within **docassemble**, such as running some code or asking a
question.  Typically the URL will be part of a [Markdown] link inside
of a [question], or in a `note` within a set of [fields].

In order for the action to be performed, you need to create a block of
`initial` code containing the command `process_action(current_info)`.
The action will be carried out by this function.

Here is an example:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
initial: true
code: |
  process_action(current_info)
---
mandatory: true
code: |
  if lucky_information_confirmed:
    need(final_screen)
---
field: lucky_information_confirmed
question: |
  Please confirm the following information.
subquestion: |
  Your lucky number is ${ lucky_number }.
  [Increase](${ url_action('set_number_event', increment=1) })
  [Decrease](${ url_action('set_number_event', increment=-1) })

  Also, your lucky color is ${ lucky_color }.
  [Edit](${ url_action('lucky_color') })
---
question: What is your lucky color?
fields:
  - Color: lucky_color
---
sets: final_screen
question: Thank you
subquestion: |
  You have confirmed that your lucky color is ${ lucky_color }
  and your lucky number is ${ lucky_number }.
buttons:
  - Restart: restart
---
event: set_number_event
code: |
  lucky_number += current_info['arguments']['increment']
---
code: |
  lucky_number = 2
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/testaction.yml){:target="_blank"}.)

When the user clicks one of the links, the interview will load as
usual (much as if the user refreshed the web browser page).  The only
difference is that **docassemble** sees the additional information
stored in the URL and makes that information available to the
interview by storing it in the `current_info` [dictionary].

In the above example, when the user clicks on the link generated by
`url_action('lucky_color')`, the interview will load and
**docassemble** will process the `initial` code block, which runs the
function `process_action(current_info)`.  The `process_action`
function looks in `current_info` and sees that there was a URL
"action" called 'lucky_color'.  It will look for a `question` or
`code` block that defines `lucky_color`.  (It calls `force_ask`,
explained above.)  Since there is a question in the interview that
defines `lucky_color`, that question will be asked.

When the user clicks on the link generated by
`url_action('set_number_event', increment=1)`, the
`process_action(current_info)` function will look for a `question` or
`code` block that defines `set_number_event`.  It will find the `code`
block that was labeled with `event: set_number_event`.  (See
[Setting Variables] for more information about `event`s.)  It will
then run that code block.  Note how the [Python] code within that
block knows the value of `increment` specified in the `url_action`
function: the value is stored in
`current_info['arguments']['increment']`.

The `process_action` function will do nothing if the user did not
click on a link generated by `url_action`.

You can pass as many named parameters as you like to an "action."  For
example:

{% highlight yaml %}
---
question: Hello
subquestion: |
  You can set lots of information by [clicking this link](${
  url_action('set_stuff', fish='trout', berry='strawberry',
  money=65433, actor='Will Smith')}).
---
event: set_stuff
code: |
  user_favorite_fish = current_info['arguments']['fish']
  user_favorite_fruit = current_info['arguments']['berry']
  if current_info['arguments']['money'] > 300000:
    user_is_rich = True
  actor_to_hire = current_info['arguments']['actor']
---
{% endhighlight %}

You can control whether and when the "action" will be performed by
placing the `process_action(current_info)` statement in a particular
place in your `initial` code.  For example, you might want to ensure
that actions can only be carried when the user is logged in:

{% highlight yaml %}
---
initial: true
code: |
  if current_info['user']['is_authenticated']:
    process_action(current_info)
---
{% endhighlight %}

## prevent_going_back

**docassemble**'s back button helps users when they make a mistake and
want to go back and correct it.  But sometimes, we want to prevent
users from going back.  For example, if the interview code causes an
e-mail to be sent, or data to be written to a database, allowing the
user to go back and do the process again would create confusion.

You can call `prevent_going_back()` to instruct the web application to
prevent the user from going back past that point.  See also the
[modifier] of the same name.

# Functions for managing global variables

If you try writing your own functions, you will learn that functions
do not have access to all of the variables in your interview.
Functions only know the variables you pass to them.

If your functions need to know background information about the
interview, but you do not want to have to pass a lot of variables to
every function you call, you can use "global" variables.

You set "global" variables in **docassemble** by calling `set_info()`
and your retrieve them by calling `get_info()`.  Note that
**docassemble** will forget the values of these variables every time
the screen loads, so you will have to make sure they are set by
setting them in `initial` code, which runs every time the screen
loads.

## set_info

This function is used to store information for later retrieval by
`get_info()`.  You pass it one or more [keyword arguments]:

{% highlight yaml %}
---
initial: true
code: |
  set_info(interview_type='standard')
---
{% endhighlight %}

## get_info

This function is used to retrieve information passed to
`set_info()`.

For example, if you passed `interview_type` as a [keyword argument] to
`set_info()`, you can retrieve the value in your [Python module] by
doing:

{% highlight python %}
from docassemble.base.legal import *

class Recipe(DAObject):
    def difficulty_level(self):
        if get_info('interview_type') == 'standard':
            #etc.
{% endhighlight %}

If the item was never set, `get_info()` will return `None`.

# Language and locale functions

These functions access and change the active language and locale.  See
[language support] for more information about these features of
**docassemble**.

## get_language

If the language is set to English, `get_language()` returns `en`.

## set_language

This sets the language that will be used in the web application and in
language-specific functions of **docassemble**.  It does not change
the active [Python locale].  See `update_locale()` for information on
changing the [Python locale].

If you need to set the language to something other than the language
set in the [configuration], you need to call `set_language()` within
`initial` code.  For example:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
initial: true
code: |
  set_language(user_language)
---
question: |
  What language do you speak? (¿Qué idioma habla?)
field: user_language
choices:
  - English: en
  - Español: es
---
{% endhighlight %}

## get_locale

If the locale is set to `US.utf8`, `get_locale()` returns `US.utf8`.

## set_locale

If you run `set_locale('FR.utf8')`, then `get_locale()` will return
`FR.utf8`, but the actual [Python locale] will not change
unless you run `update_locale()`.

## update_locale

Running `update_locale` will change the [Python locale] based on the
current language and locale settings.

For example, if you run:

{% highlight python %}
import docassemble.base.util
docassemble.base.util.set_language('fr')
docassemble.base.util.set_locale('FR.utf8')
docassemble.base.util.update_locale()
{% endhighlight %}

then the [Python locale] will be changed to `fr_FR.utf8`.

Running `update_locale()` is necessary in order to affect the behavior
of functions like `currency()` and `currency_symbol()`.

Note that changes to the locale are not thread-safe.  This means that
there is a risk that between the time **docassemble** runs
`update_locale()` and the time it runs `currency_symbol()`, another
user on the same server may cause **docassemble** to run
`update_locale()` and change it to the wrong setting.

If you want to host different interviews that use different locale
settings on the same server (e.g., to format a numbers as 1,000,000 in
one interview, but 1.000.000 in another), you will need to make sure
you run the **docassemble** web server in a multi-process,
single-thread configuration.  (See [installation] for instructions on
how to do that.)  Then you would need to begin each interview with
`initial` code such as:

{% highlight yaml %}
---
initial: true
code: |
  import docassemble.base.util
  docassemble.base.util.set_language('fr')
  docassemble.base.util.set_locale('FR.utf8')
  docassemble.base.util.update_locale()
---
{% endhighlight %}

# Simple translation of words

## word

`word()` is a general-purpose translation function that is used in the
code of the web application to ensure that the text the user sees is
translated into the user's language.

`word("fish")` will return `fish` unless
`docassemble.base.util.update_word_collection()` has been used to
define a different translation for the current language.

The following [Python interpreter] session demonstrates how it works:

{% highlight python %}
>>> from docassemble.base.util import *
>>> set_language('es')
>>> word("fish")
u'fish'
>>> import docassemble.base.util
>>> docassemble.base.util.update_word_collection('es', {'fish': 'pescado'})
>>> word("fish")
u'pescado'
>>> set_language('en')
>>> word("fish")
u'fish'
{% endhighlight %}

In your own [Python] code you may wish to use `word()` to help make
your code multi-lingual.

It is not a good idea to call
`docassemble.base.util.update_word_collection()` in interviews.  You
can use it in [Python] modules, but keep in mind that the changes you
make will have global effect within the [WSGI] process.  If other
interviews on the server define the same word translations for the
same language using `docassemble.base.util.update_word_collection()`,
the module that happened to load last will win, and the results could
be unpredictable.

The best practice is to load translations at the server level by using
the `words` [configuration] directive to load translations from one or
more [YAML] files.  This causes **docassemble** to call
`docassemble.base.util.update_word_collection()` at the time the
server is initialized.

# Language-specific functions

These functions behave differently according to the language and
locale.  You can write functions for different languages, or reprogram
the default functions, by calling
`docassemble.base.util.update_language_function()`.

## capitalize

If `favorite_food` is defined as "spaghetti marinara," then
`capitalize(favorite_food)` will return `Spaghetti marinara`.
This is often used when a variable value begins a sentence.  For example:

{% highlight yaml %}
question: |
  ${ capitalize(favorite_food) } is being served for dinner.  Will you
  eat it?
yesno: user_will_eat_dinner
{% endhighlight %}

There is also the `title_case()` function, which is described below.

## comma_and_list

If `things` is a [Python list] with the elements
`['lions', 'tigers', 'bears']`, then:

* `comma_and_list(things)` returns `lions, tigers, and bears`.
* `comma_and_list(things, oxford=False)` returns `lions, tigers and bears`.
* `comma_and_list('fish', 'toads', 'frogs')` returns `fish,
toads, and frogs`.
* `comma_and_list('fish', 'toads')` returns `fish and toads`
* `comma_and_list('fish')` returns `fish`.

## comma_list

If `things` is a [Python list] with the elements
`['lions', 'tigers', 'bears']`, then `comma_list(things)` will return
`lions, tigers, bears`.

## currency

If the locale is `US.utf8`, `currency(45.2)` returns `$45.20`.

`currency(45)` returns `$45.00`, but `currency(45, decimals=False)`
returns `$45`.

With `decimals` unset or equal to `True`, this function uses the
`locale` module to express the currency.  However, `currency(x,
decimals=False)` will simply return `currency_symbol()` followed by
`x` formatted as an integer, which might not be correct in your
locale.  This is due to a limitation in the [locale module].  If the
`currency` function does not meet your currency formatting needs, you
may want to define your own.

## currency_symbol

If the locale is `US.utf8`, `currency_symbol()` returns `$`.

The locale can be set in the [configuration] or through the
`set_locale()` function.

If you set `currency symbol` in the [configuration], then
`currency_symbol()` returns the symbol specified there, and does not
use the locale to determine the symbol.

## indefinite_article

`indefinite_article('bean')` returns `a bean` and
`indefinite_article('apple')` returns `an apple`.

The English language version of this function passes through all
arguments to the `en.noun.article()` function of the
[NodeBox English Linguistics Library].

## nice_number

* `nice_number(4)` returns `four`
* `nice_number(10)` returns `ten`
* `nice_number(11)` returns `11`
* `nice_number(-1)` returns `-1`

This function can be customized by calling
`docassemble.base.util.update_nice_numbers()`.

## noun_plural

* `noun_plural('friend')` returns `friends`
* `noun_plural('fish')` returns `fish`
* `noun_plural('moose')` returns `mooses`

The English language version of
this function passes through all arguments to the `en.noun.plural()`
function of the [NodeBox English Linguistics Library].

## ordinal_number

* `ordinal_number(8)` returns `eighth`.
* `ordinal_number(11)` returns `11th`.

This function can be customized with
`docassemble.base.util.update_ordinal_numbers()` and
`docassemble.base.util.update_ordinal_function()`.

## ordinal

`ordinal(x)` returns `ordinal_number(x + 1)`.  This is useful when
working with indexes that start at zero.

## period_list

`period_list` returns a list within a list:

{% highlight python %}
[[12, "Per Month"], [1, "Per Year"], [52, "Per Week"],
[24, "Twice Per Month"], [26, "Every Two Weeks"]]
{% endhighlight %}

This is useful for using in `code` associated with periodic currency
amounts.

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
question: |
  Your income
subquestion: |
  You earn ${ currency(user_income_amount * user_income_period) }
  per year.
mandatory: true
---
question: |
  What is your income?
fields:
  - Income: user_income_amount
    datatype: currency
  - Period: user_income_period
    datatype: number
    code: |
      period_list()
---
{% endhighlight %}

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/income.yml){:target="_blank"}.)

The text in the default `period_list()` function can be translated to
different languages using the
`docassemble.base.util.update_word_collection()` function.  If you
want to customizes the choices available, you can override the default
function by including something like the following in your
[Python module]:

{% highlight python %}
def my_period_list():
  return [[365, word("Per Day")], [52, word("Per Week")]]

docassemble.base.util.update_language_function('*', 'period_list', my_period_list)
{% endhighlight %}

## title_case

`title_case("the importance of being ernest")` returns `The Importance
of Being Ernest`.

The default version of this function passes through all arguments to
the `titlecase()` function of the [titlecase] module.

There is also the `capitalize()` function, which is described above.

## verb_past

`verb_past('help')` returns `helped`.  The English language version of
this function passes through all arguments to the `en.verb.past()`
function of the [NodeBox English Linguistics Library].

## verb_present

* `verb_present('helped')` returns `help`.
* `verb_present('help', person=3)` returns `helps`.

The English language version of this function passes through all
arguments to the `en.verb.present()` function of the
[NodeBox English Linguistics Library].

# Simple language functions

The following simple language functions all have the property that if
the optional argument `capitalize=True` is added, the resulting phrase
will be capitalized.

* `her('turtle')` returns `her turtle`.
* `her('turtle', capitalize=True)` returns `Her turtle`.
* `his('turtle')` returns `his turtle`.
* `a_in_the_b('cat', 'hat')` returns `cat in the hat`.
* `do_you('smoke')` returns `do you smoke`.
* `does_a_b('Fred', 'smoke')` returns `does Fred smoke`.
* `in_the('house')` returns `in the house`.
* `of_the('world')` returns `of the world`.
* `possessify('Fred', 'cat')` returns `Fred's cat`.
* `possessify_long('Fred', 'cat')` returns `the cat of Fred`.
* `the('apple')` returns `the apple`.

Note that unlike other functions in `docassemble.base.util`, these
functions are *not* available for use within interviews.  If you do:

{% highlight yaml %}
modules:
  - docassemble.base.util
{% endhighlight %}

you will *not* be able to write things like `${ her('dog') }`.

These functions are intended to be used from within [Python modules], where you
can import them by doing:

{% highlight python %}
from docassemble.base.util import his, her
{% endhighlight %}

You can customize the functions for different languages:

{% highlight python %}
def her_fr(word, capitalize=False):
  if capitalize:
    return 'Sa ' + word
  else:
    return 'sa ' + word
docassemble.base.util.update_language_function('fr', 'her', her_fr)
{% endhighlight %}

Or, you can accomplish the same result with a handy function generator
from `docassemble.base.util`:

{% highlight python %}
docassemble.base.util.update_language_function('fr', 'her', docassemble.base.util.prefix_constructor('sa '))
{% endhighlight %}

[interview logic]: {{ site.baseurl}}/docs/logic.html
[Python list]: https://docs.python.org/2/tutorial/datastructures.html
[Python module]: https://docs.python.org/2/tutorial/modules.html
[Python modules]: https://docs.python.org/2/tutorial/modules.html
[configuration]: {{ site.baseurl}}/docs/config.html
[installation]: {{ site.baseurl}}/docs/installation.html
[Python interpreter]: https://docs.python.org/2/tutorial/interpreter.html
[attachments]: {{ site.baseurl}}/docs/documents.html
[language support]: {{ site.baseurl}}/docs/language.html
[Python locale]: https://docs.python.org/2/library/locale.html
[locale module]: https://docs.python.org/2/library/locale.html
[NodeBox English Linguistics Library]: https://www.nodebox.net/code/index.php/Linguistics
[titlecase]: https://pypi.python.org/pypi/titlecase
[Markdown]: https://daringfireball.net/projects/markdown/
[fields]: {{ site.baseurl}}/docs/fields.html
[question]: {{ site.baseurl}}/docs/questions.html
[roles]: {{ site.baseurl}}/docs/roles.html
[dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[Setting Variables]: {{ site.baseurl}}/docs/fields.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[YAML]: https://en.wikipedia.org/wiki/YAML
[keyword arguments]: https://docs.python.org/2/glossary.html#term-argument
[keyword argument]: https://docs.python.org/2/glossary.html#term-argument
[modifier]: {{ site.baseurl}}/docs/modifiers.html
