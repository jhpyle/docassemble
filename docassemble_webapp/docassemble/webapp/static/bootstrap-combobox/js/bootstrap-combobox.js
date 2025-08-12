/* =============================================================
 * bootstrap-combobox.js v1.1.8
 * =============================================================
 * Copyright 2012 Daniel Farrell
 * Modified 2018 for docassemble by Jonathan Pyle
 * Modified 2022 for docassemble by Bryce Willey
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============================================================ */

(function ($) {
  "use strict";

  /* COMBOBOX PUBLIC CLASS DEFINITION
   * ================================ */

  var Combobox = function (element, options) {
    this.options = $.extend({}, $.fn.combobox.defaults, options);
    this.template = this.options.template || this.template;
    this.$source = $(element);
    if (this.$source.hasClass("da-combobox-floating")) {
      this.$label = this.$source.next("label");
    } else {
      this.$label = null;
    }
    this.$container = this.setup();
    this.$element = this.$container.find("input[type=text]");
    this.$target = this.$container.find("input[type=hidden]");
    this.mousedover = false;
    if (this.$source.attr("disabled") !== undefined) {
      this.$target.prop("disabled", true);
    }
    this.$button = this.$container.find(".dacomboboxtoggle");
    if (this.$float) {
      this.$menu = $(this.options.menu).insertAfter(this.$float);
    } else {
      this.$menu = $(this.options.menu).insertAfter(this.$element);
    }
    this.matcher = this.options.matcher || this.matcher;
    this.sorter = this.options.sorter || this.sorter;
    this.highlighter = this.options.highlighter || this.highlighter;
    this.clearIfNoMatch = this.options.clearIfNoMatch;
    this.shown = false;
    this.selected = false;
    this.refresh();
    this.transferAttributes();
    this.listen();
  };

  Combobox.prototype = {
    constructor: Combobox,

    setup: function () {
      //console.log('setup');
      var combobox = $(this.template());
      this.$source.before(combobox);
      this.$source.hide();
      if (this.$label) {
        this.$float = $('<div class="form-floating"></div>');
        var innerText = this.$label.text();
        var inputElement = combobox.find('input[type="text"]');
        inputElement.attr("placeholder", innerText);
        inputElement.detach();
        this.$label.detach();
        this.$float.append(inputElement, this.$label);
        this.$float.insertAfter(inputElement);
      } else {
        this.$float = null;
      }
      return combobox;
    },

    template: function () {
      //console.log('template');
      if (this.options.showButton) {
        if (this.options.functionalButton) {
          return (
            '<div class="combobox-container"> <input type="hidden" /> ' +
            '<div class="input-group"> <input type="text" alt="' +
            this.options.inputBox +
            '" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-activedescendant="" autocomplete="off" /> ' +
            '<button class="btn btn-outline-secondary dacomboboxtoggle" type="button" tabindex="-1" aria-label="' +
            this.options.buttonLabel +
            '" aria-expanded="false" aria-controls="id_controls">' +
            '<span class="fa-solid fa-caret-down"></span><span class="fa-solid fa-xmark"></span>' +
            "</button></div> </div>"
          );
        } else {
          return (
            '<div class="combobox-container"> <input type="hidden" /> ' +
            '<div class="input-group"> <input type="text" alt="' +
            this.options.inputBox +
            '" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-activedescendant="" autocomplete="off" /> ' +
            '<button class="btn btn-outline-secondary" type="button" disabled tabindex="-1">' +
            '<span class="fa-solid fa-caret-down"></span>' +
            "</button></div> </div>"
          );
        }
      } else {
        return (
          '<div class="combobox-container"> <input type="hidden" /> ' +
          '<input type="text" alt="' +
          this.options.inputBox +
          '" role="combobox" aria-autocomplete="list" aria-expanded="false" aria-activedescendant="" autocomplete="off" /></div>'
        );
      }
    },

    disable: function () {
      this.$element.prop("disabled", true);
      this.$button.attr("disabled", true);
      this.$target.prop("disabled", true);
      this.$source.prop("disabled", true);
      this.disabled = true;
      this.$container.addClass("combobox-disabled");
    },

    enable: function () {
      this.$element.prop("disabled", false);
      this.$button.attr("disabled", false);
      this.$target.prop("disabled", false);
      this.$source.prop("disabled", false);
      this.disabled = false;
      this.$container.removeClass("combobox-disabled");
    },
    parse: function () {
      //console.log('parse');
      var that = this,
        map = {},
        revMap = {},
        source = [],
        selected = false,
        selectedValue = "";
      this.$source.find("option").each(function () {
        var option = $(this);
        if (option.val() === "") {
          that.options.placeholder = option.text();
          return;
        }
        map[option.text()] = option.val();
        revMap[option.val()] = option.text();
        source.push(option.text());
        if (option.prop("selected")) {
          selected = option.text();
          selectedValue = option.val();
        }
      });
      this.map = map;
      this.revMap = revMap;
      if (selected) {
        var triggerElement = false;
        var triggerTarget = false;
        var oldVal;
        oldVal = this.$element.val();
        if (oldVal !== selected) {
          this.$element.val(selected);
          triggerElement = true;
        }
        oldVal = this.$target.val();
        if (oldVal !== selectedValue) {
          this.$target.val(selectedValue);
          triggerTarget = true;
        }
        this.$container.addClass("combobox-selected");
        this.selected = true;
        if (triggerTarget) {
          this.$target.trigger("change");
        }
        if (triggerElement) {
          this.$element.trigger("change");
        }
      } else {
        this.$container.removeClass("combobox-selected");
        this.selected = false;
      }
      return source;
    },

    transferAttributes: function () {
      //console.log('transferAttributes');
      this.options.placeholder =
        this.$source.attr("data-placeholder") || this.options.placeholder;
      if (this.options.appendId !== "undefined") {
        // keep the source id on the input, otherwise the label (which refers to it by id) will be lost
        this.$element.attr("id", this.$source.attr("id"));
        this.$source.attr(
          "id",
          this.$source.attr("id") + this.options.appendId,
        );
        daComboBoxes[this.$element.attr("id")] = this;
      }
      this.$menu.attr("id", this.$element.attr("id") + "menu");
      // Set aria-controls now that things have ids
      this.$element.attr("aria-controls", this.$menu.attr("id"));
      this.$element.attr("aria-owns", this.$menu.attr("id"));
      this.$button.attr("aria-controls", this.$menu.attr("id"));
      this.$button.attr("aria-label", this.$source.attr("aria-label"));
      if (this.$source.attr("aria-labelledby")) {
        this.$element.attr(
          "aria-labelledby",
          this.$source.attr("aria-labelledby"),
        );
      } else {
        this.$source.attr("aria-labelledby", "daMainQuestion");
      }
      this.$button.attr(
        "aria-labelledby",
        this.$source.attr("aria-labelledby"),
      );
      this.$button.attr(
        "aria-describedby",
        this.$source.attr("aria-describedby"),
      );
      this.$element.attr("placeholder", this.options.placeholder);
      this.$target.prop("name", this.$source.prop("name"));
      this.$target.val(this.$source.val());
      this.$source.removeAttr("name"); // Remove from source otherwise form will pass parameter twice.
      this.$element.attr("required", this.$source.attr("required"));
      this.$element.attr("rel", this.$source.attr("rel"));
      this.$element.attr("title", this.$source.attr("title"));
      this.$element.attr("class", this.$source.attr("class"));
      if (this.$element.hasClass("daspaceafter")) {
        this.$element.removeClass("daspaceafter");
        this.$container.addClass("daspaceafter");
      }
      this.$element.attr("tabindex", this.$source.attr("tabindex"));
      this.$source.removeAttr("tabindex");
      if (!this.$target.val() && this.$source.data("default")) {
        var defaultVal = this.$source.data("default");
        this.$element.val(defaultVal);
        this.$target.val(defaultVal);
      }
      this.$element.addClass("danovalidation");
      this.$source.addClass("danovalidation");
      if (this.$source.attr("disabled") !== undefined) this.disable();
    },

    select: function () {
      //console.log("select");
      var val = this.$menu.find(".active").attr("data-value");
      var oldVal;
      var triggerElement = false;
      var triggerTarget = false;
      var triggerSource = false;
      this.$container.parent().find(".da-has-error").remove();
      oldVal = this.$element.val();
      var newVal = this.updater(val);
      if (oldVal !== newVal) {
        this.$element.val(newVal);
        triggerElement = true;
      }
      oldVal = this.$target.val();
      if (oldVal !== this.map[val]) {
        this.$target.val(this.map[val]); //.trigger("change");
        triggerTarget = true;
      }
      oldVal = this.$source.val();
      if (oldVal !== this.map[val]) {
        this.$source.val(this.map[val]);
        triggerSource = true;
      }
      this.$container.addClass("combobox-selected");
      this.selected = true;
      this.hide();
      if (triggerTarget) {
        this.$target.trigger("change");
      }
      if (triggerElement) {
        this.$element.trigger("change");
      }
      if (triggerSource) {
        this.$source.trigger("change");
      }
      return;
    },

    manualSelect: function (val) {
      //console.log("manualSelect");
      var oldVal;
      var found = false;
      var triggerSource = false;
      var triggerTarget = false;
      this.$container.parent().find(".da-has-error").remove();
      if (val !== "" && this.revMap[val] !== undefined) {
        this.$element.val(this.revMap[val]);
        found = true;
      } else {
        this.$element.val(val);
      }
      oldVal = this.$target.val();
      if (oldVal !== val) {
        this.$target.val(val);
        triggerTarget = true;
      }
      oldVal = this.$source.val();
      if (oldVal !== val) {
        this.$source.val(val);
        triggerSource = true;
      }
      if (val !== "" && found) {
        this.$container.addClass("combobox-selected");
        this.selected = true;
      }
      if (triggerTarget) {
        this.$target.trigger("change");
      }
      this.$element.trigger("change");
      if (triggerSource) {
        this.$source.trigger("change");
      }
      return;
    },

    updater: function (item) {
      //console.log('updater');
      return item;
    },

    show: function () {
      //console.log("show");
      var pos = $.extend({}, this.$element.position(), {
        height: this.$element[0].offsetHeight,
      });
      this.$menu
        .insertAfter(this.$element)
        .css({
          top: pos.top + pos.height,
          left: pos.left,
        })
        .show();

      this.hidden = false;

      this.$element.attr("aria-expanded", true);
      this.$button.attr("aria-expanded", true);

      this.shown = true;
      return this;
    },

    hide: function () {
      //console.log('hide');
      this.$menu.hide();
      this.hidden = true;
      this.$element.on("blur", $.proxy(this.blur, this));
      this.$element.attr("aria-expanded", false);
      this.$button.attr("aria-expanded", false);
      this.shown = false;
      return this;
    },

    lookup: function (event) {
      //console.log("lookup");
      this.query = this.$element.val();
      this.process(this.source);
    },

    process: function (items) {
      var that = this;

      items = $.grep(items, function (item) {
        return that.matcher(item);
      });

      items = this.sorter(items);

      if (!items.length) {
        return this.shown ? this.hide() : this;
      }

      return this.render(items.slice(0, this.options.items)).show();
    },

    matcher: function (item) {
      //console.log('matcher');
      return ~item.toLowerCase().indexOf(this.query.toLowerCase());
    },

    sorter: function (items) {
      //console.log('sorter');
      var beginswith = [],
        caseSensitive = [],
        caseInsensitive = [],
        item;

      while ((item = items.shift())) {
        if (!item.toLowerCase().indexOf(this.query.toLowerCase())) {
          beginswith.push(item);
        } else if (~item.indexOf(this.query)) {
          caseSensitive.push(item);
        } else {
          caseInsensitive.push(item);
        }
      }

      return beginswith.concat(caseSensitive, caseInsensitive);
    },

    highlighter: function (item) {
      //console.log('highlighter');
      var query = this.query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, "\\$&");
      if (!query) {
        return item;
      }
      return item.replace(
        new RegExp("(" + query + ")", "ig"),
        function ($1, match) {
          return "<b>" + match + "</b>";
        },
      );
    },

    render: function (items) {
      //console.log('render');
      var that = this;

      items = $(items).map(function (i, item) {
        i = $(that.options.item)
          .attr("data-value", item)
          .attr("aria-label", item);
        i.attr("id", that.$element.attr("id") + "-option-" + item);
        i.html(that.highlighter(item));
        return i[0];
      });

      this.setActive(items.first());
      this.$menu.html(items);
      return this;
    },

    setActive: function (elem) {
      elem.addClass("active").attr("aria-selected", true);
      this.$element.attr("aria-activedescendant", elem.attr("id"));
    },

    swapActive: function (oldElem, newElem) {
      oldElem.removeClass("active").attr("aria-selected", false);
      this.setActive(newElem);
    },

    next: function (event) {
      //console.log('next');
      var active = this.$menu.find('[aria-selected="true"]');
      var next = active.next();

      if (!next.length) {
        next = $(this.$menu.find("li")[0]);
      }

      this.swapActive(active, next);
    },

    prev: function (event) {
      //console.log('prev');
      var active = this.$menu.find('[aria-selected="true"]');
      var prev = active.prev();

      if (!prev.length) {
        prev = this.$menu.find("li").last();
      }

      this.swapActive(active, prev);
    },

    toggle: function (e) {
      //console.log("toggle");
      if (!this.disabled) {
        if (this.$container.hasClass("combobox-selected")) {
          this.clearAll();
          this.$element.attr("aria-expanded", false);
          this.$button.attr("aria-expanded", false);
        } else {
          if (this.shown) {
            this.$element.attr("aria-expanded", false);
            this.$button.attr("aria-expanded", false);
            this.hide();
          } else {
            this.$element.attr("aria-expanded", true);
            this.$button.attr("aria-expanded", true);
            this.clearElement();
            this.lookup();
          }
        }
      }
      if (e) {
        e.preventDefault();
        e.stopPropagation();
      }
      return false;
    },

    clearAll: function () {
      //console.log('clearAll');
      var triggerElement = false;
      var triggerSource = false;
      var triggerTarget = false;
      var oldVal;
      oldVal = this.$element.val();
      if (oldVal !== "") {
        this.$element.val("");
        triggerElement = true;
      }
      oldVal = this.$source.val();
      if (oldVal !== "") {
        this.$source.val("");
        triggerSource = true;
      }
      oldVal = this.$target.val();
      if (oldVal !== "") {
        this.$target.val("");
        triggerTarget = true;
      }
      this.$container.removeClass("combobox-selected");
      if (triggerTarget) {
        this.$target.trigger("change");
      }
      if (triggerElement) {
        this.$element.trigger("change");
      }
      if (triggerSource) {
        this.$source.trigger("change");
      }
    },

    clearElement: function () {
      //console.log('clearElement');
      this.$element.val("").focus();
    },

    clearTarget: function () {
      //console.log('clearTarget');
      this.$source.val("");
      this.$target.val("");
      this.$container.removeClass("combobox-selected");
      this.selected = false;
    },

    refresh: function () {
      //console.log('refresh');
      this.source = this.parse();
      this.options.items = this.source.length;
    },

    listen: function () {
      //console.log('listen');
      this.$element
        .on("focus", $.proxy(this.focus, this))
        .on("change", $.proxy(this.change, this))
        .on("blur", $.proxy(this.blur, this))
        .on("keypress", $.proxy(this.keypress, this))
        .on("keyup", $.proxy(this.keyup, this));

      if (this.eventSupported("keydown")) {
        this.$element.on("keydown", $.proxy(this.keydown, this));
      }

      this.$menu
        .on("click", $.proxy(this.click, this))
        .on("mouseenter", "li", $.proxy(this.mouseenter, this))
        .on("mouseleave", "li", $.proxy(this.mouseleave, this))
        .on("mousedown", "li", $.proxy(this.mousedown, this));

      if (this.options.showButton && this.options.functionalButton) {
        this.$button.on("click touchend", $.proxy(this.toggle, this));
      }
    },

    eventSupported: function (eventName) {
      //console.log('eventSupported');
      var isSupported = eventName in this.$element;
      if (!isSupported) {
        this.$element.setAttribute(eventName, "return;");
        isSupported = typeof this.$element[eventName] === "function";
      }
      return isSupported;
    },

    move: function (e) {
      //console.log("move");
      if (!this.shown) {
        return;
      }

      switch (e.keyCode) {
        case 9: // tab
        case 13: // enter
        case 27: // escape
          e.preventDefault();
          break;

        case 38: // up arrow
          e.preventDefault();
          this.prev();
          this.fixMenuScroll();
          break;

        case 40: // down arrow
          e.preventDefault();
          this.next();
          this.fixMenuScroll();
          break;
      }
      e.stopPropagation();
    },

    fixMenuScroll: function () {
      //console.log('fixMenuScroll');
      var active = this.$menu.find(".active");
      if (active.length) {
        this.$element.attr("aria-activedescendant", active.attr("id"));
        var top = active.position().top;
        var bottom = top + active.height();
        var scrollTop = this.$menu.scrollTop();
        var menuHeight = this.$menu.height();
        if (bottom > menuHeight) {
          this.$menu.scrollTop(scrollTop + bottom - menuHeight);
        } else if (top < 0) {
          this.$menu.scrollTop(scrollTop + top);
        }
      }
    },

    setActiveDescendant: function (e) {
      if (this.mousedover) {
        this.swapActive(this.$menu.find(".active"), $(e.currentTarget));
      }
    },

    keydown: function (e) {
      //console.log('keyDown');
      this.suppressKeyPressRepeat = ~$.inArray(e.keyCode, [40, 38, 9, 13, 27]);
      this.move(e);
    },

    keypress: function (e) {
      //console.log('keyPress');
      if (this.suppressKeyPressRepeat) {
        return;
      }
      this.move(e);
    },

    keyup: function (e) {
      //console.log("keyUp");
      switch (e.keyCode) {
        case 40: // down arrow
          if (!this.shown) {
            this.toggle();
          }
          break;
        case 39: // right arrow
        case 38: // up arrow
        case 37: // left arrow
        case 36: // home
        case 35: // end
        case 16: // shift
        case 17: // ctrl
        case 18: // alt
          break;

        case 9: // tab
        case 13: // enter
          if (e) {
            e.stopPropagation();
            e.preventDefault();
          }
          daFetchAjaxTimeoutFetchAfter = false;
          daFetchAcceptIncoming = false;
          if (!this.shown) {
            return;
          }
          if (!this.selected) {
            this.select();
          } else {
            var val = this.$element.val();
            var opts = this.$menu.find("li");
            var n = opts.length;
            for (var i = 0; i < n; ++i) {
              if ($(opts[i]).attr("data-value") == val) {
                e.stopPropagation();
                e.preventDefault();
                $(opts[i]).click();
                return false;
              }
            }
          }
          break;

        case 27: // escape
          if (e) {
            e.stopPropagation();
            e.preventDefault();
          }
          daFetchAjaxTimeoutFetchAfter = false;
          daFetchAcceptIncoming = false;
          if (!this.shown) {
            return;
          }
          this.hide();
          break;

        default:
          if (this.options.lookupWhileTyping) {
            this.clearTarget();
            this.$target.val(this.$element.val());
            this.lookup();
          } else {
            this.query = this.$element.val();
          }
      }

      e.stopPropagation();
      e.preventDefault();
    },

    focus: function (e) {
      //console.log('focus');
      this.focused = true;
    },

    blur: function (e) {
      //console.log('blur');
      var that = this;
      this.focused = false;
      var val = this.$element.val();
      if (this.shown) {
        var opts = this.$menu.find("li");
        var n = opts.length;
        for (var i = 0; i < n; ++i) {
          if ($(opts[i]).attr("data-value") == val) {
            $(opts[i]).click();
            return;
          }
        }
      }
      var oldVal;
      var triggerElement = false;
      var triggerSource = false;
      var triggerTarget = false;
      if (this.clearIfNoMatch && !this.selected && val !== "") {
        oldVal = this.$element.val();
        if (oldVal !== "") {
          this.$element.val("");
          triggerElement = true;
        }
        oldVal = this.$source.val();
        if (oldVal !== "") {
          this.$source.val("");
          triggerSource = true;
        }
        oldVal = this.$target.val();
        if (oldVal !== "") {
          this.$target.val(""); //.trigger("change");
          triggerTarget = true;
        }
      }
      if (!this.selected) {
        oldVal = this.$target.val();
        if (oldVal !== val) {
          this.$target.val(val); //.trigger("change");
          triggerTarget = true;
        }
      }
      if (triggerTarget) {
        this.$target.trigger("change");
      }
      if (triggerElement) {
        this.$element.trigger("change");
      }
      if (triggerSource) {
        this.$source.trigger("change");
      }
      if (!this.mousedover && this.shown) {
        setTimeout(function () {
          that.hide();
        }, 200);
      }
    },

    click: function (e) {
      //console.log("click");
      if (e) {
        e.stopPropagation();
        e.preventDefault();
      }
      daFetchAjaxTimeoutFetchAfter = false;
      daFetchAcceptIncoming = false;
      this.select();
      this.$element.focus();
    },

    mouseenter: function (e) {
      //console.log('mouseenter');
      this.mousedover = true;
      this.setActiveDescendant(e);
    },

    mousedown: function (e) {
      this.mousedover = true;
      this.setActiveDescendant(e);
      this.mousedover = false;
      if (!this.hidden) {
        if (e.target.tagName == "UL") {
          this.$element.off("blur");
        }
      }
    },

    mouseleave: function (e) {
      //console.log('mouseleave');
      this.mousedover = false;
      this.setActiveDescendant(e);
    },
  };

  /* COMBOBOX PLUGIN DEFINITION
   * =========================== */
  $.fn.combobox = function (option) {
    return this.each(function () {
      var $this = $(this),
        data = $this.data("combobox"),
        options = typeof option == "object" && option;
      if (!data) {
        $this.data("combobox", (data = new Combobox(this, options)));
      }
      if (typeof option == "string") {
        data[option]();
      }
    });
  };

  $.fn.combobox.defaults = {
    bsVersion: "5",
    menu: '<ul role="listbox" class="typeahead typeahead-long dropdown-menu"></ul>',
    item: '<li role="option" class="dropdown-item dapointer"></li>',
    appendId: "combobox",
    buttonLabel: "dropdown",
    clearIfNoMatch: false,
    showButton: true,
    functionalButton: true,
    inputBox: "Input box",
    lookupWhileTyping: true,
  };

  $.fn.combobox.Constructor = Combobox;
})(window.jQuery);
