FROM php:${PHP_VERSION}-fpm

RUN apt update 

RUN apt install -y \
        zlib1g-dev \
        libonig-dev \
        sendmail \
        libpng-dev \
        libzip-dev \
        libicu-dev \
        zip 

#Mandatory extensions
RUN docker-php-ext-install mysqli

RUN docker-php-ext-install mbstring

RUN docker-php-ext-install zip

RUN docker-php-ext-install gd 
 
RUN docker-php-ext-install intl

RUN docker-php-ext-install calendar

#imap
RUN apt-get -y install libssl-dev libc-client2007e-dev libkrb5-dev \
    && docker-php-ext-configure imap --with-imap-ssl --with-kerberos \
    && docker-php-ext-install imap

EXPOSE 9000