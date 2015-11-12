---
layout: docs
title: User Login System
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
"privilege" is that of "user," which has the lowest privileges.  There are
four privileges defined by default in **docassemble**:

* user
* admin
* developer
* advocate

A user who has the "admin" privilege can upgrade the privleges of any
user by going to the User List on the menu.

When **docassemble** is first installed, it creates a user with
"admin" privileges with the following login information:

* Email: admin@admin.com
* Password: password

As soon as **docassemble** is set up, you should log in as this user,
go to User List, edit the admin@admin.com user, and change its e-mail
address and password.

You can also change these defaults during [installation] by editing the
[configuration] before running the `create_tables.py` script from the
`docassemble.webapp` package.

Users can log in with Facebook or Google.  This requires obtaining API
keys with those companies.  See [configuration] for details.

If you do not want your users to be able to log in, you can hide the
Login button by setting the `show_login` setting in the
[configuration].

[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
