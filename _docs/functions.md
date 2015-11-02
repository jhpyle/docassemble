---
layout: docs
title: Functions
short_title: Functions
---

## force_ask 


{% highlight yaml %}
---
question: |
  Are you a communist?
yesno: user_is_communist
---
mandatory: true
code: |
  if user_is_communist:
    allow_user_to_reconsider
---
question: |
  Why don't you reconsider your answer?

{% endhighlight %}
