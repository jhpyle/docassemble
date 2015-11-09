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

By default, the active language and locale are determined by the
`language` and `locale` settings in the **docassemble** [configuration].

The value of `language` must be a two-character lowercase [ISO-639-1]
code.  For example, Spanish is `es`, French is `fr`, and Arabic is `ar`.

The value of `locale` must be a locale name without the language
prefix, such as `US.utf8` or `DE.utf8`.  Any locale you use must be
available on your system.

The functions `set_language` and `set_locale` from
`docassemble.base.util` will change the active language and locale.
If you write functions that need to know the current language or
locale, use the `get_language()` and `get_locale()` function from the
`docassemble.base.util` module.

The `language` and `locale` settings have the following effects:

* When **docassemble** looks for a `question` or `code` block that
  define a variable, it first tries `question`s and `code` blocks for
  which the `language` [modifier] is set to the active language.  If it
  does not find any such `question`s or `code` blocks, it looks for
  ones that do not have `language` [modifier] set.
* Built-in words like "Continue" for a continue button, or "Login" for
  the login link, can be translated into the active language.
  Whenever **docassemble** prints such a word or phrase, it calls the
  `word()` function from the `docassemble.base.util` module.  Calling
  `word('Login')` will look up the word `Login` in a translation
  table.  If the `word()` function finds the word `Login` in the
  translation table for the active language, it will return
  the translated value.  If it does not find a translation, it will
  return `Login`.
* Some functions have language-specific responses, such as `today()`
  in the `docassemble.base.util` module, which returns today's date in
  a readable format such as "October 31, 2015" (for language `en`) or
  "31 octobre 2015" (for language `fr`).
* When **docassemble** highlights `terms` in a question (see
  [initial blocks]), it will only highlight words specified in `terms`
  blocks for which `language` matches the language of the question.
  Or, if the question does not have a `language` set, **docassemble**
  will look for a `terms` block that does not have `language` set.
* When **docassemble** displays `interview help` text, it will only
  display the content of `interview help` blocks for which the
  `language` is the same as the language of the question.  Or, if the
  question does not have a `language` set, **docassemble** will look
  for an `interview help` block that does not have `language` set.

## Best practices for single-language interviews

If your interview only works in one language, do not set `language`
for any blocks and do not use `default language`, and do not call
`set_language` or `set_locale`.  Instead, simply make sure that the
default language and locale in the [configuration] are set to the
correct values.

## Best practices for multi-language interviews

If you use the `language` [modifier] or the `default language`
[initial block], you will need to have `initial` code that calls
`set_language()`.  **docassemble** does not remember the active
language from one question to the next, but the `initial` code will
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

## Creating documents in languages other than English

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
[configuration]: {{ site.baseurl }}/docs/configuration.html
[modifier]: {{ site.baseurl }}/docs/modifiers.html
[Unicode]: https://en.wikipedia.org/wiki/Unicode
[documents]: {{ site.baseurl }}/docs/documents.html
[Mako]: http://www.makotemplates.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[LaTeX]: http://www.latex-project.org/
[polyglossia]: https://www.ctan.org/pkg/polyglossia
[babel]: https://www.ctan.org/pkg/babel
