## <a name="current_info"></a>current_info

`current_info` is a [Python dictionary] that is defined by
**docassemble** every time a screen loads.  It allows interviews to
access certain information from **docassemble**, such as the identity
of the person logged in and other information.

`current_info` contains the following keys:

* `default_role` - the default role for the interview, as defined by
  the [`default role` initial block];
* `session` - the session key, which is a secret identifier that
  unlocks access to the variable store of the user's interview.  If
  passed as the `session` parameter of a URL, the interview will load
  using the variable store for that session key.
* `url` - the base URL of the docassemble application (e.g.,
  `http://demo.docassemble.org`).
* `user` - a [Python dictionary] containing the following keys:
  * `is_authenticated` - whether the user is logged in (True or False)
  * `is_anonymous` - whether the user is not logged in (True or False)
  * `email` - the user's e-mail address
  * `theid` - the unique ID of the user
  * `roles` - a [Python list] containing the user's roles, as defined
    by a site administrator.  (Administrators can change user roles on
    the [User List] page.)
  * `firstname` - the user's first name.  This and the following can
    all be set by the user on the [Profile] page.
  * `lastname` - the user's last name.
  * `country` - the user's country.
  * `subdivisionfirst` - in the U.S., the state.
  * `subdivisionsecond` - in the U.S., the county.
  * `subdivisionthird` - in the U.S., the municipality.
  * `organization` - the user's organization.
  * `location` - if [`track_location`] (see below) is set to true, and
    the user's location is successfully obtained, this entry will
    contain a dictionary with the keys `latitude` and `longitude`,
    indicating the user's location.
* `yaml_filename` - the filename of the current interview, in the
  package:path form (e.g., `docassemble.demo:data/questions/questions.yml`)
