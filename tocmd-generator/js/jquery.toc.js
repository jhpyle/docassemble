/*
 * jQuery Table of Content Generator for Markdown v1.0
 *
 * https://github.com/dafi/tocmd-generator
 * Examples and documentation at: https://github.com/dafi/tocmd-generator
 *
 * Requires: jQuery v1.7+
 *
 * Copyright (c) 2013 Davide Ficano
 *
 * Dual licensed under the MIT and GPL licenses:
 *   http://www.opensource.org/licenses/mit-license.php
 *   http://www.gnu.org/licenses/gpl.html
 */
(function($) {
    var toggleHTML = '<div id="toctitle"><h2>Contents</h2> <span class="toctoggle">[<a id="toctogglelink" class="internal" href="#">hide</a>]</span></div>';
    var tocContainerHTML = '<div id="toc-container"><table class="toc" id="toc"><tbody><tr><td>%1<ul>%2</ul></td></tr></tbody></table></div>';

    function createLevelHTML(anchorId, tocLevel, tocSection, tocNumber, tocText, tocInner) {
        var link = '<a href="#%1"><span class="tocnumber">%2</span> <span class="toctext">%3</span></a>%4'
            .replace('%1', anchorId)
            .replace('%2', tocNumber)
            .replace('%3', tocText)
            .replace('%4', tocInner ? tocInner : '');
        return '<li class="toclevel-%1 tocsection-%2">%3</li>\n'
            .replace('%1', tocLevel)
            .replace('%2', tocSection)
            .replace('%3', link);
    }

    $.fn.toc = function(settings) {
        var config = {
            anchorPrefix: 'tocAnchor-',
            showAlways: false,
            saveShowStatus: true,
            contentsText: 'Contents',
            hideText: 'hide',
            showText: 'show'};

        if (settings) {
            $.extend(config, settings);
        }

        var tocHTML = '';
        var tocLevel = 1;
        var tocSection = 1;
        var itemNumber = 1;

        var tocContainer = $(this);

        tocContainer.find('h1').each(function() {
            var levelHTML = '';
            var innerSection = 0;
            var h1 = $(this);

            h1.nextUntil('h1').filter('h2').each(function() {
                ++innerSection;
                var anchorId = config.anchorPrefix + tocLevel + '-' + tocSection + '-' +  + innerSection;
                $(this).attr('id', anchorId);
                levelHTML += createLevelHTML(anchorId,
                    tocLevel + 1,
                    tocSection + innerSection,
                    itemNumber + '.' + innerSection,
                    $(this).text());
            });
            if (levelHTML) {
                levelHTML = '<ul>' + levelHTML + '</ul>\n';
            }
            var anchorId = config.anchorPrefix + tocLevel + '-' + tocSection;
            h1.attr('id', anchorId);
            tocHTML += createLevelHTML(anchorId,
                tocLevel,
                tocSection,
                itemNumber,
                h1.text(),
                levelHTML);

            tocSection += 1 + innerSection;
            ++itemNumber;
        });

        var hasOnlyOneTocItem = tocLevel == 1 && tocSection <= 2;
        var show = config.showAlways ? true : !hasOnlyOneTocItem;

        // check if cookie plugin is present otherwise doesn't try to save
        if (config.saveShowStatus && typeof($.cookie) == "undefined") {
            config.saveShowStatus = false;
        }

        if (show && tocHTML) {
            var replacedToggleHTML = toggleHTML
                .replace('%1', config.contentsText)
                .replace('%2', config.hideText);
            var replacedTocContainer = tocContainerHTML
                .replace('%1', replacedToggleHTML)
                .replace('%2', tocHTML);
            tocContainer.prepend(replacedTocContainer);

            $('#toctogglelink').click(function() {
                var ul = $($('#toc ul')[0]);
                
                if (ul.is(':visible')) {
                    ul.hide();
                    $(this).text(config.showText);
                    if (config.saveShowStatus) {
                        $.cookie('toc-hide', '1', { expires: 365, path: '/' });
                    }
                    $('#toc').addClass('tochidden');
                } else {
                    ul.show();
                    $(this).text(config.hideText);
                    if (config.saveShowStatus) {
                        $.removeCookie('toc-hide', { path: '/' });
                    }
                    $('#toc').removeClass('tochidden');
                }
                return false;
            });

            if (config.saveShowStatus && $.cookie('toc-hide')) {
                var ul = $($('#toc ul')[0]);
                
                ul.hide();
                $('#toctogglelink').text(config.showText);
                $('#toc').addClass('tochidden');
            }
        }
        return this;
    }
})(jQuery);
