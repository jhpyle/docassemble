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
with which you can edit [YAML]&nbsp;[interview] files.

![playground]({{ site.baseurl }}/img/playground-main.png)

To create a new [YAML] file, click the <i class="glyphicon
glyphicon-plus-sign" aria-hidden="true"></i> icon.

You can use multiple files to organize parts of a single interview.
For example, if you have a file called "interview.yml" and a file called
"questions.yml," you can incorporate one into the other by reference.

For example, suppose your "interview.yml" file contains:

{% highlight yaml %}
---
include:
  - questions.yml
---
mandatory: True
code:
  say_hello
---
{% endhighlight %}

and suppose your "questions.yml" file contains:

{% highlight yaml %}
---
sets: say_hello
question: |
  Hello, world!
---
{% endhighlight %}

If you run the "interview.yml" file, you will go to an interview that says
"Hello, world!"  The "interview.yml" interview knew how to ask `say_hello`
because it incorporated the "questions.yml" file by reference.

If you write more than one interview, you might want to put all of
your questions into a separate [YAML] file (e.g. "questions.yml") so
that you can easily re-use the questions in different contexts.  Your
main interview files will consist only of "mandatory" code blocks.
Improvements you make to the questions will be available automatically
to all interviews.

## Folders

Within your Playground there are five "folders" where you can upload,
download, and/or create various resources related to the development
of your interviews.  These include:

* [Templates](#templates) for storing [Markdown] and PDF
  templates that are used in documents and interview questions.
* [Static files](#static) for images, Javascript, CSS, and other
  auxillary files that your interview uses.
* [Sources](#sources) for [YAML] files containing translations of text
  into other languages, as well as for training data for the
  [machine learning] function of **docassemble**.
* [Modules](#modules) for [Python] code that extends the features of
  your interview.  You can also embed [Python] code directly into your
  interviews, but your interviews will be more readable if you keep
  its embedded [Python] code limited to if/then/else statements.
* [Packages](#packages) for bundling your interviews into packages for
  installation on a production server or other means of distribution.

### <a name="templates"></a>The Templates folder

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

{% include scroll-image.html image="playground-templates-page-clipped.png" %}

In the Templates folder, you can upload files.  Markdown and YAML
files can be edited.  From the Templates screen, you can convert
uploaded files from [Microsoft Word] format (`.docx`, `.doc`, or
`.rtf`) or [OpenDocument] format (`odt`) to Markdown (`.md`) format,
so that you can include the text in your documents.

### <a name="static"></a>The Static folder

If your interviews include images or sound, you can bundle image and
audio files with your interview's **docassemble** [package] by
including them within the `data/static` subdirectory.  In the
Playground, these files are located within the "Static" folder.

{% include scroll-image.html image="playground-static-page-clipped.png" %}

In this area, you can upload files or write files of your own.  For
example, you might want to write your own Javascript files here, or
upload images that you want to include in interview questions.

### <a name="sources"></a>The Sources folder

{% include scroll-image.html image="playground-sources-page-clipped.png" %}

This is where you can store data files for use by your interviews,
including:

* Translation files for the [`word()`] function, which you can include
using the [`words`] directive in the [configuration].
* Training data for the [machine learning] function.

### <a name="modules"></a>The Modules folder

If your interviews contain any complicated Python code, or you want to
create your own classes, you should create a Python module and import
its names into your interview.  In a **docassemble** [package], these
are located in the main directory (the directory that contains the
`data` subdirectory).  In the Playground, these files are located
within the "Modules" folder.  In this area, you can write your own
Python classes and functions.

{% include scroll-image.html image="playground-modules-page-clipped.png" %}

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

### <a name="packages"></a>The Packages folder

The Packages area allows you to bundle the [interview files], [templates],
[static files], and/or [modules] from your Playground into a
[Python package] that can be downloaded as a ZIP file.

You can keep track of one or more packages in the Packages folder.  Each
package has its own tab.  To create a new package, click the <i
class="glyphicon glyphicon-plus-sign" aria-hidden="true"></i> icon.

{% include scroll-image.html image="playground-packages-page-clipped.png" %}

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
* **README file**: This is a text box into which you can type the
  contents of the `README.md` file that will be included in your
  package.  If you leave this blank, the `README.md` file will list
  the package name, package description, and author.

At the bottom of the page, you can press one of the following buttons:

* **Save**: Saves the package definition and does nothing more.
* **Download**: Saves the package definition and provides the package
  as a ZIP file for you to download.
* **Install**: Saves the package definition, creates a ZIP file
  containing the package, and installs that ZIP file on the server.
* **Delete**: Deletes the package definition.  If you installed the
  package on the system, it does not uninstall the package.

To change the author information that is included in the package, edit
your [profile].

For more information on managing [Python packages] within
**docassemble**, see [packages].

## <a name="variables"></a>The Variables, etc. area

![variables]({{ site.baseurl }}/img/playground-variables.png)

The "Variables, etc." area is a coding aid.  It contains a list of
variables and other names that are available for use in your
interview.  Clicking on one of the names will insert the name into the
text editor.  You may find this helpful if you are not sure of the
exact spelling of a variable or a function.

In addition, if you start typing a name and then press Ctrl-Space, the
editor will attempt to auto-complete the name for you.  If there are
multiple possibilities, you can choose the name from the list.

The list is updated when the page loads, or when you press "Save" or "Save
and Run."

The area lists the following types of names (which are color-coded):

* Variables: variables that are mentioned in your questions and code
  blocks, or that have been included in the Python namespace through a
  [`modules`] statement.  Variables in light blue are
  **docassemble**'s [special variables].
* Functions: functions that are available because they have been
  included in the Python namespace through a [`modules`] statement.
* Classes: classes that are available because they have been
  included in the Python namespace through a [`modules`] statement.
* Modules defined: modules that are available because they have been
  included in the Python namespace through a [`import`] statement.
* Modules available in Playground: modules that are available to be
  included with [`modules`] or [`import`] because they exist in the
  [modules] folder of the Playground.
* Templates: template files available in the [Templates folder] of the
  Playground.
* Static files: static files available in the [Static folder] of the
  Playground.
* Decorations: decorations defined with [`images`] or [`image sets`]
  that are available for inclusion with [`decoration`] or [emoji] markup.

By default, the "Variables, etc." area shows variables for the [YAML]
file you are currently editing.  However, if the [YAML] file you are
editing is a component of an interview, the information in the
"Variables, etc." will not be complete.  At the top of the "Variables,
etc." area, you can select a different file that should be used for
purposes of populating the "Variables, etc." section.  Usually the
file you want to select here is the "top level" file for your
interview, which [`include`]s the file you are editing.

### Meaning of icons

* Clicking ![magnifying glass]({{ site.baseurl
  }}/img/playground-icon-magnifying-glass.png) next to a variable name
  will search the [text editor] for the variable name.
* Clicking ![information]({{ site.baseurl
  }}/img/playground-icon-info.png) shows a pop-up containing
  information about the item and a link to the item's documentation.
* Clicking ![cog]({{ site.baseurl }}/img/playground-icon-cog.png)
  reveals the methods of an [object].
* Clicking ![question mark]({{ site.baseurl
  }}/img/playground-icon-question-mark.png) next to a category name
  shows information about that category.

## The buttons

![buttons]({{ site.baseurl }}/img/playground-buttons.png){: .full-width }

The "Save" button will save the interview and do nothing more.

The "Save and Run" button will save the interview and run the
interview in another window.

The "Delete" button will remove the interview from the Playground.

To give a link to the interview to someone else, right-click on the
"<i class="glyphicon glyphicon-link" aria-hidden="true"></i> Share"
button and copy the URL to your clipboard.

Note that users do not need to log in to be able to run interviews
using these links.  If you want to protect your interviews during
development, you can add an initial block like this, which will stop
anyone other than a developer from using the interview:

{% highlight yaml %}
---
initial: True
code: |
  if not user_has_privilege('developer'):
    message("Only developers can access this interview.", show_restart=False)
---
{% endhighlight %}

Note that the "Playground" is a development platform.  If you are
going to put an interview into production, put it into a package.  You
can create a package in the [packages area].

## <a name="examples"></a>The examples area

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
containing the example block will open in another tab.  There is a
"View documentation" button that will open the page of the
**docassemble** documentation pertaining to the concept illustrated in
the example.
* The "Source" part contains the text of the example block.  You can
click "Insert" to copy it into the text editor.  You can click "Show
context of example" to see the other blocks that are necessary for the
example block to run as part of a working interview.  This working
interview is what you will run when you click the "Preview"
screenshot.

# <a name="wizard"></a>The Wizard

If you are new to **docassemble**, a good way to learn is by using the
"Wizard" to construct a document assembly interview.  To launch the
wizard, click the "Wizard" button.

![buttons]({{ site.baseurl }}/img/playground-wizard.png)

The Wizard allows you to upload one or more documents in Microsoft
Word format in which you have indicated with square brackets the areas
where the interview needs to "fill in the blanks."

For example, your Word file could include:

  > Your phone number is \[phone number\] and you live in \[city\].

Along the way, the Wizard will show you what blocks it is adding the
interview it is generating.

When you are done specifying the elements of your interview, the
Wizard allows you to download the assembled interview as a [package].

# Recovering from infinite loops

If you accidentially write code that gets into an infinite loop, the
only way to stop the code is to terminate the process in which the
code is runnnig.  In a production web server environment, this could
impact other users because the process may be running multiple threads
for different users, only one of which is stuck in an infinite loop.
Unfortunately, it is not possible in [Python] to terminate a specific
thread.

Restarting the web server will terminate the process.

If you are running the [Docker] implementation of **docassemble**, a
watchdog runs in the background ([`docassemble.webapp.watchdog`]),
looks for [Apache] processes that appear to be stuck, and terminates
them after 60-90 seconds.

If the interview with the infinite loop is in the Playground, and the
code with the infinite loop runs at the beginning of the interview,
the editing screen will not load at all.  This is due to the fact that
the Playground page's [Variables, etc.](#variables) feature needs to
run the interview in order to figure out what variables are in use.
To get around this, you need to edit the URL that accesses the
interview.  If your interview is `myinterview.yml`, the URL that edits
the interview will be something like

{% highlight text %}
https://dev.example.com/playground?file=myinterview.yml
{% endhighlight %}

You will need to add `&debug=1` to the end:

{% highlight text %}
https://dev.example.com/playground?file=myinterview.yml&debug=1
{% endhighlight %}

Then the editing screen will load.

[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[package]: {{ site.baseurl }}/docs/packages.html
[packages]: {{ site.baseurl }}/docs/packages.html
[Python package]: {{ site.baseurl }}/docs/packages.html
[Python packages]: {{ site.baseurl }}/docs/packages.html
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
[interview files]: #interview_files
[templates]: #templates
[template files]: #templates
[static files]: #static
[modules]: #modules
[packages area]: #packages
[emoji]: {{ site.baseurl }}/docs/markup.html#emoji
[`decoration`]: {{ site.baseurl }}/docs/modifiers.html#decoration
[profile]: {{ site.baseurl }}/docs/users.html#profile
[Microsoft Word]: https://en.wikipedia.org/wiki/Microsoft_Word
[OpenDocument]: https://en.wikipedia.org/wiki/OpenDocument
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[Docker]: {{ site.baseurl }}/docs/docker.html
[`docassemble.webapp.watchdog`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/watchdog.py
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`word()`]: {{ site.baseurl }}/docs/functions.html#word
[`words`]: {{ site.baseurl }}/docs/config.html#words
[configuration]: {{ site.baseurl }}/docs/config.html
[machine learning]: {{ site.baseurl }}/docs/ml.html
[object]: {{ site.baseurl }}/docs/objects.html
[text editor]: #interview_files
[Templates folder]: #templates
[Static folder]: #static
[special variables]: {{ site.baseurl }}/docs/special.html
