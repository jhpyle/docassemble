Interviews are developered as [YAML] files.  Within the [YAML] files, the
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
Interview developers do not need to have any prior experience with
[Python] or computer programming in order to create **docassemble**
interviews.  The only [Python] statements developers may need to write
are if/then/else statements that are very close to plain English.  For
example:

{% highlight python %}
if user.is_citizen or user.is_legal_permanent_resident:
  user.is_eligible = True
else:
  user.is_eligible = False
{% endhighlight %}

## Support is available

Although **docassemble** has extensive [documentation], you may have
questions about how to use it.  To [get help] from the community of
developers and other users, you can chat in real time with
knowledgeable developers on the [**docassemble** Slack group].  If you
find a bug, you can [submit an issue on GitHub].  You can also [e-mail
the developer].

In June 2018 and June 2019, the **docassemble** community convened for <a
href="https://docacon.com">Docacon</a>, a one-day docassemble
conference.

[get help]: {{ site.baseurl }}/docs/support.html
[documentation]: {{ site.baseurl }}/docs.html
[submit an issue on GitHub]: https://github.com/jhpyle/docassemble/issues
[docassemble mailing list]: https://mail.python.org/mm3/mailman3/lists/docassemble.python.org/
[e-mail the developer]: mailto:jhpyle@gmail.com
[Markdown]: https://daringfireball.net/projects/markdown/syntax
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[YAML]: https://en.wikipedia.org/wiki/YAML
[**docassemble** Slack group]: https://join.slack.com/t/docassemble/shared_invite/enQtMjQ0Njc1NDk0NjU2LTAzYzY5NWExMzUxNTNhNjUyZjRkMDg0NGE2Yjc2YjI0OGNlMTcwNjhjYzRhMjljZWU0MTI2N2U0MTFlM2ZjNzg
