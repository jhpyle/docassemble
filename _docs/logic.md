---
layout: docs
title: Interview logic
short_title: Interview Logic
---

# <a name="intro"></a>Introduction

Unlike other guided interview systems, in which the interview
developer maps out a decision tree or flowchart to indicate which
questions should be asked and in which order, **docassemble** figures
out what questions to ask and when to ask them based on rules that
you specify.  You specify these rules using [YAML] blocks.

## <a name="intro_mandatory"></a>Simple interviews: all blocks mandatory

The simplest type of rule you can specify is marking a block as
[`mandatory`].

{% include demo-side-by-side.html demo="all-mandatory" %}

When **docassemble** runs an interview, it looks at the [YAML] and
tries to run each block that is marked as "mandatory." It will run
them in the order in which they appear in the [YAML].  In this
example, first the "Welcome to the interview!" [`question`] is asked.
When the user clicks the "Continue" button, **docassemble** moves on
to the second [`mandatory`] block, which asks "What is your favorite
fruit?"  When that question is answered, **docassemble** asks "What is
your favorite vegetable?" When that question is answered
**docassemble** moves on to the final [`question`], "Here is your
document," which lets the user download a document.  This is a very
simple interview because there is no branching logic.

Suppose that instead of asking for the user's favorite vegetable, you
wanted to ask for the user's favorite apple, but only if the user said
that their favorite fruit is "apple."  In the previous interview, we
set [`mandatory`] to `True` every time, but we can actually set
[`mandatory`] to a [Python expression] that evaluates to a true or
false value.  For example:

{% include demo-side-by-side.html demo="branch-mandatory" %}

Here, the "What is your favorite type of fruit" [`question`] is only
"mandatory" if the user says that `apple` is their favorite type of
fruit.  Thus, if the `favorite_fruit` variable is `'banana'`, then
**docassemble** will skip over the "What is your favorite type of
apple?" [`question`] and proceed directly to the "Here is your document"
[`question`].

By setting the [`mandatory`] directive to a [Python expression] that
uses variables defined in previous [`question`] blocks, you can write
complex interviews that branch in a lot of different directions
depending on the interview answers.

However, in a complex interview with a number of nested branches of
logic, the [Python expressions] you will need to write to indicate
whether a [`question`] should be asked could be very long and
complicated.  In the next section, we will discuss another way of
implementing branching logic that avoids this complication.

## <a name="intro_dependency"></a>Complex interviews: dependency satisfaction

As explained in the previous section, when **docassemble** runs your
interview, it goes through your [YAML] from beginning to end and
attempts to run each block that is marked as [`mandatory`].  Marking a
[`question`] as "mandatory" is one way to tell **docassemble** you
want a [`question`] to be displayed.

**docassemble** can also do "dependency satisfaction."  For example,
you can write an interview like this:

{% include demo-side-by-side.html demo="dependency-demo" %}

In this interview, there is a mandatory question and then two
questions that do not have a [`mandatory`] directive on them.  If you
run the interview, the first question asked is "What is your favorite
fruit?"  How did **docassemble** know it needed to ask that question,
even though it was not marked as [`mandatory`]?  What happened was
that **docassemble** tried to display the "Your favorite fruit is ..."
question, but in the process of doing so, it encountered an undefined
variable `favorite_fruit`.  So then it looked for a block that defines
the 'favorite_fruit' variable, and it found one, so it asked the "What
is your favorite fruit?" question.

If the user types `grapes` in answer to that question, the interview
asks a follow-up question, "Which vineyard do you think produces the
best grapes?" and then proceeds to the final screen, which says "Your
favorite fruit is grapes."  However, if the user says their favorite
fruit is "apples," the interview will skip the "Which vineyard do you
think produces the best grapes?" question and will proceed directly to
the final screen, which says "Your favorite fruit is apples."  Thus,
with a single [`mandatory`] question, the interview does branching
logic.

The branching logic is a by-product of the attempt to display the
single [`mandatory`] question.  If you were to change the text of the
question and remove the reference to `favorite_vineyard`, the "Which
vineyard do you think produces the best grapes?" question would never
be asked.  Or, if you were to change the `question` text to `Your
favorite fruit is ${ favorite_fruit } and your favorite vegetable is
${ favorite_vegetable }.` then the order of questions would change,
and the question that defines `favorite_vegetable` question would be
asked right after the `favorite_fruit` question.  When dependency
satisfaction is used to ask questions, the order of questions is
determined by which variables **docassemble** sees first.

Note that the order in which non-[`mandatory`] questions appear in the
[YAML] does not affect the order in which questions are asked.  Each
block in in your [YAML] is a just a "rule," and you can specify as
many "rules" in your [YAML] as you want, in any order.

For example, the following block is a rule that indicates whether the
user is eligible for a benefit.

{% highlight yaml %}
code: |
  if user.age_in_years() >= 60 or user.is_disabled:
    user.eligible = True
  else:
    user.eligible = False
{% endhighlight %}

The rule says that the user is eligible if they are 60 or older, or if
they are disabled, otherwise the user is not eligible.

Rules in **docassemble** are instructions for how to define a
particular variable.  The [`code`] block above is a rule for how to
define `user.eligible`.  [`question`] blocks are also rules.  Here is
a rule that specifies how to define `user.is_disabled`:

{% highlight yaml %}
question: Are you disabled?
yesno: user.is_disabled
{% endhighlight %}

This says that the rule for defining `user.disabled` is to ask the
user a yes/no question.

It is possible to specify rules in fairly complex ways, as we will see
later; you can write multiple blocks that define the same variable, so
you can have alternative rules for different circumstances, or you can
have a general rule that is overridden by a more specific rule in
certain circumstances.  You can write generic rules that apply to a
variety of different variables.

When **docassemble** runs your interview, it will try to run your
[`mandatory`] blocks, in the order in which the blocks appear in your
[YAML].  In the course of trying to run a block, **docassemble** might
encounter a variable that hasn't been defined yet.  When this happens,
**docassemble** will evaluate the "rules" you have defined, and it
will run [`code`] blocks, [`question`] blocks, or other types of
blocks in order to try to obtain a definition of the undefined
variable.

In the course of trying to define a variable, **docassemble** might
encounter yet another undefined variable, in which case it will try to
obtain a definition of that variable, and in the course of trying to
define that variable, it may encounter yet another undefined variable.
A rule that defines a variable may "depend on" the values of other
variables.  **docassemble**'s logic engine will perform "dependency
satisfaction" by automatically figuring out what variable definitions
are necessary and running the appropriate [`code`] blocks or showing
the appropriate [`question`] screens to the user.

This allows you, as the interview author, to specify rules and use
variables in your interview or in your documents as you see fit, while
**docassemble** does all the thinking about which questions need to
be asked and in what order to ask them.

**docassemble** automatically refrains from asking unnecessary
questions.  For example, consider this example:

{% highlight yaml %}
code: |
  if user.age_in_years() >= 60 or user.is_disabled:
    user.eligible = True
  else:
    user.eligible = False
{% endhighlight %}

If the user is 60 or older, there is no need to ask the user if they
are disabled.  It would waste the user's time to ask that question.
**docassemble** infers this from the rule.  Thus "how to conduct the
interview" and "what the legal rules are" are effectively the same
thing, and can be specified in a single location.

## <a name="intro_manual_order"></a>Manually specifying the order of questions

Sometimes, you might not want the order of questions in the interview
to be implicitly determined by the way **docassemble** processes
rules; you might want to explicitly specify the order of questions.
You can do this using a [`code`] block.

{% include demo-side-by-side.html demo="dependency-demo-code" %}

In this interview, the mandatory [`code`] block drives the interview
using dependency satisfaction, but in an explicit order.  This block
contains a few lines of [Python] code.  The first variable encountered
is `favorite_fruit`, which means that the `favorite_fruit` question
will be asked.  If `favorite_fruit` is `'grapes'`, then
`favorite_vineyard` is evaluated, which means that `favorite_vineyard`
will be asked.  Then `favorite_vegetable` is asked, and then
`final_screen` is sought.  Because `final_screen` is a special screen,
and the `event` directive is set to `final_screen`, the variable
`final_screen` will actually not be defined; the screen is a dead-end
screen with no fields and no "Continue" button.

If the mandatory [`code`] block was not present, and instead the
`final_screen` block was marked [`mandatory`], then the questions
would have been asked in a different order: first `favorite_fruit`,
then `favorite_vegetable`, and then `favorite_vineyard` (if the
`favorite_fruit` was `'grapes'`).  We were able to instruct
**docassemble** to ask for `favorite_vineyard` immediately after
`favorite_fruit` by specifying different interview logic in the
[`code`] block.

This mandatory [`code`] block serves as an "outline" for the
interview.  Instead of ordering blocks in your [YAML], you can simply
order lines in your mandatory [`code`] block.  The [`code`] block lets
you see the order of your interview at a glance, without having to
page through a long interview.  The indentation of text under `if`
statements makes clear where there is a "branch" in the logic.

If you are familiar with [Python], you might think that the mandatory
[`code`] block is weird, because simply putting the name of a variable
by itself on a line doesn't do anything; it's not something that
programmers normally do.  However, it does something in
**docassemble**, because if the variable is undefined, a [Python
exception] will be "raised," and the raising of that exception will
tell **docassemble** that a definition of that variable needs to be
obtained.  **docassemble**'s dependency satisfaction system operates
through the triggering of undefined variable exceptions.

So far, we have discussed three different techniques for specifying
interview logic in **docassemble**:

#. A series of [`question`] blocks with [`mandatory`] directives on them;
#. Allowing `question` blocks to be asked implicitly as a result of
   dependency satisfaction; and
#. Writing a [`code`] block marked as [`mandatory`] containing an explicit
   outline of the variables that need to be gathered and the
   conditions under which each variable definition should be sought.

These three techniques are not mutually exclusive; you can use them
together.  For example, you might have a mandatory [`question`] block
followed by a mandatory [`code`] block, followed by a mandatory
[`question`] block.

{% highlight yaml %}
mandatory: True
question: |
  Welcome!
continue button field: intro_screen
---
mandatory: True
code: |
  intro_screen
  user.name.first
  final_screen
---
mandatory: True
question: |
  Your preferences.
subquestion: |
  Your favorite fruit is ${ favorite_fruit }.

  Your favorite vegetable is ${ favorite_vegetable }.

  % if favorite_vegetable == 'turnip' and user.grows_own_turnips:
  I grow turnips too!
  % endif
{% endhighlight %}

Or you could have a mandatory [`code`] block that only partially
specifies the order of questions, and allows many questions to be
asked explicitly.  For example:

{% highlight yaml %}
mandatory: True
code: |
  intro_screen
  user.name.first
  final_screen
---
question: |
  Welcome!
continue button field: intro_screen
---
event: final_screen
question: |
  Your preferences.
subquestion: |
  Your favorite fruit is ${ favorite_fruit }.

  Your favorite vegetable is ${ favorite_vegetable }.

  % if favorite_vegetable == 'turnip' and user.grows_own_turnips:
  I grow turnips too!
  % endif
{% endhighlight %}

Here, the mandatory [`code`] block ensures that `intro_screen` and
`user.name.first` are asked up front, but then uses dependency
satisfaction to trigger the asking of `favorite_fruit` and
`favorite_vegetable`, as well as the display of the `final_screen`.

## <a name="legal_logic"></a>Writing law as code to drive the interview

**docassemble**'s "rules"-based logic system is particularly
well-suited for legal applications.  You can write legal logic in
Python code, and **docassemble** will figure out how to ask the
necessary questions to arrive at a legal judgment.

For example, suppose your interview needs to determine whether the
user has legal standing as a grandparent to seek custody of a child.
The relevant statute states that a grandparent can seek custody under
the following circumstance:

{% highlight text %}
(3) A grandparent of the child who is not in loco parentis to the child:

   (i) whose relationship with the child began either with the consent
       of a parent of the child or under a court order;

   (ii) who assumes or is willing to assume responsibility for the
        child; and

   (iii) when one of the following conditions is met:

      (A) the child has been determined to be a dependent child under
          42 Pa.C.S. Ch. 63 (relating to juvenile matters);

      (B) the child is substantially at risk due to parental abuse,
          neglect, drug or alcohol abuse or incapacity; or

      (C) the child has, for a period of at least 12 consecutive
          months, resided with the grandparent, excluding brief
          temporary absences of the child from the home, and is
          removed from the home by the parents, in which case the
          action must be filed within six months after the removal of
          the child from the home.
{% endhighlight %}

The interview developer can rewrite this statute in Python, converting
each legal concept into a variable.

{% highlight yaml %}
comment: 23 Pa. C.S.A. 5324(3)
code: |
  if relationship == 'Grandparent' \
     and (relationship_began_with_consent \
          or relationship_began_with_court_order) \
     and willing_to_assume_responsibility \
     and (child_is_dependent \
          or child_is_at_risk \
          or cared_for_child_for_a_year):
    has_grandparent_standing = True
  else:
    has_grandparent_standing = False
{% endhighlight %}

Note: if you are wondering why there are `\` marks at the end of some
of the lines, this is Python syntax for formatting source code and
avoiding writing a very long line of code.  If the `\` was not
present, there would be a syntax error, because Python would interpret
the newline to mean that you were done specifying a condition, and it
would think you forgot to write a `:` to indicate the end of the
condition.  The `\` basically means "ignore the following newline and
pretend this is all one long line."

The values of a variable like `relationship_began_with_consent` could
be determined by asking the user a `question`.

{% highlight yaml %}
question: |
  At some point, did one of the child's parents agree to let you care
  for the child?
yesno: relationship_began_with_consent
{% endhighlight %}

Other variables, like `cared_for_child_for_a_year`, might be too
complex to reduce to a single question.  In that case, rather than
using a [`question`] as the "rule" for what the variable means, you
can use a [`code`] block instead, and you can break the legal concept
down into smaller pieces.

{% highlight yaml %}
code: |
  if (not child_lives_with_client) \
     and child_used_to_live_with_client \
     and child_taken_from_client_by_parent \
     and child_taken_within_last_six_months \
     and child_moved_in_at_least_12_months_before \
     and child_lived_with_client_continuously:
       cared_for_child_for_a_year = True
  else:
       cared_for_child_for_a_year = False
{% endhighlight %}

The rules for what these variables mean can in turn be specified as
[`question`] or [`code`] blocks:

{% highlight yaml %}
question: |
  Does the child currently live with you?
yesno: child_lives_with_client
---
code: |
  if as_datetime(date_child_taken_away) >= date_as_of_six_months_ago:
    child_taken_within_last_six_months = True
  else:
    child_taken_within_last_six_months = False
{% endhighlight %}

Given [YAML] rules like this, **docassemble** can automatically
conduct a parsimonious interview; that is, it will not ask any
unnecessary questions.  For example, if
`willing_to_assume_responsibility` is `False`, it will not ask
`child_is_dependent`.  The only thing you need to do to trigger this
process is to set up a [`mandatory`] block that requires a definition
of `has_grandparent_standing`.

{% highlight yaml %}
mandatory: True
code: |
  if relationship == 'Grandparent' and not has_grandparent_standing:
    grandparent_not_eligible
  final_screen
---
event: grandparent_not_eligible
question: |
  Sorry, you do not have standing as a grandparent to seek custody
  under Pennsylvania law.
{% endhighlight %}

Many beginners find this style of rule-based logic specificiation to
be confusing; they would rather specify exactly which questions are
asked, and exactly what happens as a result of the answer to each
question.  However, when there are numerous legal rules and the
interaction of the legal rules leads to a large number of possible
scenarios, planning in advance the interview process for each one of
these scenarios is time-consuming, and the work involved is mechanical
rather than substantive.  If you are going to offer users the ability
to spot-edit any of their prior answers to questions in the middle of
the interview, you will need to think about exactly which follow-up
processes are necessary when the user makes such changes.

The "declarative" style of logic is very useful in these
circumstances.  All you need to do is the work of a lawyer --
concentrate on specifying rules that are legally correct.  You can
specify multiple overlapping rules, covering special cases and general
cases.

# <a name="interview_logic"></a>How rules determine interview process

Many people envision a guided interview as a process whereby an
interviewee starts at the beginning screen, then moves through a
series of screens and then arrives at the end screen of the interview.
At any point in time, the interviewee is envisioned as being located
at a certain "place" in the interview process.

However, when the interview is driven by rules, this way of
envisioning the interview process is misleading.  For example,
consider the following structure for an interview:

#. Ask "What is your name?"
#. Ask "When were you injured?"
#. If the injury took place more than two years ago, say, "Sorry, the
   statute of limitations has expired, so you cannot file a complaint."
#. Ask "Where did the injury take place?"
#. Ask "How much did you pay in medical bills?"
#. Ask "How much time did you have to take off from work?"
#. etc.
#. Here is a complaint you can file in court.

Suppose the user started the interview one day before the statute of
limitations expired, and proceeded as far as the "How much did you pay
in medical bills?" question, but then took a few days to locate their
medical bills, and didn't complete the interview until a week after
the statute of limitations expired.  Should the guided interview allow
the user to download a complaint, or should it tell the user, "Sorry,
the statute of limitations has expired, so you cannot file a
complaint."?  If you think of the interview process as one where the
interviewee is "located" at a particular "place" in the interview, you
would say that since the user has "gone past" the part of the
interview process that checked for a statute of limitations problem,
the user should be allowed to proceed.

The philosophy behind **docassemble** is that a robust interview
process is one where the "current question" in the interview is
determined not by which question "comes after" the previous question,
but rather by the application of a set of rules to a set of facts.  If
there is a legal rule about the statute of limitations, it should be
applied every time the screen loads, not just once at the beginning of
the interview.

In **docassemble**, the interview logic is envisioned more as a
"checklist" than a process.  Each time the screen loads,
**docassemble** reviews the checklist.  What it does next depends on
the application of the checklist to the current state of affairs.

By analogy, an airplane pilot will go through a checklist prior to
takeoff.  Whether the airline pilot turns onto the runway or goes back
to the gate depends on the application of the checklist to the state
of the aircraft and external factors like the weather.  Likewise, what
**docassemble** does when the screen loads depends on the application
of the interview logic (specified in the [YAML]) to the current state
of the interview answers and external factors like the date.

From the user's perspective, the **docassemble** interview process
looks like something that has a beginning, an end, and a "current
location," but this is really just the by-product of **docassemble**
running through a checklist every time the screen loads.  "Do we know
the user's name?  Check.  Has the statute of limitations expired?
Check.  Do we know where the injury took place?  Check."

If you observe an airplane pilot at work, you might think, "gosh, the
pilot spends so much time going through boring repetitive checklists,
can't he just grab the controls and fly the plane?"  Similarly, you
might look at what **docassemble** does every time the screen loads,
and you might think, "ugh, why is it wasting time going through all of
this logic, can't it just move on to the next question?"  Although the
checklist method is repetitive, it is robust and is capable of
catching hard-to-foresee problems.

The **docassemble** interview developer's job is to design the
checklist that leads to the interview process, not to specify the
process directly.  In most situations, this is a distinction without a
difference, because the developer can write something like this:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  favorite_fruit
  favorite_vegetable
  final_screen
{% endhighlight %}

This is a checklist for what should be considered every time the
screen loads: "if the name is not known, ask the name.  If the
favorite fruit is not known, ask for the favorite fruit.  If the
favorite vegetable is not known, ask for the favorite vegetable.  Then
show the 'final_screen' screen."  This translates directly into a
process: "first ask for the name, then the favorite fruit, then the
favorite vegetable, then show the final screen."

In more complicated interviews, the connection between the checklist
and the process is less explicit.  For example:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  plaintiffs.gather()
  defendants.gather()
  if not jurisdiction_is_proper:
    kick_out_user
  final_screen
{% endhighlight %}

In this interview, after the user is asked for their name,
**docassemble** gathers a list of plaintiffs and then gathers a list
of defendants.  The process of [gathering groups] is complex and
involves multiple `question` blocks.  The line `plaintiffs.gather()`
is effectively a checklist item that means "make sure the plaintiffs
are gathered."  Groups can be gathered in a variety of ways.  The
questions might be "What is the name of the first plaintiff?", "Are
there any other plaintiffs?", "What is the name of the second
plaintiff?", "Are there any other plaintiffs?", etc.  The line `if not
jurisdiction_is_proper` implicitly triggers the defining of
`jurisdiction_is_proper`, which is defined by a [`code`] block.

By specifying a checklist, you can ensure the integrity of your
interview's logic, control the order of questions, and use to trigger
the asking of questions that it would be too tedious to specify
individually.  There are things you need to think about, however, to
ensure that your checklist results in a process that makes sense.

## <a name="idempotency"></a>Beware of non-idempotency

When designing the checklist that **docassemble** runs every time the
screen loads, you need to be careful about how you specify the
checklist items.  For example, you wouldn't want the checklist to be
the following:

#. Ask for the user's name.
#. Ask for the user's date of birth.
#. Give the user an assembled document.

That would mean that every time the screen loads, it would ask for the
user's name.  Instead, the checklist should be:

#. If the user's name is unknown, ask them for it.
#. If the user's date of birth is unknown, ask them for it.
#. Give the user an assembled document.

When you write a checklist in Python format, it looks like this:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  user.birthdate
  final_screen
{% endhighlight %}

In **docassemble**, referencing the name of a variable like
`user.birthdate` effectively means "if `user.birthdate` is undefined,
stop what we are doing and seek out a definition of `user.birthdate`;
otherwise, proceed to the next line."

By contrast, if you use the [`force_ask()`] function, it will always
ask the question:

{% highlight yaml %}
mandatory: True
code: |
  force_ask('user.name.first')
  force_ask('user.birthdate')
  final_screen
{% endhighlight %}

Here, the first "checklist" item says that **docassemble** must ask a
question to determine the value of `user.name.first` even if the
variable is already defined.  This is not what you want to do in a
checklist; the user will be confused about why the interview asks for
their name again when they just provided it.  (This is is one of the
reasons why the [`force_ask()`] function is rarely used.)

**docassemble** allows you to run Python functions inside of a
checklist, and in most situations this works as expected.  For
example:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  user.birthdate
  if not record_exists_in_database_for(user):
    error_screen
  final_screen
{% endhighlight %}

Here, there is a function called `record_exists_in_database_for()`
that looks up the user based on the user's name and birthdate.  It is
ok if this function runs every time the screen loads.

However, beginning developers sometimes assume that they can do this:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  user.email
  send_email(to=user, subject="Welcome", body="Welcome to the interview!")
  user.birthdate
  final_screen
{% endhighlight %}

This means that after the user provides their name and e-mail address,
**docassemble** will send them an e-mail.  However, it also means that
every time the screen loads thereafter, **docassemble** will send
another e-mail!  The checklist item should have been written in such a
way that the e-mail is only sent once:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  user.email
  if not task_performed('welcome_email'):
    send_email(to=user, subject="Welcome", body="Welcome to the interview!", task='welcome_email')
  user.birthdate
  final_screen
{% endhighlight %}

The [`task_performed()`] function, combined with the `task` paramater
of the [`send_email()`] function, is one way to ensure that code only
runs once.  Another method is to use a separate [`code`] block that
defines a variable:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  user.email
  email_sent
  user.birthdate
  final_screen
---
code: |
  send_email(to=user, subject="Welcome", body="Welcome to the interview!")
  email_sent = True
{% endhighlight %}

The logic behind the `email_sent` line is: "if `email_sent` is not
defined, run the code block in order to define it; otherwise continue
to the next line."

Another mistake that beginning developers sometimes make is writing a
checklist that results in the user seeing a different screen if they
refresh the screen without providing input.  For example, consider
this interview:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  user.email
  if not task_performed('data_stored'):
    store_data(user)
    mark_task_as_performed('data_stored')
    user.wants_email
    if user.wants_email:
      send_email(to=user, template=confirmation_email)
  user.birthdate
  final_screen
---
question: |
  Do you want a confirmation e-mail?
yesno: user.wants_email
{% endhighlight %}

In this example, after the user provides their e-mail address,
**docassemble** will run the `store_data()` function, then it will
mark the `data_stored` "task" as having been completed, and then it
will see that `user.wants_email` is undefined, so it will ask the user
if they would like to receive a confirmation e-mail.  Suppose that the
user, instead of answering the question, refreshes the screen.  The
interview logic will be evaluated again.  Now, since the `data_stored`
"task" has been marked as complete, the Python code skips the `if`
clause and asks the user for `user.birthdate`.  But this defeats the
user's expectation; the user reasonably expects that when they refresh
the screen, they will see the `user.wants_email` question again.  The
problem is with the interview logic.

Software developers use the term "idempotent" to describe a system
that produces the same result if an action is repeated.  The interview
logic in this circumstance is not idempotent because when it is
repeated, a different result is produced.

Normally, your "checklist" should be designed to result in idempotent
behavior.  The exception would be if the passage of time has made the
"current question" obsolete.  For example, if the user started the
interview before the statute of limitations period expired, and then
tried to continue with the interview after the statute of limitations
period expired, it would be reasonable for the user to see a different
screen when they refreshed the screen.

Another consequence of non-idempotent logic is that users might see a
pop-up message saying "Input not processed."  This is because of a
security feature in **docassemble**: if the browser tries to submit
input for a `question` that is different from what the current
`question` is according to the interview logic, **docassemble** will
reject the browser's attempt to change the interview answers.  In the
example above, if the user clicked "Yes" or "No" in response to the
question "Do you want a confirmation e-mail?", the user would have
seen an "Input not processed" error and been sent to the
`user.birthdate` question.

To fix the idempotency problem, you could take the e-mail sending code
out of the conditional statement:

{% highlight yaml %}
mandatory: True
code: |
  user.name.first
  user.email
  if not task_performed('data_stored'):
    store_data(user)
    mark_task_as_performed('data_stored')
  user.wants_email
  if user.wants_email:
    send_email(to=user, template=confirmation_email)
  user.birthdate
  final_screen
{% endhighlight %}

Writing idempotent logic is also important because of the way that
**docassemble** runs [`code`] blocks.  Consider the following
interview, which has a [`code`] block for calculating the user's total
income:

{% highlight yaml %}
mandatory: True
question: |
  Tell me about your income and expenses.
fields:
  - Benefits income: benefits_income
    datatype: currency
  - Business income: business_income
    datatype: currency
  - Business expenses: business_expenses
    datatype: currency
---
mandatory: True
code: |
  total_income = 0.0
---
mandatory: True
code: |
  total_income = total_income + benefits_income
  total_income = total_income + net_business_income
---
code: |
  net_business_income = business_income - business_expenses
---
mandatory: True
question: |
  Your total income is ${ currency(total_income) }.
{% endhighlight %}

At first glance, this logic looks correct; the interview gathers
information from the user, initializes `total_income` to zero, then
adds the benefits income and the net business income to
`total_income`.  However, you will find that the calculation is
incorrect; `benefits_income` will be counted twice.

The problem is that this [`code`] block is not idempotent:

{% highlight yaml %}
mandatory: True
code: |
  total_income = total_income + benefits_income
  total_income = total_income + net_business_income
{% endhighlight %}

If this code runs more than once, the `total_income` will be increased
each time.  If you try to run this interview, this code block will run
more than once.  The first time it runs, it adds `benefits_income` to
`total_income`, but then stops because `net_business_income` is
undefined.  **docassemble** obtains a definition of
`net_business_income` in microseconds by running the [`code`] block that
defines `net_business_income`.  But after it does that, it does not
resumt where it left off (adding `net_business_income` to
`total_income`).  It will repeat the [`code`] block again, from the
beginning.  So `benefits_income` will be added to `total_income` a
second time, and then `net_business_income` will be added, and then
the "mandatory" block will be marked as having been completed, because
it ran through all the way to the end.

If you are familiar with computer programming, **docassemble** works
by trapping exceptions.  When Python encounters an undefined variable,
it raises an exception.  **docassemble** traps that exception, figures
out what variable was undefined, and then tries to define it.  It does
this either by asking the user a `question` or by running a 'code'
block.  Either way, the exception halts code execution, and Python is
unable pick up exactly where it left off when the exception was
raised.

The solution to this problem is to write the [`code`] block so that it
can be run repeatedly without making a miscalculation:

{% highlight yaml %}
mandatory: True
code: |
  total_income = 0
  total_income = total_income + benefits_income
  total_income = total_income + net_business_income
{% endhighlight %}

This way, the code will produce the correct total no matter how many
undefined variables **docassemble** encounters along the way.

Inexperienced developers also sometimes make the error of assuming
that all [`code`] blocks will run to completion.  For example, suppose
that the above interview was written like this, with only one
`mandatory` block:

{% highlight yaml %}
question: |
  Tell me about your income and expenses.
fields:
  - Benefits income: benefits_income
    datatype: currency
  - Business income: business_income
    datatype: currency
  - Business expenses: business_expenses
    datatype: currency
---
code: |
  total_income = 0.0
  total_income = total_income + benefits_income
  total_income = total_income + net_business_income
---
code: |
  net_business_income = business_income - business_expenses
---
mandatory: True
question: |
  Your total income is ${ currency(total_income) }.
{% endhighlight %}

This interview appears to be reasonable, but actually it contains a
flaw.  When **docassemble** tries to show the [`mandatory`] question, it
encounters an undefined variable `total_income`, so it seeks out a
definition of `total_income`.  It tries to run this [`code`] block:

```
code: |
  total_income = 0.0
  total_income = total_income + benefits_income
  total_income = total_income + net_business_income
```

**docassemble** sets `total_income` to zero, and then encounters an
undefined variable, `benefits_income`, so it asks the `question` that
defines `benefits_income`.  However, what if the user refreshed the
screen on the question that asks for the `benefits_income`?
**docassemble** would attempt to show the [`mandatory`] question again,
and this time `total_income` is defined, so **docassemble** can
display the screen, which says that the total income is zero.  "But
wait," you say, "it didn't finish running the [`code`] block that
defines `total_income`!"  True, but the rule of **docassemble**'s
logic is that it goes through your [YAML], runs [`mandatory`] blocks
that haven't been run before, and tries to obtain definitions for any
undefined variables that are encountered along the way.  Nothing in
this rule says that it will remember if it left a [`code`] block early
and go back to it.

The moral of the story is that if you are going to use dependency
satisfaction, do not allow your dependencies to be satisfied
prematurely.  The [`code`] block should be written instead as:

{% highlight yaml %}
code: |
  total_income = benefits_income + net_business_income
{% endhighlight %}

or
{% highlight yaml %}
code: |
  total_income = benefits_income + net_business_income
  draft_total_income = 0.0
  draft_total_income = total_income + benefits_income
  draft_total_income = total_income + net_business_income
  total_income = draft_total_income
  del draft_total_income
{% endhighlight %}

You can think of the undefined-ness of a variable as **docassemble**'s
incentive to obtain the definition of the variable.  It is like hiring
a busy contractor to do work on your house; if you give the contractor
his final payment after he is only halfway done with the job, he might
leave at the end of the day and forget to come back later to finish
the work.

You might be tempted to combine the definition of several variables in
a single [`code`] block, perhaps because you think it saves space or is
easier to read:

```
code: |
  subtotal = 0
  for item in asset:
    if item.countable:
      subtotal = subtotal + item.value
  total_assets = subtotal
  temp_list = []
  for item in income:
    if item.included and item.type not in income.items:
      temp_list.append(item.type)
  income_items = temp_list
```

Think about what will happen if the interview needs a value of
`total_assets`.  It will run the [`code`] block, and halfway through,
the value of `total_assets` will be obtained.  But the code will not
stop executing; it will go on to start building the `income_items`
list.  This will work fine if the `income` list has been completely
gathered, but what if it has not been?  Then the [`code`] block may
result in the asking of a question about the `income` list, but if the
user refreshes the screen, that question will go away.  This
introduces an idempotency problem.

It is a much better practice to separate your code into single-purpose
`code` blocks:

```
code: |
  subtotal = 0
  for item in asset:
    if item.countable:
      subtotal = subtotal + item.value
  total_assets = subtotal
---
code: |
  temp_list = []
  for item in income:
    if item.included and item.type not in income.items:
      temp_list.append(item.type)
  income_items = temp_list
```

This way, no matter whether your interview needs `total_assets` first
or `income_items` first, and regardless of whether it has already
gathered `income` or `asset`, these [`code`] blocks will perform their
function and deliver a definition without causing any non-idempotent
questions to be asked.

As a general rule, Let each [`code`] block serve a single purpose, or a
set of closely-related purposes, and let it deliver its award (the
defining of the variable sought) on the last line.  If you get into
this habit, you will avoid hard-to-debug logic errors.

Although typically your non-`mandatory` [`code`] blocks should only set
one variable at a time, it is ok if they set other variables
incidentally.  However, in that situation you should probably use the
[`only sets`] modifier.

For example, suppose you have an interview in which you want to ask
the user, "Do you receive income from public benefits?", and you want
to set the variable `has_benefits` to the answer, but as a
double-check on the validity of the answer, you want to set
`has_benefits` to `True` during the income gathering process if the
user indicates that they have income from disability or welfare
income.

{% highlight yaml %}
question: |
  Do you receive income from public benefits?
yesno: has_benefits
---
code: |
  temp_total = []
  for item in income:
    if item.included and item.type not in income.items:
      temp_total.append(item.type)
    if item.type in ['disability', 'welfare']:
      has_benefits = True
  total_income = temp_total
{% endhighlight %}

The problem here is that the income gathering question will now be
called upon to set `has_benefits`.  If `has_benefits` is needed before
`total_income`, the interview will start asking about income items,
but will mysteriously stop in the middle of the process if the user
enters a disability or welfare income item.  Then, when `total_income`
is needed later in the interview, it will resume asking questions
about the income items.  It would be better if you used `only sets`:

{% highlight yaml %}
only sets: total_income
code: |
  temp_total = []
  for item in income:
    if item.included and item.type not in income.items:
      temp_total.append(item.type)
    if item.type in ['disability', 'welfare']:
      has_benefits = True
  total_income = temp_total
{% endhighlight %}

That way, the [`code`] block will only be called upon to define
`total_income`.  It can still have the side effect of setting
`has_benefits` to `True`, but it will not be called upon to define
anything other than `total_income`.

# <a name="order"></a>The logical order of an interview

In the previous sections, we have explained that when **docassemble**
runs your interview, it goes through your [YAML] looking for blocks
that are [`mandatory`], and it tries to run them in order.  When it
encounters an undefined variable, it stops what it is doing and tries
to obtain a definition of that undefined variable.

If a [`mandatory`]<span></span> [`question`] is answered, or a
[`mandatory`]<span></span> [`code`] block's [Python] code runs all the
way through to end, then **docassemble** remembers that the
[`mandatory`] block has been completed, and the next time it evaluates
the interview logic, it will skip over the block.

(Technical note: how does **docassemble** remember that a block has
been completed?  It stores a variable in the interview answers, inside
of a special dictionary called `_internal`.  In order to identify the
blocks that have been completed, it uses the block's [`id`].  If you
do not specify an [`id`] on a [`mandatory`] block, **docassemble**
will generate an identifier like `Question_0` or `Question_1` for the
first and second blocks in your [YAML] file.  This means that if you
have an interview that is "in production" and users have active
sessions in that interview, and then you change the [YAML] to insert
new blocks or move them around, you could cause these identifiers to
change, and then users who started sessions before you changed the
YAML could experience problems where questions they have already
answered are re-asked.  In order to avoid this problem, make sure to
attach a unique [`id`] to each [`mandatory`] block in your interview.
That way, even if you rearrange the [YAML], users with existing
sessions will not experience problems.)

In addition to [`mandatory`], there is a second type of modifier you
can use to force a [`code`] block to be processed.  If you mark a
[`code`] block with `initial: True`, then the block will be run every
time the screen loads, even if it has run before.  The block is
"initial" in the sense that it initializes the interview logic that
will be evaluated during the screen load.

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

# <a name="specifiers"></a>Specifiers that control interview logic

## <a name="mandatory"></a>`mandatory`

By default, all blocks in an interview are optional; they will be
called upon only if needed to retrieve the value of a variable.
However, if all blocks are optional, the interview has nothing to do.
You can use the [`mandatory`] modifier to indicate that a block must be
run.  The first [`mandatory`] block in your interview will be the
starting point of the interview logic when the user first starts the
interview.

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
simple [`mandatory`]<span></span> [`code`] block that sets the
interview in motion.

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

Here, the single [`mandatory`] block contains simple [Python] code that
contains the entire logic of the interview.

If a [`mandatory`] specifier is not present within a block, it is as
though [`mandatory`] was set to `False`.

The value of [`mandatory`] can be a [Python] expression.  If it is a
[Python] expression, the [`question`] or [`code`] block will be
treated as mandatory if the expression evaluates to a true value.

{% include side-by-side.html demo="mandatory-code" %}

It is a best practice to tag all [`mandatory`] blocks with an [`id`].

## <a name="initial"></a>`initial`

The `initial` modifier causes the [`code`] block to be run every time
**docassemble** processes your interview (i.e., every time the screen
loads during an interview).  [`mandatory`] blocks, by contrast, are
never run again during the session if they are successfully "asked"
once.  **docassemble** executes the code in an [`initial`] block in
the same way it executes the code of [`mandatory`] blocks, except that
running to completion does not mean the block will not be executed again.

`initial` blocks should be used in the following situations:

* "Initializing" the Python context in a [multi-user interview]
  depending on who the user is.  For example, if your interview uses a
  variable `user` that should always refer to an [`Individual`] object
  corresponding to the user, you can write an `initial` block that
  looks at `user_info().email` to figure out who the logged-in user
  is.
* When you are using the [actions] feature and you want to make sure
  the [actions] are processed only in particular circumstances.

Here is an example that illustrates how `initial` blocks work:

{% include side-by-side.html demo="initial" %}

Note in this example that from screen to screen, the `counter`
increments from 1 to 2 and then to 4.  The counter does not count the
number of screens displayed, but rather the number of times the
interview logic was evaluated.  The "passes" through the interview are:

1. The interview logic is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The interview then
   tries to run the [`code`] block to get `fruit`, but encounters an
   undefined variable `peaches`, so it asks a question to gather
   `peaches`.
2. The interview logic is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The interview then
   tries to run the [`code`] block to get `fruit`, but encounters an
   undefined variable `pears`, so it asks a question to gather
   `pears`.
3. The interview logic is evaluated, but the evaluation stops when the
   undefined variable `fruit` is encountered.  The interview then runs
   the [`code`] block, and this time, `fruit` is successfully defined.
4. The interview logic is evaluated again, and the final question is
   displayed.

Like [`mandatory`], `initial` can be set to `True`, `False`, or to
[Python] code that will be evaluated to see whether it evaluates to a
true or false value.

If your interview has a single [`mandatory`] code block and it is
incapable of running to completion, then you don't really need an
`initial` block because you can put the logic that needs to run every
time the screen loads at the beginning of that [`mandatory`] block.

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

If any of the variables listed under `need` are undefined,
**docassemble** will obtain their definitions before processing the
content of the [`question`].  For example, suppose you have the
following [`question`]:

{% highlight yaml %}
need:
  - favorite_fruit
question: |
  Your favorite apple is ${ favorite_apple }.
continue button field: fruit_verified
{% endhighlight %}

If both `favorite_fruit` and `favorite_apple` are undefined, the
definition of `favorite_fruit` will be sought first.

What if you wanted `favorite_fruit` to be sought **after**
`favorite_apple`?  To do this, you can use the following special form
of `need`:

{% highlight yaml %}
need:
  post:
    - favorite_fruit
question: |
  Your favorite apple is ${ favorite_apple }.
continue button field: fruit_verified
{% endhighlight %}

In this case, the definition of `favorite_fruit` will be sought after
all of the prerequisites of the `question` have been satisfied.

You can organize your `need` items into `pre` and `post` items:

{% highlight yaml %}
need:
  pre:
    - favorite_vegetable
  post:
    - favorite_fruit
{% endhighlight %}

You can also include `post` among a list of other items:

{% highlight yaml %}
need:
  - favorite_vegetable
  - post:
      - favorite_fruit
{% endhighlight %}

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

If `reconsider` is set to `True` on a [`code`] block, then
**docassemble** will always "reconsider" the values of any of the
variables set by the block.  That is, every time the interview is
assembled (every time the screen loads) **docassemble** will forget
about the value of any of the variables set by the [`code`] block.

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
[`review`]: {{ site.baseurl }}/docs/fields.html#review
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
[gathering groups]: {{ site.baseurl }}/docs/groups.html
[`task_performed()`]: {{ site.baseurl }}/docs/functions.html#task_performed
[`only sets`]: {{ site.baseurl}}/docs/modifiers.html#only sets
[Python expressions]: http://stackoverflow.com/questions/4782590/what-is-an-expression-in-python
[Python expression]: http://stackoverflow.com/questions/4782590/what-is-an-expression-in-python
[Python exception]: https://docs.python.org/3/tutorial/errors.html
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
