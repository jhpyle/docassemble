FROM debian:latest

RUN echo "deb http://debian.cc.lehigh.edu/debian jessie main" > /etc/apt/sources.list && apt-get clean && apt-get update && apt-get -y install python-markdown python-yaml python-mako python-dateutil python-setuptools python-httplib2 python-dev python-imaging wget unzip git locales pandoc texlive texlive-latex-extra apache2 postgresql python-psycopg2 libapache2-mod-wsgi libapache2-mod-xsendfile python-speaklater poppler-utils python-pil libffi-dev libffi6 libjs-jquery imagemagick gcc supervisor libaudio-flac-header-perl libaudio-musepack-perl libmp3-tag-perl libogg-vorbis-header-pureperl-perl perl make libvorbis-dev libcddb-perl libinline-perl libcddb-get-perl libmp3-tag-perl libaudio-scan-perl libaudio-flac-header-perl libparallel-forkmanager-perl libav-tools automake autoconf automake1.11

RUN easy_install pip
RUN pip install --upgrade us 3to2 guess-language-spirit html2text
RUN pip install --upgrade mdx_smartypants titlecase pygeocoder
RUN pip install --upgrade cffi
RUN pip install --upgrade bcrypt
RUN pip install --upgrade wtforms werkzeug rauth simplekv Flask-KVSession flask-user pypdf flask flask-login flask-sqlalchemy Flask-WTF babel blinker sqlalchemy

RUN mkdir -p /var/www/.local /var/www/.cache && chown www-data.www-data /var/www/.local /var/www/.cache
RUN mkdir -p /var/lib/docassemble/webapp
COPY docassemble_webapp/docassemble.wsgi /var/lib/docassemble/webapp/
RUN chown www-data.www-data /var/lib/docassemble/webapp/docassemble.wsgi
RUN mkdir -p /usr/share/docassemble/files && chown www-data.www-data /usr/share/docassemble/files
RUN mkdir -p /etc/docassemble
COPY Docker/config.yml /etc/docassemble/config.yml
RUN chown www-data.www-data /etc/docassemble/config.yml
COPY Docker/apache.conf /etc/apache2/sites-available/000-default.conf
COPY Docker/run-on-docker.sh /var/lib/docassemble/webapp/

WORKDIR /tmp
RUN git clone https://github.com/nekstrom/pyrtf-ng && cd pyrtf-ng && python setup.py install && cd /tmp && wget https://www.nodebox.net/code/data/media/linguistics.zip && unzip linguistics.zip -d /usr/local/lib/python2.7/dist-packages && rm linguistics.zip && git clone git://git.code.sf.net/p/pacpl/code pacpl-code && cd pacpl-code && ./configure; make && make install && cd ..

RUN mkdir -p /tmp/docassemble
COPY . /tmp/docassemble/
WORKDIR /tmp/docassemble
RUN ./compile.sh
WORKDIR /tmp/docassemble
RUN Docker/setup-docassemble.sh

RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
RUN locale-gen
RUN update-locale LANG=en_US.UTF-8
RUN a2enmod wsgi
RUN a2enmod xsendfile
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
EXPOSE 80

CMD ["/var/lib/docassemble/webapp/run-on-docker.sh"]
