FROM jhpyle/docassemble-os
COPY . /tmp/docassemble/
RUN DEBIAN_FRONTEND=noninteractive TERM=xterm LC_CTYPE=C.UTF-8 LANG=C.UTF-8 \
bash -c \
"apt-get -y update \
&& ln -s /var/mail/mail /var/mail/root \
&& cp /tmp/docassemble/docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/ \
&& cp /tmp/docassemble/Docker/*.sh /usr/share/docassemble/webapp/ \
&& cp /tmp/docassemble/Docker/VERSION /usr/share/docassemble/webapp/ \
&& cp /tmp/docassemble/Docker/pip.conf /usr/share/docassemble/local3.10/ \
&& cp /tmp/docassemble/Docker/config/* /usr/share/docassemble/config/ \
&& cp /tmp/docassemble/Docker/cgi-bin/index.sh /usr/lib/cgi-bin/ \
&& cp /tmp/docassemble/Docker/syslog-ng.conf /usr/share/docassemble/webapp/syslog-ng.conf \
&& cp /tmp/docassemble/Docker/syslog-ng-docker.conf /usr/share/docassemble/webapp/syslog-ng-docker.conf \
&& cp /tmp/docassemble/Docker/smart-multi-line.fsm /usr/share/syslog-ng/smart-multi-line.fsm \
&& cp /tmp/docassemble/Docker/docassemble-syslog-ng.conf /usr/share/docassemble/webapp/docassemble-syslog-ng.conf \
&& cp /tmp/docassemble/Docker/apache.logrotate /etc/logrotate.d/apache2 \
&& cp /tmp/docassemble/Docker/nginx.logrotate /etc/logrotate.d/nginx \
&& cp /tmp/docassemble/Docker/docassemble.logrotate /etc/logrotate.d/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-monthly.sh /etc/cron.monthly/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-weekly.sh /etc/cron.weekly/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-daily.sh /etc/cron.daily/docassemble \
&& cp /tmp/docassemble/Docker/cron/docassemble-cron-hourly.sh /etc/cron.hourly/docassemble \
&& cp /tmp/docassemble/Docker/cron/syslogng-cron-daily.sh /etc/cron.daily/logrotatepost \
&& cp /tmp/docassemble/Docker/cron/donothing /usr/share/docassemble/cron/donothing \
&& cp /tmp/docassemble/Docker/docassemble.conf /etc/apache2/conf-available/ \
&& cp /tmp/docassemble/Docker/docassemble-behindlb.conf /etc/apache2/conf-available/ \
&& cp /tmp/docassemble/Docker/docassemble-supervisor.conf /etc/supervisor/conf.d/docassemble.conf \
&& cp /tmp/docassemble/Docker/ssl/* /usr/share/docassemble/certs/ \
&& cp -r /tmp/docassemble/Docker/ssl /usr/share/docassemble/config/defaultcerts \
&& chmod og-rwx /usr/share/docassemble/certs/* \
&& chmod og-rwx /usr/share/docassemble/config/defaultcerts/* \
&& cp /tmp/docassemble/Docker/rabbitmq.config /etc/rabbitmq/ \
&& cp /tmp/docassemble/Docker/config/exim4-router /etc/exim4/conf.d/router/101_docassemble \
&& cp /tmp/docassemble/Docker/config/exim4-filter /etc/exim4/docassemble-filter \
&& cp /tmp/docassemble/Docker/config/exim4-main /etc/exim4/conf.d/main/01_docassemble \
&& cp /tmp/docassemble/Docker/config/exim4-acl /etc/exim4/conf.d/acl/29_docassemble \
&& cp /tmp/docassemble/Docker/config/exim4-update /etc/exim4/update-exim4.conf.conf \
&& cp /tmp/docassemble/Docker/config/nascent.conf /usr/share/docassemble/config/nascent.conf \
&& cp /tmp/docassemble/Docker/nascent.html /var/www/nascent/index.html \
&& cp /tmp/docassemble/Docker/daunoconv /usr/bin/daunoconv \
&& chmod ogu+rx /usr/bin/daunoconv \
&& update-exim4.conf \
&& chown -R www-data:www-data \
   /usr/share/docassemble/log \
   /usr/share/docassemble/files \
&& chmod ogu+r /usr/share/docassemble/config/config.yml.dist \
&& chmod 755 /etc/ssl/docassemble \
&& cd /tmp \
&& echo \"en_US.UTF-8 UTF-8\" >> /etc/locale.gen \
&& locale-gen \
&& update-locale \
&& /usr/bin/pip3 install --break-system-packages unoconv \
&& cp /usr/local/bin/unoconv /usr/bin/unoconv \
&& python3.10 -m venv --copies /usr/share/docassemble/local3.10 \
&& source /usr/share/docassemble/local3.10/bin/activate \
&& pip install --upgrade pip==24.3.1 \
&& pip install --upgrade wheel==0.45.1 \
&& pip install --upgrade mod_wsgi==5.0.2 \
&& pip install --upgrade \
   acme==3.0.1 \
   certbot==3.0.1 \
   certbot-apache==3.0.1 \
   certbot-nginx==3.0.1 \
   certifi==2024.8.30 \
   cffi==1.17.1 \
   charset-normalizer==3.4.0 \
   click==8.1.7 \
   ConfigArgParse==1.7 \
   configobj==5.0.9 \
   cryptography==44.0.0 \
   distro==1.9.0 \
   idna==3.10 \
   joblib==1.4.2 \
   josepy==1.14.0 \
   nltk==3.9.1 \
   parsedatetime==2.6 \
   pycparser==2.22 \
   pyOpenSSL==24.3.0 \
   pyparsing==3.2.0 \
   pyRFC3339==2.0.1 \
   python-augeas==1.1.0 \
   pytz==2024.2 \
   regex==2024.11.6 \
   requests==2.32.3 \
   six==1.16.0 \
   tqdm==4.67.1 \
   urllib3==2.2.3 \
&& pip install \
   /tmp/docassemble/docassemble \
   /tmp/docassemble/docassemble_base \
   /tmp/docassemble/docassemble_demo \
   /tmp/docassemble/docassemble_webapp \
&& mv /etc/crontab /usr/share/docassemble/cron/crontab \
&& ln -s /usr/share/docassemble/cron/crontab /etc/crontab \
&& mv /etc/cron.daily/apache2 /usr/share/docassemble/cron/apache2 \
&& ln -s /usr/share/docassemble/cron/apache2 /etc/cron.daily/apache2 \
&& mv /etc/cron.daily/exim4-base /usr/share/docassemble/cron/exim4-base \
&& ln -s /usr/share/docassemble/cron/exim4-base /etc/cron.daily/exim4-base \
&& mv /etc/syslog-ng/syslog-ng.conf /usr/share/docassemble/syslogng/syslog-ng.conf \
&& ln -s /usr/share/docassemble/syslogng/syslog-ng.conf /etc/syslog-ng/syslog-ng.conf \
&& { if [[ '$(dpkg --print-architecture)' == 'amd64' ]]; then cp /usr/share/docassemble/local3.10/lib/python3.10/site-packages/mod_wsgi/server/mod_wsgi-py310.cpython-310-x86_64-linux-gnu.so /usr/lib/apache2/modules/mod_wsgi.so-3.10; else cp /usr/share/docassemble/local3.10/lib/python3.10/site-packages/mod_wsgi/server/mod_wsgi-py310.cpython-310-aarch64-linux-gnu.so /usr/lib/apache2/modules/mod_wsgi.so-3.10; fi; } \
&& rm -f /usr/lib/apache2/modules/mod_wsgi.so \
&& ln -s /usr/lib/apache2/modules/mod_wsgi.so-3.10 /usr/lib/apache2/modules/mod_wsgi.so \
&& rm -f /etc/cron.daily/apt-compat \
&& sed -i -e 's/^\(daemonize\s*\)yes\s*$/\1no/g' -e 's/^bind 127.0.0.1/bind 0.0.0.0/g' /etc/redis/redis.conf \
&& sed -i -e 's/#APACHE_ULIMIT_MAX_FILES/APACHE_ULIMIT_MAX_FILES/' -e 's/ulimit -n 65536/ulimit -n 8192/' /etc/apache2/envvars \
&& sed -i '/session    required     pam_loginuid.so/c\#session    required   pam_loginuid.so' /etc/pam.d/cron \
&& LANG=en_US.UTF-8 \
&& { a2dismod ssl \
; a2enmod rewrite \
; a2enmod xsendfile \
; a2enmod proxy \
; a2enmod proxy_http \
; a2enmod proxy_wstunnel \
; a2enmod headers \
; a2enconf docassemble \
; echo 'export TERM=xterm' >> /etc/bash.bashrc; }"

USER www-data
RUN bash -c \
"source /usr/share/docassemble/local3.10/bin/activate \
&& python /tmp/docassemble/Docker/nltkdownload.py \
&& cd /var/www/nltk_data/corpora \
&& unzip -o wordnet.zip \
&& unzip -o omw-1.4.zip \
&& cd /tmp \
&& mkdir -p /tmp/conv \
&& pandoc --pdf-engine=lualatex -M latextmpdir=./conv -M pdfa=false /usr/share/docassemble/local3.10/lib/python3.10/site-packages/docassemble/base/data/templates/Legal-Template.yml --template=/usr/share/docassemble/local3.10/lib/python3.10/site-packages/docassemble/base/data/templates/Legal-Template.tex --from=markdown+raw_tex-latex_macros -s -o /tmp/temp.pdf /usr/share/docassemble/local3.10/lib/python3.10/site-packages/docassemble/base/data/templates/hello.md \
&& rm /tmp/temp.pdf \
&& pandoc --pdf-engine=lualatex -M latextmpdir=./conv -M pdfa=false --template=/usr/share/docassemble/local3.10/lib/python3.10/site-packages/docassemble/base/data/templates/Legal-Template.rtf -s -o /tmp/temp.rtf /usr/share/docassemble/local3.10/lib/python3.10/site-packages/docassemble/base/data/templates/hello.md \
&& rm /tmp/temp.rtf"

USER root
RUN rm -rf /tmp/docassemble

EXPOSE 80 443 9001 514 25 465 8080 8081 8082 5432 6379 4369 5671 5672 25672
ENV \
CONTAINERROLE="all" \
LOCALE="en_US.UTF-8 UTF-8" \
TIMEZONE="America/New_York" \
SUPERVISORLOGLEVEL="info" \
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
RABBITMQ="" \
DASUPERVISORUSERNAME="" \
DASUPERVISORPASSWORD=""

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
