---
layout: docs
title: Functions
short_title: Functions
---

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
  I am glad you are a true American
  % endif
{% endhighlight %}

This may be useful in particular circumstances.  Note, however, that
it does not make any change to the variables that are defined.  If the
user refreshes the screen while looking at the `user_is_communist`
question a second time, the interview will not ask the question again.

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

## a_in_the_b

`a_in_the_b('cat', 'hat')` will evaluate to `cat in the hat` if the
language is English.  Other languages will phrase this differently.

## capitalize

If `favorite_food` is defined as "spaghetti marinara," then
`capitalize(favorite_food)` will evaluate to `Spaghetti marinara`.
This is often used when a variable value begins a sentence.  For example:

{% highlight yaml %}
question: |
  ${ capitalize(favorite_food) } is being served for dinner.  Will you
  eat it?
yesno: user_will_eat_dinner
{% endhighlight %}


## comma_and_list

If `things` is a [Python] [list] with the elements
`['lions', 'tigers', 'bears']`, then:

* `comma_and_list(things)` evaluates to `lions, tigers, and bears`.
* `comma_and_list(things, oxford=False)` evaluates to `lions, tigers and bears`.
* `comma_and_list('fish', 'toads', 'frogs')` evaluates to `fish,
toads, and frogs`.
* `comma_and_list('fish', 'toads')` evaluates to `fish and toads`
* `comma_and_list('fish')` evaluates to `fish`.

## comma_list

If `things` is a [Python] [list] with the elements
`['lions', 'tigers', 'bears']`, then:



## currency




## currency_symbol




## do_you




## does_a_b




## force_ask




## get_language




## get_locale




## her




## his




## in_the




## indefinite_article




## need




## nice_number




## noun_plural




## of_the




## ordinal




## period_list




## pickleable_objects




## possessify




## possessify_long




## set_language




## space_to_underscore




## static_image




## the




## titlecase




## underscore_to_space




## url_of




## verb_past




## verb_present




## word




## words




## your



[interview logic]: {{ site.baseurl}}/docs/logic.html
