#!/bin/sh


if [ ! -f "/tmp/init_done" ]; then
	/certbot-auto --noninteractive --nginx --agree-tos --email ciprianbadescu@yahoo.com --domains itec.nokia-romania-garage.ro,staging.itec.nokia-romania-garage.ro
    touch "/tmp/init_done"
fi

exec nginx -g "daemon off;"
