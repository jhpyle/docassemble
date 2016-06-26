#! /bin/bash
cd static/app
#wget https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap-theme.min.css
#wget https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css
#wget https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js
wget https://cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/css/jasny-bootstrap.min.css
wget https://cdnjs.cloudflare.com/ajax/libs/jasny-bootstrap/3.1.3/js/jasny-bootstrap.min.js
wget https://ajax.aspnetcdn.com/ajax/jquery.validate/1.14.0/jquery.validate.min.js
wget https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js
cd ..
rm -rf bootstrap
wget https://github.com/twbs/bootstrap/releases/download/v3.3.6/bootstrap-3.3.6-dist.zip
unzip bootstrap-3.3.6-dist.zip
rm bootstrap-3.3.6-dist.zip
mv bootstrap-3.3.6-dist bootstrap
