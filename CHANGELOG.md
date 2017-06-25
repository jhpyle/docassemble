# Change Log

## [0.1.16] - 2017-06-24
### Added
- GitHub integration
- dow_of() function
### Changed
- Changed PyPI username and passwords from a configuration setting to
  a user setting
### Fixed
- More stable transition when transitioning server from non-cloud data
  storate to cloud data storage
- month_of() now uses defined language/locale rather than system
  locale when word_of is True
- Executables that run as root no longer writable by www-data
- Turned off auto-start on sync supervisor process

## [0.1.15] - 2017-06-18
### Added
- SMS option for two-factor authentication
- Option for requiring confirmation of user e-mail addresses
### Fixed
- Problem with apt-get update at start of Dockerfile

## [0.1.14] - 2017-06-17
### Changed
- renamed configuration directives from "second factor" to "two factor"

## [0.1.13] - 2017-06-17
### Added
- Two-factor authentication
- Phone login

## [0.1.12] - 2017-06-06
### Changed
- To facilitate GitHub workflow, attempted to preserve timestamps on
  filenames in Zip files

## [0.1.11] - 2017-06-04
### Changed
- Increased font size for better mobile experience

## [0.1.10] - 2017-06-03
### Changed
- Look and feel of signature pages now match regular interface on
  larger screens

## [0.1.9] - 2017-06-02
### Fixed
- Various bugs from previous version

## [0.1.8] - 2017-06-01
### Fixed
- Bug with Google Drive

## [0.1.7] - 2017-06-01
### Fixed
- Bug with server-side encryption

## [0.1.6] - 2017-05-30
### Added
- Google Drive integration

## [0.1.5] - 2017-05-28
### Fixed
- Bug with logins in the middle of interviews

## [0.1.4] - 2017-05-27
### Changed
- New algorithm for generic variables and index variables
### Added
- Additional examples

## [Unreleased] - 2017-05-26
### Changed
- PDF fill-in files now editable
- Started using bumpversion
- Started a changelog
