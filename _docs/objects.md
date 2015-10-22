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
include:
  - docassemble.base:data/questions/basic-questions.yml
---
question: What's your name?
fields:
  - First: user.name.first
  - Last: user.name.last
---
question: |
  Hello, ${ user.name }!
mandatory: true
{% endhighlight %}

Loading the `basic-questions.yml` file means that your code can assume
that the `user` variable is an object of type `Individual`.

And in fact, it is even easier than that.  You can write:

    Hello, ${ user }!

instead.

(to be continued...)

[object-oriented programming]: https://en.wikipedia.org/wiki/Object-oriented_programming
