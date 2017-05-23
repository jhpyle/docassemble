Interviews are authored as [YAML] files.  Within the [YAML] files, the
text of the interview questions and documents is formatted with
[Markdown], and the logic of the interview flow is expressed with
if/then/else statements in [Python].

{% include side-by-side.html demo="yaml-markdown-python" %}

## YAML, Markdown, and Python?  Sounds scary!

[YAML] is a text format for expressing information in a way that is
both human-readable and machine readable.

{% highlight yaml %}
food: bread
ingredients:
  - flour
  - yeast
  - water
  - salt
{% endhighlight %}

[Markdown] is a text format for expressing typographical formatting.
For example, if you write this [Markdown] text:

{% highlight text %}
It is *very* important that you obtain your
[free credit report](https://www.annualcreditreport.com) as soon
as possible.
{% endhighlight %}

then you get text that looks like this:

> It is *very* important that you obtain your
> [free credit report](https://www.annualcreditreport.com) as soon
> as possible.

[Python] is a language designed to be readable and easy to learn.
Authors do not need to have any prior experience with [Python] or
computer programming in order to create **docassemble** interviews.
The only [Python] statements authors may need to write are if/then/else
statements that are very close to plain English.  For example:

{% highlight python %}
if user.is_citizen or user.is_legal_permanent_resident:
  user.is_eligible = True
else:
  user.is_eligible = False
{% endhighlight %}

[Markdown]: https://daringfireball.net/projects/markdown/syntax
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[YAML]: https://en.wikipedia.org/wiki/YAML

