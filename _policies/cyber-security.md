---
layout: policy
title: Cybersecurity
short_title: Cybersecurity
---

Since **docassemble** is in no way a "software as a service" product,
cybersecurity is largely the responsibility of the implementer.
However, there are cybersecurity risks to **docassemble** as an
open-source project.

### Risk of accidental inclusion of faulty code

There is a risk that a new version of **docassemble** could introduce
a defect that could compromise security and reliability.  The software
is provided with an "as is" license; no warranty is made that the
software is free of defects.

The following techniques are used to to mitigate this risk:

* The entire source code is available to the public for inspection.
* `git diff` is used to carefully inspect all changes made to the
  code.  Individual commits can be inspected on GitHub.
* Whenever possible, popular libraries are used rather than homegrown
  code.  The skeleton of the web app is based on Flask and widely used
  Flask plugins.  Bootstrap is used for the user interface.  While
  **docassemble** itself may not be widely tested, these libraries are
  much more widely used, and defects are thus more likely to surface.
* Before a new version is pushed, a comprehensive suite of `aloe` tests
  is performed to ensure that the software works as expected.


### Open-source infrastructure attacks

A malicious hacker could break into the `jhpyle/docassemble` GitHub
account, Docker Hub account, PyPI account, CloudFlare account, or DNS
provider.

These risks are mitigated by the use of two-factor authentication on
all of these accounts.

If any of these accounts were to be compromised, Jonathan Pyle would
immediately inform the **docassemble** community and work with the
hosting provider to disable the unauthorized access.

### Compromised dependencies

Even if the **docassemble** code base is never compromised, since it
depends on many other pieces of software, there is a risk that one of
these pieces of software could become infected, and then the infection
would pass down to all implementers of the software through the
software update mechanism.

The following techniques are employed to mitigate this risk:

* The `Dockerfile` depends on a specific, stable distribution of
  Debian Linux (`buster`), which only receives security updates.
* Python dependencies are pinned to specific versions.  Dependencies
  of dependencies and their versions are specified in the `setup.py`
  files of **docassemble**.  Once a specific version is posted to
  PyPI, it is the policy of PyPI that it cannot be changed.
* Because of the "pinning" of versions of dependencies, the software
  inside the **docassemble** container is not automatically upgraded
  when new versions become available.  This increases the likelihood
  that the code will be well-tested and thoroughly scanned for
  vulnerabilities.
* GitHub scans the code to identify vulnerabilities.
* As part of **docassemble**'s normal development process, the code is
  scanned using Clair.
* The `stable` branch on GitHub (version 1.0.x) receives only bug
  fixes, not feature enhancements.  Thus, upgrading to a new 1.0.x
  version will not install any new software dependencies in to a
  server.
  
