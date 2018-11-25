---
layout: docs
title: "Question Blocks: Modifier Components"
short_title: "- Modifier Components"
---

There are a number of optional components that can be included in
[`question`] blocks of your [DALang] to modify the appearance or behavior of the
question.

# <a name="audio"></a>Including `audio`

{% include side-by-side.html demo="audio" %}

The `audio` component allows you to add audio to your questions.  An
audio player will appear above the question, and the user can press
play to hear the sound.

The filename can be constructed with [Mako].  A plain file path will
be assumed to point to a file in the `static` directory of the Steward.
A reference to another Steward may also be
included: e.g., `docassemble.demo:data/static/schumann-clip-3.mp3`.
A URL beginning with `http` or `https` may also be provided.

You can also play uploaded files:

{% include side-by-side.html demo="upload_audio" %}

Note that in this example, we use `file` as the `datatype`, which is
the standard way to upload files.  You can also use the `datatype` of
[`microphone`], which in some browsers (mostly on mobile platforms) will
launch an audio recording app to create the file to upload.

{% include side-by-side.html demo="upload_audio_microphone" %}

Stewards use the [HTML5 audio tag] to allow users to play the
audio.  Not all browsers support every type of audio file.  In order
to make your audio files accessible to the greatest number of users,
if you provide static audio files, you should include files in
both `mp3` and `ogg` format.

For example, if your `audio` component points to a file, such as
`nyc_question.mp3`, then your Steward should contain a file
called `nyc_question.mp3` in the `data/static` directory.  If you also
include an OGG version of this audio file, called `nyc_question.ogg`,
in the same directory, then the Steward will make both files
available to the user, and the user's browser will use whichever file
works.  In your `audio` component, you can refer to either the `mp3`
or the `ogg` file.

Or, if your `mp3` and `ogg` alternatives are located in different
directories, you can do this:

{% highlight yaml %}
---
question: Are you traveling to New York City?
yesno: going_to_nyc
audio:
  - mp3/nyc_question.mp3
  - ogg/nyc_question.ogg
---
{% endhighlight %}

Or, if you are using hyperlinks to files on another server, you can
include different versions by doing something like this:

{% highlight yaml %}
---
question: Are you traveling to New York City?
yesno: going_to_nyc
audio:
  - http://example.com/files/audio/51/nyc_question.mp3
  - http://example.com/files/audio/23/nyc_question.ogg
---
{% endhighlight %}

If you refer to an uploaded file, the Steward will take care of
providing both `mp3` and `ogg` versions.  When users upload an audio
file, the Steward tries to convert it to the appropriate formats.
For this to work, ffmpeg and pacpl must be installed on your system.
Currently, Stewards can handle audio files uploaded in `mp3`,
`ogg`, `3gpp`, and `wav` formats.  If you need to be able to process
another type of audio file, docassemble's source code can probably
be modified to support that audio type.

Note that there a number of limitations to playing audio in browsers.
For example, older Android devices will not play audio retrieved
through https, but will play the same audio retrieved through http.

See [special variables] for information about enabling a Steward's
automatic text-to-speech features.

# <a name="video"></a>Including `video`

The `video` component is just like the [`audio`](#audio) component
except that it displays a video instead of an audio file.

{% highlight yaml %}
---
question: Are you traveling to New York City?
yesno: going_to_nyc
video: nyc_tourism.mp4
---
{% endhighlight %}

Stewards uses the [HTML5 video tag] to allow users to play the
audio.  Just as you should include both `mp3` and `ogg` audio files,
you should include both `mp4` and `ogv` video files, so that users of
many different browsers will all be able to see your videos.  These
are the two formats that the [HTML5 video tag] most widely supports.

If you refer to an uploaded video file, the Steward will take care
of providing both `mp4` and `ogv` versions.  When users upload a
video file, the Steward tries to convert it to the appropriate
formats.  For this to work, ffmpeg and pacpl must be installed on your
system.  Currently, Stewards can handle videos uploaded in
`mp4`, `ogv`, and `mov` formats.  If you need to be able to process
another type of video, docassemble's source code can probably
be modified to support that audio type.

You can also use the `video` component to embed [YouTube] and
[Vimeo] videos.  For example, if you want to embed a [YouTube] video
and the URL for the video is
`https://www.youtube.com/watch?v=9bZkp7q19f0` or
`https://youtu.be/9bZkp7q19f0`, you would write something like this:

{% include side-by-side.html demo="video" %}

If you want to embed a [Vimeo] video, the URL of which is
`https://vimeo.com/96044910`, you would write:

{% include side-by-side.html demo="vimeo" %}

Note that you could not have written the above as this:

{% highlight yaml %}
---
field: ready_to_proceed
question: |
  Welcome to the interview.
subquestion: |
  Please watch this introductory video
  before proceeding with the interview.
video: [VIMEO 96044910]
---
{% endhighlight %}

This would generate an error because [YAML] thinks square brackets
indicate a list of items, not plain text.  If you want to write the
component on one line, write `video: "[VIMEO 96044910]"`.

`[YOUTUBE ...]` and `[VIMEO ...]` assume that the aspect ratio of the
vide is 16:9.  If the aspect ratio of the video is 4:3, you can use
`[YOUTUBE4:3 ...]` or `[VIMEO4:3 ...]`.  You can also explicitly state
that the aspect ratio is 16:9 by using `[YOUTUBE16:9 ...]` or
`[VIMEO16:9 ...]`

# <a name="help"></a>Providing `help` Text to Users

{% include side-by-side.html demo="help-damages" %}

In the web app, users can use the navigation bar to toggle between the
"Question" tab and the "Help" tab.  The contents of the "Help" tab
consist of the contents of any `help` component in the question being
presented, followed by the contents of any `interview help` blocks
contained within the [DALang]'s [initial blocks].

You can add audio to your help text:

{% include side-by-side.html demo="help-damages-audio" %}

You can also add video to help text using the `video` component.

When [`interview help`] is available but question-specific `help` is
not available, the help tab is merely labeled "Help."  When
question-specific help is available, the help tab is bright yellow and
is marked with a star.  If you want the label to be something other
than "Help", you can add a `label` inside the `help` component:

{% include side-by-side.html demo="help-damages-label" %}

If the [`question help button`] feature is enabled, and
question-specific `help` is available, a "Help" button will be
available on the button bar, which when pressed will show the help
tab.  The button label is "Help" by default, but if a `label` is
provided to the question-specific `help`, the button will bear this
label instead.  When a help button is present, the help tab in the
navigation bar will always be labeled "Help," and it will never be
highlighted in yellow.

The default label "Help" can be changed on a per-interview basis.  If
you set an [`interview help`] initial block and provide a `label` as
part of it, the value of this `label` will be used instead of "Help"
as the name of the "Help" tab in the navigation bar.

# <a name="decoration"></a>Adding Icons to Question: `decoration`

{% include side-by-side.html demo="decoration" %}

The `decoration` modifier adds an icon to the right of the
[`question`] text.  In the example above, `kids` has been defined in
an [`image sets`] or [`images`] block.

By default, if a `decoration` modifier refers to an image that has not
been defined in an [`image sets`] or [`images`] block, users will see an
error message.  However, if you set the [`use font awesome`] directive
in the [Configuration] to `True`, then any reference to an image not
defined with [`image sets`] or [`images`] will be treated as the name of a
[Font Awesome] icon.

{% include side-by-side.html demo="font-awesome" %}

This method also works with [inline icons].

# <a name="script"></a>Adding [Javascript]: `script`

If you know how to write [Javascript] and [CSS], you can add
[Javascript] code and [CSS] formatting to a question.

To add [Javascript] or [CSS] to all questions, you can use a
[`features`] block to include [Javascript] and [CSS] files on the web
page.

The `script` modifier contains raw HTML to be appended to the bottom
of the web page for the question.

{% include side-by-side.html demo="script" %}

# <a name="css"></a>Adding [CSS]: `css`

The `css` modifier contains raw HTML that will be appended to the HTML `<head>`.

{% include side-by-side.html demo="css" %}

It is best only to include [CSS] that is tied to specified HTML
elements you include in your questions, rather than include [CSS] that
has global effects (like the example above).  Because of the way
Stewards operate, [CSS] applied in one question will
affect later questions until the screen is reloaded.

# <a name="progress"></a>The Progress Bar

Stewards can be configured to show a
[progress bar].  This will show the user a progress indicator to give
the user a sense of how much longer the interview session will take.

The progress along the bar at any question needs to be set with the
`progress` modifier.  For example:

{% include side-by-side.html demo="progress" %}

The value of `progress` needs to be a number between 0 and 100.  If
the value is zero, the progress bar is hidden for the current
question.  If the value is greater than 100, a full progress bar will
be shown.  If the value is `None` (`null` in [YAML]), then the
progress bar will be hidden and will not advance until it is set to
something else.

You can also control the progress meter with the [`get_progress()`]
and [`set_progress()`] functions.

If the [progress bar] is enabled and the Steward encounters a
question that does not have a `progress` setting, the progress bar
will advance automatically.  The amount by which the progress bar
automatically advances gets smaller as the progress
bar gets closer to 100%.

As a result, you do not need to attach a `progress` setting to every
question; you can just set `progress` on a few questions, and let the
automatic advancing mechanism take care of increasing the progress.

If the Steward reaches a question with a `progress` setting that is
less than the current position of the [progress bar], the position of
the [progress bar] will stay the same.  This ensures that the user
does not see the [progress bar] go backward.

If you want the [progress bar] to go back or reset, you can use the
[`set_progress()`] function to force the [progress bar] setting to a
particular value.  For example:

{% include side-by-side.html demo="progress-multi" %}

# <a name="section"></a>The Section Navigation Bar

Stewards can be configured to show a left-hand
[navigation bar] on screens large enough to show one.  The navigation
bar will contain a list of the sections in the interview, as specified
in the [`sections`] initial block or using the [`nav.set_sections()`]
function.  In the navigation bar, the current section will be
highlighted.

Adding the `section` modifier to a question will update the current
section when the Steward asks the question.  This section will
continue to be the current section until another question is reached
that contains a `section` modifier that specifies a different section.

As explained in the documentation for the [`sections`] initial block,
you have the option of referring to a section by a keyword that is
different from the name of the section that is displayed to the user.
If you are using this feature, your `section` modifier needs to refer
to the keyword, not the displayed name.

{% include side-by-side.html demo="sections" %}

You can also set the current section using the [`nav.set_section()`]
function.

# <a name="prevent going back"></a>Disable the Back Button: `prevent going back`

Normally, Stewards allows the user to click the back button to
get back to earlier steps in the interview session.  Sometimes, it is
necessary to prevent the user from doing so.

If you add a `prevent going back` component to a [`question`], the Steward
will not offer the user a back button while showing the question.

{% include side-by-side.html demo="prevent-going-back" %}

There is also a [`prevent_going_back()` function] that accomplishes
the same thing from [Python] code.  This may be more useful than the
`prevent going back` modifier if the need to prevent the user from
clicking the back button depends on the outcome of a process.

# <a name="back button"></a>Adding a Back Button Inside the Question

You can add a "Back" button to the buttons at the bottom of the screen
by setting the `back button` modifier.

{% include side-by-side.html demo="question-back-button-sometimes" %}

If `back button` is set to `True` or to [Python] code that evaluates
to a true value, then the button will be shown.

You can configure this on an interview-wide basis by setting the
[`question back button`] feature.

# <a name="back button label"></a>Changing the Text of the Back Button

When you add a "Back" button to the buttons at the bottom of the
screen by setting the [`back button`] modifier or the [`question back
button`] feature, you can change the text of the button using the
`back button label` modifier.

{% include side-by-side.html demo="question-back-button-sometimes-label" %}

The text of the label can include [Mako] templating.

# <a name="terms"></a><a name="auto terms"></a>Vocabulary `terms` and `auto terms`

Using the modifiers `terms` or `auto terms`, you can specify the
definitions of particular vocabulary terms, and the Steward will
turn them into green hyperlinks.  When the user clicks on the
hyperlink, a popup appears with the word's definition.

You can define the vocabulary terms using `terms` and then put curly
brackets around the instances of the words that you want to become
hyperlinks.

{% include side-by-side.html demo="question-terms" %}

Alternatively, you can define the vocabulary terms using `auto terms`,
in which case you do not need to use curly brackets, and the terms
will be highlighted in green every time they appear in the question.

If you want the terms to be highlighted every time they are used,
whether in curly brackets or not, use `auto terms`.

{% include side-by-side.html demo="question-autoterms" %}

If you want vocabulary terms to be highlighted throughout the
interview, not just for a specific question, you can use `terms` and
`auto terms` as [initial blocks].

# <a name="language"></a>The `language` of the Question

{% highlight yaml %}
---
question: |
  What is the meaning of life?
fields:
  - Meaning of life: meaning_life
---
language: es
question: |
  ¿Cuál es el significado de la vida?
fields:
  - Significado de la Vida: meaning_life
---
{% endhighlight %}

Multilingual [language support] allows a single Steward to asks
questions different ways depending on the user's language.  You can
write questions in different languages that set the same variables.
The Steward will use whatever question matches the active
language.

The value of `language` must be a two-character lowercase [ISO-639-1]
code.  For example, Spanish is `es`, French is `fr`, and Arabic is `ar`.

For more information about how to set the active language, see
[language support].

Instead of explicitly setting a `language` for every question, you can
use [default language] to apply a particular language to the remaining
questions in the [DALang] file (see [initial blocks]).

# <a name="continue button label"></a>Changing the `continue button label`

Some types of questions feature a "Continue" button.  If you want the
label on the button to be something other than the word "Continue,"
add a `continue button label` modifier.

{% include side-by-side.html demo="continue-button-label" %}

The types of questions that feature a "Continue" button include:

* [`field` with `choices`]
* [`fields`]
* [`field` without `buttons` or `choices`]

This modifier also allows you to customize the "Done" button that
appears in [`signature`] questions.

# <a name="generic object"></a>Reusable Questions: `generic object`

{% include side-by-side.html demo="generic-object" %}

`generic object` is a very powerful feature in [DALang] that
allows authors to express questions in general terms.

The above example will cause the Steward to ask "Does Sally Smith
like cats?" if the [interview flow] calls for `neighbor.likes_cats` and
`neighbor` is an object of type [`Individual`] whose name has been set
to "Sally Smith."  The same question will also ask "Does William Jones
like cats?" if the [interview flow] calls for `teacher.likes_cats`, and
`teacher` is an object of type [`Individual`] whose name has been set
to "William Jones."

<a name="x"></a>`x` is a special variable that should only be used in
`generic object` questions.  The above question definition tells
the Steward that if it ever needs the `likes_cats` attribute for
any object of type [`Individual`], it can get an answer by asking this
question.

If your Steward needs a definition for `spouse.likes_cats`, where
`spouse` is an object of type `Individual`, the Steward will first
look for a question that offers to define `spouse.likes_cats`.  If no
such question exists, it will then look for a question that offers to
defined `x.likes_cats`, where the `generic object` is [`Individual`].
If no such question exists, it will look for `generic object`
questions for the parent types of [`Individual`].  The variables that
will be sought, in the order in which they will be sought, are:

* `spouse.likes_cats`
* `x.likes_cats` where `generic object` is [`Individual`].
* `x.likes_cats` where `generic object` is [`Person`].
* `x.likes_cats` where `generic object` is [`DAObject`].

This way, you can provide layers of `generic object` blocks to handle
special cases as well as general cases, based on the object type.  For
example, suppose your [DALang] uses objects of type [`Individual`],
[`Organization`], and [`Person`].  An [`Individual`] is a special type
of [`Person`], and an [`Organization`] is also a special type of
[`Person`].  Suppose you have a general way of asking for a mailing
address ("What is so-and-so's address?"), but you want to have a
special way of asking the question if you need the mailing address of
an [`Organization`] (e.g., "What is ABC Incorporated's primary place
of business?").  You would write a question with `generic object:
Person` for the general case, and a question with `generic object:
Organization` for the special case.  The general question would be
used for objects of type [`Individual`] and [`Person`], and the
special question would be used for objects of type [`Organization`].

You can also use `generic object` [`code`] blocks in a [fallback]
arrangement to capture special cases within object types.  Suppose you
have a function `retrieve_ein()` that can automatically determine an
organization's Employer Identification Number (EIN), but only for
organizations organized as non-profits.  For organizations not
organized as non-profits, you will need to ask the user for the EIN.
You could use the following two blocks to accomplish this:

{% include side-by-side.html demo="generic-object-ein" %}

Whenever the `.ein` of an organization is needed, the [`code`] block
will be run, but the attribute will not be set if the organization is
not a non-profit.  In that case, the Steward will notice that the
attribute is still not defined, and it will "fall back" to the
[`question`] that asks the user to manually enter the EIN.

As explained in the [fallback] section of the documentation, the order
in which these two blocks appear in the [DALang] file matters; the
[`code`] block will be tried first only if it appears later in the
[DALang] file than the [`question`] block.

The `generic object` modifier can be used on any block that sets a
variable, including [`question`], [`code`], [`template`], [`table`],
[`attachment`], and [`objects`], [`objects from file`], [`data`],
[`data from code`].

A similar feature to `generic object` and its special variable `x` is
the special [index variable `i`].  For more information about this
feature, see the [index variable documentation] and the documentation
in the [data structures section].

# <a name="role"></a>The `role` of the Question

{% highlight yaml %}
---
role: advocate
question: Is the client's explanation a sound one?
subquestion: |
  ${ client } proposed the following explanation:
  
  > ${ explanation }

  Is this a legally sufficient explanation?
yesno: explanation_is_sound
---
{% endhighlight %}

If your Steward uses the [roles]({{ site.baseurl}}/docs/roles.html)
feature for multi-user interviews, the `role` modifier in a [`question`]
block will tell the Steward that if it ever tries to ask this
question, the user will need to have a particular role in order to
proceed.

`role` can be a list.
{% highlight yaml %}
role:
  - advocate
  - supervisor
{% endhighlight %}
In this case, the user's role can either "advocate" or "supervisor" in
order to be asked the question.

If the user does not have an appropriate role, the Steward will
look for a question in the [DALang] in which `event` has been set to
`role_event`.

# <a name="reload"></a>Automatically `reload` the Screen

To cause the screen to reload in the web browser after a number of
seconds, use the `reload` modifier.

{% include side-by-side.html demo="reload" %}

If you set `reload` to `True`, the screen on which the question is
asked will reload every 10 seconds.  To use a different number of
seconds, set `reload` to the number of seconds you wish to use.  E.g.,

{% highlight yaml %}
reload: 5
{% endhighlight %}

Since it is not good to reload the screen too quickly, you cannot use
a number of seconds less than four.  If the number of seconds is less
than four, four seconds will be used as the number of seconds.

You can use [Mako] to determine the number of seconds.  If the
`reload` value evaluates to `False` or `None`, the screen will not
reload.

# <a name="id"></a>Tag a Block with a Unique ID

In some situations, you may need to tag a block in your [DALang] with
a unique ID.  You can use the `id` component to do so.

{% highlight yaml %}
---
id: initialize
mandatory: True
code: |
  initial_value = 48
---
{% endhighlight %}

In the absence of an `id` component, the Steward would refer to a
block like this with a name like `Question_3` (if this block was the
third block in the DALang).  But with `id` set to `initialize`,
the Steward will internally refer to this block with the ID
`initialize`.

In most cases, your blocks do not need to have unique IDs.  However,
there are some features in DALang, such as the
[changing order of precedence](#precedence) feature discussed
[below](#precedence), which use `id` component.

Also, in some situations, it can be important to tag your DALang
blocks with a unique name that does not change when the blocks in the
DALang file change.  This is because when a Steward
stores interview answers, it not only stores the current state of the
DALang variables, but it also stores information about which
`mandatory` blocks have run to completion.  When it does so, it tracks
the block using the ID for the block.  If the IDs are arbitrary names
like `Question_3`, users could encounter problems

For example, think about what would happen if a user started working
an interview session on April 3, and got half-way through, and then saved her
answers and logged out, intending to log back in on April 10.  Then
suppose that on April 8, you install a new version of the Steward,
adding new functionality to that interview.  When the user logs back in on April 10, her
interview answers might not be compatible with your new version of the
DALang.  For example, suppose that on April 3, the
[`mandatory`]<span></span> [`code`] block known as `Question_12` ran
to completion.  But when the user logs in on April 10 and resumes the
interview session, the code block formerly known as `Question_12` is now known
as `Question_14`.  When the Steward evaluates her interview
session, it will determine that the [`mandatory`]
<span></span>[`code`] block known as `Question_14` has not run yet, so
it will run that code block.  This might cause information in the
user's session to be overwritten.  You can avoid problems like these
by tagging your code blocks with `id` tags, so that the names of the
blocks do not change between versions of your interview.

Another way to avoid problems with the impact of software upgrades on
existing sessions is to use a different DALang file for each
version of an interview.  So a user that starts
`docassemble.tax:data/questions/tax-controversy-v2.yml` will always
use the same [YAML] file, even when users who started later are using
`docassemble.tax:data/questions/tax-controversy-v3.yml`.

The `id` of a question needs to be set in order to use the
[`forget_result_of()`] function.

# <a name="sets"></a>Manually Indicating that a Block Sets a Variable

Usually, Stewards can figure out which variables a block is
capable of defining.  If a code block consists of:

{% highlight yaml %}
---
code: |
  if hell.temperature_in_celcius == 0:
    claim_is_valid = True
---
{% endhighlight %}

The Steward will try to run this [DALang] block if it needs a definition for
`claim_is_valid`.  Sometimes, however, the Steward needs a hint.

You can explicitly indicate that a block sets a variable using `sets`:

{% highlight yaml %}
---
sets: claim_is_valid
code: |
  if hell.temperature_in_celcius == 0:
    claim_is_valid = True
---
{% endhighlight %}

It also accepts multiple values:

{% highlight yaml %}
---
sets: 
  - claim_is_valid
  - type_of_claim
code: |
  if hell.temperature_in_celcius == 0:
    claim_is_valid = True
    type_of_claim = 'tort'
---
{% endhighlight %}

# <a name="precedence"></a>Changing Order of Precedence

As explained in [how Stewards find questions for variables],
if there is more than one [`question`] or [`code`] block that offers
to define a particular variable, blocks that are later in the [DALang]
file will be tried first.

For example, suppose your friend developed a DALang file with
questions and code blocks that define the variables `client.age`,
`client.eligible`, and `docket_number`.  In your interview, you would
like to define `client.age` and `client.eligible` the same way your
friend does.  You can accomplish this by using [`include`] to
incorporate by reference your friend's DALang file.  But suppose you
don't like the way your friend asks the question to determine
`docket_number`.  No problem; just write a [`question`] in your own
DALang file that defines `docket_number`, and make sure that this
[`question`] appears after the [`include`] block that incorporates
your friend's DALang file.  That way, your question will be used
instead of your friend's.

However, there may be times when the relative placement of blocks
within the DALang file is not a convenient way for you to designate
which questions override other questions.

For example, suppose there are two [`question`] blocks in your
DALang that define `favorite_fruit`.  The second one is always used
because it appears later in the DALang; the second question supersedes
the first.

{% include side-by-side.html demo="supersede-regular" %}

If you wanted the first question to be asked instead, you could
rearrange the order of questions, but what if you wanted to keep the
order the same?

One alternative is to use the `id` and `supersedes` components:

{% include side-by-side.html demo="supersede" %}

In this example, the `id` and `supersedes` components tell the
Steward that the first question takes precedence over the second.

Another way of changing the order of precedence is to use the
[`order` initial block].

# <a name="if"></a>Putting Conditions on Whether a Question is Applicable

If you have multiple [`question`]s in your [DALang] that define a
given variable, you can tell the Steward under what conditions a
given question may be asked.  You do so by using the `if` modifier.

{% include side-by-side.html demo="if" %}

Here's how this works:

* The [`mandatory`] question requires a definition of `answer`, so the
  Steward looks for blocks that offer to define `answer`.
* The Steward considers asking the "What is 2+2?" question.  It
  considers this question first because it appears last in the DALang
  source.
* This question has a condition, so the Steward evaluates the
  [Python expression].  However, the expression depends on the
  variable `user_intelligence`, which is undefined, so the Steward
  asks a question to determine that value of this variable.
* When the user answers the `user_intelligence` question, the
  Steward tries to ask the `mandatory` question again, then
  looks for a definition of `answer`, then considers asking the
  "What is 2+2?" question, then evaluates the `if` expression.
* If the expression evaluates to true, then the Steward asks "What
  is 2+2?"
* If the expression evaluates to false, then the Steward skips the
  question and moves on to the "What is the square root of 50% of 32?"
  question.  It evaluates the `if` statement, and will ask the
  question if the expression evaluates to true.

The content of the `if` modifier must be a [Python expression] or a
list of [Python expression]s.  If a list of expressions is provided,
each expression must evaluate to true in order for the question to be
asked.

# <a name="scan for variables"></a>Turn Off Variable Scanning

By default, Steward looks at every block in your [DALang] and
automatically discerns what variables each block is capable of
setting.  Then, when it is conducting the interview session, if it encounters an
undefined variable it goes through all the blocks that are capable of
defining the variable.  As discussed above, if there are multiple
blocks that are capable of defining a variable, it tries the ones that
are later in the file first, unless an [`order` initial block] or a
[`supersedes` modifier] alters that order.

Sometimes, however, a block that the Steward tries to use to
define a variable is one that you don't want the Steward to even
consider when looking for a way to define a variable.

This is particularly likely to happen when you have code that changes
the values of previously-defined variables.

For example, in the [DALang] below, the intention is that:

* A variable is gathered from the user 
* The variable is reported back to the user
* Then variable is changed through code
* The variable is reported to the user again.

{% include side-by-side.html demo="scan-for-variables-original" %}

However, this DALang does something the author did not intend: when
it goes looking for a definition for `best_color`, the first thing it
does is run the [`mandatory`] code block that depends on
`time_of_day`.  So the first question that gets asked is
`time_of_day`, not `best_color`.  "Ugh!" the author thinks, "that's
not what I wanted!  I only wanted that mandatory code block to be run
later in the interview."

To fix this problem, the author can modify the code block with 
`scan for variables: False`:

{% include side-by-side.html demo="scan-for-variables" %}

Now, when the Steward goes searching for a block that will define
`best_color`, it will disregard the [`code`] block that depends on
`time_of_day`.

This modifier can be used on any block that sets variables to make it
effectively "invisible" to the Stewards's automatic logic.  If a
block is marked with `scan for variables: False`, the [`event`] and
[`sets`] modifiers will still be effective, so you can use them to
explicitly indicate that a block should be tried when the Steward
needs a definition of a particular variable.

In this variation of the DALang, for example, we first want to
gather `best_color` from the user.  Then we want to determine
`best_thing` based on the time of day, and we want a side effect of
setting `best_thing` to be setting `best_color` to something different.

{% include side-by-side.html demo="scan-for-variables-sets" %}

If we did not use `scan for variables: False`, then the Steward
would never ask the user for `best_color`; the [`code`] block would
have been used to get an initial definition of `best_color`.  But by
turning off automatic variable scanning and explicitly indicating that
the [`code`] block should only be used for determining the definition
of `best_thing`, we were able to get the Steward to behave the way
we wanted it to.

# <a name="sets"></a>Specifying which Variables a Block `sets`

As discussed in the previous section, the Steward looks at every
block in your [DALang] and tries to discern what variables each block
is capable of setting.  However, sometimes it is not able to determine
this correctly.
This is most likely to occur when working with [Mako] templates inside of your question block.

To make the situation simpler, we will just look at a [`code`] block.
For example, if you have a [`code`] block that uses a method to set an
attribute on an object, the Steward will not be able to see that
the code block is capable of setting the attribute.  Here is one such
[`code`] block:

{% highlight yaml %}
---
code: |
  user.initializeAttribute('allergies', DAList)
---
{% endhighlight %}

If you want the Steward to run this [`code`] block when it needs a
definition of `user.allergies`, then you need to add a `sets` modifier:

{% highlight yaml %}
---
sets: user.allergies
code: |
  user.initializeAttribute('allergies', DAList)
---
{% endhighlight %}

You can also give `sets` a list of variables:

{% highlight yaml %}
---
sets: 
  - user.allergies
  - user.skills
code: |
  user.initializeAttribute('allergies', DAList)
  user.initializeAttribute('skills', DAList)
---
{% endhighlight %}

# <a name="comment"></a>Hidden `comment`s

To make a note to yourself about a question, which will not be seen by
the end user, you can use a `comment` component.  It will be ignored
by the Steward, so it can contain any valid [YAML].

{% include side-by-side.html demo="comment-weather" %}

[YAML]: https://en.wikipedia.org/wiki/YAML
[`event`]: {{ site.baseurl }}/docs/fields.html#event
[`sets`]: #sets
[`order` initial block]: {{ site.baseurl }}/docs/initial.html#order
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[how Stewards find questions for variables]: {{ site.baseurl }}/docs/logic.html#variablesearching
[YAML]: https://en.wikipedia.org/wiki/YAML
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[language support]: {{ site.baseurl }}/docs/language.html
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[Mako]: http://www.makotemplates.org/
[HTML5 audio tag]: http://www.w3schools.com/html/html5_audio.asp
[HTML5 video tag]: http://www.w3schools.com/html/html5_video.asp
[YouTube]: https://www.youtube.com/
[Vimeo]: https://vimeo.com/
[`prevent_going_back()` function]: {{ site.baseurl }}/docs/functions.html#prevent_going_back
[special variables]: {{ site.baseurl }}/docs/special.html
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`image sets`]: {{ site.baseurl }}/docs/initial.html#image sets
[`images`]: {{ site.baseurl }}/docs/initial.html#images
[default language]: {{ site.baseurl }}/docs/initial.html#default language
[progress bar]: {{ site.baseurl }}/docs/initial.html#features
[navigation bar]: {{ site.baseurl }}/docs/initial.html#navigation bar
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`Person`]: {{ site.baseurl }}/docs/objects.html#Person
[`DAObject`]: {{ site.baseurl }}/docs/objects.html#DAObject
[`Organization`]: {{ site.baseurl }}/docs/objects.html#Organization
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`microphone`]: {{ site.baseurl }}/docs/fields.html#microphone
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[`field` with `choices`]: {{ site.baseurl }}/docs/fields.html#field with choices
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
[`field` without `buttons` or `choices`]: {{ site.baseurl }}/docs/fields.html#field
[`signature`]: {{ site.baseurl }}/docs/fields.html#signature
[Javascript]: https://en.wikipedia.org/wiki/JavaScript
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[`features`]: {{ site.baseurl }}/docs/initial.html#features
[fallback]: {{ site.baseurl }}/docs/logic.html#fallback
[`code`]: {{ site.baseurl }}/docs/code.html#code
[`nav.show_sections()`]: {{ site.baseurl}}/docs/functions.html#DANav.show_sections
[`nav.set_section()`]: {{ site.baseurl}}/docs/functions.html#DANav.set_section
[`nav.set_sections()`]: {{ site.baseurl}}/docs/functions.html#DANav.set_sections
[`sections`]: {{ site.baseurl}}/docs/initial.html#sections
[index variable `i`]: {{ site.baseurl }}/docs/fields.html#index variables
[data structures section]: {{ site.baseurl }}/docs/groups.html
[index variable documentation]: {{ site.baseurl }}/docs/fields.html#index variables
[`supersedes` modifier]: #precedence
[Python expression]: http://stackoverflow.com/questions/4782590/what-is-an-expression-in-python
[`get_progress()`]: {{ site.baseurl}}/docs/functions.html#get_progress
[`set_progress()`]: {{ site.baseurl}}/docs/functions.html#set_progress
[Font Awesome]: https://fontawesome.com
[`use font awesome`]: {{ site.baseurl}}/docs/config.html#use font awesome
[Configuration]: {{ site.baseurl}}/docs/config.html
[inline icons]: {{ site.baseurl}}/docs/markup.html#emoji
[`interview help`]: {{ site.baseurl}}/docs/initial.html#interview help
[`question help button`]: {{ site.baseurl}}/docs/initial.html#question help button
[`question back button`]: {{ site.baseurl}}/docs/initial.html#question back button
[`back button`]: #back button
[`forget_result_of()`]: {{ site.baseurl}}/docs/functions.html#forget_result_of
[DALang]: {{ site.baseurl }}/docs/interviews.html#yaml
[server]: {{ site.baseurl }}/docs/installation.html
[interview flow]: {{ site.baseurl }}/docs/logic.html
[`template`]: {{ site.baseurl}}/docs/template.html#template
[`table`]: {{ site.baseurl}}/docs/template.html#table
[`attachment`]: {{ site.baseurl}}/docs/documents.html#attachment
[`objects`]: {{ site.baseurl}}/docs/initial.html#objects
[`objects from file`]: {{ site.baseurl}}/docs/initial.html#objects from file
[`data`]: {{ site.baseurl}}/docs/initial.html#data
[`data from code`]: {{ site.baseurl}}/docs/initial.html#data from code