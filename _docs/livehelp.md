---
layout: docs
title: "Live help: chat, phone, monitoring"
short_title: Live Help
---

# Introduction

Sometimes, users need assistance with answering the questions of an
interview.  **docassemble** facilitates such assistance in a number of
ways, some of which are automatic and others of which require the
intervention of a human operator:

* Users can go to the "Help" tab to read [`interview help`] and
question-specific [`help`] text.
* Users can listen to [`audio`] or watch [`video`] embedded in
questions or help text.
* The [roles] feature can be used to involve a human assistant as a
co-interviewee.  When the interview requires the assistant to answer a
question, **docassemble** will e-mail the assistant a notification
while telling the user to wait.  After the assistant provides the
necessary input, **docassemble** notifies the user by e-mail that he
or she can proceed with the interview.

This section explains three additional features that facilitate the
provision of assistance to users in real time.

### First feature: session monitor

![monitor-example]({{ site.baseurl }}/img/monitor-example.png){:
 .col-md-7 .col-sm-8 .col-xs-12 .nofloat }

On the [monitor] screen, operators can see a list of currently active
interviews.  They can communicate via [live chat] with users and
control which users are allowed to contact them by [phone].  While
communicating by [live chat] or by [phone], the operator can
[see the screen](#observe) that the user is currently seeing.  The
user's changes to the screen are shown to the operator in real time.
The operator can also [join] the interview as a co-interviewee.
Interviews can be set up so that operators can make corrections to the
user's answers.

### Second feature: text-based "live chat"

During a [live chat] conversation, the user sees a screen like the
following:

![chat-conversation-user-view]({{ site.baseurl }}/img/chat-conversation-user-view.png){: .maybe-full-width }

Meanwhile, the operator sees something like this on the [monitor] screen:

![chat-conversation-operator-view]({{ site.baseurl }}/img/chat-conversation-operator-view.png){: .maybe-full-width }

The operator can carry on multiple [live chat] conversations simultaneously.

Conversations will typically take place between the user and an
operator, but it is also possible for the users of a multi-user
interview to use [live chat] to communicate with each other.

### Third feature: telephone call forwarding

![phone-demo]({{ site.baseurl }}/img/phone-demo.png){: .maybe-full-width }

If [live chat] is not convenient to answer the user's questions, the
operator can connect with the user by telephone.  By clicking a
button, the operator can instruct the user to call a phone number and
then type in a four-digit access code.  The user's call will then be
transferred to the operator.  This hides the operator's actual phone
number from the user.  The access code expires after a period of
minutes.  (This feature requires a [Twilio] account; call forwarding
charges apply.)

These three features are explained in more detail in the sections below.

# <a name="monitor"></a>Session monitor

To go to the Monitor, log in to **docassemble** as a user with "admin"
or "advocate" [privileges] and select "Monitor" from the menu.

The Monitor page looks like this:

![monitor-example]({{ site.baseurl }}/img/monitor-example.png){: .maybe-full-width }

It shows a list of currently active interviews for which the live help
features have been enabled.  Operators can use this screen to chat
with one or more users simultaneously, as well as to observe users'
interviews.

## Chat availability settings

Users who activate chat will automatically be
connected to an available operator, if an operator is available.

Whether an operator is available depends on two settings.

First, operators can control whether they are available for chatting
at all by toggling their "status" between "Not available for chat" and
"Available for chat."

![monitor-not-available-to-chat]({{ site.baseurl }}/img/monitor-not-available-to-chat.png)
![monitor-available-to-chat]({{ site.baseurl }}/img/monitor-available-to-chat.png) 

Second, operators can select the "roles" for they wish to be
available.  The interviews on your server may cover a variety of
topics, and your operators may only be willing to serve as operators
if they are asked about interviews within their areas of expertise.

Operators can use the "roles" feature on the Monitor to indicate this
subject matter preference.  In this example, there are two possible
areas of expertise: a general "advocate" and a more specific "family
law" area of expertise.

![monitor-roles]({{ site.baseurl }}/img/monitor-roles.png){: .maybe-full-width }

When an interview developer uses [`set_live_help_status()`] to enable the chat
feature, the developer indicates which "partner roles," or areas of
expertise, are required for the interview.  One interview may indicate
"estates" as a partner role, while another may indicate "family law."
This is the source of the "roles" that the operator sees on the
Monitor screen.

Selecting more than one "role" means that the operator is available to
serve in any of the roles.  (That is, the roles are connected by "or"
rather than "and.")

## Phone number setting

If the [telephone call forwarding] feature has been [configured] in
the **docassemble** [configuration], then operators will be given the
opportunity to enter their phone number.

![monitor-phone-number-box]({{ site.baseurl }}/img/monitor-phone-number-box.png){: .maybe-full-width }

Once a phone number is set, the operator can use the
[telephone call forwarding] feature.

## <a name="sessions"></a>List of sessions

Under "Sessions," the operator will see a list of active interviews
where the interview developer has used [`set_live_help_status()`] to enable
the user and the operator to communicate.

Active sessions for interviews where [`set_live_help_status()`] has not
been run will be invisible.

(It is important for interview developers to inform users that operators
may be monitoring their session.  Interview logic can be used to run
[`set_live_help_status()`] only if and only when the user has consented to
monitoring by an operator.)

![monitor-session-listing]({{ site.baseurl }}/img/monitor-session-listing.png){: .maybe-full-width }

Each session listing consists of:

* A status indicator:
    * ![monitor-indicator-waiting]({{ site.baseurl }}/img/monitor-indicator-waiting.png)
      means that the user is waiting for available chat partners to
      appear;
    * ![monitor-indicator-standby]({{ site.baseurl }}/img/monitor-indicator-standby.png) 
      means that a chat partner is available, but the user has not
      activated chat;
    * ![monitor-indicator-on]({{ site.baseurl }}/img/monitor-indicator-on.png) 
      means that the user has activated [live chat]; and
    * ![monitor-indicator-off]({{ site.baseurl }}/img/monitor-indicator-off.png)
      means that [live chat] is turned off in the user's interview,
      but the user's screen can still be [observed] and [controlled].
    * ![monitor-indicator-offline]({{ site.baseurl }}/img/monitor-indicator-offline.png) 
      means that the user's session has become inactive.
* The interview title (as set in the [metadata]).
* The name of the interviewee, if the user is signed in.
* Control buttons:
    * ![monitor-button-observe]({{ site.baseurl }}/img/monitor-button-observe.png)
      allows the operator to see a [real-time view](#observe) of the
      user's screen, and then take [control] of the screen if necessary;
    * ![monitor-button-join]({{ site.baseurl }}/img/monitor-button-join.png)
      opens a new tab in the operator's browser, where the operator
      [becomes a co-interviewee](#join) in the on-going interview.
    * ![monitor-button-block]({{ site.baseurl }}/img/monitor-button-block.png)
      can be used by the operator to [terminate](#block) an existing chat
      conversation or to prevent the user from initiating one, without
      affecting the operator's availability to other sessions.

When a user is connected with an operator, a [live chat] conversation
area will appear within the session entry.

![chat-example-05]({{ site.baseurl }}/img/chat-example-05.png){: .maybe-full-width }

The operator can carry on multiple conversations at the same time.

To help the operator manage these conversations, the Monitor attempts
to use the desktop notifications feature of the browser.  When a chat
message arrives, the session entry will be highlighted in yellow and
remain highlighted until the operator clicks inside of the message
box.  If a chat message arrives in a session for which the entry is
off-screen, the operator will be notified whether the new message is
above or below.

![monitor-new-conversation-above]({{ site.baseurl }}/img/monitor-new-conversation-above.png){: .maybe-full-width }

## <a name="observe"></a>Observing the interview in progress

The ![monitor-button-observe]({{ site.baseurl }}/img/monitor-button-observe.png)
button displays a real time view of a user's interview screen.  It
changes as the user makes changes to a form or moves from screen to
screen.

![monitor-example-with-observe]({{ site.baseurl }}/img/monitor-example-with-observe.png){: .maybe-full-width }

When the window first opens, the user's changes may take up to six
seconds to be reflected in the window.  After that, changes are
reflected without delay, except for typing in a text box, which may
take up to six seconds to be reflected.

The view of the user's screen is "read-only."  Operators cannot make
changes.  Clicking ![monitor-button-stop-observing]({{ site.baseurl }}/img/monitor-button-stop-observing.png)
will hide the operator's view of the user's screen.

Users do not receive any kind of notification when an operator starts
viewing their screen.  It is up to the interview developer to inform the
user that an operator might be watching.  This can be done before
[`set_live_help_status()`] is called, or at the same time.

## <a name="control"></a>Controlling the interview in progress

In addition to [observing] the user's screen, the operator
can take control and start answering questions on behalf of the user,
while the user watches what the operator does.

When the operator presses the
![monitor-button-control]({{ site.baseurl }}/img/monitor-button-control.png)
button, the user sees a notification like this:

![control-example-controlled]({{ site.baseurl }}/img/control-example-controlled.png){: .maybe-full-width }

While in this mode, the user sees changes that the operator makes to
the screen in real time.  The buttons on the user's screen are
disabled, so that the user cannot submit any changes.  (The other
controls are not disabled, but any changes that the user makes will be
overwritten.)

Meanwhile, the operator can make changes to the user's page in the
miniature window:

![monitor-example-with-control]({{ site.baseurl }}/img/monitor-example-with-control.png){: .maybe-full-width }

When the operator presses the
![monitor-button-stop-controlling]({{ site.baseurl }}/img/monitor-button-stop-controlling.png)
button, the user regains control of the interview:

![control-example-no-longer-controlled]({{ site.baseurl }}/img/control-example-no-longer-controlled.png){: .maybe-full-width }

Note that whenever the live help [availability] setting for an
interview is set to `'observeonly'` or `'available'`, then any
operator can [observe] and [control] the interview without the user's
consent.  Therefore, when you design interviews, it is important that
before you call [`set_live_help_status()`] to set the [availability],
you inform the user that their session may be monitored.

## <a name="join"></a>Joining the interview in progress

When the operator clicks the
![monitor-button-join]({{ site.baseurl }}/img/monitor-button-join.png)
button, a new tab opens up in the operator's browser.  The effect is
similar to that of clicking on a URL created by the
[`interview_url()`] function.  One difference is that the
[`multi_user`] variable does not need to be set to `True` in order to
allow an operator to join an interview from the [monitor].

The operator will join the interview with his or her own user
identity, rather than with the identity of the user.  This means that
the view the operator sees is not necessarily the same as the view
the user sees.  Interview developers can (and probably should) create a
special "back door" into the interview specifically for operators.
For example, the interview developer could write the following into the
interview:

{% include side-by-side.html demo="join" image="join-example.png" %}

Changes that the operator makes to the interview dictionary will be
saved.  However, the user will not see the effect of those changes
until going to a new screen or reloading the page in the web browser.

# <a name="chat"></a>Live chat

The live chat system needs to be enabled by the interview using the
[`set_live_help_status()`] function.  Then, depending on whether a chat
partner is available, the user will be able to go to the help tab
and chat with one or more chat partners.

## Controlling the live chat system from an interview

Interview developers control the [live chat] system from an interview.
They specify whether or not the user should have the option of using
[live chat], and the types of people with whom the user should
be able to chat.

There are two functions that interact with the [live chat] system:
[`set_live_help_status()`] and [`chat_partners_available()`].

### The <a name="set_live_help_status"></a>`set_live_help_status()` function

The `set_live_help_status()` function takes three keyword arguments in
order to control three different settings.

For example:

{% include side-by-side.html demo="chat-example-1" %}

Omitting a keyword argument simply means that the setting will not be
affected.

<a name="availability"></a>The options for `availability` are:

* `'available'`: the user will be able to use [live chat].  Note,
  however, that unless a potential chat partner is available, users
  may not see the feature on the screen.  Operators will also be able
  to [observe] and [control] the user's screen.
* `'unavailable'`: the user will not be able to use [live chat]; they will
  not see any evidence that the feature exists.  Operators will not
  see the interview [session] listed in the monitor.
* `'observeonly'`: the user will not be able to use [live chat], but
  operators will be able to [observe] and [control] the user's screen.

<a name="mode"></a>The options for `mode` are:

* <a name="help mode"></a>`'help'`: the user will be able to have a
  private conversation with an administrator who is using the
  [monitor] system.  In [multi-user interviews], the other users will
  not be able to see the chat conversation.
* <a name="peer mode"></a>`'peer'`: In a [multi-user interview], the
  user will be able to have a group conversation among all of the
  users who are currently using the same interview.
* <a name="peerhelp mode"></a>`'peerhelp'`: This mode is a combination
  of `'help'` and `'peer'`.  Users can get help from an administrator
  using the [monitor] system, but any other users who use the
  interview will be able to see the chat history.

<a name="partner_roles"></a>The `partner_roles` setting is used to
indicate the necessary qualifications of any operator using the
[monitor] who will be able to chat with the user.  For example, if
your interview concerns tax law, but the operators logged in to the
[monitor] only know about family law and criminal law, then you would
not want the user to be able to chat with one of the operators at that
time.

You can set `partner_roles` to either a list of roles
(`['tax law', 'estate law']`) or to a single value (`'family law'`).
If you use multiple values, an operator who selects any one of roles
will be connected with clients.  (That is, they are connected by "or"
rather than "and.")  The values themselves are up to the interview
developer.  When a user is using the interview, the [monitor] will see a
list of the partner roles requested and will be able to select the
roles for which they wish to make themselves available to chat.  The
partner roles are case sensitive.

At least one "role" must be set.

Note that these "partner role" names are separate and distinct from
the names of [privileges] of user accounts and the names of "roles" in
[multi-user interviews].  The names of [privileges] need to be set up
by an administrator on the [Privileges List].  The names of "roles" in
[multi-user interviews] are controlled by interview developers using the
special variables [`role`] and [`role_needed`] and the
[`role` modifier].  Although you may use common names among these
systems (e.g., "advocate,") the three systems are independent.

### The <a name="chat_partners_available"></a>`chat_partners_available()` function 

If no operators or peers are available to chat, you might not want to
turn on the live help system, or even inform the user about the
existence of the system.

You can use the `chat_partners_available()` to find out how many
people are available to chat.

{% include side-by-side.html demo="chat-partners-available" %}

Given a list of [partner roles], `chat_partners_available()` returns
an object with two attributes: `.help` and `.peer`.  Both values will
be integers representing the number of potential chat partners in each
category.

The [partner roles] can be provided in a few different ways.  The
following all do the same thing:

* `chat_partners_available('advocate', 'family law')`
* `chat_partners_available(['advocate', 'family law'])`
* `chat_partners_available(partner_roles=['advocate', 'family law'])`

If you are only interested in the value of `.peer`, you do not need to
provide any [partner roles]; you can simply get the value of
`chat_partners_available().peer`.

### The <a name="get_chat_log"></a>`get_chat_log()` function 

If you want to access the chat log from the interview dictionary, you
can use the `get_chat_log()` function.  It will return a list of chat
messages in chronological order.  Each entry in the list will be a
dictionary with the following keys:

* `message` - the text of the message
* `datetime` - a [`datetime.datetime`] object (with a timezone)
  representing the time the message was sent.
* `user_email` - the e-mail address of the sender.  This will be
  `None` if the user is anonymous.
* `user_first_name` - the first name of the sender.  This will be
  `None` if the user is anonymous, and `''` if the user has not set up
  a first name on the user profile page.
* `user_last_name` - the last name of the sender.  This will be
  `None` if the user is anonymous, and `''` if the user has not set up
  a last name on the user profile page.

The `get_chat_log()` takes two optional keyword arguments:

* `utc` - if `True`, then `datetime` values are reported in [Coordinated Universal
  Time].
* `timezone` - if you want the `datetime` values to be in a specific
  time zone, you can indicate the time zone with the `timezone`
  argument.  This should be a plain text time zone like
  `'US/Eastern'`.  (See [`timezone_list()`] and the [`pytz`] module.)

## Live chat from the user's perspective

The user conducts live chat on the help tab of the interview.

The user can get to the help tab either by pressing "Help" in the
navigation bar or pressing the chat icon.  If there is
[`interview help`] or question-specific [`help`] text, the user will
see a "Help" tab in the navigation bar at the top of the screen.  If
there is no "Help" tab in the navigation bar (i.e. because no
[`interview help`] or question-specific [`help`] text exists), the
user will be able to access the "help" tab by clicking the live chat
icon:

![Chat icon]({{ site.baseurl }}/img/chat-grey-icon.png)

## An example

Here is an scenario that illustrates how live chat works in
[`help`](#help mode) mode.

Suppose the user is in the middle of an interview when an operator
goes to the [monitor] and sets his or her status to "Available to
chat."  On the user's screen, the chat icon appears in the navigation
bar:

![chat-icon-with-popup]({{ site.baseurl }}/img/chat-icon-with-popup.png){: .maybe-full-width }

The user clicks the green chat icon and is taken the the "help" tab.

![chat-example-02]({{ site.baseurl }}/img/chat-example-02.png){: .maybe-full-width }

The chat session has not been activated yet -- the input box is greyed
out.  At the bottom of the screen is a message showing that there is
one operator standing by to chat with the user.

The user then clicks the
![chat-button-activate-chat]({{ site.baseurl }}/img/chat-button-activate-chat.png)
button.

![chat-example-03]({{ site.baseurl }}/img/chat-example-03.png){: .maybe-full-width }

Now the input box is no longer greyed out.

Meanwhile, the operator who is using the Monitor can see that the
status of the session is now "on."

![chat-example-05]({{ site.baseurl }}/img/chat-example-05.png){: .maybe-full-width }

The session entry is highlighted in yellow to alert the operator that
there is a new chat conversation.

Back on the user side, the user can now type a question:

![chat-example-04]({{ site.baseurl }}/img/chat-example-04.png){: .maybe-full-width }

After the user clicks send or presses "Enter," the message is sent.

![chat-example-06]({{ site.baseurl }}/img/chat-example-06.png){: .maybe-full-width }

The message appears on the operator's screen.  The session entry is
highlighted in yellow to indicate that a new chat message has arrived.

![chat-example-07]({{ site.baseurl }}/img/chat-example-07.png){: .maybe-full-width }

As soon as the operator clicks inside the chat box, the yellow
highlighting goes away.  (The color helps the operator keep track of
which chat sessions are still awaiting operator input.)

The operator then starts typing a response.

![chat-example-08]({{ site.baseurl }}/img/chat-example-08.png){: .maybe-full-width }

After the operator clicks send or presses "Enter," the message is
sent.

![chat-example-09]({{ site.baseurl }}/img/chat-example-09.png){: .maybe-full-width }

Note that the two parties to the conversation are represented in
different colors.  The user's own messages are yellow and flush right,
while the chat partner's messages are blue and on the left.

The user sees the operator's question:

![chat-example-10]({{ site.baseurl }}/img/chat-example-10.png){: .maybe-full-width }

If the operator signs off, the user will still be able to access the
chat log, but the icon in the navigation bar is no longer green.

![chat-example-12]({{ site.baseurl }}/img/chat-example-12.png){: .maybe-full-width }

## Effect of chat "mode" setting

If the [`mode`] is [`help`](#help mode), the user will only be able to activate chat
if an operator is available.

If the [`mode`] is [`peer`] or [`peerhelp`], the user will be able to
activate chat even if no operators or peers are available.  This
allows users of an interview to use the chat system as a "message
board" to leave messages for one another.

## <a name="block"></a>Blocking live chat for a session

The user can terminate a [live chat] session by clicking the
![chat-button-turn-off-chat]({{ site.baseurl }}/img/chat-button-turn-off-chat.png)
button.

The operator can terminate a [live chat] session by clicking the
![monitor-button-block]({{ site.baseurl }}/img/monitor-button-block.png)
button.

Note that when the operator sets his or her status to "Not available
to chat," this does not have the effect of terminating any on-going
chat sessions; rather, it has the effect of preventing new chat
sessions from initiating.

If a chat session is on-going when the block button is pressed, the
chat session will be disconnected.  In addition, it also prevents new
chat sessions from being initiated.  For example, if there are three
operators available, and one of the operators blocks a session, the
user will be prevented from initiating a [live chat] session with any
of the operators.

The operator can reverse the effect of the block by clicking the 
![monitor-button-unblock]({{ site.baseurl }}/img/monitor-button-unblock.png)
button.

If the [chat mode] is [`peer`] or [`peerhelp`], blocking the user will
have the effect of taking operators out of the conversation, but the
user will still be allowed to communicate with other peers.

# <a name="phone"></a>Telephone help

The telephone help feature allows an operator to provide a user with a
phone number and an access code that the user can use to reach the
operator by telephone.

![phone-example-snippet]({{ site.baseurl }}/img/phone-example-snippet.png){: .maybe-full-width }

The user will not know the operator's actual phone number.  The phone
number provided to the user is a central phone number for the server,
and the access code is only valid temporarily.

This feature requires an account on [Twilio], and it requires that
your **docassemble** server be accessible from the internet.

## <a name="phone setup"></a>Setting up call forwarding

To enable the call forwarding feature, first go to [Twilio] and:

* Sign up for an account.
* Note your "account SID."
* Buy a phone number.  Note the phone number.
* Under the "Voice" configuration for the phone number, instruct
  Twilio that when a user calls the phone number, Twilio should go to
  the `/voice` URL on your **docassemble** server to receive TwiML
  instructions for responding to the call.  For example, if you access
  interviews at https://example.com, set the URL for incoming voice
  calls to https://example.com/voice.

![phone-twilio-configuration]({{ site.baseurl }}/img/phone-twilio-configuration.png){: .maybe-full-width }

Then, in your **docassemble** [configuration], add lines like:

{% highlight yaml %}
twilio:
  voice: True
  account sid: ACfad8e668d876f5473fb232a311243b58
  number: "+12762410114"
{% endhighlight %}

where `account sid` is the value you copy and paste from your [Twilio]
account dashboard, and `number` is the phone number you purchased.
The phone number must be written in [E.164] format.

## Set phone number for the operator

The call forwarding feature will only be available to an operator if
the operator has specified a phone number.

![phone-example-number]({{ site.baseurl }}/img/phone-example-number.png){: .maybe-full-width }

The phone number must by specified in [E.164] format.  In the United
States, this simply means that the phone number must begin with "1,"
which is the country code for the United States, and must then be
followed by the area code and the rest of the phone number.

Once the phone number is entered, and it is not invalid, buttons for
activating call forwarding will appear within each session.

After the operator clicks the button, the operator's screen will look
like this, indicating that telephone calls with the first session are enabled.

![phone-example-green-icon]({{ site.baseurl }}/img/phone-example-green-icon.png)

Clicking the ![phone-button-green]({{ site.baseurl }}/img/phone-button-green.png)
button will toggle the enabling of call forwarding.

Within seconds of the operator enabling call forwarding, the user will
see a green telephone icon at the top of the screen.

![phone-example-user-icon-with-popup]({{ site.baseurl }}/img/phone-example-user-icon-with-popup.png){: .maybe-full-width }

When users click on the icon (or otherwise go to the Help tab) they
will see instructions about how to make the phone call.

![phone-example-message]({{ site.baseurl }}/img/phone-example-message.png)

Once the phone call is placed, the code will be deactivated, and the
user will not longer see the calling instructions or the phone icon.

[configuration]: {{ site.baseurl }}/docs/config.html
[roles]: {{ site.baseurl }}/docs/roles.html
[multi-user interview]: {{ site.baseurl }}/docs/roles.html
[multi-user interviews]: {{ site.baseurl }}/docs/roles.html
[monitor]: #monitor
[Monitor]: #monitor
[`interview help`]: {{ site.baseurl }}/docs/initial.html#interview help
[`help`]: {{ site.baseurl }}/docs/modifiers.html#help
[`audio`]: {{ site.baseurl }}/docs/modifiers.html#audio
[`video`]: {{ site.baseurl }}/docs/modifiers.html#video
[Twilio]: https://twilio.com
[E.164]: https://support.twilio.com/hc/en-us/articles/223183008-Formatting-International-Phone-Numbers
[privilege]: {{ site.baseurl }}/docs/users.html#privileges
[privileges]: {{ site.baseurl }}/docs/users.html#privileges
[Privileges List]: {{ site.baseurl }}/docs/users.html#privileges
[Telephone call forwarding]: #phone
[`set_live_help_status()`]: #set_live_help_status
[`chat_partners_available()`]: #chat_partners_available
[telephone call forwarding]: #phone
[phone]: #phone
[metadata]: {{ site.baseurl }}/docs/initial.html#metadata
[Observe]: #observe
[observe]: #observe
[observing]: #observe
[control]: #control
[controlling]: #control
[observed]: #observe
[controlled]: #control
[session]: #sessions
[sessions]: #sessions
[Join]: #join
[Block]: #join
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[configured]: #phone setup
[partner roles]: #partner_roles
[live chat]: #chat
[chat]: #chat
[`interview_url()`]: {{ site.baseurl }}/docs/functions.html#interview_url
[`role`]: {{ site.baseurl }}/docs/special.html#role
[`role_needed`]: {{ site.baseurl }}/docs/special.html#role
[`role` modifier]: {{ site.baseurl }}/docs/modifiers.html#role
[`help` mode]: #help mode
[`peer` mode]: #peer mode
[`peerhelp` mode]: #peerhelp mode
[`peer`]: #peer mode
[`peerhelp`]: #peerhelp mode
[chat mode]: #mode
[`mode`]: #mode
[availability]: #availability
[`datetime.datetime`]: https://docs.python.org/2/library/datetime.html#datetime.datetime
[Coordinated Universal Time]: https://en.wikipedia.org/wiki/Coordinated_Universal_Time
[`timezone_list()`]: {{ site.baseurl }}/docs/functions.html#timezone_list
[`pytz`]: http://pytz.sourceforge.net/
