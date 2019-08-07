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
`docassemble.webapp` and `docassemble.base`.  (There is also a
"namespace" package called `docassemble`, which is necessary but
contains no substantive code.)  [Python packages] are the mechanism by
which **docassemble** interviews are published and shared.  Also, if
any of your interviews needs to perform a non-standard function, you
can install a third-party [Python] package that provides that
functionality.  For example, suppose you wanted your interview to
integrate with your organization's [Slack] server.  You could install
the [Python] package called [`slackclient`], and then use an
[`imports`] block to incorporate the functionality of [`slackclient`]
into your interview.

The "Package Management" screen is where users with `admin` or
`developer` privileges can manage [Python] packages.  The screen
effectively serves as a front end to [Python]'s [pip] utility.

### <a name="upgrade"></a>Upgrade docassemble

Under the "Upgrade docassemble" part, you can see what version of
**docassemble** you are running.  If a new version of **docassemble**
is available, it will also show you current version.  You can press
the "Upgrade" button to upgrade to the latest version of
**docassemble** from [PyPI].

This updates only **docassemble**'s [Python] packages.  It does not
upgrade any of the system files that **docassemble** uses.  A few
times a year, you may see a notification on the screen saying:

> A new docassemble system version is available.  If you are using
> Docker, install a new Docker image.

This means that non-Python files in the **docassemble** system have
been upgraded.  If you are using [Docker] with [persistent storage],
then you should then [upgrade your container].

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
click "Update" on the wrong package.

However, if the only packages you "Update" or "Uninstall" are
**docassemble** extension packages, or dependency packages that you
installed originally, then there is little risk that you will cause a
problem with your system.

## <a name="logs"></a>Logs

The "Logs" screen provides a web interface to some of the log files on
the underlying system.  In a [multi-server arrangement], log messages
are consolidated from all servers, and "Logs" provides a way to see
all of them together.

The log messages shown in the box on the screen are just the tail end
of the actual log file.  To see the complete log file, you will need
to download it.

Note that the log files are managed by [logrotate].  Generally, the
current log file for the `docassemble.log` file is simply
`docassemble.log`, and the next most recent is `docassemble.log.1`,
and then `docassemble.log.2`, etc.  As a result, the log messages you
want to view may not be in `docassemble.log`, but could be in
`docassemble.log.1`.  Also, given the way log rotation interacts with
open file handles, note that the very most recent log messages may be
in `docassemble.log.1` rather than `docassemble.log`.

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

Documentation for the [Playground] can be found in the [Playground
section].

## <a name="utilities"></a>Utilities

The "Utilities" screen provides two miscellaneous services that do not
fit in anywhere else.  They are available to users with `admin` or
`developer` privileges.

### <a name="pdf fields"></a>Get list of fields from PDF/DOCX template

If you are assembling a [document] using the [`pdf attachment file`]
or the [`docx attachment file`] options, you can use this utility to
generate a first draft of a [`question`] that fills in all of the
fields referenced in the PDF or Word file.

If you have a Word file that you are referencing with [`docx
attachment file`], you probably do not need to use this utility,
because your template can be populated directly using variables in
your interview.  Populating the template with a [list of fields] is
optional.

This utility is primarily useful when you are using the [`pdf
attachment file`] option.  This option requires you to provide a
dictionary of [`fields`] (or [`field code`], or [`field variables`])
in which the keys are the names of fields in the underlying PDF file.
This utility provides a handy way of obtaining the list of fields.

If your PDF field names use non-[ASCII] characters such as characters
with accent marks, the various software packages that **docassemble**
uses to fill PDF forms may not be able to fill those fields properly.
If you find that some fields are being filled and others are not,
check to see if the fields that are not being filled have accented
characters.  In the PDF template, try replacing the accented
characters with non-accented characters, and see if you get a better
result.

### <a name="translate"></a>Translate system phrases into another language

The second utility on the "Utilities" screen is helpful if your site
does not use English, or you are developing [multi-lingual
interviews].

There are many words and phrases that appear to the user on various
screens and in various circumstances.  By default, **docassemble**
only provides these words and phrases in English.  However,
**docassemble** allows you to provide a [YAML] dictionary that maps
each English word or phrase to a word or phrase in another language.
For more information about how this feature works, see the [`words`]
directive.

This utility will produce a draft [YAML] file that you can then edit,
store within a [package], and reference from the [`words`] directive
of your [Configuration].

To use this utility, provide a language in the form of a lowercase
[ISO-639-1] code (e.g., `fr` for French) and press "Translate."  You
will be provided with a text box containing a [YAML] data structure
that you can copy and paste into a text file.

If you have configured a Google `api key` inside your [`google`]
directive in the [Configuration], and you have enabled the [Google
Cloud Translation API] inside your [Google Developers Console], then
**docassemble** will run each word or phrase through the [Google
Cloud Translation API].

If you have already configured a [`words`] directive, this utility
will pass through all of the words defined in existing [`words`]
files, and will only try to translate phrases that do not already
exist in existing [`words`] files.

### <a name="translation file"></a>Download an interview phrase translation file

The third utility on the "Utilities" screen is helpful if you are
developing [multi-lingual interviews].  It allows you to download an
Excel spreadsheet for side-by-side translation of the phrases used in
a given interview.  Once translated, the spreadsheet can be included
in a [package] and mentioned in a [`translations`] block.  Then
**docassemble** will use the translations in the file when it needs a
translation of a given phrase.

To download a translation file from the "Utilities" screen, you need
to provide the name of an interview (e.g.,
`docassemble.demo:data/questions/questions.yml`) and the target
language in [ISO-639-1] or [ISO-639-3] format (e.g., `fr` for French).

The resulting spreadsheet will contain a row for each unique phrase
used in the interview file, including interview files incorporated by
reference.

The columns of the spreadsheet are:

* interview: the name of the YAML file containing the question that
  contained the phrase.
* question_id: the [`id`] of the question the phrase, or the generic
  name of the question (which could change if the interview changes).
* index_num: an number that indexes the phrase within a given
  question.
* hash: an [MD5 hash] of the phrase (which can be used to test whether
  the text in the "orig_text" column was edited, which it should not be) 
* orig_lang: the original language of the phrase, as indicated by the
  [`language`] specifier of the [`question`].
* tr_lang: the language into which the phrase should be translated.
* orig_text: the text of the phrase
* tr_text: the translated phrase (which is blank if the phrase has not
  yet been translated.

You can then give the spreadsheet to a translator who will fill in the
"tr_text" column with a translation of the text in the "orig_text"
column.

The spreadsheet with the completed translations can then be uploaded
to the [sources] folder of a package and included in the interview
using a [`translations`] block.  If the target language of the
spreadsheet is French (`fr`), then the French translations of phrases
will be used if the current language in the interview (as determined
by the [`set_language()`] function is French.

If the interview contains a [`translations`] block, the file or files
referenced in the [`translations`] block will be scanned and the
translations specified in those files will be included as default
translations.

If the files referenced in the [`translations`] block contain phrases
that are not present in the interview, perhaps because they used to be
present but are no longer present, these extra phrases will be listed
at the end of the interview and their "index_num" values will be
numbered starting with 1000.

### <a name="word addin manifest"></a>Word add-in manifest XML file

The fourth utility is "Download Office add-in manifest file."  You will
need this if you want to enable a [Playground]-like task pane inside
Microsoft Word.

In Microsoft Office, third party add-ins are enabled through XML
"manifest" files.  Through this utility, you can download a manifest
file that is customized for your server.  You need to download this
XML file and then install it in your Microsoft Office setup.

For more instructions on how to do this, see the [Word add-in section].

## <a name="user list"></a>User List

The "User List" is available to users with `admin` privileges.  It
lists all of the user accounts on the system and allows you to edit a
user's information.

When you click the "Edit" button for a user account, you can edit that
user's profile.  Under the "Menu," you can "Add a user," "Invite
a user," or "Edit privileges."

### <a name="edit user profile"></a>Edit a user profile

When you are editing a user profile, you can disable the user's
account by unchecking the "Active" checkbox.

You can edit a user's [privileges].  Note that the selector is a
multi-select; you can assign more than one privilege to a user.
Privileges are additive; a user who has `developer` and `advocate`
privileges can do anything a developer can do and everything an
advocate can do.

The profile fields that you can edit include:

* E-mail: this must be unique; no two users can have the same e-mail address.
* First name
* Last name 
* Country code: an uppercase [ISO 3166] country code
* State
* County
* Municipality
* Organization
* Language: a lowercase [ISO-639-1] or [ISO-639-3] language code
  representing the user's language.

The words "State," "County," and "Municipality" are actually
translated phrases defined in
`docassemble.base:data/sources/us-words.yml`, which is included as a
[`words`] file in the default [Configuration]:

{% highlight yaml %}
en:
  First subdivision: State
  Second subdivision: County
  Third subdivision: Municipality
{% endhighlight %}

You can use the [`user_info()`] and [`set_user_info()`] function to
retrieve and set the user profile attributes, where the state, county,
and municipality are known by these attributes:

* `subdivision_first`
* `subdivision_second`
* `subdivision_third`

Under "Other settings," you have the option to "Delete account but
keep shared sessions."  This will delete the user's account and all of
their data.  However, if any of the user's sessions are [multi-user
interview] that had been joined by another user, those sessions will
not be deleted.

You also have the option under "Other settings" to "Delete account and
shared sessions."  This will delete the user's account and all of
their data, including any [multi-user interview] the user had joined.

These account deletion options can be turned off using the [`admin can
delete account`] directive in the [Configuration].

### <a name="add user"></a>Add a user

On the "Add a user" page, you can create a new user account by
entering an e-mail address and password.  Optionally, you can set the
user's first and last names.  You can also select the user's
[privileges] with a multiselect selector.

Note that when a user is added using this tool, the user is _not_
notified that an account has been created.

### <a name="invite user"></a>Invite a user

On the "Invite a user" page, you can send an e-mail invitation to a
prospective new user.  The privileges of the prospective user can be
set in advance.  The e-mail will contain a link with an embedded
code.  Visiting the link will start the process of registration; until
that process is completed, no user account will actually exist.

### <a name="edit privileges"></a>Edit privileges

The "Edit privileges" page allows you to manage the [privileges] that
exist on the system.  The built-in [privileges] (`user`, `admin`,
`developer`, `advocate`, `cron`, and `trainer`) cannot be removed.
There is one built-in privilege, `customer`, which has no special
meaning within `docassemble` itself, so you are able to delete it.

You can create custom privileges using "Edit privileges," assign them
to users, and then use the [`user_has_privilege()`] and
[`user_privileges()`] in your interviews to do different things
depending on what privileges the user has.

User privilege assignment can be controlled by:

1. Manually [editing a user's profile] from the [User List] page.
2. Calling the [`set_user_info()`] function with the `privileges`
   keyword parameter (calling this function requires `admin`
   [privileges]); or
3. Calling the [`/api/user/<user_id>/privileges`] API.

For example, you may wish to use the [privileges] system to keep track
of which user accounts are paying customers, or to keep track of
different tiers of paying customers.

## <a name="configuration"></a>Configuration

The "Configuration" page allows a user with `admin` privileges to edit
the server [Configuration].  It provides a [YAML] text editor in the
browser.  When the [Configuration] is saved, the services on the
server that depend on the [Configuration] are restarted.

The configuration file for a given server is found at
`/usr/share/docassemble/config/config.yml`.  If you are using
cloud-based [data storage], the `config.yml` file is also stored in
the cloud whenever the [Configuration] is saved.  If you are using
[persistent volumes], the configuration is copied to the persistent
volume when the server shuts down.  Then, when the server starts, the
`config.yml` file is restored from storage.

# <a name="menu"></a>Menu items for all logged-in users

The following menu items are available to all logged-in users
regardless of privileges.

## <a name="available interviews"></a>Available Interviews

The "Available Interviews" page, which is at the URL `/list`, shows a
list of interviews that users can run.  The list can be configured
using the [`dispatch`] directive in the [Configuration].  If there is
no `dispatch` directive, this page will redirect to the system's
default interview, which can be configured using the [`default
interview`] directive in the [Configuration].

By default, the "Available Interviews" menu item is not shown.  It can
be enabled by setting [`show dispatch link`] to `True` in the
[Configuration].

If an interview is listed under [`dispatch`], but the [`metadata`] of
the interview contains the specifier [`unlisted`] set to `True`, then
the interview will not be listed in the `/list`, although it will
still be usable with a `/start` shortcut.

The URL parameter `tag` can be used to filter the list of available
interviews.  For example, if you set `tag=estates`, then the only
interviews that will be listed are those that have `estates` as one of
the [`tags`] in the interview [`metadata`].

You can use the [`required privileges`] specifier in the [`metadata`]
of each interview listed under [`dispatch`] to control whether the
interview should appear in the list, depending on the [privileges] of
the user.

For information about how to customize the "Available Interviews"
page, see the [Configuration] directives that begin with [`start
page`], or configure the [`start page template`], or replace the page
with an interview using [`dispatch interview`].

## <a name="my interviews"></a>My Interviews

The "My Interviews" page, which is at the URL `/interviews`, shows a
list of the user's existing interview sessions.

For more information about how sessions work in **docassemble**, see
the subsections on [how you run a **docassemble** interview] and
[leaving an interview and coming back].

The "My Interviews" menu item can be hidden from the menu using the
[`show interviews link`] directive in the [Configuration].

For information about how to customize the "My Interviews" page, see
the [Configuration] directives that begin with [`interview page`], or
configure the [`interview page template`], or replace the page with an
interview using [`session list interview`].

## <a name="profile"></a>Profile

The "Profile" page allows the user to edit their user account
profile.  The following fields can be changed:

* First name
* Last name

If the user registered using the [phone login] method, the user can
also edit his or her e-mail address.  However, users who registered
with other methods cannot edit their e-mail address.

In addition, users with privileges of `admin` or `developer` can edit
the following fields:

* Country code: an uppercase [ISO 3166] country code
* State
* County
* Municipality
* Organization
* Language: a lowercase [ISO-639-1] or [ISO-639-3] language code
  representing the user's language.
* PyPI Username
* PyPI Password

From the "Other settings" menu, the user can:

* Change their password
* Configure [Google Drive synchronization]
* Configure [OneDrive synchronization]
* Configure [multi-factor authentication]
* Configure [GitHub integration]
* [Manage API keys]
* Manage their account

Whether these commands are available depends on the [Configuration].
The "Manage account" setting allows the user to delete their account.
To disable this, edit the [`user can delete account`] directive in the
[Configuration].

## <a name="sign out"></a>Sign Out

The "Sign Out" menu item logs the user out and expires the user's
session cookies.  If the user was in the process of using an
interview, the interview session will not be deleted.

<!--# <a name="architecture"></a>System architecture

Technical information about how to get the components of
**docassemble** up and running can be found in the [Installation] and
[Docker] sections.  This subsection provides a brief technical
overview of how **docassemble** operates in order to help
administrators appreciate, at a high level, what is going on under the
hood-->

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
[Playground section]: {{ site.baseurl }}/docs/playground.html#packages
[`slackclient`]: https://pypi.org/project/slackclient/
[`imports`]: {{ site.baseurl }}/docs/initial.html#imports
[multi-server arrangement]: {{ site.baseurl }}/docs/docker.html#multi server arrangement
[background tasks]: {{ site.baseurl }}/docs/background.html#background
[package]: {{ site.baseurl }}/docs/packages.html
[document]: {{ site.baseurl }}/docs/documents.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`pdf attachment file`]: {{ site.baseurl }}/docs/documents.html#pdf attachment file
[`docx attachment file`]: {{ site.baseurl }}/docs/documents.html#docx attachment file
[list of fields]: {{ site.baseurl }}/docs/documents.html#particfields
[`fields`]: {{ site.baseurl }}/docs/documents.html#pdf attachment file
[`field variables`]: {{ site.baseurl }}/docs/documents.html#template code
[`field code`]: {{ site.baseurl }}/docs/documents.html#template code
[multi-lingual interviews]: {{ site.baseurl }}/docs/language.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[`words`]: {{ site.baseurl }}/docs/config.html#words
[Configuration]: {{ site.baseurl }}/docs/config.html
[`google`]: {{ site.baseurl }}/docs/config.html#google
[Google Cloud Translation API]: https://cloud.google.com/translate/
[Google Developers Console]: https://console.developers.google.com/
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[ISO-639-3]: https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
[ISO 3166]: http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
[`user_info()`]: {{ site.baseurl }}/docs/functions.html#user_info
[`set_user_info()`]: {{ site.baseurl }}/docs/functions.html#set_user_info
[`user_has_privilege()`]: {{ site.baseurl }}/docs/functions.html#user_has_privilege
[`user_privileges()`]: {{ site.baseurl }}/docs/functions.html#user_privileges
[User List]: #user list
[editing a user's profile]: #edit user profile
[`/api/user/<user_id>/privileges`]: {{ site.baseurl }}/docs/api.html#user_privilege_add
[data storage]: {{ site.baseurl }}/docs/docker.html#data storage
[persistent volumes]: {{ site.baseurl }}/docs/docker.html#persistent
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[`start page`]: {{ site.baseurl }}/docs/config.html#customization
[`interview page`]: {{ site.baseurl }}/docs/config.html#customization
[`start page template`]: {{ site.baseurl }}/docs/config.html#start page template
[`interview page template`]: {{ site.baseurl }}/docs/config.html#interview page template
[`show dispatch link`]: {{ site.baseurl }}/docs/config.html#show dispatch link
[`show interviews link`]: {{ site.baseurl }}/docs/config.html#show interviews link
[`show profile link`]: {{ site.baseurl }}/docs/config.html#show profile link
[`session list interview`]: {{ site.baseurl }}/docs/config.html#session list interview
[`dispatch interview`]: {{ site.baseurl }}/docs/config.html#dispatch interview
[`default interview`]: {{ site.baseurl }}/docs/config.html#default interview
[leaving an interview and coming back]: {{ site.baseurl }}/docs/interviews.html#comingback
[how you run a **docassemble** interview]: {{ site.baseurl }}/docs/interviews.html#invocation
[phone login]: {{ site.baseurl }}/docs/config.html#phone login
[Slack]: https://slack.com
[logrotate]: https://manpages.debian.org/stretch/logrotate/logrotate.8.en.html
[Word add-in section]: {{ site.baseurl }}/docs/playground.html#word addin
[ASCII]: https://en.wikipedia.org/wiki/ASCII
[`translations`]: {{ site.baseurl }}/docs/initial.html#translations
[`id`]: {{ site.baseurl }}/docs/modifiers.html#id
[MD5 hash]: https://en.wikipedia.org/wiki/MD5#MD5_hashes
[`language`]: {{ site.baseurl }}/docs/modifiers.html#language
[sources]: {{ site.baseurl }}/docs/playground.html#sources
[`set_language()`]: {{ site.baseurl }}/docs/functions.html#set_language
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[`tags`]: {{ site.baseurl }}/docs/initial.html#tags
[`required privileges`]: {{ site.baseurl }}/docs/initial.html#required privileges
[`unlisted`]: {{ site.baseurl }}/docs/initial.html#unlisted
[multi-user interview]: {{ site.baseurl }}/docs/special.html#multi_user
[`user can delete account`]: {{ site.baseurl }}/docs/config.html#user can delete account
[Manage API keys]: {{ site.baseurl }}/docs/api.html#manage_api
[GitHub integration]: {{ site.baseurl }}/docs/installation.html#github
[multi-factor authentication]: {{ site.baseurl }}/docs/config.html#mfa
[OneDrive synchronization]: {{ site.baseurl }}/docs/installation.html#onedrive
[Google Drive synchronization]: {{ site.baseurl }}/docs/installation.html#google drive
[`admin can delete account`]: {{ site.baseurl }}/docs/config.html#admin can delete account
