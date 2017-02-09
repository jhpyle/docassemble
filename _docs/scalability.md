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
`jhpyle/docassemble` with the environment variable [`CONTAINERROLE`] set
to `sql:redis:rabbitmq:log:cron:mail`.  You will ask for one of these services
to run (i.e. the "desired count" of this service is set to 1).

The "app" service consists of a single "task," where the task is
defined as a single [Docker] "container" running the "image"
`jhpyle/docassemble` with the environment variable [`CONTAINERROLE`] set
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

## Instructions

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
VPC" is "Yes.")  Make a note of the [VPC CIDR] address for the VPC,
which will be something like `172.68.0.0/16` or `10.1.0.0/16`.

Go to the [EC2 Console] and set up a new [Security Group] called
`docassembleSg` with two rules.  One rule should allow traffic of
"Type" SSH from "Source" Anywhere.  The other rule should allow "All
traffic" from "Source" Custom IP, where the address is the [CIDR]
address you noted.  This will provide the "firewall rules" for your
servers so that you can connect to them via SSH and so that they can
communicate among each other.

Go to the "Launch Configuration" section of the [EC2 Console] and
create a new [Launch Configuration] called `docassembleLc`.  When it
asks what [AMI] you want to use, go to "Community AMIs," search for
the keyword "ecs-optimized" and pick the most recent [AMI] that comes
up.  The [AMI]s will not be listed in any useful order, so you have to
look carefully at the names, which contain the dates the [AMI]s were
created.  As of this writing, the most recent ECS-optimzed [AMI] is
"amzn-ami-2016.09.b-amazon-ecs-optimized."  Set the "IAM role" of the
[Launch Configuration] to `docassembleInstanceRole`, the [IAM] role
you created earlier.  Set the security group to `docassembleSg`, the
[Security Group] you created earlier.

Then go to the "Auto Scaling Groups" section of the [EC2 Console] and
create a new [Auto Scaling Group] called `docassembleAsg`.  Connect it
with `docassembleLc`, the [Launch Configuration] you just created.
Use a fixed number of instances without scaling policies that respond
to [CloudWatch] alarms.  Set the number of instances to 3.  Once the
[Auto Scaling Group] is saved, [AWS] should start running three [EC2]
instances.  Since you chose an [ECS]-optimized AMI, the instances
should automatically register with your [ECS] cluster.

The next step is to create an [Application Load Balancer].  The load
balancer will accept HTTPS requests from the outside world and forward
them to the application servers as HTTP requests.  It will forward two
types of requests: regular HTTP requests and [WebSocket] requests.
(The [live help] features of **docassemble** use the [WebSocket]
protocol for real time communication between operators and users.)
The [Application Load Balancer] needs to treat [WebSocket] requests
differently.  While regular [HTTP] requests can be forwarded randomly
to any application server, [WebSocket] requests for a given session
need to be forwarded to the same server every time.

To set up the [Application Load Balancer], first you need to create a
[Security Group] that will allow communication from the outside world
through HTTPS.  Go to the "Security Groups" section of the
[EC2 Console] and create a new [Security Group].  Set the "Security
group name" to `docassembleLbSg` and set the "Description" to
"docassemble load balancer security group."  Attach it to your default
[VPC].  Add two "Inbound" rules to allow HTTP and HTTPS traffic from
anywhere.  For the first rule, set "Type" to HTTPS and "Source" to
"Anywhere."  For the second rule, set "Type" to HTTP and "Source" to
"Anywhere."

Then go to the "Load Balancing" -> "Target Groups" section of the
[EC2 Console] and create a new "Target Group."  Set the "Target group
name" to `web`, set the "Protocol" to HTTP, set the "Port" to 80, and
set the "VPC" to your default [VPC].  Under "Health check settings,"
set the "Protocol" to HTTP and the "Path" to `/health_check`.  The
"health check" is the load balancer's way of telling whether a web
server is healthy.  The path `/health_check` on a **docassemble** web
server is a page that responds with a simple "OK."  (All the load
balancer cares about is whether the page returns an
[HTTP success code] or not.)  Under "Advanced health check settings,"
set the "Healthy threshold" to 10, "Unhealthy threshold" to 2,
"Timeout" to 10 seconds, "Interval" to 120 seconds, and keep other
settings at their defaults.  Then click "Create."

Once that "Target Group" is created, create a second "Target Group"
called `websocket` with the same settings.  Then, once the `websocket`
"Target Group" is created, do Actions -> Edit Attributes on it, and
under "Stickiness," select "Enable load balancer generated cookie
stickiness."  Keep other settings at their defaults.  Then click
"Create."

Finally, create a third "Target Group" called `http-redirect`.  The
purpose of this target group is very limited: it will forward any HTTP
requests to your HTTPS site.  Set the "Protocol" to HTTP, set the
"Port" to 8081, and set the "VPC" to your default [VPC].  Under
"Health check settings," set the "Protocol" to HTTP and the "Path" to
`/health_check`.  Under "Advanced health check settings," change
"Success codes" from 200 to 301.  This is because all requests to this
target group should respond with an [HTTP redirect] response, the code
for which is 301.  Then click "Create."

Then go to the "Load Balancers" section of the [EC2 Console] and
create a "Load Balancer."  Select "Application Load Balancer" as the
type of load balancer.

On the "Configure Load Balancer" page, set the name to
`docassembleLb`.  Under "Listeners," keep the HTTP listener listening
to port 80 and click "Add listener" to add a second listener.  Set the
"Load Balancer Protocol" to HTTPS and set the "Load Balancer Port" to
port 443.

Under "Availability Zones," make sure your default [VPC] is selected.
Then select all of the "available subnets" by clicking the plus buttons
next to each one.  (If it gives you any trouble about adding subnets,
just add as many subnets as it will let you add.)

On the "Configure Security Settings" page, it will ask about SSL
certificates and security policies.  Accept all of the defaults.  This
should result in [Amazon] creating an SSL certificate for you.

On the "Configure Security Groups" page, select the `docassembleLbSg`
[Security Group] you created earlier.

On the "Configure Routing" page, set "Target group" to "Existing
target group" and select `web` as the "Name" of the Target Group.

Skip past the "Register Targets" page.  On the "Review" page, click
"Create" to create the Load Balancer.

Once the `docassembleLb` load balancer is created, you need to make a
few manual changes to it.

In the "Load Balancers" section, select the `docassembleLb` load
balancer, and open the "Listeners" tab.  Click "Edit" next to the HTTP
listener.  Set the "Default target group" to "http-redirect."

Once those changes are saved, open up the HTTPS rule by clicking the
right arrow icon.  Click "Add rule."  For the "Path pattern," enter
`/ws/*`.  Under "Target group name," select `websocket`.  Keep
"Priority" as 1.  Then click "Save."

Now the `docassembleLb` load balancer will listen to 443 and act on
requests according to two "Rules."  The first rule says that if the
path of the HTTPS request starts with `/ws/`, which is
**docassemble**'s path for [WebSocket] communication, then the request
will be forwarded using the `websocket` "Target Group," which has the
"stickiness" feature enabled.  The second rule says that all other
traffic will use the `web` "Target Group," for which "stickiness" is
not enabled.

Finally, go to the "Description" tab for the `docassembleLb` load
balancer and make note of the "DNS name."  It will be something like
`docassemblelb-174526082.us-west-1.elb.amazonaws.com`.

Edit the [DNS] configuration of your domain and create a [CNAME] that
maps the [DNS] name that your users will use (e.g.,
`docassemble.example.com`) to the [DNS] name of the load balancer
(e.g., `docassemblelb-174526082.us-west-1.elb.amazonaws.com`).  This
will allow your users to connect to the load balancer.

Then go to the [ECS Console].

Create a [Task Definition] called `backend` using the [JSON]
configuration below.  Edit the [`TIMEZONE`], [`DAHOSTNAME`], and
[`S3BUCKET`] environment variables.

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
          "containerPort": 25,
          "hostPort": 25
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
      "essential": True,
      "environment": [
        {
          "name": "CONTAINERROLE",
          "value": "sql:redis:rabbitmq:log:cron"
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
          "name": "TIMEZONE",
          "value": "America/New_York"
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

The [`CONTAINERROLE`] variable indicates that this server will serve the
functions of SQL, [Redis], [RabbitMQ], and log message aggregation.
The [`DAHOSTNAME`] variable indicates the hostname at which the user
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
configuration below.  Edit the [`S3BUCKET`] environment variable.

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
          "containerPort": 8081,
          "hostPort": 8081
        },
        {
          "containerPort": 9001,
          "hostPort": 9001
        }
      ],
      "essential": True,
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

Create a Service called `app` that uses the task definition `app`.
Set the "Number of tasks" to 2.  Under "Elastic load balancing," click
the "Configure ELB" button.  Set "ELB type" to "Elastic Load
Balancer."  The "IAM role for service" should be `ecsServiceRole`, an
[IAM] role that [ECS] creates for you automatically.  Set "ELB Name"
to `docassembleLb`, the name of the [Application Load Balancer] you
created earlier.  Under "Container to load balance," select
"app:80:80" and click "Add to ELB."  Set the "Target group name" to
`web`, the "Target Group" you created earlier.  Then click "Save."

Just one more thing needs to be done to make the **docassemble**
server fully functional: you need to associate the `websocket` "Target
Group" with the same [EC2] instances that are associated with the
`web` "Target Group."  (Unfortunately, this is not something that the
[ECS] system can do automatically yet.)  To fix this, go to the
[EC2 Console], go to the "Target Groups" section, select the
`web` Target Group, go to the "Targets" tab, and note the Instance IDs
of the "Registered Instances."  Now de-select `web`, select
`websocket`, and click the "Edit" button within the "Targets" tab.  On
the "Register and deregister instances" page that appears, select the
instances you just noted and click the "Add to registered" button.

### Controlling AWS from the command line

In the **docassemble** [GitHub repository], there is a command-line
utility called [`da-cli`] (which is short for "**docassemble** command
line interface") that you can use to manage your multi-server
configuration on [AWS].

It depends on the [boto3] library, so you may need to run `sudo pip
install boto3` in order for it to work.  You need to initialize
[boto3] by running `aws configure`.

* `da-cli start_up 2` - bring up two `app` services and one `backend`
  service after bringing up three [EC2] instances with the
  `docassembleAsg` [Auto Scaling Group].  It also registers the
  appropriate instances for the `websocket` Target Group.
* `da-cli shut_down` - bring the count of the `app` and `backend`
  services down to zero, then bring the `docassembleAsg`
  [Auto Scaling Group] count down to zero.
* `da-cli shutdown_unused_ec2_instances` - finds [EC2] instances in
  the `docassembleAsg` [Auto Scaling Group] that are not being used to
  host a service, and terminates them.
* `da-cli update_ec2_instances 4` - increases the `docassembleAsg`
  [Auto Scaling Group] count to 4 and waits for the instances to
  become available.
* `da-cli connect_string app` - prints a command that you can use to
  SSH to each [EC2] instance running the service `app`.
* `da-cli fix_web_sockets` - registers target instances for the
  `websocket` Target Group.
* `da-cli update_desired_count app 4` - increases the desired count
  for the `app` service to 4.

If your [AWS] resources go by names different from those in the above
setup instructions, you can easily edit the `da-cli` script, which is
a simple [Python] module.  The things you can do in the [AWS] web
interface can be done using the [boto3] library.

# Single-server configuration on EC2 Container Service

You can use [EC2] to run **docassemble** in a single-server
arrangement.  (It is not particularly "scalable" to do so, but you
might find it convenient.)

To do so, start one [EC2] instance with an [ECS]-optimized [AMI], and
then go to the [ECS Console] and set up a "service" that runs a single
"task" with a [Task Definition] like the following.

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
      "essential": True,
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
          "name": "USELETSENCRYPT",
          "value": "true"
        },
        {
          "name": "LETSENCRYPTEMAIL",
          "value": "admin@example.com"
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

Edit [`DAHOSTNAME`], [`LETSENCRYPTEMAIL`], and [`S3BUCKET`].  Note
that [`CONTAINERROLE`] is not specified, but it will default to `all`.

# How it works

Each **docassemble** application server reads its [configuration] from
`/usr/share/docassemble/config.yml`.  The default configuration for
connecting to the central SQL database is:

{% highlight yaml %}
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: localhost
{% endhighlight %}

This will cause **docassemble** to connect to [PostgreSQL] on the
local machine as the user "docassemble" and open the database
"docassemble."  This configuration can be modified to connect to a
remote server.  If you use a remote SQL server that is not a [Docker]
container running the [`CONTAINERROLE`] `sql`, then you need to make
sure that you create the user and database first, and give permission
to the user to create tables in the database.

By default, the [Redis] server is assumed to be found at
`redis://localhost` and the [RabbitMQ] server at
`pyamqp://guest@your.hostname.local//`, where `your.hostname.local` is
the value of [`socket.gethostname()`].  However, you can modify the
locations of the [Redis] server and [RabbitMQ] server in the
[configuration] using the [`redis`] and [`rabbitmq`] directives:

{% highlight yaml %}
redis: redis://redis.example.local
rabbitmq: pyamqp://guest@rabbit.example.local//'
{% endhighlight %}

## Log file aggregation

In a multi-server configuration, log files can be centralized and
aggregated by using [Syslog-ng] on the application servers to forward
local log files to port 514 on a central server, which in turn runs
[Syslog-ng] to listen to port 514 and write what it hears to files in
`/usr/share/docassemble/log`.  The hostname of this central server is
set using the [`log server`] directive in the [configuration]:

{% highlight yaml %}
log server: log.example.local
{% endhighlight %}

If this directive is set, **docassemble** will write its own log
messages to port 514 on the central server rather than appending to
`/usr/share/docassemble/log/docassemble.log`.

When [`log server`] is set, the "Logs" page of the web interface will
call http://log.example.local:8080/ to get a list of available log
files, and will retrieve the content of files by accessing URLs like
http://log.example.local:8080/docassemble.log.

The following files make this possible:

* [`Docker/cgi-bin/index.sh`] - CGI script that should be copied to
  `/usr/lib/cgi-bin/`.
* [`Docker/config/docassemble-log.conf.dist`] - template for an
  [Apache] site configuration file that connects port 8080 to the
  `index.sh` CGI script above.
* [`Docker/docassemble-syslog-ng.conf`] - on application servers, this
  is copied into `/etc/syslog-ng/conf.d/docassemble`.  It depends on
  an environment variable `LOGSERVER` which should be set to the
  hostname of the central log server (e.g., `log.example.local`).  It
  causes log messages to be forwarded to port 514 on the central log
  server.  Note that [Syslog-ng] needs to run in an environment where
  the `LOGSERVER` environment variable is defined, or the file needs
  to be edited to include the hostname explicitly.
* [`Docker/syslog-ng.conf`] - on the central log server, this is
  copied to `/etc/syslog-ng/syslog-ng.conf`.  It causes [Syslog-ng] to
  listen to port 514 and copy messages to files in
  `/usr/share/docassemble/log/`.

## Auto-discovery of services

If you use [S3], you can can use **docassemble** in a multi-server
configuration without manually specifying the hostnames of central
services in the [configuration] file.

If any of the following [configuration] directives are `null` or
undefined, and [S3] is enabled, then a **docassemble** application
server will try to "autodiscover" the hostname of the service.

* [`host`] in the [`db`] section
* [`redis`]
* [`rabbitmq`]
* [`log server`]

**docassemble** will look for keys in the [S3 bucket] called:

* `hostname-sql`
* `hostname-redis`
* `hostname-rabbitmq`
* `hostname-log`

If a key is defined, **docassemble** will assume that the value is a
hostname, and will set the corresponding [configuration] variable
appropriately (e.g., by adding a `redis://` prefix to the [Redis]
hostname).

The [Docker] initialization script runs the
[`docassemble.webapp.s3register`] module, which writes the hostname to
the appropriate [S3] keys depending on the value of the environment
variable `CONTAINERROLE`.

## File sharing

Configuring a cluster of **docassemble** servers requires centralizing
the location of uploaded files, either by using an [Amazon S3] bucket
(the [`s3` configuration setting]) or by making the uploaded file
directory a network drive mount (the [`uploads`] configuration
setting).

For more information about using [S3] for file sharing, see the
[file sharing] and [data storage] sections of the [Docker] page.

The default location of uploaded user files is defined by the
`uploads` [configuration] setting:

{% highlight yaml %}
uploads: /usr/share/docassemble/files
{% endhighlight %}

However, **docassemble** will use [Amazon S3] instead of this folder
if [S3] is enabled as follows:

{% highlight yaml %}
s3:
  enable: True
  access_key_id: FWIEJFIJIDGISEJFWOEF
  secret_access_key: RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
  bucket: yourbucketname
{% endhighlight %}

When developers install new Python packages, the packages are unpacked
in `/usr/share/docassemble/local` (controlled by [configuration]
variable [`packages`]).

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
ec2: True
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
  port: Null
  table_prefix: Null
{% endhighlight %}

If you installed the web servers before installing the SQL server,
note that the [`create_tables`] module will need to be run in order to
create the database tables that **docassemble** expects.

# Mail server

If you are launching **docassemble** within [EC2], note that Amazon does
not allow e-mail to be sent from [SMTP] servers operating within an [EC2]
instance, unless you obtain special permission.  Therefore, you may
wish to use an [SMTP] server on the internet with which you can connect
through [SMTP Authentication]. 

If you have a Google account, you can use Google's [SMTP] server by
setting the following in your [configuration]:

{% highlight yaml %}
mail:
  server: smtp.gmail.com
  username: yourgoogleusername
  password: yourgooglepassword
  use_ssl: True
  port: 465
  default_sender: '"Administrator" <no-reply@example.com>'
{% endhighlight %}

Note that for this to work, you will need to go into your Google
settings and set "Allow less secure apps" to "ON."

You can also use the [Amazon SES] service to send e-mail.  When you
set it up, you will be given a username, password, and server.  In the
**docassemble** configuration, you would write something like this:

{% highlight yaml %}
mail:
  username: WJYAKIBAJVIFYAETTC3G
  password: At6Cz2BH8Tx1zqPp0j3XhzlhbRnYsmBx7WwoItL9N5GU
  server: email-smtp.us-east-1.amazonaws.com
  default_sender: '"Example Inc." <no-reply@example.com>'
{% endhighlight %}

In order to send e-mail through [Amazon SES], you will need to verify
your domain.  Among other things, this involves editing your [DNS]
configuration to add a [TXT record] for the host `_amazonses`.

To ensure that e-mails from your application are not blocked by spam
filters, you should also add a [TXT record] with [SPF] information for
your domain, indicating that [Amazon SES] is authorized to send e-mail
for your domain:

{% highlight text %}
v=spf1 mx include:amazonses.com ~all
{% endhighlight %}

# Using S3 without passing access keys in the configuration

If you are running **docassemble** on an [EC2] instance, or on a
[Docker] container within an [EC2] instance, you can set up the
instance with an [IAM role] that allows access [S3] without supplying
credentials.  In this case, the configuration in **docassemble** does
not include an `access_key_id` or a `secret_access_key`.

{% highlight yaml %}
s3:
  enable: True
  bucket: yourbucketname
{% endhighlight %}

# Performance

With one central server and two application servers, all three of
which are [t2.micro] instances running on [Amazon Web Services],
**docassemble** can handle 100 concurrent requests without errors or
significant slowdown:

{% highlight text %}
Server Software:        Apache/2.4.10
Server Hostname:        test.docassemble.org
Server Port:            443
SSL/TLS Protocol:       TLSv1.2,ECDHE-RSA-AES128-GCM-SHA256,2048,128

Document Path:          /
Document Length:        44602 bytes

Concurrency Level:      100
Time taken for tests:   14.606 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      44932939 bytes
HTML transferred:       44602000 bytes
Requests per second:    68.47 [#/sec] (mean)
Time per request:       1460.582 [ms] (mean)
Time per request:       14.606 [ms] (mean, across all concurrent requests)
Transfer rate:          3004.27 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:      231  257  29.4    245     402
Processing:   408 1109 149.4   1109    1671
Waiting:      255 1017 150.1   1018    1574
Total:        650 1366 160.6   1361    2073

Percentage of the requests served within a certain time (ms)
  50%   1361
  66%   1396
  75%   1425
  80%   1449
  90%   1513
  95%   1640
  98%   1806
  99%   1928
 100%   2073 (longest request)
{% endhighlight %}

# PostgreSQL concurrency

You can expect each application server to maintain 11 concurrent
connections to PostgreSQL:

* 5 connections for the web server
* 5 connections for the [WebSocket] server
* 1 connnection for the [Celery] server

This assumes that the server has one CPU.  The [Celery] server will
start one process per CPU.  So if the server has two CPUs, the total
number of PostgreSQL connections will be 12.

[t2.micro]: https://aws.amazon.com/ec2/instance-types/t2/
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
[background processes]: {{ site.baseurl }}/docs/background.html#background
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
[EC2 Console]: https://console.aws.amazon.com/ec2/home
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
[WebSocket]: https://en.wikipedia.org/wiki/WebSocket
[`CONTAINERROLE`]: #CONTAINERROLE
[`S3BUCKET`]: #S3BUCKET
[HTTP success code]: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes#2xx_Success
[GitHub repository]: {{ site.github.repository_url }}
[boto3]: https://boto3.readthedocs.io/en/latest/
[`da-cli`]: {{ site.github.repository_url }}/blob/master/da-cli
[`socket.gethostname()`]: https://docs.python.org/2/library/socket.html#socket.gethostname
[Syslog-ng]: https://en.wikipedia.org/wiki/Syslog-ng
[`rabbitmq`]: {{ site.baseurl }}/docs/config.html#rabbitmq
[`redis`]: {{ site.baseurl }}/docs/config.html#redis
[`packages`]: {{ site.baseurl }}/docs/config.html#packages
[`uploads`]: {{ site.baseurl }}/docs/config.html#uploads
[`s3` configuration setting]: {{ site.baseurl }}/docs/config.html#s3
[`Docker/config/docassemble-log.conf.dist`]: {{ site.github.repository_url }}/blob/master/Docker/config/docassemble-log.conf.dist
[`Docker/docassemble-syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/docassemble-syslog-ng.conf
[`Docker/syslog-ng.conf`]: {{ site.github.repository_url }}/blob/master/Docker/syslog-ng.conf
[`Docker/cgi-bin/index.sh`]: {{ site.github.repository_url }}/blob/master/Docker/cgi-bin/index.sh
[file sharing]: {{ site.baseurl }}/docs/docker.html#file sharing
[data storage]: {{ site.baseurl }}/docs/docker.html#data storage
[TXT record]: https://en.wikipedia.org/wiki/TXT_record
[SPF]: https://en.wikipedia.org/wiki/Sender_Policy_Framework
[HTTP redirect]: https://en.wikipedia.org/wiki/HTTP_301
[CIDR]: https://en.wikipedia.org/wiki/Classless_Inter-Domain_Routing
[HTTP]: https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
[`TIMEZONE`]: {{ site.baseurl }}/docs/docker.html#TIMEZONE
[`DAHOSTNAME`]: {{ site.baseurl }}/docs/docker.html#DAHOSTNAME
[`LETSENCRYPTEMAIL`]: {{ site.baseurl }}/docs/docker.html#LETSENCRYPTEMAIL
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[PostgreSQL]: http://www.postgresql.org/
[`docassemble.webapp.s3register`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/s3register.py
[S3 bucket]: http://docs.aws.amazon.com/AmazonS3/latest/dev/UsingBucket.html
[`log server`]: {{ site.baseurl }}/docs/config.html#log server
[`db`]: {{ site.baseurl }}/docs/config.html#db
[`host`]: {{ site.baseurl }}/docs/config.html#db host
[SMTP]: https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol

