---
layout: policy
title: Data Privacy Policy
short_title: Data Privacy
---

# Data privacy policy

*Note: **docassemble** is licensed under the [MIT License].  This
policy does not modify that license or create any contract.*

## Data privacy and the application

**docassemble** is not software-as-a-service; it is just software.
The **docassemble** software itself does not contain any code that
surreptitiously "phones home" or tracks user activity.  Jonathan Pyle
is not aware that any of the dependencies do that, either.

Data privacy is the responsibility of the people who deploy
**docassemble**.  A lot depends on how it is implemented; for example,
how the SQL server is set up may provide greater or lesser data
privacy depending on the choices of the implementer.

**docassemble** contains a number of privacy features that benefit end
user data privacy, such as:
* Server-side encryption where the user's interview answers are
  encrypted by the user's password.  The downside is that if a user
  forgets their password, they are locked out of their answers.
* Password-based login system.  There are also other authentication
  mechanisms, but they diminish the security of server-side encryption
  because the decryption key is stored inside the sever.
* Role-based authorization system that allows administrators to assign
  varying levels of permission to users.
* Automatic banning of any IP addresses that try to guess passwords.

**docassemble** contains a number of features that enable end users'
the right to be forgotten, such as:

* Ability for the user to delete their own account in the user
  profile; and 
* Automatic session deletion after a period of time.

There are optional features that implicate end user privacy, such as:

* Google Analyics and Segment cookie tracking;
* Ability of administrators to turn off server-side encryption;
* Ability of administrators to prevent users from deleting their own
  data;
* Ability of administrators to access user data through the API and
  other means.
* Social login features that diminish the security provided by
  server-side encryption by storing the decryption key on the server.
  
Unless the administrator takes steps to retain user data, a request by
a user to delete their information will be effective, subject to the
following considerations:

* User information may continue to exist in logs and rotating backups,
  which can persist for a few weeks after the user has deleting their data.
* User information may exist in temporary files, which by default are
  culled after a few hours.
* A record will persist in a table indicating that a user with a given
  integer user ID once existed.

If Jonathan Pyle becomes aware of a security issue in a dependency, he
will endeavor to fix the issue as soon as possible.  Notification to
users will be in the form of GitHub commit messages and changelog
messages.

## Data privacy and the development community

The **docassemble** community collaborates in a number of ways:

* A [Slack group];
* An annual conference called [Docacon]; and
* A [mailing list];

### Slack

Jonathan Pyle created a [Slack group] for the the **docassemble**
community to ask questions and help each other.  The [Slack group] is
on [Slack]'s free plan, which means that access to older messages is
restricted.  The group is open to the public.  [Slack] contains
private chats, group chats, and a member list containing names and
e-mails.

If a user accidentally shares sensitive information on Slack, such as
an API key, and Jonathan Pyle sees it, he will notify the user that
they shared sensitive information.

Sometimes people write to Jonathan Pyle privately because they do not
want to reveal details of their projects to the group.  Jonathan Pyle
will keep the content of those conversations private.

Jonathan Pyle is the sole administrator of the [Slack group].  He is
the only one with access to the e-mail addresses of members.  He does
not back up or make copies of the e-mail addresses and will not share
the e-mail address list with third parties.

A few APIs are enabled on the Slack group, such as an API that posts
messages in Slack when there is activity on GitHub.  If an intruder
obtains unauthorized access to the Slack group through an API,
Jonathan Pyle will make best efforts to block the intruder's access.

If [Slack] itself suffers a data breach, such that e-mail addresses
are exposed, Jonathan Pyle will post a message in the `#general`
channel to let users know that it happened.

### Docacon

The Docacon conference is open to the public.  Attendees sign up on
Google Forms.  Data about attendees and sponsors exists in Google
Forms.  Access to the sign-up list is limited to event organizers,
which includes Jonathan Pyle and other people.  Copies of the sign-up
list may have been made.

If Google Forms suffers a data breach, Jonathan Pyle will take no
action.

### Mailing list

Jonathan Pyle created a [mailing list] on [python.org].  It was
originally used the way the [Slack group] is used now, but once we
switched to Slack, the mailing list does not get much use.  The
primary purpose of the mailing list is to communicate with people who
sign up for the mailing list but have not joined Slack or do not check
Slack.  Jonathan Pyle is the sole maintainer of the list.  The mailing
list hosted on [python.org] contains e-mail addresses and names of
people who have signed up.  Jonathan Pyle has not created a copy of
the mailing list anywhere outside of [python.org].

If [python.org]'s mailing list system is compromised, Jonathan Pyle
will make an effort to delete the mailing list.

[Slack]: https://slack.com
[python.org]: https://mail.python.org/archives/
[Docacon]: https://docacon.com
[mailing list]: https://mail.python.org/mm3/mailman3/lists/docassemble.python.org/
[Slack group]: {{ site.slackurl }}
[MIT License]: {{ site.baseurl }}/docs/license.html
