---
layout: docs
title: Language support
short_title: Language Support
---

**docassemble** allows you to write a single interview that asks
questions differently depending on the user's language and locale.  It
also allows [Unicode] to be used in user-facing text, user input, and
documents.  With these features, **docassemble** should be fully
usable in languages other than English.

# <a name="configuration"></a>Configuration

By default, the active language and locale are determined by the
[`language`] and [`locale`] settings in the **docassemble**
[configuration].

The value of [`language`] must be a two-character lowercase
[ISO-639-1] or [ISO-639-3] code.  For example, English is `en`,
Spanish is `es`, French is `fr`, and Arabic is `ar`.

The value of [`locale`] must be a locale name without the language
prefix, such as `US.utf8` or `DE.utf8`.  Any locale you use must be
installed in the operating system of the server.

See the [`other os locales`] configuration directive for information
about how to install locales in the operating system of your server.
By default, only the `en_US.UTF-8 UTF-8` locale (the locale for the
United States) is installed, so you will have problems if you try to
use other locales in your interviews.

Within interviews, the functions [`set_language()`] and
[`set_locale()`] will change the active language, locale, and dialect.
(The dialect is relevant only for the text-to-speech feature, which is
controlled by the [special variable `speak_text`].)

If you write functions that need to know the current language or
locale, use the [`get_language()`] and [`get_locale()`] function from
the [`docassemble.base.util`] module.  Also note that there is a
function [`get_dialect()`] for retrieving the dialect.

The language and locale settings have the following effects:

* If you have a [`translations`] block in your interview, then
  whenever **docassemble** processes a phrase (text that you can mark
  up with [Mako] templating), it will use the appropriate translation
  of that phrase if a translation for the phrase is present in one of
  the Excel files referenced in the [`translations`] block.  For more
  information about creating these Excel files, see the documentation
  for the [Download an interview phrase translation file] utility.
* Built-in words and phrases from the "core" **docassemble** code will
  be translated into the active language.  Whenever **docassemble**
  prints such a word or phrase, it calls the [`word()`] function from
  the [`docassemble.base.util`] module.  Calling `word('Login')` will
  look up the word `Login` in a translation table.  If the [`word()`]
  function finds the word `Login` in the translation table for the
  active language, it will return the translated value.  If it does
  not find a translation, it will return `Login`.  For more
  information about how [`word()`] works, see [functions].  For
  information on how to define translations for a server, see the
  [`words`] directive in the [configuration].  For information on
  downloading a complete list of these phrases so that you can
  translate them into another language, see the documentation for the
  [utility] called [Translate system phrases into another language].
* When **docassemble** looks for a [`question`] or [`code`] block that
  defines a variable, it first tries [`question`]s and [`code`] blocks
  for which the [`language` modifier] is set to the active language
  (either explicitly or by operation of the [`default language`]
  [initial block]).  If **docassemble** does not find any such
  [`question`]s or [`code`] blocks, it looks for ones that do not have
  [`language` modifier] set.  This means that if your interview only
  uses one language, you do not need to worry about setting the
  [`language` modifier].  If you are using the [`translations`] block
  to translate all of the phrases in your interview, you probably will
  not need to use the [`language` modifier] on [`question`] blocks,
  but you will need to use it on your [`sections`] block if you have one.
* Some functions have language-specific responses, such as [`today()`]
  in the [`docassemble.base.util`] module, which returns today's date in
  a readable format such as "October 31, 2015" (for language `en`) or
  "31 octobre 2015" (for language `fr`).  However, not all languages
  are supported by the [`babel.dates`] package; you may need to fall
  back to a different language.  To configure how this works, set the
  [`babel dates map`] directive in the [Configuration].
* When **docassemble** highlights [`terms`] in a question (see
  [initial blocks]), it will only highlight words specified in
  [`terms`] blocks for which the `language` of the term matches the
  language of the question.  Or, if the question does not have the
  [`language` modifier] set, **docassemble** will look for a [`terms`]
  block that does not have `language` set.
* When **docassemble** displays [`interview help`] text, it will only
  display the content of [`interview help`] blocks for which the
  [`language` modifier] is the same as the language of the question.
  Or, if the question does not have the [`language` modifier] set,
  **docassemble** will look for an [`interview help`] block that does
  not have the [`language` modifier] set.
* If you have defined default text for various "screen parts" (such as
  [`pre`], [`post`], and [`submit`]) using the [`metadata`] block and
  you defined values for multiple languages, **docassemble** will use
  the value for the current language.

On pages other than interviews, the language that is used for
translation purposes is determined as follows:

* If the user is logged in, the user has a "profile" that includes a
  field called `language`.  If the `language` field in the user's
  profile is defined, this language will be used for translations.
  When a user first registers, this `language` field is blank.  You
  can use logic in an interview to set it to something.  In
  interviews, you can read this profile by calling [`get_user_info()`]
  and change it by calling [`set_user_info()`].
* If the user is not logged in, or the user does not have a `language`
  defined in their profile, **docassemble** will look for a URL
  parameter `lang`.  For example, if you have a web site and you want
  to put a link on that web site to direct the user to log in to your
  **docassemble** server, you could use a URL like
  `https://docassemble.example.com/user/sign-in?lang=es` and the user
  will see a login screen that is in Spanish.  Other URLs with which
  you might want to use the `lang` parameter are `/user/register` and
  `/list`.
* If there is no `lang` parameter in the URL, **docassemble** will
  look for an `Accept-Language` header in the request from the user's
  browser.  This is typically set by the user's web browser to
  whatever language is defined in the web browser settings.  So if the
  user is a German speaker who is using a web browser that is set up
  to use the language `de`, then the language `de` will be used for
  translations.  In interviews, you can read this language by calling
  [`language_from_browser()`].
* If a language cannot be found in the `Accept-Language` header, the
  language defined by the [`language`] directive in the
  [Configuration] is used.

# <a name="bpsingle"></a>Best practices for single-language interviews

If your interview only works in one language, do not set the
[`language` modifier] for any blocks, do not use [`default language`],
and do not call [`set_language()`] or [`set_locale()`].  Instead,
simply make sure that the default [`language`] and [`locale`] in the
[configuration] are set to the correct values.

# <a name="bpmulti"></a>Best practices for multi-language interviews

If you have an interview that needs to function in multiple languages,
you will need to have [`initial`] code that calls [`set_language()`].
**docassemble** does not remember the active language from one screen
to the next , but the [`initial`] code will make sure that it is
always set to the correct value.

{% highlight yaml %}
objects:
  - user: Individual
---
initial: True
code: |
  set_language(user.language)
  process_action()
---
question: |
  What language do you speak?
field: user.language
choices:
  - "English": en
  - "Español": es
{% endhighlight %}

Note that the function [`process_action()`] is called after setting
`set_language()`.  By default, [actions] are processed at the very
beginning of your interview logic, before your YAML's `initial` and
`mandatory` blocks are processed.  However, if you have an `initial`
block that needs to define some "ground rules," such as setting the
operative language, you need to explicitly call `process_action()` in
your `initial` block so that the "ground rules" are defined before
actions are processed.

Note that when a user is logged in, they have a user profile, and a
`language` field is part of their user profile.  The value of this
field will determine what language is used when a user logs in and
visits a page like `/interviews`.  When a user registers, this field
is left unset, and users do not have the ability to change their
language.  You can set the `language` field in the user profile
during an interview, using code like this:

{% highlight yaml %}
objects:
  - user: Individual
---
initial: True
code: |
  set_language(user.language)
  process_action()
---
mandatory: True
code: |
  if user_logged_in() and not get_user_info()['language']:
    set_user_info(language=user.language)
---
question: |
  What language do you speak?
field: user.language
choices:
  - "English": en
  - "Español": es
{% endhighlight %}

If you want to avoid asking the user for their language in situations
where the `language` field of the user profile has already been
defined, you can use a `code` block to set `user.language` without
asking a `question`:

{% highlight yaml %}
objects:
  - user: Individual
---
initial: True
code: |
  set_language(user.language)
  process_action()
---
mandatory: True
code: |
  if user_logged_in() and not get_user_info()['language']:
    set_user_info(language=user.language)
---
question: |
  What language do you speak?
field: user.language
choices:
  - "English": en
  - "Español": es
---
code: |
  if user_logged_in() and get_user_info()['language'] in ('en', 'es'):
    user.language = get_user_info()['language']
{% endhighlight %}

You can also avoid asking the user for their language by assuming that
they speak whatever language their web browser is set up to use, which
you can determine by calling [`language_from_browser()`].

{% highlight yaml %}
objects:
  - user: Individual
---
initial: True
code: |
  set_language(user.language)
  process_action()
---
mandatory: True
code: |
  if user_logged_in() and not get_user_info()['language']:
    set_user_info(language=user.language)
---
question: |
  What language do you speak?
field: user.language
choices:
  - "English": en
  - "Español": es
---
code: |
  if user_logged_in() and get_user_info()['language'] in ('en', 'es'):
    user.language = get_user_info()['language']
  elif language_from_browser('en', 'es'):
    user.language = language_from_browser('en', 'es')
{% endhighlight %}

**docassemble** does not handle language selection automatically
because there is no one-size-fits-all solution.  For example, suppose
a user's primary language was French, but you had some interviews on
your system that were only available in English and German.  You would
want to give the user a chance to select whether they saw the
interview in English or German.  Handling language selection in the
interview logic allows interview developers to customize the way that
the applicable language is determined.

The reason for using an `initial` block to set the language is based
on the fact that an interview session can have multiple users, who
might speak different languages.  For example, you might have a legal
advice interview where the user may be Spanish-speaking but the
advocate may be English-speaking.  Here is an interview where the
`user` object is different depending on whether the active user is the
client or the advocate:

{% highlight yaml %}
objects:
  - client: Individual
  - advocate: Individual
---
initial: True
  if user_logged_in() and user_has_privilege('advocate'):
    user = advocate
  else:
    user = client
  set_language(user.language)
  process_action()
---
generic object: Individual
question: |
  What language ${ x.do_question('speak') }?
field: x.language
choices:
  - "English": en
  - "Español": es
---
{% endhighlight %}

If you are writing an interview that offers multiple language options
and you are using the [`language` modifier] or the [`default
language`] [initial block], you may want to break out your interview
into different files:

* `code.yml` - for language-independent [initial blocks],
  [interview logic], [questions], and [code blocks].
* `en.yml` - for English-language [`question`]s and [`terms`], with
  `default language: en` as the first line.
* `es.yml` - for Spanish-language [`question`]s and [`terms`], with
  `default language: es` as the first line.
* `interview.yml` - the main file, which simply [`include`]s the above
  three files.

Below is an example of a multi-language interview that asks the user
for a language, then asks for a number, then makes a statement about
the number.  The interview is split into the four files listed above,
and all files reside in a folder called `bestnumber` within the
`data/questions` folder.

The contents of `code.yml` are:

{% highlight yaml %}
initial: True
code: |
  set_language(user_language)
  process_action()
  need(final_screen)
---
question: |
  What language do you speak?  (¿Qué idioma habla?)
choices:
  - "English": en
  - "Español": es
field: user_language
---
code: |
  best_number = favorite_number + 1
{% endhighlight %}

The contents of `en.yml` are:

{% highlight yaml %}
default language: en
---
terms:
  favorite number: The number you most like to calculate.
---
question: |
  What is your favorite number?
fields:
  - Number: favorite_number
    datatype: number
---
sets: final_screen
question: |
  All done.
subquestion: |
  The best number in the world is not ${ favorite_number },
  but ${ best_number }.
buttons:
  - Restart: restart
{% endhighlight %}

The contents of `es.yml` are:

{% highlight yaml %}
default language: es
---
terms:
  numero favorito: El número que más le guste para calcular.
---
question: |
  ¿Cual es tu numero favorito?
fields:
  - Número: favorite_number
    datatype: number
---
sets: final_screen
question: |
  Completado
subquestion: |
  El mejor número en el mundo es de ${ best_number },
  no ${ favorite_number }.
buttons:
  - Reanudar: restart
{% endhighlight %}

Finally, the contents of `interview.yml` are:

{% highlight yaml %}
include:
  - code.yml
  - en.yml
  - es.yml
{% endhighlight %}

[Try it out here]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/bestnumber/interview.yml){:target="_blank"}.

# <a name="translators"></a>Working with third-party translators

While it is generally a good thing that **docassemble** allows you to
write complicated [`question`]s that make heavy use of [Mako]
templating, [Markdown], and embedded Python code, a downside is that
all of this "code" can make the translation process more complicated.
Translators may be confused by all of the code, even when you give
them an [interview phrase translation file] in Excel format.  They may
ask you to convert your code to Microsoft Word, putting a great deal
of conversion work on you.  Or they may translate what you give them
incorrectly, for example by translating variable names when they
shouldn't.

You may be tempted to change the way that you code interviews to
optimize for the needs of the tech-phobic translators you hire.  For
example, if you have a single [`question`] that has ten different
variations, you may decide to split this into ten separate
[`question`]s so that the translator has an easier time translating.
Or you might decide to remove [Mako] templating and substitute generic
language that is easier to translate.

However, there is no reason that you should have to make your
interview less functional or less maintainable just because the
translators you tried to hire were confused by "code."  The solution
is to find a different translator.  Although hiring a translator other
than the "lowest bidder" could increase the out-of-pocket costs of
your project, you should think about the net cost of your project,
including your own time, and think about costs and benefits in the
long term.

While there are many translators who will be confused by having to
"translate around code," there are also many translators for whom
"translating around code" is not a problem at all.  Companies like
[Morningside Translations] regularly handle technical translations and
provide quality control to ensure that the translators do not disturb
embedded Python.  Shop around before concluding that you have to "dumb
down" your interview to make it translatable.

# <a name="documents"></a>Creating documents in languages other than English

If your interview uses the [`docx template file`] feature, you can
prepare separate DOCX files for each language and then [use code] to
select which file to use.  For example:

{% highlight yaml %}
mandatory: True
question: |
  Here is your document.
attachment:
  - name: Your letter
    filename: letter
    docx template file: 
      code: |
        'letter_' + get_language() + '.docx'
{% endhighlight %}

This will use the file `letter_en.docx` if the language is English,
and `letter_es.docx` if the language is Spanish, etc.  This is
primarily useful if you are using the [`translations`] block for
translating phrases and you are not using the [`language` modifier] on
your [`question`]s.

The [documents] feature that allows documents to be created from
[Markdown] text with [Mako] templating supports languages other than
English to the extent that RTF, [Pandoc], and [LaTeX] do.  [LaTeX] has
support for internationalization, and the default [LaTeX] template
will load either the [polyglossia] package or the [babel] package,
depending on what is available.  The language used by [LaTeX] can be
set using the `metadata` entries `lang` and `mainlang` in the
`attachment` specification.  For some languages, you may need to write
your own templates in order to enable fonts that support your
language.

# <a name="customizing"></a>Customizing based on language and locale

The [language-specific functions], many of which are used internally
by **docassemble** object methods, can all be overridden with your own
versions.  You can write special functions that should be used
depending on which language is the active language (as set by
[`set_language()`]).  For example, there is an internal function
`your()` that when called as `your('apple')` returns `'your apple`'.
The default language is English, and there are no definitions for any
other languages, so if you want to use a language other than English,
you will need to write alternatives.  For more information about how
to do this, see the sections on [language-specific functions] and
[simple language functions].

While many functions depend on the current language, there are a few
that depend on the locale.  One is [`nice_number()`] (one of the
[language-specific functions] that can be overridden).  When the given
number is not among the numbers that should be converted to a word
(see [`update_nice_numbers()`]), it is formatted according to the
locale.  For example, in locale `en_US` (English, United States),
`nice_number(6242235.4)` becomes `'6,242,235.4'`, but in locale
`es_ES` (Spanish, Spain), it becomes `'6.242.235,4'`.

Other locale-dependent functions are [`currency()`] and
[`currency_symbol()`].  In locale `en_US` (English, United States),
`currency(101.34)` becomes `'$101.34'`, but in locale `es_ES`
(Spanish, Spain), it becomes `'101,34 EUR'`.  In locale `en_US`
(English, United States), [`currency_symbol()`] becomes `$`, but
in locale `es_ES` (Spanish, Spain), it becomes `'EUR'`.

The **docassemble** features that work with currencies are complicated
because the way that currency is represented depends on locale, and
you might want to support more than one locale, but Python's [`locale`
module] assumes that the locale setting is server-wide.

The [`currency()`] function and the [`currency_symbol()`] functions
are both [language-specific functions], which means that you can
substitute your own functions in their place in order to have full
control over currency formatting.  For example, if you include the
following in a Python module, then whenever the active language is
French, the currency symbol will be € by default and the `currency()`
function will return the number followed by €, instead of the currency
symbol followed by the number.

{% highlight python %}
import locale
import docassemble.base.functions
docassemble.base.functions.update_language_function('fr', 'currency_symbol', lambda: u'€')
def fr_currency(value, decimals=True, symbol=None):
    docassemble.base.functions.ensure_definition(value, decimals, symbol)
    if symbol is None:
        symbol = u'€'
    if decimals:
        return locale.format_string('%.2f', value, grouping=True) + ' ' + symbol
    else:
        return locale.format_string('%.0f', value, grouping=True) + ' ' + symbol
docassemble.base.functions.update_language_function('fr', 'currency', fr_currency)
{% endhighlight %}

You can also override the default [`currency()`] and
[`currency_symbol()`] functions using the catch-all language `'*'`
instead of `'fr'`.  You could use [`set_locale()`] (without
[`update_locale()`]) in an [`initial`] block and use [`get_locale()`] in
your `currency()` and `currency_symbol()` functions to do different
things depending on the locale.

If you have a specific currency symbol that you want to use on your
server, you can set the [`currency symbol`] directive in the
[configuration].  This will have a global effect.  Suppose you set
this in the [configuration]:

{% highlight yaml %}
currency symbol: €
{% endhighlight %}

This is equivalent to doing:

{% highlight python %}
import docassemble.base.functions
docassemble.base.functions.update_language_function('fr', 'currency_symbol', lambda: u'€')
{% endhighlight %}

[`currency symbol`]: {{ site.baseurl }}/docs/config.html#currency symbol
[`locale` module]: https://docs.python.org/3.8/library/locale.htmle
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[initial blocks]: {{ site.baseurl }}/docs/initial.html
[initial block]: {{ site.baseurl }}/docs/initial.html
[interview logic]: {{ site.baseurl}}/docs/logic.html
[code blocks]: {{ site.baseurl}}/docs/code.html
[questions]: {{ site.baseurl}}/docs/questions.html
[configuration]: {{ site.baseurl }}/docs/config.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[functions]: {{ site.baseurl }}/docs/functions.html
[Unicode]: https://en.wikipedia.org/wiki/Unicode
[documents]: {{ site.baseurl }}/docs/documents.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[LaTeX]: http://www.latex-project.org/
[polyglossia]: https://www.ctan.org/pkg/polyglossia
[babel]: https://www.ctan.org/pkg/babel
[ISO-639-1]: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
[ISO-639-3]: https://en.wikipedia.org/wiki/List_of_ISO_639-3_codes
[Pandoc]: http://johnmacfarlane.net/pandoc/
[`language` modifier]: {{ site.baseurl }}/docs/modifiers.html#language
[`language`]: {{ site.baseurl }}/docs/config.html#language
[`locale`]: {{ site.baseurl }}/docs/config.html#locale
[`set_language()`]: {{ site.baseurl }}/docs/functions.html#set_language
[`set_locale()`]: {{ site.baseurl }}/docs/functions.html#set_locale
[`update_locale()`]: {{ site.baseurl }}/docs/functions.html#update_locale
[`get_language()`]: {{ site.baseurl }}/docs/functions.html#get_language
[`get_dialect()`]: {{ site.baseurl }}/docs/functions.html#get_dialect
[`get_locale()`]: {{ site.baseurl }}/docs/functions.html#get_locale
[`word()`]: {{ site.baseurl }}/docs/functions.html#word
[`default language`]: {{ site.baseurl }}/docs/initial.html#default language
[`question`]: {{ site.baseurl }}/docs/questions.html#question
[`include`]: {{ site.baseurl }}/docs/initial.html#include
[`initial`]: {{ site.baseurl }}/docs/logic.html#initial
[`code`]: {{ site.baseurl }}/docs/code.html#code
[`terms`]: {{ site.baseurl }}/docs/initial.html#terms
[`today()`]: {{ site.baseurl }}/docs/functions.html#today
[`interview help`]: {{ site.baseurl }}/docs/initial.html#interview help
[`docassemble.base.util`]: {{ site.github.repository_url }}/blob/master/docassemble_base/docassemble/base/util.py
[special variable `speak_text`]: {{ site.baseurl }}/docs/special.html#speak_text
[`other os locales`]: {{ site.baseurl }}/docs/config.html#other os locales
[`words`]: {{ site.baseurl }}/docs/config.html#words
[`docx template file`]: {{ site.baseurl }}/docs/documents.html#docx template file
[Pandoc]: http://johnmacfarlane.net/pandoc/
[selection]: {{ site.baseurl }}/docs/documents.html#metadata pdf
[additional software packages]: https://packages.debian.org/stretch/texlive-lang-all
[`translations`]: {{ site.baseurl }}/docs/initial.html#translations
[`metadata`]: {{ site.baseurl }}/docs/initial.html#metadata
[`pre`]: {{ site.baseurl }}/docs/initial.html#pre
[`post`]: {{ site.baseurl }}/docs/initial.html#post
[`submit`]: {{ site.baseurl }}/docs/initial.html#submit
[Utilities]: {{ site.baseurl }}/docs/admin.html#utilities
[interview phrase translation file]: {{ site.baseurl }}/docs/admin.html#translation file
[Download an interview phrase translation file]: {{ site.baseurl }}/docs/admin.html#translation file
[`sections`]: {{ site.baseurl }}/docs/initial.html#sections
[utility]: {{ site.baseurl }}/docs/admin.html#utilities
[Translate system phrases into another language]: {{ site.baseurl }}/docs/admin.html#translate
[use code]: {{ site.baseurl }}/docs/documents.html#template file code
[Morningside Translations]: https://www.morningtrans.com/
[`babel.dates`]: http://babel.pocoo.org/en/latest/api/dates.html
[`babel dates map`]: {{ site.baseurl }}/docs/config.html#babel dates map
[language-specific functions]: {{ site.baseurl }}/docs/functions.html#linguistic
[simple language functions]: {{ site.baseurl }}/docs/functions.html#simplelang
[`nice_number()`]: {{ site.baseurl }}/docs/functions.html#nice_number
[`update_nice_numbers()`]: {{ site.baseurl }}/docs/functions.html#update_nice_numbers
[`currency_symbol()`]: {{ site.baseurl }}/docs/functions.html#currency_symbol
[`currency()`]: {{ site.baseurl }}/docs/functions.html#currency
[`get_user_info()`]: {{ site.baseurl }}/docs/functions.html#get_user_info
[`set_user_info()`]: {{ site.baseurl }}/docs/functions.html#set_user_info
[`language_from_browser()`]: {{ site.baseurl }}/docs/functions.html#language_from_browser
[`process_action()`]: {{ site.baseurl }}/docs/functions.html#process_action
[actions]: {{ site.baseurl }}/docs/functions.html#url_action
