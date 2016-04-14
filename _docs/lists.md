---
layout: docs
title: List variables
short_title: Lists
---

# Why use lists

Consider the following interview, which tells a funny story based on
words provided by the interviewee.

{% highlight yaml %}
---
question: A funny story
subquestion: |
  One day, ${ person_one } went to the ${ noun_one } to purchase a
  ${ noun_two }, but along the way he ${ verb_one } into a
  ${ adjective_one } ${ noun_three } with a ${ adjective_two }
  ${ noun_four }.
sets: all_done
---
question: Give me a person.
fields:
  - Person: person_one
---
question: Give me a noun.
fields:
  - Noun: noun_one
---
question: Give me a noun.
fields:
  - Noun: noun_two
---
question: Give me a noun.
fields:
  - Noun: noun_three
---
question: Give me a noun.
fields:
  - Noun: noun_four
---
question: Give me an adjective.
fields:
  - Adjective: adjective_one
---
question: Give me an adjective.
fields:
  - Adjective: adjective_two
---
question: Give me a verb.
fields:
  - Verb: verb_one
---
mandatory: true
code: all_done
---
{% endhighlight %}

This works, but it is a little bit tedious to create a separate
variable name and a separate question for each noun, adjective, and
verb.

