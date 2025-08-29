---
layout: docs
title: Overview of the development process
short_title: Overview
---

There are a variety of workflows that **docassemble** developers can
use.  Which one is best for you will depend on your circumstances.

# <a name="quickstart"></a>Workflow for a quick start

If you are new to **docassemble**, we recommend that you start by
installing **docassemble** on your personal laptop or desktop using
[Docker].  Then you can access **docassemble** at `http://localhost`.
You can log in using the default username of `admin@example.com` and the
default password of `password`.  After you change your password, you
can use the menu in the upper-right hand corner to navigate to the
User List, where you can click "Edit" next to the `admin@example.com`
user and change its e-mail address to a real e-mail address.  Then you
can use the menu to go to the [Playground], where you can try
modifying the default interview, or go through the steps of the
[tutorial].

Using the [Playground], you can start developing and testing
interviews of your own, with the help of the [documentation] and the
[examples area].

# <a name="speedy"></a>Workflow for speedy development

The [Playground] allows you to edit your interview in the browser and
then immediately test the interview by pressing "Save and Run."

Even when you are in the middle of testing an interview, you can make
changes to the interview source, reload the screen in the tab of your
web browser containing your test interview, and immediately see the
effect of your changes.  (Note, however, that there are some
circumstances when you will need to backtrack or restart your
interview to see changes, for example if you change a [`mandatory`]
block that your interview has already processed.)

If you are using [DOCX templates] and you are making frequent changes
to your DOCX template, you may find it cumbersome to repetitively
save and upload the template.  You can make this process faster by
configuring [Google Drive integration].  That way, you can see all of
the files in your [Playground] in your Google Drive folder on your
hard drive, and can edit them there.  Then, when you are ready to test
your interview, press the "Sync" button to synchronize your
[Playground] with your Google Drive.

You may also wish to use [Google Drive integration] if you have a
favorite text editor that you like to use to edit text files like
[YAML] interview files and [Markdown] templates.

# <a name="upgrading"></a>Workflow for upgrading docassemble

As you continue to use **docassemble**, you will probably want to take
advantage of updates to the software.  To see what version you are
running, go to "Configuration" from the menu.  You can find the
current version of **docassemble** on the [PyPI page] or the
[GitHub page].

Most **docassemble** software upgrades can be accomplished by going to
"Package Management" from the menu and clicking the "Upgrade" button.

However, sometimes new versions of the **docassemble** software
require an update to the whole system.  You will see a notification on
the screen if the underlying system needs an upgrade.  The problem
with doing an update to the underyling system is that if your user
profiles and [Playground] data are stored in the **docassemble**
[Docker] container, then removing and reinstalling the container will
delete all that data.

You can back up your [Playground] data by creating a [package]
containing all of your work product, then downloading that [package]
as a ZIP file.  You can then [stop] and [remove] the [Docker]
container, [pull] the latest version, [run] a new version of
**docassemble**, and upload that ZIP file into the [Playground] on the
new system.  This will restore your [Playground] work product, but it
will not keep your user profiles or any data from interview sessions.

There are other, less cumbersome ways to ensure that your [Playground]
data and other data persist through the process of removing and
reinstalling the [Docker] container:

1. You can sign up with [Amazon Web Services] and create an
   [S3 bucket] to store the contents of your [Playground], so that the
   contents persist "in the cloud" after you remove the
   **docassemble** container.  This requires figuring out how [AWS]
   and its access keys work.  [AWS] is a bit complicated, but this is
   a good learning curve to climb, because [AWS] is used in many
   different contexts.  A big advantage of transitioning to [S3]
   storage is that you can continue to use your personal laptop or
   desktop, but when you want to transition your **docassemble**
   server to the cloud, the process of transitioning will be seamless.
2. Instead of using [S3], you could use [Azure blob storage], another
   cloud storage service.
3. Instead of storing your information in the cloud, you could store
   it in a [Docker volume] on the same computer that runs your
   [Docker] container.  The disadvantage is that the data will be
   located in a [hard-to-find directory] on the computer's hard drive,
   and if you want to move **docassemble** to a different server, you
   will need to manually move this directory.

To transition to using [S3] for persistent storage, you need to create
a [bucket] on [S3], add an [`s3`] directive to your [configuration]
that refers to the [bucket], and then immediately [stop] the container
and [start] it again.  Similarly, to transition to
[Azure blob storage], you need to create a container on the
[Azure Portal], add an [`azure`] directive to your [configuration]
that refers to the container, and then immediately [stop] the
container and [start] it again.

Transitioning to using a [Docker volume] for persistent storage is not
as seamless.  Start by creating a [package] in your [Playground]
containing all of the work you have developed so far.  Then download
this package as a ZIP file.  This will back up your work.  Then you
can stop and remove the container, pull the new **docassemble** image
from [Docker Hub], and run it with the configuration necessary to use
one of the above [data storage] techniques.  Then, log in to the
Playground, go to the [packages folder], and upload the ZIP file.
You will need to recreate your user accounts on the new system.

Once you set up persistent storage, all you need to do to upgrade the
full system is [stop] your [Docker] container, [remove] it, [pull] the
new image from [Docker Hub], and [run] the new image.  Your user
profiles, [Playground] data, and installed packages will automatically
appear in the new container.

# <a name="manualtesting"></a>Workflow for manual testing

Manual testing of interviews should be part of your workflow.
Automated testing is also important -- there is a [separate
section](#testing) on that -- but you need to put yourself in your
user's shoes to see how your interview operates.  People other than
yourself should also try out the interviews, because they will likely
use the system in a different way than you do and thereby uncover
problems that you would not encounter.

If your development server is accessible over the network, you can
involve testers in your interview while it is still in the
[Playground].  Every interview in the [Playground] is accessible at a
hyperlink.  To get this hyperlink, right-click on the "<i
class="fas fa-link" aria-hidden="true"></i> Share" button
in the [Playground], copy the URL to your clipboard, then paste the
URL into an e-mail to your testers.

If your development server is your desktop computer, and you access it
in your browser at `http://localhost`, other users will not be able to
run your interviews by going to `http://localhost`.  However, if you
can figure out your computer name, and if your computer's firewall
does not block access to the HTTP port (port 80), then other people
should be able to access **docassemble** at a URL like
`http://johnsmithcomputer` or `http://johnsmith.mycompany.local`.

If you have testers who do not have access to your local area network,
you should consider putting your development server on a server on the
internet.  If you run **docassemble** on your desktop computer, you
could configure your firewall to direct traffic from an external IP
address to your desktop, but for security reasons this is probably not
a good idea.  It is better to put your **docassemble** server on a
dedicated machine (or virtual machine) that is connected to the
internet.  When you do so, you should enable HTTPS so that passwords
are encrypted.

If you are using a local machine for hosting but using [S3] or [Azure
blob storage] for storage, moving from a local server to a cloud
server is relatively easy because your configuration and data is
already in the cloud.  You just need to [stop] your local [Docker]
container and then start a [Docker] container on the cloud server
using environment variables that point to your persistent storage in
the cloud (e.g., [`S3ENABLE`], [`S3BUCKET`], [`AZUREENABLE`],
[`AZUREACCOUNTNAME`], [`AZURECONTAINER`], etc.).

If you are not using cloud storage or [Docker volume]s, you can move
your server from your local machine to a machine in the cloud using
[Docker] tools.  You will need to [stop] your container, [commit] your
container to an image, [save] the image as a file, move the file to
the new server, [load] the file on the new server to create the image
there, and then [run] the image.

# <a name="production"></a>Production environment workflow

## <a name="dev"></a>Separating production from development

If end users are using your interviews, you will need to make sure
that they are reliable, so that your users do not encounter the types
of problems that tend to appear unexpectedly in a development
environment.

Therefore, it is recommended that you run two servers:

1. a development server; and
2. a production server.

On your development server, you will make sure your interviews run as
intended, and then you will put your interview into a [package] and
save that package somewhere: on [PyPI], on [Github], or in a ZIP file.
You will then install that [package] on the production server by
logging into the production server as an administrator and going to
"Package Management" from the menu.  Your users will access the
interviews at links like
`https://docassemble.example.com/interview?i=docassemble.bankruptcy:data/questions/chapter7.yml`,
where `docassemble.example.com` is the address of your production
server, `docassemble.bankruptcy` is the name of your [package], and
`chapter7.yml` is the main [YAML] file of your interview.

This way, your users will always see a "stable" version of your
software.  When you are actively developing an interview, you never
know when a change that you make might have unanticipated side
effects.

To minimize the risk that your end users will see errors, you should
make sure the development server and the production server are as
similar as possible.  Ideally, they should both be running the same
version of **docassemble**, they should both have the same
[configuration], except for minor differences like server name, and
they should both have the same set of [Python] packages installed,
with the same version numbers for each package.  This protects against
the risk that an interview will fail on your production server when it
works without a problem on your development server.

For example, if you forget to specify a [Python] package as a
dependency in your **docassemble** [extension package], your package
will still work on the development server even though it will fail on
the production server.  Problems could also occur if your interview
depends on a [configuration] setting that exists on your development
server but not on your production server.  There could be other,
hard-to-predict reasons why an interview might work on one server but
not on another.  If you ensure that your development server is
virtually identical to your production server, you will protect
against these types of problems.

It is also important to separate the development server and the
production server because there is a risk that the process of
developing a new interview could interfere with the operation of
existing interviews.  A **docassemble** user who has developer
privileges can run any arbitrary [Python] code on the server, can
install any [Python] package, and can change the contents of many
files on which **docassemble** depends for its stable operation.  A
user who has administrator privileges can edit the [configuration],
and it is possible to edit the [configuration] in such a way that the
system will crash.

Since a development server is often used for experimentation, it can
be difficult to keep its configuration matched with that of the
production server.  It may be easier to use three servers:

1. a development server where you develop interviews using the
   [Playground],
2. a production server; and
3. a testing server which is virtually identical to the production
   server and exists primarily to test the installation of your
   interview [packages] to make sure they work as intended before you
   install them on the production server.

It is a good idea to use the [`metadata`] block or the [README area]
of your package to make a note about where the original development
files are located.  For convenience, you may find yourself using
multiple servers for development and experimentation, and if time
passes, you may forget where the authoritative version of the package
lives.

## <a name="production upgrade"></a>Managing the production upgrade process

Since **docassemble** sessions can be saved and resumed later, it is
possible that a user could start an interview in January, log out, and
then you upgrade the software behind that interview in February, and
then the user logs back in again in March.

This could lead to problems.  Suppose that in the first version of
your interview, you had a variable named `recieved_income`.  But in
the second version of the interview, you changed the name of the
variable to `received_income`.  If the user had already answered the
question that defined `recieved_income`, then when they log in and use
the second version of the interview, they may be asked the same
question again, since `received_income` is not defined in their
interview answers.

Or, if the user started an interview in December, and then resumed it
in January, but in the meantime an applicable law changed, the
interview may have made legal determinations that are now outdated and
need to be reconsidered.

So if you will be upgrading your software as your users are using it,
you will need to be careful about ensuring that your changes are
"backwards-compatible."

There are a variety of techniques that you can use to prevent problems
caused by software updates.

1. You could include a version number in your package.  So if users
   start using the interview
   `docasemble.bankruptcy102:data/questions/controversy.yml`, you can
   upgrade your software by publishing
   `docasemble.bankruptcy103:data/questions/controversy.yml`, and the
   users with existing sessions will continue to use version 102.
2. When you upgrade, you can add a [`mandatory`] code block early on
   in your interview that performs upgrade-related functions, like
   renaming the variable `recieved_income` to `received_income`. (Note
   that each [`mandatory`] code block must have a unique `id`.
   Otherwise inserting a new [`mandatory`] code block could cause
   logic problems for users who have existing sessions.)
3. In every version of your interview, you can include a [`mandatory`]
   code block that sets a variable like `interview_version` to
   whatever the current interview version is.  Then, if the user
   resumes an old session, your code can be aware of the fact that the
   session was started under the old version.

# <a name="collaboration"></a>Workflow for collaboration

## <a name="googledrive"></a>Sharing files with Google Drive

If you are working as part of a team of developers on a single
interview, you can use [Google Drive integration] so that all members
of the team share the same [Playground], even though you log in under
different accounts.  One developer would set up [Google Drive
integration], and then share his or her "docassemble" folder with the
other developers.  The other developers would each create a "shortcut"
from the root of their Google Drive to the shared folder.  They would
then set up [Google Drive integration] and select the shared folder
(the shortcut to it) as the folder to use.

If more than one developer tries to edit the same file at the same
time, there will be problems; one developer's synchronization may
overwrite files another developer was editing.  However, if the
interview is split up into separate files, and each developer works
only on designated files, this should not be a problem.

It is important that developers use different **docassemble** accounts
to log into the [Playground].  If two web browsers use the
[Playground] at the same time, there is a danger that one developer's
changes could be erased by another developer's activity.

## <a name="versioncontrol"></a>Using version control

As you work on interview development, you should use version control
to track your changes.

If you enable the [GitHub integration] feature, you will have a
"GitHub" button on your [packages folder] page.  Every time you want
to take a snapshot of your code, press the "GitHub" button, type a
"commit message" that describes what changed in the latest snapshot,
and then press "Commit."  Your changes will be "committed" to your
package's repository on [GitHub].

You can also bring files from a package's [GitHub] repository into the
[Playground] using the ["Pull" button].

This enables a workflow like the following (assuming you know how to
use [git]):

1. Start a [package] in the [Playground].
2. Push the [package] to [GitHub] using the "GitHub" button in the
   [packages folder].
3. On your computer, [clone] the [GitHub] repository and make changes
   to the package by editing files with a text editor, by copying
   files into the `data` folders, or other means.
4. When you want to use the [Playground] again for testing, [push]
   your changes to [GitHub], and then go into the [packages folder]
   and use the ["Pull" button] to bring the updated package files into
   the [Playground].

This also facilitates collaboration:

1. You could do all your development in the [Playground], while
committing snapshots to [GitHub] as you go.
2. If another person has an idea for a change to your package, he or
she could open a [pull request] on the [GitHub] repository for your
package.
3. If you like the changes that person made, you could [merge] the
pull request on [GitHub], and then to bring the changes into your
[Playground], you could press the ["Pull" button].

## <a name="separatepackages"></a>Using separate packages

Developers can work independently while still working collaboratively.

The open-source software community does this all the time: for
example, one [Python] developer will create a package, and then other
developers will make that package a "dependency" for their own
packages and [`import`] it into their code.  The initial developer can
continue to make improvements to the software package, and the other
developers can take advantage of these changes.  Every time the
developers reinstall their own packages, [Python] downloads and
installs the latest version of the dependencies.  The other developers
can use the first developer's code without needing to copy and paste
it, or even look at it.

This kind of collaboration is possible among **docassemble** interview
developers as well, since interviews can be uploaded as
[Python packages] to [PyPI] and [GitHub].

1. Developer One creates an interview, packages it, and presses the
   "PyPI" button to upload the package to [PyPI] as
   `docassemble.bankruptcy`.
2. Developer Two, using a different **docassemble** server, goes to
   "Package Management" from the menu and installs the
   `docassemble.bankruptcy` package from [PyPI].
4. Developer Two then develops an interview file that makes reference
   to files in the `docassemble.bankruptcy` package.  For example, the
   interview might [`include`] the file
   `docassemble.bankruptcy:data/questions/common_questions.yml`, a
   file that contains some standard [`question`]s that might be asked
   of a debtor.
3. Developer Two then goes to the [packages folder] of the
   [Playground], creates a package called `debtconsult`, and makes
   `docassemble.bankruptcy` a dependency of that package.
4. Developer Two then presses the "PyPI" button to upload the package
   to [PyPI] as `docassemble.debtconsult`.
5. Months later, Developer Three, using yet another **docassemble**
   server, goes to "Package Management" from the menu and installs the
   `docassemble.debtconsult` package from [PyPI].  This will cause the
   latest versions of both `docassemble.bankruptcy` and
   `docassemble.debtconsult` to be installed.

In order to facilitate collaboration, Developer One should prepare
interview files in a "modular" way, putting general purpose [`question`]s
and [`code`] blocks in separate [YAML] files that are [`include`]d in
special-purpose interview files.

# <a name="githubprivate"></a>Using private GitHub repositories

If you want to keep your docassemble extension package in a private
GitHub repository, you can still use the [Playground].

Create the repository on [GitHub], give it a name that follows the
standard naming convention (`docassemble-debtconsult`), and mark it as
private.

Then, on your **docassemble** development server, [set up GitHub
integration]({{ site.baseurl }}/docs/installation.html#github) so that
your [Playground] can access the private repositories that your GitHub
account can access.  Then, using the "Packages" folder, you can create
a package called, e.g., `debtconsult`, and when you save it, you will
see that the Playground recognizes that the package is already
installed on GitHub.  When you use the Commit button, you will commit
to the private repository.

You can also "Pull" your private repository into your Playground.
When you click "Pull," it asks for a GitHub URL.  For public
repositories, this is usually something like
`https://github.com/jsmith/docassemble-debtconsult`, for private
repositories you can use the SSH form of the repository, which is
`git@github.com:jsmith/docassemble-debtconsult.git`.

When it comes time to install your private repository on a production
server, you will not be able to use SSH authentication, so you will
need a GitHub URL that embeds an "OAuth" code.  You can create these
codes on the GitHub web site.  Within your "Settings," go to
"Developer settings" and go to the "Personal access tokens" tab.
Click "Generate new token."  You can set the "Token description" to
whatever you like (e.g. "docassemble").  Check the "repo" checkbox, so
that all of the capabilities under "repo" are selected.  Then click
"Generate token."  Copy the "personal access token" and keep it in a
safe place.  If your token is
`e8cc02bec7061de98ba4851263638d7483f63d41`, your GitHub username is
`jsmith`, and your package is called
`docassemble-debtconsult`, then you can access your private
repository at this URL:

{% highlight text %}
https://e8cc02bec7061de98ba4851263638d7483f63d41:x-oauth-basic@github.com/jsmith/docassemble-debtconsult
{% endhighlight %}

This functions just like a URL to a public repository.  For example, you could do:

{% highlight bash %}
git clone https://e8cc02bec7061de98ba4851263638d7483f63d41:x-oauth-basic@github.com/jsmith/docassemble-debtconsult
{% endhighlight %}

Within **docassemble**, you can go to "Package Management" and enter
this URL into the "GitHub URL".  This will install the package on your
server.  Any time you wanted to update the package, you could visit
the link
`/updatepackage?action=update&package=docassemble.debtconsult` on your
server.

Note that the URL cannot have a trailing slash.

# <a name="cli"></a>Editing package files in a text editor on a local machine

The [Playground] is designed for people who are just getting started
with **docassemble**.  Once you start creating packages, it can be
more useful to work on your interview files on your local machine, so
that you can use all of the features of command-line [git].

If you already have an interview working in the Playground, you can
use the "Packages" folder of the [Playground] to create a package
(e.g., called "custody") and then download it as
`docassemble-custody.zip`.  When you uncompress the ZIP file, you will
have a directory called `docassemble-custody`.  Your YAML files are in
the `docassemble/custody/data/questions` directory.

If your interview is packaged and on [GitHub], you can install [git]
on your personal computer and then run `git clone` to copy the
package.  This has the advantage that `git` will already be configured
inside the directory.

You can also download [a dummy package] to serve as the shell for your
own package.  Make sure to replace the word `dummy` with your own
package name, and make other changes as appropriate, to the following
files and directories:

* README.md
* LICENSE
* setup.py
* docassemble/dummy

Using your personal computer to manage your template files and YAML
files is very convenient.  If you haven't used a text editor before,
try installing [Sublime Text], [Notepad++], or [Visual Studio Code].

To test your interview, you should use the `dainstall` command-line
utility, which is part of the [`docassemblecli`] Python package.
Then, to install your package on a remote server, just run:

{% highlight bash %}
dainstall docassemble-custody
{% endhighlight %}

If you haven't made any changes to module files, you can run it as:

{% highlight bash %}
dainstall --norestart docassemble-custody
{% endhighlight %}

Without a restart, a package will install in about 5.5
seconds. Installing a package without a restart only works if the
server is a single machine rather than a cluster.

By default, when you run `dainstall`, it installs the package on the
server itself, not in the [Playground] on the server.  So in order to
test the interview you would visit, e.g.,
`/start/custody/myinterview/`.

If you want to install the package into the Playground, call
`dainstall` with `--playground`:

{% highlight bash %}
dainstall --norestart --playground docassemble-custody
{% endhighlight %}

The interview files are available almost immediately when installing
into the Playground.

You can also use the `dainstall` with `--watch` to upload files to
your server automatically when any file in a directory changes:

{% highlight bash %}
dainstall --watch --playground docassemble-custody
{% endhighlight %}

The `dainstall --watch` code tries to work as efficiently as
possible. Unless you modify a Python file, it will not restart the
server. When used with `--playground`, it will only upload the file
that you changed. When using `dainstall --watch --playground`, there
is virtually no wait time between saving your changes to a YAML file
and being able to test the changes.

For more information about these commands, consult the README for the
[`docassemblecli`] Python package.

# <a name="core"></a>Workflow for making changes to the core docassemble code

If you want to make changes to the **docassemble** code, clone the
[GitHub repository]:

{% highlight bash %}
git clone {{ site.github.clone_url }}
{% endhighlight %}

The source code of **docassemble** will be in the `docassemble`
directory.

In order to test your changes, it helps to have a convenient workflow
for installing your changed code.  Theoretically, your workflow could
involve running [`docker build`] to build a [Docker] container, but
that would probably be overkill.  Most of the time, you will make
changes to [Python] code, rather than system files.  To test your
code, you will only need to install the [Python] packages and then
restart the three services that use those packages (the web server,
[Celery] server, and web sockets server).

The first complication is that the machine on which it is convenient
for you to edit files may not be the machine where you are running
**docassemble**.  You may wish to edit the files on your laptop, but
you have **docassemble** running in a [Docker] container on your
laptop, or on another machine entirely.

There are a variety of ways to get around this problem.  If your local
machine uses Linux, you can follow the [installation] instructions and
run **docassemble** without [Docker].  Then your source code will be
on the same machine as your server, and you can run `pip` directly on
your source files.

Another alternative is to fork the **docassemble** [GitHub repository]
and use [GitHub] as a means of transmitting all of your code changes
from your local machine to your server.  You can use `git add`, `git
commit`, `git push` on your local machine to publish a change, and
then, on the server, you can use `git clone` to make a copy of your
repository on the remote machine (and use `git pull` to update it).
Then on the server you can run `pip` to install the updated versions
of your packages.

If you are using [Docker] on your local machine, you can use a [Docker
volume] to share your code with your container.  If you cloned the
**docassemble** [GitHub repository], then from the directory in which the
`docassemble` directory is located, launch your [Docker] container by
running something like:

{% highlight bash %}
docker run \
--env WWWUID=`id -u` --env WWWGID=`id -g` \
-v `pwd`/docassemble:/tmp/docassemble \
-d -p 80:80 jhpyle/docassemble
{% endhighlight %}

Then you can [`docker exec`] into the container and run `cd
/tmp/docassemble` to go to the directory in which the docassemble
source code is located.

The second complication is that you need to install the [Python]
packages in the right place, using the right file permissions.  On
your server, your **docassemble** server will be running in a [Python
virtual environment] located in `/usr/share/docassemble/local3.12` (unless
you significantly deviated from the standard installation procedures).
The files in this folder will all be owned by `www-data`.  The [uWSGI]
web server process that runs the **docassemble** code runs as this
user.  The files in the virtual environment are owned by `www-data` so
that you can use the web application to install and upgrade [Python]
packages.  If you change the ownership of any of the files in
`/usr/share/docassemble/local3.12` to `root` or another user, you may get
errors in the web application.  When using `pip` from the command line
to install your own version of the **docassemble** packages, you need
to first become `www-data` by running `su www-data` as root.  Then you
need to tell `pip` that you are using a specific [Python virtual
environment] by running `source
/usr/share/docassemble/local3.12/bin/activate`.  Then, you can run `pip`
to install your altered version of the **docassemble** code.  This
line will install all the packages:

{% highlight bash %}
pip install --no-deps --no-index --force-reinstall --upgrade ./docassemble_base ./docassemble_webapp ./docassemble_demo ./docassemble
{% endhighlight %}

The `--no-deps` and `--no-index` flags speed up the installation
process because they cause `pip` not to go on the internet to update
all the dependency packages.

After you run `pip`, you need to restart the services that use the
[Python] code.  If you are only going to test your code using the web
server, and you aren't going to use background tasks, it is enough to
run `touch /usr/share/docassemble/webapp/docassemble.wsgi` as the
`www-data` user.  This updates the timestamp on the root file of the
web application.  Updating the timestamp causes the web server to
recompile the [Python] code from scratch.  Restarting the [uWSGI]
service also does that, but it is slower.

If you want to ensure that all the code on your server uses the new
versions of the [Python] packages, you can run the following as `root`
(or with `sudo`):

{% highlight bash %}
supervisorctl start reset
{% endhighlight %}

This will do `touch /usr/share/docassemble/webapp/docassemble.wsgi`
and will also restart [Celery] and the web sockets server.

Then you can test your changes.

These are significant barriers to a smooth workflow of testing changes
to **docassemble** code, but with the help of shell scripts, you
should be able to make the process painless.

Here is one set of scripts that could be used.  You can run the script
`compile.sh` as yourself.  It will ask you for the `root` password,
and then it will run the second script, `www-compile.sh`, as
`www-data` after switching into the [Python virtual environment].

Here are the contents of `compile.sh`:

{% highlight bash %}
#! /bin/bash
su -c '/bin/bash --init-file ./www-compile.sh -i' www-data" root
{% endhighlight %}

Here are the contents of `www-compile.sh`:

{% highlight bash %}
#! /bin/bash
source /etc/profile
source /usr/share/docassemble/local3.12/bin/activate
pip install --no-deps --no-index --force-reinstall --upgrade ./docassemble_base ./docassemble_webapp ./docassemble_demo ./docassemble && touch /usr/share/docassemble/webapp/docassemble.wsgi
history -s "source /usr/share/docassemble/local3.12/bin/activate"
history -s "pip install --no-deps --no-index --force-reinstall --upgrade ./docassemble_base ./docassemble_webapp ./docassemble_demo ./docassemble && touch /usr/share/docassemble/webapp/docassemble.wsgi"
{% endhighlight %}

When `compile.sh` runs, it will leave you logged in as `www-data` in
the virtual environment.  It also populates the shell history so that
to run `pip` again and reset the web server, all you need to do is
press "up arrow" followed by "enter."  This is then the process for
re-installing your changes to the **docassemble** [Python] code.

These scripts might not work for you in your specific situation, but
some variation on them may be helpful.

# <a name="quality"></a><a name="testing"></a>Ensuring quality

How can you ensure that a **docassemble** interview is high quality?

A common mindset is that the way you produce a web application is to
hire a developer for a "project."  The developer writes code over a
period of time and then provides a "deliverable" that meets your
specifications.  The developer then goes away and works on other
projects.  After you publish the application on the internet, your
expectation is that it will work perfectly and operate indefinitely.
Over time, it may need to be tweaked because of changing
circumstances, so you may hire someone to make minor changes to the
application.  But otherwise, you consider the application "done" when
the developer delivers it to you.  If quality problems emerge after
the developer has moved on to other things, you are annoyed.  You wish
that you had hired a better developer, or that you had done a better
job communicating your requirements.  You feel like you shouldn't have
to be bothered with bugs; the application should just work, and should
require minimal maintenance.  Maybe after a few years, your annoyance
reaches a point where you take the application down and hire a
different developer to produce a new version of the application.

This mindset can be present even when you are a computer programmer
yourself.  After you have "finished" the application, you want to be
able to move on and do other things.  Making changes to an application
is something you feel like you don't have time to do.  Even if you
budgeted time for "maintenance," because you expected there was a
finite probability that something would need to be fixed, you would
still like to minimize the time you spend fixing bugs.

Another aspect of the common mindset is to think of web applications
as falling under the "information technology" umbrella.  If there are
quality problems, people think it's an "IT issue" that needs to be
delegated to a person with computer skills, even when the quality
issues are actually related to poor communication or poor substantive
design, neither of which are information technology problems.

These ways of thinking are bound to result in low-quality web
applications.

Managers of technology "projects" need to understand that quality
assurance is not simply a technology problem; like all problems, it
involves "[people, process, and technology]."  All three need to be
considered when planning for quality assurance.

Who are the **people** who should ensure that a guided interview is
high-quality?  What skill sets are necessary?  Do interviews need to
be developed by individuals who have subject matter expertise as well
as technical skills?  Or can subject matter experts without technical
skills work together with people who have technical skills?  Should
someone take on a managerial role to coordinate developers and subject
matter experts?  If subject matter experts work on the project, should
their role be to "look things over" and be available for questions,
or should they play an active role in the design?

Which subject matter experts should be involved?  Even if a subject
matter expert knows the subject matter very well, that doesn't mean
they are good at communicating about that subject matter through the
medium of an app.  In litigation, by analogy, lawyer A who has written
briefs for 20 years may understand the law as well as lawyer B who has
tried cases in court for 20 years, but that doesn't mean that lawyer A
is capable of standing up in court and persuading the jury to favor
his or her client.  One lawyer may be very good at litigating contract
disputes, but not good at drafting contracts so that they are concise
and anticipate every possible scenario that may develop.

What **processes** should be used to ensure that an interview is
high-quality?  Should the development work be seen as part of a
time-limited "project," or rather as a long-term commitment to deliver
a "product" or "service" to users?  Should the output of the interview
be reviewed by a human before it is provided to the user?  Should
users have access to customer support while using the interview?
Should someone be staffed with [observing] users as they use the
application in order to figure out why users are getting stuck?  Is
"testing" a process that is started shortly before the interview goes
live, or is "testing" integrated into the development process from the
beginning?  How intensive should the testing be?  Should the testing
process be informal ("try it out, click around, see if it breaks") or
formal ("Try scenario A to completion, then scenario B to
completion")?  Should a process of continuous quality improvement be
followed, in which information is collected from user surveys or
customer service requests and used as the basis for improvements?
Should [metrics] be collected and reviewed?  Should team meetings be
held to brainstorm improvements?  Should testing be conducted every
time a new version is published?  Should this testing process test new
features only, or also test features that used to work without a
problem?  After an interview goes live, should a subject matter expert
review it periodically to make sure the logic is not out of date?
Should the interview be tested in some way every day to make sure the
site hasn't crashed without sending a notification?

Lastly, how can **technology** assist the people who implement these
processes?  It is important to view technology for quality assurance
in this context.  Think about the role of technology _after_ you think
about what people and processes are optimal.

Before thinking about how you wish to provide quality assurance, it
may be helpful to read about various approaches to [software
development] as a whole (such as the difference between [waterfall]
and [Agile] lifecycles, and the [DevOps] methodology) and specifically
about different approaches to [software testing].  The approaches that
have been used in the past are not necessarily "best practices."
However, reading about other people's approaches may help you realize
that your initial ideas about how to handle quality assurance may not
make sense.

In particular, think about breaking out of the project-oriented,
time-limited development paradigm.  Do what is right for your users,
not what other people do.  Don't imitate big corporations;
corporations that charge a lot of money still produce low-quality
products.  When it comes to guided interviews, "building the airplane
while flying it" is not an absurdity; it may even be advisable.  It
may be better to spread development resources out over the course of
your product's lifetime than to invest them all at the beginning and
hope that your "specification" was perfect.  If you develop a minimum
viable product, let users use it, study the pain points, and adapt
your product incrementally to address the actual concerns of actual
users, perhaps your product will be higher quality than anything you
could have pre-envisioned while sitting in meetings talking about what
"requirements" to give to a vendor.  Is it the end of the world if a
user encounters a bug?  Perhaps the user will not mind about the bug
if you communicate with them immediately, demonstrate that you care,
and fix the bug promptly.  In fact, if the user sees that there are
real people behind the application, and that those people truly
respect the users, their opinion of your application may increase
after they encounter a bug.

Think of every event in the software lifecycle as good, important, and
worthy of allocation of resources.  Did you discover a flaw in your
software after it went live?  Good, fix it; now your product is more
robust than it was yesterday.  Did your code break because a
dependency changed?  Great, make changes to adapt; now your code is
more up-to-date.  If you concentrate all your energy on preventing,
insuring against, or hiding from low-probability events, rather being
resilient when those events happen, your software will stop evolving.
When your software stops evolving, it will start being "legacy."

You might think, "I don't have the resources to pay developers to
continually improve a product."  First, maybe the resources necessary
are not as expensive as you think.  Maybe how you are managing the
development of the software is the problem, not the money you are
spending.  For example, maybe instead of spending hundreds of hours of
staff time developing a custom color scheme, you could allocate those
hours toward something that matters more, like developing a continuous
quality improvement process that ensures the application does what it
is supposed to do.  Second, maybe you do have the necessary resources,
but you are not allocating them to software development because you
have a preconceived notion of how you should be allocating those
resources.  Are you actually thinking about return on investment, or
do you just assume that software development is only worth a small
amount of money?  Third, if you truly lack the resources to produce a
quality software application, that's fine; in that case, instead of
putting a low-quality product on-line, maybe you should allocate
resources to something more worthwhile.

People who are involved in the development of a web application but
lack technology skills often feel a lack of agency over the way the
application operates.  Sometimes this is because the engineers do not
allow them to have such agency.  Other times, the non-technical people
do have agency, but do not exercise it because of "learned
helplessness"; they know that problem-solving is difficult, and they
can avoid it by telling themselves that the task of problem-solving is
someone else's responsibility, namely, the "IT people."

How should subject matter experts be involved, and what can be
expected of them?

There are different levels of subject matter expert engagement in a
guided interview project.  Many experts may view working on a guided
interview project as an "extra credit" responsibility, which they can
take on when they already have a day job without decreasing their
existing work load.  They may see their role as reviewing the work of
others, spotting substantive mistakes, and suggesting improvements.

At the other end of the spectrum, the subject matter expert could see
their role as that of a tech startup founder, who wants to build a
great guided interview that thoroughly implements their subject matter
expertise.  They see their role as ensuring excellence, and will give
the development process their full attention.

Since an expertise automation "industry" does not really exist yet,
there is no clearly defined role for the expert.  How much should the
expert be expected to understand the technology?  How much should the
technologists be expected to understand the subject matter?

For purposes of comparison, consider the film industry.  Is the role
of the subject matter expert like that of the screenwriter, who has a
clear vision for the end result and does much of the creative work?
Or is it like that of a film critic, who critiques the film
after-the-fact and suggests ways that it could have been better?

Or consider the construction industry.  Is the role of the subject
matter expert like that of the architect, who creates the blueprints,
or like that of a municipal agency that approves building permits?

Because there is no existing expertise automation "industry," there
are no existing expectations of what roles are necessary to create a
high-quality guided interview.  In the film industry, there are
producers, screenwriters, directors, cinematographers, lighting
directors, and more, who are acknowledged to be practitioners of a
craft.  In the construction industry, there is an understanding that
architects, structural engineers, and builders work together to get
buildings constructed and make sure they don't fall down.  Each of
these roles is acknowledged to be a special skill, the development of
which depends on talent, education, and experience.

In the guided interview industry, by contrast, there is a popular
belief that expertise automation is inherently "easy," and that a
subject matter expert from any background just needs to sit down in
front of a computer, use some user-friendly software, and produce a
high-quality app by themselves in a short period of time.  Others
assume that guided interviews are an "IT thing," and some "smart
techie" can do all the work if there is a subject matter expert who
makes themselves available to answer questions.  Others assume that a
guided interview project simply needs a project manager who
communicates specifications to contracted developers who work offsite.

Whether expertise automation is inherently "easy" depends on the
complexity of the expertise automation process being attempted.  At
one end of the spectrum there are "form-filling" projects that simply
involve asking a question for each field in a PDF form, with a little
bit of logic, and delivering a PDF form.  At the other end of the
spectrum there are guided interviews that ask the same question
multiple times from different angles, reconcile API-gathered
information with user-gathered information, allow the user to
spot-edit information while ensuring logical correctness, allow
administrators to have special back-door access to investigate and
resolve problems, and contain safeguards to allow incorrect
information to be identified and corrected.  Whether the development
of complex guided interview systems can be made "easy" with technology
is doubtful.  When it is difficult to even figure out what you want
the system to do, the computer is not going to be able to read your
mind.

While a typical subject-matter expert may be able to figure out how to
use TypeForm and WebMerge, they may not be able to envision the most
elegant data structure for collecting nested information, or envision
what to do in every circumstance where a call to an API might fail.
Nor may they know the right way to communicate effectively with a user
through the medium of a guided interview.

Is "guided interview developer" a profession?  The problem with
professions is that it is very difficult to determine in advance
whether a professional would add value over what you could do yourself
with the right tools, or just extract a fee.  However, just because
you can go to Ikea and get a nice piece of furniture that you can
assemble yourself with a screwdriver does not mean that there is never
a good reason to hire an experienced cabinet maker.  If you have a
firm belief that building beautiful, functional, and durable custom
furniture should be as easy and quick as assembling Ikea furniture,
and you think tech companies just need to hurry up and build DIY tools
for this, you're probably going to be waiting a long time.  Although
the profession of "guided interview developer" does not really exist
yet, it is likely that over time, it will be acknowledged to be a
skilled profession that is necessary in situations of greater
complexity.

If the complexity of a project exceeds what is possible for a subject
matter expert to accomplish with DIY tools, who should be part of the
team?  Some assume that a "guided interview developer" is synonymous
with "someone good with computers."  However, IT professionals who
understand network administration may not have sufficient facility
with algorithms, data structures, and debugging to implement complex
guided interview processes.  Someone who has too much expertise in
certain areas of software development may not not be ideal for the
"guided interview developer" role.  As the saying goes, "if the only
tool you have is a hammer, everything looks like a nail."  Front-end
developers tend to want to write complicated CSS and JavaScript.
Developers with experience on other platforms will tend to spend time
thinking about integrating the guided interview platform with their
favorite platform, rather than working within the guided interview
platform they are using.

A good developer does not just deliver the deliverable, but will
figure out a way to do so in the simplest way possible.  Simplicity
means maintainability; it means that the code base will not need to be
scrapped just because the person who created it gets a job elsewhere.
If the project is implemented in the simplest way possible, another
developer will be able to step in and build on the work of the prior
developer.  However, if that prior work is inscrutable, the new
developer will have no choice but to redo it.

Maintaining simplicity sometimes means pushing back against feature
requests.  Even if the developer could implement a feature, if there
is a high maintainability cost to adding the feature (a cost which is
usually invisible to everyone except the developer), it may make sense
to modify the feature or not implement it at all.  In many cases, if
the feature that someone wants cannot be implemented without harming
maintainability, it might be a bad feature anyway.  When a feature
cannot be implemented elegantly, this is often because it diverges
from standards.  Features that adhere to standards tend to be easier
to implement and often result in a better product for the end user
because they are similar to features the user has seen in other
products.  Often, the only person who knows enough to advocate for
standards is the developer who is asked to implement a feature, since
the non-developers who request features may not be aware of what the
standards are.

Other skills sets that are necessary for a guided interview project
include user experience design.  User experience is more than a matter
of [CSS]; it's about making sure the flow through the interview is
intuitive.

A related skill set is plain language communication.  How do you ask a
question in a way that is concise and readable and yet conveys the
correct meaning?

There is no reason to expect that any given subject matter expert or a
software developer will have all of these skills.  Subject matter
experts whose professional life involves communicating with other
experts in the same subject matter typically have a difficult time
writing in plain language.  Maybe subject matter experts and
developers could acquire these skills over time, but if you want your
guided interview to be good, these skills need to be on the team.
Someone needs to be able to look at the product objectively, with
empathy for the wide variety of users who might use the guided
interview, and envision ways that it can be better.  The designer does
not need to be able to write code to indicate how they think an
interview could be re-designed; they could convey it on paper.  The
coder then needs to be able to figure out ways to implement what the
designer suggests without breaking with standards or making the
interview unmaintainable.

All of the people contributing to the project are "guided interview
developers," just like producers, screenwriters, directors,
cinematographers, lighting directors are all "movie developers."  All
the people involved in guided interview developed should think of
themselves as artists producing a masterpiece; none of them should
think that "development" is something someone else is doing; they are
all "developing."

## <a name="bdd"></a>Behavior-driven development

Automated testing of software is useful because when you have a
rapidly changing code base, unexpected changes may occur at any time.
If you can automatically run [acceptance tests] to ensure that the
software behaves the way you and your subject matter experts think it
should behave, you can detect not only obvious bugs and also the
stealthy bugs that most people won't notice or report.

**docassemble** comes with scripts and examples for running automated
acceptance tests using [Behave], which is a Python version of the
[Cucumber] system for [Behavior-Driven Development].

The idea behind "[Behavior-Driven Development]" is for development and
management teams to work together write acceptance tests in a
human-readable domain-specific language that can also be interpreted
by the computer in order to test the software.  In [Cucumber] and
[Behave], this human-readable language is a plain text file written
in the [Gherkin] format.  **docassemble** allows interview developers
to write [Gherkin] scripts that look like this:

{% highlight text %}
Scenario: Test the interview "Annual income calculator"
  Given I start the interview "docassemble.demo:data/questions/income.yml"
  Then I should see the phrase "What is your income?"
  And I set "Income" to "400"
  And I select "Twice Per Month" as the "Period"
  And I click the button "Continue"
  Then I should see the phrase "You earn $9,600 per year."
{% endhighlight %}

These scripts test the interviews by automating Chrome or Firefox.
The software converts human-readable commands into keystrokes and
pointer clicks, and reads the screen to verify that the correct
language appears.  This ensures that testing is thorough because it
tests the software from the user's perspective.  Everything the
technology does, from the JavaScript running in the user's browser to
the background processes running on **docassemble**, is tested.  More
information about deploying [Behave] is available [below](#behave).

Technology for web browser automation exists that allows you to
"record" keystrokes and button clicks and then "play" it back at a
later time.  By comparison, it may seem time time consuming to write
out English language sentences.  However, the advantage is that
English language sentences are human-readable.  The [Gherkin] scripts
themselves can be reviewed by a subject matter expert for validity,
and can easily be edited when the underlying interview changes.

Acceptance testing using the [Behavior-Driven Development] model
requires management and development teams to envision different
scenarios and precisely specify the expected outputs that result from
particular inputs.  As the interview changes, the [Gherkin] scripts
will need to be changed in parallel.  This is a significant commitment
of time.  However, the strictness of the testing scripts helps to
uncover unexpected bugs.  When an interview passes a test at one time
and then fails it later due to a subtle change, that subtlety can be
the tip of the iceberg of a more systemic problem.

The downside of the [Behavior-Driven Development] model is that it is
not feasible to envision and test every possible scenario.  For
example, if an interview has five multiple-choice questions with five
choices each, that means there are 3,125 possible scenarios.  It would
be too much work to envision and separately test that many scenarios.
While there may be a latent bug lurking in one of those 3,125
combinations of answers, in practice, [Behavior-Driven Development]
teams will only have the resources to conduct acceptance testing on a
handful of those scenarios.  If these scenarios are diverse, they will
catch a lot of bugs, but they won't catch all the bugs.

## <a name="random"></a>Random-input testing

Another way to test interviews is use **docassemble**'s [API], which
allows an interview session to be driven with a computer program.
Using the [API], an interview can be repeatedly tested with random
multiple-choice selections and random input values.  If a random
combination of inputs results in an error screen, the test fails, and
the developer will know that there is a bug in the interview.

An example of such a script is the [`random-test.py`] file in the
[`docassemble.demo`] package.  This is a general-purpose script for
testing any interview, but you will likely need to tweak it to work
appropriately with any of your own interviews.  For example, it does
not adapt to questions that use the [`show if`] feature to conceal
fields.

Repeatedly testing a web application with random data can uncover bugs
that result in the user seeing an error message, but it cannot
identify substantive errors, such as situations where the user is
asked an inappropriate question or given inappropriate information.

## <a name="prepoplate"></a>Input-output testing

Another approach for testing a **docassemble** interview without using
[Behavior-Driven Development] is to manually populate a full set of
interview answers and then inspect the "output" of the interview to
ensure it correctly corresponds to the input.  This procedure bypasses
the information-gathering process of the interview and tests only the
end-result logic.

One way to do this is to add blocks to your interview like:

{% highlight yaml %}
mandatory: True
code: |
  if user_has_privilege(['developer', 'admin']):
    if scenario_to_test != 'skip':
      value(scenario_to_test)
---
question: |
  Which scenario do you want to test?
field: scenario_to_test
choices:
  - Scenario One: scenario_one_defined
  - Scenario Two: scenario_two_defined
  - No Scenario: skip
---
code: |
  # Make sure necessary objects are defined
  # early on so that this block can run idempotently.
  client.name
  client.asset
  client.name.first = 'Joseph'
  client.name.last = 'Jones'
  client.birthdate = as_datetime('5/1/1995')
  car = client.asset.appendObject()
  car.value = 323
  car.purchase_date = as_datetime('5/1/2015')
  # etc. etc.
  scenario_one_defined = True
{% endhighlight %}

If the user is not a developer or an administrator, the `mandatory`
runs to completion and is never run again.  But if the user is a
developer or administrator, the interview will start with a screen
that the user can use to select a scenario.  The `mandatory` block
uses the [`value()`] function to seek a definition of
`scenario_one_defined` or `scenario_two_defined`.  Once the scenario
is defined, the `mandatory` block runs to completion and the interview
proceeds normally.  The next screen that is shown is whatever screen
would be shown to a user who had input the information listed in the
scenario.

You can use this technique to "fast forward" to a part of the
interview you want to test, or to "fast forward" to the very end.

You could use "sub-scenarios" so that you can mix-and-match different
collections of variables.  For example, your `scenario_one_defined`
block could seek the definition of `scenario_user_self_employed` and
`scenario_high_tax_bracket`, while your `scenario_two_defined` block
could seek the definition of `scenario_user_has_employer` and
`scenario_high_tax_bracket`.  This will allow you to avoid having to
copy and paste code.

You could then have a [Behave] script that starts with:

{% highlight text %}
Scenario: Test the interview "Debt collection advice"
  Given I log in with "jsmith@example.com" and "sUper@sEcr3t_pAssWd"
  And I start the interview "docassemble.massachusetts:data/questions/debt.yml"
  Then I should see the phrase "Which scenario do you want to test?"
  And I click the "Scenario One" option
  And I click the button "Continue"
{% endhighlight %}

These few lines effectively "stand in" for many lines of [Gherkin]
sentences you would otherwise have to write to simulate the user typing in
information.  A [Behave] script like this is easier to maintain than
one that you have to modify every time you make a change to the
language or order of your information-gathering screens.

Another way to prepopulate interview answers is to use the [API].
However, the downside of using the [API] to set variables is that the
[API]'s variable-setting endpoint is not capable of creating objects.

Since there can be bugs in the logic of the information-gathering
process, this procedure is not as thorough as a [Behavior-Driven
Development] approach that goes through all of the
information-gathering screens.

## <a name="unittesting"></a>Unit testing

**docassemble** also supports the technique of testing components of
an interview in isolation ("[unit testing]").  Unit testing is
feasible when the legal logic of an interview is written in the form
of [Python] classes, methods, and functions.  For example, the
interview might have an algorithm that determines jurisdiction:

{% highlight python %}
class Plaintiff(Individual):
    def jurisdiction_state(self, cause_of_action):
        if self.lived_in_current_state_for_two_years():
            return self.address.state
        return cause_of_action.state_arose_in
{% endhighlight %}

This method could be tested on a variety of inputs to ensure that the
legally correct answer is given:

{% highlight python %}
import unittest
from docassemble.base.util import as_datetime
from .massachusetts_law import Plaintiff, CauseOfAction

class TestJurisdiction(unittest.TestCase):

    def test_moved_recently(self):
        plaintiff = Plaintiff()
        plaintiff.address.state = 'MA'
        plaintiff.address.move_in_date = as_datetime('1/5/2017')
        plaintiff.prior_address.appendObject(state='NH', move_in_date='9/2/2015')
        cause_of_action = CauseOfAction(state_arose_in='NH')
        self.assertEqual('NH', plaintiff.jurisdiction_state(cause_of_action))

    def test_did_not_move_recently(self):
        plaintiff = Plaintiff()
        plaintiff.address.state = 'MA'
        plaintiff.address.move_in_date = as_datetime('10/5/2005')
        cause_of_action = CauseOfAction(state_arose_in='NH')
        self.assertEqual('MA', plaintiff.jurisdiction_state(cause_of_action))

if __name__ == '__main__':
    unittest.main()
{% endhighlight %}

This module uses the [`unittest` framework].  A module using the
[`unittest` framework] can be called from an interview using the
[`run_python_module()`] function.

It may seem like a waste of time to write a computer program to test
two scenarios when it would be much faster to simply test the two
scenarios manually, and if they work right, conclude that the feature
works and will continue to work.  However, writing out the test
scripts is worthwhile because test scripts can then be run in the
future in an automated fashion to prevent "regression."  Very often,
bugs in software come from features that used to work but that stop
working for hard-to-predict reasons.  Something that used to work
might suddenly stop working because of a change in the code of a
dependency, such as a software library written by someone else.  Code
may also stop working because changes you made elsewhere in your
package have unanticipated long-distance effects.

When using `unittest`, note that many of the functions and classes in
`docassemble.base.util` depend on external functionality. As a result,
your tests may raise exceptions. In the **docassemble** web
application, the package `docassemble.webapp` provides the external
functionality that the `docassemble.base.util` functions and objects
require.

To enable this external functionality for your unit tests, you can use
a `TestContext` object from the `docassemble.webapp.server` module:

{% highlight yaml %}
if __name__ == '__main__':
    from docassemble.webapp.server import TestContext
    with TestContext('docassemble.demo'):
        unittest.main()
{% endhighlight %}

You must provide the name of your package as a positional parameter to
`TestContext`. If your code contains any relative file references such
as `mypicture.png`, this package name is used to locate those files.
The context provided by `TestContext()` is one in which a user with
`admin` privileges is logged in, so `user_logged_in()` will return
`True`, and `user_has_privilege('admin')` will return `True`.

If importing `TestContext` is not necessary for your tests to run, it
is best not to import it, because `docassemble.webapp.server` is a
large module that takes a long time to load (twice as long as
`docassemble.base.util`).

Legal logic algorithms can also be "unit tested" using brief test
interviews that are separate from the main interview and exist only
for testing purposes.  These test interviews could be operated by
subject matter experts manually, who could manually try out various
possibilities in to make sure the algorithm produces the legally
correct response.  These same interviews could also be tested in an
automated fashion with [Behave] scripts.  For example, a test
interview, `test-jurisdiction.yml`, might look like this:

{% highlight yaml %}
modules:
  - .massachusetts_law
---
objects:
  - plaintiff: Plaintiff
  - cause_of_action: CauseOfAction
---
mandatory: True
code: |
  plaintiff.prior_address.appendObject()
  plaintiff.prior_address.gathered = True
---
question: |
  Please provide the following information.
fields:
  - Current state: plaintiff.address.state
    code: states_list()
  - Move-in date: plaintiff.address.move_in_date
    datatype: date
  - Prior address state: plaintiff.prior_address[0].state
    code: states_list()
    required: False
  - Prior address move-in date: plaintiff.prior_address[0].move_in_date
    datatype: date
    required: False
  - State in which cause of action arose: cause_of_action.state_arose_in
    code: states_list()
---
mandatory: True
question: |
  The state of jurisdiction is 
  ${ state_name(plaintiff.jurisdiction_state(cause_of_action)) }.
---
{% endhighlight %}

The corresponding [Behave] script would look like this:

{% highlight text %}
Feature: Determination of jurisdiction
  I want to see if the code determines jurisdiction correctly.

  Scenario: Test jurisdiction when the plaintiff has lived in Massachusetts for a long time.
    Given I start the interview "docassemble.massachusetts:data/questions/test-jurisdiction.yml"
    And I select "Massachusetts" as the "Current state"
    And I set "Move-in date" to "1/5/2017"
    And I select "New Hampshire" as the "Prior address state"
    And I set "Prior address move-in date" to "9/2/2015"
    And I select "New Hampshire" as the "State in which cause of action arose"
    And I click the button "Continue"
    Then I should see the phrase "The state of jurisdiction is New Hampshire."

  Scenario: Test jurisdiction when the plaintiff has lived in Massachusetts for a long time.
    Given I start the interview "docassemble.massachusetts:data/questions/test-jurisdiction.yml"
    And I select "Massachusetts" as the "Current address"
    And I set "Move-in date" to "10/5/2005"
    And I select "New Hampshire" as the "State in which cause of action arose"
    And I click the button "Continue"
    Then I should see the phrase "The state of jurisdiction is Massachusetts."
{% endhighlight %}

You could have a number of testing scripts like these, which you could
run to ensure that the legal logic of your interview is proper.
Unlike [Behave] scripts that test your actual interview, these
scripts will not need to be changed whenever you make stylistic
modifications to your interview.  In that way, they are much easier to
maintain.

You might think it is inefficient to write 40 lines of [YAML] and
[Gherkin] to test an algorithm that is five lines long.  But there is
no logical basis for assuming that the the algorithm itself should
take up less space than its testing code.  Nor is there a logical
basis for assuming that the task of writing the algorithm should take
longer than testing the algorithm (or writing documentation for the
algorithm).  All of this work is important.

You do not need to develop a rigid habit of writing test scripts for
every piece of code you write.  If you have a `code` block that
capitalizes a word, for example, it is reasonable to "test" it by
"eyeballing" it or testing it incidentally as part of a
whole-interview [Behave] script.  But if you have mission-critical
algorithms that do somewhat tricky things, spending a lot of time on
test code will yield a good return on investment.

The next section provides a practical explanation of how to use
[Behave] to test **docassemble** interviews.

## <a name="behave"></a>Using Behave

[Behave] is a Python program that runs on your local computer.  It
uses [selenium] to automate the behavior of a web browser such as
Firefox or Chrome.

The way that [Behave] works is beyond the scope of this
documentation.  This section describes only a broad outline of how
[Behave] can be used to test **docassemble** interviews.

Before installing [Behave], install Google Chrome. To install
[Behave], do:

{% highlight bash %}
pip install behave selenium webdriver-manager
{% endhighlight %}

If your docassemble extension package is in the directory
`/home/jsmith/docassemble-lt`, then you would do:

{% highlight bash %}
$ cd /home/jsmith/docassemble-lt/tests
$ behave
{% endhighlight %}

Of course, you first need to create a `tests` directory and create the
appropriate directory structure within it, 

This directory structure needs to be as follows:

{% highlight text %}
docassemble-lt
|-- docassemble
|-- ... various files like README.md ...
`-- tests
    `-- features
        `-- __init__.py
        |-- steps
            `-- __init__.py
            |-- docassemble.py
        |-- environment.py
        `-- MyTest.feature
{% endhighlight %}

The `__init__.py` files are empty placeholder files.  The file
`MyTest.feature` can be called anything, and you can have more than
one `.feature` file.  When you run `behave`, all of the feature files
will be used.

The `environment.py` and `docassemble.py` files are the [Python] modules
that perform the web browser automation.  Versions of these files are
available in the **docassemble** [GitHub repository], but you may need
to edit these modules to get your tests to work.

A starting point for the `environment.py` module is available here:

* [`environment.py`](https://github.com/jhpyle/docassemble/blob/master/tests/features/environment.py)

A starting point for the `docassemble.py` module is available here:

* [`docassemble.py`](https://github.com/jhpyle/docassemble/blob/master/tests/features/steps/docassemble.py)
  
The test file itself, which is called `MyTest.feature` above, would
look something like this:

{% highlight text %}
Feature: Interview that works with actions
  In order to ensure my interview is running properly I want to
  see how it reacts to input.

  Scenario: Test the interview "Action with arguments"
    Given I start the interview "docassemble.base:data/questions/examples/actions-parameters.yml"
    And I click the link "Add blue fish"
    When I wait 1 second
    Then I should see the phrase "You have 3 blue fishes"
    And I click the button "Continue"
    Then I should see the phrase "You have 3 blue fishes"
{% endhighlight %}

One useful feature is the "step" invoked by "I wait forever."  If you
run this step, the browser will stay open and you can use it.  This
can be helpful if you want to use [Behave] to bring you to a
particular step in your interview, without you having to re-do all of
the steps by hand.

For more information about how automated testing works, read the
documentation for [Behave].  You may also wish to read about
the [Behavior-Driven Development] concept in general before starting
to use [Behave].

## <a name="nontechnical"></a>Improving quality with non-technical staff

One barrier to involving non-programmers in the development of guided
interviews is that guided interviews are technologically complex.

It is commonly believed that "code" is the barrier that locks out
non-programmers from being involved in the development process, and if
only we had a user friendly UI, non-programmers could develop
applications just as well as programmers.  However, this may not be
the case.  For example, a non-programmer can conceptually understand
what a list is and what a dictionary is, but if you ask a
non-programmer "what's the optimal data structure for gathering
information about witnesses, their current employer, and their past
employers," a non-programmer is going to struggle with that question.
It can even be a difficult question for a programmer.  The barrier for
the non-programmer is not that they don't know whether a semicolon
goes at the end of the line or what brackets to use to specify a
dictionary.  The programmer's advantage in answering the question is
not that they have memorized the syntax of coding.  Experience with
coding leads to a way of thinking; it develops problem-solving skills
in the technical domain.

Therefore, it is unlikely that you will be able to develop a
maintainable, elegant software product without involving a skilled
computer programmer to figure out issues of logic and data structure.
However, there are ways that non-programmers can and should be deeply
involved in the development of guided interviews.

Notice the popularity of the [DevOps] methodology in software
development, which breaks down the silos of "operations" engineers and
"development" engineers.  Your non-technical people who know the
subject matter of your interview may not think of themselves as
"engineers," but they are similar in many ways to the "operations"
side of [DevOps].

You can involve a non-technical person on the team who knows how to
communicate in writing with succinct phrases, who knows when the text
is too short and too long, knows when to hide information behind a
hyperlink, and knows when to include it in the main page.  A
non-technical person may not know how to figure out tricky logic
problems, but they can envision what the end result should be, and
express that to the developers.  When the developers implement it
imperfectly, the non-technical person can see the imperfections and
clean them up.

A non-technical person can be an advocate for the users against the
developers, who may tend to make decisions in a way that makes life
easier for themselves at the expense of the user.  For example, the
non-technical person could say, "we are asking the user if they lived
outside the state in the last five years, but we already asked them
when they moved to their current address, and if they gave a date that
was before five years ago, we don't need to ask them that question."
The developers might say, "well, that would be complicated for us
because of x, y, and z."  And the non-technical person could say,
"That's nice, I am sure you can figure it out."  Then the developers
will begrudgingly figure it out, and the interview will be improved.

When an application is live, non-technical people can provide customer
service to users.  They can learn about users' difficulties,
prioritize the changes that are most important, and communicate
with the developers so that the difficulties are minimized in the
future.

Non-technical people can also get involved in reading and writing
code.  They can express what they want to see in a guided interview by
writing and editing [Gherkin] scripts, which the developers can clean
up for syntax and use as a basis for implementing changes.
Non-technical people can review [Gherkin] scripts to make sure they
make sense from a substantive perspective.  They can edit them to add
additional conditions so that the [Behave] tests are more
comprehensive.

It is possible to structure [YAML] interview files so that they are
readable and editable by non-technical people.  To facilitate this,
developers can:

* Use the [`include`] feature and split up the [YAML] in such a way
  that complicated blocks are isolated in [YAML] files that
  non-technical people never see, while [`question`]s and easy-to-read
  [`code`] blocks are put in files that non-technical people can
  review and edit.
* Keep [`question`]s readable.  While **docassemble** allows [Python],
  [HTML], [CSS], and [JavaScript] to be sprinkled throughout a [YAML]
  file, a better practice is to hide away this complexity in other
  files.  Developers can move [Python] into module files and other
  content into [`template`] blocks.  That way, the [YAML] will
  primarily contain content that non-technical people can read and
  edit.
* Teach non-technical people to edit [YAML] using GitHub.  Since it is
  possible that non-technical people will introduce errors when
  editing the content of [YAML] files, the developers should always
  review the changes and make corrections as necessary.  But by having
  the power to read, search, and edit the YAML, non-technical people
  will be able to have a greater deal of control.  Non-technical
  people should be about to figure out [Markdown] and much of [Mako]
  with enough confidence to draft questions and make edits.
* Insert [`comment`]s into the [YAML] to explain what the different
  blocks do, and arrange the blocks in a relatively sensible order.
  Non-technical people may not be able to learn the system
  sufficiently to write flawless code themselves, but they can at
  least understand the big picture.

If non-technical people are going to be effective members of the team,
they need to adapt as well.  They need to challenge themselves to
learn new things every day.  The process of learning is not difficult
if they are willing to try.  Learning how things works involves typing
unusual words and phrases into Google (and the **docassemble** web
site, and the GitHub web site) and reading what comes up.

Sometimes, the non-technical members of a team are viewed as "subject
matter experts" because they have an expert knowledge of the subject
matter of the guided interview.  These experts can be important
members of a team if they devote significant time to the work.  But if
their involvement in the work is in addition to a full time job, they
will not be very helpful except as consultants to call for answers to
specific questions.  It is better to have a dedicated staff member who
knows a little about the subject matter than to have a distracted
staff member who knows a lot about the subject matter.

[Mako]: https://www.makotemplates.org/
[`comment`]: {{ site.baseurl }}/docs/modifiers.html#comment
[`template`]: {{ site.baseurl }}/docs/initial.html#template
[HTML]: https://en.wikipedia.org/wiki/HTML
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[selenium]: https://selenium-python.readthedocs.io/getting-started.html
[Behavior-Driven Development]: https://en.wikipedia.org/wiki/Behavior-driven_development
[install chromedriver]: https://chromedriver.storage.googleapis.com/index.html?path=2.33/
[Behave]: https://behave.readthedocs.io/en/stable/index.html
[Cucumber]: https://cucumber.io/
[`docker stop`]: https://docs.docker.com/engine/reference/commandline/stop/
[`docker rm`]: https://docs.docker.com/engine/reference/commandline/rm/
[`docker run`]: https://docs.docker.com/engine/reference/commandline/run/
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`code`]: {{ site.baseurl }}/docs/code.html#code
[configuration]: {{ site.baseurl }}/docs/config.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[extension package]: {{ site.baseurl }}/docs/packages.html
[Docker Hub]: https://hub.docker.com/
[documentation]: {{ site.baseurl }}/docs.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[Playground]: {{ site.baseurl }}/docs/playground.html
[examples area]: {{ site.baseurl }}/docs/playground.html#examples
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[Azure blob storage]: {{ site.baseurl }}/docs/docker.html#persistent azure
[S3]: {{ site.baseurl }}/docs/docker.html#persistent s3
[Docker volume]: {{ site.baseurl }}/docs/docker.html#persistent
[YAML]: https://en.wikipedia.org/wiki/YAML
[DOCX templates]: {{ site.baseurl }}/docs/documents.html#docx template file
[Google Drive integration]: {{ site.baseurl }}/docs/playground.html#google drive
[Markdown]: https://daringfireball.net/projects/markdown/
[PyPI page]: https://pypi.python.org/pypi/docassemble.webapp/
[GitHub page]: https://github.com/jhpyle/docassemble/releases
[stop]: https://docs.docker.com/engine/reference/commandline/stop/
[remove]: https://docs.docker.com/engine/reference/commandline/rm/
[pull]: https://docs.docker.com/engine/reference/commandline/pull/
[run]: https://docs.docker.com/engine/reference/commandline/run/
[start]: https://docs.docker.com/engine/reference/commandline/start/
[commit]: https://docs.docker.com/engine/reference/commandline/commit/
[save]: https://docs.docker.com/engine/reference/commandline/save/
[load]: https://docs.docker.com/engine/reference/commandline/load/
[hard-to-find directory]: https://docs.docker.com/engine/reference/commandline/volume_inspect/
[`s3`]: {{ site.baseurl }}/docs/config.html#s3
[`azure`]: {{ site.baseurl }}/docs/config.html#azure
[bucket]: https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[Azure Portal]: https://portal.azure.com/
[`S3ENABLE`]: {{ site.baseurl }}/docs/docker.html#S3ENABLE
[`S3BUCKET`]: {{ site.baseurl }}/docs/docker.html#S3BUCKET
[`AZUREENABLE`]: {{ site.baseurl }}/docs/docker.html#AZUREENABLE
[`AZUREACCOUNTNAME`]: {{ site.baseurl }}/docs/docker.html#AZUREACCOUNTNAME
[`AZURECONTAINER`]: {{ site.baseurl }}/docs/docker.html#AZURECONTAINER
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[README area]: {{ site.baseurl }}/docs/playground.html#README
[package]: {{ site.baseurl }}/docs/packages.html
[packages]: {{ site.baseurl }}/docs/packages.html
[GitHub integration]: {{ site.baseurl }}/docs/packages.html#github
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[Amazon Web Services]: https://aws.amazon.com
[AWS]: https://aws.amazon.com
[S3 bucket]: https://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[packages folder]: {{ site.baseurl }}/docs/playground.html#packages
[PyPI]: https://pypi.python.org/pypi
[GitHub]: https://github.com/
[data storage]: {{ site.baseurl }}/docs/docker.html#data storage
["Pull" button]: {{ site.baseurl }}/docs/playground.html#pull
[clone]: https://git-scm.com/docs/git-clone
[push]: https://git-scm.com/docs/git-push
[git]: https://git-scm.com
[pull request]: https://help.github.com/articles/about-pull-requests/
[merge]: https://help.github.com/articles/merging-a-pull-request/
[`import`]: https://docs.python.org/3/tutorial/modules.html
[Python packages]: https://docs.python.org/3/tutorial/modules.html#packages
[sshfs]: https://en.wikipedia.org/wiki/SSHFS
[installation]: https://docassemble.org/docs/installation.html
[GitHub repository]: {{ site.github.repository_url }}
[`docker build`]: https://docs.docker.com/engine/reference/commandline/build/
[`docker exec`]: https://docs.docker.com/engine/reference/commandline/exec/
[Celery]: https://docs.celeryq.dev/en/stable/
[Python virtual environment]: https://docs.python-guide.org/dev/virtualenvs/
[Gherkin]: https://en.wikipedia.org/wiki/Cucumber_(software)#Gherkin_language
[`docassemble.demo`]: {{ site.github.repository_url }}/tree/master/docassemble_demo
[`random-test.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/random-test.py
[unit testing]: https://en.wikipedia.org/wiki/Unit_testing
[people, process, and technology]: https://www.christopherspenn.com/2018/01/transforming-people-process-and-technology-part-1/
[waterfall]: https://en.wikipedia.org/wiki/Waterfall_model
[Agile]: https://en.wikipedia.org/wiki/Agile_software_development
[software testing]: https://en.wikipedia.org/wiki/Software_testing
[software development]: https://en.wikipedia.org/wiki/Software_development
[`unittest` framework]: https://docs.python.org/3/library/unittest.html
[`run_python_module()`]: {{ site.baseurl }}/docs/functions.html#run_python_module
[`show if`]: {{ site.baseurl }}/docs/fields.html#show if
[API]: {{ site.baseurl }}/docs/api.html
[metrics]: {{ site.baseurl }}/docs/config.html#google analytics
[observing]: {{ site.baseurl }}/docs/livehelp.html#observe
[acceptance tests]: https://en.wikipedia.org/wiki/Acceptance_testing
[`value()`]: {{ site.baseurl }}/docs/functions.html#value
[DevOps]: https://en.wikipedia.org/wiki/DevOps
[uWSGI]: https://uwsgi-docs.readthedocs.io/en/latest/
[a dummy package]: {{ site.baseurl }}/img/docassemble-dummy.zip
[Notepad++]: https://notepad-plus-plus.org/
[Sublime Text]: https://www.sublimetext.com/
[Visual Studio Code]: https://code.visualstudio.com/
[`docassemblecli`]: https://pypi.org/project/docassemblecli/
