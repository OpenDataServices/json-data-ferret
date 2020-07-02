# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- In settings, `jsonschema_file` key changed to `json_schema`. Contents should now be the actual schema, not a filename.

### Added

#### Features

- Add way to write an event comment when making event. Show in UI (both viewing and when taking actions).
- Add tabs UI to some pages
- Add breadcrumbs
- Add list of records that need moderation
- Add Edit using JSON Editor and JSON Schema

#### Python API

- Add apply_edit_get_new_cached_data to utils
- Add does_this_create_or_change_record to NewEventData
- Add Record.objects.filter_needs_moderation_by_type

## [0.1.0] - 2020-05-29

First release of new project
