FROM debian:latest
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get clean && apt-get update
RUN until apt-get -q -y install tzdata python python-dev wget unzip git locales pandoc texlive texlive-latex-extra apache2 postgresql libapache2-mod-wsgi libapache2-mod-xsendfile poppler-utils libffi-dev libffi6 imagemagick gcc supervisor libaudio-flac-header-perl libaudio-musepack-perl libmp3-tag-perl libogg-vorbis-header-pureperl-perl make perl libvorbis-dev libcddb-perl libinline-perl libcddb-get-perl libmp3-tag-perl libaudio-scan-perl libaudio-flac-header-perl libparallel-forkmanager-perl libav-tools autoconf automake libjpeg-dev zlib1g-dev libpq-dev logrotate tmpreaper cron pdftk fail2ban libxml2 libxslt1.1 libxml2-dev libxslt1-dev redis-server libreoffice libtool libtool-bin; do sleep 1; done
RUN cd /tmp && git clone git://git.code.sf.net/p/pacpl/code pacpl-code && cd pacpl-code && ( ./configure || ./configure || true ) && make && make install && cd .. && wget https://github.com/jgm/pandoc/releases/download/1.17.1/pandoc-1.17.1-2-amd64.deb && dpkg -i pandoc-1.17.1-2-amd64.deb
RUN mkdir -p /etc/ssl/docassemble /usr/share/docassemble/local /usr/share/docassemble/certs /usr/share/docassemble/backup /usr/share/docassemble/config /usr/share/docassemble/webapp /usr/share/docassemble/files /var/www/.pip /var/www/.cache /usr/share/docassemble/log /tmp/docassemble && chown -R www-data.www-data /var/www && chsh -s /bin/bash www-data
RUN cd /usr/share/docassemble && git clone https://github.com/letsencrypt/letsencrypt && cd letsencrypt && ./letsencrypt-auto --help
COPY docassemble_webapp/docassemble.wsgi /usr/share/docassemble/webapp/
COPY Docker/initialize.sh /usr/share/docassemble/webapp/
COPY Docker/run-cron.sh /usr/share/docassemble/webapp/
COPY Docker/run-postgresql.sh /usr/share/docassemble/webapp/
COPY Docker/config.yml /usr/share/docassemble/config/config.yml.dist
COPY Docker/apache.conf /usr/share/docassemble/config/docassemble-http.conf.dist
COPY Docker/apache-ssl.conf /usr/share/docassemble/config/docassemble-ssl.conf.dist
COPY Docker/apache.logrotate /etc/logrotate.d/apache2
COPY Docker/docassemble.logrotate /etc/logrotate.d/docassemble
COPY Docker/docassemble-cron-monthly.sh /etc/cron.monthly/docassemble
COPY Docker/docassemble-cron-weekly.sh /etc/cron.weekly/docassemble
COPY Docker/docassemble-cron-daily.sh /etc/cron.daily/docassemble
COPY Docker/docassemble-cron-hourly.sh /etc/cron.hourly/docassemble
COPY Docker/docassemble.conf /etc/apache2/conf-available/
COPY Docker/docassemble-supervisor.conf /etc/supervisor/conf.d/docassemble.conf
COPY Docker/docassemble.key /etc/ssl/docassemble/docassemble.key.orig
COPY Docker/docassemble.crt /etc/ssl/docassemble/docassemble.crt.orig
COPY Docker/docassemble.ca.pem /etc/ssl/docassemble/docassemble.ca.pem.orig
COPY . /tmp/docassemble/
RUN bash -c "chown -R www-data.www-data /usr/share/docassemble /tmp/docassemble && chmod ogu+r /usr/share/docassemble/config/config.yml.dist && chmod -R og-rwx /etc/ssl/docassemble && cd /tmp && wget https://bootstrap.pypa.io/get-pip.py && python get-pip.py && pip install --upgrade virtualenv"

USER www-data
RUN bash -c "cd /tmp && virtualenv /usr/share/docassemble/local && source /usr/share/docassemble/local/bin/activate && pip install --upgrade pip && pip install 'git+https://github.com/nekstrom/pyrtf-ng#egg=pyrtf-ng' /tmp/docassemble/docassemble /tmp/docassemble/docassemble_base /tmp/docassemble/docassemble_demo /tmp/docassemble/docassemble_webapp"

USER root
RUN sed -i 's/^\(daemonize\s*\)yes\s*$/\1no/g' /etc/redis/redis.conf
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen
RUN update-locale LANG=en_US.UTF-8
RUN a2dismod ssl
RUN a2enmod wsgi
RUN a2enmod rewrite
RUN a2enmod xsendfile
RUN a2enconf docassemble
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
EXPOSE 80
EXPOSE 443
EXPOSE 9001

VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql", "/usr/share/docassemble/log", "/usr/share/docassemble/files", "/usr/share/docassemble/config", "/usr/share/docassemble/backup", "/etc/letsencrypt", "/etc/apache2/sites-available", "/var/run/postgresql"]

CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
