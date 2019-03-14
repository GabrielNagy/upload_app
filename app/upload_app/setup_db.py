#!/usr/bin/env python
import couchdbkit
import os


if __name__ == "__main__":
    path = os.path.dirname(os.path.abspath(__file__))
    couchdbkit.set_logging('info')
    if 'COUCHDB_USER' and 'COUCHDB_PASS' in os.environ:
        ip = "http://%s:%s@couchdb-node:5984" % (os.getenv('COUCHDB_USER'), os.getenv('COUCHDB_PASS'))
    else:
        ip = "http://admin:admin@couchdb-node:5984"
    database = "upload_app"
    server = couchdbkit.Server(ip)
    db = server.get_or_create_db(database)
    couchdbkit.designer.push(os.path.join(path, '_design', 'users'), db)
