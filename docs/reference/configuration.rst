Configuration
=============

Types
-----

Some configuration options for each different type can be set in the normal Django configuration.

.. code-block:: python

    JSONDATAFERRET_TYPE_INFORMATION = {
        "type1": {
            "json_schema": {...},
            "spreadsheet_form_guide": "full filename"
        },
        "type2": {
            "json_schema": {...},
            "spreadsheet_form_guide": "full filename"
            "fields": [...],
        },
    }

The key for each type (eg `type1`, `type2`) should match the `public_id` field in the `Type` record in the database.

JSON Schema
~~~~~~~~~~~

If this is set,

* Any data will be validated against the JSON Schema and any errors or success will be shown to the user in the Web UI.
* The user will be able to edit the data in a web browser using a JSON Schema widget.

The value should be the actual JSON Schema as a python dictionary. You will probably load it in the settings module.

.. code-block:: python

    with open(...) as fp:
        org_json_schema = json.load(fp)

    JSONDATAFERRET_TYPE_INFORMATION = {
        "org": {
            "json_schema": org_json_schema,
        },

This is optional; if not set basic operations will still work.

Spreadsheet Guide Form
~~~~~~~~~~~~~~~~~~~~~~

If this is set,

* The user will be able to download and import a spreadsheet in the Web UI.

The value should be the filename of the spreadsheet. Ideally make it a absolute filename.

`See the documentation for the Spreadsheet forms library for more on guide forms. <https://spreadsheet-forms.readthedocs.io/en/latest/>`_

This is optional; if not set basic operations will still work.

Fields
~~~~~~

If this is set,

* The user will see a list of data from the JSON data presented as fields.

The value should be a list of python dictionaries.

If there is only one value in the data, the dictionary should look like:

.. code-block:: python

    {"key": "/project_name/value", "title": "Project Name (value)"},

The `key` should be the JSON path to the value and the `title` is what is shown to the user.

Where the data contains a list of dictionaries, you can also specify that.
In this mode, you specify where the list is in the data then specify fields for each item in the list.

.. code-block:: python

    {
        "type": "list",
        "key": "/outcomes",
        "title": "Outcomes",
        "fields": [
            {"key": "/outcome", "title": "Outcome"},
            {"key": "/definition", "title": "Definition"},
        ],
    },

This is optional; if not set basic operations will still work.
