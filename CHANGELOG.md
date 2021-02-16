# Change Log

## [1.2.31] - 2021-02-16
### Added
- The `post` option for `need`.
### Changed
- Deleting a package in the Playground will now delete the memory of
  the last pull of that package.

## [1.2.30] - 2021-02-13
### Fixed
- False positive infinite loop detection with `objects` block.

## [1.2.29] - 2021-02-12
### Fixed
- Package Management issue with waiting for restart.

## [1.2.28] - 2021-02-09
### Changed
- In the question data, `decoration_url` and `decoration_name` have
  been converted to a `decoration` dictionary.
### Fixed
- The `title_case` function now converts its parameter to a string.
- Package Management issue with waiting for restart.

## [1.2.27] - 2021-02-05
### Fixed
- Restored default behavior of not converting to HTML in question
  data.

## [1.2.26] - 2021-02-04
### Changed
- Added `variable_name` to items under `attachments` in the JSON
  representation of a question.
### Fixed
- Removed use of `certbot-auto`.

## [1.2.25] - 2021-01-27
### Added
- The `region` parameter under the `google` Configuration directive,
  for biasing the address autocomplete feature.
### Fixed
- Unicode characters in PDF forms were altered if they were not part
  of `latin1`.

## [1.2.24] - 2021-01-24
### Not changed
- The license.  (Just in case you thought the 1/14/2021 @docassemble
  Twitter thread about the dystopian MIT-SAFE License was real.)
### Changed
- The `from_url()` method will now raise an exception if there is an
  error retrieving the URL.
- The `avconv` Configuration directive is now called `ffmpeg`.
- Uploading a video no longer runs a conversion to `.ogg`.
### Added
- Option for connecting to a PostgreSQL database using SSL with `db`
  and other database configurations.  A system update is required to
  use this feature.
### Fixed
- Problem writing error messages to the logs when Mailgun mail sending
  fails.
- Error in `pdf_concatenate()` when JavaScript in a PDF is text
  instead of bytes.
- Non-graceful failure on Google Drive configuration page when API for
  obtaining a file listing raises an exception.

## [1.2.23] - 2021-01-07
### Changed
- Expanded the information available in the data view of a question.
- Unicode passed in URL arguments is no longer escaped.
### Fixed
- The `next` parameter now contains the session ID upon attempting to
  access a session in an interview with `require login`.
- `depends on` and `on change` now can be used with generic object
  and/or index variables even when the fields being changed do not
  literally match the variable name specified in `depends on` or `on
  change`.
- Problem with `show if` when there are two fields with the same name
  visible on the screen at the same time.

## [1.2.22] - 2021-01-04
### Changed
- Expanded the information available in the data view of a question.
### Fixed
- Issue with combobox update triggers.
- Issue with `DADict` objects in `code` for multiple choice lists.

## [1.2.21] - 2020-12-29
### Changed
- The `list collect` feature will now show the `minimum_number` of
  entries if `minimum_number` is set.

## [1.2.20] - 2020-12-28
### Fixed
- Error with `generic object` inheritance.

## [1.2.19] - 2020-12-26
### Fixed
- Error in `.object_name()`.

## [1.2.18] - 2020-12-22
### Fixed
- Adapted to new version of `pip`.

## [1.2.17] - 2020-12-22
### Changed
- Different startup mechanism for `celery`.
- Removed `--force-reinstall` from `pip` invocation.

## [1.2.16] - 2020-12-15
### Added
- The `chain` function from `itertools`.
### Fixed
- Forced deletion of `Flask-User`.

## [1.2.15] - 2020-12-14
### Fixed
- Pinned dependencies of fork dependencies.

## [1.2.14] - 2020-12-09
### Fixed
- Problem with the way in which `pip` was invoked, given new version
  of `pip`.

## [1.2.13] - 2020-12-09
### Fixed
- Typo in `setup.py`.

## [1.2.12] - 2020-12-09
### Changed
- Dependencies on `aloe` and `selenium`.
### Fixed
- Interview filenames with spaces in the Configuration were disregarded.

## [1.2.11] - 2020-12-07
### Added
- XLIFF support.
- The `user can request developer account` Configuration directive.
### Fixed
- User information that non-privileged users are not allowed to edit
  in Profile but that was set with code was overwritten when user
  edited their user profile.
- Problem with `datereplace.js` in recipe.

## [1.2.10] - 2020-12-05
### Added
- The `raw` datatype.
### Changed
- Additional items colorized in spreadsheet translations.
- HTML stripped from fields with `datatype` of `text`.
### Fixed
- Issue with server-side validation where multiple `question` blocks
  have the same `id`.

## [1.2.9] - 2020-12-04
### Fixed
- Bug in `comma_and_list()`.

## [1.2.8] - 2020-12-03
### Changed
- Different limiting mechanism for the nested use of
  `include_docx_template()`.
- Enabled the `md_in_html` extension of the `Markdown` package.

## [1.2.7] - 2020-12-02
### Added
- The `new window` option to `action buttons`.
### Fixed
- Ajax error with xhr responses.

## [1.2.6] - 2020-12-01
### Fixed
- Error in `update_terms()`.

## [1.2.5] - 2020-11-30
### Fixed
- JavaScript error in Internet Explorer.

## [1.2.4] - 2020-11-29
### Changed
- The `setup.py` file created by the Playground now sets the minimum
  version of dependencies to the latest version on PyPI that is not
  more recent than the version installed on the server.
### Fixed
- Browser warning about Google Analytics cookies.

## [1.2.3] - 2020-11-29
### Fixed
- Upgraded to new version of Azure Blob Storage API.

## [1.2.2] - 2020-11-29
### Fixed
- Reverted Azure Blob Storage API version.

## [1.2.1] - 2020-11-28
### Fixed
- Error on Package Management page.

## [1.2.0] - 2020-11-28
### Changed
- Upgraded Python to version 3.8 and upgraded dependencies.  These
  changes require a system upgrade.  See
  https://docassemble.org/docs/docker.html#upgrading for instructions
  on how to perform a system upgrade.  Because Python changed between
  version 3.6 and and 3.8, you should test your code carefully to make
  sure it still works in Python 3.8.
- Among other upgrades, Bootstrap has been upgraded to version 4.5.3.
  If you are using Bootstrap themes, you may wish to upgrade your
  Bootstrap theme.
### Fixed
- Issue with user privileges.

## [1.1.112] - 2020-11-26
### Changed
- Upgrading through Package Management is turned off because the
  upgrade to 1.2.0 requires a system upgrade.

## [1.1.111] - 2020-11-26
### Fixed
- Some Jinja2 filters did not work correctly.

## [1.1.110] - 2020-11-25
### Changed
- The API can now be used to set variables to class names.
### Fixed
- The `sort` Jinja2 filter did not work correctly.

## [1.1.109] - 2020-11-24
### Added
- The `suppress error notificiations` Configuration directive.
- Error message if file upload will exceed `maximum content length`.
### Fixed
- Google Drive synchronization did not work with shortcuts to folders.

## [1.1.108] - 2020-11-22
### Changed
- The `markdown` and `inline_markdown` filters now respect the `type`
  and `start` attributes of `<ol>`.

## [1.1.107] - 2020-11-21
### Changed
- Upgraded LibreOffice (system upgrade required for this change).
### Fixed
- Bug in previous version.

## [1.1.106] - 2020-11-21
### Added
- The `change_numbering` keyword parameter to `include_docx_template()`.

## [1.1.105] - 2020-11-20
### Changed
- The `.make_ocr_pdf_in_background()` method can now handle mixed file
  types.
### Fixed
- Markdown internal anchor links now work in the web interface.

## [1.1.104] - 2020-11-20
### Added
- German translations of country names.
### Changed
- The `states_list()`, `state_name()`, and `subdivision_type()`
  functions now pass output through the `word()` translation system.
### Fixed
- The `language` modifier for an attachment did not work with `docx
  template file` attachments.

## [1.1.103] - 2020-11-19
### Added
- The `temporary session` specifier under `metadata`.
### Changed
- The `countries_list()` and `country_name()` functions will now pass
  country names through the `word()` translation system.

## [1.1.102] - 2020-11-19
### Fixed
- The local PostgreSQL database was being created with the default
  encoding, which did not allow UTF-8 strings to be saved in `jsonb`
  format.
- An `attachment` that uses a different language than the current
  language did not restore the correct language after an exception.

## [1.1.101] - 2020-11-14
### Fixed
- Issue with `interview_url()` and `interview_url_action()` with `i`
  parameter when short URL is in use.

## [1.1.100] - 2020-11-13
### Fixed
- Translation of phrases on registration page.

## [1.1.99] - 2020-11-12
### Changed
- Different logic for whether hyperlinks open in the same tab or a
  different tab.

## [1.1.98] - 2020-11-12
### Fixed
- Bug in `bates_number()`.

## [1.1.97] - 2020-11-10
### Added
- The `/api/clear_cache` endpoint.

## [1.1.96] - 2020-11-08
### Added
- The `lang` URL parameter for non-interview screens.

## [1.1.95] - 2020-11-06
### Fixed
- Unnecessary incrementing of PyPI version.
- Recent installations (since June 25, 2020, possibly) contained a
  Debian security update that disabled ImageMagick's ability to inject
  signature images onto PDFs.  Running `docker stop` and `docker
  start` is required to enable the PDF signature image feature.

## [1.1.94] - 2020-11-03
### Added
- The `set_object_type()` method of `DAList` and `DADict`.
- The `variable` attribute of the return value of `user_info()`.
- The `reset_geolocation()` method of `Address` and the `reset`
  keyword parameter of the `geolocate()` method.
### Fixed
- The `map` Jinja2 filter looked up dictionary items instead of
  attributes.
- Could not mix a Python-based `show if` with a JavaScript-based `hide
  if` or vice-versa.

## [1.1.93] - 2020-10-27
### Fixed
- Markdown in popover field help.

## [1.1.92] - 2020-10-24
### Added
- The `update_terms()` function.
### Changed
- When using `terms`, you can specify that text other than the term
  name should be displayed using `|`.
- When specifying `terms` and `auto terms`, you can use `phrases` and
  `definition` to indicate that multiple terms are associated with a
  single definition.

## [1.1.91] - 2020-10-24
### Fixed
- Bug in GitHub configuration.

## [1.1.90] - 2020-10-20
### Changed
- Enabled a variety of functions to operate as Jinja2 filters.
### Fixed
- Corrected operation of `selectattr` Jinja2 filter.

## [1.1.89] - 2020-10-19
### Added
- The `make_ocr_pdf()` and `make_ocr_pdf_in_background()`, and
  `bates_number()` methods of `DAFile` and `DAFileList`.
- The `reverse()`, `insert()`, and `count()` methods of `DAList`.

## [1.1.88] - 2020-10-16
### Added
- The `required privileges for initiating` specifier under `metadata`.
### Changed
- The JSON format of questions now includes analytics information.
### Fixed
- The `delete_variables` feature of `/api/session` did not work when
  passing the request in JSON format.

## [1.1.87] - 2020-10-14
### Fixed
- False error messages on package update screen.

## [1.1.86] - 2020-10-13
### Changed
- Monitor disabled when `checkin interval` is zero.
### Fixed
- Potential OAuth2 issue with Google Drive.

## [1.1.85] - 2020-10-12
### Added
- The `table css class` screen part.
- The `show_as_markdown()` method for `template`s.
- The `_inline` option for `include_docx_template()`.
- Ability to list multiple files under `docx template file`.
- Ability to set the `pre` and `post` screen parts directly on a
  `question`.
- The `enable if`, `disable if`, `js enable if`, and `js disable if`
  field modifiers.

## [1.1.84] - 2020-10-07
### Fixed
- GitHub commit issue.

## [1.1.83] - 2020-10-07
### Fixed
- `cross site domains` was not being used by CORS for web sockets.

## [1.1.82] - 2020-10-06
### Fixed
- GitHub commit error.

## [1.1.81] - 2020-10-05
### Fixed
- Tweak to focusing on first element.

## [1.1.80] - 2020-10-04
### Added
- The `middle_initial()` method of `Name`.
### Changed
- First input element on the screen is focused only if visible in the
  viewport.
- `[FILE ...]` can now be used with images declared in `images` or
  `image sets`.
### Fixed
- Issue with floating point/integer numbers and input validation.

## [1.1.79] - 2020-09-28
### Fixed
- Problem with using `[TARGET]` inside of `right`.

## [1.1.78] - 2020-09-25
### Fixed
- Issue with `get_info()`.
- Issue with `show if` `code` and generic objects/iterators.

## [1.1.77] - 2020-09-22
### Fixed
- Issue with fix in the previous version regarding group-level file permissions.

## [1.1.76] - 2020-09-22
### Added
- The `question_id` attribute of `user_info()`.
### Fixed
- Issue with group-level file permissions.

## [1.1.75] - 2020-09-20
### Fixed
- Issues with `show if` and `js show if` when multiple fields with the
  same name are on the screen.
- Issues with server-side validation not recreating values on the
  screen on error.

## [1.1.74] - 2020-09-18
### Changed
- Setting `url_args` without causing a change to the `url_args` does
  not cause a new step to be created.
### Fixed
- An empty string `min` or `max` was not being ignored.
- Issue with `generic object`.

## [1.1.73] - 2020-09-13
### Changed
- The `use_word` keyword attribute to `nice_number()` and `ordinal()`
  can be used to force a textual representation of any number.

## [1.1.72] - 2020-09-10
### Fixed
- Removal of `new_session` from URLs formed with `interview_url()`.

## [1.1.71] - 2020-09-07
### Fixed
- Better support for iterables in `comma_list()` and other places.
- Markdown table alignment in Bootstrap.
- Upgraded Pillow.

## [1.1.70] - 2020-09-05
### Added
- The `reply_to` option for `send_email()`.
### Changed
- The current section name is now the label of the `small screen
  navigation: dropdown` button.
- The breakpoint for the mobile signature view is now Bootstrap `xs`.
### Fixed
- Multiple choice fields with empty choices were being set to `None`
  despite `code`-based `show if` deselecting the field.

## [1.1.69] - 2020-09-02
### Added
- The `/api/stash_data` and `/api/retrieve_stashed_data` endpoints.
- The `stash_data()` and `retrieve_stashed_data()` functions.
- The `current` option for `referring_url()`.

## [1.1.68] - 2020-09-02
### Fixed
- Improper verb conjugation for non-English languages.

## [1.1.67] - 2020-09-01
### Fixed
- Issue with two POST requests being sent during inline file uploads.

## [1.1.66] - 2020-08-30
### Added
- The `small screen navigation` option under `features`.
- The `email template`, `email subject`, `email body`, and `email
  address default` options for customizing the functionality of the
  `attachment`/`attachment code` interface.
### Changed
- The horizontal section interface is no longer hidden on small
  screens.
- The vertical section interface becomes the horizontal section
  interface on small screens.
- The default body of the e-mail that the user can send from an
  `attachment`/`attachment code` interface is now translated using the
  phrases `Your document, %s, is attached.` and `Your documents, %s, are
  attached.`.

## [1.1.65] - 2020-08-28
### Added
- The `style` keyword parameter for `interview_url()`.
### Changed
- The `/start/` path for starting an interview now transforms into
  `/run` instead of `/interview`.  It also has a second form for
  referring to the package name and filename (without using
  `dispatch`).
### Fixed
- The Playground "Share" link did not update correctly based on the
  interview being run.

## [1.1.64] - 2020-08-26
### Fixed
- Issue with relative image URLs when embedding in a `<div>`.

## [1.1.63] - 2020-08-25
### Added
- The `corner back button label` screen part.
### Changed
- Upgraded bootstrap-fileupload.
### Fixed
- The `progress` modifier did not behave as described in the documentation.

## [1.1.62] - 2020-08-23
### Added
- The modifiers `include attachment notice`, `include download tab`,
  and `manual attachment list` for tweaking the display of attached
  documents.
### Fixed
- Step advanced when session started with URL parameters.
- The signature screen scrolled at submission.
- The `next` parameter was forgotten when using social login methods.
- The `reconsider` modifier did not work with iterator variables.

## [1.1.61] - 2020-08-20
### Fixed
- JavaScript error with `getField()`.

## [1.1.60] - 2020-08-19
### Changed
- Playground Packages page now reports local date and time of a commit.
### Fixed
- Issue with two file fields or two fields with a `validate` that have
  the same variable name and one is hidden by `show if`.

## [1.1.59] - 2020-08-18
### Fixed
- Cron problem introduced in 1.1.56.

## [1.1.58] - 2020-08-16
### Fixed
- Backwards-compatibility issue related to `DAEmpty` introduced in 1.1.54.

## [1.1.57] - 2020-08-16
### Fixed
- Backwards-compatibility issue related to `DAEmpty` introduced in 1.1.54.

## [1.1.56] - 2020-08-16
### Added
- The `session_local`, `device_local`, and `user_local` objects in the
  interview answers.
- The `require login` `metadata` directive.
### Changed
- When the API is in use, `interface()` will return `'api'`.
### Fixed
- `review` blocks were not compatible with iterator variables.
- `combobox` fields not working right in `list collect` mode.
- `address autocomplete` did not initialize when the address was
  hidden by a `show if`.
- Submission blocked when an empty non-required file upload field was
  present in an embedded interview.

## [1.1.55] - 2020-08-06
### Added
- The `create_session()` function.
- The `package` attribute of the output of `user_info()`.
- The `make_copy` keyword parameter for `all_variables()`.
- The `overwrite` keyword parameter for `set_session_variables()`.
- The `overwrite` parameter for the `/api/session` POST endpoint.
- The `persistent` option for the `/api/session/action` POST endpoint.
- Recipe for passing variables from one session to a newly created
  other session.

## [1.1.54] - 2020-08-04
### Added
- The `attr_name()` method of the `DAObject` class.
- The `dry_run` keyword parameter for `send_email()` and `send_sms()`.
### Changed
- The `str` keyword parameter when initializing a `DAEmpty` object.
- New recipe for gathering multiple signatures; uses a modular
  approach.
### Fixed
- Missing control for `capitalize` in some language functions.
- SendGrid fails when subject line is empty string.
- The `temporary` and `once_temporary` keyword parameters for
  `interview_url_action()` were not working.
- Problem with running interviews in a different tab in Playground on
  Chrome.

## [1.1.53] - 2020-07-29
### Fixed
- Error in Docassemble-Flask-User dependency.

## [1.1.52] - 2020-07-29
### Fixed
- Moved evaluation of section information to post-assembly when
  getting question data.

## [1.1.51] - 2020-07-28
### Added
- The `footer` screen part.
- `terms` and `autoterms` are now included in JSON question data.
### Fixed
- `signature` blocks did not support `continue button field`.
- System message translation system had gaps due to the integration
  with Flask-User's translation system not working as intended.
- Inconsistent behavior of `force_ask()` depending on whether an item
  was listed first or not.

## [1.1.50] - 2020-07-21
### Added
- Feature for viewing names in an interview and the YAML blocks
  associated with them.
### Fixed
- Missing `.copy()` method for `DAList`.
- The `init()` method of the `DAFileCollection` class did not accept
  arbitrary parameters.
- Fully qualified image URLs now work in e-mail HTML.

## [1.1.49] - 2020-07-07
### Fixed
- Additional input validation on parameters passed to APIs.

## [1.1.48] - 2020-07-06
### Fixed
- The `/api/user_info` API endpoint and the `get_user_info()` function
  now do case insensitive searches for e-mail addresses.

## [1.1.47] - 2020-07-05
### Added
- The `store_variables_snapshot()` function.

## [1.1.46] - 2020-07-05
### Fixed
- Error in restart module.

## [1.1.45] - 2020-07-05
### Fixed
- Error in table creation module.

## [1.1.44] - 2020-07-05
### Changed
- The `interview_list()` function, when called without an `action`,
  now uses pagination and returns a tuple instead of a list.  Note
  that this change is not backwards-compatible, so you will need to
  change any code that you have that calls `interview_list()`.
- The `get_user_list()` function now uses pagination and returns a
  tuple instead of a list.  Note that this change is not
  backwards-compatible, so you will need to change any code that you
  have that calls `interview_list()`.
- The `/api/interviews`, `/api/user/interviews`,
  `/api/user/<user_id>/interviews`, and `/api/user_list` GET endpoints
  of the API now use pagination and return a dictionary, not a list.
  Note that this change is not backwards-compatible, so you will need
  to change any code that you have that uses these APIs.
- Removed the `PY2`, `string_types`, and `text_type` names from
  `docassemble.base.util`.  Note that if you have used any of these,
  this change may break your code.
### Added
- The `persistent` optional keyword parameter for
  `mark_task_as_performed()` and related functions.
- The `task_persistent` optional keyword parameter for `send_email()`,
  `send_sms()`, and the `DAWeb` methods.
### Fixed
- Issue with encryption in functions launched during the loading of
  the first page of an interview session.
- Issue with multi-server configurations and the order in which
  container software is updated that can result in some containers
  unable to start.

## [1.1.43] - 2020-06-30
### Changed
- The `complete_elements()` method now returns a `DAList`.  Note that
  this may break existing code that uses `complete_elements()`.  To
  get a plain list of the complete elements, use
  `complete_elements().elements`.
- Spanish ordinal numbers removed.
- Upgraded jQuery and jQuery Validation Plugin.
### Fixed
- Possible fix to iframe reloading issue.

## [1.1.42] - 2020-06-25
### Added
- Aliases for JavaScript functions that have the `da` prefix.
### Fixed
- Jinja2 filter was converting Python built-in types to strings.

## [1.1.41] - 2020-06-22
### Fixed
- Bug in `recursive_eval_textobject()`.

## [1.1.40] - 2020-06-19
### Added
- `question metadata`, `field metadata`, and the `send question data`
  option under `features`.
- The `country` keyword parameter for `.sms_number()`.
- The `field` keyword parameter for `validation_error()`.

## [1.1.39] - 2020-06-17
### Fixed
- Issue with `interview_url_action()` and `force_ask()`.
- Upgraded `docxtpl` and `docx`.

## [1.1.38] - 2020-06-11
### Added
- The `add another label` option for `list collect`.
- The `manual_line_breaks` Jinja2 filter.
### Changed
- The `.all_false()` and related `DADict` methods reflect Python
  notions of true and false values rather than literal equivalence of
  the values to `True` or `False`.
- Sessions that were created using the API will now appear immediately
  in My Interviews.

## [1.1.37] - 2020-06-10
### Fixed
- Attempt to force reinstall of pdfminer.six.

## [1.1.36] - 2020-06-10
### Fixed
- Another attempt to force uninstall of pdfminer3k.

## [1.1.35] - 2020-06-08
### Fixed
- Force uninstall of pdfminer3k.

## [1.1.34] - 2020-06-08
### Fixed
- Error with `objects_from_file()`.

## [1.1.33] - 2020-06-04
### Changed
- `help` can be added to `note` and `html` fields.
### Fixed
- Support for icons in terms.

## [1.1.32] - 2020-05-30
### Fixed
- Issue with `objects_from_file()`.

## [1.1.31] - 2020-05-29
### Fixed
- Issue with nested question file inclusion change in 1.1.30.

## [1.1.30] - 2020-05-29
### Fixed
- Issue with screen reader and labels containing HTML codes.
- Issue with nested question file inclusion.

## [1.1.29] - 2020-05-27
### Fixed
- Issue with `set_save_status()`.
- Issue with checkbox validation text when the "none of the above"
  choice contained HTML.
- Bug prevented `admin` users from changing other users' information
  with the API.

## [1.1.28] - 2020-05-21
### Added
- The `skip undefined` option for `pdf template file`
### Fixed
- Issue with nested `datatype: object` fields in a `list collect`.
- Issue with `disable others` referring to a list in a `list collect`.

## [1.1.27] - 2020-05-19
### Fixed
- Issue with `js show if` and `list collect`.

## [1.1.26] - 2020-05-17
### Fixed
- Duplicative `under` text when `attachment` is used.
- Error when reading certain types of PDF files.

## [1.1.25] - 2020-05-07
### Added
- The `if_started` keyword parameter for the `number_gathered()`
  method.
### Changed
- If `ask_number` on a `DAList` or `DADict` is `True` and
  `target_number` is defined, removing an item using the table editing
  interface will decrease `target_number` by one.

## [1.1.24] - 2020-05-04
### Fixed
- Unicode problem with JSON sent from the browser.

## [1.1.23] - 2020-05-03
### Added
- The `getFields()` JavaScript function.
### Changed
- A `question` with `fields` that contains a single multiple choice
  field where the choices are empty is not skipped if the `question`
  has a `continue button field`.
- The branch and commit are shown in the Packages page of the
  Playground when GitHub integration is enabled and the package has a
  known presence on GitHub.
- Upgraded Font Awesome to 5.13.0.
### Fixed
- Infinite loop when a list is gathered and `object_type` is set to a
  class for which the textual representation or `complete_element` is
  pre-defined and a set number of items are to be gathered.
- The `sql ping` feature was not fully implemented.

## [1.1.22] - 2020-04-30
### Changed
- When a item is added to or removed from a group, the `there_are_any`
  attribute is updated even if `there_are_any` was not previously
  defined.
### Fixed
- Package update problem due to `pip freeze` changing behavior in
  version 20.1.

## [1.1.21] - 2020-04-30
### Fixed
- PDF export value issue where two export values are present in the
  PDF for a checkbox field.

## [1.1.20] - 2020-04-30
### Changed
- Upgraded LibreOffice to version 6.4.
### Fixed
- `review` screens shown as part of the interview logic were being
  treated as actions.

## [1.1.19] - 2020-04-29
### Changed
- If `help` accompanies a `yesno` field, it will be available as a
  popup accessed from an icon.
### Fixed
- GitHub issue when committing to a new branch.
- Exception when trying to edit a non-existent user.
- Bug in `comma_and_list()`.
- The `disable others` and `uncheck others` features did not work
  correctly in a `list collect`.

## [1.1.18] - 2020-04-28
### Changed
- The `checkbox export value` feature is no longer documented because
  PDF field filling now inspects the PDF for the export value.
### Fixed
- The `address autocomplete` feature was not compatible with `show
  if`.

## [1.1.17] - 2020-04-27
### Added
- The `hyperlink style` option for an `attachment`.
### Fixed
- Sendgrid API e-mails to multiple "To" recipients only reached the
  first recipient.

## [1.1.16] - 2020-04-26
### Added
- Test script screenshot mechanism.
### Changed
- Subfolder paths now allowed in URLs for static files.
### Fixed
- S3 file sync problem.

## [1.1.15] - 2020-04-23
### Added
- The `default date min` and `default date max` options under
  `features`.

## [1.1.14] - 2020-04-22
### Changed
- The GitHub button on the Playground Packages page will now respect
  the GitHub repository that was pulled and will make an initial
  commit when the repository exists on GitHub but is empty.

## [1.1.13] - 2020-04-21
### Added
 - The `title url` and `title url opens in other window` screen parts.
 - A "retry" button on the error screen.
### Changed
 - Auto-focus on page load will only be given to an element in the first non-`note`,
   non-`html` field.
### Fixed
 - Pressing enter key on the list collect screen clicked a hidden
   button.
 - Changes in 1.1.11 blocked certain types of uploads.

## [1.1.12] - 2020-04-20
### Fixed
 - Fields with an object-based `datatype` did not work when `list
   collect` was used.
 - Error with exporting tables to Excel.

## [1.1.11] - 2020-04-19
### Added
- Ability to download files by specifying a `filename` parameter to
  GET requests to `/api/playground`.
- The `use_word` keyword argument to `ordinal()`.
- The `always include editable files` specifier for omitting the
  checkbox in the attachment UI.
- The `nginx ssl protocols` Configuration directive.
### Changed
- If `use https` or `behind https load balancer` are enabled, a
  `Strict-Transport-Security` header is returned.
- If `allow embedding` is not set to `True`, the `X-Frame-Options` and
  `Content-Security-Policy` will block iframes.  If `allow embedding`
  is set to `True` and `cross site domains` is set, the list of
  domains will be used for the `Content-Security-Policy` header.
- More than one `address autocomplete` can now be used on a screen.
### Fixed
- Disconnecting from GitHub integration failed if the existing
  integration no longer functioned.

## [1.1.10] - 2020-04-15
### Added
- The `mailgun_variables` option for `send_email()`.
- The `docx_concatenate()` function.
### Changed
- When more than one file with the same name is added to a ZIP file,
  the files are renamed to avoid name collision.

## [1.1.9] - 2020-04-14
### Fixed
- Typo in `Address.on_one_line()`.

## [1.1.8] - 2020-04-13
### Fixed
- Error when `code` is used to generate `fields` and manually entered
  fields follow.
- Jinja2 index error converted to attribute error.
- Incorrect focus when first fields have `hide if`.

## [1.1.7] - 2020-04-13
### Fixed
- Error with serving files through `/uploadedfile/<number>`.

## [1.1.6] - 2020-04-12
### Added
- The `social` Configuration directive for meta tags.
- The `social` specifier under `metadata` for meta tags.
- The `allow robots` Configuration directive.
- Czech translation.

## [1.1.5] - 2020-04-09
### Added
- The `required` modifier for the `signature` block.
### Fixed
- Error message about blank signature not showing.

## [1.1.4] - 2020-04-08
### Changed
- `DAEmpty` now accepts index assignments.
- Obtaining a `new_session` during an interview now preserves
  `url_args` and the `referring_url()`, consistent with the behavior
  of `restart`.

## [1.1.3] - 2020-04-06
### Added
- The `use_familiar` attribute of the `Individual` class.
- The `familiar()` method of the `Name` class.
### Fixed
- Issue with too many flash messages on CSRF error.
- Issue with multiple DOCX documents and subdocuments.

## [1.1.2] - 2020-04-04
### Fixed
- Issue with file names and `.url_for()`.

## [1.1.1] - 2020-04-04
### Added
- The `attachment` keyword parameter for `.url_for()`.
- The `_attachment` keyword parameter for `url_of()`.
### Changed
- Securing of uploaded filenames less strict.

## [1.0.11] - 2020-04-15
### Fixed
- Typo in `Address.on_one_line()`.
- Error when code is used to generate fields and manually entered
  fields follow.
- Jinja2 index error converted to attribute error.
- Incorrect focus when first fields have `hide if`.

## [1.0.10] - 2020-04-12
### Fixed
- Removed 302 redirects.
- Mako filter error.
- Inline upload error.

## [1.0.9] - 2020-04-06
### Fixed
- Issue with too many flash messages on CSRF error.
- Issue with multiple DOCX documents and subdocuments.

## [1.0.8] - 2020-04-05
### Added
- The `DASQLPING` Docker environment variable

## [1.0.7] - 2020-04-05
### Fixed
- Display of available version on Package Management page.

## [1.0.6] - 2020-04-04
### Added
- The `stable version` Configuration directive.

## [1.0.5] - 2020-04-02
### Fixed
- Apache initial certbot run used wrong syntax.
- Synchronizing local updates to files inside projects on OneDrive failed.

## [1.0.4] - 2020-03-31
### Fixed
- Error when `disable others` is used inside of a `show if` or `js
  show if`.

## [1.0.3] - 2020-03-30
### Fixed
- `update_ordinal_numbers()` and `update_ordinal_function` missing
  from `docassemble.base.util`.
- `sql ping` workaround for SQL connections being cut off.

## [1.0.2] - 2020-03-25
### Fixed
- Fixed issue with incomplete pull request by dependabot.

## [1.0.1] - 2020-03-25
### Fixed
- Deprecated use of access token in URL parameter when retrieving
  branch listing from GitHub API when repository reference uses an
  `oauth-basic` URL.

## [1.0.0] - 2020-03-22
### Added
- The `show_country` keyword parameter for the `.on_one_line()` and
  `.block()` methods of the `Address` class.
- The `international` keyword parameter for the `.block()` method of
  the `Address` class.
- The `assemble_docx()` function.
### Changed
- Switched to a different versioning system.  The `stable` branch on
  GitHub will be version 1.0.  Patch versions within version 1.0
  (1.0.1, 1.0.2, etc.) will be for bug fixes and security upgrades
  only.  The `master` branch on GitHub will be version 1.1.  Patch
  versions within version 1.1 will include bug fixes as well as
  feature enhancements.
- The `omit_default_country` parameter of the `.on_one_line()` method
  of the `Address` class is deprecated.
### Fixed
- Bug with `restrict input variables` and attachment e-mailing and
  downloading.
- `pip show` inefficiency unnecessarily slowed down initial start up
  time.

## [0.5.111] - 2020-03-20
### Added
- The `auto open` option for the `sections` block.
- The `pages()` method for Twilio fax status.
### Fixed
- The caret next to automatically closed subsections in the section
  navigation bar defaulted to the wrong setting.
- The `received()` method of the fax send status did not correctly
  respond `True` when the fax was in `'delivered'` status.
- Error message when clicking the back button under certain
  circumstances.

## [0.5.110] - 2020-03-17
### Fixed
- Bug affecting `raw global javascript`.

## [0.5.109] - 2020-03-11
### Changed
- Deleting an item in a table now undefines `there_is_another` when it is
  `True`.
### Fixed
- The `bootstrap theme` in the Configuration will apply to interviews
  if `bootstrap theme` in `features` is not set.
- Errors in global CSS and JS Configuration directives not intercepted
  and logged.

## [0.5.108] - 2020-03-08
### Fixed
- Issue with `bootstrap theme` and other Configuration directives that
  require Flask URL formation.

## [0.5.107] - 2020-03-03
### Changed
- More flexible handling of `default` values with `datatype: date`.
- The `allow embedding` Configuration directive now accepts the value
  `'Lax'`, which is the default.

## [0.5.106] - 2020-02-29
### Changed
- LibreOffice Word to PDF conversion no longer reduces image
  resolution.
### Fixed
- Log server in multi-server mode accessed on wrong port.
- URL parameters stripped when redirecting to login when `allow
  anonymous access` is `False`.

## [0.5.105] - 2020-02-26
### Changed
- If the database is PostgreSQL, the Alembic table alteration
  introduced in 0.5.97 for MySQL compatibility purposes is no longer
  applied by default because it might take too much time on a server
  with a large SQL database.  The discrepancy between the SQLAlchemy
  column type specification (varchar) and the actual PostgreSQL column
  types (text) is harmless.  If your SQL database is not large, you
  can set `force text to varchar upgrade: True` in your Configuration
  before upgrading to force the column type alteration to take place
  during the upgrade.  After upgrading to 0.5.105+, you can remove
  `force text to varchar upgrade` from the Configuration.  This is
  only applicable if upgrading from 0.5.96 or before; if you already
  upgraded to 0.5.97 - 0.5.104, then the alteration has already taken
  place.
### Fixed
- Upgraded `bleach` due to security vulnerability.

## [0.5.104] - 2020-02-25
### Fixed
- Error with `allow embedding`.

## [0.5.103] - 2020-02-23
### Fixed
- Error with `DAContext` variables.

## [0.5.102] - 2020-02-23
### Added
- The `user auto delete` Configuration directive.
- The `allow embedding` Configuration directive, which if `True` sets
  the `SameSite` flag in cookies to `None`.
### Changed
- The `SameSite` flag is now set to `Strict` in cookies by default.
  For the old behavior, set `allow embedding: True` in the
  Configuration.

## [0.5.101] - 2020-02-23
### Changed
- Playground syntax highlighting now highlights Python code as Python
  code.
### Fixed
- The `interview_menu()` function did not accept parameters.

## [0.5.100] - 2020-02-20
### Added
- The `.data_type_guess()` method of `DACatchAll`.
- The `.keys()` method of `DAStore`.
### Fixed
- Issue with default values after input validation fails and two
  fields set the same variable.

## [0.5.99] - 2020-02-19
### Added
- Catchall questions.
### Fixed
- When item under `edit` in a `table` has no question associated with
  it, an error was raised only if the item was first.

## [0.5.98] - 2020-02-18
### Fixed
- Typo causing `/playgroundstatic` file links to fail.

## [0.5.97] - 2020-02-17
### Added
- The `forget prior` option for `action buttons`.
### Changed
- Calls to subprocesses now have timeouts.
- Database columns used as indices changed from text to variable character.
### Fixed
- Bug with table export.

## [0.5.96] - 2020-02-15
### Changed
- `depends on` no longer implies `need`.

## [0.5.95] - 2020-02-14
### Added
- The `show incomplete` and `not available label` options for `table`
  blocks.
- The `gathering_started()` method of groups.

## [0.5.94] - 2020-02-13
### Added
- The `allow external auth with admin accounts` Configuration
  directive.
- The url parameter feature of `url_of()`.

## [0.5.93] - 2020-02-13
### Changed
- `code` blocks with `event` work with `depends on` now.
- Playground folders have download buttons now.
- `re` and `json` are now available inside the interview namespace.
### Fixed
- Let's Encrypt issue.

## [0.5.92] - 2020-02-11
### Added
- The `add_separators()` function.
- The `session error redirect url` Configuration directive.
### Changed
- Calling `as_noun()` on a group with one item will return the
  `noun_singular()` of the applicable noun.

## [0.5.91] - 2020-02-07
### Added
- The `/api/interview_data` API endpoint.
### Fixed
- Interview cache not cleared after Playground pull.

## [0.5.90] - 2020-02-06
### Added
- The `convert_to` method of `DAFile`.
### Changed
- Functionality of `depends on` extended to additional block types.

## [0.5.89] - 2020-02-04
### Changed
- Backend health monitor HTTP server moved to port 8082 from port
  8080.

## [0.5.88] - 2020-02-03
### Added
- The `response_code` option for `response()` and `json_response()`.
- The `sendgrid api key` Configuration directive for sending e-mail
  using the SendGrid API.
### Changed
- A `question` with a Continue button that sets a variable to `True`,
  or a `review` screen with a Continue button instead of a Resume
  button, can be indicated with `continue button field` instead of
  `field`.

## [0.5.87] - 2020-02-02
### Fixed
- Overwriting of README in Playground Packages when README.md is in
  a first level subfolder.
- Fields hidden by `show if` that uses `code` could prevent the
  display of a `question`.

## [0.5.86] - 2020-01-31
### Added
- The `default_for` class method and `is_object` attribute of
  `CustomDataType`.
### Changed
- The `datatype` of `area` should now be expressed as `input type:
  area`.  For backwards compatibility, `datatype: area` still works.
### Fixed
- Bug in `/api/file` introduced in 0.5.85.

## [0.5.85] - 2020-01-28
### Added
- CSS classes on HTML elements related to attachments.
### Fixed
- Missing static file in existing package generated exception instead
  of a 404 error.

## [0.5.84] - 2020-01-27
### Added
- The `restrict input variables` Configuration directive.
- The `allowed to set` question modifier.
### Fixed
- PDF image overlays failed with any image that contained a density in
  the metadata.

## [0.5.83] - 2020-01-26
### Added
- Input validation features for `CustomDataType` classes.
- Ability to use `DAOAuth` without being logged in.
### Fixed
- JavaScript failure on error screens during interviews.

## [0.5.82] - 2020-01-23
### Added
- Warnings in the logs if unrecognized keys used in interview YAML
  dictionaries.
### Fixed
- The `disable others` feature interfered with the `show if` feature.

## [0.5.81] - 2020-01-22
### Added
- The `allow updates` Configuration directive and `DAALLOWUPDATES`
  Docker environment variable.
### Fixed
- Google Drive issue with files reporting no size.
- Erroneous reference to text_type.

## [0.5.80] - 2020-01-20
### Fixed
- Variables with iterators or generic object references could not be
  set through the API or `set_session_variables()`.

## [0.5.79] - 2020-01-18
### Added
- The `convert_file` API endpoint.
### Fixed
- Incorrect tab order in Playground Pull.

## [0.5.78] - 2020-01-14
### Added
- The `depends on` modifier.
- The `on change` block.
- The `invalidate()` function.
- The `.invalidate_attr()` method of `DAObject`.
- The `invalidate` option in a `review` block.

## [0.5.77] - 2020-01-12
### Added
- Ability to convert DOCX to PDF using CloudConvert.
- The `cloudconvert secret` Configuration directive.

## [0.5.76] - 2020-01-08
### Fixed
- Playground variables sidebar did not always switch to the most
  recently-run interview.
- Restart process used IP address and port that may not be available
  internally.

## [0.5.75] - 2020-01-07
### Added
- The `date format`, `datetime format`, and `time format`
  interview-wide defaults.
### Fixed
- Line breaking issue with `terms` and `auto terms`.

## [0.5.74] - 2020-01-06
### Fixed
- Error when checkbox values are not strings.

## [0.5.73] - 2020-01-05
### Fixed
- Error in watchdog process launch.
- UI bug in list collect.

## [0.5.72] - 2020-01-05
### Added
- The `admin full width` Configuration directive.
- The `wrap lines in playground` Configuration directive.
### Changed
- Moved Download button to below the editor in the Playground.
### Fixed
- Bug in `legal.py`.
- Not safe to concatenate a `DAList` and a `DAEmpty`.

## [0.5.71] - 2020-01-05
### Changed
- Discontinued support for Python 2.7.

## [0.5.70] - 2019-12-30
### Added
- The `phone_number_formatted()` function.
- The `fr-words.yml` translation file in `docassemble.base`.
### Fixed
- Errors when building the Dockerfile on the ARM architecture.

## [0.5.69] - 2019-12-24
### Added
- The `.user_access()` and `.privilege_access()` methods of `DAFile`.
- The `persistent`, `private`, `allow users`, and `allow privileges`
  specifiers for `attachments` and field modifiers for `datatype:
  file` fields.
### Fixed
- User could not access a private and persistent file after the
  deletion of the session in which the file was created.
- Issue with `js show if` and `list collect`.

## [0.5.68] - 2019-12-21
### Fixed
- JQuery Validation Plugin message for integer and step input
  validation was not customizable.
- Dependency was incompatible with Python 3.5.

## [0.5.67] - 2019-12-19
### Added
- The `help generator` and `image generator` field modifiers.
### Fixed
- Error when `code` was used with `content file` and the code
  returned a list.
- Backup of Redis database when password is used.

## [0.5.66] - 2019-12-19
### Fixed
- Issue with Redis and passwords.

## [0.5.65] - 2019-12-19
### Added
- The `DAWeb` object.
- The Configuration page now reports the underlying Python version.
### Fixed
- The `PATCH` endpoints for API-related API calls only accepted URL
  parameters.
- The `step` specifier for `datatype: range` fields was not effective.
- The `re_run_logic()` function did not re-run from the start of the
  interview logic in all situations.
- The `redis` directive in the Configuration did not support
  passwords.
- A checkbox with the empty string as the value triggered an error.

## [0.5.64] - 2019-12-15
### Fixed
- Back button after `url_args` are set repeated the setting of the
  `url_args`.
- The `resume interview after login` feature did not work correctly
  with the default menu.

## [0.5.63] - 2019-12-14
### Added
- API endpoints for managing API keys.

## [0.5.62] - 2019-12-12
### Fixed
- JavaScript error, introduced in 0.5.31, impeded embedded field
  validation.
- The `default interview` was ignored if a `dispatch` directive
  existed.
- Error in package listing when installing from GitHub.

## [0.5.61] - 2019-12-11
### Fixed
- The `subtitle` screen part was not updated correctly by
  `set_parts()`.
- In the Playground, the "Share" link was not updated when the
  "Variables, etc." file name changed.

## [0.5.60] - 2019-12-09
### Fixed
- Issue with `supersedes`.

## [0.5.59] - 2019-12-09
### Fixed
- Issue with `supersedes`.

## [0.5.58] - 2019-12-09
### Fixed
- Modules included in YAML files with relative references were loading
  from the main YAML file's package, not in the package of the YAML
  file containing the `modules` or `imports` block.

## [0.5.57] - 2019-12-09
### Changed
- Different way of finding GitHub e-mail address.
### Fixed
- Cron issues.

## [0.5.56] - 2019-12-08
### Added
- The `action buttons` specifier for `question`s.

## [0.5.55] - 2019-12-06
### Fixed
- Styling of Font Awesome icons inside buttons.
- Some variables in Variables, etc. inappropriately flagged as undefined.

## [0.5.54] - 2019-12-05
### Added
- The `confirm registration` Configuration directive.
### Changed
- CSRF errors pop up in a "flash" box.
- Cron jobs run with nice 19 (system upgrade required for this
  change).
- Messages from Flask-User are now translated through the
  **docassemble** system phrase translation system.
### Fixed
- Styling of Font Awesome icons inside buttons.

## [0.5.53] - 2019-12-03
### Added
- The `hook_on_remove()` method.
- The `SQLObjectList`, `SQLRelationshipList`,
  `StandardRelationshipList`, and `SQLObjectRelationship` classes in
  `docassemble.base.sql`.
- The `.any()`, `all()`, and `.filter()` class methods of `SQLObject`.
- The `.has_child()`, `.add_child()`, `.get_child()`, `.del_child()`,
  `.has_parent()`, `.add_parent()`, `.get_parent()`, and `.del_parent()`
  methods of `SQLObject`.
- The `_session` attribute of `SQLObject`.
- The option to opt out of module pre-loading by adding `# do not
  pre-load` to a line at the top of the module file.
### Changed
- The `message` parameter of `.add_action()` has been renamed to
  `label` (backwards-compatibility is maintained).
- The `.get_session()` method of `SQLObject` has been removed in favor
  of the `._session` attribute.

## [0.5.52] - 2019-11-29
### Fixed
- Bug in package update script.

## [0.5.51] - 2019-11-28
### Changed
- The `pt-words.yml` file has been renamed to `pt-br-words.yml`.  If
  you are using this file, you will need to change your `words`
  configuration.
### Fixed
- HTML codes non-printable in dropdown lists.

## [0.5.50] - 2019-11-26
### Added
- The `inline_markdown` Jinja2 filter.
### Fixed
- Problem with XLSX translation file colorization.

## [0.5.49] - 2019-11-24
### Fixed
- Python 2.7 bug introduced in 0.5.47.

## [0.5.48] - 2019-11-24
### Added
- The `external` keyword parameter for the `.url_for()` method.
### Changed
- Access to files is now granted to users across sessions, whether the
  session was active in the browser's session or not.  Previously,
  access was restricted based on sessions that had been active in the
  browser's session.
- The `.url_for()` method when used with `temporary=True` now implies
  `external=True`, which means that the URL returned includes the
  protocol and hostname.  Use `external=False` to preserve the old
  behavior.
- A superscripted question mark icon is now shown in the green text
  when `help` is added to a field.
- When committing to GitHub from the Playground Packages screen, you
  can choose to also publish on PyPI and install the package on the
  server.
- When publishing to PyPI from the Playground Packages screen, you can
  choose to also install the package on the server.

## [0.5.47] - 2019-11-24
### Added
- The `prevent_dependency_satisfaction` decorator.
- The `interview delete days by filename` Configuration directive.
- The `review button color` and `review button icon` options under
  `features`.
- The `sleep` option for `response()` and `command()`.
### Fixed
- Cron job inefficiencies.
- JavaScript error when using `check in` and `list collect` at the
  same time.
- Error when `admin` user signs in with a social login.
- An `input type: ajax` in `list collect` did not allow adding
  additional items.
- Ampersands in Jinja2 code were converted to `&amp;`.

## [0.5.46] - 2019-11-21
### Fixed
- Possible race condition in `interview_list()`.

## [0.5.45] - 2019-11-20
### Added
- The `backup` directive under `db`.
### Fixed
- Problem converting some types of interview answers to JSON.

## [0.5.44] - 2019-11-20
### Fixed
- Cron job was overtaxing the SQL server.
- `does_verb()` used the wrong tense.

## [0.5.43] - 2019-11-18
### Added
- Ability to pass keyword parameters to the `show()` method of a
  template.
### Fixed
- Problem with object storage cache invalidation.

## [0.5.42] - 2019-11-17
### Fixed
- Problem unpickling from 2.7.

## [0.5.41] - 2019-11-16
### Fixed
- Problem with the Playground API using the Templates folder.
- Playground API did not support projects other than the default
  project.
- HTML typo that was introduced in 0.5.40.
- Problem unpickling from 2.7.

## [0.5.40] - 2019-11-15
### Added
- The `button style` Configuration directive.
- The `disable analytics` option under `features`.
### Fixed
- The LDAP login feature was not compatible with the new version of
  the `python-ldap` package.

## [0.5.39] - 2019-11-13
### Changed
- Multi-server syslog system improved.
- `objects_from_file()` now accepts `DAFile` and related objects.
### Fixed
- Problem with `DAStore` being used with the API.
- Logrotate not rotating all files.

## [0.5.38] - 2019-11-11
### Changed
- Testing scripts now support the `aloe` package as an alternative to
  `lettuce`.
### Fixed
- Web sockets logs not sent to syslog.
- `RABBITMQ` and `REDIS` not overridden when
  `ENVIRONMENT_TAKES_PRECEDENCE` is true.
- Reverted change made in 0.5.37 regarding HTML codes.

## [0.5.37] - 2019-11-09
### Added
- Method of initializing admin e-mail and password through volume
  mount.
- The `collect statistics` Configuration directive.
### Changed
- External PostgreSQL database created if it does not exist.
### Fixed
- Dependency on `mod_wsgi` caused problems when upgrading.
- HTML codes non-printable in dropdown lists.
- Potential problem with too-short RabbitMQ heartbeat.

## [0.5.36] - 2019-11-04
### Fixed
- Exceptions raised by syslog calls were not trapped.
- Problems with restarting server in multi-server configuration.

## [0.5.35] - 2019-10-31
### Changed
- The "remember me" feature removed.
### Fixed
- Deleted or renamed playground modules not culled from Python
  installation.
- Content of new file in Playground lost if filename blank.
- Erroneous `session` parameter added to result of
  `interview_url_action()` if `i` specified.

## [0.5.34] - 2019-10-30
### Fixed
- Erroneous dependency on `pkg-resources` in `docassemble.base` for
  Python 2.7.

## [0.5.33] - 2019-10-30
### Changed
- All Python dependencies have version numbers explicitly indicated.
- Backend server health check tests for completion of initialization.
- The `websockets ip` Configuration directive no longer defaults to localhost.
### Fixed
- Better handling of Markdown when passing values to a DOCX file
  directly.
- Ordinal functions now accept arbitrary keyword arguments.
- Some phrases for translation not detected.
- The `verbatim()` function did not escape formatting characters in
  some circumstances.

## [0.5.32] - 2019-10-25
### Added
- `ENVIRONMENT_TAKES_PRECEDENCE` Docker environment variable.
- The `use minio` Configuration directive.
- Added `account_type` as a response from `get_user_info().
### Changed
- Improved backup and logging in multi-server configuration.
- Any `admin` can upgrade or downgrade packages.
### Fixed
- The `subtitle` did not work with `set_parts()`.
- Certain PDF fields raised error.
- Not all language functions were compatible with keyword parameters.
- Manual newlines in Markdown not converted to line breaks.
- Double quotes in HTML input element values not properly escaped.

## [0.5.31] - 2019-10-13
### Added
- Ability to use `code` in `content file` specifiers of `template`s
  and `attachment`s.
### Changed
- When `labels above fields` is used, the input element will now be
  wrapped in a `<div>` with CSS class `dafieldpart`.
- Server-side validation errors are now scrolled to when the screen
  loads.
### Fixed
- Broken link to variables and values on error page.

## [0.5.30] - 2019-10-11
### Fixed
- Free disk space indicator not compatible with Python 2.7.

## [0.5.29] - 2019-10-11
### Added
- Ability to download all log files as a ZIP file.
- Free disk space indicator on Configuration page.
### Fixed
- Problem with Google Drive Sync and zero-byte files.

## [0.5.28] - 2019-10-10
### Fixed
- Problem with NGINX and `POSTURLROOT`.

## [0.5.27] - 2019-10-10
### Fixed
- Problem with session deletion.

## [0.5.26] - 2019-10-09
### Changed
- Limited data retrieved by Google address autocomplete feature.
### Fixed
- NGINX configuration omitted `POSTURLROOT`.

## [0.5.25] - 2019-10-09
### Changed
- Configuration page now shows a listing of errors in the
  Configuration, if there are any.
### Fixed
- Error with URLs to cloud-hosted files.

## [0.5.24] - 2019-10-08
### Fixed
- Error with Run button in Playground.
- Erroneous space in the CSS class names of some fieldsets.
- Error with non-cloud temporary URLs.

## [0.5.23] - 2019-10-08
### Added
- Additional cache invalidation headers.

## [0.5.22] - 2019-10-08
### Added
- The `/api/fields` endpoint.
- The `use cloud urls` directive in the Configuration.
### Fixed
- Miscellaneous problems with ajax field type.
- Syntax with Let's Encrypt renewal not compatible with all
  configuration types.
- Problem with obtaining JSON version of `question` where `js show if`
  is in use.
- Unnecessary saving of interview answers with the wrong encryption.

## [0.5.21] - 2019-10-04
### Fixed
- Error when Playground project name matched name of a Playground
  package.

## [0.5.20] - 2019-10-04
### Fixed
- Problem with office task pane.
- Problem with YAML in field scanner in utilities.
- Problem with `endpoint url` option.

## [0.5.19] - 2019-10-02
### Fixed
- Problem with background tasks and uploads.

## [0.5.18] - 2019-10-02
### Added
- Projects system in the Playground.
- The `verbatim()` function.

## [0.5.17] - 2019-09-26
### Added
- An option for assembling text files by setting `raw: True` under
  `attachment`.

## [0.5.16] - 2019-09-25
### Added
- Custom `datatype` feature.
### Fixed
- Session-related bug.
- Thumbnail generation bug.
- Image icon problems.
- External URLs calculated inconsistently.

## [0.5.15] - 2019-09-23
### Added
- The `css class` screen part.
- The `allow anonymous access` Configuration directive.
### Fixed
- Session-related bug.

## [0.5.14] - 2019-09-23
### Fixed
- Markdown of single-column `table`s not recognized.

## [0.5.13] - 2019-09-22
### Added
- The `use_objects` option for `objects_from_file()`
- The `use objects` option for `objects from file`.
### Changed
- The `objects_from_file()` function and the `objects from file` block
  now support JSON files as well as YAML files.
### Fixed
- Transitional error related to session upgrade.

## [0.5.12] - 2019-09-21
### Changed
- Users can run multiple sessions in different browser tabs.
- The `i` URL parameter is required for any endpoint that uses the
  current sesion.
- The `DAEmpty` class now supports comparison operators.
### Fixed
- IndexErrors appeared under some circumstances when using actions.
- Live Help bug.

## [0.5.11] - 2019-09-16
### Fixed
- Problem with checkbox object initialization inside of `DADict`.
- Error when trying to inspect functions to get usage information for
  the Playground sidebar.
- Renewal of Let's Encrypt included obsolete domains.

## [0.5.10] - 2019-09-15
### Added
- The `symbol` keyword parameter of `currency()`.
- The `currency_symbol` keyword parameter of `set_locale()`.
### Fixed
- Problem with `disable others` when `allow non-idempotent questions`
  was `False`.
- Problem with `reconsider` under certain circumstances.
- Error when `command()` used immediately after a file upload.
- Error when exporting dates in a table to Excel.

## [0.5.9] - 2019-09-12
### Fixed
- `NoneType` error when using `data` with `use objects`.
- Error when non-base64 dictionary keys happened to be valid base64.

## [0.5.8] - 2019-09-11
### Added
- The `delattr` method of the `DAObject` class.
### Changed
- Different behavior when `allow non-idempotent questions` is set to
  `False`.
### Fixed
- Unpickling errors in `user_interviews()` not trapped appropriately.

## [0.5.7] - 2019-09-10
### Changed
- The `url_action_perform()` and `url_action_call()` JavaScript
  functions are renamed to `action_perform()` and `action_call()`.
  Aliases are in place for backwards-compatibility.
- Widths of images inserted into DOCX files now support centimeters
  and twips as units.
- The `continue button field` can now be used with other types of
  `question`s that set variables, rather than just `fields`.
### Fixed
- Unpickling errors in `user_interviews()` not trapped.

## [0.5.6] - 2019-09-08
### Added
- Option in the JavaScript `flash()` function to clear existing
  messages.
### Fixed
- Error when displaying the JSON form of certain `question`s.
- Error when using `Value` objects in the `choices` of a `datatype:
  object` field.

## [0.5.5] - 2019-09-07
### Added
- The `require gathered` specifier for tables.
### Changed
- Running `.pop()` on a `DAList` no longer triggers list gathering.
- Every module file installed in the `docassemble` namespace that
  contains a class definition will be loaded when the server starts or
  restarts.
### Fixed
- Erroneous message about starting new interview was appearing on
  restart.
- Default values not appearing for some `datatype: object` fields.
- Unpickle errors when modules that contain classes are not loaded.
- Tooltips not showing up on sliders.

## [0.5.4] - 2019-09-05
### Fixed
- The `maximum content length` was being superseded by a NGINX content
  length limiter.
- Word add-in bug.

## [0.5.3] - 2019-09-04
### Added
- The `exit url` specifier under `metadata`.

## [0.5.2] - 2019-09-03
### Fixed
- S3 error.

## [0.5.1] - 2019-09-02
### Fixed
- `get_question_data()` and related functions raised exception.
- Let's Encrypt renewal error.

## [0.5.0] - 2019-09-02
### Added
- The `advance_progress_meter` option for the `/api/session` POST API
  endpoint.
- The `DAWEBSERVER` Docker environment variable and the `web server`
  Configuration directive.
- The `S3ENDPOINTURL` Docker environment variable and the `endpoint
  url` Configuration directive under `s3`.
### Changed
- Upgrade Docker OS to Debian buster.
- Upgrade Python from 3.5 to 3.6.
- The default web browser under Docker is now NGINX.
- The Docker image now builds in two parts.  The jhpyle/docassemble-os
  image is the base image for jhpyle/docassemble.
- The `get_session_variables()` and `set_session_variables()`
  functions use the current user's decryption key by default.

## [0.4.80] - 2019-08-22
### Fixed
- Setting of `__version__` in Python 2.7 raised Unicode error.
- Back button after action in URL repeated the action.
- The `progress` value was missing from the JSON representation of the
  question.

## [0.4.79] - 2019-08-21
### Added
- The `SQLObject` class.
- The `input type` called `ajax`.
- The `paragraphs` Jinja2 filter.
### Changed
- The `__version__` variable is now defined in packages generated from
  the Playground packages folder.
- UTM parameters are retained if an `analytics id` is defined under
  `google` in the Configuration, or a `segment id` directive is
  defined in the Configuration.
- The Playground packages folder GitHub commit process now uses `git
  merge` to merge changes, which means it might fail if a commit would
  overwrite changes.
- The Playground packages folder now allows for committing to a new
  remote branch.
### Fixed
- Incorrect behavior during initial visit to `/interview` when
  interview uses unique sessions.
- Interview advanced a step despite `validation code` raising an
  exception.

## [0.4.78] - 2019-08-15
### Added
- The `features` option `labels above fields`.
### Fixed
- Errors with `sessions are unique` and `required privileges`.

## [0.4.77] - 2019-08-14
### Added
- The `enable playground` Configuration directive.
### Changed
- The behavior of the `label` option of `list collect` no longer
  prints text before `1.`, `2.`, etc.  Now the `label` supplies the
  whole label for the item, and it can include the number by way of
  the index variable.
### Fixed
- The `list collect` feature raised an exception when the field
  definition included Mako substitution.
- Non-required upload fields were creating zero-byte files on some
  servers.

## [0.4.76] - 2019-08-12
### Changed
- The syslog-ng server is now started after the web server.
### Fixed
- Unhelpful error message when there was an interview parsing error.
- `DAStaticFile` objects not being included in DOCX files correctly.

## [0.4.75] - 2019-08-12
### Added
- The `administrative interviews` Configuration directive
- The `sessions are unique`, `required privileges for listing`, and
  `hidden` specifiers under `metadata`.
### Changed
- The `words` system no longer uses code names like `pdf_message` and
  `save_as_multiple`.
- The `required privileges` specifier under `metadata` now prevents
  users without a valid privilege from starting the interview.  The
  `required privileges for listing` now controls whether the interview
  is listed under `/list`.
### Fixed
- Passing an asterisk in a list to Flask-CORS resulted in a regular
  expression error.
- Not all Flask packages accept integers as the
  `PERMANENT_SESSION_LIFETIME`.

## [0.4.74] - 2019-08-09
### Fixed
- The `undefine()` function did not always find the interview
  answers.

## [0.4.73] - 2019-08-09
### Added
- Support for noun pluralizing and verb conjugation in Spanish,
  French, Italian, German, and Dutch.
- Additional methods for `DAOAuth` objects.
### Changed
- The output of the `interview_menu()` function, the `/api/list`
  endpoint, and the `/list?json=1` endpoint now include interview
  metadata.
- The `undefine()` function now accepts multiple variables names.
### Fixed
- `DAObject`s that are attributes of `DAList` items had their
  `instanceName`s rewritten when the parent list was altered.
- When an object that was already defined was edited using `fields`
  with `datatype: object` or `datatype: object_radio`, the default
  value was not showing.
- The office add-in was not using the best method to determine the
  full URL of the server.

## [0.4.72] - 2019-08-07
### Fixed
- Translation of metadata titles not compatible with `translations`.
- JavaScript evaluated in local context rather than global context.
- Language not set when e-mailing assembled document in the
  background.

## [0.4.71] - 2019-08-06
### Changed
- API for making user accounts inactive now supports permanent
  deletion.
- API for setting variables now supports initializing `DAObject`s.
- Multiple choice options specified with code can be specified with
  lists of tuples.
### Fixed
- Missing system phrase used in input validation.

## [0.4.70] - 2019-08-03
### Added
- Account deletion options.
- Options in the user profile for controlling which repositories will
  be considered when the Playground packages folder looks for and
  commits to GitHub repositories.
- Configuration directives `session lifetime seconds`, `babel dates
  map`, `admin can delete account`, `user can delete account`, and
  `delete account deletes shared`.
### Changed
- In tables, ordered dictionaries will use their built-in order.
- Base64 padding removed from field names.
### Fixed
- Poppler upgrade interfered with width of images in popups.
- File upload widget JavaScript bug.

## [0.4.69] - 2019-07-29
### Fixed
- Unnecessary file cache invalidation affected Playground performance
  when using cloud storage.
- Incorrect method of setting Debian timezone.

## [0.4.68] - 2019-07-28
### Added
- The `/api/resume_url`, `/api/temp_url`, `/api/config`,
  `/api/package`, and `/api/package_update_status` API endpoints.
- The `expire` and `session` parameters of `/api/login_url`.
- The `hook_on_gather()` and `hook_after_gather()` methods of
  `DAList`, `DADict`, and `DASet`.
### Fixed
- Bug in the `complete_elements()` method of `DADict`.
- Incomplete support for editing lists that have `auto_gather` turned
  off.

## [0.4.67] - 2019-07-25
### Added
- The `confirm` option for table editing.
### Changed
- The "Select..." option on a dropdown is omitted when the field is
  required and a default value is selected.
### Fixed
- The `keys()` method of `DADict` was removed when `keys` included in
  constructor.
- The language did not switch unless it did not match the default
  language.
- Restart buttons did not work from `event` screens.

## [0.4.66] - 2019-07-23
### Changed
- Allow sending multiple invite e-mails at once.
### Fixed
- Canceling phone live help availability failed.
- The 404 error from `/interview` did not use the 404 template.

## [0.4.65] - 2019-07-19
### Fixed
- Erasing phone number in Monitor raised an error.
- OneDrive synchronization error.

## [0.4.64] - 2019-07-17
### Changed
- Upgraded CSS and JavaScript dependencies.
### Fixed
- JavaScript for file uploads was incompatible with a Firefox add-on.
- Error during initialize process possibly caused by stderr being made
  non-blocking.
- Bug in `indent()` function.
- File upload previews shown twice under certain circumstances due to
  `show if` JavaScript.

## [0.4.63] - 2019-07-16
### Added
- The `/resume` endpoint.
### Fixed
- Unpickleable object added to the document cache in the internal
  variables.

## [0.4.62] - 2019-07-14
### Added
- The `temporary` and `once_temporary` options to the
  `interview_url()` and related functions.
### Fixed
- Too many monitor connections led to SQL error.
- Some functions did not work in actions.

## [0.4.61] - 2019-07-10
### Added
- The `set_status()` and `get_status()` functions.
### Changed
- Disabled `pip` cache.
- Restored pre-0.4.55 behavior allowing Mako in multiple choice
  values.

## [0.4.60] - 2019-07-09
### Changed
- More robust Docker scripts.
### Fixed
- Error with cloud cache.

## [0.4.59] - 2019-07-05
### Changed
- Changes manually made to `/etc/apache2/sites-available` files while
  the container is running will now be backed up upon shutdown and
  restored upon startup.
### Fixed
- Fatal error when invalid global javascript file referenced in
  Configuration.

## [0.4.58] - 2019-07-05
### Changed
- CORS headers now handled by Flask rather than Apache.
- The `cross site domain` Configuration directive is renamed to `cross
  site domains` and the value must be a list.
- Removed the `CROSSSITEDOMAIN` Docker environment variable.
- More frequent deletion of temporary files.

## [0.4.57] - 2019-07-01
### Added
- The `explain()`, `clear_explanations()`, and `explanation()`
  functions.
### Fixed
- Problems with Google sign-in on Python 3.

## [0.4.56] - 2019-06-29
### Added
- The `initializeObject` method of `DAList`.
### Fixed
- Error gathering `DAList` of `datatype: checkboxes` items.
- Error when using `default` and `list collect`.
- Errors with `DAStore`.

## [0.4.55] - 2019-06-28
### Added
- The `DAStore` object.
### Changed
- Mako no longer allowed in non-label items of `choices` or `buttons`.
- If `backup days` is `0`, no daily backups will be done.
### Fixed
- Error when `dialects` enabled under `voicerss`.

## [0.4.54] - 2019-06-26
### Added
- The `language map` directive under the `voicerss` Configuration
  directive.
### Changed
- Renamed `languages` under the `voicerss` Configuration directive to
  `dialects` (with backwards compatibility).
### Fixed
- `list collect` on empty non-object list did not show the first item.
- Wrong protection on some cells in translation spreadsheets.
- `nan` values appeared in translation spreadsheets.
- Terms with capital letters were not being translated.
- System terms were not appearing in translation YAML when Google
  Cloud Translation API was not configured.

## [0.4.53] - 2019-06-26
### Added
- Jinja2 filters `markdown` and `RichText`.
### Changed
- Ampersand correction for DOCX now happens in Jinja2 even if pipe
  already used.
### Fixed
- The `hint` was missing from the data representation of a field.
- The `note` and `html` were missing from the data representation of a
  field when not standalone.
- Group editing did not work with non-object lists and dictionaries.
- Buttons on `message()` screens did not work.

## [0.4.52] - 2019-06-18
### Added
- The `javascript` option for `log()`.
### Fixed
- Potential error in Playground sidebar if the same variable name is
  used for two different types of object.
- Error if `json` URL parameter is not an integer.

## [0.4.51] - 2019-06-13
### Changed
- Added the `initial` option for `update on start`.
- Using a different mechanism for restarting servers after a software
  update.
### Fixed
- LibreOffice failing when multiple instances of LibreOffice run
  simultaneously.

## [0.4.50] - 2019-06-12
### Added
- The `update on start` Configuration directive.
- The `expose websockets`, `websockets ip`, and `websockets port`
  Configuration directives.
### Changed
- The `include_docx_template()` function now includes images, shapes,
  styles, footnotes, etc. from the sub-document.
- Problem with websockets on servers with a `root` other than `/`.
- The `/api/session` POST API endpoint will now convert dates to
  `DADateTime` objects, unless the `raw` parameter is `1`.
### Fixed
- Triple spacing in RTF documents.
- Flask route ambiguity with `/api/user/new`.

## [0.4.49] - 2019-06-08
### Changed
- Revised the CSS classes for error messages.
### Fixed
- Word add-in did not work for servers with a `root` other than `/`.

## [0.4.48] - 2019-06-06
### Added
- The `.is_encrypted()` method of `DAFile` and other file objects.
### Fixed
- Dependency problems when `docassemble.base` was used without
  `docassemble.webapp`.
- Errors in the `DAFileCollection` version of `num_pages()` and
  `size_in_bytes()`.
- JavaScript used `.includes()` and `.startsWith()` methods, which are
  not universally supported.

## [0.4.47] - 2019-05-31
### Added
- Option for `'link'` style buttons with `action_button_html()`.
### Fixed
- Some types of `fields` gave errors with `list collect`.
- Error re `UserModel`.

## [0.4.46] - 2019-05-30
### Fixed
- Recursion error with `capitalize()` function.
- A CSS class was called `vspace` instead of `davspace`.
- Multiple choice options not included in translation spreadsheets.

## [0.4.45] - 2019-05-27
### Added
- The `DAOAuth` class.
### Changed
- Made modifications to facilitate embedding interviews in a `<div>`
  in another site.
- CSS and JavaScript files are now bundled.
### Fixed
- Errors from OneDrive integration.
- Error reading fields from PDF.
- Inserting certain types of images into RTF files resulted in a fatal
  error rather than a non-fatal error.

## [0.4.44] - 2019-05-21
### Added
- Version-specific caching of CSS and JavaScript files.
- The `sort()` and `sort_elements()` methods for `DAList`.
### Changed
- `terms` and `auto terms` are now compatible with the `translations`
  block.
- Files in the Playground will be served from server rather than block
  storage.
### Fixed
- `static_image()` did not work with unqualified file names.
- Some initial blocks were not included in side-by-side translation
  files.
- Orphaned translations did not receive syntax highlighting in
  translation files.
- Indented Mako was not receiving syntax highlighting in translation
  files.
- Translations containing emojis were being truncated in translation
  files.

## [0.4.43] - 2019-05-16
### Added
- The `tag` parameter for `/list`, `/api/list`, and
  `interview_menu()`.
- The `DAContext` object and the `use objects` option for the `data`
  and `data from code` blocks.
### Fixed
- HTML error when `hide standard menu` is in use.

## [0.4.42] - 2019-05-11
### Changed
- Many CSS classes and IDs renamed and given the `da` prefix.
### Fixed
- Errors with SMS interface.
- Subclasses of `DAList` were not allowed in `list collect`.
- Inefficiency with `last_access_time()`.

## [0.4.41] - 2019-05-02
### Added
- The `get_docx_variables()` method of `DAFile` and other file
  objects.
### Fixed
- ProxyFix settings for Docker containers behind reverse proxies.

## [0.4.40] - 2019-04-29
### Fixed
- Python 2.7 error.

## [0.4.39] - 2019-04-29
### Fixed
- Variables could not be converted to JSON where `None` used as
  dictionary key.
- Compile errors due to unused non-Python-3-compliant code in copy of
  rtfng.
- Playground package description formatted as text area, which
  resulted in newlines that caused problems when uploading to GitHub.

## [0.4.38] - 2019-04-25
### Added
- The `single_to_double_newlines()` function.
- The `get_pdf_fields()` method of `DAFile` and other file objects.
- The `playground examples` directive in the Configuration.
- The `new markdown to docx` directive in the Configuration.
### Changed
- Style of chat messages updated; content of message from the monitor
  is now contained in the notification received by the end user while
  looking at a question.
### Fixed
- Python 3.5 error in utility function for Azure Blob Storage.

## [0.4.37] - 2019-04-23
### Fixed
- Error affecting Python 2.7.

## [0.4.36] - 2019-04-23
### Changed
- Syntax highlighting and word wrap for interview phrase translation files.
- New style for chat messages.
### Fixed
- PAM failure in cron on Amazon Linux.
- Link to show help tab called wrong JavaScript function.

## [0.4.35] - 2019-04-20
### Added
- The `translations` block and the interview phrase translation file
  download utility.

## [0.4.34] - 2019-04-16
### Changed
- Downgraded s3cmd.

## [0.4.33] - 2019-04-16
### Added
- `XSENDFILE` Docker environment variable.
### Changed
- API will now process JSON as well as form-data.
- By default, `xsendfile` will be set to `False` in the initial
  Configuration if `BEHINDHTTPSLOADBALANCER` is true.
### Fixed
- New version of ProxyFix not called with arguments for processing
  HTTP scheme.

## [0.4.32] - 2019-04-15
### Added
- The `as_df()` method of a table.
- The `segment`, `segment id`, and `ga id` specifiers.
- The `log format` Configuration directive.
- German translations.
### Changed
- Upgraded s3cmd.
### Fixed
- Error when reading log files in multiple server configuration in
  Python 3.

## [0.4.31] - 2019-04-07
### Fixed
- Errors with `read_qr()`.

## [0.4.30] - 2019-04-07
### Added
- The `editable mimetypes` and `editable extensions` configuration
  directives.
### Changed
- The `worker.log` no longer exempt from backup.
- The Redis database now backed up to rolling backup.
- Relaxed some restrictions on multiple developers working on same
  package in their Playgrounds.
### Fixed
- Problem with `write()` method of `DAFile`.
- Problem with creating packages when author not defined.
- Problem with `source_code` when `debug` mode not in effect.

## [0.4.29] - 2019-03-28
### Added
- The `.size_in_bytes()` method for `DAFile`.
### Fixed
- Python3 could not write to S3.

## [0.4.28] - 2019-03-28
### Added
- Portuguese translations.
### Fixed
- Swagger-generated setup.py files in ZIP files could not be parsed.
- Error with gender set to "other"

## [0.4.27] - 2019-03-27
### Added
- The `list collect` feature for allowing users to add multiple items
  of `DAList` on one screen.
### Fixed
- GitHub error with packages that have dependency packages with null
  attributes.

## [0.4.26] - 2019-03-25
### Fixed
- Enter key caused browsers to press the `question back button`.
- Newest version of `textstat` not compatible with Python 2.7.

## [0.4.25] - 2019-03-22
### Changed
- When using Google Drive Sync, deleting file from Playground now
  permanently deletes file from Google Drive, rather than send it to
  the Trash.
### Fixed
- KeyError during initial GitHub repository creation.
- Exception could be raised if docstring in a dependency module was
  bytes.
- Methods not appearing in Playground sidebar in Python 3.
- File uploads failing in Internet Explorer.

## [0.4.24] - 2019-03-21
### Added
- The `maximum content length` configuration directive.
- The `image upload type` configuration directive, feature, and field
  specifier.
### Fixed
- Error in `log` service.
- A long interview title could cause wrapping in the navigation bar on
  mobile.

## [0.4.23] - 2019-03-19
### Added
- The `progress bar multiplier` and `progress bar method` features.
### Changed
- Embedded blocks can use generic objects and iterators.
- Help buttons are now "info" color instead of "secondary" color.
### Fixed
- Error when uploading files through the API.
- Error resulting from `add_action()` under some circumstances.

## [0.4.22] - 2019-03-17
### Fixed
- Section setting error.

## [0.4.21] - 2019-03-16
### Added
- The `nav.hide()`, `nav.unhide()`, and `nav.visible()` methods.
### Fixed
- Excessive memory usage while looking for cron tasks.
- Could not upload more than one module file to Playground at the same time.
- Playground Wizard errors.

## [0.4.20] - 2019-03-13
### Added
- The `set_save_status()` function.
- The `id_tag` option to `action_button_html()`.
- Field number in error messages.
### Changed
- Removed redirects after non-standard URL parameters.
- The `add_action()` button behaves more consistently with `.gather()`.
- The `new_window` option to `action_button_html()` can be used to set
  the `target` of the hyperlink.
### Fixed
- Field trim JavaScript was affecting file variables and triggering an
  error.

## [0.4.19] - 2019-03-10
### Added
- The `only sets` modifier.
### Changed
- The `allow non-idempotent questions` specifier in `metadata` was
  removed and replaced with a Configuration directive.
- The `allow non-idempotent questions` Configuration directive is set
  to `False` by default in the default Configuration.  This will
  affect new servers but not existing servers.
- The API validation `Referer` constraint checks against the `Origin` if
  there is no `Referer`.

## [0.4.18] - 2019-03-09
### Added
- Fullscreen option for code editing.
### Fixed
- Python 3 errors during GitHub integration process.

## [0.4.17] - 2019-03-08
### Added
- The `python packages` Configuration directive and the
  `PYTHONPACKAGES` Docker environment variable.
### Fixed
- Error when updating references in .docx file.
- `object_type_repr` error raised from Jinja2.
- `filter()` returning zero elements from non-empty list caused
  re-gathering.
- Dueling `uncheck others` fields had wrong CSS after unchecking.
- Thumbnails for .docx files.
- Blanking of dates in Firefox on blur.

## [0.4.16] - 2019-03-04
### Fixed
- Playground packages copied to wrong location on Python 3.

## [0.4.15] - 2019-03-04
### Fixed
- LuaLaTeX was not properly being detected.

## [0.4.14] - 2019-03-04
### Fixed
- LibreOffice initialization encountered circularity.

## [0.4.13] - 2019-03-03
### Changed
- The `none of the above` specifier can be used with `datatype:
  object_radio`.
- The `docassemble.base.util` is now loaded by default.
- Switched to LuaLaTeX for better Cyrillic support.  Requires server restart.

## [0.4.12] - 2019-03-01
### Added
- The `allow reordering` specifier in `table`.
### Fixed
- Unicode problem reading S3 keys as strings.

## [0.4.11] - 2019-02-28
### Added
- The `error action` specifier in `metadata`.

## [0.4.10] - 2019-02-27
### Added
- The `tagged pdf` option for `docx template file` document assembly.
### Changed
- The `pdf/a` options now create PDF/A documents directly with
  LibreOffice.
- The `comma_list()` and `comma_and_list()` now work with a wider
  variety of iterables.

## [0.4.9] - 2019-02-25
### Added
- Support for sending text messages using WhatsApp using `send_sms`.
### Changed
- Non-required file upload variables will be set to `None` instead of
  being ignored.
### Fixed
- Unicode error during package upgrade when `pip show` returns bytes
  that cannot be decoded as UTF-8.
- JavaScript error with Google Maps.

## [0.4.8] - 2019-02-24
### Changed
- Upgraded Font Awesome to 5.7.2.

## [0.4.7] - 2019-02-23
### Fixed
- Unicode problem with user names.
- Unicode problem with OCR.
- SQL concurrency problem with row updates.
- The `instanceName` on file uploads.

## [0.4.6] - 2019-02-19
### Changed
- The `error help` metadata specifier now accepts a dictionary of
  language codes and messages.
### Added
- The `verbose error messages` configuration directive.
### Fixed
- Unicode problem with Markdown documents.
- Deep copy error with `get_question_data()`.

## [0.4.5] - 2019-02-18
### Changed
- Group gathering with `ask_number=True` will use the value of
  `there_are_any` if it is defined and set to false.
- When editing list using a table, completeness of elements will be
  re-evaluated.
- Back button embedded in question is now "link" style.
### Added
- The `subject_as_html()` and `content_as_html()` methods of objects
  generated from a `template`.
- The `hide navbar` feature.
- The `js_target` URL parameter for embedding the **docassemble**
  interview into an element on another web site.
- The `gathered_and_complete()` method of the `DAList` and `DADict`.
### Fixed
- Error logging in with Auth0 in Python 3.
- The `comma_and_list()` function was not Unicode-friendly.
- Method of adjusting encryption of interviews in session after
  logging in was inefficient.
- API verification not working in Python 3.
- Screen reader in Python 3.
- Playground commit not pushing to organizational repositories.

## [0.4.4] - 2019-02-15
### Added
- The `convertapi secret` configuration directive.
- API endpoints for listing and deleting Playground files.
### Fixed
- JSON serialization with unusual dict keys.
- Screen scrolling problem in Playground folders.

## [0.4.3] - 2019-02-13
### Added
- The `string_types` and `PY2` names, imported from the `six` package.
- The `allow non-idempotent questions` specifier in `metadata`.
### Changed
- The `post` screen part is now positioned below the `right` screen
  part on small screens.
### Fixed
- The screen parts feature was not fully implemented and documented.
- The `required privileges` feature was not fully implemented.
- Editing yourself through `/userlist` would disable yourself.
- Error with text-to-speech cache.
- Non-required file upload variables were being set to `'None'`
  instead of being ignored.

## [0.4.2] - 2019-02-10
### Added
- Additional SQL indexes.
- The `default screen parts` block.
- The `required privileges` specifier in `metadata`.
### Changed
- The `set_title()` function was renamed to `set_parts()` and now
  supports setting any screen part.
### Fixed
- Error with OCR.
- Error with screen reader.
- Error with `concatenate_files()`.
- The current section when showing a `nav` in a question was not
  always current.
- Wrong formatting of subsections in sections sidebar under some
  circumstances.

## [0.4.1] - 2019-02-04
### Added
- Placeholder CSS classes for customization.
- Support for alternative Redis ports and database offsets.

## [0.4.0] - 2019-02-04
### Added
- The `DAPYTHONVERSION` Docker environment variable.
- The `text_type()` function.
### Changed
- The system is now compatible with Python 3.5.
- The `subdivision_type()` algorithm was improved.
### Fixed
- The update script failed under some circumstances due to a SQL
  error.

## [0.3.36] - 2019-01-24
### Fixed
- Not all login methods were redirecting the user back to the
  interview when they should have.

## [0.3.35] - 2019-01-22
### Added
- The `resume interview after login` configuration directive.
### Changed
- The `/api/session` API endpoint and the `set_session_variables()`
  function now accept the `event_list` parameter and can get past
  `force_ask()` diversions.
- More robust code injection detection mechanism.
### Fixed
- Unicode error with certain Spanish numbers.

## [0.3.34] - 2019-01-20
### Added
- Customizability of standard validation messages using the `validation
  messages` field modifier or the `default validation messages` block.
- Option to `.geolocate()` method to populate attributes of `Address`
  using a single-string address.
- Options for setting `alt_text` using `[FILE]`, `[QR]`, `.show()`,
  and the `.alt_text` attribute on `DAFile` or `DAStaticFile`.
- The `.set_alt_text()` and `.get_alt_text()` methods of file objects.
- The `template password` option for `pdf template file` (new `docker
  run` required).
### Changed
- Upgraded Pandoc to version 2.5.1 (new `docker run` required).
- UI changes for keyboard navigation of sections.
### Fixed
- Empty documents generated by Markdown were resulting in zero byte
  PDFs rather than one-page blank PDFs from Pandoc.
- The field names on some types of PDF files were not being identified
  correctly on the Utilities screen.

## [0.3.33] - 2019-01-16
### Changed
- API calls can be authenticated with an `X-API-Key` cookie or HTTP
  header.
- API responses contain CORS-friendly HTTP headers.
### Fixed
- JSON error when running `ocr_file_in_background()`.
- XML error when assembling DOCX files.

## [0.3.32] - 2019-01-16
### Changed
- UI and HTML changes for accessibility.
### Fixed
- Timing of initialization of Google autocomplete fields resulted in
  JavaScript error in some circumstances.
- OneDrive synchronization errors due to changes in the Microsoft Graph API.

## [0.3.31] - 2019-01-14
### Changed
- Additional information added to data representation of question.
- HTML more standards-compliant for accessibility.
### Fixed
- Package update process was not detecting missing packages.
- The watchdog's process terminations were causing unnecessary
  internal server errors under high system load, mistaking a busy
  Apache process for an out-of-control Apache process.  The threshold
  has been adjusted.  The change will only take effect after a `docker
  stop` and `docker start`.  Alternatively, `docker exec` into the
  container and run `supervisorctl restart watchdog`.

## [0.3.30] - 2019-01-05
### Added
- The `/api/login_url` API endpoint.
- The `/api/user_info` API endpoint.
### Changed
- The `/api/user/new` API endpoint will now create a random password
  if a password is not provided.
### Fixed
- The `/api/user/new` API endpoint used `email` when the correct
  parameter is `username`.

## [0.3.29] - 2019-01-03
### Added
- The `question_name` option for the POST method of the `/api/session`
  API endpoint and the `set_session_variables()` function.
### Fixed
- Unicode error from `/api/secret`.

## [0.3.28] - 2018-12-31
### Added
- The `accept` specifier for `datatype: file` fields.
- The `create_user()` function.
- The `/api/user/new` endpoint.

## [0.3.27] - 2018-12-24
### Changed
- Table edit attribute names treated as "follow up" actions.

## [0.3.26] - 2018-12-21
### Changed
- Reverted `reconsider()` to 0.3.24 version.

## [0.3.25] - 2018-12-20
### Changed
- Exception raised if unsafe filename used for a `DAFile`.
### Fixed
- Problem with caching of stand-alone `attachment` blocks.

## [0.3.24] - 2018-12-17
### Added
- The `inline` keyword parameter for the `url_for()` method.
- The `describe()` method of the output of `date_difference()`.
### Changed
- The result of `date_difference()` when reduced to text now runs the
  `describe()` method instead of stating the number of days.
- The `space_to_underscore()` function now uses
  `werkzeug.secure_filename()` and replaces more than just non-ASCII
  characters and spaces.
### Fixed
- Error in `.export()` method of tables.

## [0.3.23] - 2018-12-15
### Added
- The `get_question_data()` function.
### Fixed
- Error from Playground sidebar for interviews using `imports`.

## [0.3.22] - 2018-12-14
### Added
- Insertion of PDF files into DOCX files.
- Links in Playground sidebar to source code on GitHub.
### Changed
- Data representation of a question now includes plain attachment file
  numbers.
### Fixed
- Not all thread local variables were reset before request.
- Unicode error when exporting README.
- Azure Blob storage missing content type.

## [0.3.21] - 2018-12-10
### Added
- The `object labeler` option in `fields`.

## [0.3.20] - 2018-12-08
### Added
- The `exclude_privileges` keyword parameter of the
  `last_access_time()` function and related functions.
### Changed
- The `/api/user_list` API method and the `get_user_list()` function
  now return a user's privileges under a dictionary key called
  `privileges`.  Previously the key `roles` was used.
### Fixed
- The `update()` and `has_key()` methods of `DADict` did not work.
- Multiple `template`s on a screen using iterators did not work
  correctly.
- Browser back button sometimes required two clicks to go back one
  step.
- Unhelpful error when uploading invalid file type to Wizard.
- Temporary PDF files accumulating in `/tmp`.

## [0.3.19] - 2018-12-02
### Added
- The `DAOrderedDict` class.
### Changed
- Protections against adding non-modules to Modules folder.
- Keep memory of visited sections when the available sections change.
### Fixed
- Visiting `/user/sign-in` or `/user/register` while being signed in
  will now redirect to the `auto resume interview`, if any.

## [0.3.18] - 2018-11-30
### Fixed
- Unicode error in text to speech engine.

## [0.3.17] - 2018-11-30
### Added
- The `.show(editable=False)` option for tables.
- The `include_dict` option for `interview_list()`.
- The `formatted_unit()` method for `Address`.
### Changed
- Icons on the User List page highlighting users with special
  privileges.
- Admin users cannot take away their own admin privilege.
- Admin users cannot disable their own accounts.
### Fixed
- Validation error messages in admin pages were black when they should
  have been red.
- Typo in `.add_action()` method for `DADict()`.
- Error during `.export()` because `pandas` erroneously requires a
  nanosecond attribute in dates.
- Error in `instanceName` guessing in the context of a function.

## [0.3.16] - 2018-11-26
### Added
- The `export()` method of tables.

## [0.3.15] - 2018-11-26
### Added
- The `overlay_pdf()` function.

## [0.3.14] - 2018-11-25
### Added
- The `.filter()` method of the `DAList` class.
- The `mmdc()` function for generating diagrams and flowcharts with
  mermaid.  Requires system upgrade.

## [0.3.13] - 2018-11-23
### Added
- "Sync and Run" button in the Playground.

## [0.3.12] - 2018-11-22
### Fixed
- Problem with `value()` using a variable as an iterator.

## [0.3.11] - 2018-11-15
### Added
- The `/api/playground` file upload feature.

## [0.3.10] - 2018-11-13
### Added
- The `page after login` feature.

## [0.3.9] - 2018-11-10
### Added
- The `allow for`, `required for`, `allow sms`, and `allow app`
  options of `two factor authentication`.
- The `progressive` option for `sections`.

## [0.3.8] - 2018-11-04
### Added
- The `backup days` configuration directive.
### Fixed
- The `word()` function did not work on words with non-ASCII
  characters.
- Empty fields question skipping did not work where variable was
  attribute of a non-existent object.
- Interviews that changed the language changed the language of the Playground.

## [0.3.7] - 2018-10-28
### Fixed
- Error importing `textstat`.

## [0.3.6] - 2018-10-28
### Changed
- Validation is now applied in required fields so that spaces alone
  cannot bypass validation.
- Color of pressed button now "secondary" rather than "success" and
  colors of non-pressed buttons now "light" instead of "secondary."
### Fixed
- Problem with editing lists where the `complete_attribute` is not
  defined by a `code` block.
- No proper error message when a non-text string is used as a variable
  name in `fields`.
- Problems with locking-related changes from 0.3.5.
- Admin users were allowed to give `admin` privilege to users with
  social logins.
- Python error in cron.py.

## [0.3.5] - 2018-10-23
### Added
- The `edit_url_only` and `delete_url_only` parameters to the
  `item_actions()` methods.
- The `url_only` parameter to the `add_action()` method.
- The `url_ask()` and `action_button_html()` functions.
### Changed
- A `message` parameter to `add_action()` is now passed through
  `word()`.
- Removed the new feature from 0.3.3 where interview answers are saved
  before a `leave`.
- Different method of locking while copying playground modules.
### Fixed
- Percent signs in `number` fields may have avoided validation.
- Database access for chat log not protected by locking.

## [0.3.4] - 2018-10-20
### Fixed
- Links not appearing in the inline navigation bar.
- Toggle button not present in the vertical navigation bar.

## [0.3.3] - 2018-10-19
### Added
- The ability to set a `read only` attribute on a `table` to indicate
  that some rows cannot be deleted or edited.
### Changed
- Editing a table will cause the definition of the `complete_element`
  attribute, if any, to be recomputed after the `edit` attributes are
  sought.
- Interview answers saved before a `leave`.
- Background task callbacks that raise exceptions will no longer save
  interview answers.
### Fixed
- Dependencies not being properly scanned from `setup.py` files.
- Review screen resume button that set variable had unicode instead of
  boolean data type.
- Text was not scanned for emojis unless `images` were defined or the
  `default icons` directive was set.
- The `get()` method of `DADict` did not work.
- Random errors where dictionary cannot be retrieved (potential fix).
- The `minimum_number` feature introduced in 0.3.2 did not work on
  `table`s based on `DADict` objects.
- Elements could not be added through `add_action()` when the list was
  empty.
- The `rows` directive of a table resulted in an error if the
  expression used a compound operator (e.g., `+`).
- Changes to fields made by remote user not reflected in observer window.
- Back button did not work when remote controlling.
- Updated deprecated pandas code in the machine learning module.

## [0.3.2] - 2018-10-13
### Changed
- Using `table` with a `DADict` now sets `row_index` to the key and
  `row_item` to the value, and `DADict`s can be edited using tables.
- No delete buttons on a `table` when deletion would cause the number
  of items to fall below `minimum_number`.
- The `edit` option on a `table` can now use reference indices as well
  as attributes.
- The default `message` for the `add_action()` method on a group is
  "Add an item" if the group is empty.
- Clicking on a navigable section header empties the action queue,
  ensuring that clicking "Resume" puts the user back in the interview,
  rather than the screen they saw before they clicked the header.
### Added
- The `delete buttons` option when using `edit` on a `table`.
- The `only_if_empty` option on the `reset_gathered()` method.
- The `slice` method of the `DADict` class.
- The `re_gather` attribute of groups to `basic-questions.yml`.
- The `follow up` option in a `review` block `fields`.
- The `reconsider()` function.
- The `preloaded modules` configuration directive.
- The `action_button_html()` function.
### Fixed
- URL for restarting interview session conflicted with another URL
  when user logged in.
- `table`s could not appear inside of `review` blocks because they
  were always undefined.
- Navigable section headers not styled correctly.
- One of two processes simultaneously loading the playground modules at
  same time could encounter an empty directory.
- Screen loads through `url_action_perform()` did not show the
  spinner.
- Some thread variables were not reset between requests.
- The OCR background function did not work, so rolled back celery and
  kombu to 4.1.0.

## [0.3.1] - 2018-10-02
### Changed
- When a variable is force-asked or the goal of an action and a
  `question` is not found, no error will be raised.  This facilitates
  the use of optional follow-up questions in a `review` block.
### Fixed
- Aliased template variables generated pickle errors.

## [0.3.0] - 2018-09-28
### Changed
- Upgraded OS from Debian stretch from Debian jessie.  Upgraded pandoc
  to version 2.3.  LibreOffice upgraded to version in
  stretch-backports.  A system upgrade is required to realize these
  changes.
- Setting a `minlength` on a `datatype: checkboxes` field turns off the
  "None of the above" item.

## [0.2.102] - 2018-09-27
### Changed
- LibreOffice upgraded to version in jessie-backports.
### Added
- Options for `new_session` and `exit_logout` under buttons,
  `command()`, and `url_of()`.
### Fixed
- Logging in with e-mail and password where e-mail already used for a
  social login generated an exception.

## [0.2.101] - 2018-09-25
### Changed
- The `.copy_into()` method of `DAFile` now accepts `DAFile`,
  `DAStaticFile`, `DAFileList`, and `DAFileCollection` objects as
  the argument, as well as the direct file path of the other file.
### Fixed
- Problem with converting to PDF after `update references` for some
  tables of contents.
- The `.copy_into()` and `.from_url()` methods now update PDF and
  image information after the file contents change.

## [0.2.100] - 2018-09-23
### Added
- The `forget_result_of()` and `re_run_logic()` functions.
- Additional test interviews.
### Changed
- `note` and `html` can now be used to insert text in the right
  column, along side a field.
### Fixed
- The `minlength` and `maxlength` modifiers did not work on
  `checkboxes`.
- The `insert_docx_template()` function was not intercepting all
  parameters of class `DAObject` and passing them as objects.
- Too many line breaks in .docx address block.
- Static file videos did not work.
- Static file videos were static width.

## [0.2.99] - 2018-09-19
### Added
- The `back button` and `back button label` modifiers.
- The `show login` directive in interview `metadata`.

## [0.2.98] - 2018-09-18
### Fixed
- Error in Word manifest XML file.

## [0.2.97] - 2018-09-18
### Added
- Playground "Variables, etc." for the Word task pane.
### Changed
- It is no longer necessary to remove curly quotes from .docx Jinja2
  code.  They will be converted to straight quotes before processing.
### Fixed
- Google Maps JavaScript was loading synchronously, which slowed down
  loading.
- A `choices` list could not contain a list of numeric, boolean,
  or `NoneType` values.
- `DAStaticFile`s could not be inserted into .docx templates.

## [0.2.96] - 2018-09-12
### Added
- Integration between Microsoft OneDrive and the Playground.
- The `debug` directive inside `features`.
### Changed
- Upgraded Font Awesome to 5.3.1.

## [0.2.95] - 2018-09-08
### Added
- The `update references` setting on `attachment`s.

## [0.2.94] - 2018-09-05
### Added
- The `redact()` function and `redact` option on `attachment`s.
### Changed
- The `template` and `table` blocks now become `DALazyTemplate`
  objects rather than `DATemplate` objects.  Their contents are
  evaluated at the time they are reduced to text, not at the time they
  are created.
### Fixed
- Problem with `currency()` and other functions when used from a `docx
  template file` where undefined variables did not raise exceptions.
- The `create_new_interview()` function caused unnecessary 4 second delay.
- Users with `user` privileges could not access API key management.
- The `interview_url()` function was returning a URL based on how the
  current request was made, rather than the actual URL for getting to
  an interview.

## [0.2.93] - 2018-08-31
### Fixed
- Problem with `DATemplate` variables with string indices.

## [0.2.92] - 2018-08-27
### Added
- The `show progress bar percentage` feature.
### Changed
- The `background_response()` function can be called using
  `background_response('refresh')` to refresh the user's screen.

## [0.2.91] - 2018-08-25
### Added
- The `getField()` and `setField()` JavaScript functions.
### Fixed
- The `fields` version of `background_response()` could not set radio
  buttons.

## [0.2.90] - 2018-08-23
### Fixed
- Problem with checkboxes inside a `show if`.

## [0.2.89] - 2018-08-20
### Changed
- The `variables_as_json()` function now accepts `include_internal` as
  a keyword parameter.
- The `variables_as_json()` function now produces pretty-printed JSON
  output.
- Only ordinary users will see flash messages about switching to a
  different interview.
### Fixed
- Template and static file deletion in Playground.
- Setting the instance name of items that are already in a list.
- Non-mandatory questions were being marked as answered in the
  internal dictionary.

## [0.2.88] - 2018-08-20
### Fixed
- The recent version of WTForms is incompatible; set to 2.1.
- The `simplify` parameter of `get_session_variables()` was fixed to `True`.

## [0.2.87] - 2018-08-19
### Changed
- Moved interview HTML into a `<div>` to provide compatibility with
  add-ons.

## [0.2.86] - 2018-08-17
### Added
- The `js show if` and `js hide if` field modifiers.
- The `val()` JavaScript function.
- The `continue button field` feature.
### Changed
- Upgraded Font Awesome to 5.2.0.
- Two `DAList`s added together will yield a `DAList`.
### Fixed
- `zip_file()` returned an empty archive when given a
  `DAFileCollection`.

## [0.2.85] - 2018-08-15
### Fixed
- Problem with screen reader flagging help text with Markdown
  formatting as a defined term.
- Problem with Internet Explorer passing through commas in numeric
  values.

## [0.2.84] - 2018-08-13
### Changed
- Word processing files and text files can now be included in
  documents in the same way that images can.
- Reducing a `DAFileCollection` to text no longer attempts to show all
  versions in the collection, but only includes one.

## [0.2.83] - 2018-08-11
### Changed
- Playground UI highlights most recently edited files.
### Fixed
- Writing to `DAFile`s.

## [0.2.82] - 2018-08-08
### Changed
- Some exceptions raised by Jinja2 will now be accompanied by a
  snippet of document context.
### Added
- Initial support for Travis CI deployment.
- Method `.slurp()` for `DAFileList`.
### Fixed
- Setting of text fields to `None` when the value is the string
  `"None"`.
- Vertical alignment of section labels in horizontal mode.
- User text causing Pandoc to enter LaTeX math mode.
- Reconstruction of certain types of bookmarks after adding signature
  to PDF.
- Addresses that normalize without a street address.

## [0.2.81] - 2018-07-31
### Changed
- Interviews are now served from `/interview` rather than `/`.  This
  change is backward-compatible.
- Error notification e-mails will no longer include the interview
  variables as a JSON file unless `error notification variables` is
  set to true in the Configuration.
- Non-mandatory blocks no longer get tracked in the internal
  dictionary as having been answered.
### Added
- The `root redirect url` Configuration directive.
- The `include_internal` parameter of `all_variables()`.
- Warning if `mandatory` is used on a block that does not support the
  `mandatory` modifier.
### Fixed
- Missing unique IDs for API calls.
- HTML typo in Logs page.

## [0.2.80] - 2018-07-24
### Added
- The `/me` resource with information about the user.
### Changed
- JSON returned by API and `/vars` is now pretty-printed.
- Referencing a non-existent section no longer triggers an error.

## [0.2.79] - 2018-07-21
### Changed
- The `append` method to the `DAList` class now accepts an optional
  keyword argument `set_instance_name`.
### Fixed
- Any package name starting with `base` or `demo` was being blocked
  when `allow demo` was not set to `False`.

## [0.2.78] - 2018-07-17
### Added
- The `index()` method of the `DAList` class.
### Changed
- File uploads are now at the top of the screen in Playground folders.
### Fixed
- Problem with `datatype: checkboxes` and `show if`.

## [0.2.77] - 2018-07-13
### Fixed
- The `post` HTML was missing on signature pages.
- The `value()` function was not working properly.

## [0.2.76] - 2018-07-11
### Fixed
- Possible fix for "group by" SQL error in `user_interviews()`.

## [0.2.75] - 2018-07-11
### Added
- The `step` option for `datatype: number` and `datatype: currency`.
### Changed
- Fields with `datatype: number` are no longer limited to two decimal
  places.
### Fixed
- The "exit" command was logging the user out.

## [0.2.74] - 2018-07-11
### Added
- The `error help` configuration and metadata directives.
- The `.copy_shallow()` and `.copy_deep()` methods of `DAObject`s.
### Changed
- Error e-mails now attempt to attach the interview variables as a
  JSON file.
### Fixed
- Error in cron about missing `session_uid`.
- Auth0 login was erroneously enabled by default.

## [0.2.73] - 2018-07-07
### Added
- The `set_instance_name` option for use with `elements` when
  initializing a `DAList`.
- The `skip undefined` option for `review` blocks.
### Changed
- The `block()` method of `Address` now includes the word "Unit"
  before the unit, if the unit exists.
- On iOS mobile devices, an `<optgroup>` is now added to `<select>`
  via JavaScript.
### Fixed
- Vertical spacing between buttons in the Actions column of a table.
- Templates with variable names containing iterators were not being
  regenerated.
- Default date values were not displayed in `fields`.

## [0.2.72] - 2018-06-27
### Fixed
- Error message when publishing to PyPI.
- Unicode error in YAML dump.

## [0.2.71] - 2018-06-21
### Added
- The `undefine`, `recompute`, and `set` options inside of a `review`
  block.
### Changed
- To indicate that a multiple-choice under `fields` should use `radio`
  buttons, a `pulldown`, or a `combobox`, use `input type` instead of
  `datatype`.  The `datatype` can then be set to something else, like
  `number`.  This change is backwards compatible.
- Removed sublocality from normalized addresses.
### Fixed
- The `show if` JavaScript comparison is now more lenient when the
  values look like numbers.
- The `delete_all` function did not delete all interviews.
- The `defined` function did not work well with lists and dictionaries
  in the process of being gathered.

## [0.2.70] - 2018-06-14
### Changed
- Calls to `force_ask()` and calls to actions now result in more
  persistent variable seeking.
- Improved editing of lists.
### Fixed
- Using `show if` with `datatype: file`.
- Using `show if` with a value of `0`.

## [0.2.69] - 2018-06-12
### Fixed
- Section headers with hyperlinks.
- Google Drive with a large number of files.

## [0.2.68] - 2018-06-10
### Fixed
- Problems with Google Drive timestamps when cloud storage in use.
- Invalid use of echo in Dockerfile.

## [0.2.67] - 2018-06-09
### Changed
- When a non-text field is not required, and the user does not provide
  a value, the variable will be set to `None`.
- Required field markers show differently in some contexts.
- Additional log messages for Google Drive.
### Added
- New Debian dependencies `ttf-mscorefonts-installer`,
  `fonts-ebgaramond-extra`, `ttf-liberation`, and `fonts-liberation`
  in Docker.
### Fixed
- Problems with Google Drive initial set-up.

## [0.2.66] - 2018-06-07
### Changed
- Code editing boxes are now sized relative to screen size.

## [0.2.65] - 2018-06-06
### Added
- Login via Auth0.
### Fixed
- Better error handling after uploads.
- Better error handling during software updates.

## [0.2.64] - 2018-05-31
### Added
- Feature for uploading files through dataurls to the Template Folder
  of the Playground.
### Changed
- Comboboxes now accept free text input.
### Fixed
- PDF bookmarks restored after inserting images.

## [0.2.63] - 2018-05-25
### Added
- The `error notification email` configuration option.
### Fixed
- Error with PDF fields and signature overlay.

## [0.2.62] - 2018-05-23
### Added
- JSON interface to the "Variables, etc." and list of Playground
  files.
### Fixed
- Error during invitation and registration.

## [0.2.61] - 2018-05-19
### Changed
- The `disable others` directive now accepts a list of fields.
- Most natural language functions now accept an optional keyword
  parameter `language`.
- The `country` and `subdivisionfirst` database fields have longer
  allowable lengths.
- Additional system phrases are translatable.

## [0.2.60] - 2018-05-15
### Fixed
- Error on registration page.

## [0.2.59] - 2018-05-15
### Added
- Horizontal navigation bar option.
- Option for disabling the `pip` cache when installing a package.
- The `validation_error()` function and the `DAValidationError` error
  type.
### Changed
- The `interview_list()` function now returns `temp_user_id`.
### Fixed
- PDF assembly resulted in a missing AcroForm error in some circumstances.
- PyPI publishing code used out-of-date upload URL.
- Deleting session in multi-user interview deleted sessions for all
  users.
- Visiting registration page while logged in did not redirect to My
  Interviews page.
- An inappropriate error was raised about `validate` input validation
  functions for certain input types and values.

## [0.2.58] - 2018-05-08
### Added
- Version number on the Package Management page.
### Fixed
- Problem with checkboxes inside of `show if`.
- CSS problem with the "required" asterisk.

## [0.2.57] - 2018-05-07
### Added
- The `validation_error()` function.
- The `num_pages()` method on `DAFile`, `DAFileList`, and
  `DAFileCollection` objects.
### Changed
- On the mobile `signature` page, the "Clear" button is replaced with
  a "Back" button.
- Python `validate` code now works on document uploads.
### Fixed
- The `question back button` was missing from the buttons on the
  desktop `signature` page.
- Problem with spacing of the `question back button` next to other
  buttons.

## [0.2.56] - 2018-05-07
### Changed
- The `min` and `max` field modifiers on `datatype: date` fields now
  accept a wider range of date formats.

## [0.2.55] - 2018-05-06
### Changed
- The `DACloudStorage` object can now be initialized to use
  Configuration directives other than `s3` and `azure`.
- The `min` and `max` field modifiers now work with `datatype: date`.
### Added
- The `slurp()` method for `DAStaticFile` objects.
- Support for editing HTML and other text file formats in the Static
  Files folder of the Playground.
### Fixed
- List of branches in pull-down cut off at a certain length.
- Live Help had problems with encryption.
- Missing help button on `field` with `choices`.

## [0.2.54] - 2018-05-05
### Fixed
- Bug in `set_info()`.

## [0.2.53] - 2018-05-02
### Changed
- Social logins now populate first and last name in the user profile.
- The `all_variables()` function now has an optional keyword argument
  `special` that returns information about an interview that is not
  stored in the variables.
### Added
- Support for `long_description` in setup.py files.
### Fixed
- Update button in `/updatepackage` reverted package to `master`
  branch.
- Unicode problem in `/logs`.

## [0.2.52] - 2018-05-01
### Fixed
- The setup.py file for `docassemble.webapp` did not depend on
  particular versions of `docassemble.base` and `docassemble`.

## [0.2.51] - 2018-05-01
### Changed
- The `advocate` privilege grants access to see user information using
  the API.
- The `interview_list()` function and `/api/interviews` API now act
  upon interviews of anonymous users.
### Fixed
- Questions not centered on screen when navigation bar in use but empty.
- Google Places API populating `unit` with `subpremise` and leaving
  `city` blank.

## [0.2.50] - 2018-04-28
### Changed
- Upgraded user interface from Bootstrap 3.3 to Bootstrap 4.0.0.
- Headless Chrome now used by default in `lettuce` tests.
### Added
- The `show dispatch link` Configuration directive.
### Fixed
- Exception triggered by importation of word translation files with
  YAML errors.
- The `indefinite_article()` function used "a" for any capitalized
  word.
- Issue where Chrome extensions interfered with file uploads.

## [0.2.49] - 2018-04-15
### Fixed
- Use of deprecated flag when calling `pip`.

## [0.2.48] - 2018-04-14
### Changed
- The `Address` methods no longer require `.city` to be defined.
- The `Address` object and the `address autocomplete` feature now
  use more of the possible address components of addresses returned by
  the Google APIs.
### Fixed
- Bug in code for getting temporary URLs to cloud storage.

## [0.2.47] - 2018-04-12
### Fixed
- Problem with quoting glossary terms in HTML.

## [0.2.46] - 2018-04-11
### Fixed
- Bug in new `show if` code.

## [0.2.45] - 2018-04-11
### Fixed
- Identification of names of ZIP files uploaded through Package Management.
- Exception raised by Unicode non-breaking spaces in interview files.
- The `show if` JavaScript feature now works with checkbox values.

## [0.2.44] - 2018-03-31
### Added
- The `analytics id` subdirective of the `google` Configuration directive.
### Changed
- Nested `show if`s are supported.
### Fixed
- Exception caused by mandatory `review` blocks without an `event`,
  `field`, or `sets`.

## [0.2.43] - 2018-03-28
### Changed
- JavaScript specific to a question now executes after `raw global javascript`.
### Fixed
- Exception caused by ampersands in docx template field values.
- Exception caused by unicode in parameters passed to `include_docx_template()`.
- Place Autocomplete returning `undefined` for some address components.

## [0.2.42] - 2018-03-25
### Added
- The `zip_file()` function.
- The `allow downloading` modifier.
- The `centered` feature.
- The `right` question part.
### Changed
- The `allow emailing` modifier now accepts Python code.
- Margins in navigation bar.
### Fixed
- Version of `Flask-User`.

## [0.2.41] - 2018-03-24
### Added
- The `DACloudStorage` and `DAGoogleAPI` objects.
- The `/api/file/<file_number>` API.
- The `delete_variables` option for the POST operation of the `/api/session` API.
### Changed
- Less stringent input sanitation so that Playground files with
  parentheses can be deleted.
- Labels inside buttons will now wrap.
### Fixed
- Escaping of anchor text in `DALink`s.

## [0.2.40] - 2018-03-19
### Added
- The `.complete_elements()` method of `DAList` and `DADict`.
### Fixed
- Removed any dependency on `import pip`.

## [0.2.39] - 2018-03-15
### Changed
- The `review` block can now be used with `field` instead of `event`.
- Temporarily removed warning about `content file`.
### Fixed
- Issue with pressing enter causing two screens to submit.

## [0.2.38] - 2018-03-14
### Added
- The `show interviews link` configuration directive.
### Changed
- The user profile link in the menu will always be shown if the user
  has `admin` privileges.
- Different formatting of user list.
- Author name and e-mail in "Packages" folder of Playground.
### Fixed
- Problem with `show if` not recognizing `False` value of checkbox
  yes/no field.

## [0.2.37] - 2018-03-10
### Added
- Example for `user_logged_in()`.
- Example for appending a row to a Google Sheet.
- The `scale` option for the `range` datatype.
### Changed
- The `include_docx_template()` function accepts keyword parameters.
  This has the effect of including Jinja2 `set` commands at the
  beginning of the included sub-document.
### Fixed
- Error when registering.

## [0.2.36] - 2018-03-08
### Added
- The `DALink` object type, which allows hyperlinks to be inserted
  into .docx files.
### Changed
- The `showif()` and `showifdef()` functions can now be configured to
  return a default value other than the empty string.
### Fixed
- Cron jobs and environment variables.  This requires a system reset.

## [0.2.35] - 2018-03-06
### Changed
- Replaced Package Management with the former "Update a Package."
### Fixed
- Issues with unicode.

## [0.2.34] - 2018-03-06
### Added
- The `main page pre`, `main page submit`, and `main page post`
  configuration directives.
- The `pre`, `submit`, and `post` metadata items.
### Changed
- Pressing enter has effect of pressing Continue, even on pages
  without input elements.
### Fixed
- Issues with unicode.

## [0.2.33] - 2018-03-04
### Fixed
- Problem with using Upgrade button.

## [0.2.32] - 2018-03-04
### Added
- The `ldap login` configuration directive.  Using this feature will
  require a system upgrade (running a new instance), as the
  `libsasl2-dev` `libldap2-dev` Debian packages are required
  dependencies of the `python-ldap` Python module.

## [0.2.31] - 2018-03-02
### Added
- Configuration directives `use font awesome` and `default icons`.
- CSS support for Material Icons.
- The `question help button` feature.
- Ability to `label` the help tab.
### Fixed
- Reference to non-existent image file during image preloading.
- Error when reviving SMS session for which answers had been deleted.
- SMS interface bugs related to signatures and attachments.

## [0.2.30] - 2018-02-27
### Changed
- SVG instead of PNG for images in checkboxes and radio buttons.
### Fixed
- Page layout when side navigation bar in use.
- Slow submit time when many checkboxes are used.

## [0.2.29] - 2018-02-25
### Added
- The `define()` function.
- The features `question back button` and `navigation back button`.
- The `raw global css` and `raw global javascript` configuration
  directives.
### Changed
- Main content block for page is now centered on desktop.
### Fixed
- Problem with calling background action from code triggered by the API.
- Problem with including a table while gathering the rows of the table.

## [0.2.28] - 2018-02-08
### Added
- The `enable remember me` configuration directive.
### Changed
- The `repr()` of a `DAList`, `DADict`, or `DASet` is the `repr()` of
  its elements, and `repr()` triggers the gathering process.
- The `.salutation()` method of the `Individual` object now uses the
  optional attributes `.salutation_to_use` and `.is_doctor`.
### Fixed
- Problem with `exclude` on a manual list of choices.
- Lack of curly quote in "I don't know" buttons.
- JavaScript error introduced in 0.2.23 that interfered with `hide if`
  functionality.

## [0.2.27] - 2018-01-31
### Added
- The `start_time()` function.
- The `package protection` configuration option.
### Changed
- The `last_access_time()` now returns the last access time as a
  datetime object with a time zone; previously the object was "naive"
  with respect to time zone.
### Fixed
- Problem with branch name of new GitHub repository.
- Problem with `as_datetime()` converting times to midnight when the
  argument is already a datetime object.
- Problem with `noyes` and `noyeswide` checkbox fields.

## [0.2.26] - 2018-01-29
### Fixed
- Problem where `format_date()` was acting like `format_datetime()`.

## [0.2.25] - 2018-01-29
### Changed
- Tweaks to the `interview_url()` function.
### Fixed
- Unicode error on interview page after interview decryption failure.
- Problem with list gathering and `.there_is_another`.

## [0.2.24] - 2018-01-28
### Fixed
- Problem with missing uid in background tasks.

## [0.2.23] - 2018-01-28
### Added
- The `DADateTime` class.
- The `time` and `datetime` `datatype`s for fields.
- The `format_datetime()` function.
- The `/api/session/back` API and the `go_back_in_session()` function.
- The `/api/privileges` and `/api/user/<user_id>/privileges` APIs, and
  the `manage_privileges()` function.
- The `.as_serializable()` method of the `DAObject`.
### Changed
- The `/api/session` POST API now returns the current question, unless the
  `question` data value is set to `0`.
- The `/api/session` POST API now accepts file uploads.
- Changed the name "roles" to the name "privileges" in the
  user-related APIs.
- The `set_user_info()` function can now be used to change user
  privileges.
- Fields with `datatype: date` will now set a variable of type
  `DADateTime`, rather than a plain text variable.
- The `today()` now returns a `DADateTime` object if it is called
  without a `format` parameter.
- The JavaScript for the `show if` and `hide if` functionality now
  animates the showing and hiding of fields.

## [0.2.22] - 2018-01-23
### Added
- Configuration directive `allow demo` for allowing demonstration
  interviews in production mode.
- Ability to send e-mail using the Mailgun API instead of SMTP.
- The `decimal places` option for automatically formatting floating
  point numbers passed to DOCX and PDF forms using `field code`,
  `code`, or `field variables`.
### Changed
- If the `checkin interval` configuration directive is set to `0`, the
  browser will not "check in" at all.
- When the `/api/session/question` API encounters an undefined
  variable for which a definition is not available, it will no longer
  return an error code, but will return a success code and indicate
  what variable was not defined.
### Fixed
- Invalid HTML in navigation bar.
- Removed unnecessary invalidation of interview cache.
- Problem with address autocomplete when variable name contains a bracket.

## [0.2.21] - 2018-01-19
### Added
- The `get_chat_log()` function.
- An API interface.
- Administrative functions.
### Fixed
- Result of `user_interviews()` was reporting the wrong `utc_modtime`.
- Error with `google maps api key` when an `api key` alone was set under
  `google` in the Configuration.
- Problem with formatting of chat log after going back into a session.

## [0.2.20] - 2018-01-14
### Added
- The `send_fax()` function for sending faxes using Twilio.
- The `include_docx_template()` function for including .docx content
  within a .docx file.

## [0.2.19] - 2018-01-12
### Added
- Ability to run `interview_list()` on all users.  Additional keys
  `user_id` and `email` are included in results.
- Integrated the Place Autocomplete feature from the Google Places API.
### Fixed
- Bug in YAML parser triggered sometimes by fields with blank labels.
- Newline to space error in docx templates that affected Word but not LibreOffice.

## [0.2.18] - 2018-01-06
### Added
- The `user` and `environment` datatypes.
### Fixed
- Typo in HTML when `camera` and other HTML5 upload datatypes were used.

## [0.2.17] - 2018-01-04
### Changed
- Better features in background actions for handling exceptions.
### Added
- The `background_error_action()` function.

## [0.2.16] - 2018-01-01
### Fixed
- Problems with cron jobs, including an error in the documentation;
  the variable is not `use_cron`, but `allow_cron`.

## [0.2.15] - 2018-01-01
### Changed
- When filling a PDF form, the Document JavaScripts and Field
  Calculation Order of the template file will be reproduced in the
  resulting PDF file.
- When concatenating PDF files, the Document JavaScripts and Field
  Calculation Order of the first file will be reproduced in the
  resulting PDF file.
### Fixed
- Problem with using specific person as sender of an e-mail.

## [0.2.14] - 2017-12-27
### Added
- Customizable 404 error message.
- The `any_true()` and `all_true()` methods for the `DADict` object.
### Fixed
- Typo in password complexity error message.

## [0.2.13] - 2017-12-24
### Added
- Ability to change the `password complexity` requirements in the
  Configuration.
- Ability to control whether registering users must retype their
  passwords.

## [0.2.12] - 2017-12-24
### Fixed
- The `for` attributes of `<label>` elements were mislabeled when a
  field with `show if` defined the same variable.

## [0.2.11] - 2017-12-18
### Fixed
- Problem with validating fields inside `show if`.

## [0.2.10] - 2017-12-15
### Fixed
- Problem recognizing string indices in code.

## [0.2.9] - 2017-12-15
### Fixed
- Problem with dictionaries inside of dictionaries.
- Some of the administrative page customizations did not work.

## [0.2.8] - 2017-12-14
### Fixed
- Inserting images into PDFs using `field code`.

## [0.2.7] - 2017-12-13
### Added
- Configuration directives for inserting HTML, CSS, and JavaScript
  into administrative pages.

## [0.2.6] - 2017-12-12
### Fixed
- GitHub pagination problem with `links_from_header`.

## [0.2.5] - 2017-12-12
### Changed
- The `global css` and `global javascript` now apply to all pages on
  the site.
- Curly quote conversion is re-enabled.
### Added
- Password protection on generated PDF files.
### Fixed
- Documents with `variable name`s containing generic object or
  iterator references can now be used with `attachment code`
- Error when uploading Zip file to Playground packages folder.
- Problem setting boolean character of yesno variables that are
  specified using brackets.
- Problem with referring to `get_url_from_file_reference()` outside of
  request context.

## [0.2.4] - 2017-12-06
### Changed
- Automatically remove newlines from e-mail subject lines
- PDF thumbnails now have the filename as the "title."
- Background tasks no longer try to process responses if exception
  triggered.
### Added
- Ability to set `exit link` and `exit label` in metadata and
  `set_title()`.
### Fixed
- Error when pulling "master" branches of GitHub packages into the
  Playground.
- Flash message showing when interview YAML file changes and "allow
  login" is False.

## [0.2.3] - 2017-12-04
### Changed
- Turned off automatic curly quote conversion until Unicode error
  in textstat can be fixed.

## [0.2.2] - 2017-12-04
### Added
- Pulling and pushing using GitHub branches.
- The `.failed()` method on result of background task.

## [0.2.1] - 2017-11-30
### Changed
- The hard-coded limit on JSON nesting depth, which was mentioned
  in the 0.2.0 changes, has been changed from 6 to 20.
### Fixed
- Apache could not start unless Docker container started with a
  `DAHOSTNAME`.
- GitHub push using GitHub integration failed because of an SSH
  issue.

## [0.2.0] - 2017-11-29
### Added
- The `logo` option of `set_title()` and `metadata`.
### Changed
- The `all_variables()` and `variables_as_json()` functions now
  contain a limitation on nesting depth.  The limit is hard-coded at
  6 levels, after which values will be "null."  This is to prevent
  exceptions being triggered by circular references.
- Setting Google Drive Synchronization folder to "Do not link" will
  now erase the connection between the OAuth app and the user.
- When populating PDF checkboxes, passing `None` to the checkbox or to
  the `yesno()` or `noyes()` functions will result in the box not
  being checked.
- Apache web server variables are now reset after a restart (e.g.,
  after the Configuration is changed.
- When pulling the contents of a **docassemble** extension package
  into the Playground, it will now remember the GitHub URL or PyPI
  package name so that when you go to Pull again, you will not need to
  retype.  This works even if you have not enabled GitHub integration.
### Fixed
- PDF checkbox inconsistencies.
- Git pull into Playground packages without integration generated an
  error message.
- When datatype is object and variable existed, it would try to reduce
  the object to text in order to see if it should be highlighted as a
  pre-selected default value.

## [0.1.99] - 2017-11-23
### Added
- Option for changing the UID and GID of www-data within the Docker
  container, so that `/usr/share/docassemble/files` can be mounted as
  a Docker volume and the Playground files can be edited.
### Changed
- Multiple choice questions in `fields` will set boolean `True` or
  `False` if those are the only options.
- Additional headers are set to enable cross-site resource sharing
  if the CROSSSITEDOMAIN variable is set.
- Apache configuration files in Docker are configured differently;
  existing site configuration files will not be overwritten and
  configuration options are now implemented as Apache variables.
- `DAList` objects now work with the `+` operator; a regular list can
  be added to a `DAList` but not the other way around.
### Fixed
- The `uncheck others` feature triggered an error if it was not the
  last field.

## [0.1.98] - 2017-11-20
### Changed
- Going to "/exit" will now log out the user, if the user is logged
  in.
- When using `&json=1` for JSON responses, the `interface()` function
  will return `'json'`.
### Added
- Action for `logout`, which works like `exit` but also logs the user out.
### Fixed
- Default values in object choices.

## [0.1.97] - 2017-11-14
### Fixed
- JavaScript issue with buttons.
- Problem with Playground interviews not being decrypted.

## [0.1.96] - 2017-11-12
### Fixed
- JSON conversion problem when using `/interviews?json=1`.

## [0.1.95] - 2017-11-12
### Fixed
- Bug in 0.1.94 regarding detection of variable names.

## [0.1.94] - 2017-11-12
### Fixed
- Improved detection of variable names in code.

## [0.1.93] - 2017-11-10
### Changed
- The `Individual` class no longer initializes the `child`, `income`,
  `asset`, and `expense` attributes, but there are `objects` blocks in
  basic-questions.yml that will initialize these attributes.
- The `Organization` class no longer initializes the `office`
  attribute, unless `offices` is provided as a keyword parameter
  during object construction.
### Added
- Interview tags system and the `session_tags()` function.

## [0.1.92] - 2017-11-09
### Added
- The `checkbox export value` option when using `pdf template file`.
### Changed
- The Markdown to HTML converter now uses the Attribute Lists extension.
- The `server_capabilities()` function now has a `google_maps` item.
- When the server is not in `debug` mode, users must be logged in as
  with administrator or developer privileges to run interviews in
  `docassemble.base` and `docassemble.demo`.  In the SMS interface,
  interviews in these packages are always inoperable unless the server
  is in `debug` mode.
### Fixed
- The `server_capabilities()` was not recognizing the `enable`
  settings.

## [0.1.91] - 2017-11-07
### Changed
- Exceptions triggered during code block execution will now show the
  line, not just indicate the line number.
- The `server_capabilities()` function is now imported by default and
  it reports additional features.
- The `interview_list()` function now returns interview metadata.
### Added
- Dynamically-generated `fields` items.
- The `cross site domain` configuration directive and
  `CROSSSITEDOMAIN` environment variable, for enabling APIs to be
  used.
### Fixed
- Azure blob storage fixes.

## [0.1.90] - 2017-11-05
### Changed
- New features in the `Address.geolocate()` method.
### Added
- The `Address.normalize()` method.
- The `session list interview` and `dispatch interview` configuration
  directives.

## [0.1.89] - 2017-11-04
### Added
- Ability to use `json=1` with `/user/sign-in`, `/list`, and
  `/interviews` pages.
- `interview_list()` and `interview_menu()` functions.
- Twitter login.
### Fixed
- Thread unsafe language setting.

## [0.1.88] - 2017-11-02
### Fixed
- `object_name()` raised an exception.
- Including MP4 videos did not work when OGG not provided.

## [0.1.87] - 2017-11-02
### Fixed
- `docx template file` combined with `code` resulted in error
  due to recent change that attempted to provide better error
  messages.

## [0.1.86] - 2017-11-01
### Added
- `decoration size`, `decoration units`, `button icon size`,
  `button icon units`, and `button size` configuration options.
- `encode_name()` and `decode_name()`.
### Changed
- Clicking the back button when looking at question help will return
  the user to the question.
### Fixed
- Width of images in .docx files.

## [0.1.85] - 2017-10-29
### Added
- Option for `google maps api key` in the `google` section of the
  configuration.
### Changed
- A Google API key is now required for using `map_of()`.

## [0.1.84] - 2017-10-29
### Fixed
- UI issues when switching between help and questions tabs.
- Added `pop()` method to `DAList`.
- Machine learning errors when entries are blank.

## [0.1.83] - 2017-10-26
### Added
- The `log()` function.
- The `fields` option for `background_response()`.
### Changed
- Responses from `check in` events can use the `javascript` option of
  `background_response()` to communicate results to the browser.

## [0.1.82] - 2017-10-26
### Added
- The `pdf_concatenate()` function converts word processing files.
- The `flash()` JavaScript function.
### Changed
- When using `complete_attribute`, list gathering will not
  first seek a textual representation of the object.
### Fixed
- Inclusion of images in RTF when a width not specified.
- `value()`, `defined()`, and `undefine()` no longer raise exceptions
  when passed constants or internal Python names.
- Errors in list gathering.

## [0.1.81] - 2017-10-25
### Changed
- Google Drive synchronization is now handled as a background task so
  that it will not be interrupted by a web browser timeout.
### Fixed
- Uploads embedded in docx template files.

## [0.1.80] - 2017-10-23
### Added
- The `set_title()` function.
### Changed
- Interview title functionality in the `metadata` initial block.
### Fixed
- Image URLs to PDF page images with S3/Azure Blob Storage.

## [0.1.79] - 2017-10-23
### Fixed
- PDF page retrieval index error.
- File permissions issue in S3 that prevents server restart.  S3 users
  must upgrade the Docker image.
- Incorrect timestamps when downloading from persistent cloud storage.

## [0.1.78] - 2017-10-22
### Changed
- When using S3 or Azure Blob Storage, the files will now be cached
  on the server file system and updated when they change.
- When using the Playground and S3 or Azure Blob Storage is in use,
  and there are more than ten decorations, no preview images will be
  shown in "Variables, etc."
- The values of `SavedFile` objects will be cached in memory for the
  duration of a web request, so that when you create a new
  `SavedFile`, attributes will be set from memory.
- The first argument to a `MachineLearner` object will no longer be
  used as a literal `group_id`.  Rather, an argument `'fruit'` it will
  be converted into a group_id of the form
  `docassemble.packagename:data/sources/ml-interviewname.json:fruit`.
  You can still set a literal `group_id` using the keyword parameter
  `group_id`.
- When an `initial_file` is given to a `MachineLearner` object, two
  different formats can be used: an array, or a dictionary of arrays.
  If a dictionary of arrays, the keys will be checked and if the key
  matches the `group_id` (with the part before the final
  colon, if any, removed), the array corresponding to that key will be
  used.
### Fixed
- Playground wizard not including pdf and docx template files in package.
- Playground wizard not including static files in package.
- Playground wizard pickle error when using S3 or Azure blob storage.
- Bug where key 'sought' not found.

## [0.1.77] - 2017-10-20
### Added
- The `pdf_concatenate()` function.
### Fixed
- Missing dependencies for `RandomForestMachineLearner`.

## [0.1.76] - 2017-10-20
### Added
- `RandomForestMachineLearner` for machine learning with numeric and
  categorical values.
- Context for `SyntaxError`s.
### Fixed
- `code` to specify fields in docx template.
- S3 problems.

## [0.1.75] - 2017-10-18
### Added
- `inline width` field modifier for embedded fields.
- `DAStaticFile` object.
- `set_data()` and `get_data()` methods for `DARedis`.
### Fixed
- `DAFile` initialize function now handles keyword arguments as
  advertised.

## [0.1.74] - 2017-10-15
### Added
- `data` block.
### Changed
- Validation errors for embedded fill-in-the-blanks elements now
  appear under the fields.
- Embedded radio buttons and checkboxes now use standard HTML
  input elements.
- Embedded currency fields use standard text to represent the currency
  symbol.

## [0.1.73] - 2017-10-15
### Changed
- Referring to a non-existent DAList item after the list has been
  gathered will now generate an exception.
### Fixed
- Brought back gradients on buttons, which had been removed in 0.1.72.

## [0.1.72] - 2017-10-14
### Added
- `bootstrap theme` and `inverse navbar` features and configuration
  directives.
### Fixed
- CSS and JavaScript files imported through features without a
  specified package now use the package of the features block.
- Logout now deletes cookies.

## [0.1.71] - 2017-10-11
### Changed
- `currency()` now returns `''` on non-numeric input.
### Fixed
- AWS secret access codes with slashes.
- Recognition of iterators with constant integers.

## [0.1.70] - 2017-10-10
### Added
- Method `item()` for `DAList` and `DADict`.
- Lettuce tests in directory `tests`.
### Changed
- Playground variable detection now shows attributes.
- Playground variable detection now adjusts for temporary Mako variables.
- The `split()` function now splits on newlines.
- Playground no longer loads each example interview into memory.
### Fixed
- Template file Google Drive deletion.
- Problem with pickling result of `.using()`.
- Scanning for variable names involving patterns like `[i][j]`.

## [0.1.69] - 2017-10-05
### Added
- Class method `.using()` for adding parameters to object definitions.
### Changed
- Backups only kept now for 14 days.  Container upgrade necessary.
### Fixed
- Use of iterators and generic objects in `if` modifiers.
- Azure cron backup.  Container upgrade necessary.

## [0.1.68] - 2017-10-05
### Added
- `if` modifier.
### Changed
- Interview cache invalidation now handled through thread local
  variables and a redis counter, rather than by modification times on
  YAML files.  This may avoid potential problems with Google Drive
  sync.
- Google Drive sync now has a page that tells the user not to stop the
  web browser.
### Fixed
- Error on URL redirection.
- Playground package page asking for GitHub sign-in after expiration
  of credentials.
- History on error page restored.

## [0.1.67] - 2017-10-02
### Added
- Warnings in the Playground when use of a particular file name would
  overwrite an existing file.
- Functions `yesno`, `split`, `showif`, `showifdef`, and `phone_number_part`.
### Changed
- Fields in a PDF fill-in form can be specified as a list of dictionaries.
### Fixed
- When `maximum image size` in effect, files that got converted to PNG
  by the browser still had original file extensions.
- Typo introduced in 0.1.65 affecting the processing of lists of
  choices in multiple-choice questions.

## [0.1.66] - 2017-10-01
### Fixed
- Problem with empty upload fields.

## [0.1.65] - 2017-09-30
### Changed
- More consistent behavior in multiple choice listings.
- When a multiple choice question's choices are determined by code,
  the image can be an uploaded file.
### Added
- The `if` modifier.
- The `scan for variables` modifier.
- The `dispatch` function.
- The `has_been_gathered()` method on groups.
- More expansive error messages in debug mode.
### Fixed
- Errors if variable names in `question` blocks are invalid.
- Error in `date_difference()`.
- Layout problem when sections and progress meter both turned on.

## [0.1.64] - 2017-09-26
### Fixed
- Gathering of Asset items.

## [0.1.63] - 2017-09-26
### Added
- Example of editing a list after it has been gathered.
### Fixed
- Embedded fields where the variable names contain iterators.
- Lists instanceNames adjusting after removal of a list element.

## [0.1.62] - 2017-09-24
### Changed
- Fields can now be embedded in `note` text.
### Added
- Multiple choice type `combobox` and `datatype: combobox` for
  `fields`.
### Fixed
- Mandatory multiple-choices questions with embedded code blocks.
- `DAList` and `DADict` objects in choices lists.

## [0.1.61] - 2017-09-23
### Changed
- After back button is pressed, defaults will be populated on fields
  that accept defaults.
### Added
- Methods on `DAFileCollection` so that it can be used like a
  `DAFile`.
- `run_python_module()` function.
### Fixed
- Checkbox defaults specified as `DADict` objects not recognized.

## [0.1.60] - 2017-09-21
### Changed
- Added a new type of infinite loop detection.

## [0.1.59] - 2017-09-21
### Changed
- Added a different type of infinite loop detection.

## [0.1.58] - 2017-09-19
### Added
- Multiple choice type `dropdown`.
- Code example for `fields` dropdown.
### Fixed
- YouTube video widths not responsive.
- Javascript and CSS files in features not loading without full
  package/file references.

## [0.1.57] - 2017-09-19
### Fixed
- Bug that affected some file-related operations.
- Detection of infinite loops.

## [0.1.56] - 2017-09-17
### Changed
- The way that the `objects` block gets executed has changed.  It no
  longer executes as a mandatory block unless it is marked as
  mandatory.
- In addition, the way that questions are asked has changed
  accordingly.  If any fields that would be set by the question have
  attributes, **docassemble** will try to ensure that the underlying
  variable is already defined, which may trigger a process of defining
  the variable.  This will ensure that objects mentioned in object
  blocks will be created before they are necessary.
- These new changes enable the use of iterator variables like `i` in
 `objects` blocks.
### Fixed
- Problem with deletion of keys on S3.
- Problem with response() on second and subsequent screens.

## [0.1.55] - 2017-09-16
### Added
- The `id` and `precedence` modifiers and the `order` initial block.
- The JSON interface.

## [0.1.54] - 2017-09-16
### Fixed
- Upgraded from boto to boto3.
- Fixed issues with documents and cloud storage.

## [0.1.53] - 2017-09-15
### Fixed
- Problem with docassemble.base as a dependency in extension packages.

## [0.1.52] - 2017-09-15
### Fixed
- Problem with assembled documents on cloud storage.

## [0.1.51] - 2017-09-14
### Added
- JSON version of information on each screen.
### Fixed
- Problem with signatures in pdf fill documents.

## [0.1.50] - 2017-09-10
### Added
- Options for `maximum image size` to reduce size of uploaded images
  in the browser before uploading.
- Interview feature `cache documents` for disabling document caching.
### Fixed
- E-mailing of assembled documents.

## [0.1.49] - 2017-09-07
### Added
- Additional document caching feature.
### Fixed
- Problem with caching of certain document types.

## [0.1.48] - 2017-09-06
### Added
- Option for `go full screen` that limits behavior to mobile only.
- Caching of assembled documents.  Clicking on assembled documents
  will now open them in a new browser tab rather than offering them
  as attachment downloads.
### Changed
- In Google Drive synchronization, .tmp and .gdoc files are now
  ignored.
### Fixed
- Spinner did not appear on signature pages.
- Date validation forcing input even when date not required.
- Images included in terms not appearing unless fully qualified.

## [0.1.47] - 2017-09-04
### Added
- Function `referring_url()` for accessing the original "referer" URL.
- Feature `go full screen` for breaking out of iframes.
- Support in Docker for MySQL connections.
### Fixed
- Error accessing machine learning training area.
- Undefined mimetype error with e-mail receiving feature.
- "Next will be" message in SMS interface skipped `note` and `html`.

## [0.1.46] - 2017-09-02
### Added
- Methods `.true_values()` and `.false_values()` for `DADict`.
### Fixed
- Multiple choice questions where list of selections is empty.
- SMS interface for multiple choice questions where list of
  selections is empty.

## [0.1.45] - 2017-08-31
### Added
- Configuration directive `password login`, which will hide the
  username and password fields on the login screen.
### Fixed
- Better error messages when packages fail to install.
- Better error messages in `worker.log` when background processes
  do not complete.

## [0.1.44] - 2017-08-30
### Changed
- Datatype `object_checkboxes` will now create the variable if it does not
  exist.
### Fixed
- Control mode submitting clicks twice in some circumstances.
- Voice call forwarding.
- Duplicate checkbox validation error message.
- `send_email()` did not e-mail .docx files when given
  DAFileCollection objects.
- Inconsistency in handling of nested questions.

## [0.1.43] - 2017-08-27
### Fixed
- Extraneous call to checkin for chat log.
- Clicking elements in control mode in live chat.
- Problems with db table prefixes.
- Adjusted to changes in flask-user.
- Downgraded to Debian jessie because there was a problem with corrupt
  HTTP responses.

## [0.1.42] - 2017-08-24
### Added
- set_attributes() method for `DAFile` and `DAFileList` in order to
  allow uploaded files to be used across interview sessions and not be
  deleted when the session in which the file was uploaded is deleted.
- url_for() method for `DAFileList`.
### Changed
- Hyperlinks to actions (e.g., created through `url_action()` or
`action_menu_item()`) are now carried out through Ajax.
### Fixed
- Compatibility of UI elements with 'control' live help feature.
- Extraneous "Menu" entry in mobile menu when custom menu used.

## [0.1.41] - 2017-08-23
### Added
- Configuration directive `require referer` that allows users who use
  referer blockers to use **docassemble**.
- `.show()` method for `DATemplate` objects, for interchangability
  with images in `DAFile` objects.
### Fixed
- Error when `valid types` was set to `pdf` when `docx template file`
  was in use.
- Typo in HTML of monitor page.
- Auto-updating of version numbers in package listing.
- Updating of package table so that core packages are retrieved from
  pip, not GitHub.

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
  always edit `install_requires` in the setup.py file.
### Fixed
- Bug fixes to SMS interface.

## [0.1.34] - 2017-08-10
### Fixed
- Checkboxes became `DADict`s a few weeks ago but the auto-gathering
  system on them was not turned off; it is turned off now.

## [0.1.33] - 2017-08-09
### Fixed
- Backwards compatibility for interviews started before `nav` added as
  a variable in the user dictionary.
- Extension packages now depend on `docassemble.webapp` so that when a
  package is updated, all of docassemble is updated, not just
  `docassemble.base`.

## [0.1.32] - 2017-08-08
### Changed
- `force_ask()` can ask a series of questions.
### Added
- Configuration directives for customization of global Javascript and
  CSS.
- Configuration directives for customization of start page and
  interview list.

## [0.1.31] - 2017-08-07
### Changed
- Review page buttons now Ajax.
- Screen reverts to review page after field edit.
### Fixed
- Problem with PDF/A due to old version of pdfx.

## [0.1.30] - 2017-08-07
### Added
- PDF/A support.
- Navigation bar option.
### Fixed
- Problem with files when user logged in.

## [0.1.29] - 2017-08-03
### Added
- Input validation with Python code.
- Input validation for dates, in addition to the limited Javascript validation.

## [0.1.28] - 2017-08-01
### Fixed
- DADict object now defines ask_object_type by default
- Bug with `using` combined with `ml`.

## [0.1.27] - 2017-07-31
### Added
- `ml` and `mlarea` data types and training system.
### Fixed
- Better error message in Playground when interview has a syntax error.
- Problem with temporary files introduced in 0.1.23 that was causing
  PDF fill-in to fail.

## [0.1.26] - 2017-07-25
### Fixed
- Minor git issue again.

## [0.1.25] - 2017-07-24
### Changed
- Back button style.
### Fixed
- labelauty issue.

## [0.1.24] - 2017-07-24
### Fixed
- Minor git issue.

## [0.1.23] - 2017-07-23
### Changed
- Additional deletion of temporary files through cron job.
### Fixed
- Improved performance by optimizing markdown and regex.
- Newer version of labelauty, with modifications to include benefits
  of older version, for compatibility with IE/Edge.

## [0.1.22] - 2017-07-22
### Added
- `read_qr()` function.
- `new_object_type` option for groups.
### Changed
- The default for the `debug` configuration directive is now `True`.
### Fixed
- The `disable others` field modifier can now be used on a field with
  the same variable name as that of another field on the same page.
- Term definition Markdown is now converted to HTML.
- Fixed bug with code blocks using iterators.
- Fixed problem with document attachments affecting data storage and
  multiple application servers.
- Playground run now resets page counter.

## [0.1.21] - 2017-07-14
### Changed
- Checkboxes now create `DADict` objects rather than `dict` objects.
### Added
- `all_true()` and `all_false()` methods for DADict.
### Fixed
- Fixed bug when user invitation e-mail fails to send.
- Error message when code and question blocks are combined.

## [0.1.20] - 2017-07-10
### Fixed
- Fixed another bug in edit user profile page.

## [0.1.19] - 2017-07-10
### Fixed
- Fixed bug in edit user profile page.

## [0.1.18] - 2017-06-28
### Added
- Pull package into Playground with PyPI.
### Changed
- `initial` directive now accepts code, just like `mandatory`.
- Error page now returns 404 instead of 501 when user tries to access
  an interview file that does not exist.
### Fixed
- Added MANIFEST.in so that README.md is included when packages are
  bundled using setup.py.
- Uploading files to Playground now checks to make sure the file is
  YAML and is readable.

## [0.1.17] - 2017-06-24
### Changed
- Updated the required system version to 0.1.17.
### Fixed
- If you updated the Python packages to 0.1.15 or 1.1.16 without
  updating the system, you may have experienced an error.  Now, if
  changes to the Python packages alter the necessary PostgreSQL
  columns or tables, those columns and tables will be changed upon
  reboot after the updating of the Python packages, and will not have
  to wait until an upgrade of the system.
- Fixed reference in Dockerfile to non-existent file.

## [0.1.16] - 2017-06-24
### Added
- GitHub integration.
- `dow_of()` function.
### Changed
- Changed PyPI username and passwords from a configuration setting to
  a user setting.
### Fixed
- More stable transition when transitioning server from non-cloud data
  storate to cloud data storage
- `month_of()` now uses defined language/locale rather than system
  locale when `word_of` is `True`.
- Executables that run as root no longer writable by www-data.
- Turned off auto-start on sync supervisor process.

## [0.1.15] - 2017-06-18
### Added
- SMS option for two-factor authentication.
- Option for requiring confirmation of user e-mail addresses.
### Fixed
- Problem with apt-get update at start of Dockerfile.

## [0.1.14] - 2017-06-17
### Changed
- Renamed configuration directives from "second factor" to "two factor."

## [0.1.13] - 2017-06-17
### Added
- Two-factor authentication.
- Phone login.

## [0.1.12] - 2017-06-06
### Changed
- To facilitate GitHub workflow, attempted to preserve timestamps on
  filenames in Zip files.

## [0.1.11] - 2017-06-04
### Changed
- Increased font size for better mobile experience.

## [0.1.10] - 2017-06-03
### Changed
- Look and feel of signature pages now match regular interface on
  larger screens,

## [0.1.9] - 2017-06-02
### Fixed
- Various bugs from previous version.

## [0.1.8] - 2017-06-01
### Fixed
- Bug with Google Drive integration.

## [0.1.7] - 2017-06-01
### Fixed
- Bug with server-side encryption.

## [0.1.6] - 2017-05-30
### Added
- Google Drive integration.

## [0.1.5] - 2017-05-28
### Fixed
- Bug with logins in the middle of interviews.

## [0.1.4] - 2017-05-27
### Changed
- New algorithm for generic variables and index variables.
### Added
- Additional examples.

## [Unreleased] - 2017-05-26
### Changed
- PDF fill-in files now editable.
- Started using bumpversion.
- Started a changelog.
