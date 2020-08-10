Introduction
============

This Django application provides models and helper code to help a Django app manage some data.

This data store can be several different types of data. Each type can have separate configuration options and schemas for the data it holds.

Each type can hold a number of Records. Each record has a public ID (slug type) and one block of JSON.

The system keeps a history of all changes to the data, by way of Events. Each event has one or more Edits attached.
Each event can optionally be linked to a user account and have a comment attached.

The system also provides a way for edits to be suggested, and a moderator to approve or reject these edits.

Each Edit can provide a whole new block of JSON to replace the current value with, or a smaller JSON value that will be merged into the current JSON value.
Edits can also approve or reject previous edits.

The application provides a admin web interface which any Django user with the correct permission can access.
This gives them access to call any operation on the data and a handy way to look at the current state of the data.

But it is anticipated most applications will include this code as a library and then provide their own application that
will provide user-friendly interfaces and can build meaning on top of the JSON data.
In this repository an example application is included to illustrate this.

To help users work with the data each type can also have:

* A JSON Schema file against which data will be validated.
* A spreadsheet guide form file that lets users download spreadsheets with the existing data, edit them and import them.
