---
layout: policy
title: Business Continuity Policy
short_title: Business Continuity
---

# Business continuity policy

*Note: **docassemble** is licensed under the [MIT License].  This
policy does not modify that license or create any contract.*

**docassemble** is expected to continue to be maintained so long as
there is interest in using it.

## Risks

### Loss of main developer

To date, the vast majority of the work on **docassemble** has been
undertaken by the lead developer, Jonathan Pyle.  If Jonathan Pyle
were to be longer able to maintain **docassemble**, there would be a
risk that **docassemble** would no longer be maintained.

There are reasons to expect that **docassemble** would continue to be
maintained in the absence of the lead developer.  Since the
**docassemble** source code is available in its entirety on GitHub,
anyone in the world could step in and maintain it at any time.  It is
possible that someone would maintain it because:

* Software developers have contributed pull requests in the past.
* Documate and Community.lawyer use it.
* Large law firms and corporations use it.
* The non-profit Merlin Legal Open Source Foundation could receive and
  distribute funds for the continued development of **docassemble**.

### Competitor projects

If another open-source project emerges that users think is better than
**docassemble**, users may drop **docassemble** and go to that
product.  If such a competitor emerges, Jonathan Pyle would seek to
improve the features of **docassemble** to compete with the other
product.

### Loss of a key dependency

**docassemble** has a number of essential dependencies.  If one of the
dependencies was to stop being maintained, or if the license changes
so that new versions cannot be used, this could impact the viability
of the **docassemble** project.

While **docassemble** relies upon many significant dependencies, most
have alternatives.  For example, if PostgreSQL stopped being
maintained, MariaDB could be used.  If Flask stopped being maintained,
Django could be used.

Other packages, like the `pattern` package, are important but would
likely function well for many years without updates.

Most packages that **docassemble** uses are popular, which increase
the likelihood that they will be maintained, or forked for maintenance
purposes.

Because the dependencies are open source, it often takes little work
to fork a project and update its code.  For example, in February 2020,
the `flask-kvsession` package contained some outdated code and the
maintainers of the package had not updated the code.  It took a matter
of minutes for Jonathan Pyle to fork the code on GitHub, make the
necessary changes, and then post the forked version on PyPI so it
could be a dependency for **docassemble**.

One of the key dependencies that is a niche package and that does not
have any known alternatives is `python-docx-template`, which is used
for assembling DOCX files.  If the package were not to be maintained
any longer, this would pose a problem for **docassemble**.  However,
the package is lightweight and to a significant extent is a wrapper
around other, more widely-used packages (`jinja2` and `docx`).  The
project could be forked and maintained.

Another risk is that technologies that today are open could be closed
in the future.  The PDF specificiation, for example, is currently
open, which allows for open-source third party code to do form filling
in PDF files fairly easily.  But new versions of the PDF specification
may use proprietary code that prevents open-source software from
filling PDF fields.

There is a similar danger that a future version of the Microsoft Word
file could be proprietary and not interoperable, unlike the current
DOCX format.  However, Microsoft is currently investing significant
resources in open-source, so these would seem unlikely.

[MIT License]: {{ site.baseurl }}/docs/license.html
