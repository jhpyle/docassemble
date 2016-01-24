---
layout: docs
title: Hello world example
short_title: Hello world
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

To run this on your own **docassemble** server, follow these steps.
(This assumes you have already followed the [installation]
instructions.)

1. Click "Log in" in the upper right hand corner and log in as:
 
   * **E-mail**: admin@admin.com
   * **Password**: password

   Or, if you have already [reconfigured user roles] on your system,
   log in as any user with the privileges of an Administrator or a
   Developer.
2. On the menu in the upper right hand corner, select Package Management.
3. Click "Create a package."
4. Enter `hello_world` as the package name and click "Get template."
5. Save the resulting .zip file to your computer.
6. Unpack the .zip file somewhere.  (On Windows, right-click the .zip
   file and there will be an option to unpack it.)
7. Open your favorite text editor.  (On Windows, use [WordPad] unless
   you have installed a more advanced editor like [Notepad++].)  Open
   the file
   `docassemble_hello_world/docassemble/hello_world/data/questions.yml`
   and replace its contents with the above [YAML] text.
8. Create a new .zip file containing the `docassemble_hello_world`
   folder.  (On Windows, right-click the `docassemble_hello_world`
   folder, select "Send To," then select "Compressed (zipped)
   Folder.")
9. In the **docassemble** web app, go back to Package Management.
10. Click "Update a package."
11. Upload the .zip file you just created.  You should see a message
    that the package was installed successfully.
12. Point your browser to
    `http://localhost/demo?i=docassemble.hello_world:data/questions/questions.yml`
    (substituting the actual domain and base URL of your
    **docassemble** site).  The base url is set during the
    [installation] of the WSGI server and in the **docassemble**
    [configuration] file.
13. You should see "Hello, world!" with an exit button.

(If you do not have a server yet, you can [try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/hello.yml){:target="_blank"}.)

# Adding a question

Now let's change the interview so that it asks the user a [question].  Edit
`docassemble_hello_world/docassemble/hello_world/data/questions.yml`
again and change the contents to:

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

Then repeat steps 8 through 12, above.  (If you do not have your own server yet, you can [try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/hello2.yml){:target="_blank"}.)

It should now ask you "What is your planet's name?" and then greet
your world by its name.

# Adding some Python code

Now let's extend the interview by adding a [code] section that
makes a calculation based on a number provided by the user.

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

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/hello3.yml){:target="_blank"}.)

# Creating a document

Now let's provide the user with a [document] by adding an `attachment`.

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

([Try it out here](https://demo.docassemble.org?i=docassemble.demo:data/questions/hello4.yml){:target="_blank"}.)

This illustrates the complete workflow for producing final
**docassemble** interviews.  If you are trying to work out a problem
with an interview, it may be cumbersome to go through the process of
uploading a new package and then updating the package within
**docassemble**.  To test out interview [YAML] on-the-fly, you can use
the [Playground] area.

[Playground]: {{ site.baseurl }}/docs/playground.html
[installation]: {{ site.baseurl }}/docs/installation.html
[configuration]: {{ site.baseurl }}/docs/config.html
[reconfigured user roles]: {{ site.baseurl }}/docs/users.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[WordPad]: http://windows.microsoft.com/en-us/windows/using-wordpad#1TC=windows-7
[Notepad++]: https://notepad-plus-plus.org/
[document]: {{ site.baseurl }}/docs/documents.html
[code]: {{ site.baseurl }}/docs/code.html
[question]: {{ site.baseurl }}/docs/questions.html
