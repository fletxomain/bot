FROM php:8.3-apache
RUN docker-php-ext-install opcache
RUN a2enmod headers
COPY secure.php /var/www/html/index.php
EXPOSE 80
