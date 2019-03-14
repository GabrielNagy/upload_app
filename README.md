# upload_app

Flask-based web app with register/login capabilities where users upload their C/C++/Pascal/Java sources to be asynchronously tested by the app with the results returned to them live. Current mode tests using predefined input files.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Docker version update

Just run ```start_all.sh```. It should bring up nodes one by one in the right order to avoid race conflicts. You may also want to modify or get rid of nginx entirely for testing purposes.

All logic resides in a single Python source file, so if you value your sanity don't go near it. I never got to properly rewrite it. One day, maybe.

### Prerequisites

* Python 2.7 (not tested on 3)
* pip
* Redis
* CouchDB
* gcc/g++/fpc/javac (depending on what you want to compile)

Besides packages installed with ```pip```, you also need Redis and CouchDB installed on your system. A quick guide to install Redis can be found [here](https://redis.io/download), while CouchDB can be installed from [here](http://couchdb.apache.org/#download). They may also be available in your preferred distribution's package manager.

### Installing and running

Clone the repo

``` bash
mkdir app/upload_app/run/build
```

Wrap sources in a ```virtualenv``` for easier package management.

``` bash
virtualenv .venv
source ./.venv/bin/activate
```

Install the required packages

``` bash
pip install -r requirements.txt
```

Export flask needed global variables, run helper script to create database and views in CouchDB, then run flask app.

``` bash
upload_app$ export FLASK_APP=upload_app
upload_app$ export FLASK_DEBUG=1
upload_app$ python upload_app/setup_db.py
upload_app$ flask run
```

Run a celery worker instance to be able to test uploaded files

```
upload_app$ celery worker -A upload_app.upload_app.celery --loglevel=info
```

## Running a test

Assuming you already created and logged in to your account, to run a quick test just upload ```tests/kfib/implementations/kfib.cpp``` to the web app, then click on Begin test.

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [CouchDB](http://couchdb.apache.org/) - Database where user info is stored
* [Redis](https://redis.io/) - Database where celery data is stored
* [Celery](http://www.celeryproject.org/) - Distributed Task Queue
* [Bootstrap](https://getbootstrap.com/)
