---
layout: docs
title: Attaching documents to questions
short_title: Documents
---

# <a name="attachments"></a>The `attachments` statement

The `attachments` statement (which can also be written `attachment`)
provides documents to the user.  Users can preview, download, and/or
e-mail the documents.

## Creating PDF and Word files from Markdown

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

## <a name="content file"></a>Storing document text in separate files

If the content of your document is lengthy and you would rather not
type it into the interview [YAML] file as `content`, you can import
the content from a separate file using `content file`:

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

{% highlight text %}
Hello, world!
{% endhighlight %}

Files referenced with `content file` are assumed to reside in the
`data/templates` directory within the package in which the interview
[YAML] file is located.  You can specify filenames in other locations
by specifying a package name and path.  For example:
`docassemble.demo:data/templates/complaint.md`.

The `content file` can also refer to a list of file names:

{% highlight yaml %}
content file:
  - introduction.md
  - jurisdiction.md
  - discussion.md
{% endhighlight %}

The content of multiple `content file` files will be concatenated.

## <a name="pdf template file"></a>Filling PDF forms

If you have a PDF file that contains fillable fields (e.g. fields
added using Adobe Acrobat Pro), **docassemble** can assemble a PDF
file by filling in fields in that template.  To do this, provide a
`pdf template file` and a dictionary of `fields`.

For example, here is an interview that populates fields in a file
called [sample-form.pdf]({{ site.demourl }}/packagestatic/docassemble.demo/sample-form.pdf):

{% highlight yaml %}
---
mandatory: true
question: |
  Here is your PDF form
attachments:
  - name: A filled-in form
    filename: filled-form
    pdf template file: sample-form.pdf
    fields:
      Your Name: |
        ${ user }
      Your Organization: |
        ${ user.organization }
      Apple Checkbox: |
        ${ likes_apples }
      Orange Checkbox: |
        ${ likes_oranges }
      Pear Checkbox: |
        ${ likes_pears }
      Toast Checkbox: |
        ${ likes_toast }
---
{% endhighlight %}

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/testfill.yml){:target="_blank"}.)

The `pdf template file` is assumed to reside in the `data/templates`
directory of your package, unless a specific package name is
specified.  E.g.:

{% highlight yaml %}
    pdf template file: docassemble.missouri-family-law:data/templates/form.pdf
{% endhighlight %}

The `fields` must be in the form of a [YAML] dictionary.  Checkbox
fields will be checked if the value evaluates to "True" or "Yes."

### <a name="list field names"></a>How to get a list of field names in a PDF file

When logged in to **docassemble** as a developer, you can go to
"Utilities" from the menu and, under "Get list of fields from fillable
PDF," you can upload a PDF file that has fillable fields in it.
**docassemble** will scan the PDF file, identify its fields, and
present you with the [YAML] text of a question that uses that PDF file
as a `pdf template file`.

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
signature into the template [Transfer-of-Ownership.pdf]({{ site.demourl }}/packagestatic/docassemble.demo/Transfer-of-Ownership.pdf):

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - user: Individual
  - friend: Individual
---
mandatory: true
code: |
  need(user.name.first, friend.name.first, prized_collection, final_screen)
---
question: |
  What is your name?
fields:
  - First Name: user.name.first
  - Last Name: user.name.last
---
question: |
  What is your best friend's name?
fields:
  - First Name: friend.name.first
  - Last Name: friend.name.last
---
question: What objects do you collect?
fields:
  - Collection: prized_collection
    hint: baseball cards, fine china
---
question: |
  Please sign your name below.
signature: user.signature
under: |
  ${ user }
---
sets: final_screen
question: Congratulations!
subquestion: |
  You have now transferred everything you own to ${ friend }.
attachment:
  - name: Transfer of Ownership
    filename: Transfer-of-Ownership
    pdf template file: Transfer-of-Ownership.pdf
    fields:
      "grantor": ${ user }
      "grantee": ${ friend }
      "collection": ${ prized_collection }
      "signature": ${ user.signature }
---
{% endhighlight %}

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/testfillsignature.yml){:target="_blank"}.)

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

## <a name="variable name"></a>Saving documents as variables

Including an `attachments` section in a [`question`] block will offer
the user a chance to download an assembled document and e-mail it to
themselves.

Sometimes, you might want to do other things with the document, like
e-mail it, or post it to a web site.

You can save an assembled document to a variable by adding
a `variable name` key to an attachment.  For example:

{% highlight yaml %}
---
modules:
  - docassemble.base.legal
---
objects:
  - authority: Individual
---
question: Your document is ready.
subquestion: |
  Would you like to submit the document below to the authorities?
yesno: submit_to_authority
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    variable name: hello_file
    content: |
      Hello, world!
---
mandatory: true
question: Ok, all done.
subquestion: |
  % if submit_to_authority:
    % if sent_ok:
  Your document was sent.
    % else:
  For some reason, I was not able to send your document.
    % endif
  % else:
  Ok, I will not send your document to The Man.
  % endif
---
code: |
  sent_ok = send_email(to=[authority], template=my_email, attachments[hello_file])
---
code: |
  authority.name.first = 'The'
  authority.name.last = 'Man'
  authority.email = 'man@hegemony.gov'
---
template: my_email
subject: |
  A PDF file that says hello world!
content: |
  Dear Authority,

  Please see attached.
---
{% endhighlight %}

You can also assemble a document and save it to a variable without
presenting it to the user.  The following example creates a PDF file
containing the message "Hello, world!" and posts it to a slack.com
site.

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
mandatory: true
code: |
  import slacker
  slacker.Slacker(daconfig['slack_api_key']).files.upload(my_file.pdf.filename)
---
mandatory: true
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

Note that the varible indicated by `variable name` will be defined as
an object of class `DAFileCollection`.  An object of this type will
have attributes for each file type generated, where the attributes are
objects of type `DAFile`.  So `my_file.pdf` is the PDF `DAFile`, and
`my_file.rtf` is the RTF `DAFile`.  A `DAFile` has the following
attributes:

* `filename`: the path to the file on the filesystem;
* `mimetype`: the MIME type of the file;
* `extension`: the file extension (e.g., `pdf` or `rtf`); and
* `number`: the internal integer number used by **docassemble** to
  keep track of documents stored in the system

See [objects] for an explanation of the `DAFile` and
`DAFileCollection` classes.

## <a name="valid formats"></a>Limiting availability of formats

You can also limit the file formats available:
{% highlight yaml %}
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    valid formats:
      - pdf
    description: A document with a **classic** message
    content: |
      Hello, world!
---
{% endhighlight %}

In this example, the user will not have the option of seeing an HTML
preview and will only be able to download the PDF file:

![document screenshot]({{ site.baseurl }}/img/document-example-pdf-only.png)

## <a name="docx"></a>Assembling documents in DOCX format

**docassemble** can use [Pandoc] to convert [Markdown] into a
Microsoft Word .docx file.  These .docx files are not created by
default because they do not support all of the features that are
supported by RTF and PDF formats, such as tables (which are necessary
for case captions).  To generate .docx files, specify `docx` as one of
the `valid formats`:

{% highlight yaml %}
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    valid formats:
      - docx
      - pdf
    description: A document with a **classic** message
    content: |
      # Hey there
      
      Hello, world!
---
{% endhighlight %}

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/testdocx.yml){:target="_blank"}.)

To customize document styles, headers, and footers, see the `docx
reference file` setting, discussed below.

## <a name="language"></a>Assembling documents in a different language than the current language

If you need to produce a document in a different language than the
user's language, then the [`word()`] function may operate in a way you
do not want it to operate.

For example, if your user is Spanish-speaking, but you need to produce
an English language document, you may find that a word or two in the
English language document has been translated into Spanish.  (E.g.,
this can happen if your document template uses linguistic [functions]
from [`docassemble.base.util`]).  You can remedy this by defining a
`language` for the document.

For example:

{% highlight yaml %}
---
language: es
question: El documento está listo.
sets: provide_user_with_document
attachment:
  - name: Alimentos
    language: en
    filename: food_order
    content: |
      This customer would like to order
      ${ comma_and_list('fries', 'a Coke') }.
---
{% endhighlight %}

## <a name="allow emailing"></a>Preventing the user from e-mailing documents

When [`attachments`] are included in a [`question`], the user will be
given an option to e-mail the documents to an e-mail address.  If you
would like to disable this feature, set `allow emailing` to `false`.

By default, the user can e-mail documents:

{% include side-by-side.html demo="allow-emailing-true" %}

Including `allow emailing: false` will disable this:

{% include side-by-side.html demo="allow-emailing-false" %}

# <a name="markup"></a>Formatting documents with special markup tags

In addition to using [Markdown] syntax, you can use
**docassemble**-specific markup tags to control the appearance of
documents.

* `[INDENTATION]` - From now on, indent the first line of every paragraph.
* `[NOINDENTATION]` - From now on, do not indent the first line of
  every paragraph.
* `[BEGIN_TWOCOL] First column text [BREAK] Second column text
  [END_TWOCOL]` - Puts text into two columns.
* `[FLUSHLEFT]` - Used at the beginning of a paragraph to indicate
  that the paragraph should be flushed left and not indented.
* `[FLUSHRIGHT]` - Used at the beginning of a paragraph to indicate
  that the paragraph should be flushed right and not indented.
* `[CENTER]` - Used at the beginning of a paragraph to indicate that
  the paragraph should be centered.
* `[BOLDCENTER]` - Like `[CENTER]` except that text is bolded.
* `[INDENTBY 1in]` - Used at the beginning of a paragraph to indicate
  that all the lines paragraph should be indented on the left.  In
  this example, the amount of indentation is one inch.  You can
  express lengths using units of `in` for inches, `pt` for points, or
  `cm` for centimeters.
* `[INDENTBY 1in 0.5in]` - This is like the previous tag, except it
  indents both on the left and on the right.  In this example, the
  amount of left indentation is one inch and the amount of right
  indentation is half an inch.
* `[BORDER]` - Used at the beginning of a paragraph to indicate that
  the paragraph should have a box drawn around it.  (The border will
  only go around one paragraph; that is, the effect of `[BORDER]`
  lasts until the next empty line.  You can use `[NEWPAR]` in place of
  an empty line to extend the effect of the `[BORDER]` tag to
  another paragraph.)
* `[SINGLESPACING]` - From now on, paragraphs should be single-spaced.
* `[ONEANDAHALFSPACING]` - From now on, paragraphs should be
  one-and-a-half-spaced.
* `[DOUBLESPACING]` - From now on, paragraphs should be double-spaced.
* `[NBSP]` - Insert a non-breaking space.
* `[ENDASH]` - Normally, `--` produces an en-dash, but if you want to
  be explicit, `[ENDASH]` will do the same thing.
* `[EMDASH]` - Normally, `---` produces an em-dash, but if you want to
  be explicit, `[EMDASH]` will do the same thing.
* `[HYPHEN]` - Insert a hyphen.  Normally, `---` produces an em-dash, but if you want to
  be explicit, `[HYPHEN]` will do the same thing.
* `[PAGEBREAK]` - Insert a manual page break.
* `[PAGENUM]` - Insert the current page number.
* `[SECTIONNUM]` - Insert the current section number.
* `[NEWPAR]` - Insert a paragraph break.  (Cannot be used within
  `[FLUSHLEFT]`, `[FLUSHRIGHT]`, `[CENTER]`, or `[BOLDCENTER]` environments.)
* `[SKIPLINE]` - Skip a line (insert vertical space).  This is
  different from `[NEWPAR]` because `[NEWPAR]` breaks a paragraph but
  multiple calls to `[NEWPAR]` will not insert additional vertical
  space.  (Cannot be used within `[FLUSHLEFT]`, `[FLUSHRIGHT]`,
  `[CENTER]`, or `[BOLDCENTER]` environments.)
* `[BR]` - Insert a line break.  `[BR]` is useful to use with
  environments like `[FLUSHLEFT]`, `[FLUSHRIGHT]`, `[CENTER]`, and
  `[BOLDCENTER]` that only apply to a single paragraph.  Within the
  `[BEGIN_TWOCOL]` environment, a standard [Markdown] paragraph break
  (pressing enter twice, i.e., leaving one blank line) has the same
  effect.
* `[TAB]` - Insert a tab (horizontal space), e.g., to indent the first
  line of a paragraph when it otherwise would not be indented.

# <a name="pandoc"></a>Formatting documents with Pandoc templates and metadata

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

Metadata values can contain [Mako] template commands.

## <a name="metadata rtf pdf"></a>Metadata applicable to RTF and PDF files

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
  
## <a name="metadata pdf"></a>Metadata applicable to PDF only

The following metadata tags only apply to PDF file generation.  To
change analogous formatting in RTF files, you will need to create your
own RTF document template (for more information on how to do that, see
the next section).

* `fontfamily` - default is `mathptmx` (Times Roman).
* `lang` and `mainlang` - not defined by default.  If defined,
  [polyglossia] (for XeTeX) or [babel] is loaded and the language is
  set to `mainlang` if [polyglossia] is loaded and `lang` if [babel]
  is loaded.
* `papersize` - default is `letterpaper`.
* `documentclass` - default is `article`.
* `numbersections` - default is `true`.  If true, sections are
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

# <a name="customization"></a>Additional customization of document formatting

You can exercise greater control over document formatting by creating
your own template files for [Pandoc].  The default template files are
located in the [`docassemble.base`] package in the
`docassemble/base/data/templates` directory.  The files include:

* `Legal-Template.tex`: this is the [LaTeX] template that [Pandoc]
  uses to generate PDF files.
* `Legal-Template.yml`: default [Pandoc] metadata for the
  `Legal-Template.tex` template, in [YAML] format.  Options passed
  through `metadata` items within an `attachment` will append or
  overwrite these default options.
* `Legal-Template.rtf`: this is the template that [Pandoc] uses to
  generate RTF files.
* `Legal-Template.docx`: this is the reference file that [Pandoc] uses
  to generate DOCX files.  You can edit this file to change default
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
* `docx reference file`: a single `.docx` file to be used as the
  [Pandoc] docx reference file for converting [Markdown] to DOCX.

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

# <a name="customization note"></a>A note about customization of document formatting

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
[objects]: {{ site.baseurl }}/docs/objects.html
[function]: {{ site.baseurl }}/docs/functions.html
[functions]: {{ site.baseurl }}/docs/functions.html
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`attachments`]: #attachments
[`IndividualName`]: #IndividualName
[`ChildList`]: #ChildList
[`Income`]: #Income
[`Asset`]: #Asset
[`Expense`]: #Expense
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[`word()`]: {{ site.baseurl }}/docs/functions.html#word
