---
layout: docs
title: Recipes
short_title: Recipes
---

This section contains miscellaneous recipes for solving problems in
**docassemble**.

# Require a checkbox to be checked

## Using `validation code`

{% highlight yaml %}
modules:
  - docassemble.base.util
---
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

# Use a variable to track when an interview has been completed

One way to track whether an interview is completed is to set a
variable when the interview is done.  That way, you can inspect the
interview answers and test for the presence of this variable.

{% highlight yaml %}
modules:
  - docassemble.base.util
---
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
modules:
  - docassemble.base.util
---
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

# Exit interview with a hyperlink rather than a redirect

Suppose you have a final screen in your interview that looks like this:

{% highlight yaml %}
modules:
  - docassemble.base.util
---
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
modules:
  - docassemble.base.util
---
mandatory: True
code: |
  kick_out
---
event: kick_out
question: Bye
subquestion: |
  ${ action_button_html("https://example.com", size='md', color='primary', label='Exit', new_window=False) }
{% endhighlight %}

# Re-Use a Master List of Individuals

In some circumstances, the same Individual's information might need to be recorded multiple times.  In these
cases it can be helpful to allow the user to select from Individuals whose information has already been
entered.

In other circumstances, it is important to know whether the Individuals filling to roles are the same Individual.
For example, you might want to verify that the user is not making the executor of a document one of the witnesses also.

These purposes can be achieved by using a master list of Individuals.  When an individual needs to be specified, you can
allow the user to either choose an existing Individual, or enter a new one.

This technique requires non-idempotently checking for all Individuals that might have been set in an `initial` block,
and adding them to the
master list of Individuals using the `set_instance_name=True` parameter to `DAList.append()`.

{% highligh yaml %}
modules:
  - docassemble.base.core
  - docassemble.base.util
---
objects:
  - people: DAList.using(object_type=Individual)
  - boss: Individual
  - employee: Individual
  - customers: DAList.using(object_type=Individual)
---
initial: True
code: |
  if boss.name.defined():
    if boss not in people:
      people.append(boss,set_instance_name = True)
  if employee.name.defined():
    if employee not in people:
      people.append(employee, set_instance_name = True)
  for c in customers.complete_elements():
    if c.name.defined():
      if c not in people:
        people.append(c, set_instance_name = True)
---
mandatory: True
code: |
  people.there_are_any = False
  people.gathered = True
---
mandatory: True
question: |
  Summary
subquestion: |
  The boss is ${ boss }.
  
  The employee is ${ employee }.
  
  The customers are ${ customers }.
  
  % if boss in customers or employee in customers:
  Either the boss or the employee is also a customer.
  % else:
  Neither the boss nor the employee is also a customer.
  % endif
---
question: Are there any customers?
yesno: customers.there_are_any
---
question: Is there another customer?
yesno: customers.there_is_another
---
question: |
  Who is the boss?
fields:
  - Existing or New: boss.existing_or_new
    datatype: radio
    default: Existing
    choices:
      - Existing
      - New
  - Person: boss
    show if:
      variable: boss.existing_or_new
      is: Existing
    datatype: object
    choices: people
  - First Name: boss.name.first
    show if:
      variable: boss.existing_or_new
      is: New
  - Last Name: boss.name.last
    show if:
      variable: boss.existing_or_new
      is: New
  - Birthday: boss.birthdate
    datatype: date
    show if:
      variable: boss.existing_or_new
      is: New
---
question: |
  Who is the employee?
fields:
  - Existing or New: employee.existing_or_new
    datatype: radio
    default: Existing
    choices:
      - Existing
      - New
  - Person: employee
    show if:
      variable: employee.existing_or_new
      is: Existing
    datatype: object
    choices: people
  - First Name: employee.name.first
    show if:
      variable: employee.existing_or_new
      is: New
  - Last Name: employee.name.last
    show if:
      variable: employee.existing_or_new
      is: New
  - Birthday: employee.birthdate
    datatype: date
    show if:
      variable: employee.existing_or_new
      is: New
---
question: |
  Who is the customer?
fields:
  - Existing or New: customers[i].existing_or_new
    datatype: radio
    default: Existing
    choices:
      - Existing
      - New
  - Person: customers[i]
    show if:
      variable: customers[i].existing_or_new
      is: Existing
    datatype: object
    choices: people
  - First Name: customers[i].name.first
    show if:
      variable: customers[i].existing_or_new
      is: New
  - Last Name: customers[i].name.last
    show if:
      variable: customers[i].existing_or_new
      is: New
  - Birthday: customers[i].birthdate
    datatype: date
    show if:
      variable: customers[i].existing_or_new
      is: New
{% endhighlight %}
