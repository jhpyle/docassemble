---
layout: docs
title: Marking Up Text
short_title: Markup
---

[DALang] allows you to format your text using [Markdown] and to
use [Mako] to make your text "smart."  These [mark up] methods
are available for use in [`question`] text, field labels, [`interview
help`] text, the content of [documents], and other text elements.

# <a name="markdown"></a>Markdown

The syntax of [Markdown] is explained well
[elsewhere](https://daringfireball.net/projects/markdown/).

When generating [documents], a Steward uses [Pandoc] to convert
your [Markdown] to PDF, RTF, and HTML.  (Unless you are using
[Microsoft Word templates], in which case you will use the [Jinja2]
templating language in the Word document.)

Here are some examples of things you can do with Markdown.

{% include side-by-side.html demo="markdown-demo" %}

All of these types of markup will format text in questions as well as
text in assembled documents (with the exception of the `!` image insertion
command, which does not work within PDF and RTF documents).

# <a name="mako"></a>Using Mako for Logic and Generated Text

[DALang] uses a templating system called [Mako] to allow
authors to insert variables and code into questions and documents.

You can insert the values of variables into question text using [Mako]'s
`${ ... }` syntax.

{% include side-by-side.html demo="mako-01" %}

You can use [Mako]'s `if/endif` syntax to insert text conditionally:

{% include side-by-side.html demo="mako-02" %}

You can also express more complicated logic:

{% include side-by-side.html demo="mako-03" %}

The [Mako] syntax for if/then/else statements is based on
[Python's `if` statement], but is a little bit different.

The `%` at the beginning of the line signifies that you are doing
something special with [Mako].

[Python] itself does not use `endif` -- it only uses indentation to
designate where the if/then/else statement ends.  [Mako] requires the
use of `endif` because it does not see indentation.

In [Python], `elif` is short for "else if."  In the example above, the
if/then/else statement means:

> If the day of the month is less than three, write "The month just
> started!", but otherwise if the day of the month is less than 15,
> write "It is the beginning part of the month."; otherwise, write "It
> is the latter part of the month."

As with [Python], it is critical that you include `:` at the end of
any line where you indicate a condition.

You can put `if/endif` statements inside of other `if/endif`
statements:

{% include side-by-side.html demo="mako-04" %}

In this example, the `% if`, `% else`, and `% endif` lines are
indented, but they do not have to be.  Since nested if/then/else
statements can be hard to read, the indentation helps make the
statement more readable.  Note that the the actual text itself is not
indented, even though the `%` lines are indented; this is because
indentation means something in [Markdown].  If you indent a line by
four spaces, [Markdown] will treat the line as a [code block], which
might not be what you want.

<a name="for"></a>[Mako] also allows you to work with lists of things
using `% for` and `% endfor`:

{% include side-by-side.html demo="mako-05" %}

This is based on [Python's `for` statement].

The `for` loop is useful for working with groups of [objects]:

{% include side-by-side.html demo="mako-06" %}

<a name="loop"></a>Within `for` loops, [Mako] provides a useful object called [`loop`],
which contains information about the current iteration of the loop.

{% include side-by-side.html demo="mako-09" %}

Note that `loop.index` is a number in a range that starts with zero.
The [`ordinal()`] function converts these numbers to words.

For more information about working with groups of things, see
[data structures].

In addition to allowing you to insert [Python] expressions with the `${
... }` syntax, [Mako] allows you to embed [Python] statements using
the `<%`/`%>` syntax:

{% include side-by-side.html demo="mako-07" %}

[Mako] also allows you to insert special code that cuts short the text
being rendered:

{% include side-by-side.html demo="mako-08" %}

The same thing could also be accomplished with an `else` statement,
but using [`STOP_RENDERING`] may be more readable.

For more information about [Mako], see the [Mako documentation].
Note, however, that not all features of [Mako] are available in
[DALang].  For example, in normal [Mako], you can write:

{% highlight text %}
% if some_variable is UNDEFINED:
...
% endif
{% endhighlight %}

In DALang, this will not work as intended.  Instead, you
would use the [`defined()` function]:

{% highlight text %}
% if not defined('some_variable'):
...
% endif
{% endhighlight %}

If you want to use the [`<%def>`] construct of [Mako], see the
[`def` initial block].

## <a name="formatting"></a>Formatting Variables

When the variable you insert with `${ ... }` is a number, the way that
it is formatted may not be to your liking.  There are a variety of
ways to format numbers in [Python].

{% include side-by-side.html demo="number-formatting" %}

# <a name="inserting images"></a>Inserting Images

To insert an image that is located in the `static` folder of an installed Steward,
use the `FILE` command.  This works within PDF, RTF,
and DOCX documents as well as within questions.

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

This example presumes that there is a Steward named
`docassemble.crimesolver` installed on the [server], and there is a file
`mugshot.jpg` located within the `static` directory inside that
Steward.

If you omit the package name (e.g., `[FILE mugshot.jpg]`),
your Steward will assume you are referring to a file located in its own
`static` directory.

Optionally, you can set the width of the image:

    [FILE docassemble.crimesolver:mugshot.jpg, 100%]

or:

    [FILE docassemble.crimesolver:mugshot.jpg, 150px]

<a name="inserting uploaded images"></a>To insert an image that has
been uploaded, or created using a [signature field], simply refer to
the variable using [Mako].  For example:

{% include side-by-side.html demo="upload" %}

Alternatively, you can call the [`show()`] method on the file object:

{% include side-by-side.html demo="upload-show" %}

The [`show()`] method takes an optional argument, `width`:

{% include side-by-side.html demo="upload-show-width" %}

In the above example, the picture will be shrunk or expanded so that
its width is 250 pixels.

# <a name="emoji"></a>Inserting Inline Icons

If you have defined "decorations" in an [`image sets`] block (see
[initial blocks]), you can include these decorations as icons (having
the same size as the text) by referencing them "emoji-style," putting
colons around the decoration name.  This works not only in `question`
and [`subquestion`] areas, but also in question choices.

This works within PDF and RTF documents as well as within questions.

{% include side-by-side.html demo="emoji-inline" %}

By default, if an "emoji-style" reference refers to an image that has
not been defined in an [`image sets`] or [`images`] block, the
reference will be treated as a reference to a [Font Awesome] icon.

{% include side-by-side.html demo="font-awesome" %}

As explained in the [Configuration], only one "style" of [Font
Awesome] icon (by default, the "solid" style) can be used at one time.
If you need to use a different "style" for a particular icon, or you
want to apply additional formatting to an icon, you can include the
raw [HTML] for the icon. For example:

{% highlight yaml %}
---
question: |
  Social media usage
subquestion: |
  Do you use <i class="fab fa-facebook-f"></i>?
yesno: user_is_on_facebook
---
{% endhighlight %}

Note that while ordinary inline icon references work in documents as
well as on the web, [Font Awesome] references only work in questions,
not in documents.

# <a name="audio and video"></a>Inserting Audio and Video

In addition to using the [`audio`] and [`video`]<span></span> [modifier components], you can
insert audio and video into your [Mako] text in questions.

{% include side-by-side.html demo="audio-upload" %}

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

You can also embed [YouTube] and [Vimeo] videos (which is far
preferable to working with video files, which are enormous).  For
example, if you want to embed a [YouTube] video for which the URL is
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

See [modifier components] for more information about including audio and video.

# <a name="qr"></a>Inserting QR Codes

You can also display or insert QR codes using `[QR ...]`, where `...`
is the text you want to encode.  This works like `[FILE ...]` in that
you can give the image a width.  The QR code images can be displayed
on the screen or inserted into a document.

This works within PDF and RTF documents as well as within questions.

For example, this [DALang] provides a QR code that directs the user to
[Google News](http://news.google.com):

{% include side-by-side.html demo="qr-code-demo" %}

See also the [`qr_code()`] function, which allows you to insert the
`[QR ...]` markup using [Python].

# <a name="inserting other"></a>Inserting Other Types of Files

Just as you can insert images with `[FILE
docassemble.crimesolver:mugshot.jpg]` or `${ user_picture }`, you can
also insert other types of files.

If you insert a text file (MIME type `text/plain`), the raw contents
of the file will be inserted.

If you insert a [Markdown] file (MIME type `text/markdown`), the
contents of the file will be treated as a [`DATemplate`].

The behavior when you insert a PDF file depends on the context:

* In a `question`, the user will see a thumbnail of the first page of
  the document, and clicking the thumbnail will open the PDF file.
* In a [document] created by converting [Markdown] to PDF, the PDF
  pages will be inserted into the document.
* When assembling documents in other formats, the pages of the PDF
  will be converted to images and inserted into the document in the
  same way images are inserted.

When you insert a word processing file, the file will be converted to
PDF and inserted into the document the way a PDF file is inserted.
However, if you include a .docx file inside a .docx file created using
[`docx template file`], the result is like that of calling
[`include_docx_template()`].

# <a name="tables"></a>Inserting Tables

Tables can be inserted in the format known as [PHP Markdown Extra].

{% include side-by-side.html demo="table-markdown" %}

If you want to construct a table based on information in a list, the
best practice is to collect the list information into an [object] and
then use the [`table` block] to create a template for the table.

If you want to write tables in [Markdown] manually, note that the
alignment characters do not have do be perfectly aligned from row to
row.

{% include side-by-side.html demo="table-markdown-unaligned" %}

Under the [Markdown] rules, the text for each row needs to be all on
the same line in your [Markdown] text.  If you want to include a line
break within a cell, use the `[BR]` tag, which is documented in the
[document markup] section.

Exactly how your text is converted from [Markdown] into an actual
table depends on the output format.  If you are including a table that
is viewed on the screen, see [tables in HTML] for the details.  If you
are including a table that is inserted into an attachment, see
[tables in attachments].

If you want to have fine-grained control over the formatting of
tables, [Markdown] will disappoint you.

For example, the [PHP Markdown Extra] format _requires_ that you
include a header in your table, even if you do not want one.  You can
try to make the header row blank with the following trick.

{% include side-by-side.html demo="table-markdown-noheader" %}

If you want a very specific type of table, you can use [raw HTML] for
a table that displays in a question or [raw LaTeX] for a table that
displays in a PDF-only [`attachment`].

If you want a simple two-column table that fills the width of the
page, note that there are special [document markup] tags for this
special case: you can write `[BEGIN_TWOCOL]` (text of first column)
`[BREAK]` (text of second column) `[END_TWOCOL]`.

# <a name="field"></a>Embedding Fields

In a [`fields`] component, you can use the markup syntax `[FIELD ...]` to
embed fields within the [`subquestion`] text.  For more
information about this feature, see the section on
[Embedding fields within a paragraph].

# <a name="target"></a>Embedding Areas for Interim Information

If you include the markup `[TARGET ...]` within text, you will create
an invisible area where text can be placed by [`code`].  For more
information about this feature, see the section on
[Processing interim user input].

[document markup]: {{ site.baseurl }}/docs/documents.html#markup
[`table` block]: {{ site.baseurl }}/docs/template.html#table
[raw LaTeX]: https://en.wikibooks.org/wiki/LaTeX/Tables
[raw HTML]: https://www.w3schools.com/html/html_tables.asp
[PHP Markdown Extra]: https://michelf.ca/projects/php-markdown/extra/#table
[tables in attachments]: http://pandoc.org/MANUAL.html#extension-pipe_tables
[tables in HTML]: https://pythonhosted.org/Markdown/extensions/tables.html
[`code`]: {{ site.baseurl }}/docs/code.html
[Processing interim user input]: {{ site.baseurl }}/docs/background.html#target
[Embedding fields within a paragraph]: {{ site.baseurl }}/docs/fields.html#embed
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
[document]: {{ site.baseurl }}/docs/documents.html
[documents]: {{ site.baseurl }}/docs/documents.html
[modifier components]: {{ site.baseurl }}/docs/modifiers.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[YAML]: https://en.wikipedia.org/wiki/YAML
[mark up]: https://en.wikipedia.org/wiki/Markup_language
[Pandoc]: http://johnmacfarlane.net/pandoc/
[YouTube]: https://www.youtube.com/
[Vimeo]: https://vimeo.com/
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[function]: {{ site.baseurl }}/docs/functions.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`subquestion`]: {{ site.baseurl }}/docs/questions.html#subquestion
[`interview help`]: {{ site.baseurl }}/docs/initial.html#interview help
[`show()`]: {{ site.baseurl }}/docs/objects.html#DAFile.show
[`images`]: {{ site.baseurl }}/docs/initial.html#images
[`image sets`]: {{ site.baseurl }}/docs/initial.html#image sets
[`audio`]: {{ site.baseurl }}/docs/modifiers.html#audio
[`video`]: {{ site.baseurl }}/docs/modifiers.html#video
[`qr_code()`]: {{ site.baseurl }}/docs/functions.html#qr_code
[code block]: https://daringfireball.net/projects/markdown/syntax#precode
[Python's `if` statement]: https://docs.python.org/2.7/tutorial/controlflow.html#if-statements
[Python's `for` statement]: https://docs.python.org/2.7/tutorial/controlflow.html#for-statements
[object]: {{ site.baseurl }}/docs/objects.html
[objects]: {{ site.baseurl }}/docs/objects.html
[data structures]: {{ site.baseurl }}/docs/groups.html
[`loop`]: http://docs.makotemplates.org/en/latest/runtime.html#loop-context
[`STOP_RENDERING`]: http://docs.makotemplates.org/en/latest/syntax.html#exiting-early-from-a-template
[`ordinal()`]: {{ site.baseurl }}/docs/functions.html#ordinal
[Mako documentation]: http://docs.makotemplates.org/en/latest/index.html
[`defined()` function]: {{ site.baseurl }}/docs/functions.html#defined
[`<%def>`]: http://docs.makotemplates.org/en/latest/defs.html#using-defs
[`def` initial block]: {{ site.baseurl }}/docs/initial.html#def
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
[signature field]: {{ site.baseurl }}/docs/fields.html#signature
[Font Awesome]: https://fontawesome.com
[`use font awesome`]: {{ site.baseurl}}/docs/config.html#use font awesome
[Configuration]: {{ site.baseurl}}/docs/config.html
[HTML]: https://en.wikipedia.org/wiki/HTML
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[Microsoft Word templates]: {{ site.baseurl}}/docs/documents.html#docx template file
[Jinja2]: http://jinja.pocoo.org/docs/2.9/
[`DATemplate`]: {{ site.baseurl }}/docs/objects.html#DATemplate
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[`include_docx_template()`]: {{ site.baseurl }}/docs/functions.html#include_docx_template
[DALang]: {{ site.baseurl }}/docs/interviews.html#yaml
[server]: {{ site.baseurl }}/docs/installation.html