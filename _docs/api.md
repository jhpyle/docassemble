---
layout: docs
title: API
short_title: API
---

Many features in **docassemble** can be controlled through an
HTTP-based [Application Program Interface] (API).  All requests must
be authenticated using an [API key](#manage_api).

# <a name="manage_api"></a>Obtaining an API key

In order to call the **docassemble** API, you need an API key.  A user
can obtain an API key by clicking "API keys" on the user profile page.
Whether a user can obtain an API key depends on the [`api privileges`]
setting in the [Configuration].  By default, only users with
privileges of `admin` or `developer` can obtain API keys.

For security, API keys can be restricted to particular IP addresses or
particular HTTP referrers.  A user can create more than one API key.

An API key is tied to the user; when the API call authenticates, the
user effectively logs in.  If the API call uses one of the "session"
functions, the user in the interview will be the owner of the API key.
As discussed [below](#secret), the owner of an API key can access the
encrypted interview answers of any user, if that user's username and
password are known, but the identity of the user in the interview will
always be that of the owner of the API key.

# <a name="calling"></a>How to call the API

The API functions can be called by any method capable of sending HTTP
requests.

Here is an example of calling the [list](#list) API using [cURL].

{% highlight bash %}
curl http://localhost/api/list?key=H3PLMKJKIVATLDPWHJH3AGWEJPFU5GRT
{% endhighlight %}

The output returned is in [JSON] format:

{% highlight json %}
[
  {
    "filename": "docassemble.base:data/questions/examples/combobox.yml", 
    "link": "http://localhost/interview?i=docassemble.base%3Adata%2Fquestions%2Fexamples%2Fcombobox.yml", 
    "package": "docassemble.base", 
    "status_class": null, 
    "subtitle": null, 
    "subtitle_class": null, 
    "tags": [], 
    "title": "Combobox"
  }, 
  {
    "filename": "docassemble.demo:data/questions/questions.yml", 
    "link": "http://localhost/interview?i=docassemble.demo%3Adata%2Fquestions%2Fquestions.yml", 
    "package": "docassemble.demo", 
    "status_class": null, 
    "subtitle": null, 
    "subtitle_class": null, 
    "tags": [
      "demo", 
      "legal"
    ], 
    "title": "Demonstration interview"
  }
]
{% endhighlight %}

Here is an example of calling the same function using the [`requests`]
module in [Python].

{% highlight python %}
import requests
import json
api_key = 'H3PLMKJKIVATLDPWHJH3AGWEJPFU5GRT'
r = requests.get("http://localhost/api/list", params={'key': api_key})
if r.status_code != 200:
    raise Exception("Unable to get list of available interviews")
interviews = json.loads(r.text)
{% endhighlight %}

To make a [POST] request using [cURL], use standard form data to send the API key and other parameters:

{% highlight bash %}
curl -d key=H3PLMKJKIVATLDPWHJH3AGWEJPFU5GRT -d first_name=John -d last_name=Smith http://localhost/api/user
{% endhighlight %}

{% highlight python %}
import requests
api_key = 'H3PLMKJKIVATLDPWHJH3AGWEJPFU5GRT'
r = requests.get("http://localhost/api/user", data={'key': api_key, 'first_name': 'John', 'last_name': 'Smith'})
if r.status_code != 204:
    raise Exception("Unable to set user information")
{% endhighlight %}

You can also make [POST] requests where the body is a [JSON] object
and the content type of the request is `application/json`.  In this
case, when a [POST] parameter expects a [JSON] array or [JSON] object,
you can simply provide an array or an object as part of [JSON] data
structure that you are sending.  The exception to this is if you are
making a [POST] request that includes file uploads.  In this
situation, the format of the [POST] body cannot be [JSON], but must be
traditional 'multipart/form-data' format in which text parameters are
provided along with file contents, with boundary separators.

Instead of passing the API key in the URL parameter or the POST body,
you can pass it in a cookie called `X-API-Key`:

{% highlight bash %}
curl --cookie "X-API-Key=H3PLMKJKIVATLDPWHJH3AGWEJPFU5GRT" http://localhost/api/list
{% endhighlight %}

You can also send the API key in an HTTP header called `X-API-Key`:

{% highlight bash %}
curl -H "X-API-Key: H3PLMKJKIVATLDPWHJH3AGWEJPFU5GRT" http://localhost/api/list
{% endhighlight %}

By default, all API endpoints return headers to facilitate [Cross-Origin Resource
Sharing] ([CORS]), such as:

{% highlight text %}
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, HEAD
Access-Control-Max-Age: 21600
Access-Control-Allow-Headers: Content-Type, origin
{% endhighlight %}

However, if you configure [`cross site domains`] in your
[Configuration], the headers indicated by the configuration setting
will be sent instead.

Note that the library you use for calling the API may impose [CORS]
limitations on you, which you may need to override, if they can be
overridden at all.  If you want to send an API key as a cookie, you
may need to set [`cross site domains`] to a specific domain, because
otherwise the library may not allow you to send a cookie.  Typically,
server-side libraries do not impose these restrictions, but you will
encounter them if you try to use them from a web browser.

If you do call the API from a web browser, note that the API key will
be visible to the user.  Make sure that the owner of any API key you
share in a web browser does not have any special privileges.
Possessing the API key of a basic user does not give someone greater
privileges than they would have if they used the standard web
interface.

# <a name="functions"></a>Available API functions

## <a name="user_new"></a>Create a new user

Description: Creates a user with a given e-mail address and password.

Path: `/api/user/new`

Method: [POST]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `username`: the user's e-mail address.
 - `password` (optional): the user's password.  If a password is not
   supplied, a random password will be generated.
 - `privileges` (optional): a [JSON] array of user privileges (e.g.,
   `['developer', 'trainer']`), or a string containing a single
   privilege (e.g., `'advocate'`).  If not specified, the new user
   will have a single privilege, `user`.  (If your request has the
   `application/json` content type, you do not need to convert the
   array to [JSON].)
 - `first_name` (optional): the user's first name.
 - `last_name` (optional): the user's last name.
 - `country` (optional): the user's country code (e.g., `US`).
 - `subdivisionfirst` (optional): the user's state.
 - `subdivisionsecond` (optional): the user's county.
 - `subdivisionthird` (optional): the user's municipality.
 - `organization` (optional): the user's organization 
 - `timezone` (optional): the user's time zone (e.g. `'America/New_York'`).
 - `language` (optional): the user's language code (e.g., `en`).

Required privileges: `admin`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate, or if
   the owner of the API key lacks `admin` privileges.
 - [400] "An e-mail address must be supplied." if the `username`
   parameter is missing.
 - [400] "A password must be supplied." if the `password` parameter is
   missing.
 - [400] "List of privileges must be a string or a list." if the list
   of privileges could not be parsed.
 - [400] "Invalid privilege name." if a privilege did not exist in the
   system.
 - [400] "That e-mail address is already being used." if another user
   is already using the given `username`.
 - [400] "Password too short or too long" if the password has fewer than
   four or more than 254 characters.
 
Response on success: [200]

Body of response: a [JSON] object with the following keys:

 - `user_id`: the user ID of the new user.
 - `password`: the password of the new user.

## <a name="user_list"></a>List of users

Description: Provides a list of registered users on the system.

Path: `/api/user_list`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `include_inactive` (optional): set to `1` if inactive users should
   be included in the list.

Required privileges:
 - `admin` or
 - `advocate`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate or the
   required privileges are not present.

Response on success: [200]

Body of response: a [JSON] list of objects with the following keys:

 - `active`: whether the user is active.  This is only included if the
   `include_inactive` parameter is set.
 - `country`: user's country code.
 - `email`: user's e-mail address.
 - `first_name`: user's first name.
 - `id`: the integer ID of the user. 
 - `language`: user's language code.
 - `last_name`: user's last name.
 - `organization`: user's organization.
 - `privileges`: list of the user's privileges (e.g., `'admin'`, `'developer'`).
 - `subdivisionfirst`: user's state.
 - `subdivisionsecond`: user's county.
 - `subdivisionthird`: user's municipality.
 - `timezone`: user's time zone (e.g. `'America/New_York'`).

## <a name="user_retrieve"></a>Retrieve user information by username

Path: `/api/user_info`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `username`: the e-mail address of the user.

Required privileges:
 - `admin` or
 - `advocate`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate or the
   required privileges are not present.
 - [400] "An e-mail address must be supplied." if the `username`
   parameter was missing
 - [400] "Error obtaining user information" if there was a problem
   getting user information.
 - [404] "User not found" if the user ID did not exist.

Response on success: [200]

Body of response: a [JSON] object with the following keys:

 - `active`: whether the user is active.
 - `country`: user's country code.
 - `email`: user's e-mail address.
 - `first_name`: user's first name.
 - `id`: the integer ID of the user. 
 - `language`: user's language code.
 - `last_name`: user's last name.
 - `organization`: user's organization.
 - `privileges`: list of the user's privileges (e.g., `'admin'`, `'developer'`).
 - `subdivisionfirst`: user's state.
 - `subdivisionsecond`: user's county.
 - `subdivisionthird`: user's municipality.
 - `timezone`: user's time zone (e.g. `'America/New_York'`).

## <a name="user"></a>Retrieve information about the user

Description: Provides information about the user who is the owner of
the API key.

Path: `/api/user`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).

Required privileges: none.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 
Response on success: [200]

Body of response: a [JSON] object with the following keys describing
the API owner:
 - `country`: user's country code.
 - `email`: user's e-mail address.
 - `first_name`: user's first name.
 - `id`: the integer ID of the user. 
 - `language`: user's language code.
 - `last_name`: user's last name.
 - `organization`: user's organization 
 - `privileges`: list of the user's privileges (e.g., `'admin'`, `'developer'`).
 - `subdivisionfirst`: user's state.
 - `subdivisionsecond`: user's county.
 - `subdivisionthird`: user's municipality.
 - `timezone`: user's time zone (e.g. `'America/New_York'`).

## <a name="user_post"></a>Set information about the user

Description: Sets information the user who is the owner of
the API key.

Path: `/api/user`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `first_name` (optional): the user's first name.
 - `last_name` (optional): the user's last name.
 - `country` (optional): the user's country code (e.g., `US`).
 - `subdivisionfirst` (optional): the user's state.
 - `subdivisionsecond` (optional): the user's county.
 - `subdivisionthird` (optional): the user's municipality.
 - `organization` (optional): the user's organization 
 - `timezone` (optional): the user's time zone (e.g. `'America/New_York'`).
 - `language` (optional): the user's language code (e.g., `en`).
 - `password` (optional): the user's password.

Required privileges: None, except that only users with `admin`
privileges can use the API to change a password.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [403] "You must have admin privileges to change a password." if the
   `password` parameter is included but the owner of the API lacks
   administrator privileges.

Response on success: [204]

Body of response: empty.

This method can be used to edit the profile of the user who owns the
API key.

## <a name="user_user_id"></a>Information about a given user

Description: Provides information about the user with the given user ID.

Path: `/api/user/<user_id>`

Example: `/api/user/22`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).

Required privileges: `admin` or `advocate`, or the API owner's user ID is the
same as `user_id`.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "User ID must be an integer" if the user_id parameter cannot be
   interpreted as an integer.
 - [400] "Error obtaining user information" if there was a problem
   getting user information.
 - [404] "User not found" if the user ID did not exist.

Response on success: [200]

Body of response: a [JSON] object with the following keys describing
the user with a user ID equal to the `user_id`:
 - `country`: user's country code (e.g., `US`).
 - `email`: user's e-mail address.
 - `first_name`: user's first name.
 - `id`: the integer ID of the user. 
 - `language`: user's language code (e.g., `en`).
 - `last_name`: user's last name.
 - `organization`: user's organization 
 - `privileges`: list of the user's privileges (e.g., `'admin'`, `'developer'`).
 - `subdivisionfirst`: user's state.
 - `subdivisionsecond`: user's county.
 - `subdivisionthird`: user's municipality.
 - `timezone`: user's time zone (e.g. `'America/New_York'`).

## <a name="user_user_id_delete"></a>Make a user inactive

Description: Makes a user account inactive, so that the user can no
longer log in.

Path: `/api/user/<user_id>`

Example: `/api/user/22`

Method: [DELETE]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).

Required privileges: `admin`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "User ID must be an integer" if the user_id parameter cannot be
   interpreted as an integer.
 - [404] "User not found" if the user ID did not exist.

Response on success: [204]

Body of response: empty.

## <a name="user_user_id_post"></a>Set information about a user

Description: Sets information about a user.

Path: `/api/user/<user_id>`

Example: `/api/user/22`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `country` (optional): user's country code (e.g., `US`).
 - `first_name` (optional): user's first name.
 - `language` (optional): user's language code (e.g., `en`).
 - `last_name` (optional): user's last name.
 - `organization` (optional): user's organization 
 - `subdivisionfirst` (optional): user's state.
 - `subdivisionsecond` (optional): user's county.
 - `subdivisionthird` (optional): user's municipality.
 - `timezone` (optional): user's time zone
   (e.g. `'America/New_York'`).
 - `password` (optional): the user's password.

Required privileges: `admin`, or `user_id` is the same as the user ID
of the API owner.  Only users with `admin` privileges can use the API
to change a password.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [403] "You must have admin privileges to change a password." if the
   `password` parameter is included but the owner of the API lacks
   administrator privileges.
 - [400] "User ID must be an integer" if the user_id parameter cannot be
   interpreted as an integer.
 - [400] "Error obtaining user information" if there was a problem
   retrieving information about the user.
 - [404] "User not found" if the user ID did not exist.
 - [400] "You cannot call set_user_info() unless you are an
   administrator" if the API is called by a user without `admin` privileges.

Response on success: [204]

Body of response: empty.

## <a name="privileges"></a>List available privileges

Description: Returns a list of names of privileges that exist in the
system.

Path: `/api/privileges`

Method: [GET]

Parameters:
- `key`: the API key (optional if the API key is passed in an
  `X-API-Key` cookie or header).

Required privileges:
- `admin` or
- `developer`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.

Response on success: [200]

Body of response: a [JSON] list of role names.

## <a name="privileges_post"></a>Add a role to the list of available privileges

Description: Given a role name, adds the name to the list of available privileges.

Path: `/api/privileges`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `privilege`: the name of the privilege to be added to the list.

Required privileges: `admin`.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "A privilege name must be provided" if the `privilege` data value
   is missing.
 - [400] "The given privilege already exists" if a privilege with the
   same name as that provided in the `privilege` data value already.

Response on success: [204]

Body of response: empty.

## <a name="user_privilege_add"></a>Give a user a privilege

Description: Give a user a privilege that the user with the given
`user_id` does not already have.

Path: `/api/user/<user_id>/privileges`

Example: `/api/user/22/privileges`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `privilege`: the name of the privilege to be given to the user.

Required privileges: `admin`.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "A privilege name must be provided" if the `privilege` data value
   is missing.
 - [404] "User not found" if the user ID did not exist.
 - [400] "The specified privilege does not exist" if the privilege was
   not on the list of existing privileges.
 - [400] "The user already had that privilege" if the user already had
   the given privilege.

Response on success: [204]

Body of response: empty.

## <a name="user_privilege_remove"></a>Take a privilege away from a user

Description: Take away a privilege that the user with the given
`user_id` has.

Path: `/api/user/<user_id>/privileges`

Example: `/api/user/22/privileges`

Method: [DELETE]

Form data:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `privilege`: the name of the privilege to be taken away from the user.

Required privileges: `admin`.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "A privilege name must be provided" if the `privilege` data value
   is missing.
 - [404] "User not found" if the user ID did not exist.
 - [400] "The specified privilege does not exist" if the privilege was
   not on the list of existing privileges.
 - [400] "The user did not already have that privilege" if the user
   did not already have the given privilege.

Response on success: [204]

Body of response: empty.

## <a name="interviews"></a>List interview sessions on the system

Description: Provides a filterable list of interview sessions that are
stored on the system.

Path: `/api/interviews`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `secret` (optional): set to the user's [secret](#secret) if you
   want to be able to access information about interview sessions that
   may be encrypted.
 - `tag` (optional): set to a tag if you want to select only those
   interview sessions with the given tag.
 - `i` (optional): set to an interview filename if you want to select
   only those interview sessions with the given interview filename.
 - `session` (optional): set to a session ID if you want to select
   only the interview session with the given session ID.
 - `include_dictionary` (optional): set to `1` if you want a [JSON]
   version of the interview dictionary to be returned.

Required privileges:
- `admin` or
- `advocate`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Error reading interview list." if there was a problem
   obtaining the list of interviews.

Response on success: [200]

Body of response: a [JSON] list of objects representing interview
sessions, where each object has the following keys:

- `email`: The e-mail address of the user.
- `filename`: The filename of the interview.
- `metadata`: An object representing the metadata of the interview.
- `modtime`: The last time the interview dictionary was modified,
  expressed as a local time.
- `session`: The session ID of the session.
- `starttime`: The time the interview was started, expressed as a
  local time.
- `subtitle`: The subtitle of the interview, or `null`.
- `tags`: An array of tags.
- `temp_user_id`: The user ID of the temporary user, if the user was
  not logged in, or `null` if the user was logged in.
- `title`: The title of the interview.
- `user_id`: The user ID of the user, or `null` if the user was not
  logged in.
- `utc_modtime`: The last time the interview dictionary was modified,
  in UTC format.
- `utc_starttime`: The time the interview was started, in UTC format.
- `valid`: Whether all of the information about the interview could be
  read.  This will be `false` if the interview is encrypted and the
  `secret` is missing or does not match the encryption key used by the
  interview.

## <a name="interviews_delete"></a>Delete interview sessions on the system

Description: Deletes interview sessions on the server.

Path: `/api/interviews`

Method: [DELETE]

Required privileges: `admin`

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `tag` (optional): set to a tag if you want to delete only those
   interview sessions with the given tag.
 - `i` (optional): set to an interview filename if you want to delete
   only those interview sessions with the given interview filename.
 - `session` (optional): set to a session ID if you want to delete
   only the interview session with the given session ID.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Error reading interview list." if there was a problem
   obtaining the list of interviews to delete.

Response on success: [204]

Body of response: empty.

This API, which is available only to administrators, allows you to
delete interview sessions from the system, even all of them.  The filters
`tag`, `i`, and `session` are cumulatively applied (as if connected
with "and").  If you include no filters, all of the interview
sessions, regardless of user, are deleted.

See also the [`/api/user/interviews`](#user_interview_delete) method
and the [`/api/user/<user_id>/interviews`](#user_user_id_interviews_delete) method.

## <a name="user_interviews"></a>List interviews of the user

Description: Provides a filterable list of interview sessions stored
on the system where the owner of the API is associated with the session.

Path: `/api/user/interviews`

Method: [GET]

Required privileges: none.

This works just like the [`/api/interviews`], except it only returns
interviews belonging to the owner of the API.

## <a name="user_interviews_delete"></a>Delete interview sessions of the user

Description: Deletes interview sessions stored on the system that were
started by the owner of the API key.

Path: `/api/user/interviews`

Method: [DELETE]

Required privileges: none.

This works just like the [DELETE] method of [`/api/interviews`],
except it only deletes interview sessions associated with the owner of
the API.

Note that if an interview associated with the owner of the API is also
associated with another user, the actual underlying interview will not
be removed from the system.  It will only disappear from the system if
there is only one user associated with the interview.

## <a name="user_user_id_interviews"></a>List interview sessions of another user

Description: Provides a filterable list of interview sessions stored
on the system where the user with the given user ID started the interview.

Path: `/api/user/<user_id>/interviews`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `i` (optional): set to a filename of an interview, e.g.,
   `docassemble.demo:data/questions/questions.yml`, if you want to
   retrieve only those sessions for a given interview file.
 - `tag` (optional): set to a tag if you want to retrieve only those
   interview sessions with the given tag.

Required privileges: `admin` or `advocate`, or `user_id` is the same
as the user ID of the API owner.

This works just like the [`/api/interviews`], except it only returns
interviews belonging to the user with user ID `user_id`.

## <a name="user_user_id_interviews_delete"></a>Delete interview sessions of another user

Description: Deletes interview sessions belonging to a particular user.

Path: `/api/user/<user_id>/interviews`

Method: [DELETE]

Required privileges: `admin` or `advocate`, or `user_id` is the same
as the user ID of the API owner.

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `i` (optional): set to a filename of an interview, e.g.,
   `docassemble.demo:data/questions/questions.yml`, if you want to
   delete only those sessions for a given interview file.
 - `tag` (optional): set to a tag if you want to delete only those
   interview sessions with the given tag.

This works just like the [`/api/interviews`], except it only deletes
interviews belonging to the user with user ID `user_id`.

## <a name="list"></a>Get a list of advertised interviews

Description: Provides a list of interviews advertised by the system
through the [`dispatch`] configuration directive.

Path: `/api/list`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `tag` (optional): if set to `estates`, then the list of interviews
   is limited to those that have `estates` as one of the [`tags`] in
   the [interview `metadata`].
 - `absolute_urls` (optional): if `0`, the `link` URL returned will be
   relative (i.e., will not include the hostname).  By default, the
   `link` URLs are absolute.

Required privileges: none.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.

Response on success: [200]

Body of response: a [JSON] list of objects representing interviews,
where each object has the following keys:

- `filename`: the filename of the interview.  E.g., `docassemble.demo:data/questions/questions.yml`.
- `link`: a URL path that can be used to start the interview.
- `package`: the package in which the interview resides.  E.g., `docassemble.demo`.
- `status_class`: usually `null`, but will be set to
  `dainterviewhaserror` if the interview cannot be loaded.
- `subtitle`: the subtitle of the interview, from the [interview `metadata`].
- `subtitle_class`: usually `null`, but will be set to `invisible` if
  the interview cannot be loaded.
- `tags`: an array of tags, from the [interview `metadata`].
- `title`: the title of the interview, from the [interview `metadata`].

## <a name="secret"></a>Obtain a decryption key for a user

Description: Given a username and password, provides a key that can be
used for decrypting the user's stored interview answers.

Path: `/api/secret`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `username`: the user name of the user whose secret you wish to retrieve.
 - `password`: the password of the user whose secret you wish to retrieve.

Required privileges: none.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "A username and password must be supplied" if the username
   and/or password is not provided.
 - [403] "Username not known" if the user did not exist on the system.
 - [403] "Secret will not be supplied because two factor authentication
   is enabled"
 - [403] "Password not set" if the password could not be obtained.
 - [403] "Incorrect password" if the password did not match the password
   on the server.

Response on success: [200]

Body of response: a [JSON] string containing the decryption key.

## <a name="login_url"></a>Obtain a temporary URL for logging a user in

Description: Returns a temporary URL, to which a user can be
redirected, which will log the user in without the user needing to
enter a username or password.

Path: `/api/login_url`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `username`: the user name of the user.
 - `password`: the password of the user.
 - `i` (optional): the filename of an interview to which the user will
   be redirected after they log in.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `url_args` (optional): a [JSON] object containing additional URL
   arguments that should be included in the URL to which the user is
   directed after they log in.  (If your request has the
   `application/json` content type, you do not need to convert the
   object to [JSON].)
 - `next` (optional): if the user should be directed after login to a
   page that is not an interview, you can omit `i` and instead set
   this parameter to a value like `playground` (for the [Playground])
   or `config` (for the [Configuration] page).  For a list of all
   possible values, see the documentation for [`url_of()`].  If
   `url_args` are supplied, these will be included in the resulting
   URL.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "A username and password must be supplied" if the username
   and/or password is not provided.
 - [403] "Username not known" if the user did not exist on the system.
 - [403] "Secret will not be supplied because two factor authentication
   is enabled"
 - [403] "Password not set" if the password could not be obtained.
 - [403] "Incorrect password" if the password did not match the password
   on the server.
 - [400] "Malformed URL arguments" if `url_args` are supplied and are
   not a [JSON] object.
 - [400] "Unknown path for next" if the path provided to `next` could
   not be recognized.

Response on success: [200]

Body of response: a [JSON]-formatted URL.  It will be in a format like
`https://docassemble.example.com/user/autologin?key=EaypzffGGDbmiBpjqkASSLCtFWPpbiCFqMNlEbti`.
The code will expire in 15 seconds, so it is only useful if you
immediately redirect a user to the URL after you obtain the URL.

## <a name="session_new"></a>Start an interview

Description: Starts a new session for a given interview and returns
the ID of the session.

Path: `/api/session/new`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `secret` (optional): the encryption key to use with the interview,
   if the interview uses server-side encryption.

Required privileges: none.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameter i is required" if the `i` parameter is not included.

Response on success: [200]

Body of response: a [JSON] object with the following keys:

- `i`: the filename of the interview (same as what was passed in the
  `i` parameter).
- `session`: the session ID for the new interview session.
- `encrypted`: `true` or `false` indicating whether the interview is
  using server-side encryption
- `secret` (sometimes): if no `secret` was provided as a parameter,
  and the interview uses server-side encryption, a `secret` will be
  provided.  This will be the decryption key that must be passed in
  all other API calls related to the session, in order for the
  interview answers to be decrypted.

If you know that the interview immediately sets [`multi_user`] to
`True`, you do not need to provide a `secret` parameter.

If the interview does not immediately set [`multi_user`] to `True`,
then server-side encryption will be used.  If the interview uses
encryption, typically you would first call [`/api/secret`] to obtain
your encryption key, and then pass the encryption key to
[`/api/session/new`] as the `secret` parameter.  If no `secret` is
provided, but the interview uses server-side encryption, a random
encryption key will be generated for use with the interview, and will
be returned in the response.  An interview session with a random
encryption key is fully usable through the API, but you will not be
able to log in using your web browser and resume the interview.

If you pass any parameters to [`/api/session/new`] other than those
listed above, the values will be added to the [`url_args`] variable.

## <a name="session_get"></a>Get variables in an interview

Description: Provides a [JSON] representation of the current interview
dictionary.

Path: `/api/session`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session`: the session ID of the interview.
 - `secret` (optional): the encryption key to use with the interview,
   if the interview uses server-side encryption.

Required privileges: none.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameters i and session are required" if the `i` parameter
   and `session` parameters are not included.
 - [400] "Unable to obtain interview dictionary" if there was a
   problem locating the interview dictionary.  The `i` and/or
   `session` might be incorrect, or the interview session for the
   given `i` and `session` might have been deleted.
 - [400] "Unable to decrypt interview dictionary" if there was a problem
   obtaining and decrypting the interview dictionary.

Response on success: [200]

Body of response: a [JSON] object representing the interview
dictionary.  Note that the interview dictionary is a [Python dict]
containing [Python objects], so it cannot be converted to [JSON]
without some information being lost in translation.  However, the data
structure will be useful for many applications.  For more information
about how the conversion is done, see the documentation for the
[`all_variables()`] functions.

## <a name="session_post"></a>Set variables in an interview

Description: Sets variables in the interview dictionary and returns a
[JSON] representation of the current question in the interview.

Path: `/api/session`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session`: the session ID of the interview.
 - `secret` (optional): the encryption key to use with the interview,
   if the interview uses server-side encryption.
 - `variables` (optional): a [JSON] object where the keys are variable
   names and the values are the values those variables should have.
   (If your request has the `application/json` content type, you do
   not need to convert the object to [JSON].)
 - `raw` (optional): if set to `0`, then no attempt will be made to
   identify and convert dates that appear in the `variables` (see note
   below).
 - `question_name` (optional): if set to the name of a question (which
   you can obtain from the `questionName` attribute of a question), it
   will mark the question as having been answered.  This is necessary
   only if you are setting variables in response to a [`mandatory`]
   question (which you can determine from the `mandatory` attribute of
   a question).
 - `question` (optional): if set to `0`, then the interview is not
   evaluated after the variables are set and the current question in
   the interview is not returned in response to the request.  You may
   wish to set `question` to `0` if you want to change the interview
   dictionary, but you do not want to trigger any side effects by
   causing the interview to be evaluated.
 - `delete_variables` (optional): a [JSON] array in which the items
   are names of variables to be deleted with [`del`].  The deletion of
   these variables happens after the `variables` are assigned.  (If
   your request has the `application/json` content type, you do not
   need to convert the array to [JSON].)
 - `file_variables` (optional): if you are uploading one or more
   files, and the name of the `DAFileList` variable cannot be passed
   as the name of the file upload, you can set `file_variables` to a
   [JSON] representation of an object with key/value pairs that
   associate the names of file uploads with the variable name you want
   to use.  For example, if `file_variables` is `{"my_file":
   "user.relative['aunt']"}`, then when you upload a file using the
   input name `my_file`, this will have the effect of setting the
   [Python] variable `user.relative['aunt']` equal to a [`DAFileList`]
   containing the file.
 - `event_list` (optional): a [JSON] array of variable names that
   triggered the question to which you are responding.  This is
   necessary in cases where there is a diversion from the normal
   interview logic.  The value of `event_list` can be obtained from
   [`/api/session/question`].  (If your request has the
   `application/json` content type, you do not need to convert the
   array to [JSON].)

File uploads: you can include file uploads in the POST request.  Note
that if you include a file upload, you cannot use the
`application/json` content type, and any arrays or objects you send as
parameters will need to be individually converted to [JSON].

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameters i and session are required" if the `i` parameter
   and `session` parameters are not included.
 - [400] "Unable to obtain interview dictionary" if there was a problem
   locating the interview dictionary.
 - [400] "Unable to decrypt interview dictionary" if there was a problem
   obtaining and decrypting the interview dictionary.
 - [400] "Variables data is not a dict" if `variables` is not a [JSON]
   object.
 - [400] "File variables data is not a dict" if `file_variables` is
   not a [JSON] object.
 - [400] "Delete variables data is not a list" if `delete_variables`
   is not a [JSON] array.
 - [400] "Event list data is not a list" if `event_list` is not a
   [JSON] array.
 - [400] "Malformed variables" if `variables` is not valid [JSON].
 - [400] "Malformed list of file variables" if `file_variables` is not
   valid [JSON].
 - [400] "Malformed file variable" if a file variable is invalid.
 - [400] "Malformed list of delete variables" if `delete_variables` is
   not valid [JSON].
 - [400] "Malformed event list" if `event_list` is not valid [JSON].
 - [400] "Problem setting variables" if there was an error while
   setting variables in the dictionary.
 - [400] "Failure to assemble interview" if the interview generates an
   error.

Response on success: [200], but if `question` is set to `0`, then [204].

Body of response: a [JSON] representation of the current question.
This response is the same as that of [`/api/session/question`].
However, if the `question` data value is set to `0`, then the response
is empty.

When this API is called, the `variables` object is converted from
[JSON] to a [Python dict].  For each key/value pair in the [Python
dict], an assignment statement is executed inside the interview
dictionary.  The key is used as the left side of the assignment
operator and the value is used as the right side.

For example, if `variables` is this [JSON] string:

{% highlight json %}
{"defense['latches']": false, "client.phone_number": "202-555-3434"}
{% endhighlight %}

Then the following statements will be executed in the interview
dictionary:

{% highlight python %}
defense['latches'] = False
client.phone_number = '202-555-3434'
{% endhighlight %}

If a variable value in the [JSON] is in [ISO 8601] format (e.g.,
`2019-06-13T21:40:32.000Z`), then the variable will be converted from
text into a [`DADateTime`] object.  If you do not want dates to be
converted, set the `raw` parameter to `1`.

You can also upload files along with a [POST] request to this API.  In
HTTP, a [POST] request can contain one or more file uploads.  Each
file upload is associated with a name, just as a data element is
associated with a name.  Your [POST] request can contain zero or more
of these names, and each name can be associated with one or more
files.

When a [POST] request includes one or more names associated with file
uploads, **docassemble** creates a [`DAFileList`] object for each
name.  This object can contain one or more files.

After all the variables from the `variables` data have been set, the
interview is evaluated and a [JSON] representation of the current
question is returned.  However, if the `question` data value is set to
`0`, this step is skipped and an empty response is returned.

## <a name="session_question"></a>Get information about the current question

Description: Provides a [JSON] representation of the current question
in the interview.

Path: `/api/session/question`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session`: the session ID of the interview.
 - `secret` (optional): the encryption key to use with the interview,
   if the interview uses server-side encryption.
   
Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameters i and session are required" if the `i` parameter
   and `session` parameters are not included.
 - [400] "Unable to obtain interview dictionary" if there was a problem
   locating the interview dictionary.
 - [400] "Unable to decrypt interview dictionary" if there was a problem
   obtaining and decrypting the interview dictionary.
 - [400] "Failure to assemble interview" if the interview generates an
   error.

Response on success: [200]

Body of response: a [JSON] representation of the current question.
The structure of the object varies by question type and is largely
self-explanatory.

The `message_log` is a list of messages generated by the [`log()`]
function if the priority of the message was something other than
`'log'`.  For example, if the interview ran `log("Hello, world!",
priority="info")`, then the `message_log` would look like the
following:

{% highlight json %}
{
  "message_log": [
    {
      "message": "Hello, world!", 
      "priority": "info"
    }
  ],
  "etc.": "etc."
}
{% endhighlight %}

The `event_list` is a list of variables that mark the "event" that led
to the question being asked.  When you send POST request to
[`/api/session`] in response to a question, you should pass the
`event_list` back.  This is necessary in some circumstances to
indicate to **docassemble** that you wish to get past a diversion in
the interview logic.

Some of the information in the response may only be relevant to you
if you are trying to create a front end similar to **docassemble**'s
web application.

## <a name="session_action"></a>Run an action in an interview

Description: Runs an action in an interview.

Path: `/api/session/action`

Method: [POST]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session`: the session ID of the interview.
 - `secret` (optional): the encryption key to use with the interview,
   if the interview uses server-side encryption.
 - `action`: the name of the action you want to run.
 - `arguments` (optional): a [JSON] object in which the keys are
   argument names and the values are argument values.  (If your
   request has the `application/json` content type, you do not need to
   convert the object to [JSON].)

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameters i, session, and action are required" if the
   required parameters are not provided.
 - [400] "Malformed arguments" if the arguments are not in [JSON] format.
 - [400] "Arguments data is not a dict" if the arguments are not a
   [Python dict] after being converted from [JSON].
 - [400] "Unable to obtain interview dictionary" if there was a problem
   locating the interview dictionary.
 - [400] "Unable to decrypt interview dictionary" if there was a problem
   obtaining and decrypting the interview dictionary.
 - [400] "Failure to assemble interview" if the interview generates an
   error.
 - [400] "Could not send file" if there was a problem with a file
   [`response()`].

Responses on success: 
 - [200] if content is included
 - [204] if no content is included

Body of response: empty, unless the action ends with a call to
[`response()`], in which case the contents of the response are
returned.

For more information about how actions run in **docassemble**
interviews, see [actions].

## <a name="session_back"></a>Go back one step in an interview session

Description: Goes back one step in the interview session and returns a
[JSON] representation of the current question in the interview.

Path: `/api/session/back`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session`: the session ID of the interview.
 - `secret` (optional): the encryption key to use with the interview,
   if the interview uses server-side encryption.
 - `question` (optional): if set to `0`, then the interview is not
   evaluated and the current question in the interview is not returned
   in response to the request.  You may wish to set `question` to `0`
   if you want to go back a step, but you do not want to trigger any
   side effects by causing the interview to be evaluated.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Cannot go back" if the interview is just beginning and
   cannot go back.
 - [400] "Parameters i and session are required" if the `i` parameter
   and `session` parameters are not included.
 - [400] "Unable to obtain interview dictionary" if there was a problem
   locating the interview dictionary.
 - [400] "Unable to decrypt interview dictionary" if there was a problem
   obtaining and decrypting the interview dictionary.
 - [400] "Failure to assemble interview" if the interview generates an
   error.

Response on success: [200], but if `question` is set to `0`, then [204].

Body of response: a [JSON] representation of the current question.
This response is the same as that of [`/api/session/question`].
However, if the `question` data value is set to `0`, then the response
is empty.

After the last step in the interview is undone, the interview is
evaluated and a [JSON] representation of the current question is
returned.  However, if the `question` data value is set to `0`, this
step is skipped and an empty response is returned.

## <a name="session_delete"></a>Delete an interview session

Description: Deletes a single interview session.

Path: `/api/session`

Method: [DELETE]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session`: the session ID of the interview.

Required privileges: none.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameters i and session are required" if the `i` parameter
   and `session` parameters are not included.

Response on success: [204]

Body of response: empty.

## <a name="session_retrieve"></a>Retrieve a stored file

Description: Retrieves a stored file

Path: `/api/file/<file_number>`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of the interview.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session`: the session ID of the interview.
 - `extension` (optional): a specific file extension to return for the
   given file.
 - `filename` (optional): a specific filename to return from the given
   file's directory.

Required privileges: none.

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameters i and session are required" if the `i` parameter
   and `session` parameters are not included.
 - [404] "File not found" if the given file could not be located.

Response on success: [200]

Body of response: the contents of the file

## <a name="playground_get"></a>List files in Playground

Description: Returns a list of files in a folder of the [Playground].

Path: `/api/playground`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `user_id` (optional): the user ID of the user whose [Playground]
   should be read.  Only users with `admin` privileges can read from a
   different user's [Playground].  The default is the user ID of the
   owner of the API key.
 - `folder` (optional): the folder in the [Playground] from which to
   obtain the list of files.  Must be one of `questions`, `sources`,
   `static`, `templates`, or `modules`.

Required privileges: `admin` or `developer`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Invalid user_id" if the user does not have administrative
   privileges and the `user_id` is different from the current user's
   user ID.
 - [400] "Invalid folder" if the value of `folder` is unknown.

Response on success: [200]

Body of response: a [JSON] array of file names

## <a name="playground_delete"></a>Delete a file in the Playground

Description: Deletes a file in a folder of the [Playground].

Path: `/api/playground`

Method: [DELETE]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `user_id` (optional): the user ID of the user whose [Playground]
   should be read.  Only users with `admin` privileges can read from a
   different user's [Playground].  The default is the user ID of the
   owner of the API key.
 - `folder` (optional): the folder in the [Playground] from which to
   obtain the list of files.  Must be one of `questions`, `sources`,
   `static`, `templates`, or `modules`.  The default is `static`.
 - `filename`: the name of the file to be deleted.  If the filename
   does not exist, a success code is still returned.

Required privileges: `admin` or `developer`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Invalid user_id" if the user does not have administrative
   privileges and the `user_id` is different from the current user's
   user ID.
 - [400] "Invalid folder" if the value of `folder` is unknown.
 - [400] "Missing filename." if a `filename` is not provided.

Response on success: [204]

Body of response: empty.

## <a name="playground_upload"></a>Upload files to the Playground

Description: Saves one or more uploaded files to a folder in the [Playground].

Path: `/api/playground`

Method: [POST]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `user_id` (optional): the user ID of the user whose [Playground]
   should be written to.  Only users with `admin` privileges can write
   to a different user's [Playground].  The default is the user ID of the
   owner of the API key.
 - `folder` (optional): the folder in the [Playground] to which the
   uploaded file(s) should be written.  Must be one of `questions`,
   `sources`, `static`, `templates`, or `modules`.
 - `file` or `files[]`: the files to upload.

Required privileges: `admin` or `developer`

Responses on failure: 
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Invalid user_id" if the user does not have administrative
   privileges and the `user_id` is different from the current user's
   user ID.
 - [400] "Invalid folder" if the value of `folder` is unknown.
 - [400] "Error saving file(s)" if an error occurred during the
   process of saving files.
 - [400] "No file found." if no uploaded files were provided.

Response on success: [204]

Body of response: empty.

# <a name="questionless"></a>Example of usage: questionless interview

One way to use the API is to use **docassemble** as nothing more than
a logic engine, ignoring **docassemble**'s system for asking
questions.

The following interview, which is in the [`docassemble.demo`] package,
contains no [`question`] blocks, but it is still usable through an API.

{% highlight yaml %}
mandatory: True
code: |
  json_response({'final': True, 'inhabitants': inhabitant_count})
---
code: |
  if favorite_number == 42 and user_agrees_to_waive_penalties:
    inhabitant_count = 2
  else:
    inhabitant_count = 2000 + favorite_number * 45
{% endhighlight %}

Its sole purpose is to return a [`json_response()`] to the user,
letting the user know the number of "inhabitants."

Here is how you would use it:

First, do a [GET] request to [`/api/session/new`] with
`i=docassemble.demo:data/questions/examples/questionless.yml` and
obtain a session ID and encryption key for a new interview.

{% highlight json %}
{
  "encrypted": true, 
  "i": "docassemble.base:data/questions/examples/questionless.yml", 
  "secret": "aZLbSszVzfVpnOfK", 
  "session": "YOwLSycrtezLXEWhIUheRSpLNLEfRMxP"
}
{% endhighlight %}
   
Next, do a [GET] request to `/api/session/question`, passing the
`i`, `session`, and `secret` values as parameters.  You will get back:

{% highlight json %}
{
  "message_log": [], 
  "questionType": "undefined_variable", 
  "variable": "favorite_number"
}
{% endhighlight %}

This indicates that the interview was unable to reach achieve its end
goal because the variable `favorite_number` was undefined, and there
was no [`question`] that could be asked to define the variable.  In
the web interface, this situation would result in a [501] error, but
in an interview designed for use with the API, this situation results
in [JSON] like the above, telling you that you need to do something to
define the variable `favorite_number`.

To define this variable, you would next send a [POST] request to
[`/api/session`], including as data values the `i`, `session`, and
`secret` values, as well as a data value `variables`, which needs to
be an object where the keys are variable names and the values are the
values you want those variables to have.

For example if you set `variables` to `{"favorite_number": 42}`, then
the [Python] variable `favorite_number` will be set to the integer
`42`.

The interview will then be evaluated and the current state of the
interview will be returned:

{% highlight json %}
{
  "message_log": [], 
  "questionType": "undefined_variable", 
  "variable": "user_agrees_to_waive_penalties"
}
{% endhighlight %}

You would then send another [POST] request to [`/api/session`] in
order to provide a definition for `user_agrees_to_waive_penalties`.
Setting `variables` equal to `{"user_agrees_to_waive_penalties":
false}` yields the following response:

{% highlight json %}
{
  "final": true, 
  "inhabitants": 3890
}
{% endhighlight %}

Note that this [JSON] originates directly from the [`json_response()`]
function.

[`json_response()`]: {{ site.baseurl }}/docs/functions.html#json_response
[GET]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET
[POST]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST
[DELETE]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/DELETE
[Configuration]: {{ site.baseurl }}/docs/config.html
[`api privileges`]: {{ site.baseurl }}/docs/config.html#api privileges
[Application Program Interface]: https://en.wikipedia.org/wiki/Application_programming_interface
[cURL]: https://en.wikipedia.org/wiki/CURL
[JSON]: https://en.wikipedia.org/wiki/JSON
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`requests`]: https://pypi.python.org/pypi/requests
[`dispatch`]: {{ site.baseurl }}/docs/config.html#dispatch
[`cross site domains`]: {{ site.baseurl }}/docs/config.html#cross site domains
[interview `metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[`tags`]: {{ site.baseurl }}/docs/initial.html#tags
[`/api/interviews`]: #interviews
[`/api/secret`]: #secret
[`/api/session`]: #session_post
[`/api/session/new`]: #session_new
[`/api/session/question`]: #session_question
[Python dict]: https://docs.python.org/2.7/tutorial/datastructures.html#dictionaries
[Python objects]: https://docs.python.org/2.7/tutorial/classes.html
[`all_variables()`]: {{ site.baseurl }}/docs/functions.html#all_variables
[`url_args`]: {{ site.baseurl }}/docs/special.html#url_args
[`multi_user`]: {{ site.baseurl }}/docs/special.html#multi_user
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[`response()`]: {{ site.baseurl }}/docs/functions.html#response
[200]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/200
[204]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/204
[400]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/400
[403]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/403
[404]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
[501]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/404
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`docassemble.demo`]: https://github.com/jhpyle/docassemble/tree/master/docassemble_demo/docassemble/demo
[`log()`]: {{ site.baseurl }}/docs/functions.html#log
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`del`]: https://docs.python.org/2.0/ref/del.html
[Playground]: {{ site.baseurl }}/docs/playground.html
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`url_of()`]: {{ site.baseurl }}/docs/functions.html#url_of
[Redis]: http://redis.io/
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[CORS]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`DADateTime`]: {{ site.baseurl }}/docs/objects.html#DADateTime
[ISO 8601]: https://en.wikipedia.org/wiki/ISO_8601
