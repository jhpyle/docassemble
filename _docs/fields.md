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
* `Nyan-Cat` (this is arithmetic: `Nyan` minus `Cat`)
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
pair in which the key is the word [`code`](#code), then **docassemble**
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

To provide a multiple-choice question with a dropdown "select"
element, you need to use a [`fields`] statement; see [below](#select).

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

# Uploads

## <a name="uploading"></a>Storing files as variables

Users can upload files, and the files are stored as a variable in **docassemble**.

{% include side-by-side.html demo="upload" %}

Note that this question uses the [`fields`] statement, which is
explained in more detail [below](#fields).

When set, the variable `user_picture` will be a special [object] of
type [`DAFileList`].  For instructions about how to make use of
uploaded files, see [inserting images].

## <a name="signature"></a>Gathering the user's signature into a file variable

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

Signatures can be also be inserted into assembled [documents] in the
same way.  They can also be inserted into [.docx fill-in forms] and
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

### <a name="summary datatype"></a>`datatype`

`datatype` affects how the data will be collected, validated and
stored.  For a full explanation of how this is used, see the
[section on `datatype`] below.

### <a name="required"></a>`required`

`required` affects whether the field will be optional or required.  If
a field is required, it will be marked with a red asterisk.  The value
of `required` can be `True` or `False`.  By default, all fields are
required, so you never need to write `required: True` unless you want
to.

{% include side-by-side.html demo="optional-field" %}

Instead of writing `True` or `False`, you can write [Python] code.
This code will be evaluated for whether it turns out to be true or
false.  For example, instead of `True` or `False`, you could use the
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
also use [Mako] templates.

{% include side-by-side.html demo="text-default" %}

### <a name="choices"></a>`choices`

The `choices` modifier is used with multiple-choice fields.  It must
refer to a list of possible options.  Can be a list of key/value pairs
(key is what the variable will be set to; value is the label seen by
the user) or a list of plain text items (in which case the label and
the variable value are the same).

{% include side-by-side.html demo="fields-choices" %}

When the [`datatype`] is [`object`], [`object_radio`], or
[`object_checkboxes`], `choices` indicates a list of objects from
which the user will choose.  For more information about using objects
in multiple choice questions, see the
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

### <a name="exclude"></a>`exclude`

If you build the list of choices with `code`, you can exclude items
from the list using `exclude`, where the value of `exclude` is
[Python] code.

{% include side-by-side.html demo="fields-mc-exclude" %}

In this example, the value of `exclude` is a single variable.  If
given a list of things, it will exclude any items that are in the list.

### <a name="none of the above"></a>`none of the above`

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

### When the list of choices is empty

If the list of choices for a multiple choice question is empty,
**docassemble** will try to deal with the situation gracefully.  If
there is only a single field listed under `fields`, or the question is
a [standalone multiple choice question](#field with buttons), then the
variable that will be set by the user's selection will be set to
`None`, and the question (or the field, if there are other fields
listed under `fields`) will be skipped.

If the `datatype` is `checkboxes`, the variable will be set to an
empty [`DADict`] (a type of [dictionary] specific to **docassemble**).
If the `datatype` is `object_checkboxes`, the variable will be set to
an empty [`DAList`] (a type of [list] specific to **docassemble**).

### <a name="shuffle"></a>`shuffle`

`shuffle` can be used on multiple-choice fields (defined with
[`code`](#code) or [`choices`](#choices)).  When `True`, it randomizes
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

If `disable others` is set to `True`, then when the user changes the
value of the field to something, all the other fields in the question
will be disabled.

{% include side-by-side.html demo="disable-others" %}

### <a name="note"></a>`note`

The value of `note` is [Markdown] text that will appear on the screen;
useful for providing guidance to the user on how to enter information.

{% include side-by-side.html demo="note" %}

### <a name="html"></a>`html`

The `html` directive is like [`note`](#note), except the format is
expected to be raw [HTML].  It can be used in combination with the
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

## <a name="datatype"></a>Data types

Within a [`fields`] question, there are many possible `datatype`
values, which affect what the user sees and how the input is stored in
a variable.  The following sections describe the available
`datatype`s.

## Plain text

<a name="text"></a>A `datatype: text` provides a single-line text
input box.  This is the default, so you never need to specify it
unless you want to.

{% include side-by-side.html demo="text-field" %}

<a name="area"></a>`datatype: area` provides a multi-line text area.

{% include side-by-side.html demo="text-box-field" %}

## Passwords

<a name="password"></a>`datatype: password` provides an input box
suitable for passwords.

{% include side-by-side.html demo="password-field" %}

## <a name="date"></a>Dates

`datatype: date` provides a date entry input box.  The style of the
input box depends on the browser.

{% include side-by-side.html demo="date-field" %}

Note that while input validation is applied, the resulting variable
will be plain text, not a special [Python] date object.  For more
information about working with date variables, see the documentation
for the [date functions].  These functions are flexible and will work
correctly if you give them dates as text, as long as a date can be
discerned from the text.

If you set a [`default`] value for a date field, write the date in the
format YYYY-MM-DD.  Many browsers have built-in "date pickers" that
expect dates to be in this format.  See [Mozilla's documentation] of
the date input field.  If the browser uses a date picker, then your
interview will see text values in the form YYYY-MM-DD, but on other
browsers, like [Firefox], the format may be some other format.

## <a name="email"></a>E-mail addresses

`datatype: email` provides an e-mail address input box.

{% include side-by-side.html demo="email-field" %}

## Numbers

<a name="integer"></a>`datatype: integer` indicates that the input
should be a valid whole number.

<a name="number"></a>`datatype: number` indicates that the input
should be a valid numeric value.

{% include side-by-side.html demo="number-field" %}

## Currency

<a name="currency"></a>`datatype: currency` indicates that the input
should be a valid numeric value.  In addition, the input box shows a
currency symbol based on locale defined in the [configuration].

{% include side-by-side.html demo="money-field" %}

The variable will be set to a number, just as if `datatype: number`
was used.  For information about how to display currency values, see
the [`currency()`] function.

## Sliders

<a name="range"></a>`datatype: range` shows a slider that the user can use to
select a number within a given range.  The range must be supplied by
providing `min` and `max` values.  An option `step` value can also be
provided, the default of which is 1.

{% include side-by-side.html demo="range" %}

## <a name="file"></a><a name="files"></a>File uploads

Using the `file` or `files` datatypes within a `fields` list, you can
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

<a name="camcorder"></a>`datatype: camcorder` is just like `camera`,
except for recording a video.

<a name="microphone"></a>`datatype: microphone` is just like `camera`,
except for recording an audio clip.

Whether these special data types do anything different from the `file`
data type is dependent on the web browser.  Mobile browsers are the
most likely to respond to these features.

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

## <a name="select"></a>Multiple-choice selection list

If you provide a list of [`choices`](#choices) or some
choice-generating [`code`](#code) for a field within a list of
`fields`, the user will see a dropdown [select] element.  The variable
will be set to the value of the selected choice.

{% include side-by-side.html demo="fields-choices-dropdown" %}

## <a name="radio"></a>Radio buttons

`datatype: radio` shows a [`choices`](#choices) list as a list of
radio buttons instead of as a dropdown [select] element (which is
[the default](#select)).  The variable will be set to the value of the
selected choice.

{% include side-by-side.html demo="radio-list" %}

## <a name="object"></a>Multiple-choice with objects

`datatype: object` is used when you would like to use a variable to
refer to an existing object.  You need to include `choices`, which can
be a list of objects.

{% include side-by-side.html demo="object" %}

If `choices` refers to a variable that is a list of things, the list
will be unpacked and used as the list of items from which the user can
select.  [Python] code can be used here.

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

## <a name="ml"></a>Machine learning

From the user's perspective, `datatype: ml` works just like `datatype:
text` (which is the default if no `datatype` is indicated), and
`datatype: mlarea` works just like `datatype: area`.

From the interview author's perspective, however, the variable that is
set is not a piece of text, but an object representing a
classification of the user's input, based on a machine learning model
that is "trained" to classify user input.

{% include demo-side-by-side.html demo="predict-happy-sad" %}

For more information about how to use machine learning variables, see
the [machine learning section].

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
  characters in a textbox, number of checkboxes checked, etc.  This is
  passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/minlength-method).
* <a name="maxlength"></a>`maxlength`: require a maximum number of
  characters in a textbox, number of checkboxes checked, etc.  This is
  passed directly to the
  [jQuery Validation Plugin](http://jqueryvalidation.org/maxlength-method).

{% include side-by-side.html demo="minlength" %}

You can also use [Python] code to validate an input field.  To do so,
add a `validate` directive to the field description that refers to the
name of a [function] that returns `True` (or something that [Python]
considers "true") if the value is valid, and `False` (or something
that [Python] considers "not true") if the value is invalid.

{% include demo-side-by-side.html demo="validation-test" %}

In this example, the function `is_multiple_of_four` is defined as
follows:

{% highlight python %}
def is_multiple_of_four(x):
    return x/4 == int(x/4)
{% endhighlight %}

This [Python] code is in the [`validationfuncs.py`] file.  The
`modules` block includes this code.  The function returns `True` if 4
divides the input value into a whole number

The error message that the user will see is a generic error message,
"Please enter a valid value."  In most cases you will want to explain
to the user why the input did not validate.  To provide a more
descriptive error message, your function can [raise an exception]
using the error message you would like the user to see.  Both a false
return value and an exception signal that the input is not valid.

{% include demo-side-by-side.html demo="validation-test-two" %}

In this example, the function `is_multiple_of_four` is defined as
follows:

{% highlight python %}
def is_multiple_of_four(x):
    if x/4 != int(x/4):
        raise Exception("The number must be a multiple of four")
    return True
{% endhighlight %}

This [Python] code is in the [`validationfuncstwo.py`] file.  If 4
does not divide the input value into a whole number, then an exception
is raised.  The text passed to `Exception()` will be the text the user
sees if the value does not validate.  If 4 does divide the input value
by a whole number, `True` is returned.

One limitation of these validation functions is that they can only
test for characteristics inherent in the variable being validated;
they cannot compare the variable to other variables.

You can get around this restriction using the `validation code`
modifier.

{% include demo-side-by-side.html demo="validation-code" %}

Note that the code under `validation code` is not within a function,
so it should not try to `return` any values.  If the code runs through
to the end, this indicates that the input for the question is valid.
If an exception is raised, the input for the question is invalid.

If the input is invalid, the user will see a message at the top of the
screen containing the error message passed to the [`Exception`] that
was raised.

## A comprehensive example

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
write questions in a generalized way: the [`generic object`](#generic)
modifier, and [index variables](#index variables).

## <a name="generic"></a>The `generic object` modifier

The [`generic object` modifier] is explained more fully in the
[section on modifiers], but here is an example:

{% include side-by-side.html demo="generic-object" %}

The special variable `x` stands in for any object of type
[`Individual`].

If you are not yet familiar with the concept of "[objects]," see the
[objects section].

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

If you click "Favorite fruit," you are taken to a [`question`] where
you can edit the value of `fruit`.  This has the same effect as
calling [`force_ask()`] on `'fruit'` or running an [action] on
`'fruit'`; whatever block in your interview offers to define `fruit`
will be used.  After the user edits the value of the variable, the
user will return to the `review` screen again.

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
[groups]: {{ site.baseurl }}/docs/groups.html
[groups section]: {{ site.baseurl }}/docs/groups.html
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
[tooltip]: http://www.w3schools.com/tags/att_title.asp
[list]: https://docs.python.org/2/tutorial/datastructures.html
[dictionary]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[dictionaries]: https://docs.python.org/2/tutorial/datastructures.html#dictionaries
[.docx fill-in forms]: {{ site.baseurl }}/docs/documents.html#signature docx
[PDF fill-in forms]: {{ site.baseurl }}/docs/documents.html#signature
[documents]: {{ site.baseurl }}/docs/markup.html#inserting uploaded images
[`generic object` modifier]: {{ site.baseurl }}/docs/modifiers.html#generic object
[section on modifiers]: {{ site.baseurl }}/docs/modifiers.html#generic object
[objects section]: {{ site.baseurl }}/docs/objects.html
[`currency()`]: {{ site.baseurl }}/docs/functions.html#currency
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[date functions]: {{ site.baseurl }}/docs/functions.html#date functions
[machine learning section]: {{ site.baseurl }}/docs/ml.html#howtouse
[raise an exception]: https://en.wikibooks.org/wiki/Python_Programming/Exceptions
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
