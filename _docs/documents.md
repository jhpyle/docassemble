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

The above question creates a document containing the text "Hello,
world!"  By default, the document is created in PDF and RTF format,
and the user will be given the option to e-mail the document to
himself.  The filenames will be `Hello_World_Document.pdf` and
`Hello_World_Document.rtf`

The `name`, `filename`, and `description` items can contain [Mako]
templates.  The `name` and `description` filenames can also contain
[Markdown].  (The `filename` cannot contain [Markdown], since it's a
filename, after all.)

The `content` item, of course, can contain [Mako] and [Markdown].
[Pandoc] converts the content into HTML (for previewing in the
browser), PDF, and RTF.

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

## Special markup

* `[INDENTATION]` - From now on, indent every paragraph.
* `[NOINDENTATION]` - From now on, do not indent every paragraph.
* `[BEGIN_TWOCOL] First column text [BREAK] Second column text [END_TWOCOL]` -
  Puts text into two columns.  The text in the columns cannot contain [Markdown].
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
* `[SKIPLINE]` - Skip a line (insert vertical space).  Cannot be used
  within environments like `[FLUSHLEFT]`, `[CENTER]`, and
  `[BOLDCENTER]`.
* `[BR]` - Insert a line break.  `[BR]` is useful to use with
  environments like `[FLUSHLEFT]`, `[CENTER]`, and `[BOLDCENTER]` that
  only apply to a single paragraph.  Within `[BEGIN_TWOCOL]`, a paragraph
  break (pressing enter twice, i.e., leaving one blank line) has the
  same effect.
* `[TAB]` - Insert a tab (horizontal space), e.g., to indent the first
  line of a paragraph when it otherwise would not be indented.

## Document metadata



[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[YAML]: [YAML]: https://en.wikipedia.org/wiki/YAML
[Pandoc]: http://johnmacfarlane.net/pandoc/
