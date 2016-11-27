---
layout: docs
title: Scalability of docassemble
short_title: Scalability
---

**docassemble** can easily be scaled in the cloud.  A cluster of web
servers can serve responses to client browsers, while communicating
with centralized services.  The limit to scalability will then be a
question of how responsive a single SQL server can be and how
responsive a single [Redis] server can be.

# Quick start

If you want to run **docassemble** in a scalable
[multi-server arrangement], there are a variety of ways to do so, but
the following is the recommended way to get started.  It takes
advantage of the many features of [Amazon Web Services] ([AWS]).

## Overview

In this example, one server will perform central functions (SQL,
[Redis], [RabbitMQ], and log message aggregation) and two separate
servers will act as application servers.  The application servers will
act as web servers, receiving requests that are distributed by a
[load balancer].  These servers will also operate as [Celery] nodes,
running [background processes] for **docassemble** interviews.  All
three of the servers will be [EC2] virtual machines situated within a
private network on [AWS] called a [Virtual Private Cloud] ([VPC]).

Users will point their browsers at a URL like
`https://docassemble.example.com`, where the [DNS] entry for
`docassemble.example.com` is a [CNAME] that points to an
[Application Load Balancer] (at an address like
`myloadbalancer-198225082.us-west-1.elb.amazonaws.com`).  The
[Application Load Balancer] will take care of generating and serving
SSL certificates for the encrypted connection.

The [Application Load Balancer] will convert the HTTPS requests into
HTTP requests and send them to the web servers.  From the perspective
of the web servers, all incoming requests will use the HTTP scheme.
But from the perspective of the web browser, the web site uses the
HTTPS scheme.

Within the [VPC], the web servers will communicate with the central
server using a variety of TCP ports.

The three servers will all be part of an [Auto Scaling Group].  This
means that as more people use your site, you can expand beyond two web
servers to any number of web servers.

The software will be deployed on the servers by the
[EC2 Container Service] ([ECS]).  [ECS] is [Amazon]'s system for
automatically deploying [Docker] containers on [EC2] instances.

In the vocabulary of [ECS], there will be one "[cluster]" (the default
cluster) running two services: "backend" and "app."

The "backend" service consists of a single "task," where the task is
defined as a single [Docker] "container" running the "image"
`jhpyle/docassemble` with the environment variable `CONTAINERROLE` set
to `sql:redis:rabbitmq:log`.  You will ask for one of these services
to run (i.e. the "desired count" of this service is set to 1).

The "app" service consists of a single "task," where the task is
defined as a single [Docker] "container" running the "image"
`jhpyle/docassemble` with the environment variable `CONTAINERROLE` set
to `web:celery`.  You will ask for two of these services to run
(i.e. the "desired count" of this service is set to 2).  (You will be
able to change this count in the future.)

The result of this configuration will be that three [EC2] virtual
machines will exist, all of which will be running [Docker].  Each
virtual machine will "run" the same [Docker] container, except that
the "backend" instance will run with different environment variables
than the "app" instances.

To shutdown your **docassemble** setup, you would first edit the "app"
service and set the "count" to zero.  Then, after a few minutes, the
[Docker] containers will stop.  Once the "app" services are no longer
running, you will then do the same with the "backend" service.  Then,
if you want to turn off your [EC2] virtual machines, you would edit
the [Auto Scaling Group] and set the desired number of instances to zero.

You can then restart your **docassemble** system and it will pick up
exactly where it left off.  This is because **docassemble** will back
up SQL, [Redis], and other information to [S3] when the containers
shut down, and restore from the backups when they start up again.  To
restart, you would edit the [Auto Scaling Group] to set the desired
number of instances to 3.  When they are up and running, you would
then update the "backend" service and set the "desired count" to 1.
Once that service is up and running, you would update the "app"
service and set the "desired count" to 2.

## Setup instructions

The following instructions will guide you through the process of using
[AWS] to set up a **docassemble** installation.  [AWS] itself is
beyond the scope of this documentation.  If you have never used [AWS]
before, you are encouraged to consult the [AWS] documentation.

These instructions assume that you own a [domain name] and can add
[DNS] entries for the domain.  (If you do not have a [domain name],
you can purchase one from a site like [GoDaddy] or [Google Domains].)
In this example, we will use `docassemble.example.com` as the example
hostname, but you will need to replace this with whatever hostname you
are going to use.

First, sign up for an [Amazon Web Services] account.

Log in to the [AWS Console].  If you have not used [ECS] before,
navigate to the service called "EC2 Container Service" and click "Get
Started" to follow the steps of the introductory "wizard."  Check the
option for "deploy a sample application onto an Amazon ECS Cluster."
Follow the default selections.  The wizard will create a [cluster]
called "default," an [IAM] role called `ecsInstanceRole`, and several
resources, including a [CloudFormation] stack, an [Internet Gateway],
[VPC], a [Route Table], a [VPC Attached Gateway], two [subnets], a
[Security Group] for an [Elastic Load Balancer], a [Security Group]
for [ECS] instances, a [Launch Configuration], and an
[Auto Scaling Group].

Most of what the wizard creates is not needed and should be deleted.
The running [EC2] instance may also cost you money.  To delete the
unnecessary resources:

1. Go to the [ECS Console], find the service "sample-webapp," update
it, and set the "Number of tasks" to 0.  Then you can delete
"sample-webapp."  Also go into "Task Definitions" and delete the one
[Task Definition] there.
2. Go to the [EC2 Console], go into the "Instances" section, and change
the "Instance State" of the one running instance to "Terminate."
3. Then go into the "Auto Scaling Groups" section and delete the one
[Auto Scaling Group].
4. Then go into the "Launch Configurations" section and delete the one
[Launch Configuration].
5. Then go to the [VPC Console], select the [VPC] for which "Default
VPC" is "No," and delete it.  (Be careful not to delete the default
VPC!)

Next, we need to create an [S3] "bucket" in which your **docassemble**
system can store files, backups, and other things.  To do this, go to
the [S3 Console], click "Create Bucket," and pick a name.  If your
site is at docassemble.example.com, a good name for the bucket is
`docassemble-example-com`.  (Client software will have trouble
accessing your bucket if it contains `.` characters.)  Under "Region,"
pick the region nearest you.

Next, we need to create an [IAM] role for the [EC2] instances that
will run **docassemble**.  This role will empower the server to
operate on [ECS] and to access the [S3] "bucket" you created.  To do
this, go to the [IAM Console] and go to "Roles" -> "Create New Role."
Call your new role "docassembleInstanceRole" or some other name of
your choosing.  Under "AWS Service Roles," select "Amazon EC2 Role for
EC2 Container Service."  On the "Attach Policy" screen, check the
checkbox next to "AmazonEC2ContainerServiceforEC2Role," and continue
on to create the role.

Once the role is created, go into the "Inline Policies" area of the
role and create a new inline policy.  Select "Custom Policy," enter a
"Policy Name" like "S3DocassembleExampleCom," and set the "Policy
Document" to the following (substituting the name of the bucket you
created in place of `docassemble-example-com` in the two places it
appears):

{% highlight json %}
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::docassemble-example-com"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::docassemble-example-com/*"
            ]
        }
    ]
}
{% endhighlight %}

(Note that instead of creating an inline policy that limits access to
a particular bucket, you could attach the "AmazonS3FullAccess" policy
to the role and give [EC2] instances full access to all of your
account's [S3] buckets.)

This inline policy allows any application running on a machine given
the `docassembleInstanceRole` role to access your [S3] bucket.  This
saves you from having to include long and complicated secret keys in
the environment variables you pass to **docassemble** [Docker]
containers.  All of the [EC2] instances you create in later steps will
be given the `docassembleInstanceRole` [IAM] role.

Go to [VPC Console] and inspect the description of the default [VPC].
(If you have more than one [VPC], look for the [VPC] where "Default
VPC" is "Yes.")  Make a note of the [VPC CIDR] address for the VPC, which will be
something like `172.68.0.0/16` or `10.1.0.0/16`.

Go to the [EC2 Console] and set up a new [Security Group] called
`docassembleSg` with permissions on port 22 (SSH) for all addresses,
and all traffic for the CIDR address you noted.

Go to the "Launch Configuration" section of the [EC2 Console] and
create a new [Launch Configuration] called `docassembleLc`.  When it
asks what [AMI] you want to use, go to Community AMIs, search for the
keyword "ecs-optimized" and pick the most recent AMI that comes up.
The AMIs will not be listed in any useful order, so you have to look
carefully at the names, which contain the dates the AMIs were created.
As of this writing, the most recent ECS-optimzed AMI is
"amzn-ami-2016.09.b-amazon-ecs-optimized."  Set the "IAM role" of the
[Launch Configuration] to `docassembleInstanceRole`, the [IAM] role
you created earlier.  Set the security group to `docassembleSg`, the
[Security Group] you created earlier.

Then go to the "Auto Scaling Groups" section of the [EC2 Console] and
create a new [Auto Scaling Group] called `docassembleAsg`.  Connect it
with `docassembleSg`, the [Launch Configuration] you just created.
Use a fixed number of instances without scaling in response to
[CloudWatch] alarms.  Set the number of instances to 3.

Then go to the [ECS Console].

Create a [Task Definition] called `backend` using the [JSON]
configuration below.  Edit the `TIMEZONE`, `DAHOSTNAME`, and
`S3BUCKET` environment variables.

{% highlight json %}
{
  "family": "backend",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "jhpyle/docassemble",
      "cpu": 1,
      "memory": 900,
      "portMappings": [
        {
          "containerPort": 8080,
          "hostPort": 8080
        },
        {
          "containerPort": 5432,
          "hostPort": 5432
        },
        {
          "containerPort": 514,
          "hostPort": 514
        },
        {
          "containerPort": 6379,
          "hostPort": 6379
        },
        {
          "containerPort": 4369,
          "hostPort": 4369
        },
        {
          "containerPort": 5671,
          "hostPort": 5671
        },
        {
          "containerPort": 5672,
          "hostPort": 5672
        },
        {
          "containerPort": 25672,
          "hostPort": 25672
        },
        {
          "containerPort": 9001,
          "hostPort": 9001
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "CONTAINERROLE",
          "value": "sql:redis:rabbitmq:log"
        },
        {
          "name": "DAHOSTNAME",
          "value": "docassemble.example.com"
        },
        {
          "name": "EC2",
          "value": "true"
        },
        {
          "name": "BEHINDHTTPSLOADBALANCER",
          "value": "true"
        },
        {
          "name": "S3BUCKET",
          "value": "docassemble-example-com"
        }
      ],
      "mountPoints": []
    }
  ],
  "volumes": []
}
{% endhighlight %}

The `CONTAINERROLE` variable indicates that this server will serve the
functions of SQL, [Redis], [RabbitMQ], and log message aggregation.
The `DAHOSTNAME` variable indicates the hostname at which the user
will access the **docassemble** application.  The `EC2` variable
instructs **docassemble** that it will be running on [EC2], which
means that the server needs to use a special method of obtaining its
own [fully-qualified domain name].

Then, check the [ECS Console] and look at the `default` [cluster].
There should be three [container instances] available.  (If not,
something is wrong with the [Auto Scaling Group] you created, or
perhaps the instances are still starting up.)

Then, create a Service called `backend` that uses the task definition
you just created.  Set the number of tasks to 1.  Do not choose an
[Elastic Load Balancer].  This will cause the **docassemble** [Docker]
image to be installed on one of the [container instances].  It will
take some time for the image to download and start.  In the meantime,
the [ECS Console] should show one "pending task."

Next, create a [Task Definition] called `app` using the [JSON]
configuration below.  Edit the `S3BUCKET` environment variables.

{% highlight json %}
{
  "family": "app",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "jhpyle/docassemble",
      "cpu": 1,
      "memory": 900,
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80
        },
        {
          "containerPort": 9001,
          "hostPort": 9001
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "CONTAINERROLE",
          "value": "web:celery"
        },
        {
          "name": "S3BUCKET",
          "value": "docassemble-example-com"
        }
      ],
      "mountPoints": []
    }
  ],
  "volumes": []
}
{% endhighlight %}

Create a Service called `app` that uses the task definition
`docassemble-app`.  Set the number of tasks to 1 and use the [Elastic Load
Balancer] you just created.
11. Set up the security groups on the [Elastic Load Balancer] and the
[VPC] so that the instances within the [VPC] can send any traffic among
each other, but that only HTTP (or HTTPS) is open to the outside world.
12. Decide what URL you want users to use, and edit your DNS to add a
CNAME pointing from that URL to the URL of the load balancer.
13. Create a sufficient number of [EC2] instances so that the
`docassemble-sql`, `docassemble-log`, and `docassemble-app` tasks all
have room to run.
14. Create an [Auto Scaling Group] for the `docassemble-app` task so
that any number of instances (up to a limit) can support the
`docassemble-app` task.

Go to [VPC] and copy the CIDR of the network.

Go to [EC2] and create a new security group.  Allow all traffic from
the CIDR of your [VPC].





## All in one

{% highlight json %}
{
  "family": "docassemble-all",
  "containerDefinitions": [
    {
      "name": "docassemble-all",
      "image": "jhpyle/docassemble",
      "memory": 900,
      "cpu": 1,
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80
        },
        {
          "containerPort": 443,
          "hostPort": 443
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "DAHOSTNAME",
          "value": "docassemble.example.com"
        },
        {
          "name": "EC2",
          "value": "true"
        },
        {
          "name": "USEHTTPS",
          "value": "true"
        },
        {
          "name": "S3BUCKET",
          "value": "docassemble-example-com"
        }
      ]
    }
  ]
}
{% endhighlight %}


# Alternative method without using EC2 Container Service

1. Get an [Amazon Web Services] account.
2. Go to [Amazon S3] and obtain an access key and a secret access
key.  Create a bucket.
3. Go to [Amazon EC2] and launch three [Amazon Linux] instances in the
same [Virtual Private Cloud] ([VPC]).
4. Edit your [VPC] so that "DNS Resolution" Yes and "DNS Hostnames" is
   Yes.
5. Install [Docker] in all three instances: `sudo yum -y update && sudo yum
-y install docker && sudo usermod -a -G docker ec2-user`.  Then log
out and log back in again.  See [Amazon's Docker instructions] for
more information.
6. In the first [EC2] instance, start a PostgreSQL container using the
official **docassemble** [Docker] image: `docker run -d -p 5432:5432
jhpyle/docassemble-sql`.
7. In the second [EC2] instance, start a log container using the
official **docassemble** [Docker] image: `docker run -d -p 514:514 -p
8080:80 jhpyle/docassemble-log`.
7. Note the "Private DNS" hostname of these instances.  Then go to
[Amazon Route 53] and create a Hosted Zone with the type "Private
Hosted Zone for Amazon VPC."  Use a domain like `docassemble.local` or
whatever you want (this is purely internal).  Create a CNAME that maps
`sql.docassemble.local` (or other name of your choosing) to the
"Private DNS" hostname of the instance running the SQL server.  This
is so that the application servers can locate the SQL server by
`sql.docassemble.local`.  Alternatively, you could forget about
[Amazon Route 53] and just use the "Private IP" address of the SQL
instance in place of the hostname, but it is nicer to be able to use
DNS, in case the underlying IP address ever changes.
8. Do the same for the log server (`log.docassemble.local`).
8. Go to the third [EC2] instance and create a file called `env.list`
similar to the example below.  Substitute your own values for
`DBHOST`, `LOGSERVER`, `S3ACCESSKEY`, `S3SECRETACCESSKEY`, and `S3BUCKET`.
9. Run `docker run --env-file=env.list -d -p 80:80 -p 443:443 -p
9001:9001 jhpyle/docassemble`
10. Edit the [Security Group] on the second instance to allow HTTP
traffic from anywhere.
11. Point your browser to the "Public IP" of the second instance.  A
**docassemble** interview should appear.
12. You can create as many additional instances as you want and deploy
**docassemble** on them by repeating steps 8-9.  Make sure these new
instances use the same security group, so you don't have to repeat
step 10.
13. Add the instances (other than the SQL and log server instances) to a load
balancer.

Here is an example `env.list` file:

{% highlight text %}
CONTAINERROLE=webserver
DBNAME=docassemble
DBUSER=docassemble
DBPASSWORD=abc123
DBHOST=sql.docassemble.local
LOGSERVER=log.docassemble.local
S3ENABLE=true
S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF
S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
S3BUCKET=yourbucketname
EC2=true
{% endhighlight %}

# Explanation

Each server's [configuration] is defined in
`/usr/share/docassemble/config.yml`.  The default configuration for
the SQL connection is:

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: null
  password: null
  host: null
  port: null
{% endhighlight %}

This will cause **docassemble** to connect to PostgreSQL on the local
machine with peer authentication and use the database "docassemble."
This configuration can be modified to connect to a remote server.

Configuring a cluster of **docassemble** servers requires centralizing
the location of uploaded files, either by using an [Amazon S3] bucket
(the `s3` [configuration] setting) or by making the uploaded file
directory a network drive mount (the `uploads` [configuration]
setting).

The default location of uploaded user files is defined by the
`uploads` [configuration] setting:

{% highlight yaml %}
uploads: /usr/share/docassemble/files
{% endhighlight %}

However, **docassemble** will use [Amazon S3] instead of this folder
if [S3] is enabled as follows:

{% highlight yaml %}
s3:
  enable: true
  access_key_id: FWIEJFIJIDGISEJFWOEF
  secret_access_key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
  bucket: yourbucketname
{% endhighlight %}

When developers install new Python packages, the packages are unpacked
in `/usr/share/docassemble/local` (controlled by [configuration]
variable `packages`).

The web server will restart, and re-read its Python source code, if
the modification time on the WSGI file,
`/usr/share/docassemble/webapp/docassemble.wsgi`, is changed.  The
path of the WSGI file is defined in the [Apache configuration] and in
the **docassemble** configuration file:

{% highlight yaml %}
webapp: /usr/share/docassemble/docassemble.wsgi
{% endhighlight %}

# Synchronizing configuration and installs with supervisor

If you are using Amazon EC2, set the following in the [configuration]:

{% highlight yaml %}
ec2: true
{% endhighlight yaml %}

This can also be set with the `EC2` environment variable if
[using Docker].

# SQL server

To start a postgresql server in an [Amazon Linux] instance:

{% highlight bash %}
sudo yum install postgresql-server
sudo service postgresql initdb
sudo service postgresql start
sudo -u postgres createuser --login --pwprompt docassemble
sudo -u postgres createdb --owner=docassemble docassemble
{% endhighlight %}

The "createuser" line will ask for a password; enter something like `abc123`.

Now that the server is running, you can set up web servers to
communicate with the server by setting something like the following in
the [configuration]:

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: 192.168.0.56
  port: null
  table_prefix: null
{% endhighlight %}

If you installed the web servers before installing the SQL server,
note that the [`create_tables`] module will need to be run in order to
create the database tables that **docassemble** expects.

# Mail server

If you are launching **docassemble** within [EC2], note that Amazon does
not allow e-mail to be sent from SMTP servers operating within an [EC2]
instance, unless you obtain special permission.  Therefore, you may
wish to use an SMTP server on the internet with which you can connect
through [SMTP Authentication]. 

If you have a Google account, you can use Google's SMTP server by
setting the following in your [configuration]:

{% highlight yaml %}
mail:
  server: smtp.gmail.com
  username: yourgoogleusername
  password: yourgooglepassword
  use_ssl: true
  port: 465
  default_sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

Note that for this to work, you will need to go into your Google
settings and set "Allow less secure apps" to "ON."

Alternatively, you could set up an e-mail server on [Amazon SES].  It
is easy to set up, but in order to get permission to send e-mails to
the outside world, you will need to explain to Amazon what your
purposes for sending e-mail are, and explain your policy of dealing
with replies and bounce-backs.

# Using S3 without passing access keys in the configuration

If you are running **docassemble** on an [EC2] instance, or on a
[Docker] container within an [EC2] instance, you can set up the
instance with an [IAM role] that allows access [S3] without supplying
credentials.  In this case, the configuration in **docassemble** does
not include an `access_key_id` or a `secret_access_key`.

{% highlight yaml %}
s3:
  enable: true
  bucket: yourbucketname
{% endhighlight %}

[IAM role]: http://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_use_switch-role-ec2.html
[SMTP Authentication]: https://en.wikipedia.org/wiki/SMTP_Authentication
[Apache]: https://en.wikipedia.org/wiki/Apache_HTTP_Server
[Apache configuration]: {{ site.baseurl }}/docs/installation.html
[configuration]: {{ site.baseurl }}/docs/config.html
[installation]: {{ site.baseurl }}/docs/installation.html
[SQLAlchemy]: http://www.sqlalchemy.org/
[S3]: https://aws.amazon.com/s3/
[Amazon S3]: https://aws.amazon.com/s3/
[Amazon EC2]: https://aws.amazon.com/ec2/
[EC2]: https://aws.amazon.com/ec2/
[Amazon SES]: https://aws.amazon.com/ses/
[Amazon Linux]: https://aws.amazon.com/amazon-linux-ami/
[Amazon Web Services]: https://aws.amazon.com
[AWS]: https://aws.amazon.com
[Docker]: {{ site.baseurl }}/docs/docker.html
[Amazon's Docker instructions]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/docker-basics.html
[Virtual Private Cloud]: https://aws.amazon.com/vpc/
[VPC]: https://aws.amazon.com/vpc/
[Amazon Route 53]: https://aws.amazon.com/route53/
[Security Group]: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-network-security.html
[supervisor]: http://supervisord.org/
[EC2 Container Service]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
[ECS]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html
[Elastic Load Balancer]: https://aws.amazon.com/elasticloadbalancing/
[Auto Scaling Group]: http://docs.aws.amazon.com/AutoScaling/latest/DeveloperGuide/AutoScalingGroup.html
[create your own Docker image]: {{ site.baseurl }}/docs/docker.html#build
[using Docker]: {{ site.baseurl }}/docs/docker.html#build
[`create_tables`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/create_tables.py
[JSON]: https://en.wikipedia.org/wiki/JSON
[Redis]: http://redis.io/
[RabbitMQ]: https://www.rabbitmq.com/
[background processes]: {{ site.baseurl }}/docs/functions.html#background
[live help]: {{ site.baseurl }}/docs/livehelp.html
[Celery]: http://www.celeryproject.org/
[DNS]: https://en.wikipedia.org/wiki/Domain_Name_System
[load balancer]: https://en.wikipedia.org/wiki/Load_balancing_(computing)
[CNAME]: https://en.wikipedia.org/wiki/CNAME_record
[AMI]: http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/AMIs.html
[VPC CIDR]: http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Subnets.html
[autoscaling tutorial]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/cloudwatch_alarm_autoscaling.html
[Application Load Balancer]: https://aws.amazon.com/elasticloadbalancing/applicationloadbalancer/
[cluster]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_clusters.html
[DNS server]: https://en.wikipedia.org/wiki/Domain_Name_System
[domain name]: https://en.wikipedia.org/wiki/Domain_name
[GoDaddy]: https://www.godaddy.com/
[Google Domains]: https://domains.google.com/
[AWS Console]: https://aws.amazon.com/console/
[S3 Console]: https://console.aws.amazon.com/s3/home
[IAM Console]: https://console.aws.amazon.com/iam
[ECS Console]: https://console.aws.amazon.com/ecs/home
[VPC Console]: https://console.aws.amazon.com/vpc/home
[Launch Configuration]: http://docs.aws.amazon.com/autoscaling/latest/userguide/LaunchConfiguration.html
[CloudFormation]: https://aws.amazon.com/cloudformation/
[Internet Gateway]: http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Internet_Gateway.html
[Route Table]: http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Route_Tables.html
[VPC Attached Gateway]: http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Internet_Gateway.html#Add_IGW_Attach_Gateway
[subnets]: http://docs.aws.amazon.com/AmazonVPC/latest/UserGuide/VPC_Subnets.html
[Task Definition]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_defintions.html
[Amazon]: https://amazon.com
[IAM]: https://aws.amazon.com/iam/
[CloudWatch]: https://aws.amazon.com/cloudwatch/
[container instance]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_instances.html
[container instances]: http://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_instances.html
[fully-qualified domain name]: https://en.wikipedia.org/wiki/Fully_qualified_domain_name
[multi-server arrangement]: {{ site.baseurl }}/docs/docker.html#multi server arrangement
