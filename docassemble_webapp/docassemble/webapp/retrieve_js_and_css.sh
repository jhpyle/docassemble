#! /bin/bash

# The docassemble web application depends on a variety of third-party
# Javascript and CSS libraries.
# All necessary Javascript and CSS files are hosted on the docassemble
# server, as opposed to being retrieved from CDNs.
#
# This script will obtain new versions of the Javascript and CSS files

source /usr/share/docassemble/local/bin/activate # for running pygmentize

cd static/app
rm -f jasny-bootstrap.min.css
wget https://cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css
rm -f jasny-bootstrap.min.js
wget https://cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/js/jasny-bootstrap.min.js
rm -f jquery.validate.min.js
wget https://ajax.aspnetcdn.com/ajax/jquery.validate/1.15.0/jquery.validate.min.js
rm -f jquery.min.js
wget https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js
rm -f socket.io.*
wget https://cdn.socket.io/socket.io-1.4.5.js
mv socket.io-*.js socket.io.min.js
pygmentize -S default -f html > pygments.css
cd ..
rm -rf bootstrap
wget https://github.com/twbs/bootstrap/releases/download/v3.3.7/bootstrap-3.3.7-dist.zip
unzip bootstrap-*-dist.zip
rm bootstrap-*-dist.zip
mv bootstrap-*-dist bootstrap
rm -rf areyousure
git clone https://github.com/codedance/jquery.AreYouSure
mv jquery.AreYouSure areyousure
rm -rf bootstrap-fileinput
git clone https://github.com/kartik-v/bootstrap-fileinput
rm -r bootstrap-slider
git clone https://github.com/seiyria/bootstrap-slider
rm -rf codemirror
wget http://codemirror.net/codemirror.zip
unzip codemirror.zip
rm -f codemirror.zip
mv codemirror-* codemirror
rm -rf jquery-labelauty
git clone https://github.com/fntneves/jquery-labelauty
