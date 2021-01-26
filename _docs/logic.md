---
layout: docs
title: Interview logic
short_title: Interview Logic
---

# <a name="intro"></a>Introduction

Unlike other guided interview systems, in which the interview developer
maps out a decision tree or flowchart to indicate which questions
should be asked and in which order, **docassemble** implicitly figures
out what questions to ask and when to ask them.

For example, if the point of your interview is to assemble a document,
and one of the fields in the document is the user's Social Security
Number (SSN), the interview will ask the user for his or her SSN;
**docassemble** does not need to be told to ask for the SSN.

However, if your document only displays the SSN conditionally,
**docassemble** will only ask for the SSN if that condition is met.
For example, your document template might include:

{% highlight text %}
The petitioner is ${ petitioner }.  Petitioner is a
% if petitioner.is_citizen:
citizen of the United States.
Petitioner's SSN is ${ petitioner.ssn }.
% else:
lawful resident of the United States.
% endif
{% endhighlight %}

This will cause the interview to ask for the petitioner's name and
whether the petitioner is a citizen, because that information is
necessary.  The interview will ask for the SSN only if the petitioner
is a citizen.

In other guided interview systems, the logic of the document assembly
is separate from the logic that determines what interview questions
are asked.  In the case of the template above, the dependence of the
SSN on citizenship would need to be mapped out both in the document
and in the specification of the interview questions.  In
**docassemble**, however, the logic of the interview is determined
implicitly from the requirements of the end result (in this case, a
document).  So the logic only needs to be specified in one place.

# <a name="endgoals"></a>End goals and the satisfaction of prerequisites

By default, all questions in a **docassemble** interview are asked
only if and when they are needed.

However, in order to start asking questions, **docassemble** needs to
be given some direction.  You need to provide this direction by
marking at least one [`question`] block or [`code`] block as
[`mandatory`] (or one [`code`] block as [`initial`]).

If **docassemble** does not know what question to ask, it will give
you an error that looks like this:

{% include side-by-side.html demo="no-mandatory" %}

To prevent this error in this interview, we can mark as `mandatory`
the final `question` block -- the screen that is the endpoint for the
interview.

{% include side-by-side.html demo="with-mandatory" %}

Now **docassemble** knows what to do: it needs to present the final
screen.

Note that the two questions in the interview ("How are you doing?"
and "What is your favorite color?") were not marked as `mandatory`,
but are nevertheless still asked during the interview.  Since the text
of the final `question` depends on the answers to these questions, the
questions are asked automatically.  The order in which the questions
are asked depends on the order in which **docassemble** needs the
answers (not the order in which the questions appear in the
interview text).

The interview above effectively tells **docassemble** the following:

1. If a definition of `how_doing` is needed, but `how_doing` is
   undefined, you can get a definition of `how_doing` by asking the "How
   are you doing?" question.
2. If a definition of `favorite_color` is needed, but `favorite_color`
   is undefined, you can get a definition of `favorite_color` by
   asking the "What is your favorite color?" question.
3. You must present the "Your favorite color is . . ."  screen to the
   user.

Here is what happens in this interview:

1. The user clicks on a link and goes to the **docassemble** interview.
1. **docassemble** tries to present the "Your favorite color is . . ."
   screen to the user.
2. **docassemble** realizes it needs the definition of the
   `favorite_color` variable, but it is undefined, so it asks the
   "What is your favorite color?" question.
3. When the user answers the question, the variable `favorite_color`
   is set to the user's answer.
4. **docassemble** again tries to present the "Your favorite color is
   . . ." screen to the user.
5. **docassemble** realizes it needs the definition of the `how_doing`
   variable, but it is undefined, so it asks the "How
   are you doing?" question.
6. When the user answers the question, the variable `how_doing`
   is set to the user's answer.
7. **docassemble** again tries to present the "Your favorite color is
   . . ." screen to the user.
8. **docassemble** does not encounter any undefined variables, so it
   is able to present the "Your favorite color is . . ." screen to
   the user.
9. The interview is now over because the "Your favorite color is
   . . ."  screen does not allow the user to press any buttons to move
   forward.

By making only the final screen `mandatory`, this interview takes
advantage of **docassemble**'s feature for automatically satifying
prerequisites.  The developer simply needs to provide a collection of
questions, in any order, and **docassemble** will figure out if and
when to ask those questions, depending on what is necessary during any
given interview.

Alternatively, you could make every question `mandatory`:

{% include side-by-side.html demo="all-mandatory" %}

Here is what happens in this version of the interview:

1. The user clicks a link to the **docassemble** interview.
2. **docassemble** presents the mandatory "How are you doing?"
   question to the user.
3. When the user answers the question, the variable `how_doing`
   is set to the user's answer.
4. **docassemble** presents the mandatory "What is your favorite color?"
   question to the user.
5. When the user answers the question, the variable `favorite_color`
   is set to the user's answer.
6. **docassemble** presents the mandatory "Your favorite color is
   . . ." screen to the user.  It does not need to ask any questions
   because the variables this screen depends on, `favorite_color` and
   `how_doing`, are already defined.

The approach of marking everything as `mandatory` bypasses
**docassemble**'s process of automatically satisfying prerequisites.

When interview developers first start using **docassemble**, they tend to
use the approach of marking all questions as `mandatory` and listing
them one after another.  For simple, linear interviews, this approach
is attractive; it gives the developer tight control over the interview
flow.

But what if there are questions that only need to be asked in certain
circumstances?  If you make all the questions `mandatory`, some of
your users will spend time providing information that is never used.

Furthermore, when the complexity of your interview increases, you will
find that the questions can no longer be represented in a simple
linear list, because your interview has branching paths.

And as the complexity increases even more, you will find that the
questions cannot even feasibly be represented in a flowchart, because
any flowchart that can accommodate every possible path of a
complicated interview would look like a plate of spaghetti.

The automatic satisfaction of prerequisites is a powerful feature of
**docassemble**.  It allows interview developers to build any level of
complexity into their interviews.  It frees the developer from having to
envision all of the possible paths that could lead to the endpoint of
an interview.  This allows the interview developer to concentrate on the
substance of the interview's end goal rather than the process of
gathering the information.

The most "scalable" approach to building an interview is to allow
**docassemble**'s prerequisite-satisfying algorithm to do the heavy
lifting.  This means using `mandatory` as little as possible.

## <a name="changeorder"></a>Changing the order of questions

You may encounter situations where you don't like the order
in which **docassemble** asks questions.  You can always tweak the
order of questions.  For example, suppose you want to make sure that
your interview asks "How are you doing?" as the first question, rather
than "What is your favorite color?"

One approach to change the order of questions is to use the
[`need` specifier] (explained in more detail [below](#need)):

{% include side-by-side.html demo="with-mandatory-tweak-a" %}

In this example, the [`need` specifier] says that before can present
the "Your favorite color is . . ."  screen to the user, it needs to
make sure that the variables `how_doing` and `favorite_color` are
defined.  It also indicates that **docassemble** should seek the
definitions of these variables in a specific order.  Thus, "How are
you doing?" is asked first.

Another approach to tweaking the order of questions is to use a
[`code`] block as the single `mandatory` block that will control the
course of the interview.

{% include side-by-side.html demo="with-mandatory-tweak-b" %}

In this example, the [`code`] block effectively tells **docassemble**:

1. Before doing anything else, make sure that `how_doing` is defined.
2. Next, do what is necessary to show the [special screen] called
   `final_screen`.

The prerequisite-satisfying process also works with [`code`] blocks.

{% include side-by-side.html demo="code" %}

In this example, when **docassemble** seeks the definition of
`fruits`, it sees that it will find it by running the [`code`] block.
When it tries to run this block, it will find that it does not know the
definition of `peaches`, so it will ask a question to gather it.  Then
it will find that it does not know the definition of `pears`, so it
will ask a question to gather it.

There are two important things to know about how **docassemble**
satisfies prerequisites.

First, remember that **docassemble** asks questions when it encounters
a variable that is _undefined_.  In the above example, if `fruits` had
already been defined, **docassemble** would not have run the [`code`]
block; it would have proceeded to display the final screen.  There are
some exceptions to this.  The [`reconsider`] specifier [discussed
below](#reconsider) is one such exception; the [`force_ask()`]
function is another.

Second, note that the process of satisfying a prerequisite is
triggered whenever **docassemble** needs to know the value of a variable,
but finds the variable is undefined.  If you write [Python] code
(which is what [`code`] blocks are), keep in mind that under the rules
of [Python], the mere mention of a variable name can trigger the
process.

Suppose that in the example above, the [`code`] block was the following:

{% highlight yaml %}
---
code: |
  fruit = peaches + pears
  apples
---
{% endhighlight %}

The statement `apples` does not "do" anything -- it is just a
reference to a variable -- but it is still part of the [Python] code,
and the [Python] interpreter will evaluate it.  If [Python] finds that
the variable is undefined, the prerequisite-satisfying process will be
triggered.

On the other hand, if `apples` is placed in a context that the
[Python] interpreter will not evaluate, the prerequisite-satisfying
process will not be triggered.

{% highlight yaml %}
---
code: |
  fruit = peaches + pears
  if fruit > 113121:
    apples
---
{% endhighlight %}

In this case, [Python] will not "need" the value of `apples` unless
the number of peaches and pears exceeds 113,121, so the mention of
`apples` does not necessarily trigger the asking of a question.

## <a name="singlecode"></a>Specifying the logic of an interview in one place

A useful technique for managing complex interview logic is to use a
single [`mandatory`]<span></span> [`code`] block to drive the logic of
your interview.

{% include demo-side-by-side.html demo="single-code" %}

In this example:
* When **docassemble** tries to run the [`mandatory`]<span></span>
  [`code`] block, it encounters an undefined variable `likes_fruit`,
  so it gets its definition by asking "Do you like fruit?"
* If the user answers "Yes," `likes_fruit` is set to `True`.  Now,
  when **docassemble** tries to run the [`mandatory`]<span></span>
  [`code`] block, it will know that `likes_fruit` is true, so it will
  evaluate the code underneath the `if` statement.  The first variable
  it encounters is `favorite_fruit`, which is undefined.  So
  **docassemble** will stop evaluating the [`code`] block and will ask
  the question "What is your favorite fruit?" in order to get a
  definition of `favorite_fruit`.
* The next time around, **docassemble** will get past `likes_fruit`
  and `favorite_fruit`, but then it will try to evaluate `if
  puts_fruit_in_smoothies:` and it will stop because
  `puts_fruit_in_smoothies` is undefined.  So it will ask the user "Do
  you like to put fruit in smoothies?"  Suppose the user answers "No."
  In that case, `puts_fruit_in_smoothies` will be set to `False`.
* The next time around, **docassemble** will get past `likes_fruit`
  and `favorite_fruit`, and when it reaches `if
  puts_fruit_in_smoothies:`, it will know that
  `puts_fruit_in_smoothies` is false, so it will not try to evaluate
  the code under the `if` statement.  It will proceed to the end of
  the `code` block, where there is a reference to the variable
  `final_screen`.  It will seek a definition of `final_screen` and it
  will "ask" the `question` that is marked with `event: final_screen`
  (which results in a screen with no buttons that says "Thanks for
  that information."  However, this `question` is not actually capable
  of setting the `final_screen` variable; it is just an endpoint
  screen.
* If the user had answered "No" to the original question "Do you like
  fruit?" then the variable `likes_fruit` would be set to `False`, and
  **docassemble** would have skipped the whole line of questioning
  about fruit.  It would have proceeded to evaluate the code under the
  `else:` line.  It would have encountered the undefined variable
  `favorite_vegetable`.  Thus it would have asked the question "Well,
  since you don't like fruit, what is your favorite vegetable?"  Once
  `favorite_vegetable` gets populated with the user's favorite
  vegetable, the logic is done except for the reference to
  `final_screen`, which will never be defined, and the only thing the
  user can do is look at the screen that says "Thanks for that
  information."

Trying to specify the complete logic of your interview in a
[`mandatory`]<span></span> [`code`] block could become tiresome.  On
the other hand, relying completely on **docassemble**'s automatic
prerequisite-satisfying mechanism could be confusing because you would
need to follow a trail of variable references through your whole
[YAML] file.  Typically it makes sense to use a technique that is
somewhere between these two extremes; you don't have to specify in
your [`code`] block every single variable that your interview might
gather, but you can specify the important ones, and trust the automatic
prerequisite-satisfying mechanism to trigger the gathering of the rest
of the variables.

# <a name="specifiers"></a>Specifiers that control interview logic

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

Here, the single `mandatory` block contains simple [Python] code that
contains the entire logic of the interview.

If a `mandatory` specifier is not present within a block, it is as
though `mandatory` was set to `False`.

The value of `mandatory` can be a [Python] expression.  If it is a
[Python] expression, the [`question`] or [`code`] block will be
treated as mandatory if the expression evaluates to a true value.

{% include side-by-side.html demo="mandatory-code" %}

It is a best practice to tag all `mandatory` blocks with an [`id`].

## <a name="initial"></a>`initial`

The `initial` modifier is very similar to [`mandatory`].  It can only
be used on a [`code`] block.  It causes the [`code`] block to be run
every time **docassemble** processes your interview (i.e., every time the
screen loads during an interview).  [`mandatory`] blocks, by contrast,
are never run again during the session if they are successfully
"asked" once.

{% include side-by-side.html demo="initial" %}

Note in this example that from screen to screen, the `counter`
increments from 1 to 2 and then to 4.  The counter does not count the
number of screens displayed, but rather the number of times the
interview logic was evaluated.  The "passes" through the interview are:

1. The interview logic is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The interview then
   tries to run the `code` block to get `fruit`, but encounters an
   undefined variable `peaches`, so it asks a question to gather
   `peaches`.
2. The interview logic is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The interview then
   tries to run the `code` block to get `fruit`, but encounters an
   undefined variable `pears`, so it asks a question to gather
   `pears`.
3. The interview logic is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The interview then runs
   the `code` block, and this time, `fruit` is successfully defined.
4. The interview logic is evaluated again, and the final question is
   displayed.

Like [`mandatory`], `initial` can be set to `True`, `False`, or to
[Python] code that will be evaluated to see whether it evaluates to a
true or false value.

`initial` blocks are useful in a variety of contexts:

* When you are using a [multi-user interview] and you want to set
  interview variables to particular values depending on the user who
  is currently using the interview.
* When you are using the [actions] feature and you want to make sure
  the [actions] are processed only in particular circumstances.

## <a name="need"></a>`need`

The `need` specifier allows you to manually specify the prerequisites
of a [`question`] or [`code`] block.  This can be helpful for tweaking
the order in which questions are asked.

{% include side-by-side.html demo="need-specifier" %}

In this example, the ordinary course of the interview logic would ask
"What is your favorite animal?" as the first question.  However,
everyone knows that the first question you should ask of a child is
"How old are you?"  The `need` specifier indicates that before
**docassemble** should even try to present the "Thank you for that
information" screen, it should ensure that `number_of_years_old` old
is defined, then ensure that `favorite_animal`, and then try to
present the screen.

The variables listed in a `need` specifier do not have to actually be
used by the question.  Also, if your question uses variables that are
not mentioned in the `need` list, **docassemble** will still pursue
definitions of those variables.

## <a name="depends on"></a>`depends on`

The `depends on` specifier indicates that if the listed variables
change, the results of the [`question`] or [`code`] block should be
invalidated.

{% include side-by-side.html demo="depends-on" %}

In this example, if the user goes through the interview to the end,
but then edits `a`, then if and when `a` is changed to a different
value, `c` and `b` will be undefined.  The original value of `b` will
be remembered, so that when the interview logic asks the question to
define `b`, the original value will be presented as a default.  When
`a` is set, `c` is also undefined, so that when the interview logic
requires a definition of `c`, the [`code`] block will be run to
recompute the value of `c`.

If the user goes through the interview and then edits `b`, a change in
`b` will trigger the invalidation of `c`.

The `depends on` specifier will also cause variables to be invalidated
when they are changed by a [`code`] block.

{% include side-by-side.html demo="depends-on-code" %}

In this interview, the variable `b` is set by a [`code`] block.  If
the user edits `a` to a different value, the `depends on` specifier on
the [`code`] block causes the [`code`] block to be re-run.  The change
in `b` causes the value of `c` to be invalidated.  As a result, `c` is
automatically updated when `a` changes.

Note that the `depends on` specifier results in invalidation when a
variable is changed, not when it is defined.  If a variable is
undefined and is then defined, this is not considered a change for
purposes of the `depends on` specifier.  If a user presses Continue on
a screen but does not change the value of a variable, the `depends on`
logic is not triggered.

The `depends on` specifier can be used with iterator variables.

{% include side-by-side.html demo="depends-on-iterator" %}

In this interview, the "Edit" button on the table only triggers the
asking of the `.pay_period` question, but the `depends on` logic will
cause the `.income` question to be re-asked, and the `.annual_income`
amount to be re-calculated, if the `.pay_period` answer changes.

In situations where variables that are part of a list need to be
invalidated when a variable that is not part of the same list item
changes, the [`on change`] block can be used.

## <a name="reconsider"></a>`reconsider`

The `reconsider` modifier can be used in two ways: it can be set to a
list of variables, or it can be set to `True`.

### Effect when set to a list of variable names

When you set `reconsider` to a list of variable names, then before the
`question` is asked, the variables will be undefined (if they are
defined at all), and then the definition of each variable will be
sought again.

{% highlight yaml %}
reconsider:
  - minutes_since_world_series
question: |
  It has been ${ minutes_since_world_series } minutes since
  your team won the world series.  Have you gotten over
  your excitement yet?
yesno: gotten_over_excitement
{% endhighlight %}

This can be useful when your [`question`] refers to a computed
variable that might have become out-of-date since the last time it was
computed.

### Effect when set to `True`

If `reconsider` is set to `True` on a `code` block, then
**docassemble** will always "reconsider" the values of any of the
variables set by the block.  That is, every time the interview is
assembled (every time the screen loads) **docassemble** will forget
about the value of any of the variables set by the `code` block.

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

## <a name="undefine"></a>`undefine`

When you set `undefine` to a list of variable names, then before the
`question` is asked, the variables will be undefined.

{% highlight yaml %}
undefine:
  - favorite_foods
question: |
  What is your favorite fruit?
fields:
  - Favorite fruit: favorite_fruit
---
code: |
  favorite_foods = [favorite_vegetable, favorite_fruit]
---
mandatory: True
question: |
  Your favorite foods are
  ${ comma_and_list(favorite_foods) }.
{% endhighlight %}

This can be useful when you allow users to change their answers using
review screens.  Sometimes a change to one variable will invalidate
answers to other [`question`]s, or to computations made by [`code`]
blocks.

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

1. Hello!
2. What is your name?
3. What is your favorite food?
4. Do you like penguins?

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

## <a name="overriding"></a>Overriding one question with another

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
reference that developer's [YAML] file into an interview that assesses
whether a user is maximizing his or her public benefits.  When the law
about food stamps changes, that developer will be responsible for
updating his or her [YAML] file; your interview will not need to
change.  This allows for a division of labor.  All you will need to do
is make sure that the **docassemble** [package] containing the food
stamp [YAML] file gets updated on the server when the law changes.

## <a name="fallback"></a>Fallback questions

If a [`code`] block does not, for whatever reason, actually define the
variable, **docassemble** will "fall back" to a block that is located
earlier in the [YAML] file.  For example:

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

This "fall back" process can also happen with special [`question`]
blocks that use the [`continue`] option.

{% include side-by-side.html demo="fallback" %}

In this case, the special [`continue`] choice causes **docassemble**
to skip the [`question`] block and look elsewhere for a definition of
`user_wants_to_go_to_dance`.  **docassemble** will "fall back" to the
version of the question that exists within `question-library.yml`.
When looking for a block that offers to define a variable,
**docassemble** starts at the bottom and works its way up.

(Note that [`question`]s using [`continue`] are of limited utility
because they cannot use the [`generic object` modifier] or [index
variables].  However, [`code`] blocks do not have this limitation.)

So, to recapitulate: when **docassemble** considers what blocks it
_must_ process, it goes from top to bottom through your interview
[YAML] file, looking for [`mandatory`] and [`initial`] blocks; if a
block is later in the file, it is processed later in time.  However,
when **docassemble** considers what question it should ask to define a
particular variable, it goes from bottom to top; if a block is later
in the file, it is considered to "supersede" blocks that are earlier
in the file.

As explained [below](#precedence), however, instead of relying on
relative placement of blocks in the [YAML] file, you can explicitly
indicate which blocks take precedence over other blocks.

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

# <a name="variablesearching"></a>How **docassemble** finds questions for variables

There can be multiple questions or code blocks in an interview that
can define a given variable.  You can write [`generic object`]
questions in order to define attributes of objects, and you can use
[index variables] to refer to any given item in a [`DAList`] or
[`DADict`] (or a subtype of these objects).  Which one will be used?

In general, if you have multiple questions or code blocks that are
capable of defining a variable, **docassemble** will try the more
specific ones first, and then the more general ones.

For example, if the interview needs a definition of
`fruit['a'].seed_info.tally['b'].molecules[4].name`, it will look for
questions that offer to define the following variables, in this order:

{% highlight text %}
fruit['a'].seed_info.tally['b'].molecules[4].name
fruit[i].seed_info.tally['b'].molecules[4].name
fruit['a'].seed_info.tally[i].molecules[4].name
fruit['a'].seed_info.tally['b'].molecules[i].name
fruit[i].seed_info.tally[j].molecules[4].name
fruit[i].seed_info.tally['b'].molecules[j].name
fruit['a'].seed_info.tally[i].molecules[j].name
fruit[i].seed_info.tally[j].molecules[k].name
{% endhighlight %}

Then it will look for [`generic object`] blocks that offer to define
the following variables, in this order:

{% highlight text %}
x['a'].seed_info.tally['b'].molecules[4].name
x[i].seed_info.tally['b'].molecules[4].name
x['a'].seed_info.tally[i].molecules[4].name
x['a'].seed_info.tally['b'].molecules[i].name
x[i].seed_info.tally[j].molecules[4].name
x[i].seed_info.tally['b'].molecules[j].name
x['a'].seed_info.tally[i].molecules[j].name
x[i].seed_info.tally[j].molecules[k].name
x.seed_info.tally['b'].molecules[4].name
x.seed_info.tally[i].molecules[4].name
x.seed_info.tally['b'].molecules[i].name
x.seed_info.tally[i].molecules[j].name
x.tally['b'].molecules[4].name
x.tally[i].molecules[4].name
x.tally['b'].molecules[i].name
x.tally[i].molecules[j].name
x['b'].molecules[4].name
x[i].molecules[4].name
x['b'].molecules[i].name
x[i].molecules[j].name
x.molecules[4].name
x.molecules[i].name
x[4].name
x[i].name
x.name
{% endhighlight %}

Moreover, when **docassemble** searches for a [`generic object`]
question for a given variable, it first look for [`generic object`]
questions with the object type of `x` (e.g., [`Individual`]).  Then it
will look for [`generic object`] questions with the parent type of
object type of `x` (e.g., [`Person`]).  It will keep going through the
ancestors, stopping at the most general object type, [`DAObject`].

Note that the order of questions or code blocks in the [YAML] matters
where the variable name is the same; the blocks that appear later in
the [YAML] will be tried first.  But when the variable name is
different, the order of the blocks in the [YAML] does not matter.
If your interview has a question that offers to define
`seeds['apple']` and another question that offers to define
`seeds[i]`, the `seeds['apple']` question will be tried first,
regardless of where the question is located in the the [YAML].

Here is an example in which a relatively specific question, which sets
`veggies[i][1]`, will be used instead of a more general question,
which sets `veggies[i][j]`, when applicable:

{% include side-by-side.html demo="nested-veggies-override" %}

<a name="precedence"></a>These rules about which blocks are tried
before other blocks can be overriden using the [`order` initial block]
or the [`id` and `supersedes`] modifiers.  You can use the [`if`
modifier] to indicate that a given [`question`] should only be asked
under certain conditions.  You can use the [`scan for variables`
modifier] to indicate that a [`question`] or [`code`] block should
only be considered when looking to define a particular variable or set
of variables, even though it is capable of defining other variables.

# <a name="multiple interviews"></a>Combining multiple interviews into one

## <a name="multiple interviews umbrella"></a>Using an umbrella YAML file

If you have multiple interviews and you want the user to choose which
interview to run, you could offer the multiple interviews as a single
interview, where there is an "umbrella" [YAML] file that [`include`]s
the others.

For example:

{% include side-by-side.html demo="umbrella-interview" %}

Note that this interview [`include`]s three separate [YAML] files.
The controlling logic is the [`code`] block in the "umbrella"
interview that pursues a different endpoint depending on the value of
`interview_choice`.

The three interview files included are:

* [interview-fruit.yml]
* [interview-vegetables.yml]
* [interview-flowers.yml]

Note that these interview files contain everything needed for the
interview except for any [`mandatory`] blocks that would define an
interview endpoint; that function is reserved for the "umbrella"
interview.

## <a name="multiple interviews links"></a>Using hyperlinks

There are other ways to offer users a choice of interviews.  For
example, you can use the [`interview_url()`] function with the `i`
optional keyword parameter to point users from one interview to
another:

{% include side-by-side.html demo="interview-url-refer" %}

You might also offer these hyperlinks in the menu, using the
[`menu_items`] special variable:

{% include side-by-side.html demo="menu-items-refer" %}

You can also use the [`dispatch`] configuration directive in
combination with [`show dispatch link`] to allow the user to access a
list of interviews available on your server by selecting "Available
Interviews" from the menu.

## <a name="multiple interviews redirect"></a>A/B testing with redirects

The hyperlinks described in the previous subsection can also be used
with the [`command()`] function to automatically redirect the user to
a particular interview, for example for the purposes of A/B testing.

The following interview seamlessly redirects the user to either the
[demo interview] or the [example interview for the `redact()`
function], depending on a computational coin flip.

{% include demo-side-by-side.html demo="ab-test" %}

The use of `'exit'` in the [`command()`] function is important here
because it will cause this brief interview session to be deleted from
the user's list of interview sessions, since its sole purpose is to
redirect the user.

An interview like this might also log some data for purposes of
collecting metrics, perhaps using [Redis].  In the interviews being
A/B tested, metrics could be logged using [Redis] or the [Google
Analytics feature].

## <a name="subinterview"></a>Using multiple endpoints in a single interview

<a name="subinterview"></a>Another way to offer an "interview inside
an interview" is to populate variables and then delete them.

{% include demo-side-by-side.html demo="interview_in_interview" %}

The central logic of this interview is in the following [`code`]
block:

{% highlight yaml %}
mandatory: True
code: |
  while True:
    del endpoint[user.goal]
    del user
{% endhighlight %}

This is concise but cryptic, so it may be easier to understand what
the interview is doing by writing out the variables for which [Python]
will seek definitions, in the order in which [Python] will seek them:

{% highlight yaml %}
mandatory: True
code: |
  while True:
    user.goal
    endpoint[user.goal]
    del endpoint[user.goal]
    del user
{% endhighlight %}

First, the interview asks for the goal (`user.goal`) -- whether the
user wants do an interview about fruit, vegetables, or legumes.

Next, it seeks an endpoint for that goal -- a variable like
`endpoint['vegetable']`.  This results in the "sub-interview" being
conducted.  Once that endpoint is reached (e.g., when
`endpoint['vegetable']` is set to `True` by the final question of the
"sub-interview"), then the variables `endpoint['vegetable']` and
`user` are deleted (using the [Python] `del` statement).  Then the
logic loops back around to where it began.  At this point, `user.goal`
will be undefined, because the entire variable `user` had been
deleted.  So the user will be presented with the "fruit, vegetable, or
legume" choice again, and can choose to repeat the same
"sub-interview," or start a different "sub-interview."

Note that an interview like this is different from an interview that
concludes with a [restart button].  While a [restart button] wipes out
all of the user's answers, this interview retains some of the
information that was gathered.  It does so by using two objects to
track information about the user: information that is permanent is
stored in the `user_global` object, and information that is temporary
is stored in the `user` object.

Note that the interview developer only uses the object `user` when
writing [`question`]s that refer to characteristics of the user.  The
following [`code`] blocks assert that information about the `user`'s
name and age should by defined by reference to attributes of the
`user_global` object:

{% highlight yaml %}
code: |
  user.name.first = user_global.name.first
  user.name.last = user_global.name.last
---
code: |
  user.age_category = user_global.age_category
{% endhighlight %}

This means that whenever the interview needs the definition of
`user.name.first`, it will actually seek out `user_global.name.first`.
If the user has been asked for their name before, no question needs to
be asked; the [`code`] will take care of defining `user.name.first`
and `user.name.last`.  But other attributes, like
`user.favorite_fruit`, are lost when the interview logic does `del
user`.  As a result, the interview will remember some answers and
forget others.

# <a name="bplogic"></a>Best practices for interview logic and organization

* Use only a single [`mandatory`]<span></span> [`code`] block for each
  interview, and put it at the top of the file after the
  [initial blocks].

# <a name="bpsharing"></a>Best practices for sharing with others

* Don't reinvent the wheel; [`include`] other people's questions.
* Share your [`question`]s, [`code`], and [`template`]s with others.
* To that end, keep your [`question`] blocks in a separate [YAML] file
  from your [`mandatory`] interview logic, so that other people can
  incorporate your questions without having to edit your work.  Your
  main interview file would consist only of:
    * A [`metadata`] block saying who you are and what your interview
    is for;
	* A block to [`include`] your file of questions;
	* Any [`interview help`] blocks;
	* A [`default role`] block, if you use [roles];
	* Any [`initial`] code;
	* Your [`mandatory`] code or questions that set your interview in motion.
* [`include`] other people's question files directly from their
  **docassemble** packages, rather than by copying other people's
  files into your package.  That way, when the other developers make
  improvements to their questions, you can gain the benefit of those
  improvements automatically.
* Don't invent your own scheme for variable names; follow conventions
  and replicate what other people are doing.
* If other people are including your questions and code, avoid
  changing your variable names unnecessarily, or else you will "break"
  other people's interviews.  This does limit your autonomy somewhat,
  but the benefits for the community of interview developers more than
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
[`template`]: {{ site.baseurl }}/docs/initial.html#template
[`event`]: {{ site.baseurl }}/docs/fields.html#event
[special screen]: {{ site.baseurl }}/docs/fields.html#event
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`action_menu_item()`]: {{ site.baseurl }}/docs/functions.html#action_menu_item
[`menu_items`]: {{ site.baseurl }}/docs/special.html#menu_items
[`review`]: {{ site.baseurl }}/docs/fields.html#menu_items
[`reset` initial block]: {{ site.baseurl }}/docs/initial.html#reset
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[package]: {{ site.baseurl }}/docs/packages.html
[interview-fruit.yml]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/examples/interview-fruit.yml
[interview-vegetables.yml]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/examples/interview-vegetables.yml
[interview-flowers.yml]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/examples/interview-flowers.yml
[`interview_url()`]: {{ site.baseurl }}/docs/functions.html#interview_url
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[index variables]: {{ site.baseurl }}/docs/fields.html#index variables
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`Person`]: {{ site.baseurl }}/docs/objects.html#Person
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`generic object`]: {{ site.baseurl }}/docs/modifiers.html#generic object
[multi-user interview]: {{ site.baseurl }}/docs/roles.html
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[`need` specifier]: #need
[`reconsider`]: #reconsider
[`force_ask()`]: {{ site.baseurl }}/docs/functions.html#force_ask
[`id`]: {{ site.baseurl}}/docs/modifiers.html#id
[`id` and `supersedes`]: {{ site.baseurl}}/docs/modifiers.html#precedence
[`order` initial block]: {{ site.baseurl }}/docs/initial.html#order
[`if` modifier]: {{ site.baseurl}}/docs/modifiers.html#if
[`scan for variables` modifier]: {{ site.baseurl}}/docs/modifiers.html#scan for variables
[restart button]: {{ site.baseurl}}/docs/questions.html#special buttons
[`command()`]: {{ site.baseurl }}/docs/functions.html#command
[demo interview]: https://demo.docassemble.org/interview?i=docassemble.demo:data/questions/questions.yml
[example interview for the `redact()` function]: https://demo.docassemble.org/interview?i=docassemble.demo:data/questions/examples/redact-docx.yml
[`show dispatch link`]: {{ site.baseurl }}/docs/config.html#show dispatch link
[Redis]: {{ site.baseurl }}/docs/functions.html#redis
[Google Analytics feature]: {{ site.baseurl }}/docs/config.html#google analytics
[`generic object` modifier]: {{ site.baseurl }}/docs/fields.html#generic
[`on change`]: {{ site.baseurl }}/docs/initial.html#on change
