---
layout: docs
title: Interview developers' playground
short_title: Playground
---

The "Playground" within the **docassemble** web application is a
testing ground for interviews.  It allows you to write [YAML] in one
or more "files" and then run an interview with one click.

# Components of the Playground page

![playground]({{ site.baseurl }}/img/playground.png){: .full-width }

## The YAML text editor

The main area of the Playground consists of an in-browser text editor
in which you can edit YAML [interview] files.

![playground]({{ site.baseurl }}/img/playground-main.png)

Each "tab" on the Playground page represents a separate [YAML] file,
or a folder in which you can store files.

To create a new [YAML] file, click the <i class="glyphicon
glyphicon-plus-sign" aria-hidden="true"></i> icon.

You can use each tab for a different interview.

You can also use multiple tabs to organize parts of a single
interview.  For example, if you have a tab called "interview.yml" and a tab
called "questions.yml," you can incorporate one into the other by
reference.

For example, suppose your "interview.yml" tab contains:

{% highlight yaml %}
---
include:
  - questions.yml
---
mandatory: true
code:
  say_hello
---
{% endhighlight %}

and suppose your "questions.yml" tab contains:

{% highlight yaml %}
---
sets: say_hello
question: |
  Hello, world!
---
{% endhighlight %}

If you run the "interview.yml" tab, you will go to an interview that says
"Hello, world!"  The "interview.yml" interview knew how to ask `say_hello`
because it incorporated the "questions.yml" tab by reference.

If you write more than one interview, you might want to put all of
your questions into a separate [YAML] file (e.g. "questions.yml") so
that you can easily re-use the questions in different contexts.  Your
main interview files will consist only of "mandatory" code blocks.
Improvements you make to the questions will be available automatically
to all interviews.

## The Templates folder

![Templates]({{ site.baseurl }}/img/playground-templates.png)

If you create [documents], you might want to use separate document
templates.  In a typical **docassemble** package, these templates are
files in the `data/templates` subdirectory.  In the Playground, they
are stored in the "Templates" folder.  For more information about the
different types of template files that can be provided as options to
the `attachments` directive, see [documents].

For example, you can write Markdown text in a separate text file
called `small_claims_complaint.md` in the Templates folder and then
incorporate that text by reference by including the line `content
file: small_claims_complaint.md` within an `attachments` directive.

## The Static folder

![Static]({{ site.baseurl }}/img/playground-static.png)

If your interviews include images or sound, you can bundle image and
audio files with your interview's **docassemble** [package] by
including them within the `data/static` subdirectory.  In the
Playground, these files are located within the "Static" folder.  In
this area, you can upload files or write files of your own.  For
example, you might want to write your own Javascript files here.

## Variables, etc.

![variables]({{ site.baseurl }}/img/playground-variables.png)

The "Variables, etc." area contains a list of variables and other
names that are available for use in your interview.  Clicking on one
of the names will insert the name into the text editor.  You may find
this helpful if you are not sure of the exact spelling of a variable.

The list is updated when the page loads, or when you press "Save" or "Save
and Run."

The area lists the following types of names (which are color-coded):

* Variables: variables that are mentioned in your questions and code
  blocks, or that have been included in the Python namespace through a
  `modules` statement
* Functions: functions that are available because they have been
  included in the Python namespace through a `modules` statement
* Classes: classes that are available because they have been
  included in the Python namespace through a `modules` statement
* Modules: modules that are available because they have been included
  in the Python namespace through a `import` statement

## Example blocks

![example area]({{ site.baseurl }}/img/playground-example-area.png){: .full-width }

The part of the page below the text editor is an interactive area where
you can browse example blocks that demonstrate various features of
**docassemble**.  You can use these examples as models or to remind
you of what the valid **docassemble** syntax is.  You can also insert blocks
directly into the text editor.

The area consists of three parts:

* The "Example blocks" part is a list, in outline form, of example
blocks that you can view.
* The "Preview" part is a screenshot demonstrating what the example
block does.  If you click on the preview, an example interview
containing the example block will open in another tab.
* The "Source" part contains the text of the example block.  You can
click "Insert" to copy it into the text editor.  You can click "Show
context of example" to see the other blocks that are necessary for the
example block to run as part of a working interview.  This working
interview is what you will run when you click the "Preview"
screenshot.

# How to use the Playground

* The "Save and Run" function will open an interview in another window.  Your
  browser might block this as an unwanted pop-up window.  Make sure to
  tell your browser to allow pop-ups from **docassemble**.
* Once you are running the interview in another tab, changes that you
  make to the interview you ran will be visible if you refresh the
  screen.  However, these changes will only re-appear if you changed
  the same file that you ran; you will not see changes to files
  included by reference unless you re-save the file you ran.
* Interviews you create in the "Playground" cannot directly be run by
  the general public or by other developers; to share an interview
  with others, you need to prepare a [package].
* The "Playground" does not offer a full range of authoring
  functionality.  It does not allow you to edit [Python modules].  It
  is a place to test interview code quickly, not a complete
  development platform.  To learn how to access the full range of
  authoring functionality, see the [packages] section.

[package]: {{ site.baseurl }}/docs/packages.html
[packages]: {{ site.baseurl }}/docs/packages.html
[Python package]: {{ site.baseurl }}/docs/packages.html
[Python modules]: https://docs.python.org/2/tutorial/modules.html
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[interview]: {{ site.baseurl }}/docs/interviews.html
[documents]: {{ site.baseurl }}/docs/documents.html
