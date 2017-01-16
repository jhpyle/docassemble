---
layout: docs
title: Setting variables (and doing other things) with questions
short_title: Setting Variables
---

To instruct **docassemble** to store user input in a variable in
response to a [question], you need to include in your [`question`] a
[variable name](#variable names) within a directive that indicates how
you would like **docassemble** to ask for the value of the variable.

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
* `fried.fish1` (this is valid code, but [Python] will think you are
referring to the attribute `fish1` of the object `fried`)
* `user's_phone_number` (apostrophes are not allowed; [Python]
  recognizes them as single quotes)
* `favorite animal` (spaces are not allowed)
* `beneficiary#1` (punctuation marks other than `_` are not allowed)
* `applicant_résumé` (only plain alphabet characters can be used)

See [reserved variable names] for a list of variable names that you
cannot use because they conflict with built-in names that [Python] and
**docassemble** use.

# Multiple choice questions (one variable only)

## Yes or no questions

### <a name="yesno"></a><a name="noyes"></a>The `yesno` and `noyes` statements

The `yesno` statement causes a question to set a boolean (true/false)
variable when answered.

{% include side-by-side.html demo="yesno" %}

In the example above, the web app will present "Yes" and "No" buttons
and will set `over_eighteen` to `True` if "Yes" is pressed, and
`False` if "No" is pressed.

The `noyes` statement is just like `yesno`, except that "Yes" means
`False` and "No" means `True`.

{% include side-by-side.html demo="noyes" %}

Note that yes/no fields can also be gathered on a screen along with
other fields; to make screens like that, use [`fields`] below.

### <a name="yesnomaybe"></a><a name="noyesmaybe"></a>`yesnomaybe` or `noyesmaybe`

These statements are just like `yesno` and `noyes`, except that they
offer a third choice, "I don't know."  If the user selects "I don't
know," the variable is set to `None`, which is a special
[Python constant] that represents the absence of a value.

{% include side-by-side.html demo="yesnomaybe" %}

## <a name="field with buttons"></a>Multiple choice buttons

A [`question`] block with a `buttons` statement will set the variable
identified in `field` to a particular value depending on which of the
buttons the user presses.

The `buttons` statement must always refer to a [YAML] list, so that
**docassemble** knows the order of the buttons.

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

A powerful feature of `buttons` is the ability to use [Python] code to
generate button choices.  If an item under `buttons` is a key-value
pair in which the key is the word `code`, then **docassemble**
executes the value as [Python] code, which is expected to return a list.
This code is executed at the time the question is asked, and the code
can include variables from the interview.  **docassemble** will
process the resulting list and create additional buttons for each
item.

{% include side-by-side.html demo="buttons-code-list" %}

Note that the [Python] code needs to return a list of key-value pairs
([Python dictionaries]) where the key is what the variable should be
set to and the value is the button label.  This is different from the
[YAML] syntax.

This is equivalent to:

{% include side-by-side.html demo="buttons-code-list-equivalent" %}

You can use `buttons` as an alternative to [`yesno`] where you want
different text in the labels.

{% include side-by-side.html demo="yesno-custom" %}

## <a name="field with choices"></a>Multiple choice list

To provide a multiple choice question with "radio buttons" and a
"Continue" button, use `field` with a `choices` list:

{% include side-by-side.html demo="choices" %}

You can specify a default value using `default`:

{% include side-by-side.html demo="choices-with-default" %}

## <a name="image button"></a>Adding images to buttons and list items

To add a decorative icon to a choice, use a key/value pair and add
`image` as an additional key.

{% include side-by-side.html demo="buttons-icons" %}

This works with `choices` as well:

{% include side-by-side.html demo="choices-icons" %}

## <a name="code button"></a>Embedding [`question`] and [`code`] blocks within multiple choice questions

Multiple choice questions can embed [`question`] blocks and [`code`]
blocks.  These questions are just like ordinary questions, except they
can only be asked by way of the questions in which they are embedded.

You embed a question by providing a [YAML] key-value list (a
dictionary) (as opposed to text) as the value of a label in a
`buttons` or `choices` list.

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

# <a name="field"></a>A simple "continue" button that sets a variable

{% include side-by-side.html demo="continue-participation" %}

A [`question`] with a `field` and no `buttons` will offer the user a
"Continue" button.  When the user presses "Continue," the variable
indicated by `field` will be set to `True`.

# <a name="uploading"></a>Storing files as variables

Users can upload files, and the files are stored as a variable in **docassemble**.

{% include side-by-side.html demo="upload" %}

Note that this question uses the [`fields`] statement, which is
explained in more detail [below](#fields).

When set, the variable `user_picture` will be a special [object] of
type [`DAFileList`].  For instructions about how to make use of
uploaded files, see [inserting images].

# <a name="signature"></a>Gathering the user's signature into a file variable

The `signature` directive presents a special screen in which the user
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

# <a name="fields"></a>Setting multiple variables with one screen

## Creating a list of fields

The `fields` statement is used to present the user with a list of
fields.

{% include side-by-side.html demo="text-field-example" %}

The `fields` must consist of a list in which each list item consists
of one or more key/value pairs.  One of these keys
([typically](#label)) is the label the user sees, where the value
associated with the key is the name of the variable that will store
the user-provided information for that field.  The other key/value
pairs in the item (if any) are modifiers that allow you to customize
how the field is displayed to the user.

These modifiers are distinguished from label/variable pairs based on
the key; if the key is uses one of the names listed below, it will be
treated as a modifier; if it is anything else, it will be treated as a
label.

## Customizing each field

The following are the keys that have special meaning:

### <a name="datatype summary"></a>`datatype`

`datatype` affects how the data will be collected, validated and
stored.  For a full explanation of how this is used, see the
[section on `datatype`] below.

### <a name="required"></a>`required`

`required` affects whether the field will be optional or required.  If
a field is required, it will be marked with a red asterisk.  The value
of `required` can be `true` or `false`.  By default, all fields are
required, so you never need to write `required: true` unless you want
to.

{% include side-by-side.html demo="optional-field" %}

Instead of writing `true` or `false`, you can write [Python] code.
This code will be evaluated for whether it turns out to be true or
false.  For example, instead of `true` or `false`, you could use the
name of a variable that is defined by a [`yesno`] question (as long as
that variable was defined before the screen loads; the red asterisk
cannot be toggled in real time within the browser).

{% include side-by-side.html demo="required-code" %}

### <a name="hint"></a>`hint`

You can guide users as to how they should fill out a text field by
showing greyed-out text in a text box that disappears when the user
starts typing in the information.  In HTML, this text is known as the
[placeholder].  You can set this text for a text field by setting
`hint`.  You can use [Mako] templates.

{% include side-by-side.html demo="text-hint" %}

### <a name="help"></a>`help`

You can provide contextual help to the user regarding the meaning of a
field using the `help` modifier.  The label will be green to indicate
that it can be clicked on, and the value of `help` will appear on the
screen when the user clicks the green text.  You can use [Mako]
templates.

{% include side-by-side.html demo="text-help" %}

### <a name="default"></a>`default`

You can provide a default value to a field using `default`.  You can
use [Mako] templates.

{% include side-by-side.html demo="text-default" %}

### <a name="choices"></a>`choices`

The `choices` modifier is used with multiple-choice fields.  It must
refer to a list of possible options.  Can be a list of key/value pairs
(key is what the variable will be set to; value is the label seen by
the user) or a list of plain text items (in which case the label and
the variable value are the same).

{% include side-by-side.html demo="fields-choices" %}

When the [`datatype`] is [`object`], [`object_radio`], or
[`object_checkboxes`], `choices` indicates a list of objects from which
the user will choose.  See the
[section on selecting objects](#objects), below.

### <a name="exclude"></a>`exclude`

`exclude` is used in combination with [`choices`](#choices) when the
[`datatype`] is [`object`], [`object_radio`], or
[`object_checkboxes`].  Any object in `exclude` will be omitted from the
list of choices if it is present in [`choices`](#choices).  See the
[section on selecting objects](#objects), below.

### <a name="code"></a>`code`

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

### <a name="shuffle"></a>`shuffle`

`shuffle` can be used on multiple-choice fields (defined with
[`code`](#code) or [`choices`](#choices)).  When `true`, it randomizes
the order of the list of choices; the default is not to "shuffle" the
list.

{% include side-by-side.html demo="shuffle" %}

### <a name="show if"></a>`show if`

You can use the `show if` modifier if you want the field to be hidden
under certain conditions.  There are three methods of using `show if`,
which have different syntax.

Using the first method, the field will appear or disappear in the web
browser depending on the value of another field in the `fields` list.
Under this method, `show if` refers to a [YAML] dictionary with two
keys: `variable` and `is`, where `variable` refers to the variable
name of the other field, and `is` refers to the value of the other
field that will cause this field to be shown.

This can be useful when you have a multiple-choice field that has an
"other" option, where you want to capture a text field but only if the
user selects the "other" option.

{% include side-by-side.html demo="other" %}

The second method is like the first, but is for the special case where
the other field in `fields` is a yes/no variable.  Under this method,
`show if` refers to the other field's variable name.  If that variable
is true, the field will be shown, and if it is not true, the field
will be hidden.

{% include side-by-side.html demo="showif-boolean" %}

Under the third method, the field is either shown or not shown on the
screen when it loads, and it stays that way.  You can use [Python]
code to control whether the field is shown or not.  Unlike the first
method, you are not limited to using variables that are part of the
`fields` list; you can use any [Python] code.  Under this method,
`show if` must refer to a [YAML] dictionary with one key, `code`,
where `code` contains [Python] code.  The code will be evaluated and
if it evaluates to a positive value, the field will be shown.

{% include side-by-side.html demo="showif" %}

### <a name="hide if"></a>`hide if`

This works just like [`show if`](#show if), except that it hides the
field instead of showing it.

{% include side-by-side.html demo="hideif-boolean" %}

### <a name="disable others"></a>`disable others`

If `disable others` is set to `true`, then when the user changes the
value of the field to something, all the other fields in the question
will be disabled.

### <a name="note"></a>`note`

The value of `note` is [Markdown] text that will appear on the screen;
useful for providing guidance to the user on how to enter information.

{% include side-by-side.html demo="note" %}

### <a name="html"></a>`html`

The `html` directive is like [`note`](#note), except the format is
expected to be raw HTML.  It can be used in combination with the
[`css`] and [`script`] modifiers.

{% include side-by-side.html demo="html" %}

### <a name="no label"></a>`no label`

If you use `no label` as the label for your variable, the label will
be omitted.  On wide screens, the field will fill more of the width of
the screen if the label is set to `no label`.

{% include side-by-side.html demo="no-label-field" %}

To keep the width of the field normal, but have a blank label, use
`""` as the label.

{% include side-by-side.html demo="blank-label-field" %}

### <a name="label"></a>`label` and `field`

Instead of expressing your labels and variable names in the form of `-
Label: variable_name`, you can specify a label using the `label` key
and the variable name using the `field` key.

{% include side-by-side.html demo="label" %}

## <a name="datatype"></a>Possible data types for fields

There are many possible `datatype` values, which affect what the user
sees and how the input is stored in a variable.

### Text fields

<a name="text"></a>A `datatype: text` provides a single-line text input box.  This is the
default, so you never need to specify it unless you want to.

{% include side-by-side.html demo="text-field" %}

<a name="area"></a>`datatype: area` provides a multi-line text area.

{% include side-by-side.html demo="text-box-field" %}

<a name="date"></a>`datatype: date` provides a date entry input box
and requires a valid date.

{% include side-by-side.html demo="date-field" %}

<a name="email"></a>`datatype: email` provides an e-mail address input
box.

{% include side-by-side.html demo="email-field" %}

<a name="password"></a>`datatype: password` provides an input box
suitable for passwords.

{% include side-by-side.html demo="password-field" %}

### Numeric fields

<a name="integer"></a>`datatype: integer` indicates that the input
should be a valid whole number.

<a name="number"></a>`datatype: number` indicates that the input
should be a valid numeric value.

{% include side-by-side.html demo="number-field" %}

<a name="currency"></a>`datatype: currency` indicates that the input
should be a valid numeric value.  In addition, the input box shows a
currency symbol based on locale defined in the [configuration].

{% include side-by-side.html demo="money-field" %}

<a name="range"></a>`datatype: range` shows a slider that the user can use to
select a number within a given range.  The range must be supplied by
providing `min` and `max` values.  An option `step` value can also be
provided, the default of which is 1.

{% include side-by-side.html demo="range" %}

### File uploads

<a name="file"></a><a name="files"></a>Using the `file` or `files`
datatypes within a `fields` list, you can allow users to upload one or
more files.

`datatype: file` indicates that the user can upload a single file.
The variable is set to a [`DAFileList`] object containing the
necessary information about the uploaded file.

{% include side-by-side.html demo="upload" %}

`datatype: files` indicates that the user can upload one or more
files.  The variable is set to a [`DAFileList`] object containing the
necessary information about the uploaded files.

{% include side-by-side.html demo="upload-multiple" %}

<a name="camera"></a>`datatype: camera` is just like `file`, except with [HTML5] that
suggests using the device's camera to take a picture.  On many
devices, this is no different from `datatype: file`.

<a name="camcorder"></a>`datatype: camcorder` is just like `camera`,
except for recording a video.

<a name="microphone"></a>`datatype: microphone` is just like `camera`,
except for recording an audio clip.

### Yes/no fields

<a name="fields yesno"></a><a name="fields noyes"></a>`datatype:
yesno` will show a checkbox with a label, aligned with labeled fields.
`datatype: noyes` is like `datatype: yesno`, except with True and
False inverted.

{% include side-by-side.html demo="fields-yesno" %}

<a name="fields yesnowide"></a><a name="fields
noyeswide"></a>`datatype: yesnowide` will show a checkbox with a label
that fills the full width of area.  `datatype: noyeswide` is like
`datatype: yesnowide`, except with True and False inverted.

{% include side-by-side.html demo="fields-yesnowide" %}

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

### Multiple-choice fields

<a name="fields checkboxes"></a>`datatype: checkboxes` will show the
[`choices`](#choices) list as checkboxes.  The variable will be a
dictionary with items set to true or false depending on whether the
option was checked.  No validation is done to see if the user selected
at least one, regardless of the value of `required`.

{% include side-by-side.html demo="fields-checkboxes" %}

<a name="radio"></a>`datatype: radio` shows a [`choices`](#choices) list as a list of
radio buttons instead of as a dropdown [select] tag (which is the
default).  The variable will be set to the value of the choice.

{% include side-by-side.html demo="radio-list" %}

<a name="object"></a>`datatype: object` is used when you would like to use a variable to
refer to an existing object.  You need to include `choices`, which can
be a list of objects.

{% include side-by-side.html demo="object" %}

If `choices` refers to a variable that is a list of things, the list
will be unpacked and used as the list of items from which the user can
select.  [Python] code can be used here.

{% include side-by-side.html demo="object-selections" %}

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

{% include side-by-side.html demo="object-checkboxes" %}

## Input validation

For some field types, you can require input validation by adding the
following to the definition of a field:

* <a name="min"></a>`min`: for `currency` and `number` data types,
  require a minimum value.  This is passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/min-method).
* <a name="max"></a>`max`: for `currency` and `number` data types,
  require a maximum value.  This is passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/max-method).

{% include side-by-side.html demo="min" %}

* <a name="minlength"></a>`minlength`: require a minimum number of
  characters in a textbox, number of checkboxes checked, etc.  This is
  passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/minlength-method).
* <a name="maxlength"></a>`maxlength`: require a maximum number of
  characters in a textbox, number of checkboxes checked, etc.  This is
  passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/maxlength-method).

{% include side-by-side.html demo="minlength" %}

## Example

Here is a lengthy example that illustrates many of these features.

{% include side-by-side.html demo="fields" %}

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
`fields` list, where the [`choices`](#choices) are the names of the objects from
which to choose.  (Optionally, you can set a `default` value, which is
also the name of a variable.)

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

If any of the objects listed under `choices` represent lists of
objects, such as `case.defendant` or `client.child` (objects of type
`PartyList`, those lists will be expanded and every item will be
included.  You can also include under `choices` [Python] code, such as
`case.parties()` or `case.all_known_people()`.

The [`datatype`] of `object` presents the list of choices as a
pull-down.  If you prefer to present the user with radio buttons, set
the [`datatype`] to `object_radio`.

# Special screens

## <a name="event"></a>Performing special actions requested by the user

In **docassemble**, you can allow users to click links or menu items
that take the user to a special screen that the user would not
ordinarily encounter in the course of the interview.  You can create
such a screen using the `event` statement.

An `event` statement acts just like `sets`: it advertises to
**docassemble** that the question will potentially define a variable.

In the following example, the variable `show_date` is never defined;
it is simply sought.  The [`task_not_yet_performed()`] function is
used to make sure that the dialog box only appears once.

{% include side-by-side.html demo="dialog-box" %}

The `event` statement is important if you use the [roles] feature to
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

This directive can also be used to create screens that the user can
reach from the menu or from hyperlinks embedded in question text.  For
information and examples, see [url_action()], [process_action()],
[action_menu_item()], and [menu_items].

## <a name="review"></a>Creating a special screen where the user can review his or her answers

A `review` block allows interview authors to provide a screen where
users can review and edit their answers.  Typically, the user will get
to this screen by selecting an option from the web app menu (e.g.,
"Review Answers"), or by clicking on a hyperlink within `subquestion`
text (e.g., "to review the answers you have provided so far, click
here").

Here is an example of a `review` block that is launched from the menu:

{% include side-by-side.html demo="review-1" image="review-block.png" %}

Note that the `review` block does not show a link for "Favorite
fungus" because the variable `fungi` has not been defined yet.
However, once `fungi` is defined, the `review` block would show it.

This behavior is different from the typical behavior of
**docassemble** blocks.  Normally, referring to a variable that has
not yet been defined will trigger the asking of a question that will
define that variable.  In the `review` block, however, the presence of
an undefined variable simply causes the item to be omitted from the
display.

For more information about adding menu items, see the sections on
[special variables] and [functions].

### <a name="review customization"></a>Customizing the display of `review` options

You can provide the user with a review of answers and buttons that the
user can press to revisit an answer:

{% include side-by-side.html demo="review-2" image="review-block-buttons.png" %}

In addition, the `review` block, like the `fields` block, allows you
to use `note` and `html` entries.

If these are modified with the optional `show if` modifier, they will
only be displayed if the variable referenced by the `show if` modifier
has been defined.  In addition, if any of these entries refer to a
variable that has not been defined yet, they will be omitted.

{% include side-by-side.html demo="review-3" image="review-block-note.png" %}

The `review` block allows you to add `help` text to an entry, in
which case the text is shown underneath the hyperlink.  If this text
expects a variable to be defined that has not actually been defined,
the item will not be shown.  Note: this is not available with the
`button` display format.

{% include side-by-side.html demo="review-4" image="review-block-help.png" %}

### <a name="resume button label"></a>Customizing the Resume button

By default, the `review` block puts a "Resume" button at the bottom of
the screen.  If you want the label on the button to be something other
than the word "Resume," add a `resume button label` modifier.

{% include side-by-side.html demo="resume-button-label" image="review-block-custom-button.png" %}

### <a name="review auto"></a>Why can't `review` blocks be automatically generated?

The list of variables to display to the user in a `review` block needs
to be specified by the interview author.  There are several reasons
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
   interview author control what the user can edit.
2. A list of answers already provided might not be user-friendly
   unless the interview author presents it in a logically organized
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
[`yesno`]: #yesno
[groups]: {{ site.baseurl }}/docs/groups.html
[Python constant]: https://docs.python.org/2/library/constants.html
[inserting images]: {{ site.baseurl }}/docs/markup.html#inserting uploaded images
[`fields`]: #fields
[Python dictionaries]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[HTML5]: https://en.wikipedia.org/wiki/HTML5
[`selections()` function]: {{ site.baseurl }}/docs/functions.html#selections
[`exclude`]: #exclude
[`object`]: #object
[`object_radio`]: #object_radio
[`object_checkboxes`]: #object_checkboxes
[section on `datatype`]: #datatype
[`datatype`]: #datatype
[roles]: {{ site.baseurl }}/docs/roles.html
[`task_not_yet_performed()`]: {{ site.baseurl }}/docs/functions.html#task_not_yet_performed
[`css`]: {{ site.baseurl }}/docs/modifiers.html#css
[`script`]: {{ site.baseurl }}/docs/modifiers.html#script
