---
layout: docs
title: Document Assembly
short_title: Document Assembly
---

# <a name="attachment"></a><a name="attachments"></a>The `attachments` Component

The `attachments` component (which can also be written `attachment`)
creates documents that users can download and/or e-mail.

It can be used within a [`question`] block or outside of a [`question`] block.

{% include side-by-side.html demo="attachment-simple" %}

The `name`, `filename`, and `description` items can contain [Mako]
templates.  The `name` and `description` filenames can also contain
[Markdown].  (The `filename` cannot contain [Markdown], since it's a
filename, after all.)

# <a name="oview"></a>Overview of Document Creation Methods

There are several ways to make downloadable documents using the
`attachments` block.  Each has its own features and limitations.

## <a name="scratch"></a>Method 1: Generating Documents from Scratch using Markdown

First, you can [generate attachments from Markdown](#from markdown).
In the same way that you format the text of questions, you can format
the text of attachments.  This document source:

{% highlight markdown %}
Hello, ${ user }.  This text is in **bold face**.
{% endhighlight %}

would become this document content:

> Hello, John Doe.  This text is in **bold face**.

In this way, you can produce documents in [PDF](#pdf), [RTF](#rtf),
and [DOCX](#docx) format.

In addition to using [Markdown], you can use [DALang] specific
[markup](#markup) codes to do things like center text, insert a page
break, or insert a case caption.

## <a name="filling"></a>Method 2: Filling in Fields

The second way to make attachments is to generate [PDF](#pdf template
file) or [DOCX](#docx template file) files using templates that you prepare
in [Adobe Acrobat Pro] or [Microsoft Word].  You put the template file
in the `data/templates` folder of your Steward's [package] (or the
["Templates" folder] in the [Playground]).  The `attachments` block
will take the template and "[fill in the blanks](#fill-in forms)"
using values from [DALang] variables, providing the user with a
filled-in version of the template.

Here is an example that generates a PDF file:

{% include side-by-side.html demo="pdf-fill" %}

Here is an example that generates a DOCX file:

{% include side-by-side.html demo="docx-template" %}

## <a name="comparison"></a>Comparison of the Methods

Each method has benefits.

The advantage of the [fill-in-fields method](#fill-in forms) is that
you have more direct, [WYSIWYG] control over document formatting.

The advantage of the [Markdown](#from markdown) method is that you can
concentrate on the content and let the Steward handle the
formatting.  For example, there are automatic methods for generating
case captions in legal documents created from [Markdown], whereas if
you create your legal document in DOCX format, you will need to
construct your caption in the [DOCX template file](#docx template
file) and make sure that it gets filled in correctly.  The
[Markdown](#from markdown) method allows for more readable embedded
if/then/else statements.  In the [DOCX template](#docx template file)
method, you have to write:

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
they do not require this itemization of fields.  Also, note that the
[DOCX fill-in forms](#docx template file) method provides not only a
DOCX file, but a PDF version of that DOCX file.

# <a name="from markdown"></a>Creating Files from Markdown

## <a name="pdf"></a><a name="rtf"></a>Creating PDF and RTF Files from Markdown

The following `attachment` component offers the user a PDF file and an RTF
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

## <a name="docx"></a>Creating DOCX Files from Markdown

A Steward can use [Pandoc] to convert [Markdown] into a
Microsoft Word DOCX file.  These DOCX files are not created by
default because they do not support all of the features that are
supported by [RTF](#rtf) and [PDF](#pdf) formats.  To generate DOCX
files, specify `docx` as one of the [`valid formats`]:

{% include side-by-side.html demo="document-docx" %}

To customize document styles, headers, and footers in your DOCX file,
see the [`docx reference file`] setting, discussed below.

There are some formatting features that [Pandoc] supports when
converting to .rtf that are not available when converting to DOCX, so
you might want to use .rtf conversion for that reason.  However, the
.rtf format can be user-unfriendly, and in some circumstances it would
be better to have a DOCX version.  Luckily, [LibreOffice] can convert
.rtf files to DOCX format.  If you include `rtf to docx` as one of
the [`valid formats`], the Steward will convert [Markdown] to RTF
format and then use [LibreOffice] to convert the RTF file to DOCX
format.  The result is that you get a DOCX file instead of an .rtf
file.

{% include side-by-side.html demo="document-docx-from-rtf" %}

Note that you can also assemble DOCX files from templates that you
compose in Mirosoft Word.  See the [`docx template file`] feature,
which is described [below](#docx template file).

## <a name="content file"></a>Reading Markdown Content from Separate Files

If the content of your document is lengthy and you would rather not
type it into the [DALang] file as a `content` sub-component within
an `attachments` component, you can import the content from a separate
file using `content file`:

{% include side-by-side.html demo="document-file" %}

The content of the [Markdown] file, [hello.md], is:

{% highlight text %}
Hello, world!
{% endhighlight %}

Files referenced with the `content file` sub-component are assumed to reside in the
`data/templates` directory within the current Steward's package.
You can specify filenames in other locations
by specifying the Steward's package name and the file path.  For example:

{% highlight yaml %}
content file: docassemble.demo:data/templates/complaint.md
{% endhighlight %}

The `content file` sub-component can also refer to a list of file names:

{% highlight yaml %}
content file:
  - introduction.md
  - jurisdiction.md
  - discussion.md
{% endhighlight %}

In this case, the content of multiple `content file` files will be
concatenated.

## <a name="markup"></a>Formatting Documents with DALang Tags

In addition to using [Markdown] syntax, you can use
[DALang]-specific markup tags to control the appearance of
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

This DALang demonstrates these features:

{% include side-by-side.html demo="document-markup" %}

## <a name="pandoc"></a>Formatting Documents with Pandoc Templates and Metadata

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

## <a name="metadata rtf pdf"></a>Metadata Applicable to RTF and PDF Files

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

## <a name="metadata pdf"></a>Metadata Applicable to Generated PDFs Only

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

## <a name="customization"></a>Additional Customization of Document Formatting

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
sub-component to the [`attachment`] component:

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
of the current Steward's package.  You
can specify filenames in other packages by referring to that Steward's package name and the file
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

If this question appears within a [DALang] file located in the package for the Steward
`docassemble.pa_family_law`, the assumption is that the files
`summary_judgment_template.tex` and `summary_judgment_template.rtf`
will exist in the directory `docassemble/pa_family_law/data/templates`
within that Steward's package.

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

# <a name="fill-in forms"></a>Creating Files by Filling in a Template

## <a name="pdf template file"></a>Filling PDF Templates

If you have a PDF file that contains fillable fields (e.g. fields
added using [Adobe Acrobat Pro] or a similar application),
a Steward can fill in the fields of the PDF file using
information from an interview and provide the user with a copy of that
PDF file with the fields filled in.  To do this, use the
[`attachments`] component as above, but instead of providing `content`
or `content file` sub-component, provide a `pdf template file` sub-component and a dictionary of
`fields` sub-component.

For example, here is an interview that populates fields in a file
called [sample-form.pdf]:

{% include side-by-side.html demo="pdf-fill" %}

The `pdf template file` is assumed to reside in the `data/templates`
directory of your Steward's package, unless a Steward's specific package name is
specified.  For example, you could refer to a file in another Steward's package
by writing:

{% highlight yaml %}
pdf template file: docassemble.missouri-family-law:data/templates/form.pdf
{% endhighlight %}

In [Adobe Acrobat Pro]'s "Add or Edit Fields" mode, the PDF file looks
like this:

![sample form]({{ site.baseurl }}/img/sample-form.png){: .maybe-full-width }

The `fields` sub-component must be in the form of a [YAML] list of dictionaries, or
a single dictionary.  The names of the fields listed in `fields` must
correspond _exactly_ with the names of the fields in the PDF file.
Luckiliy, there is [a tool] that will help you extract the literal
field names from a PDF file.

Note: If your PDF document has many fields, it is strongly recommended
that you use [Adobe Acrobat Pro] to give each field a concise,
meaningful, and accurate field name (as well as a helpful tooltip).
[Adobe Acrobat Pro] has a feature for automatically assigning names to
fields, but this tool often assigns incorrect names.  You should go
through this process _before_ you [generate] the `attachment`
component for filling fields in the PDF file.

While it is legal for a PDF file to contain more than one field with
the same name, please note that Stewards are unable to populate
such fields.  You must give each field in your PDF file a unique name.

When writing the values of the fields, you can use [Mako], but not
[Markdown].  If you use [Markdown], it will be interpreted literally.
Checkbox fields will be checked if and only if the value evaluates to
"True" or "Yes."

The section below on [passing values using code](#template code)
explains alternative ways that you can populate the values of fields
in a PDF template.

You have a choice whether to list fields as a single dictionary or a
list of dictionary items.  Providing the fields in the form of a list
is usually preferable because it provides an order in which the fields
should be evaluated; if you only provide a single dictionary, the
items will be evaluated in a random order.

The section below on [using code to find a template file] explains how
you can use code to determine what template file to use with `pdf
template file`.

### <a name="editable"></a>Making PDF Templates Non-Editable

By default, the PDF files created by filling in
forms in a `pdf template file` can be edited by the user; the fill-in
form boxes will still exist in the resulting document.

If you want to prevent users from editing the forms created through
`pdf template file`, set the `editable` sub-component to `False`.  For
example:

{% include side-by-side.html demo="pdf-fill-not-editable" %}

### <a name="signature"></a>How to Insert Signatures or Other Images into PDF Templates

To add a signature or other image to a fillable PDF file, use
[Adobe Acrobat Pro] to insert a "Digital Signature" into the document
where you want the signature to appear.  Give it the height and width
you want the image to have.  Give the field a unique name.

Then, the image will be a field, just like a checkbox or a text box is
a fill-in field.  In your `pdf template file`, set the field to `${
user.signature }` or another reference to an image.  The Steward
will trim whitespace from the edges of the image and fit the image
into the "Digital Signature" box.

For example, here is an interview that populates text fields and
inserts a signature into the template [Transfer-of-Ownership.pdf]:

{% include side-by-side.html demo="pdf-fill-signature" %}

It is important that each "Digital Signature" field have a unique
name.  If there is more than one field in the PDF template with the
same name, the Steward will not be able to locate it.  If you want
to insert the same signature in more than one spot in a document, you
can do so as long as each "Digital Signature" field has a different
name.  For example:

{% highlight yaml %}
    fields:
      - first signature: ${ user.signature }
      - second signature: ${ user.signature }
      - third signature: ${ user.signature }
{% endhighlight %}

### <a name="checkbox export value"></a>Changing the "export value" of Checkbox Fields

By default, when populating checkboxes, the Steward sets the
checkbox value to `'Yes'` if the checkbox should be checked.  This is
the default "Export Value" of a checked checkbox in Adobe Acrobat.

If your PDF file uses a different "Export Value," you can set it
manually by using an expression like 
`${ 'affirmative' if likes_toast else 'negative }`.

You can also set the `checkbox export value` option to the value you
want to use.  This example uses `'yes'` instead of `'Yes'`.

{% include side-by-side.html demo="checkbox-export-value" %}

When the `checkbox export value` sub-component is set, then if the value of a PDF field
evaluates to `True`, the `checkbox export value` will be substituted.
In addition, [`yesno()`] and [`noyes()`] will return the `checkbox
export value` instead of `'Yes'`.

The `checkbox export value` sub-component can contain [Mako].  If the value you want
to use has special meaning in [YAML], as `yes` does, make sure to
quote the value.

## <a name="docx template file"></a>Filling DOCX Templates

You can fill in fields in DOCX template files by referring to a `docx
template file`.

{% include side-by-side.html demo="docx-template" %}

This allows you to use [Microsoft Word] to design your document and
apply formatting.  The Steward will simply "fill in the blanks."
(This is in contrast to the method of
[using `docx` as one of the `valid formats`], described
[above](#docx).  When you use that method, you assemble a document
from scratch by writing [Markdown] text that is then converted to
DOCX format.)

The file referenced with `docx template file` sub-component is assumed to reside in
the `data/templates` directory of your Steward's package, unless a specific Steward's
package name is specified.  For example, you could refer to a DOCX
file in another package by writing:

{% highlight yaml %}
docx template file: docassemble.missouri-family-law:data/templates/form.docx
{% endhighlight %}

In the example above, the [letter_template.docx] file contains the
following text:

![letter template source]({{ site.baseurl }}/img/letter_template_source.png){: .maybe-full-width }

The `docx template file` feature relies heavily on the [Python]
package known as [`python-docx-template`].  This package uses the
[Jinja2] templating system to indicate fields in the DOCX file.
[Jinja2] is different from the [Mako] templating system, which
[DALang] primarily uses. Therefore, we will refer to this code as Embedded DALang.

When you work with Embedded DALang in DOCX templates, be careful not to confuse the rules
of these two templating formats.  The biggest difference between the
formats is that [Mako] uses the syntax `${ variable_name }`, while
[Jinja2] uses the syntax `{% raw %}{{ variable_name }}{% endraw %}`.

In [Mako], used in DALang, you would write an if/else statement like this:

{% highlight markdown %}
You may wish to distribute your property to your
% if user.child.number() > 0:
heirs.
% else:
friends.
% endif
{% endhighlight %}

In [Jinja2], used in Embedded DALang, you would write:

{% highlight text %}
You may wish to distribute your property to your 
{% raw %}{% if user.child.number() > 0 %}heirs.{% else %}friends.{% endif %}{% endraw %}
{% endhighlight %}

Also, the [`python-docx-template`] package uses a slightly different
version of the [Jinja2] syntax to account for the fact that it is
being used inside of a DOCX file.  The standard [Jinja2] way of
writing a "for loop" is:

{% highlight text %}
{% raw %}{% for item in fruit_list %}
{{ item }} is a type of fruit.
{% endfor %}{% endraw %}
{% endhighlight %}

In a DOCX template, however, this will result in extraneous line
breaks.  You can avoid this by writing the following in Embedded DALang:

{% highlight text %}
{% raw %}{%p for item in fruit_list %}
{{ item }} is a type of fruit.
{%p endfor %}{% endraw %}
{% endhighlight %}

The `p` tag indicates that the paragraph containing the 
`{% raw %}{%p ... %}{% endraw %}` statement should be removed from 
the document.  When you edit the spacing of paragraphs in your DOCX
file, you need to edit the paragraph spacing of paragraphs that do
_not_ contain `{% raw %}{%p ... %}{% endraw %}` statements.  You may
need to change both the spacing after a paragraph and the spacing
before a paragraph in order to get the results you want.  Other
tags besides `p` include `tr` for table rows and `tc` for table
columns.

If you have a bulleted or numbered list in a DOCX template and you want
to display an item in the list conditionally (using an if .. endif statement),
you should use the  `{% raw %}{%p if ... %}{% endraw %}` syntax. Place 
the `{% raw %}{%p if ... %}{% endraw %}` and
the `{% raw %}{%p endif %}{% endraw %}` statements on their own lines in the list. 
If you place the `{% raw %}{%p endif %}{% endraw %}` on the same line
as the `{% raw %}{%p if... %}{% endraw %}` line, you may get an error about
a missing `endif` statement, since the `p` tag could cause the 
`endif` statement to be deleted before it is processed.

The following Embedded DALang in a DOCX template:

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
Embedded DALang in this paragraph, but don't actually include this paragraph in
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
the Embedded DALang in this row, but don't actually include this row in the
assembed document."

When using a "for" loop over the columns of a table, you would include
extra columns:

| Name                               | {% raw %}{%tc for inc_type in inc_types %}{% endraw %} | {% raw %}{{ inc_type }}{% endraw %}                           | {% raw %}{%tc endfor %}{% endraw %} |
|------------------------------------|--------------------------------------------------------|---------------------------------------------------------------| ------------------------------------|
| {% raw %}{{ grantor }}{% endraw %} | {% raw %}{%tc for inc_type in inc_types %}{% endraw %} | {% raw %}{{ currency(grantor.income[inc_type]) }}{% endraw %} | {% raw %}{%tc endfor %}{% endraw %} |
| {% raw %}{{ grantee }}{% endraw %} | {% raw %}{%tc for inc_type in inc_types %}{% endraw %} | {% raw %}{{ currency(grantee.income[inc_type]) }}{% endraw %} | {% raw %}{%tc endfor %}{% endraw %} |
{: .table .table-bordered }

The `tc` prefix in `{% raw %}{%tc ... %}{% endraw %}` means "process
the Embedded DALang in this table cell, but don't actually include this table
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
references need to be by themselves inside of fields.

When you use the `docx template file` sub-component, the user is provided with both a
PDF file and a DOCX file.  The PDF file is generated by converting
the DOCX file to PDF format using [LibreOffice].  To suppress the
creation of the PDF version, you can add a [`valid formats`]
sub-component.

Note that you cannot use [Markdown] formatting syntax in text that you
insert into a DOCX file.  If you do, it will pass through literally.
Apply all of your formatting in the DOCX template file.

Here is an example that demonstrates how to use [`DAList`] and [`DADict`]
[objects] in a DOCX template using Embedded DALang's [Jinja2] formatting.

{% include side-by-side.html demo="docx-jinja2-demo" %}

The `docx-jinja2-demo.docx` file looks like this:

![docx jinja2 source]({{ site.baseurl }}/img/docx-jinja2-demo.png){: .maybe-full-width }

For more information on using Embedded DALang in DOCX templates, see the
documentation of [`python-docx-template`].

The section below on [using code to find a template file] explains how
you can use code to determine what template file to use with the `docx
template file` sub-component.

### <a name="include_docx_template"></a>Inserting Other DOCX Files into DOCX Templates

You can include the paragraphs of a DOCX file inside of your DOCX
template.

![include_docx_template]({{ site.baseurl }}/img/include_docx_template.png)

See the documentation for the [`include_docx_template()`] function for
more information.  Note that it is important to use the `p` form of
[Embedded DALang] markup, by itself on a line in the document:

> {% raw %}{{p include_docx_template('sub_document.docx') }}{% endraw %}

If you have a DOCX file in the form of a [`DAFile`] or [`DAFileList`]
object, then you can do:

> {% raw %}{{p include_docx_template(the_file) }}{% endraw %}

or just

> {% raw %}{{p the_file }}{% endraw %}

### <a name="docx tables"></a>Inserting Tables into DOCX Templates

You can assemble tables in a DOCX template using an [Embedded DALang] "for loop."

Here is an example.  The DOCX template looks like this:

![table template source]({{ site.baseurl }}/img/table_template.png){: .maybe-full-width }

Note that the row that should be repeated is sandwiched between two
rows containing `for` and `endfor` Embedded DALang statements.  Both of these
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
see the [Dictionary] subsection of the [data structures] section of the
documentation.

Your DOCX tables can also loop over the columns of a table.

![table columns template source]({{ site.baseurl }}/img/docx-table-columns-template.png){: .maybe-full-width }

![table columns template result]({{ site.baseurl }}/img/docx-table-columns-assembled.png){: .maybe-full-width }

The following interview, which uses the template [docx-table-columns.docx],
illustrates this.

{% include side-by-side.html demo="docx-table-columns" %}

### <a name="particfields"></a>Passing Values Only for Particular Fields

By default, all of the variables in your interview's [DALang] will be available
in the DOCX template.  If you do not want this, perhaps because your
DOCX template uses a different variable naming convention, you can
use the `fields` sub-component to indicate a mapping between the fields in
the DOCX template and the values that you want to be filled in.  This
operates much like the [PDF fill-in fields](#pdf template file)
sub-component.

The content of `fields` is converted into a data structure, which is
passed to the `render()` method of [`python-docx-template`].  The data
structure needs to be a [Python dict], but it can contain other data
types.  For example, in this interview, `fields` contains a list of
ingredients:

{% include side-by-side.html demo="docx-recipe" %}

In your DOCX template, you will need to use appropriate [Embedded DALang] syntax
in order to process the list of ingredients.  Here is an example of a
DOCX template that uses the above data structure:

![recipe template source]({{ site.baseurl }}/img/recipe_template.png){: .maybe-full-width }

For more information on using Embedded DALang in DOCX templates, see the
documentation of [`python-docx-template`].

## <a name="template code"></a>Passing Values using Code

When you use the `fields` sub-component with [`pdf template file`], you
have to use [Mako] in order to pass the values of [DALang] variables
to the template.  For example, suppose you have a PDF file with these
fields:

![fruit template]({{ site.baseurl }}/img/fruit_template.png){: .maybe-full-width }

You can use an interview like this to populate the fields:

{% include side-by-side.html demo="fruit-template-alt-1" %}

However, this is a bit punctuation-heavy and repetitive.  As an
alternative, you can use the `field variables` sub-component to list the
variables you want to pass:

{% include side-by-side.html demo="fruit-template-alt-2" %}

This will have the same effect.

The `field variables` sub-component only works when your variable in the
template has the same name as the variable in your interview, and when
you do not need to perform any transformations on the variable before
passing it to the template.

The `field variables` sub-component, and other sub-components described in
this subsection, work both with [`pdf template file`] and
[`docx template file`] components.  But note that since the
[DOCX assembly process](#docx template file) by default accesses all
of your interview's DALang variables, you will normally only need to use `field
variables` with PDF templates.

Suppose you want to pass the results of functions or methods to a 
template that looks like this:

![letter template]({{ site.baseurl }}/img/letter.png){: .maybe-full-width }

One way to pass the results of functions or methods it is to use
`fields`, where every value is a [Mako] variable reference containing
code:

{% include side-by-side.html demo="pdf-template-alt-1" %}

You can achieve the same result with less punctuation by using the
`field code` sub-component:

{% include side-by-side.html demo="pdf-template-alt-2" %}

There is still another way of passing values to a template: you can
include a `code` sub-component that contains [Python] code that evaluates
to a [Python dict] in which the keys are the names of variables in the
template, and the values are the values you want those variables to
have.  For example:

{% include side-by-side.html demo="pdf-template-alt-3" %}

Note that the `code` must be a single [Python] expression, not a list
of statements.  It can be difficult to cram a lot of logic into a
[Python] expression, so you may want to create a variable to hold the
values.  For example:

{% include side-by-side.html demo="pdf-template-alt-4" %}

Note that the use of the [`reconsider`] component is important here.
[Remember] that a Steward will only ask a question or run code
when it encounters an undefined variable.  If the recipient's address
is undefined when a Steward tries to run the [DALang] above,
the Steward will ask a question to gather it, but once that
question is answered, the Steward will have no reason to run the
above code again because `letter_variables` will already be defined --
albeit in an incomplete state, with a `letter_date` item and a
`subject_line` item but without a `recipient_address` item.  Setting
the `reconsider` component to `True` ensures that whenever the Steward
needs to know the value of `letter_variables`, that value will be
"reconsidered"---treated as undefined---and the DALang above will be
re-run in order to obtain a fresh definition of `letter_variables`.

The `fields`, `field variables`, and `field code` sub-components are not
mutually exclusive.  When they are used together, they supplement each
other.  (In DOCX templates, however, the fields do not supplement the
values of variables in the [interview session dictionary]; if you use `fields`,
`field variables`, or `field code` sub-components, the Steward will not use the
interview session dictionary as a whole.)

Here is a variation on the original PDF fill-in example [above](#pdf
template file) that uses `code` to supplement the values of `fields`:

{% include side-by-side.html demo="pdf-fill-code" %}

If you use the DALang tag `${ ... }`, the `fields`, `field variables`, and
`field code` sub-components your Steward will convert the values of your variables to a
format suitable for display in the assembled document.  If you are using a DOCX template
and you only use the [Embedded DALang] tag `{% raw %}{{ ... }}{% endraw %}` in
your DOCX template, the same type of formatting will occur.  However, if you want to
use "for loops" and other features of Embedded DALang when passing variables
using `fields`, `field variables`, or `field code` sub-components, you should read
the next section, which explains how to pass "raw", unformated variables
to the template.

When using `field code`, `code`, or `field variables` to define your
fields, there is an additional sub-component for formatting decimal numbers: set the
option `decimal places` to the number of decimal places you want to
use.

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
template with a method other than the `field code`, `code`, or `field
variables` sub-components.  In other cases, you will need to manually format your
numbers, for example by writing something like `${ '%.3f' %
ounces_of_gold }`.

### <a name="raw field variables"></a>Turning Off Automatic Conversion of DOCX Variables

Normally, all values that you transfer to a DOCX template using
`fields`, `field variables`, and `field code` sub-components are converted so that
they display appropriately in your DOCX file.  For example, if the
value is a [`DAFile`] graphics image, it will be converted so that it
displays in the DOCX file as an image.  Or, if the value contains
[document markup] codes that indicate line breaks, these will display
as actual line breaks in the DOCX file, rather than as codes like
`[BR]`.

However, if your DOCX file uses [Embedded DALang] to do complicated
things like "for loops", this conversion might cause problems.

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
real list that your Embedded DALang can process.  The output will be what you expected:

> Don't forget to bring potatoes!
> Don't forget to bring beets!

The conversion to text is also done if you use `field code` or `code`
to pass variables to a DOCX template.  In order to pass variables in
"raw" form using `field code` or `code`, you can wrap the code in the
[`raw()`] function.  For more information, see the
[documentation for the `raw()` function].

## <a name="list field names"></a>How to Get a List of Field Names in a PDF or DOCX File

When logged in to your [server] as a developer, you can go to
"Utilities" from the menu and, under "Get list of fields from PDF/DOCX
template," you can upload a [PDF](#pdf template file) or [DOCX](#docx
template file) file that has fillable fields in it.  The server
will scan the file, identify its fields, and present you with the
[DALang] for a question that uses that file as a
[`pdf template file`] or a [`docx template file`] with a list of
`fields`.

This example output is from the [letter_template.docx] template [shown above]:

{% highlight yaml %}
question: Here is your document.
event: some_event
attachment:
  - name: letter_template
    filename: letter_template
    docx template file: letter_template.docx
    fields:
      "subject_matter": Something
      "phone_number": Something
      "adverse_party": Something
      "today": Something
      "user": Something
{% endhighlight %}

# <a name="variable name"></a>Saving Documents as Variables

Including an `attachments` component in a [`question`] block will offer
the user a chance to download an assembled document and e-mail it to
themselves.

Sometimes, you might want to do other things with the document, like
e-mail it somewhere (behind the scenes), or post it to a web site.

You can save an assembled document to a variable by adding
a `variable name` sub-component to an attachment component.  For example:

{% include side-by-side.html demo="document-variable-name" %}

# <a name="attachment block"></a>Creating an Attachments Block

You can also assemble a document and save it to a variable without
presenting it to the user.  To do so, you don't use
[`attachments`] within a [`question`] block. `attachments` can stand on their own, as an `attachments` block, and it
will be evaluated when the Steward needs the definition of the
variable indicated by `variable name` component.

The following example creates a PDF file and an RTF file containing
the message "Hello, world!" and offers the files as hyperlinks.

{% include side-by-side.html demo="document-variable-name-link" %}

The varible indicated by the `variable name` component will be defined as an object
of class [`DAFileCollection`].  An object of this type will have
attributes for each file type generated, where each atttribute is an
object of type [`DAFile`].  In the above example, the variable
`my_file.pdf` will be the PDF [`DAFile`], and the variable
`my_file.rtf` will be the RTF [`DAFile`].  A [`DAFile`] has the
following attributes:

* `filename`: the path to the file on the filesystem
* `mimetype`: the MIME type of the file
* `extension`: the file extension (e.g., `pdf` or `rtf`); and
* `number`: the internal integer number used by the [server] to
  keep track of documents stored in the system

See [objects] for an explanation of the [`DAFile`] and
[`DAFileCollection`] classes.

# <a name="attachment code"></a>Using Code to Generate the List of Attachments

The list of attachments shown in a question can be generated by
[Python] code that returns a list of [`DAFileCollection`] objects.  If
the `attachment code` component is included in the question, the value will be
evaluated as [Python] code.

In the following example, the [Python] code returns an array of three
[`DAFileCollection`] objects, each of which was generated with a
separate [`attachments`] block.

{% include side-by-side.html demo="attachment-code" %}

# <a name="valid formats"></a>Limiting Availability of File Formats

You limit the file formats that are generated by `attachments`.

{% include side-by-side.html demo="valid-formats" %}

In this example, the user will not have the option of seeing an HTML
preview and will only be able to download the PDF file.

Note that when you use [`docx template file`], the user is normally
provided with both a PDF file and a DOCX file.  The PDF file is
generated by converting the DOCX file to PDF format.  To hide the PDF
file, set `valid formats` sub-component to `docx` only.

# <a name="template file code"></a>Using Code to Find a Template File

Typically, when you refer to a filename in an `attachments` component/block
using the `pdf template file` or `docx template file` sub-component/component, you refer to a file
in the `data/templates` directory of a [package], or the ["Templates"
folder] of the [Playground].

Alternatively, you can refer to files using a `code` sub-subcomponent.

{% include side-by-side.html demo="template-code" %}

The `code` sub-subcomponent needs to refer to a [Python] expression (e.g., a variable
name).  The expression can return:

* A [`DAFile`].
* A [`DAFileList`].  In the example above, the variable
  `the_template_file` will be set to a [`DAFileList`] when the file is
  uploaded.  The first file in the [`DAFileList`] will be used.
* A URL beginning with `http://` or `https://`.  In this case, the
  file at the URL will be downloaded and used as the template.
* A piece of text.  In this case, the text will be treated in much the
  same way as if it was used included directly in the [DALang] file.
  For example:
  * If the text is `sample_document.docx`, the Steward will look
    for a file called `sample_document.docx` in the `data/templates`
    directory of the [package], or the ["Templates" folder] of the
    [Playground].
  * If the text is `docassemble.missouri:data/static/sample_form.pdf`,
    that file will be retrieved from the package of the Steward named `docassemble.missouri`.

# <a name="display"></a>Alternative Ways of Displaying Documents

There are alternatives to using [`attachment`] or [`attachment code`] as components
for displaying assembled files to the user.  If you use
the [`variable name`] component in a `attachments` block to create a [`DAFileCollection`] object that
represents the assembled file, you can use this variable to provide
the file to the user in the context of a [`question`] block in a number of
different ways:

{% include side-by-side.html demo="document-links" %}

The [`.url_for()`] method works on [`DAFileCollection`] and [`DAFile`]
objects.

If a [`DAFile`] is inserted as code 
(e.g., with `${ complaint }`), and the [`DAFile`] is a PDF, a shrunken
image of the first page is shown.  If the [`DAFile`] is an RTF or a
DOCX file, a link is shown.

If a [`DAFileCollection`] object is inserted as code, each
file type is inserted.  If you use [`valid formats`] component to limit the file
types created, only the specified file types will be inserted.  For
example:

{% include side-by-side.html demo="document-links-limited" %}

# <a name="update references"></a>Using Tables of Contents and Other References in DOCX Files

If you are using the `docx template file` sub-component and your template file uses a
table of contents or other page references that will change depending
on how the document is assembled, set the `update references` sub-component to `True`.

{% include demo-side-by-side.html demo="update-references" %}

This will cause [LibreOffice] to update all of the references in the
document before saving it and converting it to PDF.

You can also set the `update references` sub-component to a [Python] expression.  If the
expression evaluates to a `True` value, the references will be updated.

If `update references` is not specified, the default behavior is not
to update the references.

# <a name="pdfa"></a>Producing PDF/A Files

If you want the [PDF] file produced by an attachment to be in
[PDF/A] format, you can set the `pdf/a` sub-component to `True`:

{% include side-by-side.html demo="pdf-a" %}

You can also set the `pdf/a` sub-component with [Python] code.  If the code evaluates to
a `True` value, a [PDF/A] will be produced.

If `pdf/a` is not specified, the default behavior is determined by the
interview's [`pdf/a` features setting].

# <a name="password"></a>Protecting PDF Files with a Password

If you want the [PDF] file produced by an attachment to be protected
with a password, you can set the `password` sub-component, and the [PDF] file will be
encrypted.  There are two passwords that can be set: an
"owner" password and a "user" password.

The `password` can be specified in the following ways:

* If set to a string, only the "user" password will be set.
* If set to a list, the first element is the "owner" password and the
  second element is the "user" password.
* If set to a [Python dict], the value of the `owner` key is the
  "owner" password and the value of the `user` key is the "user"
  password.

If the user password and the owner password are the same, then only
the "user" password will be set.

# <a name="language"></a>Assembling Documents in a Different Language than the Current Language

If you need to produce a document in a different language than the
user's language, then the [linguistic functions] may operate in a way
you do not want them to operate.

For example, if your user is Spanish-speaking, but you need to produce
an English language document, you may find that a word or two in the
English language document has been translated into Spanish.  (E.g.,
this can happen if your document template uses [linguistic functions]
from [`docassemble.base.util`]).  You can remedy this by setting the
`language` sub-component/component for the `attachment` component/block.

{% include side-by-side.html demo="document-language" %}

Without the `language: en` sub-component, the output would be:

> This customer would like to order fries y a Coke.

With the `language: en` sub-component, the output is:

> This customer would like to order fries and a Coke.

# <a name="redact"></a>Redacting Information from Documents

If you want to assemble a document but redact certain pieces of
information from it, you can use the [`redact()`] function on the
parts you want redacted, and the text will be replaced with black
rectangles.  If you want to produce an unredacted version of the same
document, assemble it with the `redact: False` sub-component.

{% include side-by-side.html demo="redact" %}

For more information about this feature, see the documentation for the
[`redact()`] function.

# <a name="enable emailing"></a>Enabling the e-mailing of Documents

Most internet service providers block e-mail communications as part of
their efforts to combat [spam], so if you install a [server] locally,
the e-mail feature probably will not work.

As a result, in most cases you will need to edit your [Configuration]
in order for e-mailing to work.  The easiest and most effective way to
enable e-mailing is to use the [Mailgun API] (which is free), but you
can also use an [external SMTP server] hosted by [Mailgun] or another
provider.

# <a name="allow emailing"></a>Preventing the User from e-mailing Documents

When the [`attachments`] component is included in a [`question`] block, the user will be
given an option to e-mail the documents to an e-mail address.  If you
would like to disable this feature, set the `allow emailing` component to `False`.

By default, the user can e-mail documents:

{% include side-by-side.html demo="allow-emailing-true" %}

Including the `allow emailing: False` component will disable this:

{% include side-by-side.html demo="allow-emailing-false" %}

You can also use a [Python] expression instead of `True` or `False`.

# <a name="allow downloading"></a>Allowing the User to Download All Files at Once

If you would like users to be able to download all of the
[`attachments`] as a single [ZIP file], set the `allow downloading` component to
`True`.  By default, this feature is disabled.

{% include side-by-side.html demo="allow-downloading-true" %}

You can also use a [Python] expression instead of `True` or `False`.

You can customize the name of the [ZIP file] by setting the `zip
filename` component:

{% include side-by-side.html demo="allow-downloading-true-zip-filename" %}

# <a name="caching"></a>Document Caching and Regeneration

Since document assembly can take the server a long time,
Stewards use caching to avoid assembling the same document
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
the interim.  To force the re-assembly of the document, use [`code`]
to deletes the variable that represents the document.  Here is an example:

{% include side-by-side.html demo="document-cache-invalidate" %}

If you want to turn off document caching entirely for a given
interview, see the [`cache documents` feature].

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
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
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
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`.comma_and_list()`]: {{ site.baseurl }}/docs/objects.html#DAList.comma_and_list
[`reconsider`]: {{ site.baseurl }}/docs/code.html#reconsider
[Remember]: {{ site.baseurl }}/docs/logic.html
[Dictionary]: {{ site.baseurl }}/docs/groups.html#gather dictionary
[data structures]: {{ site.baseurl }}/docs/groups.html
[a tool]: #list field names
[generate]: #list field names
[`signature` block]: {{ site.baseurl }}/docs/fields.html#signature
[dictionary]: {{ site.baseurl }}/docs/groups.html#gather dictionary
[`pdf/a` features setting]: {{ site.baseurl }}/docs/initial.html#pdfa
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
[Configuration]: {{ site.baseurl }}/docs/configuration.html
[external SMTP server]: {{ site.baseurl }}/docs/configuration.html#smtp
[Mailgun API]: {{ site.baseurl }}/docs/configuration.html#mailgun api
[Mailgun]: https://www.mailgun.com/
[ZIP file]: https://en.wikipedia.org/wiki/Zip_(file_format)
[`redact()`]: {{ site.baseurl }}/docs/functions.html#redact
[docx-table-columns.docx]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/docx-table-columns.docx
[using code to find a template file]: #template file code
[shown above]: #docx template file
[DALang]: {{ site.baseurl }}/docs/interviews.html#yaml
[server]: {{ site.baseurl }}/docs/installation.html
[interview flow]: {{ site.baseurl }}/docs/logic.html
[Embedded DALang]: {{ site.baseurl }}/docs/documents.html#docx template file
[interview session dictionary]: {{ site.baseurl }}/docs/interviews.html#howstored