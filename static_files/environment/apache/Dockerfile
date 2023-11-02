FROM debian:buster-slim

RUN apt-get update \
    && apt-get install -y apache2 \
    && a2enmod proxy_fcgi


COPY ./000-default.conf /etc/apache2/sites-available/.

CMD /usr/sbin/apache2ctl -D FOREGROUND