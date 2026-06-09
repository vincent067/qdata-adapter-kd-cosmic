# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.3] - 2026-06-09

### Added

- `create_object` now supports `_api_version` in data (e.g. `"v2/null"` for EasyCloud APIs)
- `create_object` automatically wraps dict into list for `qeasy*` operations (e.g. `qeasyadd` requires `{"data": [...]}`)
- Added unit tests for `_api_version` path building and `qeasyadd` list wrapping

## [0.1.2] - 2026-06-09

### Added

- `create_object` now supports custom operation types via:
  - `data["_operation"]`` (e.g. `"qeasyadd"` for Kingdee EasyCloud add APIs)
  - explicit `operation` parameter (takes precedence over `data._operation`)
- Added unit tests for `create_object` covering default `save`, custom operation via data, and explicit operation parameter

### Changed

- Abstract `create_object` signature in `BaseInterface` updated to accept optional `operation` parameter
- `KdCosmicAdapter.create_object` proxy updated to forward `operation` to the interface

## [0.1.1] - 2026-06-04

### Added

- Initial release of qdata-adapter-kd-cosmic
- Basic adapter structure with KdCosmicAdapter
- Authentication implementation
- Core data operations (list, get, create)
- Complete test suite with pytest

## [0.1.0] - 2026-06-04

### Initial Release

- Project scaffold generated
- Base adapter implementation
- CI/CD configuration
