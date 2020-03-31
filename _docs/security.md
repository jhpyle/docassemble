---
layout: docs
title: Security
short_title: Security
---

**docassemble** is designed with user privacy in mind.

# Security features

## <a name="server_encryption"></a>Server-side information storage

User passwords are encrypted.  [Flask-Login] is the basis for the
username/password system.

Interview answers are stored in a SQL database in encrypted form,
unless the [`multi_user`] variable is set to `True`, in which case the
answers are not encrypted.

If users log in with [external authentication methods] or the
[phone login] feature, interview answers are still encrypted (unless
the [`multi_user`] variable is set to `True`), but a resourceful
hacker could figure out the encryption key.  Therefore, if server-side
encryption is important to you, it is recommended that you do not
enable [external authentication methods] or the [phone login] feature.

Uploaded and assembled documents are stored on the server (and on
[Amazon S3], if [S3] is being used, or [Microsoft Azure], if [Azure
blob storage] is being used) without encryption.  These documents
cannot be accessed from the internet without an appropriate access key
in the cookie.  In some situations, the user is provided with a
temporary URL to an [S3] resource that allows anyone who has the URL
to access the document.  In other situations, the **docassemble**
server retrieves the file from [S3] and serves it.

When a user clicks an "Exit" button (or the `/exit` path is visited,
or the `/exit_logout` path is visited, or `command('exit')` is run, or
`command('exit_logout') is run), **docassemble** will delete all of
the information related to the interview from the server, including
the database, uploaded documents, and assembled documents.  See
[deleting user information] for more information.

## <a name="signin"></a>Sign-in security

**docassemble** blocks brute-force password-guessing attacks.

**docassemble** also supports [two-factor authentication].

By default, users do not need to verify their e-mail addresses, but
you can require them to do so.  See the documentation for the
[`email confirmation privileges`] configuration directive.

# <a name="https"></a>Importance of using HTTPS

It is important for security purposes to deploy **docassemble** using
HTTPS rather than HTTP.  If you use HTTP, passwords and security keys
will be sent over the network in plain text.

# <a name="separateservers"></a>Separate development and production servers

Users with "developer" access can run arbitrary code on the server.
For this reason, it is recommended that you not allow developer
accounts on production servers, and that you only install
**docassemble** add-on packages that you have carefully reviewed.

On a production server, you should make sure the [Configuration]
contains the following:

{% highlight yaml %}
debug: False
allow demo: False
enable playground: False
{% endhighlight %}

The [`debug`] directive will turn off the "Source" tab, so that users
cannot see any source code of the interviews.  This will also improve
site performance.

The [`allow demo`] directive will prevent users from accessing any of
the sample interviews in the `docassemble.base` and `docassemble.demo`
packages.  These are helpful on a development server because
developers can access them from the Examples page of the
[Playground].  However, on a production server there is no reason why
users should be able to run such interviews.

The [`enable playground`] directive will make the [Playground]
inoperable.  Any attempt by a user to use a [Playground] interview
will fail.  Users with developer and administrator accounts will not
see the [Playground]-related options in the menus.

# <a name="sessionkeys"></a>Avoiding sharing session keys

Each session of a **docassemble** interview is uniquely identified by
a session key, which is a series of randomly-generated characters.  If
server-side encryption is turned off (by setting [`multi_user`] to
`True`), then anyone who possesses the encryption key can access the
interview session.  Thus there is a risk to e-mailing a user a link to
an interview generated by [`interview_url()`], since the URL will
contain the session key.  This URL is like the URL to a Google Docs
file where "anyone with the link can edit."  You can mitigate this
risk somewhat by using the `temporary` keyword argument or the
`once_temporary` keyword argument to [`interview_url()`].  Then, the
link that you share will not contain the actual interview session key,
and the link will expire after a period of time.

# <a name="multiuser"></a>Security in multi-user interviews

If you have a [multi-user interview], you will set [`multi_user`] to
`True` in order to turn off server-side encryption.  Then anyone with
the session key can access a session.

In the ordinary course of a [multi-user interview], each user will
only see the screens your interview expects them to see.  For example,
you could design a divorce mediation interview in which two parties to
a divorce each share confidential information into the same session,
and one spouse will not be able to see information entered by the
other spouse.

However, **docassemble**'s [front end interface] is designed to be
open and flexible, so that developers have the freedom to innovate.
By default, the [JavaScript] function [`get_interview_variables()`] is
available, which will retrieve all of the interview answers in [JSON]
format from the server.

If one of the users who has access to the session key is not fully
trusted, you may worry that they will teach themselves how
**docassemble** works and take steps to "snoop around" in the
interview and access information they shouldn't, for example by
running [`get_interview_variables()`] in the [JavaScript] console or
visiting the `/vars?i=...` page (which is called by
[`get_interview_variables()`] to obtain a [JSON] version of the
interview answers for the current session).

You can take steps to "harden" your interview against such
unauthorized snooping.  You can include the following at the beginning
of your interview:

{% highlight yaml %}
mandatory: True
code: |
  set_status(variable_access=False)
{% endhighlight %}

This will disable the [`get_interview_variables()`] feature.

Another way that a user could snoop around is by using
the [JavaScript] function [`url_action()`] to access screens they are
not supposed to see.  For example, if your two users are represented
by two [`Individual`]s in your interview answers called `petitioner`
and `respondent`, the respondent might try to call
[`url_action("petitioner.ssn")`] from the [JavaScript] console.

You can provide security over the [actions] mechanism by calling
[`process_action()`] manually inside of a [`code`] block that has
[`initial`] set to `True`.  By default, **docassemble** will run
[`process_action()`] for you, but if it sees that you have a [`code`]
block that calls [`process_action()`], it will refrain from calling it
automatically.  You can use the [`action_argument()`] function to
obtain the action being requested.

{% highlight yaml %}
initial: True
code: |
  if action_argument() in ():
    process_action()
{% endhighlight %}

# <a name="deleting"></a>Deleting user information

By default, interview sessions are deleted after 90 days of
inactivity.  This period can be modified using the [`interview delete
days`] directive in the [Configuration].

Users who are logged in can delete their interview sessions by going
to [My Interviews] and clicking the "Delete All" button or by deleting
individual interviews.  The interview session can also be deleted
through the use of an `exit` [button], an `exit_logout` [button], a
call to [`command()`] with `'exit'` or `'exit_logout'` as the
parameter, or if the user visits `/exit` or `/exit_logout`.

Users who are logged in can delete their entire account by going to
[Profile], "Other settings," "Manage account."  A URL for the "Manage
account" page can be obtained by calling `url_of('manage')`.  When a
user deletes their account, this has same effect as "Delete All" on
the [My Interviews] page, and it also deletes other information, such
as the user profile data.  By default, account deletion does not
delete multi-user interview sessions that have been entered by another
user.  However, if you want users to have the power to delete
multi-user interview sessions, you can set [`delete account deletes
shared`] in the [Configuration] to `True`.

Users who are not logged in can also delete their data by going to the
`/user/manage` page (the URL for which can be obtained by calling
`url_of('manage')`).

Administrators can delete user accounts on the [User List]
page by editing an individual user.  Administrators have the option
to delete the account but leave shared interviews alone, or delete the
account and all of its shared interviews.

When **docassemble** deletes an interview session, it deletes:

* All steps of the interview answers (from SQL).
* All files associated with the interview session (e.g., uploaded
  files, generated files) except for files with the `persistent`
  attribute set.
* Cached speech-to-text audio files.
* E-mail addresses generated by [`interview_email()`].
* E-mails sent to addresses generated by [`interview_email()`].
* [Live Help] chat logs from the session.

When **docassemble** deletes an interview session, it does **not**
delete:

* Records created during the session using [`DAStore`], [`DARedis`], or
  [`write_record()`].
* Records created in the machine learning system from the session.
* Files with the `persistent` attribute set to true.

When **docassemble** deletes a user account, it deletes:

* All interview sessions started by the user (except for shared
  interview sessions joined by another user, which are not deleted
  unless the administrator chooses to include them in the deletion
  process).
* Records stored by the user with [`DAStore`].
* The name, organization, and other information in the user's
  [Profile].
* The contents of the user's [Playground].
* Other information associated with the user, such as authentication
  tokens for integration with the GitHub API and authentication tokens
  created for the user's e-mail address with [`DAOAuth`].

When **docassemble** deletes a user account, it does not delete:
* Records created by the user using [`DARedis`] or [`write_record()`].
* Records created by the user in the machine learning system.
* Files containing user data that set the `persistent` attribute set
  to true.

If you are using a [multi-server arrangement] with cloud storage, then
when you delete a file, copies of the file in a cache directory on
/tmp on some servers may persist until cleaned out by a cron job.  The
[Docker] hourly cron job deletes files from the cache if they have not
been accessed in the past two hours.

# <a name="issues"></a>Issues to look out for

**docassemble** makes extensive use of [eval] and [exec], including to
process information supplied by the user.  There are protections in
place to prevent code injection, but more work could be done to harden
**docassemble** against such threats.

The options for allowing users to log in with Google, Facebook,
Twitter, Azure, and mobile phone numbers are provided for convenience,
but you may wish not to enable these features because the encryption
of interview answers on the server is less effective when users log in
without a password.  This is because the password is used as the
encryption key, which is advantageous because it is not stored
anywhere on the server; the user remembers it and it is stored in a
cookie in the user's browser.  When users log in with something other
than a password, however, there is no such key available.  As a
result, the key for encrypting user answers on the server is
constructed based on information that is stored on the server.  As a
result, an intruder with access to the server could reverse-engineer
the encrpytion key for an interview belonging to a user who logs in
with something other than a password.

On [Docker], **docassemble** installs [npm] from a [different source]
because [npm] is missing from [Debian stretch] due to unresolved
security issues in a Javascript library.  The installation of [npm]
may have security implications.  However, the only Javascript-based
application that **docassemble** uses is [`azure-storage-cmd`], and
this is only used when [Azure blob storage] is enabled.

[Azure blob storage]: {{ site.baseurl }}/docs/docker.html#persistent azure
[`azure-storage-cmd`]: https://www.npmjs.com/package/azure-storage-cmd
[different source]: http://linuxbsdos.com/2017/06/26/how-to-install-node-js-lts-on-debian-9-stretch/
[Debian stretch]: https://wiki.debian.org/DebianStretch
[npm]: https://www.npmjs.com
[login/password system]: {{ site.baseurl }}/docs/users.html
[fail2ban]: https://en.wikipedia.org/wiki/Fail2ban
[Docker]: {{ site.baseurl }}/docs/docker.html
[eval]: https://docs.python.org/3/library/functions.html#eval
[exec]: https://docs.python.org/3/reference/simple_stmts.html#exec
[Amazon S3]: https://aws.amazon.com/s3/
[S3]: https://aws.amazon.com/s3/
[Microsoft Azure]: https://azure.microsoft.com/
[Azure blob storage]: https://azure.microsoft.com/en-us/services/storage/blobs/
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[two-factor authentication]: {{ site.baseurl }}/docs/config.html#mfa
[external authentication methods]: {{ site.baseurl }}/docs/config.html#oauth
[phone login]: {{ site.baseurl }}/docs/config.html#phone login
[`email confirmation privileges`]: {{ site.baseurl }}/docs/config.html#email confirmation
[multi-user interview]: {{ site.baseurl }}/docs/roles.html
[`get_interview_variables()`]: {{ site.baseurl }}/docs/functions.html#js_get_interview_variables
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[JSON]: https://en.wikipedia.org/wiki/JSON
[`interview_url()`]: {{ site.baseurl }}/docs/functions.html#interview_url
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#js_url_action
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[Configuration]: {{ site.baseurl }}/docs/config.html
[My Interviews]: {{ site.baseurl }}/docs/admin.html#my interviews
[Profile]: {{ site.baseurl }}/docs/admin.html#profile
[`delete account deletes shared`]: {{ site.baseurl }}/docs/config.html#delete account deletes shared
[User List]: {{ site.baseurl }}/docs/admin.html#user list
[`interview_email()`]: {{ site.baseurl }}/docs/functions.html#interview_email
[Live Help]: {{ site.baseurl }}/docs/livehelp.html
[`DAStore`]: {{ site.baseurl }}/docs/objects.html#DAStore
[`write_record()`]: {{ site.baseurl }}/docs/functions.html#write_record
[Playground]: {{ site.baseurl }}/docs/playground.html
[button]: {{ site.baseurl }}/docs/questions.html#special buttons
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`action_argument()`]: {{ site.baseurl }}/docs/functions.html#action_argument
[`command()`]: {{ site.baseurl }}/docs/functions.html#command
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`code`]: {{ site.baseurl }}/docs/code.html#code
[Flask-Login]: https://flask-login.readthedocs.io/en/latest/
[multi-server arrangement]: {{ site.baseurl }}/docs/docker.html#multi server arrangement
[deleting user information]: #deleting
[`debug`]: {{ site.baseurl }}/docs/config.html#debug
[`allow demo`]: {{ site.baseurl }}/docs/config.html#allow demo
[`enable playground`]: {{ site.baseurl }}/docs/config.html#enable playground