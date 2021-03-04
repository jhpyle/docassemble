/* =============================================================
 * bootstrap-combobox.js v1.1.8
 * =============================================================
 * Copyright 2012 Daniel Farrell
 * Modified 2018 for docassemble by Jonathan Pyle
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
    this.$container = this.setup();
    this.$element = this.$container.find("input[type=text]");
    this.$target = this.$container.find("input[type=hidden]");
    if (this.$source.attr("disabled") !== undefined) {
      this.$target.prop("disabled", true);
    }
    this.$button = this.$container.find(".dacomboboxtoggle");
    this.$menu = $(this.options.menu).appendTo("body");
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
      return combobox;
    },

    disable: function () {
      //console.log('disable');
      this.$element.prop("disabled", true);
      this.$button.attr("disabled", true);
      this.disabled = true;
      this.$container.addClass("combobox-disabled");
    },

    enable: function () {
      //console.log('enable');
      this.$element.prop("disabled", false);
      this.$button.attr("disabled", false);
      this.disabled = false;
      this.$container.removeClass("combobox-disabled");
    },
    parse: function () {
      //console.log('parse');
      var that = this,
        map = {},
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
        source.push(option.text());
        if (option.prop("selected")) {
          selected = option.text();
          selectedValue = option.val();
        }
      });
      this.map = map;
      if (selected) {
        this.$element.val(selected);
        this.$target.val(selectedValue);
        this.$container.addClass("combobox-selected");
        this.selected = true;
      }
      return source;
    },

    transferAttributes: function () {
      //console.log('transferAttributes');
      this.options.placeholder =
        this.$source.attr("data-placeholder") || this.options.placeholder;
      if (this.options.appendId !== "undefined") {
        this.$element.attr(
          "id",
          this.$source.attr("id") + this.options.appendId
        );
        daComboBoxes[this.$element.attr("id")] = this;
      }
      this.$element.attr("placeholder", this.options.placeholder);
      this.$target.prop("name", this.$source.prop("name"));
      this.$target.val(this.$source.val());
      this.$source.removeAttr("name"); // Remove from source otherwise form will pass parameter twice.
      this.$element.attr("required", this.$source.attr("required"));
      this.$element.attr("rel", this.$source.attr("rel"));
      this.$element.attr("title", this.$source.attr("title"));
      this.$element.attr("class", this.$source.attr("class"));
      this.$element.attr("tabindex", this.$source.attr("tabindex"));
      this.$source.removeAttr("tabindex");
      if (!this.$target.val() && this.$source.data("default")) {
        var defaultVal = this.$source.data("default");
        this.$element.val(defaultVal);
        this.$target.val(defaultVal);
      }
      if (this.$source.attr("disabled") !== undefined) this.disable();
    },

    select: function () {
      //console.log("select");
      var val = this.$menu.find(".active").attr("data-value");
      var oldVal;
      this.$container.parent().find(".da-has-error").remove();
      this.$element.val(this.updater(val));
      oldVal = this.$target.val();
      if (oldVal != this.map[val]) {
        this.$target.val(this.map[val]); //.trigger("change");
      }
      oldVal = this.$source.val();
      if (oldVal != this.map[val]) {
        this.$source.val(this.map[val]).trigger("change");
      }
      this.$container.addClass("combobox-selected");
      this.selected = true;
      this.hide();
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

      $(".dropdown-menu").on("mousedown", $.proxy(this.scrollSafety, this));

      this.shown = true;
      return this;
    },

    hide: function () {
      //console.log('hide');
      this.$menu.hide();
      $(".dropdown-menu").off("mousedown", $.proxy(this.scrollSafety, this));
      this.$element.on("blur", $.proxy(this.blur, this));
      this.shown = false;
      return this;
    },

    lookup: function (event) {
      //console.log("lookup");
      this.query = this.$element.val();
      this.process(this.source);
    },

    process: function (items) {
      //console.log("process");
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

    template: function () {
      //console.log('template');
      if (this.options.bsVersion == "2") {
        return '<div class="combobox-container"><input type="hidden" /> <div class="input-append"> <input type="text" autocomplete="off" /> <span class="add-on dropdown-toggle" data-dropdown="dropdown"> <span class="caret"/> <i class="icon-remove"/> </span> </div> </div>';
      } else {
        return '<div class="combobox-container"> <input type="hidden" /> <div class="input-group"> <input type="text" autocomplete="off" /> <div class="input-group-append"> <button class="btn btn-outline-secondary dacomboboxtoggle" data-toggle="dropdown" type="button"><span class="fas fa-caret-down"></span><span class="fas fa-times"></span></button> </div> </div>';
      }
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
      return item.replace(new RegExp("(" + query + ")", "ig"), function (
        $1,
        match
      ) {
        return "<strong>" + match + "</strong>";
      });
    },

    render: function (items) {
      //console.log('render');
      var that = this;

      items = $(items).map(function (i, item) {
        i = $(that.options.item).attr("data-value", item);
        i.html(that.highlighter(item));
        return i[0];
      });

      items.first().addClass("active");
      this.$menu.html(items);
      return this;
    },

    next: function (event) {
      //console.log('next');
      var active = this.$menu.find(".active").removeClass("active"),
        next = active.next();

      if (!next.length) {
        next = $(this.$menu.find("a")[0]);
      }

      next.addClass("active");
    },

    prev: function (event) {
      //console.log('prev');
      var active = this.$menu.find(".active").removeClass("active"),
        prev = active.prev();

      if (!prev.length) {
        prev = this.$menu.find("a").last();
      }

      prev.addClass("active");
    },

    toggle: function (e) {
      //console.log("toggle");
      if (!this.disabled) {
        if (this.$container.hasClass("combobox-selected")) {
          this.clearTarget();
          this.triggerChange();
          this.clearElement();
        } else {
          if (this.shown) {
            this.hide();
          } else {
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

    scrollSafety: function (e) {
      //console.log("scrollsafety");
      if (e.target.tagName == "UL") {
        this.$element.off("blur");
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

    triggerChange: function () {
      //console.log('triggerChange');
      this.$source.trigger("change");
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
        .on("mouseenter", "a", $.proxy(this.mouseenter, this))
        .on("mouseleave", "a", $.proxy(this.mouseleave, this));

      this.$button.on("click", $.proxy(this.toggle, this));
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
          if (!this.shown) {
            return;
          }
          this.select();
          break;

        case 27: // escape
          if (!this.shown) {
            return;
          }
          this.hide();
          break;

        default:
          this.clearTarget();
          this.$target.val(this.$element.val());
          this.lookup();
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
      var oldVal;
      if (this.clearIfNoMatch && !this.selected && val !== "") {
        this.$element.val("");
        oldVal = this.$source.val();
        if (oldVal != "") {
          this.$source.val("").trigger("change");
        }
        oldVal = this.$target.val();
        if (oldVal != "") {
          this.$target.val(""); //.trigger("change");
        }
      }
      if (!this.selected) {
        oldVal = this.$target.val();
        if (oldVal != val) {
          this.$target.val(val); //.trigger("change");
        }
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
      this.$menu.find(".active").removeClass("active");
      $(e.currentTarget).addClass("active");
    },

    mouseleave: function (e) {
      //console.log('mouseleave');
      this.mousedover = false;
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
    bsVersion: "4",
    menu: '<div class="typeahead typeahead-long dropdown-menu"></div>',
    item: '<a href="#" class="dropdown-item"></a>',
    appendId: "combobox",
    clearIfNoMatch: false,
  };

  $.fn.combobox.Constructor = Combobox;
})(window.jQuery);
