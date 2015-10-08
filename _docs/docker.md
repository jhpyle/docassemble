---
layout: docs
title: Installing on Docker
short_title: Docker
---

If you want to avoid having to install all of **docassemble**'s
dependencies on your server, you can run it as a [Docker] image.

**docassemble** works particularly well running as a [Docker]
container on [Amazon AWS] within an EC2 virtual machine running Amazon
Linux.

[Docker] is a good platform to try out **docassemble** and it is also
a good platform for deploying **docassemble**.  Amazon's EC2 Container
Service can be used to maintain a cluster of **docassemble** images.

## Installing Docker

On Amazon Linux (assuming the username ec2-user):

    sudo yum update
    sudo yum install docker
	sudo usermod -a -G docker ec2-user

On Ubuntu (assuming username ubuntu):

	sudo apt-get update
	sudo apt-get install docker.io
	sudo usermod -a -G docker ubuntu

The last line allows the non-root user to run Docker.  You may need to
log out and log back in again for the new user permission to take
effect.

## Running docassemble from a pre-packaged Docker image

**docassemble** is available on [Docker Hub](https://hub.docker.com/r/jhpyle/docassemble/).  You can download and run the image by doing:

    docker run -p 80:80 jhpyle/docassemble

Or, if you are already using port 80 on your machine, use something
like `-p 8080:80` instead.

To make changes to the configuration, you can gain access to the
running container by running:

    docker exec -t -i <containerid> bash

You can find out the ID of the container by doing `docker ps`.

## Creating your own Docker image

To create your own docker image of docassemble, first download docassemble:

	git clone https://github.com/jhpyle/docassemble

The files used for setup are in the directory docassemble

	docker build -t yourdockerhubusername/mydocassemble .

You can then run your image:

    docker run -p 80:80 yourdockerhubusername/mydocassemble

Or push it to Docker Hub:

    docker push yourdockerhubusername/mydocassemble

[Docker]: https://www.docker.com/
[Amazon AWS]: http://aws.amazon.com
