---
layout: docs
title: Scheduled tasks
short_title: Scheduled tasks
---

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
mandatory: true
code: |
  use_cron = True
  multi_user = True
---
initial: true
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
mandatory: true
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
[server-side encryption].

{% highlight yaml %}
---
mandatory: true
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
initial: true
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
mandatory: true
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
[special variable] [`cron_daily`].  This code will run once per day.

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

# <a name="enabling"></a>Enabling scheduled tasks

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

# What the "cron" module does

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

# <a name="cron user"></a>The cron user

Scheduled tasks do not run as the user who started the interview; they
always run using the special "cron user."  Therefore, if you want your
scheduled task to send an e-mail to "the user," make sure you collect
the real user's e-mail address into a variable beforehand.  During the
scheduled task, a call to [`user_info()`] will retrieve information
about the "cron user," which is not what you want.

[cron user]: #cron user
[interview deletion]: #deleting
[Docker]: {{ site.baseurl }}/docs/docker.html
[installed]: {{ site.baseurl }}/docs/installation.html
[cron]: https://en.wikipedia.org/wiki/Cron
[configured]: {{ site.baseurl }}/docs/config.html#interview_delete_days
[`current_datetime()`]: {{ site.baseurl }}/docs/functions.html#current_datetime
[`date_difference()`]: {{ site.baseurl }}/docs/functions.html#date_difference
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[`task_not_yet_performed()`]: {{ site.baseurl }}/docs/functions.html#tasks
[task system]: {{ site.baseurl }}/docs/functions.html#tasks
[`cron_daily`]: {{ site.baseurl }}/docs/special.html#cron_daily
[special variable]: {{ site.baseurl }}/docs/special.html
[`template`]: {{ site.baseurl }}/docs/template.html
[`leave`]: {{ site.baseurl }}/docs/questions.html#leave
[`exit`]: {{ site.baseurl }}/docs/questions.html#exit
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`event`]: {{ site.baseurl }}/docs/fields.html#event
[events]: {{ site.baseurl }}/docs/fields.html#event
[interview logic]: {{ site.baseurl }}/docs/logic.html
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`code`]: {{ site.baseurl }}/docs/code.html
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[functions]: {{ site.baseurl }}/docs/functions.html
[`use_cron`]: {{ site.baseurl }}/docs/special.html#use_cron
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[server-side encryption]: {{ site.baseurl }}/docs/security.html#server_encryption
[virtualenv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[Python]: https://www.python.org/
[`docassemble.webapp.cron`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/cron.py
[action]: {{ site.baseurl }}/docs/functions.html#actions
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`cron_hourly`]: {{ site.baseurl }}/docs/special.html#cron_hourly
[`cron_daily`]: {{ site.baseurl }}/docs/special.html#cron_daily
[`cron_weekly`]: {{ site.baseurl }}/docs/special.html#cron_weekly
[`cron_monthly`]: {{ site.baseurl }}/docs/special.html#cron_monthly
[`user_info()`]: {{ site.baseurl }}/docs/functions.html#user_info
