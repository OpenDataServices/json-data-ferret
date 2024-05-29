# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.7.1] - 2024-05-29

### Fixed

- get_records() on Event model could have SQL error due to lack of space

## [0.7.0] - 2022-10-26

### Added

- Add get_new_data_when_event_applied_to_latest_record_cached_data to jsondataferret.pythonapi.newevent.NewEventData

## [0.6.0] - 2022-06-29

### Changed

- For calculating diffs, use already used "json_merge_patch" library. 
  The library "jsondiff" caused crashes by returning data that was not valid JSON.

## [0.5.1] - 2022-06-10 - The improved history release that works with merge mode

### Fixed

- Edit & CachedRecordHistory - fix crash in get_data_diff_previous_cached_record_history_html
- Edit - make get difference methods work with MERGE mode
- Web UI for an event: Shows correct data in MERGE mode. Shows edit data with no modifications.

### Added

- Edit has a new method get_new_data_when_edit_applied_to_data
- Edit has a new method get_new_data_when_edit_applied_to_latest_record_cached_data
- Edit has a new method get_new_data_when_edit_applied_to_previous_cached_record_history
- Edit has a new method get_new_data_when_edit_applied_to_previous_cached_record_history_html

### Changed

- apply_edit_get_new_cached_data in utils is now replaced with edit.get_new_data_when_edit_applied_to_latest_record_cached_data()
  But the old function is left for backwards compatibility

## [0.5.0] - 2022-06-10 - The improved history release

### Added

- Added CachedRecordHistory model
- Added new code for working with this:
-- Edit has a new method get_data_fields_include_differences_from_previous_data()
-- Edit has a new method get_previous_cached_record_history
-- Edit has a new method get_data_diff_previous_cached_record_history
-- Edit has a new method get_data_diff_previous_cached_record_history_html
- Event.get_records has new optional parameter approved_edits_only
- get_field_list_from_json_with_differences method added to utils
- Added new things to Web UI made possible by new data:
-- Web UI for an event: shows you previous JSON, diff, fields. Shows you approved changes per record. Has separate screen for each edit. 
- Added new requirement, jsondiff


Note: After this version is installed, the runeventstreamtodatabase cli command must be run to populate the new CachedRecordHistory cache.

## [0.4.0] - 2022-06-09

### Fixed

- Field type changed to Django JSONField, to be compatible with Django 3.2 and 4
- Lock default_auto_field to AutoField
- Web UI moderate screen; if 2 edits waiting to be moderated at once, the JSON/Fields tabs were broken
- Python packaging fixed so it can be used via PyPi

### Changed

- Set Django minimum version to 3.2 (this is minimum still supported)
- Set Python minimum version to 3.8 (this is minimum Django 4 supports, comes with Ubuntu 20.04 LTS and is what our current production uses)
- In web UI, Only leave moderate page if an action is actually carried out. 
  If user presses submit but has not selected any actions, stay on same page.
- Web UI shows fields that are removed by an edit on the moderation screen
- Web UI on the list events screen: shows some records the event is about
- Web UI List events page can be filtered by created date

### Added

- Record.get_cached_data_fields and Edit.get_data_fields return an new key in each item "key". This should be unique, unlike "title", which may not be.
- Edit has a new method get_data_fields_include_differences_from_latest_data() which returns a list of fields with the new boolean key different_from_latest_value
- Web UI shows changed fields in bold on moderation screen
- Event has new method get_records to return records linked in the event
- Event has new method get_records_summary to return first 4 records and a boolean flag if there are more

## [0.3.0] - 2021-01-06

### Fixed

- In web UI, on event detail page is said "Edits Approved" when it should have said "Edits Refused"

### Changed

- In web UI, order records

### Added

- In web UI, show more info when moderating records
- In web UI, paginate list of events and records
- In web UI, add heading on event details page so if 
  there is more than one edit it's easier to see where one edit stops and the next one begins.
- New function and CLI command to purge a record from database entirely

## [0.2.0] - 2020-07-02

### Changed

- In settings, `jsonschema_file` key changed to `json_schema`. Contents should now be the actual schema, not a filename.

### Added

#### Features

- Add way to write an event comment when making event. Show in UI (both viewing and when taking actions).
- Add tabs UI to some pages
- Add breadcrumbs
- Add list of records that need moderation
- Add Edit using JSON Editor and JSON Schema
- New command `updatejsonschemavalidations` - after a JSON Schema has changed, run to update all relevant cached information.

#### Python API

- Add apply_edit_get_new_cached_data to utils
- Add does_this_create_or_change_record to NewEventData
- Add Record.objects.filter_needs_moderation_by_type

## [0.1.0] - 2020-05-29

First release of new project
