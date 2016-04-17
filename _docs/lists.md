---
layout: docs
title: List variables
short_title: Lists
---

To gather information about multiple things, you could do something
like:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
mandatory: true
code: all_done
---
sets: all_done
question: |
  Summary of the parties in this case
subquestion: |
  The parties in this case are ${ first_party }, ${ second_party },
  and ${ third_party }.
---
objects:
  - first_party: Individual
  - second_party: Individual
  - third_party: Individual
---
question: |
  Who is the first party?
fields:
  First Name: first_party.name.first
  Last Name: first_party.name.last
---
question: |
  Who is the second party?
fields:
  First Name: second_party.name.first
  Last Name: second_party.name.last
---
question: |
  Who is the third party?
fields:
  First Name: third_party.name.first
  Last Name: third_party.name.last
---
{% endhighlight %}

However, this is a bit repetitive.  What if you needed to collect
information about eight people?

An easier way to collect information about multiple things is to use a
list.  A list is a variable that contains multiple things.  You refer
to an item in the list using an index number.  The index number starts
with zero.  So if `fruit` is a list, `fruit[0]` refers to the first
item in the list, `fruit[1]` refers to the second item, and `fruit[2]`
refers to the third item.




