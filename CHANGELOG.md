# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]


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
