---
layout: docs
title: Package Management
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
|-- LICENSE
|-- README.md
`-- setup.py
{% endhighlight %}

When installed on the server, the interview can be run by going to a
link like `https://example.com?i=docassemble.baseball:hitters.yml`.

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
{% endhighlight %}

# Creating your own packages

## On-line

You can create your own **docassemble** package on-line using the
[Packages area] of the [Playground].

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
4. Enter a name for the package, such as `missouri_family_law` and click "Get template."
5. Save the resulting .zip file to your computer.

The full name of your package will be
`docassemble.missouri_family_law`.  You will refer to files in your
package with names like
`docassemble.missouri_family_law:questions.yml`.

There are a lot of subdirectories in the .zip file (this is the nature
of [namespace packages]).  The `data` directory resides at 
`docassemble_missouri_family_law/docassemble/missouri_family_law/data`.

There are reasons for all of these subdirectories.

1. The top-level directory, `docassemble_missouri_family_law`, is
important because when you unpack the .zip file, you want everything
in one directory.
2. Within that, the `docassemble` directory is necessary so that your
package is a subpackage of `docassemble`.
3. Within that, the `missouri_family_law` directory is necessary
because when packages within the `docassemble` [namespace package] are
installed on a system, [Python] needs them to be in separate
directories under `docassemble`.
4. Within `missouri_family_law` you have `objects.py`, which you can
use to write [Python] code.  The `__init.py__` file is necessary for
declaring `missouri_family_law` to be a package.
5. You also have a `data` directory with subdirectories `questions`,
`static`, `sources`, and `templates`.  These are for [interviews],
static files, data files, and [document templates].

## Installing your package

### Installing through GitHub

The best way to install interviews on a server is through [GitHub].
[GitHub] has an excellent command line interface on Linux and also has
a high-quality [Windows application].

1. Set up a git repository in the top level directory
(`docassemble_missouri_family_law`).
2. Push the repository to [GitHub].
3. In the **docassemble** web app, go to Package Management.
4. Click "Update a package."
5. Enter the [GitHub] URL into the Git URL field and click "Update."

The package will be installed and the [WSGI] server will reset upon
the next page load.

### Installing through a .zip file

1. Create a new .zip file containing the `docassemble_missouri_family_law`
folder.  (On Windows, right-click the `docassemble_missouri_family_law`
folder, select "Send To," then select "Compressed (zipped) Folder.")
2. In the **docassemble** web app, go back to Package Management.
3. Click "Update a package."
4. Upload the .zip file you just created.  You should see a message
that the package was installed successfully.

## Testing your new interview

Point your browser to
`http://localhost/demo?i=docassemble.missouri_family_law:data/questions/questions.yml`
(substituting the actual domain and base URL of your **docassemble**
site).  The base url is set during the [installation] of the [WSGI]
server and in the **docassemble** [configuration] file (where it is
called [`root`]).

Note that you can also test interview [YAML] using the **docassemble**
[Playground].

# Python packages installed on the server

If your **docassemble** interviews or code depend on other
[Python packages] being installed, you can install packages from the
**docassemble** front end:

1. Make sure you are logged in as a developer or administrator.
2. Go to "Package Management" on the menu.
3. Go to "Update a package."
4. Indicate the package you want to install, or click 

Packages can be installed in three different ways:

* **GitHub URL**: Enter the URL for the GitHub repository containing the
  Python package you want to install.  The repository must be in a
  format that is compatible with [pip].
* **Zip File**: Provide a Zip file containing your Python package.
  The Zip file must be in a format that is compatible with [pip].
* **Package on [PyPI]**: Provide the name of a package that exists on
  [PyPI].

Packages will be installed using the [pip] package manager.  A log
of the output of [pip] will be shown.

If you are running **docassemble** on Mac and Windows, make sure that
the web server user has a home directory to which [pip] can write.
(See [pip/utils/appdirs.py].)

## <a name="updating"></a>Updating Python packages

To upgrade a package that you installed from a GitHub URL or from
[PyPI], you can click the "Update" button next to the package name on
the "Update a package" screen.  You will only see these Update buttons
if you are an administrator or if you are the person who caused the
packages to be installed.

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

[Packages area]: {{ site.baseurl }}/docs/playground.html#packages
[Playground]: {{ site.baseurl }}/docs/playground.html
[interviews]: {{ site.baseurl }}/docs/interviews.html
[YAML]: https://en.wikipedia.org/wiki/YAML
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
[mandatory]: {{ site.baseurl }}/docs/logic.html#mandatory
[initial]: {{ site.baseurl }}/docs/logic.html#initial
[initial blocks]: {{ site.baseurl }}/docs/logic.html#mandatory
[machine learning]: {{ site.baseurl }}/docs/ml.html
[translations]: {{ site.baseurl }}/docs/config.html#words
[pip/utils/appdirs.py]: https://github.com/pypa/pip/blob/master/pip/utils/appdirs.py
