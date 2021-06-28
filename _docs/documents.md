---
layout: docs
title: Assembling documents
short_title: Documents
---

# <a name="oview"></a>Overview of document creation methods

There are several ways to make downloadable documents using the
`attachment` block.  Each has its own features and limitations.

## <a name="scratch"></a>Method 1: generating documents from scratch using Markdown

First, you can [generate attachments from Markdown](#from markdown).
In the same way that you format the text of questions, you can format
the text of attachments.  Suppose you write this in the document source:

{% highlight text %}
Hello, ${ user }.  This text is in **bold face**.

% if user.age_in_years() > 30:
You cannot be trusted!
% endif
{% endhighlight %}

This become the following in the resulting document:

> Hello, John Doe.  This text is in **bold face**.
>
> You cannot be trusted!

In this way, you can produce documents in [PDF](#pdf), [RTF](#rtf),
and [DOCX](#docx) format.

In addition to using [Markdown], you can use **docassemble**-specific
[markup](#markup) codes to do things like center text, insert a page
break, or insert a case caption.

## <a name="scratch"></a>Method 2: generating documents from DOCX templates

The second method of assembling documents is to prepare a document
template in [DOCX](#docx template file) format and use the [Jinja2]
template language to plug in variables from your interview.

For example, suppose you write this in the [DOCX](#docx template file)
template file:

> Hello, {% raw %}{{ user }}{% endraw %}.  This text is in **bold face**.
> 
> {% raw %}{%p if user.age_in_years() > 30 %}{% endraw %}<br>
> You cannot be trusted!<br>
> {% raw %}{%p endif %}{% endraw %}

The document content would look like this:

> Hello, John Doe.  This text is in **bold face**.
>
> You cannot be trusted!

From the [DOCX](#docx template file) template, you can generate PDF or
DOCX output.

## <a name="filling"></a>Method 3: filling in fields in a PDF

The third way to assemble documents is to generate [PDF](#pdf template
file) files using templates that you prepare in [Adobe Acrobat Pro] or
other software that can edit PDF form fields.  You put the template
file in the `data/templates` folder of a [package] (or the
["Templates" folder] in the [Playground]).  The `attachment` block
will take the template and "[fill in the blanks](#fill-in forms)"
using values from interview variables, providing the user with a
filled-in version of the template.

## <a name="comparison"></a>Comparison of the methods

Each method has benefits.

The advantage of the [DOCX](#docx template file) and [PDF](#pdf
template file) methods is that you have more direct, [WYSIWYG] control
over document formatting.

The advantage of the [Markdown](#from markdown) method is that you can
concentrate on the content and let **docassemble** handle the
formatting.  For example, there are automatic methods for generating
case captions in legal documents created from [Markdown], whereas if
you create your legal document in [DOCX](#docx template file) format,
you will need to construct your caption in the [.docx template
file](#docx template file) and make sure that it gets filled in
correctly.  The [Markdown](#from markdown) method allows for more
flexible formatting of the if/then/else statements within paragraphs.
In the [.docx template](#docx template file) method, you have to
write:

> I {% raw %}{% if employed %}have a job.{% else %}am unemployed.{% endif %}{% endraw %}

By contrast, [Markdown](#from markdown) treats single line breaks as
spaces, so you can write:

{% highlight text %}
I
% if employed:
have a job.
% else
am unemployed.
% endif
{% endhighlight %}

You may find it easier to read your if/then/else statements when you can
arrange them vertically in this fashion -- particularly when you have
nested if/else statements.

If you use the [PDF fill-in field](#pdf template file) method to
populate fields in a PDF file, you will have total control over
pagination, but you will need to worry about whether the user's
content will fit into the provided fields.  Also, the
[PDF fill-in field](#pdf template file) method requires that you write
an itemized list of fields in your document and the values you want
those fields to have.  [Markdown](#from markdown) documents and
[DOCX fill-in forms](#docx template file) are more flexible because
they do not require this itemization of fields.

All three of these methods make use of the [`attachment`] specifier to
indicate how a document should be made.

# <a name="from markdown"></a>Creating files from Markdown

## <a name="pdf"></a><a name="rtf"></a>Creating PDF and RTF files from Markdown

The following `attachment` block offers the user a PDF file and an RTF
file containing the phrase "Hello, world!"

{% include side-by-side.html demo="attachment-simple" %}

The `content` item can contain [Mako] and [Markdown].  [Pandoc]
converts the content into PDF, RTF, and HTML (the HTML is just for
previewing the document in the browser).

The PDF file will be called `Hello_World.pdf` and will look
like this in a PDF viewer (depending on the user's software):

![document screenshot]({{ site.baseurl }}/img/document-example-pdf.png){: .maybe-full-width }

The RTF file will be called `Hello_World.rtf` and will look
like this in a word processor (depending on the user's software):

![document screenshot]({{ site.baseurl }}/img/document-example-rtf.png){: .maybe-full-width }

If the user clicks the "Preview" tab, an HTML version of the document
will be visible:

![document screenshot]({{ site.baseurl }}/img/document-example-preview.png)

## <a name="docx"></a>Creating DOCX files from Markdown

**docassemble** can use [Pandoc] to convert [Markdown] into a
Microsoft Word .docx file.  These .docx files are not created by
default because they do not support all of the features that are
supported by [RTF](#rtf) and [PDF](#pdf) formats.  To generate .docx
files, specify `docx` as one of the [`valid formats`]:

{% include side-by-side.html demo="document-docx" %}

To customize document styles, headers, and footers in your .docx file,
see the [`docx reference file`] setting, discussed below.

There are some formatting features that [Pandoc] supports when
converting to .rtf that are not available when converting to .docx, so
you might want to use .rtf conversion for that reason.  However, the
.rtf format can be user-unfriendly, and in some circumstances it would
be better to have a .docx version.  Luckily, [LibreOffice] can convert
.rtf files to .docx format.  If you include `rtf to docx` as one of
the [`valid formats`], **docassemble** will convert [Markdown] to RTF
format and then use [LibreOffice] to convert the RTF file to .docx
format.  The result is that you get a .docx file instead of an .rtf
file.

{% include side-by-side.html demo="document-docx-from-rtf" %}

Note that you can also assemble .docx files from templates that you
compose in Mirosoft Word.  See the [`docx template file`] feature,
which is described [below](#docx template file).

## <a name="content file"></a>Reading Markdown content from separate files

If the content of your document is lengthy and you would rather not
type it into the interview [YAML] file as a `content` specifier within
an `attachment` block, you can import the content from a separate
file using `content file`:

{% include side-by-side.html demo="document-file" %}

The content of the [Markdown] file, [hello.md], is:

{% highlight text %}
Hello, world!
{% endhighlight %}

Files referenced with `content file` are assumed to reside in the
`data/templates` directory within the package in which the interview
[YAML] file is located.  You can specify filenames in other locations
by specifying a package name and path.  For example:

{% highlight yaml %}
content file: docassemble.demo:data/templates/complaint.md
{% endhighlight %}

The `content file` can also refer to a list of file names:

{% highlight yaml %}
content file:
  - introduction.md
  - jurisdiction.md
  - discussion.md
{% endhighlight %}

In this case, the content of multiple `content file` files will be
concatenated.

If `content file` refers to a dictionary in which the only key is
`code`, the `code` will be evaluated as [Python] code, and the result
will be used as the file.

{% include side-by-side.html demo="document-file-code" %}

In this example, the `code` evaluated to the name of a file in the
templates folder.  The `code` may also evaluate to a URL, [`DAFile`],
[`DAFileList`], [`DAFileCollection`], or [`DAStaticFile`].

## <a name="markup"></a>Formatting documents with special markup tags

In addition to using [Markdown] syntax, you can use
**docassemble**-specific markup tags to control the appearance of
documents.

* `[START_INDENTATION]` - From now on, indent the first line of every paragraph.
* `[STOP_INDENTATION]` - From now on, do not indent the first line of
  every paragraph.
* <a name="twocol"></a>`[BEGIN_TWOCOL] First column text [BREAK] Second column text
  [END_TWOCOL]` - Puts text into two columns.
* <a name="flushleft"></a>`[FLUSHLEFT]` - Used at the beginning of a paragraph to indicate
  that the paragraph should be flushed left and not indented.
* <a name="flushright"></a>`[FLUSHRIGHT]` - Used at the beginning of a paragraph to indicate
  that the paragraph should be flushed right and not indented.
* <a name="center"></a>`[CENTER]` - Used at the beginning of a paragraph to indicate that
  the paragraph should be centered.
* <a name="boldcenter"></a>`[BOLDCENTER]` - Like `[CENTER]` except that text is bolded.
* <a name="noindent"></a>`[NOINDENT]` - Used at the beginning of a
  paragraph to indicate that the first line of the paragraph should
  not be indented.
* <a name="indentby"></a>`[INDENTBY 1in]` - Used at the beginning of a paragraph to indicate
  that all the lines of the paragraph should be indented on the left.  In
  this example, the amount of indentation is one inch.  You can
  express lengths using units of `in` for inches, `pt` for points, or
  `cm` for centimeters.
* `[INDENTBY 1in 0.5in]` - This is like the previous tag, except it
  indents both on the left and on the right.  In this example, the
  amount of left indentation is one inch and the amount of right
  indentation is half an inch.
* <a name="border"></a>`[BORDER]` - Used at the beginning of a paragraph to indicate that
  the paragraph should have a box drawn around it.  (The border will
  only go around one paragraph; that is, the effect of `[BORDER]`
  lasts until the next empty line.  You can use `[NEWPAR]` in place of
  an empty line to extend the effect of the `[BORDER]` tag to
  another paragraph.)
* <a name="singlespacing"></a>`[SINGLESPACING]` - From now on,
  paragraphs should be single-spaced without indentation the first lines.
* <a name="oneandahalfspacing"></a>`[ONEANDAHALFSPACING]` - From now on, paragraphs should be
  one-and-a-half-spaced, with indentation of first lines.
* <a name="doublespacing"></a>`[DOUBLESPACING]` - From now on,
  paragraphs should be double-spaced, with indentation of first lines.
* <a name="triplespacing"></a>`[TRIPLESPACING]` - From now on,
  paragraphs should be triple-spaced, with indentation of first lines.
* <a name="tightspacing"></a>`[TIGHTSPACING]` - This is like
  `[SINGLESPACING]` except there is no spacing between paragraphs.
* <a name="nbsp"></a>`[NBSP]` - Insert a non-breaking space.
* <a name="endash"></a>`[ENDASH]` - Normally, `--` produces an en-dash, but if you want to
  be explicit, `[ENDASH]` will do the same thing.
* <a name="emdash"></a>`[EMDASH]` - Normally, `---` produces an em-dash, but if you want to
  be explicit, `[EMDASH]` will do the same thing.
* <a name="hyphen"></a>`[HYPHEN]` - Insert a hyphen.  Normally, `---` produces an em-dash, but if you want to
  be explicit, `[HYPHEN]` will do the same thing.
* <a name="blank"></a>`[BLANK]` - Insert `___________________`.
* <a name="blank"></a>`[BLANKFILL]` - Insert a wider version of 
  `__________________`.  In some output formats, this will fill the
  width of the area.
* <a name="pagebreak"></a>`[PAGEBREAK]` - Insert a manual page break.
* <a name="pagenum"></a>`[PAGENUM]` - Insert the current page number.
* <a name="sectionnum"></a>`[SECTIONNUM]` - Insert the current section number.
* <a name="newpar"></a>`[NEWPAR]` - Insert a paragraph break.  (Cannot be used within
  `[FLUSHLEFT]`, `[FLUSHRIGHT]`, `[CENTER]`, or `[BOLDCENTER]` environments.)
* <a name="skipline"></a>`[SKIPLINE]` - Skip a line (insert vertical space).  This is
  different from `[NEWPAR]` because `[NEWPAR]` breaks a paragraph but
  multiple calls to `[NEWPAR]` will not insert additional vertical
  space.  (Cannot be used within `[FLUSHLEFT]`, `[FLUSHRIGHT]`,
  `[CENTER]`, or `[BOLDCENTER]` environments.)
* <a name="br"></a>`[BR]` - Insert a line break.  `[BR]` is useful to use with
  environments like `[FLUSHLEFT]`, `[FLUSHRIGHT]`, `[CENTER]`, and
  `[BOLDCENTER]` that only apply to a single paragraph.  Within the
  `[BEGIN_TWOCOL]` environment, a standard [Markdown] paragraph break
  (pressing enter twice, i.e., leaving one blank line) has the same
  effect.
* <a name="tab"></a>`[TAB]` - Insert a tab (horizontal space), e.g., to indent the first
  line of a paragraph when it otherwise would not be indented.

This interview demonstrates these features:

{% include side-by-side.html demo="document-markup" %}

## <a name="pandoc"></a>Formatting documents with Pandoc templates and metadata

You can also control global formatting options by setting `metadata`
for the document.  These options are passed through to [Pandoc], where
they are applied to document templates.

{% highlight yaml %}
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    metadata:
      SingleSpacing: True
      fontsize: 10pt
    description: A document with a **classic** message
    content: |
      Hello, world!  Quisque ut tempus enim. Aliquam tristique
      placerat metus sollicitudin imperdiet. Donec eget dignissim
      libero, eu elementum justo.

      Maecenas iaculis mollis aliquam. Nullam vestibulum erat in
      sapien ultrices dignissim eu et turpis. Vivamus vestibulum felis
      eu sodales ornare. Nunc auctor sapien et porttitor posuere.
---
{% endhighlight %}

Metadata values can contain [Mako] template commands.

## <a name="metadata rtf pdf"></a>Metadata applicable to RTF and PDF files

* If you wish to use a standard document title, set the following:
  * `title`
  * `author` - a list
  * `date`
* `toc` - default is not defined.  If defined, a table of contents is
  included.
* `SingleSpacing` - set this to `True` for single spacing and no
  indentation of first lines of paragraphs.
* `OneAndAHalfSpacing` - set to `True` for 1.5 spacing, with
  indentation of first lines.
* `DoubleSpacing` - set this to `True` for double spacing with
  indentation of first lines.  This is the default.
* `TripleSpacing` - set this to `True` for triple spacing with
  indentation of first lines.
* `fontsize` - default is `12pt`.  Must be one of `10pt`, `11pt`, and `12pt`.
* `Indentation` - not defined by default.  By default, the first line
  of each paragraph is indented, unless `SingleSpacing` is set, in
  which case there is no indentation.
* `IndentationAmount` - not defined by default.  When double spacing
  is used, the default is 0.5 inches of first-line indentation in each
  paragraph.
* To set the text of headers and footers (which can contain [Mako] and
  [Markdown]), define one or more of the following:
  * `FirstFooterLeft`
  * `FirstFooterCenter`
  * `FirstFooterRight`
  * `FirstHeaderLeft`
  * `FirstHeaderCenter`
  * `FirstHeaderRight`
  * `FooterLeft`
  * `FooterCenter`
  * `FooterRight`
  * `HeaderLeft`
  * `HeaderCenter`
  * `HeaderRight`

## <a name="metadata pdf"></a>Metadata applicable to generated PDFs only

The following metadata tags only apply to PDF file generation.  To
change analogous formatting in RTF files, you will need to create your
own RTF document template (for more information on how to do that, see
the next section).

* `HangingIndent` - set this to `True` if you want text in lists to
  using hanging indentation.
* `fontfamily` - default is `Times New Roman`, but if you installed
  your system before version 0.4.13, the default is `mathptmx`, which
  is a variant of Times Roman.
* `lang` and `mainlang` - not defined by default.  If defined,
  [polyglossia] (for [XeTeX]) or [babel] is loaded and the language is
  set to `mainlang` if [polyglossia] is loaded and `lang` if [babel]
  is loaded.
* `papersize` - default is `letterpaper`.
* `documentclass` - default is `article`.
* `numbersections` - default is `True`.  If true, sections are
  numbered; if false, they are not.  (In [LaTeX], `secnumdepth` is
  set to 5, otherwise 0.)
* `geometry` - default is
  `left=1in,right=1in,top=1in,bottom=1in,heightrounded`.  These are
  options for the the [geometry] package that set the page margins.
* `TopMargin` - default is `1in`.  If you changed the top margin in
  `geometry`, change it here as well.
* `BottomMargin` - default is `1in`.  If you changed the bottom margin
  in `geometry`, change it here as well.
* `FooterSkip` - default is not defined.  If defined, will set the
  `footskip` option of the [geometry] package to control spacing
  between the footer and the text.
* `author-meta` - default is not defined.  Sets author item of PDF
  metadata using the `pdfauthor` option of [hyperref].
* `title-meta` - default is not defined.  Sets title item of PDF
  metadata using the `pdftitle` option of [hyperref].
* `citecolor` - default is not defined.  Sets the `citecolor` option
  of [hyperref], which will default to `blue` if this is not defined.
* `urlcolor` - default is not defined.  Sets the `urlcolor` option
  of [hyperref], which will default to `blue` if this is not defined.
* `linkcolor` - default is not defined.  Sets the `linkcolor` option
  of [hyperref], which will default to `magenta` if this is not defined.
* `abstract` - default is not defined.  If defined, it will include an
  article abstract in the standard [LaTeX] format.

## <a name="customization"></a>Additional customization of document formatting

You can exercise greater control over document formatting by creating
your own template files for [Pandoc].  The default template files are
located in the [`docassemble.base`] package in the
`docassemble/base/data/templates` directory.  The files include:

* `Legal-Template.tex`: this is the [LaTeX] template that [Pandoc]
  uses to generate PDF files.
* `Legal-Template.yml`: default [Pandoc] metadata for the
  `Legal-Template.tex` template, in [YAML] format.  Options passed
  through `metadata` items within an [`attachment`] will append or
  overwrite these default options.
* `Legal-Template.rtf`: this is the template that [Pandoc] uses to
  generate RTF files.
* `Legal-Template.docx`: this is the reference file that [Pandoc] uses
  to generate DOCX files.  You can edit this file to change default
  styles, headers, and footers.

To use your own template files, specify them using the following
options to [`attachment`]:

* <a name="initial yaml"></a>`initial yaml`: one or more [YAML] files from which [Pandoc]
  metadata options should be gathered.  If specified, the default file
  `Legal-Template.yml` is not loaded.  If specifying more than one
  file, use [YAML] list syntax.
* <a name="additional yaml"></a>`additional yaml`: one or more [YAML] files from which [Pandoc]
  metadata options should be gathered, in addition to whatever options
  are loaded through `initial_yaml`.  This can be used to load the
  metadata in `Legal-Template.yml` but to overwrite particular values.
  If specifying more than one file, use [YAML] list syntax.
* <a name="template file"></a>`template file`: a single `.tex` file to be used as the [Pandoc]
  template for converting [Markdown] to PDF.
* <a name="rtf reference file"></a>`rtf template file`: a single `.rtf` file to be used as the [Pandoc]
  template for converting [Markdown] to RTF.
* <a name="docx reference file"></a>`docx reference file`: a single `.docx` file to be used as the
  [Pandoc] docx reference file for converting [Markdown] to DOCX.

Filenames are assumed to reside in the `data/templates` directory
within the package in which the interview [YAML] file is located.  You
can specify filenames in other packages by including a reference to a
package and directory.  For example:

{% highlight yaml %}
template file: docassemble.demo:data/templates/MyTemplate.tex
{% endhighlight %}

Here is an example:

{% highlight yaml %}
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: Response to Motion for Summary Judgment
    filename: Summary_Judgment_Response
    additional yaml:
      - docassemble.pennsylvania:data/templates/legal_format.yml
      - docassemble.pennsylvania:data/templates/pleading_format.yml
    template file: summary_judgment_template.tex
    rtf template file: summary_judgment_template.rtf
    content: |
      The court should decide in my favor.
---
{% endhighlight %}

If this question appears within a [YAML] file located in the package
`docassemble.pa_family_law`, the assumption is that the files
`summary_judgment_template.tex` and `summary_judgment_template.rtf`
will exist in the directory `docassemble/pa_family_law/data/templates`
within that package.

If you want to use a custom template for all the attachments in a
given interview, you do not have to specify the same values for every
attachment.  Instead, you can set attachment template options that
will be applied to all attachments in the interview:

{% highlight yaml %}
---
attachment options:
  additional yaml:
    - docassemble.pennsylvania:data/templates/legal_format.yml
    - docassemble.pennsylvania:data/templates/pleading_format.yml
  template file: summary_judgment_template.tex
  rtf template file: summary_judgment_template.rtf
---
{% endhighlight %}

If you use an interview-wide `attachment options` block to set
defaults, you can override those defaults for a particular attachment
by providing specific options within the question block.

# <a name="docx template file"></a>Assembling DOCX templates

You can assemble documents from DOCX template files by referring to a
`docx template file`.

{% include side-by-side.html demo="docx-template" %}

This allows you to use [Microsoft Word] to design your document and
apply formatting.  **docassemble** will simply "fill in the blanks."
(This is in contrast to the method of
[using `docx` as one of the `valid formats`], described
[above](#docx).  When you use that method, you assemble a document
from scratch by writing [Markdown] text that is then converted to
DOCX format.)

The file referenced with `docx template file` is assumed to reside in
the `data/templates` directory of your package, unless a specific
package name is specified.  For example, you could refer to a DOCX
file in another package by writing:

{% highlight yaml %}
docx template file: docassemble.missouri-family-law:data/templates/form.docx
{% endhighlight %}

In the example above, the [letter_template.docx] file contains the
following text:

![letter template source]({{ site.baseurl }}/img/letter_template_source.png){: .maybe-full-width }

If you give `docx template file` a [YAML] list of files, the files
will be concatenated and then assembled.  (Note that some DOCX
features can be lost in the process of concatenation.)

The `docx template file` feature relies heavily on the [Python]
package known as [`python-docx-template`].  This package uses the
[Jinja2] templating system to indicate fields in the DOCX file and
logic based on Python expressions.  [Jinja2] is different from the
[Mako] templating system, which **docassemble** primarily uses, but it
serves the same general purpose.

When you work on DOCX templates, be careful not to confuse the rules
of [Mako] and [Jinja2].  The biggest difference between the formats is
that [Mako] uses the syntax `${ variable_name }`, while [Jinja2] uses
the syntax `{% raw %}{{ variable_name }}{% endraw %}`.

In [Mako], you would write an if/else statement like this:

{% highlight markdown %}
You may wish to distribute your property to your
% if user.child.number() > 0:
heirs.
% else:
friends.
% endif
{% endhighlight %}

In [Jinja2], you would write:

{% highlight text %}
You may wish to distribute your property to your 
{% raw %}{% if user.child.number() > 0 %}heirs.{% else %}friends.{% endif %}{% endraw %}
{% endhighlight %}

Another big difference is that [Jinja2] does not allow you to use
[Python built-in functions] like `max()` and `any()`, or built-in
Python names like `None`.  Instead, it provides you with a variety of
[filters] and [tests].  For example, instead of writing `You have {%
raw %}{{ len(favorite_fruits) }}{% endraw %} favorite fruits`, you
would write `You have {% raw %}{{ favorite_fruits | length }}{% endraw
%} favorite fruits`.  Instead of writing `{% raw %}{% if
result_of_api_call is None %}N/A{% endif %}{% endraw %}` you would
write `{% raw %}{% if none(result_of_api_call) %}N/A{% endif %}{%
endraw %}`

Also, the [`python-docx-template`] package uses a slightly modified
version of the [Jinja2] syntax to account for the fact that it is
being used inside of a DOCX file.  The standard [Jinja2] way of
writing a "for loop" is:

{% highlight text %}
{% raw %}{% for item in fruit_list %}
{{ item }} is a type of fruit.
{% endfor %}{% endraw %}
{% endhighlight %}

In a DOCX template, however, this will result in extraneous line
breaks.  You can avoid this by writing:

{% highlight text %}
{% raw %}{%p for item in fruit_list %}
{{ item }} is a type of fruit.
{%p endfor %}{% endraw %}
{% endhighlight %}

The `p` modifier indicates that the paragraph containing the `{% raw
%}{%p ... %}{% endraw %}` statement should be removed from the
document.  When you edit the spacing of paragraphs in your DOCX
template file, you need to edit the paragraph spacing of paragraphs
that do _not_ contain `{% raw %}{%p ... %}{% endraw %}` statements.
You may need to change both the spacing after a paragraph and the
spacing before a paragraph in order to get the results you want.
Other modifiers besides `p` include `tr` for table rows, `tc` for
table columns, and `r` for "rich text."

If you have a bulleted or numbered list in a DOCX template and you want
to display an item in the list conditionally (using an if .. endif statement),
you should use the  `{% raw %}{%p if ... %}{% endraw %}` syntax. Place 
the `{% raw %}{%p if ... %}{% endraw %}` and
the `{% raw %}{%p endif %}{% endraw %}` statements on their own lines in the list. 
If you place the `{% raw %}{%p endif %}{% endraw %}` on the same line
as the `{% raw %}{%p if... %}{% endraw %}` line, you may get an error about
a missing `endif` statement, since the `p` modifier could cause the 
`endif` statement to be deleted before it is processed.

The following code in a DOCX template:

> 1. {% raw %}{% if my_var == 'A' %}{% endraw %}The variable is A.{% raw %}{% endif %}{% endraw %}
> 2. item2
> 3. item3

will result in the following output if `my_var` is not equal to `'A'`:

> 1. 
> 2. item2
> 3. item3

Instead, if you write:

> 1. {% raw %}{%p if my_var == 'A' %}{% endraw %}
> 2. The variable is A.
> 3. {% raw %}{%p endif %}{% endraw %}
> 4. item2
> 5. item3

The output will be:

> 1. item2
> 2. item3

The `p` prefix in `{% raw %}{%p ... %}{% endraw %}` means "process the
Jinja2 in this paragraph, but don't actually include this paragraph in
the assembled document."

You will need to do something similar when using [tables](#docx
tables) in your DOCX file.  For example, when using a "for" loop over
the rows of a table, you would include two extra rows:

| Name                                               | Age                                             |
|----------------------------------------------------|------------------------------------------------ |
| {% raw %}{%tr for child in children %}{% endraw %}                                                   |
| {% raw %}{{ child }}{% endraw %}                   | {% raw %}{{ child.age_in_years() }}{% endraw %} |
| {% raw %}{%tr endfor %}{% endraw %}                                                                  |
{: .table .table-bordered }

The `tr` prefix in `{% raw %}{%tr ... %}{% endraw %}` means "process
the Jinja2 in this row, but don't actually include this row in the
assembed document."

When using a "for" loop over the columns of a table, you would include
extra columns:

| Name                               | {% raw %}{%tc for inc_type in inc_types %}{% endraw %} | {% raw %}{{ inc_type }}{% endraw %}                           | {% raw %}{%tc endfor %}{% endraw %} |
|------------------------------------|--------------------------------------------------------|---------------------------------------------------------------| ------------------------------------|
| {% raw %}{{ grantor }}{% endraw %} | {% raw %}{%tc for inc_type in inc_types %}{% endraw %} | {% raw %}{{ currency(grantor.income[inc_type]) }}{% endraw %} | {% raw %}{%tc endfor %}{% endraw %} |
| {% raw %}{{ grantee }}{% endraw %} | {% raw %}{%tc for inc_type in inc_types %}{% endraw %} | {% raw %}{{ currency(grantee.income[inc_type]) }}{% endraw %} | {% raw %}{%tc endfor %}{% endraw %} |
{: .table .table-bordered }

The `tc` prefix in `{% raw %}{%tc ... %}{% endraw %}` means "process
the Jinja2 in this table cell, but don't actually include this table
cell in the row."

For more information about tables in DOCX files, see the [subsection
on tables](#docx tables) below.

<a name="signature docx"></a>Images can be inserted into DOCX files.
This is illustrated in the example above: the variable
`user.signature` is a graphics image (an image of the user's signature
created with the [`signature` block]).  You can insert [`DAFile`],
[`DAFileList`], and [`DAStaticFile`] objects into DOCX files in a
similar way.  (See [`include_docx_template()`] below for instructions
on inserting other DOCX files inside a DOCX file.)  If you insert a
PDF file, it will be converted into a series of page images.  If you
insert a text file, the raw text will be included.  You can also use
the `[FILE ...]` markup syntax to [insert an image].  Do not mix image
references with other text inside of a single field (e.g., by writing
`{% raw %}{{ "Here is my dog: " + a_file }}{% endraw %}`.  Image
references need to be by themselves inside of `{% raw %}{{ }}{% endraw
%}` brackets.

Note that the paragraph spacing of the paragraph into which you insert
an image may affect the appearance of the image.  For example, if the
line spacing of the paragraph is fixed, the image that you insert will
be cropped if it is taller than the line spacing.  To prevent the
image from being cropped, select a flexible line spacing like "single"
or "double."

Because of a limitation in the [`python-docx-template`] package,
images cannot be inserted into headers, footers, or footnotes.

When you insert text into a DOCX file using `{% raw %}{{ }}{% endraw
%}` brackets, any newlines in the text you are inserting will be
treated as spaces, and any [Markdown] formatting codes will be passed
through literally.  If you want your newlines and [Markdown]
formatting codes to translate into DOCX formatting, see the section
below on [inserting multi-line or formatted text into a single field
in a DOCX file].

When you use `docx template file`, the user is provided with both a
PDF file and a DOCX file.  The PDF file is generated by converting
the DOCX file to PDF format using [LibreOffice].  To suppress the
creation of the PDF version, you can add a [`valid formats`]
specifier.

Here is an example that demonstrates how to use [`DAList`] and [`DADict`]
[objects] in a DOCX template and using [Jinja2] templating code.

{% include side-by-side.html demo="docx-jinja2-demo" %}

The `docx-jinja2-demo.docx` file looks like this:

![docx jinja2 source]({{ site.baseurl }}/img/docx-jinja2-demo.png){: .maybe-full-width }

For more information on using [Jinja2] in DOCX templates, see the
documentation of [`python-docx-template`].

The section below on [using code to find a template file] explains how
you can use code to determine what template file to use with `docx
template file`.

## <a name="include_docx_template"></a>Inserting other DOCX files into DOCX templates

You can include the paragraphs of a DOCX file inside of your DOCX
template.

![include_docx_template]({{ site.baseurl }}/img/include_docx_template.png)

See the documentation for the [`include_docx_template()`] function for
more information.  Note that it is important to use the `p` form of
[Jinja2] markup, by itself on a line in the document:

> {% raw %}{{p include_docx_template('sub_document.docx') }}{% endraw %}

If you have a DOCX file in the form of a [`DAFile`] or [`DAFileList`]
object, then you can do:

> {% raw %}{{p include_docx_template(the_file) }}{% endraw %}

or just

> {% raw %}{{p the_file }}{% endraw %}

## <a name="docx tables"></a>Inserting tables into DOCX templates

You can assemble tables in a DOCX template using a [Jinja2] "for loop."

Here is an example.  The DOCX template looks like this:

![table template source]({{ site.baseurl }}/img/table_template.png){: .maybe-full-width }

Note that the row that should be repeated is sandwiched between two
rows containing `for` and `endfor` [Jinja2] statements.  Both of these
statements use the `tr` prefix.  These two rows, which span the width
of the table, will not appear in the final output.  The final output
will look something like this:

![table template result]({{ site.baseurl }}/img/table_template_result.png){: .maybe-full-width }

In this example, each row corresponds to an item in a [Python dict]
called `seeds_of_fruit`.  Here is an example of an interview that
gathers items into a [`DADict`] called `seeds_of_fruit` and provides
the DOCX file.

{% include side-by-side.html demo="docx-template-table" %}

For more information about gathering items into a [`DADict`] object,
see the [Dictionary] subsection of the [Groups] section of the
documentation.

Your DOCX tables can also loop over the columns of a table.

![table columns template source]({{ site.baseurl }}/img/docx-table-columns-template.png){: .maybe-full-width }

![table columns template result]({{ site.baseurl }}/img/docx-table-columns-assembled.png){: .maybe-full-width }

The following interview, which uses the template [docx-table-columns.docx],
illustrates this.

{% include side-by-side.html demo="docx-table-columns" %}

## <a name="particfields"></a>Passing values for particular fields

By default, all of the variables in your interview will be available
in the DOCX template.  If your DOCX template uses different variable
names than are present in your interview, you can use the `fields` or
`field code` specifiers to indicate a mapping between variable names
in the DOCX template and the values that you want to be filled in.
This operates much like the [PDF fill-in fields](#pdf template file)
feature.  If a variable in the DOCX file is not explicitly
defined in the `fields` or `field code` list, definitions will be
sought in the interview answers.

The content of `fields` is converted into a data structure, which is
passed to the `render()` method of [`python-docx-template`].  The data
structure needs to be a [Python dict], but it can contain other data
types.  For example, in this interview, `fields` contains a list of
ingredients:

{% include side-by-side.html demo="docx-recipe" %}

In your DOCX file, you will need to use appropriate [Jinja2] syntax
in order to process the list of ingredients.  Here is an example of a
DOCX file that uses the above data structure:

![recipe template source]({{ site.baseurl }}/img/recipe_template.png){: .maybe-full-width }

## <a name="raw field variables"></a>Turning off automatic conversion of DOCX variables

Normally, all values that you transfer to a DOCX template using
`fields`, `field variables`, and `field code` are converted so that
they display appropriately in your DOCX file.  For example, if the
value is a [`DAFile`] graphics image, it will be converted so that it
displays in the DOCX file as an image.  Or, if the value contains
[document markup] codes that indicate line breaks, these will display
as actual line breaks in the DOCX file, rather than as codes like
`[BR]`.

However, if your DOCX file uses [Jinja2] templating to do complicated
things like for loops, this conversion might cause problems.

For example, suppose you have a variable `vegetable_list` that is
defined as a [`DAList`] with items `['potatoes', 'beets']`, and you
pass it to a DOCX template as follows.

{% highlight yaml %}
event: document_shown
question: |
  Here are your instructions.
attachment:
  docx template file: instruction_template.docx
  field variables:
    - vegetable_list
{% endhighlight %}

This will work as intended if your template uses `vegetable_list` in a
context like:

{% highlight text %}
make sure to bring {% raw %}{{ vegetable_list }}{% endraw %} to the party
{% endhighlight %}

This will result in:

> make sure to bring potatoes and beets to the party

When the [`DAList`] is converted, the [`.comma_and_list()`] method is
automatically applied to make the data structure "presentable."

However, suppose you wanted to write:

{% highlight text %}
{% raw %}{%p for vegetable in vegetable_list: %}
Don't forget to bring {{ vegetable }}!
{%p endfor %}{% endraw %}
{% endhighlight %}

In this case, since the variable `vegetable_list` has been converted
into a literal piece of text, `potatoes and beets`, the `for` loop
will loop over each character, not over each vegetable.  You will get:

> Don't forget to bring p!
>
> Don't forget to bring o!
>
> Don't forget to bring t!
>
> Don't forget to bring a!
>
> Don't forget to bring t!

and so on.

You can prevent the conversion of `vegetable_list` into text by using `raw
field variables` instead of `field variables`.  For example:

{% highlight yaml %}
event: document_shown
question: |
  Here are your instructions.
attachment:
  docx template file: instruction_template.docx
  raw field variables:
    - vegetable_list
{% endhighlight %}

Now, the `vegetable_list` variable in the DOCX template will be a
real list that [Jinja2] can process.  The output will be what you expected:

> Don't forget to bring potatoes!
> Don't forget to bring beets!

The conversion to text is also done if you use `field code` or `code`
to pass variables to a DOCX template.  In order to pass variables in
"raw" form using `field code` or `code`, you can wrap the code in the
[`raw()`] function.  For more information, see the
[documentation for the `raw()` function].

## <a name="markdown to docx"></a>Inserting multi-line or formatted text into a single field in a DOCX file

If you insert text into a [`docx template file`] using `{% raw %}{{
the_variable }}{% endraw %}`, and the the text you are inserting
contains newlines, the newlines will show up as spaces in the DOCX
file.  Also, if the text contains [Markdown] formatting, it will be
inserted into the DOCX file literally.

If the text that you want to insert contains newlines, and you want
the newlines to be reflected in the DOCX file as manual line breaks,
write `{% raw %}{{ the_variable | manual_line_breaks }}{% endraw %}`
instead.

If the text that you want to insert contains [Markdown] formatting,
and you want that formatting to be translated into DOCX formatting,
insert it using `markdown` [Jinja2] filter or the `inline_markdown`
filter.

It is important that you understand the difference between
character-level content and paragraph-level content.  You see this
distinction in Microsoft Word when you use "Styles."  Some Styles are
character-level or "inline" because they only affect things like bold,
italics, underline, and color.  Other Styles are paragraph-level
because they affect things like paragraph indentation, bullets, or
numbering.  A paragraph break is a paragraph-level concept, whereas a
manual line break is a character-level concept.

Under the rules of [`python-docx-template`], you need to use the
prefix `{% raw %}{{r{% endraw %}` when the contents return
character-level DOCX text, and you need to use `{% raw %}{{p{% endraw
%}` when the contents return paragraph-level DOCX text.  It is very
important that you get this right, because the symptoms of a mistake
are confusing: the contents may simply disappear, or the DOCX file may
get corrupted because you are inserting bad XML.

The `markdown` filter will return paragraph-level text, and the
`inline_markdown` filter will return character level text.  However,
this depends on whether you have enabled `new markdown to docx: True`
in your [Configuration].  If you created your server relatively
recently (since April 2020), this will already be there in your
[Configuration], but if your server is relatively old, you will need
to add `new markdown to docx: True` to your [Configuration] to upgrade
to the "new" behavior.  Just keep in mind that when you make this
change, you may have to update your `docx template file`s.  (That's
why you need to opt in to the new system.)

Under the `new markdown to docx: True` system, the `markdown` filter
inserts paragraph-level text, and needs to be used with `{% raw
%}{{p{% endraw %}`.  Under the "old" Markdown-to-DOCX system, the
`markdown` filter only inserted character-level text, and it needed to
be used with `{% raw %}{{r{% endraw %}`.  The rest of the
documentation will assume that you are using `new markdown to docx:
True`, which you should.  So if you have not made that change yet, you
should do so.

If you want to insert [Markdown]-formatted text within a paragraph
(character-level text), you can use the `inline_markdown` filter:

> {% raw %}{{r the_text \| inline_markdown }}{% endraw %}

With this filter, the text in `the_text` will be inserted as
characters into the existing paragraph.  If the [Markdown] contains
paragraph breaks, the paragraph breaks will be manual newlines rather
than actual paragraph breaks.

If you are insert a `template` variable into a DOCX file, the
`markdown` filter is applied automatically (and how it works depends
on the `new markdown to docx` setting).  Suppose your YAML has:

{% highlight yaml %}
template: disclaimer
content: |
  I disclaim **everything**.
  
  I have zero liability.  ZERO.
{% endhighlight %}

In your DOCX file, you would write:

> {% raw %}{{p disclaimer }}{% endraw %}

Since the `{% raw %}{{p{% endraw %}` prefix is being used, this needs
to be by itself in a DOCX paragraph.

If you have a `template` but you want the contents to be inserted as
character-level text, you can write

> Here is the disclaimer.
> {% raw %}{{r disclaimer.show_as_markdown() }}{% endraw %}
> There you have it.

A `template` block will create a [`DALazyTemplate`] object, and
`.show_as_markdown()` is one of the methods of the [`DALazyTemplate`]
class.  It is a variant on the method `.show()`, which is the method
that is called implicitly when you reduce a [`DALazyTemplate`] object
to a textual form.

Note that according to the [Markdown] standard, a single newline does
not break a paragraph; you need two newlines to break a paragraph.  If
you want to convert single newlines into paragraphs breaks, there is
another [Jinja2] filter that can help.  Instead of writing `the_text |
markdown`, write `the_text | paragraphs | markdown`.  The `paragraphs`
filter runs the text through the [`single_to_double_newlines()`]
function.

Another way to insert formatted text using [Jinja2] is to use the
"rich text" feature of [`python-docx-template`].  The `RichText`
[Jinja2] filter allows you to include line breaks inside of variable
text:

> The swift brown {% raw %}{{r animal \| RichText }}{% endraw %}
> jumped over the lazy dog.

Using this filter, any newline (`\n`) in `animal` will be converted
into a manual line break and any `\a` character will be converted into
a paragraph break.  When using `RichText`, you must always use the `r`
prefix, `{% raw %}{{r ... }}{% endraw %}`.

## <a name="filters"></a>Jinja2 filters

[Jinja2] does not allow you to write every kind Python expression, the
way that [Mako] does; there are limitations, such as not being able to
refer to certain built-in names like `None`.  [Jinja2] allows you to
do sophisticated things, however, but it encourages the use of
"filters" rather than the writing of [Python] code.  There are a
number of [built-in filters] in [Jinja2] that you can use.  In
addition, there are some **docassemble**-specific filters, which are
either discussed above or are the names of [functions].

* `RichText`
* `add_separators`
* `alpha`
* `capitalize`
* `comma_and_list`
* `comma_list`
* `country_name`
* `currency`
* `fix_punctuation`
* `inline_markdown`
* `manual_line_breaks`
* `markdown`
* `nice_number`
* `ordinal_number`
* `ordinal`
* `paragraphs`
* `phone_number_formatted`
* `phone_number_in_e164`
* `redact`
* `roman`
* `salutation`
* `single_paragraph`
* `title_case`
* `verbatim`
* `word`

<a name="register_jinja_filter"></a>You can also write your own
filters. To do so, you need to write a module file.  For example, here
is a module file that creates a filter called `no_ssn` for removing
Social Security Numbers.

{% highlight python %}
    # pre-load
    import re
    from docassemble.base.util import register_jinja_filter

    def remove_ssn(text):
        return re.sub(r'[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9][0-9][0-9]', 'XXX-XX-XXXX', text)

    register_jinja_filter('no_ssn', remove_ssn)
{% endhighlight %}

For this to work, the module file has to be installed on the server or
present in the Modules folder of a user's Playground.

The `register_jinja_filter()` function is similar to
[`update_language_function()`] in that it needs to run when the server
starts and the server loads modules.  That is why the line `#
pre-load` is at the top.  Also note that `register_jinja_filter` is
not exported when you do `from docassemble.base.util import *`.

## <a name="macros"></a>Inserting blocks of text more than once in a document

[Jinja2] supports the use of "[macros]," which are like [Python]
commands except that instead of running [Python] code, they insert
content into the document.

Here is an example of a document in which a paragraph following a
particular template needs to be inserted multiple times.  The `docx
template file` is a file called [`team.docx`], which contains the
following content:

![team.docx screenshot]({{ site.baseurl }}/img/macros_screenshot.png){: .maybe-full-width }

Note the use of `{% raw %}{%p macro ... %}{% endraw %}` and 
`{% raw %}{%p endmacro ... %}{% endraw %}`.

The [macro] in this document contains two paragraphs with [Jinja2]
statements.  The DOCX formatting defined in the [macro] will be
reproduced wherever the macro is inserted.

Here is an interview that assembles a document from [`team.docx`]:

{% include demo-side-by-side.html demo="macros" %}

You can also define a [macro] that includes character-level text.

> {% raw %}{% macro say_hello(friend) %}Hello, {{ friend }}!{% endmacro %}{% endraw %}

Then you can use the macro by calling it inside brackets:

> {% raw %}{{ say_hello(plaintiff) }}{% endraw %}  How are you today?

The difference from the previous example is that the `p` prefix is not
used.

When you need to insert text programmatically into different parts of
a DOCX document, using a [macro] in [Jinja2] is generally preferable
to inserting a [`template`] or [Markdown-formatted text].  It is a
good general practice to use the DOCX file to control anything
relating to document formatting.  Keep in mind that [Markdown] was not
designed for typesetting; it was designed for indicating the general
meaning of parts of text in a form-independent manner.

## <a name="update references"></a>Using tables of contents and other references in DOCX files

If you are using `docx template file` and your template file uses a
table of contents or other page references that will change depending
on how the document is assembled, set `update references` to `True`.

{% include demo-side-by-side.html demo="update-references" %}

This will cause [LibreOffice] to update all of the references in the
document before saving it and converting it to PDF.

You can also set `update references` to a [Python] expression.  If the
expression evaluates to a `True` value, the references will be updated.

If `update references` is not specified, the default behavior is not
to update the references.

# <a name="pdf template file"></a>Filling PDF templates

If you have a PDF file that contains fillable fields (e.g. fields
added using [Adobe Acrobat Pro] or a similar application),
**docassemble** can fill in the fields of the PDF file using
information from an interview and provide the user with a copy of that
PDF file with the fields filled in.  To do this, use the
[`attachment`] specifier as above, but instead of providing `content`
or `content file`, provide a `pdf template file` and a dictionary of
`fields`.

For example, here is an interview that populates fields in a file
called [sample-form.pdf]:

{% include side-by-side.html demo="pdf-fill" %}

The `pdf template file` is assumed to reside in the `data/templates`
directory of your package, unless a specific package name is
specified.  For example, you could refer to a file in another package
by writing:

{% highlight yaml %}
pdf template file: docassemble.missouri-family-law:data/templates/form.pdf
{% endhighlight %}

In [Adobe Acrobat Pro]'s "Add or Edit Fields" mode, the PDF file looks
like this:

![sample form]({{ site.baseurl }}/img/sample-form.png){: .maybe-full-width }

The `fields` must be in the form of a [YAML] list of dictionaries, or
a single dictionary.  The names of the fields listed in `fields` must
correspond _exactly_ with the names of the fields in the PDF file.
Luckiliy, there is [a tool] that will help you extract the literal
field names from a PDF file.

If your PDF document has many fields, it is strongly recommended that
you use [Adobe Acrobat Pro] to give each field a concise, meaningful,
and accurate field name (as well as a helpful tooltip).  [Adobe
Acrobat Pro] has a feature for automatically assigning names to
fields, but this tool often assigns incorrect names.  You should go
through this process _before_ you [generate] the `attachment`
specifier for filling fields in the PDF file.

While it is legal for a PDF file to contain more than one field with
the same name, please note that **docassemble** is unable to populate
such fields.  You must give each field in your PDF file a unique name.

When writing the values of the fields, you can use [Mako], but not
[Markdown].  If you use [Markdown], it will be interpreted literally.

The section below on [passing values using code](#template code)
explains alternative ways that you can populate the values of fields
in a PDF file.

You have a choice whether to list fields as a single dictionary or a
list of dictionary items.  Providing the fields in the form of a list
is usually preferable because it provides an order in which the fields
should be evaluated; if you only provide a single dictionary, the
items will be evaluated in a random order.

The section below on [using code to find a template file] explains how
you can use code to determine what template file to use with `pdf
template file`.

## <a name="editable"></a>Making PDF files non-editable

By default, the PDF files created by filling in
forms in a `pdf template file` can be edited by the user; the fill-in
form boxes will still exist in the resulting document.

If you want to prevent users from editing the forms created through
`pdf template file`, set the `editable` specifier to `False`.  For
example:

{% include side-by-side.html demo="pdf-fill-not-editable" %}

## <a name="signature"></a>How to insert signatures or other images into fillable PDF files

To add a signature or other image to a fillable PDF file, use
[Adobe Acrobat Pro] to insert a "Digital Signature" into the document
where you want the signature to appear.  Give it the height and width
you want the image to have.  Give the field a unique name.

Then, the image will be a field, just like a checkbox or a text box is
a fill-in field.  In your `pdf template file`, set the field to `${
user.signature }` or another reference to an image.  **docassemble**
will trim whitespace from the edges of the image and fit the image
into the "Digital Signature" box.

For example, here is an interview that populates text fields and
inserts a signature into the template [Transfer-of-Ownership.pdf]:

{% include side-by-side.html demo="pdf-fill-signature" %}

It is important that each "Digital Signature" field have a unique
name.  If there is more than one field in the PDF template with the
same name, **docassemble** will not be able to locate it.  If you want
to insert the same signature in more than one spot in a document, you
can do so as long as each "Digital Signature" field has a different
name.  For example:

{% highlight yaml %}
    fields:
      - first signature: ${ user.signature }
      - second signature: ${ user.signature }
      - third signature: ${ user.signature }
{% endhighlight %}

## <a name="template code"></a>Passing values using code

When you use the `fields` specifier with [`pdf template file`], you
have to use [Mako] in order to pass the values of interview variables
to the template.  For example, suppose you have a PDF file with these
fields:

![fruit template]({{ site.baseurl }}/img/fruit_template.png){: .maybe-full-width }

You can use an interview like this to populate the fields:

{% include side-by-side.html demo="fruit-template-alt-1" %}

However, this is a bit punctuation-heavy and repetitive.  As an
alternative, you can use the `field variables` specifier to list the
variables you want to pass:

{% include side-by-side.html demo="fruit-template-alt-2" %}

This will have the same effect.

The `field variables` specifier only works when your variable in the
template has the same name as the variable in your interview, and when
you do not need to perform any transformations on the variable before
passing it to the template.

The `field variables` specifier, and other specifiers described in
this subsection, work both with [`pdf template file`] and
[`docx template file`].  But note that since the
[.docx assembly process](#docx template file) by default accesses all
of your interview variables, you will normally only need to use `field
variables` with PDF templates.

Suppose you want to pass the results of functions or methods to a 
template that looks like this:

![letter template]({{ site.baseurl }}/img/letter.png){: .maybe-full-width }

One way to pass the results of functions or methods it is to use
`fields`, where every value is a [Mako] variable reference containing
code:

{% include side-by-side.html demo="pdf-template-alt-1" %}

You can achieve the same result with less punctuation by using the
`field code` specifier:

{% include side-by-side.html demo="pdf-template-alt-2" %}

There is still another way of passing values to a template: you can
include a `code` specifier that contains [Python] code that evaluates
to a [Python dict] in which the keys are the names of variables in the
template, and the values are the values you want those variables to
have.  For example:

{% include side-by-side.html demo="pdf-template-alt-3" %}

Note that the `code` must be a single [Python] expression, not a list
of statements.  It can be difficult to cram a lot of logic into a
[Python] expression, so you may want to create a variable to hold the
values.  For example:

{% include side-by-side.html demo="pdf-template-alt-4" %}

Note that the use of the [`reconsider`] modifier is important here.
[Remember] that **docassemble** will only ask a question or run code
when it encounters an undefined variable.  If the recipient's address
is undefined when **docassemble** tries to run the code above,
**docassemble** will ask a question to gather it, but once that
question is answered, **docassemble** will have no reason to run the
above code again because `letter_variables` will already be defined --
albeit in an incomplete state, with a `letter_date` item and a
`subject_line` item but without a `recipient_address` item.  Setting
`reconsider` to `True` ensures that whenever a screen in the interview
needs to know the value of `letter_variables`, that value will be
"reconsidered"---treated as undefined---and the code above will be
re-run in order to obtain a fresh definition of `letter_variables`.

The `fields`, `field variables`, and `field code` specifiers are not
mutually exclusive.  When they are used together, they supplement each
other.  (In DOCX templates, however, the fields do not supplement the
values of variables in the interview dictionary; if you use `fields`,
`field variables`, and `field code`, **docassemble** will not use the
interview dictionary as a whole.)

Here is a variation on the original PDF fill-in example [above](#pdf
template file) that uses `code` to supplement the values of `fields`:

{% include side-by-side.html demo="pdf-fill-code" %}

Like the [Mako] tag `${ ... }`, the `fields`, `field variables`, and
`field code` specifiers will convert the values of your variables to a
format suitable for printing.  If you are using the DOCX template
format and you only use the `{% raw %}{{ ... }}{% endraw %}` syntax in
your template, this will always be appropriate.  But if you want to
use "for loops" and other features of [Jinja2] when passing variables
using `fields`, `field variables`, or `field code`, you should read
the next section, which explains how to pass variables in "raw" format
to the template.

<a name="decimal places"></a>When using `field code`, `code`, or
`field variables` to define your fields, there is a shortcut for
formatting decimal numbers: set the option `decimal places` to the
number of decimal places you want to use.

{% highlight yaml %}
---
attachment:
  name: My Document
  filename: my_document
  pdf template file: letter_template.pdf
  variable name: the_document
  decimal places: 2
---
{% endhighlight %}

By default, when `decimal places` is not used, numbers are converted
to text using the standard [Python] method, which uses at least one
decimal place.

Note that `decimal places` does nothing for variables passed to your
template with a method other than `field code`, `code`, or `field
variables`.  In other cases, you will need to manually format your
numbers, for example by writing something like `${ '%.3f' %
ounces_of_gold }`.

<a name="skip undefined"></a>If you want to assemble a PDF with `pdf
template file` and produce a file even if some of the variables needed
for the fields are undefined, set `skip undefined` to `True`.  If
`skip undefined` is true, then blanks will be substituted for any
fields for which a value cannot be determined due to a variable being
undefined.  You can also set `skip undefined` to a Python expression
that evaluates to a true or false value.  This setting also works with
`docx template file` when `field code`, `code`, or `field variables`
is used.

The `skip undefined` setting should only be used if the document does
not need to be robust.  For example, it could be used to show the user
an intermediate draft of a PDF document.  It should not be used as a
crutch for allowing users to generate documents even though there are
bugs in the interview logic.  Whether a variable happens to be defined
at the time a document is produced is not a good rationale for
omitting information from a document.  The real question is whether
the substantive logic requires it to be defined; if the variable
should be defined, its definition should be obtained.  The default
behavior of `skip undefined: False` imposes rigor to your interview
logic, ensuring that errors will surface.

In general, you should never rely upon defined-ness to control
anything important.  Especially when your users can edit their answers
with `review` screens, a variable may be defined but may be
inapplicable because of another variable.  For example, if you ask "Do
you want to include your cell phone number?" and then you ask "What is
your cell phone number," the user's cell phone number will be defined.
If the user then changes the answer to the "Do you want to include
your cell phone number?" question, then you will have a situation
where the user's cell phone number is defined but it should not be
used.  If you relied on `skip undefined: True` to omit the user's cell
phone from the document, this would only work in situations when the
user did not change their mind.  If the user initially said "no" to
the "Do you want to include your cell phone number?" question but then
later changed their mind and changed the answer to "yes," then `skip
undefined: True` might result in the cell phone number not being
included in the document even though it should be included.
Defined-ness is an unreliable indicator of whether information is
relevant.  Your logic should always be based on substantive facts, not
defined-ness.

## <a name="list field names"></a>How to get a list of field names in a PDF file

When logged in to your server as a developer, you can go to
"Utilities" from the menu and, under "Get list of fields from PDF/DOCX
template," you can upload a [PDF](#pdf template file) or [DOCX](#docx
template file) file that has fillable fields in it.  **docassemble**
will scan the file, identify its fields, and present you with the
[YAML] text of a question that uses that file as a [`pdf template
file`] or a [`docx template file`] with a list of `fields`.

The following example output is from the [sample-form.pdf] template
referenced earlier:

{% highlight yaml %}
---
question: Here is your document.
event: some_event
attachment:
  - name: sample-form
    filename: sample-form
    pdf template file: sample-form.pdf
    fields:
      - "Your Name": something
      - "Your Organization": something
      - "Apple Checkbox": No
      - "Orange Checkbox": No
      - "Pear Checkbox": No
      - "Toast Checkbox": No
---
{% endhighlight %}

# <a name="attachment"></a><a name="attachments"></a>The `attachment` specifier

The `attachment` specifier (which can also be written `attachments`)
creates documents that users can download and/or e-mail.

It can be used within a [`question`] or outside of a [`question`] (standalone).

{% include side-by-side.html demo="attachment-simple" %}

The `name`, `filename`, and `description` items can contain [Mako]
templates.  The `name` and `description` filenames can also contain
[Markdown].  (The `filename` cannot contain [Markdown], since it's a
filename, after all.)

## <a name="variable name"></a>Saving documents as variables

Including an `attachment` section in a [`question`] block will offer
the user a chance to download an assembled document and e-mail it to
themselves.

Sometimes, you might want to do other things with the document, like
e-mail it somewhere (behind the scenes), or post it to a web site.

You can save an assembled document to a variable by adding
a `variable name` key to an attachment.  For example:

{% include side-by-side.html demo="document-variable-name" %}

You can also assemble a document and save it to a variable without
presenting it to the user.  You do not need to use [`attachment`]
with a [`question`]; it can stand on its own, and it will be evaluated
when **docassemble** needs the definition of the variable indicated by
a `variable name` within the [`attachment`] block.

The following example creates a PDF file and an RTF file containing
the message "Hello, world!" and offers the files as hyperlinks.

{% include side-by-side.html demo="document-variable-name-link" %}

The variable indicated by `variable name` will be defined as an object
of class [`DAFileCollection`].  An object of this type will have
attributes for each file type generated, where each atttribute is an
object of type [`DAFile`].  In the above example, the variable
`my_file.pdf` will be the PDF [`DAFile`], and the variable
`my_file.rtf` will be the RTF [`DAFile`].  A [`DAFile`] has the
following attributes:

* `filename`: the path to the file on the filesystem
* `mimetype`: the MIME type of the file
* `extension`: the file extension (e.g., `pdf` or `rtf`)
* `number`: the internal integer number used by **docassemble** to
  keep track of documents stored in the system

See [objects] for an explanation of the [`DAFile`] and
[`DAFileCollection`] classes.

## <a name="valid formats"></a>Limiting availability of file formats

You limit the file formats that are generated by `attachment`.

{% include side-by-side.html demo="valid-formats" %}

In this example, the user will not have the option of seeing an HTML
preview and will only be able to download the PDF file.

Note that when you use [`docx template file`], the user is normally
provided with both a PDF file and a DOCX file.  The PDF file is
generated by converting the DOCX file to PDF format.  To hide the PDF
file, set `valid formats` to `docx` only.

## <a name="template file code"></a>Using code to find a template file

Typically, when you refer to a filename in an `attachment` block
using `pdf template file` or `docx template file`, you refer to a file
in the `data/templates` directory of a [package], or the ["Templates"
folder] of the [Playground].

Alternatively, you can refer to files using code.

{% highlight yaml %}
question: |
  Please upload the template file.
subquestion: |
  For best results, download
  [this file] and then upload
  it here.

  [this file]: ${ url_of('letter_template.docx') }
fields:
  - File: the_template_file
    datatype: file
---
mandatory: True
question: |
  Here is your document.
attachment:
  - name: Your letter
    filename: letter
    docx template file: 
      code: |
        the_template_file
{% endhighlight %}

The `code` needs to refer to a [Python] expression (e.g., a variable
name).  The expression can return:

* A [`DAFile`].
* A [`DAFileList`].  In the example above, the variable
  `the_template_file` will be set to a [`DAFileList`] when the file is
  uploaded.  The first file in the [`DAFileList`] will be used.
* A URL beginning with `http://` or `https://`.  In this case, the
  file at the URL will be downloaded and used as the template.
* A piece of text.  In this case, the text will be treated in much the
  same way as if it was used included directly in the [YAML] file.
  For example:
  * If the text is `sample_document.docx`, **docassemble** will look
    for a file called `sample_document.docx` in the `data/templates`
    directory of the [package], or the ["Templates" folder] of the
    [Playground].
  * If the text is `docassemble.missouri:data/static/sample_form.pdf`,
    that file will be retrieved from the `docassemble.missouri` package.

## <a name="pdfa"></a>Producing PDF/A files

If you want the [PDF] file produced by an attachment to be in
[PDF/A] format, you can set `pdf/a` to `True`:

{% include side-by-side.html demo="pdf-a" %}

You can also set it to [Python] code.  If the code evaluates to
a `True` value, a [PDF/A] will be produced.

If `pdf/a` is not specified, the default behavior is determined by the
interview's [`pdf/a` features setting].

<a name="tagged pdf"></a>When using [`docx template file`], you also
have the option of creating a "tagged PDF" which is similar to
[PDF/A].

{% include demo-side-by-side.html demo="tagged-pdf" %}

You can also set it to [Python] code.  If the code evaluates to
a `True` value, a tagged PDF will be produced.

If `tagged pdf` is not specified, the default behavior is determined
by the interview's [`tagged pdf` features setting].

## <a name="password"></a>Protecting PDF files with a password

If you want the [PDF] file produced by an attachment to be protected
with a password, you can set a `password`, and the [PDF] file will be
encrypted.  There are two passwords that can be set: an
"owner" password and a "user" password.

{% highlight yaml %}
question: |
  Here is your document.
attachment:
  name: Your letter
  filename: letter
  pdf template file: letter_template.pdf
  password: nelson
{% endhighlight %}

The `password` can be specified in the following ways:

* If set to a string, only the "user" password will be set.
* If set to a list, the first element is the "owner" password and the
  second element is the "user" password.
* If set to a [Python dict], the value of the `owner` key is the
  "owner" password and the value of the `user` key is the "user"
  password.

If the user password and the owner password are the same, then only
the "user" password will be set.

## <a name="template password"></a>Using encrypted templates

If your template file uses encryption, you can set a `template
password` to the password of the PDF template so that it can be
decrypted.

If you get an encryption error when trying to use a PDF, it might be
the case that your PDF is encrypted with the empty string.  In this
case, it might help to do:

{% highlight yaml %}
question: |
  Here is your document.
attachment:
  name: Your letter
  filename: letter
  pdf template file: letter_template.pdf
  template password: ""
{% endhighlight %}

## <a name="hyperlink style"></a>Character style of hyperlinks in DOCX files

When you are using [`docx template file`], you can insert hyperlinks
into your assembled file using the [Markdown] format for a hyperlink.

For example, you can put the following into a DOCX file.

> For more information, visit {% raw %}{{r the_link \| inline_markdown }}{% endraw %}.

Then in your [YAML] you can write something like:

{% highlight yaml %}
code: |
  if legal_issue == 'family':
    the_link = "the [Family Law Information Portal](https://familylawinfo.com)"
  else:
    the_link = "your [local law library](https://lawlibrarydirectory.org), which may be able to help you"
{% endhighlight %}

If your DOCX file contains a character style called `Hyperlink` (the
default in [Microsoft Word]) or `InternetLink` (the default in
[LibreOffice]), this character style will be used.

If you are using [Microsoft Word], your document may not contain a
character style called `Hyperlink`.  The character style is not
created by default when you create a new file in [Microsoft Word].
However, it is easy to cause the style to be added: edit your template
in Microsoft Word, add a hyperlink manually (any hyperlink will do),
save the file, and then delete the hyperlink.  When you create the
link, [Microsoft Word] will create the character style `Hyperlink` and
it the character style will persist even after you delete the
hyperlink.

If you want to manually specify a character style to be used for
hyperlinks, you can set a `hyperlink style`.

{% include side-by-side.html demo="hyperlink-style" %}

If there is no `hyperlink style` and no character style called
`Hyperlink` or `InternetLink`, then underlined blue text will be used
for hyperlinks.

## <a name="language"></a>Assembling documents in a different language than the current language

If you need to produce a document in a different language than the
user's language, then the [linguistic functions] may operate in a way
you do not want them to operate.

For example, if your user is Spanish-speaking, but you need to produce
an English language document, you may find that a word or two in the
English language document has been translated into Spanish.  (E.g.,
this can happen if your document template uses [linguistic functions].
You can remedy this by defining a `language` for the `attachment`.

{% include side-by-side.html demo="document-language" %}

Without `language: en`, the output would be:

> This customer would like to order fries y a Coke.

With `language: en`, the output is:

> This customer would like to order fries and a Coke.

The value of `language` must be plain text like `en` or `fr`; it
cannot be a [Mako] expression.

## <a name="raw"></a>Assembling text files

If you want to use **docassemble** to assemble text files, set `raw:
True` and use a [`content file`].

{% include demo-side-by-side.html demo="raw" %}

The only option on the download screen will be a download.

If you use [`variable name`], the result will be a
[`DAFileCollection`] object with the attribute `raw` set to a
[`DAFile`] object representing the assembled text file.

## <a name="permissions"></a>Controlling file permissions

By default, access to documents is limited to the user who created it
and to any other users who have joined the interview session.  Access
to files can be managed using the methods [`.set_attributes()`],
[`.user_access()`], and [`.privilege_access()`] if you set a
[`variable name`].  You can also control the permissions on files
using specifiers under `attachment`.

<a name="persistent"></a>By default, any file that a user uploads
during a session will be deleted when that session is deleted.  If you
want the file to continue to exist after the session is deleted, you
can set the `persistent` specifier to `True`.  The modifier also
accepts [Python] code; if the code evaluates to a true value, the file
will persist.  This has the same effect as calling the
[`.set_attributes()`] method on the file variable using the keyword
attribute `persistent`.

<a name="private"></a>By default, any file that a user uploads will
only be downloadable by a session user or by an administrator.  If you
want the file to be accessible to anyone, set the field modifier
`private` to `False`.  The modifier also accepts [Python] code; if the
code evaluates to a false value, the file will be available to anyone.
This has the same effect as calling the [`.set_attributes()`] method
on the file variable using the keyword attribute `persistent`.

<a name="allow users"></a>If you set `private: False`, then the file
is available to anyone, including non-logged in users.  Even a bot
that guesses URLs could download the file.  If you want to share with
particular users, you can indicate specific users using the `allow
users` specifier.  If `allowed users` refers to a [YAML] list, the list
is expected to be a list of e-mail addresses of users or integers
indicating the numeric user IDs of users.  If `allow users` refers
to text, the text is treated as a single item.  If `allow users`
refers to a [YAML] dictionary, the single key of which is `code`, you
can define the list with [Python] code.  The code is expected to
evalute to an e-mail address, an integer user ID, an [`Individual`]
with the `email` attribute set, or a list or [`DAList`] of any of the
above.  You can also use the [`.user_access()`] method to control
which users have access to a file.

<a name="allow privileges"></a>Instead of granting access to specific
other users, you can grant access to categories of users by
referencing [privileges] by name, such as `user`, `developer`, or
`advocate`.  If the `allow privileges` specifier refers to a [YAML]
list, the list items are expected to be text items like `user` or
`developer`.  If `allow privileges` refers to a string, it is treated
as a single item.  If it refers to a [YAML] dictionary, the single key
of which is `code`, you can define the privileges using [Python] code,
which is expected to evaluate to text (e.g., `'user'`) or a list of
text strings (e.g., `['user', 'developer']`).  You can also use the
[`.privilege_access()`] method to control which users have access to a
file.

## <a name="redact"></a>Redacting information from documents

If you want to assemble a document but redact certain pieces of
information from it, you can use the [`redact()`] function on the
parts you want redacted, and the text will be replaced with black
rectangles.  If you want to produce an unredacted version of the same
document, assemble it with `redact: False`.

{% include side-by-side.html demo="redact" %}

For more information about this feature, see the documentation for the
[`redact()`] function.

# <a name="attachment code"></a>Using code to generate the list of attachments

The list of attachments shown in a question can be generated by
[Python] code that returns a list of [`DAFileCollection`] objects.  If
`attachment code` is included in the question, the value will be
evaluated as [Python] code.

In the following example, the [Python] code returns an array of three
[`DAFileCollection`] objects, each of which was generated with a
separate [`attachment`] block.

{% include side-by-side.html demo="attachment-code" %}

# <a name="customization"></a>Customizing the display of documents

## <a name="enable emailing"></a>Enabling the e-mailing of documents

Most internet service providers block e-mail communications as part of
their efforts to combat [spam], so when you first set up your
**docassemble** server, the e-mail feature will probably not work "out
of the box."

As a result, in most cases you will need to edit your [Configuration]
in order for e-mailing to work.  The easiest and most effective way to
enable e-mailing is to use the [Mailgun API] (which is free), but you
can also use an [external SMTP server] hosted by [Mailgun] or another
provider.

## <a name="email template"></a><a name="email subject"></a><a name="email body"></a><a name="email address default"></a>Customizing e-mailing

When the user e-mails a document to an e-mail address using the
`attachment` interface, the subject of the email consists of the names
of the document (defaulting to "Document") and the body consists of
the message "Your document, (document name), is attached."  This
phrase can be translated or customized on a server-wide basis using
the [`words`] feature by providing translations of the following
phrases:

* `Your document, %s, is attached.`
* `Your documents, %s, are attached.`

If you want to customize the subject and body of the e-mail, you can
use the `email template` modifier:

{% include side-by-side.html demo="document-email-custom" %}

The `email template` modifier needs to refer to a [Python] expression
referring to a [`template`].

Instead of setting `email template`, you can use the modifiers `email
subject` and `email body`.  You can set these to text that you want to
appear in the subject and/or body of the e-mail.  You can use [Mako]
and [Markdown] in these modifiers.  Whether you use a [`template`] or `email
subject` and `email body`, [Markdown] will be converted to HTML for
purposes of creating the HTML version of the e-mail message.  The `email
subject` and `email body` modifiers take precedence over the parts of
the [`template`] indicated by `email template`.

The e-mail address field in the `attachment` interface is blank by
default if the user is not logged in, and if the user is logged in, it
is set to the user's e-mail address.  If you would like to set another
default value, you can use the `email address default` modifier.
[Mako] and [Markdown] can be used.  If the result does not look like
an e-mail address, it will be ignored.

For greater customization of the sending of e-mails attaching
documents, use the [`send_email()`] function in custom code.  The
`attachment` interface is simple and exists only to allow an end user
to e-mail a document to an address of their own choosing.  More
complex workflows should be created using [`send_email()`].

## <a name="always include editable files"></a>Always include editable files

By default, if an attachment includes a [PDF] version along with an
editable version, such as a DOCX file, the user will have an option of
including the editable version in the e-mail or download.  If you want
the editable documents to always be included, set `always include
editable files` to `True`.

{% include side-by-side.html demo="always-include" %}

## <a name="allow emailing"></a>Preventing the user from e-mailing documents

When [`attachments`] are included in a [`question`], the user will be
given an option to e-mail the documents to an e-mail address.  If you
would like to disable this feature, set `allow emailing` to `False`.

By default, the user can e-mail documents:

{% include side-by-side.html demo="allow-emailing-true" %}

Including `allow emailing: False` will disable this:

{% include side-by-side.html demo="allow-emailing-false" %}

You can also use a [Python] expression instead of `True` or `False`.

## <a name="allow downloading"></a>Allowing the user to download all files at once

If you would like users to be able to download all of the
[`attachments`] as a single [ZIP file], set `allow downloading` to
`True`.  By default, this feature is disabled.

{% include side-by-side.html demo="allow-downloading-true" %}

You can also use a [Python] expression instead of `True` or `False`.

You can customize the name of the [ZIP file] by setting a `zip
filename`:

{% include side-by-side.html demo="allow-downloading-true-zip-filename" %}

## <a name="include download tab"></a><a name="include attachment notice"></a><a name="manual attachment list"></a>Omitting parts of the display

By default, when an attachment is available, a message appears saying
"The following document has been created for you."  To omit this, set
`include attachment notice` to `False`.

By default, the download links appear under a tab called "Download."
Sometimes there is a "Preview" tab or a "Markdown" tab.  To omit this
tab bar, set `include download tab` to `False`.

{% include side-by-side.html demo="attachment-notice" %}

To omit all of the attachment display except for the "Email these
documents" and/or the "Download all documents as a ZIP file" boxes,
set `manual attachment list` to `True`.

{% include side-by-side.html demo="manual-attachment-list" %}

## <a name="display"></a>Alternative ways of displaying documents

There are alternatives to using [`attachment`] or [`attachment code`]
for displaying assembled files to the user.  If you use [`variable
name`] within an [`attachment`] to create a [`DAFileCollection`]
object that represents the assembled file, you can use this variable
to provide the file to the user in the context of a [`question`] in a
number of different ways:

{% include side-by-side.html demo="document-links" %}

The [`.url_for()`] method works on [`DAFileCollection`] and [`DAFile`]
objects.

If a [`DAFile`] is inserted into a template 
(e.g., with `${ complaint }`), and the [`DAFile`] is a PDF, a shrunken
image of the first page is shown.  If the [`DAFile`] is an RTF or a
DOCX file, a link is shown.

If a [`DAFileCollection`] object is inserted into a template, each
file type is inserted.  If you use [`valid formats`] to limit the file
types created, only the specified file types will be inserted.  For
example:

{% include side-by-side.html demo="document-links-limited" %}

If you want to include the "Email these documents" and/or the
"Download all documents as a ZIP file" boxes after your list of
documents, you can use `attachment code` in combination with `manual
attachment list: True`.

{% include side-by-side.html demo="manual-attachment-list" %}

# <a name="caching"></a>Document caching and regeneration

Since document assembly can take the server a long time,
**docassemble** uses caching to avoid assembling the same document
more than once.

This interview demonstrates how the document caching works:

{% include side-by-side.html demo="document-cache" %}

In most situations, document caching is a welcome feature because
users do not have to wait as long.  However, it might not always be
what you want.

For example, if you present the same document in two different
[`question`]s using [`attachment code`], the same document that was
assembled for the first [`question`] will be presented in the second
[`question`], even if changes were made to the underlying variables in
the interim.  To force the re-assembly of the document, you can use
[`code`] to delete the variable that represents the document.  Here is
an example:

{% include side-by-side.html demo="document-cache-invalidate" %}

If you want to turn off document caching entirely for a given
interview, see the [`cache documents` feature].

[`content file`]: #content file
[`cache documents` feature]: {{ site.baseurl }}/docs/initial.html#cache documents
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[YAML]: https://en.wikipedia.org/wiki/YAML
[Pandoc]: http://johnmacfarlane.net/pandoc/
[graphicx]: https://en.wikibooks.org/wiki/LaTeX/Importing_Graphics#The_graphicx_package
[geometry]: https://www.ctan.org/pkg/geometry?lang=en
[fancyhdr]: https://www.ctan.org/pkg/fancyhdr
[hyperref]: https://www.ctan.org/pkg/hyperref
[polyglossia]: https://www.ctan.org/pkg/polyglossia
[babel]: https://www.ctan.org/pkg/babel
[HotDocs]: https://en.wikipedia.org/wiki/HotDocs
[WYSIWYG]: https://en.wikipedia.org/wiki/WYSIWYG
[LaTeX]: http://www.latex-project.org/
[objects]: {{ site.baseurl }}/docs/objects.html
[function]: {{ site.baseurl }}/docs/functions.html
[functions]: {{ site.baseurl }}/docs/functions.html
[`code`]: {{ site.baseurl }}/docs/code.html#code
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`attachment code`]: #attachment code
[`attachment`]: #attachment
[`attachments`]: #attachments
[`IndividualName`]: #IndividualName
[`ChildList`]: #ChildList
[`Income`]: #Income
[`Asset`]: #Asset
[`Expense`]: #Expense
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`word()`]: {{ site.baseurl }}/docs/functions.html#word
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`DAStaticFile`]: {{ site.baseurl }}/docs/objects.html#DAStaticFile
[`DAFileCollection`]: {{ site.baseurl }}/docs/objects.html#DAFileCollection
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[hello.md]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/hello.md
[sample-form.pdf]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/sample-form.pdf
[Transfer-of-Ownership.pdf]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/Transfer-of-Ownership.pdf
[letter_template.docx]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/letter_template.docx
[Slack]: https://slack.com
[linguistic functions]: {{ site.baseurl }}/docs/functions.html#linguistic
[`pdf template file`]: #pdf template file
[`docx template file`]: #docx template file
[using `docx` as one of the `valid formats`]: #docx
[`python-docx-template`]: http://docxtpl.readthedocs.io/en/latest/
[documentation of that package]: http://docxtpl.readthedocs.io/en/latest/
[Jinja2]: http://jinja.pocoo.org/docs/2.9/
[Microsoft Word]: https://en.wikipedia.org/wiki/Microsoft_Word
[insert an image]: {{ site.baseurl }}/docs/markup.html#inserting images
[updated]: https://docs.python.org/3/library/stdtypes.html#dict.update
[Python dict]: https://docs.python.org/3/library/stdtypes.html#dict
[Adobe Acrobat Pro]: https://en.wikipedia.org/wiki/Adobe_Acrobat
[WYSIWYG]: https://en.wikipedia.org/wiki/WYSIWYG
[LibreOffice]: https://www.libreoffice.org/
[`valid formats`]: #valid formats
[package]: {{ site.baseurl }}/docs/packages.html
[`docx reference file`]: #docx reference file
[XeTeX]: https://en.wikipedia.org/wiki/XeTeX
[document markup]: {{ site.baseurl }}/docs/documents.html#markup
[documentation for the `raw()` function]: {{ site.baseurl }}/docs/functions.html#raw
[`raw()`]: {{ site.baseurl }}/docs/functions.html#raw
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`.comma_and_list()`]: {{ site.baseurl }}/docs/objects.html#DAList.comma_and_list
[`reconsider`]: {{ site.baseurl }}/docs/code.html#reconsider
[Remember]: {{ site.baseurl }}/docs/logic.html
[Dictionary]: {{ site.baseurl }}/docs/groups.html#gather dictionary
[Groups]: {{ site.baseurl }}/docs/groups.html
[a tool]: #list field names
[generate]: #list field names
[`signature` block]: {{ site.baseurl }}/docs/fields.html#signature
[dictionary]: {{ site.baseurl }}/docs/groups.html#gather dictionary
[`pdf/a` features setting]: {{ site.baseurl }}/docs/initial.html#pdfa
[`tagged pdf` features setting]: {{ site.baseurl }}/docs/initial.html#tagged pdf
[PDF]: https://en.wikipedia.org/wiki/Portable_Document_Format
[PDF/A]: https://en.wikipedia.org/wiki/PDF/A
["Templates" folder]: {{ site.baseurl }}/docs/playground.html#templates
[Playground]: {{ site.baseurl }}/docs/playground.html
[`variable name`]: #variable name
[`.url_for()`]: {{ site.baseurl }}/docs/objects.html#DAFile.url_for
[`yesno()`]: {{ site.baseurl }}/docs/functions.html#yesno
[`noyes()`]: {{ site.baseurl }}/docs/functions.html#noyes
[pdftk]: https://www.pdflabs.com/tools/pdftk-the-pdf-toolkit/
[`include_docx_template()`]: {{ site.baseurl }}/docs/functions.html#include_docx_template
[spam]: https://en.wikipedia.org/wiki/Email_spam
[Configuration]: {{ site.baseurl }}/docs/config.html
[external SMTP server]: {{ site.baseurl }}/docs/config.html#smtp
[Mailgun API]: {{ site.baseurl }}/docs/config.html#mailgun api
[Mailgun]: https://www.mailgun.com/
[ZIP file]: https://en.wikipedia.org/wiki/Zip_(file_format)
[`redact()`]: {{ site.baseurl }}/docs/functions.html#redact
[docx-table-columns.docx]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/docx-table-columns.docx
[using code to find a template file]: #template file code
[`attachment code`]: #attachment code
[`template`]: {{ site.baseurl }}/docs/initial.html#template
[`single_to_double_newlines()`]: {{ site.baseurl }}/docs/functions.html#single_to_double_newlines
[`new markdown to docx`]: {{ site.baseurl }}/docs/config.html#new markdown to docx
[inserting multi-line or formatted text into a single field in a DOCX file]: #markdown to docx
[macro]: https://jinja.palletsprojects.com/en/2.11.x/templates/#macros
[macros]: https://jinja.palletsprojects.com/en/2.11.x/templates/#macros
[`team.docx`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/data/templates/team.docx
[Markdown-formatted text]: #markdown to docx
[`.set_attributes()`]: {{ site.baseurl }}/docs/objects.html#DAFile.set_attributes
[`.user_access()`]: {{ site.baseurl }}/docs/objects.html#DAFile.user_access
[`.privilege_access()`]: {{ site.baseurl }}/docs/objects.html#DAFile.privilege_access
[privileges]: {{ site.baseurl }}/docs/users.html
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`words`]: {{ site.baseurl }}/docs/config.html#words
[`send_email()`]: {{ site.baseurl }}/docs/functions.html#send_email
[built-in filters]: https://jinja.palletsprojects.com/en/2.11.x/templates/#filters
[Python built-in functions]: https://docs.python.org/3.8/library/functions.html
[filters]: https://jinja.palletsprojects.com/en/2.11.x/templates/#filters
[tests]: https://jinja.palletsprojects.com/en/2.11.x/templates/#list-of-builtin-tests
[`DALazyTemplate`]: {{ site.baseurl }}/docs/objects.html#DALazyTemplate
[`update_language_function()`]: {{ site.baseurl }}/docs/functions.html#linguistic
