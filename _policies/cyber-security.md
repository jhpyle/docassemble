---
layout: policy
title: Cybersecurity
short_title: Cybersecurity
---

# Cybersecurity policy

*Note: **docassemble** is licensed under the [MIT License].  This
policy does not modify that license or create any contract.*

Since **docassemble** is in no way a "software as a service" product,
cybersecurity is largely the responsibility of the implementer.
However, there are cybersecurity risks to **docassemble** as an
open-source project.

# Risk of accidental inclusion of faulty code

There is a risk that a new version of **docassemble** could introduce
a defect that could compromise security and reliability.  The software
is provided with an "as is" license; no warranty is made that the
software is free of defects.

The following techniques are used to to mitigate this risk:

* The entire source code is available to the public for inspection.
* `git diff` is used to carefully inspect all changes made to the
  code.  Individual commits can be inspected on GitHub.
* Any pull requests are scrutinized heavily before being accepted.
* Whenever possible, popular libraries are used rather than homegrown
  code.  The skeleton of the web app is based on Flask and widely used
  Flask plugins.  Bootstrap is used for the user interface.  While
  **docassemble** itself may not be widely tested, these libraries are
  much more widely used, and defects are thus more likely to surface.
* Before a new version is pushed, a comprehensive suite of `aloe` tests
  is performed to ensure that the software works as expected.

# Open-source infrastructure attacks

A malicious hacker could break into the `jhpyle/docassemble` GitHub
account, Docker Hub account, PyPI account, CloudFlare account, or DNS
provider.

These risks are mitigated by the use of two-factor authentication on
all of these accounts.

If any of these accounts were to be compromised, Jonathan Pyle would
immediately inform the **docassemble** community and work with the
hosting provider to disable the unauthorized access.

There is a risk of unauthorized access to Jonathan Pyle's computers,
which could possibly expose SSL encryption keys to a bad actor.
Personal computers are secured by passwords and cloud computers are
not accessible with passwords alone, but require SSL certificates or
two-factor authentication.

If Jonathan Pyle discovers unauthorized access to any of his
computers, he will notify the **docassemble** community via Slack and
e-mail and change all encryption keys on remote servers (such as
GitHub).

If Docker Hub becomes unavailable, https://harbor.docassemble.org will
be used to distribute Docker images.

If GitHub becomes unavailable, Bitbucket will be used.

If PyPI becomes unavailable, a PyPI mirror will be created, unless a
widely-used public mirror becomes available, in which case that server
will be used instead.

# Compromised dependencies

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

# Development practices

**docassemble** has been developed with awareness and understanding of
the security vulnerabilities including the [OWASP Top Ten].

## Injection

**docassemble** code mitigates against injection attacks by using
SQLAlchemy to form SQL statements, by sanitizing input such as file
names.

## Authentication

**docassemble** uses Flask packages for user authentication rather
than homegrown packages.

## Sensitive data

**docassemble** protects [data privacy] by using server-side
encryption and other techniques.

## XML External Entities

**docassemble** rarely uses XML but when it does, it uses up-to-date
XML processing libraries.

## Authorization

**docassemble** contains an authorization system based on Flask so
that ordinary users cannot access parts of the system that only
administrators should be able to access.

## Security configuration

**docassemble** is a platform rather than a product.  It is possible
to implement it in an insecure way, for example by opening S3 to the
public.  However, if implementers know what they are doing and follow
the documentation, they can configure the system with full security.

## Cross-site scripting

**docassemble** contains features to avoid cross-site attacks, such as
CSRF and cookie flags.

## Dependencies

**docassemble** contains a number of dependencies, and to the extent
that any of them have known vulnerabilities, countermeasures have been
taken.  The code is scanned and CVEs on dependencies have been
reviewed and acted upon if necessary.

## Serialization

**docassemble** makes extensive use of serialization (YAML, JSON, and
pickle).  The YAML and JSON methods are secure.  Python's pickle
feature has security implications, but **docassemble** only unpickles
data that it has pickled itself.  If the SQL and Redis databases are
not kept secure, then it is conceivable that malicious pickled data
could be injected into the databases and that data could be processed
by the application.

## Logging

**docassemble**'s logs are sufficiently detailed that they can be used
as a tool for discovering errors and intrusion attempts.
**docassemble** can be configured to send error messages via e-mail.

# Incident reporting

If Jonathan Pyle becomes aware of a issue with the **docassemble**
software or its dependencies that could compromise the security of
users' systems, he will notify the **docassemble** community over
Slack and e-mail and attempt to patch the software as soon as
possible.  Once a fix is found, a message will be posted to Slack and
e-mail recommending that users install the new Docker image.

# Insurance

**docassemble** is an open-source project, not an entity.  There is no
insurance.  The code is provided under an "as-is" license.

[data privacy]: {{ site.baseurl }}/policies/data-privacy.html 
[MIT License]: {{ site.baseurl }}/docs/license.html
[OWASP Top Ten]: https://owasp.org/www-project-top-ten/
