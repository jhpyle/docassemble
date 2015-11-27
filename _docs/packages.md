---
layout: docs
title: Package Management
short_title: Packages
---

# How **docassemble** uses packages

**docassemble** interviews exist in a [Python package] and are
installed on a server as part of that [Python package].  The
[Python package] also includes:

* [Python modules], which include any [classes] and other code that you might
write to go along with your interviews;
* Static content (images, downloads) that you want to include with
your interview; and
* Any [document templates] you created.

A package containing **docassemble** code needs to be a subpackage of
the `docassemble` package.  The `docassemble` package itself is just
a shell (a [namespace package]) that contains subpackages.  These
subpackages include **docassemble**'s core components as well as
user-created packages.

# Creating your own packages

To create your own package, start by downloading a **docassemble**
package template from your **docassemble** server.

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
`docassemble.missouri_family_law:data/questions/questions.yml`

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
`static`, and `templates`.  These are for [interviews], static files,
and [document templates].

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
called `root`).

# Best practices for packaging your interviews

It is a good practice to bundle related interviews in a single
package.  Think about making it easy for other people to install your
packages on their system and make use of your [questions] and [code].

[interviews]: {{ site.baseurl }}/docs/interviews.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[Python packages]: https://docs.python.org/2/tutorial/modules.html#packages
[Python package]: https://docs.python.org/2/tutorial/modules.html#packages
[installation]: {{ site.baseurl }}/docs/installation.html
[configuration]: {{ site.baseurl }}/docs/config.html
[user login system]: {{ site.baseurl }}/docs/users.html
[document templates]: {{ site.baseurl }}/docs/documents.html
[questions]: {{ site.baseurl }}/docs/questions.html
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
