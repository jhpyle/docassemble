---
layout: docs
title: Objects
short_title: Objects
---

Python allows [object-oriented programming] and so does
**docassemble**.

Here is a non-object-oriented way of saying hello to the user by name:

{% highlight yaml %}
---
question: What is your name?
fields:
  - First: user_first_name
  - Last: user_last_name
---
question: |
  Hello, ${ user_first_name } ${ user_last_name }!
mandatory: true
{% endhighlight %}

A better way is to take advantage of the **docassemble** object,
`Individual`:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - user: Individual
---
question: |
  What's your name?
fields:
  - First: user.name.first
  - Last: user.name.last
---
question: |
  Hello, ${ user }!
mandatory: true
---
{% endhighlight %}



[object-oriented programming]: https://en.wikipedia.org/wiki/Object-oriented_programming
