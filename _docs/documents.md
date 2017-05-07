---
layout: docs
title: Attaching documents to questions
short_title: Documents
---

# <a name="attachment"></a><a name="attachments"></a>The `attachments` statement

The `attachments` block (which can also be written `attachment`)
creates documents that users can download and/or e-mail.

It can be used within a [`question`] or outside of a [`question`].

{% include side-by-side.html demo="attachment-simple" %}

The `name`, `filename`, and `description` items can contain [Mako]
templates.  The `name` and `description` filenames can also contain
[Markdown].  (The `filename` cannot contain [Markdown], since it's a
filename, after all.)

# Overview of document creation methods

There are several ways to make downloadable documents using the
`attachments` block.  Each has its own features and limitations.

## Method 1: generating documents from scratch using Markdown

First, you can [generate attachments from Markdown](#from markdown).
In the same way that you format the text of questions, you can format
the text of attachments.  This document content:

{% highlight markdown %}
Hello, ${ user }.  This text is in **bold face**.
{% endhighlight %}

would become:

> Hello, John Doe.  This text is in **bold face**.

In this way, you can produce documents in [PDF](#pdf), [RTF](#rtf),
and [DOCX](#docx) format.

The example above uses this method of document assembly.

In addition to using [Markdown], you can use **docassemble**-specific
[markup](#markup) codes to do things like center text, insert a page
break, or insert a case caption.

## Method 2: filling in fields

The second way to make attachments is to generate [PDF](#pdf template
file) or [DOCX](#docx template file) files by creating a template in
[Adobe Acrobat Pro] or [Microsoft Word] with named "fields."  You put
the template in the `data/templates` folder of a [package].  The
`attachments` block will take the template and
"[fill in the blanks](#fill-in forms)" using values from interview
variables, providing the user with a filled-in version of the
template.

Here is an example that generates a PDF file:

{% include side-by-side.html demo="pdf-fill" %}

## Comparison of the methods

Each method has benefits and drawbacks.

The advantage of the [fill-in-fields method](#fill-in forms) is that
you have more direct, [WYSIWYG] control over document formatting.

The downside is that you have to be attentive to all the variables
your document might need, and specify them all in the `attachments`
block.

For example, if you are generating a [DOCX](#docx template file)
fill-in form, you can write `{% raw %}{{ favorite_fruit }}{% endraw
%}` in your Microsoft Word file where the name of the user's favorite
fruit should be plugged in.  Then you will have to indicate how the
variables in your Word file "map" to variables in your interview by
including a line like the following in your `attachments` block:

{% highlight yaml %}
    favorite_fruit: ${ user.favorite_fruit }
{% endhighlight %}

The variable `favorite_fruit` is a variable in the Word file, and the
variable `user.favorite_fruit` is a variable in your interview.  The
Word file does not know anything about your interview variables, and
vice-versa; you have to explicitly tell the Word file all the
information it might need to know.

As a result, your interview might ask the user for information that
does not need to be asked.  There are ways around this, but they
require you as the interview author to plan for these contingencies.

By contrast, when you
[assemble documents directly from Markdown](#from markdown), all you
need to do is refer to `${ user.favorite_fruit }` in the `content` of
your document.  If the reference is only conditionally displayed, your
interview will automatically refrain from asking the user about his or
her favorite fruit, if the information is not needed.

If you use the [PDF fill-in field](#pdf template file) method to
populate fields in a PDF file, you will have perfect control over
formatting, but you will need to worry about whether the user's
content will fit into the provided fields.  [DOCX fill-in forms](#docx
template file) are more flexible, and they also provide a PDF version.

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

![document screenshot]({{ site.baseurl }}/img/document-example-pdf.png)

The RTF file will be called `Hello_World.rtf` and will look
like this in a word processor (depending on the user's software):

![document screenshot]({{ site.baseurl }}/img/document-example-rtf.png)

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

Note that you can also create .docx files using the
[`docx template file`] feature, which is described below.

To customize document styles, headers, and footers in your .docx file,
see the [`docx reference file`] setting, discussed below.

## <a name="content file"></a>Reading Markdown content from separate files

If the content of your document is lengthy and you would rather not
type it into the interview [YAML] file as a `content` directive within
an `attachments` block, you can import the content from a separate
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
* `fontfamily` - default is `mathptmx` (Times Roman).
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
can specify filenames in other packages by referring to the package
name.  For example:

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

# <a name="fill-in forms"></a>Creating files by filling in a template

## <a name="pdf template file"></a>Filling PDF templates

If you have a PDF file that contains fillable fields (e.g. fields
added using [Adobe Acrobat Pro]), **docassemble** can assemble a PDF
file by filling in fields.  To do this, provide a `pdf template file`
and a dictionary of `fields`.

For example, here is an interview that populates fields in a file
called [sample-form.pdf]:

{% include side-by-side.html demo="pdf-fill" %}

The `pdf template file` is assumed to reside in the `data/templates`
directory of your package, unless a specific package name is
specified.  E.g.:

{% highlight yaml %}
pdf template file: docassemble.missouri-family-law:data/templates/form.pdf
{% endhighlight %}

The `fields` must be in the form of a [YAML] dictionary.  Checkbox
fields will be checked if the value evaluates to "True" or "Yes."

### <a name="signature"></a>How to insert signatures or other images into fillable PDF files

To add a signature or other image to a fillable PDF file, use Adobe
Acrobat Pro to insert a "Digital Signature" into the document where
you want the signature to appear.  Give the field a unique name.

Then, the signature will be a field, just like a checkbox or a text
box is a fill-in field.  In your `pdf template file`, set the field to
`${ user.signature }` or another reference to an image.  **docassemble**
will trim whitespace from the edges of the image and fit the image
into the "Digital Signature" box.

For example, here is an interview that populates text fields and a
signature into the template [Transfer-of-Ownership.pdf]:

{% include side-by-side.html demo="pdf-fill-signature" %}

It is important that each "Digital Signature" field have a unique
name.  If there is more than one field in the PDF template with the
same name, **docassemble** will not be able to locate it.  If you want
to insert the same signature in more than one spot in a document, you
can do so as long as each "Digital Signature" field has a different
name.  For example:

{% highlight yaml %}
    fields:
      first signature: ${ user.signature }
      second signature: ${ user.signature }
      third signature: ${ user.signature }
{% endhighlight %}

## <a name="docx template file"></a>Filling DOCX templates

Much in the same way as you can fill in fields in a PDF file using
[`pdf template file`], you can fill in fields in a .docx file using
[`docx template file`].

{% include side-by-side.html demo="docx-template" %}

This allows you to use [Microsoft Word] to design your document and
apply all the fancy formatting you want to it.  **docassemble** will
simply "fill in the blanks."  This is in contrast to the method of
[using `docx` as one of the `valid formats`], described
[below](#docx), where you assemble a document from scratch by writing
[Markdown] text that is then converted to .docx format.

The `docx template file` is assumed to reside in the `data/templates`
directory of your package, unless a specific package name is
specified.  E.g.:

{% highlight yaml %}
docx template file: docassemble.missouri-family-law:data/templates/form.docx
{% endhighlight %}

The `docx template file` feature relies heavily on the [Python]
package known as [`python-docx-template`].  You should consult the
[documentation of that package] in order to learn how to use `docx
template file`.

In the example above, the [letter_template.docx] file contains the
following text:

![letter template source]({{ site.baseurl }}/img/letter_template_source.png)

The `fields` list in the `attachment` maps variable names used in the
.docx file to pieces of text.  You can use [Mako] templating to
generate these pieces of text.  In the example above, `phone_number`
maps to the text `202-555-1234`, while `full_name` maps to `${
user.name }`.

The [`python-docx-template`] uses the [Jinja2] templating system.
[Jinja2] is different from the [Mako] templating system, which
**docassemble** uses primarily.  It is important that you do confuse
the rules of these two templating formats.  The biggest difference
between the two formats is that [Mako] uses the syntax `${
variable_name }` while [Jinja2] uses the syntax `{% raw %}{{
variable_name }}{% endraw %}`.

If any of your [Mako] statements contain an image, the image will be
used for the variable in the .docx file.  This is illustrated in the
example above by the mapping of `signature` to `${ user.signature }`:
the variable `user.signature` is a graphics image (an image of the
user's signature).  You can also use the `[FILE ...]` markup syntax to
[insert an image].  However, do not mix image references with other
text, because the other text will be lost.

When you use `docx template file`, the user is provided with both a
PDF file and a DOCX file.  The PDF file is generated by converting the
DOCX file to PDF format using [LibreOffice].  Note that the quality of
this conversion might not be as good as a PDF conversion done by
[Microsoft Word].  To hide the PDF version, you can add a
[`valid formats`] directive.

Note that if you include [Markdown] formatting syntax in substituted
text, it will pass through literally, so you will want to avoid using
[Markdown] syntax.  Some of the [markup](#markup) tags explained
[below](#markup) can be used, such as `[BR]` and `[TAB]`, but the vast
majority are ignored.  If you want to apply formatting, apply it in
the .docx template file.

The content of `fields` is converted into a data structure, which is
passed to the `render()` method of [`python-docx-template`].  The data
structure can contain structure.  For example:

{% highlight yaml %}
question: |
  Here is your document.
attachment:
  name: Your recipe
  filename: recipe
  docx template file: recipe_template.docx
  fields:
    title: Mandelbrot cookies
    oven temperature: ${ oven_degrees } degrees
    ingredients:
      - apple sauce
      - ${ special_ingredient }
      - flour
      - sugar
    preparation time: 48 hours
{% endhighlight %}

You will then have to use appropriate [Jinja2] syntax in order to
process this data structure.

Note that **docassemble** does not pass interview variables directly
to the Word file.  You cannot pass the variable `user` as one of the
`fields` and expect to be able to use `{% raw %}{{
user.name.first }}{% endraw %}` and `{% raw %}{{
user.name.last }}{% endraw %}` in your Word file.  You have to be
more specific.

The [`python-docx-template`] package allows you to use variables made
up of attributes, but it expects that the information will be provided
to it as a [Python dict] rather than as a [Python] object.  If you
wanted to use variables like `{% raw %}{{ user.name.first }}{% endraw
%}` in your Word file, you would need to pass the values this way:

{% highlight yaml %}
fields:
  user:
    name:
      first: ${ user.name.first }
      last: ${ user.name.last }
  favorite_fruit: ${ favorite_fruit }
{% endhighlight %}

For more information, see the documentation of
[`python-docx-template`].

## <a name="template code"></a>Passing values using code

You can also use [Python] code to populate the values of fields that
are filled in with [`pdf template file`] and [`docx template file`].

The `fields` directive allows you to use [Mako] to pass the values
of variables to the template.  For example:

{% highlight yaml %}
fields:
  favorite_fruit: ${ favorite_fruit }
  favorite_vegetable: ${ favorite_vegetable }
  favorite_legume: ${ favorite_legume }
  favorite_fungus: ${ favorite_fungus }
{% endhighlight %}

This is a bit repetitive and punctuation-heavy.  Instead, you can use
the `field variables` directive to list the variables you want to pass:

{% highlight yaml %}
field variables:
  - favorite_fruit
  - favorite_vegetable
  - favorite_legume
  - favorite_fungus
{% endhighlight %}

This will have the same effect.

The `field variables` directive only works when your variable in the
template has the same name as the variable in your interview, and when
you do not need to perform any transformations on the variable before
passing it to the template.

For example, you can use `fields` to pass the following values to a
template:

{% highlight yaml %}
fields:
  letter_date: ${ today() }
  subject_line: ${ subject_of_letter }
  recipient_address: ${ recipient.address_block() }
{% endhighlight %}

Note that every value is a [Mako] variable reference.  You can achieve
the same result with less punctuation by using the `field code`
directive:

{% highlight yaml %}
field code:
  letter_date: today()
  subject_line: subject_of_letter
  recipient_address: recipient.address_block()
{% endhighlight %}

There is an even more advanced way of passing values to a template:
you can include a `code` directive containing [Python] code that
evaluates to a [Python dict] in which the keys are the names of
variables in the template, and the values are the values you want
those variables to have.

The `fields`, `field variables`, and `field code` directives can all
be used together; they will supplement each other.

Here is a variation on the PDF fill-in example above that uses `code`
to supplement the values of `fields`:

{% include side-by-side.html demo="pdf-fill-code" %}

Here is a variation on the .docx template example above that uses
`code` to supplement the values of `fields`:

{% include side-by-side.html demo="docx-template-code" %}

### <a name="raw field variables"></a>Turning off automatic conversion of .docx variables

Normally, all values that you transfer to a .docx template are
converted so that they display appropriately in your .docx file.  For
example, if the value is a [`DAFile`] graphics image, it will be
converted so that it displays in the .docx file as an image.  Or, if
the value contains [document markup] codes that indicate line breaks,
these will display as actual line breaks in the .docx file, rather
than as codes like `[BR]`.

However, if your .docx file uses [Jinja2] templating to do complicated
things like for loops, this conversion might cause problems.

For example, suppose you have a variable `vegetable_list` that is
defined as a [`DAList`] with items `['potatoes', 'beets']`, and you
pass it to a .docx template as follows.

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
> Don't forget to bring o!
> Don't forget to bring t!
> Don't forget to bring a!
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

Now, the `vegetable_list` variable in the .docx template will be a
real list that [Jinja2] can process.  The output will be what you expected:

> Don't forget to bring potatoes!
> Don't forget to bring beets!

The conversion to text is also done if you use `field code` or `code`
to pass variables to a .docx template.  In order to pass variables in
"raw" form using `field code` or `code`, you can wrap the code in the
[`raw()`] function.  For more information, see the
[documentation for the `raw()` function].

## <a name="list field names"></a>How to get a list of field names in a PDF or DOCX file

When logged in to **docassemble** as a developer, you can go to
"Utilities" from the menu and, under "Get list of fields from PDF/DOCX
template," you can upload a [PDF](#pdf template file) or [DOCX](#docx
template file) file that has fillable fields in it.  **docassemble**
will scan the file, identify its fields, and present you with the
[YAML] text of a question that uses that file as a
[`pdf template file`] or a [`docx template file`].

# <a name="variable name"></a>Saving documents as variables

Including an `attachments` section in a [`question`] block will offer
the user a chance to download an assembled document and e-mail it to
themselves.

Sometimes, you might want to do other things with the document, like
e-mail it, or post it to a web site.

You can save an assembled document to a variable by adding
a `variable name` key to an attachment.  For example:

{% include side-by-side.html demo="document-variable-name" %}

You can also assemble a document and save it to a variable without
presenting it to the user.  The following example creates a PDF file
containing the message "Hello, world!" and posts it to a [Slack]
site.

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
mandatory: True
code: |
  import slacker
  slacker.Slacker(daconfig['slack api key']).files.upload(my_file.pdf.path())
---
mandatory: True
question: |
  I have posted a Hello World file to Slack!
---
attachments:
  - variable name: my_file
    filename: hello_world
    content: |
      Hello, world!
---
{% endhighlight %}

The varible indicated by `variable name` will be defined as an object
of class [`DAFileCollection`].  An object of this type will have
attributes for each file type generated, where each atttribute is an
object of type [`DAFile`].  In the above example, the variable
`my_file.pdf` will be the PDF [`DAFile`], and the variable
`my_file.rtf` will be the RTF [`DAFile`].  A [`DAFile`] has the
following attributes:

* `filename`: the path to the file on the filesystem;
* `mimetype`: the MIME type of the file;
* `extension`: the file extension (e.g., `pdf` or `rtf`); and
* `number`: the internal integer number used by **docassemble** to
  keep track of documents stored in the system

See [objects] for an explanation of the [`DAFile`] and
[`DAFileCollection`] classes.

# <a name="attachment code"></a>Using code to generate the list of attachments

The list of attachments shown in a question can be generated by
[Python] code that returns a list of [`DAFileCollection`] objects.  If
`attachment code` is included in the question, the value will be
evaluated as [Python] code.

In the following example, the [Python] code returns an array of three
[`DAFileCollection`] objects, each of which was generated with a
separate [`attachment`] block.

{% include side-by-side.html demo="attachment-code" %}

# <a name="valid formats"></a>Limiting availability of file formats

You can also limit the file formats available.

{% include side-by-side.html demo="valid-formats" %}

In this example, the user will not have the option of seeing an HTML
preview and will only be able to download the PDF file.

Note that when you use [`docx template file`], the user is provided
with both a PDF file and a DOCX file.  The PDF file is generated by
converting the DOCX file to PDF format.  To hide the PDF file, set
`valid formats` to `docx` only.

# <a name="language"></a>Assembling documents in a different language than the current language

If you need to produce a document in a different language than the
user's language, then the [linguistic functions] may operate in a way
you do not want them to operate.

For example, if your user is Spanish-speaking, but you need to produce
an English language document, you may find that a word or two in the
English language document has been translated into Spanish.  (E.g.,
this can happen if your document template uses [linguistic functions]
from [`docassemble.base.util`]).  You can remedy this by defining a
`language` for the document.

{% include side-by-side.html demo="document-language" %}

Without `language: en`, the output would be:

> This customer would like to order fries y a Coke.

With `language: en`, the output is:

> This customer would like to order fries and a Coke.

# <a name="allow emailing"></a>Preventing the user from e-mailing documents

When [`attachments`] are included in a [`question`], the user will be
given an option to e-mail the documents to an e-mail address.  If you
would like to disable this feature, set `allow emailing` to `False`.

By default, the user can e-mail documents:

{% include side-by-side.html demo="allow-emailing-true" %}

Including `allow emailing: False` will disable this:

{% include side-by-side.html demo="allow-emailing-false" %}

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
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`attachment`]: #attachment
[`attachments`]: #attachments
[`IndividualName`]: #IndividualName
[`ChildList`]: #ChildList
[`Income`]: #Income
[`Asset`]: #Asset
[`Expense`]: #Expense
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`word()`]: {{ site.baseurl }}/docs/functions.html#word
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
[updated]: https://docs.python.org/2/library/stdtypes.html#dict.update
[Python dict]: https://docs.python.org/2/library/stdtypes.html#dict
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
