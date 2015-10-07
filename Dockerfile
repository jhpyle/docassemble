FROM debian:latest

RUN apt-get update && apt-get install -y python-html2text python-markdown python-yaml python-mako python-dateutil python-setuptools python-httplib2 python-dev python-imaging python-pip wget unzip git locales pandoc texlive texlive-latex-extra apache2 postgresql python-psycopg2 libapache2-mod-wsgi python-bcrypt python-speaklater poppler-utils python-pil libffi-dev libffi6 libjs-jquery

RUN pip install us 3to2 guess-language-spirit
RUN pip install mdx_smartypants titlecase
RUN pip install cffi
RUN pip install wtforms werkzeug rauth simplekv Flask-KVSession flask-user pypdf flask flask-login flask-sqlalchemy Flask-WTF babel blinker sqlalchemy
RUN ./compile.sh

RUN mkdir -p /var/www/.local
RUN chown www-data.www-data /var/www/.local
RUN mkdir -p /var/lib/docassemble/webapp
COPY docassemble_webapp/flask.wsgi /var/lib/docassemble/webapp/
RUN chown www-data.www-data /var/lib/docassemble/webapp/flask.wsgi
RUN mkdir -p /usr/share/docassemble/files
RUN chown www-data.www-data /usr/share/docassemble/files
RUN mkdir -p /etc/docassemble
COPY docassemble_base/config.yml /etc/docassemble/
COPY docassemble_webapp/apache.conf /etc/apache2/sites-available/000-default.conf 

USER postgres
RUN echo 'create role "www-data" login; create database docassemble;' | psql
RUN python docassemble_webapp/docassemble/webapp/create_tables.py
RUN echo 'grant all on all tables in schema public to "www-data"; grant all on all sequences in schema public to "www-data";' | psql docassemble

USER root
WORKDIR /tmp
RUN git clone https://github.com/nekstrom/pyrtf-ng && cd pyrtf-ng && python setup.py install
WORKDIR /tmp
RUN wget https://www.nodebox.net/code/data/media/linguistics.zip && unzip linguistics.zip -d /usr/local/lib/python2.7/dist-packages && rm linguistics.zip

RUN a2enmod wsgi
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2

EXPOSE 80

CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]
