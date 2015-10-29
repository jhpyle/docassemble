---
layout: docs
title: Attaching documents to questions
short_title: Documents
---

The `attachments` statement (which can also be written `attachment`)
provides documents to the user.  Users can preview, download, and/or
e-mail the documents.

{% highlight yaml %}
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    description: A document with a **classic** message
    content: |
      Hello, world!
---
{% endhighlight %}

On the screen, the user will see:

![document screenshot]({{ site.baseurl }}/img/document-example.png)

The `name`, `filename`, and `description` items can contain [Mako]
templates.  The `name` and `description` filenames can also contain
[Markdown].  (The `filename` cannot contain [Markdown], since it's a
filename, after all.)

The `content` item can contain [Mako] and [Markdown].  [Pandoc]
converts the content into PDF, RTF, and HTML (for previewing in the
browser).

The PDF file will be called `Hello_World_Document.pdf` and will look
like this in a PDF viewer (depending on the user's software):

![document screenshot]({{ site.baseurl }}/img/document-example-pdf.png)

The RTF file will be called `Hello_World_Document.rtf` and will look
like this in a word processor (depending on the user's software):

![document screenshot]({{ site.baseurl }}/img/document-example-rtf.png)

If the user clicks the "Preview" tab, an HTML version of the document
will be visible:

![document screenshot]({{ site.baseurl }}/img/document-example-preview.png)

## Storing document text in separate files

If the `content` is lengthy and you would rather not type it into the
interview [YAML] file, you can import the content from a separate file
using `content file`:

{% highlight yaml %}
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    content file: hello.md
---
{% endhighlight %}

Content of the [Markdown] file, `hello.md`:

{% highlight markdown %}
Hello, world!
{% endhighlight %}

Files referenced with `content file` are assumed to reside in the
`data/templates` directory within the package in which the interview
[YAML] file is located.  You can specify filenames in other packages
by referring to the package name.  For example:
`docassemble.demo:data/templates/complaint.md`.

The `content file` can also refer to a list of file names:

{% highlight yaml %}
content file:
  - introduction.md
  - jurisdiction.md
  - discussion.md
{% endhighlight %}

The content of multiple `content file` files will be concatenated.

## Limiting availability of formats

You can also limit the file formats available:
{% highlight yaml %}
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    valid_formats:
      - pdf
    description: A document with a **classic** message
    content: |
      Hello, world!
---
{% endhighlight %}

In this example, the user will not have the option of seeing an HTML
preview and will only be able to download the PDF file:

![document screenshot]({{ site.baseurl }}/img/document-example-pdf-only.png)

## Formatting documents with special markup tags

In addition to using [Markdown] syntax, you can use
**docassemble**-specific markup tags to control the appearance of
documents.

* `[INDENTATION]` - From now on, indent every paragraph.
* `[NOINDENTATION]` - From now on, do not indent every paragraph.
* `[BEGIN_TWOCOL] First column text [BREAK] Second column text [END_TWOCOL]` -
  Puts text into two columns.
* `[FLUSHLEFT]` - Used at the beginning of a paragraph to designate
  that the paragraph should be flushed left and not indented.
* `[CENTER]` - Used at the beginning of a paragraph to designate that
  the paragraph should be centered.
* `[BOLDCENTER]` - Like `[CENTER]` except that text is bolded.
* `[SINGLESPACING]` - From now on, paragraphs should be single-spaced.
* `[DOUBLESPACING]` - From now on, paragraphs should be double-spaced.
* `[NBSP]` - Insert a non-breaking space.
* `[ENDASH]` - Insert an en dash.
* `[EMDASH]` - Insert an em dash.
* `[HYPHEN]` - Insert a hyphen.
* `[PAGEBREAK]` - Insert a manual page break.
* `[PAGENUM]` - Insert the current page number.
* `[SECTIONNUM]` - Insert the current section number.
* `[SKIPLINE]` - Skip a line (insert vertical space).  (Cannot be used
  within `[FLUSHLEFT]`, `[CENTER]`, and `[BOLDCENTER]` environments.)
* `[BR]` - Insert a line break.  `[BR]` is useful to use with
  environments like `[FLUSHLEFT]`, `[CENTER]`, and `[BOLDCENTER]` that
  only apply to a single paragraph.  Within the `[BEGIN_TWOCOL]`
  environment, a standard [Markdown] paragraph break (pressing enter
  twice, i.e., leaving one blank line) has the same effect.
* `[TAB]` - Insert a tab (horizontal space), e.g., to indent the first
  line of a paragraph when it otherwise would not be indented.

## Formatting documents with Pandoc templates and metadata

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
      SingleSpacing: true
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

Metadata values can contain [Mako] template commands.  However, they
cannot contain [Markdown].

### Metadata applicable to RTF and PDF files

* If you wish to use a standard document title, set the following:
  * `title`
  * `author` - a list
  * `date`
* `toc` - default is not defined.  If defined, a table of contents is
  included.
* `SingleSpacing` - set this to `true` for single spacing.
* `OneAndAHalfSpacing` - set to `true` for 1.5 spacing.
* `DoubleSpacing` - set this to `true` for double spacing.  Double spacing
  is the default.
* `TripleSpacing` - set this to `true` for triple spacing.
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
* `HeaderLines` - if you have a header containing more than one line
  (lines should be separated by `[BR]`), set `HeaderLines` to the number
  of the lines in the header, so that [LaTeX] can apply the
  appropriate spacing between the header and the text.

The use of `HeaderLines` is important.  For example, a business letter
may contain a first page header with three lines on it, and a second
page header with two lines:

{% highlight yaml %}
    metadata:
      FirstHeaderRight: |
        Example, LLP [BR] 123 Main Street, Suite 1500 [BR]
        Philadelphia, PA 19102
      HeaderLeft: |
        ${ client } [BR] ${ today() } [BR] Page [PAGENUM]
      HeaderLines: "3"
{% endhighlight %}

In this case, the `HeaderLines: "3"` metadata will ensure that [LaTeX]
formats the headers correctly.  Otherwise the header may overlap the
document text.

### Metadata applicable to PDF only

The following metadata tags only apply to PDF file generation.  To
change analogous formatting in RTF files, you will need to create your
own RTF document template (for more information on how to do that, see
the next section).

* `fontfamily` - default is `mathptmx` (Times Roman).
* `lang` - not defined by default.  If defined, [polyglossia] (for
  XeTeX) or [babel] is loaded and the language is set to this.
* `papersize` - default is `letterpaper`.
* `documentclass` - default is `article`.
* `numbersections` - default is `true`.  If true, sections are
  numbered; if false, they are not.  (In [LaTeX], `secnumdepth` is
  set to 5, otherwise 0.)
* `geometry` - default is
`left=1in,right=1in,top=1in,heightrounded,includeheadfoot`.  These are
options for the the [geometry] package that set the page margins.
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

## Additional customization of document formatting

You can exercise greater control over document formatting by creating
your own template files for [Pandoc].  The default template files are
located in the `docassemble.base` package in the `docassemble/base/data/templates`
directory.  The files include:

* `Legal-Template.tex`: this is the [LaTeX] template that [Pandoc]
  uses to generate PDF files.
* `Legal-Template.yml`: default [Pandoc] metadata for the
  `Legal-Template.tex` template, in [YAML] format.  Options passed
  through `metadata` items within an `attachment` will append or
  overwrite these default options.
* `Legal-Template.rtf`: this is the template that [Pandoc] uses to
  generate RTF files.  You can edit this file to change default
  styles, headers, and footers.

To use your own template files, specify them using the following
options to `attachment`:

* `initial yaml`: one or more [YAML] files from which [Pandoc]
  metadata options should be gathered.  If specified, the default file
  `Legal-Template.yml` is not loaded.  If specifying more than one
  file, use [YAML] list syntax.
* `additional yaml`: one or more [YAML] files from which [Pandoc]
  metadata options should be gathered, in addition to whatever options
  are loaded through `initial_yaml`.  This can be used to load the
  metadata in `Legal-Template.yml` but to overwrite particular values.
  If specifying more than one file, use [YAML] list syntax.
* `template file`: a single `.tex` file to be used as the [Pandoc]
  template for converting [Markdown] to PDF.
* `rtf template file`: a single `.rtf` file to be used as the [Pandoc]
  template for converting [Markdown] to RTF.

Filenames are assumed to reside in the `data/templates` directory
within the package in which the interview [YAML] file is located.  You
can specify filenames in other packages by referring to the package
name.  For example: `docassemble.demo:data/templates/MyTemplate.tex`.

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

## A note about customization of document formatting

If exercising fine-grained control over document formatting is
important to you, and you are not prepared to learn how [Pandoc] and
[LaTeX] work, then **docassemble** may not be right tool for you.
**docassemble** does not allow for [WYSIWYG] formatting of document
templates the way [HotDocs] does.

Rather, **docassemble** is designed to allow template authors to focus
on substance rather than form.  Producing a case caption by typing `${
pleading.caption() }` is ultimately easier on the author of a legal
form than worrying about the formatting of the case caption on each
page of every legal document the author writes.

[Pandoc] and [LaTeX] are powerful tools.  There are published books
written in [Markdown] and converted to PDF with [Pandoc].  There is
little that [LaTeX] cannot do.

The skill set needed to achieve a particular formatting objective
using [Pandoc] and [LaTeX] is different from the skill set needed to
write a user-friendly interview and design the substance of a
document.  Ideally, a software engineer will design appropriate
templates and functions for use by authors, who can concentrate on
substantive content.

[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
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
