#What does it do?

This plugin replaces the default checkboxes and radio inputs for better looking ones.

##Features:

* Compatible with IE7+, Chrome, Firefox, Safari and mobile browsers;
* Custom design, kindly provided by [Bruno O. Barros](http://ilustrebob.com.br/);
* Four color options (Twitter bootstrap) + [editable PSD](http://arthurgouveia.com/prettyCheckable/goodies/prettyCheckable.psd);
* Better look & size;
* Super easy implementation;
* Selectable with Tab and checkable with keyboard;
* Change events & Chainning preserved;
* More area of click/touch. A plus for mobile devices.

##Install & Setup

[Download the files](https://github.com/arthurgouveia/prettyCheckable/zipball/master) (or [fork it](https://github.com/arthurgouveia/prettyCheckable)) and include jQuery 1.9+ and prettyCheckable files (make sure you're mapping the sprite correctly on your CSS):

    <link rel="stylesheet" href="js/prettyCheckable/prettyCheckable.css">

    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
    <script src="js/prettyCheckable/prettyCheckable.js"></script>

Write your inputs and add a class for the jQuery selector:

    <input type="checkbox" class="myClass" value="yes" id="answer" name="answer"/>

Setup prettyCheckable for your input and you're all set:

    $('.myClass').prettyCheckable();

If you have several inputs, make a loop and call the plugin on each one:

    for (var i = inputList.length - 1; i >= 0; i--) {
        $(inputList[i]).prettyCheckable();
    }

You can start the plugin with the options you see on the documentation bellow and they will be applied to all matching inputs:

    $('.myClass').prettyCheckable({
      color: 'red'
    });

If you want to apply something to all the inputs but you need a few specific ones to be different, you can add the specifics inline:

    <input type="checkbox" class="myClass" value="yes" id="answer" name="answer" data-color="green" />

##Documentation

*None of the parameters is mandatory.*

###Customizing

####CSS only (AKA lame option)

You can simply use the images inside /img/sprite and create your own sprite manually. Make sure you update your sprite name, match it to the url inside your CSS and also the states positions for each one of the types and states the checkables can assume.

####Grunt & Compass (Fuck Yeah Method)

Sprites are being automagically generated with the help of Compass.
The sizes of all the checkables are assumed to be the same, so that's calculated from your first image size.
The positioning of each sprite is also mapped automatically.

- Clone this repo;
- Install Sass &amp; Compass;
- Run 'npm install';
- Run 'grunt' to build it or 'grunt w' to watch for changes.

ps.: If you're wondering why I set a capital letter in front of each file, that's done because I want Compass to generate the sprite it in a logical order. Found a better way? Pull Request!

###Options

<table>
  <tbody>
    <tr>
      <td>Name</td>
      <td>Values</td>
      <td>Description</td>
    </tr>
    <tr>
      <td>
        <strong>label</strong>
      </td>
      <td>
        string<br/>
        <em>The value for your label</em>
      </td>
      <td>
        <p>If informed, this will overwrite the auto-detected label (if exists) but is overwriten by the inline-option "data-label"</p>
      </td>
    </tr>
    <tr>
      <td>
        <strong>labelPosition</strong>
      </td>
      <td>
        string<br>
        <em>left, right(default)</em>
      </td>
      <td>
        <p>This is the position where the label for the inputs should be placed, if informed.</p>
      </td>
    </tr>
    <tr>
      <td>
        <strong>customClass</strong>
      </td>
      <td>
        string<br>
        <em>A class name.</em>
      </td>
      <td>
        <p>This will add a class you want to the wrapping div surrounding the input, created by the plugin.</p>
      </td>
    </tr>
  </tbody>
</table>

###Inline Options

*All inline configs will overwrite the ones you initialized the plugin with.*

<table class="table table-striped">
  <tbody>
    <tr>
      <td>Name</td>
      <td>Values</td>
      <td>Description</td>
    </tr>
    <tr>
      <td>
        <strong>data-label</strong>
      </td>
      <td>
        string<br>
        <em>Text for your label</em>
      </td>
      <td>
        <p>If informed, this will create a label attached to the input.</p>
      </td>
    </tr>
    <tr>
      <td>
        <strong>data-labelPosition</strong>
      </td>
      <td>
        string<br>
        <em>left, right(default)</em>
      </td>
      <td>
        <p>This is the position where the label for the inputs should be placed, if informed.</p>
      </td>
    </tr>
    <tr>
      <td>
        <strong>data-customClass</strong>
      </td>
      <td>
        string<br>
        <em>A class name.</em>
      </td>
      <td>
        <p>This will add a class you want to the wrapping div surrounding the input, created by the plugin.</p>
      </td>
    </tr>
  </tbody>
</table>

###Methods

<p><em>Using prettyCheckable is already pretty darn easy, right? What if I told you using it's methods is easy peasy lemon squeezy? Just use</em></p>

    $('#myInput').prettyCheckable('check');

<table class="table table-striped">
  <tr>
    <td>Name</td>
    <td>Description</td>
  </tr>
  <tr>
    <td class="param-name">
      <strong>enable OR disable</strong>
    </td>

    <td>
      <p>Um... well... it enables/disables the input.</p>
    </td>
  </tr>
  <tr>
    <td class="param-name">
      <strong>check OR uncheck</strong>
    </td>
    <td>
      <p>Um... well... it checks/unchecks the input.</p>
    </td>
  </tr>
  <tr>
    <td class="param-name">
      <strong>destroy</strong>
    </td>
    <td>
      <p>Gives you your ugly input back, destroying the DOM wrapped around it and creating a label (if there was one present) right before it.</p>
    </td>
  </tr>
</table>

### Knockout compatibility

####Html
    <input type="checkbox" data-bind="checked: isFurnished, prettyCheckable: {color: 'gray', label: 'Furnished' }"/>

####Custom binding
    ko.bindingHandlers.prettyCheckable = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            var val = ko.utils.unwrapObservable(valueAccessor());
            $(element).prettyCheckable({ label: val.label });
        },
        update: function(element, valueAccessor, allBindingsAccessor, viewModel, bindingContext) {
            $(element).trigger("change");
        }
    };

##Customization

If you want to create your own designed checkboxes or you just need a different color set, download the [prettyCheckable PSD](http://arthurgouveia.com/prettyCheckable/goodies/prettyCheckable.psd), do whatever you need to, add the entries to your CSS and pass the name of your color/style in the color or customClass parameters, according to the CSS code you can see on [prettyCheckable.css](http://arthurgouveia.com/prettyCheckable/js/prettyCheckable/prettyCheckable.css).
