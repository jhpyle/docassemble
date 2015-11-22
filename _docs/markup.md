---
layout: docs
title: Marking up text
short_title: Markup
---

**docassemble** allows you to format your text using [Markdown] and to
use [Mako] to make your documents "smart."  These [mark up] methods
are available for use in `question` text, field labels, `interview
help` text, the content of [documents], and other text elements.

## Markdown

The syntax of [Markdown] is explained well
[elsewhere](http://www.makotemplates.org/).

When generating [documents], **docassemble** uses [Pandoc] to convert
your [Markdown] to PDF, RTF, and HTML.

Here are some examples of things you can do with Markdown:

{% highlight yaml %}
---
question: Markdown demonstration
subquestion: |
  This is *italic text*.
  This is **bold text**.
  This is __also bold text__.

  > This is some block-quoted
  > text

  ### This is a heading

  This is an image:

  ![Bass logo](https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Bass_logo.svg/199px-Bass_logo.svg.png)

  Here is a bullet list:

  * Apple
  * Peach
  * Pear

  Here is a numbered list:

  1. Nutmeg
  2. Celery
  3. Oregano

  Here is a [link to a web site](http://google.com).
---
{% endhighlight %}

In the web application, this comes out looking like this:

![Markdown demo screenshot]({{ site.baseurl }}/img/markdown-demo.png)

All of these methods will format text in questions as well as PDF and
RTF documents, with the exception of the `!` image insertion command,
which does not work within PDF and RTF documents.

## Inserting images

To insert an image that is located in the `static` folder of a custom
Python package, use the `IMAGE` command.  This works within PDF and
RTF documents as well as within questions.

For example:

{% highlight yaml %}
---
question: |
  Did your attacker look like this?
subquestion: |
  Please study the face below closely before answering.

  [FILE docassemble.crimesolver:mugshot.jpg]
yesno: suspect_identified
{% endhighlight %}

This example presumes that there is a Python package called
`docassemble.crimesolver` installed on the server, and there is a file
`mugshot.jpg` located within the `static` directory inside that
package.

Optionally, you can set the width of the image:

    [FILE docassemble.crimesolver:mugshot.jpg, 100%]

or:

    [FILE docassemble.crimesolver:mugshot.jpg, 150px]

To insert an image that has been uploaded, simply refer to the
file variable using [Mako].  For example:

{% highlight yaml %}
---
question: |
  Do you look cute in this picture?
subquestion: |
  ${ user_picture }
yesno: user_is_cute
---
question: |
  Please upload a picture of yourself.
fields:
  - Your Picture: user_picture
    datatype: file
---
{% endhighlight %}

Alternatively, you can call the `show()` method on the file object:

{% highlight yaml %}
---
question: |
  Do you look cute in this picture?
subquestion: |
  ${ user_picture.show() }
yesno: user_is_cute
---
{% endhighlight %}

The `show()` method takes an optional argument, `width`:

{% highlight yaml %}
---
question: |
  Do you look cute in this picture?
subquestion: |
  ${ user_picture.show(width='250px') }
yesno: user_is_cute
---
{% endhighlight %}

In the above example, the picture will be shrunk or expanded so that
its width is 250 pixels.

## Inserting audio and video

In addition to using the `audio` and `video` [modifiers], you can
insert audio and video into your [Mako] text.

{% highlight yaml %}
---
question: Listen to this!
subquestion: |
  Best song ever:

  ${ my_file }

  Don't you think so?
---
question: Upload an audio file.
fields:
  - no label: my_file
    datatype: file
---
{% endhighlight %}

Or, if you have a file in `data/static`, you can write:

{% highlight yaml %}
---
question: Listen to this!
subquestion: |
  This excerpt of whalesong will give you goosebumps.

  [FILE whale_song.mp3]
---
{% endhighlight %}

It works the same with videos.

{% highlight yaml %}
---
question: Watch this!
subquestion: |
  This video of otters sunbathing is going to go viral.

  [FILE awesome_otters.mp4]
---
{% endhighlight %}

You can also embed [YouTube] and [Vimeo] videos.  For example, if you
want to embed a [YouTube] video for which the URL is
`https://www.youtube.com/watch?v=RpgYyuLt7Dx` or
`https://youtu.be/RpgYyuLt7Dx`, you would write this:

{% highlight yaml %}
---
question: Are you traveling to New York City?
yesno: going_to_nyc
video: |
  New York is such a happening place.  Check it out:

  [YOUTUBE RpgYyuLt7Dx]
---
{% endhighlight %}

See [modifiers] for more information about including audio and video.

[documents]: {{ site.baseurl }}/docs/documents.html
[modifiers]: {{ site.baseurl }}/docs/modifiers.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
[mark up]: https://en.wikipedia.org/wiki/Markup_language
[Pandoc]: http://johnmacfarlane.net/pandoc/
