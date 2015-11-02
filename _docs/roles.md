---
layout: docs
title: Roles
short_title: Roles
---

**docassemble** allows you to create multi-user interviews.

There are several possible applications for multi-user interviews:
* In a legal application, a client uses the interview first to answer
  questions about the facts of a case, and then an attorney reviews
  the responses, applies the law to the facts, makes some decisions,
  and then the client comes back to the interview to receive a legal
  advice letter.
* If a user's language is not English, a translator will be invited to
  join the interview to translate the user's textual responses into
  English before the interview process is completed.
* In a negotiation context, two parties will fill in answers to an
  interview, and when both are done, the interview will suggest a
  resolution based on the answers of both parties.

Multi-user interviews are implemented through the [user login] feature
and three authoring features that were introduced in other sections:

* `role` [modifier]: designates certain questions as being reserved
  for particular users to fill out.
* `default role` [initial block]: sets the role for questions that do
  not have a `role` set.  Its associated `code` is run as `initial`
  code and should set the variable `role` depending on the identity of
  the person logged in (which can be determined from the
  `current_info['user']` dictionary).
* `event` [variables]: when the current user cannot proceed further
  with the interview because the interview needs input from a
  different user, **docassemble** will need to display a message for
  the current user.  The way it is this is by looking for a question
  that offers to define the variable `role_event`.  So if you create a
  question with a line indicating `event: role_event`, **docassemble**
  will present this question to the user when the required role
  changes.

To see how the multi-user system works, consider the following example
of a three-role interview.

The interview starts with an organizer, who clicks past an
introductory screen and is asked for the e-mail addresses of two
participants who will bid on a contract.  The organizer is then asked
to invite the participants to bid by clicking on a particular link and
logging in.  Once both bidders have entered their bids, the winner
(the participant with the lowest bid) is announced.  Until both
participants have entered bids, users will see a page telling them to
wait and to press the "Check" button to see if the bids are in yet.

{% highlight yaml %}
---
default role: organizer
code: |
  role = 'organizer'
  if introduction_made and participants_invited:
    if current_info['user']['is_authenticated']:
      if current_info['user']['email'] == first_person_email:
        role = 'first_person'
      elif current_info['user']['email'] == second_person_email:
        role = 'second_person'
---
event: role_event
question: Waiting on another participant
subquestion: |
  % if 'first_person' in role_needed or 'second_person' in role_needed:
  We are waiting for a participant to put in a bid.
  % else:
  We are waiting for the organizer.
  % endif

  % if not current_info['user']['is_authenticated']:
  If you were invited to participate, please click "Sign in."
  % endif

  Press **Check** to check on the status.
buttons:
  - Check: refresh
---
mandatory: true
code: |
  if role == 'first_person':
    first_person_bid
  if role == 'second_person':
    second_person_bid
  announce_winner
---
field: introduction_made
question: |
  Welcome to a test of the multi-user system!
subquestion:
  This is the start of a test of the multi-user system.
  You are the organizer.  To continue, press **Continue**.
---
code: |
  if first_person_email == second_person_email:
    organizer_messed_up
  else:
    recipients_ok = True
---
field: participants_invited
need: recipients_ok
question: |
  Invite the bidders
subquestion: |
  Ok, organizer, send e-mails to ${ first_person_email } and
  ${ second_person_email } inviting them to submit bids.

  Tell them to go to the following URL:

  [${ interview_url }](${ interview_url })
---
code: |
  interview_url = current_info['url'] + '?i=' + current_info['yaml_filename'] + '&session=' + current_info['session']
---
sets: announce_winner
role:
  - organizer
  - first_person
  - second_person
question: And the winner is...
subquestion: |
  % if first_person_bid < second_person_bid:
  The winning bidder is First Person!
  % elif first_person_bid > second_person_bid:
  The winning bidder is Second Person!
  % else:
  Sorry, no winner.  The bids matched.
  % endif
---
question: |
  What are the e-mail addresses of the participating bidders?
fields:
  - First Person: first_person_email
    datatype: email
  - Second Person: second_person_email
    datatype: email
---
role: first_person
question: |
  How much will you bid for the contract?
fields:
  - Amount: first_person_bid
    datatype: currency
---
role: second_person
question: |
  How much will you bid for the contract?
fields:
  - Amount: second_person_bid
    datatype: currency
---
sets: organizer_messed_up
question: |
  That won't work.
subquestion: |
  Please try again.  This time enter different e-mail addresses
  for the participants.
buttons:
  - Restart: restart
...
{% endhighlight %}

Most of the code is self-explanatory, but a few of the blocks warrant
explanation.

Consider the first block:

{% highlight yaml %}
---
default role: organizer
code: |
  role = 'organizer'
  if introduction_made and participants_invited:
    if current_info['user']['is_authenticated']:
      if current_info['user']['email'] == first_person_email:
        role = 'first_person'
      elif current_info['user']['email'] == second_person_email:
        role = 'second_person'
---
{% endhighlight %}

Here, we set the `default role` to organizer.  This simply means that
questions in the interview that do not have a `role` specified will
require the `organizer` role.

The `code` is `initial` code, the purpose of which is to set the
`role` variable, which is the role of whichever user is currently in
the interview.  This code runs every single time the page loads for
any user.

First, note that the `role` for all users will remain `organizer`
until the organizer has seen the introductory page and the
participants have been invited.

Second, note that the flow of the interview is being controlled here.
The references to `introduction_made` and `participants invited` mean
that questions will be asked to define those variables if they are
undefined.  This is the code that causes those questions to appear for
the organizer.

Third, note that by requiring `participants invited` to be set before
we consider whether the user's e-mail address is equal to
`first_person_email`, we ensure that the interview flow proceeds the
way we want it to.  Suppose we did not check for `participants
invited` before doing this.  If the organizer was logged in and gave
his own e-mail address as that of a participant, he would assume the
role of a participant before learning the URL that he needs to give to
the other participant.  There are times when you just want
**docassemble** to figure out the interview flow implicitly, and there
are times when you want to be explicit about it.  Setting up roles is
one situation where you want to be explicit, so that you account for
all the unexpected scenarios that may occur.

Another block that warrants explanation is the `mandatory` `code`
block:

{% highlight yaml %}
---
mandatory: true
code: |
  if role == 'first_person':
    first_person_bid
  if role == 'second_person':
    second_person_bid
  announce_winner
---
{% endhighlight %}

We could simply shorten the code to `announce_winner`, and the
interview could still get done, because `announce_winner` implicitly
asks for both `firth_person_bid` and `second_person_bid`.  The problem
(or inconvenience) is that `announce_winner` looks for the value of
`first_person_bid` before it looks for the value of
`second_person_bid`.  This means that the second participant would
have to wait to enter his bid until the first participant had done so.
This would be arbitrary and could cause unnecessary delay.  The
additional code here will ask each participant for his bid regardless
of which one is first to log in.

[initial block]: {{ site.baseurl }}/docs/initial.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[fields]: {{ site.baseurl }}/docs/fields.html
