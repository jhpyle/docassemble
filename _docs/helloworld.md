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
mandatory: True
---
{% endhighlight %}

To try this out yourself, follow these steps.

1. Log in to your **docassemble** site as an administrator or a
   developer.
2. Go to Package Management.
3. Click "Create a package."
4. Enter `hello_world` as the package name and click "Get template."
5. Save the resulting .zip file to your computer.
6. Unpack the .zip file.
7. Edit the file
   `docassemble_hello_world/docassemble/hello_world/data/questions.yml`
   and replace its contents with the above YAML text.
8. Create a new .zip file containing the `docassemble_hello_world`
folder.
9. Go back to Package Management.
10. Click "Update a package."
11. Upload the .zip file you created.  You should see a message that
the package was installed successfully.
12. Point your browser to
    `http://localhost/demo?i=docassemble.hello_world:data/questions/questions.yml`
    (substituting the actual URL of your **docassemble** site).
