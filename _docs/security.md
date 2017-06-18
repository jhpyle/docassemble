---
layout: docs
title: Security
short_title: Security
---

**docassemble** is designed with user privacy in mind.

# Importance of using HTTPS

It is important for security purposes to deploy **docassemble** using
HTTPS rather than HTTP.  If you use HTTP, passwords and security keys
will be sent over the network in plain text.

# <a name="server_encryption"></a>Server-side information storage

User passwords and interview answers are stored in a SQL database in
encrypted form, unless the [`multi_user`] variable is set to `True`,
in which case the answers are not encrypted.

If users log in with [external authentication methods] or the
[phone login] feature, interview answers are still encrypted (unless
the [`multi_user`] variable is set to `True`), but a resourceful
hacker could figure out the encryption key.  Therefore, if server-side
encryption is important to you, it is recommended that you do not
enable [external authentication methods] or the [phone login] feature.

Uploaded and assembled documents are stored on the server (and on
[Amazon S3], if [S3] is being used, or [Microsoft Azure], if
[Azure blob storage] is being used) without encryption.  These
documents cannot be accessed from the internet without an appropriate
access key in the cookie.

When a user clicks an "Exit" button, **docassemble** will delete all of
the information related to the interview from the server, including
the database, uploaded documents, and assembled documents.  However,
temporary files in /tmp will persist until cleaned out by [tmpreaper].

# Separate development and production servers

Users with "developer" access can run arbitrary code on the server.
For this reason, it is recommended that you not allow developer
accounts on production servers, and that you only install
**docassemble** add-on packages that you have carefully reviewed.

# <a name="mfa"></a>Two-factor authentication

**docassemble** blocks brute-force password-guessing attacks.  It also
supports [two-factor authentication].

# Additional protections

It is recommended that you run [fail2ban] on servers that host
**docassemble**.

# Issues to look out for

The standard [Docker] deployment of **docassemble** uses [tmpreaper]
to clean out temporary files.  There have been warnings about security
issues related to [tmpreaper], which are discussed in
/usr/share/doc/tmpreaper/README.security.gz in the Debian package.

**docassemble** makes extensive use of [eval] and [exec], including to
process information supplied by the user.  There are protections in
place to prevent code injection, but more work could be done to harden
**docassemble** against such threats.

The option of logging in with Google and Facebook is provided for
convenience, but you may wish to turn it off because the encryption of
interview answers on the server is less effective when users log in
without a password.  This is because the password is typically used as
the encryption key, which is advantageous because it is not stored
anywhere on the server; the user remembers it and it is stored in a
cookie in the user's browser.  When users log in with Google or
Facebook, however, there is no such key available.  As a result, the
key for encrypting user answers on the server is constructed based on
information that is stored on the server.  As a result, an intruder
with access to the server could reverse-engineer the encrpytion key
for an interview belonging to a user who logs in with Google or Facebook.

[login/password system]: {{ site.baseurl }}/docs/users.html
[fail2ban]: https://en.wikipedia.org/wiki/Fail2ban
[Docker]: {{ site.baseurl }}/docs/docker.html
[tmpreaper]: https://packages.debian.org/sid/admin/tmpreaper
[eval]: https://docs.python.org/2/library/functions.html#eval
[exec]: https://docs.python.org/2/reference/simple_stmts.html#exec
[Amazon S3]: https://aws.amazon.com/s3/
[S3]: https://aws.amazon.com/s3/
[Microsoft Azure]: https://azure.microsoft.com/
[Azure blob storage]: https://azure.microsoft.com/en-us/services/storage/blobs/
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[two-factor authentication]: {{ site.baseurl }}/docs/config.html#mfa
[external authentication methods]: {{ site.baseurl }}/docs/config.html#oauth
[phone login]: {{ site.baseurl }}/docs/config.html#phone login
