* Integrate with Bluemix

* INDENTBY block
\begingroup\setlength{\leftskip}{2in} \noindent content \par\endgroup

* Integrate with Tyler
https://www.tylertech.com/contact-us

I have developed free open-source software, https://docassemble.org, designed to help low-income people prepare court pleadings.  The application produces PDF files.  I would like to incorporate e-filing into the application using Tyler's e-filing API.

I was wondering if Tyler could set me up with an account on a dummy e-filing system so that I could test the API.  I am also interested in any documentation about the API.

I can be reached at 215-391-9686.

I work at an LSC-funded legal services organization and I am involved
with LSC's Technology Initiative Grants program

* Ajax for updating on POST - things that would change:
    * Integrate signature code into regular page
    * html tag, lang property updating with Javascript
    * head > title tag updating with Javascript
    * move jQuery ready functions into a separate function that is
      triggered both by ready and by Javascript after $("#body")
      replaced.
    * add validation code in standardformatter, make it run dynamically.
    * signature.js code available all the time without interfering with Bootstrap
    * extra_scripts executed with eval
    * extra_css updating with Javascript
    * fileinput.min.js code available all the time
    * loading of async defer Google Maps script with Javascript
    * geolocation code daSetPosition and daShowError available all the
      time
    * submithandler on validation errors should be defined in advance
    * redirects
* SMTP
    * server: email-smtp.us-east-1.amazonaws.com
    * username: AKIAJWJYC3GIVEBTTFYA
    * password: At2XhbB61zqPCzH8TsmBx7Wwoxp0j3RnYItL9hzlN5GU
    * SMTP Username: AKIAJ33MABXZAKZ5MK5Q
    * SMTP Password: Al9+8i1+E+TRXkDilYyzV0FZckh5JmitR8megAjf7nBI
perl -MMIME::Base64 -e 'print encode_base64("\000AKIAJ33MABXZAKZ5MK5Q\000Al9+8i1+E+TRXkDilYyzV0FZckh5JmitR8megAjf7nBI")' 

EHLO email-smtp.us-east-1.amazonaws.com
AUTH PLAIN AEFLSUFKMzNNQUJYWkFLWjVNSzVRAEFsOSs4aTErRStUUlhrRGlsWXl6VjBGWmNraDVKbWl0UjhtZWdBamY3bkJJ

RUN apt-get -q -y build-dep pacpl && apt-get -q -y remove pacpl
RUN cd /tmp && git clone git://git.code.sf.net/p/pacpl/code pacpl-code
&& cd pacpl-code && ( ./configure || true ) && ( make || ( make clean && ( ./configure || true ) && make ) && make install ) && cd ..
docker cloud API key: jhpyle 9651eba4-cdd8-448b-8cec-b052f9f654f7

Advocate side:

* Javascript variables
    * daAvailableForChat (boolean)
    * daPartnerChatRoles (array)
    * daFirstTime
* Advocate logs into monitor - initial page load
    * daFirstTime = 1
    * if 'da:monitor:available:<user_id>' exists:
        * daAvailableForChat = true
    * else:
        * daAvailableForChat = false
    * on load, call update_monitor, callback draws screen
* Advocate clicks "available for new conversations"
    * set daAvailableForChat = true
    * call update_monitor()
* Advocate clicks "not available for new conversations"
    * set daAvailableForChat = false
    * call update_monitor()
* Advocate clicks button to end a chat session
    * publish 'chatdisconnect' to the individual chat channel
    * redis delete 'da:chatpresence:uid:<uid>:i:<i>:userid:*:participant:<user_id>'
* Advocate websocket
    * on connect
    * on disconnect
        * publish 'chatdisconnect' to 'monitor'
        * redis delete 'da:monitor:available:<user_id>'
        * redis delete 'da:monitor:role:*:userid:<user_id>'
    * if 'updatemonitor' comes in
        * obtain list of active chats
            * search redis for
              'da:chatpresence:uid:<uid>:i:<i>:userid:*:participant:<user_id>'
            * for each,
                * obtain information about how to access chat history
                 by doing redis get 'da:session:uid:<uid>:i:<i>:userid:<user_id>'
                * obtain the chat history
        * if daAvailableForChat is true
            * redis set 'da:monitor:available:<user_id>' = 1 with expire in 60 seconds
            * For each role in keys of 'da:monitor:userrole:<user_id>':
                * redis set 'da:monitor:role:<role>:userid:<user_id>' =
                user_id with expire in 60 seconds
        * if daAvailableForChat is false and 'da:monitor:available:<user_id>' exists:
            * redis delete 'da:monitor:available:<user_id>'
            * redis delete 'da:monitor:role:*:userid:<user_id>'
        * obtain list of possible partner roles based on search for 'da:chat:roletype:*'
        * retrieve list of subscribed roles from hkeys of
          'da:monitor:userrole:<user_id>'
        * if any of the keys is not among daPartnerChatRoles, hdel it
        * if any of daPartnerChatRoles are not among the keys, hset
          the key in 'da:monitor:userrole:<user_id>'
        * if 'da:monitor:userrole:<user_id>' exists, update its expire
          time to 30 days
        * return
            * dict of possible partner roles indicating which ones are
              subscribed
            * list of sessions
                * redis search for 'da:session:*'
                * for those where chatstatus is 'waiting', display the
                  partner roles sought
                * for those that are active, provide chat history
    * if 'chatmessage' comes in
        * pub it to the designated sid

* Advocate's websocket background thread
    * Listens to redis 'monitor'
    * If 'chatdisconnect' message comes in
        * if sid of sender matches sid of listener
            * if channel is 'monitor'
                * publish 'chatdisconnect' to each sid channel
                * break loop
            * else
                * unsubscribe from channel
    * If 'newchatpartner' message comes in
        * ignore it
    * If 'chatready' message comes in
        * Ignore if target sid does not match
        * Call pubsub.subscribe([sid])
        * redis set 'da:chatpresence:uid:<uid>:i:<i>:userid:<user_id>:participant:<mon_user_id>' to 1
          with expire 60 minutes
        * Publish 'newchatpartner' message to this channel
        * Send 'newchatpartner' message to socket client, containing
          uid, i, secret
            * The client saves the secret in memory in array with
              uid as the key
            * The client then creates a chat box for the uid
    * If 'chatmessage' comes in
        * usersid is message 'channel'
        * set expire on
          'da:chatpresence:uid:<uid>:i:<i>:userid:<user_id>:participant:<mon_user_id>' to
          60 minutes
        * send 'chatmessage' to client, which puts it on the screen
* on interval of five seconds, send 'updatemonitor' message with
  values of javascript variables.  On callback:
    * redraw the list of chat roles
    * if session is already on the screen, update
    * otherwise, append

Client side:

* Long poll
    * user_id is 't' + temp_user_id or just user_id
    * key is 'da:session:uid:<uid>:i:<i>:userid:<user_id>' and value
      is dict.
    * key expires in 60 seconds
    * expiration of 'da:html:uid:<uid>:i:<i>:userid:<user_id>' is update
      to 60 seconds
    * If chatstatus is 'waiting' or 'standby', dict contains info for accessing interview
    * If chatstatus is 'ringing,' 'waiting' or 'standby', search redis for chat partner
        * If mode is help
            * For each partner role
                * update redis key 'da:chat:role:<role>' with expire in 30 days
                * search redis for 'da:monitor:role:<role>:userid:*'
                * if a key is found and value is not current user id:
                    * extract the partner user_id from
                      'da:monitor:role:<role>:userid:<user_id>'
        * If partner found
            * If status is 'waiting'
                * on return, set status to 'standby' and indicate who
                  is available to chat
            * If status is 'standby'
                * return with status unchanged
            * If status is 'ringing'
                * return with instructions to call daTurnOnChat, along
                  with with the partner sid
        * If partner not found
            * If status is 'standby' or 'ringing'
                * on return, set status to 'waiting'
* UI
    * Call daTurnOffChat if user closes chat
    * If user is open to chatting with other users, add 'peer' to own
      role and 'peer' to partner role.

* User's websocket
    * background task
        * If 'chatdisconnect' message comes in
            * search redis for
              'da:chatpresence:uid:<uid>:i:<i>:userid:<user_id>:participant:*'
              and count results
            * emit 'chatdisconnect' message to client with number of
              remaining chat partners
        * If 'newchatpartner' message comes in
            * emit 'newchatpartner' message to client
        * If 'chatmessage' message comes in
            * search 'da:chatpresence:uid:<uid>:i:<i>:userid:<user_id>:participant:*'
            * if nothing, emit 'chatdisconnect' message to client with number of
              remaining chat partners
    * On connect
        * get info from 'da:session:uid:<uid>:i:<i>:userid:<user_id>'
        * redis set 'da:chatsession:uid:<uid>:i:<i>:userid:<user_id>'
        * join room sid
        * pub into 'monitor' with a 'chatready' message targeting the
          partner sid
    * On disconnect
        * redis delete 'da:chatsession:uid:<uid>:i:<i>:userid:<user_id>:*'
        * publish 'chatdisconnect' message to sid
* User's browser web socket
    * On 'newchatpartner' message
        * if daChatActive is false
            * show box allowing user to send chat message
    * On ''
* chat status
    * off: user will not see any evidence of chat
    * waiting: user will see chat history.  System will check during
      long poll if someone is available to chat.
    * standby: indicates that someone is available to chat.  User is
      offered the opportunity to turn on chat
    * ringing: user has turned on chat, but nobody has connected yet.
    * on: a user has connected into chat
* chat availability
    * unavailable: no chat
    * available: any user can choose to turn on chat
* chat modes:
    * help: single user with advocate(s)
    * peerhelp: all users with advocate(s)
    * peer: all users
* For each interview, there is a single internal dictionary that
  specifies:
    * chat availability
    * chat mode
    * partner roles for help
* In the browser:
    * daChatAvailable
    * daChatMode
    * daChatStatus
* user-side process
    * if availability is "unavailable"
        * if chat status is "on"
            * hide chat box
            * hide button
            * turn off the web socket
            * turn on the long poll
        * if chat status is "ringing" or "standby"
            * hide chat box
            * hide button
            * clear the checkin interval and set it again
        * set status to "off"
    * during daInitialize
        * if chat status is not "off" and there is chat history, show it.
        * if chat status is "on"
            * call daTurnOnChat()
    * if status is waiting, check to see if someone is available,
      depending on the chat mode and partner roles
        * if someone is available
            * offer the "turn on chat" button
            * set status to standby
            * if user clicks "turn on chat"
                * change button to "turn off chat"
                * clear the checkin interval
                * set status to ringing
                * immediately call checkin
                * appropriate people are notified
                * if people still available
                    * during callback, call daStartChat
                        * this sets status to "on"
                        * turn on the websocket
                * if people not available
                    * set status to standby
                    * change button back to "turn on chat"
                    * turn on the long poll
            * if user clicks "turn off chat"
                * set status to standby
                * hide chat box, offer "turn on chat" button
                * turn off the web socket
                * turn on the long poll

# Example docker run command

{% highlight bash %}
docker run \
-e CONTAINERROLE=sql:log:redis:rabbitmq \
-e S3BUCKET=hosted-docassemble-org \
-v pgetc:/etc/postgresql \
-v pglog:/var/log/postgresql \
-v pglib:/var/lib/postgresql \
-v pgrun:/var/run/postgresql \
-v dalog:/usr/share/docassemble/log \
-v daconfig:/usr/share/docassemble/config \
-v dabackup:/usr/share/docassemble/backup \
-p 9001:9001 -p 5432:5432 -p 514:514 -p 6379:6379 \
-p 4369:4369 -p 5671:5671 -p 5672:5672 -p 25672:25672  \
-d jhpyle/docassemble
{% endhighlight %}

{% highlight bash %}
docker run \
-e CONTAINERROLE=web:celery \
-e S3BUCKET=hosted-docassemble-org \
-v dafiles:/usr/share/docassemble/files \
-v certs:/usr/share/docassemble/certs \
-v daconfig:/usr/share/docassemble/config \
-v dabackup:/usr/share/docassemble/backup \
-v letsencrypt:/etc/letsencrypt \
-v apache:/etc/apache2/sites-available \
-p 80:80 -p 443:443 -p 9001:9001 \
-d jhpyle/docassemble
{% endhighlight %}

{% highlight bash %}
docker run \
-e CONTAINERROLE=all \
-e S3BUCKET=hosted-docassemble-org \
-v pgetc:/etc/postgresql \
-v pglog:/var/log/postgresql \
-v pglib:/var/lib/postgresql \
-v pgrun:/var/run/postgresql \
-v dalog:/usr/share/docassemble/log \
-v dafiles:/usr/share/docassemble/files \
-v certs:/usr/share/docassemble/certs \
-v daconfig:/usr/share/docassemble/config \
-v dabackup:/usr/share/docassemble/backup \
-v letsencrypt:/etc/letsencrypt \
-v apache:/etc/apache2/sites-available \
-d -p 80:80 -p 443:443 \
jhpyle/testdocassemble
{% endhighlight %}


{% highlight bash %}
docker run \
-e CONTAINERROLE=all \
-e USEHTTPS=true \
-e DAHOSTNAME=hosted.docassemble.org \
-e USELETSENCRYPT=true \
-e LETSENCRYPTEMAIL=jhpyle@gmail.com \
-e S3ENABLE=true \
-e S3BUCKET=hosted-docassemble-org \
-e EC2=true \
-e TIMEZONE=America/New_York \
-v pgetc:/etc/postgresql \
-v pglog:/var/log/postgresql \
-v pglib:/var/lib/postgresql \
-v pgrun:/var/run/postgresql \
-v dalog:/usr/share/docassemble/log \
-v dafiles:/usr/share/docassemble/files \
-v certs:/usr/share/docassemble/certs \
-v daconfig:/usr/share/docassemble/config \
-v dabackup:/usr/share/docassemble/backup \
-v letsencrypt:/etc/letsencrypt \
-v apache:/etc/apache2/sites-available \
-d -p 80:80 -p 443:443 -p 9001:9001 \
jhpyle/docassemble
{% endhighlight %}

{% highlight bash %}
sudo yum -y update
sudo yum -y install git screen
cat > ~/.screenrc
escape ^Tt
startup_message off

git clone https://github.com/jhpyle/docassemble
cd docassemble
git checkout testing
git pull
screen
docker build -t jhpyle/mydocassemble .
cd ..
docker run \
-e USEHTTPS=true \
-e DAHOSTNAME=test5.docassemble.org \
-e USELETSENCRYPT=true \
-e LETSENCRYPTEMAIL=jhpyle@gmail.com \
-e S3ENABLE=true \
-e S3BUCKET=test5-docassemble-org \
-e EC2=true \
-e TIMEZONE=America/New_York \
-d -p 80:80 -p 443:443 \
jhpyle/docassemble
{% endhighlight %}

docker run \
-e S3BUCKET=dev-docassemble-org \
-d -p 80:80 -p 443:443 \
jhpyle/docassemble

docker run \
-e CONTAINERROLE=sql:log:redis:rabbitmq \
-e S3BUCKET=hosted-docassemble-org \
-d -p 80:8080 -p 5432:5432 -p 514:514 \
-p 6379:6379 -p 4369:4369 -p 5671:5671 \
-p 5672:5672 -p 25672:25672 -p 9001:9001 \
jhpyle/docassemble

docker run \
-e CONTAINERROLE=web:celery \
-e S3BUCKET=hosted-docassemble-org \
-d -p 80:80 -p 443:443 -p 9001:9001 \
jhpyle/docassemble


[
('FromZip', u'19406'),
('From', u'+12153919686'),
('SmsMessageSid', u'SM91c2e48095d1d1909852d2e1fcfebbfb'),
('FromCity', u'KING OF PRUSSIA'),
('ApiVersion', u'2010-04-01'),
('To', u'+12672140104'),
('NumMedia', u'0'),
('NumSegments', u'1'),
('AccountSid', u'ACfad8e668b5f9e15d499ab823523b9358'),
('SmsSid', u'SM91c2e48095d1d1909852d2e1fcfebbfb'),
('ToCity', u''),
('FromState', u'PA'),
('FromCountry', u'US'),
('Body', u'Hello!'),
('MessageSid', u'SM91c2e48095d1d1909852d2e1fcfebbfb'),
('SmsStatus', u'received'),
('ToZip', u''),
('ToCountry', u'US'),
('ToState', u'PA')]


('FromZip', u'19145'),
('From', u'+12157404796'),
('SmsMessageSid', u'MMc17581302aae77027e920ba94922db0c'),
('FromCity', u'PHILADELPHIA'),
('ApiVersion', u'2010-04-01'),
('To', u'+12672140104'),
('MediaUrl0', u'https://api.twilio.com/2010-04-01/Accounts/ACfad8e668b5f9e15d499ab823523b9358/Messages/MMc17581302aae77027e920ba94922db0c/Media/MEf3733c53d9beb89668982e40507fe9ff'),
('NumSegments', u'1'),
('MediaContentType0', u'image/jpeg'),
('AccountSid', u'ACfad8e668b5f9e15d499ab823523b9358'),
('SmsSid', u'MMc17581302aae77027e920ba94922db0c'),
('ToCity', u''),
('FromState', u'PA'),
('ToState', u'PA'),
('Body', u''),
('MessageSid', u'MMc17581302aae77027e920ba94922db0c'),
('SmsStatus', u'received'),
('FromCountry', u'US'),
('ToZip', u''),
('ToCountry', u'US'),
('NumMedia', u'1')


aws ec2 run-instances --image-id ami-7abc111a --count 1 --instance-type t2.micro --key-name oregon --security-group-ids sg-8ac5f7ee --subnet-id subnet-ef41458a --block-device-mappings "[{\"DeviceName\":\"/dev/xvdcz\",\"Ebs\":{\"VolumeSize\":22,\"DeleteOnTermination\":true}}]" --iam-instance-profile Name=ecsInstanceRole

aws ec2 create-tags --resources i- --tags Key=Name,Value=test5

aws ec2 describe-instances --instance-ids i-

ec2-54-147-228-212.compute-1.amazonaws.com

aws ec2 describe-network-interfaces --filters association.public-dns-name

aws ecs start-task --task-definition docassemble-backend --container-instances "308e39e5-fe2e-410f-b9cf-a998ed848b51"

Do you need a security group to allow access within a subnet? Yes.

aws autoscaling update-auto-scaling-group --auto-scaling-group-name daapp --desired-capacity 3

aws ecs update-service --service backend --desired-count 1

aws ecs update-service --service daapp --desired-count 2


aws ecs update-service --service daapp --desired-count 0

aws ecs update-service --service backend --desired-count 0

aws autoscaling update-auto-scaling-group --auto-scaling-group-name daapp --desired-capacity 0

aws ec2 describe-vpcs

Get the CidrBlock


ses-smtp-user.20161126-113411
SMTP Username:
AKIAIHQGROREAN33QFNQ
SMTP Password:
AuJB8N1TkO+U/9T22GZyQXsodTYHqzRov+7MVAb1SuPi

perl -MMIME::Base64 -e 'print encode_base64("\000AKIAJWJYC3GIVEBTTFYA\000At2XhbB61zqPCzH8TsmBx7Wwoxp0j3RnYItL9hzlN5GU")'

openssl s_client -starttls smtp -crlf -connect email-smtp.us-east-1.amazonaws.com:25

EHLO testing
AUTH PLAIN AEFLSUFKV0pZQzNHSVZFQlRURllBAEF0MlhoYkI2MXpxUEN6SDhUc21CeDdXd294cDBqM1JuWUl0TDloemxONUdV

CloudFormation stack:
arn:aws:cloudformation:us-east-1:805858324670:stack/EC2ContainerService-default/02e2bf30-b41b-11e6-a4c2-500c28688861

Internet Gateway:
igw-7d0a8c1a

VPC:
vpc-f8a45c9e

Route Table:
rtb-37042c51

VPC Attached Gateway:
EC2Co-Attac-BSA6J2VCGQ3S

Subnet 1:
subnet-085ce353

ELB Security Group:
sg-33ed744e

Subnet 2:
subnet-73fc254f

Public Routing:
EC2Co-Publi-1A66T3O9HOO65

ECS Security Group:
sg-28ed7455

Subnet 2 association:
rtbassoc-bf90a2c6

Auto Scaling Group:
EC2ContainerService-default-EcsInstanceAsg-LYOCQQXIFG8

Launch Configuration:
EC2ContainerService-default-EcsInstanceLcWithoutKeyPair-ORTPM89CGJTV

# Multi-server arrangement

To run **docassemble** in a [multi-server arrangement] using [Docker],
you need to:

1. Start a container that will provide the SQL server;
2. Start a container that will provide the log server;
3. Start one or more other containers that will handle the
**docassemble** application and web server.

These containers can be on separate hosts.

The containers need to have a way to share files with one another.
The best way to do this is with [Amazon S3].  Before proceeding, go to
[Amazon S3] and obtain an access key and a secret access key.  Then
create a bucket and remember the name of the bucket.

First, go to the machine that will host the SQL server.  To start the
SQL server, do:

{% highlight bash %}
docker run -d -p 5432:5432 jhpyle/docassemble-sql
{% endhighlight %}

Note the IP address or hostname of the [Docker] host on the local
network.  You will need to feed this address, and other information,
to the [Docker] container that responds to web requests.

Now go to the machine that will run your log server (if different).
To start the log server, do:

{% highlight bash %}
docker run -d -p 514:514 -p 8080:80 jhpyle/docassemble-log
{% endhighlight %}

Note the IP address or hostname of this server as well.

Now go to the machine that will run your application server (if different).

Plug the IP addresses or hostnames for the SQL server and log server
into a file called `env.list`, along with your [S3] information:

{% highlight text %}
CONTAINERROLE=webserver
DBNAME=docassemble
DBUSER=docassemble
DBPASSWORD=abc123
DBHOST=192.168.0.56
USEHTTPS=false
DAHOSTNAME=host.example.com
USELETSENCRYPT=false
LETSENCRYPTEMAIL=admin@admin.com
S3ENABLE=true
S3ACCESSKEY=FWIEJFIJIDGISEJFWOEF
S3SECRETACCESSKEY=RGERG34eeeg3agwetTR0+wewWAWEFererNRERERG
S3BUCKET=yourbucketname
EC2=false
TIMEZONE=America/New_York
LOGSERVER=192.168.0.57
{% endhighlight %}

The address for the SQL server is `DBHOST`.  The address for the log
server is `LOGSERVER`.

Then start the application server:

{% highlight bash %}
docker run --env-file=env.list -d -p 80:80 -p 443:443 -p 9001:9001 jhpyle/docassemble
{% endhighlight %}

You can start multiple application servers in this way.

Port 9001 is opened so that application servers can coordinate with
one another.  For example, if one of the servers updates the
configuration, it can send a message to all of the other servers,
instructing them to retrieve the new configuration.

See [scalability of docassemble] for more information about running
**docassemble** in a multi-server arrangement.

If you do not have the s3cmd utility, install it:

{% highlight bash %}
apt-get install s3cmd
{% endhighlight %}

{% highlight bash %}
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.crt s3://yourbucket/certs/docassemble.crt
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.key s3://yourbucket/certs/docassemble.key
s3cmd --access_key=YOURACCESSKEY --secret_key=YOURSECRETKEY put yourserver.ca.pem s3://yourbucket/certs/docassemble.ca.pem
{% endhighlight %}

# Prerequisites

Make sure you have at least 12GB of storage space.  (**docassemble**
has a lot of large dependencies.)  At the end of installation, only
about 4GB will be taken up, but the build and installation processes
require more storage than that to be available.

# Without using EC2 Container Service

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

If you are using a [multi-server arrangement], the [WSGI] file needs to be
stored on a central network drive.  When a package is updated, all
servers need to reset, not just the server that happened to process
the package update.

---

http://pydoc.net/Python/Flask-User/0.6.7/flask_user.tests.tst_app/

2016-11-30 13:35:22 UTC [171-1] LOG:  checkpoints are occurring too frequently (
1 second apart)
2016-11-30 13:35:22 UTC [171-2] HINT:  Consider increasing the configuration par
ameter "checkpoint_segments".

celeryconfig:
from docassemble.base.config import daconfig

task_serializer='pickle'
accept_content=['pickle', 'json']
result_serializer='pickle'
timezone=daconfig.get('timezone', 'America/New_York')
enable_utc=True

* flask_user still using Form; might have to not import RegisterForm

2016-12-06 03:05:04 UTC [169-1] LOG:  database system was shut down at 2016-12-06 02:00:35 UTC
2016-12-06 03:05:04 UTC [169-2] LOG:  MultiXact member wraparound protections are now enabled
2016-12-06 03:05:04 UTC [168-1] LOG:  database system is ready to accept connections
2016-12-06 03:05:04 UTC [173-1] LOG:  autovacuum launcher started
2016-12-06 03:05:35 UTC [219-1] postgres@postgres ERROR:  database "docassemble" does not exist
2016-12-06 03:05:35 UTC [219-2] postgres@postgres STATEMENT:  DROP DATABASE docassemble;
2016-12-06 03:05:37 UTC [170-1] LOG:  checkpoints are occurring too frequently (2 seconds apart)
2016-12-06 03:05:37 UTC [170-2] HINT:  Consider increasing the configuration parameter "checkpoint_segments".
2016-12-06 03:09:31 UTC [634-1] docassemble@docassemble LOG:  could not receive data from client: Connection reset by peer
2016-12-06 03:34:53 UTC [1096-1] docassemble@docassemble LOG:  could not receive data from client: Connection reset by peer

select client_addr, count(datid) from pg_stat_activity where usename='docassemble' group by client_addr order by client_addr;

removed from docassemble_webapp/docassemble.wsgi

os.environ["XDG_CACHE_HOME"] = docassemble.base.config.daconfig.get('packagecache', "/tmp/docassemble-cache")
#os.environ["PYTHONUSERBASE"] = docassemble.base.config.daconfig.get('packages', "/usr/share/docassemble/local")
#site.addusersitepackages("") 

old Docker/docassemble.wsgi:

import os, site
import docassemble.base.config
docassemble.base.config.load(filename="/usr/share/docassemble/config/config.yml")
os.environ["PYTHONUSERBASE"] = docassemble.base.config.daconfig.get('packages', "/usr/share/docassemble/local")
os.environ["XDG_CACHE_HOME"] = docassemble.base.config.daconfig.get('packagecache', "/var/www/.cache")
site.addusersitepackages("") 
from docassemble.webapp.server import app as application

# Configuration default values

{% highlight yaml %}
debug: false
root: /
exitpage: /
db:
  prefix: postgresql+psycopg2://
  name: docassemble
  user: docassemble
  password: abc123
  host: localhost
  port: 5432
  table_prefix: none
  schema_file: /usr/share/docassemble/config/db-schema.txt
appname: docassemble
brandname: docassemble
default_title: docassemble
default_short_title: docassemble
uploads: /usr/share/docassemble/files
packages: /usr/share/docassemble/local
packagecache: /usr/share/docassemble/cache
webapp: /usr/share/docassemble/docassemble.wsgi
mail:
  default_sender: None
  username: none
  password: none
  server: localhost
  port: 25
  use_ssl: false
  use_tls: true
use_progress_bar: false
default_interview: docassemble.demo:data/questions/questions.yml
flask_log: /tmp/flask.log
language: en
dialect: us
locale: US.utf8
default_admin_account:
  nickname: admin
  email: admin@admin.com
  password: password
secretkey: 38ihfiFehfoU34mcq_4clirglw3g4o87
png_resolution: 300
png_screen_resolution: 72
show_login: true
xsendfile: true
log: /usr/share/docassemble/log
ec2: false
ec2_ip_url: http://169.254.169.254/latest/meta-data/local-ipv4
interview_delete_days: 90
{% endhighlight %}

The key `config_file` does not appear in the configuration file, but
it will be set to the file path for the configuration file.  (The
function `docassemble.webapp.config.load` sets it.)

## <a name="packagecache"></a>packagecache

When [pip] runs, it needs a directory for caching files.  [pip] uses
the value of the XDG_CACHE_HOME environment variable, or `~/.cache`.

**docassemble** sets XDG_CACHE_HOME to the value of the `packagecache`
directory, or `/var/www/.cache` if `packagecache` is not

{% highlight yaml %}
packagecache: /tmp/package_cache
{% endhighlight %}

On Mac and Windows, make sure that the web server user has a home
directory to which [pip] can write.  (See [pip/utils/appdirs.py].)

removed from config:

admin_address: '"Administrator" <admin@example.com>'

* config: This site appears to use a scroll-linked positioning effect. This may not work well with asynchronous panning; see https://developer.mozilla.org/docs/Mozilla/Performance/ScrollLinkedEffects for further details and to join the discussion on related tools and features!

The second method is longer but also demonstrates **docassemble**'s
system for packaging and distributing interviews.  It involves these
steps:

1. On the menu in the upper right hand corner, select Package Management.
2. Click "Create a package."
3. Enter `hello-world` as the package name and click "Get template."
4. Save the resulting .zip file to your computer.
5. Unpack the .zip file somewhere.  (On Windows, right-click the .zip
   file and there will be an option to unpack it.)
6. Open your favorite text editor.  (On Windows, use [WordPad] unless
   you have installed a more advanced editor like [Notepad++].)  Open
   the file
   `docassemble-hello-world/docassemble/hello-world/data/questions.yml`
   and replace its contents with the above [YAML] text.
7. Create a new .zip file containing the `docassemble-hello-world`
   folder.  (On Windows, right-click the `docassemble-hello-world`
   folder, select "Send To," then select "Compressed (zipped)
   Folder.")
8. In the **docassemble** web app, go back to Package Management.
9. Click "Update a package."
10. Upload the .zip file you just created.  You should see a message
    that the package was installed successfully.
11. Point your browser to
    `http://localhost?i=docassemble.hello-world:data/questions/questions.yml`
    (substitute the actual domain and base URL of your **docassemble**
    site).  The base url is set during [installation] using the `root`
    value in the **docassemble** [configuration] file.  If [`root`] is
    `/`, you just use `localhost?i=...` or, e.g., `192.168.1.5?i=...`.
    If [`root`] is `/demo/`, you would use `localhost/demo?i=...`.
12. You should see "Hello, world!" with an exit button.

Then repeat steps 8 through 12, above.

(`docassemble-hello-world/docassemble/hello-world/data/questions/questions.yml`
if you downloaded the package)

(Or, if you have already [reconfigured user roles] on your system, log
in as any user with the privileges of an Administrator or a
Developer.)

filesystem.md:

To do:

* Replace file upload storage with WebDAV
* Replace touching of the WSGI file with redis or memcached
* Replace playground storage with WebDAV
* Replace uploading of ZIP file with WebDAV
* When a user updates a Python package, there should be a queue in
  redis that all servers have to follow where they fetch from GitHub
  or from WebDAV

quickstart.md:


# Quick Start with Amazon Web services

1. Go to [Amazon Web Services](https://aws.amazon.com/) and create an
   account.  You will be asked for your credit card, but you will not
   be charged for anything if you stay within the free tier.
2. Sign in to the AWS Console.
3. From the Services menu, select "EC2 Container Service."
4. Click "Get Started" and then click "Cancel."
5. Click "Create Cluster" and name your cluster "docassemble."
6. Click "Task Definitions" and then "Create new Task Definition."
7. Click "Configure via JSON."
8. Copy and paste the JSON configuration below into text area, click
"Save," then click "Create."
9. Click "Clusters" on the menu on the left, then open the
   "docassemble" cluster by clicking the name "docassemble."
10. Under the "Services" tab, click "Create."
11. Make sure the Task Definition is set to "docassemble:1" and the
    Cluster is set to "docassemble."
12. Enter "docassemble" as the "Service name."
13. Set the "Number of tasks" to 1.
14. Click "Create Service."
15. Click "Clusters" on the menu on the left, then open the
   "docassemble" cluster by clicking the name "docassemble."
16. Under "ECS Instances," click "Amazon EC2."  This will open the EC2
    Management Console in another tab.
17. Click "Launch Instance."
18. Click "Community AMIs."  Type "amazon-ecs-optimized" in the
    "Search community AMIs field" and press the Enter key. Choose
    Select next to the "amzn-ami-2016.03.b-amazon-ecs-optimized" AMI.
19. Go to "6. Configure Security Group" and click "Add Rule."  Set the
    "Type" to "HTTP."
20. Click "Review and Launch," then "Launch."
21. Change "Choose an existing key pair" to "Create a new key pair."
    Set the "Key pair name" to "docassemble" and click "Download Key
    Pair."  Save this file in a secure place.
22. Click "Launch Instances."
23. Click "View Instances" and wait until the instance is up and
    running.  ("Status Checks" will read "2/2 checks.")
24. Go back to the EC2 Container Service console.
25. Go to the "Tasks" tab and click "Run new Task."
26. Make sure the "Task Definition" is set to "docassemble:1,"
    "Cluster" is set to "docassemble," and "Number of tasks" is set to
    "1."  Then click "Run Task."
27. 


{% highlight json %}
{
  "family": "docassemble",
  "containerDefinitions": [
    {
      "name": "docassemble",
      "image": "jhpyle/docassemble",
      "memory": 900,
      "cpu": 1,
      "portMappings": [
        {
          "containerPort": 80,
          "hostPort": 80
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "EC2",
          "value": "true"
        },
        {
          "name": "TIMEZONE",
          "value": "America/New_York"
        }
      ]
    }
  ]
}
{% endhighlight %}

Docker/docassemble-site.conf:

<VirtualHost *:80>
    ServerAdmin webmaster@localhost
    ServerName docassemble.example.com
    DocumentRoot /var/www/html
    <IfModule mod_ssl.c>
	RewriteEngine On
	RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
    </IfModule>
    RewriteEngine On
    RewriteCond %{REQUEST_URI}     ^/ws/socket.io         [NC]
    RewriteCond %{QUERY_STRING}    transport=websocket    [NC]
    RewriteRule /ws/(.*)           ws://localhost:5000/$1 [P,L]
    ProxyPass /ws/ http://localhost:5000/
    ProxyPassReverse /ws/ http://localhost:5000/
    <IfModule !mod_ssl.c>
	XSendFile on
	XSendFilePath /usr
	XSendFilePath /tmp
	WSGIDaemonProcess docassemble.webserver user=www-data group=www-data threads=5
	WSGIScriptAlias / /usr/share/docassemble/webapp/docassemble.wsgi
	<Directory /usr/share/docassemble/webapp>
	    WSGIProcessGroup docassemble.webserver
	    WSGIApplicationGroup %{GLOBAL}
	    AllowOverride none
	    Require all granted
	</Directory>
    </IfModule>
    Alias /robots.txt /var/www/html/robots.txt
    Alias /favicon.ico /var/www/html/favicon.ico
    ErrorLog /var/log/apache2/error.log
    CustomLog /var/log/apache2/access.log combined
</VirtualHost>
<IfModule mod_ssl.c>
    <VirtualHost *:443>
        ServerAdmin webmaster@example.com
        ServerName docassemble.example.com
        SSLEngine on
        SSLCertificateFile /etc/ssl/docassemble/docassemble.crt
        SSLCertificateKeyFile /etc/ssl/docassemble/docassemble.key 
        SSLCertificateChainFile /etc/ssl/docassemble/docassemble.ca.pem
        XSendFile on
        XSendFilePath /usr
        XSendFilePath /tmp
        RewriteEngine On
        RewriteCond %{REQUEST_URI}      ^/wss/socket.io         [NC]
        RewriteCond %{QUERY_STRING}     transport=websocket     [NC]
        RewriteRule /wss/(.*)           ws://localhost:5000/$1 [P,L]
        ProxyPass /wss/ http://localhost:5000/
        ProxyPassReverse /wss/ http://localhost:5000/
        WSGIDaemonProcess docassemble.webserver user=www-data group=www-data threads=5
        WSGIScriptAlias / /usr/share/docassemble/webapp/docassemble.wsgi
        <Directory /usr/share/docassemble/webapp>
            WSGIProcessGroup docassemble.webserver
            WSGIApplicationGroup %{GLOBAL}
            AllowOverride none
            Require all granted
        </Directory>
        Alias /robots.txt /var/www/html/robots.txt
        Alias /favicon.ico /var/www/html/favicon.ico
        ErrorLog /var/log/apache2/error.log
        CustomLog /var/log/apache2/access.log combined
    </VirtualHost>
</IfModule>

azure_94e79d28bf7df60a1629a53caac2de80@azure.com

YXp1cmVfOTRlNzlkMjhiZjdkZjYwYTE2MjlhNTNjYWFjMmRlODAuY29t

UjJGc1lYaDVU

Old password, GalaxyNote1: R2FsYXh5Tm90ZTE=

New password: R2FsYXh5T

reset.sh:

#! /bin/bash

supervisorctl stop apache2
su -c "dropdb docassemble" postgres
su -c "createdb -O www-data docassemble" postgres
su -c "/usr/share/docassemble/local/bin/python -m docassemble.webapp.create_tables" www-data
rm -rf /usr/share/docassemble/files/0*
supervisorctl start apache2

mail:
  username: azure_94e79d28bf7df60a1629a53caac2de80@azure.com
  password: R2FsYXh5T
  server: smtp.sendgrid.net
  default_sender: '"Philadelphia Legal Assistance" <no-reply@philalegal.org>'

Here is a script that backs up all of the **docassemble** volumes
running on a remote server, `docassemble.example.com`:

{% highlight bash %}
rsync -au --rsync-path="sudo rsync" docassemble.example.com:/var/lib/docker/volumes /my-local-backup-directory
{% endhighlight %}

Note: for this to run unattended, you need to edit `~/.ssh/config` to
indicate where the identity file is located:

{% highlight text %}
Host docassemble.example.com
    HostName docassemble.example.com
    User ec2-user
    IdentityFile /root/ec2-user.pem
{% endhighlight %}

During startup, the
`LOCALE` will be appended to `/etc/locale.gen` and `locale-gen` and
`update-locale` will be run.  The `TIMEZONE` will be stored in
`/etc/timezone` and `dpkg-reconfigure -f noninteractive tzdata` will
set the system timezone.

* introduce Mako properly in the documentation, in markup#mako
* finish writing section in code on for loops
* document DAList gathering
* prevent infinite loops when using all_variables()
* web API

{% include side-by-side.html demo="dadict" %}

{% include side-by-side.html demo="dalist2" %}

{% include side-by-side.html demo="lists" %}

{% include side-by-side.html demo="madlibs" %}

{% include side-by-side.html demo="nested-for-loop" %}

{% include side-by-side.html demo="nested-gather" %}

* remove references to datetime in demo code
* yolk -l -f license

### <a name="exclude"></a>`exclude`

`exclude` is used in combination with [`choices`](#choices) when the
[`datatype`] is [`object`], [`object_radio`], or
[`object_checkboxes`].  Any object in `exclude` will be omitted from the
list of choices if it is present in [`choices`](#choices).  See the
[section on selecting objects](#objects), below.

As explained in the section on [functions]({{ site.baseurl
}}/docs/functions.html#howtouse), a prerequisite to using functions
like `background_action()` is including a [`modules`] block that makes
these special functions available:

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
{% endhighlight %}

The second block is also important:
{% highlight yaml %}
---
initial: true
code: |
  process_action()
---
{% endhighlight %}

Background actions will not work unless your interview contains a call
to [`process_action()`] in [`initial`] code.  This code needs to run
early on -- after you have screened out unwanted users, but before the
substance of your interview begins.

The background action runs much like other [actions] do: via the
[`process_action()`] function.  If you call `background_action()` in
your interview, make sure that you have included [`initial`] code that
calls [`process_action()`], as in the example above.  This is
important because it gives interview authors the ability to determine
the context in which the [`process_action()`] function is called.  For
example, you might want to call [`set_info()`] first to declare the
role of the user.

if $local_part matches "[a-z]{6}"
then
pipe /usr/share/docassemble/webapp/process-email.sh
seen finish
endif

grep --include='*.py' -Roh -e 'word("[^"]*")' -e "word('[^']*')" | sed -e 's/word("\(.*\)")/"\1": Null/' -e "s/word('\(.*\)')/\"\1\": \Null/" | sort | uniq > 

However, if your interview does not contain any blocks marked with
`event` directives, then **docassemble** will assume you are not using
any [actions], and it will not import the [`docassemble.base.util`]
module or run [`process_action()`].

from playground files:

  {%- for file in editable_files %}
  {%- if file == current_file %}
  <li class="active">
    <a><span class="glyphicon glyphicon-file" aria-hidden="true"></span> {{ file }}</a>
  </li>
  {%- else %}
  <li>
    <a href="?section={{ section }}&file={{ file }}"><span class="glyphicon glyphicon-file" aria-hidden="true"></span> {{ file }}</a>
  </li>
  {%- endif %}
  {%- endfor %}
  {%- if current_file not in editable_files %}
  <li class="active">
    <a href="#">{{ word('New') }}</a>
  </li>
  {%- endif %}

from playground_packages:

  {%- for file in editable_files %}
  {%- if file == current_file %}
  <li class="active">
    <a><span class="glyphicon glyphicon-file" aria-hidden="true"></span> {{ file }}</a>
  </li>
  {%- else %}
  <li>
    <a href="?file={{ file }}">
      <span class="glyphicon glyphicon-file" aria-hidden="true"></span> {{ file }}</a>
  </li>
  {%- endif %}
  {%- endfor %}
  {%- if current_file not in editable_files %}
  <li class="active">
    <a href="#">{{ word('New') }}</a>
  </li>
  {%- endif %}


* New chat connection messages arriving twice, at least on Linux
* Google translate of YAML, Markdown
    * question
    * subquestion
    * under
    * fields
        * labels
        * hint
        * help
    * continue button label
    * resume button label
    * interview help (on its own, or)
        * heading
        * content
    * help (on its own, or)
        * content
    * template
        * subject
        * content
* Back button is a bit messed up with fallback.yml

As **docassemble** goes through the interview file from top to bottom,
looking for [`mandatory`] and [`initial`] blocks.  When it encounters
an [`include`] statement, it immediately goes through the included
file from top to bottom, and then returns to the original file and
picks up where it left off.

At the top of your interview file, you can [`include`] question files
that other authors have written and then later in the interview file,
you can "override" particular questions you would like to ask
differently.

[program:denyhosts]
command=python /usr/sbin/denyhosts --purge --config=/etc/denyhosts.conf
user=0
autostart=true
autorestart=true
exitcodes=0
startsecs=1
priority=70

ACTION:

[Definition]

actionstart = iptables -N fail2ban-docassemble
              iptables -A fail2ban-docassemble -j RETURN
              iptables -I FORWARD -p tcp -m multiport --dports 80,443 -j fail2ban-docassemble

actionstop = iptables -D FORWARD -p tcp -m multiport --dports 80,443 -j fail2ban-docassemble
             iptables -F fail2ban-docassemble
             iptables -X fail2ban-docassemble

actioncheck = iptables -n -L FORWARD | grep -q 'fail2ban-docassemble[ \t]'

actionban = iptables -I fail2ban-docassemble 1 -s <ip> -j DROP

actionunban = iptables -D fail2ban-docassemble -s <ip> -j DROP

FILTER:

[INCLUDES]

before = common.conf

[Definition]

failregex = ^\[[^\]]*\] \[(:?error|\S+:\S+)\]( \[pid \d+(:\S+ \d+)?\])? \[(client|remote) <HOST>(:\d{1,5})?\] Invalid password

ignoreregex = 

JAIL:

[docassemble]

enabled  = true
filter   = docassemble
port     = http,https
logpath  = %(apache_error_log)s

### Running OCR tasks in the background

Note that the OCR process usually takes a long time.  Unless the
document is only one page long, the user will have to wait, looking at
a spinner, for far too long.

The best practice is to run OCR tasks in the background, using the
[`background_action()`] function discussed in the
[background processes] section.

The following example demonstrates how this can be done.  First, the
user is asked to upload a PDF file.  Then, the OCR task is started in
the background.  Then, the user is asked to answer another question,
which will take significant time.  Hopefully, by the time the user
finishes answering that question, the OCR will be finished.  But just
in case it hasn't finished, the user will be shown a screen telling
the user to wait.  This screen reloads every five seconds, so that
when then OCR process does finish, the user will be able to proceed to
the rest of the interview.

{% include side-by-side.html demo="ocr-background" %}

For more information about using [background processes], see the
documentation for the [`background_action()`] function and its related
functions.

[GitHub] has an excellent command line interface on Linux and also has
a [Windows application].

1. Create a new .zip file containing the `docassemble-missouri-family-law`
folder.  (On Windows, right-click the `docassemble-missouri-family-law`
folder, select "Send To," then select "Compressed (zipped) Folder.")

The base url is set during the [installation] of the [WSGI]
server and in the **docassemble** [configuration] file (where it is
called [`root`]).

# Python packages installed on the server

If your **docassemble** interviews or code depend on other
[Python packages] being installed, you can install packages from the
**docassemble** front end:

1. Make sure you are logged in as a developer or administrator.
2. Go to "Package Management" on the menu.
3. Go to "Update a package."

Packages can be installed in three different ways:

* **GitHub URL**: Enter the URL for the GitHub repository containing the
  Python package you want to install.  The repository must be in a
  format that is compatible with [pip].
* **Zip File**: Provide a Zip file containing your Python package.
  The Zip file must be in a format that is compatible with [pip].
* **Package on [PyPI]**: Provide the name of a package that exists on
  [PyPI].

Packages will be installed using the [pip] package manager.  A log
of the output of [pip] will be shown.

If you are running **docassemble** on Mac and Windows, make sure that
the web server user has a home directory to which [pip] can write.
(See [pip/utils/appdirs.py].)

Then, create a `.pypirc` configuration file in your home directory
containing your [PyPI] username and password.  On Windows, you can use
Notepad to create this file; save it in your `C:\Users\yourusername`
directory.

The file should have the following contents (substitute your [PyPI]
username and password in place of `YOURUSERNAME` and `YOURPASSWORD`):

{% highlight text %}
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
repository: https://pypi.python.org/pypi
username: YOURUSERNAME
password: YOURPASSWORD

[pypitest]
repository: https://testpypi.python.org/pypi
username: YOURUSERNAME
password: YOURPASSWORD
{% endhighlight %}

In order to publish to [PyPI], you will need [Python] installed on
your computer.  You can install [Python for Windows] if you have a
Windows PC; just make sure that when you install it, you enable the
option to "Add python.exe to Path."

If you have not done so already, download the `docassemble-helloworld`
package as a ZIP file and extract the contents to your computer.
Windows will suggest extracting to
`C:\Users\yourusername\Desktop\docassemble-helloworld`, but you should
change that path to `C:\Users\yourusername`; after extraction, your
package directory will be
`C:\Users\yourusername\docassemble-helloworld`.

The next steps require the command line, so open a shell (e.g.,
[PowerShell] on Windows).

First, navigate using `cd` to directory that contains the `setup.py`
file for your package.  For example,

{% highlight bash %}
cd docassemble-helloworld
{% endhighlight %}

Within that directory, run the following commands:

{% highlight bash %}
python setup.py register -r pypi
python setup.py sdist upload -r pypi
{% endhighlight %}

If the upload is successful, you will be able to see the package on
the [PyPI] web site.

![PyPI page]({{ site.baseurl }}/img/pypi-helloworld-page.png){: .maybe-full-width }

Then, create a `.pypirc` configuration file in your home directory
containing your [PyPI] username and password.  The file should have
the following contents (substitute your [PyPI] username and password
in place of `YOURUSERNAME` and `YOURPASSWORD`):

{% highlight text %}
[distutils]
index-servers =
  pypi
  pypitest

[pypi]
repository: https://pypi.python.org/pypi
username: YOURUSERNAME
password: YOURPASSWORD

[pypitest]
repository: https://testpypi.python.org/pypi
username: YOURUSERNAME
password: YOURPASSWORD
{% endhighlight %}

On Windows, you can use Notepad to create this file; save it in your
`C:\Users\yourusername` directory.

If you are maintaining your package in the [Playground], download it
as a ZIP file and extract the files.

The next part requires the command line, so open a shell (e.g.,
[PowerShell] on Windows).

First, use `cd` to navigate to the directory that
contains the `setup.py` file.  For example,

{% highlight bash %}
cd docassemble-missouri-family-law
{% endhighlight %}

Within that directory, run the following commands:

{% highlight bash %}
python setup.py register -r pypi
python setup.py sdist upload -r pypi
{% endhighlight %}

To upload to the test server instead of the main server, use
`pypitest` in place of `pypi`.

Once your packages have been uploaded, you can inspect what they look
like on the [PyPI] web site.  The URL will be something like
`https://pypi.python.org/pypi/docassemble.missouri-family-law`.

You can repeat this process every time you make a change to your
package.  However, first change the version number, or else you may
get an error.  You can change the version number of your package in
the "Packages" folder of the [Playground] and then re-download the ZIP
file and re-extract the files.  Or, you can manually edit the
`version=` line in the `setup.py` file.

For more information about uploading packages to [PyPI], see
[how to submit a package to PyPI].

# <a name="customization note"></a>A note about customization of document formatting

If exercising fine-grained control over document formatting is
important to you, and you are not prepared to learn how [Pandoc] and
[LaTeX] work, then **docassemble** may not be right tool for you.
**docassemble** does not allow for [WYSIWYG] formatting of document
templates the way [HotDocs] does.

Rather, **docassemble** is designed to allow template authors to focus
on substance rather than form.  Producing a case caption by typing `${
pleading.caption() }` is ultimately easier on the author of a legal
form than worrying about the formatting of the case caption on each
page of every legal document the author writes.

[Pandoc] and [LaTeX] are powerful tools.  There are published books
written in [Markdown] and converted to PDF with [Pandoc].  There is
little that [LaTeX] cannot do.

The skill set needed to achieve a particular formatting objective
using [Pandoc] and [LaTeX] is different from the skill set needed to
write a user-friendly interview and design the substance of a
document.  Ideally, a software engineer will design appropriate
templates and functions for use by authors, who can concentrate on
substantive content.

If you have an existing .docx file and you want to use **docassemble**
to fill in fields in that file, use [`docx template file`].  If you
want to create a document from scratch (i.e. by writing raw
[Markdown]), use `docx` as one of the `valid formats`.  Both methods
allow you to generate a PDF version of the document along with the
.docx version.

RTF indentation in this context:

    | Quisque nisl felis,
    | venenatis tristique,
    | dignissim in, ultrices
    | sit amet, augue.

    Fusce ac turpis quis ligula
    lacinia aliquet. Mauris ipsum.


If you use a plain [`DADict`] object, the process will look for 

The downside is that you have to be attentive to all the variables
your document might need, and specify them all in the `attachments`
block.

For example, if you are generating a [DOCX](#docx template file)
fill-in form, you can write 
`{% raw %}{{ favorite_fruit }}{% endraw %}`
in your Microsoft Word file where the name of the user's favorite
fruit should be plugged in.  Then you will have to indicate how the
variables in your Word file "map" to variables in your interview by
including a line like the following in your `attachments` block:

{% highlight yaml %}
    favorite_fruit: ${ user.favorite_fruit }
{% endhighlight %}

The variable `favorite_fruit` is a variable in the Word file, and the
variable `user.favorite_fruit` is a variable in your interview.  The
Word file does not know anything about your interview variables, and
vice-versa; you have to explicitly tell the Word file all the
information it might need to know.

As a result, your interview might ask the user for information that
does not need to be asked.  There are ways around this, but they
require you as the interview author to plan for these contingencies.

By contrast, when you
[assemble documents directly from Markdown](#from markdown), all you
need to do is refer to `${ user.favorite_fruit }` in the `content` of
your document.  If the reference is only conditionally displayed, your
interview will automatically refrain from asking the user about his or
her favorite fruit, if the information is not needed.

event: role_event
question: You are done for now.
subquestion: |
  % if 'advocate' in role_needed:
  An advocate needs to review your answers before you can proceed.

  Please remember the following link and come back to it when you
  receive notice to do so:

  [${ interview_url() }](${ interview_url() })  
  % else:
  Thanks, the client needs to resume the interview now.
  % endif

  % if role_change.send_email(role_needed, advocate={'to': advocate, 'email': role_event_email_to_advocate}, client={'to': client, 'email': role_event_email_to_client}):
  An e-mail has been sent.
  % endif
decoration: exit
buttons:
  - Exit: leave
---
template: role_event_email_to_advocate
subject: |
  Client interview waiting for your attention: ${ client }
content: |
  A client, ${ client }, has partly finished an interview.
  ${ client.pronoun_subjective(capitalize=True, thirdperson=True) }
  needs you to review
  ${ client.pronoun_possessive('answers', thirdperson=True) }
  so that ${ client.pronoun_subjective(thirdperson=True) } can obtain
  ${ client.pronoun_possessive('advice letter', thirdperson=True) }
  and ${ pleading.title }.

  Please go to [the interview](${ interview_url() }) as soon as possible.

  Thank you!
---
template: role_event_email_to_client
subject: |
  Your interview answers have been reviewed
content: |
  ${ client.salutation() } ${ client.name.last }:
  
  An advocate has finished reviewing your answers.

  Please go to [${ interview_url() }](${ interview_url() })
  to continue the interview.

  Thank you for your patience.

---
objects:
  - role_change: RoleChangeTracker
---
initial: True
code: |
  if role == 'advocate' and not defined('client.name.first'):
    welcome_advocate
  # track_location = user.location.status()
  set_language(user.language)
---
role: advocate
event: welcome_advocate
question: |
  No role for advocate yet.
subquestion: |
  You are an advocate and this interview is not yet ready for your participation.
---
question: Is this reason a sound one?
subquestion: |
  The client, ${ client }, proposed the following reason for winning:
  
  > ${ explanation }

  Is this a sound reason for why the judge should rule in the client's
  favor in this ${ law_category } case?
yesno: explanation_is_sound
role: advocate
---
mandatory: True
code: |
  set_live_help_status(availability='observeonly', mode='help', partner_roles=['advocate'])
---
  
---
question: Your document is ready.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    description: A document with a **classic** message
    content file: 
      - base_template.md
      - hello_template.md
---
question: Your document is ready, ${ user }.
sets: provide_user_with_document
attachment:
  - name: A *hello world* document
    filename: Hello_World_Document
    description: A document with a **classic** message
    metadata:
      FirstFooterLeft: Can you do *markdown*?
    content: |
      Hello, ${ user }!

---
code: |
  if client.address.address and retry_address:
    retry_address = False
    force_ask('client.address.address')
comment: |
  This is an example of how the "force_ask" function can be used to
  ask a question that has already been asked.
---
question: Would you like to enter your address yet again?
yesno: retry_address

{% highlight yaml %}
---
question: |
  Is ${ case.plaintiff[i].child[j] } 
  old enough to accept service?
yesno: case.plaintiff[i].child[j].able_to_accept_service
---
{% endhighlight %}

So, if you wanted to write a question that gathered the birthdate of
any individual, you would write something like this:

{% highlight yaml %}
generic object: Individual
question: |
  What is the birthdate of ${ x }?
fields:
  - Birthdate: x.birthdate
    datatype: date
{% endhighlight %}

            #output = '<!doctype html>\n<html lang="' + interview_language + '">\n  <head>\n    <meta charset="utf-8">\n    <meta name="mobile-web-app-capable" content="yes">\n    <meta name="apple-mobile-web-app-capable" content="yes">\n    <meta http-equiv="X-UA-Compatible" content="IE=edge">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0, user-scalable=0" />\n    <title>' + interview_status.question.interview.get_title().get('full', default_title) + '</title>\n    <link href="' + url_for('static', filename='app/signature.css') + '" rel="stylesheet">\n  </head>\n  <body class="dasignature">\n'

blue color:
131
179
221

Note that any machine that connects to an SMTP server will need to
identify itself to the SMTP server using a
[fully qualified domain name].  E-mail sending will be slow if your
**docassemble** application servers have trouble finding their fully
qualified domain names.  To test this, do:

{% highlight text %}
$ python
>>> import socket
>>> print socket.getfqdn()
{% endhighlight %}

The `socket.getfqdn()` function should run instantaneously.  If it
does not, you should configure your system so that it can find its
fully qualified domain name faster.  On Linux, you can do this by
editing `/etc/hosts`.

To transition to one of these systems, create a [package] in your
[Playground] containing all of the work you have developed so far, and
then download this package as a ZIP file.  This will back up your
work.  Then you can stop and remove the container, pull the new
**docassemble** image from [Docker Hub], and run it with the
configuration necessary to use one of the above [data storage]
techniques.  Then, log in to the Playground, go to the
[packages folder], and upload the ZIP file.

greenlet==0.4.10 
eventlet==0.19.0

If you do not have [git] on your computer, install it.  If you use
Windows, install [git for Windows], choosing all of the default
options when installing.

Then create a [GitHub] repository.  If your **docassemble** extension
package is `docassemble.missouri-family-law`, the name of the [GitHub]
package should be `docassemble-missouri-family-law`.

After you press ![Create Repository]({{ site.baseurl
}}/img/github-create-repository.png), your browser will go to the URL
for your new repository, which will be in a form like
`https://github.com/jhpyle/docassemble-missouri-family-law`.  In this
example, `jhpyle` is the username, and
`docassemble-missouri-family-law` is the name of the repository.

In the "Packages" folder of the **docassemble** [Playground], edit
your package and add the [GitHub] URL as the "URL" of the package.
This will ensure that if your package is a dependency for another
package, that other package will be able to install your package as
one of its dependencies when it is installed on a server.

Then save your package and then download it as a ZIP file.  Extract
the files from the ZIP file to a convenient place on your computer.

You will see a directory with the name of your package (e.g.,
`docassemble-missouri-family-law`.  This directory will contain a
directory called `docassemble` and a file called `setup.py`.  The top
directory (e.g., `docassemble-missouri-family-law`) will be the root
directory of your new [GitHub] repository.

The process of initializing a package as a [GitHub] repository
requires using the shell.  (On Windows, you can use [PowerShell].)
The web page at the URL for your repository on [GitHub] contains some
instructions about how to initialize your repository.  First, use `cd`
to change into the directory that contains the package you want to
install (in this example, we'll use `docassemble-missouri-family-law`)
and then run the [git] commands suggested by [GitHub].  For example:

{% highlight text %}
cd docassemble-missouri-family-law
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/jhpyle/docassemble-missouri-family-law.git
git push -u origin master
{% endhighlight %}

The last command will prompt you for your [GitHub] credentials.  After
you put in the credentials, your package will be uploaded to
[GitHub].  If you reload your [GitHub] repository's page at the
[GitHub] URL, you will see the listing of files.

  git init
  git add README.md
  git commit -m "first commit"
  git remote add origin git@github.com:jhpyle/docassemble-deleteme.git
  git push -u origin master
  
GIT_SSH_COMMAND='ssh -i private_key_file' git clone host:repo.git
{u'public_repos': 8, u'site_admin': False, u'subscriptions_url':
u'https://api.github.com/users/jhpyle/subscriptions', u'gravatar_id':
u'', u'hireable': None, u'id': 11341940, u'followers_url':
u'https://api.github.com/users/jhpyle/followers', u'following_url':
u'https://api.github.com/users/jhpyle/following{/other_user}',
u'blog': u'', u'followers': 7, u'location': u'Philadelphia, PA',
u'type': u'User', u'email': u'jhpyle@gmail.com', u'bio': u'Lawyer,
computer programmer.', u'gists_url':
u'https://api.github.com/users/jhpyle/gists{/gist_id}', u'company':
None, u'events_url':
u'https://api.github.com/users/jhpyle/events{/privacy}', u'html_url':
u'https://github.com/jhpyle', u'updated_at': u'2017-06-20T02:09:47Z',
u'received_events_url':
u'https://api.github.com/users/jhpyle/received_events',
u'starred_url':
u'https://api.github.com/users/jhpyle/starred{/owner}{/repo}',
u'public_gists': 0, u'name': u'Jonathan Pyle', u'organizations_url':
u'https://api.github.com/users/jhpyle/orgs', u'url':
u'https://api.github.com/users/jhpyle', u'created_at':
u'2015-03-06T00:45:34Z', u'avatar_url':
u'https://avatars0.githubusercontent.com/u/11341940?v=3',
u'repos_url': u'https://api.github.com/users/jhpyle/repos',
u'following': 0, u'login': u'jhpyle'}

pypi username: jpyle
pypi password: gj_6Uygdi4


  If you distribute your package on [GitHub], you will need to set
  this to the [GitHub] URL for your package.  See the
  [packages section] for more information about why this is necessary.

If your package is on [GitHub], you will be able to go to
[Package Management] on a **docassemble** server and install your
package using the URL to the [GitHub] repository.

In order to publish files on [GitHub], you will need the [git]
application.  If you do not have [git] on your computer, install it.
If you use Windows, install [git for Windows], choosing all of the
default options when installing.

To share your interview on [GitHub], first create a [GitHub]
repository.

The name of the repository for a **docassemble** extension package
should be in the form of `docassemble-helloworld`.

![GitHub Repository]({{ site.baseurl }}/img/github-helloworld.png){: .maybe-full-width }

After you press ![Create Repository]({{ site.baseurl
}}/img/github-create-repository.png), you will get a URL for your
repository, which will be in a form like
`https://github.com/jhpyle/docassemble-helloworld`, where your
[GitHub] username will be in place of `jhpyle`, and your repository
name will be in place of `docassemble-helloworld`.

In the ["Packages" folder] of the **docassemble** [Playground], edit
your package and add the [GitHub] URL as the "URL" of the package.

![GitHub URL]({{ site.baseurl }}/img/playground-packages-github-url.png)

![Save]({{ site.baseurl }}/img/playground-packages-button-save.png)
your package and then ![Download]({{ site.baseurl
}}/img/playground-packages-button-download.png) it as a ZIP file.

Extract the files from the ZIP file to a convenient place on your
computer.  Windows will suggest extracting to
`C:\Users\yourusername\Desktop\docassemble-helloworld`, but you should
change that path to `C:\Users\yourusername`; after extraction, your
package directory will be
`C:\Users\yourusername\docassemble-helloworld`.

You will see a `docassemble-helloworld` directory containing a
directory called `docassemble` and a file called `setup.py`.  The
`docassemble-helloworld` directory will be the root directory of your
new [GitHub] repository.

Using a shell (e.g., [PowerShell] on Windows), run the following commands.

{% highlight text %}
cd docassemble-helloworld
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/jhpyle/docassemble-helloworld.git
git push -u origin master
{% endhighlight %}

aws ec2 run-instances --profile default --image-id ami-11120768 --count 1 --instance-type t2.micro --key-name oregon --security-group-ids sg-8ac5f7ee --subnet-id subnet-ef41458a  --block-device-mappings "[{\"DeviceName\":\"/dev/xvdcz\",\"Ebs\":{\"VolumeSize\":22,\"DeleteOnTermination\":true}}]" --iam-instance-profile Name=ecsInstanceRole
aws ec2 describe-instances --profile default | jq -r '.Instances[0].InstanceId'

ssh -i oregon.pem ec2-user@test17.docassemble.org

DAHOSTNAME=test17.docassemble.org
USEHTTPS=true
USELETSENCRYPT=true
LETSENCRYPTEMAIL=jhpyle@gmail.com

docker run --env-file=env.list -d -p 80:80 -p 443:443 jhpyle/docassemble

AWS_INSTANCE_ID=`aws ec2 describe-instances --profile default | jq -r '.Reservations[0].Instances[0].InstanceId'`

AWS_DOMAIN=`aws ec2 describe-instances --profile default | jq -r '.Reservations[0].Instances[0].PublicDnsName'`

aws --profile default ec2 terminate-instances --instance-ids 

curl -X GET "https://api.cloudflare.com/client/v4/zones/cd7d0123e3012345da9420df9514dad0" \
     -H "Content-Type:application/json" \
     -H
     "X-Auth-User-Service-Key:v1.0-e24fd090c02efcfecb4de8f4ff246fd5c75b48946fdf0ce26c59f91d0d90797b-cfa33fe60e8e34073c149323454383fc9005d25c9b4c502c2f063457ef65322eade065975001a0b4b4c591c5e1bd36a6e8f7e2d4fa8a9ec01c64c041e99530c2-07b9efe0acd78c82c8d9c690aacb8656d81c369246d7f996a205fe3c18e9254a"`

CloudFlare API key: 410a69cb068cc3bbfa79208399da68343bdbf
Zone: 6279e86288c5e8fc74781356a3c54e20

smtp.mailgun.org
postmaster@mg.docassemble.org
a5a40d5e3fa20b5cf69a0622176a05ed

Like [`question`] questions, [`code`] questions are not "asked" unless
they contain variables that **docassemble** needs.  All [`question`] and
[`code`] blocks are only called when and if they are needed.

One difficulty is that the ideal environment
for testing, which is **docassemble**'s Playground, is not directly
integrated with [GitHub] or any other version control system.  If you
use [Google Drive integration], you could run version control inside
your Google Drive, but the file structure of the `docassemble`
directory is specific to your [Playground], and you will probably want
your version control to be specific to a [package].

To take advantage of version control, you can use the following process:

* Develop and test your interview in the [Playground].
* Create a [package] containing your interview and its associated files.
* When you are ready to make your first commit, download the package
  as a ZIP file and unpack it on your computer.
* Initialize the version control system inside the root directory of
  the package (i.e. the directory containing `README.md` and
  `setup.py`) (e.g., by running `git init`).
* Then do your first commit (e.g., `git commit -m 'first commit'`).
* Work on the interview some more in the [Playground].
* When you are ready to make your next commit, download the package as
  a ZIP file and unpack it into the same place on your computer as
  before, overwriting the existing files.
* Do your next commit (e.g., `git commit -m 'second commit'`).


      jQuery.validator.addMethod("strictDate", function(value, element) {
          var theDate = new Date(value);
          var stringDate = theDate.toString();
          if (/Invalid|NaN/.test(stringDate)){
              return false;
          }
          element.value = theDate.getFullYear() + "-" + ("0" + (theDate.getMonth() + 1)).slice(-2) + "-" + ("0" + theDate.getDate()).slice(-2);
          return true;
      }, '""" + word("Please enter a valid date") + """');

Note that if you are using [persistent volumes] and/or [S3](#persistent
s3)/[Azure blob storage](#persistent azure), launching a new
**docassemble** container with different variables is not necessarily
going to change the way **docassemble** works.

The `.gather()` method only asks enough questions about each item in
order to display it.  For example, if you have a [`PartyList`] called
`witness`, the items will be [`Individual`]s, and the bare minimum
information needed to display an [`Individual`] is the
[`Individual`]'s `.name.first`.  So if you have a question that offers
to set the `.name.first` attribute, this question will be asked during
the gathering process.  However, questions that set other attributes
of the object will not be asked during the gathering process.  If your
interview uses these attributes, the questions to gather them will be
asked after the list is gathered.  This might not be an ideal ordering
of the questions in your interview.

You can tweak the way information is gathered about the items in a
list by setting the `.complete_attribute` to the name of an attribute
that is defined whenever all the necessary attributes have been set.
This way, you can include a [`code` block] that sets the attribute
after ensuring that all necessary attributes have been defined.  This
[`code` block] will be run during the process of gathering each item.
Here is an example:

{% include side-by-side.html demo="gather-manual-gathered-object" %}

Note that when `.complete_attribute` is set to the text
`'complete'`, the attribute that will be used is `.complete`.  You can
use any attribute name here.

In fact, this particular example could be simplified, since there is
just one question that needs to be asked to gather the necessary
attributes.

{% include side-by-side.html demo="gather-manual-gathered-object-simple" %}

This way, you do not need to use a [`code` block].  However, if your
interview needs to ask multiple questions about each item in the
group, it is better to use an artificial attribute like `.complete`.


AZUREENABLE=true
AZUREACCOUNTNAME=docassembletest
AZUREACCOUNTKEY=1TGSCr2P2uSw9/CoLucfNIAEFqcakAC7kViwJsKLX56X3yugWnwNFRgQRfRHrenGVyc5KujusYSNnXDGXzuDDA==

* Persistent sessions tied to login
* rtf HangingIndent
* codemirror lines too long
* Google translation of interviews
* create issue for problem with eventlet
* more expansive documentation of document formatting features
* create videos:
    * Tour of features
    * Installing, running test interview
        * On Windows
        * On AWS
    * Logging in, changing your password
    * Intro to authoring
        * The hello world example
        * Overview: questions, templates, static files 
        * How the automatic interview logic works
* Integrate with Abhijeet's legal glossary
    * Basic English Legal Glossary with Spanish Explanations http://writeclearly.openadvocate.org/oarc/2016-08-22-EN.csv
    * Common Usage Spanish Legal Glossary http://writeclearly.openadvocate.org/oarc/2016-08-22-ES.csv
    * Expanded Plain Language English Legal Glossary http://writeclearly.openadvocate.org/oarc/2015-12-23-EN.csv
    * Basic English Legal Glossary http://writeclearly.openadvocate.org/oarc/2015-01-15-EN.csv
* Date validation
* Warn when multiple variable names in a field
