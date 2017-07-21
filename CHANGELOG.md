# Change Log

## [0.1.22]
### Added
- read_qr() function
### Changed
- The default for the debug configuration directive is now True
### Fixed
- The "disable others" field modifier can now be used on a field with
  the same variable name as that of another field on the same page
- Term definition Markdown is now converted to HTML

## [0.1.21] - 2017-07-14
### Changed
- checkboxes now create DADict objects rather than dict objects
### Added
- all_true() and all_false() methods for DADict
### Fixed
- Fixed bug when user invitation e-mail fails to send
- Error message when code and question blocks are combined

## [0.1.20] - 2017-07-10
### Fixed
- Fixed another bug in edit user profile page

## [0.1.19] - 2017-07-10
### Fixed
- Fixed bug in edit user profile page.

## [0.1.18] - 2017-06-28
### Added
- Pull package into Playground with PyPI
### Changed
- "initial" directive now accepts code, just like "mandatory"
- Error page now returns 404 instead of 501 when user tries to access
  an interview file that does not exist.
### Fixed
- Added MANIFEST.in so that README.md is included when packages are
  bundled using setup.py
- Uploading files to Playground now checks to make sure the file is
  YAML and is readable.

## [0.1.17] - 2017-06-24
### Changed
- Updated the required system version to 0.1.17
### Fixed
- If you updated the Python packages to 0.1.15 or 1.1.16 without
  updating the system, you may have experienced an error.  Now, if
  changes to the Python packages alter the necessary PostgreSQL
  columns or tables, those columns and tables will be changed upon
  reboot after the updating of the Python packages, and will not have
  to wait until an upgrade of the system.
- Fixed reference in Dockerfile to non-existent file

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
