---
layout: docs
title: Interview logic
short_title: Interview Logic
---

Like [`question`] questions, [`code`] questions are not "asked" unless
they contain variables that **docassemble** needs.  All [`question`] and
[`code`] blocks are only called when and if they are needed.

For your interview to start asking questions, you need to mark at
least one [`question`] block or [`code`] block with the modifier
`mandatory: True`.

# Directives that control interview logic

## <a name="mandatory"></a>`mandatory`

Consider the following as a complete interview file:

{% highlight yaml %}
---
question: What is the capital of Maine?
fields:
  - Capital: maine_capital
---
question: Are you sitting down?
yesno: user_sitting_down
mandatory: True
---
question: Your socks do not match.
mandatory: True
---
{% endhighlight %}

The interview will ask "Are you sitting down" and then it will say
"Your socks do not match."  It will not ask "What is the capital of
Maine?"

Another way to control the logic of an interview is to have a single,
simple `mandatory` [`code`] block that sets the interview in motion.

For example:

{% highlight yaml %}
---
mandatory: True
code: |
  if user_sitting_down:
    user_informed_that_socks_do_not_match
  else:
    user_will_not_sit_down
---
question: What is the capital of Maine?
fields:
  - Capital: maine_capital
---
question: Are you sitting down?
yesno: user_sitting_down
---
question: Your socks do not match.
sets: user_informed_that_socks_do_not_match
---
question: You really should have sat down.
subquestion: I had something important to tell you.
sets: user_will_not_sit_down
---
{% endhighlight %}

Here, the `mandatory` block of [`code`] contains simple [Python] code that
contains the entire logic of the interview.

If a `mandatory` directive is not present, it is treated as `False`.

The value of `mandatory` can be a [Python] expression.  If it is a
[Python] expression, the [`question`] or [`code`] block will be
treated as mandatory if the expression evaluates to a true value.

{% include side-by-side.html demo="mandatory-code" %}

## <a name="initial"></a>`initial`

The `initial` modifier is very similar to [`mandatory`].  It causes a
[`code`] block to be run every time **docassemble** processes your
interview.  [`mandatory`] blocks, by contrast, are never run again if
they are successfully "asked" once.

{% highlight yaml %}
---
initial: True
code: |
  my_counter = 0
---
{% endhighlight %}

## <a name="reconsider"></a>`reconsider`

The `reconsider` modifier can only be used on [`code`] blocks.

If `reconsider` is set to `True`, then **docassemble** will always
"reconsider" the values of any of the variables set by the `code`
block.

That is, every time the interview is assembled (every time the screen
loads) **docassemble** will forget about the value of any of the
variables set by the `code` block.

You will want to set `reconsider` to `True` if your interview flow is
such that you want **docassemble** to reconsider its definition of a
variable based on information that might be gathered in the future.

For example, see if you can find the problem with the interview below.

{% highlight yaml %}
---
code: |
  cat_food_cans_needed = number_of_cats * 4
---
question: |
  Does your neighbor's cat sometimes eat at your house?
subquestion: |
  To feed your own cat, you will need ${ cat_food_cans_needed } cans
  of cat food, but you might need more for your neighbor's cat.
buttons:
  - "Yes":
      code: |
        number_of_cats = number_of_cats + 1
        has_neighboring_cat = True
  - "No":
      code: |
        has_neighboring_cat = False
---
question: How many cats do you have?
fields:
  - Cats: number_of_cats
    datatype: integer
---
question: |
  To feed your cat
  % if has_neighboring_cat:
  and your neighbor's cat
  % endif
  you will need to buy ${ cat_food_cans_needed } cans of cat food.
sets: all_done
---
mandatory: True
code: all_done
{% endhighlight %}

The problem with this interview is that it will compute the number of
cans of cat food needed when it says "To feed your own cat, you will
need . . . cans of cat food," but it will not increase the number of
cans of cat food to account for later-acquired information (i.e. the
fact that the neighbor's cat comes over).  Once `cat_food_cans_needed`
has been defined once, **docassemble** will continue to use that
definition whenever the interview calls for the definition of
`cat_food_cans_needed`.

This problem can be fixed by adding `reconsider: True` to the [`code`]
block:

{% highlight yaml %}
---
code: |
  cat_food_cans_needed = number_of_cats * 4
reconsider: True
---
{% endhighlight %}

The `reconsider` modifier tells **docassemble** to always reconsider
the variables in the [`code`] block.  When the final screen comes up,
**docassemble** will have forgotten about the earlier-defined value of
`cat_food_cans_needed` and will therefore re-define the value by
re-running the [`code`] block.

{% include side-by-side.html demo="reconsider" %}

The `reconsider` modifier is particularly important to use when you
allow interviewees to go back and modify past answers using a
[`review`] block.  For more information about how to implement such
features, see [`review`], [`event`], [`url_action()`], [`process_action()`],
[`action_menu_item()`], and [`menu_items`].

**docassemble** also offers the [`reset` initial block], which has the
same effect as the `reconsider` modifier, but using a different way of
specifying which variables should be reconsidered.  Whether you use
the [`reset` initial block] or the `reconsider` modifier is a question
of what you consider to be more convenient and/or readable.

# <a name="order"></a>The logical order of an interview

[`mandatory`] and [`initial`] blocks are evaluated in the order they
appear in the question file.  Therefore, the location in the interview
of [`mandatory`] and [`initial`] blocks, relative to each other, is
important.

The order in which non-[`mandatory`] and non-[`initial`] questions
appear is usually not important.  If **docassemble** needs a
definition of a variable, it will go looking for a block that defines
the variable.

Consider the following example:

{% include side-by-side.html demo="order-of-blocks" %}

The order of the questions is:

#. Hello!
#. What is your name?
#. What is your favorite food?
#. Do you like penguins?

The first two questions are asked because the corresponding
[`question`] blocks are marked as [`mandatory`].  They are asked in
the order in which they are asked because of the way the [`question`]
blocks are ordered in the [YAML] file.

The next two questions are asked implicitly.  The third and final
[`mandatory`] block makes reference to two variables: `favorite_food`
and `user_likes_penguins`.  Since the [`question`]s that define these
variables are not `mandatory`, they can appear anywhere in the [YAML]
file, in any order you want.  In this case, the `favorite_food`
[`question`] block is at the end of the [YAML] file, and the
`user_likes_penguins` [`question`] block is at the start of the [YAML]
file.

The order in which these two questions are asked is determined by the
order of the variables in the text of the final [`mandatory`]
question.  Since `favorite_food` is referenced first, and
`user_likes_penguins` is referenced afterwards, the user is asked
about food and then asked about penguins.

Note that there is also an extraneous question in the interview that
defines `user_likes_elephants`; the presence of this [`question`]
block in the [YAML] file has no effect on the interview.

Generally, you can order non-[`mandatory`] blocks in your [YAML] file
any way you want.  You may want to group them by subject matter into
separate [YAML] files that you [`include`] in your main [YAML] file.
When your interviews get complicated, there is no natural order to
questions.  In some situations, a question may be asked early, and in
other situations, a question may be asked later.

## Overriding one question with another

The order in which non-[`mandatory`] blocks appear in the [YAML] file
is only important if you have multiple blocks that each offer to
define the same variable.  In that case, the order of these blocks
relative to each other is important.  When looking for blocks that
offer to define a variable, **docassemble** will use later-defined
blocks first.  Later blocks "supersede" the blocks that came before.

This allows you to [`include`] "libraries" of questions in your
interview while retaining the ability to customize how any particular
question is asked.

As explained in the [initial blocks] section, the effect of an
[`include`] block is basically equivalent to copying and pasting the
contents of the included file into the original file.

For example, suppose that there is a [YAML] file called
`question-library.yml`, which someone else wrote, which consists of
the following questions:

{% highlight yaml %}
question: |
  Nice evening, isn't it?
yesno: user_agrees_it_is_a_nice_evening
---
question: |
  Interested in going to the dance tonight?
yesno: user_wants_to_go_to_dance
{% endhighlight %}

You can write an interview that uses this question library:

{% include side-by-side.html demo="use-question-library" %}

When **docassemble** needs to know the definition of
`user_agrees_it_is_a_nice_evening` or `user_wants_to_go_to_dance`, it
will be able to find a block in `question-library.yml` that offers to
define the variable.

Suppose, however, that you thought of a better way to ask the
`user_wants_to_go_to_dance` question, but you don't want to get rid of
`question-library.yml` entirely.  You could override the
`user_wants_to_go_to_dance` question in `question-library.yml` by
doing the following:

{% include side-by-side.html demo="override" %}

This interview file loads the two questions defined in
`question-library.yml`, but then, later in the list of questions,
provides a different way to get the value of
`user_wants_to_go_to_dance`.  When **docassemble** goes looking for a
question to provide a definition of `user_wants_to_go_to_dance`, it
starts with the questions that were defined last, and it will
prioritize your question over the question in `question-library.yml`.
Your [`question`] block takes priority because it is located _later_ in
the [YAML] file.

This is similar to the way law works: old laws do not disappear from
the law books, but they can get superseded by newer laws.  "Current
law" is simply "old law" that has not yet been superseded.

A big advantage of this feature is that you can include "libraries"
written by other people without having to edit those other files in
order to tweak them.  You can use another person's work without taking
on the responsibility of maintaining that person's work over time; you
can just incorporate by reference that person's file, which they
continue to maintain.

For example, if someone else has developed interview questions that
determine a user's eligibility for food stamps, you can incorporate by
reference that author's [YAML] file into an interview that assesses
whether a user is maximizing his or her public benefits.  When the law
about food stamps changes, that author will be responsible for
updating his or her [YAML] file; your interview will not need to
change.  This allows for a division of labor.  All you will need to do
is make sure that the **docassemble** [package] containing the food
stamp [YAML] file gets updated on the server when the law changes.

## Fallback questions

If a more recently-defined [`question`] or [`code`] block does not,
for whatever reason, actually define the variable, **docassemble**
will fall back to a block that is located earlier in the [YAML] file.
For example:

{% include side-by-side.html demo="fallback" %}

In this case, the special [`continue`] choice causes **docassemble**
to skip the [`question`] block and look elsewhere for a definition of
`user_wants_to_go_to_dance`.  **docassemble** will "fall back" to the
version of the question that exists within `question-library.yml`.
When looking for a block that offers to define a variable,
**docassemble** starts at the bottom and works its way up.

Such fall-backs can also happen with [Python] code that could
potentially define a variable, but for whatever reason does not
actually do so.  For example:

{% include side-by-side.html demo="fallback2" %}

In this case, when **docassemble** tries to get a definition of
`user_wants_to_go_to_dance`, it will first try running the [`code`]
block, and then it will encounter `we_already_agreed_to_go` and seek
its definition.  If the value of `we_already_agreed_to_go` turns out
to be false, the [`code`] block will run its course without setting a
value for `user_wants_to_got_to_dance`.  Not giving up,
**docassemble** will keep going backwards through the blocks in the
[YAML] file, looking for one that offers to define
`user_wants_to_got_to_dance`.  It will find such a question among the
questions included by reference from `question_library.yml`, namely
the question "Interested in going to the dance tonight?"

So, to summarize: when **docassemble** considers what blocks it _must_
process, it goes from top to bottom through your interview [YAML]
file, looking for [`mandatory`] and [`initial`] blocks; if a block is
later in the file, it is processed later in time.  However, when
**docassemble** considers what question it should ask to define a
particular variable, it goes from bottom to top; if a block is later
in the file, it is considered to "supersede" blocks that are earlier
in the file.

# <a name="howitworks"></a>How **docassemble** runs your code

**docassemble** goes through your interview [YAML] file from start to
finish, incorporating [`include`]d files as it goes.  It always
executes [`initial`] code when it sees it.  It executes any
[`mandatory`]<span></span> [`code`] blocks that have not been
successfully executed yet.  If it encounters a
[`mandatory`]<span></span> [`question`] that it has not been
successfully asked yet, it will stop and ask the question.

If at any time it encounters a variable that is undefined, for example
while trying to formulate a question, it will interrupt itself in
order to go find the a definition for that variable.

Whenever **docassemble** comes back from one of these excursions to
find the definition of a variable, it does not pick up where it left
off; it starts from the beginning again.

Therefore, when writing code for an interview, you need to keep in
mind that any particular block of code may be re-run from the
beginning multiple times.

For example, consider the following code:

{% highlight yaml %}
---
mandatory: True
code: |
  if user_has_car:
    user_net_worth = user_net_worth + resale_value_of_user_car
    if user_car_brand == 'Toyota':
      user_is_sensible = True
    elif user_car_is_convertible:
      user_is_sensible = False
---
{% endhighlight %}

The intention of this code is to increase the user's net worth by the
resale value of the user's car, if the user has a car.  If the code
only ran once, it would work as intended.  However, because of
**docassemble**'s design, which is to ask questions "as needed," the
code actually runs like this:

1. **docassemble** starts running the code; it encounters
 `user_has_car`, which is undefined.  It finds a question that defines
 `user_has_car` and asks it.  (We will assume `user_has_car` is set to True.)
2. **docassemble** runs the code again, and tries to increment the
 `user_net_worth` (which we can assume is already defined); it
 encounters `resale_value_of_user_car`, which is undefined.  It finds
 a question that defines `resale_value_of_user_car` and asks it.
3. **docassemble** runs the code again.  The value of `user_net_worth`
 is increased.  Then the code encounters `user_car_brand`, which is
 undefined.  It finds a question that defines
 `user_car_brand` and asks it.
4. **docassemble** runs the code again.  The value of `user_net_worth`
 is increased (again).  If `user_car_brand` is equal to "Toyota," then
 `user_is_sensible` is set.  In that case, the code runs successfully
 to the end, and the [`mandatory`] code block is marked as completed, so
 that it will not be run again.
5. However, if `user_car_brand` is not equal to "Toyota," the code
 will encounter `user_car_is_convertible`, which is undefined.
 **docassemble** will find a question that defines
 `user_car_is_convertible` and ask it.  **docassemble** will then run
 the code again, the value of `user_net_worth` will increase yet
 again, and then (finally) the code will run successfully to the end.

The solution here is to make sure that your code is prepared to be
stopped and restarted.  For example, you could have a separate code
block to compute `user_net_worth`:

{% highlight yaml %}
---
mandatory: True
code: |
  user_net_worth = 0
  if user_has_car:
    user_net_worth = user_net_worth + resale_value_of_user_car
  if user_has_house:
    user_net_worth = user_net_worth + resale_value_of_user_house
---
{% endhighlight %}

Note that [`mandatory`] must be true for this to work sensibly.
If this were an optional code block, it would not run to completion
because `user_net_worth` would already be defined when **docassemble**
came back from asking whether the user has a car.

# Best practices for interview logic and organization

* Use only a single [`mandatory`]<span></span> [`code`] block for each
  interview, and put it at the top of the file after the
  [initial blocks].

# Best practices for sharing with others

* Don't reinvent the wheel; [`include`] other people's questions.
* Share your [`question`]s, [`code`], and [`template`]s with others.
* To that end, keep your [`question`] blocks in a separate [YAML] file
  from your [`mandatory`] interview logic, so that other people can
  incorporate your questions without having to edit your work.  Your
  main interview file would consist only of:
    * A [`metadata`] statement saying who you are and what your interview
    is for;
	* A statement to [`include`] your file of questions;
	* Any [`interview help`] blocks;
	* A [`default role`] block, if you use [roles];
	* Any [`initial`] code;
	* Your [`mandatory`] code or questions that set your interview in motion.
* [`include`] other people's question files directly from their
  **docassemble** packages, rather than by copying other people's
  files into your package.  That way, when the other authors make
  improvements to their questions, you can gain the benefit of those
  improvements automatically.
* Don't invent your own scheme for variable names; follow conventions
  and replicate what other people are doing.
* If other people are including your questions and code, avoid
  changing your variable names unnecessarily, or else you will "break"
  other people's interviews.  This does limit your autonomy somewhat,
  but the benefits for the community of interview authors more than
  make up for the loss of autonomy.

[roles]: {{ site.baseurl }}/docs/roles.html
[`continue`]: {{ site.baseurl }}/docs/questions.html#continue
[YAML]: https://en.wikipedia.org/wiki/YAML
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`code`]: {{ site.baseurl }}/docs/code.html
[`mandatory`]: #mandatory
[`initial`]: #initial
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[`interview help`]: {{ site.baseurl }}/docs/initial.html#interview help
[`default role`]: {{ site.baseurl }}/docs/initial.html#default role
[`template`]: {{ site.baseurl }}/docs/template.html
[`event`]: {{ site.baseurl }}/docs/fields.html#event
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`action_menu_item()`]: {{ site.baseurl }}/docs/functions.html#action_menu_item
[`menu_items`]: {{ site.baseurl }}/docs/special.html#menu_items
[`review`]: {{ site.baseurl }}/docs/fields.html#menu_items
[`reset` initial block]: {{ site.baseurl }}/docs/initial.html#reset
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[package]: {{ site.baseurl }}/docs/packages.html
