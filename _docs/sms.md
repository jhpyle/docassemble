---
layout: docs
title: Text messaging interface
short_title: Text messaging
---

# Introduction

While the primary interface for **docassemble** interviews is through
a web browser, your users can also interact with interviews using text
messaging (also known as [SMS]).

![sms-example-web]({{ site.baseurl }}/img/sms-example-web.png)
![sms-example-sms]({{ site.baseurl }}/img/sms-example-sms.png)

Users start by texting a phone number with a keyword representing the
interview they will start.  Then, the user's interactions will be with
that interview until the interview exits.

This feature requires a [Twilio] account.

# <a name="sms setup"></a>Setting up the SMS interface

To enable the text messaging feature, first go to [Twilio] and:

* Sign up for an account.
* Note your "account SID."
* Buy a phone number.  Note the phone number.
* Under the "Messaging" configuration for the phone number, instruct
  Twilio that when a user sends a text to the phone number, Twilio should go to
  the `/sms` URL on your **docassemble** server to receive TwiML
  instructions for responding to the message.  For example, if you access
  interviews at https://example.com, set the URL for incoming voice
  calls to https://example.com/sms.

![text-twilio-configuration]({{ site.baseurl }}/img/text-twilio-configuration.png){: .maybe-full-width }

Then, in your **docassemble** [configuration], add lines like:

{% highlight yaml %}
twilio:
  sms: true
  account sid: ACfad8e668d876f5473fb232a311243b58
  caller id: "+12762410114"
  dispatch:
    color: docassemble.base:data/questions/examples/buttons-code-color.yml
    doors: docassemble.base:data/questions/examples/doors.yml
  default interview: docassemble.demo:data/questions/questions.yml
{% endhighlight %}

The `sms: true` line tells **docassemble** that you intend to use the
text messaging feature.  (Note that the `twilio` [configuration]
section is also used to enable the [call forwarding] feature.)

The `account sid` is the value you copy and paste from your [Twilio]
account dashboard.

The `caller id` is the phone number you purchased.  The phone number
must be written in [E.164] format.  This is the phone number with
which your users will exchange [SMS] messages.

<a name="dispatch"></a>The `dispatch` configuration allows you to
direct users to different interviews.  For example, with the above
configuration, you can tell your prospective users to "text 'color' to
276-241-0114."  Users who initiate a conversation by sending the SMS
message "help" to the [Twilio] phone number will be started into the
`docassemble.base:data/questions/examples/sms.yml` interview.

If a user's first SMS message to the [Twilio] phone number is not one
of the choices under `dispatch`, the `default interview` is used.

# Special messages

If the user sends a text consisting of any of the following, a special
action will be taken:

* `?` shows the help for the question ([`help`]) and/or the interview
([`interview help`]).  The definition of [`terms`] is included.
* `question` shows the question again.
* `exit` deletes the interview session.  Nothing is returned.  This
  allows the user to start a different interview by texting a
  [`dispatch`] keyword.
* `back` goes back one page.
* `skip` is an option for questions that ask for non-required fields.
* `none` is an option for checkbox questions.

# What works and what does not

The text messaging interface can receive document uploads ([`file`],
[`files`], etc.) and send attachments ([`attachment`],
[`attachments`]) through [MMS].  However, it cannot handle
[`signature`] blocks.  All other methods of [setting variables] are
supported.

Since text messages are plain text, the text messaging interface
cannot handle [decorations], [inline images], [emoji], or [markup]
such as bold, italics, etc.  Nor can it handle interaction with the
user through the menu ([`action_menu_item()`]) or through links
([`url_action()`]).  The [`reload` modifier] is not supported, but
users can manually "reload" the screen by typing `question`.

The [`terms`] feature is supported.  Users can send `?` to read the
definitions of terms.

The [live help] features are not supported.

# How to write SMS-friendly interviews

When giving instructions to the user that relate to the user
interface, use the [`interface()` function] to identify the manner in
which the user is accessing the interview.  If [`interface()`] is
`'web'`, give instructions like "use the menu in the upper right to
. . ."  If [`interface()`] is `'sms'`, give instructions like "type
help to get help."

Avoid using vocabulary that is specific to a particular interface.
For example, instead of telling users to "check" checkboxes, ask them
to "select" choices from a list.

Make sure that users never have to type special [SMS] keywords.  These
include:

* `cancel`
* `end`
* `help`
* `info`
* `quit`
* `stop`
* `stopall`
* `unsubscribe`

For more information about this limitation, see
_[Industry standards for U.S. short code HELP and STOP]_.

[`signature`]: {{ site.baseurl }}/docs/fields.html#signature
[`file`]: {{ site.baseurl }}/docs/fields.html#file
[`files`]: {{ site.baseurl }}/docs/fields.html#files
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
[`attachments`]: {{ site.baseurl }}/docs/documents.html#attachments
[Industry standards for U.S. short code HELP and STOP]: https://support.twilio.com/hc/en-us/articles/223182208-Industry-standards-for-U-S-short-code-HELP-and-STOP
[`interface()`]: {{ site.baseurl }}/docs/functions.html#interface
[`interface()` function]: {{ site.baseurl }}/docs/functions.html#interface
[SMS]: https://en.wikipedia.org/wiki/Short_Message_Service
[MMS]: https://en.wikipedia.org/wiki/Multimedia_Messaging_Service
[call forwarding]: {{ site.baseurl }}/docs/livehelp.html#phone setup
[configuration]: {{ site.baseurl }}/docs/config.html
[Twilio]: https://twilio.com
[E.164]: https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers
[`terms`]: {{ site.baseurl }}/docs/initial.html#terms
[`interview help`]: {{ site.baseurl }}/docs/initial.html#interview help
[`help`]: {{ site.baseurl }}/docs/modifiers.html#help
[`dispatch`]: #dispatch
[live help]: {{ site.baseurl }}/docs/livehelp.html
[decorations]: {{ site.baseurl }}/docs/modifiers.html#decoration
[markup]: {{ site.baseurl }}/docs/markup.html
[inline images]: {{ site.baseurl }}/docs/markup.html#inserting images
[emoji]: {{ site.baseurl }}/docs/markup.html#emoji
[setting variables]: {{ site.baseurl }}/docs/fields.html
[`action_menu_item()`]: {{ site.baseurl }}/docs/functions.html#action_menu_item
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`reload` modifier]: {{ site.baseurl }}/docs/modifiers.html#reload
