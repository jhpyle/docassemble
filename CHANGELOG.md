# Change Log

## [0.1.41] - 2017-08-23
### Added
- Configuration directive `require referer` that allows users who use
  referer blockers to use **docassemble**.

## [0.1.40] - 2017-08-23
### Changed
- Upgraded from Debian jessie to Debian stretch
### Added
- Ability to specify filenames in `attachment` blocks using `code`.
### Fixed
- Error when GIFs inserted into RTF file.

## [0.1.39] - 2017-08-20
### Added
- Page where administrator can add users manually without going
  through invitation process.
### Fixed
- Non-ASCII characters in PDF field defaults no longer stripped out
  when scanning through utilities.

## [0.1.38] - 2017-08-16
### Fixed
- Bug in Alembic upgrade process

## [0.1.37] - 2017-08-16
### Changed
- Fields with `datatype: checkboxes` now have a "None of the above"
  option by default, and input validation ensures that something is
  checked.  The `none of the above` field modifer configures it.
- After registration, users will bypass the "Interviews" screen and
  go right back to their interview, if they have started an interview.
### Added
- Option in `fields` called `uncheck others` when `datatype` is
  `yesno`, `noyes`, `yesnowide`, or `noyeswide`.  Enables a yes/no
  field to act as a "None of the above" option.
- "Upgrade docassemble" button on the "Update a package" page.
### Fixed
- Automatic login after registration was not working, so users had to
  enter username and password information twice.
- Improved CSS for when name of interview on mobile is too long to fit
  in navigation bar.
- Non-ASCII characters in PDF fields when scanning through utilities
  no longer cause an error.
- Fixed problem introduced in 0.1.22 where interview data would be
  destroyed when switching back to an interview during the same session.

## [0.1.36] - 2017-08-13
### Fixed
- Small typo that made 0.1.35 unusable.

## [0.1.35] - 2017-08-13
### Added
- Support for help text next to choices in a multiple choice list.
### Changed
- Database upgrades now handled by alembic by default.  See the 'use
  alembic' configuration directive.
- Extension packages no longer depend on the docassemble.base or
  docassemble.webapp packages.  As a result, installation of an
  extension package will no longer trigger a total software update.
  If you want to upgrade docassemble, upgrade docassemble.webapp.
  Note that packages created in earlier versions will still have these
  dependencies until they are regenerated in the Playground.  You can
  always edit 'install_requires' in the setup.py file.
### Fixed
- Bug fixes to SMS interface.

## [0.1.34] - 2017-08-10
### Fixed
- Checkboxes became DADicts a few weeks ago but the auto-gathering
  system on them was not turned off; it is turned off now.

## [0.1.33] - 2017-08-09
### Fixed
- Backwards compatibility for interviews started before 'nav' added as
  a variable in the user dictionary.
- Extension packages now depend on docassemble.webapp so that when a
  package is updated, all of docassemble is updated, not just
  docassemble.base.

## [0.1.32] - 2017-08-08
### Changed
- force_ask() can ask a series of questions
### Added
- Configuration directives for customization of global Javascript and
  CSS
- Configuration directives for customization of start page and
  interview list

## [0.1.31] - 2017-08-07
### Changed
- Review page buttons now Ajax
- Screen reverts to review page after field edit
### Fixed
- Problem with PDF/A due to old version of pdfx

## [0.1.30] - 2017-08-07
### Added
- PDF/A support
- Navigation bar option
### Fixed
- Problem with files when user logged in

## [0.1.29] - 2017-08-03
### Added
- Input validation with Python code
- Input validation for dates, in addition to the limited Javascript validation

## [0.1.28] - 2017-08-01
### Fixed
- DADict object now defines ask_object_type by default
- Bug with 'using' combined with 'ml'

## [0.1.27] - 2017-07-31
### Added
- ml and mlarea data types and training system
### Fixed
- Better error message in Playground when interview has a syntax error
- Problem with temporary files introduced in 0.1.23 that was causing
  PDF fill-in to fail

## [0.1.26] - 2017-07-25
### Fixed
- Minor git issue again

## [0.1.25] - 2017-07-24
### Changed
- Back button style
### Fixed
- labelauty issue

## [0.1.24] - 2017-07-24
### Fixed
- Minor git issue

## [0.1.23] - 2017-07-23
### Changed
- Additional deletion of temporary files through cron job
### Fixed
- Improved performance by optimizing markdown and regex
- Newer version of labelauty, with modifications to include benefits
  of older version, for compatibility with IE/Edge

## [0.1.22] - 2017-07-22
### Added
- read_qr() function
- new_object_type option for groups
### Changed
- The default for the debug configuration directive is now True
### Fixed
- The "disable others" field modifier can now be used on a field with
  the same variable name as that of another field on the same page
- Term definition Markdown is now converted to HTML
- Fixed bug with code blocks using iterators
- Fixed problem with document attachments affecting data storage and
  multiple application servers
- Playground run now resets page counter

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
