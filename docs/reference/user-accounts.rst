User Accounts
=============

Normal Django user accounts are used.

The permission `Admin - Can Admin All Data Managed by JSON Data Ferret` is required for a user to access the admin web interface for the app.
This will give them full permissions to change and moderate data.

This permission is not needed if a user calls some custom code in another app that calls one of the libraries Python API's. In that case, it's up to the calling code to check any user permissions as required.

