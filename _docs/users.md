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
are six privileges defined by default in **docassemble**:

* user
* admin
* cron
* customer
* developer
* advocate

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

Users can log in with Facebook or Google.  This requires obtaining API
keys with those companies.  See the documentation for the [`oauth`]
configuration directive for details.

If you do not want your users to be able to log in, you can hide the
Login button by setting the [`show_login`] setting in the
[configuration].

When a user is logged in, the user's information is made available to
**docassemble** interviews through the [`user_info()`] function

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

## <a name="invite">Invite User</a>

Administrators can invite people to register by clicking "Invite a
user" on the [User List] page.  **docassemble** will send an e-mail
with a link that the person can click on to register.  If
[`allow_registration`] is set to `False`, this is the only way that
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

[country code]: http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[special variables]: {{ site.baseurl }}/docs/special.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
[roles]: {{ site.baseurl }}/docs/roles.html
[Python dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[`oauth`]: {{ site.baseurl }}/docs/config.html#oauth
[`show_login`]: {{ site.baseurl }}/docs/config.html#show_login
[`docassemble.webapp`]: {{ site.baseurl }}/docs/installation.html#docassemble.webapp
[`create_tables.py`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[User List]: #user_list
[Profile]: #profile
[Privileges List]: #profile
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[`user_info()`]: {{ site.baseurl }}/docs/functions.html#user_info
[`allow_registration`]: {{ site.baseurl }}/docs/config.html#allow_registration
[`appname`]: {{ site.baseurl }}/docs/config.html#appname
