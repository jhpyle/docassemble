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
    "metadata": {
      "title": "Combobox"
    },
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
    "metadata": {
      "title": "Demonstration interview"
    },
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

Form data:

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

Required privileges: `admin`.

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
 - `advocate`.

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
 - `advocate`.

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

Required privileges: None.

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
longer log in, or deletes the account entirely.

Path: `/api/user/<user_id>`

Example: `/api/user/22`

Method: [DELETE]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `remove` (optional): set this to `'account'` if you want to remove
   the user's account entirely.  This will irrevocably remove the
   user's data and prevent them from logging in.  The only things that
   will be retained are [`multi_user`] interview sessions that were
   joined by another user.  If you set `remove` to
   `'account_and_shared'`, then these shared interview sessions will
   also be removed.  If you leave `account` unset, the user's account
   will simply be made inactive, which will prevent the user from
   logging in, but will not delete their account or their data.

Required privileges: `admin`.

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

## <a name="fields"></a>Extract fields from a template file

Description: Returns information about the field names used in a PDF,
DOCX, or Markdown file.

Path: `/api/fields`

Method: [POST]

Form data:
 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `format` (optional): the desired output format.  The default is
   `json`, where the response to the request is a [JSON] data
   structure with information about the fields.  The other option is
   `yaml`, in which case the response to the request is plain text
   containing a draft [`question`] in [YAML] format, which can be used
   as the starting point for how you might use the template in an interview.

File data:
 - `template`: a template file in PDF or DOCX format.

Required privileges:
- `admin` or
- `developer`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Invalid output format" if the `format` is not `json` or
   `yaml`.
 - [400] "File not included." if a file is not uploaded with the
   request.
 - [400] "Invalid input format." if the file that is uploaded does not
   have the extension `.pdf` or `.docx`.
 - [400] "No fields could be found." if the `format` is `yaml` and no
   fields could be detected in the file.

Response on success: [200]

Body of response: a [JSON] list of field information, or a [YAML]
draft [`question`], depending on the requested `format`.

The [JSON] output for the file [sample-form.pdf] looks like this:

{% highlight javascript %}
{
  "default_values": {
    "Apple Checkbox": "No",
    "Orange Checkbox": "No",
    "Pear Checkbox": "No",
    "Toast Checkbox": "No",
    "Your Name": "",
    "Your Organization": ""
  },
  "fields": [
    "Your Name",
    "Your Organization",
    "Apple Checkbox",
    "Orange Checkbox",
    "Pear Checkbox",
    "Toast Checkbox"
  ],
  "locations": {
    "Apple Checkbox": {
      "box": [
        72.1975,
        580.914,
        94.395,
        600.593
      ],
      "page": 1
    },
    "Orange Checkbox": {
      "box": [
        72.1975,
        555.494,
        94.3951,
        575.173
      ],
      "page": 1
    },
    "Pear Checkbox": {
      "box": [
        72.1975,
        529.42,
        94.3951,
        549.099
      ],
      "page": 1
    },
    "Toast Checkbox": {
      "box": [
        72.1975,
        505.025,
        94.3951,
        524.704
      ],
      "page": 1
    },
    "Your Name": {
      "box": [
        127.32,
        652.84,
        288.12,
        677.44
      ],
      "page": 1
    },
    "Your Organization": {
      "box": [
        157.92,
        627.4,
        288.12,
        652.0
      ],
      "page": 1
    }
  },
  "types": {
    "Apple Checkbox": "/Btn",
    "Orange Checkbox": "/Btn",
    "Pear Checkbox": "/Btn",
    "Toast Checkbox": "/Btn",
    "Your Name": "/Tx",
    "Your Organization": "/Tx"
  }
}
{% endhighlight %}

The field "types" come from the PDF specification.  Common values are
`/Btn`, `/Tx`, and `/Sig`.

The "locations" indicate the page number and bounding box of the
fields.  For "box" coordinates a, b, c, and d, the coordinates refer
to:

* a: lower-left corner, horizontal coordinate
* b: lower-left corner, vertical coordinate
* c: upper-right corner, horizontal coordinate
* d: upper-right corner, vertical coordinate

The coordinates are measured in "points" (there are 72 points in an
inch).  The "origin" for this coordinate system is the lower-left corner of the page.

If no fields could be found, the [JSON] response will look like this:

{% highlight javascript %}
{
  "fields": []
}
{% endhighlight %}

If the file format of the template is DOCX, only "fields" will be returned.

If the output `format` is `yaml`, the response will be like that of
the [Get list of fields from PDF/DOCX template] utility.  For example:

{% highlight yaml %}
---
question: Here is your document.
event: some_event
attachment:
  - name: sample-form
    filename: sample-form
    pdf template file: sample-form.pdf
    fields:
      - "Your Name": something
      - "Your Organization": something
      - "Apple Checkbox": No
      - "Orange Checkbox": No
      - "Pear Checkbox": No
      - "Toast Checkbox": No
---
{% endhighlight %}

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
- `developer`.

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
- `advocate`.

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

Required privileges: `admin`.

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

Required privileges: None.

This works just like the [`/api/interviews`], except it only returns
interviews belonging to the owner of the API.

## <a name="user_interviews_delete"></a>Delete interview sessions of the user

Description: Deletes interview sessions stored on the system that were
started by the owner of the API key.

Path: `/api/user/interviews`

Method: [DELETE]

Required privileges: None.

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

Required privileges: None.

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

Required privileges: None.

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
 - `session` (optional): the session ID for the interview session (if
   `i` is also provided).  Providing this here rather than in the
   `url_args` prevents sending the session ID to the user's browser.
 - `expire` (optional): the number of seconds after which the URL will
   expire.  The default is 15 seconds.
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

Required privileges: `admin`.

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
By default, the code will expire in 15 seconds, so it is primarily
useful if you immediately redirect a user to the URL after you obtain
it.

## <a name="resume_url"></a>Obtain a redirect URL for an existing session

Description: Returns a temporary URL, to which a user can be
redirected, which will cause the user to resume an existing interview
session.  The [`multi_user`] variable should be set to `True` in the
interview session unless the user possesses the decryption key for the
interview session.  The advantage of using this method rather than
redirecting the user to an `/interview` URL with a `session` parameter
is that this method does not transmit the session parameter to the
user's browser.

Path: `/api/resume_url`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `i`: the filename of an interview to which the user will
   be redirected after they log in.  E.g.,
   `docassemble.demo:data/questions/questions.yml`.
 - `session` (optional): the session ID of the interview session to
   which the user should be redirected.  If not included, the user is
   redirected to a new interview session.
 - `expire` (optional): the number of seconds after which the URL will
   expire.  The default is 3,600 seconds (one hour).
 - `one_time` (optional): if set to `1`, the URL will expire after
   being used once.  The default is `0`.
 - `url_args` (optional): a [JSON] object containing additional URL
   arguments that should be included in the URL to which the user will
   be directed.  (If your request has the `application/json` content
   type, you do not need to convert the object to [JSON].)

Required privileges: None.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "No filename supplied." if the `i` parameter is not included.
 - [400] "Malformed URL arguments" if `url_args` are supplied and are
   not a [JSON] object.
 - [400] "Invalid number of seconds." if `expire` is not a number
   greater than or equal to 1.

Response on success: [200]

Body of response: a [JSON]-formatted URL.  It will be in a format like
`https://docassemble.example.com/launch?c=VnNNcACOTgOihEUQdeiLTKWzTowmwygn`.

## <a name="temp_url"></a>Obtain a general-purpose redirect URL

Description: Given any URL, returns a URL that will respond with a [302
redirect] to the given URL.  The URL will expire after one hour, or
after another period of time that you specify.  The URL can be
configured so that it can only be used once.

Path: `/api/temp_url`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `url`: the URL to which you want the user to be redirected.
 - `expire` (optional): set this to the number of seconds after which
   the URL should expire.  The default is 3,600 seconds (one hour).
 - `one_time` (optional): if set to `1`, the URL will expire after
   being used once.  The default is `0`.

Required privileges: None.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "No url supplied." if the `url` is not provided.
 - [400] "Invalid number of seconds." if `expire` is not a number
   greater than or equal to 1.

Response on success: [200]

Body of response: a [JSON]-formatted URL.  It will be in a format like
`https://docassemble.example.com/goto?c=AfQqwtZVYedxlYzsOHfvOhxdDejQkkyp`.

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

Required privileges: None.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Parameter i is required" if the `i` parameter is not
   included.
 - [400] "Insufficient permissions to run this interview" if the owner
   of the API does not have the [`required privileges`] to run the
   interview.

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

Required privileges: None.

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
 - `advance_progress_meter` (optional): if set to `1`, then the
   progress meter will be advanced.  The default is not to advance the
   progress meter.  The `advance_progress_meter` parameter is not
   effective if `question` is `0`.
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

If a variable value is a [JSON] object with keys `_class` and
`instanceName`, then the variable will be converted into a [Python]
object of the given class, and keys other than `_class` will be used
to set attributes of the object.  This is the same format by which
[Python] objects are reduced to [JSON] elsewhere in the API.  Thus,
you should be able to take [JSON] representations of objects that you
read from the [GET] action of this endpoint and pass them back to the
[POST] action of this endpoint.  Note that this is not guaranteed to
be a 100% reliable method of [Python] object serialization.  It is not
as robust as [Python]'s [pickle] system, and it may not work for every
class.

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

Form data:

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

Required privileges: None.

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

Required privileges: None.

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
 - `project` (optional): the project in the [Playground] from which to
   obtain the list of files.  The default is `default`, which is the
   "Default Playground" project.

Required privileges:
- `admin` or
- `developer`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Invalid user_id" if the user does not have administrative
   privileges and the `user_id` is different from the current user's
   user ID.
 - [400] "Invalid folder" if the value of `folder` is unknown.
 - [400] "Invalid project" if the project given by `project` does not
   exist.

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
   should be used.  Only users with `admin` privileges can delete from
   a different user's [Playground].  The default is the user ID of the
   owner of the API key.
 - `folder` (optional): the folder in the [Playground] from which to
   delete the file.  Must be one of `questions`, `sources`, `static`,
   `templates`, or `modules`.  The default is `static`.
 - `project` (optional): the project in the [Playground] from which to
   delete the file.  The default is `default`, which is the
   "Default Playground" project.
 - `filename`: the name of the file to be deleted.  If the filename
   does not exist, a success code is still returned.

Required privileges:
- `admin` or
- `developer`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Invalid user_id" if the user does not have administrative
   privileges and the `user_id` is different from the current user's
   user ID.
 - [400] "Invalid folder" if the value of `folder` is unknown.
 - [400] "Invalid project" if the project given by `project` does not
   exist.
 - [400] "Missing filename." if a `filename` is not provided.

Response on success: [204]

Body of response: empty.

## <a name="playground_upload"></a>Upload files to the Playground

Description: Saves one or more uploaded files to a folder in the [Playground].

Path: `/api/playground`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `user_id` (optional): the user ID of the user whose [Playground]
   should be written to.  Only users with `admin` privileges can write
   to a different user's [Playground].  The default is the user ID of the
   owner of the API key.
 - `folder` (optional): the folder in the [Playground] to which the
   uploaded file(s) should be written.  Must be one of `questions`,
   `sources`, `static`, `templates`, or `modules`.
 - `project` (optional): the project in the [Playground] to which the
   uploaded file(s) should be written.  The default is `default`,
   which is the "Default Playground" project.

File data:
 - `file` or `files[]`: the files to upload.

Required privileges:
- `admin` or
- `developer`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Invalid user_id" if the user does not have administrative
   privileges and the `user_id` is different from the current user's
   user ID.
 - [400] "Invalid folder" if the value of `folder` is unknown.
 - [400] "Invalid project" if the project given by `project` does not
   exist.
 - [400] "Error saving file(s)" if an error occurred during the
   process of saving files.
 - [400] "No file found." if no uploaded files were provided.

Response on success: [204]

Body of response: empty.

## <a name="config_read"></a>Get the server configuration

Description: Returns the [Configuration] in [JSON] format.

Path: `/api/config`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).

Required privileges: `admin`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate or the
   required privileges are not present.
 - [400] "Could not parse Configuration." if there is a problem with
   the existing [Configuration].

Response on success: [200]

Body of response: a [JSON] representation of the [Configuration].

## <a name="config_write"></a>Write the server configuration

Description: Writes a new [Configuration] to the server and then
restarts the system.  Note that the system may take significant time
to restart.

Path: `/api/config`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `config`: a [JSON] object representing the new [Configuration].
   (If your request has the `application/json` content type, you do
   not need to convert the object to [JSON].)

Required privileges: `admin`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate or the
   required privileges are not present.
 - [400] "Configuration not supplied." if the `config` parameter is
   missing.
 - [400] "Configuration was not valid JSON." if the `config` parameter
   contained data that could not be parsed as [JSON].

Response on success: [204]

Body of response: empty.

## <a name="package_list"></a>List the packages installed

Description: Provides a list of [Python] packages installed on the system.

Path: `/api/package`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).

Required privileges: `admin`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate or the
   required privileges are not present.

Response on success: [200]

Body of response: a [JSON] list of objects, where each object has the
following keys (when applicable):

- `name`: The name of the package.
- `version`: The installed version of the package.
- `type`: Either `'pip'`, `'zip'`, or `'git'`, if the package was installed
  from [PyPI], a ZIP file, or [GitHub], respectively.
- `can_uninstall`: Whether or not the owner of the API key is allowed
  to uninstall this package.
- `can_update`: Whether or not the owner of the API key is allowed
  to update this package.
- `git_url`: If the `type` is `'git'`, this contains the [GitHub] URL of
  from which the package was installed.
- `branch`: if the `type` is `'git'`, and a particular branch of the
  [GitHub] repository was installed, this is set to the name of the
  branch.
- `zip_file_number`: if the `type` is `'zip'`, this contains the file
  number of the ZIP file from which the package was installed.

## <a name="package_install"></a>Install or update a package

Description: Installs or updates a package and returns a task ID that
can be used to inspect the status of the package update process.

Path: `/api/package`

Method: [POST]

Form data:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `update` (optional): the name of an already-installed [Python]
   package that you want to update.  (This is not useful if the
   package was installed from an uploaded ZIP file.)
 - `github_url` (optional): the URL of a [GitHub] package to install.
 - `branch` (optional): if a `github_url` is provided and you want to
   install from a non-standard branch, set `branch` to the name of the
   branch you want to install.
 - `pip` (optional): the name of [Python] package to install from [PyPI].

File data:
 - `zip`: a file upload of a ZIP file containing a package.

Required privileges:
- `admin` or
- `developer`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "No instructions provided." if no file was uploaded and
   `update`, `github_url`, and `pip` are not provided.
 - [400] "Only one package can be installed or updated at a time." if
   more than one of `update`, `github_url`, `pip`, and `zip` were
   provided.
 - [400] "Package not found." if the package referenced in `update`
   was not already installed.
 - [400] "You are not allowed to update that package." if the package
   referenced in `update` was not one that the owner of the API key is
   allowed to update.
 - [400] "You do not have permission to install that package." if the
   package referenced by `github_url`, `pip`, or `zip` is not one that
   the owner of the API key is allowed to install.
 - [400] "There was an error when installing that package." if there
   was an error while unpacking and reading the uploaded ZIP file.

Response on success: [200]

Body of response: a [JSON] object in which the key `task_id` refers to
a code that can be passed to [`/api/package_update_status`] to check
on the status and result of the package update process.  The `task_id`
expires after one hour.

## <a name="package_uninstall"></a>Uninstall a package

Description: Uninstalls a package and returns a task ID that can be
used to inspect the status of the package uninstallation process.

Path: `/api/package`

Method: [DELETE]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `package`: the name of an already-installed [Python] package that
   you want to uninstall.

Required privileges:
- `admin` or
- `developer`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Missing package name." if the `package` parameter was not
   provided.
 - [400] "Package not found." if the package referenced in `package`
   was not already installed.
 - [400] "You are not allowed to uninstall that package." if the
   package referenced by `package` is not one that the owner of the
   API key is allowed to uninstall.

Response on success: [200]

Body of response: a [JSON] object in which the key `task_id` refers to
a code that can be passed to [`/api/package_update_status`] to check
on the status and result of the package update process.  The `task_id`
expires after one hour.

## <a name="package_update_status"></a>Poll the status of a package process

Description: Obtains information about the status of a package update
process.

Path: `/api/package_update_status`

Method: [GET]

Parameters:

 - `key`: the API key (optional if the API key is passed in an `X-API-Key`
   cookie or header).
 - `task_id`: the task ID that was obtained from a [POST] or
   [DELETE] call to the [`/api/package`] endpoint.

Required privileges:
- `admin` or
- `developer`.

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Missing task_id" if no `task_id` was provided.

Response on success: [200]

Body of response: a [JSON] object describing the status of the
background task.  The keys are:

- `status`: If this is `'working'`, the package update process is still
  proceeding.  If it is `'completed'`, then the package update process
  is done, and other information will be provided.  If it is
  `'unknown'`, then the `task_id` has expired.  The API endpoint will
  return a `'completed'` response only once, and then the `task_id` will
  expire.
- `ok`: This is provided when the `status` is `'completed'`.  It is set
  to `true` or `false` depending on whether [pip] return an error
  code.
- `log`: if `status` is `'completed'` and `ok` is `true`, the `log` will
  contain information from the output of [pip].
- `error_message`: if `status` is `'completed'` and `ok` is `false`,
  the `error_message` will contain a [pip] log or other error message
  that may explain why the package update process did not succeed.

## <a name="api_user_api_get"></a>Get information about the user's API keys

Description: Provides information about the API keys of the user who
is the owner of the API key.

Path: `/api/user/api`

Method: [GET]

Parameters:
 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `api_key` (optional): the API key for which information should be
   retrieved.
 - `name` (optional): the name of an API key for which information should be
   retrieved.

Required privileges: None

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "Error accessing API information" if information about the
   user's API keys could not be retrieved
 - [404] "No such API key could be found." if `api_key` or `name` is
   specified and no API key matching the description could be found.

Response on success: [200]

Body of response: if `api_key` or `name` was provided, the API will
return a [JSON] object with the following keys:

- `name`: the name of the API key.
- `key`: the API key.
- `method`: the method by which the API key controls access.  Can be
  `ip` (accepting only requests from IP addresses specified in the
  `constraints`), `referer` (accepting only requests for which the
  `Referer` header matches one of the `constraints`), or `none` (all
  requests accepted regardless of origin).
- `constraints`: a list of allowed origins (applicable if `method` is
  `ip` or `referer`).

If neither `api_key` or `name` is provided, the API will return a
[JSON] list of objects with the above keys, representing all of the
API keys belonging to the user.

## <a name="api_user_api_delete"></a>Delete an API key belonging to the user

Description: Deletes an API key belonging to the user who is the owner
of the API key used to access the API.

Path: `/api/user/api`

Method: [DELETE]

Parameters:
 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `api_key`: the API key that should be deleted.

Required privileges: None

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "An API key must supplied" if no `api_key` is provided.
 - [400] "Error deleting API key" if there was a problem deleting the
   API key.

Response on success: [204]

Note that the API will return a success code even if the API key did
not exist.

Body of response: empty.

## <a name="api_user_api_post"></a>Add a new API key for the user

Description: Adds a new API key belonging to the user who
is the owner of the API key that is used to access the API.

Path: `/api/user/api`

Method: [POST]

Parameters:
 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `name`: the name of the API key.  It cannot be longer than 255
   characters and it must be unique for the user.
 - `method` (optional): the method used to control access to the API
   with the API key.  Can be `ip` (accepting only requests from IP
   addresses specified in the `allowed`), `referer` (accepting only
   requests for which the `Referer` header matches one of the
   `allowed`), or `none` (all requests accepted).  The default is
   `none`.
 - `allowed` (optional): a [JSON] list of allowed IP addresses (where
   `method` is `ip`) or URLs (if `method` is `referer`).  (If your
   request has the `application/json` content type, you do not need to
   convert the object to [JSON].)  If the `allowed` parameter is not
   provided, it will default to an empty list.  This parameter is not
   applicable if `method` is `none`.

Required privileges: None

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "A name must be supplied" if a `name` was not provided.
 - [400] "The name is invalid" is the `name` is longer than 255 characters.
 - [400] "The given name already exists" if an API with the same name
   as `name` already exists for the user.
 - [400] "Invalid security method" if the `method` was not one of
   `ip`, `referer`, or `none`.
 - [400] "Allowed sites list not a valid list" if the `allowed` list
   could not be parsed.
 - [400] "Error creating API key" if there was an error creating the
   API key.

Response on success: [200]

Body of response: a [JSON] string containing the new API key.

## <a name="api_user_api_patch"></a>Update an API key for the user

Description: Updates information about an API key belonging to the
user who is the owner of the API key that is used to access the API.

Path: `/api/user/api`

Method: [PATCH]

Parameters:
 - `key`: the API key (optional if the API key is passed in an
   `X-API-Key` cookie or header).
 - `api_key` (optional): the name of the API key to modify.  The API
   key must belong to the user who owns the API key that was used to
   access the API.  If `api_key` is not provided, the API key that was
   used to access the API key is used.
 - `name` (optional): the new name of the API key.  It cannot be
   longer than 255 characters and it must be unique for the user.
 - `method` (optional): the new method that should be used to control
   access to the API with the API key.  Can be `ip` (accepting only
   requests from IP addresses specified in the `allowed`), `referer`
   (accepting only requests for which the `Referer` header matches one
   of the `allowed`), or `none` (all requests accepted).
 - `allowed` (optional): a [JSON] list of allowed IP addresses (where
   `method` is `ip`) or URLs (if `method` is `referer`).  This will
   replace the existing list.
 - `add_to_allowed` (optional): an item to be added to the list of origins from
   which requests are allowed.  (Applicable if `method` is `ip` or
   `referer`.)  This can also be expressed as a [JSON] list
   of items.
 - `remove_from_allowed` (optional): an item to be removed from the list of
   origins from which requests are allowed.  (Applicable if `method`
   is `ip` or `referer`.)  This can also be expressed as a [JSON] list
   of items.

Required privileges: None

Responses on failure:
 - [403] "Access Denied" if the API key did not authenticate.
 - [400] "No API key given" if the `api_key` parameter is missing.
 - [400] "The given API key cannot be modified" if the API key given
   by `api_key` does not exist, or does not belong to the user.
 - [400] "The name is invalid" is the `name` is longer than 255 characters.
 - [400] "Invalid security method" if the `method` was not one of
   `ip`, `referer`, or `none`.
 - [400] "add_to_allowed is not a valid list" if the `add_to_allowed`
   parameter appeared to be a [JSON] list but could not be parsed as
   one.
 - [400] "remove_from_allowed is not a valid list" if the
   `remove_from_allowed` parameter appeared to be a [JSON] list but
   could not be parsed as one.
 - [400] "Allowed sites list not a valid list" if the `allowed` list
   could not be parsed.
 - [400] "Error updating API key" if there was an error updating the
   API key.

Response on success: [204]

Body of response: empty.

## <a name="api_user_user_id_api_get"></a>Get information about a given user's API keys

Description: Provides information about the API keys of a particular user.

Path: `/api/user/<user_id>/api`

Method: [GET]

This behaves just like the [GET method of `/api/user/api`](#api_user_api_get),
except it retrieves the API keys (or a single API key) of the user
given by `user_id`.

Required privileges: `admin`, or the API owner's user ID is the same
as `user_id`.

## <a name="api_user_user_id_api_delete"></a>Delete an API key belonging to a given user

Description: Deletes an API key belonging to the user with the given
user ID.

Path: `/api/user/<user_id>/api`

Method: [DELETE]

This behaves just like the [DELETE method of `/api/user/api`](#api_user_api_delete),
except it deletes an API key of the user given by `user_id`.

Required privileges: `admin`, or the API owner's user ID is the same
as `user_id`.

## <a name="api_user_user_id_api_post"></a>Add a new API key for a given user

Description: Adds a new API key belonging to a given user.

Path: `/api/user/<user_id>/api`

Method: [POST]

This behaves just like the [POST method of `/api/user/api`](#api_user_api_post),
except it adds an API key belonging to the user given by `user_id`.

Required privileges: `admin`, or the API owner's user ID is the same
as `user_id`.

## <a name="api_user_user_id_api_patch"></a>Update an API key for a given user

Description: Updates information about an API key belonging to the
user with the given user ID.

Path: `/api/user/<user_id>/api`

Method: [PATCH]

This behaves just like the [PATCH method of `/api/user/api`](#api_user_api_patch),
except it modifies an API key belonging to the user given by
`user_id`.  Another difference is that the `api_key` parameter is
required rather than optional.

Required privileges: `admin`, or the API owner's user ID is the same
as `user_id`.

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
[PATCH]: https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/PATCH
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
[Python dict]: https://docs.python.org/3.6/tutorial/datastructures.html#dictionaries
[Python objects]: https://docs.python.org/3.6/tutorial/classes.html
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
[`del`]: https://docs.python.org/3/tutorial/datastructures.html#the-del-statement
[Playground]: {{ site.baseurl }}/docs/playground.html
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`url_of()`]: {{ site.baseurl }}/docs/functions.html#url_of
[Redis]: http://redis.io/
[Cross-Origin Resource Sharing]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[CORS]: https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS
[`DADateTime`]: {{ site.baseurl }}/docs/objects.html#DADateTime
[ISO 8601]: https://en.wikipedia.org/wiki/ISO_8601
[PyPI]: https://pypi.python.org/pypi
[GitHub]: https://github.com/
[`/api/package_update_status`]: #package_update_status
[`/api/package`]: #package_install
[pip]: https://en.wikipedia.org/wiki/Pip_%28package_manager%29
[302 redirect]: https://en.wikipedia.org/wiki/HTTP_302
[pickle]: https://docs.python.org/3.6/library/pickle.html
[`required privileges`]: {{ site.baseurl }}/docs/initial.html#required privileges
[YAML]: https://en.wikipedia.org/wiki/YAML
[sample-form.pdf]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/templates/sample-form.pdf
[Get list of fields from PDF/DOCX template]: {{ site.baseurl }}/docs/admin.html#pdf fields
