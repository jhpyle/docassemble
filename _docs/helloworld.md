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
mandatory: true
---
{% endhighlight %}

To run this, first set up your server using [Docker].

Once **docassemble** is up and running in your web browser, click "Log
in" in the upper right hand corner.  The default username and password
are:
 
   * **E-mail**: admin@admin.com
   * **Password**: password

Then, from the menu, select [Playground].

![Playground]({{ site.baseurl }}/img/menu-selection-playground.png)

Then, click the ![Add]({{ site.baseurl }}/img/playground-button-add.png)
button to create a new interview.  Call it "hello.yml."

![New interview]({{ site.baseurl }}/img/playground-new-interview.png)

Then, copy and paste the interview code above into the editor:

![Code copied into interview]({{ site.baseurl }}/img/playground-new-interview-with-code.png)

Then, click the ![Save and Run]({{ site.baseurl }}/img/playground-button-save-and-run.png) button.

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
mandatory: true
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
mandatory: true
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

# Creating a document

Now let's provide the user with a [document] by adding an [`attachment`].

{% highlight yaml %}
---
question: Hello, ${ planet }!
subquestion: |
  I surmise that you have no more than ${ inhabitant_count }
  inhabitants.
attachment:
  - name: A letter for the inhabitants of ${ planet }
    filename: hello
    metadata:
      SingleSpacing: true
    content: |
      Dear ${ planet } residents,

      Hello to all ${ inhabitant_count } of you.

      Goodbye,

      Your friend
buttons:
  - Exit: exit
mandatory: true
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

# Decorate with an image

Now let's decorate one of the questions with an image.

First we need to upload the image we want to use.

From the [Playground], go to the Folders menu and select "Static
files."  (The files are called "static" because they do not change,
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

Now, click ![Back to playground]({{ site.baseurl
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

Under `images`, we indicate that the name we will give our image is
`earth`.

Now, edit the "What is your planet's name?" question and add a
[`decoration`] line:

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

# Packaging your interview

Now, let's bundle the interview into a package so that we can
share it with other developers or post it on [GitHub].

Go to the Folders menu and select "Packages."

![Packages menu item]({{ site.baseurl }}/img/playground-menu-packages.png)

This will take you to the "Packages" folder, where you can create and
edit packages.

![Packages folder]({{ site.baseurl }}/img/playground-folder-packages.png)

If there is an existing package, click the ![Add]({{ site.baseurl
}}/img/playground-button-add.png) button to create a new package.
Otherwise, edit the "New" package.

Call your new package "helloworld."

![Package called helloworld]({{ site.baseurl }}/img/playground-package-example-helloworld.png)

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

Click the ![Download]({{ site.baseurl
}}/img/playground-packages-button-download.png) button to retrieve
your package as a ZIP file called `docassemble-helloworld.zip`.

If you unpack the contents of the ZIP file, you will have a folder
called `docassemble-helloworld`.  You can make changes to the files,
then re-ZIP the `docassemble-helloworld` folder, and install the
revised package on a **docassemble** server using the
[Package Management] tool.

If you want to share your interview on [GitHub], make this folder the
root folder of a new [GitHub] repository.  Then you will be able to go
to [Package Management] on a **docassemble** server and install your
package using the URL to the [GitHub] repository.

For more ideas about how you can extend your interview, check out the
examples area of the [Playground].

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
[`code`]: {{ site.baseurl }}/docs/code.html
[question]: {{ site.baseurl }}/docs/questions.html
[package]: {{ site.baseurl }}/docs/packages.html
[`root`]: {{ site.baseurl }}/docs/config.html#root
[Docker]: {{ site.baseurl }}/docs/docker.html
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
