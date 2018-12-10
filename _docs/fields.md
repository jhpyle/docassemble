---
layout: docs
title: Setting variables (and doing other things) with questions
short_title: Setting Variables
---

To instruct **docassemble** to store user input that it receives in
response to a [question], you need to include in your [`question`] a
[variable name](#variable names) to hold the information.  You also
need to indicate what type of variable it is (e.g., text, a date, a
number), and how you want to ask for the input (e.g., with a label).

This section explains the many ways that variables can be populated
using [`question`]s.

# <a name="variable names"></a>A note about variable names

Variable names are [Python identifiers], which means they can be any
sequence of uppercase or lowercase letters, digits, and underscores,
except the first character cannot be a digit.  No spaces are allowed
and no punctuation is allowed except for the underscore, `_`.

The following are valid variable names:

* `fried_fish1`
* `NyanCat`
* `nyancat` (variables are case-sensitive, so this is not the same as
  the above)
* `__f645456DG_greij_43` (but why would you use something so ugly?)
* `USER_PHONE_NUMBER` (ok, but why are you yelling?)

The following are **not** valid variable names, and if you try to use
such variable names you will may get an error or unexpected results:

* `8th_plaintiff` (you can't begin a variable name with a number;
  [Python] will say "invalid syntax")
* `Nyan-Cat` (this is arithmetic: `Nyan` minus `Cat`)
* `fried.fish1` (this is valid code, but [Python] will think you are
referring to the attribute `fish1` of the object `fried`)
* `user's_phone_number` (apostrophes are not allowed; [Python]
  recognizes them as single quotes)
* `favorite animal` (spaces are not allowed)
* `beneficiary#1` (punctuation marks other than `_` are not allowed)
* `applicant_résumé` (only plain alphabet characters can be used)

If you find yourself using variable names like `automobile_one` and
`automobile_two`, you should learn about [groups] and
[generalizing](#general).  It would make more sense to work with
variables `automobile[0]` and `automobile[1]`, or `automobile[i]`.

If you find yourself using variable names like `employment_income`,
`self_employment_income`, and `retirement_income`, you should learn
about the [`DADict`] (a type of [group]).  It would make more sense to
work with variables like `income['employment']`,
`income['self-employment']`, and `income['retirement']`.  Then you
could [generalize](#general) the questions you ask.

And if you find yourself using variable names like
`defendant_spouse_ssn` and `defendant_spouse_date_of_birth`, you
should learn about [objects].  It would make more sense to work with
variables like `defendant.spouse.ssn` and
`defendant.spouse.birthdate`.  There are many advantages of working
with objects, such as being able to write `defendant.age_in_years()`
and `defendant.spouse.age_in_years()` to calculate the ages of people
based on their birthdates.

See [reserved variable names] for a list of variable names that you
cannot use because they conflict with built-in names that [Python] and
**docassemble** use.

# <a name="mconevar"></a>Multiple choice questions (one variable only)

## <a name="yesornoquestions"></a>Yes or no questions

### <a name="yesno"></a><a name="noyes"></a>`yesno` and `noyes`

`yesno` causes a question to set a boolean (true/false)
variable when answered.

{% include side-by-side.html demo="yesno" %}

In the example above, the web app will present "Yes" and "No" buttons
and will set `over_eighteen` to `True` if "Yes" is pressed, and
`False` if "No" is pressed.

`noyes` is just like `yesno`, except that "Yes" means
`False` and "No" means `True`.

{% include side-by-side.html demo="noyes" %}

Note that yes/no fields can also be gathered on a screen along with
other fields; to make screens like that, use [`fields`] below.

### <a name="yesnomaybe"></a><a name="noyesmaybe"></a>`yesnomaybe` or `noyesmaybe`

These are just like `yesno` and `noyes`, except that they offer a
third choice, "I don't know."  If the user selects "I don't know," the
variable is set to `None`, which is a special [Python constant] that
represents the absence of a value.

{% include side-by-side.html demo="yesnomaybe" %}

## <a name="field with buttons"></a>Multiple choice buttons

A [`question`] block with `buttons` will set the variable
identified in `field` to a particular value depending on which of the
buttons the user presses.

`buttons` must always refer to a list, so that **docassemble** knows
the order of the buttons.

If an item under `buttons` is a [YAML] key-value pair (written in the
form of `- key: value`), then the key will be the button label that the
user sees, and the value will be what the variable identified in `field`
will be set to if the user presses that button.

{% include side-by-side.html demo="buttons-labels" %}

An item under `buttons` can also be plain text; in that case
**docassemble** uses this text for both the label and the variable
value.

{% include side-by-side.html demo="buttons" %}

In other words, this:

{% include side-by-side.html demo="buttons-variation-1" %}

is equivalent to this:

{% include side-by-side.html demo="buttons-variation-2" %}

### <a name="code generated buttons"></a>Using code to generate the choices

A powerful feature of `buttons` (which also works with
[`choices`](#field with choices), [`dropdown`](#field with dropdown),
and [`combobox`](#field with combobox)) is the ability to use [Python]
code to generate button choices.  If an item under `buttons` is a
key-value pair in which the key is the word [`code`](#code), then
**docassemble** executes the value as [Python] code, which is expected
to return a list.  This code is executed at the time the question is
asked, and the code can include variables from the interview.
**docassemble** will process the resulting list and create additional
buttons for each item.

{% include side-by-side.html demo="buttons-code-list" %}

Note that the [Python] code needs to return a list of key-value pairs
([Python dictionaries]) where the key is what the variable should be
set to and the value is the button label.  This is different from the
[YAML] syntax.

This is equivalent to:

{% include side-by-side.html demo="buttons-code-list-equivalent" %}

You can mix choices that are specified manually with choices that are
specified with code:

{% include side-by-side.html demo="buttons-code-list-partial" %}

As explained [below](#image button), you can also use code to
[decorate the buttons with images](#image button).

### <a name="boolean buttons"></a>True/False buttons

You can use `buttons` as an alternative to [`yesno`] where you want
different text in the labels.

{% include side-by-side.html demo="yesno-custom" %}

## <a name="field with choices"></a>Multiple choice list

To provide a multiple choice question with "radio buttons" and a
"Continue" button, use `field` with a `choices` list:

{% include side-by-side.html demo="choices" %}

You can specify a default value using `default`:

{% include side-by-side.html demo="choices-with-default" %}

Another way to set a default is by adding `default: True` to the
choice that you want to be the default.

{% include side-by-side.html demo="choices-with-default-item" %}

You can also provide help text for a radio button using `help`:

{% include side-by-side.html demo="choices-with-help" %}

These customizations can also be specified when building a list of
choices using code:

{% include side-by-side.html demo="choices-from-code" %}

## <a name="field with dropdown"></a>Multiple choice dropdown

To provide a multiple choice question with a dropdown selector, use
`field` with a `dropdown` list:

{% include side-by-side.html demo="choices-dropdown" %}

## <a name="field with combobox"></a>Multiple choice combobox

To provide a multiple choice question with a "combobox" selector, use
`field` with a `combobox` list:

{% include side-by-side.html demo="choices-combobox" %}

The "combobox" selector allows users to choose a selection from a list
or enter a value of their own.

## <a name="image button"></a>Adding images to buttons and list items

To add a decorative icon to a `buttons` choice, use a key/value pair
and add `image` as an additional key.

{% include side-by-side.html demo="buttons-icons" %}

This works with `choices` as well:

{% include side-by-side.html demo="choices-icons" %}

It is not possible to decorate `dropdown` or `combobox` choices with
images.

In these examples, `calendar` and `map` are the names of decorations
that are defined in an [`images`] or [`image sets`] block.

If you create the list of choices with [`code`](#code generated
buttons), you can specify an image by including an additional
key/value pair within an item, where the key is `image`.

{% include side-by-side.html demo="buttons-icons-code" %}

There is an additional feature available when you assemble buttons
with [`code`](#code generated buttons): you can use [`DAFile`] or
[`DAFileList`] objects to indicate the image.  This example uses an
uploaded image file as the source of the image for one of the buttons:

{% include side-by-side.html demo="buttons-icons-code-upload" %}

## <a name="code button"></a>Embedding [`question`] and [`code`] blocks within multiple choice questions

Multiple choice questions can embed [`question`] blocks and [`code`]
blocks.  These questions are just like ordinary questions, except they
can only be asked by way of the questions in which they are embedded.

You embed a question by providing a [YAML] key-value list (a
dictionary) (as opposed to text) as the value of a label in a
`buttons`, `choices`, or `dropdown` list.

{% include side-by-side.html demo="buttons-code-color" %}

While embedding [`question`] blocks can be useful sometimes, it is
generally not a good idea to structure interviews with a lot of
embedded questions.  You will have more flexibility if your questions
stand on their own.

It is also possible for multiple-choice questions to embed [`code`]
blocks that execute [Python] code.  (If you do not know what [`code`]
blocks are yet, read the section on [code blocks] first.)  This can be
useful when you want to set the values of multiple variables with one
button.

{% include side-by-side.html demo="buttons-code" %}

The question above tells **docassemble** that if the [interview logic]
calls for either `car_model` or `car_make`, the question should be
tried.  When the user clicks on one of the buttons, the code will be
executed and the variables will be set.

To undo a user's choice on a [`question`] that embeds blocks, tag the
[`question`] with an [`id`] and call the [`forget_result_of()`]
function with the ID.

# <a name="field"></a>A simple "continue" button that sets a variable

{% include side-by-side.html demo="continue-participation" %}

A [`question`] with a `field` and no `buttons` will offer the user a
"Continue" button.  When the user presses "Continue," the variable
indicated by `field` will be set to `True`.

# <a name="fields"></a>Setting multiple variables with one screen

`fields` is used to present the user with a list of fields.

{% include side-by-side.html demo="text-field-example" %}

The `fields` must consist of a list in which each list item consists
of one or more key/value pairs.  One of these keys
([typically](#label)) is the label the user sees, where the value
associated with the key is the name of the variable that will store
the user-provided information for that field.  The other key/value
pairs in the item (if any) allow you to modify how the field is
displayed to the user.

These field modifiers are distinguished from label/variable pairs
based on the key; if the key is uses one of the names listed below, it
will be treated as a field modifier; if it is anything else, it will
be treated as a label.

# <a name="data types"></a><a name="input types"></a>Data types and input types in [`fields`]

Within a [`fields`] question, there are many possible [`datatype`]
values, which affect what the user sees and how the input is stored in
a variable.

The possible values of [`datatype`] are:

* [`area`](#area)
* [`user`](#camera)
* [`camera`](#camera)
* [`environment`](#camera)
* [`camcorder`](#camera)
* [`checkboxes`](#fields checkboxes)
* [`currency`](#currency)
* [`date`](#date)
* [`datetime`](#datetime)
* [`email`](#email)
* [`file`](#file)
* [`files`](#files)
* [`integer`](#integer)
* [`microphone`](#microphone)
* [`ml`](#ml)
* [`mlarea`](#mlarea)
* [`noyes`](#fields noyes)
* [`noyesmaybe`](#fields noyesmaybe)
* [`noyesradio`](#fields noyesradio)
* [`noyeswide`](#fields noyeswide)
* [`number`](#number)
* [`object`](#object)
* [`object_checkboxes`](#object_checkboxes)
* [`password`](#password)
* [`range`](#range)
* [`text`](#text) (the default)
* [`time`](#time)
* [`yesno`](#fields yesno)
* [`yesnomaybe`](#fields yesnomaybe)
* [`yesnoradio`](#fields yesnoradio)
* [`yesnowide`](#fields yesno)

In most cases, [`datatype`] controls both the user interface and the
format in which the data is stored.  But for certain multiple choice
questions, you can use [`datatype`] to indicate how you want the data
stored, and use [`input type`] to indicate the type of user interface
to use. The possible values of [`input type`] are:

* [`dropdown`](#select) (the default)
* [`radio`](#radio)
* [`combobox`](#combobox)

The following subsections describe the available [`datatype`]s and
[`input type`]s that you can assign to a field within [`fields`].

## <a name="plaintext"></a>Plain text

<a name="text"></a>A `datatype: text` provides a single-line text
input box.  This is the default `datatype`, so you never need to
specify it unless you want to.

{% include side-by-side.html demo="text-field" %}

<a name="area"></a>`datatype: area` provides a multi-line text area.

{% include side-by-side.html demo="text-box-field" %}

## <a name="password"></a>Passwords

<a name="password"></a>`datatype: password` provides an input box
suitable for passwords.

{% include side-by-side.html demo="password-field" %}

## <a name="date"></a>Dates

`datatype: date` provides a date entry input box.  The style of the
input box depends on the browser.

{% include side-by-side.html demo="date-field" %}

Validation is applied to ensure that the date can be parsed by
[`dateutil.parser.parse`].

The variable resulting from `datatype: date` is a special [Python]
object of the class [`DADateTime`], which is a subclass of the
standard [Python] class [`datetime.datetime`].  So if the name of the
date variable is `date_of_filing`, then you can do things like:

{% include side-by-side.html demo="date-demo" %}

Note that the field on the screen only asks for a date, but
[`DADateTime`] represents both a date and a time.  The time portion of
the [`DADateTime`] object will be set to midnight of the date.  If you
want a [`DADateTime`] with a time other than midnight, you can use the
[`.replace_time()`] or [`.replace()`] methods of [`DADateTime`] to
generate a new object with the same date but a different time.

For more information about working with date variables, see
the documentation for the [date functions].  These functions are
generally very flexible about formats, so you can pass a string like
`'12/25/2018'` or a date object, and the function will produce the
correct result either way.

In particular, if you want to format a date variable for inclusion in
a document or a question, you will probably want to use the
[`.format_date()`] method or the [`format_date()`] function.

If you set a [`default`] value for a date field, write the date in the
format YYYY-MM-DD.  Many browsers have built-in "date pickers" that
expect dates to be in this format.  See [Mozilla's documentation] of
the date input field.  If the browser uses a date picker, then your
interview will see text values in the form YYYY-MM-DD, but on other
browsers, like [Firefox], the format may be some other format.

## <a name="time"></a>Times

`datatype: time` provides an input box for times.  The style of the
input box depends on the browser.

Validation is applied to ensure that the time can be parsed by
[`dateutil.parser.parse`].

{% include side-by-side.html demo="time-field" %}

The resulting variable will be an object of type [`datetime.time`].

If you want to format a time variable for inclusion in a document or a
question, see the [`.strftime()`] method or the [`format_time()`]
function.

If you want to gather both a date and a time from a user, and combine
the values together into a single [`DADateTime`] object, you can do so
with the [`.replace_time()`] method.  For example:

{% include side-by-side.html demo="date-and-time-fields" %}

If you want to format a date and time for inclusion in a document or a
question, see the [`.format_datetime()`] method or the
[`format_datetime()`] function.

## <a name="datetime"></a>Combined dates and times

`datatype: datetime` provides an input box for dates and times
together in one field.  The style of the input box depends on the
browser.  Note: not all browsers have a "widget" for combined date and
times, and users might be confused if they are presented with a plain
text box.  For this reason, use of `datatype: datetime` is not
recommended until browser support for the
[`datetime-local`](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/datetime-local)
becomes more widespread.

Validation is applied to ensure that the time can be parsed by
[`dateutil.parser.parse`].

{% include side-by-side.html demo="datetime-field" %}

The resulting variable will be an object of type [`DADateTime`].  The
object can be formatted using the [`.format_datetime()`] method or the
[`format_datetime()`] function.

## <a name="email"></a>E-mail addresses

`datatype: email` provides an e-mail address input box.

{% include side-by-side.html demo="email-field" %}

## <a name="numbers"></a>Numbers

<a name="integer"></a>`datatype: integer` indicates that the input
should be a valid whole number.

<a name="number"></a>`datatype: number` indicates that the input
should be a valid numeric value.

{% include side-by-side.html demo="number-field" %}

You can use the optional field modifier `step` to limit the number to a
certain number of decimal places and to control the way the browser
widget controls work:

{% include side-by-side.html demo="number-field-step" %}

## <a name="currency"></a>Currency

`datatype: currency` indicates that the input should be a valid
numeric value.  In addition, the input box shows a currency symbol
based on locale defined in the [configuration].

{% include side-by-side.html demo="money-field" %}

The variable will be set to a number, just as if `datatype: number`
was used.  For information about how to display currency values, see
the [`currency()`] function.

## <a name="range"></a>Sliders

`datatype: range` shows a slider that the user can use to select a
number within a given range.  The range must be supplied by providing
`min` and `max` values.  An option `step` value can also be provided,
the default of which is 1.

{% include side-by-side.html demo="range" %}

You can also include an optional `scale`, which you can set to
`logarithmic`.

{% include side-by-side.html demo="range-log" %}

## <a name="file"></a><a name="files"></a>File uploads

Using the `file` or `files` datatypes within a [`fields`] list, you can
allow users to upload one or more files.

`datatype: file` indicates that the user can upload a single file.
The variable is set to a [`DAFileList`] object containing the
necessary information about the uploaded file.

{% include side-by-side.html demo="upload" %}

`datatype: files` indicates that the user can upload one or more
files.  The variable is set to a [`DAFileList`] object containing the
necessary information about the uploaded files.

{% include side-by-side.html demo="upload-multiple" %}

<a name="maximum image size"></a>If your users upload digital photos
into your interviews, the uploads may take a long time.  You can
configure an upload field so that images are reduced in size before
they are uploaded by modifying your field definition with a 
`maximum image size`.  The image will be reduced in size so that is 
no taller than or wider than the number of pixels designated by 
`maximum image size`.

In this example, images will be reduced in size to no more than 100
pixels in height or width:

{% include side-by-side.html demo="upload-max-image-size" %}

Note that the image file type of the uploaded file may be changed to
[PNG] during the conversion process.  Different browsers behave
differently.

If you have a lot of document upload fields, you can set a default 
`maximum image size` on an interview-wide basis with the
[`maximum image size` interview feature] and on a site-wide basis with
the [`maximum image size` configuration directive].  If you have a
default set up, but you want to override it for a particular field,
you can set the `maximum image size` field modifier to `None`.

There are a few other data types that result in file uploads:

<a name="camera"></a>`datatype: camera` is just like `file`, except
with an [HTML5] input type that suggests using the device's camera to take a
picture.  On many devices, this is no different from `datatype: file`.

<a name="user"></a>`datatype: user` is just like `camera`, except with
an [HTML5] input type that suggests using the device's front
(user-facing) camera.

<a name="environment"></a>`datatype: environment` is just like
`camera`, except with an [HTML5] input type that suggests using the
device's rear (environment-facing) camera.

<a name="camcorder"></a>`datatype: camcorder` is just like `camera`,
except for recording a video.

<a name="microphone"></a>`datatype: microphone` is just like `camera`,
except for recording an audio clip.

Whether these special data types do anything different from the `file`
data type is dependent on the web browser.  Mobile browsers are the
most likely to respond to these features.

For more information about uploading files, and for instructions on
uploading signature images, see the [Uploads](#uploads) subsection.

## <a name="fields yesno"></a><a name="fields noyes"></a>Yes/no fields

`datatype: yesno` will show a checkbox with a label, aligned with
labeled fields.  `datatype: noyes` is like `datatype: yesno`, except
with True and False inverted.

{% include side-by-side.html demo="fields-yesno" %}

<a name="fields yesnowide"></a><a name="fields
noyeswide"></a>`datatype: yesnowide` will show a checkbox with a label
that fills the full width of area.  `datatype: noyeswide` is like
`datatype: yesnowide`, except with True and False inverted.

{% include side-by-side.html demo="fields-yesnowide" %}

<a name="uncheck others"></a>Sometimes, when you are using a series of
these checkboxes, you might want to have a "none of the above"
selection.  To do this, add a field for the selection, and associate
it with a variable.  (Your interview does not need to use the
variable.)  Then modify the field with `uncheck others: True`.

{% include side-by-side.html demo="fields-yesno-uncheck-others" %}

This will cause the field to act as a "none of the above" field for
all the other yes/no checkbox fields on the page.  If you want the
field to only relate to specific other fields, use a list of the
variable names of those fields instead of `True`.

{% include side-by-side.html demo="fields-yesno-uncheck-others-list" %}

<a name="fields yesnoradio"></a>`datatype: yesnoradio` will show radio
buttons offering choices "Yes" and "No."

<a name="fields noyesradio"></a>`datatype: noyesradio` is like
`datatype: yesnoradio`, except with True and False inverted.

{% include side-by-side.html demo="fields-yesnoradio" %}

<a name="fields yesnomaybe"></a>`datatype: yesnomaybe` will show radio
buttons offering choices "Yes," "No," and "I don't know."

{% include side-by-side.html demo="fields-yesnomaybe" %}

<a name="fields noyesmaybe"></a>`datatype: noyesmaybe` is like
`datatype: yesnomaybe`, except with True and False inverted.

{% include side-by-side.html demo="fields-noyesmaybe" %}

## <a name="fields checkboxes"></a>Checkboxes

`datatype: checkboxes` will show the [`choices`](#choices) list as
checkboxes.  The variable will be a [`DADict`] (a type of [dictionary]
specific to **docassemble**) with items set to `True` or `False`
depending on whether the option was checked.  No validation is done to
see if the user selected at least one, regardless of the value of
`required`.

{% include side-by-side.html demo="fields-checkboxes" %}

As you can see in this example, the keys of the resulting dictionary
are the names of fruit, the values that are checked are `True`, and
the values that were not checked are `False`.

In the example above, the keys of the dictionary are the same as the
labels displayed to the user.  If you want labels to be different
from the keys, you can specify the choices in the following manner:

{% include side-by-side.html demo="fields-checkboxes-different-labels" %}

You can generate checkbox choices with code:

{% include side-by-side.html demo="fields-checkboxes-code" %}

The [`all_true()`], [`all_false()`], [`any_true()`] and [`any_false()`]
methods can be used to analyze the values set by a checkboxes field.

### <a name="fields checkboxes defaults"></a>Default values for checkboxes

To set default values in a checkbox list, you have a few options.

If you want to select just one option, just indicate the name of the
option:

{% include side-by-side.html demo="fields-checkboxes-default-0" %}

If you want to select multiple options, indicate a [YAML] list:

{% include side-by-side.html demo="fields-checkboxes-default-1" %}

You can also indicate your defaults in the form of a [YAML] dictionary:

{% include side-by-side.html demo="fields-checkboxes-default-2" %}

You can also use [Python] code to generate the defaults:

{% include side-by-side.html demo="fields-checkboxes-default-3" %}

Your [Python] code can also return a [dictionary]:

{% include side-by-side.html demo="fields-checkboxes-default-4" %}

If you generate the checkbox options with `code`, you can include
defaults directly within your code when you use a [list] of
[dictionaries]<span></span>:

{% include side-by-side.html demo="fields-checkboxes-default-5" %}

This also works if your code returns a [list] of [list]s:

{% include side-by-side.html demo="fields-checkboxes-default-6" %}

## <a name="select"></a>Multiple-choice dropdown

If you provide a list of [`choices`](#choices) or some
choice-generating [`code`](#code) for a field within a list of
[`fields`], the user will see a dropdown.  The variable will be set to
the value of the selected choice.

{% include side-by-side.html demo="fields-choices-dropdown" %}

You can also include `input type: dropdown`:

{% include side-by-side.html demo="fields-choices-dropdown-input-type" %}

The `input type: dropdown` does not actually have any effect, since
`dropdown` is the default `input type`.  (The other options for `input
type` are [`radio`](#radio) and [`combobox`](#combobox).)

The [`code`](#code) option, which uses [Python] code to generate the
list of choices, is often used in combination with
[`exclude`](#exclude), which excludes one or more items from the list
of choices.

## <a name="combobox"></a>Multiple-choice combobox

`input type: combobox` shows a [`choices`](#choices) list as a
[combobox] instead of as a dropdown [select] element (which is
[the default](#select)).

{% include side-by-side.html demo="fields-choices-combobox" %}

The "combobox" selector allows users to choose a selection from a list
or enter a value of their own.

## <a name="radio"></a>Radio buttons

`input type: radio` shows a [`choices`](#choices) list as a list of
radio buttons instead of as a dropdown [select] element (which is
[the default](#select)).  The variable will be set to the value of the
selected choice.

{% include side-by-side.html demo="radio-list" %}

## <a name="object"></a>Multiple-choice with objects

`datatype: object` is used when you would like to use a variable to
refer to an existing object.  You need to include
[`choices`](#choices), which can be a list of objects.

{% include side-by-side.html demo="object" %}

If [`choices`](#choices) refers to a variable that is a list of
things, the list will be unpacked and used as the list of items from
which the user can select.  [Python] code can be used here.

{% include side-by-side.html demo="object-selections" %}

By using `datatype: object` in combination with [`disable others`],
you can create questions that either set the attributes of an object
or set the object equal to another object.

{% include demo-side-by-side.html demo="someone-already-mentioned" %}

In this example, if the gardener and the cook are the same person, the
interview effectively does the following in [Python]:

{% highlight python %}
gardener = cook
{% endhighlight %}

Please note that `datatype: object` cannot be used with
[the `generic object` modifier](#generic) if the variable being set is
`x`.

<a name="object_radio"></a>`datatype: object_radio` is like `datatype:
object`, except the user interface uses radio buttons rather than a
pull-down list.

{% include side-by-side.html demo="object-radio" %}

For a fuller discussion on using multiple-choice object selectors, see
the [section on selecting objects](#objects), below.

<a name="object_checkboxes"></a>`datatype: object_checkboxes` is used
when you would like to use a question to set the elements of an object
of type [`DAList`] (or a subtype thereof).  The choices in
[`choices`](#choices) (optionally modified by [`exclude`]) will be
presented to the user as checkboxes.  The `.gathered` attribute of the
variable will be set to `True` after the elements are set.  See
[groups] for more information.

{% include side-by-side.html demo="object-checkboxes-dalist" %}

You can also use `datatype: object_checkboxes` on variables that
already exist in your interview.  You would need to do this if you
wanted the variable to be a subtype of [`DAList`].  If you use a
variable name that already exists, note that the `question` will only
be used when the `.gathered` attribute is needed.  To avoid questions
asking for `.there_are_any` and `.there_is_another`, set
`.auto_gather` to `False`.  For example:

{% include side-by-side.html demo="object-checkboxes-dalist" %}

Another advantage of using an already-existing variable is that the
choices in the question will default to the current elements in the
list.  In this example, we use the [`.append()`] method to initialize
the list of villains.

{% include side-by-side.html demo="object-checkboxes-default" %}

## <a name="ml"></a><a name="mlarea"></a>Machine learning

From the user's perspective, `datatype: ml` works just like `datatype:
text` (which is the default if no `datatype` is indicated), and
`datatype: mlarea` works just like `datatype: area`.

From the interview developer's perspective, however, the variable that is
set is not a piece of text, but an object representing a
classification of the user's input, based on a machine learning model
that is "trained" to classify user input.

{% include demo-side-by-side.html demo="predict-happy-sad" %}

For more information about how to use machine learning variables, see
the [machine learning section].

# <a name="fields options"></a>Options for [`fields`] items

The following are the keys that have special meaning within a list
item under [`fields`].

## <a name="datatype"></a>`datatype`

`datatype` affects how the data will be collected, validated and
stored.  For a full explanation of how this is used, see [above](#data
types).

## <a name="inputtype"></a>`input type`

The `input type` is similar to `datatype`.  It is used in situations
where the `datatype` might be [`date`], [`number`], etc., but you want
the field to use a particular type of multiple-choice input element,
such as a list of [radio buttons](#radio) or [a combobox](#combobox).
For a full explanation of how this is used, see [above](#input types).

## <a name="required"></a>`required`

`required` affects whether the field will be optional or required.  If
a field is required, it will be marked with a red asterisk, and input
validation will be enforced to make sure the user provides a value.

If the user skips a non-required field, the variable will be blank for
text-based fields and `None` for multiple-choice and yes/no fields.

Some `datatype`s are never marked with a red asterisk.  For example,
[`range`](#range) and [`yesno`](#fields yesno) fields are set to real
values by default, so the user cannot actuall skip the question.

The value of `required` can be `True` or `False`.  By default, all
fields are required, so you never need to write `required: True`
unless you want to.

{% include side-by-side.html demo="optional-field" %}

Instead of writing `True` or `False`, you can write [Python] code.
This code will be evaluated for whether it turns out to be true or
false.  For example, instead of `True` or `False`, you could use the
name of a variable that is defined by a [`yesno`] question (as long as
that variable was defined before the screen loads; the red asterisk
cannot be toggled in real time within the browser).

{% include side-by-side.html demo="required-code" %}

## <a name="hint"></a>`hint`

You can guide users as to how they should fill out a text field by
showing greyed-out text in a text box that disappears when the user
starts typing in the information.  In HTML, this text is known as the
[placeholder].  You can set this text for a text field by setting
`hint`.  You can use [Mako] templates within `hint`s.

{% include side-by-side.html demo="text-hint" %}

The `hint` is also used to provide the default text the user sees when
they fill out a [multiple-choice dropdown] or a [`combobox`] input
element within a [`fields`] question.

## <a name="help"></a>`help`

You can provide contextual help to the user regarding the meaning of a
field using the `help` field modifier.  The label will be green to
indicate that it can be clicked on, and the value of `help` will
appear on the screen when the user clicks the green text.  You can use
[Mako] templates within `help` text.

{% include side-by-side.html demo="text-help" %}

## <a name="default"></a>`default`

You can provide a default value to a field using `default`.  You can
use [Mako] templates in `default` text.

{% include side-by-side.html demo="text-default" %}

## <a name="choices"></a>`choices`

The `choices` field modifier is used with multiple-choice fields.  It
must refer to a list of possible options.  Can be a list of key/value
pairs (key is what the variable will be set to; value is the label
seen by the user) or a list of plain text items (in which case the
label and the variable value are the same).

{% include side-by-side.html demo="fields-choices" %}

When the [`datatype`] is [`object`], [`object_radio`], or
[`object_checkboxes`], `choices` indicates a list of objects from
which the user will choose.  For more information about using objects
in multiple choice questions, see the
[section on selecting objects](#objects), below.

## <a name="code"></a>`code`

If you have a multiple-choice question and you want to reuse the same
selections several times, you do not need to type in the whole list
every time.  You can define a variable to contain the list and a
[`code`] block that defines the variable.

Adding `code` to a field makes it a multiple-choice question.  The
`code` itself refers to [Python] code that generates a list of
possible options for a multiple choice field.

{% include side-by-side.html demo="fields-mc" %}

The [Python] code runs at the time the question is asked.  Therefore,
you can use the `code` feature to create multiple-choice questions
that have dynamically-created lists of choices.

The [Python] code needs to be a single expression.  The result of the
expression can take several forms.

It can be a [list] of single-item [dictionaries], as in the example above.

It can be a [dictionary] (in which case you cannot control the order
of items):

{% include side-by-side.html demo="fields-mc-2" %}

It can be a [list] of text items (in which case the values and labels will be
the same):

{% include side-by-side.html demo="fields-mc-3" %}

It can be a [list] of two-element [list]s:

{% include side-by-side.html demo="fields-mc-4" %}

You can specify a default by including a three-element list where the
third element is `True` if the choice should be selected by default.

{% include side-by-side.html demo="fields-mc-5" %}

You can include "help text" for a choice by including a fourth element
in one of the lists, where the element contains the help text you want
to be available.  The user can see the help text by touching the
question mark button.

{% include side-by-side.html demo="fields-mc-6" %}

If your code is a [list] of dictionaries, you can include a
`'default'` key in the dictionary indicating a true or false value
that represents whether the choice should be selected by default.

{% include side-by-side.html demo="fields-mc-7" %}

Similarly, you can include help text in a [list] of dictionaries by
including a `'help'` key in the dictionary indicating the help text
that should be available to the user.

{% include side-by-side.html demo="fields-mc-8" %}

## <a name="exclude"></a>`exclude`

If you build the list of choices with `code`, you can exclude items
from the list using `exclude`, where the value of `exclude` is
[Python] code.

{% include side-by-side.html demo="fields-mc-exclude" %}

In this example, the value of `exclude` is a single variable.  If
given a list of things, it will exclude any items that are in the list.

## <a name="none of the above"></a>`none of the above`

If you use [`datatype: checkboxes`](#fields checkboxes), then by
default a "None of the above" choice is added.

{% include side-by-side.html demo="fields-checkboxes-nota" %}

You can turn off the "None of the above" choice by setting the 
`none of the above` option to `False`.

{% include side-by-side.html demo="fields-checkboxes-nota-false" %}

You can also change the phrase from "None of the above" to something
else, even a [Mako] expression.  Just set `none of the above` to the
text you want to be displayed.

{% include side-by-side.html demo="fields-mc-nota" %}

## <a name="shuffle"></a>`shuffle`

`shuffle` can be used on multiple-choice fields (defined with
[`code`](#code) or [`choices`](#choices)).  When `True`, it randomizes
the order of the list of choices; the default is not to "shuffle" the
list.

{% include side-by-side.html demo="shuffle" %}

## <a name="show if"></a>`show if`

You can use the `show if` field modifier if you want the field to be
hidden under certain conditions.  There are three methods of using
`show if`, which have different syntax.

Using the first method, the field will appear or disappear in the web
browser depending on the value of another field in the [`fields`] list.
Under this method, `show if` refers to a [YAML] dictionary with two
keys: `variable` and `is`, where `variable` refers to the variable
name of the other field, and `is` refers to the value of the other
field that will cause this field to be shown.

This can be useful when you have a multiple-choice field that has an
"other" option, where you want to capture a text field but only if the
user selects the "other" option.

{% include side-by-side.html demo="other" %}

The second method is like the first, but is for the special case where
the other field in [`fields`] is a yes/no variable.  Under this method,
`show if` refers to the other field's variable name.  If that variable
is true, the field will be shown, and if it is not true, the field
will be hidden.

{% include side-by-side.html demo="showif-boolean" %}

If `show if` refers to a variable that is itself hidden by a `show
if`, then the condition is considered to be false.

{% include side-by-side.html demo="showif-nested" %}

Under the third method, the field is either shown or not shown on the
screen when it loads, and it stays that way.  You can use [Python]
code to control whether the field is shown or not.  Unlike
the first method, you are not limited to using variables that are part
of the [`fields`] list; you can use any [Python] code; however, you
cannot refer to any of the variables that are defined by the current
question.  Under this method, `show if` must refer to a [YAML]
dictionary with one key, `code`, where `code` contains [Python] code.
The code will be evaluated and if it evaluates to a positive value,
the field will be shown.

{% include side-by-side.html demo="showif" %}

With all of these methods, if any field is not visible on the screen
when the user presses the Continue button, no variable will be set to
anything for that field; it as if the field was never part of the
`question`.

## <a name="hide if"></a>`hide if`

This works just like [`show if`](#show if), except that it hides the
field instead of showing it.

{% include side-by-side.html demo="hideif-boolean" %}

## <a name="js show if"></a>`js show if`

Sometimes you might want to do more complicated evaluations with
on-screen variables than you can do with `show if` and `hide if`.
When you use the `show if` and `hide if` field modifiers to refer to
fields that are on the screen, you are able to test whether the fields
are true, or have particular values, but you cannot do anything more
complex, such as test whether the value is one of two values, or
the values of two fields.

The `js show if` and `js hide if` features allow you to use any
arbitrary [JavaScript] expression to determine whether a field should
be shown or not.  In these expressions, the special [JavaScript]
function [`val()`] is used to obtain the values of fields.  Given the
name of an on-screen field as a string, the [`val()`] function
returns the current value of that field.

{% include side-by-side.html demo="jsshowif" %}

The string that is passed to [`val()`] must perfectly match the
variable name that is used in the underlying [`question`].

The field will be shown or hidden whenever any of the variables
referenced with [`val()`] change.  Thus, if your [JavaScript]
expression does not use [`val()`], it will not be triggered except at
the time the screen loads.  Your expression is parsed, but is not
evaluated, when determining what fields your expression references
with [`val()`].  Thus, if you pass something other than a literal
string to [`val()`], you may find that the showing or hiding is not
triggered, even though [`val()`] would return the appropriate value.

## <a name="js hide if"></a>`js hide if`

This works just like [`js show if`](#js show if), except that it hides
the field instead of showing it.

## <a name="disable others"></a>`disable others`

If `disable others` is set to `True`, then when the user changes the
value of the field to something, all the other fields in the question
will be disabled.

{% include side-by-side.html demo="disable-others" %}

Alternatively, `disable others` can be set to a list of variables on
the same screen that should be disabled.

{% include side-by-side.html demo="disable-others-list" %}

## <a name="note"></a>`note`

The value of `note` is [Markdown] text that will appear on the screen.
This is useful for providing guidance to the user on how to enter
information.

If the `note` is by itself as its own "field" in the list of `fields`,
the text appears along with the other fields:

{% include side-by-side.html demo="note" %}

However, if the `note` is used as a field modifier, the note will
appear to the right of field on wide screens.  On small screens, the
note will appear after the field:

{% include side-by-side.html demo="side-note" %}

On wide screens, the location of each `note`s is based on the location
of the field itself.  This means that if you have `note`s on two
adjacent fields, and one of the `note`s is lengthy, the `note`s could
overlap on the screen.  Therefore, make sure to keep your notes short.

## <a name="html"></a>`html`

`html` is like [`note`](#note), except the format is expected to be
raw [HTML].  It can be used in combination with the [`css`] and
[`script`] question modifiers.

If `html` is by itself as its own "field" in the list of `fields`, the
HTML will appear along with the other fields:

{% include side-by-side.html demo="html" %}

However, if the `html` is used as a modifier for a field, the HTML
will appear to the right of field on wide screens.  On small screens,
the HTML will appear after the field:

{% include side-by-side.html demo="side-html" %}

## <a name="no label"></a>`no label`

If you use `no label` as the label for your variable, the label will
be omitted.  On wide screens, the field will fill more of the width of
the screen if the label is set to `no label`.

{% include side-by-side.html demo="no-label-field" %}

To keep the width of the field normal, but have a blank label, use
`""` as the label.

{% include side-by-side.html demo="blank-label-field" %}

## <a name="label"></a>`label` and `field`

Instead of expressing your labels and variable names in the form of `-
Label: variable_name`, you can specify a label using the `label` key
and the variable name using the `field` key.

{% include side-by-side.html demo="label" %}

# <a name="misc features"><a>Other features of [`fields`]

## <a name="emptychoices"></a>When the list of choices is empty

If the list of choices for a multiple choice question is empty,
**docassemble** will try to deal with the situation gracefully.  If
there is only a single field listed under [`fields`], or the question is
a [standalone multiple choice question](#field with buttons), then the
variable that will be set by the user's selection will be set to
`None`, and the question (or the field, if there are other fields
listed under [`fields`]) will be skipped.

If the `datatype` is `checkboxes`, the variable will be set to an
empty [`DADict`] (a type of [dictionary] specific to **docassemble**).
If the `datatype` is `object_checkboxes`, the variable will be set to
an empty [`DAList`] (a type of [list] specific to **docassemble**).

## <a name="min"></a><a name="input validation"></a>Input validation

Some datatypes, such as numbers, dates, and e-mail addresses, have
validation features that prevent the user from moving to the next page
if the input value does not meet the requirements of the data type.
The [jQuery Validation Plugin](http://jqueryvalidation.org) is used.

For some field types, you can require additional input validation by
adding the following to the definition of a field:

* `min`: for `currency` and `number` data types, require a minimum
  value.  This is passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/min-method).
* <a name="max"></a>`max`: for `currency` and `number` data types,
  require a maximum value.  This is passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/max-method).

{% include side-by-side.html demo="min" %}

* <a name="minlength"></a>`minlength`: require a minimum number of
  characters in a textbox, number of checkboxes checked, etc.  This
  uses the [jQuery Validation
  Plugin](http://jqueryvalidation.org/minlength-method).
* <a name="maxlength"></a>`maxlength`: require a maximum number of
  characters in a textbox, number of checkboxes checked, etc.  This
  uses the [jQuery Validation
  Plugin](http://jqueryvalidation.org/maxlength-method).

{% include side-by-side.html demo="minlength" %}

<a name="validate"></a>You can also use [Python] code to validate an
input field.  To do so, add a `validate` field modifier that refers to
the name of a [function] that returns `True` (or something that
[Python] considers "true") if the value is valid, and `False` (or
something that [Python] considers "not true") if the value is invalid.

{% include demo-side-by-side.html demo="validation-test" %}

In this example, the function `is_multiple_of_four` is defined as
follows:

{% highlight python %}
def is_multiple_of_four(x):
    return x/4 == int(x/4)
{% endhighlight %}

This [Python] code is in the [`validationfuncs.py`] file.  The
[`modules`] block includes this code.  The function returns `True` if 4
divides the input value into a whole number

The error message that the user will see is a generic error message,
"Please enter a valid value."  In most cases you will want to explain
to the user why the input did not validate.  To provide a more
descriptive error message, your function can call the
[`validation_error()`] function with the error message the user should
see.

{% include demo-side-by-side.html demo="validation-test-two" %}

In this example, the function `is_multiple_of_four` is defined as
follows:

{% highlight python %}
from docassemble.base.util import *

def is_multiple_of_four(x):
    if x/4 != int(x/4):
        validation_error("The number must be a multiple of four")
    return True
{% endhighlight %}

This [Python] code is in the [`validationfuncstwo.py`] file.  If 4
does not divide the input value into a whole number, then
[`validation_error()`] is called.  The [`validation_error()`] function
[`raise`]s an exception, which means that code stops processing once
the [`validation_error()`] function is called.  That is, if
[`validation_error()`] is called, the `return True` statement will not
be executed.

The text passed to [`validation_error()`] is the text the user will
see if the value does not validate.  If 4 does divide the input value
by a whole number, the function returns `True`, which indicates that
the input is valid.

Note that the `validate` field modifier is not available for use with
fields having `datatype: checkboxes`.  (However, note that you can use
[`minlength`] and [`maxlength`] to require a certain number of
checkboxes to be checked when [`none of the above`] is disabled.)

A more general limitation of these validation functions is that they
can only test for characteristics inherent in the variable being
validated; they cannot compare the variable to other variables.

<a name="validation code"></a>You can get around this restriction
using `validation code`.

{% include demo-side-by-side.html demo="validation-code" %}

Note that the code under `validation code` is not within a function,
so it should not try to `return` any values.  If the code runs through
to the end, this indicates that the input for the question is valid.
If [`validation_error()`] is called, or an [exception is raised], the
input for the question is considered invalid.

If the input is invalid, the user will see a message at the top of the
screen containing the error message passed to [`validation_error()`],
or the error message for the error that was otherwise [`raise`]d.

## <a name="address autocomplete"></a>Address autocomplete

If you have defined a [`google maps api key`] in the [Configuration],
you can use the [Place Autocomplete] feature of the
[Google Places API] to help your users enter addresses.  Address
suggestions will be provided as the user begins to type.  To use this
feature, modify the street address (`.address`) field by setting
`address autocomplete` to `True`.

{% include side-by-side.html demo="address-autocomplete" %}

For more information on using this feature, see the documentation for
the [`Address`] object.

This feature can be used internationally with a variety of address
types.  Here is an example that illustrates all of the possible
attributes of the [`Address`] object that can be set by [Place Autocomplete].

{% include side-by-side.html demo="address-autocomplete-test" %}

## <a name="continue button field"></a>Setting a variable with the Continue button

When the user presses the Continue button on a `question` containing
[`fields`], all of the variables listed under [`fields`] are set.
Sometimes, it is useful for the `question` to also set a single
variable to `True`, much like the [simple "continue" button that sets
a variable](#field) question does.

If you want your [`fields`] question to set a variable to `True` when
the user presses "Continue," add a `continue button field` line to
the `question` indicating the variable that should be set to True.

{% include side-by-side.html demo="continue-button-field" %}

## <a name="objects"></a>Assigning existing objects to variables

Using [Mako] template expressions ([Python] code enclosed in `${ }`), you can
present users with multiple-choice questions for which choices are
based on information gathered from the user.  For example:

{% include side-by-side.html demo="object-try-1" %}

But what if you wanted to use a variable to refer to an object, such
as a person?  You could try something like this:

{% include side-by-side.html demo="object-try-2" %}

In this case, `tallest_person` would be set to the _name_ of the
`client` or the _name_ of the `advocate`.  But what if you wanted to
then look at the birthdate of the tallest person, or some other
attribute of the person?  If all you had was the person's name, you
would not be able to do that.  Instead, you would want
`tallest_person` to be defined as the object `client` or the object
`advocate`, so that you can refer to `tallest_person.birthdate` just
as you would refer to `client.birthdate`.

You can accomplish this by setting [`datatype`] to `object` within a
[`fields`] list, where the [`choices`](#choices) are the names of the
objects from which to choose.  (Optionally, you can set a `default`
value, which is also the name of a variable.)

For example:

{% include side-by-side.html demo="object-try-3" %}

Note that this interview incorporates the [`basic-questions.yml`] file
which defines objects that are commonly used in [legal applications],
including `client` and `advocate`.  It also contains questions for
asking for the names of these people.

The interview above presents the names of the `client` and the
`advocate` and asks which of these people is the villain.

If the user clicks the name of the advocate, then **docassemble** will
define the variable `villain` and set it equal to `advocate`.

Note that because `advocate` is an [object], `villain` will be an
_alias_ for `advocate`, not a _copy_ of `advocate`.  If you
subsequently set `advocate.birthdate`, you will immediately be able
retrieve that value by looking at `villain.birthdate`, and vice-versa.

Also because `villain` is an alias, if you refer to
`villain.favorite_food` and it is not yet defined, **docassemble**
will go searching for a question that offers to define
`advocate.favorite_food`.  This is because **docassemble** objects
have an intrinsic identity, a unique name given to them at the time
they are created.  (You can inspect this by referring to
`villain.instanceName` in a question and will see that it returns
`advocate`.)  For more information about this, see the discussion in
the documenation for [DAObject].  (All **docassemble** objects are
subtypes of [DAObject].)

If any of the objects listed under [`choices`](#choices) represent
lists of objects, such as `case.defendant` or `client.child` (objects
of type `PartyList`, those lists will be expanded and every item will
be included.  You can also include under `choices` [Python] code, such
as `case.parties()` or `case.all_known_people()`.

The [`datatype`] of `object` presents the list of choices as a
pull-down.  If you prefer to present the user with radio buttons, set
the [`datatype`] to `object_radio`.

<a name="object labeler"></a>By default, the objects listed in the
user interface are labeled by their textual representations.  For
example, if the object in a `choices` list is an [`Individual`], the
label for the object will be the textual representation for an
[`Individual`], which is the individual's name.  To use an alternate
label, provide a `object labeler`.  The `object labeler` must be a
Python expression that evaluates to a function.

For example:

{% highlight yaml %}
question: Who is the villain?
fields:
  - The villain is: villain
    datatype: object
    default: antagonist
    object labeler: |
      lambda y: y.nickname
    choices:
      - protagonist
      - antagonist
{% endhighlight %}

In this case, the `protagonist` and the `antagonist` will be labeled
using the `nickname` attribute.  The `object labeler` in this example
is a Python [lambda function], which is a shorthand way of creating a
function.  You could also used a named function, if you wrote one in a
module.  For example, suppose you had some code in a module that
defined the function `my_labeling_function`:

{% highlight python %}
def my_labeling_function(obj):
    return obj.nickname
{% endhighlight %}

Suppose also that you imported this function into your interview using
a [`modules`] block.  Then, in your `fields` item you could simply
write `object labeler: my_labeling_function`.

## <a name="embed"></a>Embedding fields within a paragraph

Within a [`fields`] question, you can include fill-in fields within
the text of the [`subquestion`] using markup of the form
`[FIELD variable_name]`.

{% include side-by-side.html demo="embed" %}

Any variable name referenced in `[FIELD ...]` must be one of the
variable names listed in the `fields:` list.  If a field is referenced
this way in the [`subquestion`], it will not be displayed the way that
fields are ordinarily displayed, but will be moved into the
[`subquestion`], where it will be formatted differently.  Any fields
in the `fields:` list that are not referenced in the [`subquestion`]
will appear on the screen in the normal fashion.

The label of an embedded field is used as the [tooltip] of the field.

<a name="inline width"></a>When you are using embedded fields, you can
add the field modifier `inline width` to change the initial width of
the field.  For example, if you include `inline width: 15em`, the
[CSS] will be altered so that the field is 15em wide.  This field
modifier has no effect when embedded fields are not being used.

## <a name="fields code"></a>Generating fields with code

You can use [Python] code to generate items inside a [`fields`].  To do
so, simply add an entry under [`fields`] that contains `code` (and
nothing more).  The contents of `code` will be evaluated as a [Python]
expression.

The expression must evaluate to a list of dictionaries, and the format
must be the Python equivalent of a regular [`fields`] item, which you
would normally express in [YAML].

For example, if you want the fields to be like this:

{% highlight yaml %}
question: |
  How many of each fruit?
fields:
  - Apples: num_apples
    datatype: integer
  - Oranges: num_oranges
    datatype: integer
{% endhighlight %}

you would write this:

{% highlight yaml %}
question: |
  How many of each fruit?
fields:
  - code: |
      [{'Apples': 'num_apples', 'datatype': 'integer'},
       {'Oranges': 'num_oranges', 'datatype': 'integer'}']
{% endhighlight %}

Here is an example that asks for the names of a number of people
on a single screen:

{% include side-by-side.html demo="fields-code" %}

Note that it is necessary to use the [`sets`] modifier on the question
to manually indicate that the question will define
`people[i].name.first`.  Normally, **docassemble** automatically
detects what variables a question is capable of defining, but when the
[`fields`] are dynamically generated with code, it is not able to do so.

Note also that this example uses the [`label` and `field`] method for
indicating the label and the variable name for each field.  This is
not required, but it may make field-generating code more readable.

Dynamically-created lists of fields can be paired with
dynamically-created `subquestion` text that [embeds] the fields.

{% include side-by-side.html demo="fields-code-embed" %}

It is also possible to mix dynamic fields with non-dynamic fields:

{% highlight yaml %}
question: |
  Tell me about your food preferences.
fields:
  - Favorite fruit: favorite_fruit
  - code: food_list
  - Favorite vegetable: favorite_vegetable
---
reconsider: True
code: |
  food_list = [{'Favorite candy': 'favorite_candy'}]
  if likes_legumes:
    food_list.append({'Favorite legume': 'favorite_legume'})
{% endhighlight %}

Writing [Python] code that generates a list of fields can be pretty
complex.  This should be considered an advanced feature.  Note that
the code above uses the [Python] function [`str()`] to reduce the
index of a list (which is an integer) into a string, for purposes of
constructing variable names like `people[0].name.first` and
`people[1].name.first`.

If you work with dictionaries ([`DADict`] objects) instead of lists
([`DAList`] objects), a useful function is the [Python] function
[`repr()`], which returns a string containing a string with quotation
marks around it.

For example, suppose you want to replicate this:

{% highlight yaml %}
question: |
  Tell me about the seeds.
fields:
  - label: Seeds of a kiwi
    field: fruit['kiwi'].seeds
  - label: Seeds of a tomato
    field: fruit['tomato'].seeds
{% endhighlight %}

You could do something like the following:

{% highlight yaml %}
question: |
  Tell me about the seeds.
fields:
  - code: field_list
---
code: |
  field_list = list()
  for key in fruit:
    field_list.append({"label": "Seeds of a " + key, 
                       "field": "fruit[" + repr(key) + "].seeds"})
{% endhighlight %}

The alternative is to try to provide the quotation marks manually,
which can look messier, and then you have to worry about what to do if
the `key` string contains an apostrophe; will that cause a syntax
error?  The [`repr()`] function takes care of this problem by
producing a robust [Python] representation of the string.

## <a name="bigexample"></a>A comprehensive example

Here is a lengthy example that illustrates many of the features of
[`fields`].

{% include side-by-side.html demo="fields" %}

# <a name="uploads"></a>Uploads

## <a name="uploading"></a>Storing files as variables

Users can upload files, and the files are stored as a variable in
**docassemble**.

{% include side-by-side.html demo="upload" %}

Note that this question uses [`fields`], which is explained in more
detail [above](#fields).  Specifically, it uses the [`file`](#file)
data type.

When set, the variable `user_picture` will be a special [object] of
type [`DAFileList`].  For more information about how to make use of
uploaded files, see [inserting images].

## <a name="signature"></a>Gathering the user's signature into a file variable

The `signature` block presents a special screen in which the user
can sign his or her name with the trackpad or other pointing device.

{% include side-by-side.html demo="signature" %}

On the screen, the [`question`] text appears first, then the
[`subquestion`] text, then the signature area appears, and then the
`under` text appears.

In this example, the `user_signature` variable will be set to an
object of type [`DAFile`].  This variable can be included in the same
way that a document upload can be included.  For example:

{% highlight yaml %}
---
question: |
  Is this your signature?
subquestion: |
  ${ user_signature }
yesno: user_signature_verified
---
{% endhighlight %}

or, if you want to control the width of the image:

{% highlight yaml %}
---
question: |
  Is this your signature?
subquestion: |
  ${ user_signature.show(width='1in') }
yesno: user_signature_verified
---
{% endhighlight %}

Signatures can be also be inserted into assembled [documents] in the
same way.  They can also be inserted into [DOCX fill-in forms] and
[PDF fill-in forms].

On a small screen, users need as much of the screen as possible to
write their signature.  For this reason, **docassemble** will reduce
the size of the navigation bar and put the [`question`] text into the
navigation bar.  For this reason, you should make sure your
[`question`] text is very brief -- no longer than "Sign your name."
You should also make the [`subquestion`] text as brief as possible.
Although you may be developing your app on a desktop or laptop
monitor, your users are probably using smartphones, so test your app
on a smartphone.

# <a name="general"></a>Generalizing questions

**docassemble** lets you write a single question that can be re-used
  throughout an interview.

For example, suppose you want to gather the following variables:

* `spouse.birthdate`
* `mother.birthdate`
* `father.birthdate`

or:

* `plaintiff[0].served`
* `plaintiff[1].served`
* `plaintiff[2].served`

It would be tedious to have to write separate questions for each of
these variables.

Luckily, there are two features in **docassemble** that allow you to
write questions (and other blocks that set a variable) in a
generalized way: the [`generic object`](#generic) modifier, and [index
variables](#index variables).

## <a name="generic"></a>The `generic object` modifier

The [`generic object` modifier] is explained more fully in the
[section on question modifiers], but here is an example:

{% include side-by-side.html demo="generic-object" %}

The special variable `x` stands in for any object of type
[`Individual`].

If you are not yet familiar with the concept of "[objects]," see the
[objects section].

The [`generic object` modifier] can be used with [`question`] blocks,
[`code`] blocks, and any other blocks that set variables
([`template`], [`table`], [`attachment`], and [`objects`], [`objects
from file`], [`data`], [`data from code`]).

## <a name="index variables"></a>Index variables

If you have an [object] that is a type or subtype of [`DAList`] or
[`DADict`], you can refer generically to any item within the object
using an index variable.

{% include side-by-side.html demo="index-variable" %}

<a name="i"></a>The special variable `i` will stand in for the index
of whichever list member your interview asks about.

You can nest iterators up to six levels, using the variables `i`,
`j`, `k`, `l`, `m`, and `n`, but you have to use them in this order.

{% include side-by-side.html demo="nested-veggies" %}

For more information about populating groups of things, see the
[groups section].

For more information about how **docassemble** identifies what
question to ask in order to define a given variable, see the 
[interview logic]({{ site.baseurl }}/docs/logic.html#variablesearching)
section.

Index variables can be used with [`question`] blocks, [`code`] blocks,
and any other blocks that set variables ([`template`], [`table`],
[`attachment`], and [`objects`], [`objects from file`], [`data`],
[`data from code`]).

## <a name="generic tips"></a>Tips on using generalized questions

If you use generic object variable `x`, or index variables like `i`,
`j`, `k`, etc., it is important that you do not use them in blocks
that you have marked as `mandatory`.

Suppose you have a block that defines `fruit[i].seeds`.  When
**docassemble** needs a specific value, like `fruit[2].seeds`, it will
find your block automatically, no matter where it is in the interview
source file.  **docassemble** will take care of setting `i = 2` before
"running" your block.  Your block will only work correctly if `i` is
set to the right value.

If you mark the block as `mandatory` in order to force it to be run,
you will be forcing the running of [Python] code in a context where
the value of `i` could be anything; it might be a number like `0` or
`5`, or it might be a string like `'income'`.  The variable `i` might
not even be defined at all.

Thus, you should only use `x`, `i`, `j`, `k`, etc. when you are
letting **docassemble** choose which block to use.

# <a name="specialscreens"></a>Special screens

## <a name="event"></a>Performing special actions requested by the user

You can allow users to click links or menu items that take the user to
a special screen that the user would not ordinarily encounter in the
course of the interview.  You can create such a screen using an
`event` specifier.

An `event` specifier acts just like [`sets`]: it advertises that the
question will potentially define a variable.

In the following example, the variable `show_date` is never defined;
it is simply sought.  The [`task_not_yet_performed()`] function is
used to make sure that the dialog box only appears once.

{% include side-by-side.html demo="dialog-box" %}

The `event` specifier is important if you use the [roles] feature to
conduct multi-user interviews.

{% include side-by-side.html demo="event-role-event" %}

In the example above, the `event` line tells **docassemble** that this
[`question`] should be displayed to the user if **docassemble**
encounters the `role_event`, which is a special "event" that can
happen in multi-user interviews.  The event is triggered when the
interview reaches a point when a person other than the current user
needs to answer a question.  For example, while a client is filling
out an interview, the [interview logic] might call for a variable that
can only be set by an advocate who reviews the client's answers.  In
this scenario, a `role_event` will be triggered.  When this happens,
**docassemble** will look for a [`question`] or [`code`] block that
defines the variable `role_event`, and it will find the example
question above.

`event` can also be used to create screens that the user can reach
from the menu or from hyperlinks embedded in question text.  For
information and examples, see [url_action()], [process_action()],
[action_menu_item()], and [menu_items].

## <a name="review"></a>Creating a special screen where the user can review his or her answers

The `review` specifier allows interview developers to create a
`review` screen.  A `review` screen is type of `question` that allows
users to review and edit their answers, whether the user is part of the
way through the interview or all the way through the interview.
Typically, the user will get to this screen by selecting an option
from the web app menu (e.g., "Review Answers"), or by clicking on a
hyperlink within `subquestion` text (e.g., "to review the answers you
have provided so far, click here").

Here is an example of a `review` screen that is launched from the
menu:

{% include side-by-side.html demo="review-1" %}

If you click "Favorite fruit," you are taken to a [`question`] where
you can edit the value of `fruit`.  This has the same effect as
calling [`force_ask()`] on `'fruit'` or running an [action] on
`'fruit'`; whatever block in your interview offers to define `fruit`
will be used.  After the user edits the value of the variable, the
user will return to the `review` screen again.

Note that the `review` screen does not show a link for "Favorite
fungus" because the variable `fungi` has not been defined yet.
However, once `fungi` is defined, the `review` screen would show it.

This behavior is different from the typical behavior of
**docassemble** blocks.  Normally, referring to a variable that has
not yet been defined will trigger the asking of a question that will
define that variable.  In the `review` screen, however, the presence of
an undefined variable simply causes the item to be omitted from the
display.

For more information about adding menu items, see the sections on
[special variables] and [functions].

In the above example, note that the `question` with the `review`
specifier is tagged with `event: review_answers`.  For more
information about how [`event`]s work, [see above](#event).  The
interview will show this screen whenever it seeks out the definition
of the variable `review_answers`.  Since the screen is displayed based
on an [`event`], it can be called as many times during the interview
session as the user likes.  Depending on which variables have been
defined, the user will see different things.

### <a name="review customization"></a>Customizing the display of `review` options

You can provide the user with a list of answers the user has provided
with buttons that the user can press to revisit an answer:

{% include side-by-side.html demo="review-2" %}

The `review` specifier, like the [`fields`] specifier, allows you
to use `note` and `html` entries.

If these are modified with the optional `show if` field modifier, they
will only be displayed if the variable referenced by the `show if`
field modifier has been defined.  In addition, if any of these entries
refer to a variable that has not been defined yet, they will be
omitted.

{% include side-by-side.html demo="review-3" %}

If you include `note` and `html` as modifiers of an item under the
`review` specifier, the text will appear to the right of the item on
wide screens.  On small screens, the HTML will appear after the item.

{% include side-by-side.html demo="review-side-note" %}

You can add `help` text to an item, in which case the text is shown
underneath the hyperlink.  If this text expects a variable to be
defined that has not actually been defined, the item will not be
shown.  Note: this is not available with the `button` display format.

{% include side-by-side.html demo="review-4" %}

By referring to a list of variables instead of a single variable, you
can indicate that more than one variable should be sought.  The fields
mentioned will not appear on the `review` screen until all have been
gathered.

{% include side-by-side.html demo="review-5" %}

If there is a follow-up question that might need to come after the
changing of a variable, you can list the follow-up variable in the
`fields` under `follow up`.

{% include side-by-side.html demo="review-conditional" %}

You will need to tag the follow-up question with an [`if`] modifier;
in order for the `review` screen to skip the field when it is not
required, it needs to find no [`question`]s that will define the
variable.  If the follow-up question is set up in this way, you can
list its variable under `follow up`, and **docassemble** will ask the
question if the `if` condition is true, but will ignore the `follow
up` variable if the `if` condition is false.

You can also indicate more than one variable when using `show if`:

{% include side-by-side.html demo="review-6" %}

Some of the variables that you use in your interview might be computed
by [`code`] based on answers to [`question`]s, rather than defined
directly by asking the user a question.  Thus, if the user changes the
answers to these underlying questions, you may want your interview to
recompute the values of these variables.  This recalculation does not
happen automatically; however, you can cause it to happen in your
`review` screen by including `recompute` in the list of variables to
be re-asked.

{% include side-by-side.html demo="review-7" %}

In this example, it would not have worked to merely include the
variable `salad` in the list of variables, as follows:

{% highlight yaml %}
  - Edit:
      - fruit
      - vegetable
      - salad
      - fungi
{% endhighlight %}

Here, the presence of `salad` in this list means "ask a [`question`]
to redefine the variable `salad`."  If there is no [`question`] that
defines `salad`, the interview will generate an error.  Including
`salad` in a `recompute` list, as in the above interview, indicates
that it is ok if the variable is defined by `code`.

You might also want to use `recompute` with variables that are defined
by [`code`] in some circumstances but are defined by [`question`]s in
other circumstances.

When you write lists of operations to be performed when a user clicks
a link on a `review` page, you will probably want to make sure that at
least one of the variables in the list will trigger the asking of a
[`question`].  Otherwise, the user might click the link and be
returned back to the same page again, and when that happens they may
assume that clicking the link didn't do anything, and the app is
broken.

There are two other special commands that you can use in a list of
variables in a `review` item: `set` and `undefine`.  The following
example illustrates `set`:

{% include side-by-side.html demo="review-8" %}

This interview demonstrates how to re-do the geolocation of an
[`Address`].  When you call [`.geolocate()`] on an [`Address`] the
first time, the address is geolocated and the `.geolocated` attribute
of the object is changed from `False` to `True`.  If you call
[`.geolocate()`] on the object again, the first thing it does is check
the `.geolocated` attribute, and if it is `True`, it will immediately
return without doing anything.  This is useful for avoiding
unnecessary API calls, which can slow down the responsiveness of your
app.  However, if the user edits the underlying attributes of the
address, you need to "reset" the geolocation in order to get it to run
again.

In the above interview, the `set` command sets `address.geolocated` to
`False`, which means that when the `address.county` is recomputed, and
the [`.geolocate()`] method is run again by the `code` block, then the
[`.geolocate()`] method will actually geolocate the new address.

### <a name="review field"></a>Placing a `review` screen within the interview logic

In the examples above, the `question` containing the `review`
specifier is identified with an `event` specifier like `event:
review_answers`, meaning that the variable `review_answers` does not
actually get defined, though it gets sought.

As a result, a `review` screen identified with an `event` can only be
shown when triggered by a user action (e.g., clicking a link,
selecting an item from the menu), or with [`code`].

If you would like to insert a `review` screen into the normal course
of an interview, so that it appears to the user one time, you can use
`field` instead of `event`.

{% include side-by-side.html demo="review-field" %}

In this example, the variable `answers_reviewed` actually gets
defined; it gets set to `True` when the user clicks "Continue."  It
works much like a [standard question with a "Continue" button that sets a
variable to `True`](#field).

The interview flow in this interview is set by the [`code`] block.
First the interview asks about the user's favorite fruit, vegetable,
and fungus.  Then the `review` screen is shown.  Then the final
screen is shown.

### <a name="skip undefined"></a>Ensuring variables are defined first

By default, when a `review` screen encounters and undefined variable,
it does not seek out its definition.  This is so you can have a single
`review` screen that is used throughout an interview (or a section of
an interview), where the user only sees that fields that have already
been asked about.

If you would like to use the functionality of a `review` screen, but
you want all the variables to be defined first, set `skip undefined`
to `False`:

{% highlight yaml %}
skip undefined: False
question: |
  Review your answers
review:
  ...
{% endhighlight %}

This enables you to use tables in your `review` screen.  Ordinarily,
tables are always undefined (so that their contents always reflect the
current state of the list, so a `review` screen would never display them.

### <a name="resume button label"></a>Customizing the Resume button

By default, the `review` screen puts a "Resume" button at the bottom of
the screen.  If you want the label on the button to be something other
than the word "Resume," add a `resume button label` modifier.

{% include side-by-side.html demo="resume-button-label" %}

However, if `review` is used with `field`, a "Continue" button is
used.  The "Continue" button can be customized using the modifier
[`continue button label`].

### <a name="review auto"></a>Why can't `review` screens be automatically generated?

The list of variables to display to the user in a `review` screen needs
to be specified by the interview developer.  There are several reasons
why this needs to be done manually as opposed to automatically:

1. Variables in your interview may be interdependent.  You do not
   necessarily want to allow the interviewee to edit any past answer
   at will because this may result in internal inconsistencies or
   violations of the logic of your interview.  For example, if your
   interview has a variable called `eligible_for_medicare`, which is
   set after the user answers a series of questions, you would not
   want the user to be able to go back and set his or her age to 30,
   at least not without a reconsideration of the definition of
   `eligible_for_medicare`.  Therefore, it is important that the
   interview developer control what the user can edit.
2. A list of answers already provided might not be user-friendly
   unless the interview developer presents it in a logically organized
   fashion.  The order in which the questions were asked is not
   necessarily the most logical way to present the information for
   editing.

[configuration]: {{ site.baseurl }}/docs/config.html
[select]: http://www.w3schools.com/tags/tag_select.asp
[placeholder]: http://www.w3schools.com/tags/att_input_placeholder.asp
[code blocks]: {{ site.baseurl }}/docs/code.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[YAML]: https://en.wikipedia.org/wiki/YAML
[object]: {{ site.baseurl }}/docs/objects.html
[objects]: {{ site.baseurl }}/docs/objects.html
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[Python identifiers]: https://docs.python.org/2/reference/lexical_analysis.html#identifiers
[reserved variable names]: {{ site.baseurl }}/docs/reserved.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[question]: {{ site.baseurl }}/docs/questions.html
[function]: {{ site.baseurl }}/docs/functions.html
[functions]: {{ site.baseurl }}/docs/functions.html
[special variables]: {{ site.baseurl }}/docs/special.html
[legal applications]: {{ site.baseurl }}/docs/legal.html
[interview logic]: {{ site.baseurl }}/docs/logic.html
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`code`]: {{ site.baseurl }}/docs/code.html#code
[DAObject]: {{ site.baseurl }}/docs/objects.html#DAObject
[url_action()]: {{ site.baseurl }}/docs/functions.html#url_action
[process_action()]: {{ site.baseurl }}/docs/functions.html#process_action
[action_menu_item()]: {{ site.baseurl }}/docs/functions.html#action_menu_item
[menu_items]: {{ site.baseurl }}/docs/special.html#menu_items
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`subquestion`]: {{ site.baseurl }}/docs/questions.html#subquestion
[`code`]: {{ site.baseurl }}/docs/code.html
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`DAFileList`]: {{ site.baseurl }}/docs/objects.html#DAFileList
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`need()`]: {{ site.baseurl }}/docs/functions.html#need
[`basic-questions.yml`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/data/questions/basic-questions.yml
[`validationfuncs.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/validationfuncs.py
[`validationfuncstwo.py`]: {{ site.github.repository_url }}/blob/master/docassemble_demo/docassemble/demo/validationfuncstwo.py
[`yesno`]: #yesno
[group]: {{ site.baseurl }}/docs/groups.html
[groups]: {{ site.baseurl }}/docs/groups.html
[groups section]: {{ site.baseurl }}/docs/groups.html
[Python constant]: https://docs.python.org/2/library/constants.html
[inserting images]: {{ site.baseurl }}/docs/markup.html#inserting uploaded images
[`fields`]: #fields
[Python dictionaries]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[HTML5]: https://en.wikipedia.org/wiki/HTML5
[`selections()` function]: {{ site.baseurl }}/docs/functions.html#selections
[`exclude`]: #exclude
[`event`]: #event
[`object`]: #object
[`object_radio`]: #object_radio
[`object_checkboxes`]: #object_checkboxes
[`datatype`]: #datatype
[roles]: {{ site.baseurl }}/docs/roles.html
[`task_not_yet_performed()`]: {{ site.baseurl }}/docs/functions.html#task_not_yet_performed
[`css`]: {{ site.baseurl }}/docs/modifiers.html#css
[`script`]: {{ site.baseurl }}/docs/modifiers.html#script
[tooltip]: http://www.w3schools.com/tags/att_title.asp
[list]: https://docs.python.org/2/tutorial/datastructures.html
[dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[dictionaries]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[DOCX fill-in forms]: {{ site.baseurl }}/docs/documents.html#signature docx
[PDF fill-in forms]: {{ site.baseurl }}/docs/documents.html#signature
[documents]: {{ site.baseurl }}/docs/markup.html#inserting uploaded images
[`generic object` modifier]: {{ site.baseurl }}/docs/modifiers.html#generic object
[section on question modifiers]: {{ site.baseurl }}/docs/modifiers.html#generic object
[objects section]: {{ site.baseurl }}/docs/objects.html
[`currency()`]: {{ site.baseurl }}/docs/functions.html#currency
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[date functions]: {{ site.baseurl }}/docs/functions.html#date functions
[machine learning section]: {{ site.baseurl }}/docs/ml.html#howtouse
[raise an exception]: https://en.wikibooks.org/wiki/Python_Programming/Exceptions
[exception is raised]: https://en.wikibooks.org/wiki/Python_Programming/Exceptions
[`Exception`]: https://docs.python.org/2/library/exceptions.html#exceptions.Exception
[`force_ask()`]: {{ site.baseurl }}/docs/functions.html#force_ask
[action]: {{ site.baseurl }}/docs/functions.html#actions
[HTML]: https://en.wikipedia.org/wiki/HTML
[`disable others`]: #disable others
[`.append()`]: {{ site.baseurl }}/docs/objects.html#DAList.append
[`default`]: #default
[Mozilla's documentation]: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input/date
[Firefox]: https://www.mozilla.org/en-US/firefox/
[`maximum image size` configuration directive]: {{ site.baseurl }}/docs/config.html#maximum image size
[`maximum image size` interview feature]: {{ site.baseurl }}/docs/initial.html#maximum image size
[combobox]: https://github.com/danielfarrell/bootstrap-combobox
[multiple-choice dropdown]: #select
[`combobox`]: #combobox
[`images`]: {{ site.baseurl }}/docs/initial.html#images
[`image sets`]: {{ site.baseurl }}/docs/initial.html#image sets
[`sets`]: {{ site.baseurl }}/docs/modifiers.html#sets
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[PNG]: https://en.wikipedia.org/wiki/Portable_Network_Graphics
[embeds]: #embed
[`label` and `field`]: #label
[`str()`]: https://docs.python.org/2/library/functions.html#str
[`repr()`]: https://docs.python.org/2/library/functions.html#repr
[`all_true()`]: {{ site.baseurl }}/docs/objects.html#DADict.all_true
[`all_false()`]: {{ site.baseurl }}/docs/objects.html#DADict.all_false
[`any_true()`]: {{ site.baseurl }}/docs/objects.html#DADict.any_true
[`any_false()`]: {{ site.baseurl }}/docs/objects.html#DADict.any_false
[`Address`]: {{ site.baseurl }}/docs/objects.html#address autocomplete
[`google maps api key`]: {{ site.baseurl }}/docs/config.html#google
[Place Autocomplete]: https://developers.google.com/places/web-service/autocomplete
[Google Places API]: https://developers.google.com/places/
[`datetime.datetime`]: https://docs.python.org/2/library/datetime.html#datetime-objects
[`datetime.time`]: https://docs.python.org/2/library/datetime.html#datetime.time
[`DADateTime`]: {{ site.baseurl }}/docs/objects.html#DADateTime
[`as_datetime()`]: {{ site.baseurl }}/docs/functions.html#as_datetime
[`dateutil.parser.parse`]: http://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.parse
[`.replace_time()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.replace_time
[`.replace()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.replace
[`.format_date()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_date
[`.format_time()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_time
[`.format_datetime()`]: {{ site.baseurl }}/docs/objects.html#DADateTime.format_datetime
[`format_date()`]: {{ site.baseurl }}/docs/functions.html#format_date
[`format_time()`]: {{ site.baseurl }}/docs/functions.html#format_time
[`format_datetime()`]: {{ site.baseurl }}/docs/functions.html#format_datetime
[`.strftime()`]: https://docs.python.org/2/library/datetime.html#datetime.time.strftime
[`continue button label`]: {{ site.baseurl }}/docs/modifiers.html#continue button label
[`validation_error()`]: {{ site.baseurl }}/docs/functions.html#validation_error
[`raise`]: https://docs.python.org/2.7/tutorial/errors.html#raising-exceptions
[`date`]: #date
[`number`]: #number
[`.geolocate()`]: {{ site.baseurl }}/docs/objects.html#Address.geolocate
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[`val()`]: {{ site.baseurl }}/docs/functions.html#js_val
[`input type`]: #input type
[`minlength`]: #minlength
[`maxlength`]: #maxlength
[`none of the above`]: #none of the above
[`forget_result_of()`]: {{ site.baseurl }}/docs/functions.html#forget_result_of
[`id`]: {{ site.baseurl }}/docs/modifiers.html#id
[`if`]: {{ site.baseurl }}/docs/modifiers.html#if
[`template`]: {{ site.baseurl }}/docs/template.html#template
[`table`]: {{ site.baseurl }}/docs/template.html#table
[`attachment`]: {{ site.baseurl }}/docs/documents.html#attachment
[`objects`]: {{ site.baseurl }}/docs/initial.html#objects
[`objects from file`]: {{ site.baseurl }}/docs/initial.html#objects from file
[`data`]: {{ site.baseurl }}/docs/initial.html#data
[`data from code`]: {{ site.baseurl }}/docs/initial.html#data from code
[lambda function]: https://docs.python.org/2.7/tutorial/controlflow.html#lambda-expressions
[`modules`]: {{ site.baseurl }}/docs/initial.html#modules
