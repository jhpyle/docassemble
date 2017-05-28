---
layout: docs
title: Package management
short_title: Packages
---

# How **docassemble** uses packages

**docassemble** interviews can be packaged into [Python packages] that
are installed on a server.  The [Python package] also includes:

* [Python modules], which include any [classes] and other code that you might
write to go along with your interviews;
* Static content (images, downloadable files) that you want to include
with your interview;
* Data files ([translations], [machine learning] training data) on which
  your interview depends; and
* Any [document templates] you created.

A package containing **docassemble** code needs to be a subpackage of
the `docassemble` package.  The `docassemble` package itself is just
a shell (a [namespace package]) that contains subpackages.  These
subpackages include **docassemble**'s core components as well as
user-created packages.

# Anatomy of a docassemble package

Here is the file structure of a **docassemble** package called
`docassemble.baseball`.

{% highlight text %}
docassemble-baseball
|-- docassemble
|   |-- baseball
|   |   |-- baseball-stats.py
|   |   |-- data
|   |   |   |-- questions
|   |   |   |   |-- baseball-questions.yml
|   |   |   |   `-- hitters.yml
|   |   |   |-- static
|   |   |   |   |-- catcher.jpg
|   |   |   |   `-- pitcher.jpg
|   |   |   |-- sources
|   |   |   |   `-- words.yml
|   |   |   `-- templates
|   |   |       `-- game-summary.md
|   |   `-- __init__.py
|   `-- __init__.py
|-- LICENSE.txt
|-- README.md
|-- setup.cfg
`-- setup.py
{% endhighlight %}

The package is known as `docassemble.baseball` in [Python], but the
name `docassemble-baseball`, replacing the dot with a hyphen, is
sometimes used.  There are reasons for using the hyphen -- in certain
contexts, the dot is considered an invalid character.

There are a lot of subdirectories (this is the nature of
[namespace packages]).  There are reasons for all of these
subdirectories.

1. The top-level directory, `docassemble-baseball`, is
important because a complete [Python] package should be all in one directory.
2. Within that, the `docassemble` directory is necessary so that the
package is a subpackage of `docassemble`.
3. Within that, the `baseball` directory is necessary
because when packages within the `docassemble` [namespace package] are
installed on a system, [Python] needs them to be in a subdirectory
under a directory called `docassemble`.
4. Within `baseball`, you have `baseball-stats.py`, which contains
[Python] code.  The `__init.py__` file is necessary for declaring
`baseball` to be a package; you never have to edit that file.
5. There is also a `data` directory with subdirectories `questions`,
`static`, `sources`, and `templates`.  These are for [interviews],
[static files], [data files], and [document templates].

When installed on the server, the interview `hitters.yml` can be run
by going to a link like
`https://example.com?i=docassemble.baseball:hitters.yml`.

In your own interviews, you can include resources from this package by
writing things like the following:

{% highlight yaml %}
---
include:
  - docassemble.baseball:baseball-questions.yml
---
yesno: person_is_a_catcher
question: |
  Did the person look like this?
subquestion: |
  [FILE docassemble.baseball:catcher.jpg]
---
question: |
  Here is how the game went down.
sets: user_given_summary
attachment:
  - name: Summary of ${ game }
    filename: game_summary
    content file: docassemble.baseball:game-summary.md
---
modules:
  - docassemble.baseball.baseball-stats
{% endhighlight %}

The first example uses [`include`] to incorporate by reference a
[YAML] file located in the `data/questions` directory of the package.

The second example uses a [file reference] to refer to an image file in
the `data/static` directory of the package.

The third example uses [`content file`] within an [`attachment`] to
refer to a [Markdown] file in the `data/templates` directory of the
package.

The fourth example uses [`modules`] to import [Python] names from the
`baseball-stats.py` file.

# Creating your own packages

## On-line

You can create your own **docassemble** package on-line using the
[Packages area] of the [Playground].  This allows you to download a
package as a ZIP file that contains resources from various "folders"
in the [Playground].

## Off-line

To create your own **docassemble** package off-line, start by downloading a
**docassemble** package template from your **docassemble** server.

1. Click "Log in" in the upper right hand corner and log in as:
 
   * **E-mail**: admin@admin.com
   * **Password**: password

   Or, if you have already [reconfigured user roles] on your system,
   log in as any user with the privileges of an Administrator or a
   Developer.
2. On the menu in the upper right hand corner, select Package Management.
3. Click "Create a package."
4. Enter a name for the package, such as `missouri-family-law` and click "Get template."
5. Save the resulting .zip file to your computer.

Then you will have a ZIP file called
`docassemble-missouri-family-law.zip`, which contains a directory
`docassemble-missouri-family-law`.  You can extract this directory to
a convenient location on your computer, so that you can make changes
to the files and/or add files of your own.

# Dependencies

If your package uses code from other [Python] packages that are not
distributed with the standard **docassemble** installation, you will
need to indicate that these packages are "dependencies" of your
package.

This will ensure that if you share your package with someone else and
they install it on their system, the packages that your package needs
will be automatically installed.  Otherwise, that person will get
errors when they try to use your package.

If you maintain your package in the [Packages area] of the
[Playground], you can indicate the dependencies of your package by
selecting them from a multi-select list.

If you maintain your package off-line, you will need to edit the
`setup.py` file and change the line near the end that begins with
`install_requires`.  This refers to a list of [Python] packages.  For
example:

{% highlight python %}
      install_requires=['docassemble', 'docassemble.base', 'docassemble.helloworld', 'kombu'],
{% endhighlight %}

This line indicates that the package relies on `docassemble` and
`docassemble.base` (as all **docassemble** packages do), and also
relies on the **docassemble** extension package
`docassemble.helloworld`, as well as the [Python] package `kombu`.
When someone tries to install `docassemble.baseball` on their system,
`docassemble.helloworld` and `kombu` will be installed first, and any
packages that these packages depend on will also be installed.

Note that if your package depends on a package that exists on [GitHub]
but not on [PyPI], you will also need to add an extra line so that the
system knows where to find the package.  For example, if
`docassemble.helloworld` did not exist on [PyPI], you would need to
include:

{% highlight python %}
      install_requires=['docassemble', 'docassemble.base', 'docassemble.helloworld', 'kombu'],
      dependency_links=['git+https://github.com/jhpyle/docassemble-helloworld#egg=docassemble.helloworld-0.1'],
{% endhighlight %}

If you use the [Packages area] of the [Playground] to maintain your
package, this is all handled for you.

# Installing a package

You can install a **docassemble** extension package, or any other
[Python] package, using the **docassemble** web application.

From the menu, go to Package Management.  Then click "Update a package."

**docassemble** installs packages using the [pip] package manager.
This installation process may take a long time.  A log of the output
of [pip] will be shown when the installation is complete, and in the
background, the server will restart.

## <a name="github_install"></a>Installing through GitHub

One way to install [Python] packages on a server is through [GitHub].

1. Find the [GitHub] URL of the package you want to install.  This is
in the location bar when you are looking at a [GitHub] repository.
For example, the [GitHub] URL of the `docassemble-missouri-family-law`
package may be `https://github.com/jhpyle/docassemble-missouri-family-law`.
2. In the **docassemble** web app, go to Package Management.
3. Click "Update a package."
4. Enter `https://github.com/jhpyle/docassemble-missouri-family-law`
   into the "GitHub URL" field.
5. Click "Update."

## <a name="zip_install"></a>Installing through a .zip file

You can also install [Python] packages from ZIP files.  For example,
if you have a package `docassemble-missouri-family-law`, the ZIP file
will be called `docassemble-missouri-family-law.zip`.  It will contain
a single directory called `docassemble-missouri-family-law`, which in
turn contains `setup.py`, a subdirectory called `docassemble`, and
other files.

1. In the **docassemble** web app, go back to Package Management.
2. Click "Update a package."
3. Under "Zip File," upload the `.zip` file you want to install.
4. Click "Update."

## <a name="pypi_install"></a>Installing through PyPI

You can also install [Python] packages from [PyPI].  [PyPI] is the
central repository for [Python] software.  Anyone can register on
[PyPI] and upload software to it.  For example, if you want to install
the `docassemble-missouri-family-law` package:

1. Make sure the `docassemble-missouri-family-law` package exists on [PyPI].
2. In the **docassemble** web app, go to Package Management.
3. Click "Update a package."
4. Type `docassemble.missouri-family-law` into the "Package on PyPI"
   field.
5. Click "Update."

# Running interviews from installed packages

Once a **docassemble** extension package is installed, you can start
using its interviews.  For example, if you installed
`docassemble.missouri-family-law`, and there was an interview file in
that package called `questions.yml`, you would point your browser to
`http://localhost/?i=docassemble.missouri-family-law:data/questions/questions.yml`
(substituting the actual domain and base URL of your **docassemble**
site).

# <a name="updating"></a>Updating Python packages

To upgrade a package that you installed from a [GitHub] URL or from
[PyPI], you can click the "Update" button next to the package name on
the "Update a package" screen.  You will only see these Update buttons
if you are an administrator or if you are the person who caused the
packages to be installed.  Also, the "Update" buttons will not appear
if the package was installed using a ZIP file.

# <a name="publishing"></a>Publishing a package

## <a name="pypi"></a>Publishing on PyPI

The best place to publish a **docassemble** extension packages is on
[PyPI], the central repository for [Python] software.

In order to publish to [PyPI], you will first need to create an
account on [PyPI].  You will need to choose a username and password
and verify your e-mail address.

Then, go to "Configuration" on the menu and add the username and
password into the **docassemble** [configuration] like so:

{% highlight yaml %}
pypi username: johndoe
pypi password: xX_s3cret_Xx
{% endhighlight %}

After you save the [configuration], go to the ["Packages" folder] of
the **docassemble** [Playground] and open the package you want to
publish (e.g., `docassemble-missouri-family-law`).

Press the ![Publish]({{ site.baseurl
}}/img/playground-packages-publish-button.png) button to publish the
package to [PyPI].

If your package already exists on [PyPI], then clicking the Publish
button will increment the version of your package.  This is necessary
because you cannot overwrite files that already exist on [PyPI].

When the publishing is done, you will see an informational message
with the output of the uploading commands.  Check this message to see
if there are any errors.

If the publishing was successful, then at the bottom of the page
describing your package, you should see a message that the package now
exists on [PyPI].

![PyPI Info]({{ site.baseurl }}/img/playground-packages-published.png)

You can click on the link to see what the package looks like on [PyPI].

Now, on the **docassemble** menu (of this server or another server),
you can go to Package Management -> Update a Package, and
[install](#pypi_install) the package by specifying a "Package on PyPI"
and typing in `docassemble.missouri-family-law`.

## <a name="github"></a>Publishing on GitHub

You can publish your package on [GitHub] in addition to (or instead
of) publishing it on [PyPI].  Publishing on both sites is recommended,
however.  [PyPI] is the simplest and safest way to distribute [Python]
packages, while [GitHub] is a version control system with many
features for facilitating sharing and collaboration.

If you do not have [git] on your computer, install it.  If you use
Windows, install [git for Windows], choosing all of the default
options when installing.

Sign up for a [GitHub] account if you do not already have one.

Then create a [GitHub] repository.  If your **docassemble** extension
package is `docassemble.missouri-family-law`, the name of the [GitHub]
package should be `docassemble-missouri-family-law`.

After you press ![Create Repository]({{ site.baseurl
}}/img/github-create-repository.png), your browser will go to the URL
for your new repository, which will be in a form like
`https://github.com/jhpyle/docassemble-missouri-family-law`.  In this
example, `jhpyle` is the username, and
`docassemble-missouri-family-law` is the name of the repository.

In the "Packages" folder of the **docassemble** [Playground], edit
your package and add the [GitHub] URL as the "URL" of the package.
This will ensure that if your package is a dependency for another
package, that other package will be able to install your package as
one of its dependencies when it is installed on a server.

Then save your package and then download it as a ZIP file.  Extract
the files from the ZIP file to a convenient place on your computer.

You will see a directory with the name of your package (e.g.,
`docassemble-missouri-family-law`.  This directory will contain a
directory called `docassemble` and a file called `setup.py`.  The top
directory (e.g., `docassemble-missouri-family-law`) will be the root
directory of your new [GitHub] repository.

The process of initializing a package as a [GitHub] repository
requires using the shell.  (On Windows, you can use [PowerShell].)
The web page at the URL for your repository on [GitHub] contains some
instructions about how to initialize your repository.  First, use `cd`
to change into the directory that contains the package you want to
install (in this example, we'll use `docassemble-missouri-family-law`)
and then run the [git] commands suggested by [GitHub].  For example:

{% highlight text %}
cd docassemble-missouri-family-law
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/jhpyle/docassemble-missouri-family-law.git
git push -u origin master
{% endhighlight %}

The last command will prompt you for your [GitHub] credentials.  After
you put in the credentials, your package will be uploaded to
[GitHub].  If you reload your [GitHub] repository's page at the
[GitHub] URL, you will see the listing of files.

Now, on the **docassemble** menu, you can go to Package Management ->
Update a Package, and install the package using its [GitHub] URL.

# Best practices for packaging your interviews

It is a good practice to bundle related interviews in a single
package.  Think about making it easy for other people to install your
packages on their system and make use of your [questions] and [code].

It is also a good practice to separate your interview into at least
three files, separately containing:

* [mandatory] and [initial] code
* [initial blocks]
* [question] and [code] blocks

This way, other people can take advantage of your work product in
interviews that might have a very different purpose.

[Python for Windows]: https://www.python.org/downloads/windows/
[git for Windows]: https://git-scm.com/download/win
[how to submit a package to PyPI]: https://packaging.python.org/distributing/
[PowerShell]: https://en.wikipedia.org/wiki/PowerShell
[Packages area]: {{ site.baseurl }}/docs/playground.html#packages
[Playground]: {{ site.baseurl }}/docs/playground.html
[interviews]: {{ site.baseurl }}/docs/interviews.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[Markdown]: https://daringfireball.net/projects/markdown/
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[Python packages]: https://docs.python.org/2/tutorial/modules.html#packages
[Python package]: https://docs.python.org/2/tutorial/modules.html#packages
[installation]: {{ site.baseurl }}/docs/installation.html
[configuration]: {{ site.baseurl }}/docs/config.html
[user login system]: {{ site.baseurl }}/docs/users.html
[document templates]: {{ site.baseurl }}/docs/documents.html
[questions]: {{ site.baseurl }}/docs/questions.html
[question]: {{ site.baseurl }}/docs/questions.html#question
[code]: {{ site.baseurl }}/docs/code.html
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[namespace package]: https://www.python.org/dev/peps/pep-0420/
[namespace packages]: https://www.python.org/dev/peps/pep-0420/
[reconfigured user roles]: {{ site.baseurl }}/docs/users.html
[GitHub]: https://github.com/
[WSGI]: http://en.wikipedia.org/wiki/Web_Server_Gateway_Interface
[Windows application]: https://desktop.github.com/
[Python modules]: https://docs.python.org/2/tutorial/modules.html
[classes]: https://docs.python.org/2/tutorial/classes.html
[`root`]: {{ site.baseurl }}/docs/config.html#root
[pip]: https://en.wikipedia.org/wiki/Pip_%28package_manager%29
[PyPI]: https://pypi.python.org/pypi
[PyPI test server]: https://testpypi.python.org/pypi
[mandatory]: {{ site.baseurl }}/docs/logic.html#mandatory
[initial]: {{ site.baseurl }}/docs/logic.html#initial
[initial blocks]: {{ site.baseurl }}/docs/logic.html#mandatory
[machine learning]: {{ site.baseurl }}/docs/ml.html
[translations]: {{ site.baseurl }}/docs/config.html#words
[pip/utils/appdirs.py]: https://github.com/pypa/pip/blob/master/pip/utils/appdirs.py
[file reference]: {{ site.baseurl }}/docs/markup.html#inserting images
[`content file`]: {{ site.baseurl }}/docs/documents.html#content file
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[static files]: {{ site.baseurl }}/docs/playground.html#static
[data files]: {{ site.baseurl }}/docs/playground.html#sources
[git]: https://git-scm.com/
["Packages" folder]: {{ site.baseurl }}/docs/playground.html#packages
