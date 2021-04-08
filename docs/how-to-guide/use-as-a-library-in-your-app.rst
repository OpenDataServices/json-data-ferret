Use as a library in your app
============================

Include library
---------------

Add as a requirement:

.. code-block:: bash

    -e git+https://github.com/OpenDataServices/json-data-ferret.git@v0.3.0#egg=jsondataferret

(Choosing the version you want)

In your Django settings file, add this to INSTALLED_APPS:

.. code-block:: bash

    INSTALLED_APPS = [
        ...
        "jsondataferret.apps.JsondataferretConfig",
        ...
    ]

Set up Types
------------

Now you need to set up the types you want to use. You do this by creating `Type` models. You can do this by any usual Django means - logging in to admin interface as a super user is probably easiest.

In your Django settings file you may also want to add a `JSONDATAFERRET_TYPE_INFORMATION` setting with extra information.
:doc:`See the Configuration reference for more <../reference/configuration>`



Use from your custom code
-------------------------

You can now use the Python API and read the models of this library as you require.
:doc:`See the Python API reference for more <../reference/python-apis>`

Web UI
------

If you want people to be able to use the Web UI, you must first enable it and give the relevant user accounts permission.

In your Django app's urls file add:

.. code-block:: bash

    urlpatterns = [
        ...
        path("jsondataferret/", include("jsondataferret.urls")),
        ...
    ]

You need to set the correct permissions for each user of the web UI. You can do this by any means Django allows - e.g. logging into the admin interface as a superuser.
:doc:`See the reference for more <../reference/user-accounts>`

