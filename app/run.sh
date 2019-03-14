#!/bin/sh
python /app/upload_app/setup_db.py
gunicorn -b 0.0.0.0:8000 \
        --access-logfile - \
        --reload \
        "upload_app.upload_app:app"

curl -X PUT http://admin:admin@couchdb-node:5984/_users
curl -X PUT http://admin:admin@couchdb-node:5984/_replicator

