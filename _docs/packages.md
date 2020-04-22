---
layout: docs
title: Package management
short_title: Packages
---

# <a name="how"></a>How **docassemble** uses packages

**docassemble** interviews can be packaged into [Python packages] that
bundle together:

* [YAML] files representing interview files that start interviews, or
  [YAML] files that are [`include`]d in other files;
* Any [document templates] that your interviews use;
* Static content (images, downloadable files) that you want to include
  with your interview;
* [Python modules], which include any [classes] and other code that
  you might write to go along with your interviews; and
* Data files ([translations], [machine learning] training data) on
  which your interview depends.

A [Python package] also contains metadata such as author information,
a brief description, and a list of other [Python packages] on which the
package depends.  It also contains a "README" file, typically styled
with [Markdown], which describes the package in detail.

A package containing **docassemble** interviews must be a [subpackage]
of the `docassemble` package.  In practice, this means that the
official package name with `docassemble.`; e.g.,
`docassemble.missourifamilylaw`.  The `docassemble` package itself is
just a shell (a [namespace package]) that contains subpackages.  These
subpackages include **docassemble**'s core components
(`docassemble.base`, `docassemble.webapp`) as well as user-created
packages (e.g., `docassemble.missourifamilylaw`).

# <a name="playground"></a>Using the Playground to make packages

One of the features of the **docassemble** web application is the
[Playground], a browser-based development platform for developing and
testing interviews.  This is a "sandbox" in which you can make changes
to an interview and immediately test the effect of those changes.  You
can use the [Playground] to create a variety of resources (interview
files, template files, static files, data files) and then [build
packages] out particular resources.

Every interview that you run on **docassemble** is part of a package.
When you are running an interview in the [Playground], the package is
called `docassemble.playground1` or something similar; the `1` at the
end is the user ID of the person who is using the [Playground].

Packages like `docassemble.playground1` should be considered temporary
and should only be used for development and testing.  When you want
your users to actually use your interview, you should move your
interview out of the [Playground] and into a package with an
appropriate name.

Suppose you have an interview file called `custody.yml`, which you are
developing in the [Playground].  When you right click the "<i
class="glyphicon glyphicon-link" aria-hidden="true"></i> Share"
button, and copy the link URL, or you look at your browser location
bar when you are testing the interview, you will see that the URL for
the interview contains`?i=docassemble.playground1:custody.yml`.  This
means that the interview (`i`) is in the `docassemble.playground1`
package and is called `custody.yml`.  This link always runs the
version of your interview that is current in the [Playground].  So if
you make a change that accidentally introduces a bug, anyone who uses
the interview will see an error message.

When you have actual users, you want to be able to make "upgrades" to
your interviews without causing users to see error messages.  You need
to have a distinction between your "development" version and your
"production" version.  Here is a workflow for accomplishing this:

1. Develop your `custody.yml` interview in the [Playground] and keep
   improving it until it is ready for use by users.
2. In the ["Packages" folder] of the [Playground], create a package
   called, e.g., `johnsmithlaw`.  Give it a version number like 0.0.1.
   Include within the package the `custody.yml` interview file and any
   other resources on which `custody.yml` depends.
3. This will create a [Python package] called
   `docassemble.johnsmithlaw`.
4. In the ["Packages" folder] of the [Playground], click the "Install"
   button.  This will install the `docassemble.johnsmithlaw` package
   on your server.
5. Your users can now access your interview at a URL that ends with
   `/interview?i=docassemble.johnsmithlaw:data/questions/custody.yml`.
6. Now you can continue making changes to the `custody.yml` interview
   in the [Playground], and even if you break something, your users
   will not get an error, because they will be using the installed
   version of the package, not the version in your [Playground].
7. When the new version of your interview is ready, you can go to the
   ["Packages" folder] and press "Install" again.
8. Your users will still use the same URL to access the interview (one
   that ends with
   `/interview?i=docassemble.johnsmithlaw:data/questions/custody.yml`), but now
   they will be using the new version of your interview.

For more information, see [how you run a **docassemble** interview],
the [Playground], the [packaging your interview] section of the [hello
world] example, and the [development workflows] section.

From the ["Packages" folder], you can also press "<i class="glyphicon
glyphicon-download" aria-hidden="true"></i> Download" to obtain a ZIP
file of the [Python] package.  If you open this file, you can see what
the structure of a **docassemble** extension package looks like.

# <a name="anatomy"></a>Anatomy of a docassemble package

Here is the file structure of a (fictional) **docassemble** package
called `docassemble.baseball`.

{% highlight text %}
docassemble-baseball
|-- docassemble
|   |-- baseball
|   |   |-- baseballstats.py
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
|-- LICENSE
|-- README.md
|-- setup.cfg
`-- setup.py
{% endhighlight %}

The package is known as `docassemble.baseball` within [Python] code,
but the name `docassemble-baseball`, replacing the dot with a hyphen,
is used in other contexts, such as when referring to a package
published on the [PyPI] site, or a folder on your system that contains
the source code of the package.

There are a lot of subdirectories (this is the nature of
[namespace packages]).  There are reasons for all of these
subdirectories.

1. The top-level directory, `docassemble-baseball`, is important
because a complete [Python] package should be all in one directory.
If you are publishing a package on [GitHub], this directory should be
the root of the repository; `docassemble-baseball/.git` will contain
the [git]-related information for the package.
2. Within that, the `docassemble` directory is necessary so that the
package is a subpackage of `docassemble`.
3. Within that, the `baseball` directory is necessary
because when packages within the `docassemble` [namespace package] are
installed on a system, [Python] needs them to be in a subdirectory
under a directory called `docassemble`.
4. Within `baseball`, you have `baseballstats.py`, which contains
[Python] code.  Files in this directory correspond with files in the
["Modules" folder] of the [Playground].  The `__init.py__` file is
necessary for declaring `baseball` to be a package; you never have to
edit that file.  The `__init.py__` file is mostly empty except for a
`__version__` definiton, but its presence is still important.
5. There is also a `data` directory with subdirectories `questions`,
`static`, `sources`, and `templates`.  These are for [interviews],
[static files], [data files], and [document templates].  The
`questions` directory contains the [YAML] files that are in the main
part of the [Playground].

Note that in the [Playground], there is a ["Modules" folder] along
with a ["Templates" folder], a ["Static" folder], etc., but in a
[Python] package, there is no `docassemble/baseball/data/modules`
folder, even though there is a `docassemble/baseball/data/templates`
folder and a `docassemble/baseball/data/static` folder.  The modules
files (`.py` files) are located in a different place: directly under
`docassemble/baseball`.  Since the main purpose of a [Python] package
is to store [Python] modules, modules files are the "main attraction"
and everything else is just associated "data."  A [Python module] that
you refer to as `docassemble.baseball.baseballstats` must be a file
`baseballstats.py` that is located in the subdirectory
`docassemble/baseball/`.  (This is how [Python] works.)

When installed on the server, the interview `hitters.yml` can be run
by going to a link like
`https://example.com/interview?i=docassemble.baseball:data/questions/hitters.yml`.

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
  - docassemble.baseball.baseballstats
{% endhighlight %}

The first block uses [`include`] to incorporate by reference a
[YAML] interview file located in the `data/questions` directory of the
package.

The second block uses a [file reference] to refer to an image file in
the `data/static` directory of the package.

The third block uses [`content file`] within an [`attachment`] to
refer to a [Markdown] file in the `data/templates` directory of the
package.

The fourth block uses [`modules`] to import [Python] names from the
`baseballstats.py` file.

Since a [Python] package is just a collection of files in a particular
structure, you can maintain your **docassemble** extension packages
"offline" (outside of the [Playground]) if you want.  This allows you
to expand the directory structure beyond what the [Playground]
supports.

# <a name="dependencies"></a>Dependencies

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
selecting them from a multi-select list.  (If you the Python package
you need is not listed, you need to install it on your system using
"Package Management" on the menu.)

If you maintain your package off-line, you will need to edit the
`setup.py` file and change the line near the end that begins with
`install_requires`.  This refers to a list of [Python] packages.  For
example:

{% highlight python %}
install_requires=['docassemble.helloworld', 'kombu'],
{% endhighlight %}

This line indicates that the package relies on the **docassemble**
extension package `docassemble.helloworld`, as well as the [Python]
package `kombu`.  When someone tries to install `docassemble.baseball`
on their system, `docassemble.helloworld` and `kombu` will be
installed first, and any packages that these packages depend on will
also be installed.

Note that if your package depends on a package that exists on [GitHub]
but not on [PyPI], you will also need to add an extra line so that the
system knows where to find the package.  For example, if
`docassemble.helloworld` did not exist on [PyPI], you would need to
include:

{% highlight python %}
install_requires=['docassemble.helloworld', 'kombu'],
dependency_links=['git+https://github.com/jhpyle/docassemble-helloworld#egg=docassemble.helloworld-0.1'],
{% endhighlight %}

If you use the [Packages area] of the [Playground] to maintain your
package, this is all handled for you.

# <a name="installing"></a>Installing a package

You can install a **docassemble** extension package, or any other
[Python] package, using the **docassemble** web application.

From the menu, go to "Package Management."

**docassemble** installs packages using the [pip] package manager.
This installation process may take a long time.  A log of the output
of [pip] will be shown when the installation is complete.  The server
will restart so that any old versions of the package that are still in
memory will be refreshed.

## <a name="github_install"></a>Installing through GitHub

One way to install [Python] packages on a server is through [GitHub].

1. Find the [GitHub] URL of the package you want to install.  This is
in the location bar when you are looking at a [GitHub] repository.
For example, the [GitHub] URL of the `docassemble-baseball`
package may be `https://github.com/jhpyle/docassemble-baseball`.  (No
such package actually exists.)
2. In the **docassemble** web app, go to Package Management.
3. Enter `https://github.com/jhpyle/docassemble-baseball`
   into the "GitHub URL" field.
4. The "GitHub Branch" field will be updated with the default branch
   of the repository (usually `master`).  You can select another
   branch if you wish to install a different branch of the repository.
5. Click "Update."

![GitHub Install]({{ site.baseurl }}/img/github-install.png){: .maybe-full-width }

If you want to install from a private [Github] repository, you will
need a URL that points to your repository and that includes
authentication information.  To make such a URL, you will need a
"personal access token."  If you do not already have a personal access
token, go to your "Settings," go to "Developer settings," and go to
the "Personal access tokens" tab.  Click "Generate new token."  You
can set the "Token description" to whatever you like (e.g. "for
installing on docassemble").  Check the "repo" checkbox, so that all
of the capabilities under "repo" are selected.  Then click "Generate
token."  Copy the "personal access token" and keep it in a safe place.

If your token is `e8cc02bec7061de98ba4851263638d7483f63d41`, your
GitHub username is `johnsmith`, and your package is called
`docassemble-missouri-familylaw`, then the GitHub URL for your private
repository will be:

{% highlight text %}
https://e8cc02bec7061de98ba4851263638d7483f63d41:x-oauth-basic@github.com/johnsmith/docassemble-missouri-familylaw
{% endhighlight %}

You can enter this into the "GitHub URL" field.

## <a name="zip_install"></a>Installing through a .zip file

You can also install [Python] packages from ZIP files.  For example,
if you have a package `docassemble-baseball`, the ZIP file
will be called `docassemble-baseball.zip`.  It will contain
a single directory called `docassemble-baseball`, which in
turn contains `setup.py`, a subdirectory called `docassemble`, and
other files.

1. In the **docassemble** web app, go back to Package Management.
2. Under "Zip File," upload the `.zip` file you want to install.
3. Click "Update."

![Zip Install]({{ site.baseurl }}/img/zip-install.png){: .maybe-full-width }

## <a name="pypi_install"></a>Installing through PyPI

You can also install [Python] packages from [PyPI].  [PyPI] is the
central repository for [Python] software.  Anyone can register on
[PyPI] and upload software to it.  For example, if you want to install
the `docassemble-baseball` package:

1. Make sure the `docassemble-baseball` package does not already exist
   on [PyPI] (note: it doesn't; it is just a fictional package).
2. In the **docassemble** web app, go to Package Management.
3. Type `docassemble.baseball` into the "Package on PyPI"
   field.
4. Click "Update."

![PyPI Install]({{ site.baseurl }}/img/pypi-install.png){: .maybe-full-width }

Once a version of a package is installed on [PyPI], it
exists there permanently.  When you install a version of a package on
[PyPI], the version will automatically increment.

## <a name="package permissions"></a>Permissions on packages

The "Package Management" system remembers which user installed which
package.  Thus, if developer Fred installs a package called
`docassemble.guardianship`, and developer George tries to install a
package called `docassemble.guardianship`, George will get an error.
These permissions do not apply to package dependencies, however.

A user with `admin` privileges can install or uninstall any package.

The purpose of the permission system is to facilitate the use of a
single server by a team of developers by implementing some minor
safeguards that prevent developers from interfering with each others'
work.  It is not the case that each developer works in an insulated
"sandbox."  All interviews on the system run with the same system
[UID] (`www-data`).

# <a name="running"></a>Running interviews from installed packages

Once a **docassemble** extension package is installed, you can start
using its interviews.  For example, if you installed
`docassemble.baseball`, and there was an interview file in that
package called `questions.yml`, you would point your browser to
`http://localhost/interview?i=docassemble.baseball:data/questions/questions.yml`
(substituting the actual domain and base URL of your **docassemble**
site).  Note that a URL like this is different from the URL you see
when you are running an interview in the [Playground] ([see
above](#playground)).

For more information about starting **docassemble** interviews, see
[how you run a **docassemble** interview].

# <a name="updating"></a>Updating Python packages

To upgrade a package that you installed from a [GitHub] URL or from
[PyPI], you can press the "Update" button next to the package name on
the "Package Management" screen.  You will only see these Update buttons
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

Then, go to "Configuration" on the menu and enable the PyPI publishing
feature in **docassemble** [configuration] like so:

{% highlight yaml %}
pypi: True
{% endhighlight %}

After you save the [configuration], go to "Profile" on the menu and
fill in "PyPI Username" and "PyPI Password" with the username and
password you obtained from [PyPI].

Next, go to the ["Packages" folder] of the **docassemble**
[Playground] and open the package you want to publish (e.g.,
`docassemble-baseball`).

Press the ![PyPI]({{ site.baseurl
}}/img/playground-packages-button-pypi.png) button to publish the
package to [PyPI].

If your package already exists on [PyPI], then pressing the Publish
button will increment the version of your package.  This is necessary
because you cannot overwrite files that already exist on [PyPI].

When the publishing is done, you will see an informational message
with the output of the uploading commands.  Check this message to see
if there are any errors.

If the publishing was successful, then at the bottom of the page
describing your package, you should see a message that the package now
exists on [PyPI].

![PyPI Published]({{ site.baseurl }}/img/playground-packages-pypi-published.png){: .maybe-full-width }

You can click on the link to see what the package looks like on [PyPI].

![PyPi Page]({{ site.baseurl }}/img/playground-packages-on-pypi.png){: .maybe-full-width }

Now, on the **docassemble** menu (of this server or another server),
you can go to Package Management and
[install the package](#pypi_install) by typing in
"docassemble.baseball" into the "Package on PyPI" field.

![PyPi Install]({{ site.baseurl }}/img/pypi-install.png){: .maybe-full-width }

## <a name="github"></a>Publishing on GitHub

You can publish your package on [GitHub] in addition to (or instead
of) publishing it on [PyPI].  (Publishing on both sites is
recommended.  [PyPI] is the simplest and safest way to distribute
[Python] packages, while [GitHub] is a version control system with
many features for facilitating sharing and collaboration.)

To configure integration with [GitHub], follow the steps in the
[setting up GitHub integration] section, and edit the
[GitHub section of the configuration].

When that configuration is done, each user who is a developer will
need to connect their [GitHub] accounts with their accounts on your
**docassemble** server.  From the menu, the user should go to
"Profile," click "GitHub integration," and follow the instructions.
If the user is not currently logged in to [GitHub] in the same
browser, [GitHub] will ask for log in information.  (Users without
[GitHub] accounts can [create one].)  Users will need to give consent
to giving the **docassemble** server to have privileges of making
changes to repositories and SSH keys within the [GitHub] account.

(Note: it is not possible to connect more than one **docassemble**
account on a single **docassemble** server with the same [GitHub]
account.  However, it is possible to connect accounts on multiple
servers with the same [GitHub] account, so long as the [`appname`] on
each **docassemble** server is different.)

To publish a package on [GitHub], go to the [Packages area] of the
[Playground] and press the ![GitHub]({{ site.baseurl
}}/img/playground-packages-button-github.png) button.  You will be asked
for a "commit message."  This is a brief, one-line message that
describes the changes made to your package since the last time you
"committed" changes.  Each "commit" is like a snapshot, and the history
of "commit" messages is a record of the development of your project.

![Commit]({{ site.baseurl }}/img/playground-packages-github-commit.png){: .maybe-full-width }

When you press the "Commit" button after writing the commit message,
your package will be "pushed" to a [GitHub] repository in your
account.  If a repository does not already exist on [GitHub] with the
name of your package, a new repository will be created.

![GitHub published]({{ site.baseurl }}/img/playground-packages-github-published.png){: .maybe-full-width }

You can follow the hyperlink to your package's page on [GitHub].

![GitHub repository]({{ site.baseurl }}/img/playground-packages-github-repository.png){: .maybe-full-width }

After your first commit, [GitHub] reports that there have been two
commits; this is because the initial creation of the repository caused
a commit (containing a `LICENSE` file only) and then the addition of
the files of your package caused a second commit.

Once your package is on [GitHub], then on the **docassemble** menu,
you can go to Package Management and [install the package](#github_install) using its [GitHub] URL.

![GitHub Install]({{ site.baseurl }}/img/github-install.png){: .maybe-full-width }

# <a name="bestpractices"></a>Best practices for packaging your interviews

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

# <a name="autoloading"></a>How **docassemble** loads modules

During the **docassemble** web app startup process, the packages in
the `docassemble` namespace are scanned and modules are `import`ed if
they contain any class definitions or if the
`update_language_function()` function is called.  The early loading of
class definitions helps to prevent problems when unpickling data from
the SQL database.  The `update_language_function()` has a global
effect, and it is important that **docassemble**'s linguistic behavior
is uniform over time and does not vary depending on which interviews
the server has used.  This also means that you have to be careful
about which packages you install on your server -- even a package you
never use could have an effect on the way your server operates.

If you want to disable the auto-loading of a module, put this line
near the top of the .py file (before any class definitions or
references to `update_language_function()`):

{% highlight text %}
# do not pre-load
{% endhighlight %}

If this line is present, then the server will not pre-load the module file.

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
[Python packages]: https://docs.python.org/3/tutorial/modules.html#packages
[Python package]: https://docs.python.org/3/tutorial/modules.html#packages
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
[Python module]: https://docs.python.org/3/tutorial/modules.html
[Python modules]: https://docs.python.org/3/tutorial/modules.html
[classes]: https://docs.python.org/3/tutorial/classes.html
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
["Modules" folder]: {{ site.baseurl }}/docs/playground.html#modules
["Packages" folder]: {{ site.baseurl }}/docs/playground.html#packages
["Templates" folder]: {{ site.baseurl }}/docs/playground.html#templates
["Static" folder]: {{ site.baseurl }}/docs/playground.html#static
[Setting up GitHub integration]: {{ site.baseurl }}/docs/installation.html#github
[GitHub section of the configuration]: {{ site.baseurl }}/docs/config.html#github
[create one]: https://github.com/join
[`appname`]: {{ site.baseurl }}/docs/config.html#appname
[build packages]: {{ site.baseurl }}/docs/playground.html#packages
[subpackage]: https://packaging.python.org/guides/packaging-namespace-packages/
[how you run a **docassemble** interview]: {{ site.baseurl }}/docs/interviews.html#invocation
[packaging your interview]: {{ site.baseurl }}/docs/hello.html#packaging
[hello world]: {{ site.baseurl }}/docs/hello.html
[development workflows]: {{ site.baseurl }}/docs/development.html
[UID]: http://www.linfo.org/uid.html
