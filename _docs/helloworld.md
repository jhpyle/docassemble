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

To try this out yourself, follow these steps.  (This assumes you have
already followed the [installation] instructions.)

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
folder, select "Send To," then select "Compressed (zipped) Folder.")
9. In the **docassemble** web app, go back to Package Management.
10. Click "Update a package."
11. Upload the .zip file you just created.  You should see a message
that the package was installed successfully.
12. Point your browser to
    `http://localhost/demo?i=docassemble.hello_world:data/questions/questions.yml`
    (substituting the actual domain and base URL of your
    **docassemble** site).
	13. You should see "Hello, world!" with an exit button.

Now let's get it to ask a question.  Edit
`docassemble_hello_world/docassemble/hello_world/data/questions.yml`
again and change the contents to:

{% highlight yaml %}
---
question: Hello, ${ planet }!
buttons:
  - Exit: exit
mandatory: true
---
question: What is your planet's name?
fields:
  - Your Planet: planet
---
{% endhighlight %}

Then repeat steps 8 through 12, above.

It should now ask you "What is your planet's name?" and then greet
your world by its name.

[installation]: {{ site.baseurl }}/docs/installation.html
[reconfigured user roles]: {{ site.baseurl }}/docs/users.html
[YAML]: https://en.wikipedia.org/wiki/YAML
[WordPad]: http://windows.microsoft.com/en-us/windows/using-wordpad#1TC=windows-7
[Notepad++]: https://notepad-plus-plus.org/
