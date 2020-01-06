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

# <a name="progressive disclosure"></a>Progresive disclosure

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
        classname = ' bg-light'
    else:
        classname = ' ' + classname.strip()
    the_id = re.sub(r'[^A-Za-z0-9]', '', template.instanceName)
    return u"""\
<a class="collapsed" data-toggle="collapse" href="#{}" role="button" aria-expanded="false" aria-controls="collapseExample"><span class="pdcaretopen"><i class="fas fa-caret-down"></i></span><span class="pdcaretclosed"><i class="fas fa-caret-right"></i></span> {}</a>
<div class="collapse" id="{}"><div class="card card-body{} pb-1">{}</div></div>\
""".format(the_id, template.subject_as_html(trim=True), the_id, classname, template.content_as_html())
{% endhighlight %}

This uses the [collapse feature] of [Bootstrap].

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

# <a name="document signing"></a>Multi-user interview for getting a client's signature

This is an example of a multi-user interview where one person (e.g.,
an attorney) writes a document that they want a second person (e.g, a
client) to sign.  It is a multi-user interview (with `multi_user` set
to `True`).  The attorney inputs the attorney's e-mail address and
uploads a DOCX file containing:

> {% raw %}{{ signature }}{% endraw %}

where the client's signature should go.  The attorney then receives a
hyperlink that the attorney can send to the client.

When the client clicks on the link, the client can read the unsigned
document, then agree to sign it, then sign it, then download the
signed document.  After the client signs the document, it is e-mailed
to the attorney's e-mail address.

{% include demo-side-by-side.html demo="sign" %}

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

# <a name="two stage"></a>Inserting Jinja2 with Jinja2

If you use Jinja2 to insert Jinja2 template tags into a document
assembled through [`docx template file`], you will find that the tags
in the included text will not be evaluated.  However, you can conduct
your document assembly in two stages, so that first you assemble a
template and then you use the DOCX output as the input for another assembly.

{% include demo-side-by-side.html demo="twostage" %}

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
$(document).on('daPageLoad', function(){
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

In your interview, include `idle.js` in a [`features`] block.

{% highlight yaml %}
features:
  javascript: idle.js
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
---
event: log_user_out
code: |
  command('logout')
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
other data types will require more work.

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

Create a module file called `dastripe.py` with the following contents:

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
      amount=int(float('%.2f' % self.amount)*100.0),
      currency=self.currency,
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

Create a [YAML] file with the following contents:

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

Test the interview with a [testing card number].  When you are
satisfied that it works, you can set your `stripe public key` and
`stripe secret key` to your "live" [Stripe] API keys.

The attributes of the `DAStripe` object (known as `payment` in this
example) that can be set are:

* `payment.currency`: this is the currency that the payment will use.
  Set this to `'usd'` for U.S. dollars.  See [supported accounts and
  settlement currencies] for information about which currencies are
  available.
* `payment.payor`: this contains information about the person who is
  paying.  You can set this to an `Individual` or `Person` with a
  `.billing_address` (an `Address`), a name, a `.phone_number`, and an
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
reported by [Stripe], followed by the value of `request.error_message`.
The value of `request.error_message` is passed through `word()`, so
you can use the `words` translation system to translate it.

If the payment is successful, the JavaScript on the page performs the
`request.success` "action" in the interview.  Your interview needs to
provide a code block that handles this action.  The action needs to
call `payment.process()`.  This will save the data returned by [Stripe]
and will also call the [Stripe] API to verify that payment was actually
made.

The next time `request.paid` is evaluated, the [Stripe] API is not
called again.

Payment processing is a very complicated subject, so this recipe
should only be considered a starting point.  The advantage of this
design is that it keeps a lot of the complexity of payment processing
out of the interview [YAML] and hides it in the module.

[Stripe]: https://stripe.com/
[testing card number]: https://stripe.com/docs/testing#cards
[supported accounts and settlement currencies]: https://stripe.com/docs/payouts#supported-accounts-and-settlement-currencies
[Configuration]: {{ site.baseurl }}/docs/config.html
[`exhibit_insert.docx`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/templates/exhibit_insert.docx
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
[Redis]: https://redis.io/
[Celery]: http://www.celeryproject.org/
[background task]: {{ site.baseurl }}/docs/background.html#background
[background tasks]: {{ site.baseurl }}/docs/background.html#background
[core document properties]: https://python-docx.readthedocs.io/en/latest/dev/analysis/features/coreprops.html
[pickled]: https://docs.python.org/3/library/pickle.html
[pickling]: https://docs.python.org/3/library/pickle.html
[docx]: https://python-docx.readthedocs.io/
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[YAML]: https://en.wikipedia.org/wiki/YAML
[`signature-diversion.yml`]: https://github.com/jhpyle/docassemble/blob/master/docassemble_demo/docassemble/demo/data/questions/signature-diversion.yml
[collapse feature]: https://getbootstrap.com/docs/4.0/components/collapse/
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
