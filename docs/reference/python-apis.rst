Python API's
============

Read from models directly
-------------------------

There are Django models with information, and currently you are encouraged to read from them to look up certain information.

In particular, the `Record` model contains some cached columns of the latest data.

Write to models directly
------------------------

You can write to the `Type` model, to set up new types.

Do NOT write to the `Record`, `Event` or `Edit` models directly. Instead, use the Python API's below (in particular `jsondataferret.pythonapi.newevent`) to write new data to the system.

jsondataferret.pythonapi.newevent
---------------------------------

The function `newEvent` is used to write new data to the system.

It should be passed:

* `datas` - an array of objects, described below.
* `user` - A Django User
* `comment` - A text comment

The items in the `datas` array should be instances of one of the following classes:

* `NewEventData` - used to add new data to the system.
* `NewEventApproval` - used to approve an edit that has previously been written to the system (moderate it successfully)
* `NewEventRejection` - used to reject an edit that has previously been written to the system (moderate it and fail)

jsondataferret.pythonapi.purge
------------------------------

The function `purge_record` is used to delete a record and all associated data from the system permanently. There is no undo.

jsondataferret.pythonapi.runevents
----------------------------------

The function `clear_data_and_run_all_events` clears all caches on Records, then tries to updates them all to the latest value.

This should not have to be run in normal operations, but may be needed to clear a problem.
