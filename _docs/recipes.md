---
layout: docs
title: Recipes
short_title: Recipes
---

This section contains miscellaneous recipes for solving problems in
**docassemble**.

# <a name="require checkbox"></a>Require a checkbox to be checked

## Using `validation code`

{% highlight yaml %}
question: |
  You must agree to the terms of service.
fields:
  - I agree to the terms of service: agrees_to_tos
    datatype: yesnowide
validation code: |
  if not agrees_to_tos:
    validation_error("You cannot continue until you agree to the terms of service.")
---
mandatory: True
need: agrees_to_tos
question: All done.
{% endhighlight %}

## Using `datatype: checkboxes`

{% highlight yaml %}
question: |
  You must agree to the terms of service.
fields:
  - no label: agrees_to_tos
    datatype: checkboxes
    minlength: 1
    choices:
      - I agree to the terms of service
    validation messages:
      minlength: |
        You cannot continue unless you check this checkbox.
---
mandatory: True
need: agrees_to_tos
question: All done
{% endhighlight %}

# <a name="completion"></a>Use a variable to track when an interview has been completed

One way to track whether an interview is completed is to set a
variable when the interview is done.  That way, you can inspect the
interview answers and test for the presence of this variable.

{% highlight yaml %}
objects:
  - user: Individual
---
question: |
  What is your name?
fields:
  - First name: user.name.first
  - Last name: user.name.last
---
mandatory: True
code: |
  user.name.first
  user_finish_time
  final_screen
---
code: |
  user_finish_time = current_datetime()
---
event: final_screen
question: |
  Goodbye, user!
buttons:
  Exit: exit
{% endhighlight %}

You could also use Redis to store the status of an interview.

{% highlight yaml %}
objects:
  - user: Individual
  - r: DARedis
---
question: |
  What is your name?
fields:
  - First name: user.name.first
  - Last name: user.name.last
---
mandatory: True
code: |
  interview_marked_as_started
  user.name.first
  interview_marked_as_finished
  final_screen
---
code: |
  redis_key = user_info().filename + ':' + user_info().session
---
code: |
  r.set(redis_key, 'started')
  interview_marked_as_started = True
---
code: |
  r.set(redis_key, 'finished')
  interview_marked_as_finished = True
---
event: final_screen
question: |
  Goodbye, user!
buttons:
  Exit: exit
{% endhighlight %}

# <a name="exit hyperlink"></a>Exit interview with a hyperlink rather than a redirect

Suppose you have a final screen in your interview that looks like this:

{% highlight yaml %}
mandatory: True
code: |
  kick_out
---
event: kick_out
question: Bye
buttons:
  - Exit: exit
    url: https://example.com
{% endhighlight %}

When the user clicks the "Exit" button, an Ajax request is sent to the
**docassemble** server, the interview logic is run again, and then
when the browser processes the response, the browser is redirected
by JavaScript to the url (https://example.com).

If you would rather that the button act as a hyperlink, where clicking
the button sends the user directly to the URL, you can make the button
this way:

{% highlight yaml %}
mandatory: True
code: |
  kick_out
---
event: kick_out
question: Bye
subquestion: |
  ${ action_button_html("https://example.com", size='md', color='primary', label='Exit', new_window=False) }
{% endhighlight %}

# <a name="two fields match"></a>Ensure two fields match

{% highlight yaml %}
question: |
  What is your e-mail address?
fields:
  - E-mail: email_address_first
    datatype: email
  - note: |
      Please enter your e-mail address again.
    datatype: email
  - E-mail: email_address
    datatype: email
  - note: |
      Make sure the e-mail addresses match.
    js hide if: |
      val('email_address') != '' && val('email_address_first') == val('email_address')
  - note: |
      <span class="text-success">E-mail addresses match!</span>
    js show if: |
      val('email_address') != '' && val('email_address_first') == val('email_address')
validation code: |
  if email_address_first != email_address:
    validation_error("You cannot continue until you confirm your e-mail address")
---
mandatory: True
question: |
  Your e-mail address is ${ email_address }.
{% endhighlight %}

# <a name="progressive disclosure"></a>Progressive disclosure

{% include demo-side-by-side.html demo="progressive-disclosure" %}

Add `progressivedisclosure.css` to the "static" data folder of your package.

{% highlight css %}
a span.pdcaretopen {
    display: inline;
}

a span.pdcaretclosed {
    display: none;
}

a.collapsed .pdcaretopen {
    display: none;
}

a.collapsed .pdcaretclosed {
    display: inline;
}
{% endhighlight %}

Add `progressivedisclosure.py` as a Python module file in your
package.

{% highlight python %}
import re

__all__ = ['prog_disclose']

def prog_disclose(template, classname=None):
    if classname is None:
        classname = ' bg-secondary-subtle'
    else:
        classname = ' ' + classname.strip()
    the_id = re.sub(r'[^A-Za-z0-9]', '', template.instanceName)
    return u"""\
<a class="collapsed" data-bs-toggle="collapse" href="#{}" role="button" aria-expanded="false" aria-controls="collapseExample"><span class="pdcaretopen"><i class="fas fa-caret-down"></i></span><span class="pdcaretclosed"><i class="fas fa-caret-right"></i></span> {}</a>
<div class="collapse" id="{}"><div class="card card-body{} pb-1">{}</div></div>\
""".format(the_id, template.subject_as_html(trim=True), the_id, classname, template.content_as_html())
{% endhighlight %}

This uses the [collapse feature] of [Bootstrap].

# <a name="accordion"></a>Accordion user interface

Helper functions defined in a module file can be useful for inserting
complex HTML into your `question` blocks without making the `question`
blocks less readable.

In the [`docassemble.demo`] package, there is a module,
[`docassemble.demo.accordion`], which demonstrates a set of functions,
`start_accordion()`, `next_accordion()`, and `end_accordion()`, that
return HTML.

The following example demonstrates how to use the functions exported
by [`docassemble.demo.accordion`] to create an accordion interface in
a `review` screen, using the [accordion feature] of [Bootstrap].

{% include demo-side-by-side.html demo="testaccordion1" %}

The same could be done with a `fields` list.

{% include demo-side-by-side.html demo="testaccordion2" %}

The above two examples make use of the [`raw html`] feature that was
introduced in version 1.4.94.

The functions in [`docassemble.demo.accordion`] can also be used in
other parts of a screen, such as the `subquestion`.

{% include demo-side-by-side.html demo="testaccordion3" %}

If you need empty accordions to be hidden you can use some CSS to hide
empty accordions.

{% include demo-side-by-side.html demo="testaccordion4" %}

The CSS in the `accordion.css` file is:

{% highlight css %}
div.accordion-item:has(.accordion-body:empty) h2 {
    display: none;
}

div.accordion-item:has(.accordion-body:empty) div {
    display: none;
}
{% endhighlight %}

When using functions like these that change the HTML structure of the
screen, it is very important not to forget to call the functions that
insert closing HTML tags, like `end_accordion()` in this example. If
the correct functions are not called, the HTML of the screen could be
invalid.

**docassemble** add-on packages could be created that offer user
interface enhancements invoked through functions. In the examples
above, the functionality was imported through a `modules` block, but
it would also be possible to instruct users of an add-on package to
use an `include` block to activate the functionality. The `include`
block could point to a file in the `questions` folder of the add-on
package that contains a `modules` block that imports the functions, as
well as a `features` block that activates custom JavaScript and CSS.

# <a name="cards"></a>Displaying cards

[Bootstrap] has a component called a [Card] that puts text in a box
with rounded corners. Here is an example of an add-on utility that
facilitates the use of the [Card].

{% include demo-side-by-side.html demo="testcards" %}

The YAML file [`cards.yml`] consists of:

{% highlight yaml %}
modules:
  - .cards
{% endhighlight %}

The Python module [`cards.py`] consists of:

{% highlight python %}
import re

__all__ = ['card_start', 'card_end']

def card_start(label, color=None, icon=None):
    if color not in ('primary',
                     'secondary',
                     'success',
                     'danger',
                     'warning',
                     'info',
                     'light',
                     'dark',
                     'link'):
        color_text = ''
    else:
        color_text = ' text-bg-' + color
    if icon is None:
        icon_text = ''
    else:
        icon_text = re.sub(r'^(fa[a-z])-fa-', r'\1 fa-', str(icon))
        if not re.search(r'^fa[a-z] fa-', icon_text):
            icon_text = 'fas fa-' + icon
        icon_text = '<i class="' + icon_text + '"></i> '
    return f'<div class="card{color_text} mb-3" markdown="span"><div class="card-body" markdown="1"><h2 class="card-title h4" markdown="span">{icon_text}{label}</h2>'

def card_end():
    return '</div></div>'
{% endhighlight %}

The module defines two functions, `card_start()` and `card_end()`,
which are used to mark the beginning and end of a [Card]. The two
functions return HTML. The text that you want to appear in the [Card]
is written in Markdown format in between the call to `card_start()`
and the call to `card_end()`. If you forget to include `card_end()`,
there will be an HTML error on the screen.

Note that the `card_start()` function makes use of the [Markdown in
HTML extension]. Using `markdown="span"` enables the parsing of
Markdown in the interior of the `<div>`. Otherwise, any Markdown
formatting in the body of the [Card] would be presented literally on
the screen.

To use this module in your own interviews, save [`cards.yml`] and
[`cards.py`] to your package and modify them as you wish. Since
[`cards.yml`] only has a single `modules` block, so you might be
tempted to do away with it and simply include [`cards.py`] directly in
interviews that need to use the [Card] UI. However, using a YAML file
makes sense because you may wish to format [Card] elements with custom
CSS classes. In that case, you can add a `features` block to your
[`cards.yml`] file, and any interviews that include `cards.yml` will
not need to be modified.

# <a name="new or existing"></a>New object or existing object

The [`object` datatype] combined with the [`disable others`] can be
used to present a single question that asks the user either to select
an object from a list or to enter information about a new object.

Another way to do this is to use `show if` to show or hide fields.

This recipe gives an example of how to do this in an interview that
asks about individuals.

{% include demo-side-by-side.html demo="new-or-existing" %}

This recipe keeps a master list of individuals in an object called
`people`.  Since this list changes throughout the interview, it is
re-calculated whenever a question is asked that uses `people`.

When individuals are treated as unitary objects, you can do things
like use Python's `in` operator to test whether an individual is a
part of a list.  This recipe illustrates this by testing whether
`boss` is part of `customers` or `employee` is part of `customers`.

# <a name="resume via email"></a>E-mailing the user a link for resuming the interview later

If you want users to be able to resume their interviews later, but you
don't want to use the username and password system, you can e-mail
your users a URL created with [`interview_url()`].

{% include demo-side-by-side.html demo="save-continue-later" %}

# <a name="hybrid"></a>E-mailing or texting the user a link for purposes of using the touchscreen

Using a desktop computer is generally very good for answering
questions, but it is difficult to write a signature using a mouse.

Here is an example of an interview that allows the user to use a
desktop computer for answering questions, but use a mobile device with
a touchscreen for writing the signature.

{% include demo-side-by-side.html demo="food-with-sig" %}

This interview includes a [YAML] file called
[`signature-diversion.yml`], the contents of which are:

{% highlight yaml %}
mandatory: True
code: |
  multi_user = True
---
question: |
  Sign your name
subquestion: |
  % if not device().is_touch_capable:
  Please sign your name below with your mouse.
  % endif
signature: user.signature
under: |
  ${ user }
---
sets: user.signature
code: |
  signature_intro
  if not device().is_touch_capable and user.has_mobile_device:
    if user.can_text:
      sig_diversion_sms_message_sent
      sig_diversion_post_sms_screen
    elif user.can_email:
      sig_diversion_email_message_sent
      sig_diversion_post_email_screen
---
question: |
  Do you have a mobile device?
yesno: user.has_mobile_device
---
question: |
  Can you receive text messages on your mobile device?
yesno: user.can_text
---
question: |
  Can you receive e-mail messages on your mobile device?
yesno: user.can_email
---
code: |
  send_sms(user, body="Click on this link to sign your name: " + interview_url_action('mobile_sig'))
  sig_diversion_sms_message_sent = True
---
code: |
  send_email(user, template=sig_diversion_email_template)
  sig_diversion_email_message_sent = True
---
template: sig_diversion_email_template
subject: Sign your name with your mobile device
content: |
  Make sure you are using your
  mobile device.  Then
  [click here](${ interview_url_action('mobile_sig') })
  to sign your name with
  the touchscreen.
---
question: |
  What is your e-mail address?
fields:
  - E-mail: user.email
---
question: |
  What is your mobile number?
fields:
  - Number: user.phone_number
---
event: sig_diversion_post_sms_screen
question: |
  Check your text messages.
subquestion: |
  We just sent you a text message containing a link.  Click the link
  and sign your name.

  Once we have your signature, you will move on automatically.
reload: 5
---
event: sig_diversion_post_email_screen
question: |
  Check your e-mail on your mobile device.
subquestion: |
  We just sent you an email containing a link.  With your mobile
  device, click the link and sign your name.

  Once we have your signature, you will move on automatically.
reload: 5
---
event: mobile_sig
need: user.signature
question: |
  Thanks!
subquestion: |
  We got your signature:

  ${ user.signature }

  You can now resume the interview on your computer.
{% endhighlight %}

The above interview requires setting `multi_user = True`.  To avoid
this you can use the following pair of interviews.

First interview:

{% highlight yaml %}
objects:
  - r: DARedis
---
mandatory: True
code: |
  email_sent
  signature_obtained
  final_screen
---
code: |
  send_email(to=email_address, template=email_template)
  email_sent = True
---
question: |
  What is your e-mail address?
fields:
  - E-mail address: email_address
    datatype: email
---
template: email_template
subject: |
  Your signature needed
content: |
  [Click here](${ interview_url(i=user_info().package + ':second-interview.yml', c=redis_key, new_session=1) })
  to sign your name with a touchscreen device.
---
code: |
  need(r)
  import random
  import string
  redis_key = ''.join(random.choice(string.ascii_lowercase) for i in range(15))
  r.set_data(redis_key, 'waiting', expire=60*60*24)
---
event: final_screen
question: Your signature
subquestion: |
  ${ signature }
---
event: timeout_screen
question: |
  Sorry, you didn't sign in time.
buttons:
  - Restart: restart
---
prevent going back: True
event: waiting_screen
question: |
  Waiting for signature
subquestion: |
  Open your e-mail on a touchscreen device.

  You should get an e-mail soon asking you
  to provide a signature.  Click the link
  in the e-mail.
reload: 5
---
code: |
  result = r.get_data(redis_key)
  if result is None:
    del result
    timeout_screen
  elif result == 'waiting':
    del result
    waiting_screen
  signature = DAFile('signature')
  signature.initialize(filename="signature.png")
  signature.write(result, binary=True)
  signature.commit()
  r.delete(redis_key)
  signature_obtained = True
  del result
{% endhighlight %}

Second interview (referenced in the first as `second-interview.yml`):

{% highlight yaml %}
objects:
  - r: DARedis
---
mandatory: True
code: |
  signature_saved
  final_screen
---
code: |
  if 'c' not in url_args or r.get_data(url_args['c']) != 'waiting':
    message('Unauthorized', show_restart=False, show_exit=False)
  r.set_data(url_args['c'], signature.slurp(auto_decode=False), expire=600)
  signature_saved = True
---
question: Sign your name
signature: signature
---
prevent going back: True
event: final_screen
question: |
  Thanks!
subquestion: |
  You can now resume your interview.
{% endhighlight %}

# <a name="document signing"></a>Multi-user interview for getting a client's signature

This is an example of a multi-user interview where one person (e.g.,
an attorney) writes a document that they want a second person (e.g, a
client) to sign.  It is a multi-user interview (with [`multi_user`] set
to `True`).  The attorney inputs the attorney's e-mail address and
uploads a DOCX file containing:

> {% raw %}{{ signature }}{% endraw %}
{: .blockquote}

where the client's signature should go.  The attorney then receives a
hyperlink that the attorney can send to the client.

When the client clicks on the link, the client can read the unsigned
document, then agree to sign it, then sign it, then download the
signed document.  After the client signs the document, it is e-mailed
to the attorney's e-mail address.

{% highlight yaml %}
metadata:
  title: Signature
---
mandatory: True
code: |
  multi_user = True
---
mandatory: True
code: |
  multi_user = True
  signature = '(Your signature will go here)'
---
mandatory: True
code: |
  intro_seen
  email_address
  template_file
  notified_of_url
  agrees_to_sign
  signature_reset
  signature
  document_emailed
  final_screen
---
code: |
  notified_of_url = True
  prevent_going_back()
  force_ask('screen_with_link')
---
question: |
  What is your e-mail address?
subquestion: |
  The signed document will be e-mailed to this address.
fields:
  - E-mail: email_address
---
event: screen_with_link
question: |
  Share this link with the signer.
subquestion: |
  Suggested content for e-mailing to the signer:

  > I need you to sign a document.  You can
  > sign it using a touchscreen or with a
  > mouse.  To see the document and start
  > the signing process, [click here].

  [click here]: ${ interview_url() }
---
signature: signature
question: Sign your name
---
question: |
  Do you agree to sign this document?
subquestion: |
  Click the document image below to read the document
  before signing it.

  ${ draft_document.pdf }
field: agrees_to_sign
continue button label: I agree to sign
---
attachment:
  name: Document
  filename: signed_document
  variable name: draft_document
  docx template file:
    code: template_file
---
question: |
  Collect an electronic signature
subquestion: |
  If you provide your e-mail address and upload a document,
  you can get a link that you can give to someone, where
  they can click the link, sign their name, and then the
  signed document will be e-mailed to you.

  The document you upload needs to be in .docx format.

  In the place where you want the signature to be, you need to
  include the word "signature" surrounded by double curly brackets.
  For example:

  > I swear that the above is true and correct.
  >
  > {{ signature }}
  >
  > Angela Washington

  If you do not include "{{ signature }}" in exactly this way,
  a signature will not be inserted.
field: intro_seen
---
sets: template_file
question: |
  Unauthorized access
---
if: user_has_privilege(['admin', 'developer', 'advocate'])
question: |
  Please upload the document you want to be signed.
fields:
  - Document: template_file
    datatype: file
    accept: |
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
---
code: |
  del signature
  signature_reset = True
---
attachment:
  name: Document
  filename: signed_document
  variable name: signed_document
  valid formats:
    - pdf
  docx template file:
    code: template_file
---
event: final_screen
prevent going back: True
question: |
  Here is your signed document.
attachment code: signed_document
---
template: email_template
subject: Signed document
content: |
  The attached document has been signed.
---
code: |
  send_email(to=email_address, template=email_template, attachments=signed_document.pdf)
  document_emailed = True
{% endhighlight %}

[Here](https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/examples/signdoc.yml)
is a more complex version that handles multiple documents in Word
or PDF format and integrates with the Legal Server case management
system.  It requires login and expects the [Configuration] to contain
the Legal Server domain name in the directive `legal server domain`.

# <a name="upload validation"></a>Validating uploaded files

Here is an interview that makes the user upload a different file if
the file the user uploads is too large.

{% include demo-side-by-side.html demo="upload-file-size" %}

# <a name="mail merge"></a>Mail merge

Here is an example interview that assembles a document for every row
in a Google Sheet.

{% include demo-side-by-side.html demo="google-sheet-3" %}

# <a name="generic document"></a>Documents based on objects

This example is similar to the [mail merge example] in that it uses a
single template to create multiple documents.  In this case, however,
the same template is used to generate a document for two different
objects.

{% include demo-side-by-side.html demo="generic-document" %}

This makes use of the [`generic object` modifier].  The template file
[generic-document.docx] refers to the person using the variable `x`.

# <a name="docxproperties"></a>Altering metadata of generated DOCX files

This example demonstrates using the [docx] package to modify the
[core document properties] of a generated DOCX file.

{% include demo-side-by-side.html demo="docxproperties" %}

Note that this interview uses [Python] code in a [`code`] block that
should ideally go into a module file.  The `docx` variable is an
object from a third party module and is not able to be [pickled].  The
code works this way in this interview because the [`code`] block
ensures that the variable `user_name` is defined before the `docx`
variable is created, and it deletes the `docx` variable with `del
docx` before the [`code`] block finishes.  If the variable `user_name`
was undefined, **docassemble** would try to save the variable `docx`
in the interview answers before asking about `user_name`, and this
would result in a pickling error.  If the `docx` variable only existed
inside of a function in a module, there would be no problem with
[pickling].

# <a name="idle"></a>Log out a user who has been idle for too long

Create a static file called `idle.js` with the following contents.

{% highlight javascript %}
var idleTime = 0;
var idleInterval;
$(document).ready(function(){
    idleInterval = setInterval(idleTimerIncrement, 60000);
    $(document).mousemove(function (e) {
        idleTime = 0;
    });
    $(document).keypress(function (e) {
        idleTime = 0;
    });
});

function idleTimerIncrement() {
    idleTime = idleTime + 1;
    if (idleTime > 60){
        url_action_perform('log_user_out');
        clearInterval(idleInterval);
    }
}
{% endhighlight %}

In your interview, include `idle.js` in a [`features`] block and
include an `event: log_user_out` block that executes
`command('logout')`.

{% highlight yaml %}
features:
  javascript: idle.js
---
event: log_user_out
code: |
  command('logout')
---
mandatory: True
code: |
  welcome_screen_seen
  final_screen
---
question: |
  Welcome to the interview.
field: welcome_screen_seen
---
event: final_screen
question: |
  You are done with the interview.
{% endhighlight %}

This logs the user out after 60 minutes of inactivity in the browser.
To use a different number of minutes, edit the line
`if (idleTime > 60){`.

# <a name="background tail"></a>Seeing the progress of a running background task

Since [background tasks] run in a separate [Celery] process, there is
no simple way to get information from them while they are running.

However, [Redis] lists provide a helpful mechanism for keeping track
of log messages.

Here is an example that uses a [`DARedis`] object to store log
messages about a long-running [background task].  It uses [`check in`]
to poll the server for new log messages.

{% include demo-side-by-side.html demo="background-tail" %}

Since the task in this case (adding one number to another) is not
actually long-running, the interview uses `time.sleep()` to make it
artificially long-running.

# <a name="python to javascript"></a>Sending information from Python to JavaScript

If you use [JavaScript] in your interviews, and you want your
[JavaScript] to have knowledge about the interview answers, you can
use [`get_interview_variables()`], but it is slow because it uses
[Ajax].  If you only want a few pieces of information to be available
to your [JavaScript] code, there are a few methods you can use.

One method is to use the [`script` modifier].

{% include demo-side-by-side.html demo="pytojs-script" %}

Note that the variable is only guaranteed to be defined on the screen
showing the [`question`] that includes the [`script` modifier].  While
the value will persist from screen to screen, this is only because
screen loads use [Ajax] and the [JavaScript] variables are not cleared
out when a new screen loads.  But a browser refresh will clear the
[JavaScript] variables.

Another method is to use the `"javascript"` form of the [`log()`] function.

{% include demo-side-by-side.html demo="pytojs-log" %}

In this example, the [`log()`] function is called from a [`code`]
block that has [`initial`] set to `True`.  Thus, you can rely on the
`myColor` variable being defined on every screen of the interview
after `favorite_color` gets defined.

Another method is to pass the values of [Python] variables to the
browser using the [DOM], and then use [JavaScript] to retrieve the values.

{% include demo-side-by-side.html demo="pytojs-dom" %}

All of these methods are read-only.  If you want to be able to change
variables using [JavaScript], and also have the values saved to the
interview answers, you can insert `<input type="hidden">` elements
onto a page that has a "Continue" button.

{% include demo-side-by-side.html demo="pytojs-hidden" %}

This example uses the [`encode_name()`] function to convert the
variable name to the appropriate field name.  For more information on
manipulating the **docassemble** front end, see the section on [custom
front ends].  The example above works for easily for text fields, but
other data types will require more work.  Also, the example above only
works if the [Configuration] contains `restrict input variables: false`.

# <a name="ajax"></a>Running actions with Ajax

Here is an example of using [JavaScript] to run an action using [Ajax].

{% include demo-side-by-side.html demo="ajax" %}

The features used in this example include:

* [`action_button_html()`] to insert the HTML of a button.
* [Running Javascript at page load time] using the `daPageLoad` event.
* Setting an [`id`] and using the [CSS custom class] that results.
* [`flash()`] to flash a message at the top of the screen.
* [`action_call()`] to call an action using [Ajax].
* [`val()`] to obtain the value of a field on the screen using [JavaScript].
* [`set_save_status()`] to prevent the interview answers from being
  saved after an action completes.
* [`action_argument()`] to obtain the argument that was passed to [`action_call()`].
* [`json_response()`] to return [JSON] back to the web browser.

# <a name="collate"></a>Collating assembled and uploaded documents

Here is an interview that uses [`pdf_concatenate()`] to bring
assembled documents and user-provided documents in a single PDF file.

{% include demo-side-by-side.html demo="collate" %}

The Exhibit labeling sheets are generated by the template
[`exhibit_insert.docx`].

# <a name="stripe"></a>Payment processing with [Stripe]

First, sign up for a [Stripe] account.

From the dashboard, obtain your test API keys.  There are two keys: a
"publishable key" and a "secret key."  Put these into your
[Configuration] as follows:

{% highlight yaml %}
stripe public key: pk_test_ZjkQYPUU0pjQibxamUq28PlM00381Pd25e
stripe secret key: sk_test_YW41CYyivW0Vo7EN0mFD5i4P01ZLeQAPS8
{% endhighlight %}

The `stripe public key` is the "publishable key."  The `stripe secret
key` is the "secret key."

Confirm that you have the `stripe` package installed by checking the
list of packages under "Package Management".  If `stripe` is not
listed, follow the directions for [installing a package].  `stripe` is
available on [PyPI].

Create a Python module called `dastripe.py` with the following contents:

{% highlight python %}
import stripe
import json
from docassemble.base.util import word, get_config, action_argument, DAObject, prevent_going_back
from docassemble.base.standardformatter import BUTTON_STYLE, BUTTON_CLASS

stripe.api_key = get_config('stripe secret key')

__all__ = ['DAStripe']

class DAStripe(DAObject):
  def init(self, *pargs, **kwargs):
    if get_config('stripe public key') is None or get_config('stripe secret key') is None:
      raise Exception("In order to use a DAStripe object, you need to set stripe public key and stripe secret key in your Configuration.")
    super().init(*pargs, **kwargs)
    if not hasattr(self, 'button_label'):
      self.button_label = "Pay"
    if not hasattr(self, 'button_color'):
      self.button_color = "primary"
    if not hasattr(self, 'error_message'):
      self.error_message = "Please try another payment method."
    self.is_setup = False

  def setup(self):
    float(self.amount)
    str(self.currency)
    self.intent = stripe.PaymentIntent.create(
      amount=int(float('%.2f' % float(self.amount))*100.0),
      currency=str(self.currency),
    )
    self.is_setup = True

  @property
  def html(self):
    if not self.is_setup:
      self.setup()
    return """\
<div id="stripe-card-element" class="mt-2"></div>
<div id="stripe-card-errors" class="mt-2 mb-2 text-alert" role="alert"></div>
<button class="btn """ + BUTTON_STYLE + self.button_color + " " + BUTTON_CLASS + '"' + """ id="stripe-submit">""" + word(self.button_label) + """</button>"""

  @property
  def javascript(self):
    if not self.is_setup:
      self.setup()
    billing_details = dict()
    try:
      billing_details['name'] = str(self.payor)
    except:
      pass
    address = dict()
    try:
      address['postal_code'] = self.payor.billing_address.zip
    except:
      pass
    try:
      address['line1'] = self.payor.billing_address.address
      address['line2'] = self.payor.billing_address.formatted_unit()
      address['city'] = self.payor.billing_address.city
      if hasattr(self.payor.billing_address, 'country'):
        address['country'] = address.billing_country
      else:
        address['country'] = 'US'
    except:
      pass
    if len(address):
      billing_details['address'] = address
    try:
      billing_details['email'] = self.payor.email
    except:
      pass
    try:
      billing_details['phone'] = self.payor.phone_number
    except:
      pass
    return """\
<script>
  var stripe = Stripe(""" + json.dumps(get_config('stripe public key')) + """);
  var elements = stripe.elements();
  var style = {
    base: {
      color: "#32325d",
    }
  };
  var card = elements.create("card", { style: style });
  card.mount("#stripe-card-element");
  card.addEventListener('change', ({error}) => {
    const displayError = document.getElementById('stripe-card-errors');
    if (error) {
      displayError.textContent = error.message;
    } else {
      displayError.textContent = '';
    }
  });
  var submitButton = document.getElementById('stripe-submit');
  submitButton.addEventListener('click', function(ev) {
    stripe.confirmCardPayment(""" + json.dumps(self.intent.client_secret) + """, {
      payment_method: {
        card: card,
        billing_details: """ + json.dumps(billing_details) + """
      }
    }).then(function(result) {
      if (result.error) {
        flash(result.error.message + "  " + """ + json.dumps(word(self.error_message)) + """, "danger");
      } else {
        if (result.paymentIntent.status === 'succeeded') {
          action_perform(""" + json.dumps(self.instanceName + '.success') + """, {result: result})
        }
      }
    });
  });
</script>
    """
  @property
  def paid(self):
    if not self.is_setup:
      self.setup()
    if hasattr(self, "payment_successful") and self.payment_successful:
      return True
    if not hasattr(self, 'result'):
      self.demand
    payment_status = stripe.PaymentIntent.retrieve(self.intent.id)
    if payment_status.amount_received == self.intent.amount:
      self.payment_successful = True
      return True
    return False
  def process(self):
    self.result = action_argument('result')
    self.paid
    prevent_going_back()
{% endhighlight %}

Create an interview [YAML] file (called, e.g., `teststripe.yml`) with
the following contents:

{% highlight yaml %}
modules:
  - .dastripe
---
features:
  javascript: https://js.stripe.com/v3/
---
objects:
  - payment: DAStripe.using(payor=client, currency='usd')
  - client: Individual
  - client.billing_address: Address
---
mandatory: True
code: |
  # Payor information may be required for some payment methods.
  client.name.first
  # client.billing_address.address
  # client.phone_number
  # client.email
  if not payment.paid:
    payment_screen
  favorite_fruit
  final_screen
---
question: |
  What is your name?
fields:
  - First: client.name.first
  - Last: client.name.last
---
question: |
  What is your phone number?
fields:
  - Phone: client.phone_number
---
question: |
  What is your e-mail address?
fields:
  - Phone: client.email
---
question: |
  What is your billing address?
fields:
  - Address: client.billing_address.address
    address autocomplete: True
  - Unit: client.billing_address.unit
    required: False
  - City: client.billing_address.city
  - State: client.billing_address.state
    code: states_list()
  - Zip: client.billing_address.zip
---
question: |
  How much do you want to pay?
fields:
  - Amount: payment.amount
    datatype: currency
---
event: payment.demand
question: |
  Payment
subquestion: |
  You need to pay up.  Enter your credit card information here.

  ${ payment.html }
script: |
  ${ payment.javascript }
---
event: payment.success
code: |
  payment.process()
---
question: |
  What is your favorite fruit?
fields:
  - Fruit: favorite_fruit
---
event: final_screen
question: Your favorite fruit
subquestion: |
  It is my considered opinion
  that your favorite fruit is
  ${ favorite_fruit }.
{% endhighlight %}

Test the interview with a [testing card number] and adapt it to your
particular use case.

The attributes of the `DAStripe` object (known as `payment` in this
example) that can be set are:

* `payment.currency`: this is the currency that the payment will use.
  Set this to `'usd'` for U.S. dollars.  See [supported accounts and
  settlement currencies] for information about which currencies are
  available.
* `payment.payor`: this contains information about the person who is
  paying.  You can set this to an [`Individual`] or [`Person`] with a
  `.billing_address` (an [`Address`]), a name, a `.phone_number`, and an
  `.email`.  This information will not be sought through dependency
  satisfaction; it will only be used if it exists.  Thus, if you want
  to send this information (which may be required for the payment to
  go through), make sure your interview logic gathers it.
* `payment.amount`: the amount of the payment to be made, in whatever
  currency you are using for the payment.
* `payment.button_label`: the label for the "Pay" button.  The default
  is "Pay."
* `payment.button_color`: the Bootstrap color for the "Pay" button.
  The default is `primary`.
* `payment.error_message`: the error message that the user will see at
  the top of the screen if the credit card is not accepted.  The
  default is "Please try another payment method."

The attribute `.paid` returns `True` if the payment has been made or
`False` if it has not.  It also triggers the payment process.  If
`payment.amount` is not known, it will be sought.

The user is asked for their credit card information on a "special
screen" tagged with `event: request.demand`.  The variable
`request.demand` is sought behind the scenes when the interview logic
evaluates `request.paid`.

The `request.demand` page needs to include `${ payment.html }` in the
`subquestion` and `${ payment.javascript }` in the `script`.  The
JavaScript produced by `${ payment.javascript }` assumes that the file
`https://js.stripe.com/v3/` has been loaded in the browser already;
this can be accomplished through a `features` block containing a
`javascript` reference.

The "Pay" button is labeled "Pay" by default, but this can be
customized with the `request.button_label` attribute.  This value is
passed through `word()`, so you can use the `words` translation system
to translate it.

If the payment is not successful, the user will see the error message
reported by [Stripe], followed by the value of
`request.error_message`, which is `'Please try another payment
method.'` by default.  The value of `request.error_message` is passed
through `word()`, so you can use the `words` translation system to
translate it.

If the payment is successful, the JavaScript on the page performs the
`request.success` "action" in the interview.  Your interview needs to
provide a `code` block that handles this action.  The action needs to
call `payment.process()`.  This will save the data returned by
[Stripe] and will also call the [Stripe] API to verify that payment
was actually made.  The `code` block for the "action" will run to the
end, so the next thing it will do is evaluate the normal interview
logic.  When `request.paid` is encountered, it will evaluate to `True`.

The [Stripe] API is only called once to verify that the payment was
actually made.  Subsequent evaluations of `request.paid` will return
`True` immediately without calling the API again.

Thus, the interview logic for the process of requiring a payment is
just two lines of code:

{% highlight python %}
if not payment.paid:
  payment_screen
{% endhighlight %}

Payment processing is a very complicated subject, so this recipe
should only be considered a starting point.  The advantage of this
design is that it keeps a lot of the complexity of payment processing
out of the interview [YAML] and hides it in the module.

If you want to have the billing address on the same screen where the
credit card number is entered, you could use custom HTML forms, or a
`fields` block in which the `Continue` button is hidden.

When you are satisfied that your payment process work correctly, you
can set your `stripe public key` and `stripe secret key` to your
"live" [Stripe] API keys on your production server.

# <a name="formio"></a>Integration with form.io, AWS Lambda, and the **docassemble** API

This recipe shows how you can set up [form.io] to send a webhook
request to an [AWS Lambda] function, which in turn calls the
**docassemble** [API] to start an interview session, inject data into
the interview answers of the session, and then send a notification to
someone to let them know that a session has been started.

On your server, create the following interview, calling it `fromformio.yml`.

{% highlight yaml %}
mandatory: True
code: |
  multi_user = True
---
code: |
  start_data = None
---
mandatory: |
  start_data is not None
code: |
  send_email(to='jpyle@docassemble.org', template=start_of_session)
---
template: start_of_session
subject: Session started
content: |
  A session has started.  [Go to it now](${ interview_url() }).
---
mandatory: True
question: |
  The start_data is:

  `${ repr(start_data) }`
{% endhighlight %}

Create an [AWS Lambda] function and trigger it with an HTTP REST API
that is authenticated with an API key.

![AWS Lambda]({{ site.baseurl }}/img/formio03.png){: .maybe-full-width }

![AWS Lambda API key]({{ site.baseurl }}/img/formio04.png){: .maybe-full-width }

Add a layer that provides the `requests` module.  Then write a
function like the following.

![lambda function code]({{ site.baseurl }}/img/formio06.png){: .maybe-full-width }

{% highlight python %}
import json
import os
import requests

def lambda_handler(event, context):
    try:
        start_data = json.loads(event['body'])
    except:
        return { 'statusCode': 400, 'body': json.dumps('Could not read JSON from the HTTP body') }
    key = os.environ['daapikey']
    root = os.environ['baseurl']
    i = os.environ['interview']
    r = requests.get(root + '/api/session/new', params={'key': key, 'i': i})
    if r.status_code != 200:
        return { 'statusCode': 400, 'body': json.dumps('Error creating new session at ' + root + '/api/session/new')}
    session = r.json()['session']
    r = requests.post(root + '/api/session', data={'key': key,
                                                   'i': i,
                                                   'session': session,
                                                   'variables': json.dumps({'start_data': start_data, 'event_data': event}),
                                                   'question': '1'})
    if r.status_code != 200:
        return { 'statusCode': 400, 'body': json.dumps('Error writing data to new session')}
    return { 'statusCode': 204, 'body': ''}
{% endhighlight %}

Set the environment variables so that your provide the function with
an API key for the **docassemble** [API] (which you can set up in your
Profile), the URL of your server, and the name of the interview you
want to run (in this case, `fromformio.yml` is a Playground
interview).

![AWS Lambda]({{ site.baseurl }}/img/formio07.png){: .maybe-full-width }

Go to [form.io] and create a form that looks like this:

![form.io form]({{ site.baseurl }}/img/formio01.png){: .maybe-full-width }

Attach a "webhook" action that sends a POST request to your [AWS
Lambda] endpoint.  Add the API key for the HTTP REST API trigger as
the `x-api-key` header.

![form.io action]({{ site.baseurl }}/img/formio02.png){: .maybe-full-width }

Under Forms, click the "Use" button next to the form that you created
and try submitting the form.  The e-mail recipient designated in your
YAML code should receive an e-mail containing the text:

> A session has started. Go to it now.
{: .blockquote}

where "Go to it now" is a hyperlink to an interview session.  When the
e-mail recipient clicks the link, they will resume an interview
session in which the variable `start_data` contains the information
from the [form.io] form.

![interview session]({{ site.baseurl }}/img/formio08.png){: .maybe-full-width }

# <a name="object_conversion"></a>Converting the result of object questions

When you gather objects using [`datatype: object_checkboxes`] or one
of the other object-based data types, you might not want the variable
you are setting to use object references.  You can use the
[`validation code`] feature to apply a transformation to the variable
you are defining.

{% include demo-side-by-side.html demo="object-checkboxes-copy" %}

The result is that the `fruit_preferences` objects are copies of the
original `fruit_data` object and have separate `instanceName`s.

# <a name="repeatable"></a>Repeatable session with defaults

If you want to restart an interview session and use the answers from
the just-finished session as default values for the new session, you
can accomplish this using the [`depends on`] feature.

{% include demo-side-by-side.html demo="repeatable" %}

When the variable `counter` is incremented by the `new_version`
[action], all of the variables set by [`question`] blocks that use
`depends on: counter` will be undefined, but the old values will be
remembered and offered as defaults when the [`question`] blocks are
encountered again.

# <a name="universal"></a>Universal document assembler

Here is an example of using the [catchall questions] feature to
provide an interview that can ask questions to define arbitrary
variables that are referenced in a document.

{% include demo-side-by-side.html demo="universal-document" %}

For security purposes, this example interview requires `admin` or
`developer` privileges.  You can find the source [on GitHub](https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/examples/universal-document.yml) and try it
out on your own server.

# <a name="adust_language_for_second_or_third_person"></a>Adjust Language for Second or Third Person

You may want to have a single interview that can be used either by a
person for themselves, or by a person who is assisting another person.
In the following example, there is an object named `client` that is of
the type [`Individual`].  The variable `user_is_client` indicates
whether the user is the client, or the user is assisting a third
party.

Here is the text of the question and subquestion written in second
person:

```
question: |
  Should your attorney be compensated for out-of-pocket expenses
  out of your property?
subquestion: |
  Your attorney may incur expenses in administering your property.
  If you allow your attorney to be compensated for out-of-pocket
  expenses out of your property, that may make the attorney's life
  easier.

  Do you want your attorney to be compensated for out-of-pocket
  expenses out of your property?
yesno: should_be_compensated
```

Here is how you might convert that text so that it will work properly
if the user is the client, or if the client is someone else:

```
initial: True
code: |
  if user_is_client:
    set_info(user=client)
---
question: |
  Should ${ client.possessive('attorney') } be compensated for
  out-of-pocket expenses out of ${ client.possessive('property') }?
subquestion: |
  ${ client.possessive('attorney', capitalize=True) }
  may incur expenses in administering
  ${ client.pronoun_possessive('property') }.
  If
  ${ client.subject() }
  ${ client.does_verb("allow") }
  ${ client.pronoun_possessive('attorney') }
  to be compensated for out-of-pocket expenses out of
  ${ client.pronoun_possessive('property') },
  that may make the attorney's life easier.

  ${ client.do_question('want', capitalize=True) }
  ${ client.pronoun_possessive('attorney') }
  to be compensated for out-of-pocket expenses out of
  ${ client.pronoun_possessive('property') }?
yesno: should_be_compensated
```

This one block can now do two different things, and is still
relatively readable.

## Possessives

The first mention of the client in the sentence should use the client's
name. If the first mention of the client in the sentence is possessive,
you should use `${ client.possessive('object') }` to generate either
"Client Name's object" or "your object".

## Capitalization

Any of the language functions can be modified with `capitalize=True` if
they are being used at the start of a sentence.

# <a name="read before signing"></a>Allow user to read a document before signing it

This interview uses [`depends on`] to force the reassembly of a
document after the user has viewed a draft version with a "sign here"
sticker in place of the signature.

{% include demo-side-by-side.html demo="signature-preview" %}

# <a name="multisignature"></a>Gathering multiple signatures on a document

This interview sends a document out for signature to an arbitrary
number of signers, and then e-mails the document to the signers
when all signatures have been provided.

{% include demo-side-by-side.html demo="demo-multi-sign" %}

This interview uses [`include`] to bring in the contents of
[`docassemble.demo:data/questions/sign.yml`].  This [YAML] file
disables server-side encryption by setting [`multi_user`] to `True`,
and loads the `SigningProcess` class from the
[`docassemble.demo.sign`] module.  The object `sign`, an instance of
`SigningProcess`, controls the gathering and display of signatures.
Note the way signatures and the dates of signatures are included in
the DOCX template file, [declaration_of_favorite_fruit.docx]:

![Declaration of Favorite Fruit]({{ site.baseurl }}/img/declaration-favorite-fruit.png){: .maybe-full-width }

The template uses methods on the `sign` object to include the
signature images and dates.  To include a signature of an [`Individual`]
or [`Person`] called `the_person`, you would call
`sign.signature_of(the_person)`.  To include the date when the person
signed, you would call `sign.signature_date_of(the_person)`.

Note also the way that a line is placed underneath the signature
image: on the line following the reference to
`sign.signature_of(user)`, there is an empty table with a top
border and no other borders.

The interview gathers the user's name, the user's e-mail address, and
the names and e-mail addresses of one or more witnesses.

When the interview logic calls `sign.out_for_signature()`, this
triggers the following process:

1. In a background process, e-mails are sent to the user and the
   witnesses with a hyperlink they can click on to sign the document.
2. The hyperlink was created by `interview_url_action()` using the
   [action] name `sign.request_signature` and an [action] argument
   called `code` that contains a special code that identifies who the
   signer is.
3. When the signer clicks the hyperlink, they join the interview
   session and the [action] is run, and the [action] calls
   `force_ask()` to set up a series of screens that signer should see.
   First the signer agrees to sign, then the signer signs, and then
   the signer sees a "thank you" screen on which the signer can
   download the document containing their signature.
4. When all of the signatures have been collected, e-mails are sent to
   the signers attaching the final signed document.

The `sign.signature_of(the_person)` method is smart; it will return the empty
string `''` if `the_person` has not signed yet, and it will return the
person's signature if `the_person` has signed.  Similarly,
`sign.signature_date_of(the_person)` returns a line of underscores if
the person has not signed yet, and otherwise returns a `DADateTime`
object containing the date when the person signed.  Specifically, when
the person has not signed yet, the methods return a [`DAEmpty`]
object.  This means you can safely write
`sign.signature_of(the_person).show(width='1in')` or
`sign.signature_date_of(the_person).format('yyyy-MM-dd')` and the
method will still return the empty string or a line of underscores.

In this example, only one document, `statement`, is assembled.  When
you initialize a `SigningProcess` object, you could specify more than
one document.  For example, instead of `documents='statement'`, you
could write `documents=['statement', 'certificate_of_service']`.  Then
the system would send out two documents for signature.

{% include demo-side-by-side.html demo="demo-multi-sign-2" %}

Note that `documents` refers not to the actual variables `statement`
and `certificate_of_service`, but to the variables as text:
`'statement'` and `'certificate_of_service'`.  This is important; if
you were to write `documents=statement` or `documents=[statement,
certificate_of_service]`, you would get an error.  It is necessary to
refer to the documents using text references because the document
itself contains references to `sign`, and if `sign` could not be
defined until `statement` was defined, that would be a Catch-22.

The `SigningProcess` object knows who the signers are because of the
calls to `sign.signature_of()` and `sign.signature_date_of()` that
were made while the document was being assembled.  Therefore, you
don't have to explicitly state who needs to sign the document; you can
use logic in your document to determine who the signers are.

Note that in the `attachment code` part of the final `question`, it
refers to `sign.list_of_documents(refresh=True)` instead of
`statement`.  This is important because the underlying document is
constantly changing as the signatures are added.  Calling
`sign.list_of_documents(refresh=True)` will re-assemble the document
and then return `[statement]` (the `statement` document inside a
Python list).  The `list_of_documents()` method simply returns a list of
[`DAFileCollection`] objects.

The signing process is customizable.  The [`sign.yml`] file, which is
included at the top of the interview [YAML] file above, contains
default [`template`] and [`question`] blocks that you can override in
your own [YAML].  For example, the default content for the initial
e-mail to a signer is:

{% highlight yaml %}
generic object: SigningProcess
template: x.initial_notification_email[i]
subject: |
  Your signature needed on
  ${ x.singular_or_plural('a document', 'documents') }:
  ${ x.documents_name() }
content: |
  ${ x.signer(i) },

  Your signature is requested on
  % if x.number_of_documents() == 1:
  a document called
  ${ x.documents_name() }.
  % else:
  the following
  ${ x.singular_or_plural('document', 'documents') }:

  % for document in x.list_of_documents():
  * ${ document.info['name'] }
  % endfor
  % endif

  To sign, [click here].

  If you are willing to sign this document, please do so
  in the next ${ nice_number(x.deadline_days) } days.
  If you do not sign by
  ${ today().plus(days=x.deadline_days) }, the above link
  will expire.

  [click here]: ${ x.url(i) }
{% endhighlight %}

You can overwrite this by including the following rule in your own
[YAML], which will take precedence over the above rule.

{% highlight yaml %}
template: sign.initial_notification_email[i]
subject: |
  Please sign the Declaration of Favorite Fruit for ${ user }.
content: |
  ${ sign.signer(i) },

  I would greatly appreciate it if you would sign the
  Declaration of Favorite Fruit for ${ user } by
  [clicking here](${ sign.url(i) }).

  If you are not willing to sign, please
  call me at 555-555-2929.
{% endhighlight %}

For more information about what templates are used, see the
[`sign.yml`] file.  Some of the blocks in this file define `action`s;
do not try to modify these unless you are sure you know what you are
doing.

The methods of the `SigningProcess` object that you might use are as
follows.

`sign.out_for_signature()` initiates the signing process.  It is safe
to run this more than once.  If the signing process has already been
started, the method will not do anything.

`sign.signer(i)` is usually invoked in a `template` in a context where
`i` is a code that uniquely identifies the signer.  It returns the
signer as an object.

`sign.url(i)` is also used inside of `template` blocks.  It returns
the link that a signer should click on in order to join the interview
and sign the document or documents.

`sign.list_of_documents()` returns the assembled documents as a list
of [`DAFileCollection`] objects.  If the optional keyword parameter
`refresh` is set to `True`, then the documents will be re-assembled
before they are returned.

`sign.number_of_documents()` returns the number of documents as an
integer.

`sign.singular_or_plural()` is useful when writing `template`s.  The
first argument is what should be returned if there is one document.
The second argument is what should be returned if there are multiple
documents.

`sign.documents_name()` will return a `comma_and_list()` of the names
of the documents.

`sign.has_signed(the_signer)` will return `True` if `the_signer` has
signed the document yet, and otherwise will return `False`.

`sign.all_signatures_in()` will return `True` if all of the signers
have signed, and otherwise will return `False`.

`sign.list_of_signers()` will return a `DAList()` of the signers.
`sign.number_of_signers()` will return the number of signers as an
integer.  `sign.signers_who_signed()` will return the subset who have
signed, and `sign.signers_who_did_not_sign()` will return the subset
who have not yet signed.

The methods `sign.signature_of(the_signer)` and
`sign.signature_date_of(the_signer)` are discussed above.  These are
typically used inside of documents.

There is also the method `sign.signature_datetime_of(the_signer)`,
which returns a `DADateTime` object representing the exact time the
signer's signature was recorded.  There is also the method
`sign.signature_ip_address_of(the_signer)`, which returns the IP
address the signer was using.  The IP address, along with the date and
time, are widely used ingredients of digital signatures.

`sign.sign_for(the_signer, the_signer.signature)` will insert a
signature manually, where `the_signer` is a person whose signature is
referenced in the document, using the `signature_of()` method, and
`the_signer.signature` is a variable defined by a [`signature`] block
(a [`DAFile`] object).  Note that if this method is called more than
once, each new time the date of the signature will be updated.  You
may want to avoid this by doing:

{% highlight python %}
if not sign.has_signed(the_signer):
  sign.sign_for(the_signer, the_signer.signature)
{% endhighlight %}

Then this code can safely be called more than once without changing
the date of the signature.

Calling `sign.refresh_documents()` will generate fresh copies of the
documents.  (It uses the [`reconsider()`] function.)

Note that in the [`sign.yml`] file, the [`signature`] block uses
`validation code` that calls `x.validate_signature(i)`.  This is
important because it performs the additional tasks necessary to record
the signature, such as recording the IP address.  You will probably
not need to call `validate_signature()` outside of this context; the
`sign_for()` method calls `validate_signature()` for you.

# <a name="phonenumber"></a>Validating international phone numbers

Here is a simple way to validate international phone numbers.

{% include demo-side-by-side.html demo="phone-number" %}

Here is a way to validate international phone numbers using a single screen.

{% include demo-side-by-side.html demo="phone-number-2" %}

# <a name="customdate"></a>Customizing the date input

If you don't like the way that web browsers implement date inputs, you
can customize the way dates are displayed.

{% include demo-side-by-side.html demo="customdate" %}

This interview uses a [JavaScript] file [`datereplace.js`].  The
[JavaScript] converts a regular date input element into a hidden
element and then adds name-less elements to the [DOM].  This approach
preserves default values.

# <a name="side processes"></a>Running side processes outside of the interview logic

Normally, the order of questions in a **docassemble** interview is
determined by the interview logic: questions are asked to obtain the
definitions of undefined variables, and the interview ends when all
the necessary variables have been defined.

Sometimes, however, you might want to send the user through a logical
process that is not driven by the need to definitions of undefined
variables.  For example, you might want to:

* Ask a series of questions again to make sure the user has a second
  chance to get the answers right;
* Ask the user specific follow-up questions after the user makes an
  edit to an answer.
* Give the user the option of going through a process one or more
  times.

The following interview is an example of the latter.  At the end of
the interview logic, the user has the option of pressing a button in
order to go through a repeatable multi-step process that contains
conditional logic.

{% include demo-side-by-side.html demo="courtfile" %}

This takes advantage of an important feature of [`force_ask()`].  If
you give [`force_ask()`] a variable and there is no question in the
interview [YAML] that can be asked in order to define that variable,
then [`force_ask()`] will ignore that variable.  The call to
[`force_ask()`] lists all of the questions that might be asked in the
process, and the [`if`] modifiers are used to indicate under what
conditions the questions should be asked.

# <a name="passing"></a>Passing variables from one interview session to another

Using [`create_session()`], [`set_session_variables()`], and
[`interview_url()`], you can start a user in one session, collect
information, and then initiate a new session, write variables into the
interview answers of that session, and direct the user to that session.

{% include demo-side-by-side.html demo="stage-one" %}

The interview that the user is directed to is the following.

{% include demo-side-by-side.html demo="stage-two" %}

Note that when the user starts the session in the second interview,
the interview already knows the object `user` and already knows the
value of `favorite_fruit`.

# <a name="basic"></a>Making generic questions customizable

If you have a lot of questions in your interviews that are very
similar, such as questions that ask for names and addresses, you might
want to create a YAML file that contains [`generic object`]
questions and then include that YAML file in all of your interviews.
This is a way to ensure consistency across your interviews without
having to maintain the same information in multiple places across your
YAML files.

Having a common set of [`generic object`] questions does not inhibit
your ability to customize [`question`] blocks when you need to; you
can always override the [`generic object`] question with a more
specific question if you would like to ask a question a different way
if you have a special case.

It is also possible to customize your [`generic object`] questions
without overriding.  This recipe demonstrates a method of designing
[`generic object`] questions that allows for the customization of
specific details of questions.

Here is an example of an interview that gathers names, e-mail
addresses, and addresses of three [`Individual`]s while relying
entirely on [`generic object`] questions to gather the information.

{% include demo-side-by-side.html demo="demo-with-basic-questions" %}

The interview starts by including [`demo-basic-questions.yml`].  This
is a parent YAML file for including other YAML files.  Its full
contents are:

{% highlight yaml %}
include:
  - demo-basic-questions-name.yml
  - demo-basic-questions-address.yml
{% endhighlight %}

The contents of [`demo-basic-questions-name.yml`] are as follows.

{% highlight yaml %}
generic object: Individual
question: |
  ${ x.ask_name_template.subject }
subquestion: |
  ${ x.ask_name_template.content }
fields:
  - First name: x.name.first
    required: x.first_name_required
    show if:
      code: x.name.uses_parts
    default: ${ x.name.default_first }
  - Middle name: x.name.middle
    required: x.middle_name_required
    show if:
      code: x.name.uses_parts and x.ask_middle_name
    default: ${ x.name.default_middle }
  - Last name: x.name.last
    required: x.last_name_required
    show if:
      code: x.name.uses_parts
    default: ${ x.name.default_last }
  - Name: x.name.text
    show if:
      code: not x.name.uses_parts
  - E-mail: x.email
    datatype: email
    required: x.email_required
    show if:
      code: x.ask_email_with_name
---
generic object: Individual
question: |
  ${ x.ask_email_template.subject }
subquestion: |
  ${ x.ask_email_template.content }
fields:
  - E-mail: x.email
    datatype: email
---
generic object: Individual
template: x.ask_name_template
subject: |
  % if get_info('user') is x:
  What is your name?
  % else:
  What is the name of ${ x.description }?
  % endif
content: ""
---
generic object: Individual
if: x.ask_email_with_name
template: x.ask_name_template
subject: |
  % if x is get_info('user'):
  What is your name and e-mail address?
  % else:
  What is the name and e-mail address of ${ x.description }?
  % endif
content: ""
---
generic object: Individual
template: x.ask_email_template
subject: |
  % if x is get_info('user'):
  What is your e-mail address?
  % else:
  What is the e-mail address of ${ x.description }?
  % endif
content: ""
---
generic object: Individual
code: |
  x.description = x.object_name()
---
generic object: Individual
code: |
  if user_logged_in() and user_info().first_name:
    x.name.default_first = user_info().first_name
  else:
    x.name.default_first = ''
---
generic object: Individual
code: |
  if user_logged_in() and user_info().last_name:
    x.name.default_last = user_info().last_name
  else:
    x.name.default_last = ''
---
generic object: Individual
code: |
  x.name.default_middle = ''
---
generic object: Individual
code: |
  x.first_name_required = True
---
generic object: Individual
code: |
  x.last_name_required = True
---
generic object: Individual
code: |
  x.email_required = True
---
generic object: Individual
code: |
  x.ask_middle_name = False
---
generic object: Individual
code: |
  x.middle_name_required = False
---
generic object: Individual
code: |
  x.ask_email_with_name = False
{% endhighlight %}

The contents of [`demo-basic-questions-address.yml`] are as follows.

{% highlight yaml %}
generic object: Individual
question: |
  ${ x.ask_address_template.subject }
subquestion: |
  ${ x.ask_address_template.content }
fields:
  - "Street address": x.address.address
    address autocomplete: True
  - 'Unit': x.address.unit
    required: x.address_unit_required
  - 'City': x.address.city
  - 'State': x.address.state
    code: states_list()
  - 'Zip code': x.address.zip
    required: x.address_zip_code_required
---
if: x.ask_about_homelessness
generic object: Individual
question: |
  ${ x.ask_address_template.subject }
subquestion: |
  ${ x.ask_address_template.content }
fields:
  - label: |
      % if get_info('user') is x:
      I am
      % else:
      ${ x } is
      % endif
      experiencing homelessness.
    field: x.address.homeless
    datatype: yesno
  - "Street address": x.address.address
    address autocomplete: True
    hide if: x.address.homeless
  - 'Unit': x.address.unit
    required: x.address_unit_required
    hide if: x.address.homeless
  - 'City': x.address.city
  - 'State': x.address.state
    code: states_list()
  - 'Zip code': x.address.zip
    required: x.address_zip_code_required
    hide if: x.address.homeless
---
generic object: Individual
template: x.ask_address_template
subject: |
  % if get_info('user') is x:
  Where do you live?
  % else:
  What is the address of ${ x }?
  % endif
content: ""
---
generic object: Individual
code: |
  x.address_zip_code_required = True
---
generic object: Individual
code: |
  x.address_unit_required = False
---
generic object: Individual
code: |
  x.ask_about_homelessness = False
{% endhighlight %}

Note that all of the blocks in these YAML files are [`generic object`]
blocks.  There are  [`question`] blocks that define questions to be
used.  These [`question`] blocks make reference to a lot of different
object attributes that function as "settings."  After the [`question`]
blocks, there are [`template`] blocks and [`code`] blocks that
set default values for these settings.

This means that in your own interviews, you have the option of
overriding any of those settings simply by including a block that
sets a value for one of the settings.  For example, the default value
of the `.ask_about_homelessness` attriute is `False`, but in the
example interview, this was overridden for the object `client`:

{% highlight yaml %}
code: |
  client.ask_about_homelessness = True
{% endhighlight %}

Note the strategies that are being used in the
[`demo-basic-questions-name.yml`] file and the
[`demo-basic-questions-address.yml`] file to provide a variety of
options for the ways that questions are asked:

* Using [`template`]s to specify the `question` and `subquestion`
  text, using the `subject` part and the `content` part of the
  template.  Alternatively, you could use separate templates for the
  `question` and `subquestion`, so that your interviews could override
  the `question` part without overriding the `subquestion` part, and
  vice-versa.
* Specifying multiple [`question`] blocks and using the [`if`]
  modifier to choose which one is applicable, depending on the values
  of "settings."
* Using the `code` variant of [`show if`] to select or deselect fields
  in a list of fields, depending on the values of settings.

When making use of these strategies, make sure you understand [how
**docassemble** finds questions for variables].

# <a name="preview"></a>Showing a partial preview of document assembly

This example uses the `[TARGET]`
[feature]({{ site.baseurl }}/docs/background.html#target)
to show a document assembly preview in the `right` portion of the
screen that continually updates as the user enters information into
fields.

{% include demo-side-by-side.html demo="preview" %}

# <a name="exceldb"></a>Using a spreadsheet as a database for looking up information

If you have a table of information and you want to be able to look
things up in that table of information during your interview, one of
the ways you can accomplish this is by keeping the information in a
spreadsheet in the Source folder of your package.  Python can be used
to read the spreadsheet and look up information in it.

The [`fruit_database` module] uses the [`pandas`] module to read an
XLSX spreadsheet file into memory.  The `get_fruit_names()` function
returns a list of fruits (from the "Name" column) and the
`fruit_info()` function returns a dictionary of information about a
given fruit.

{% include demo-side-by-side.html demo="fruits-database" %}

Note that the interview does not simply import the
`fruit_info_by_name` dictionary into the interview answers.  Although
technically you can import dictionaries, lists, and other Python data
types into your interview, doing so is generally not a good idea
because those values will then become part of the interview answers
that are stored in the database for every step of the interview.  This
wastes hard drive space and it also wastes time re-loading the data
out of your module every time the screen loads.  It is a best practice
to use helper functions like `get_fruit_names()` and `fruit_info()` to
bring in information on an as-needed basis.

If your database is particularly large, reading it into memory may not
be a good idea.  You might want to rewrite the functions so that they
read information out of the file on an as-needed basis.  You also
might want to adapt the functions to read data from a Google Sheet or
Airtable rather than from an Excel spreadsheet that is part of your package.

# <a name="docxongd"></a>Using a template that lives on Google Drive

When you use the [`docx template file`] or [`pdf template file`]
features to assemble documents, your document templates are typically
located in the Templates folder of your package, and you refer to
templates by their file names.  However, the [`docx template file`] or
[`pdf template file`] specifiers [can be given] `code` instead of a
filename.  Your template could be a [`DAFile`] object.

You can use this feature to retrieve templates from Google Drive.
There is a convenient [Python] package called [`googledrivedownloader`]
that allows you to download a file from Google Drive based on its ID.
The following example demonstrates how to use this in a document
assembly interview:

{% include demo-side-by-side.html demo="realtimegd" %}

It is necessary that the sharing settings on the file in Google Drive
be set so that "anyone with the link" can view the file.  In this
example, the Google Drive file is a DOCX file with [this sharing
link](https://docs.google.com/document/d/1MsiAA632Ehyj0jEW_WEBpZOd-qokqyni/edit?usp=sharing&ouid=118246287503150138684&rtpof=true&sd=true). The
ID of the file on Google Drive is
`'1MsiAA632Ehyj0jEW_WEBpZOd-qokqyni'`.  This ID can be seen inside of
the URL, before the query part (the part beginning with `?`).

If you wish to use a file on Google Drive without creating a link that
anyone in the world can view, you can use the [`DAGoogleAPI`] object,
which allows you to use Google's API with [service account]
credentials that are stored in the [Configuration] under [`service
account credentials`] within the [`google`] directive.

This example uses a Google Drive file with the id of
`'1IGvzA-oOB_bVTmDB7TPW9UgQT-6MGtSe'`.  This file is not accessible
via a link; it is shared only with the special e-mail address of the
[service account].

{% include demo-side-by-side.html demo="realtimegd2" %}

This interview uses a Python module [`docassemble.demo.gd_fetch`],
which provides a function called `fetch_file()`, which downloads a
file from Google Drive.

{% highlight python %}
from docassemble.base.util import DAGoogleAPI
import apiclient

__all__ = ['fetch_file']

def fetch_file(file_id, path):
    service = DAGoogleAPI().drive_service()
    with open(path, 'wb') as fh:
        response = service.files().get_media(fileId=file_id)
        downloader = apiclient.http.MediaIoBaseDownload(fh, response)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
{% endhighlight %}

The `fetch_file()` function retrieves the file with the given
`file_id` from Google Drive, using Google's API, and then saves the
contents of the file to `path`, which is a file path.

The Python module `apiclient` provides the interface to Google's API.
`apiclient` is the name of the module contained in the
[`google-api-python-client`] package.  The `fetch_file()` function
uses a [`DAGoogleAPI`] object to get authentication credentials from
the [Configuration].  All that `.drive_service()` does is:

{% highlight python %}
apiclient.discovery.build('drive', 'v3', http=self.http('https://www.googleapis.com/auth/drive'))
{% endhighlight %}

On the server `demo.docassemble.org`, the [Configuration] contains
credentials for a Google service account, and the Google Drive file
`'1IGvzA-oOB_bVTmDB7TPW9UgQT-6MGtSe'` has been shared with that
service account.

Although it is convenient for document templates to be stored in
Google Drive instead of inside of a package, keep in mind that there
are risks to storing templates on Google Drive.  If you have a
production interview that uses your template from Google Drive, and
you edit the template in such a way that it causes an error (for
example, a Jinja2 syntax error), your users will start seeing errors
immediately.  It would be better if you only released a new version of
a template as part of a process that involves testing and validating
your changes to a template.  Another issue is that you are opening up
a back door for code injection.  If someone has edit access to the
template on Google Drive, they could potentially find a way to use
Jinja2 to execute arbitrary Python code on your server.  Templates are
a form of software, so ideally they should live where the other
software lives, which is inside of a software package.

# <a name="language selector"></a>Changing the language using the navigation bar

This example interview provides the user with a language selector
interface in the navigation bar.  It uses [`default screen parts`] to
set the [`navigation bar html`], which is a [screen part] inside of a
`<ul class="nav navbar-nav">` element in the navigation bar.

{% include demo-side-by-side.html demo="navbar-language" %}

Note that [`default screen parts`] is used instead of [`metadata`] so
that [Mako] can be used.  The [`url_of()`] function is used to insert
the URL of an image into the `src` attribute of an `<img>` element.

The [action] that changes the language uses [`set_save_status()`] to
prevent language switches from introducing a step in the interview
process.

For more information about **docassemble**'s support for multi-lingual
interviews, see the [Language Support] section.

# <a name="stats"></a>Tracking statistics about user activity

Redis has a convenient feature for incrementing a counter.  Since the
data in [Redis] is not affected by the deletion of interview sessions
or users pressing the Back button, [Redis] can be used to keep track
of event counters.  The following interview uses a [`DARedis`] object
to access [Redis] and increment counters that track how many times
particular screens in an interview were reached.

{% include demo-side-by-side.html demo="counter" %}

When you retrieve data from Redis, it comes through as non-decoded
binary data, so you have to decode it with `.decode()`.

Note that `r.incr()` was not called inside the
`mandatory`<span></span> `code` block.  If it had been, then the
counters for the early parts of the interview would be repeatedly
incremented every time the screen loaded.  Using the `milestone`
dictionary to track whether the milestone has been reached ensures
that the counters are not incremented duplicatively.

# <a name="headless"></a>Headless document assembly

If you want to use the document assembly features of **docassemble**
without the user interface, you can use the API to drive a "headless"
interview.

For example, you could use an interview like this:

{% highlight yaml %}
mandatory: True
code: |
  json_response(the_document.pdf.number)
---
attachment:
  variable name: the_document
  content: |
    Your favorite fruit is ${ favorite_fruit }.
{% endhighlight %}

Then you could drive the interview with the API using code like this:

{% highlight python %}
root = 'https://docassemble.myhostname.com/api'
headers = {'X-API-Key': 'XXXSECRETAPIKEYXXX'}
username = 'jsmith'
password = 'xxxsecretpasswordxxx'
i = 'docassemble.mypackage:data/questions/headless.yml'

r = requests.get(root + '/secret', params={'username': username, 'password': password}, headers=headers)
if r.status_code != 200:
    sys.exit(r.text)
secret = r.json()

r = requests.get(root + '/session/new', params={'secret': secret, 'i': i}, headers=headers)
if r.status_code != 200:
    sys.exit(r.text)
session = r.json()['session']

r = requests.post(root + '/session', json={'secret': secret, 'i': i, 'session': session, 'variables': {'favorite_fruit': 'apple'}}, headers=headers)
if r.status_code != 200:
    sys.exit(r.text)
file_number = r.json()

r = requests.get(root + '/file/' + str(file_number), params={'i': i, 'session': session, 'secret': secret}, headers=headers)
if r.status_code != 200:
    sys.exit(r.text)
with open('the_file.pdf', 'wb') as fp:
    fp.write(r.content)
{% endhighlight %}

# <a name="json index"></a>Building a database for reporting

If you want to be able to run reports on variables in interview
sessions, calling `interview_list()` may be too inefficient because
unpickling the interview answers of a large quantity of interview
sessions is computationally intensive.

The [`store_variables_snapshot()`] function allows you to save
variable values to a dictionary in a PostgreSQL database. This
database can be the the standard database where interview answers are
stored ([`db`]) or a different database ([`variables snapshot
db`]). You can then write queries that use [JSONB] to access the
variables in the dictionary.

Here is an example of a module, [`index.py`], that uses
[`store_variables_snapshot()`] to create a database that lets you run
reports showing the names of users along with when they started and
stopped their interviews.

{% highlight python %}
import json
from docassemble.base.util import store_variables_snapshot, DAObject, user_info, start_time, variables_snapshot_connect

__all__ = ['MyIndex']

class MyIndex(DAObject):
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        if not hasattr(self, 'data'):
            self.data = {}
        if not hasattr(self, 'key'):
            self.key = 'myindex'
    def save(self):
        data = dict(self.data)
        data['session'] = user_info().session
        data['filename'] = user_info().filename
        data['start_time'] = start_time().astimezone()
        store_variables_snapshot(data, key=self.key)
    def set(self, data):
        if not isinstance(data, dict):
            raise Exception("MyIndex.set: data parameter must be a dictionary")
        self.data = data
        self.save()
    def update(self, new_data):
        self.data.update(new_data)
        self.save()
    def report(self, filter_by=None, order_by=None):
        if filter_by is None:
            filter_string = ''
        else:
            filter_string = ' and ' + filter_by
        if order_by is None:
            order_string = ''
        else:
            order_string = ' order by ' + order_by
        with variables_snapshot_connect() as conn:
            with conn.cursor() as cur:
                cur.execute("select data from jsonstorage where tags='" + self.key + "'" + filter_string + order_string)
                results = [record[0] for record in cur.fetchall()]
        return results

{% endhighlight %}

Here is an example of an interview that uses a `MyIndex` object to
store information about each interview in JSON storage.

{% include demo-side-by-side.html demo="indexdemo" %}

Note that the `index` object is defined in a `mandatory` block. This
ensures that the `index` object exists before the [`on change`] code
runs. Code that runs inside of [`on change`] cannot encounter any
undefined variables.

To run a query on the data, you can do something like this:

{% include demo-side-by-side.html demo="indexdemoquery" %}

# <a name="flask page"></a>Building a custom page with Flask

**docassemble** is a [Flask] application, which means that web
endpoints can be added simply by declaring a function that uses the
[Flask] `route` decorator.

Here is an example of a Python module that, when installed on a
**docassemble** server, enables `/hello` as a GET endpoint.

{% highlight python %}
# pre-load

from docassemble.webapp.app_object import app
from flask import render_template_string
from markupsafe import Markup

@app.route('/hello', methods=['GET'])
def hello_endpoint():
    content = """\
{% raw %}{% extends "base_templates/base.html" %}{% endraw %}

{% raw %}{% block main %}{% endraw %}
<div class="row">
  <div class="col">
    <h1>Hello, {% raw %}{{ planet }}{% endraw %}!</h1>

    <p>Modi velit ut aut delectus alias nisi a. Animi
    in rerum quia error et. Adipisci dolores occaecati
    quasi veniam aliquid asperiores sint sint. Aliquid
    veritatis qui autem quo laborum. Enim et repellendus
    sed sed quasi.</p>
  </div>
</div>
{% raw %}{% endblock %}{% endraw %}
"""
    return render_template_string(
        content,
        bodyclass='daadminbody',
        title='Hello world',
        tab_title='Hello tab',
        page_title='Hello there',
        extra_css=Markup('\n    <!-- put your link href="" stuff here -->'),
        extra_js=Markup('\n    <!-- put your script src="" stuff here -->'),
        planet='world')
{% endhighlight %}

This example uses the `base_templates/base.html` Jinja2 template,
which is the default template for pages in **docassemble**. Using this
template allows you to create a page that uses the same look-and-feel
and the same metadata as other pages of the **docassemble** app. Note
that the keyword arguments to `render_template_string()` define
variables that the `base_templates/base.html` uses. You can customize
different parts of the page by setting these values. The exception is
`planet`, which is a variable that is used in the HTML for the
`/hello` page. Note that in order to insert raw HTML using keyword
parameters, you need to use the `Markup()` function.

[Flask] only permits one template folder, and the template folder in
the **docassemble** app is the one in `docassemble.webapp`. This
cannot be changed. However, you can provide a complete HTML page to
`render_template_string()` if you do not want to use a template.

The line `# pre-load` at the top of the module is important. This
ensures that the module will be loaded when the server starts. Note
that it is important not to load multiple modules that contain a
definition of the same endpoint; if you do, [Flask] will give an
error. You may need to use the [`module blacklist`] Configuration
directive to avoid this.

The root endpoint `/` already has a definition in
`docassemble.webapp.server`, but you can tell the server to redirect
requests from `/` to a custom endpoint that you create.

{% highlight yaml %}
root redirect url: /hello
{% endhighlight %}

You might want to use this technique to host your own web site on
various endpoints of the **docassemble** server and then incorporate
**docassemble** interviews using a `<div>` or an `<iframe>`. This
avoids problems with CORS that might otherwise interfere with
embedding.

# <a name="custom api"></a>Building a custom API endpoint with Flask

Much as you can create a custom page in the web application using
Flask, you can create a custom API endpoint.

Here is an example of a Python module that, when installed on a
**docassemble** server, enables `/create_prepopulate` as a POST
endpoint. This endpoint creates a session in an interview indicated by
the URL parameter `i`, and then prepopulates variables in the
interview answers using the POST data. This might be useful in a
situation where you want to combine multiple API calls into one.

{% highlight python %}
# pre-load
from flask import request, jsonify
from flask_cors import cross_origin
from docassemble.base.util import create_session, set_session_variables, interview_url
from docassemble.webapp.app_object import app, csrf
from docassemble.webapp.server import api_verify, jsonify_with_status

@app.route('/create_prepopulate', methods=['POST'])
@csrf.exempt
@cross_origin(origins='*', methods=['POST', 'HEAD'], automatic_options=True)
def create_prepopulate():
    if not api_verify():
        return jsonify_with_status({"success": "False", "error_message": "Access denied."}, 403)
    post_data = request.get_json(silent=True)
    if post_data is None:
        post_data = request.form.copy()
    if 'i' not in request.args:
        return jsonify_with_status({"success": False, "error_message": "No 'i' specified in URL parameters."}, 400)
    session_id = create_session(request.args['i'])
    if len(post_data):
        set_session_variables(request.args['i'], session_id, post_data, overwrite=True, process_objects=False)
    url = interview_url(i=request.args['i'], session=session_id, style='short_package', temporary=90*24*60*60)
    return jsonify({"success": True, "url": url})
{% endhighlight %}

The `api_verify()` function handles authentication using
**docassemble**'s API key system, and it logs in the owner of the API
key, so that subsequent Python code will run with the permissions of
that user. Note that the code in an API endpoint does not run in the
context of a **docassemble** interview session, so there are many
functions that you cannot call because they depend on that context

The POST data may be in `application/json` or
`application/x-www-form-urlencoded` format.

The line `# pre-load` at the top of the module is important. This
ensures that the module will be loaded when the server starts. Note
that it is important not to load multiple modules that contain a
definition of the same endpoint; if you do, [Flask] will give an
error. You may need to use the [`module blacklist`] Configuration
directive to avoid this.

## <a name="custom api background"></a>Running background tasks from endpoints

**docassemble** has a [background tasks] system that can be called
from inside of interview logic. The [`background_action()`] function
cannot be called from a custom endpoint, however, because it
depends upon the interview logic context.

In order to run background tasks from a custom endpoint, you need to
interface with [Celery] directly.

First, you need to create a `.py` file that defines Celery task
functions. In this example, the file is `custombg.py` in the
`docassemble.mypackage` package:

{% highlight python %}
# do not pre-load
from docassemble.webapp.worker_common import workerapp, bg_context, worker_controller as wc


@workerapp.task
def custom_add_four(operand):
    return operand + 4


@workerapp.task
def custom_comma_and_list(*pargs):
    with bg_context():
        return wc.util.comma_and_list(*pargs)
{% endhighlight %}

The first line, `# do not pre-load`, is important. This file should
not be loaded as an ordinary Python module. Instead, it should be
loaded using the [`celery modules`] directive:

{% highlight yaml %}
celery modules:
  - docassemble.mypackage.custombg
{% endhighlight %}

The [`celery modules`] directive ensures that the module will be
loaded at the correct time and in the correct context.

Then create a second Python file containing the code for your [Flask]
endpoints. The following file is `testcustombg.py` in the
`docassemble.mypackage` package.

{% highlight python %}
from flask import request, jsonify
from flask_cors import cross_origin
from docassemble.webapp.app_object import app, csrf
from docassemble.webapp.server import api_verify, jsonify_with_status
from docassemble.webapp.worker_common import workerapp
from docassemble.base.config import in_celery
if not in_celery:
    from docassemble.mypackage.custombg import custom_add_four, custom_comma_and_list


@app.route('/api/start_process', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def start_process():
    if not api_verify():
        return jsonify_with_status({"success": False, "error_message": "Access denied."}, 403)
    try:
        operand = int(request.args['operand'])
    except:
        return jsonify_with_status({"success": False, "error_message": "Missing or invalid operand."}, 400)
    task = custom_add_four.delay(operand)
    return jsonify({"success": True, 'task_id': task.id})


@app.route('/api/start_process_2', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def start_process_2():
    if not api_verify():
        return jsonify_with_status({"success": False, "error_message": "Access denied."}, 403)
    task = custom_comma_and_list.delay('foo', 'bar', 'foobar')
    return jsonify({"success": True, 'task_id': task.id})


@app.route('/api/poll_for_result', methods=['GET'])
@csrf.exempt
@cross_origin(origins='*', methods=['GET', 'HEAD'], automatic_options=True)
def poll_for_result():
    if not api_verify():
        return jsonify_with_status({"success": False, "error_message": "Access denied."}, 403)
    try:
        result = workerapp.AsyncResult(id=request.args['task_id'])
    except:
        return jsonify_with_status({"success": False, "error_message": "Invalid task_id."}, 400)
    if not result.ready():
        return jsonify({"success": True, "ready": False})
    if result.failed():
        return jsonify({"success": False, "ready": True})
    return jsonify({"success": True, "ready": True, "answer": result.get()})
{% endhighlight %}

To prevent a circularity in module loading, it is important to refrain
from importing the background task module,
`docassemble.mypackage.custombg`, into this module if `in_celery` is
true (meaning that [Celery] rather than the web application is loading
the `docassemble.mypackage.custombg` module). Although this creates a
situation where `custom_add_four` and `custom_comma_and_list` are
undefined when `in_celery` is true, this does not matter because the
code for your endpoints will never be called by [Celery].

The `custom_add_four` and `custom_comma_and_list` functions are called
in the standard [Celery] fashion. See the [Celery] documentation for
more information about using [Celery].

The `testcustombg.py` file above demonstrates how you can create
separate API endpoints for starting a long-running process and polling
for its result.

# <a name="screen parts"></a>Synchronizing screen parts with interview answers

If you run multiple sessions in the same interview and you want to be
able to keep sessions organized on the My Interviews page, you might
want to use [`set_parts()`] to dynamically change the interview title
or subtitle. You can use `metadata` to set default values of `title`
or `subtitle` that will apply when the user first starts the
interview. Then after the user answers certain questions, you can call
`set_parts()` to change the `title` or `subtitle`. That way, when you
go to the My Interviews page, you will be able to tell your sessions
apart.

This example uses [`on change`] to trigger calls to [`set_parts()`]
when a variable changes. Although you could also call [`set_parts()`]
in your ordinary interview logic, using `on change` is helpful because
if you allow the user to make changes to variables in a `review`
screen, you don't need to worry about making sure that [`set_parts()`]
gets called again.

{% include demo-side-by-side.html demo="setparts" %}

# <a name="watermark"></a>Inserting a watermark when using Markdown to PDF

If you are using the Markdown-to-PDF document assembly method and you
want the resulting PDF documents to bear a [watermark] on each page,
you can use the [`draftwatermark`] package in [LaTeX] to place an
image in the center of each page. This package is not enabled by
default in the [default LaTeX template] or its [default metadata], so
you need to tell **docassemble** to load it in the preamble of the
`.tex` file. The [default LaTeX template] allows you to add your own
lines to the preamble of the `.tex` file by setting the
`header-includes` metadata variable to a list of lines.

{% include demo-side-by-side.html demo="watermark" %}

Another [LaTeX] package that does something similar is [`background`].

# <a name="calendar"></a>E-mailing a calendar invite

If you install the [`ics`] package, you can send calendar invites
using [`send_email()`].

{% include demo-side-by-side.html demo="calendar" %}

This interview uses the module file [`calendar.py`], which imports
the [`ics`] package.

# <a name="duplicate"></a>Duplicating a session

This example shows to use `create_session()`,
`set_session_variables()`, and `all_variables()` to create a new
session pre-populated with variables from the current session.

Note that there are hidden variables (stored in the `_internal`
variable) that pertain to the session that can be carried
over. Copying over all of them is usually not a good idea, but some of
them can be transferred. This example copies `answered` and `answers`,
which keep track of which `mandatory` blocks have been completed and
what the answers to [multiple-choice
questions](https://docassemble.org/docs/fields.html#code%20button)
are. The `device_local` and `user_local` hidden variables are also
copied. The `starttime` and `referer` variables are not copied over,
but they could be. This example does not copy over data about any
current "actions" in progress (`event_stack`).

{% include demo-side-by-side.html demo="duplicate" %}

# <a name="nested"></a>A table in a DOCX file that uses a list nested in a dictionary

This example illustrates how to use a [`docx template file`] and
[Jinja2] to construct a table in a DOCX file that contains a list
nested in a dictionary, with a total and subtotals. The template file
is [`nested_list_table.docx`].

{% include demo-side-by-side.html demo="nested-list-docx-table" %}

# <a name="graph"></a>Generating a graph and inserting it into a document

This interview uses the [`matplotlib`] library (which is not installed
by default on a **docassemble** server) to generate a pie chart based
on user-supplied input.

{% include demo-side-by-side.html demo="graph" %}

The bulk of the work is done in the [`graph.py`] module, the contents
of which are as follows.

{% highlight python %}
__all__ = ['make_pie']

import matplotlib.pyplot as plt

def make_pie(data, the_file):
    the_file.initialize(filename='graph.svg')
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

    labels = list(data.keys())
    fracs = list(data.values())

    pies = ax.pie(fracs, labels=labels, autopct='%1.1f%%')
    with open(the_file.path(), 'wb') as f:
        plt.savefig(f, format="svg")
    the_file.commit()
    the_file.retrieve()
{% endhighlight %}

The document template, [`graph.docx`], inserts the `DAFile` object `graph`.

# <a name="button checkboxes"></a>Restyling checkboxes as buttons

CSS is a very powerful tool for customizing the user interface. Here
is an example that replaces **docassemble**'s standard checkboxes with
buttons that are grey when unselected and red when selected

{% include demo-side-by-side.html demo="button-checkboxes" %}

The transformation is done by the [`button-checkboxes.css`] file.

# <a name="continuation"></a>Adding a continuation page to a PDF form

If you have a PDF form that only allows a few lines for a list of
things, you can conditionally generate a continuation page. Here is
one way to do it.

{% include demo-side-by-side.html demo="continuation-page" %}

# <a name="upload exhibits"></a>Editing a `DAFileList` of file uploads

If you allow your users to "edit" a file upload by sending them back
to the `question` with the `datatype: file` or `datatype: files`
field, the only way they can "edit" the upload is by re-uploading a
new file or a new set of files. The value of the `DAFileList` is
simply replaced. This is because `datatype: files` and `datatype:
file` produce an `<input type="file">` HTML element, which is
incapable of having a default value.

To allow the user to edit a file upload, you can instead send them to
a `question` that lets them see the files they have uploaded, delete
particular ones, reorder the files, and add additional files.

{% include demo-side-by-side.html demo="upload-handler-demo" %}

In this example, the file [`upload-handler.yml`] defines rules that
apply to any `DAFileList` (the blocks use `generic object:
DAFileList`). The complicated part is the `validation code` on the
`question` that sets `x[i]`. Without this, the `DAFileList` `x` would
be a list of `DAFileList` objects rather than a list of `DAFile`
objects.

Note that the interview requires a definition of
`exhibits.verified`. This is important; if your interview doesn't have
logic that seeks out the `.verified` attribute, the user will not see
the screens that allow them to edit the list of uploaded files.

This recipe requires **docassemble** version 1.4.73 or higher.

# <a name="js show if yesnomaybe"></a>Using `js show if` with `yesnomaybe`

Here is an example of using `js show if` with `datatype: yesnomaybe`.

{% include demo-side-by-side.html demo="jsshowifmaybe" %}

# <a name="inside_of_class"></a>A subclass of Individual that reduces to text differently depending on the context

Normally, when you reduce an object of class `Individual` to text, the
result is the same as when you call `.name.full()` on the
object. You can make a subclass of `Individual` that reduces to text
in a different way.

Here is an example module that uses `current_context().inside_of` to
detect whether the object representing an individual is being reduced
to text inside of a document that is being assembled. If it is, the
`.name_full()` name is returned, but if the object is being reduced to
text for purposes of displaying in the web app, the first name is
returned.

{% highlight python %}
from docassemble.base.util import current_context, Individual, log

__all__ = ['AltIndividual']


class AltIndividual(Individual):

    def __str__(self):
        if current_context().inside_of != 'standard':
            return self.name.full()
        return self.name.familiar()
{% endhighlight %}

Here is an interview that demonstrates the use of the `AltIndividual`
class.

{% include demo-side-by-side.html demo="new-or-existing" %}

# <a name="access"></a>Controlling access to interviews

You can control access to interviews using the username/password
system, and you can use the [`require login`] and [`required
privileges`].

If you already have a username/password system on another
web site, and you don't want users to have to log in twice, there are
ways around this:
* If both your other site and your **docassemble** side use the same
  social sign-on system, like Azure, the login process can be fairly
  transparent.
* Your other site could synchronize the usernames and passwords
  between your other site and the **docassemble** site. The
  **docassemble** API allows for creating users, deleting users, and
  changing their passwords.
* Your users can use the **docassemble** site without logging in to
  the **docassemble** site. Your interviews can control access and
  identify the user through a different means.

To make an interview non-public, you can put something like this at the top of the interview:

{% highlight yaml %}
mandatory: True
code: |
  authorized = False
  multi_user = True
---
initial: True
code: |
  if not authorized:
    command('exit', url="https://example.com/login")
  process_action()
{% endhighlight %}

If a random person on the internet tries to access the docassemble
interview through a URL, they will be immediately redirected. A new
session will be created, but it will immediately be deleted by
the operation of `command('exit')`.

Meanwhile, users of your web site will be able to use interview
sessions that your site creates for them. Your site can call the
following [API] endpoints:

* [`/api/session/new` GET endpoint]: this creates a new session in an
  interview with the filename `i`. A `session` ID is returned.
* [`/api/session` POST endpoint]: this defines variables in the
interview answers of a session identified by `i` and `session`. For
example, using the `session` ID it obtained by calling the previous
endpoint, your site could call the [`/api/session` POST endpoint] with
`variables` set to `{'authorized': true}`.

Now you can direct the user to the URL
`https://da.example.com/interview?i=docassemble.mypackage:data/questions/myinterview.yml&session=afj32vnf23wjfhf2393d928j39d8j`
or, equivalently, `https://da.example.com/run/mypackage/myinterview/?session=afj32vnf23wjfhf2393d928j39d8j`.

The session that the user resumes will have the variable `authorized`
set to `True` and thus the user will not be redirected away. The
session code is the security mechanism.

At the same time that your site defines `authorized` as `True`, it
could also define variables such as the user's email address, or a
unique ID for the user's account on your site. These might be useful
to have in an interview.

There are other strategies for authentication without login. For
example, you could use to use the [API] to [stash] data in
**docassemble**, and then direct the user to an interview with a link
like
`https://da.example.com/start/mypackage/myinterview/?k=AFJI23FJOIJ239FASD2&s=IRUWJR2389EFIJW2333`
where `AFJI23FJOIJ239FASD2` and `IRUWJR2389EFIJW2333` are the
`stash_key` and the `secret` returned by the [`/api/stash_data`]
endpoint. Your interview logic could retrieve these values from the
`url_args` and then use [`retrieve_stashed_data()`] to obtain the
data.

{% highlight yaml %}
mandatory: True
code: |
  if 'k' not in url_args or 's' not in url_args:
    command('exit', url="https://example.com/login")
  data = retrieve_stashed_data(url_args['k'], url_args['s'])
  if not data:
    command('exit', url="https://example.com/login")
  user_name = data['user_name']
scan for variables: False
---
initial: True
code: |
  process_action()
{% endhighlight %}

The interview can commence only if `k` and `s` are present in the URL
parameters, and only if they are valid. When you [stash] the data you
can set a time period after which the data will be automatically
deleted.

This method has the advantage that it does not require using
`multi_user = True`. However, if the user does not log in to the
**docassemble** site, the user will not be able to resume an encrypted
session if `multi_user` is not set to `True`.

# <a name="openai"></a>Using the OpenAI API

You can use generative AI as a tool in a **docassemble** interview.

Here is an example that uses the [`openai`] Python package to
communicate with the [OpenAI Platform].

Prerequisites:

* On the Package Management page, install the `openai` Python
  package. (If you are developing a package, make sure that `openai` is
  a dependency.)
* In the [OpenAI Platform], create an account, enter a payment method,
  and obtain an API key.
* Put the API key into your Configuration under `openai key`.

Create this module in your Playground or in your package, calling it
`chatbot.py`:

{% highlight python %}
import openai
from docassemble.base.util import get_config, DAObject

openai.api_key = get_config('openai key')


class Conversation(DAObject):

    def init(self, *pargs, **kwargs):
        self.conversation = []
        super().init(*pargs, **kwargs)

    def ask(self, prompt):
        self.conversation.append({"role": "user", "content": prompt})
        completion = openai.chat.completions.create(
            model="gpt-5",
            messages=self.conversation
        )
        response = completion.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": response})
        return response
{% endhighlight %}

Then create an interview with the following contents, calling it
`chatbot.yml`:

{% highlight yaml %}
modules:
  - .chatbot
---
objects:
  - name_address: Conversation
  - user: Individual
---
mandatory: True
code: |
  bot_response = name_address.ask("""Pretend that you are a polite, helpful \
  chatbot called Freddy and I am someone living in the United States who is \
  asking you for help. Ask me for my name and address. You need my name and \
  address so that you can help me. Make sure I give you both my first name \
  and my last name. Once I give you my full name and address, your response \
  should be solely a JSON object containing the keys first_name, last_name, \
  street_address, city, and state. If I change the subject of conversation \
  to something other than my name and address, or smalltalk, your response \
  should be solely a JSON object {"error": "True"}. Start pretending \
  immediately.""")
---
mandatory: True
code: |
  while True:
    bot_response = name_address.ask(prompt)
    try:
      address = json.loads(bot_response)
      assert isinstance(address, dict) and \
      ('error' in address or 'first_name' in address)
      break
    except:
      pass
    del prompt
---
mandatory: True
code: |
  if not address.get("error", False):
    user.name.first = address.get('first_name', '')
    user.name.last = address.get('last_name', '')
    user.address.address = address.get('street_address', '')
    user.address.city = address.get('city', '')
    user.address.state = address.get('state', '')
  del address
---
mandatory: True
question: |
  Your name and address
subquestion: |
  % if user.name.defined():
  ${ user.address_block() }
  % else:
  You failed to cooperate.
  % endif
---
question: |
  Freddy, a chatbot
subquestion: |
  ${ bot_response }
fields:
  - no label: prompt
    datatype: area

{% endhighlight %}

As you can see, interfacing with the OpenAI API requires very little
code. The `conversation` attribute of the `Conversation` object is a
`list` such as:

{% highlight python %}
[
  {"role": "user", "content": "What is the capital of Argentina?"},
  {"role": "assistant", "content": "Buenos Aires, the capital of Argentina, is the country's economic and political centre."},
  {"role": "user", "content": "What is the most popular food there? Answer in one word."}
]
{% endhighlight %}

Each time the OpenAI API is called, the `list` with the whole
conversation is passed to the API. Whatever the API returns is then
appended to the list as a `dict` like `{"role": "assistant", "content": "Asado"}`.
The OpenAI server does not remember the context of the
conversation. Each request it receives from the **docassemble** server
is new. ChatGPT understands the context of the conversation
because the whole conversation is provided to the API each time.

In this example, the initial instruction tells ChatGPT to respond with
pure JSON when the conversation reaches a stopping point. The
interview logic detects whether the response is a JSON object by
trying to parse the response as JSON. As a safety measure, ChatGPT is
instructed to respond with a JSON object if the user changes the
subject of conversation.

The JSON that ChatGPT returns is then used to populate variables in
the interview answers

In this manner, you can use generative AI to replace `question` blocks
with a conversational interface, while still achieving the same end
goal of populating the interview answers with specific pieces of
information.

The `question` that is shown during the conversation is:

{% highlight yaml %}
question: |
  Freddy, a chatbot
subquestion: |
  ${ bot_response }
fields:
  - no label: prompt
    datatype: area
{% endhighlight %}

This `question` defines `prompt` if `prompt` is undefined. It requires
`bot_response` to be defined.

The interview logic that causes this `question` to be shown repeatedly
to the user is:

{% highlight yaml %}
mandatory: True
code: |
  bot_response = name_address.ask(initial_prompt)
---
mandatory: True
code: |
  while True:
    bot_response = name_address.ask(prompt)
    try:
      address = json.loads(bot_response)
      assert isinstance(address, dict) and \
      ('error' in address or 'first_name' in address)
      break
    except:
      pass
    del prompt
{% endhighlight %}

In the first block, the initial `bot_response` is obtained, which is
some type of greeting from ChatGPT, after ChatGPT has been given
instructions about how to behave.

Once `bot_response` is defined initially in the first `code` block,
that `code` block is not run again because it is `mandatory` and it
has run to completion. Now the second `code` block will run every time
the screen loads, until it runs to completion without raising an
exception.

The second `code` block is a loop; the `while True` means that the
code inside will continue to run indefinitely. The first thing the
code tries to do inside the loop is `bot_response =
name_address.ask(prompt)`. However, `prompt` is undefined, so an
undefined variable exception is raised (leaving `bot_response`
unchanged) and **docassemble** asks the question that defines
`prompt`. Thus, the user sees the above `question` where
`bot_response` is the welcome message that ChatGPT came up with after
being instructed to pretend to be a chatbot. The user then provides a
`prompt`, and this `code` block executes again, because it is
`mandatory` and has not run to completion. Now, `prompt` is defined,
so `bot_response` is defined by the `.ask()` method. Then the code
tries to parse the response as JSON. The `json.loads()` method will
return an exception if the response is not JSON. If the response is
JSON, the `assert` command will raise an `AssertionError` if the data
structure is not expected. (This is unlikely to happen, but perhaps a
clever user could trick ChatGPT into responding with arbitrary valid
JSON.) If the JSON was expected, then `break` terminates the `while
True` loop, and the `mandatory` block will not run again, since it
runs to completion. However, if an exception is raised, then the
exception is trapped, `pass` does nothing, `prompt` is undefined, and
then the loop goes back to the beginning. The user sees the new
`bot_response` and can respond to another iteration of the
conversation.

The next `mandatory`<span> </span>`code` block takes the
ChatGPT-generated JSON and populates variabes in the interview answers
as a result.

{% highlight yaml %}
mandatory: True
code: |
  if not address.get("error", False):
    user.name.first = address.get('first_name', '')
    user.name.last = address.get('last_name', '')
    user.address.address = address.get('street_address', '')
    user.address.city = address.get('city', '')
    user.address.state = address.get('state', '')
  del address
{% endhighlight %}

Note that the code tries to adjust for every eventuality. Maybe the
response was the signal that the user changed the subject. Maybe
ChatGPT failed to return a complete JSON object with all of the
requested keys. The code defaults to populating the empty string if
something is missing.

You can use multiple `Conversation` objects in the same interview,
each one of which fulfills a particular mission.

In this example, the `.ask()` method of the `Conversation` object is
called in a loop, because the conversation could have any number of
iterations. You could also use `Conversation` objects in the
background that only have a prompt and a response. For example:

{% highlight yaml %}
modules:
  - .chatbot
---
objects:
  - q: Conversation
---
question: |
  In what state were you injured?
fields:
  - State: state
    code: states_list()
---
code: |
  years = int(q.ask(f"""Generally, how many years is the statute of \
  limitations for tort actions in the state of {state_name(state)}? \
  Answer only with digits 0-9, and no punctuation."""))
---
mandatory: True
question: |
  You have ${ quantity_noun(years, "year") } to bring a claim.
{% endhighlight %}

Note that the ChatGPT API is slow. If your server has a lot of
traffic, calling the ChatGPT API in the foreground may cause your
server to become unresponsive.

Calling the OpenAI API in the background is possible. For example,
create a Python module `chatbot_bg.py` with the following contents:

{% highlight python %}
import openai
from docassemble.base.util import get_config, DAObject, background_action

openai.api_key = get_config('openai key')


class Conversation(DAObject):

    def init(self, *pargs, **kwargs):
        self.conversation = []
        self.stage = 0
        super().init(*pargs, **kwargs)

    def fg_ask(self, prompt):
        self.conversation.append({"role": "user", "content": prompt})
        completion = openai.chat.completions.create(
            model="gpt-5",
            messages=self.conversation
        )
        response = completion.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": response})
        return response

    def ask(self, prompt):
        if self.stage == 0:
            self.bg_action = background_action(self.attr_name('bg_ask'), prompt=prompt)
            self.stage = 1
            self.wait
        if self.stage == 1:
            if not self.bg_action.ready():
                self.wait
            response = self.bg_action.get()
            self.conversation.append({"role": "user", "content": prompt})
            self.conversation.append({"role": "assistant", "content": response})
            self.stage = 0
            del self.bg_action
            return response
        return "error"
{% endhighlight %}

Then create a YAML interview file called `chatbot-bg.yml` with the
following contents:

{% highlight yaml %}
modules:
  - .chatbot_bg
---
generic object: Conversation
event: x.bg_ask
code: |
  background_response(x.fg_ask(action_argument('prompt')))
---
generic object: Conversation
event: x.wait
question: |
  Please wait . . .
reload: 5
{% endhighlight %}

Then create a YAML file for testing this system, called
`chatbot-slow.yml`:

{% highlight yaml %}
include:
  - chatbot-bg.yml
---
objects:
  - name_address: Conversation
  - user: Individual
---
mandatory: True
code: |
  bot_response = name_address.ask("""Pretend that you are a polite, helpful \
  chatbot called Freddy and I am someone living in the United States who is \
  asking you for help. Ask me for my name and address. You need my name and \
  address so that you can help me. Make sure I give you both my first name \
  and my last name. Once I give you my full name and address, your response \
  should be solely a JSON object containing the keys first_name, last_name, \
  street_address, city, and state. If I change the subject of conversation \
  to something other than my name and address, or smalltalk, your response \
  should be solely a JSON object {"error": "True"}. Start pretending \
  immediately.""")
---
mandatory: True
code: |
  while True:
    bot_response = name_address.ask(prompt)
    try:
      address = json.loads(bot_response)
      assert isinstance(address, dict) and \
      ('error' in address or 'first_name' in address)
      break
    except:
      pass
    del prompt
---
mandatory: True
code: |
  if not address.get("error", False):
    user.name.first = address.get('first_name', '')
    user.name.last = address.get('last_name', '')
    user.address.address = address.get('street_address', '')
    user.address.city = address.get('city', '')
    user.address.state = address.get('state', '')
  del address
---
mandatory: True
question: |
  Your name and address
subquestion: |
  % if user.name.defined():
  ${ user.address_block() }
  % else:
  You failed to cooperate.
  % endif
---
question: |
  Freddy, a chatbot
subquestion: |
  ${ bot_response }
fields:
  - no label: prompt
    datatype: area
{% endhighlight %}

The only difference between `chatbot-slow.yml` and the earlier
`chatbot.yml` is that `chatbot-slow.yml` does:

{% highlight yaml %}
include:
  - chatbot-bg.yml
{% endhighlight %}

instead of:

{% highlight yaml %}
modules:
  - .chatbot
{% endhighlight %}

Any time the OpenAI API is called, the user will see the waiting
screen.

[`retrieve_stashed_data()`]: {{ site.baseurl }}/docs/functions.html#retrieve_stashed_data
[`/api/session/new` GET endpoint]: {{ site.baseurl }}/docs/api.html#session_new
[`/api/session` POST endpoint]: {{ site.baseurl }}/docs/api.html#session_post
[`sections`]: {{ site.baseurl }}/docs/initial.html#sections
[how **docassemble** finds questions for variables]: {{ site.baseurl }}/docs/logic.html#variablesearching
[`show if`]: {{ site.baseurl }}/docs/fields.html#show if
[`demo-basic-questions.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/demo-basic-questions.yml
[`demo-basic-questions-name.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/demo-basic-questions-name.yml
[`demo-basic-questions-address.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/demo-basic-questions-address.yml
[catchall questions]: {{ site.baseurl }}/docs/fields.html#catchall
[action]: {{ site.baseurl }}/docs/functions.html#actions
[`depends on`]: {{ site.baseurl }}/docs/logic.html#depends on
[`datatype: object_checkboxes`]: {{ site.baseurl }}/docs/fields.html#object_checkboxes
[`validation code`]: {{ site.baseurl }}/docs/fields.html#validation code
[AWS Lambda]: https://aws.amazon.com/lambda/
[API]: {{ site.baseurl }}/docs/api.html
[form.io]: https://form.io
[installing a package]: {{ site.baseurl }}/docs/packages.html#installing
[PyPI]: https://pypi.python.org/pypi
[Stripe]: https://stripe.com/
[testing card number]: https://stripe.com/docs/testing#cards
[supported accounts and settlement currencies]: https://stripe.com/docs/payouts#supported-accounts-and-settlement-currencies
[Configuration]: {{ site.baseurl }}/docs/config.html
[`exhibit_insert.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/exhibit_insert.docx
[`datereplace.js`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/static/datereplace.js
[`pdf_concatenate()`]: {{ site.baseurl }}/docs/functions.html#pdf_concatenate
[JSON]: https://en.wikipedia.org/wiki/JSON
[`action_button_html()`]: {{ site.baseurl }}/docs/functions.html#action_button_html
[`flash()`]: {{ site.baseurl }}/docs/functions.html#flash
[`action_call()`]: {{ site.baseurl }}/docs/functions.html#js_action_call
[`val()`]: {{ site.baseurl }}/docs/functions.html#js_val
[`set_save_status()`]: {{ site.baseurl }}/docs/functions.html#set_save_status
[`action_argument()`]: {{ site.baseurl }}/docs/functions.html#action_argument
[`json_response()`]: {{ site.baseurl }}/docs/functions.html#json_response
[`id`]: {{ site.baseurl }}/docs/modifiers.html#id
[`if`]: {{ site.baseurl }}/docs/modifiers.html#if
[CSS custom class]: {{ site.baseurl}}/docs/initial.html#css customization
[Running Javascript at page load time]: {{ site.baseurl }}/docs/functions.html#js_daPageLoad
[custom front ends]: {{ site.baseurl }}/docs/frontend.html
[DOM]: https://en.wikipedia.org/wiki/Document_Object_Model
[`encode_name()`]: {{ site.baseurl }}/docs/functions.html#encode_name
[`log()`]: {{ site.baseurl }}/docs/functions.html#log
[`code`]: {{ site.baseurl }}/docs/code.html#code
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`script` modifier]: {{ site.baseurl }}/docs/modifiers.html#script
[Ajax]: https://en.wikipedia.org/wiki/Ajax_(programming)
[`get_interview_variables()`]: {{ site.baseurl }}/docs/functions.html#js_get_interview_variables
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[`check in`]: {{ site.baseurl }}/docs/background.html#check in
[`DARedis`]: {{ site.baseurl }}/docs/objects.html#DARedis
[`.set_data()`]: {{ site.baseurl }}/docs/objects.html#DARedis.set_data
[`.get_data()`]: {{ site.baseurl }}/docs/objects.html#DARedis.get_data
[Redis]: https://redis.io/
[Celery]: https://docs.celeryq.dev/en/stable/
[background task]: {{ site.baseurl }}/docs/background.html#background
[background tasks]: {{ site.baseurl }}/docs/background.html#background
[core document properties]: https://python-docx.readthedocs.io/en/latest/dev/analysis/features/coreprops.html
[pickled]: https://docs.python.org/3/library/pickle.html
[pickling]: https://docs.python.org/3/library/pickle.html
[docx]: https://python-docx.readthedocs.io/
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[`pdf template file`]: {{ site.baseurl }}/docs/documents.html#pdf template file
[YAML]: https://en.wikipedia.org/wiki/YAML
[`signature-diversion.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/signature-diversion.yml
[collapse feature]: https://getbootstrap.com/docs/5.2/components/collapse/
[Bootstrap]: https://getbootstrap.com/
[`disable others`]: {{ site.baseurl }}/docs/fields.html#disable others
[`object` datatype]: {{ site.baseurl }}/docs/fields.html#object
[`interview_url()`]: {{ site.baseurl }}/docs/functions.html#interview_url
[`code`]: {{ site.baseurl }}/docs/code.html
[`features`]: {{ site.baseurl }}/docs/initial.html#javascript
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[mail merge example]: #mail merge
[generic-document.docx]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/generic-document.docx
[`generic object` modifier]: {{ site.baseurl }}/docs/modifiers.html#generic object
[`generic object`]: {{ site.baseurl }}/docs/modifiers.html#generic object
[`force_ask()`]: {{ site.baseurl }}/docs/functions.html#force_ask
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[`docassemble.demo:data/questions/sign.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/sign.yml
[declaration_of_favorite_fruit.docx]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/declaration_of_favorite_fruit.docx
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[`docassemble.demo.sign`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/sign.py
[`DAEmpty`]: {{ site.baseurl }}/docs/objects.html#DAEmpty
[`sign.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/sign.yml
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`DAFileCollection`]: {{ site.baseurl }}/docs/objects.html#DAFileCollection
[`signature`]: {{ site.baseurl }}/docs/fields.html#signature
[`reconsider()`]: {{ site.baseurl }}/docs/functions.html#reconsider
[`template`]: {{ site.baseurl }}/docs/initial.html#template
[`create_session()`]: {{ site.baseurl }}/docs/functions.html#create_session
[`set_session_variables()`]: {{ site.baseurl }}/docs/functions.html#set_session_variables
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`Person`]: {{ site.baseurl }}/docs/objects.html#Person
[`Address`]: {{ site.baseurl }}/docs/objects.html#Address
[`fruit_database` module]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/fruit_database.py
[`pandas`]: https://pandas.pydata.org/
[can be given]: {{ site.baseurl }}/docs/documents.html#template file code
[`googledrivedownloader`]: https://pypi.org/project/googledrivedownloader/
[`DAGoogleAPI`]: {{ site.baseurl }}/docs/objects.html#DAGoogleAPI
[`docassemble.demo.gd_fetch`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/gd_fetch.py
[`google-api-python-client`]: https://github.com/google/google-api-python-client/
[`google`]: https://docassemble.org/docs/config.html#google
[`service account credentials`]: https://docassemble.org/docs/config.html#service%20account%20credentials
[service account]: https://cloud.google.com/iam/docs/understanding-service-accounts
[`navigation bar html`]: {{ site.baseurl }}/docs/initial.html#navigation bar html
[`default screen parts`]: {{ site.baseurl }}/docs/initial.html#default screen parts
[screen part]: {{ site.baseurl }}/docs/questions.html#screen parts
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[Mako]: https://www.makotemplates.org/
[`url_of()`]: {{ site.baseurl }}/docs/functions.html#url_of
[Language Support]: {{ site.baseurl }}/docs/language.html
[`store_variables_snapshot()`]: {{ site.baseurl }}/docs/functions.html#store_variables_snapshot
[`db`]: https://docassemble.org/docs/config.html#db
[`variables snapshot db`]: https://docassemble.org/docs/config.html#variables snapshot db
[JSONB]: https://www.postgresql.org/docs/current/functions-json.html
[`on change`]: {{ site.baseurl }}/docs/initial.html#on change
[`index.py`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/index.py
[`write_record()`]: {{ site.baseurl }}/docs/functions.html#write_record
[`read_records()`]: {{ site.baseurl }}/docs/functions.html#read_records
[Flask]: https://flask.pocoo.org/
[`set_parts()`]: {{ site.baseurl }}/docs/functions.html#set_parts
[watermark]: https://en.wikipedia.org/wiki/Watermark
[LaTeX]: https://www.latex-project.org/
[`draftwatermark`]: https://www.ctan.org/pkg/draftwatermark
[default LaTeX template]: https://github.com/jhpyle/docassemble/blob/master/docassemble_base/docassemble/base/data/templates/Legal-Template.tex
[default metadata]: https://github.com/jhpyle/docassemble/blob/master/docassemble_base/docassemble/base/data/templates/Legal-Template.yml
[`background`]: https://www.ctan.org/pkg/background
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[`ics`]: https://icspy.readthedocs.io/en/stable/
[`calendar.py`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/calendar.py
[`nested_list_table.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/nested_list_table.docx
[Jinja2]: https://jinja.palletsprojects.com/en/3.0.x/
[`cards.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/examples/cards.yml
[`cards.py`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/cards.py
[Card]: https://getbootstrap.com/docs/5.2/components/card/
[Markdown in HTML extension]: https://python-markdown.github.io/extensions/md_in_html/
[`matplotlib`]: https://matplotlib.org/
[`graph.py`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/graph.py
[`graph.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/graph.docx
[`button-checkboxes.css`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/static/button-checkboxes.css
[`background_action()`]: {{ site.baseurl }}/docs/background.html#background_action
[`celery modules`]: {{ site.baseurl }}/docs/config.html#celery modules
[`upload-handler.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/examples/upload-handler.yml
[`raw html`]: {{ site.baseurl }}/docs/fields.html#raw html
[accordion feature]: https://getbootstrap.com/docs/5.3/components/accordion/
[`docassemble.demo`]: https://github.com/jhpyle/docassemble/tree/master/docassemble_demo
[`docassemble.demo.accordion`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/accordion.py
[`require login`]: {{ site.baseurl }}/docs/initial.html#require login
[`required privileges`]: {{ site.baseurl }}/docs/initial.html#required privileges
[stash]: {{ site.baseurl }}/docs/api.html#stash_data
[`/api/stash_data`]: {{ site.baseurl }}/docs/api.html#stash_data
[`module blacklist`]: {{ site.baseurl }}/docs/config.html#module blacklist
[OpenAI Platform]: https://platform.openai.com
[`openai`]: https://pypi.org/project/openai/
