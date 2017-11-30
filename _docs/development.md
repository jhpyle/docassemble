---
layout: docs
title: Overview of the development process
short_title: Overview
---

There are a variety of workflows that **docassemble** developers can
use.  Which one is best for you will depend on your circumstances.

# Workflow for a quick start

If you are new to **docassemble**, we recommend that you start by
installing **docassemble** on your personal laptop or desktop using
[Docker].  Then you can access **docassemble** at `http://localhost`.
You can log in using the default username of `admin@admin.com` and the
default password of `password`.  After you change your password, you
can use the menu in the upper-right hand corner to navigate to the
[Playground], where you can try modifying the default interview, or go
through the steps of the [tutorial].

Using the [Playground], you can start developing and testing
interviews of your own, with the help of the [documentation] and the
[examples area].

# Workflow for speedy development

The [Playground] allows you to edit your interview in the browser and
then immediately test the interview by pressing "Save and Run."

Even when you are in the middle of testing an interview, you can make
changes to the interview source, reload the screen in the tab of your
web browser containing your test interview, and immediately see the
effect of your changes.  (Note, however, that there are some
circumstances when you will need to backtrack or restart your
interview to see changes, for example if you change a [`mandatory`]
block that your interview has already processed.)

If you are using [.docx templates] and you are making frequent changes
to your .docx template, you may find it cumbersome to repetitively
save and upload the template.  You can make this process faster by
configuring [Google Drive integration].  That way, you can see all of
the files in your [Playground] in your Google Drive folder on your
hard drive, and can edit them there.  Then, when you are ready to test
your interview, press the "Sync" button to synchronize your
[Playground] with your Google Drive.

You may also wish to use [Google Drive integration] if you have a
favorite text editor that you like to use to edit text files like
[YAML] interview files and [Markdown] templates.

# Workflow for upgrading docassemble

As you continue to use **docassemble**, you will probably want to take
advantage of updates to the software.  To see what version you are
running, go to "Configuration" from the menu.  You can find the
current version of **docassemble** on the [PyPI page] or the
[GitHub page].

Most **docassemble** software upgrades can be accomplished by going to
"Package Management" from the menu, selecting "Update a package," and
clicking the "Update" button next to the package called
"docassemble.webapp."

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
new system.

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

# Workflow for testing

Thorough testing of your interviews should be part of your workflow.
You should involve people other than yourself in the testing, because
they will likely use the system in a different way than you do and
thereby uncover problems that you would not encounter.

If your development server is accessible over the network, you can
involve testers in your interview while it is still in the
[Playground].  Every interview in the [Playground] is accessible at a
hyperlink.  To get this hyperlink, right-click on the "<i
class="glyphicon glyphicon-link" aria-hidden="true"></i> Share" button
in the [Playground], copy the URL to your clipboard, then paste the
URL into an e-mail to your testers.

If your development server is your desktop computer, and you access it
in your browser at `http://localhost`, other users will not be able to
run your interviews by going to `http://localhost`.  However, if you
can figure out your computer name, and your computer's firewall does
not block access to the HTTP port (port 80), then you should also be
able to access **docassemble** at a URL like
`http://johnsmithcomputer`, and other users on your local area network
should be able to access the interviews with the same URLs.

If you have testers who do not have access to your local area network,
you should consider putting your development server on a server on the
internet.  If you run **docassemble** on your desktop computer, you
could configure your firewall to direct traffic from an external IP
address to your desktop, but for security reasons this is probably not
a good idea.  It is better to put your **docassemble** server on a
dedicated machine (or virtual machine) that is connected to the
internet.  When you do so, you should enable HTTPS so that passwords
are encrypted.

If you are using [S3] or [Azure blob storage], moving from a local
server to a cloud server is relatively easy because your configuration
and data is already in the cloud.  You just need to [stop] your local
[Docker] container and then start a [Docker] container on the cloud
server using environment variables that point to your persistent
storage in the cloud (e.g., [`S3ENABLE`], [`S3BUCKET`],
[`AZUREENABLE`], [`AZUREACCOUNTNAME`], [`AZURECONTAINER`], etc.).

If you are not using cloud storage or [Docker volume]s, you can move
your server from your local machine to a machine in the cloud using
[Docker] tools.  You will need to [stop] your container, [commit] your
container to an image, [save] the image as a file, move the file to
the new server, [load] the file on the new server to create the image
there, and then [run] the image.

# Production environment workflow

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
logging into the production server as an administrator, going to
"Package Management" from the menu, then selecting "Update a package."
Your users will access the interviews at links like
`https://docassemble.example.com?i=docassemble.bankruptcy:data/questions/chapter7.yml`,
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

# Workflow for collaboration

## Sharing files with Google Drive

If you are working as part of a team of developers on a single
interview, you can use [Google Drive integration] so that all members
of the team share the same [Playground], even though you log in under
different accounts.  One developer would set up
[Google Drive integration], and then share his or her "docassemble"
folder with the other developers.  The other developers would then set
up [Google Drive integration] and select the shared folder as the
folder to use.  If more than one developer tries to edit the same file
at the same time, there will be problems; one developer's
synchronization may overwrite files another developer was editing.
However, if the interview is split up into separate files, and each
developer works only on designated files, this should not be a
problem.

It is important that developers use different **docassemble** accounts
to log into the [Playground].  If two web browsers use the
[Playground] at the same time, there is a danger that one developer's
changes could be erased by another developer's activity.

## Using version control

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

## Using separate packages

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
   "Package Management" from the menu, selects "Update a package," and
   installs the `docassemble.bankruptcy` package from [PyPI].
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
   server, goes to "Package Management" from the menu, selects "Update
   a package," and installs the `docassemble.debtconsult` package from
   [PyPI].  This will cause the latest versions of both
   `docassemble.bankruptcy` and `docassemble.debtconsult` to be
   installed.

In order to facilitate collaboration, Developer One should prepare
interview files in a "modular" way, putting general purpose [`question`]s
and [`code`] blocks in separate [YAML] files that are [`include`]d in
special-purpose interview files.

# <a name="githubprivate"></a>Using private GitHub repositories

If you want to keep your docassemble extension package in a private
GitHub repository, you can still use the [Playground].

Create the repository on [GitHub], and mark it as private.

Then go to your user settings and go to the "Personal access tokens"
tab.  Click "Generate new token."  You can set the "Token description"
to whatever you like (e.g. "docassemble playground access").  Check
the "repo" checkbox, so that all of the capabilities under "repo" are
selected.  Then click "Generate token."  Copy the "personal access
token" and keep it in a safe place.  If your token is
`e8cc02bec7061de98ba4851263638d7483f63d41`, your GitHub username is
`johnsmith`, and your package is called
`docassemble-missouri-familylaw`, then you can access your private
repository at this URL:

{% highlight text %}
https://e8cc02bec7061de98ba4851263638d7483f63d41:x-oauth-basic@github.com/johnsmith/docassemble-missouri-familylaw
{% endhighlight %}

For example, you could do:

{% highlight bash %}
git clone https://e8cc02bec7061de98ba4851263638d7483f63d41:x-oauth-basic@github.com/johnsmith/docassemble-missouri-familylaw
{% endhighlight %}

Within docassemble, you can go to "Package Management" -> "Update a
package" and enter this URL into the "GitHub URL".  This will install
the package on your server.  Any time you wanted to update the
package, you could visit the link
`/updatepackage?action=update&package=docassemble.missouri-family-law`
on your server.

If you want to use that package within your Playground, you could go
to "Playground," open the "Packages" folder, click the "Pull" button,
put the URL into the "GitHub URL" field, and click the "Pull" button.
If you want to do another "pull" from GitHub later, go to
"Playground," open the "Packages" folder, select the package you want
to update, and then click the "Pull" button.  It will default the
"GitHub URL" to the URL of the package.

If you are using the [GitHub integration] feature, you can then
publish changes to the GitHub repository by clicking the "GitHub"
button.

# <a name="localediting"></a>Editing Playground files in a text editor on a local machine

If you are running **docassemble** [Docker] on a local machine, and
you are not using S3 or Azure Blob Storage, you can use
[Docker volume]s to access your [Playground] files using a text editor
running on your local machine.

This requires running [`docker run`], so if you already have a running
**docassemble** [Docker] container, you will have to delete it and
create a new one.

In the following commands, we create a directory called `da`, and then
use [`docker run`] to start **docassemble** in a way that maps the
`da` directory to the container's directory
`/usr/share/docassemble/files`.

{% highlight bash %}
mkdir da
docker run \
--env WWWUID=`id -u` --env WWWGID=`id -g` \
-v `pwd`/da:/usr/share/docassemble/files \
-v dabackup:/usr/share/docassemble/backup \
-d -p 80:80 -p 443:443 jhpyle/docassemble
{% endhighlight %}

The `WWWUID` and `WWWGID` options are important because they ensure
that you will be able to read and write the files in `da`.  This
command also creates a [Docker volume] called `dabackup` so that you
can use [`docker stop`] to stop the container, [`docker rm`] to remove
the container, and then you can re-run the [`docker run`] command
above, and you will not lose your work.

The contents of `da` will include:

* `000` - This is where uploaded files are stored.  You can ignore this.
* `playground` - This is where interview YAML files are.
* `playgroundmodules` - This is where module files are.
* `playgroundpackages` - This is where package information is stored.
  If you use [GitHub integration], the SSH key is stored in here, in 
  hidden files called `.ssh-private` and `.ssh-public`.
* `playgroundsources` - This is where "sources" files are stored.
* `playgroundstatic` - This is where "static" files are stored.
* `playgroundtemplate` - This is where "template" files are stored.

Within each `playground` directory, there are subdirectories with
numbers like `1`.  These refer to user numbers.  Each user has their
own separate folder.  Typically, if you have a server all to yourself,
you will do everything as user `1`.  The directories you will use most
often are `da/playground/1` and `da/playgroundtemplate/1`, for
interview files and templates, respectively.  For convenience, you
might want to create symbolic links from your home directory to these
folders.  If you change the directory structure within `da`, you will
probably cause errors.

To run interviews in your Playground, you can use links like 

{% highlight text %}
http://localhost/?i=docassemble.playground1:interview.yml&cache=0&reset=1
{% endhighlight %}

The `docassemble.playground1` part refers to the Playground of user 1,
which is a "package" that isn't really a package.

The `interview.yml` part refers to the interview file you want to run.

The `cache=0` part means that you are telling **docassemble** to
re-read the interview from the disk.  This is important; normally
**docassemble** caches interviews in its memory.  So if you make
changes to the interview file on disk, you need to tell
**docassemble** that the interview changed.  That is what `cache=0`
does.

The `reset=1` part means that you want to start the interview at the
beginning.  This might not be the case; if you want to try to resume
an interview you had already been running, you can omit `reset=1`.

If you use the [Playground] in the web browser, you can use the "Run"
button in the "Variables, etc." section to launch interviews.  Be
careful about using "Save and Run" because it will save whatever
version is in the text area in the web browser; this may overwrite the
version you had been working with.

Note that editing files in your [Playground] in this way is a "hack"
that bypasses **docassemble**'s front end, so do not be surprised if
you encounter problems.  For example, if the server is unable to
access a file because your text editor has placed a lock on it, don't
be surprised if you see an error.

# <a name="testing"></a>Workflow for automated testing

You can use [lettuce] to test your interviews.  This is a Python
program that runs on your local computer that uses [selenium] to
automate the behavior of a web browser such as Firefox or Chrome.

The way that [lettuce] works is beyond the scope of this
documentation.  This section describes only a broad outline of how
[lettuce] can be used to test **docassemble** interviews.

To install [lettuce], do:

{% highlight bash %}
pip install lettuce selenium
{% endhighlight %}

You will then need a "driver" that will control your web browser.  If
you use Chrome, you need to [install chromedriver] first.  Then you
will need to edit `terrain.py` so that it contains the appropriate
reference to the location where the `chromedriver` file can be found.

If your docassemble extension package is in the directory
`/home/jsmith/docassemble-lt`, then you would do:

{% highlight bash %}
$ cd /home/jsmith/docassemble-lt/tests
$ lettuce
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
        |-- steps
        |   `-- docassemble.py
        |-- terrain.py
        `-- MyTest.feature
{% endhighlight %}

The file `MyTest.feature` can be called anything, and you can have
more than one `.feature` file.  When you run `lettuce`, all of the
feature files will be used.

The `terrain.py` and `docassemble.py` files are the [Python] modules
that perform the web browser automation.  Versions of these files are
available in the **docassemble** [GitHub repository], but you may need
to edit these modules to get your tests to work.

A starting point for the `terrain.py` module is available here:

* [`terrain.py`](https://github.com/jhpyle/docassemble/blob/master/tests/features/terrain.py)

A starting point for the `docassemble.py` module (which is imported
into `terrain.py`) is available here:

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
can be helpful if you want to use [lettuce] to bring you to a
particular step in your interview, without you having to re-do all of
the steps by hand.

For more information about how automated testing works, read the
documentation for [lettuce].  You may also wish to read about
the [Behavior-Driven Development] concept in general before starting
to use [lettuce].

[selenium]: http://selenium-python.readthedocs.io/getting-started.html
[Behavior-Driven Development]: https://en.wikipedia.org/wiki/Behavior-driven_development
[install chromedriver]: https://chromedriver.storage.googleapis.com/index.html?path=2.33/
[lettuce]: http://lettuce.it/
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
[documentation]: {{ site.baseurl }}/docs/authoring.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[Playground]: {{ site.baseurl }}/docs/playground.html
[examples area]: {{ site.baseurl }}/docs/playground.html#examples
[tutorial]: {{ site.baseurl }}/docs/helloworld.html
[Azure blob storage]: {{ site.baseurl }}/docs/docker.html#persistent azure
[S3]: {{ site.baseurl }}/docs/docker.html#persistent s3
[Docker volume]: {{ site.baseurl }}/docs/docker.html#persistent
[YAML]: https://en.wikipedia.org/wiki/YAML
[.docx templates]: {{ site.baseurl }}/docs/documents.html#docx template file
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
[bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
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
[S3 bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
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
[`import`]: https://docs.python.org/2/tutorial/modules.html
[Python packages]: https://docs.python.org/2/tutorial/modules.html#packages
[GitHub repository]: {{ site.github.repository_url }}
