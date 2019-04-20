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

# Configuration

By default, the active language and locale are determined by the
[`language`] and [`locale`] settings in the **docassemble**
[configuration].

The value of [`language`] must be a two-character lowercase
[ISO-639-1] code.  For example, English is `en`, Spanish is `es`,
French is `fr`, and Arabic is `ar`.

The value of [`locale`] must be a locale name without the language
prefix, such as `US.utf8` or `DE.utf8`.  Any locale you use must be
installed on your system.  (See the [`other os locales`] configuration
directive.)

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
  "31 octobre 2015" (for language `fr`).
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

# Best practices for single-language interviews

If your interview only works in one language, do not set the
[`language` modifier] for any blocks, do not use [`default language`],
and do not call [`set_language()`] or [`set_locale()`].  Instead,
simply make sure that the default [`language`] and [`locale`] in the
[configuration] are set to the correct values.

# Best practices for multi-language interviews

If you have an interview that needs to function in multiple languages,
you will need to have [`initial`] code that calls [`set_language()`].
**docassemble** does not remember the active language from one screen
to the next (in a multi-user interview, the language could depend on
who the user is), but the [`initial`] code will make sure that it is
always set to the correct value.

{% highlight yaml %}
---
include:
  - basic-questions.yml
---
initial: True
code: |
  set_language(user.language)
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
---
modules:
  - docassemble.base.util
---
initial: True
code: |
  set_language(user_language)
  need(final_screen)
---
question: |
  What language do you speak?  (¿Qué idioma habla?)
choices:
  - English: en
  - Español: es
field: user_language
---
code: |
  best_number = favorite_number + 1
---
{% endhighlight %}

The contents of `en.yml` are:

{% highlight yaml %}
---
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
---
{% endhighlight %}

The contents of `es.yml` are:

{% highlight yaml %}
---
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
---
{% endhighlight %}

Finally, the contents of `interview.yml` are:

{% highlight yaml %}
---
include:
  - code.yml
  - en.yml
  - es.yml
---
{% endhighlight %}

([Try it out here]({{ site.demourl }}/interview?i=docassemble.demo:data/questions/bestnumber/interview.yml){:target="_blank"}.)

# Working with third-party translators

While it is generally a good thing that **docassemble** allows you to
write complicated [`question`]s that make heavy use of [Mako]
templating, [Markdown], and embedded Python code, a downside is that
all of this "code" can make the translation process more complicated.
Translators may be confused by all of the code.  They may ask you to
convert your code to Microsoft Word, putting a great deal of
conversion work on you, or they may translate variable names when they
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

# Creating documents in languages other than English

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
[Pandoc]: http://johnmacfarlane.net/pandoc/
[`language` modifier]: {{ site.baseurl }}/docs/modifiers.html#language
[`language`]: {{ site.baseurl }}/docs/config.html#language
[`locale`]: {{ site.baseurl }}/docs/config.html#locale
[`set_language()`]: {{ site.baseurl }}/docs/functions.html#set_language
[`set_locale()`]: {{ site.baseurl }}/docs/functions.html#set_locale
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
[Download an interview phrase translation file]: {{ site.baseurl }}/docs/admin.html#translation file
[`sections`]: {{ site.baseurl }}/docs/initial.html#sections
[utility]: {{ site.baseurl }}/docs/admin.html#utilities
[Translate system phrases into another language]: {{ site.baseurl }}/docs/admin.html#translate
[use code]: {{ site.baseurl }}/docs/documents.html#template file code
[Morningside Translations]: https://www.morningtrans.com/
