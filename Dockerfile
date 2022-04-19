FROM jhpyle/docassemble-os
COPY . /tmp/docassemble/
RUN DEBIAN_FRONTEND=noninteractive TERM=xterm \
bash -c \
"apt-get -y update \
&& chsh -s /bin/bash www-data \
&& ln -s /var/mail/mail /var/mail/root \
&& cp /tmp/docassemble/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/ \
&& cp /tmp/docassemble/Docker/*.sh /usr/share/docassemble/webapp/ \
&& cp /tmp/docassemble/Docker/VERSION /usr/share/docassemble/webapp/ \
&& cp /tmp/docassemble/Docker/pip.conf /usr/share/docassemble/local3.8/ \
&& cp /tmp/docassemble/Docker/config/* /usr/share/docassemble/config/ \
&& cp /tmp/docassemble/Docker/cgi-bin/index.sh /usr/lib/cgi-bin/ \
&& cp /tmp/docassemble/Docker/syslog-ng.conf /usr/share/docassemble/webapp/syslog-ng.conf \
&& cp /tmp/docassemble/Docker/syslog-ng-docker.conf /usr/share/docassemble/webapp/syslog-ng-docker.conf \
&& cp /tmp/docassemble/Docker/docassemble-syslog-ng.conf /usr/share/docassemble/webapp/docassemble-syslog-ng.conf \
&& cp /tmp/docassemble/Docker/apache.logrotate /etc/logrotate.d/apache2 \
&& cp /tmp/docassemble/Docker/nginx.logrotate /etc/logrotate.d/nginx \
&& cp /tmp/docassemble/Docker/docassemble.logrotate /etc/logrotate.d/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-monthly.sh /etc/cron.monthly/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-weekly.sh /etc/cron.weekly/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-daily.sh /etc/cron.daily/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-hourly.sh /etc/cron.hourly/docassemble \
&& cp /tmp/docassemble/Docker/cron/syslogng-cron-daily.sh /etc/cron.daily/logrotatepost \
&& cp /tmp/docassemble/Docker/docassemble.conf /etc/apache2/conf-available/ \
&& cp /tmp/docassemble/Docker/docassemble-behindlb.conf /etc/apache2/conf-available/ \
&& cp /tmp/docassemble/Docker/docassemble-supervisor.conf /etc/supervisor/conf.d/docassemble.conf \
&& cp /tmp/docassemble/Docker/ssl/* /usr/share/docassemble/certs/ \
&& cp -r /tmp/docassemble/Docker/ssl /usr/share/docassemble/config/defaultcerts \
&& cp /tmp/docassemble/Docker/rabbitmq.config /etc/rabbitmq/ \
&& cp /tmp/docassemble/Docker/config/exim4-router /etc/exim4/conf.d/router/101_docassemble \
&& cp /tmp/docassemble/Docker/config/exim4-filter /etc/exim4/docassemble-filter \
&& cp /tmp/docassemble/Docker/config/exim4-main /etc/exim4/conf.d/main/01_docassemble \
&& cp /tmp/docassemble/Docker/config/exim4-acl /etc/exim4/conf.d/acl/29_docassemble \
&& cp /tmp/docassemble/Docker/config/exim4-update /etc/exim4/update-exim4.conf.conf \
&& cp /tmp/docassemble/Docker/nascent.html /var/www/nascent/index.html \
&& cp /tmp/docassemble/Docker/daunoconv /usr/bin/daunoconv \
&& chmod ogu+rx /usr/bin/daunoconv \
&& update-exim4.conf \
&& chown www-data.www-data /usr/share/docassemble/config \
&& chown www-data.www-data \
   /usr/share/docassemble/config/config.yml.dist \
   /usr/share/docassemble/webapp/docassemble.wsgi \
&& chown -R www-data.www-data \
   /tmp/docassemble \
   /usr/share/docassemble/local3.8 \
   /usr/share/docassemble/log \
   /usr/share/docassemble/files \
&& chmod ogu+r /usr/share/docassemble/config/config.yml.dist \
&& chmod 755 /etc/ssl/docassemble \
&& cd /tmp \
&& echo \"en_US.UTF-8 UTF-8\" >> /etc/locale.gen \
&& locale-gen \
&& update-locale"

USER www-data
RUN LC_CTYPE=C.UTF-8 LANG=C.UTF-8 \
bash -c \
"cd /tmp \
&& /usr/bin/python3.8 -m venv --copies /usr/share/docassemble/local3.8 \
&& source /usr/share/docassemble/local3.8/bin/activate \
&& pip3 install --upgrade pip==21.1 \
&& pip3 install --upgrade wheel==0.37.1 \
&& pip3 install --upgrade mod_wsgi==4.7.1 \
&& pip3 install --upgrade \
   acme==1.26.0 \
   certbot-apache==1.15.0 \
   certbot-nginx==1.15.0 \
   certbot==1.15.0 \
   certifi==2021.10.8 \
   cffi==1.15.0 \
   charset-normalizer==2.0.12 \
   click==8.1.2 \
   ConfigArgParse==1.5.3 \
   configobj==5.0.6 \
   cryptography==36.0.2 \
   distro==1.7.0 \
   idna==3.3 \
   joblib==1.1.0 \
   josepy==1.13.0 \
   nltk==3.7 \
   parsedatetime==2.6 \
   pycparser==2.21 \
   PyOpenSSL==22.0.0 \
   pyparsing==3.0.8 \
   pyRFC3339==1.1 \
   python-augeas==1.1.0 \
   pytz==2022.1 \
   regex==2022.3.15 \
   requests-toolbelt==0.9.1 \
   requests==2.27.1 \
   six==1.16.0 \
   tqdm==4.64.0 \
   urllib3==1.26.9 \
   zope.component==5.0.1 \
   zope.event==4.5.0 \
   zope.hookable==5.1.0 \
   zope.interface==5.4.0 \
&& python /tmp/docassemble/Docker/nltkdownload.py \
&& pip3 install \
   /tmp/docassemble/docassemble \
   /tmp/docassemble/docassemble_base \
   /tmp/docassemble/docassemble_demo \
   /tmp/docassemble/docassemble_webapp \
&& touch /usr/share/docassemble/log/worker.log \
&& touch /usr/share/docassemble/log/single_worker.log \
&& touch /usr/share/docassemble/log/uwsgi.log \
&& touch /usr/share/docassemble/log/websockets.log"

USER root
RUN \
cp /usr/share/docassemble/local3.8/lib/python3.8/site-packages/mod_wsgi/server/mod_wsgi-py38.cpython-38-x86_64-linux-gnu.so /usr/lib/apache2/modules/mod_wsgi.so-3.8 \
; rm -rf /tmp/docassemble \
&& rm -f /etc/cron.daily/apt-compat \
&& sed -i -e 's/^\(daemonize\s*\)yes\s*$/\1no/g' -e 's/^bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf \
&& sed -i -e 's/#APACHE_ULIMIT_MAX_FILES/APACHE_ULIMIT_MAX_FILES/' -e 's/ulimit -n 65536/ulimit -n 8192/' /etc/apache2/envvars \
&& sed -i '/session    required     pam_loginuid.so/c\#session    required   pam_loginuid.so' /etc/pam.d/cron \
&& LANG=en_US.UTF-8 \
&& a2dismod ssl; \
a2enmod rewrite; \
a2enmod xsendfile; \
a2enmod proxy; \
a2enmod proxy_http; \
a2enmod proxy_wstunnel; \
a2enmod headers; \
a2enconf docassemble; \
echo 'export TERM=xterm' >> /etc/bash.bashrc
EXPOSE 80 443 9001 514 25 465 8080 8081 8082 5432 6379 4369 5671 5672 25672
ENV \
CONTAINERROLE="all" \
LOCALE="en_US.UTF-8 UTF-8" \
TIMEZONE="America/New_York" \
EC2="" \
S3ENABLE="" \
S3BUCKET="" \
S3ACCESSKEY="" \
S3SECRETACCESSKEY="" \
S3REGION="" \
DAHOSTNAME="" \
USEHTTPS="" \
USELETSENCRYPT="" \
LETSENCRYPTEMAIL="" \
BEHINDHTTPSLOADBALANCER="" \
DBHOST="" \
LOGSERVER="" \
REDIS="" \
RABBITMQ=""

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
