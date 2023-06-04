---
layout: docs
title: Customizing the user interface
short_title: UI Customization
---

This section provides an overview of ways that you can customize the
user interface that end users see.

# <a name="bootstrap"></a>Bootstrap

You can give **docassemble** a new "skin" by creating your own
[Bootstrap] theme. This can be configured globally for the server with
the [`bootstrap theme` Configuration directive] or for a particular
interview with the [`bootstrap theme`] feature.

Bootstrap has a "night mode" that is activated automatically based on
the browser or OS settings. You can prevent the browser from switching
into "night mode" using the [`auto color scheme`] Configuration
directive.

# <a name="css"></a>CSS customization

If you are happy with the Bootstrap theme but you want to make tweaks
to CSS in particular places, you can customize the CSS by providing
your own [`css` files]. You can store these files in the Static folder
of the Playground, or the `data/static` folder of your docassemble
add-on package. It is also possible to enable CSS files globally on
the server using the [`global css`] Configuration directive.

You can use the Inspect tool of your browser to look at the HTML
elements you want to modify, and they will usually have CSS classes
prefixed with `da`, or an `id`. You can write CSS rules that target
these elements. You can add CSS classes to field elements using the
[`css class`] field modifier. The [`action buttons`] interface allows
for the specification of a CSS class. You can set the [`css class`
modifier] on a `question` in order to attach a CSS class to the
`<body>` element for that question.

The CSS class of HTML tables can be customized at the `question` level
with the [`table css class` modifier] or at the interview level with
the `table css class` [screen part].

You can globally change the Bootstrap color that is used for the
various types of buttons by setting the [`buttons colors`]
Configuration directive. You can also modify the [`button style`] and
[`button size`].

If you use the `footer` [screen part], you can change its CSS class
using the [`footer css class`] Configuration directive.

# <a name="screen parts"></a>Screen parts

Many UI elements can be customized using [screen parts]. Screen parts
refer to particular parts of the screen, such as the interview title
in the navigation bar, the name of the tab in the web browser, or the
optional page footer. You can use screen parts to insert text or HTML
into various areas of the screen. The [screen parts] system can also
be used to customize the text and color of standard buttons, like back
buttons and help buttons.

Some of these screen parts exist on non-interview pages. These can be
customized using Configuration directives for the [screen parts of
administrative pages].

# <a name="navigation bar"></a>Navigation bar

The main navigation bar at the top of the screen can be hidden
entirely with [`hide navbar`].

By default, **docassemble** uses a Bootstrap "dark" appearance for the
navigation bar, but this can be customized using [`inverse navbar`].

The back button can be removed with [`navigation back button`]. You
can put a back button next to the Continue button using [`question
back button`].

After the back button, the navigation bar shows the `title` [screen
part]. On small screens, the `short title` [screen part] appears
instead. It is important to test interviews on a variety of devices to
make sure that the title looks appropriate. The `title` and `short
title` can be replaced with raw HTML using the `logo` and `short logo`
[screen parts]. Using large logos is strongly discouraged because
users may be using your site on small-screen devices, and they will be
annoyed that your advertising is taking up a large percent of the
screen. If your logo increases the height of the navigation bar, you
will need to customize the CSS to [correct for this].

If you see "</>" in the navigation bar when using an interview, that
means you are in debug mode. This is turned on by default when you are
using the Playground, but it is not appropriate in production. This is
controlled with the [`debug`] Configuration directive.

The interface in the upper-right corner, which reduces to a "hamburger
icon" on small screens, lets the user log in, or shows a menu, or
shows the exit button. This can be customized using:

* The [`show login` metadata specifier] or the [`show login`]
  Configuration directive.
* The [`menu_items` special variable], which lets you add your own
  items to the menu.
* The [`hide standard menu`] option in [`features`].
* The [`exit label`], [`exit link`], and [`exit url`] screen parts,
  which allow you to customize the exit button.
* The [`administrative interviews`] Configuration directive, which
  lets you add items to the menu for launching particular interviews
  or visiting particular URLs.
* The [`show profile link`] Configuration directive.
* The [`show interviews link`] Configuration directive.
* The [`show dispatch link`] Configuration directive.
* The [`hide corner interface`] feature, which completely removes the
  corner interface.

You can insert your own HTML in the upper-right corner of the screen
using the [`navigation bar html`] screen part. This is not affected by
[`hide corner interface`].

# <a name="favicon"></a><a name="progress bar"></a><a name="sections"></a>Other UI elements

You can customize the [favicon] using the [`favicon`] Configuration
directive. If you want a different favicon in different interviews,
you can use [JavaScript] to alter the [favicon].

You can add a [progress bar] to the top of the screen. You can also
add a [secondary navigation bar] that shows the sections of the
interview. This navigation bar can be vertical on the left side of the
screen or horizontal across the top of the screen. It is also possible
to insert a version of the navigation bar into the body of a question.

[`features`]: {{ site.baseurl }}/docs/initial.html#features
[`hide corner interface`]: {{ site.baseurl }}/docs/initial.html#hide corner interface
[`question back button`]: {{ site.baseurl }}/docs/initial.html#question back button
[`navigation bar html`]: {{ site.baseurl }}/docs/initial.html#navigation bar html
[secondary navigation bar]: {{ site.baseurl }}/docs/initial.html#navigation bar
[progress bar]: {{ site.baseurl }}/docs/initial.html#progress bar
[`css` files]: {{ site.baseurl }}/docs/initial.html#css
[`hide navbar`]: {{ site.baseurl }}/docs/initial.html#hide navbar
[`inverse navbar`]: {{ site.baseurl }}/docs/initial.html#inverse navbar
[`navigation back button`]: {{ site.baseurl }}/docs/initial.html#navigation back button
[`bootstrap theme`]: {{ site.baseurl }}/docs/initial.html#bootstrap theme
[`bootstrap theme` Configuration directive]: {{ site.baseurl }}/docs/config.html#bootstrap theme
[`inverse navbar`]: {{ site.baseurl }}/docs/initial.html#inverse navbar
[`hide navbar`]: {{ site.baseurl }}/docs/initial.html#hide navbar
[`hide standard menu`]: {{ site.baseurl }}/docs/initial.html#hide standard menu
[`exit label`]: {{ site.baseurl }}/docs/initial.html#exit label
[`exit link`]: {{ site.baseurl }}/docs/initial.html#exit link
[`exit url`]: {{ site.baseurl }}/docs/initial.html#exit url
[`administrative interviews`]: {{ site.baseurl }}/docs/config.html#administrative interviews
[`show profile link`]: {{ site.baseurl }}/docs/config.html#show profile link
[`show interviews link`]: {{ site.baseurl }}/docs/config.html#show interviews link
[`show dispatch link`]: {{ site.baseurl }}/docs/config.html#show dispatch link
[`show login` metadata specifier]: #show login
[`show login`]: {{ site.baseurl }}/docs/config.html#show login
[`css class`]: {{ site.baseurl }}/docs/fields.html#css class
[`id`]: {{ site.baseurl }}/docs/modifiers.html#id
[`css class` modifier]: {{ site.baseurl }}/docs/questions.html#css class
[`table css class` modifier]: {{ site.baseurl }}/docs/questions.html#table css class
[`action buttons`]: {{ site.baseurl }}/docs/questions.html#action buttons
[screen parts]: {{ site.baseurl }}/docs/questions.html#screen parts
[screen part]: {{ site.baseurl }}/docs/questions.html#screen parts
[`auto color scheme`]: {{ site.baseurl }}/docs/config.html#auto color scheme
[`footer css class`]: {{ site.baseurl }}/docs/config.html#footer css class
[`global css`]: {{ site.baseurl }}/docs/config.html#global css
[Bootstrap]: https://getbootstrap.com/
[screen parts of administrative pages]: {{ site.baseurl }}/docs/config.html#customization
[correct for this]: {{ site.baseurl }}/docs/config.html#bootstrap theme
[`debug`]: {{ site.baseurl }}/docs/config.html#debug
[`menu_items` special variable]: {{ site.baseurl }}/docs/special.html#menu_items
[`buttons colors`]: {{ site.baseurl }}/docs/config.html#buttons colors
[`button style`]: {{ site.baseurl }}/docs/config.html#button style
[`button size`]: {{ site.baseurl }}/docs/config.html#button size
[favicon]: https://en.wikipedia.org/wiki/Favicon
[`favicon`]: {{ site.baseurl }}/docs/config.html#favicon
[JavaScript]: {{ site.baseurl }}/docs/initial.html#javascript
