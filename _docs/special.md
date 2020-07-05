---
layout: docs
title: Special variables
short_title: Special Variables
---

# Variables set by **docassemble**

There are some special variables that **docassemble** sets in every
interview's variable store.

## <a name="_internal"></a>_internal

`_internal` is a [Python dictionary] that is used by **docassemble**
but that is not intended to be used in interviews.

## <a name="nav"></a>nav

`nav` is an object that is used to keep track of sections in your
interview.  This is relevant if you are using the [navigation bar]
feature.  For information about how to use it, see the documentation
for the [`nav` functions].

## <a name="url_args"></a>url_args

`url_args` is a [Python dictionary] that is used to access parameters
passed via URL.

Users start an interview by going to a URL.  A basic URL would look
like this:

{% highlight text %}
http://example.com/interview?i=docassemble.example_inc:data/questions/survey.yml
{% endhighlight %}

Here, the only parameter is `i`, the interview file name.

It is possible to use the URL to pass special parameters to the
interview code.  For example, if the user started the interview by
clicking on the following link:

{% highlight text %}
http://example.com/interview?i=docassemble.example_inc:data/questions/survey.yml&from=web
{% endhighlight %}

then the interview would load as usual, and the interview code could
access the value of the `from` parameter by looking in the `url_args`
variable in the variable store.  For example, the interview could
contain the following code:

{% highlight yaml %}
---
code: |
  if 'from' in url_args:
    origin_of_interviewee = url_args['from']
  else:
    origin_of_interviewee = 'unknown'
---
mandatory: True
question: You came from the ${ origin_of_interviewee }.
---
{% endhighlight %}

Alternatively, you could use [Python]'s [get] method to do the same
thing in less space:

{% highlight yaml %}
---
mandatory: True
question: You came from the ${ url_args.get('from', 'unknown') }.
---
{% endhighlight %}

You can test this out by trying the following links:

* [{{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=web]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=web){:target="_blank"}
* [{{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=moon]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg.yml&from=moon){:target="_blank"}

As soon as the interview loads, the parameters will no longer appear
in the browser's location bar.  Nevertheless, the parameters remain
available in the `url_args` dictionary for the life of the interview.

Moreover, you can set new `url_args` at any time during the course of
the interview.  For example:

{% highlight yaml %}
---
mandatory: True
question: You came from the ${ url_args.get('from', 'unknown') }.
subquestion: |
  % if url_args.get('fruit', 'apple') == 'apple':
  I think your favorite fruit is an apple, but [click here](?fruit=orange)
  if you disagree.
  % else:
  I see that your favorite fruit is not an apple.
  % endif
---
{% endhighlight %}

You can test this out by trying the following link:
[{{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/testurlarg2.yml&from=wild blue yonder){:target="_blank"}.

<a name="reserved url parameters"></a>The following URL parameters
have special meaning in **docassemble**.  All others are available for
you to use and to retrieve with [`url_args`].

* `i`: indicates the interview file to use
* `session`: indicates the key of the stored dictionary to use
* `action`: used by the [`url_action()`] function
* `filename`: used for retrieving documents
* `question`: used for retrieving documents
* `format`: used for retrieving documents
* `cache`: used to clear the interview evaluation cache
* `reset`: used to restart an interview session
* `new_session`: used to start a new interview session
* `index`: used for retrieving documents
* `from_list`: indicates that interview was launched from the
  Interview List page
* `js_target`: indicates that [JavaScript] should be returned that
  places the interview into the element on the screen with an `id`
  matching the given value.
* `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, and
  `utm_content`: if you have enabled an [`analytics id`] in your
  [`google`] configuration, these [UTM parameters], which are used by
  [Google Analytics] and other analytics sites, will not be processed
  as [`url_args`].  Instead, they will be retained in the location bar
  so that they can be accessed by the [JavaScript] of [Google
  Analytics] or other tracking code.

## <a name="role_needed"></a>role_needed

If you use the [multi-user interview feature] and the user reaches a
point in the interview where input is needed from a different user
before proceeding, **docassemble** will look for a [`question`] that
offers to sets [`role_event`], and ask that question.  **docassemble**
will set the variable `role_needed` to a list of roles capable of
answering the next question in the interview.

# Variables used when finding blocks to set variables

The following variables are set by **docassemble** in the course of
searching for blocks that will define variables.

* `x`
* `i`
* `j`
* `k`
* `l`
* `m`
* `n`

You should never set these variables yourself; they will be set for
you before your blocks are used.

# Variables that interviews can set

## <a name="role"></a>role

If you use the [multi-user interview feature], your interview will
need to have a [`default role` initial block] containing code that
sets the variable `role` to the user's role.

## <a name="speak_text"></a>speak_text

If this special variable is set to `True`, **docassemble** will
present the user with an HTML5 audio control at the top of the page.
When the user clicks it, **docassemble** will access the [VoiceRSS]
web service to convert the text of the question to an audio file and
then play that audio back for the user.  This requires enabling the
[`voicerss`] setting in the [configuration].

Since the [VoiceRSS] service costs money above the free usage tier,
**docassemble** does not send the request to [VoiceRSS] until the user
presses "Play" on the audio control.  It also caches the results and
reuses them whenever possible.

## <a name="track_location"></a>track_location

If set to `True`, the web app will attempt to obtain the user's
position, based on GPS or any other geolocation feature enabled in the
browser.  The [`location_known()`], [`location_returned()`], and
[`user_lat_lon()`] functions can be used to retrieve the information.

The most common way to use this feature is as follows:

{% highlight yaml %}
---
include:
  - basic-questions.yml
---
initial: True
code: |
  track_location = user.location.status()
---
{% endhighlight %}

This will cause `track_location` to be true initially, but once an
attempt has been made to gather the location, it will be set to false.
The user's location can subsequently be obtained by accessing the
`user.location` object.

## <a name="multi_user"></a>multi_user

If you want to use the [multi-user interview feature], you need to set
`multi_user` to `True`.  This is usually done in a "mandatory" or
"initial" code block.

When `multi_user` is set to `True`, **docassemble** will not encrypt
the interview answers (the [interview session dictionary]).  This is
necessary so that different people can access the same interview
session.  When the interview answers are encrypted (which is the
default), only the user who started the interview session can access
the [interview session dictionary].

Setting `multi_user` to `True` will reduce [security] somewhat, but it
is necessary for allowing the [multi-user interview feature] and for
allowing third parties to access the interview answers via the [API].

The `multi_user` variable can be changed dynamically over the course
of an interview.  For example, at a certain point in the interview,
you could ask the user:

{% highlight yaml %}
question: |
  Would you like an attorney to review your answers?
yesno: multi_user
{% endhighlight %}

After `multi_user` is set to `True`, then the next time the interview
answers are saved, encryption will not be used.  Later in the
interview, you can turn encryption back on again by setting
`multi_user` to `False`.

## <a name="menu_items"></a>menu_items

Interviews can add entries to the menu within the web app.

When `menu_items` is set to a [Python list], **docassemble** will add
entries to the menu based on the items in the list.

Each item in the list is expected to be a [Python dictionary] with
keys `label` and `url`.  Typically, these entries are generated using
the [`action_menu_item()` function], which creates a menu item that
runs an "action."  (See the [`url_action()`] and [`process_action()`]
sections of the [functions] page for more information about what
"actions" are in **docassemble**, and for documentation for the
[`action_menu_item()` function].)

{% highlight yaml %}
---
mandatory: True
code: |
  menu_items = [ action_menu_item('Review Answers', 'review_answers') ]
---
{% endhighlight %}

Alternatively, you can set items manually:

{% highlight yaml %}
---
mandatory: True
code: |
  menu_items = [ {'url': 'http://google.com', 'label': 'Go to Google!'} ]
---
{% endhighlight %}

Since menu items are controlled with [`code`] blocks, you can turn them
on and off during the course of the interview as necessary.

## <a name="allow_cron"></a>allow_cron

This variable should be set to `True` if you want to allow the server
to run [scheduled tasks] from your interview.

# Variables that stand in for events

**docassemble** interviews ask questions or run code when required by
[interview logic] and also when caused to do so by [events] and
[actions].  These [events] and [actions] are identified using
variables, which may not ever be defined by an interview.

There are some built-in variable names with special meaning:

* <a name="incoming_email"></a>[`incoming_email`] is used to indicate
  a [`code`] block that should be run when an [e-mail] is received.
* <a name="role_event"></a>[`role_event`] is used to present a special screen when the [roles]
  system requires a change in the interview role.
* <a name="cron_hourly"></a>[`cron_hourly`] is used by the [scheduled tasks] system.  This
  [event] is triggered in the background, every hour, by the server.
  (This requires that [`allow_cron`] be set to `True`.)
* <a name="cron_daily"></a>[`cron_daily`] is similar, except runs on a daily basis.
* <a name="cron_weekly"></a>[`cron_weekly`] is similar, except runs on a weekly basis.
* <a name="cron_monthly"></a>[`cron_monthly`] is similar, except runs on a monthly basis.

# <a name="reserved"></a>Reserved names

The following variables are set internally by **docassemble**.  If you
try to use these reserved names for your own purposes, you will
experience errors or unexpected results.

* <span></span>[`_internal`]: used internally by **docassemble** for various
  purposes, including keeping track of the progress bar, storing the
  answers to multiple-choice questions, and tracking which questions
  have already been answered.
* <span></span>[`cron_daily`]: a special variable that is used as
  part of the [scheduled tasks] system.
* <span></span>[`cron_hourly`]: a special variable that is used as
  part of the [scheduled tasks] system.
* <span></span>[`cron_monthly`]: a special variable that is used as
  part of the [scheduled tasks] system.
* <span></span>[`cron_weekly`]: a special variable that is used as
  part of the [scheduled tasks] system.
* <span></span>[`caller`]: within [Mako] the variable `caller` has a
  special meaning.
* <span></span>[`loop`]: within a [Mako] "for" loop, this variable has
  special meaning.
* <span></span>[`i`], [`j`], [`k`], [`l`], [`m`], [`n`]: used as iterators when
  dictionaries or lists are used.
* <span></span>[`incoming_email`]: a special variable that is used
  as part of the [background processes] system.
* <span></span>[`menu_items`]: used to add items to the menu.
* <span></span>[`multi_user`]: a special variable that is used as
  part of the [roles] system.
* <span></span>[`nav`]: used to keep track of [sections] in the interview.
* <span></span>[`role`]: used to store the role of the current user for purposes of
  the [roles] system.
* <span></span>[`role_event`]: a special variable that is used as part of the [roles]
  system.
* <span></span>[`role_needed`]: a special variable that is used as part of the [roles]
  system.
* <span></span>[`row_index`]: used with [tables].
* <span></span>[`row_item`]: used with [tables].
* <span></span>[`self`]: has a special meaning in [Python].
* <span></span>[`speak_text`]: used to indicate whether the web app should offer
  audio versions of each question, generated by text-to-speech
  synthesis.
* <span></span>[`STOP_RENDERING`]: used in [Mako] templates to end a
  template early.
* <span></span>[`track_location`]: used to indicate whether the web app should
  attempt to determine the user's latitude and longitude.
* <span></span>[`url_args`]: a dictionary available to interview code that contains
  values encoded in the URL with which the interview was initially
  loaded.
* <span></span>`user_dict`: if you use this as a name in an
  interview, your interview will not behave properly.
* <span></span>[`allow_cron`]: a special variable that is used as
  part of the [scheduled tasks] system.
* <span></span>[`x`]: used as a reference to the underlying object when
  [generic objects] are defined.

The following names are imported automatically:

* [`Address`]
* [`Asset`]
* [`ChildList`]
* [`City`]
* [`DACloudStorage`]
* [`DAContext`]
* [`DADict`]
* [`DAEmail`]
* [`DAEmailRecipient`]
* [`DAEmailRecipientList`]
* [`DAEmpty`]
* [`DAFile`]
* [`DAFileCollection`]
* [`DAFileList`]
* [`DAGoogleAPI`]
* [`DALink`]
* [`DAList`]
* [`DAOAuth`]
* [`DAObject`]
* [`DAOrderedDict`]
* [`DARedis`]
* [`DASet`]
* [`DAStaticFile`]
* [`DATemplate`]
* [`DAValidationError`]
* [`Event`]
* [`Expense`]
* [`FinancialList`]
* [`Income`]
* [`Individual`]
* [`IndividualName`]
* [`LatitudeLongitude`]
* [`MachineLearningEntry`]
* [`Name`]
* [`OfficeList`]
* [`Organization`]
* [`PeriodicFinancialList`]
* [`PeriodicValue`]
* [`Person`]
* [`RandomForestMachineLearner`]
* [`RelationshipTree`]
* [`RoleChangeTracker`]
* [`SVMMachineLearner`]
* [`SimpleTextMachineLearner`]
* [`Thing`]
* [`Value`]
* [`action_argument`]
* [`action_arguments`]
* [`action_button_html`]
* [`action_menu_item`]
* [`all_variables`]
* [`alpha`]
* [`as_datetime`]
* [`background_action`]
* [`background_error_action`]
* [`background_response`]
* [`background_response_action`]
* [`bold`]
* [`capitalize`]
* [`chat_partners_available`]
* [`comma_and_list`]
* [`comma_list`]
* [`command`]
* [`countries_list`]
* [`country_name`]
* [`create_user`]
* [`currency`]
* [`currency_symbol`]
* [`current_datetime`]
* [`date_difference`]
* [`date_interval`]
* [`day_of`]
* [`decode_name`]
* [`define`]
* [`defined`]
* [`delete_record`]
* [`device`]
* [`dispatch`]
* [`dow_of`]
* [`encode_name`]
* [`fix_punctuation`]
* [`force_ask`]
* [`force_gather`]
* [`forget_result_of`]
* [`format_date`]
* [`format_datetime`]
* [`format_time`]
* [`from_b64_json`]
* [`get_chat_log`]
* [`get_config`]
* [`get_country`]
* [`get_default_timezone`]
* [`get_dialect`]
* [`get_emails`]
* [`get_info`]
* [`get_language`]
* [`get_locale`]
* [`get_progress`]
* [`get_question_data`]
* [`get_session_variables`]
* [`get_sms_session`]
* [`get_user_info`]
* [`get_user_list`]
* [`get_user_secret`]
* [`go_back_in_session`]
* [`include_docx_template`]
* [`indefinite_article`]
* [`indent`]
* [`initiate_sms_session`]
* [`interface`]
* [`interview_email`]
* [`interview_list`]
* [`interview_menu`]
* [`interview_url`]
* [`interview_url_action`]
* [`interview_url_action_as_qr`]
* [`interview_url_as_qr`]
* [`italic`]
* [`item_label`]
* [`json_response`]
* [`language_from_browser`]
* [`last_access_days`]
* [`last_access_delta`]
* [`last_access_hours`]
* [`last_access_minutes`]
* [`last_access_time`]
* [`location_known`]
* [`location_returned`]
* [`log`]
* [`manage_privileges`]
* [`map_of`]
* [`mark_task_as_performed`]
* [`message`]
* [`month_of`]
* [`name_suffix`]
* [`need`]
* [`nice_number`]
* [`noun_plural`]
* [`noun_singular`]
* [`noyes`]
* [`objects_from_file`]
* [`ocr_file`]
* [`ocr_file_in_background`]
* [`ordinal`]
* [`ordinal_number`]
* [`overlay_pdf`]
* [`path_and_mimetype`]
* [`pdf_concatenate`]
* [`period_list`]
* [`phone_number_in_e164`]
* [`phone_number_is_valid`]
* [`phone_number_part`]
* [`plain`]
* [`prevent_going_back`]
* [`process_action`]
* [`qr_code`]
* [`quantity_noun`]
* [`quote_paragraphs`]
* [`raw`]
* [`re_run_logic`]
* [`read_qr`]
* [`read_records`]
* [`reconsider`]
* [`redact`]
* [`referring_url`]
* [`response`]
* [`returning_user`]
* [`roman`]
* [`run_python_module`]
* [`selections`]
* [`send_email`]
* [`send_fax`]
* [`send_sms`]
* [`server_capabilities`]
* [`session_tags`]
* [`set_country`]
* [`set_info`]
* [`set_language`]
* [`set_live_help_status`]
* [`set_locale`]
* [`set_parts`]
* [`set_progress`]
* [`set_save_status`]
* [`set_session_variables`]
* [`set_task_counter`]
* [`set_title`]
* [`set_user_info`]
* [`showif`]
* [`showifdef`]
* [`single_paragraph`]
* [`single_to_double_newlines`]
* [`space_to_underscore`]
* [`split`]
* [`start_time`]
* [`state_name`]
* [`states_list`]
* [`static_image`]
* [`subdivision_type`]
* [`task_not_yet_performed`]
* [`task_performed`]
* [`terminate_sms_session`]
* [`times_task_performed`]
* [`timezone_list`]
* [`title_case`]
* [`today`]
* [`undefine`]
* [`url_action`]
* [`url_ask`]
* [`url_of`]
* [`us`]
* [`user_has_privilege`]
* [`user_info`]
* [`user_lat_lon`]
* [`user_logged_in`]
* [`user_privileges`]
* [`validation_error`]
* [`value`]
* [`variables_as_json`]
* [`verb_past`]
* [`verb_present`]
* [`word`]
* [`write_record`]
* [`year_of`]
* [`yesno`]
* [`zip_file`]

If you include a [`modules`] block including
[`docassemble.base.legal`], the above names will be used, as well as
the following additional names:

* [`Case`]
* [`Court`]
* [`Document`]
* [`Jurisdiction`]
* [`LegalFiling`]
* [`PartyList`]

If you include the [`basic-questions.yml`] file from [`docassemble.base`],
the names included by [`docassemble.base.legal`] will be included, and
the following names will also be used:

* `advocate`
* `blank_signature`
* `case`
* `client`
* `court`
* `empty_signature`
* `jurisdiction`
* `pleading`
* `role`
* `role_event`
* `role_needed`
* `spouse`
* `user`
* `user_understands_how_to_use_signature_feature`
* `user_understands_no_attorney_client_relationship`

In addition, [Python] uses the following names as part of the
language.  If you use any of these as your own variable names, you may
encounter an error or an unexpected problem.

* `ArithmeticError`
* `AssertionError`
* `AttributeError`
* `BaseException`
* `BufferError`
* `BytesWarning`
* `DeprecationWarning`
* `EOFError`
* `Ellipsis`
* `EnvironmentError`
* `Exception`
* `False`
* `FloatingPointError`
* `FutureWarning`
* `GeneratorExit`
* `IOError`
* `ImportError`
* `ImportWarning`
* `IndentationError`
* `IndexError`
* `KeyError`
* `KeyboardInterrupt`
* `LookupError`
* `MemoryError`
* `NameError`
* `None`
* `NotImplementedError`
* `NotImplemented`
* `OSError`
* `OverflowError`
* `PendingDeprecationWarning`
* `ReferenceError`
* `RuntimeError`
* `RuntimeWarning`
* `StandardError`
* `StopIteration`
* `SyntaxError`
* `SyntaxWarning`
* `SystemError`
* `SystemExit`
* `TabError`
* `True`
* `TypeError`
* `UnboundLocalError`
* `UnicodeDecodeError`
* `UnicodeEncodeError`
* `UnicodeError`
* `UnicodeTranslateError`
* `UnicodeWarning`
* `UserWarning`
* `ValueError`
* `Warning`
* `WindowsError`
* `ZeroDivisionError`
* `__debug__`
* `__doc__`
* `__import__`
* `__name__`
* `__package__`
* `_`
* `abs`
* `all`
* `and`
* `any`
* `apply`
* `as`
* `assert`
* `basestring`
* `bin`
* `bool`
* `break`
* `buffer`
* `bytearray`
* `bytes`
* `callable`
* `chr`
* `class`
* `classmethod`
* `cmp`
* `coerce`
* `compile`
* `complex`
* `continue`
* `copyright`
* `credits`
* `def`
* `del`
* `delattr`
* `dict`
* `dir`
* `divmod`
* `elif`
* `else`
* `enumerate`
* `eval`
* `except`
* `exec`
* `execfile`
* `exit`
* `file`
* `filter`
* `finally`
* `float`
* `for`
* `format`
* `from`
* `frozenset`
* `getattr`
* `global`
* `globals`
* `hasattr`
* `hash`
* `help`
* `hex`
* `id`
* `if`
* `import`
* `in`
* `input`
* `int`
* `intern`
* `is`
* `isinstance`
* `issubclass`
* `iter`
* `lambda`
* `len`
* `license`
* `list`
* `locals`
* `long`
* `map`
* `max`
* `memoryview`
* `min`
* `next`
* `not`
* `object`
* `oct`
* `open`
* `or`
* `ord`
* `pass`
* `pow`
* `print`
* `print`
* `property`
* `quit`
* `raise`
* `range`
* `raw_input`
* `reduce`
* `reload`
* `repr`
* `return`
* `reversed`
* `round`
* `set`
* `setattr`
* `slice`
* `sorted`
* `staticmethod`
* `str`
* `sum`
* `super`
* `try`
* `tuple`
* `type`
* `unichr`
* `unicode`
* `vars`
* `while`
* `with`
* `xrange`
* `yield`
* `zip`

In addition, you should never use a variable name that begins with an
underscore.  Although `_internal` is the only variable in the variable
store that begins with an underscore, the **docassemble** web app uses
names that begin with underscores to communicate information between
the browser and the server, and if your variable names conflict with
these names, you may experience errors or unexpected results.  These
internal names include:

* `_attachment_email_address`
* `_attachment_include_editable`
* `_back_one`
* `_checkboxes`
* `_datatypes`
* `_email_attachments`
* `_files`
* `_question_number`
* `_question_name`
* `_save_as`
* `_success`
* `_the_image`
* `_track_location`
* `_tracker`
* `_varnames`

[API]: {{ site.baseurl }}/docs/api.html
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[Mako]: http://www.makotemplates.org/
[Profile]: {{ site.baseurl }}/docs/users.html#profile
[Python dictionary]: https://docs.python.org/3/tutorial/datastructures.html#dictionaries
[Python list]: https://docs.python.org/3/tutorial/datastructures.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[User List]: {{ site.baseurl }}/docs/users.html#user_list
[VoiceRSS]: http://www.voicerss.org/
[`Address`]: {{ site.baseurl }}/docs/objects.html#Address
[`Asset`]: {{ site.baseurl }}/docs/objects.html#Asset
[`Case`]: {{ site.baseurl }}/docs/legal.html#Case
[`City`]: {{ site.baseurl }}/docs/objects.html#City
[`ChildList`]: {{ site.baseurl }}/docs/objects.html#ChildList
[`Court`]: {{ site.baseurl }}/docs/legal.html#Court
[`DACloudStorage`]: {{ site.baseurl }}/docs/objects.html#DACloudStorage
[`DAContext`]: {{ site.baseurl }}/docs/objects.html#DAContext
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`DAEmailRecipientList`]: {{ site.baseurl }}/docs/objects.html#DAEmailRecipientList
[`DAEmailRecipient`]: {{ site.baseurl }}/docs/objects.html#DAEmailRecipient
[`DAEmail`]: {{ site.baseurl }}/docs/objects.html#DAEmail
[`DAEmpty`]: {{ site.baseurl }}/docs/objects.html#DAEmpty
[`DAFileCollection`]: {{ site.baseurl }}/docs/objects.html#DAFileCollection
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`DAGoogleAPI`]: {{ site.baseurl }}/docs/objects.html#DAGoogleAPI
[`DALink`]: {{ site.baseurl }}/docs/objects.html#DALink
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DAOAuth`]: {{ site.baseurl }}/docs/objects.html#DAOAuth
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`DAOrderedDict`]: {{ site.baseurl }}/docs/objects.html#DAOrderedDict
[`DARedis`]: {{ site.baseurl }}/docs/functions.html#redis
[`DASet`]: {{ site.baseurl }}/docs/objects.html#DASet
[`DAStaticFile`]: {{ site.baseurl }}/docs/objects.html#DAStaticFile
[`DATemplate`]: {{ site.baseurl }}/docs/objects.html#DATemplate
[`DAValidationError`]: {{ site.baseurl }}/docs/objects.html#DAValidationError
[`Document`]: {{ site.baseurl }}/docs/legal.html#Document
[`Event`]: {{ site.baseurl }}/docs/objects.html#Event
[`Expense`]: {{ site.baseurl }}/docs/objects.html#Expense
[`FinancialList`]: {{ site.baseurl }}/docs/objects.html#FinancialList
[`Income`]: {{ site.baseurl }}/docs/objects.html#Income
[`IndividualName`]: {{ site.baseurl }}/docs/objects.html#IndividualName
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`Jurisdiction`]: {{ site.baseurl }}/docs/legal.html#Jurisdiction
[`LatitudeLongitude`]: {{ site.baseurl }}/docs/objects.html#LatitudeLongitude
[`LegalFiling`]: {{ site.baseurl }}/docs/legal.html#LegalFiling
[`MachineLearningEntry`]: {{ site.baseurl }}/docs/ml.html#MachineLearningEntry
[`Name`]: {{ site.baseurl }}/docs/objects.html#Name
[`OfficeList`]: {{ site.baseurl }}/docs/objects.html#OfficeList
[`Organization`]: {{ site.baseurl }}/docs/objects.html#Organization
[`PartyList`]: {{ site.baseurl }}/docs/legal.html#PartyList
[`PeriodicFinancialList`]: {{ site.baseurl }}/docs/objects.html#PeriodicFinancialList
[`PeriodicValue`]: {{ site.baseurl }}/docs/objects.html#PeriodicValue
[`Person`]: {{ site.baseurl }}/docs/objects.html#Person
[`RandomForestMachineLearner`]: {{ site.baseurl }}/docs/ml.html#RandomForestMachineLearner
[`RelationshipTree`]: {{ site.baseurl }}/docs/objects.html#RelationshipTree
[`RoleChangeTracker`]: {{ site.baseurl }}/docs/objects.html#RoleChangeTracker
[`STOP_RENDERING`]: http://docs.makotemplates.org/en/latest/syntax.html#exiting-early-from-a-template
[`SVMMachineLearner`]: {{ site.baseurl }}/docs/ml.html#SVMMachineLearner
[`SimpleTextMachineLearner`]: {{ site.baseurl }}/docs/ml.html
[`Thing`]: {{ site.baseurl }}/docs/objects.html#Thing
[`Value`]: {{ site.baseurl }}/docs/objects.html#Value
[`_internal`]: #_internal
[`action_argument`]: {{ site.baseurl }}/docs/functions.html#action_argument
[`action_arguments`]: {{ site.baseurl }}/docs/functions.html#action_arguments
[`action_button_html`]: {{ site.baseurl }}/docs/functions.html#action_button_html
[`action_menu_item()` function]: {{ site.baseurl }}/docs/functions.html#action_menu_item
[`action_menu_item`]: {{ site.baseurl }}/docs/functions.html#action_menu_item
[`all_variables`]: {{ site.baseurl }}/docs/functions.html#all_variables
[`allow_cron`]: #allow_cron
[`alpha`]: {{ site.baseurl }}/docs/functions.html#alpha
[`as_datetime`]: {{ site.baseurl }}/docs/functions.html#as_datetime
[`background_action`]: {{ site.baseurl }}/docs/background.html#background_action
[`background_error_action`]: {{ site.baseurl }}/docs/functions.html#background_error_action
[`background_response_action`]: {{ site.baseurl }}/docs/background.html#background_response_action
[`background_response`]: {{ site.baseurl }}/docs/background.html#background_response
[`basic-questions.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[`bold`]: {{ site.baseurl }}/docs/functions.html#bold
[`caller`]: https://docs.makotemplates.org/en/latest/defs.html#calling-a-def-with-embedded-content-and-or-other-defs
[`capitalize`]: {{ site.baseurl }}/docs/functions.html#capitalize
[`chat_partners_available`]: {{ site.baseurl }}/docs/functions.html#chat_partners_available
[`code`]: {{ site.baseurl }}/docs/code.html
[`comma_and_list`]: {{ site.baseurl }}/docs/functions.html#comma_and_list
[`comma_list`]: {{ site.baseurl }}/docs/functions.html#comma_list
[`command`]: {{ site.baseurl }}/docs/functions.html#command
[`countries_list`]: {{ site.baseurl }}/docs/functions.html#countries_list
[`country_name`]: {{ site.baseurl }}/docs/functions.html#country_name
[`create_user`]: {{ site.baseurl }}/docs/functions.html#create_user
[`cron_daily`]: #cron_daily
[`cron_hourly`]: #cron_hourly
[`cron_monthly`]: #cron_monthly
[`cron_weekly`]: #cron_weekly
[`currency_symbol`]: {{ site.baseurl }}/docs/functions.html#currency_symbol
[`currency`]: {{ site.baseurl }}/docs/functions.html#currency
[`current_datetime`]: {{ site.baseurl }}/docs/functions.html#current_datetime
[`date_difference`]: {{ site.baseurl }}/docs/functions.html#date_difference
[`date_interval`]: {{ site.baseurl }}/docs/functions.html#date_interval
[`day_of`]: {{ site.baseurl }}/docs/functions.html#day_of
[`decode_name`]: {{ site.baseurl }}/docs/functions.html#decode_name
[`default role` initial block]: {{ site.baseurl }}/docs/initial.html#default_role
[`define`]: {{ site.baseurl }}/docs/functions.html#define
[`defined`]: {{ site.baseurl }}/docs/functions.html#defined
[`delete_record`]: {{ site.baseurl }}/docs/functions.html#delete_record
[`device`]: {{ site.baseurl }}/docs/functions.html#device
[`dispatch`]: {{ site.baseurl }}/docs/functions.html#dispatch
[`docassemble.base.legal`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/legal.py
[`docassemble.base`]: {{ site.baseurl }}/docs/installation.html#docassemble.base
[`dow_of`]: {{ site.baseurl }}/docs/functions.html#dow_of
[`encode_name`]: {{ site.baseurl }}/docs/functions.html#encode_name
[`fix_punctuation`]: {{ site.baseurl }}/docs/functions.html#fix_punctuation
[`force_ask`]: {{ site.baseurl }}/docs/functions.html#force_ask
[`force_gather`]: {{ site.baseurl }}/docs/functions.html#force_gather
[`forget_result_of`]: {{ site.baseurl }}/docs/functions.html#forget_result_of
[`format_date`]: {{ site.baseurl }}/docs/functions.html#format_date
[`format_datetime`]: {{ site.baseurl }}/docs/functions.html#format_datetime
[`format_time`]: {{ site.baseurl }}/docs/functions.html#format_time
[`from_b64_json`]: {{ site.baseurl }}/docs/functions.html#from_b64_json
[`get_chat_log`]: {{ site.baseurl }}/docs/functions.html#get_chat_log
[`get_config`]: {{ site.baseurl }}/docs/functions.html#get_config
[`get_country`]: {{ site.baseurl }}/docs/functions.html#get_country
[`get_default_timezone`]: {{ site.baseurl }}/docs/functions.html#get_default_timezone
[`get_dialect`]: {{ site.baseurl }}/docs/functions.html#get_dialect
[`get_emails`]: {{ site.baseurl }}/docs/functions.html#get_emails
[`get_info`]: {{ site.baseurl }}/docs/functions.html#get_info
[`get_language`]: {{ site.baseurl }}/docs/functions.html#get_language
[`get_locale`]: {{ site.baseurl }}/docs/functions.html#get_locale
[`get_progress`]: {{ site.baseurl }}/docs/functions.html#get_progress
[`get_question_data`]: {{ site.baseurl }}/docs/functions.html#get_question_data
[`get_session_variables`]: {{ site.baseurl }}/docs/functions.html#get_session_variables
[`get_sms_session`]: {{ site.baseurl }}/docs/functions.html#get_sms_session
[`get_user_info`]: {{ site.baseurl }}/docs/functions.html#get_user_info
[`get_user_list`]: {{ site.baseurl }}/docs/functions.html#get_user_list
[`get_user_secret`]: {{ site.baseurl }}/docs/functions.html#get_user_secret
[`go_back_in_session`]: {{ site.baseurl }}/docs/functions.html#go_back_in_session
[`i`]: {{ site.baseurl }}/docs/groups.html#i
[`include_docx_template`]: {{ site.baseurl }}/docs/functions.html#include_docx_template
[`incoming_email`]: {{ site.baseurl }}/docs/background.html#email
[`indefinite_article`]: {{ site.baseurl }}/docs/functions.html#indefinite_article
[`indent`]: {{ site.baseurl }}/docs/functions.html#indent
[`initiate_sms_session`]: {{ site.baseurl }}/docs/functions.html#initiate_sms_session
[`interface`]: {{ site.baseurl }}/docs/functions.html#interface
[`interview_email`]: {{ site.baseurl }}/docs/functions.html#interview_email
[`interview_list`]: {{ site.baseurl }}/docs/functions.html#interview_list
[`interview_menu`]: {{ site.baseurl }}/docs/functions.html#interview_menu
[`interview_url_action_as_qr`]: {{ site.baseurl }}/docs/functions.html#interview_url_action_as_qr
[`interview_url_action`]: {{ site.baseurl }}/docs/functions.html#interview_url_action
[`interview_url_as_qr`]: {{ site.baseurl }}/docs/functions.html#interview_url_as_qr
[`interview_url`]: {{ site.baseurl }}/docs/functions.html#interview_url
[`italic`]: {{ site.baseurl }}/docs/functions.html#italic
[`item_label`]: {{ site.baseurl }}/docs/functions.html#item_label
[`j`]: {{ site.baseurl }}/docs/groups.html#i
[`json_response`]: {{ site.baseurl }}/docs/functions.html#json_response
[`k`]: {{ site.baseurl }}/docs/groups.html#i
[`l`]: {{ site.baseurl }}/docs/groups.html#i
[`language_from_browser`]: {{ site.baseurl }}/docs/functions.html#language_from_browser
[`last_access_days`]: {{ site.baseurl }}/docs/functions.html#last_access_days
[`last_access_delta`]: {{ site.baseurl }}/docs/functions.html#last_access_delta
[`last_access_hours`]: {{ site.baseurl }}/docs/functions.html#last_access_hours
[`last_access_minutes`]: {{ site.baseurl }}/docs/functions.html#last_access_minutes
[`last_access_time`]: {{ site.baseurl }}/docs/functions.html#last_access_time
[`location_known()`]: {{ site.baseurl }}/docs/functions.html#location_known
[`location_known`]: {{ site.baseurl }}/docs/functions.html#location_known
[`location_returned()`]: {{ site.baseurl }}/docs/functions.html#location_returned
[`location_returned`]: {{ site.baseurl }}/docs/functions.html#location_returned
[`log`]: {{ site.baseurl }}/docs/functions.html#log
[`loop`]: http://docs.makotemplates.org/en/latest/runtime.html#loop-context
[`m`]: {{ site.baseurl }}/docs/groups.html#i
[`manage_privileges`]: {{ site.baseurl }}/docs/functions.html#manage_privileges
[`map_of`]: {{ site.baseurl }}/docs/functions.html#map_of
[`mark_task_as_performed`]: {{ site.baseurl }}/docs/functions.html#mark_task_as_performed
[`menu_items`]: #menu_items
[`message`]: {{ site.baseurl }}/docs/functions.html#message
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
[`month_of`]: {{ site.baseurl }}/docs/functions.html#month_of
[`multi_user`]: #multi_user
[`n`]: {{ site.baseurl }}/docs/groups.html#i
[`name_suffix`]: {{ site.baseurl }}/docs/functions.html#name_suffix
[`nav` functions]: {{ site.baseurl }}/docs/functions.html#get_section
[`nav`]: {{ site.baseurl }}/docs/initial.html#navigation bar
[`need`]: {{ site.baseurl }}/docs/functions.html#need
[`nice_number`]: {{ site.baseurl }}/docs/functions.html#nice_number
[`noun_plural`]: {{ site.baseurl }}/docs/functions.html#noun_plural
[`noun_singular`]: {{ site.baseurl }}/docs/functions.html#noun_singular
[`noyes`]: {{ site.baseurl }}/docs/functions.html#noyes
[`objects_from_file`]: {{ site.baseurl }}/docs/functions.html#objects_from_file
[`ocr_file_in_background`]: {{ site.baseurl }}/docs/functions.html#ocr_file_in_background
[`ocr_file`]: {{ site.baseurl }}/docs/functions.html#ocr_file
[`ordinal_number`]: {{ site.baseurl }}/docs/functions.html#ordinal_number
[`ordinal`]: {{ site.baseurl }}/docs/functions.html#ordinal
[`overlay_pdf`]: {{ site.baseurl }}/docs/functions.html#overlay_pdf
[`path_and_mimetype`]: {{ site.baseurl }}/docs/functions.html#path_and_mimetype
[`pdf_concatenate`]: {{ site.baseurl }}/docs/functions.html#pdf_concatenate
[`period_list`]: {{ site.baseurl }}/docs/functions.html#period_list
[`phone_number_in_e164`]: {{ site.baseurl }}/docs/functions.html#phone_number_in_e164
[`phone_number_is_valid`]: {{ site.baseurl }}/docs/functions.html#phone_number_is_valid
[`phone_number_part`]: {{ site.baseurl }}/docs/functions.html#phone_number_part
[`plain`]: {{ site.baseurl }}/docs/functions.html#plain
[`prevent_going_back`]: {{ site.baseurl }}/docs/functions.html#prevent_going_back
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[`process_action`]: {{ site.baseurl }}/docs/functions.html#process_action
[`qr_code`]: {{ site.baseurl }}/docs/functions.html#qr_code
[`quantity_noun`]: {{ site.baseurl }}/docs/functions.html#quantity_noun
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`quote_paragraphs`]: {{ site.baseurl }}/docs/functions.html#quote_paragraphs
[`raw`]: {{ site.baseurl }}/docs/functions.html#raw
[`re_run_logic`]: {{ site.baseurl }}/docs/functions.html#re_run_logic
[`read_qr`]: {{ site.baseurl }}/docs/functions.html#read_qr
[`read_records`]: {{ site.baseurl }}/docs/functions.html#read_records
[`reconsider`]: {{ site.baseurl }}/docs/functions.html#reconsider
[`redact`]: {{ site.baseurl }}/docs/functions.html#redact
[`referring_url`]: {{ site.baseurl }}/docs/functions.html#referring_url
[`response`]: {{ site.baseurl }}/docs/functions.html#response
[`returning_user`]: {{ site.baseurl }}/docs/functions.html#returning_user
[`role_event`]: {{ site.baseurl }}/docs/roles.html
[`role_needed`]: #role_needed
[`role`]: #role
[`roman`]: {{ site.baseurl }}/docs/functions.html#roman
[`row_index`]: {{ site.baseurl }}/docs/initial.html#table
[`row_item`]: {{ site.baseurl }}/docs/initial.html#table
[`run_python_module`]: {{ site.baseurl }}/docs/functions.html#run_python_module
[`selections`]: {{ site.baseurl }}/docs/functions.html#selections
[`self`]: https://docs.python.org/3.6/tutorial/classes.html
[`send_email`]: {{ site.baseurl }}/docs/functions.html#send_email
[`send_fax`]: {{ site.baseurl }}/docs/functions.html#send_fax
[`send_sms`]: {{ site.baseurl }}/docs/functions.html#send_sms
[`server_capabilities`]: {{ site.baseurl }}/docs/functions.html#server_capabilities
[`session_tags`]: {{ site.baseurl }}/docs/functions.html#session_tags
[`set_country`]: {{ site.baseurl }}/docs/functions.html#set_country
[`set_info`]: {{ site.baseurl }}/docs/functions.html#set_info
[`set_language`]: {{ site.baseurl }}/docs/functions.html#set_language
[`set_live_help_status`]: {{ site.baseurl }}/docs/functions.html#set_live_help_status
[`set_locale`]: {{ site.baseurl }}/docs/functions.html#set_locale
[`set_parts`]: {{ site.baseurl }}/docs/functions.html#set_parts
[`set_progress`]: {{ site.baseurl }}/docs/functions.html#set_progress
[`set_save_status`]: {{ site.baseurl }}/docs/functions.html#set_save_status
[`set_session_variables`]: {{ site.baseurl }}/docs/functions.html#set_session_variables
[`set_task_counter`]: {{ site.baseurl }}/docs/functions.html#set_task_counter
[`set_title`]: {{ site.baseurl }}/docs/functions.html#set_title
[`set_user_info`]: {{ site.baseurl }}/docs/functions.html#set_user_info
[`showif`]: {{ site.baseurl }}/docs/functions.html#showif
[`showifdef`]: {{ site.baseurl }}/docs/functions.html#showifdef
[`single_paragraph`]: {{ site.baseurl }}/docs/functions.html#single_paragraph
[`single_to_double_newlines`]: {{ site.baseurl }}/docs/functions.html#single_to_double_newlines
[`space_to_underscore`]: {{ site.baseurl }}/docs/functions.html#space_to_underscore
[`speak_text`]: #speak_text
[`split`]: {{ site.baseurl }}/docs/functions.html#split
[`start_time`]: {{ site.baseurl }}/docs/functions.html#start_time
[`state_name`]: {{ site.baseurl }}/docs/functions.html#state_name
[`states_list`]: {{ site.baseurl }}/docs/functions.html#states_list
[`static_image`]: {{ site.baseurl }}/docs/functions.html#static_image
[`string_types`]: https://six.readthedocs.io/#six.string_types
[`subdivision_type`]: {{ site.baseurl }}/docs/functions.html#subdivision_type
[`task_not_yet_performed`]: {{ site.baseurl }}/docs/functions.html#task_not_yet_performed
[`task_performed`]: {{ site.baseurl }}/docs/functions.html#task_performed
[`terminate_sms_session`]: {{ site.baseurl }}/docs/functions.html#terminate_sms_session
[`text_type`]: {{ site.baseurl }}/docs/functions.html#text_type
[`times_task_performed`]: {{ site.baseurl }}/docs/functions.html#times_task_performed
[`timezone_list`]: {{ site.baseurl }}/docs/functions.html#timezone_list
[`title_case`]: {{ site.baseurl }}/docs/functions.html#title_case
[`today`]: {{ site.baseurl }}/docs/functions.html#today
[`track_location`]: #track_location
[`track_location`]: #track_location
[`undefine`]: {{ site.baseurl }}/docs/functions.html#undefine
[`url_action()`]: {{ site.baseurl }}/docs/functions.html#url_action
[`url_action`]: {{ site.baseurl }}/docs/functions.html#url_action
[`url_args`]: #url_args
[`url_ask`]: {{ site.baseurl }}/docs/functions.html#url_ask
[`url_of`]: {{ site.baseurl }}/docs/functions.html#url_of
[`us`]: https://pypi.python.org/pypi/us
[`user_has_privilege`]: {{ site.baseurl }}/docs/functions.html#user_has_privilege
[`user_info`]: {{ site.baseurl }}/docs/functions.html#user_info
[`user_lat_lon()`]: {{ site.baseurl }}/docs/functions.html#user_lat_lon
[`user_lat_lon`]: {{ site.baseurl }}/docs/functions.html#user_lat_lon
[`user_logged_in`]: {{ site.baseurl }}/docs/functions.html#user_logged_in
[`user_privileges`]: {{ site.baseurl }}/docs/functions.html#user_privileges
[`validation_error`]: {{ site.baseurl }}/docs/functions.html#validation_error
[`value`]: {{ site.baseurl }}/docs/functions.html#value
[`variables_as_json`]: {{ site.baseurl }}/docs/functions.html#variables_as_json
[`verb_past`]: {{ site.baseurl }}/docs/functions.html#verb_past
[`verb_present`]: {{ site.baseurl }}/docs/functions.html#verb_present
[`voicerss`]: {{ site.baseurl }}/docs/config.html#voicerss
[`word`]: {{ site.baseurl }}/docs/functions.html#word
[`words`]: {{ site.baseurl }}/docs/functions.html#words
[`write_record`]: {{ site.baseurl }}/docs/functions.html#write_record
[`x`]: {{ site.baseurl }}/docs/modifiers.html#x
[`year_of`]: {{ site.baseurl }}/docs/functions.html#year_of
[`yesno`]: {{ site.baseurl }}/docs/functions.html#yesno
[`your`]: {{ site.baseurl }}/docs/functions.html#your
[`zip_file`]: {{ site.baseurl }}/docs/functions.html#zip_file
[actions]: {{ site.baseurl }}/docs/functions.html#actions
[background processes]: {{ site.baseurl }}/docs/background.html#background
[configuration]: {{ site.baseurl }}/docs/config.html
[e-mail]: {{ site.baseurl }}/docs/background.html#email
[event]: {{ site.baseurl }}/docs/background.html
[events]: {{ site.baseurl }}/docs/fields.html#event
[function]: {{ site.baseurl }}/docs/functions.html
[functions]: {{ site.baseurl }}/docs/functions.html
[generic objects]: {{ site.baseurl }}/docs/modifiers.html#generic object
[get]: https://docs.python.org/3/library/stdtypes.html#dict.get
[interview logic]: {{ site.baseurl }}/docs/logic.html
[interview session dictionary]: {{ site.baseurl }}/docs/interviews.html#howstored
[multi-user interview feature]: {{ site.baseurl }}/docs/roles.html
[navigation bar]: {{ site.baseurl }}/docs/initial.html#navigation bar
[roles]: {{ site.baseurl }}/docs/roles.html
[scheduled tasks]: {{ site.baseurl }}/docs/background.html#scheduled
[sections]: {{ site.baseurl }}/docs/initial.html#navigation bar
[security]: {{ site.baseurl }}/docs/security.html
[tables]: {{ site.baseurl }}/docs/initial.html#table
[UTM parameters]: https://en.wikipedia.org/wiki/UTM_parameters
[Google Analytics]: https://analytics.google.com
[`analytics id`]: {{ site.baseurl }}/docs/config.html#google analytics
[`google`]: {{ site.baseurl }}/docs/config.html#google
