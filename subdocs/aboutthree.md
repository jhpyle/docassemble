Interview authors do not have to design the "flow" of the interview;
**docassemble** will automatically determine what questions to ask,
and the order in which to ask them, based on what information is
necessary to gather.  The system will refrain from asking unnecessary
questions.  For example, if the interview contains a conditional
statement such as:

{% highlight python %}
if user.is_disabled or user.age > 60:
  special_funding_exists = True
else:
  special_funding_exists = False
{% endhighlight %}
	  
then the user will be asked if he is disabled, and will only be asked
for his age if he says he is not disabled.  Authors need to provide a
question for every variable (e.g., there need to be questions that
determine `user.is_disabled` and `user.age`) but **docassemble** will
automatically figure out when and whether to ask those questions.

This allows authors to concentrate on the end result rather than
worrying about how to construct the interview process.  Authors who
are lawyers can "practice at the top of their license" by spending
their time thinking about the law (a lawyer function) rather than
thinking about the interview process (a non-lawyer function).
