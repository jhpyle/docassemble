---
layout: docs
title: Hello world example
short_title: Hello World
---

Here is a simple interview file that says "Hello, world!" to the user.

{% highlight yaml %}
---
question: Hello, world!
buttons:
  - Exit: exit
mandatory: True
---
{% endhighlight %}

To run this, first set up your server using [Docker].

Once **docassemble** is up and running in your web browser, click "Log
in" in the upper right hand corner.  The default username and password
are:
 
   * **E-mail**: admin@admin.com
   * **Password**: password

Then, from the menu, select [Playground].  The [Playground] is a
"sandbox" area where you can develop interviews and test them, all
inside the web browser.

![Playground]({{ site.baseurl }}/img/menu-selection-playground.png)

Then, click the ![Add]({{ site.baseurl }}/img/playground-button-add.png)
button to create a new interview.  Call it "hello.yml."

![New interview]({{ site.baseurl }}/img/playground-new-interview.png)

Then, copy and paste the interview code above into the editor:

![Code copied into interview]({{ site.baseurl }}/img/playground-new-interview-with-code.png)

Then, click the ![Save]({{ site.baseurl
}}/img/playground-button-save.png) button, followed by the ![Save and run]({{ site.baseurl
}}/img/playground-button-save-and-run.png) button.

You should see:

![Hello world interview]({{ site.baseurl }}/img/tutorial-hello-world-interview-01.png)

(If you do not have a server yet, you can [try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/hello.yml){:target="_blank"}.)

# Adding a question

Now let's change the interview so that it asks the user a [question].
Edit the interview and change the contents to:

{% highlight yaml %}
---
question: Hello, ${ planet }!
buttons:
  - Exit: exit
mandatory: True
---
question: |
  What is your planet's name?
fields:
  - Your Planet: planet
---
{% endhighlight %}

(If you do not have your own server yet, you can [try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/hello2.yml){:target="_blank"}.)

It should now ask you "What is your planet's name?" and then greet
your world by its name.

Try clicking ![Source]({{ site.baseurl }}/img/button-source.png) in
the navigation bar.  This toggles the display of information that will
help you understand how a question came to be asked.  This can be
helpful for "debugging" your interview.  Information about the
readability of your interview question is also displayed.

![Source]({{ site.baseurl }}/img/hello-world-source-code-for-question.png)

Note that end users will not see the Source tab; it will only be shown
to users if the interview is in the [Playground], or if the server is
[configured as a development server].

In this example, the Source information explains that the interview
tried to show a [`mandatory`] question, but couldn't, because it
needed the definition of the variable `planet`.  Therefore it looked
for a question that offered to define `planet`, and asked that
question of the user.

# Adding some Python code

Now let's extend the interview by adding a [`code`] block that makes a
calculation based on a number provided by the user.

Change the interview code to the following:

{% highlight yaml %}
---
question: Hello, ${ planet }!
subquestion: |
  I surmise that you have no more than ${ inhabitant_count }
  inhabitants.
buttons:
  - Exit: exit
mandatory: True
---
question: |
  What is your planet's name?
fields:
  - Your Planet: planet
---
code: |
  if favorite_number == 42:
    inhabitant_count = 2
  else:
    inhabitant_count = 2000 + favorite_number * 45
---
question: What is your favorite number?
fields:
  - Number: favorite_number
    datatype: number
---
{% endhighlight %}

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/hello3.yml){:target="_blank"}.)

Note that the order in which the [question] and [code] blocks appear
does not determine the order in which questions are asked.  This is
because **docassemble** only asks questions as needed and when needed.
The path of this interview is driven by the single [`mandatory`]
question.  In order to say "Hello, \_\_\_\_\_\_", the **docassemble** needs to
know what `planet` is, so it asks the question "What is your planet's
name?"  Then, in order to say "I surmise that you have no more than
\_\_\_\_ inhabitants," **docassemble** needs to know what
`inhabitant_count` is, so it runs the `code` that computes
`inhabitant_count`.  However, in order to compute that,
**docassemble** needs to know `favorite_number`, so it asks "What is
your favorite number?"  Then it knows everything it needs to know in
order to display the `mandatory` question.

The `code` block contains [Python] code.  The syntax needs to follow
all the rules of [Python].  For example, the `==` syntax tests whether
the `favorite_number` is 42 or not.  The `+` performs addition and the
`*` performs multiplication.  The `=` sets the value of a variable.

# Creating a document

Now let's provide the user with a [document] by adding an [`attachment`].

{% highlight yaml %}
---
question: Hello, ${ planet }!
subquestion: |
  I surmise that you have no more than ${ inhabitant_count }
  inhabitants.
attachment:
  name: A letter for the inhabitants of ${ planet }
  filename: hello
  metadata:
    SingleSpacing: True
  content: |
    Dear ${ planet } residents,

    Hello to all ${ inhabitant_count } of you.

    Goodbye,

    Your friend
buttons:
  - Exit: exit
mandatory: True
---
question: |
  What is your planet's name?
fields:
  - Your Planet: planet
---
code: |
  if favorite_number == 42:
    inhabitant_count = 2
  else:
    inhabitant_count = 2000 + favorite_number * 45
---
question: What is your favorite number?
fields:
  - Number: favorite_number
    datatype: number
---
{% endhighlight %}

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/hello4.yml){:target="_blank"}.)

This creates a document "from scratch" that is available in PDF or RTF
format.  The content of the document is contained in the `content`
directive within the [`attachment`] directive.

Let's also try modifying this interview to use a [DOCX template] in
order to generate a document that will be available to the user in PDF
or DOCX format.

To do this, first open a word processing application capable of saving
files in .docx format (e.g., [Microsoft Word]).  Create a file that
looks like the following:

![Word file]({{ site.baseurl }}/img/hello_planet.png){: .maybe-full-width }

You can format [this file]({{ site.baseurl }}/img/hello_planet.docx)
however you like; in this example, we have indented some text and
inserted an image.  The important thing is that the variable names
`planet` and `inhabitant_count` are spelled correctly and are enclosed
in double curly brackets.

Save the file as a .docx file (e.g., `hello_planet.docx`).

Now you need to make this .docx file available to your interview by
putting the .docx file in the [Templates] folder of your [Playground].

To do this, go to the Folders menu and select "Templates."

![Templates]({{ site.baseurl }}/img/playground-menu-templates.png)

Then, go to "Upload a template file" and click "Browse."

![Upload a template file]({{ site.baseurl }}/img/playground-files-upload-template.png)

Locate your .docx file on your computer and select it.  Then click "Upload."

Now you should see the .docx file listed as one of your Templates.

![Template list]({{ site.baseurl }}/img/playground-files-template-listing.png)

Then, click ![Back]({{ site.baseurl
}}/img/playground-button-back-to-playground-top.png) or
![Back to playground]({{ site.baseurl
}}/img/playground-button-back-to-playground.png) to go back to the
main page of the [Playground].

Now you need to edit the interview so that it uses the .docx file.

In the block with the `attachment`, replace the `content`
directive with a [`docx template file`] directive that references the
file you uploaded.  The interview should look like this:

{% highlight yaml %}
---
question: Hello, ${ planet }!
subquestion: |
  I surmise that you have no more than ${ inhabitant_count }
  inhabitants.
attachment:
  name: A letter for the inhabitants of ${ planet }
  filename: hello
  docx template file: hello_planet.docx
buttons:
  - Exit: exit
mandatory: True
---
question: |
  What is your planet's name?
fields:
  - Your Planet: planet
---
code: |
  if favorite_number == 42:
    inhabitant_count = 2
  else:
    inhabitant_count = 2000 + favorite_number * 45
---
question: What is your favorite number?
fields:
  - Number: favorite_number
    datatype: number
---
{% endhighlight %}

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/hello6.yml){:target="_blank"}.)

For more information about assembling downloadable documents, see the
[documents] section.

# Decorate with an image

Now let's try [decorating] one of the questions with an image.

First you need to upload the image you want to use.

From the [Playground], go to the Folders menu and select "Static
files."  (The files are called "[static]" because they do not change,
unlike templates, which can be different every time.)

![Static files]({{ site.baseurl }}/img/playground-menu-static.png)

Then, go to "Upload a static file" and click "Browse."

![Upload a static file]({{ site.baseurl }}/img/playground-files-upload.png)

After you select the file (or files) on your computer that you want to
upload, click "Upload."

![File ready to be uploaded]({{ site.baseurl }}/img/playground-files-upload-with-preview.png)

You should now see the file listed as one of the "Static files."

![File uploaded]({{ site.baseurl }}/img/playground-files-listing.png)

In this example, the name of the file is `globe.svg`.

Now, click ![Back]({{ site.baseurl
}}/img/playground-button-back-to-playground-top.png) or
![Back to playground]({{ site.baseurl
}}/img/playground-button-back-to-playground.png) and add the following
to your interview:

{% highlight yaml %}
---
image sets:
  freepik:
    images:
      earth: globe.svg
    attribution: |
      Icon made by [Freepik](http://www.flaticon.com/authors/freepik)
---
{% endhighlight %}

The file `globe.svg` is a copyrighted image obtained from the Internet
with an attribution-only license.  The `image sets` block facilitates
the use of such images.  It defines a set of images, called `freepik`,
that share a common attribution.  All the images you obtain from this
source can be added to this image set, and an appropriate attribution
line will be added to the screen whenever the image is used.

Under `images`, we indicate that the shorthand name we will give our
image is `earth`.

Now, edit the "What is your planet's name?" question and add a
[`decoration`] line referencing `earth`:

{% highlight yaml %}
---
question: |
  What is your planet's name?
fields:
  - Your Planet: planet
decoration: earth
---
{% endhighlight %}

Now, when you run the interview, you can see that the image
"decorates" the question:

![Question with decoration]({{ site.baseurl }}/img/playground-interview-with-image.png)

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/hello5.yml){:target="_blank"}.)

For more ideas about how you can extend your interview, check out the
examples area of the [Playground].

# <a name="testing"></a>Testing your interview

Any time you develop an interview, you will want to test it on
multiple devices, and ask other people to test it out and give you
feedback.

The "Save and Run" button is not the only way to start using an
interview in your [Playground].  Any interview in the [Playground] can
be started by visiting its hyperlink.  To get this hyperlink,
right-click on the "<i class="glyphicon glyphicon-link"
aria-hidden="true"></i> Share" button and copy the URL to your
clipboard.  You can share this URL with other people, or bookmark it
in your browser.  When people visit this URL, they will start an
interview.  (Note that this only works if the server you are using is
accessible to the user's device; if you are using a personal computer,
your computer's firewall might prevent other people from accessing
you).

# <a name="packaging"></a>Packaging your interview

So far, we have been running our interview from the [Playground],
which is a testing area where we can test things, break things, and
"play" around with different possibilities.  If our interview has
reached a point where it is flawless and we want to put it into
"production" to that users can use it, we need to move it out of the
[Playground] and install it in a more "permanent" place.

To do this, we bundle our interview into a "package."  Packages can be
installed on the same system, or another system, or they can be shared
with other developers or posted on [GitHub].

Go to the Folders menu and select "Packages."

![Packages menu item]({{ site.baseurl }}/img/playground-menu-packages.png)

This will take you to the ["Packages" folder], where you can create and
edit packages.

![Packages folder]({{ site.baseurl }}/img/playground-folder-packages.png)

If there is an existing package, click the ![Add]({{ site.baseurl
}}/img/playground-button-add.png) button to create a new package.
Otherwise, edit the "New" package.

Call your new package "helloworld."

![Package called helloworld]({{ site.baseurl }}/img/playground-packages-example-helloworld.png)

On this screen, you can define the characteristics of your package and
indicate which resources from the [Playground] should be included in
the package.

Under "Interview files," select your `hello.yml` file.

![Interview files]({{ site.baseurl }}/img/playground-packages-interview-files.png)

Under "Static files," select your `globe.svg` file.

![Static files]({{ site.baseurl }}/img/playground-packages-static-files.png)

If you were creating an actual package for distribution, you should
type a careful description of your package and the contents of a
"README" file here.  But since this is only a tutorial, you can skip
that.

At the bottom of the screen, you will see some buttons:

![Buttons]({{ site.baseurl }}/img/playground-packages-buttons.png)

Click the ![Save]({{ site.baseurl
}}/img/playground-packages-button-save.png) button to save your
package.

Then, once your package is saved in the system, you will see the
following buttons at the top of the screen.

![Buttons]({{ site.baseurl }}/img/playground-packages-buttons-top.png)

Click the ![Install]({{ site.baseurl
}}/img/playground-packages-button-install.png) button.  This will take
a snapshot of your package, bundle it all up into a [Python] package,
and install that [Python] package on the computer.

Now, users can run the interview using a different URL.  If your
server is `interview.example.com`, users will be able to run the
interview by visiting a URL like:

> https://interview.example.com/?i=docassemble.helloworld:data/questions/hello.yml

Previously, the URL to your interview ended with something like
`?i=docassemble.playground1:hello.yml`.  That is a link to the
"bleeding edge" version of your interview as it exists in the
[Playground].  The link that ends with
`?i=docassemble.helloworld:data/questions/hello.yml` is a link to the
snapshot that you installed.  This will be a "stable" version of your
interview.

You can then continue to make changes to the [Playground] version,
while your users are using the snapshot that you installed.  When you
have made further modifications and you have a new version you want to
make available again, you can just click the "Install" button again.

For serious deployments of interviews, [it is recommended] that you use
separate "development" and "production" servers.

Another thing you can do from the "Packages" folder is click the
![Download]({{ site.baseurl
}}/img/playground-packages-button-download.png) button.  This will
download the package as a ZIP file called
`docassemble-helloworld.zip`.

If you unpack the contents of the ZIP file, you will have a folder
called `docassemble-helloworld`.  You can make changes to the files,
then re-ZIP the `docassemble-helloworld` folder, and install the
revised package on a **docassemble** server using the
[Package Management] tool.  Or, if you want to edit the revised
contents of your package in the [Playground] again, click the
![Upload]({{ site.baseurl
}}/img/playground-packages-button-upload.png) button to upload the
contents of your ZIP file into the [Playground].

## <a name="pypi"></a>Storing on PyPI

A **docassemble** package is really just a regular [Python] package.
It follows all of the conventions of [Python] software package
distribution.  As a result, you can share your package on [PyPI], the
central repository for [Python] software.  This means that other
people can install your package on their servers, just as they would
install any [Python] software.

This section of the tutorial will explain how to upload the
`docassemble.helloworld` package to [PyPI], but keep in mind that if
you try this yourself on a package called `docassemble.helloworld`,
you will probably get an error because package names on [PyPI] are
unique and the `docassemble.helloworld` package has already been
uploaded (by me!).  However, these instructions will work if you adapt
them to a unique package of your own.

First, you need to create a username and password on [PyPI].

The **docassemble** [configuration] on your server will need to be set
up to allow publishing to [PyPI].  To configure this, a user with
`admin` [privileges] needs to go to "Configuration" on the menu and
add the following to the [configuration]:

{% highlight yaml %}
pypi: True
{% endhighlight %}

If this configuration has been done, you can go to "Profile" from the
menu and scroll down to the "PyPI Username" and "PyPI Password"
fields.  Fill in these fields with the username and password you just
obtained.

![PyPI username and password]({{ site.baseurl }}/img/profile-pypi-username-password.png)

Then, go to the ["Packages" folder] of the **docassemble**
[Playground] and open your `docassemble-helloworld` package that you
created [above](#packaging).  At the bottom of the screen you will see
a message about whether the package is published on [PyPI] and/or
[GitHub].

![PyPI Info]({{ site.baseurl }}/img/playground-packages-not-published-yet.png)

Press the ![PyPI]({{ site.baseurl
}}/img/playground-packages-button-pypi.png) button to publish the
package to [PyPI].

When the publishing is done, you will see an informational message
with the output of the uploading commands.  Check this message to see
if there are any errors.

If the publishing was successful, then at the bottom of the page
describing your package, you should see a message that the package now
exists on [PyPI].  (However, sometimes the [PyPI] server is slow to
reflect the existence of the package, so you may need to give it a
minute or two.)

![PyPI Info]({{ site.baseurl }}/img/playground-packages-pypi-published.png)

If you click the link, you can see what the package looks like on the
[PyPI] web site.

![PyPI page]({{ site.baseurl }}/img/pypi-helloworld-page.png){: .maybe-full-width }

Now, on the **docassemble** menu (of this server or another server),
you can go to Package Management and [install]
the package by specifying a "Package on PyPI."

![PyPI Install]({{ site.baseurl }}/img/update-package-pypi.png)

For more information about uploading packages to [PyPI], see
the [PyPI subsection] of the [packages] section.

## <a name="github"></a>Storing on Github

You can also share your package on [GitHub], a popular
[version control system] that facilitates collaboration.

You will need an account on [GitHub].  If you do not have one, you can
[create one].

Your **docassemble** configuration will need to be configured to allow
[GitHub] integration.  The instructions for setting that up are
[in the installation section]({{ site.baseurl
}}/docs/installation.html#github).

Once your server allows [GitHub integration], you can go to "Profile"
on the menu and click the link for "GitHub integration."  Follow
the instructions to connect your [GitHub] account with your
**docassemble** account.

Once you have connected your [GitHub] account with your
**docassemble** account, go to the ["Packages" folder] of the
**docassemble** [Playground] and open your `docassemble-helloworld`
package that you created [above](#packaging).  At the bottom of the
screen you will see a message about whether the package is published
on [GitHub].

![GitHub Info]({{ site.baseurl }}/img/playground-packages-github-not-published-yet.png)

Press the ![GitHub]({{ site.baseurl
}}/img/playground-packages-button-github.png) button.

You will be asked for a "commit message."  This is a brief, one-line
message that describes the changes made to your package since the last
time you "committed" changes.  Each "commit" is like a snapshot, and
the history of "commit" messages is a record of the development of
your project.  You can give your first commit a simple name:

![Commit]({{ site.baseurl }}/img/playground-packages-github-commit-helloworld.png){: .maybe-full-width }

However, your subsequent "commits" should have meaningful names that
describe succinctly how that snapshot is different from the previous
snapshot.  You should also use the README text box to describe to
other people the history of all of your changes.

When you press the "Commit" button, your package will be "pushed" to a
"repository" in your [GitHub] account.  If a repository does not
already exist on [GitHub] with the name of your package, a new
repository will be created.

When the uploading is done, you will see an informational message with
the output of the uploading commands.  Check this message to see if
there are any errors.

If the publishing was successful, then at the bottom of the page
describing your package, you should see a message that the package now
exists on [GitHub].

![PyPI Info]({{ site.baseurl }}/img/playground-packages-github-published.png)

If you click the link, you can see what the package looks like on [GitHub]:

![GitHub Repository]({{ site.baseurl }}/img/github-helloworld-repository.png){: .maybe-full-width }

Now, on the **docassemble** menu, you can go to Package Management and
[install] the package using its [GitHub] URL.

![GitHub Install]({{ site.baseurl }}/img/update-package-github.png)

For more information about uploading packages to [GitHub], see
the [GitHub subsection] of the [packages] section.

["Packages" folder]: {{ site.baseurl }}/docs/playground.html#packages
[GitHub subsection]: {{ site.baseurl }}/docs/packages.html#github
[PyPI subsection]: {{ site.baseurl }}/docs/packages.html#pypi
[GitHub]: https://github.com
[`decoration`]: {{ site.baseurl }}/docs/modifiers.html#decoration
[Package Management]: {{ site.baseurl }}/docs/playground.html
[Playground]: {{ site.baseurl }}/docs/playground.html
[installation]: {{ site.baseurl }}/docs/installation.html
[configuration]: {{ site.baseurl }}/docs/config.html
[reconfigured user roles]: {{ site.baseurl }}/docs/users.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[WordPad]: http://windows.microsoft.com/en-us/windows/using-wordpad#1TC=windows-7
[Notepad++]: https://notepad-plus-plus.org/
[document]: {{ site.baseurl }}/docs/documents.html
[documents]: {{ site.baseurl }}/docs/documents.html
[`code`]: {{ site.baseurl }}/docs/code.html
[code]: {{ site.baseurl }}/docs/code.html
[question]: {{ site.baseurl }}/docs/questions.html
[package]: {{ site.baseurl }}/docs/packages.html
[packages]: {{ site.baseurl }}/docs/packages.html
[`root`]: {{ site.baseurl }}/docs/config.html#root
[Docker]: {{ site.baseurl }}/docs/docker.html
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[install]: {{ site.baseurl }}/docs/packages.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[git]: https://git-scm.com/
[git for Windows]: https://git-scm.com/download/win
[PowerShell]: https://en.wikipedia.org/wiki/PowerShell
[Python for Windows]: https://www.python.org/downloads/windows/
[PyPI]: https://pypi.python.org/pypi
[PyPI test server]: https://testpypi.python.org/pypi
[version control system]: https://en.wikipedia.org/wiki/Version_control
[configured as a development server]: {{ site.baseurl }}/docs/config.html#debug
[Microsoft Word]: https://en.wikipedia.org/wiki/Microsoft_Word
[Templates]: {{ site.baseurl }}/docs/playground.html#templates
[static]: {{ site.baseurl }}/docs/playground.html#static
[DOCX template]: {{ site.baseurl }}/docs/documents.html#docx template file
[decorating]: {{ site.baseurl }}/docs/modifiers.html#decoration
[create one]: https://github.com/join
[GitHub integration]: {{ site.baseurl }}/docs/packages.html#github
[privileges]: {{ site.baseurl }}/docs/users.html
[it is recommended]: {{ site.baseurl }}/docs/development.html
