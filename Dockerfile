FROM debian:latest

RUN apt-get update && apt-get install -y python-html2text python-markdown python-yaml python-mako python-dateutil python-setuptools python-httplib2 python-dev python-imaging wget unzip git locales pandoc texlive texlive-latex-extra apache2 postgresql python-psycopg2 libapache2-mod-wsgi python-speaklater poppler-utils python-pil libffi-dev libffi6 libjs-jquery imagemagick

RUN easy_install pip
RUN pip install --upgrade us 3to2 guess-language-spirit
RUN pip install --upgrade mdx_smartypants titlecase
RUN pip install --upgrade cffi
RUN pip install --upgrade bcrypt
RUN pip install --upgrade wtforms werkzeug rauth simplekv Flask-KVSession flask-user pypdf flask flask-login flask-sqlalchemy Flask-WTF babel blinker sqlalchemy

RUN mkdir -p /var/www/.local
RUN chown www-data.www-data /var/www/.local
RUN mkdir -p /var/lib/docassemble/webapp
COPY docassemble_webapp/flask.wsgi /var/lib/docassemble/webapp/
RUN chown www-data.www-data /var/lib/docassemble/webapp/flask.wsgi
RUN mkdir -p /usr/share/docassemble/files
RUN chown www-data.www-data /usr/share/docassemble/files
RUN mkdir -p /etc/docassemble
COPY docassemble_base/docker-config.yml /etc/docassemble/
COPY docassemble_webapp/apache.conf /etc/apache2/sites-available/000-default.conf 

WORKDIR /tmp
RUN git clone https://github.com/nekstrom/pyrtf-ng && cd pyrtf-ng && python setup.py install
WORKDIR /tmp
RUN wget https://www.nodebox.net/code/data/media/linguistics.zip && unzip linguistics.zip -d /usr/local/lib/python2.7/dist-packages && rm linguistics.zip

RUN mkdir -p /tmp/docassemble
COPY . /tmp/docassemble/
WORKDIR /tmp/docassemble
RUN ./compile.sh
WORKDIR /tmp/docassemble
RUN ./docassemble_webapp/setup-docassemble.sh

RUN locale-gen --purge en_US.utf-8
RUN echo -e 'LANG="en_US.UTF-8"\nLANGUAGE="en_US:en"\n' > /etc/default/locale
RUN a2enmod wsgi
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
EXPOSE 80

CMD /tmp/docassemble/docassemble_webapp/run-on-docker.sh
