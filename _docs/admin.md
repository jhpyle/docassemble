---
layout: docs
title: Overview of docassemble administration
short_title: Overview
---

When you log in to a **docassemble** server, the options available to
you in the menu in the upper-right corner will depend on what 
[privileges] have been enabled for your account.

There are four special privileges built in to **docassemble**.

- `admin`: for people who need complete control over the server.
- `developer`: for people who need to use the server to develop, test,
  and debug interviews, but do not need to be able to access user data.
- `advocate`: for people who need to be able to use the [Monitor] to
  provide remote assistance to users, or use interviews or APIs that
  provide access to user data.
- `trainer`: for people who need to be able to [train machine learning
  models].

By default, when a new user account is created, the user is given only
the privilege of `user`.  This is the "lowest" level of privilege; a
user without the `user` privilege can do everything a user with `user`
privileges can do.

A user with privileges of `admin` can control the privileges of other
users using the [User List] screen.

# <a name="specialmenu"></a>Menu items for users with special privileges

## <a name="monitor"></a>Monitor

The [Monitor] is a feature of **docassemble**'s [Live Help system]
that allows the user to chat with or share a screen with an active
user.  Users with privileges of `admin` or `advocate` can access the
[Monitor].

## <a name="train"></a>Train

The "Train" menu item allows the user to [train machine learning
models].  This is part of **docassemble**'s [machine learning system].
Users with privileges of `admin` or `trainer` can access it.

## <a name="package management"></a>Package Management

The "Package Management" menu item allows the user to install, update,
or uninstall [Python packages] that exist on the server.

### <a name="upgrade"></a>Upgrade docassemble

### <a name="install"></a>Install or update a package

### <a name="update"></a>Update or uninstall an existing package

## <a name="logs"></a>Logs

## <a name="playground"></a>Playground

## <a name="utilities"></a>Utilities

### <a name="pdf fields"></a>Get list of fields from PDF/DOCX template

### <a name="translate"></a>Translate system phrases into another language

## <a name="user list"></a>User List

## <a name="configuration"></a>Configuration

# <a name="menu"></a>Menu items for all logged-in users

## <a name="available interviews"></a>Available Interviews

## <a name="my interviews"></a>My Interviews

## <a name="profile"></a>Profile

## <a name="sign out"></a>Sign Out

# <a name="architecture"></a>System architecture

Technical information about how to get the components of
**docassemble** up and running can be found in the [Installation] and
[Docker] sections.  This subsection provides a brief technical overview of
how **docassemble** operates in order to help administrators
appreciate, at a high level, what is going on under the hood

# <a name="troubleshooting"></a>Troubleshooting

See 

[machine learning system]: {{ site.baseurl }}/docs/ml.html
[troubleshooting]: {{ site.baseurl }}/docs/docker.html#troubleshooting
[train machine learning models]: {{ site.baseurl }}/docs/ml.html#train
[Monitor]: {{ site.baseurl }}/docs/livehelp.html#monitor
[privileges]: {{ site.baseurl }}/docs/users.html
[Live Help system]: {{ site.baseurl }}/docs/livehelp.html
[User List]: #user list
