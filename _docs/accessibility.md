---
layout: docs
title: Accessibility
short_title: Accessibility
---

**docassemble** has a number of features that facilitate accessibility
for persons with disabilities, including:

* A built-in [screen reader].
* Use of text elements that are hidden in the normal web browser view
  but that are seen by screen readers.
* Use of [ARIA attributes] to give hints to assistive technologies
  about the purpose of HTML elements.
* Use of [label tags], [title attributes], and other [HTML] features
  that facilitate the use of assistive technologies.
* Use of [CSS] and [JavaScript] to facilitate use of the keyboard in
  place of the mouse, so that users can navigate using Tab and
  shift-Tab.
* Use of [alt text] in images and features for interview developers to
  include [alt text] in images that they insert into interviews, such
  as the `alt_text` attribute of [`DAFile`], the `alt_text` keyword
  parameter to the [`show()`] method, the [`set_alt_text()`] and
  [`get_alt_text()`] methods, and the variant of the [`FILE`]
  tag that includes [alt text].  The [Markdown] syntax for including
  images supports [alt text].

The **docassemble** user interface is built on [Bootstrap 4.0], which
has [accessibility features and limitations].  The default Bootstrap
color scheme does not have sufficient contrast to meet the [WCAG]
guidelines.  You may want to create your own [Bootstrap theme] with
increased color contrast.

Here are some tips on creating accessible interviews:

* Always set [alt text] on any images.  Set the [alt text] to empty
  text (`''`) when appropriate, but never omit the alt text altogether.
* Use plain language.  Use the "Source" tab to review the reading
  level of the text of your questions.  If you set a 6th grade reading
  level as your target, all of your users will benefit, even if they
  are educated professionals.
* When customizing, design for all devices, not for a particular
  device or devices.  If the HTML and CSS are device-agnostic and
  adhere to standards, it is more likely that users of assistive
  technology will be able to understand the page.
* Refrain from unnecessary user interface customization.  Plain
  vanilla **docassemble** has pretty good accessibility.  If your
  customizations make the interface more accessible, or you design
  your customizations with accessibility in mind, that's fine, but if
  you are not an expert web developer, it is more likely that your
  customizations will reduce accessibility.  If you customize for
  purposes of eye candy or marginal interface improvements, you may
  force users with disabilities to pay a big price for a small benefit
  to other users.
* Use the [WAVE Toolbar] to see if there are any accessibility errors
  or warnings in your interview that you can address.  Note that since
  **docassemble** is a single page application, you may need to
  refresh the screen before using the toolbar.
  
Even with a Bootstrap theme that has sufficient color contrast, there
may be some accessibility limitations in **docassemble**.  If you
identify any, create a [GitHub issue].

[GitHub issue]: https://github.com/jhpyle/docassemble/issues
[Bootstrap theme]: https://pikock.github.io/bootstrap-magic/app/#!/editor
[WCAG]: https://www.w3.org/WAI/standards-guidelines/wcag/
[Bootstrap 4.0]: https://getbootstrap.com/docs/4.0/getting-started/introduction/
[accessibility features and limitations]: https://getbootstrap.com/docs/4.0/getting-started/accessibility/
[HTML]: https://en.wikipedia.org/wiki/HTML
[label tags]: https://www.w3schools.com/tags/tag_label.asp
[title attributes]: https://www.w3schools.com/tags/att_title.asp
[`FILE`]: {{ site.baseurl }}/docs/markup.html#inserting images
[`DAFile`]: {{ site.baseurl }}/docs/objects.html#DAFile
[`show()`]: {{ site.baseurl }}/docs/objects.html#DAFile.show
[`set_alt_text()`]: {{ site.baseurl }}/docs/objects.html#DAFile.set_alt_text
[`get_alt_text()`]: {{ site.baseurl }}/docs/objects.html#DAFile.get_alt_text
[CSS]: https://en.wikipedia.org/wiki/Cascading_Style_Sheets
[JavaScript]: https://en.wikipedia.org/wiki/JavaScript
[ARIA attributes]: https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA
[screen reader]: {{ site.baseurl }}/docs/initial.html#speak_text
[alt text]: https://moz.com/learn/seo/alt-text
[Markdown]: {{ site.baseurl }}/docs/markup.html
[WAVE Toolbar]: https://wave.webaim.org/extension/
