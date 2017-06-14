---
layout: docs
title: Overview of development process
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
changes to the interview source, then refresh the screen in the tab of
your web browser containing your test interview, and you can
immediately see the effect of your changes.  (Note, however, that
there are some circumstances when you will need to backtrack or
restart your interview to see changes, for example if you change a
[`mandatory`] block that your interview has already processed.)

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
advantage of updates to the software.  Most **docassemble** software
upgrades can be accomplished by going to "Package Management" from the
menu, then selecting "Update a package," then clicking the "Update"
button next to the package "docassemble.webapp."

However, sometimes new versions of the **docassemble** software
require an update to the whole system.  You will see a notification on
the screen if the underlying system needs an upgrade.  The problem
with doing an update to the underyling system that if your user
profiles and [Playground] data are stored in the **docassemble**
[Docker] container, then removing and reinstalling the container will
delete all that data.

You can back up your [Playground] data by creating a [package]
containing all of your work product, then downloading that [package]
as a ZIP file.  You can then stop and remove the [Docker] container,
install a new version of **docassemble**, and upload that ZIP file
into the [Playground] on the new system.

There are other, less cumbersome ways to ensure that your [Playground]
data and other data persist through the process of removing and
reinstalling the [Docker] container:

#. You can sign up with [Amazon Web Services] and create an
   [S3 bucket] to store the contents of your [Playground], so that the
   contents persist "in the cloud" after you remove the
   **docassemble** container.  This requires figuring out how [AWS]
   and its access keys work.  [AWS] is a bit complicated, but this is
   a good learning curve to climb, because [AWS] is used in many
   different contexts.  A big advantage of transitioning to [S3]
   storage is that you can continue to use your personal laptop or
   desktop, but when you want to transition your **docassemble**
   server to the cloud, the process of transitioning will be seamless.
#. Instead of using [S3], you could use [Azure blob storage], another
   cloud storage service.
#. Instead of storing your information in the cloud, you could store
   it in a [Docker volume] on the same computer that runs your
   [Docker] container.  The disadvantage is that the data will be
   located in a hard-to-find directory on the computer's hard drive,
   and if you want to move **docassemble** to a different server, you
   will need to figure out how to move this directory.
   
Once you set this up, when it comes time to upgrade, you will be able
to stop your [Docker] container, remove it, pull the new image from
[Docker Hub], and run the new image, and your user profiles,
[Playground] data, and installed packages will automatically appear in
the new container.

To transition to one of these systems, create a [package] in your
[Playground] containing all of the work you have developed so far, and
then download this package as a ZIP file.  This will back up your
work.  Then you can stop and remove the container, pull the new
**docassemble** image from [Docker Hub], and run it with the
configuration necessary to use one of the above [data storage]
techniques.  Then, log in to the Playground, go to the
[packages folder], and upload the ZIP file.

# Workflow for testing

Thorough testing of your interviews should be part of your workflow.
People other than yourself should do testing.

If your development server is accessible over the network, you can
involve testers in your interview while it is still in the
[Playground].  In the [Playground], right-click on the "<i
class="glyphicon glyphicon-link" aria-hidden="true"></i> Share" button
and copy the URL to your clipboard, then paste it into an e-mail to
your testers.

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

# Production environment workflow

When you are ready to make your interviews public, you will need a
**docassemble** server that is connected to the internet.

If end users are using your interviews, you need to make sure that
they are reliable, so that your users do not encounter the random
problems that can occur in a development environment.

Therefore, we recommend running two servers:

1. a development server; and
2. a production server.

On your development server, you will make sure your interviews run as
intended, and then you will put your interview into a [package] and
save that package somewhere: maybe on [PyPI], on [Github], or in a ZIP
file.  You will then install that [package] on the production server
by going to "Package Management" from the menu, then selecting "Update
a package.  Your users will access interviews at links like
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
similar as possible.  They should both be running the same version of
**docassemble**.  They should both have the same [configuration],
except for minor differences like server name.  They should both have
the same [Python] packages installed, with identical version numbers
for each package.

If you are particularly risk-averse, you should have three servers:

1. a development server where you develop interviews using the
[Playground],
2. a production server; and
3. a testing server which is virtually identical to the production
   server and exists primarily to test the installation of your
   interview [packages] to make sure they work as intended before you
   install them on the production server.
   
This arrangement is helpful because it protects against the risk that
an interview will fail on your production server when it works without
a problem on your development server.  For example, if you forget to
specify a [Python] package as a dependency in your **docassemble**
[extension package], your package will still work on the development
server even though it will fail on the production server.  This could
also happen if your interview depends on a [configuration] setting
that exists on your development server but not on your production
server, There could be other, hard-to-predict reasons why an interview
might work on one server but not on another.  If you ensure that your
testing server is virtually identical to your production server, you
will protect against these types of problems.

It is also important to separate the development server and the
production server because there is a risk that the process of
developing a new interview could interfere with the operation of
existing interviews.  A **docassemble** user who has developer
privileges can run any arbitrary [Python] code on the server, can
install any [Python] package, and can change the contents of many
files on which **docassemble** depends for its stable operation.  A
user who has administrator privileges can edit the [configuration],
and it is possible to edit the [configuration] in such a way that the
system will not start.

# Workflow for collaboration

If you are working as part of a team of developers on a single
interview, you can use [Google Drive integration] so that you all
share the same [Playground], even though you log in under different
accounts.  One developer should set up [Google Drive integration], and
then share the "docassemble" folder with the other developers.  The
other developers would then set up [Google Drive integration] and
select the shared folder as the folder to use.  If more than one
developer tries to edit the same file at the same time, there will be
problems; one developer's synchronization may overwrite files another
developer was editing.

It is important that developers use different accounts to log into the
[Playground].  If two web browsers use the [Playground] at the same
time, there is a danger that one developer's changes could be erased
by another developer's activity.

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
[Google Drive integration]: {{ site.baseurl }}/docs/googledrive.html
[Markdown]: https://daringfireball.net/projects/markdown/
