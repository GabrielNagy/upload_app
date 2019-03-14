#!/bin/sh

couchdb-backup.sh -b -H localhost -d upload_app -f /var/couchdb_backup/upload_app_backup.json -u admin -p admin -z -T
