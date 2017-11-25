---
layout: docs
title: User login system
short_title: User Login
---

**docassemble** has a built-in username and password system.  Users
can click "Log in" in the upper-right-hand corner to log in, and if
they do not have a username and password on the system, they can
register.

End users who are not logged in will lose their session information if
they close their web browser.  If they register and log in, however,
they can fill out part of an interview, close the web browser, log
back in again, and pick up where they left off.

When a user registers in the **docassemble** system, their default
"privilege" is that of "user," which has the lowest privileges.  There
are seven privileges defined by default in **docassemble**:

* user
* admin
* cron
* customer
* developer
* advocate
* trainer

A user who has the "admin" privilege can upgrade the privleges of any
user by going to the [User List] on the menu.  The user can add
additional privileges by going to the [Privileges List].

The "cron" user privilege is used exclusively by the code that runs
[scheduled tasks].

When **docassemble** is first installed, it creates a user with
"admin" privileges with the following login information:

* Email: admin@admin.com
* Password: password

As soon as **docassemble** is set up, you should log in as this user,
go to [User List], edit the admin@admin.com user, and change its e-mail
address and password.

You can also change these defaults during [installation] by editing the
[configuration] before running the [`create_tables.py`] script from the
[`docassemble.webapp`] package.

Users can log in with Facebook, Google, Twitter, or Microsoft Azure.
This requires obtaining API keys with those companies.  See the
documentation for the [`oauth`] configuration directive for details.
Users can also log in with their mobile phone by receiving a
verification code via [SMS].  See the documentation for the
[`phone login`] and [`twilio`] configuration directives for details.

Users who log in with an e-mail address and password have the
additional option of using [two-factor authentication].

If you do not want your users to be able to log in, you can hide the
"Sign in or sign up to save answers" link by setting the
[`show login`] setting in the [configuration].

When a user is logged in, the user's information is made available to
**docassemble** interviews through the [`user_info()`] function.

# User administration

## <a name="profile">Profile</a>

All registered users can edit their "Profile" from the user menu.  The
fields available include:

* First name
* Last name
* Country Code (must be an official [country code] like `us`)
* First subdivision (e.g., state)
* Second subdivision (e.g., county)
* Third subdivision (e.g., municipality)
* Organization (e.g., company, non-profit organization)

## <a name="user_list">User List</a>

Administrators can go to the "User List" from the menu.  From here,
administrators can edit the profiles of each user in the system.
Users can be deactivated, so that they can no longer log in.
Deactivated accounts can be reactivated.  The privileges of each user
can be edited.  For example, a user with privileges of "user" can be
given the privileges of "developer" or "admin."

## <a name="privileges">Privileges List</a>

Administrators can go to the "Privileges List" by clicking "Edit
Privileges" on the [User List] page.  From here, administrators can
add new privilege types, or delete privilege types that were already
created.

## <a name="add">Add User</a>

Administrators can add users by clicking "Add a user" on the
[User List] page.  The user's first name, last name, e-mail, password,
and user role(s) must be set.

## <a name="invite">Invite User</a>

Administrators can invite people to register by clicking "Invite a
user" on the [User List] page.  **docassemble** will send an e-mail
with a link that the person can click on to register.  If
[`allow registration`] is set to `False`, this is the only way that
users can register on the site.

The administrator can select the role that the user will be assigned
when he or she registers.

The name of the site that is mentioned in the e-mail can be configured
with the [`appname`] directive.  If the [`appname`] is
`MyDocassemble`, the e-mail will look like this:

> You have been invited to join MyDocassemble.
> 
> To register for an account, please click on the link below.
> 
> https://mydocassemble.example.com/user/register?token=Vi7kc6ClSffW5RDKx9Coeg.CySLUQ.dJOwakdJ7F3aluWwr7SYwLAvt18
>
> -- MyDocassemble 

# Screening users

Interviews can behave differently depending on whether the user is
logged in, or the role of the logged-in user.

There are three [functions] that facilitate this:

* [`user_logged_in()`] - returns `True` or `False` depending on
  whether the user is logged in.
* [`user_info()`] - if the user is logged in, this returns information
  from the user's profile
* [`user_has_privilege()`] - returns `True` or `False` depending on
  whether the user has given privileges.

Here is an example of an interview that requires the user to be logged in:

{% highlight yaml %}
initial: true
code: |
  if not user_logged_in():
    kick_out_user
---
event: kick_out_user
question: |
  I am sorry, but you need to log in if you want to use this interview.
buttons:
  - Log in: signin
  - Exit: exit
---
mandatory: true
question: |
  Thanks for completing the interview!
{% endhighlight %}

Note that the use of the [`initial`] modifier is very important here.
It ensures that the interview will check to make sure the user is
logged in every time in the interview is processed.  If the code was
only [`mandatory`], the user could log in, then log out, and still use
the interview, because once a [`mandatory`]<span></span> [`code`]
block runs to completion, it is thereafter ignored.

Here is an example of [`code`] that directs users to different
endpoints depending on their roles:

{% highlight yaml %}
initial: true
code: |
  if user_has_privilege('litigant'):
    litigant_request_handled
  elif user_has_privilege('judge'):
    judge_request_handled
  else:
    login_screen
{% endhighlight %}

The following interview excerpt uses information about the logged-in
user in an interview question:

{% highlight yaml %}
initial: true
code: |
  if user_logged_in():
    intro_screen
    final_screen
  else:
    login_screen
---
field: intro_screen
question: |
  Welcome, ${ user_info().first_name }!
subquestion: |
  Press Continue to start the interview.
{% endhighlight %}

This [`code`] screens out a user by e-mail address:

{% highlight yaml %}
initial: true
code: |
  if not user_logged_in():
    login_screen
  if user_info().email.endswith('.gov'):
    kick_out_the_government
---
event: kick_out_the_government
question: |
  Go away, government spy!
{% endhighlight %}

# <a name="users and actions"></a>Interaction of user roles and actions

If you use [actions] in your interview, **docassemble** will run those
actions before it processes the [`initial`] and [`mandatory`]
questions in your interview.  However, if you have a screening process
in your interview, such as those illustrated in the previous section,
you might not want these [actions] to be able to bypass that
screening.

This could be a problem if, for example, you use
[`interview_url_action()`] to provide URLs to users in order to access
an interview.  Anyone in possession of such a URL could access the
interview with it, bypassing any screening process you established.

To ensure that [actions] are only run _after_ the screening process,
you can use the [`process_action()`] function.

Consider the last example from the previous section.  To ensure that
actions are only processed after the screening process is complete,
you would change the first [`code`] block to:

{% highlight yaml %}
initial: true
code: |
  if not user_logged_in():
    login_screen
  if user_info().email.endswith('.gov'):
    kick_out_the_government
  process_action()
{% endhighlight %}

This explicitly indicates to **docassemble** the point in the
interview processing when you want the [actions] to be processed.  If
your screening process prevents [`process_action()`] from running, the
[action] will be ignored.

Note that [`process_action()`] is a function within the
[`docassemble.base.util`] module, so you will need to include a
[`modules` block] in order to call it.

If you do not include a call to [`process_action()`] within a [`code`]
block in your interview, **docassemble** will automatically import the
[`docassemble.base.util`] module and run [`process_action()`]
immediately.  (The [`process_action()`] function will run after
[`imports`] and [`modules`], but before [`initial`] and
[`mandatory`]<span></span>[`code`] blocks.)

[`modules` block]: {{ site.baseurl }}/docs/initial.html#modules
[`interview_url_action()`]: {{ site.baseurl }}/docs/functions.html#interview_url_action
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[actions]: {{ site.baseurl }}/docs/background.html#background
[`code`]: {{ site.baseurl }}/docs/code.html
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[country code]: http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[special variables]: {{ site.baseurl }}/docs/special.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[`oauth`]: {{ site.baseurl }}/docs/config.html#oauth
[`show login`]: {{ site.baseurl }}/docs/config.html#show login
[`docassemble.webapp`]: {{ site.baseurl }}/docs/installation.html#docassemble.webapp
[`create_tables.py`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[User List]: #user_list
[Profile]: #profile
[Privileges List]: #profile
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[`user_info()`]: {{ site.baseurl }}/docs/functions.html#user_info
[`allow registration`]: {{ site.baseurl }}/docs/config.html#allow registration
[`appname`]: {{ site.baseurl }}/docs/config.html#appname
[`user_info()`]: {{ site.baseurl }}/docs/functions.html#user_info
[`user_logged_in()`]: {{ site.baseurl }}/docs/functions.html#user_logged_in
[`user_has_privilege()`]: {{ site.baseurl }}/docs/functions.html#user_logged_in
[functions]: {{ site.baseurl }}/docs/functions.html
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[SMS]: https://en.wikipedia.org/wiki/Short_Message_Service
[`phone login`]: {{ site.baseurl }}/docs/config.html#phone login
[`twilio`]: {{ site.baseurl }}/docs/config.html#twilio
[two-factor authentication]: {{ site.baseurl }}/docs/config.html#mfa
[`show login`]: {{ site.baseurl }}/docs/config.html#show login
[`imports`]: {{ site.baseurl }}/docs/initial.html#imports
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[action]: {{ site.baseurl }}/docs/functions.html#actions
