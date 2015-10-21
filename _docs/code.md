---
layout: docs
title: Code Questions
short_title: Code
---

In a **docassemble** interview, a `question` block tells
**docassemble** that if the interview logic wants to know the value of
a particular variable, such as `best_fruit_ever`, and that variable
has not been defined yet, **docassemble** can pose the question to the
user and the user's answer to the question may provide a definition
for that variable.

For example, this `question` block:

{% highlight yaml %}
---
question: What is the best fruit ever?
fields:
  - Fruit: best_fruit_ever
---
{% endhighlight %}

asks the user to type in the name of the best fruit ever.

The value of variables like `best_fruit_ever` can also be retrieved by
running Python code contained within `code` blocks:

{% highlight yaml %}
---
code: |
  best_fruit_ever = "Apple"
---
{% endhighlight %}

This `code` "question" is "asked" in much the same way that the
previous `question` question is asked: if and when it needs to be
asked.  **docassemble** "asks" `code` questions not by asking for the
user's input and then processing the user's input, but by running the
Python code contained in the `code` statement.

As with user `question`s, **docassemble** might find that "asking" the
`code` question did not actually define the needed variable.  In that
case, it goes looking for another question (which could be of the
`question` or `code` variety) that will provide a definition.

Once `best_fruit_ever` is defined, **docassemble** will not need to
run the `code` again if the interview logic calls for
`best_fruit_ever` at a later point.  In the same way, **docassemble**
does not need to ask the user for the user's name every time it needs
to know the user's name.

The `code` can do anything Python can do, such as retrieve information
from the web:

{% highlight yaml %}
---
import:
  - urllib2
---
code:
  response = urllib2.urlopen('http://worldsbestfruit.com/')
  best_fruit_ever = response.read()
---
{% endhighlight %}

or pick a random value from a list:

{% highlight yaml %}
---
import:
  - random
---
code:
  best_fruit_ever = random.choice(['Apple', 'Orange', 'Pear'])
---
{% endhighlight %}

(If you don't remember what an `import` block does, see
[initial blocks].)

It is not necessary to have any `code` blocks in your interviews, but
they are the most elegant way of expressing your interview logic.

## Modifiers

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

### initial

If you want your `code` to be run every time **docassemble** processes
your interview logic, add the `initial` modifier:

{% highlight yaml %}
---
initial: true
code: |
  my_counter = 0
---
{% endhighlight %}

The location of `initial` code in the interview file matters.  Code
marked as `initial` will be executed when it is encountered as
**docassemble** goes through the interview file from top to bottom
(and follows `include` statements when it sees them)

