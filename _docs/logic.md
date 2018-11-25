---
layout: docs
title: Interview Flow
short_title: Interview Flow
---

# <a name="intro"></a>Interview Flow Introduction

Unlike other guided interview systems, in which the interview developer
maps out a decision tree or flowchart to indicate which questions
should be asked and in which order, Stewards implicitly figure
out what questions to ask and when to ask them.

For example, if the point of your interview is to assemble a document,
and one of the fields in the document is the user's Social Security
Number (SSN), the Steward will ask the user for his or her SSN;
The Steward does not need to be told to ask for the SSN.

However, if your document only displays the SSN conditionally,
the Steward will only ask for the SSN if that condition is met.
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

This will cause the Steward to ask for the petitioner's name and
whether the petitioner is a citizen, because that information is
necessary.  The Steward will ask for the SSN only if the petitioner
is a citizen.

In other guided interview systems, the logic of the document assembly
is separate from the logic that determines what interview questions
are asked.  In the case of the template above, the dependence of the
SSN on citizenship would need to be mapped out both in the document
and in the specification of the interview questions.  For
a Steward however, the logic of the interview is determined
implicitly from the requirements of the end result (in this case, a
document).  So the logic only needs to be specified in one place.

# <a name="endgoals"></a>End goals and the Satisfaction of Prerequisites

By default, all questions in an interview session are asked
only if and when they are needed.

However, in order to start asking questions, the Steward needs to
be given some direction.  You need to provide this direction by
marking at least one [`question`] block or [`code`] block as
[`mandatory`] (or one [`code`] block as [`initial`]).

If the Steward does not know what question to ask, it will give
you an error that looks like this:

{% include side-by-side.html demo="no-mandatory" %}

To prevent this error in this interview, we can mark as `mandatory`
the final `question` block -- the screen that is the endpoint for the
interview.

{% include side-by-side.html demo="with-mandatory" %}

Now the Steward knows what to do: it needs to present the final
screen.

Note that the two questions in the interview ("How are you doing?"
and "What is your favorite color?") were not marked as `mandatory`,
but are nevertheless still asked during the interview session.  Since the text
of the final `question` depends on the answers to these questions, the
questions are asked automatically.  The order in which the questions
are asked depends on the order in which the Steward needs the
answers (not the order in which the questions appear in the
[DALang]).

The DALang above effectively tells the Steward the following:

1. If a definition of `how_doing` is needed, but `how_doing` is
   undefined, you can get a definition of `how_doing` by asking the "How
   are you doing?" question.
2. If a definition of `favorite_color` is needed, but `favorite_color`
   is undefined, you can get a definition of `favorite_color` by
   asking the "What is your favorite color?" question.
3. You must present the "Your favorite color is . . ."  screen to the
   user.
   
Here is what happens in a session of this interview:

1. The user clicks on a link and goes to the interview.
1. The Steward starts an interview session with the user.
1. The Steward tries to present the "Your favorite color is . . ."
   screen to the user.
2. The Steward realizes it needs the definition of the
   `favorite_color` variable, but it is undefined, so it asks the
   "What is your favorite color?" question.
3. When the user answers the question, the variable `favorite_color`
   is set to the user's answer.
4. The Steward again tries to present the "Your favorite color is
   . . ." screen to the user.
5. The Steward realizes it needs the definition of the `how_doing`
   variable, but it is undefined, so it asks the "How
   are you doing?" question.
6. When the user answers the question, the variable `how_doing`
   is set to the user's answer.
7. The Steward again tries to present the "Your favorite color is
   . . ." screen to the user.
8. The Steward does not encounter any undefined variables, so it
   is able to present the "Your favorite color is . . ." screen to
   the user.
9. The interview session is now over because the "Your favorite color is
   . . ."  screen does not allow the user to press any buttons to move
   forward.

By making only the final screen `mandatory`, this interview takes
advantage of DALang's feature for automatically satifying
prerequisites.  The developer simply needs to provide a collection of
questions, in any order, and the Steward will figure out if and
when to ask those questions, depending on what is necessary during any
given interview session.

Alternatively, you could make every question `mandatory`:

{% include side-by-side.html demo="all-mandatory" %}

Here is what happens in this version of the interview:

1. The user clicks on a link and goes to the interview.
1. The Steward starts an interview session with the user.
2. The Steward presents the mandatory "How are you doing?"
   question to the user.
3. When the user answers the question, the variable `how_doing`
   is set to the user's answer.
4. The Steward presents the mandatory "What is your favorite color?"
   question to the user.
5. When the user answers the question, the variable `favorite_color`
   is set to the user's answer.
6. The Steward presents the mandatory "Your favorite color is
   . . ." screen to the user.  It does not need to ask any questions
   because the variables this screen depends on, `favorite_color` and
   `how_doing`, are already defined.

The approach of marking everything as `mandatory` bypasses
a Steward's process of automatically satisfying prerequisites.

When Steward developers first start using DALang, they tend to
use the approach of marking all questions as `mandatory` and listing
them one after another.  For simple, linear interviews, this approach
is attractive; it gives the author tight control over the interview
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
the Docassemble Framework.  It allows Steward developers to build any level of
complexity into their interviews.  It frees the developer from having to
envision all of the possible paths that could lead to the endpoint of
an interview.  This allows the Steward developer to concentrate on the
substance of the interview's end goal rather than the process of
gathering the information.

The most "scalable" approach to building an interview is to allow
a Steward's prerequisite-satisfying algorithm to do the heavy
lifting.  This means using `mandatory` as little as possible.

## <a name="changeorder"></a>Changing the Order of Questions

You may encounter situations where you don't like the order
in which a Steward asks questions.  You can always tweak the
order of questions.  For example, suppose you want to make sure that
your Steward asks "How are you doing?" as the first question, rather
than "What is your favorite color?"

One approach to change the order of questions is to use the
[`need` component] (explained in more detail [below](#need)):

{% include side-by-side.html demo="with-mandatory-tweak-a" %}

In this example, the [`need` component] effectively tells
the Steward that before it tries to present the "Your
favorite color is . . ." screen to the user, it needs to make sure
that the variables `how_doing` and `favorite_color` are defined.  It
also indicates that the Steward should seek the definitions of
these variables in a specific order.  Thus, "How are you doing?" is asked
first.

Another approach to tweaking the order of questions is to use a
[`code`] block as the single `mandatory` block that will control the
course of the interview flow.

{% include side-by-side.html demo="with-mandatory-tweak-b" %}

In this example, the [`code`] block effectively tells the Steward:

1. Before doing anything else, make sure that `how_doing` is defined.
2. Next, do what is necessary to show the [special screen] called
   `final_screen`.

The prerequisite-satisfying process also works with [`code`] blocks.

{% include side-by-side.html demo="code" %}

In this example, when the Steward seeks the definition of
`fruits`, it sees that it will find it by running the [`code`] block.
When it tries to run this block, it will find that it does not know the
definition of `peaches`, so it will ask a question to gather it.  Then
it will find that it does not know the definition of `pears`, so it
will ask a question to gather it.

The following subsections explain in detail the `mandatory` component
and other components that control interview flow.

Before you move on, however, there are two important things to know
about how a Steward satisfies prerequisites.

First, remember that Stewards asks questions when a variable
that is _undefined_.  In the above example, if `fruits` had already
been defined, the Steward would not have run the [`code`] block;
it would have proceeded to display the final screen.  There are some
exceptions to this.  The [`reconsider`] component
[discussed below](#reconsider) is one such exception; the
[`force_ask()`] function is another.

Second, note that the process of satisfying a prerequisite is
triggered whenever the Steward needs to know the value of a variable,
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

# <a name="directives"></a>Components that Control Interview Flow

## <a name="mandatory"></a>`mandatory`

Consider the following [DALang] file as a complete interview:

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

The Steward will ask "Are you sitting down" and then it will say
"Your socks do not match."  It will not ask "What is the capital of
Maine?"

Another way to control the interview flow of a Steward is to have a single,
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

If a `mandatory` component is not present within a block, it is as
though `mandatory` was set to `False`.

The value of `mandatory` can be a [Python] expression.  If it is a
[Python] expression, the [`question`] or [`code`] block will be
treated as mandatory if the expression evaluates to a true value.

{% include side-by-side.html demo="mandatory-code" %}

## <a name="initial"></a>`initial`

The `initial` component is very similar to [`mandatory`].  It can only
be used on a [`code`] block.  It causes the [`code`] block to be run
every time the Steward is engaged (every time the screen loads).  [`mandatory`]
blocks, by contrast, are never run again if they are successfully
"asked" once.

{% include side-by-side.html demo="initial" %}

Note in this example that from screen to screen, the `counter`
increments from 1 to 2 and then to 4.  The counter does not count the
number of screens displayed, but rather the number of times the
[DALang] was evaluated.  The "passes" through the DALang are:

1. The DALang is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The Steward then
   tries to run the `code` block to get `fruit`, but encounters an
   undefined variable `peaches`, so it asks a question to gather
   `peaches`.
2. The DALang is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The Steward then
   tries to run the `code` block to get `fruit`, but encounters an
   undefined variable `pears`, so it asks a question to gather
   `pears`.
3. The DALang is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The Steward then runs
   the `code` block, and this time, `fruit` is successfully defined.
4. The DALang is evaluated again, and the final question is
   displayed.

Like [`mandatory`], `initial` can be set to `True`, `False`, or to
[Python] code that will be evaluated to see whether it evaluates to a
true or false value.

`initial` blocks are useful in a variety of contexts:

* When you are using a [multi-user interview] and you want to set
  DALang variables to particular values depending on the user who
  is currently using the interview.
* When you are using the [actions] feature and you want to make sure
  the [actions] are processed only in particular circumstances.

## <a name="need"></a>`need`

The `need` component allows you to manually specify the prerequisites
of a [`question`] or [`code`] block.  This can be helpful for tweaking
the order in which questions are asked.

{% include side-by-side.html demo="need-directive" %}

In this example, the ordinary course of the interview flow would ask
"What is your favorite animal?" as the first question.  However,
everyone knows that the first question you should ask of a child is
"How old are you?"  The `need` component indicates that before
the Steward should even try to present the "Thank you for that
information" screen, it should ensure that `number_of_years_old` old
is defined, then ensure that `favorite_animal`, and then try to
present the screen.

The variables listed in a `need` component do not have to actually be
used by the question.  Also, if your question uses variables that are
not mentioned in the `need` list, the Steward will still pursue
definitions of those variables.

## <a name="reconsider"></a>`reconsider`

The `reconsider` component can only be used on [`code`] blocks.

If `reconsider` is set to `True`, then the Steward will always
"reconsider" the values of any of the variables set by the `code`
block.

That is, every time the Steward is engaged (every time the screen
loads) it will forget about the value of any of the
variables set by the `code` block.

You will want to set `reconsider` to `True` if your interview flow is
such that you want the Steward to reconsider its definition of a
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
has been defined once, the Steward will continue to use that
definition whenever the [DALang] calls for the definition of
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

The `reconsider` component tells the Steward to always reconsider
the variables in the [`code`] block.  When the final screen comes up,
the Steward will have forgotten about the earlier-defined value of
`cat_food_cans_needed` and will therefore re-define the value by
re-running the [`code`] block.

{% include side-by-side.html demo="reconsider" %}

The `reconsider` component is particularly important to use when you
allow interviewees to go back and modify past answers using a
[`review`] block.  For more information about how to implement such
features, see [`review`], [`event`], [`url_action()`], [`process_action()`],
[`action_menu_item()`], and [`menu_items`].

DALang also offers the [`reset` initial block], which has the
same effect as the `reconsider` component, but using a different way of
specifying which variables should be reconsidered.  Whether you use
the [`reset` initial block] or the `reconsider` component is a question
of what you consider to be more convenient and/or readable.

# <a name="order"></a>The Order of DALang Blocks

[`mandatory`] and [`initial`] blocks are evaluated in the order they
appear in the [DALang] files.  Therefore, the location in the DALang
of [`mandatory`] and [`initial`] blocks, relative to each other, is
important.

The order in which non-[`mandatory`] and non-[`initial`] questions
appear is usually not important.  If a Steward needs a
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
blocks are ordered in the DALang file.

The next two questions are asked implicitly.  The third and final
[`mandatory`] block makes reference to two variables: `favorite_food`
and `user_likes_penguins`.  Since the [`question`]s that define these
variables are not `mandatory`, they can appear anywhere in the DALang
file, in any order you want.  In this case, the `favorite_food`
[`question`] block is at the end of the DALang file, and the
`user_likes_penguins` [`question`] block is at the start of the DALang
file.

The order in which these two questions are asked is determined by the
order of the variables in the text of the final [`mandatory`]
question.  Since `favorite_food` is referenced first, and
`user_likes_penguins` is referenced afterwards, the user is asked
about food and then asked about penguins.

Note that there is also an extraneous question in the interview that
defines `user_likes_elephants`; the presence of this [`question`]
block in the DALang file has no effect on the interview.

Generally, you can order non-[`mandatory`] blocks in your DALang file
any way you want.  You may want to group them by subject matter into
separate DALang files that you [`include`] in your main DALang file.
When your interviews get complicated, there is no natural order to
questions.  In some situations, a question may be asked early, and in
other situations, a question may be asked later.

## <a name="overriding"></a>Overriding One Question with Another

The order in which non-[`mandatory`] blocks appear in the [DALang] file
is only important if you have multiple blocks that each offer to
define the same variable.  In that case, the order of these blocks
relative to each other is important.  When looking for blocks that
offer to define a variable, the Steward will use later-defined
blocks first.  Later blocks "supersede" the blocks that came before.

This allows you to [`include`] "libraries" of questions in your
interview while retaining the ability to customize how any particular
question is asked.

As explained in the [initial blocks] section, the effect of an
[`include`] block is basically equivalent to copying and pasting the
contents of the included file into the original file.

For example, suppose that there is a DALang file called
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

When the Steward needs to know the definition of
`user_agrees_it_is_a_nice_evening` or `user_wants_to_go_to_dance`, it
will be able to find a block in `question-library.yml` that offers to
define the variable.

Suppose, however, that you thought of a better way to ask the
`user_wants_to_go_to_dance` question, but you don't want to get rid of
`question-library.yml` entirely.  You could override the
`user_wants_to_go_to_dance` question in `question-library.yml` by
doing the following:

{% include side-by-side.html demo="override" %}

This DALang file loads the two questions defined in
`question-library.yml`, but then, later in the list of questions,
provides a different way to get the value of
`user_wants_to_go_to_dance`.  When the Steward goes looking for a
question to provide a definition of `user_wants_to_go_to_dance`, it
starts with the questions that were defined last, and it will
prioritize your question over the question in `question-library.yml`.
Your [`question`] block takes priority because it is located _later_ in
the DALang file.

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
reference that author's DALang file into an interview that assesses
whether a user is maximizing his or her public benefits.  When the law
about food stamps changes, that author will be responsible for
updating his or her DALang file; your interview will not need to
change.  This allows for a division of labor.  All you will need to do
is make sure that the Steward's [package] containing the food
stamp DALang file gets updated on the server when the law changes.

## <a name="fallback"></a>Fallback Questions

If a more recently-defined [`question`] or [`code`] block does not,
for whatever reason, actually define the variable, the Steward
will fall back to a block that is located earlier in the DALang file.
For example:

{% include side-by-side.html demo="fallback" %}

In this case, the special [`continue`] choice causes the Steward
to skip the [`question`] block and look elsewhere for a definition of
`user_wants_to_go_to_dance`.  The Steward will "fall back" to the
version of the question that exists within `question-library.yml`.
When looking for a block that offers to define a variable,
the Steward starts at the bottom and works its way up.

Such fall-backs can also happen with [Python] code that could
potentially define a variable, but for whatever reason does not
actually do so.  For example:

{% include side-by-side.html demo="fallback2" %}

In this case, when the Steward tries to get a definition of
`user_wants_to_go_to_dance`, it will first try running the [`code`]
block, and then it will encounter `we_already_agreed_to_go` and seek
its definition.  If the value of `we_already_agreed_to_go` turns out
to be false, the [`code`] block will run its course without setting a
value for `user_wants_to_got_to_dance`.  Not giving up,
the Steward will keep going backwards through the blocks in the
DALang file, looking for one that offers to define
`user_wants_to_got_to_dance`.  It will find such a question among the
questions included by reference from `question_library.yml`, namely
the question "Interested in going to the dance tonight?"

So, to summarize: when the Steward considers what blocks it _must_
process, it goes from top to bottom through your DALang file for the interview,
looking for [`mandatory`] and [`initial`] blocks; if a block is
later in the file, it is processed later in time.  However, when
the Steward considers what question it should ask to define a
particular variable, it goes from bottom to top; if a block is later
in the file, it is considered to "supersede" blocks that are earlier
in the file.

As explained [below](#precedence), however, instead of relying on
relative placement of blocks in the DALang file, you can explicitly
indicate which blocks take precedence over other blocks.

# <a name="howitworks"></a>How a Steward Runs Your Code

A Steward goes through your DALang file for the interview from start to
finish, incorporating [`include`]d files as it goes.  It always
executes [`initial`] code when it sees it.  It executes any
[`mandatory`]<span></span> [`code`] blocks that have not been
successfully executed yet.  If it encounters a
[`mandatory`]<span></span> [`question`] that it has not been
successfully asked yet, it will stop and ask the question.

If at any time it encounters a variable that is undefined, for example
while trying to formulate a question, it will interrupt itself in
order to go find the a definition for that variable.

Whenever a Steward comes back from one of these excursions to
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
how Stewards conduct interviews, which is to ask questions "as needed," the
code actually runs like this:

1. The Steward starts running the code; it encounters
 `user_has_car`, which is undefined.  It finds a question that defines
 `user_has_car` and asks it.  (We will assume `user_has_car` is set to True.)
2. The Steward runs the code again, and tries to increment the
 `user_net_worth` (which we can assume is already defined); it
 encounters `resale_value_of_user_car`, which is undefined.  It finds
 a question that defines `resale_value_of_user_car` and asks it.
3. The Steward runs the code again.  The value of `user_net_worth`
 is increased.  Then the code encounters `user_car_brand`, which is
 undefined.  It finds a question that defines
 `user_car_brand` and asks it.
4. The Steward runs the code again.  The value of `user_net_worth`
 is increased (again).  If `user_car_brand` is equal to "Toyota," then
 `user_is_sensible` is set.  In that case, the code runs successfully
 to the end, and the [`mandatory`] code block is marked as completed, so
 that it will not be run again.
5. However, if `user_car_brand` is not equal to "Toyota," the code
 will encounter `user_car_is_convertible`, which is undefined.
 The Steward will find a question that defines
 `user_car_is_convertible` and ask it.  The Steward will then run
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
because `user_net_worth` would already be defined when the Steward
came back from asking whether the user has a car.

# <a name="variablesearching"></a>How a Steward Finds Questions for Variables

There can be multiple questions or code blocks in your [DALang] that
can define a given variable.  You can write [`generic object`]
questions in order to define attributes of objects, and you can use
[index variables] to refer to any given item in a [`DAList`] or
[`DADict`] (or a subtype of these objects).  Which one will be used?

In general, if you have multiple questions or code blocks that are
capable of defining a variable, the Steward will try the more
specific ones first, and then the more general ones.

For example, if the Steward needs a definition of
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

Moreover, when a Steward searches for a [`generic object`]
question for a given variable, it first look for [`generic object`]
questions with the object type of `x` (e.g., [`Individual`]).  Then it
will look for [`generic object`] questions with the parent type of
object type of `x` (e.g., [`Person`]).  It will keep going through the
ancestors, stopping at the most general object type, [`DAObject`].

Note that the order of questions or code blocks in the DALang matters
where the variable name is the same; the blocks that appear later in
the DALang will be tried first.  But when the variable name is
different, the order of the blocks in the DALang does not matter.
If your DALang has a question that offers to define
`seeds['apple']` and another question that offers to define
`seeds[i]`, the `seeds['apple']` question will be tried first,
regardless of where the question is located in the DALang.

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

# <a name="multiple interviews"></a>Stewards with Multiple Interviews

## <a name="multiple interviews umbrella"></a>Using an Umbrella DALang File

If you have multiple interviews and you want the user to choose which
interview to run, you could offer the multiple interviews as a single
interview, where there is an "umbrella" [DALang] file that [`include`]s
the others.

For example:

{% include side-by-side.html demo="umbrella-interview" %}

Note that this interview [`include`]s three separate DALang files.
The controlling logic is the [`code`] block in the "umbrella"
interview that pursues a different endpoint depending on the value of
`interview_choice`.

The three DALang files included are:

* [interview-fruit.yml] 
* [interview-vegetables.yml] 
* [interview-flowers.yml] 

Note that these DALang files contain everything needed for the
interview except for any [`mandatory`] blocks that would define an
interview endpoint; that function is reserved for the "umbrella"
interview.

## <a name="multiple interviews links"></a>Using Hyperlinks

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
list of interviews available on your [server] by selecting "Available
Interviews" from the menu.

## <a name="multiple interviews redirect"></a>A/B Testing with Redirects

The hyperlinks described in the previous subsection can also be used
with the [`command()`] function to automatically redirect the user to
a particular interview, for example for the purposes of A/B testing.

The following interview seamlessly redirects the user to either the
[demo interview] or the [example interview for the `redact()`
function], depending on a computational coin flip.

{% include demo-side-by-side.html demo="ab-test" %}

The use of `'exit'` in the [`command()`] function is important here
because it will cause this brief interview session to be deleted from
the user's list of interview sessions, since its sole purpose is to redirect the
user.

An interview like this might also log some data for purposes of
collecting metrics, perhaps using [Redis].  In the interviews being
A/B tested, metrics could be logged using [Redis] or the [Google
Analytics feature].

## <a name="subinterview"></a>Interviews with Multiple Endpoints 

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
the Steward is doing by writing out the variables for which [Python]
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

First, the Steward asks for the goal (`user.goal`) -- whether the
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

This means that whenever the Steward needs the definition of
`user.name.first`, it will actually seek out `user_global.name.first`.
If the user has been asked for their name before, no question needs to
be asked; the [`code`] will take care of defining `user.name.first`
and `user.name.last`.  But other attributes, like
`user.favorite_fruit`, are lost when the Steward runs `del
user`.  As a result, the Steward will remember some answers and
forget others.

# <a name="bplogic"></a>Best Practices for Interview Flow and Organization

* Use only a single [`mandatory`]<span></span> [`code`] block for each
  interview, and put it at the top of the file after the
  [initial blocks].

# <a name="bpsharing"></a>Best Practices for Sharing with Others

* Don't reinvent the wheel; [`include`] other people's questions.
* Share your [`question`]s, [`code`], and [`template`]s with others.
* To that end, keep your [`question`] blocks in a separate [DALang] file
  from your [`mandatory`] blocks, so that other people can
  incorporate your questions without having to edit your work.  Your
  main DALang file would consist only of:
  * A [`metadata`] block saying who you are and what your interview
    is for;
  * An [`include`] block to your DALang file of questions;
  * Any [`interview help`] blocks;
  * A [`default role`] block, if you use [roles];
  * Any [`initial`] code;
  * Your [`mandatory`] code or questions that set your Steward in motion.
* [`include`] other developer's DALang question files directly from their
  Steward, rather than by copying other developer's
  files into your Steward.  That way, when the other authors make
  improvements to their questions, you can gain the benefit of those
  improvements automatically.
* Don't invent your own scheme for variable names; follow conventions
  and replicate what other people are doing.
* If other people are including your questions and code, avoid
  changing your variable names unnecessarily, or else you will "break"
  other people's Stewards.  This does limit your autonomy somewhat,
  but the benefits for the community of Steward developers more than
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
[`need` component]: #need
[`reconsider`]: #reconsider
[`force_ask()`]: {{ site.baseurl }}/docs/functions.html#force_ask
[`id` and `supersedes`]: {{ site.baseurl}}/docs/modifiers.html#precedence
[`order` initial block]: {{ site.baseurl }}/docs/initial.html#order
[`if` component]: {{ site.baseurl}}/docs/modifiers.html#if
[`scan for variables` component]: {{ site.baseurl}}/docs/modifiers.html#scan for variables
[restart button]: {{ site.baseurl}}/docs/questions.html#special buttons
[`command()`]: {{ site.baseurl }}/docs/functions.html#command
[demo interview]: https://demo.docassemble.org/interview?i=docassemble.demo:data/questions/questions.yml
[example interview for the `redact()` function]: https://demo.docassemble.org/interview?i=docassemble.demo:data/questions/examples/redact-docx.yml
[`show dispatch link`]: {{ site.baseurl }}/docs/config.html#show dispatch link
[Redis]: {{ site.baseurl }}/docs/functions.html#redis
[Google Analytics feature]: {{ site.baseurl }}/docs/config.html#google analytics
[DALang]: {{ site.baseurl }}/docs/interviews.html#yaml
[server]: {{ site.baseurl }}/docs/installation.html