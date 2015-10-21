---
layout: docs
title: Code Questions
short_title: Code
---

Under construction.

## Modifiers

### initial

{% highlight yaml %}
---
initial: true
code: |
  my_counter = 0
---
{% endhighlight %}

### mandatory

This is the code that directs the flow of the interview.  It indicates
to the system that we need to get to the endpoint "user_done."  There
is a question below that "sets" the variable "user_done."  Docassemble
will ask all the questions necessary to get the information need to
pose that that final question to the user.

However, if the answer to the question
user_understands_no_attorney_client_relationship is not "understands,"
the interview will looks for a question that sets the variable
"user_kicked_out."

"Mandatory" sections like this one are evaluated in the order they
appear in the question file.

