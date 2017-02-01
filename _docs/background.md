---
layout: docs
title: Running code behind the scenes
short_title: Background code
---

Usually, your interview [code] runs whenever the user is "between
screens."  The process goes like this:

1. The user submits information from a **docassemble** screen (e.g.,
   by pressing the "Continue" button).
2. The user's device sends information to the **docassemble** server.
3. The server updates the interview variables based on that information.
4. The server then [evaluates the interview], using the updated
   interview variables, which may cause [code] to be run.
4. The server sends a new screen back to the user's device.
5. The user sees the new screen.

You may find this process too limiting for you as an interview author
if you want your [code] to run at other times.

For example:

1. If your code takes a very long time to run, the user will have to
   wait, looking at a spinner.  For example, your code may trigger a
   factual investigation process that retrieves information from a
   variety of sources on the internet, which takes a long time to
   retrieve and process.  The user may think the interview crashed
   when in fact it is hard at work.  It would be better if the
   code could run in the background while the user continues to
   interact with the interview.
2. You may want to process the user's input before the user presses
   the "Continue" button.  For example, when you conduct an interview
   in real life, you can interrupt the interviewee if he or she goes
   off on a tangent.  You may want to do the same in an electronic
   interview.  If your interview processes information that users type
   into a [large text box], your users might spend a great deal of
   time typing their life story into the text box, when the first
   sentence of the user's narrative would suffice.  If your interview
   could process the user's input as they are typing it, similar to
   the way Google gives you search suggestions as you are typing, you
   could return feedback to the user as they are typing, letting them
   know that they can stop typing.
3. If your interview guides a user through a process that lasts
   several months, you might want your interview to send an e-mail to
   the user on a particular date in the future to remind them about
   something.

There are features in **docassemble** that address each of these
limitations.

1. If you have [`code`] that takes a long time to run, you can run it
   in a [background process].
2. If you want to process user input before the user submits it, you
   can cause the user's web browser to [check in] with the server
   every few seconds and update the user's screen with the results.
3. If you want to schedule [`code`] to run at times when the user is
   not using **docassemble**, you can create a [scheduled task].

The following sections explain these features.

# <a name="background"></a>Background processes for time-consuming code

If you include code in your interview that takes a long time to run,
such as code that looks up information in an on-line database, the
screen will take a long time to load and the user may think that the
application has "crashed" when it is actually just working normally.

To get around this problem, **docassemble** allows interview authors
to run code in "background processes."  While the user is answering
other questions, or looking at a user-friendly screen that instructs
the user to wait, the **docassemble** server can be hard at work
carrying out time-consuming tasks for the user.

These processes can even operate in parallel.  For example, if your
interview searches the user's name in four different on-line
databases, all of these searches can be carried out simultaneously,
which will return a result to the user much faster than if the
searches were carried out one after the other.

**docassemble** runs these background tasks using [Celery], a
"distributed task queue" system.  [Celery] is highly scalable.  If you
are running **docassemble** on a single server and an interview starts
100 tasks at the same time, [Celery] will will queue the tasks and
handle them in order, working on several of them at a time.  And if
background tasks are particularly important for your application, you
can install [multiple servers] dedicated to handling these tasks.

To run code in the background, use the [`background_action()`]
function in combination with [`background_response()`] or
[`background_response_action()`].

The next subsections explain how these functions work.

## <a name="background_action"></a>background_action()

Here is an example that uses a background task to add a user-supplied
number to 553 and return the result.

{% include side-by-side.html demo="background_action" %}

Briefly, here is what happens in this interview.

1. The interview tries to [evaluate] the [`mandatory`] block.  The
   variable `the_task` is undefined, so the interview tries to define
   it by running [`background_action()`].  However, the interview
   finds that `value_to_add` is undefined, so it asks the user "How
   much shall I add to 553?"
2. The next time the interview is evaluated, [`background_action()`]
   runs successfully because `value_to_add` is now defined.  The
   [`background_action()`] function starts an [action] running in the
   background that adds `value_to_add` to the number 553.  The
   variable `the_task`, representing the status of the background task,
   is defined.
3. The call to `the_task.ready()` returns `False` because the task is
   still running, so the `waiting_screen` is shown.
4. Since the `waiting_screen` has the [`reload` modifier] set, the
   screen reloads after ten seconds.
5. In the meantime, the `bg_task` [action] is running in the
   background and finishes the calculation.
6. The next time the screen loads, `the_task.ready()` will return
   `True`, and the `final_screen` will be shown.  The `final_screen`
   question calls `the_task.get()` to retrieve the calculated value.

Starting a background process involves calling the
`background_action()` function.

{% highlight yaml %}
---
code: |
  the_task = background_action('bg_task', None, additional=value_to_add)
---
{% endhighlight %}

The first argument to [`background_action()`], `bg_task`, is the name
of an [action] available in the interview.  Notice that the next block
is identified with `event: bg_task`; this is the block that contains
the code you want to run in the background.

The second argument to [`background_action()`] indicates how the
result of the [action] should be communicated to the user.  In this
case, `None` means no communication (more on this
setting [below](#ui_notification)).

The keyword argument, `additional`, is an argument that is passed to
the [action] (which can be retrieved with [`action_argument()`]).  You
can have as many keyword arguments as you want, called anything you
want.  You can also have no keyword arguments at all.

The `background_action()` function returns an object that represents a
[Celery] "task."  In this example, the object is saved to a variable
called `the_task`.  This variable can be used in the following ways:

* `the_task.ready()` returns `True` if the task has been completed
  yet, and `False` if not.
* `the_task.get()` returns the result of the task, if available.

[Celery] will start trying to run the `bg_task` [action] as soon as
possible after `background_action()` is called.  If a lot of other
tasks are already running, the task will go into a queue and will be
run as soon as a [Celery] "worker" is available.

Regardless of how long the `bg_task` [action] takes to finish, the
`background_action()` function will always return a response right
away.  This means that when your interview starts a time-consuming
background task, the server will immediately present the user with a
new screen instead of making the user wait for the screen to load.
The `bg_task` [action] will run in the background, independently of
whatever goes on between the user and the interview.  It will continue
running even if the user exits the browser.

The `bg_task` [action] runs in much the same way as an [action]
invoked by the user clicking on a hyperlink generated by
[`url_action()`].  (The parameters to `background_action()` will be
familiar if you have ever used [`url_action()`].)

{% highlight yaml %}
---
event: bg_task
code: |
  # This is where time-consuming code
  # would go
  background_response(553 + action_argument('additional'))
---
{% endhighlight %}

The code in a background action can use the [`action_argument()`] and
[`action_arguments()`] functions to access the [action] parameters.
It can use the [`user_logged_in()`], [`user_has_privilege()`], and
[`user_info()`] functions to determine information about the current
user (i.e. the user who caused the `background_action()` function to
be called).  In this respect, background actions are different from
[scheduled tasks], which always run as the special "[cron user]."  In
addition, background tasks are different from [scheduled tasks] in
that you can run background tasks regardless of whether [`multi_user`]
is set to `True` or `False`.

There is one important factor about [actions] invoked through
`background_action()`, which is that any changes made to variables by
a background action will not be remembered after the action finishes.
In order to communicate back to the interview, you need to use
[`background_response()`] or [`background_response_action()`]
(discussed below).

This limitation exists because background actions are intended to run
at the same time the user is answering questions in the interview.  If
the background process starts at 3:05 p.m. and finishes at 3:10 p.m.,
but the user answers five questions between 3:05 p.m. and 3:10 p.m.,
the user's changes would be overwritten if the background process
saved its changes at 3:10 p.m.

The [`background_response()`] function is the simplest way to return a
value to the interview, but you may want to use
[`background_response_action()`] if you want to make permanent changes
to the interview variables based on the code that is run in the background.

## <a name="background_response"></a>background_response()

The `background_response()` function allows you to return information
from a background action to the interview.  The information is
accessed by using the `.get()` method on the "task" that was created.

For example, in the above example, the task is created like this:

{% highlight python %}
the_task = background_action('bg_task', None, additional=value_to_add)
{% endhighlight %}

There is now a variable `the_task` in the interview, which is used to
keep track of the status of the `bg_task` action, which is running in
the background.

The `bg_task` action does not permanently change any of the variables
in the interview, but it passes its result back to the interview using
`background_response()`.

{% highlight python %}
background_response(553 + action_argument('additional'))
{% endhighlight %}

The response value is the sum of 553 and whatever number was provided
in the `additional` parameter.  Note that this value is not saved to
any variable.  (Even if a background action _tried_ to make a change
to variables in the interview's dictionary, those changes would be
forgotten once the action completes.)

The interview can retrieve the value passed to `background_response()`
by calling the `.get()` method on the `the_task` variable.  For
example,

{% highlight yaml %}
question: |
  The answer is ${ the_task.get() }.
{% endhighlight %}

## <a name="background_response_action"></a>background_response_action()

It is possible for long-running tasks to save information to the
interview's dictionary, but they need to do so by sending the
information to a separate "action," the purpose of which is to save
the information to the interview's dictionary.  Information can be
passed to the action as arguments.

{% include side-by-side.html demo="background_action_with_response_action" %}

In this example, the action that runs in the background is `bg_task`
and the action that changes the interview's dictionary is `bg_resp`.

{% highlight yaml %}
---
event: bg_task
code: |
  value = 553 + action_argument('additional')
  background_response_action('bg_resp', ans=value)
---
event: bg_resp
code: |
  answer = action_argument('ans')
---
{% endhighlight %}

The `bg_task` action finishes by calling
`background_response_action('bg_resp', ans=value)`.
(`background_response_action()`, like other functions including
[`background_response()`], [`message()`], [`command()`], and
[`response()`], tells **docassemble** to stop whatever it is doing.
**docassemble** will not process any code that follows
`background_response_action()`.)

The first argument to `background_response_action()` is the name of
the action to be run, and the remainder of the arguments are keyword
arguments that are provided to the action.  In the above example, The
`bg_resp` action retrieves the argument `ans` and changes the variable
`answer` in the interview's dictionary to the value of `ans`.

The idea here is that `bg_task` is a long-running task, while
`bg_resp` is a short-running task devoted only to saving the results
of the long-running task.

When the code for the `bg_resp` action runs, it runs separately from
the `bg_task` action.  If `bg_task` changes a variable in the
interview's dictionary, the `bg_resp` action will not be able to see
those changes.  The only way the `bg_task` action can send information
to the `bg_resp` action is by passing arguments to it via the
`background_response_action()` function.

In computer science terminology, the `bg_resp` action is similar to a
[callback function].

## <a name="ui_notification"></a>Communicating results to the user interface

**docassemble** can automatically alert the user when a background job
finishes.  There are three ways this can be done.

The first way is to "flash" a message at the top of a user's screen.

The second way is to cause the user's screen to reload the interview
when the job finishes.  If you used [`background_response_action()`]
to change the interview's dictionary on the basis of work done by the
background process, then the user may see a different screen after the
interview reloads.  However, it is important to be mindful of the
users' perspective when using this feature; you would not want to
annoy users by refreshing their screens while they are in the middle
of entering information.

The third way is to cause the user's browser to run [Javascript] code
produced by your background process.

You can cause these responses by setting the second argument to
[`background_action()`] to `'flash'`, `'refresh'`, or `'javascript'`.
Setting the second argument to `None` means that no notification of
any kind will be sent to the user's browser.

In the following example, the value provided to
[`background_response()`] (e.g., "The answer is 555."), is
"flashed" at the top of the screen.

{% include side-by-side.html demo="background_action_flash" %}

You can also "flash" messages when you use
[`background_response_action()`] to run a separate [action]
that saves changes to the interview's dictionary.  In your action that
sets variables, conclude your code with a call to
[`background_response()`] containing the message you want to flash.

{% include side-by-side.html demo="background_response_action_flash" %}

In the next example, when the background process finishes, the user's
screen refreshes.  Since the [`background_response_action()`] function
was used to save the result of the background process to a variable
(`answer`), the result can be displayed by referring to `${ answer }`.

{% include side-by-side.html demo="background_action_refresh" %}

The next example is like the first, except the notification takes
place through [Javascript] code created by the background process,
which in this case uses the built-in [Javascript] function
[`alert()`] to send a message to the user.

{% include side-by-side.html demo="background_action_javascript" %}

Note that the user interface does not respond immediately when the
background task finishes.  The user's browser polls the server every
six seconds (edit [`checkin interval`] to adjust this).  Therefore,
users may experience up to a six-second delay after the background
process finishes before they receive notification.

## Comparison with scheduled tasks

**docassemble** also has a [scheduled tasks] feature, which is similar
to the [background processes] feature in that the code runs in the
background, without any direct interaction with the user.  The
[scheduled tasks] are different in that they are triggered at monthly,
weekly, daily, or hourly intervals, rather than being triggered by the
user.

Another difference is that [scheduled tasks] are always run by a
[special user], and this requires that server-side encryption be
disabled in the interview.  These restrictions do not apply to
[background processes].

# <a name="check in"></a>Processing interim user input

## Communicating interim information to the interview

If you set the `check in` modifier on a [`question`], the user's
browser will "check in" with the interview every few seconds and run
the given [action].  The arguments to the action (which can be
retrieved with [`action_argument()`]) will be the current values of
the fields on the screen.

{% include side-by-side.html demo="check-in" %}

The value of `check in` is the name of the [action] that should be run
(in this case, `track_drafts`). Any changes made to the interview
variables during the [action] are saved.

The "check in" process takes place:

* Every six seconds, as well as
* Every time a "change" event takes place on an input element.  For
  text inputs, this happens when the "focus" leaves the text box, as
  it does when the user clicks outside the text box or presses the tab
  key.

In the above example, a counter is incremented each time the browser
"checks in."  In addition, the current value of `favorite_food` is
tracked in a [Python set] called `drafts`.  The actual variable
`favorite_food` is not set until the user presses "Continue," but the
`track_drafts` code discovers the "draft" value by calling
[`action_argument()`].

## <a name="target"></a>Updating the screen

You can also use `check in` to communicate information back to the
screen.

In the example above, [`check in`] referred to a [`code`] block.  In
the example below, [`check in`] refers to a [`template`] block.  The
`content` of the [`template`] is inserted into the user's screen in an
area designated by the [`template`]'s `target`.

{% include side-by-side.html demo="target-template" %}

If the user types "apples," the following message will appear:

![Real time feedback]({{ site.baseurl }}/img/target-template.png)

The timeline for this process is as follows:

1. When the screen is drawn, the `[TARGET feedback]` markup in the
   [`under`] text area of the question (the area underneath the
   "Continue" button) is converted into an invisible placeholder area
   identified by the keyword `feedback`.
2. The user types "apples" into the "Favorite food" field.
3. The browser "checks in" with the server, sending the values of all
   the fields on the page.
4. On the server, **docassemble** seeks a definition for
   `question_food`.  It finds a [`template`] that offers to define
   `question_food`.  This [`template`] has a `target`, so it will
   behave differently than ordinary [`template`]s.  Instead of setting
   the variable `question_food` to a [`DATemplate`] object,
   **docassemble** will return the `content` to the browser,
   indicating that it is "targeted" for the area on the screen called
   `feedback`.
4. The web browser takes the content and plugs it into the invisible
   placeholder area identified by the keyword `feedback`.

If you want to run [`code`] and then use a [`template`] to communicate
results back to the user, just include a reference to the [`template`]
at the end of your [`code`]:

{% include side-by-side.html demo="target-code-template" %}

Another way to send messages to the user's screen is to use [`code`]
to plug raw [HTML] into `[TARGET ...]` areas:

{% include side-by-side.html demo="target-code" %}

Calling [`background_response()`] with the keyword arguments `target`
and `content` will result in the `content` being plugged into the
user's screen in the `[TARGET ...]` area designated by the `target`
argument.  Unlike the method that uses [`template`]s, this method does
not convert [Markdown] to [HTML]; rather, the `content` is inserted as
raw [HTML].

If you want to plug text into more than one `[TARGET ...]` area, you
can do so by calling [`background_response()`] with a [list] of
[dict]s, where each [dict] has the keys `target` and `content`.

{% include side-by-side.html demo="target-code-multiple" %}

If you know [Javascript], there are a variety of other ways you can
change the user's screen through communicating with the server.  See
the [Javascript functions] section for more information.

# <a name="scheduled"></a>Scheduled tasks

The "scheduled tasks" feature of **docassemble** allows your
interviews to do things when the user is not using the interview.

For example, if your interview guides a user through a legal process
that requires the user to file a document in court if the opposing
party does not respond within 20 days, your interview can send an
e-mail to the user after that 20 day period has expired, reminding the
user to resume the interview so that he or she can prepare the
appropriate legal document.

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
mandatory: True
code: |
  use_cron = True
  multi_user = True
---
initial: True
code: |
  process_actions()
---
question: |
  When was the document filed?
fields:
  - Filing Date: filing_date
    datatype: date
---
question: |
  What is your e-mail address?
fields:
  - E-mail: email_address
    datatype: email
---
mandatory: True
question: |
  Ok, I'll e-mail you at ${ email_address} 20 days
  from ${ format_date(filing_date) }.
buttons:
  Leave: leave
---
template: reminder_email
subject: |
  Hey, it's been 20 days.
content: |
  Don't forget about that thing you need to do!
---
event: cron_daily
code: |
  if task_not_yet_performed('20 day reminder') and date_difference(starting=filing_date).days > 20:
    send_email(to=email_address, template=reminder_email, task='20 day reminder')
---
{% endhighlight %}

Let's go through this example step-by-step.

First, we use [`modules`] to load [`docassemble.base.util`], which
provides a lot of the special [functions] we need.

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
{% endhighlight %}

Second, we set [`use_cron`] to `True`, which allows scheduled tasks to
run, and we set [`multi_user`] to `True`, which disables
[server-side encryption].  (We need to disable this feature so that
the computer can access the interview when the user is not logged in.
The user's data is still secure; it just does not have a layer of
special additional security.)

{% highlight yaml %}
---
mandatory: True
code: |
  use_cron = True
  multi_user = True
---
{% endhighlight %}

Then, we set up some [`initial`]<span></span> [`code`] so that the
[`process_action()`] function runs every time the [interview logic] is
processed.  This causes the [`code`] within [events] to be run, such
as the `cron_daily` [`event`], which appears later on in the
interview.

{% highlight yaml %}
---
initial: True
code: |
  process_actions()
---
{% endhighlight %}

Next, there are three standard [`question`]s that gather the
`filing_date` and `email_address` variables and present a "final"
screen to the user.  Note that on the final screen, there is no
[`exit`] button, only a [`leave`] button.  If the user clicked an
[`exit`] button, the interview session would be erased from the
server.  By contrast, clicking [`leave`] retains the interview session
on the server.  This is important because we want the interview to
persist on the server.  We need the interview to exist twenty days
after the `filing_date` so that it can send the reminder e-mail.

{% highlight yaml %}
---
question: |
  When was the document filed?
fields:
  - Filing Date: filing_date
    datatype: date
---
question: |
  What is your e-mail address?
fields:
  - E-mail: email_address
    datatype: email
---
mandatory: True
question: |
  Ok, I'll e-mail you at ${ email_address} 20 days
  from ${ format_date(filing_date) }.
buttons:
  Leave: leave
---
{% endhighlight %}

After this, we define the [`template`] for the e-mail that will be sent.

{% highlight yaml %}
---
template: reminder_email
subject: |
  Hey, it's been 20 days.
content: |
  Don't forget about that thing you need to do!
---
{% endhighlight %}

Finally, we get to the "scheduled task."  The [`event`] uses the
[special variable]<span></span> [`cron_daily`].  This code will run once per day.

{% highlight yaml %}
---
event: cron_daily
code: |
  if task_not_yet_performed('20 day reminder') and date_difference(starting=filing_date).days > 20:
    send_email(to=email_address, template=reminder_email, task='20 day reminder')
---
{% endhighlight %}

The first thing the code does (wisely) is question whether the e-mail
reminder has already been sent.  If the e-mail has already been sent,
it would be annoying to send the same e-mail again, every single day,
so we prevent that from happening.  The [`task_not_yet_performed()`]
function is part of **docassemble**'s [task system].

Next, the code evaluates whether the 20 day period has passed, using
the [`date_difference()`] function.  If at least 20 days have passed,
the e-mail is sent.  The [`send_email()`] function marks the "task" as
"performed" if the e-mail successfully sends.

## <a name="enabling"></a>Enabling scheduled tasks

Scheduled tasks need to be triggered by some external source.  On
Linux, the trigger can be a script installed as part of the [cron]
system.  For example, a script in `/etc/cron.daily` could run:

{% highlight bash %}
python -m docassemble.webapp.cron -type cron_daily
{% endhighlight %}

A script in `/etc/cron.weekly` could run:

{% highlight bash %}
python -m docassemble.webapp.cron -type cron_weekly
{% endhighlight %}

(And so on.)

The details of how exactly this command should be invoked depend on
how you have [installed] **docassemble**.  For example, the command
should run under the same user as the web server, and if you have
installed Python using a [virtualenv], you need to invoke [Python]
appropriately.

If you run **docassemble** on [Docker], you do not have to worry about
any of these implementation details; the cron tasks operate
automatically.  The tasks enabled in the [Docker] setup are:

* `cron_hourly`
* `cron_daily`
* `cron_weekly`
* `cron_monthly`

Note that you can use any variable name you want in the `-type`
argument to the [`docassemble.webapp.cron`] module.  The variable name
passed to the interview exactly as though it were the name of an
[action] given by [`url_action()`].

## What the "cron" module does

The [`docassemble.webapp.cron`] module does two things: it cleans out
inactive interviews and runs scheduled tasks in interviews.

## <a name="deleting"></a>Deleting interviews after a period of inactivity

If the type of scheduled task is `cron_daily`, the
[`docassemble.webapp.cron`] module will delete interviews that have
been inactive for 90 days or longer.  (This period can be
[configured].)  Activity is measured by whether the interview answers
have been updated within the period.  This applies to all interviews
stored in the system that have not yet been deleted.

Note that interviews can be deleted from the system two other ways:

1. When the user clicks an [`exit`] button; and
2. If the user goes to the Interviews page and clicks a "Delete"
   button next to a listed interview.

## Running scheduled tasks

The [`docassemble.webapp.cron`] looks at every interview in the system
for which [server-side encryption] has been turned off.  (This is done
by setting [`multi_user`] to `True`).  The module then inspects the
interview data to see if [`use_cron`] is set to `True`.  If is, it
will see if the interview uses the variable given with the `-type`
argument.  For example, if the type is [`cron_weekly`], the module
will check if the interview has a block that offers to define the
variable [`cron_weekly`].  If there is such a block, the module will
run the interview with the [action] `cron_weekly` (and no [action]
arguments).

Note that interviews containing scheduled tasks will run regularly,
and the answers will be updated regularly.  Even if there is no
activity from the original user, there is activity in the interview.
This means that the [interview deletion] feature will never delete
such interviews.  Usually, it is a good thing that the
[interview deletion] feature does not automatically delete interviews
with scheduled tasks; you might have an interview that does something
after a period of several months have passed.

However, you might not want your interviews to run scheduled tasks
indefinitely.  For example, in the example interview above, the
interview will persist after the e-mail sends, and will stay on the
server forever.  The [`cron_daily`] code will run on a daily basis
forever, doing nothing useful.

To get around this problem, you can instruct your scheduled task to
delete the interview when it is no longer necessary to keep the
interview alive.  For example, you can include the following:

{% highlight yaml %}
---
event: cron_monthly
code: |
  if last_access_days() > 365:
    command('exit')
---
{% endhighlight %}

This will run on a monthly basis, and will check whether interview has
been accessed by a real user (that is, a user other than the
[cron user]) in the past year.  If it has not, the interview will
[`exit`], meaning that the interview will be deleted from the server.

## <a name="cron user"></a>The cron user

Scheduled tasks do not run as the user who started the interview; they
always run using the special "cron user."  Therefore, if you want your
scheduled task to send an e-mail to "the user," make sure you collect
the real user's e-mail address into a variable beforehand.  During the
scheduled task, a call to [`user_info()`] will retrieve information
about the "cron user," which is not what you want.

If your interview is a [multi-user interview], make sure that the
"cron user" is not inadvertently kicked out of your interview before
[`process_action()`] is run.  For example, an interview with this code
could prevent scheduled tasks from running:

{% highlight yaml %}
---
default role: organizer
code: |
  multi_user = True
  role = 'organizer'
  if introduction_made and participants_invited:
    if user_logged_in():
      if user_info().email == first_person_email:
        role = 'first_person'
      elif user_info().email == second_person_email:
        role = 'second_person'
---
initial: True
code: |
  if role != first_person' and not ready_for_other_people:
    say_goodbye_to_user
---
initial: True:
code: |
  process_actions()
---
event: cron_daily
code: |
  do_something_important()
---
{% endhighlight %}

When the "cron user" accesses this interview, it will not be able to
run the `cron_daily` action, because it will immediately be presented
with the `say_goodbye_to_user` screen.

One way to get around this problem is to move the [`initial`]
<span></span> [`code`] block that runs  `process_actions()` so that it
appears before the block that runs `say_goodbye_to_user`:

{% highlight yaml %}
---
initial: True:
code: |
  process_actions()
---
initial: True
code: |
  if role != first_person' and not ready_for_other_people:
    say_goodbye_to_user
---
{% endhighlight %}

This opens up the possibility that someone in the role of
`second_person` could run [actions] without being screened.  If this
is a problem, you could alternatively do:

{% highlight yaml %}
---
initial: True
code: |
  if (role != first_person' and not user_has_privilege('cron')) and not ready_for_other_people:
    say_goodbye_to_user
---
{% endhighlight %}

The "cron user" is the only user on the system with the [privilege] of
`cron`, so you can use the [`user_has_privilege()`] function to detect
whether the user is the "cron user."

[Celery]: http://www.celeryproject.org/
[Docker]: {{ site.baseurl }}/docs/docker.html
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
[Python]: https://www.python.org/
[`action_argument()`]: {{ site.baseurl }}/docs/functions.html#action_argument
[`action_arguments()`]: {{ site.baseurl }}/docs/functions.html#action_arguments
[`alert()`]: http://www.w3schools.com/jsref/met_win_alert.asp
[`background_action()`]: #background_action
[`background_response()`]: #background_response
[`background_response_action()`]: #background_response_action
[`checkin interval`]: {{ site.baseurl }}/docs/config.html#checkin interval
[`code`]: {{ site.baseurl }}/docs/code.html
[`command()`]: {{ site.baseurl }}/docs/functions.html#command
[`cron_daily`]: {{ site.baseurl }}/docs/special.html#cron_daily
[`cron_hourly`]: {{ site.baseurl }}/docs/special.html#cron_hourly
[`cron_monthly`]: {{ site.baseurl }}/docs/special.html#cron_monthly
[`cron_weekly`]: {{ site.baseurl }}/docs/special.html#cron_weekly
[`current_datetime()`]: {{ site.baseurl }}/docs/functions.html#current_datetime
[`date_difference()`]: {{ site.baseurl }}/docs/functions.html#date_difference
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`docassemble.webapp.cron`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/cron.py
[`event`]: {{ site.baseurl }}/docs/fields.html#event
[`exit`]: {{ site.baseurl }}/docs/questions.html#exit
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`leave`]: {{ site.baseurl }}/docs/questions.html#leave
[`message()`]: {{ site.baseurl }}/docs/functions.html#message
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`response()`]: {{ site.baseurl }}/docs/functions.html#response
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[`set_info()`]: {{ site.baseurl }}/docs/functions.html#set_info
[`task_not_yet_performed()`]: {{ site.baseurl }}/docs/functions.html#tasks
[`template`]: {{ site.baseurl }}/docs/template.html
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`use_cron`]: {{ site.baseurl }}/docs/special.html#use_cron
[`user_has_privilege()`]: {{ site.baseurl }}/docs/functions.html#user_has_privilege
[`user_info()`]: {{ site.baseurl }}/docs/functions.html#user_info
[`user_logged_in()`]: {{ site.baseurl }}/docs/functions.html#user_logged_in
[action]: {{ site.baseurl }}/docs/functions.html#actions
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[background process]: #background
[background processes]: #background
[callback function]: https://en.wikipedia.org/wiki/Callback_(computer_programming)
[code]: {{ site.baseurl }}/docs/code.html
[configured]: {{ site.baseurl }}/docs/config.html#interview_delete_days
[cron user]: #cron user
[cron]: https://en.wikipedia.org/wiki/Cron
[events]: {{ site.baseurl }}/docs/fields.html#event
[functions]: {{ site.baseurl }}/docs/functions.html
[installed]: {{ site.baseurl }}/docs/installation.html
[interview deletion]: #deleting
[interview logic]: {{ site.baseurl }}/docs/logic.html
[multi-user interview]: {{ site.baseurl }}/docs/roles.html
[multiple servers]: {{ site.baseurl }}/docs/scalability.html
[privilege]: {{ site.baseurl }}/docs/users.html
[scheduled task]: #scheduled
[scheduled tasks]: #scheduled
[server-side encryption]: {{ site.baseurl }}/docs/security.html#server_encryption
[special user]: #cron user
[special variable]: {{ site.baseurl }}/docs/special.html
[task system]: {{ site.baseurl }}/docs/functions.html#tasks
[virtualenv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[large text box]: {{ site.baseurl }}/docs/fields.html#area
[Javascript functions]: {{ site.baseurl }}/docs/functions.html#javascript
[`under`]: {{ site.baseurl }}/docs/questions.html#under
[check in]: #check in
[`check in`]: #check in
[Python set]: https://docs.python.org/2/library/stdtypes.html#set
[`DATemplate`]: {{ site.baseurl }}/docs/objects.html#DATemplate
[HTML]: https://en.wikipedia.org/wiki/HTML
[list]: https://docs.python.org/2.7/tutorial/datastructures.html
[dict]: https://docs.python.org/2/library/stdtypes.html#dict
[evaluates the interview]: {{ site.baseurl }}/docs/logic.html
[`reload` modifier]: {{ site.baseurl }}/docs/modifiers.html#reload
[evaluate]: {{ site.baseurl }}/docs/logic.html
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
