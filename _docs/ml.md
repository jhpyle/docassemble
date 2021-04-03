---
layout: docs
title: Machine learning
short_title: Machine Learning
---

**docassemble** allows you to use [machine learning] in your
interviews.

# What is machine learning?

Machine learning is like "fuzzy logic."  A computer can be trained to
recognize patterns.

A common application of machine learning is "sentiment analysis" of
phrases, such as Twitter messages.  The goal is for the computer to be
able to guess the emotional state of the author of a message based on
the words that the author used.  Consider the following examples:

* I'm having a great day.
* The weather is just lovely!
* This day sucks.
* The weather is so awful.

To train the computer to recognize emotion, a human being will give
the computer examples like these along with an indication of what the
"sentiment" is.  In the examples above, the human would tell the
computer that the first two examples are "happy" messages, and the
second two are "unhappy" messages.

The computer then uses statistics to measure the association between
words and emotion.  After reading the first example, it will associate
"great" and "day" with "happy."  After reading the second example, it
will associate "weather" and "lovely" with "happy."  After reading the
third example, it will associate "day" and "sucks" with "unhappy."

After being "trained" with these three examples, if the computer was
presented with the sentence "This day is lovely," and asked to
"classify" the sentence as either "happy" or "unhappy," it could easily
figure out the correct answer.  It would consider the word "day" and
it would remember that sometimes "day" is associated with "happy" and
other times with "unhappy," so it would find this word unhelpful in
determining sentiment.  But the only other time it had seen "lovely"
was in the context of a "happy" sentence, so the presence of the word
"lovely" would suggest that the sentence is a "happy" one.

This is an example of a simple statistical "model" that looks at word
frequencies.  Other models could be more sophisticated; they could
automatically discard words like "is" and "a," they could look at the
ordering of words, and treat adjectives as more important than nouns.

Typically, models are general-purpose.  A model that can be trained to
classify sentences as "happy" or "unhappy" could also be trained to
classify sentences as "botany-related," "entomology-related," or
"ornithology-related."  Some models can only handle two possible
outcomes while others can handle any number of possible outcomes.

Once a model is trained, it can be used to "predict" a classification
based on given input.  The outcome of the prediction will the
assignment of a probability to each possible outcome.  The outcome
with the highest probability will be the "best guess."  For example, a
model trained to identify "happy" and "unhappy" statements might
predict that the phrase "I am feeling good today" has a 76% chance of
being "happy" and a 24% chance of being "unhappy.

The information you put into model and the information you get out of
a model as a prediction can both be expressed as "variables."  The
predicted value is the "dependent variable," while the information
with which the model is trained is known as the "independent
variable."  The dependent variable depends on, or "is a function of"
the independent variable or variables.  In the "sentiment analysis"
application discussed above, sentences like "I am happy today," are
"independent" variables, while terms like "happy" or "unhappy" are
"dependent" variables.  The classification variable (the value of
which is "happy" or "unhappy") _depends on_ the input variable (the
value of which which is "I am happy today," or "My life sucks," etc.).
The terminology of "dependent" and "independent" variables is the
terminology of [regression analysis] in the field of statistics.
(Machine learning is actually just a kind of regression analysis.)

Once a model has been "trained," it can be "tested" to see how
accurate its predictions are.  For example, the "sentiment analysis"
model discussed above could be tested by running 100 predictions on a
variety of happy and unhappy phrases and measuring how often the
"predictions" are correct.  If the model correctly classifies happy
statements as "happy" about 95% of the time, and also classifies
unhappy statements as "unhappy" about 95% of the time, then it
performs pretty well.

When "testing" the performance of a trained model, it is important to
use different data than the data with which the model was trained.  If
the model was trained to know that "I am feeling good today" is
classified as "happy," then if you ask the model to classify the
phrase "I am feeling good today," it is likely to give you the correct
answer.  However, that does not mean the model is any good at
classifying phrases it has never heard before.

It is helpful to understand the concepts of "models," "training,"
"testing," and "prediction," and the difference between "dependent"
and "independent" variables.  Once you understand these general
concepts, you can make use of machine learning without knowing any
further information about how particular models work or the statistics
underlying them.  All that you need to do is make sure you "train" the
model with a sufficiently diverse set of data.  If you had the most
sophisticated model in the world but you only trained it with "happy"
sentences, it wouldn't be able to recognize an "unhappy" sentence.

Some models are complex and proprietary, but nevertheless are very
easy to use.  IBM Watson, for example, which famously won a Jeopardy!
competition, is available over the internet to the general public for
a fee.  Nobody outside of IBM knows exactly how it works, but
nevertheless numerous customers have developed applications that use
IBM Watson to classify text.  You do not need to know how a model
works in order to evaluate whether it is any good; all you need to do
is thoroughly train and test it.

This section has discussed "natural language classifiers" as an
example of machine learning.  There are other types of classifiers as
well.  For example, when you shop on Amazon.com, the site gives you
suggestions about what other products you might like.  In that case,
the dependent variable is product that is purchased, and the
independent variables include various types of data such as other
products that a purchaser has purchased.

The [next section](#howtouse) will explain a simple way that you can
use natural language classifiers in your interviews.  There is also a
[lower-level way] to use **docassemble**'s machine learning
capabilities, which you can access by including [Python] code in your
interview.  This includes an option for doing
[machine learning on data](#RandomForestMachineLearner).

# <a name="howtouse"></a>How to use machine learning

In your **docassemble** interviews, instead of asking a
multiple-choice question, you can ask the user to express something in
their own words, then use a machine learning model, which you will
need to train, to guess at the user's meaning.

## Setting variables

You can use machine learning in your **docassemble** interviews by
using the `ml` or `mlarea` [data types].

{% include demo-side-by-side.html demo="predict-happy-sad" %}

The variable `mood` will be an [object] of type [`DAModel`].  The
object will have several attributes:

* `mood.prediction` is what the machine learning model guesses is the
  most likely classification of the input.  The value of `.prediction`
  is a text string (e.g., `'happy'` or `'sad'`).  These values are not
  in the interview, but come from the training process (more on that
  later).  Writing `${ mood }` in a [Mako] template (as in the example
  above) or `str(mood)` in [Python] code will return
  `mood.prediction`.  If there is no training data upon which to make
  a prediction, the value is `None`.
* `mood.probability` is the probability (a number between 0 and 1) of
  the most likely prediction, according to the machine learning model.
* `mood.predictions` is a [list] of [2-tuples] representing all of the
  model's predictions that have non-zero probability.  The first item
  of the tuple is the prediction (e.g., `'happy'`) and the second item
  is the probability (e.g., `0.4`)
* `mood.text` is the literal text that the user provided

The probabilities can give you a sense of how reliable the
classification is.

If a model is well-trained and shows good test results, you can use
the probabilities as a gauge of whether the classification is a
"borderline" case or not.  You might want to have logic in your
interview that asks additional questions if there are two
`.predictions` and they both have probabilities around 0.5, whereas
you might skip those questions if the first probability is greater
than 0.95.

Note that if your model is not well-trained, it will report
probabilities of 1.0 even when the classification is false.

If you want the user to have more space to write, you can use
`datatype: mlarea`:

{% include demo-side-by-side.html demo="predict-happy-sad-area" %}

Whenever a machine learning variable is set, the user's input will be
saved as a not-yet-classified item in the training data for the
machine learning model associated with the variable, so that it can be
[trained](#train) later.  If you do not want the input to be saved in
the training data, you can set `keep for training` to `False`:

{% highlight yaml %}
question: |
  Describe how you feel.
fields:
  - no label: mood
    datatype: ml
    keep for training: False
{% endhighlight %}

The value of `keep for training` can also be [Python] code that
evaluates to a true or false value.  For example:

{% highlight yaml %}
question: |
  Describe how you feel.
fields:
  - no label: mood
    datatype: ml
    keep for training: not is_confidential
---
question: |
  Are you a CIA agent?
yesno: is_confidential
{% endhighlight %}

If you use the variables created by `datatype: ml` and `datatype:
mlarea` in [Python] code, don't forget that they are objects, and you
need to refer to the attribute `.prediction` to get the prediction:

{% highlight yaml %}
code: |
  if mood.prediction == 'happy':
    recommended_genre = 'drama'
  else:
    recommended_genre = 'comedy'
{% endhighlight %}

If you write `if mood == 'happy'`, the result will always be `False`,
because `mood` itself is an [object].

## <a name="train"></a>Training

To train the machine learning model, select "Train" from the main
menu.  Users need to have [privileges] of `admin` or `trainer` in
order to access the training area.

Training sets are organized by [package], then by interview, and then
by variable name.  In the example interview above, the interview is
available at `docassemble.demo:data/questions/predict-happy-sad.yml`.
To train the machine learning model associated with the variable
`mood`, you would go into the `docassemble.demo` package, then into
the `predict-happy-sad` interview, and then select the model for
`mood`.

The training page for `mood` allows you to manage a list of "items" in
the training set for the model.  Each item has an "Input" value and an
"Actual" value.  The "Input" value is the "independent variable" and
the "Actual" value is the "dependent" variable.

Items in the training set that do not have "Actual" values yet are
considered not yet "classified."  By default, only not-yet-classified
items are shown.  You can click the "Show entries that are already
classified" link to toggle whether already-classified items are
hidden.  This will also affect the item counts that you see when you
are browsing through the "packages," "interviews," and "models."

"Prediction" values are shown for each "Input" value.

There are three ways to set or edit the "Actual" values:

1. Type in the value in the "Actual" text box;
2. Select the correct value from the pull-down list next to the text
   box; or
3. Press one of the "Prediction" buttons.

You can also delete an item by checking the "Delete" checkbox.

Changes take effect when you press the "Save" button.

## <a name="packaging"></a>Packaging your training sets

When you [package] your interview for publishing, you will probably
also want to include the training data along with it, since the
functionality of your interview depends on that training data.

**docassemble** has a number of features to facilitate the packaging
of machine learning training data.

In the [Playground], if you develop an interview in the file
`name-change.yml`, then a file called `ml-name-change.json` will be
created in the [Sources folder].  This file will contain the
items in the training set that have been classified, in [JSON] format.

When you go to the [Packages folder] of the [Playground] to build a
package for your interview, include the file `ml-name-change.json` in
your [package].  Then, when your package is installed on another
server, the training data will be shipped with it.  When someone runs
the `name-change.yml` interview on that server, the training data in
the `ml-name-change.json` file will be used.

If you have a [package] containing an interview called
`name-change.yml`, that interview will live in the `data/questions`
directory of the [package].  The training data will live in the
`data/sources` directory of the [package] in the file called
`ml-name-change.json`.  The naming convention for these data files is
to start with the name of the interview [YAML] file, add `ml-` to the
beginning, and replace `.yml` with `.json`.

### Details about how automatic importing works

For efficiency, training data are stored in a database.

When an interview runs, and it contains machine learning variables,
**docassemble** figures out the machine learning storage area for the
interview.  If the interview is called `predict-happy-sad.yml` and it
is part of the `docassemble.demo` package, **docassemble** will see if
there are any models in the database with a name that begins with
`docassemble.demo:data/sources/ml-predict-happy-sad.json`.  Or, if the
[`machine learning storage`] specifier is set, **docassemble** will
use that name instead.  If no models are found, **docassemble** will
read the [JSON] file and import into its database the training data
for the models found in the file.

However, if at least one model _is_ found, the [JSON] file will be
ignored.

When you download a file like `ml-name-change.json` from the
[Sources folder] of the playground, or use the [Packages folder] to
include the file in a package you are downloading or publishing, then
before using the file, **docassemble** will overwrite the file's
contents with an export from the current state of the database.

## <a name="variable sharing"></a>Sharing training sets for specific variables

You might have multiple machine learning variables in your interview
that represent the same concept but have different variable names.  It
would be duplicative to have to train each variable separately.  You
can avoid this duplication by using the `using` modifier to specify
what training set a machine learning variable should use:

{% include demo-side-by-side.html demo="predict-activity" %}

In this example, the two questions, "What kind of work do you do now?"
and "What kind of work do you see yourself doing in five years?" refer
to separate things, but for purposes of training a machine learning
model, the underlying concept is the same: classifying a description
of a job.  By adding `using: present_activity` to the specification of the
variable `future_activity`, we indicate that the `future_activity`
variable should use the same training set as the variable
`present_activity`.

Training set names are just names; if you do not use the `using`
modifier, the default name for the training set will be the same as
the name of the variable.  You can use any name you want; it does not
have to be the name of an existing variable.

For example, here is another way of sharing a common training set
across two variables:

{% include demo-side-by-side.html demo="predict-activity-activity" %}

In this interview, there is no variable named `activity`.  The name
`activity` is just a name.  In fact, `activity` is a better name for
the common training set than `present_activity`.

The `using` modifier can also be used to share training sets across
interviews.  For example, suppose you are writing an interview that
uses several machine learning variables, one of which is
`legal_problem`.  You had previously developed an interview called
`triage.yml` that included a variable called `legal_issue`, and you
spent significant time training that variable to spot legal issues.
Your variable `legal_problem` represents the same concept as
`legal_issue`.  You don't want to repeat all that training work for
your new variable `legal_problem`.  Luckily, you can use `using` so
that `legal_problem` uses the training data of the `triage.yml`
interview.

{% highlight yaml %}
question: |
  What is your legal problem?
fields:
  - Problem: legal_problem
    datatype: mlarea
    using: ml-triage.json:legal_issue
{% endhighlight %}

Note that you need to refer to the name of the [JSON] file for the
other interview's data set.  The name of the [JSON] file and the name
of the variable need to be separated by a colon.

You can also use `using` to refer to data sets in other packages:

{% highlight yaml %}
question: |
  What is your legal problem?
fields:
  - Problem: legal_problem
    datatype: mlarea
    using: docassemble.issuespotting:data/sources/ml-triage.json:legal_issue
{% endhighlight %}

Here, the `using` designator points to a file in a package, using the
file naming convention employed throughout **docassemble** (the package
name followed by colon, followed by the path to the file within the
package).  The standard file designator is followed by a colon and
the name of the "model" within that file.

## Using another interview's training sets

If you have an interview that uses machine learning, and you would
like all of its `datatype: ml` and `datatype: mlarea` variables to use
the data sets of a different interview, you can tell your interview to
use that other interview's data sets.  Include the [initial block]
called [`machine learning storage`].

{% highlight yaml %}
---
machine learning storage: ml-some-other-interview.json
---
{% endhighlight %}

The above example assumes that there is a data set in the current
package (or the same [Playground]) by the name of
`ml-some-other-interview.json`.

You can also tell your interview to use the data sets of an interview
in another package:

{% highlight yaml %}
---
machine learning storage: docassemble.someotherpackage:data/sources/ml-some-interview.json
---
{% endhighlight %}

The above example assumes that there is a data set in the
`docassemble.someotherpackage` package by the name of
`ml-some-other-interview.json`.

Note that there is no "permissions" system for the training data on a
**docassemble** server.  Anyone can change another package's training
data, and other people can change your package's training data.

## Using training sets by other names

The default name of a training set starts with the name of an
interview file, like `some-interview.yml`, then add `ml-` to the
beginning, replace `.yml` with `.json`, and to locate this file in the
`data/sources` subdirectory of the [package] (or the [Sources folder]
of the [Playground]).

However, it is allowable to use training set names that do not
correspond with a particular interview.  For example, you might want
to include the following in all of the interviews in a [package]:

{% highlight yaml %}
---
machine learning storage: ml-common.json
---
{% endhighlight %}

Then all of the interviews in your package would share the same
training data storage area.  If any of the variable names overlapped
across interviews, they would use the same training data.  It would
not matter that there is no interview named `common.yml` in your
[package].

However, there is one small downside to using data training sets
with names that do not correspond with the name of your interview:
when you go to [train](#train) models within that file, and the
training data set is empty, **docassemble** will not be able to
automatically figure out the names of the variables that need to be
trained.  You will need to run your interview (getting `None`
predictions for each variable) before you can start
[training](#train) the variables.

## Using global training sets

It is also possible to store machine learning training data in areas
that are not part of a package by using the special prefix `global`:

{% highlight yaml %}
question: |
  Describe how you feel.
fields:
  - no label: mood
    datatype: ml
    using: global:feelings
{% endhighlight %}

Normally, the full name of a model has package and file
information in it, such as
`docassemble.demo:data/sources/ml-predict-happy-sad.json:mood`.
In this example, however, the name of the model will simply be
`feelings`.  In the [training interface](#train), the model can be
located under the "Global" category.

# <a name="lowerlevel"></a>Lower-level interface

If you are an advanced interview developer and you want to be able to
control **docassemble**'s machine learning system more directly, you
can follow the steps in this section and the following sections.  Most
developers, however, will be able to use machine learning with the `ml`
and `mlarea` data types, as described in the
[previous section](#howtouse).

## <a name="predicting"></a>Predicting

Here is an example of the use of `SimpleTextMachineLearner` to predict
the classification of user-supplied text using an already-trained
model.

{% include side-by-side.html demo="ml-predict" %}

First, we create an object `ml`.

{% highlight yaml %}
  ml = SimpleTextMachineLearner('demo')
{% endhighlight %}

A `SimpleTextMachineLearner` is **docassemble**'s name for a
particular type of classification model.  `'demo'` is the name of a
set of training data, which is unique to your **docassemble**
instance.

To generate a prediction, we run the `predict()` method on the `ml`
object:

{% highlight yaml %}
  predictions = ml.predict(phrase)
{% endhighlight %}

Here, `phrase` is a piece of text that we gather from the user
using a [question].

{% highlight yaml %}
---
question: |
  Enter some text.
fields:
  - no label: phrase
---
{% endhighlight %}

The `predict()` method returns a list of predicted values, in order
from most likely to least likely.  So in this example, the most likely
prediction is the first entry, namely `predictions[0]`.

{% highlight yaml %}
subquestion: |
  % if len(predictions):
  The prediction was:

  > ${ predictions[0] }
  % else:
  There is not enough training data
  to make a prediction yet.
  % endif
{% endhighlight %}

Note that if the model has no training data available, the result of
`predict()` will be an empty list.  The example anticipates this
possibility.  It checks to see if the length of the list
(`len(predictions)`) is non-zero, and outputs a special message if it
is zero.

## Training

When you create a machine learning object by doing `ml =
SimpleTextMachineLearner('demo')`, `'demo'` refers to the name of a
training set.  The training set is stored in the **docassemble**
database on the server.  Any other interview that runs on the server
can use the same training data.

If you want your training data to be unique to your interview, follow
the standard naming convention for machine learning data sets, which
is to refer to a [JSON] file in the [sources folder] of a package
(whether or not the file actually exists), followed by a colon,
followed by a name.  For example:
`docassemble.oklahomafamilylaw:data/sources/ml-custody.json:reason_for_custody`.
This is the convention used by the [higher-level interface](#howtouse)
described above.  (The reference to a [JSON] file facilitates the
automatic importing of data from packages.)

There are several ways to add data to a training set.

### <a name="save"></a>Saving data for classification later

The `save_for_classification()` method of the
`SimpleTextMachineLearner` object will store a phrase in the training
data so that it can be classified later.  The example interview in the
previous section can be adapted to do this with the addition of just
one line:

{% include side-by-side.html demo="ml-save-and-predict" %}

Doing `ml.save_for_classification(phrase)` will put the phrase into
the training data set as an inactive entry.  The "independent"
variable will be set, but the "dependent" variable will not be set.

You can classify inactive phrases in your training set using a
**docassemble** interview like the following.

{% include side-by-side.html demo="ml-classify" %}

Here is the core code block of this interview:

{% highlight yaml %}
---
initial: True
code: |
  if defined('classification'):
    entry_to_classify.classify(classification)
    del classification
  entry_to_classify = ml.one_unclassified_entry()
  if entry_to_classify is not None:
    need(classification)
---
{% endhighlight %}

The [`.one_unclassified_entry()`] method will return a not-yet-classfied
entry in the training set.  If there are not any not-yet-classfied
entries, this method will return `None`.  It returns an object
representing the entry in the training set.  To provide a
classification for the entry, you call the [`.classify()`] method on the
object.

This interview works by doing the following:

1. It sees if there is a not-yet-classified entry, and stores it in
the variable `entry_to_classify` (by doing `entry_to_classify =
ml.one_unclassified_entry()`).
2. It asks the user how the entry should be classified, and stores the
result in the variable `classification`,
3. It modifies the `entry_to_classify` entry in the training set by
setting the "dependent variable" to the value of `classification` (by
doing `entry_to_classify.classify(classification)`).
4. It then repeats the process again.

### Loading training data in bulk

You can also load training data from a [JSON] or [YAML] file.  When
you create the `SimpleTextMachineLearner`, include as a second
argument the name of a file:

{% highlight python %}
ml = SimpleTextMachineLearner('demo2', 'training-data.json')
{% endhighlight %}

The file is presumed to exist in the [sources folder] of the current
package.  You can also specify a more explicit path:

{% highlight python %}
ml = SimpleTextMachineLearner('demo2', 'docassemble.demo:data/sources/training-data.json')
{% endhighlight %}

You can also reference a file that exists on the internet somewhere.

{% highlight python %}
ml = SimpleTextMachineLearner('demo2', 'https://example.com/data/training-data.json')
{% endhighlight %}

The file needs to contain an array of dictionaries (associative
arrays) with the keys "independent" and "dependent."

Here is an example of a valid [JSON] file:

{% highlight json %}
[
  {
    "independent": "I am pretty good",
    "dependent": "happy"
  },
  {
    "independent": "I am feeling down",
    "dependent": "unhappy"
  }
]
{% endhighlight %}

Here is an example of a valid [YAML] file:

{% highlight yaml %}
- independent: I am quite happy
  dependent: happy
- independent: I am despondent
  dependent: unhappy
- independent: I am over the moon
  dependent: happy
- independent: My life is meaningless
  dependent: unhappy
{% endhighlight %}

### Adding training data with code

You can also use code within your interview to add training data to a
training set when you know both the "independent" and the "dependent"
variable.  You can do so with the [`.add_to_training_set()`] method of
the `SimpleTextMachineLearner` object.

{% highlight python %}
ml.add_to_training_set("I am feeling blue", "unhappy")
{% endhighlight %}

The first parameter is the independent variable, and the second
parameter is the dependent variable.

The [`.add_to_training_set()`] method is explained in more detail in
the next section, which explains all of the methods available.

# <a name="DAModel"></a><a name="SimpleTextMachineLearner"></a>The `SimpleTextMachineLearner` object

The `SimpleTextMachineLearner` is an object for interacting with
**docassemble**'s machine learning features.  It uses the k-nearest
neighbor (kNN) algorithm from the [`pattern.vector`] package.

{% highlight python %}
ml = SimpleTextMachineLearner('abc')
{% endhighlight %}

The first parameter sets the attribute `group_id`, which is the name
of the data set to be used for training and/or prediction.  Assuming
that the above code exists in the interview `alphabet.yml` in the
`docassemble.demo` package, the `group_id` will be set to
`docassemble.demo:data/sources/ml-alphabet.json:abc`.  See the
[`machine learning storage`] specifier for information about modifying
this value.

It is also possible to set the `group_id` to an explicit value.  You
can do:

{% highlight python %}
ml = SimpleTextMachineLearner(group_id='abcdefg')
{% endhighlight %}

or:

{% highlight python %}
ml = SimpleTextMachineLearner()
ml.group_id = 'abcdefg'
{% endhighlight %}

Another parameter of the [`SimpleTextMachineLearner`] is
`initial_file`, which is a reference to a file (assumed to be in the
[sources folder] unless otherwise specified) that contains initial
training data.  If you want to use the conventional initial file, you
can do:

{% highlight python %}
ml = SimpleTextMachineLearner('abc', use_initial_file=True)
{% endhighlight %}

This will set the `initial_file` attribute to, for example,
`docassemble.demo:data/sources/ml-alphabet.json`.

You can also set `initial_file` to a specific value by passing an
optional second parameter:

{% highlight python %}
ml = SimpleTextMachineLearner('abc', 'initial-training-set.json')
{% endhighlight %}

Or, you can give it as an optional keyword parameter:

{% highlight python %}
ml = SimpleTextMachineLearner('abc', initial_file='initial-training-set.json')
{% endhighlight %}

Or, you can set it with code:

{% highlight python %}
ml = SimpleTextMachineLearner('abc')
ml.initial_file = 'initial-training-set.json'
{% endhighlight %}

A `SimpleTextMachineLearner` needs a `group_id` in order to operate,
but the `initial_file` is optional.

The data set is stored in the SQL database and persists beyond the
life of the interview.  Any interview can use a data set by
referencing its `group_id`.

The `initial_file` will only be used to populate the data set if the
data set is completely empty.  If you want to update a data set that
already has entries, you can use other methods, such as
[`.add_to_training_set()`].

A workflow for developing and distributing an interview that uses
machine learning is as follows:

* Create an interview file in the [Playground] called `triage.yml`.
* Initialize the model with `ml = SimpleTextMachineLearner('legal_issue',
  use_initial_file=True)`.
* Develop a training set.  You can do this using the
  [`.save_for_classification()`] method in your interview.
* Train your data set.  You can do this by going to [Train] from the
  main menu.  Or, you could use [`.one_unclassified_entry()`] in
  combination with [`.classify()`] and [`.save()`] to train from
  within an interview.  Or, you could use [`.add_to_training_set()`]
  in your interview to store complete observations.
* Package your interview in the [Playground].  Under "Sources,"
  include the file `ml-triage.json`.
* Now, if someone installs your package on their server, then your
  training data will initialize the model.

## <a name="SimpleTextMachineLearner.add_to_training_set"></a>.add_to_training_set()

If you know the independent and dependent variables for an
observation, the [`.add_to_training_set()`] method will create an
entry in the data for you.  It takes two parameters: the independent
variable and the dependent variable.

It also takes an optional keyword parameter `key`, which if set will
store the entry using the given `key`.  You do not need to use `key`s
with your data, but you may find it helpful to add `key`s to help keep
your data organized.

{% highlight python %}
ml.add_to_training_set("I hate my life", "unhappy")
ml.add_to_training_set("i luv my cat!!!!! xoxo", "happy", key='juvenile')
{% endhighlight %}

## <a name="SimpleTextMachineLearner.classified_entries"></a>.classified_entries()

The [`.classified_entries()`] method returns a [`DAList`] of objects
of type [`MachineLearningEntry`], which represent entries in the
database.  See also [`.unclassified_entries()`].

{% highlight yaml %}
question: Prediction
subquestion: |
  This prediction was based on the following data:

  % for record in ml.classified_entries():
  * "${ record.independent }" means "${ record.dependent }."
  % endfor
{% endhighlight %}

## <a name="SimpleTextMachineLearner.confusion_matrix"></a>.confusion_matrix()

The [`.confusion_matrix()`] method returns a [confusion matrix] that
can be used to evaluate the performance of the machine learner on the
data set.

Each entry in the data set is randomly assigned to either a training
set or a testing set.  The model is trained on the training set and
then tested with the testing set.  The "Actual" values are along the
top.  The "Predicted" values are along the left side.

If the dependent values are `'Unhappy'` and `'Happy'`, the
[Python dictionary] returned from `ml.confusion_matrix()` will be
something like this:

{% highlight python %}
{'Unhappy': {'Unhappy': 8, 'Happy': 3}, 'Happy': {'Unhappy': 2, 'Happy': 6}}
{% endhighlight %}

The outer keys refer to "actual" values and the inner keys refer to
"predicted" values.

The output of `ml.confusion_matrix(output_format='html')` will look like:

<table class="table table-bordered">
  <thead>
    <tr>
      <td></td>
      <td></td>
      <td style="text-align: center" colspan="2">Actual</td>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>Unhappy</th>
      <th>Happy</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align: right; vertical-align: middle;" rowspan="2">Predicted</td>
      <th>Unhappy</th>
      <td>8</td>
      <td>2</td>
    </tr>
    <tr>
      <th>Happy</th>
      <td>3</td>
      <td>6</td>
    </tr>
  </tbody>
</table>

Other valid `output_format` values are `json` and `yaml` for [JSON]
and [YAML] output, respectively.

You can limit the universe of values used for testing and training by
setting the optional keyword parameter `key`.  Then, only entries
created with that `key` will be used as part of the training and
testing.

Note that since the data set is split into a training set and a
testing set in a random fashion, there is no guarantee that the size
of the training set and the testing set will be the same.  The split
is random each time [`.confusion_matrix()`] is called, so the exact
results will not be reproducible.  It is a good idea to look at
several [confusion matrices] when assessing the functionality of a
machine learning model.

If your data set has more than a few dependent variables, you might
prefer to test the true/false question of whether the model predicts
a particular value, or not a particular value.  If you set the
optional keyword parameter `split` to `True`, [`.confusion_matrix()`]
will return a [Python dictionary] of responses, where each key is a
dependent variable in the data set and each value is a
[Python dictionary] representing the [confusion matrix].  If
`output_format` is [HTML], all of the [confusion matrices] will be
listed, with headers indicating the dependent variable being tested.

## <a name="SimpleTextMachineLearner.delete_by_id"></a>.delete_by_id()

The [`.delete_by_id()`] method will delete a single entry from the
data set, indicated by the ID.

{% highlight python %}
for entry in ml.unclassified_entries():
  if entry.independent == 'ignore':
    ml.delete_by_id(entry.id)
{% endhighlight %}

## <a name="SimpleTextMachineLearner.delete_by_key"></a>.delete_by_key()

The [`.delete_by_key()`] method will delete entries in the 
data set that use the given key.

{% highlight python %}
ml.delete_by_key('user')
{% endhighlight %}

## <a name="SimpleTextMachineLearner.delete_training_set"></a>.delete_training_set()

The [`.delete_training_set()`] method will delete all of the entries in the 
data set.

{% highlight python %}
ml.delete_training_set()
{% endhighlight %}

## <a name="SimpleTextMachineLearner.dependent_in_use"></a>.dependent_in_use()

The [`.dependent_in_use()`] method returns a sorted list of unique
values of the dependent variable for all classified entries.

{% highlight yaml %}
question: |
  What is the meaning of ${ phrase }?
fields:
  - no label: meaning
    datatype: radio
    code: |
      ml.dependent_in_use()
{% endhighlight %}

## <a name="SimpleTextMachineLearner.export_training_set"></a>.export_training_set()

If you have accumulated a data set within **docassemble** and you want
to extract it, you can export it.  The [`.export_training_set()`]
method returns [YAML] or [JSON] text containing the values of the data
set.

The [`.export_training_set()`] method takes an optional keyword parameter
`output_format`, which defaults to `'json'`.  The available output
formats are `'json'` and `'yaml'`.  The [`.export_training_set()`] method
returns a string containing the data in the `output_format` format.

All entries in the data set will be returned, but you can limit the
results to entries tagged with a particular key by setting the
optional keyword parameter `key`.

The following code creates a [`DAFile`] and writes the data set to
that file in [YAML] format.  The `yaml_export` variable contains the
data as text, and the `export` variable refers to the file to which
this text is written.

{% highlight python %}
yaml_export = ml.export_training_set(output_format='yaml')
export = DAFile()
export.write(yaml_export)
export.commit()
{% endhighlight %}

The following interview exports the data in the `'demo'` data set
to a file called `my_training_data.json` in the [sources folder] of
the user's [Playground].  (The user needs to be a developer or
administrator for this to work.)

{% highlight yaml %}
---
modules:
  - docassemble.webapp.playground
---
initial: True
code: |
  ml = SimpleTextMachineLearner('demo')
  the_data = ml.export_training_set(output_format='json')
  sources = PlaygroundSection('sources')
  sources.write_file('my_training_data.json', the_data)
---
mandatory: True
question: |
  The training data have been saved.
buttons:
  - Save again: refresh
{% endhighlight %}

The following interview exports the data in the `'demo'` dataset
directly to the browser in [JSON] format.

{% include side-by-side.html demo="ml-export" %}

The following interview exports the data in the `'demo'` data set
directly to the browser in [YAML] format.

{% include side-by-side.html demo="ml-export-yaml" %}

## <a name="SimpleTextMachineLearner.is_empty"></a>.is_empty()

The [`.is_empty()`] method indicates whether there are any entries in
the training set.  It returns `True` if there are no entries and
otherwise returns `False`.

{% highlight python %}
code: |
  if ml.is_empty():
    no_data_screen
  else:
    prediction_screen
{% endhighlight %}

## <a name="SimpleTextMachineLearner.new_entry"></a>.new_entry()

The [`.new_entry()`] method returns a single [`MachineLearningEntry`]
object.

The following interview uses [`.new_entry()`] to create a
[`MachineLearningEntry`] object.  It calls [`.save()`] on the new
entry.  This triggers the asking of a question to get the
`.independent` variable.  The entry goes into the data set as an
unclassified entry.  A prediction is made and presented to the user.
If the user presses "Try again," the slate is cleaned and the process
repeats.

{% include side-by-side.html demo="save-and-predict" %}

## <a name="SimpleTextMachineLearner.one_unclassified_entry"></a>.one_unclassified_entry()

The [`.one_unclassified_entry()`] method is useful for interactively
asking the user to classify unclassified entries.  It returns a single
[`MachineLearningEntry`] object.

To classify the entry, use the [`.classify()`] method.

{% include side-by-side.html demo="classify" %}

## <a name="DAModel.predict"></a><a name="SimpleTextMachineLearner.predict"></a>.predict()

The `.predict()` method of the `SimpleTextMachineLearner` class returns
the predictions of the machine learner for the given independent variable.

{% highlight python %}
predictions = ml.predict("I want to have my cake and eat it too.")
if len(predictions):
  sentiment = predictions[0]
{% endhighlight %}

If you call `.predict()` with the keyword parameter
`probabilities=True`, the return value will be a list of tuples, where
the first element of the tuple is the dependent variable and the
second value is the probability, expressed as a number between zero
and one.

{% include side-by-side.html demo="ml-predict-probabilities" %}

## <a name="SimpleTextMachineLearner.reset"></a>.reset()

For efficiency, **docassemble** keeps a cache of machine learning
objects in memory.

The [`.reset()`] method clears the cache and causes the machine
learner to re-read training data from the database.

## <a name="SimpleTextMachineLearner.retrieve_by_id"></a>.retrieve_by_id()

The [`.retrieve_by_id()`] method returns a [`MachineLearningEntry`]
for a given ID.

{% highlight python %}
entry = ml.retrieve_by_id(the_id)
{% endhighlight %}

## <a name="SimpleTextMachineLearner.save_for_classification"></a>.save_for_classification()

The [`.save_for_classification()`] method creates an unclassified
entry in the data set for the given independent variable and returns
the ID of the database entry.

{% highlight python %}
ml.save_for_classification("I'm so tired.  I haven't slept a wink.")
{% endhighlight %}

If an unclassified entry already exists in the data set for the given
independent variable, a new entry will not be created, and the ID of
the first existing entry will be returned.

## <a name="SimpleTextMachineLearner.set_dependent_by_id"></a>.set_dependent_by_id()

The [`.set_dependent_by_id()`] method classifies an existing entry
based on its ID.  The first parameter is the ID of the entry.  The
second parameter is the dependent variable.

{% highlight python %}
ml.set_dependent_by_id(the_id, "unhappy")
{% endhighlight %}

## <a name="SimpleTextMachineLearner.unclassified_entries"></a>.unclassified_entries()

The [`.unclassified_entries()`] method is like the
[`.classified_entries()`], except that it returns only entries that
have not yet been classified.

{% highlight yaml %}
question: |
  Unclassified entries
subquestion: |
  % for entry in ml.unclassified_entries():
  * "${ entry.independent }" has not yet been classified.
  % endfor
{% endhighlight %}

# <a name="SVMMachineLearner"></a>The `SVMMachineLearner` object

The `SVMMachineLearner` works just like `SimpleTextMachineLearner`
except that is uses the Support Vector Machines algorithm from the
[`pattern.vector`] package.

# <a name="RandomForestMachineLearner"></a>The `RandomForestMachineLearner` object

The `RandomForestMachineLearner` object works just like
[`SimpleTextMachineLearner`], except that its independent variable is
a [Python dictionary] rather than a piece of text.  Instead of
processing natural language, it uses the [random forest] algorithm
from the [sklearn] package to build a predictive model.

Here is a simple example that shows how a model can be constructed
from raw data expressed as [Python dictionaries].

{% include demo-side-by-side.html demo="random-forest" %}

Some things to note about this interview:

* It is important to use the [`.is_empty()`] method to see if the
  data set is empty before using [`.add_to_training_set()`] to
  populate the data set.  Otherwise, this interview would add
  duplicative data points to the data set every time it ran.
* `predictions[0]` is the most likely prediction.  If it exists,
  `predictions[1]` is the second most likely prediction, and so on.
* Because [`.predict()`] was called with `probabilities=True`, each
  item in `predictions` is a [tuple], the first element of which is
  the predicted value (`'apple'` or `'orange'`), and the second
  element of which is a probability, a number between 0 and 1.  Thus,
  the predicted dependent variables is `predictions[0][0]` and its
  probability is `predictions[0][1]`.
* The [`.format()` method], which is used to format the probability,
  is a standard [Python] method.  The code `{0:.1f}%` means "format
  the first number as a [floating point] number using one decimal
  place, and put a percent sign after it."

You can also train the model and make predictions using data gathered
during interviews.

Here is an example of an interview that uses a [random forest] model
to try to identify fruit based on a set of characteristics, many of
which are vague and subjective.  The independent variable is a
[`DADict`] called `characteristics`.  The dependent variables is the
name of a fruit (e.g., `'apple'`).

{% include demo-side-by-side.html demo="random-forest-interview" %}

Some things to note about this interview:

* The previous interview used a plain [Python dictionary] as the
  independent variable; this interview uses a [`DADict`].  Both will
  work.  Note that the [`.predict()`] and [`.add_to_training_set()`]
  methods do not trigger a [gathering] process on the [`DADict`].
* The interview uses a lot of [`mandatory`] questions to make sure
  that each item in `characteristics` gets defined before it is used
  in the machine learning methods.  Note that there are other ways to
  accomplish this without [`mandatory`] blocks.  One way would be to
  refer to the expression `[characteristics[c] for c in ('round',
  'color', 'seed location', 'width', 'sweetness')]`.
* This is an example of a self-learning interview.  It asks the user
  if the prediction is correct, and if the prediction is correct, the
  user's answers are added to the data set to make it even more
  robust.  If the prediction is not correct, the user is asked the
  name of the actual fruit, and this is added to the data set.
* In order to avoid adding duplicative dependent variables to the data
  set, when the interview asks the user for the name of the fruit, the
  interview transforms the name into lowercase using the
  [built-in method `.lower()`], and then uses the function
  [`noun_singular()`] to ensure that the name is in singular form.
  Otherwise, the data set would be littered with dependent variables
  like "Apples," "apples," "apple," and "Apple," as though they
  referred to different things.

# <a name="MachineLearningEntry"></a>The `MachineLearningEntry` object

The attributes of a `MachineLearningEntry` object are:

* `ml`: The `SimpleTextMachineLearner` object associated with the entry.
* `id`: The integer ID of the entry in the database.
* `independent`: The independent variable.
* `dependent`: The dependent variable.
* `create_time`: The [`datetime`] when the entry was created.
* `key`: A key associated with the entry, or `None` if no key was
  assigned.

If the entry is unclassified, the `dependent` attribute will be
undefined.

The values of an entry can be changed, but it does not become part of
the data set until it is saved, either by calling [`.classify()`] or
[`.save()`].

## <a name="MachineLearningEntry.classify"></a>.classify()

The [`.classify()`] method "classifies" the observation by saving it
to the data set with the dependent variable set to the value of the
`dependent` attribute.

{% include side-by-side.html demo="classify" %}

If called with a parameter, the `dependent` attribute will be set
before the entry is saved.

In other words, this:

{% highlight python %}
entry.classify("Unhappy")
{% endhighlight %}

is equivalent to:

{% highlight python %}
entry.dependent = "Unhappy"
entry.classify()
{% endhighlight %}

## <a name="MachineLearningEntry.predict"></a>.predict()

The `.predict()` method of the `MachineLearningEntry` class returns
the predictions of the machine learner given the entry's independent
variable.

{% highlight python %}
predictions = entry.predict()
if len(predictions):
  best_guess = predictions[0]
{% endhighlight %}

The result of calling `.predict()` is a [list] of dependent variables
from the training set arranged in order from most likely to least
likely.  If there is no training data, an empty [list] will be returned.

If you call `.predict()` with the keyword parameter
`probabilities=True`, the return value will be a list of [tuple]s, where
the first element of the [tuple] is the dependent variable and the
second value is the probability, expressed as a number between zero
and one.

{% highlight yaml %}
question: |
  The prediction
subquestion: |
  <%
    predictions = entry.predict(probabilities=True)
  %>
  The text provided was:
  > ${ entry.independent }
  
  % if len(predictions):
  The prediction was:

  % for prediction in predictions:
  * ${ '%s (%f)' % prediction }
  % endfor
  % else:
  There is not enough training data
  to make a prediction yet.
  % endif
{% endhighlight %}

## <a name="MachineLearningEntry.save"></a>.save()

The `.save()` method saves the entry to the database.  If the
independent variable has not yet been set (i.e., the `independent`
attribute is not defined), **docassemble** will ask for it.

# Creating your own machine learning functions

If you are a [Python] developer, you may want to make other machine
learning algorithms available in interviews.

The `SimpleTextMachineLearner` class is a subclass of the generic
`MachineLearner` class.  The `MachineLearner` object handles the
overhead of storing independent and dependent variables in a database,
while the `SimpleTextMachineLearner` class handles the specific
implementation (which uses the `KNN()` function of the
[`pattern.vector`]).

One way you can make machine learning algorithms available in
interviews is by creating your own subclasses of `MachineLearner` that
define the following methods:

* `_initialize()`
* `_train()`
* `predict()`

See the code of [`docassemble.webapp.machinelearning`] for more
information.

# Slow-running code

If your machine learning algorithms use very large training sets, or
take a long time to process, you may wish to call `.predict()` from a
[background action].  (The loading of the training set takes place
during the first call to `.predict()`, not during the creation of the
object.)

[background action]: {{ site.baseurl }}/docs/background.html#background
[functions]: {{ site.baseurl }}/docs/functions.html
[question]: {{ site.baseurl }}/docs/questions.html
[machine learning]: http://en.wikipedia.org/wiki/Machine_learning
[regression analysis]: http://en.wikipedia.org/wiki/Regression_analysis
[JSON]: https://en.wikipedia.org/wiki/JSON
[YAML]: https://en.wikipedia.org/wiki/YAML
[sources folder]: {{ site.baseurl }}/docs/playground.html#sources
[Playground]: {{ site.baseurl }}/docs/playground.html
[`pattern.vector`]: http://www.clips.ua.ac.be/pages/pattern-vector
[Python]: https://en.wikipedia.org/wiki/Python_%28programming_language%29
[`docassemble.webapp.machinelearning`]: {{ site.github.repository_url }}/blob/master/docassemble_webapp/docassemble/webapp/machinelearning.py
[`.reset()`]: #SimpleTextMachineLearner.reset
[`.predict()`]: #SimpleTextMachineLearner.predict
[`.delete_training_set()`]: #SimpleTextMachineLearner.delete_training_set
[`.delete_by_key()`]: #SimpleTextMachineLearner.delete_by_key
[`.delete_by_id()`]: #SimpleTextMachineLearner.delete_by_id
[`.set_dependent_by_id()`]: #SimpleTextMachineLearner.set_dependent_by_id
[`.classified_entries()`]: #SimpleTextMachineLearner.classified_entries
[`.unclassified_entries()`]: #SimpleTextMachineLearner.unclassified_entries
[`.one_unclassified_entry()`]: #SimpleTextMachineLearner.one_classified_entry
[`.retrieve_by_id()`]: #SimpleTextMachineLearner.retrieve_by_id
[`.save_for_classification()`]: #SimpleTextMachineLearner.save_for_classification
[`.add_to_training_set()`]: #SimpleTextMachineLearner.add_to_training_set
[`.is_empty()`]: #SimpleTextMachineLearner.is_empty
[`.new_entry()`]: #SimpleTextMachineLearner.new_entry
[`.dependent_in_use()`]: #SimpleTextMachineLearner.dependent_in_use
[`.export_training_set()`]: #SimpleTextMachineLearner.export_training_set
[`.confusion_matrix()`]: #SimpleTextMachineLearner.confusion_matrix
[`SimpleTextMachineLearner`]: #SimpleTextMachineLearner
[`SVNMachineLearner`]: #SVNMachineLearner
[`MachineLearningEntry`]: #MachineLearningEntry
[`.classify()`]: #MachineLearningEntry.classify
[`.save()`]: #MachineLearningEntry.classify
[`DAList`]: {{ site.baseurl }}/docs/objects.html#DAList
[`DADict`]: {{ site.baseurl }}/docs/objects.html#DADict
[`datetime`]: https://docs.python.org/3/library/datetime.html#datetime-objects
[list]: https://docs.python.org/3/tutorial/datastructures.html
[HTML]: https://en.wikipedia.org/wiki/HTML
[Python dictionary]: https://docs.python.org/3/library/stdtypes.html#dict
[confusion matrix]: https://en.wikipedia.org/wiki/Confusion_matrix
[confusion matrices]: https://en.wikipedia.org/wiki/Confusion_matrix
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[data types]: {{ site.baseurl }}/docs/fields.html#datatype
[object]: {{ site.baseurl }}/docs/objects.html#DAModel
[`DAModel`]: {{ site.baseurl }}/docs/objects.html#DAModel
[Mako]: {{ site.baseurl }}/docs/markup.html#mako
[2-tuples]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences
[tuple]: https://docs.python.org/3/tutorial/datastructures.html#tuples-and-sequences
[privileges]: {{ site.baseurl }}/docs/users.html
[package]: {{ site.baseurl }}/docs/packages.html
[Sources folder]: {{ site.baseurl }}/docs/playground.html#sources
[Packages folder]: {{ site.baseurl }}/docs/playground.html#packages
[`machine learning storage`]: {{ site.baseurl }}/docs/initial.html#machine learning storage
[`datatype`]: {{ site.baseurl }}/docs/fields.html#datatype
[initial block]: {{ site.baseurl }}/docs/initial.html
[sklearn]: http://scikit-learn.org/stable/
[Python dictionaries]: https://docs.python.org/3/library/stdtypes.html#dict
[Train]: #train
[`.format()` method]: https://docs.python.org/3/library/stdtypes.html#str.format
[floating point]: https://en.wikipedia.org/wiki/Floating-point_arithmetic
[lower-level way]: #lowerlevel
[random forest]: https://en.wikipedia.org/wiki/Random_forest
[`mandatory`]: {{ site.baseurl }}/docs/logic.html#mandatory
[built-in method `.lower()`]: https://docs.python.org/3/library/stdtypes.html#str.lower
[`noun_singular()`]: {{ site.baseurl }}/docs/functions.html#noun_singular
[gathering]: {{ site.baseurl }}/docs/groups.html#gathering
