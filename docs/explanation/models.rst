Models
======

Type
----

The app can process data of several different types.

Types should be created as records in the database.

However most of the configuration of types happens in the Django configuration.

Each type is identified by it's `public_id`, which should be unique.

Record
------

Each type can have multiple records.

Each record is identified by it's `public_id`, which should be unique in it's type.

Records are not created manually, but are instead created for you as soon as an Edit happens on a new `public_id`.

A record contains only basic information; it is a object/database row for Edits to link to.

It however also contains some columns of cached information, designed to make it easy for other apps to get data from the system.

These are:

* `cached_exists` - boolean. A record is said to exist if there has ever been any data approved for it.
* `cached_data` - JSON. The latest version of the actual data.
* `cached_jsonschema_validation_errors` - If a JSON Schema is specified, this will contain JSON Schema errors for the latest data.

Event
-----

Changes happen to data by way of Events. Think of them as a commit in git.

Each event can be linked to one or more edits in several different ways. See below.

Note:

* an event may only contain new data to be moderated, and thus may not always change the actual data in the system.
* an event may contain edits that are created and approved in the same event - data that was not moderated but approved instantly, in other words.

Each event is identified by it's `public_id`, which should be unique - but these are set automatically for you.


Edit
----


Each edit contains actual data:

* `mode` - Replace or Merge. This is how the edit is applied to the record.
* `data_key` - Not currently used - leave as the default of `/`
* `data` - The actual JSON data to merge or replace.

Each edit is linked to at least one Event by:

* `creation_event` - The event that created it. This must be set.

Each edit can also have one (but not both) of these links set:

* `approval_event` - The event that approved this data. (Note this can be the same event as the `creation_event`.)
* `refusal_event` - The event that rejected this data.

Each edit is identified by it's `public_id`, which should be unique - but these are set automatically for you.
