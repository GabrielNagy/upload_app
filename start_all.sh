#!/bin/sh

#step 1 start databases
docker-compose up -d couchdb-node
docker-compose up -d redis-node

couchdb_started=-1
while [ $couchdb_started -ne 0 ]; do
	wget --timeout=5 -qO - http://127.0.0.1:5984/_up
	couchdb_started=$?
	echo Waiting couchdb start
	sleep 1
done
curl -X PUT http://admin:admin@127.0.0.1:5984/_users
curl -X PUT http://admin:admin@127.0.0.1:5984/_replicator

redis_started=-1
while [ $redis_started -ne 0 ]; do
	(printf "PING\r\n";) | nc -N localhost 6379
	redis_started=$?
	echo Waiting redis start
	sleep 1
done


docker-compose up -d app
docker-compose up -d celery
docker-compose up -d nginx
