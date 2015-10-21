---
layout: docs
title: Attaching documents to questions
short_title: Documents
---

The `attachments` statement (which can also be written `attachment`)
provides documents to the user, which can be previewed, downloaded,
and/or e-mailed.

{% highlight yaml %}
---
question: Your document is ready
sets: provide_user_with_document
attachment:
  - name: A document with a classic message
    filename: Hello_World_Document
    content: |
	  Hello, world!
---
{% endhighlight %}

The above question creates a document containing the text "Hello,
world!"  By default, the document is created in PDF and RTF format,
and the user will be given the option to e-mail the document to
himself.

