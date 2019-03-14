# upload_app

Flask-based web app with register/login capabilities where users upload their C/C++/Pascal/Java sources to be asynchronously tested by the app with the results returned to them live. Current mode tests using predefined input files. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Python 2.7 (not tested on 3)
* pip
* Redis
* CouchDB
* svn (to easily get project files)
* gcc/g++/fpc/javac (depending on what you want to compile)

Besides packages installed with ```pip```, you also need Redis and CouchDB installed on your system. A quick guide to install Redis can be found [here](https://redis.io/download), while CouchDB can be installed from [here](http://couchdb.apache.org/#download). They may also be available in your preferred distribution's package manager.

### Installing and running

Get the sources (since they are residing in a subfolder of the repository your best solution is to use ```svn export```)

```
svn export https://github.com/GabrielNagy/Year3Projects/trunk/WT/Project/upload_app
mkdir upload_app/upload_app/run/build
```

Wrap them in a ```virtualenv``` for easier package management.

```
virtualenv upload_app
cd upload_app
source bin/activate
```

Install the required packages, then install the ```upload_app``` package.

```
upload_app$ pip install -r requirements.txt
upload_app$ pip install -e .
```

Export flask needed global variables, run helper script to create database and views in CouchDB, then run flask app.

```
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

## Author

* me!
