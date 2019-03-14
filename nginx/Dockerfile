FROM nginx

RUN apt update && apt-get install -y wget && wget https://dl.eff.org/certbot-auto && chmod a+x ./certbot-auto

COPY nginx.conf /etc/nginx/nginx.conf
COPY static-html-directory /usr/share/nginx/html

COPY ./app /app
CMD ["/app/run.sh"]
