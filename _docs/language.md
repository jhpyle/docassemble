---
layout: docs
title: Language Support
short_title: Language Support
---

**docassemble** allows you to write a single interview that asks
questions differently depending on the user's language and locale.  It
also allows [Unicode] to be used in user-facing text and
user input.  With these features, **docassemble** should be fully
usable in languages other than English.

# Configuration

By default, the active language and locale are determined by the
[`language`] and [`locale`] settings in the **docassemble**
[configuration].

The value of [`language`] must be a two-character lowercase
[ISO-639-1] code.  For example, Spanish is `es`, French is `fr`, and
Arabic is `ar`.

The value of [`locale`] must be a locale name without the language
prefix, such as `US.utf8` or `DE.utf8`.  Any locale you use must be
available on your system.

The functions [`set_language()`] and [`set_locale()`] from
[`docassemble.base.util`] will change the active language, dialect,
and locale.  (The dialect is relevant only for the text-to-speech
feature, which is controlled by the [special variable `speak_text`].)

If you write functions that need to know the current language or
locale, use the [`get_language()`] and [`get_locale()`] function from
the [`docassemble.base.util`] module.  Also note that there is a
function [`get_dialect()`] for retrieving the dialect.

The [`language`] and [`locale`] settings have the following effects:

* When **docassemble** looks for a [`question`] or [`code`] block that
  defines a variable, it first tries [`question`]s and [`code`] blocks for
  which the [`language` modifier] is set to the active language
  (either explicitly or by operation of the [`default language`]
  [initial block]).  If **docassemble** does not find any such
  [`question`]s or [`code`] blocks, it looks for ones that do not have
  [`language` modifier] set.
* Built-in words like "Continue" for a continue button, or "Login" for
  the login link, can be translated into the active language.
  Whenever **docassemble** prints such a word or phrase, it calls the
  [`word()`] function from the [`docassemble.base.util`] module.  Calling
  `word('Login')` will look up the word `Login` in a translation
  table.  If the [`word()`] function finds the word `Login` in the
  translation table for the active language, it will return
  the translated value.  If it does not find a translation, it will
  return `Login`.  For more information about how [`word()`] works, see
  [functions].  For information on how to define translations for a
  server, see [configuration].
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

# Best practices for single-language interviews

If your interview only works in one language, do not set the
[`language` modifier] for any blocks, do not use [`default language`],
and do not call [`set_language()`] or [`set_locale()`].  Instead,
simply make sure that the default language and locale in the
[configuration] are set to the correct values.

# Best practices for multi-language interviews

If you use the [`language` modifier] or the [`default language`]
[initial block], you will need to have [`initial`] code that calls
[`set_language()`].  **docassemble** does not remember the active
language from one screen to the next, but the [`initial`] code will
make sure that it is always set to the correct value.

{% highlight yaml %}
---
include:
  - basic-questions.yml
---
initial: true
code: |
  set_language(user.language)
---
generic object: Individual
question: |
  What language ${ x.do_question('speak') }?
field: x.language
choices:
  - English: en
  - Español: es
---
{% endhighlight %}

If you are writing an interview that offers multiple language options,
you may want to break out your interview into different files:

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
initial: true
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

([Try it out here]({{ site.demourl }}?i=docassemble.demo:data/questions/bestnumber/interview.yml){:target="_blank"}.)

# Creating documents in languages other than English

The [documents] feature, which allows RTF and PDF documents to be
created from [Markdown] text with [Mako] templating, supports
languages other than English to the extent that RTF, [Pandoc], and
[LaTeX] do.  [LaTeX] has support for internationalization, and the
default [LaTeX] template will load [polyglossia] or [babel], depending
on what is available.  The language used by [LaTeX] can be set using
the `metadata` entries `lang` and `mainlang` in the `attachment`
specification.  For some languages, you may need to write your own
templates in order to enable fonts that support your language.

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
