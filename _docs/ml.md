---
layout: docs
title: Machine learning
short_title: Machine Learning
---

**docassemble** allows you to integrate [machine learning] into your
interviews.

# What is machine learning?

Machine learning is like "fuzzy logic."  A computer can be trained to
recognize patterns.

A common application of machine learning is "sentiment analysis" of
Twitter messages.  The goal is for the computer to be able to guess
the emotional state of the author of a message based on the words that
the author used.  Consider the following examples:

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
independent variables.  They are used to train a model or they are
plugged into a model in order to obtain a prediction.  The
classification of "happy" or "unhappy" is the "dependent" variable.
The terminology of "dependent" and "independent" variables is the
terminology of [regression analysis] in the field of statistics.
(Machine learning is actually just a kind of regression analysis.)

Once a model has been "trained," it can be "tested" to see how
accurate its predictions are.  For example, the "sentiment analysis"
model discussed above could be tested by running 100 predictions on a
variety of happy and unhappy phrases and measuring how often the
"predictions" are correct.  If the model correctly classifies "happy"
statements as "happy" about 95% of the time, and also classifies
"unhappy" statements as "unhappy" about 95% of the time, then it
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
further information about how models work or the statistics underlying
them.  All that you need to do is make sure you "train" the model with
a sufficiently diverse set of data.  If you had the most sophisticated
model in the world but you only trained it with "happy" sentences, it
wouldn't be able to recognize an "unhappy" sentence.

Some models are complex and proprietary, but nevertheless are very
easy to use.  IBM Watson, for example, which famously won a Jeopardy!
competition, is available over the internet to the general public for
a fee.  Nobody outside of IBM knows exactly how it works, but
nevertheless numerous customers have developed applications that use
IBM Watson to classify text.  You do not need to know how it works in
order to evaluate whether it is any good; all you need to do is
thoroughly train and test it.

# How to use machine learning

You can use machine learning in your **docassemble** interviews.
Instead of asking a multiple-choice question, you could ask the user
to express something in their own words, then use a trained model to
guess at the user's meaning and ask the user "It sounds like you are
saying _x_.  Is that correct?"

To use **docassemble**'s built-in machine learning service, make sure
you include the following at the start of your interview, just as you
do when using [functions].

{% highlight yaml %}
---
modules:
  - docassemble.base.util
---
{% endhighlight %}

This makes the `SimpleTextMachineLearner` available in your interview.

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
particular type of classification model, and `demo` is the
name of a set of training data.

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
prediction is in `predictions[0]`.

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
SimpleTextMachineLearner('demo')`, the `demo` refers to the name of a
training set.  The training set is stored in the **docassemble**
database on the server.  Any other interview that runs on the server
can use the same training data.  If you want to make sure that your
training data is unique to your interview, use a specific name that
nobody else would use, like
`docassemble.oklahoma.familylaw.custody.reason`.

There are several ways to add data to a training set.

### <a name="save"></a>Adding user input to the training set

You may want to use the phrases that users type in as training data,
so that your machine learning system becomes smarter over time.

The `save_for_classification()` method of the
`SimpleTextMachineLearner` object will store a phrase in the training
data so that it can be classified later.  The example interview in the
previous section can be adapted to do this with the addition of just
one line:

{% include side-by-side.html demo="ml-save-and-predict" %}

Doing `ml.save_for_classification(phrase)` will put the phrase into
the training data set, but the entry will be inactive until a
classification is manually assigned to it.

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

The `one_unclassified_entry()` method will return a not-yet-classfied
entry in the training set.  If there are not any not-yet-classfied
entries, this method will return `None`.  It returns an object
representing the entry in the training set.  To provide a
classification for the entry, you call the `.classify()` method on the
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
ml = SimpleTextMachineLearner('demo2', 'docassemble.demo:data/sources/training-data.json')
{% endhighlight %}

In the above example, the file is located in the [sources folder] of
a package.

You can also reference a file that exists on the internet somewhere.

{% highlight python %}
ml = SimpleTextMachineLearner('demo2', 'https://example.com/data/training-data.json')
{% endhighlight %}

The file needs to contain and array of dictionaries (associative
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

You can also use code within your interviews to add training data to a
training set, using the `add_to_training_set()` method of the
`SimpleTextMachineLearner` object.

{% highlight python %}
ml.add_to_training_set("I am feeling blue", "unhappy")
{% endhighlight %}

The first argument is the independent variable, and the second
argument is the dependent variable.

# <a name="extracting"></a>Extracting training data

If you have accumulated a training set within **docassemble** and you
want to extract it, you can use the `export_training_set()` method of
the `SimpleTextMachineLearner` object to convert it to [JSON] or
[YAML].

The `export_training_set()` method takes an optional keyword argument
`output_format`, which defaults to `json`.  The available output
formats are `json` and `yaml`.  The `export_training_set()` method
returns a string containing the data in the `output_format` format.

The following interview exports the data in the `'demo'` training set
to a file called `my_training_data.json` in the [sources folder] of
the user's [Playground].  (The user needs to be a developer or
administrator for this to work.)

{% highlight yaml %}
---
modules:
  - docassemble.webapp.playground
  - docassemble.base.util
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

The following interview exports the data in the `'demo'` training set
directly to the browser in [JSON] format.

{% include side-by-side.html demo="ml-export" %}

The following interview exports the data in the `'demo'` training set
directly to the browser in [YAML] format.

{% include side-by-side.html demo="ml-export-yaml" %}

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
interviews is by creating your own subclasses of `MachineLearner`.  
See the code of [`docassemble.webapp.machinelearning`] for more
information.

## Slow-running code

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
