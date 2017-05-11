---
layout: page
title: Download docassemble
short_title: Download
---

If you want to run **docassemble**, you should download and run it
[using Docker].

If you are interested in looking at the source code of
**docassemble**, you can clone the [GitHub repository]:

{% highlight bash %}
git clone {{ site.github.clone_url }}
{% endhighlight %}

You can also download the repository as a [tarball] or a [ZIP file].

The [Python] packages of **docassemble** are also available on [PyPI]:

{% highlight bash %}
pip install docassemble.webapp
{% endhighlight %}

The **docassemble** web application requires more than just its
[Python] packages to run.  (This is why [using Docker] is
recommended.)  For details of how **docassemble** works, see the
[installation] section.

[using Docker]: {{ site.baseurl }}/docs/docker.html
[installation]: {{ site.baseurl }}/docs/installation.html
[tarball]: https://github.com/jhpyle/docassemble/archive/master.tar.gz
[ZIP file]: https://github.com/jhpyle/docassemble/archive/master.zip
[GitHub repository]: {{ site.github.repository_url }}
[Python]: https://www.python.org/
