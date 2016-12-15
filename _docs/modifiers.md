---
layout: docs
title: Question modifiers
short_title: Question Modifiers
---

There are a number of optional modifiers that can be included in
[`question`] blocks to control the appearance or behavior of the
question.

# <a name="audio"></a>`audio`

{% include side-by-side.html demo="audio" %}

The `audio` modifier allows you to add audio to your questions.  An
audio player will appear above the question, and the user can press
play to hear the sound.

The filename can be constructed with [Mako].  A plain file path will
be assumed to point to a file in the `static` directory of the package
in which the [YAML] file resides.  A package reference may also be
included: e.g., `docassemble.demo:data/static/schumann-clip-3.mp3`.
A URL beginning with `http` or `https` may also be provided.

You can also play uploaded files:

{% include side-by-side.html demo="upload_audio" %}

Note that in this example, we use `file` as the `datatype`, which is
the standard way to upload files.  You can also use the `datatype` of
[`microphone`], which in some browsers (mostly on mobile platforms) will
launch an audio recording app to create the file to upload.

{% include side-by-side.html demo="upload_audio_microphone" %}

**docassemble** uses the [HTML5 audio tag] to allow users to play the
audio.  Not all browsers support every type of audio file.  In order
to make your audio files accessible to the greatest number of users,
then if you provide static audio files, you should include files in
both `mp3` and `ogg` format.

For example, if your `audio` declaration points to a file, such as
`nyc_question.mp3`, then your interview package should contain a file
called `nyc_question.mp3` in the `data/static` directory.  If you also
include an OGG version of this audio file, called `nyc_question.ogg`,
in the same directory, then **docassemble** will make both files
available to the user, and the user's browser will use whichever file
works.  In your `audio` declaration, you can refer to either the `mp3`
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

If you refer to an uploaded file, **docassemble** will take care of
providing both `mp3` and `ogg` versions.  When users upload an audio
file, **docassemble** tries to convert it to the appropriate formats.
For this to work, ffmpeg and pacpl must be installed on your system.
Currently, **docassemble** can handle audio files uploaded in `mp3`,
`ogg`, `3gpp`, and `wav` formats.  If you need to be able to process
another type of audio file, **docassemble**'s source code can probably
be modified to support that audio type.

Note that there a number of limitations to playing audio in browsers.
For example, older Android devices will not play audio retrieved
through https, but will play the same audio retrieved through http.

See [special variables] for information about **docassemble**'s
automatic text-to-speech features.

# <a name="video"></a>`video`

The `video` declaration is just like the [`audio`](#audio) declaration
except that it displays a video instead of an audio file.

{% highlight yaml %}
---
question: Are you traveling to New York City?
yesno: going_to_nyc
video: nyc_tourism.mp4
---
{% endhighlight %}

**docassemble** uses the [HTML5 video tag] to allow users to play the
audio.  Just as you should include both `mp3` and `ogg` audio files,
you should include both `mp4` and `ogv` video files, so that users of
many different browsers will all be able to see your videos.  These
are the two formats that the [HTML5 video tag] most widely supports.

If you refer to an uploaded video file, **docassemble** will take care
of providing both `mp4` and `ogv` versions.  When users upload a
video file, **docassemble** tries to convert it to the appropriate
formats.  For this to work, ffmpeg and pacpl must be installed on your
system.  Currently, **docassemble** can handle videos uploaded in
`mp4`, `ogv`, and `mov` formats.  If you need to be able to process
another type of video, **docassemble**'s source code can probably be
modified to support that video type.

You can also use the `video` declaration to embed [YouTube] and
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
declaration on one line, write `video: "[VIMEO 96044910]"`.

# <a name="help"></a>`help`

{% include side-by-side.html demo="help-damages" %}

In the web app, users can use the navigation bar to toggle between the
"Question" tab and the "Help" tab.  The contents of the "Help" tab
consist of the contents of any `help` statements in the question being
presented, followed by the contents of any `interview help` blocks
contained within the interview.

You can add audio to your help text:

{% include side-by-side.html demo="help-damages-audio" %}

You can also add video to help text using the `video` declaration.

# <a name="decoration"></a>`decoration`

{% include side-by-side.html demo="decoration" %}

The `decoration` modifier adds an icon to the right of the
[`question`] text.  In the example above, `kids` has been defined in
an [image sets] or [images] block.

# <a name="progress"></a>`progress`

A **docassemble** interview can be configured to show a
[progress bar].  This will show the user a progress indicator to give
the user a sense of how much longer the interview will take.

The progress along the bar at any question needs to be set with the
`progress` modifier.  For example:

{% include side-by-side.html demo="progress" %}

# <a name="prevent_going_back"></a>`prevent_going_back`

Normally, **docassemble** allows the user to click the back button to
get back to earlier steps in the interview.  Sometimes, it is
necessary to prevent the user from doing so.

If you add a `prevent_going_back` directive to a [`question`], the web
app will not offer the user a back button while showing the question.

{% include side-by-side.html demo="prevent-going-back" %}

There is also a [`prevent_going_back()` function] that accomplishes
the same thing from [Python] code.  This may be more useful than the
`prevent_going_back` modifier if the need to prevent the user from
clicking the back button depends on the outcome of a process.

# <a name="language"></a>`language`

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

**docassemble**'s [language support] allows a single interview to asks
questions different ways depending on the user's language.  You can
write questions in different languages that set the same variables.
**docassemble** will use whatever question matches the active
language.

The value of `language` must be a two-character lowercase [ISO-639-1]
code.  For example, Spanish is `es`, French is `fr`, and Arabic is `ar`.

For more information about how to set the active language, see
[language support].

Instead of explicitly setting a `language` for every question, you can
use [default language] to apply a particular language to the remaining
questions in the file (see [initial blocks]).

# <a name="continue button label"></a>`continue button label`

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

# <a name="generic object"></a>`generic object`

{% highlight yaml %}
---
generic object: Individual
question: |
  So, ${ x.is_are_you() } a defendant in this case?
yesno: x.is_defendant
---
{% endhighlight %}

`generic object` is a very powerful feature in **docassemble** that
allows authors to express questions in general terms.

The above example will cause **docassemble** to ask "So, is John Smith
a defendant in this case?" if the interview logic calls for
`neighbor.is_defendant` and `neighbor` is an object of type
[`Individual`] whose name has been set to "John Smith."  Or, if the
interview logic calls for `user.is_defendant`, **docassemble** will
ask, "So, are you a defendant in this case?"

<a name="x"></a>`x` is a special variable that should only be used in
`generic object` questions.  This question definition tells
**docassemble** that if it ever needs an `is_defendant` attribute for
any object of type [`Individual`], it can get an answer by asking this
question.

# <a name="role"></a>`role`

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

If your interview uses the [roles]({{ site.baseurl}}/docs/roles.html)
feature for multi-user interviews, the `role` modifier in a [`question`]
block will tell **docassemble** that if it ever tries to ask this
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

If the user does not have an appropriate role, **docassemble** will
look for a question in the interview in which `event` has been set to
`role_event`.

# <a name="reload"></a>`reload`

To cause the screen to reload in the web browser after a number of
seconds, use the `reload` modifier.

{% include side-by-side.html demo="reload" %}

If you set `reload` to `true`, the screen on which the question is
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

# <a name="comment"></a>`comment`

To make a note to yourself about a question, which will not be seen by
the end user, you can use a `comment` statement.  It will be ignored
by **docassemble**, so it can contain any valid [YAML].

{% include side-by-side.html demo="comment-weather" %}

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
[image sets]: {{ site.baseurl }}/docs/initial.html#image sets
[images]: {{ site.baseurl }}/docs/initial.html#images
[default language]: {{ site.baseurl }}/docs/initial.html#default language
[progress bar]: {{ site.baseurl }}/docs/initial.html#features
[`Individual`]: {{ site.baseurl }}/docs/objects.html#Individual
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`microphone`]: {{ site.baseurl }}/docs/fields.html#microphone
[`field` with `choices`]: {{ site.baseurl }}/docs/fields.html#field with choices
[`fields`]: {{ site.baseurl }}/docs/fields.html#fields
[`field` without `buttons` or `choices`]: {{ site.baseurl }}/docs/fields.html#field
[`signature`]: {{ site.baseurl }}/docs/fields.html#signature
