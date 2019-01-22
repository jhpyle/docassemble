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

# Workflow for upgrading docassemble

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

## Separating production from development

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

## Managing the production upgrade process

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
2. When you upgrade, you can add a [`mandatory`] code block early
   on in your interview that performs upgrade-related functions, like
   renaming the variable `recieved_income` to `received_income`.
3. In every version of your interview, you can include a [`mandatory`]
   code block that sets a variable like `interview_version` to
   whatever the current interview version is.  Then, if the user
   resumes an old session, your code can be aware of the fact that the
   session was started under the old version.


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

Within docassemble, you can go to "Package Management" and enter this
URL into the "GitHub URL".  This will install the package on your
server.  Any time you wanted to update the package, you could visit
the link
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

## Not using Docker

If you are not using [Docker] to run **docassemble**, you can use
[sshfs] to "mount" your [Playground].

{% highlight bash %}
sshfs www-data@localhost:/usr/share/docassemble/files pg
{% endhighlight %}

This way, you can use a text editor to edit your [Playground] files.

## Using Docker

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

## Editing locally and running interviews in the Playground.

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
http://localhost/interview?i=docassemble.playground1:interview.yml&cache=0&reset=1
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
access a file because your text editor has placed a lock on it, you
might see an error.

If you are not using [Docker], but you are using Linux, you can use
sshfs to create a mount in your home directory that maps to the
[Playground].

First, if you don't have an SSH key stored in `~/.ssh/id_rsa` and
`~/.ssh/id_rsa.pub`, generate one:

{% highlight bash %}
ssh-keygen -t rsa
{% endhighlight %}

Then, run the following as root, from your home directory:

{% highlight bash %}
mkdir -p /var/www/.ssh
cat .ssh/id_rsa.pub >> /var/www/.ssh/authorized_keys
chown www-data.www-data /var/www/.ssh/authorized_keys
chmod 700 /var/www/.ssh/authorized_keys
{% endhighlight %}

{% highlight bash %}
mkdir pg
sshfs -o idmap=user www-data@localhost:/usr/share/docassemble/files pg
{% endhighlight %}

# <a name="testing"></a>Workflow for automated testing

## <a name="testing intro"></a>Introduction to testing concepts

How does an interview developer ensure that an interview is high
quality?  Automated testing features can help.

It is important to keep in mind that testing is not simply a
technology problem; like many problems, it involves "[people, process,
and technology]."

Who are the **people** who should ensure that an interview is
high-quality?  What skill sets are necessary?  Do interviews need to
be developed by individuals who have subject matter expertise as well
as technical skills?  Or can subject matter experts without technical
skills work together with people who have technical skills?  Should
someone take on a managerial role to coordinate developers and subject
matter experts?

What **processes** should be used to ensure that an interview is
high-quality?  Is testing something that should started shortly before
the interview goes live, or integrated into the development process
from the beginning?  How intensive should the testing be?  Should the
testing process be informal ("try it out, click around, see if it
breaks") or formal ("Try scenario A to completion, then scenario B to
completion")?  Should a process of continuous quality improvement be
followed, in which information is collected from user surveys or
customer service requests and used as the basis for improvements?
Should the output of the interview be reviewed by a human before it is
provided to the user?  Should testing be conducted every time a new
version is published?  Should this testing target new features only,
or also target features that used to work without a problem?  After an
interview goes live, should a subject matter expert review it
periodically to make sure the logic is not out of date?  Should the
interview be tested in some way every day to make sure the site hasn't
crashed without sending a notification?

Finally, how can **technology** assist the people who implement these
processes?  It is important to view the technology for automated
testing in this context.  Quality cannot be delegated to a computer
program; it is a subjective measure.

When thinking about how to test your interviews, it may be helpful to
read about various approaches to [software testing], as well as
various approaches to [software development] as a whole (such as the
difference between [waterfall] and [Agile] lifecycles).

**docassemble** comes with scripts and examples for running automated
acceptance tests using [Lettuce], which is a Python version of the
[Cucumber] system for [Behavior-Driven Development].  The idea behind
"[Behavior-Driven Development]" is for development and management
teams to work together write acceptance tests in a human-readable
domain-specific language that can also be carried out by the computer
in order to test the software.  In [Cucumber] and [Lettuce], this
human-readable script is a plain text file written in the [Gherkin]
format.  **docassemble** allows interview developers to write
[Gherkin] scripts that look like this:

{% highlight text %}
Scenario: Test the interview "income"
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
the background processes running on **docassemble**, is tested.

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
handful of those scenarios.

Another way to test interviews is use Docassemble's [API], which
allows an interview session to be driven with a computer program.
Using the [API], an interview can be repeatedly tested with random
multiple-choice selections and random input values.  If a random
combination of inputs results in an error screen, the test fails, and
the developer will know that there is a bug in the interview.

An example of such a script is the [`random-test.py`] file in the
[`docassemble.demo`] package.  This is a general-purpose script for
testing any interview, but you will likely need to tweak it to work
appropriately with any of your own interviews.  It does not adapt to
questions that use the [`show if`] feature to conceal fields.

Repeatedly testing a web application with random data can uncover bugs
that result in the user seeing an error message, but it cannot
identify substantive errors, such as situations where the user is
asked an inappropriate question or given inappropriate information.

Another approach for testing a Docassemble interview without using
[Behavior-Driven Development] is to use the [API] to populate a full
set of interview answers and then inspect the "output" of the
interview to ensure it correctly corresponds to the input.  This
procedure bypasses the information-gathering process of the interview
and tests only the end-result logic.  Since there can be bugs in the
logic of the information-gathering process, this procedure is not as
thorough as [Behavior-Driven Development].

Docassemble also supports the technique of testing components of an
interview in isolation ("[unit testing]").  Unit testing is feasible
when the legal logic of an interview is written in the form of
[Python] classes, methods, and functions.  For example, the interview
might have an algorithm that determines jurisdiction:

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
scenarios manually, and if they work right, there is no more that
needs to be done.  However, writing out the test scripts is worthwhile
because test scripts can then be run in the future in an automated
fashion to prevent "regression."  Very often, the bugs in software
come from features that used to work but that stop working for
hard-to-predict reasons.

Legal logic algorithms can also be "unit tested" using brief test
interviews that are separate from the main interview and exist only
for testing purposes.  These test interviews can be operated by
subject matter experts manually, who could manually try out various
possibilities in to make sure the algorithm produces the legally
correct response.  These same interviews can also be tested in an
automated fashion with scenarios specified in [Lettuce] scripts.  For
example, a test interview, `test-jurisdiction.yml`, might look like
this:

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

The corresponding [Lettuce] script would look like this:

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
Unlike [Lettuce] scripts that test your actual interview, these
scripts will not need to be changed whenever you make stylistic
modifications to your interview.

The next section provides a practical explanation about using
[Lettuce] to test **docassemble** interviews.

## <a name="lettuce"></a>Using Lettuce

[Lettuce] is a Python program that runs on your local computer.  It
uses [selenium] to automate the behavior of a web browser such as
Firefox or Chrome.

The way that [Lettuce] works is beyond the scope of this
documentation.  This section describes only a broad outline of how
[Lettuce] can be used to test **docassemble** interviews.

To install [Lettuce], do:

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
can be helpful if you want to use [Lettuce] to bring you to a
particular step in your interview, without you having to re-do all of
the steps by hand.

For more information about how automated testing works, read the
documentation for [Lettuce].  You may also wish to read about
the [Behavior-Driven Development] concept in general before starting
to use [Lettuce].

# Workflow for making changes to the core docassemble code

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
virtual environment] located in `/usr/share/docassemble/local` (unless
you significantly deviated from the standard installation procedures).
The files in this folder will all be owned by `www-data`.  The
[Apache] web server process that runs the **docassemble** code runs as
this user.  The files in the virtual environment are owned by
`www-data` so that you can use the web application to install and
upgrade [Python] packages.  If you change the ownership of any of the
files in `/usr/share/docassemble/local` to `root` or another user, you
may get errors in the web application.  When using `pip` from the
command line to install your own version of the **docassemble**
packages, you need to first become `www-data` by running `su www-data`
as root.  Then you need to tell `pip` that you are using a specific
[Python virtual environment] by running `source
/usr/share/docassemble/local/bin/activate`.  Then, you can run `pip`
to install your altered version of the **docassemble** code.  This
line will install all the packages:

{% highlight bash %}
pip install --no-deps --no-index --upgrade ./docassemble_base ./docassemble_webapp ./docassemble_demo ./docassemble
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
recompile the [Python] code from scratch.  Restarting the [Apache]
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
source /usr/share/docassemble/local/bin/activate
pip install --no-deps --no-index --upgrade ./docassemble_base ./docassemble_webapp ./docassemble_demo ./docassemble && touch /usr/share/docassemble/webapp/docassemble.wsgi
history -s "source /usr/share/docassemble/local/bin/activate"
history -s "pip install --no-deps --no-index --upgrade ./docassemble_base ./docassemble_webapp ./docassemble_demo ./docassemble && touch /usr/share/docassemble/webapp/docassemble.wsgi"
{% endhighlight %}

When `compile.sh` runs, it will leave you logged in as `www-data` in
the virtual environment.  It also populates the shell history so that
to run `pip` again and reset the web server, all you need to do is
press "up arrow" followed by "enter."  This is then the process for
re-installing your changes to the **docassemble** [Python] code.

These scripts might not work for you in your specific situation, but
some variation on them may be helpful.

[selenium]: http://selenium-python.readthedocs.io/getting-started.html
[Behavior-Driven Development]: https://en.wikipedia.org/wiki/Behavior-driven_development
[install chromedriver]: https://chromedriver.storage.googleapis.com/index.html?path=2.33/
[Lettuce]: http://lettuce.it/
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
[documentation]: {{ site.baseurl }}/docs/overview.html
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
[sshfs]: https://en.wikipedia.org/wiki/SSHFS
[installation]: https://docassemble.org/docs/installation.html
[GitHub repository]: {{ site.github.repository_url }}
[`docker build`]: https://docs.docker.com/engine/reference/commandline/build/
[`docker exec`]: https://docs.docker.com/engine/reference/commandline/exec/
[Celery]: http://www.celeryproject.org/
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[Python virtual environment]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[Gherkin]: https://en.wikipedia.org/wiki/Cucumber_(software)#Gherkin_language
[`docassemble.demo`]: {{ site.github.repository_url }}/tree/master/docassemble_demo
[`random-test.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/random-test.py
[unit testing]: https://en.wikipedia.org/wiki/Unit_testing
[people, process, and technology]: https://www.christopherspenn.com/2018/01/transforming-people-process-and-technology-part-1/
[waterfall]: https://en.wikipedia.org/wiki/Waterfall_model
[Agile]: https://en.wikipedia.org/wiki/Agile_software_development
[software testing]: https://en.wikipedia.org/wiki/Software_testing
[software development]: https://en.wikipedia.org/wiki/Software_development
[`unittest` framework]: https://docs.python.org/2/library/unittest.html
[`run_python_module()`]: {{ site.baseurl }}/docs/functions.html#run_python_module
[`show if`]: {{ site.baseurl }}/docs/fields.html#show if
[API]: {{ site.baseurl }}/docs/api.html
