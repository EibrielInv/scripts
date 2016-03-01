FROM php:5.5-cli

RUN apt-get update && apt-get install -y pound varnish rsync htop emacs24-nox php5-mysql dtrx exim4 locales libpng12-dev libjpeg-dev libicu-dev
RUN docker-php-ext-install mysqli intl mbstring && \
  docker-php-ext-configure gd --with-jpeg-dir=/usr/include/ && \
  docker-php-ext-install gd

RUN locale-gen en_US en_US.UTF-8
RUN dpkg-reconfigure locales

#RUN a2enmod rewrite
