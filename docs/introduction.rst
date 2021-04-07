Introduction
============

This is a Django application that manages JSON data with a full history of changes and moderation facilities.

What this provides
------------------

This Django application provides models and helper code to help a Django app manage some data.

There can be several types of data stored.

Each type can have:

* A JSON Schema file against which data will be validated, as a way to provide a web form to edit the data.
* A spreadsheet guide form file that lets users download spreadsheets with the existing data, edit them and import them.

Each type can hold a number of Records. Each record has a public ID (slug type) and one block of JSON.

The system keeps a history of all changes to the data, by way of Events. Each event has one or more Edits attached.
Each event can optionally be linked to a user account and have a comment attached.

The system also provides a way for edits to be suggested, and a moderator to approve or reject these edits.

Each Edit can provide a whole new block of JSON to replace the current value with, or a smaller JSON value that will be merged into the current JSON value.

Edit's can be approved straight away, or a future events can approve or reject edits.

Provided via a web interface
----------------------------

The application provides a admin web interface which any Django user with the correct permission can access.

This gives them access to call any operation on the data and a handy way to look at the current state of the data.

Provided via Python API's
-------------------------

But it is anticipated most applications will include this code as a library and then provide their own application that
will provide user-friendly interfaces and can build meaning on top of the JSON data.

In this repository an example application is included to illustrate this.

