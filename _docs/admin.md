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

The "Package Management" screen allows the user to install, update, or
uninstall [Python packages] that exist on the server.  It has three
parts:

* Upgrade docassemble
* Install or update a package
* Update or uninstall an existing package

[Python packages] play an important role in **docassemble**.  The core
functionality of **docassemble** resides in two [Python packages]:
`docassemble.webapp` and `docassemble.base`.  [Python
packages] are the mechanism by which **docassemble** interviews are
published and shared.  Also, if any of your interviews needs to perform
a non-standard function, you can install a third-party [Python] package
that provides that functionality.  For example, suppose you wanted
your interview to integrate with your organization's [Slack] server.
You could install the [Python] package called [`slackclient`], and
then use an [`imports`] block to incorporate the functionality of
[`slackclient`] into your interview.

The "Package Management" screen is where users with `admin` or
`developer` privileges can manage [Python] packages.  The screen
effectively serves as a front end to [Python]'s [pip] utility.

### <a name="upgrade"></a>Upgrade docassemble

Under the "Upgrade docassemble" part, you can press the "Upgrade"
button to upgrade to the latest version of **docassemble** from [PyPI].

This updates only **docassemble**'s [Python] packages.  It does not
upgrade any of the system files that **docassemble** uses.  A few
times a year, you may see a notification on the screen saying:

> A new docassemble system version is available.  If you are using
> Docker, install a new Docker image.

This means that non-Python files in the **docassemble** system have
been upgraded.  If you are using [Docker] with [persistent storage],
then you should [upgrade your container].

### <a name="install"></a>Install or update a package

Under the "Install or update a package" part, you can install a new
[Python] package on the system.

There are three ways you can provide a package to **docassemble**:

* GitHub
* ZIP file
* PyPI

[PyPI] is the standard place on the internet where [Python] packages
are published.  However, some Python packages are hosted directly on
[GitHub], and some are distributed as ZIP files.

When you provide a URL to a [GitHub] repository, you can choose which
branch of that repository you wish to install.

The [Playground] allows you to package one or more **docassemble**
interviews as a [Python] package and publish it on [GitHub], publish
it on [PyPI], or save it as a ZIP file.  Thus, you can use the
[Playground] on a development server to create and publish a package,
and then use "Package Management" on a production server to install
the package.

If you do not want your package to be available for anyone in the
world to read, you can store it in a private repository on [GitHub],
and then use [GitHub] to obtain a special URL for the repository that
embeds an "OAuth" authentication code.  These URLs can be used in
the "Github URL" field of "Package Management."

### <a name="update"></a>Update or uninstall an existing package

In this part of the "Package Management" screen, you can see a list of
all of the [Python] packages that are installed on your system
already.

You can click "Uninstall" to remove a package, and you can click
"Update" to update a package to the latest version.  However, be
careful; some of the listed packages are dependencies for other
packages, and those other packages may depend on a specific older
version of the package.  Thus, you could break your system if you
click "Update" on the wrong package.  However, if the only packages
you "Update" or "Uninstall" are **docassemble** extension packages,
then there is little risk that you will cause a problem with your
system.

## <a name="logs"></a>Logs

The "Logs" screen provides a web interface to some of the log files on
the underlying system.  In a [multi-server arrangement], log messages
are consolidated from all servers, and "Logs" provides a way to see
all of them together.

The log messages shown in the box on the screen are just the tail end
of the actual log file.  To see the complete log file, you will need
to download it.

Note that the log files are managed by [logrotate].  Generally, the
current log file is `docassemble.log`, and the next most recent is
`docassemble.log.1`, and then `docassemble.log.2`, etc.  As a result,
the log messages you want to view may not be in `docassemble.log`, but
could be in `docassemble.log.1`.  Also, given the way log rotation
interacts with open file handles, note that the very most recent log
messages may be in `docassemble.log.1` rather than `docassemble.log`.

Here is a summary of what the different log files represent.

* `access.log` contains entries for every request made to the web
  server.
* `docassemble.log` contains log messages and most errors generated by
  the web application.
* `error.log` contains error messages generated by the web server.
  Most error messages in **docassemble** are trapped before they can
  be raised by the web server, so `docassemble.log` should generally
  be the first place you look for an error.  If you get an "500 Internal
  Server Error" in the browser, however, the error message is likely
  in `error.log`.
* `worker.log` contains log messages and error messages generated by
  [background tasks].

In unusual situations, you may need to review other log files.  For
more information about how to find other log files, see the
[troubleshooting] section.

## <a name="playground"></a>Playground

The [Playground] is an area where users who have privileges of `admin`
or `developer` can develop and test interviews using the web browser.
Interviews can also be developed "off-line" by assembling a [package]
containing [YAML] files and other files in the appropriate locations.

Documentation for the [Playground] can be found in the [Playground]
section.

## <a name="utilities"></a>Utilities

The "Utilities" screen contains two miscellaneous services that do not
fit in anywhere else.

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

For tips on troubleshooting your **docassemble** system, see the
[troubleshooting] subsection in the [Docker] section.

[machine learning system]: {{ site.baseurl }}/docs/ml.html
[troubleshooting]: {{ site.baseurl }}/docs/docker.html#troubleshooting
[train machine learning models]: {{ site.baseurl }}/docs/ml.html#train
[Monitor]: {{ site.baseurl }}/docs/livehelp.html#monitor
[privileges]: {{ site.baseurl }}/docs/users.html
[Live Help system]: {{ site.baseurl }}/docs/livehelp.html
[User List]: #user list
[Docker]: {{ site.baseurl }}/docs/docker.html
[upgrade your container]: {{ site.baseurl }}/docs/docker.html#upgrading
[persistent storage]: {{ site.baseurl }}/docs/docker.html#data storage
[Python packages]: https://www.learnpython.org/en/Modules_and_Packages
[PyPI]: https://pypi.python.org/pypi
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[pip]: https://en.wikipedia.org/wiki/Pip_%28package_manager%29
[GitHub]: https://github.com/
[Playground]: {{ site.baseurl }}/docs/playground.html#packages
[`slackclient`]: https://pypi.org/project/slackclient/
[`imports`]: {{ site.baseurl }}/docs/initial.html#imports
[multi-server arrangement]: {{ site.baseurl }}/docs/docker.html#multi server arrangement
[background tasks]: {{ site.baseurl }}/docs/background.html#background
[package]: {{ site.baseurl }}/docs/packages.html
