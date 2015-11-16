FROM ubuntu:12.04
MAINTAINER Eibriel <eibriel@eibriel.com>

RUN apt-get update
RUN apt-get install -y \
    python2.7 \
    python-imaging \
    imagemagick \
    python-psycopg2 \
    python-pycryptopp \
    python-crypto \
    python-lxml \
    apache2 \
    sudo \
    language-pack-en

# Adding required en_US locale
RUN dpkg-reconfigure locales

WORKDIR /etc/apache2/mods-available

RUN ln -s ../mods-available/rewrite.load ../mods-enabled/
RUN ln -s ../mods-available/proxy.load ../mods-enabled/
RUN ln -s ../mods-available/proxy_http.load ../mods-enabled/
RUN ln -s ../mods-available/proxy_balancer.load ../mods-enabled/

ADD tactic-3.9.0.v10.tar.gz /

RUN ls /tactic-3.9.0.v10

RUN python /tactic-3.9.0.v10/src/install/install.py --defaults --install_db false

COPY tactic.conf /etc/apache2/conf.d/

COPY database_conf.py /database_conf.py
RUN mkdir /home/apache/projects/config/
COPY tactic_linux-conf.xml /home/apache/projects/config/tactic_linux-conf.xml

ENV TACTIC_INSTALL_DIR /home/apache/tactic
ENV TACTIC_SITE_DIR /home/apache/projects

ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2

RUN mkdir -p $APACHE_RUN_DIR $APACHE_LOCK_DIR $APACHE_LOG_DIR

COPY init.sh /init.sh

EXPOSE 80

CMD ["/init.sh"]
