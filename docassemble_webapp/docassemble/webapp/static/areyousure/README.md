Are You Sure? - A light "dirty forms" JQuery Plugin
======
**Version:** 1.9

*Are-you-sure* (```jquery.are-you-sure.js```) is simple light-weight "dirty 
form" JQuery Plugin for modern browsers.  It helps prevent users from losing 
unsaved HTML Form changes by promoting the user to save/submit.

It's simple to use.  Just add the following line to your page's ready 
function:

```javascript
$('form').areYouSure();
```

*Are-you-sure* is a minimal plugin for modern browsers.  There are plenty of 
"dirty forms" implementations out there, however they all seemed very 
heavyweight and over-engineered...! Most were written some time back and 
contain many 'hacks' to support legacy browsers, and/or rely on other fat 
dependencies such as FaceBox or jQueryUI.  *Are-you-sure* solves this by
doing this simple task in the simplest possible way.

*Are-you-sure* is as simple as it gets:

 * 100% JS with zero dependencies and no external CSS.
 * Leverages `onBeforeUnload` to detect all page/browser exit events.
 * Works on forms of any size.
 * Correct state management - if a user edits then restores a value, the form 
   is not considered dirty.
 * Easy to understand - less than a "terminal screen" of code!
 * Graceful degradation on legacy browsers (i.e. if you're running an old 
   browser... remember to save :-)

### Basic Usage

```javascript

$(function() {

    // Enable on all forms
    $('form').areYouSure();

    // Enable on selected forms
    $('form.dirty-check').areYouSure();

    // With a custom message
    $('form').areYouSure( {'message':'Your profile details are not saved!'} );

}
```
To ignore selected fields from the dirtyness check: 

```html
  <form id="myForm" name="myform" action="/post" method="post">

    Field 1: (checked)  <input type="text" name="field1"> <br />
    Field 2: (ignored): <input type="text" name="field2" data-ays-ignore="true"> <br />
    Field 3: (ignored): <input type="text" name="field3" class="ays-ignore"> <br />

    <input type="submit" value="Submit">

  </form>
```

### Advanced Usage

```javascript

$(function() {

    /*
    *  Make Are-You-Sure "silent" by disabling the warning message 
    *  (tracking/monitoring only mode). This option is useful when you wish to 
    *  use the dirty/save events and/or use the dirtyness tracking in your own 
    *  beforeunload handler.
    */
    $('form').areYouSure( {'silent':true} );
	
    /*
    *  Dirtyness Change Events
    *  Are-You-Sure fires off "dirty" and "clean" events when the form's state
    *  changes. You can bind() or on(), these events to implement your own form
    *  state logic.  A good example is enabling/disabling a Save button.
    *
    *  "this" refers to the form that fired the event.
    */
    $('form').on('dirty.areYouSure', function() {
      // Enable save button only as the form is dirty.
      $(this).find('input[type="submit"]').removeAttr('disabled');
    });
    $('form').on('clean.areYouSure', function() {
      // Form is clean so nothing to save - disable the save button.
      $(this).find('input[type="submit"]').attr('disabled', 'disabled');
    });

    /*
    *  It's easy to test if a form is dirty in your own code - just check
    *  to see if it has a "dirty" CSS class.
    */
    if ($('#my-form').hasClass('dirty')) {
        // Do something
    }

    /*
    *  If you're dynamically adding new fields/inputs, and would like to track 
    *  their state, trigger Are-You-Sure to rescan the form like this:
    */
    $('#my-form').trigger('rescan.areYouSure');

    /*
    *  If you'd like to reset/reinitialize the form's state as clean and 
    *  start tracking again from this new point onwards, trigger the
    *  reinitalize as follows. This is handy if say you've managing your
    *  own form save/submit via asyc AJAX.
    */
    $('#my-form').trigger('reinitialize.areYouSure');

    /*
    *  In some situations it may be desirable to look for other form
    *  changes such as adding/removing fields. This is useful for forms that
    *  can change their field count, such as address/phone contact forms.
    *  Form example, you might remove a phone number from a contact form
    *  but update nothing else. This should mark the form as dirty.
    */
    $('form').areYouSure( {'addRemoveFieldsMarksDirty':true} );
    
    /*
    *  Sometimes you may have advanced forms that change their state via
    *  custom JavaScript or 3rd-party component JavaScript. Are-You-Sure may 
    *  not automatically detect these state changes. Examples include:
    *     - Updating a hidden input field via background JS.
    *     - Using a [rich WYSIWYG edit control](https://github.com/codedance/jquery.AreYouSure/issues/17).
    *  One solution is to manually trigger a form check as follows:
    */
    $('#my-form').trigger('checkform.areYouSure');
	
    /*
    *  As an alternative to using events, you can pass in a custom change 
    *  function.
    */
    $('#my-adv-form').areYouSure({
        change: function() {
              // Enable save button only if the form is dirty. i.e. something to save.
              if ($(this).hasClass('dirty')) {
                $(this).find('input[type="submit"]').removeAttr('disabled');
              } else {
                $(this).find('input[type="submit"]').attr('disabled', 'disabled');
              }
            }
    });

    /*
    *  Mixing in your own logic into the warning.
    */
    $('#my-form').areYouSure( {'silent':true} );
    $(window).on('beforeunload', function() {
        isSunday = (0 == (new Date()).getDay());
        if ($('#my-form').hasClass('dirty') && isSunday) {
            return "Because it's Sunday, I'll be nice and let you know you forgot to save!";
        }
    }
    
}
```
The [demo page](http://www.papercut.com/products/free_software/are-you-sure/demo/are-you-sure-demo.html)
shows the advanced usage options in more detail.


### Install
Are-You-Sure is a light-weight jQuery plugin - it's a single standalone 
JavaScript file. You can download the 
[jquery.are-you-sure.js](https://raw.github.com/codedance/jquery.AreYouSure/master/jquery.are-you-sure.js)
file and include it in your page. Because it's so simple it seems a shame 
to add an extra browser round trip. It's recommended that you consider
concatenating it with other common JS lib files, and/or even cut-n-pasting 
the code (and license header) into one of your existing JS files.

For experimental Mobile Safari support, also include ```ays-beforeunload-shim.js``` 
(see Known Issues below).

*Are-you-sure* may also be installed with [Bower](http://twitter.github.com/bower/):

```bash
$ bower install jquery.are-you-sure
```

If you're using, or like, *Are-you-sure* make sure you **star/watch** this project
so you can stay up-to-date with updates.

### Demo
This [demo page](http://www.papercut.com/products/free_software/are-you-sure/demo/are-you-sure-demo.html)
hosts a number of example forms.

### Supported Browsers
*Are-you-sure* has been tested on and fully supports the following browsers:

* IE 9 through 11
* Google Chrome (versions since 2012)
* Firefox (versions since 2012)
* Safari (versions since 2012)

Experimental support is available on iOS and Opera via the *beforeunload* shim (see below).

### Known Issues & Limitations

#### Mobile Safari and Opera
The ```windows.beforeunload``` event is not supported on iOS (iPhone, iPad, and iPod). An
experimental shim offering partial *beforeunload* emulation is provided to help plug this gap.
It works by scanning the page for anchor links and augments the default behaviour to first
check with *Are-you-sure* before navigating away. To use, simply include 
```ays-beforeunload-shim.js``` in your page.

#### Firefox
The custom message option may not work on Firefox ([Firefox bug 588292](https://bugzilla.mozilla.org/show_bug.cgi?id=588292)).

### Development
The aim is to keep *Are-you-sure* simple and light. If you think you have 
a good idea which is aligned with this objective, please voice your thoughts 
in the issues list.

#### Pull Requests
If possible, please submit your pull request against the most recent ```dev-*``` branch rather than master. This will make it easier to merge your code into the next planned release.

#### Running tests
```bash
$ npm install
$ npm test
```

### Release History

**2014-08-13** (1.9) - This is a minor bugfix release:

* Addressed issue [#45](https://github.com/codedance/jquery.AreYouSure/issues/55) seen with empty select fields.
* Thanks [valgen](https://github.com/valgen) and [tus124](https://github.com/tus124) for the contribution.

**2014-06-22** (1.8) - This is a minor bugfix release:

* Fixed NPE that may occur when using a 'multiple' option field.
* Minor timing tweak to help mitigate bypass issue raised in [#45](https://github.com/codedance/jquery.AreYouSure/issues/45)
* Thanks [apassant](https://github.com/apassant) and [amatenkov](https://github.com/amatenkov) for the contribution.

**2014-05-28** (1.7)

* Fixed multiple warning dialogs that may appear on IE and recent versions of Chrome
* Experimental support for iOS Mobile Safari (via a *beforeunload* shim)
* Various minor fixes (e.g. support input fields with no type=)
* Minor performance improvements on pages with multiple forms
* Improved documentation and examples
* Thanks to [lfjeff](https://github.com/lfjeff) and [aqlong](https://github.com/aqlong) for the contribution and ideas!

**2014-02-07** (1.6)

* Add field count tracking (```addRemoveFieldsMarksDirty```) (contrib *jonegerton*)
* Added event to manually trigger a form check/recheck  (contrib *jonegerton*)
* Thanks to [jonegerton](https://github.com/jonegerton) for the contribution!

**2013-11-15** (1.5)

* Added support for HTML5 input field types. (contrib *albinsunnanbo*)
* New option to reinitialize/reset the dirty state.  This is handy if you're managing your own async submit/save using AJAX. (contrib *albinsunnanbo*)
* Thanks to [albinsunnanbo](https://github.com/albinsunnanbo) for the contribution!

**2013-10-2** (1.4)

* Added dirty and clean "events" 
* Added an option to disable the message (dirty tracking only)
* Added an option to rescan a form to look/detect any new fields

**2013-07-24** - Minor fix - don't fail if form elements have no "name" attribute.

**2013-05-14** - Added support for form reset buttons (contributed by codev).

**2013-05-01** - Added support for hidden and disabled form fields.

**2013-02-03** - Add demo page.

**2013-01-28** - Add ```change``` event support and a demo page.

**2012-10-26** - Use dashes in class names rather than camel case.

**2012-10-24** - Initial public release.


### Prerequisites
jQuery version 1.4.2 or higher. 2.0+ or 1.10+ recommended.


### License
The same as JQuery...

    jQuery Plugin: Are-You-Sure (Dirty Form Detection)
    https://github.com/codedance/jquery.AreYouSure/
 
    Copyright (c) 2012-2014, Chris Dance - PaperCut Software http://www.papercut.com/
    Dual licensed under the MIT or GPL Version 2 licenses.
    http://jquery.org/license
