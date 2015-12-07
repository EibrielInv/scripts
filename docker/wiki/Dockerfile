FROM php:5.6-apache
MAINTAINER Eibriel <eibriel@eibriel.com>

RUN apt-get update && apt-get install -y \
        php5-mysql \
	imagemagick \
    && docker-php-ext-install mysql

#ADD wiki.tar.gz /var/www/html
