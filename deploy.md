---
layout: docs
title: How to Deploy
short_title: Deploy
order: 40
---

The easiest way to deploy **docassemble** to install it using
[Docker]. If you want very fine-grained control, you can [install] it
without using Docker, but very few people do that.

Most people run **docassemble** on a virtual machine in the
cloud. Since **docassemble** is free software, there are no fees for
using it, but hosting a server on the internet will cost money
(between $10 and $40 per month, or more, depending on what your
performance, availability, and support needs are).

It is possible to run [Docker] on a laptop using [Docker Desktop] if
you just want to quickly test it out, but running **docassemble** on a
laptop is not a good long-term deployment platform because a laptop
sleeps, hibernates, and shuts down frequently, and your [Docker]
container might experience corruption as a result.

For high performance, you can run **docassemble** using a [cluster] of
machines. However, for the vast majority of deployments, a single
machine works fine.

## Example of a deployment

Here is an example of one way to get a **docassemble** server up and
running on the internet:

* Create an account at [Amazon Lightsail].
* In [Amazon Lightsail], create an "instance." Select the
  "Unix/Linux" platform. Select the "OS only" blueprint "Amazon Linux
  2." Choose an "instance plan" that has 4 GB of memory and an 80 GB SSD.
* Go into the configuration of your instance and go to "networking."
  Under "IPv4 Firewall," you will see that the SSH port, port 22, and
  the HTTP port, port 80, are open. This is good; you will need these
  two ports. You will also need the HTTPS port, port 443, to be open,
  so click "Add rule," select "HTTPS" as the "application," and click
  "Create."
* Note the "Public IP" of your "instance." This is the IP address that
  computers on the internet will use to connect to your
  **docassemble** server.
* Create an account with [Namecheap] or another domain name
  registrar. Purchase a domain name. For example, your domain name
  might be `foobar.com`. Then, go into the [DNS] configuration and
  create an [A record] that maps the hostname `da.foobar.com` to the
  IP address you found in the previous step. This means that your
  **docassemble** server will be available at
  `https://da.foobar.com`. If you want, you can set up your DNS so
  that `https://foobar.com` goes right to your **docassemble** server.
* Many domain name registrars will offer you additional services
  besides [DNS]. You don't need any of those things to use
  **docassemble**; you just need control over [DNS] for a domain.
* Go to the "Connect" tab and look at the information under "Use your
  own SSH client." If you aren't familiar with using SSH clients, now
  is a good time to learn. If you are a PC user, [use PuTTY], and if
  you are a Mac user, [use Terminal]. For security reasons, you need
  to use a "key" to connect to your virtual machine. This provides
  greater security than a username and password. You should get
  familiar with how to use keys. It is possible to connect via SSH
  inside the web browser if you are impatient, but you should still
  take the time to learn how to use an SSH client on your computer.
* When you are connected to your machine using SSH, you can start
  running commands to install [Docker]. There are additional
  instructions in the [Docker] section of the documentation. On a
  Lightsail Amazon Linux machine, the commands to run are:

{% highlight bash %}
sudo yum -y update
sudo yum -y install docker
sudo usermod -a -G docker ec2-user
exit
{% endhighlight %}

* Running "exit" will disconnect you from SSH. In order for the `usermod`
  command to take effect, you need to log out and log in again.
* Reconnect via SSH and then create a text file called `env.list`.

{% highlight bash %}
nano env.list
{% endhighlight %}

* Set the contents of the file the following, substituting your own
hostname in place of `da.foobar.com`, and substituting [your own
time zone] in place of `America/New_York`, and your own e-mail address
in place of `you@youremaildomain.com`.

{% highlight bash %}
DAHOSTNAME=da.foobar.com
TIMEZONE=America/New_York
USEHTTPS=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=you@youremaildomain.com
{% endhighlight %}

* When you are done, press Ctrl-s to save the file and Ctrl-x to exit
  the `nano` text editor.
* Now you can create a **docassemble** [Docker] container:

{% highlight bash %}
docker run --env-file=env.list -v dabackup:/usr/share/docassemble/backup -d -p 80:80 -p 443:443 --stop-timeout 600 jhpyle/docassemble
{% endhighlight %}

* Wait five minutes and then visit your **docassemble** server using
  your web browser (e.g., `https://da.foobar.com`).
* If it doesn't work, check out the [Troubleshooting] section.

Note that there are many different cloud providers and domain name
registrars; [Amazon Lightsail] and [Namecheap] are mentioned here only
as examples, not as recommendations.

This is one possible method of deployment. If your goal is to embed a
**docassemble** interview on a different web site, you may wish to use
a different deployment strategy using a [web server and a reverse proxy].

## Consultants

If you are interested in hiring someone to develop an interview for
you, you can propose a project in the #questions channel of the [Slack
group].  Consultants who are available for projects include:

* [Lemma Legal Consulting]

[use Terminal]: https://lightsail.aws.amazon.com/ls/docs/en_us/articles/amazon-lightsail-ssh-using-terminal
[use PuTTY]: https://lightsail.aws.amazon.com/ls/docs/en_us/articles/lightsail-how-to-set-up-putty-to-connect-using-ssh
[Amazon Lightsail]: https://aws.amazon.com/lightsail/
[Lemma Legal Consulting]: https://lemmalegal.com
[cluster]: {{ site.baseurl }}/docs/scalability.html
[install]: {{ site.baseurl }}/docs/installation.html
[Docker]: {{ site.baseurl }}/docs/docker.html
[Amazon Web Services]: https://aws.amazon.com
[Slack group]: {{ site.slackurl }}
[Docker Desktop]: https://www.docker.com/products/docker-desktop/
[your own time zone]: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
[CNAME record]: https://en.wikipedia.org/wiki/CNAME_record
[A record]: https://en.wikipedia.org/wiki/List_of_DNS_record_types#A
[Troubleshooting]: {{ site.baseurl }}/docs/docker.html#troubleshooting
[web server and a reverse proxy]: {{ site.baseurl }}/docs/docker.html#forwarding
[Namecheap]: https://www.namecheap.com/domains/
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
