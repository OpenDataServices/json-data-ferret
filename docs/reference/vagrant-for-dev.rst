Vagrant for Developers
======================

A vagrant box exists to help developers.

Simply run `vagrant up`.

After `vagrant ssh`, run `cd /vagrant` and `source .ve/bin/activate`.

Run Web Server
--------------

.. code-block:: bash

    python manage.py runserver 0:8000

Go to `http://localhost:8000`

Set up app for the first time
-----------------------------

Run normal Django database migrations.

Create a superuser via the normal django command line tool:

    python manage.py createsuperuser

Run the webserver.

Log into `/admin`.

Add some `Types` records in the `Jsondataferret` section, for use with the exaple app :

* public id: `project`, title: `Project`
* public id: `org`, title: `Organisation`

Python Packages Upgrade
-----------------------

.. code-block:: bash

    pip-compile --upgrade
    pip-compile --upgrade requirements_dev.in

Tests
-----

Run tests  (with Vagrant DB credentials):

.. code-block:: bash

    JSONDATAFERRET_DATABASE_NAME=test JSONDATAFERRET_DATABASE_USER=test JSONDATAFERRET_DATABASE_PASSWORD=test python manage.py test

Code Quality
------------

Clean up code before commit:

.. code-block:: bash

    isort --recursive djangoproject/ jsondataferret jsondataferretexampleapp/ setup.py docs/
    black djangoproject/ jsondataferret jsondataferretexampleapp/ setup.py docs/
    flake8 djangoproject/ jsondataferret jsondataferretexampleapp/ setup.py docs/


Reset Database
---------------

    sudo su postgres
    psql -c "DROP DATABASE app"
    psql -c "CREATE DATABASE app WITH OWNER app ENCODING 'UTF8'  LC_COLLATE='en_GB.UTF-8' LC_CTYPE='en_GB.UTF-8'  TEMPLATE=template0 "
    exit
    python manage.py migrate

