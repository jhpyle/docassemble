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

## <a name="interview_files"></a>The [YAML] text editor

The main area of the Playground consists of an in-browser text editor
in which you can edit [YAML] [interview] files.

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

## <a name="templates"></a>The Templates folder

![Templates]({{ site.baseurl }}/img/playground-templates.png)

If you create [documents], you might want to use separate document
templates.  In a typical **docassemble** package, these templates are
files in the `data/templates` subdirectory.  In the Playground, they
are stored in the "Templates" folder.  For more information about the
different types of template files that can be provided as options to
the [`attachments`] directive, see [documents].

For example, you can write Markdown text in a separate text file
called `small_claims_complaint.md` in the Templates folder and then
incorporate that text by reference by including the line `content
file: small_claims_complaint.md` within an [`attachments`] directive.

## <a name="static"></a>The Static folder

![Static]({{ site.baseurl }}/img/playground-static.png)

If your interviews include images or sound, you can bundle image and
audio files with your interview's **docassemble** [package] by
including them within the `data/static` subdirectory.  In the
Playground, these files are located within the "Static" folder.  In
this area, you can upload files or write files of your own.  For
example, you might want to write your own Javascript files here, or
upload images that you want to include in interview questions.

## <a name="modules"></a>The Modules folder

If your interviews contain any complicated Python code, or you want to
create your own classes, you should create a Python module and import
its names into your interview.  In a **docassemble** [package], these
are located in the main directory (the directory that contains the
`data` subdirectory).  In the Playground, these files are located
within the "Modules" folder.  In this area, you can write your own
Python classes and functions.

The best way to incorporate your module into your interview is to use
Python's notation for "relative imports."  For example, if your module
file is called `fruit.py`, you would import the module's resources by
writing a [`modules`] statement:

{% highlight yaml %}
---
modules:
  - .fruit
---
{% endhighlight %}

This notation will work both in the Playground and when the interview
is bundled as a Python module.

## <a name="packages"></a>The Packages area

![Packages]({{ site.baseurl }}/img/playground-packages.png)

The Packages area allows you to bundle the [interview files], [templates],
[static files], and/or [modules] from your Playground into a
[Python package] that can be downloaded as a ZIP file.

You can keep track of one or more packages in the Packages area.  Each
package has its own tab.  To create a new package, click the <i
class="glyphicon glyphicon-plus-sign" aria-hidden="true"></i> icon.

Packages are defined with the following elements:

* **Package Name**: By necessity, all **docassemble** packages are
  subpackages of the `docassemble` [namespace package].  If the
  Package Name is "bankruptcy," the actual [Python package] will be
  known as `docassemble.bankruptcy`.
* **Version**: The version number you indicate here will be the
  version number of your [Python package].
* **License**: This is the name of the software license that will be associated with your
  [Python package].  The default license is "The MIT License (MIT),"
  which is the license under which **docassemble** is distributed.
  This is probably what you want to use.  However, if you want to take
  greater control over your intellectual property, you can indicate a
  different license.  If you choose the MIT License, the content of
  the license will be included in the package, but if you choose
  another, you will need to edit the `LICENSE` file manually.
* **Description**: This is a short description of your package (no
  more than 255 characters).
* **URL**: This is a URL for the documentation for your package, if
  any.  Defaults to a link to the **docassemble** documentation.
* **Dependencies**: From the Python [packages] installed on the
  system, indicate the ones that are required for your package to
  operate.  When your package is installed on another system, these
  packages will be installed first.
* **Interview files**: From the [interview files] defined in your
  Playground, indicate which ones should be included in your package.
* **Template files**: From the [template files] defined in your
  Playground, indicate which ones should be included in your package.
* **Static files**: From the [static files] defined in your
  Playground, indicate which ones should be included in your package.
* **Modules**: From the [modules] defined in your
  Playground, indicate which ones should be included in your package.

At the bottom of the page, you can press one of the following buttons:

* **Save**: Saves the package definition and does nothing more.
* **Download**: Saves the package definition and provides the package
  as a ZIP file for you to download.
* **Install**: Saves the package definition, creates a ZIP file
  containing the package, and installs that ZIP file on the server.
* **Delete**: Deletes the package definition.  If you installed the
  package on the system, it does not uninstall the package.

For more information on managing [Python packages] within
**docassemble**, see [packages].

## <a name="variables"></a>Variables, etc.

![variables]({{ site.baseurl }}/img/playground-variables.png)

The "Variables, etc." area is a coding aid.  It contains a list of
variables and other names that are available for use in your
interview.  Clicking on one of the names will insert the name into the
text editor.  You may find this helpful if you are not sure of the
exact spelling of a variable or a function.

The list is updated when the page loads, or when you press "Save" or "Save
and Run."

The area lists the following types of names (which are color-coded):

* Variables: variables that are mentioned in your questions and code
  blocks, or that have been included in the Python namespace through a
  [`modules`] statement
* Functions: functions that are available because they have been
  included in the Python namespace through a [`modules`] statement
* Classes: classes that are available because they have been
  included in the Python namespace through a [`modules`] statement
* Modules defined: modules that are available because they have been
  included in the Python namespace through a [`import`] statement
* Modules available in Playground: modules that are available to be
  included with [`modules`] or [`import`] because they exist in the
  [modules] folder of the Playground.
* Templates: template files available in the Templates folder of the
  Playground
* Static files: static files available in the Static folder of the
  Playground
* Decorations: decorations defined with [`images`] or [`image sets`]
  that are available for inclusion with [`decoration`] or [emoji] markup.

## <a name="examples"></a>Example blocks

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

![buttons]({{ site.baseurl }}/img/playground-buttons.png){: .full-width }

The "Save" button will save the interview and do nothing more.

The "Save and Run" button will open an interview in another window.
Your browser might block this as an unwanted pop-up window.  Make sure
to tell your browser to allow pop-ups from **docassemble**.

Once you are running the interview in another tab, changes that you
make to the interview you ran will be visible if you refresh the
screen on the interview you are running.  However, these changes will
only re-appear if you changed the same file for which you pressed
"Save and Run"; you will not see changes to files included by
reference unless you re-save the file you ran.

The "Delete" button will remove the interview from the Playground.

To give a link to the interview to someone else, right-click on the
"<i class="glyphicon glyphicon-link" aria-hidden="true"></i> Share"
button and copy the URL to your clipboard.

Note that the "Playground" is a development platform.  If you are
going to put an interview into production, put it into a package by
going to the [packages area].

[package]: {{ site.baseurl }}/docs/packages.html
[packages]: {{ site.baseurl }}/docs/packages.html
[Python package]: {{ site.baseurl }}/docs/packages.html
[Python modules]: https://docs.python.org/2/tutorial/modules.html
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[interview]: {{ site.baseurl }}/docs/interviews.html
[documents]: {{ site.baseurl }}/docs/documents.html
[`attachments`]: {{ site.baseurl }}/docs/documents.html#attachments
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`import`]: {{ site.baseurl }}/docs/initial.html#import
[`images`]: {{ site.baseurl }}/docs/initial.html#images
[`image sets`]: {{ site.baseurl }}/docs/initial.html#image sets
[namespace package]: https://www.python.org/dev/peps/pep-0420/
[interview files]: "#interview_files"
[templates]: "#templates"
[template files]: "#templates"
[static files]: "#static"
[modules]: "#modules"
[packages area]: "#packages"
[emoji]: {{ site.baseurl }}/docs/markup.html#emoji
[`decoration`]: {{ site.baseurl }}/docs/modifiers.html#decoration
