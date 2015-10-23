---
layout: docs
title: Interview Logic
short_title: Interview Logic
---

Like `question` questions, `code` questions are not "asked" unless
they contain variables that **docassemble** needs.  All `question` and
`code` blocks are only called when and if they are needed.

For your interview to start asking questions, you need to mark at
least one `question` block or `code` block with the modifier
`mandatory: true`.

## `mandatory`

Consider the following as a complete interview file:

{% highlight yaml %}
---
question: What is the capital of Maine?
fields:
  - Capital: maine_capital
---
question: Are you sitting down?
yesno: user_sitting_down
mandatory: true
---
question: Your socks do not match.
mandatory: true
---
{% endhighlight %}

The interview will ask "Are you sitting down" and then it will say
"Your socks do not match."  It will not ask "What is the capital of
Maine?"

Another way to control the logic of an interview is to have a single,
simple `mandatory` `code` block that sets the interview in motion.

For example:

{% highlight yaml %}
---
mandatory: true
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

Here, the `mandatory` block of `code` contains simple Python code that
contains the entire logic of the interview.

## `initial`

The `initial` modifier is very similar to `mandatory`.  It causes a
`code` block to be run every time **docassemble** processes your
interview.  `mandatory` blocks, by contrast, are never run again if
they are successfully "asked" once.

{% highlight yaml %}
---
initial: true
code: |
  my_counter = 0
---
{% endhighlight %}

## The logical order of an interview

`mandatory` and `initial` blocks are evaluated in the order they
appear in the question file.  Therefore, the location in the interview
of `mandatory` and `initial` blocks, relative to each other, is
important.  Ordinary questions can appear anywhere in any order.

**docassemble** goes through the interview file from top to bottom,
looking for `mandatory` and `initial` blocks.  When it encounters an
`include` statement, it immediately goes through the included file
from top to bottom, and then picks up where it left off.

The order in which questions appear will also matter if you have
multiple `question` or `code` blocks that each offer to define the
same variables.  In that case, the order of these blocks relative to
each other is important.  **docassemble** will use later-defined
blocks first.  Later definitions "supersede" the ones that came
before.

This allows you to `import` question files that other authors have
written and then "override" particular questions you would like to ask
differently.  You do not have to edit those other files (unless they
contain `mandatory` or `initial` blocks, which could affect your
interview in unwanted ways).

For example, suppose that `question_library.yml` consists of:

{% highlight yaml %}
---
question: It's a nice evening, isn't it?
yesno: user_agrees_it_is_a_nice_evening
---
question: Do you want to go to the dance with me?
yesno: user_wants_to_go_to_dance
---
{% endhighlight %}

You could write your own interview file that looks like this:

{% highlight yaml %}
---
include:
  - question_library.yml
---
mandatory: true
code: |
  if user_agrees_it_is_a_nice_evening and user_wants_to_go_to_dance:
    life_is_good
---
question: |
  My darling, would you do me the honor of accompanying me to
  the dance this fine evening?
yesno: user_wants_to_go_to_dance
---
question: That is splendid news!
sets:
  - life_is_good
---
{% endhighlight %}

This interview file loads the two questions defined in
`question_library.yml`, but then, later in the list of questions,
provides a different way to get the value of
`user_wants_to_go_to_dance`.  When **docassemble** goes looking for a
question to provide a definition of `user_wants_to_go_to_dance`, it
starts with the questions that were defined last.

This is similar to the way law works: old laws do not disappear from
the law books, but they can get superseded by newer laws.  "The law"
is "old" law has not yet been superseded.

If a more recently-defined question does not, for whatever reason,
actually define the variable, **docassemble** will fall back on the
"older" question.

For example:

{% highlight yaml %}
---
include:
  - question_library.yml
---
mandatory: true
code: |
  if user_agrees_it_is_a_nice_evening and user_wants_to_go_to_dance:
    life_is_good
---
question: Which of these statements is true?
choices:
  - "I am old-fashioned":
      question: |
        My darling, would you do me the honor of accompanying me to
        the dance this fine evening?
      yesno: user_wants_to_go_to_dance
  - "I don't care for flowerly language": continue
---
question: That is splendid news!
sets:
  - life_is_good
---
{% endhighlight %}

In this case, the special `continue` function (see [Setting Variables]
for details) will cause **docassemble** to "fall back" on
the earlier-mentioned question.

Such fall-backs can also happen with Python code.  For example:

{% highlight yaml %}
---
include:
  - question_library.yml
---
mandatory: true
code: |
  if user_agrees_it_is_a_nice_evening and user_wants_to_go_to_dance:
    life_is_good
---
question: I forgot, did we already agree to go to the dance together?
yesno: we_already_agreed_to_go
---
code: |
  if we_already_agreed_to_go:
    user_wants_to_go_to_dance = True
---
question: That is splendid news!
sets:
  - life_is_good
---
{% endhighlight %}

In this case, when **docassemble** tries to get a definition of
`user_wants_to_go_to_dance`, it will first try running the `code`
block, and then it will seek a definition for
`we_already_agreed_to_go`.  If the value of `we_already_agreed_to_go`
turns out to be false, the `code` block will complete without setting
a value for `user_wants_to_got_to_dance`.  Not giving up,
**docassemble** will then seek an answer to
`user_wants_to_got_to_dance` by asking the "Do you want to go to the
dance with me?" question, which was defined earlier in
`question_library.yml`.

## How **docassemble** runs your code

**docassemble** goes through your interview [YAML] file from start to
finish, incorporating `include`d files as it goes.  It always executes
`initial` code when it sees it, executes `mandatory` `code` blocks
that have not been successfully executed yet, and if it encounters a
`mandatory` `question` that it has not been successfully
asked yet, it will stop and ask the question.  If at any time it
encounters a variable that is undefined, for example while trying to
formulate a question, it will interrupt itself in order to go find the
a definition for that variable.

Whenever **docassemble** comes back from one of these excursions to
find the definition of a variable, it does not pick up where it left
off; it starts from the beginning again.

Therefore, when writing code for an interview, you need to keep in
mind that any particular block of code may be re-run from the
beginning multiple times.

For example, consider the following code:

{% highlight yaml %}
---
mandatory: true
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
 to the end, and the `mandatory` code block is marked as completed, so
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
mandatory: true
code: |
  user_net_worth = 0
  if user_has_car:
    user_net_worth = user_net_worth + resale_value_of_user_car
  if user_has_house:
    user_net_worth = user_net_worth + resale_value_of_user_house
---
{% endhighlight %}

Note that `mandatory` must be true for this to work sensibly.
If this were an optional code block, it would not run to completion
because `user_net_worth` would already be defined when **docassemble**
came back from asking whether the user has a car.

## Best practices for interview logic and organization

* Use only a single `mandatory` `code` block for each interview, and
  put it at the top of the file after the [initial blocks].

## Best practices for sharing with others

* Don't reinvent the wheel; `include` other people's questions.
* Share your `question`s and `code` with others.
* To that end, keep your `question` blocks in a separate [YAML] file
  from your `mandatory` interview logic, so that other people can
  incorporate your questions without having to edit your work.  Your
  main interview file would consist only of:
    * A `metadata` statement saying who you are and what your interview
    is for;
	* A statement to `include` your file of questions;
	* Any `interview help` blocks;
	* A `default role` block, if you use [roles];
	* Any `initial` code;
	* Your `mandatory` code or questions that set your interview in motion.
* `include` other people's question files directly from their **docassemble**
  packages, rather than by copying other people's files
  into your package.  That way, when the other authors make
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
[Setting Variables]: {{ site.baseurl }}/docs/fields.html
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
[initial blocks]: {{ site.baseurl }}/docs/initial.html

