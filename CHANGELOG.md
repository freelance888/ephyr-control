Ephyr Control changelog
===============

All user visible changes to this project will be documented in this file. This project uses [Semantic Versioning 2.0.0].

## v1.1.0
### Added
- Labels to Restream
- Second `backup2` input
- `removeRestream`, `removeOutput`, `enableOutput`, `disableOutput` mutations
- Script to subscriber tu multiple Ephyr's


## v1.0.1
### Fixes
- Bug with websockets connection broking after a few seconds.
### Changed
- Shorter imports for users of Subscription API

## v1.0.0
### Removed
- Obsolete code for controlling volume.
- Obsolete examples.
### Added
- Structural dataclasses representing Ephyr's state.
- Remote control using GraphQL api.
- Asynchronous subscriptions

## v0.1.0
### Added
- Configuring by `mix.client.json`
- Change audio volume level for specific language stream


[Semantic Versioning 2.0.0]: https://semver.org