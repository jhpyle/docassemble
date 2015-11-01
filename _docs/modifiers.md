---
layout: docs
title: Question Modifiers
short_title: Question Modifiers
---

There are a number of optional modifiers that can be included in
`question` blocks to control the appearance or behavior of the
question.

## `help`

{% highlight yaml %}
---
question: How much money do you wish to seek in damages?
fields:
  - Money: damages_sought
    datatype: currency
help: |
  If you are not sure how much money to seek in damages, just ask
  for a million dollars, since you want ${ defendant } to suffer.
---
{% endhighlight %}

In the web app, users can use the navigation bar to toggle between the
"Question" tab and the "Help" tab.  The contents of the "Help" tab
consist of the contents of any `help` statements in the question being
presented, followed by the contents of any `interview help` blocks
contained within the interview.

## `decoration`

{% highlight yaml %}
---
question: Have you been saving your money?
yesno: user_has_saved_money
decoration: piggybank
---
{% endhighlight %}

The `decoration` modifier adds an icon to the right of the `question`
text.  In the example above, `piggybank` will need to have been
defined in an `image sets` or `images` block.

## `progress`

{% highlight yaml %}
---
question: Are you doing well?
yesno: user_is_well
progress: 50
---
{% endhighlight %}

If **docassemble** is configured to show a progress bar, the progress
bar will be set to 50% when this question is asked.

## `language`

{% highlight yaml %}
---
question: |
  What is the meaning of life?
fields:
  - Meaning of life: meaning_life
---
language: es
question: |
  ¿Cuál es el significado de la vida?
fields:
  - Significado de la Vida: meaning_life
---
{% endhighlight %}

**docassemble**'s [language support] allows a single interview to asks
questions different ways depending on the user's language.  You can
write questions in different languages that set the same variables.
**docassemble** will use whatever question matches the active
language.

The value of `language` must be a two-character lowercase [ISO-639-1]
code.  For example, Spanish is `es`, French is `fr`, and Arabic is `ar`.

For more information about how to set the active language, see
[language support].

Instead of explicitly setting a `language` for every question, you can
use `default language` to apply a particular language to the remaining
questions in the file (see [initial blocks]).

## `generic object`

{% highlight yaml %}
---
generic object: Individual
question: |
  So, ${ x.is_are_you() } a defendant in this case?
yesno: x.is_defendant
---
{% endhighlight %}

`generic object` is a very powerful feature in **docassemble** that
allows authors to express questions in general terms.

The above example will cause **docassemble** to ask "So, is John Smith
a defendant in this case?" if the interview logic calls for
`neighbor.is_defendant` and `neighbor` is an object of type
`Individual` whose name has been set to "John Smith."  Or, if the
interview logic calls for `user.is_defendant`, **docassemble** will
ask, "So, are you a defendant in this case?"

`x` is a special variable that should only be used in `generic object`
questions.  This question definition tells **docassemble** that if it
ever needs an `is_defendant` attribute for any object of type
`Individual`, it can get an answer by asking this question.

## `role`

{% highlight yaml %}
---
role: advocate
question: Is the client's explanation a sound one?
subquestion: |
  ${ client } proposed the following explanation:
  
  > ${ explanation }

  Is this a legally sufficient explanation?
yesno: explanation_is_sound
---
{% endhighlight %}

If your interview uses the [roles]({{ site.baseurl}}/docs/roles.html)
feature for multi-user interviews, the `role` modifier in a `question`
block will tell **docassemble** that if it ever tries to ask this
question, the user will need to have a particular role in order to
proceed.

`role` can be a list.
{% highlight yaml %}
role:
  - advocate
  - supervisor
{% endhighlight %}
In this case, the user's role can either "advocate" or "supervisor" in
order to be asked the question.

If the user does not have an appropriate role, **docassemble** will
look for a question in the interview in which `event` has been set to
`role_event`.

## `comment`

{% highlight yaml %}
---
question: Do you agree the weather is nice today? 
yesno: day_is_nice
comment: |
  We might wish to consider taking out this question.  It does not
  seem necessary.
---
{% endhighlight %}

To make a note to yourself about a question, which will not be seen by
the end user, you can use a `comment` statement.  It will be ignored
by **docassemble**, so it can contain any valid [YAML].

[YAML]: https://en.wikipedia.org/wiki/YAML
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[language support]: {{ site.baseurl }}/docs/language.html
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
