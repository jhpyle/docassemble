'use strict';

// Karma adds 'base/' to the default path
jasmine.getFixtures().fixturesPath = 'base/spec/javascripts/fixtures';

describe("A form's", function() {
  var $form = undefined;

  describe('text input', function() {
    var $textInput = undefined;

    beforeEach(function() {
      loadFixtures('input-text.html');
      $form = $('form');
      $textInput = $('input[type=text]');
      $form.areYouSure();
    });

    it('should cause dirtyness after its value changes', function(done) {
      expect($form.hasClass('dirty')).toBe(false);
      $textInput.val('new').change();
      setTimeout(function() {
        expect($form.hasClass('dirty')).toBe(true);
        done();
      }, 0);
    });
  });
});
