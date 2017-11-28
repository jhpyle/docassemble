Feature: Example interviews
  In order to ensure docassemble is running properly, I want
  to run the example interviews.

  Scenario: Test the interview "Action with arguments"
    Given I start the interview "docassemble.base:data/questions/examples/actions-parameters.yml"
    And I click the link "Add blue fish"
    When I wait 1 second
    Then I should see the phrase "You have 3 blue fishes"
    And I click the button "Continue"
    Then I should see the phrase "You have 3 blue fishes"

  Scenario: Test the interview "Action"
    Given I start the interview "docassemble.base:data/questions/examples/actions.yml"
    And I click the link "Change this"
    Then I should see that "Favorite Color" is "blue"
    And I set "Favorite Color" to "red"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite color is red"

  Scenario: Test the interview "Age of Individual"
    Given I start the interview "docassemble.base:data/questions/examples/age_in_years.yml"
    And I set the text box to "3/31/1977"
    And I click the button "Continue"
    Then I should see the phrase "You are 40 years old"

  Scenario: Test the interview "Scheduled task"
    Given I start the interview "docassemble.base:data/questions/examples/alarm-clock.yml"

  Scenario: Test the interview "Text alignment"
    Given I start the interview "docassemble.base:data/questions/examples/alignment.yml"

  Scenario: Test the interview "Checkbox method"
    Given I start the interview "docassemble.base:data/questions/examples/all-false.yml"
    And I click the "Apples" option under "Select the fruits you like"
    And I click the "Plums" option under "Select the fruits you like"
    And I click the button "Continue"
    Then I should see the phrase "It is not true that you don’t like any of the fruit."
    And I should see the phrase "It is not true that you do not like apples or pears."
    And I should see the phrase "It is not true that apples and pears are the only fruits you do not like."

  Scenario: Test the interview "Interview"
    Given I start the interview "docassemble.base:data/questions/examples/all-mandatory.yml"
    And I click the "Fine" option
    And I click the button "Continue"
    And I set "Color" to "red"
    When I click the button "Continue"
    Then I should see the phrase "I am glad you are doing well"
    And I should see the phrase "Your favorite color is red"

  Scenario: Test the interview "Disallowing e-mailing"
    Given I start the interview "docassemble.base:data/questions/examples/allow-emailing-false-pdf.yml"
    Then I should not see the phrase "E-mail this document"

  Scenario: Test the interview "Disallowing e-mailing"
    Given I start the interview "docassemble.base:data/questions/examples/allow-emailing-false.yml"
    Then I should not see the phrase "E-mail this document"

  Scenario: Test the interview "Allowing documents to be e-mailed"
    Given I start the interview "docassemble.base:data/questions/examples/allow-emailing-true.yml"
    Then I should see the phrase "E-mail this document"

  Scenario: Test the interview "Checkbox method"
    Given I start the interview "docassemble.base:data/questions/examples/all-true.yml"
    And I click the "Apples" option under "Select the fruits you like"
    And I click the "Plums" option under "Select the fruits you like"
    And I click the button "Continue"
    Then I should see the phrase "It is not true that you like all fruit."
    And I should see the phrase "It is not true that you like apples and pears."
    And I should see the phrase "It is not true that apples and pears are the only fruits you like."

  Scenario: Test the interview "Variables as dictionary"
    Given I start the interview "docassemble.base:data/questions/examples/all_variables.yml"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    And I set "Slices" to "4"
    And I click the button "Continue"
    Then I should see the phrase "'favorite_fruit': u'apple'"
    And I should see the phrase "'number_of_slices': 4"
    
  Scenario: Test the interview "Animals and vegetables"
    Given I start the interview "docassemble.base:data/questions/examples/animal.yml"
    And I set "Animal" to "pig"
    When I click the button "Continue"
    Then I should see the phrase "My favorite animal is the pig, too"
    When I exit by clicking "Exit"
    Then I should see "Docassemble" as the title of the page
    And I should see "https://docassemble.org/" as the URL of the page
    
  Scenario: Test the interview "Convert to datetime"
    Given I start the interview "docassemble.base:data/questions/examples/as-datetime.yml"
    Then I should see the phrase "The Delorean will go back in time to 1955"

  Scenario: Test the interview "Assets"
    Given I start the interview "docassemble.base:data/questions/examples/assets.yml"
    And I set "First Name" to "John"
    And I set "Last Name" to "Smith"
    When I click the button "Continue"
    Then I should see the phrase "Does the estate of John Smith have any assets?"
    When I click the button "Yes"
    And I set "Type of asset" to "fish"
    And I click the button "Continue"
    And I set "Value" to "400"
    And I click the button "Continue"
    And I click the button "Yes"
    And I set "Type of asset" to "vegetables"
    And I click the button "Continue"
    And I set "Value" to "10"
    And I click the button "Continue"
    When I click the button "No"
    Then I should see the phrase "The total value of John Smith’s estate is $410.00."

  Scenario: Test the interview "Computed attachment list"
    Given I start the interview "docassemble.base:data/questions/examples/attachment-code.yml"
    Then I should see the phrase "The first document"
    And I should see the phrase "The second document"
    And I should see the phrase "The third document"

  Scenario: Test the interview "Attachment"
    Given I start the interview "docassemble.base:data/questions/examples/attachment-simple.yml"
    Then I should see the phrase "A hello world document"
    And I should see the phrase "A document with a classic message"

  Scenario: Test the interview "Allowing documents to be e-mailed"
    Given I start the interview "docassemble.base:data/questions/examples/attachment.yml"
    Then I should see the phrase "A hello world document"
    And I should see the phrase "A document with a classic message"
    And I should see the phrase "E-mail address"

  # Scenario: Test the interview "Inheritance"
  #   Given I start the interview "docassemble.base:data/questions/examples/attorney.yml"

  # Scenario: Test the interview "Audio upload"
  #   Given I start the interview "docassemble.base:data/questions/examples/audio-upload.yml"

  # Scenario: Test the interview "Audio"
  #   Given I start the interview "docassemble.base:data/questions/examples/audio.yml"

  # Scenario: Test the interview "Global terms"
  #   Given I start the interview "docassemble.base:data/questions/examples/auto-terms.yml"

  # Scenario: Test the interview "Return a value and show a message"
  #   Given I start the interview "docassemble.base:data/questions/examples/background_action_flash.yml"

  # Scenario: Test the interview "Return a value and run Javascript"
  #   Given I start the interview "docassemble.base:data/questions/examples/background_action_javascript.yml"

  # Scenario: Test the interview "Set a variable and refresh the screen"
  #   Given I start the interview "docassemble.base:data/questions/examples/background_action_refresh.yml"

  # Scenario: Test the interview "Set a variable"
  #   Given I start the interview "docassemble.base:data/questions/examples/background_action_with_response_action.yml"

  # Scenario: Test the interview "Return a value"
  #   Given I start the interview "docassemble.base:data/questions/examples/background_action.yml"

  # Scenario: Test the interview "Set a variable and show a message"
  #   Given I start the interview "docassemble.base:data/questions/examples/background_response_action_flash.yml"

  # Scenario: Test the interview "Blank label"
  #   Given I start the interview "docassemble.base:data/questions/examples/blank-label-field.yml"

  # Scenario: Test the interview "Object"
  #   Given I start the interview "docassemble.base:data/questions/examples/branch-no-error.yml"

  # Scenario: Test the interview "Buttons that run code"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-code-color.yml"

  # Scenario: Test the interview "Buttons defined with list"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list-equivalent.yml"

  # Scenario: Test the interview "Buttons defined with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list-partial.yml"

  # Scenario: Test the interview "Buttons defined with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list.yml"

  # Scenario: Test the interview "Buttons that run code"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-code.yml"

  # Scenario: Test the interview "Buttons with icons from code"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-icons-code-upload.yml"

  # Scenario: Test the interview "Buttons with icons from code"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-icons-code.yml"

  # Scenario: Test the interview "Buttons with icons"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-icons.yml"

  # Scenario: Test the interview "Labels ≠ values"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-labels.yml"

  # Scenario: Test the interview "Buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-variation-1.yml"

  # Scenario: Test the interview "Buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-variation-2.yml"

  # Scenario: Test the interview "Buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons.yml"

  # Scenario: Test the interview "Capitalize"
  #   Given I start the interview "docassemble.base:data/questions/examples/capitalize.yml"

  # Scenario: Test the interview "Complaint for Child Support"
  #   Given I start the interview "docassemble.base:data/questions/examples/chat-example-1.yml"

  # Scenario: Test the interview "Petition To Modify Support Order"
  #   Given I start the interview "docassemble.base:data/questions/examples/chat-example-2.yml"

  # Scenario: Test the interview "Live chat partners"
  #   Given I start the interview "docassemble.base:data/questions/examples/chat-partners-available.yml"

  # Scenario: Test the interview "Live chat"
  #   Given I start the interview "docassemble.base:data/questions/examples/chat.yml"

  # Scenario: Test the interview "Checking in"
  #   Given I start the interview "docassemble.base:data/questions/examples/check-in.yml"

  # Scenario: Test the interview "Combobox"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices-combobox.yml"

  # Scenario: Test the interview "Dropdown"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices-dropdown.yml"

  # Scenario: Test the interview "Radio buttons from code"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices-from-code.yml"

  # Scenario: Test the interview "Choices with icons"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices-icons.yml"

  # Scenario: Test the interview "Radio buttons with default"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices-with-default-item.yml"

  # Scenario: Test the interview "Radio buttons with default"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices-with-default.yml"

  # Scenario: Test the interview "Radio buttons with help"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices-with-help.yml"

  # Scenario: Test the interview "Radio buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/choices.yml"

  # Scenario: Test the interview "Classifier"
  #   Given I start the interview "docassemble.base:data/questions/examples/classify.yml"

  # Scenario: Test the interview "Two plus two"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-01.yml"

  # Scenario: Test the interview "Two plus three"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-02.yml"

  # Scenario: Test the interview "Two plus three"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-03.yml"

  # Scenario: Test the interview "Two plus two in template"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-04.yml"

  # Scenario: Test the interview "Arithmetic"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-05.yml"

  # Scenario: Test the interview "Arithmetic without spaces"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-06.yml"

  # Scenario: Test the interview "If/then/else"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-07.yml"

  # Scenario: Test the interview "If/then/else in code"
  #   Given I start the interview "docassemble.base:data/questions/examples/code-example-08.yml"

  # Scenario: Test the interview "Code"
  #   Given I start the interview "docassemble.base:data/questions/examples/code.yml"

  # Scenario: Test the interview "Combobox"
  #   Given I start the interview "docassemble.base:data/questions/examples/combobox.yml"

  # Scenario: Test the interview "Comments"
  #   Given I start the interview "docassemble.base:data/questions/examples/comment-weather.yml"

  # Scenario: Test the interview "Comments"
  #   Given I start the interview "docassemble.base:data/questions/examples/comment.yml"

  # Scenario: Test the interview "Custom continue button"
  #   Given I start the interview "docassemble.base:data/questions/examples/continue-button-label.yml"

  # Scenario: Test the interview "Continue button"
  #   Given I start the interview "docassemble.base:data/questions/examples/continue-participation.yml"

  # Scenario: Test the interview "Series of Continue screens"
  #   Given I start the interview "docassemble.base:data/questions/examples/continue-serial.yml"

  # Scenario: Test the interview "Continue option"
  #   Given I start the interview "docassemble.base:data/questions/examples/continue-special.yml"

  # Scenario: Test the interview "Continue button"
  #   Given I start the interview "docassemble.base:data/questions/examples/continue.yml"

  # Scenario: Test the interview "Country selection"
  #   Given I start the interview "docassemble.base:data/questions/examples/country.yml"

  # Scenario: Test the interview "Scheduled task"
  #   Given I start the interview "docassemble.base:data/questions/examples/cron.yml"

  # Scenario: Test the interview "CSS"
  #   Given I start the interview "docassemble.base:data/questions/examples/css.yml"

  # Scenario: Test the interview "Currency"
  #   Given I start the interview "docassemble.base:data/questions/examples/currency.yml"

  # Scenario: Test the interview "Current date and time"
  #   Given I start the interview "docassemble.base:data/questions/examples/current-datetime.yml"

  # Scenario: Test the interview ""Dictionary: prepopuated objects""
  #   Given I start the interview "docassemble.base:data/questions/examples/dadict.yml"

  # Scenario: Test the interview "URL of a file"
  #   Given I start the interview "docassemble.base:data/questions/examples/dafile-url-for.yml"

  # Scenario: Test the interview "Create file with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/dafile.yml"

  # Scenario: Test the interview "Basic lists"
  #   Given I start the interview "docassemble.base:data/questions/examples/dalist2.yml"

  # Scenario: Test the interview "List of objects"
  #   Given I start the interview "docassemble.base:data/questions/examples/dalist.yml"

  # Scenario: Test the interview "DAObject"
  #   Given I start the interview "docassemble.base:data/questions/examples/daobject.yml"

  # Scenario: Test the interview "Database storage"
  #   Given I start the interview "docassemble.base:data/questions/examples/database_storage.yml"

  # Scenario: Test the interview "Difference between dates"
  #   Given I start the interview "docassemble.base:data/questions/examples/date-difference.yml"

  # Scenario: Test the interview "Date"
  #   Given I start the interview "docassemble.base:data/questions/examples/date-field.yml"

  # Scenario: Test the interview "Adding to a date"
  #   Given I start the interview "docassemble.base:data/questions/examples/date-interval.yml"

  # Scenario: Test the interview "Date parts"
  #   Given I start the interview "docassemble.base:data/questions/examples/date-parts.yml"

  # Scenario: Test the interview "Dead end question"
  #   Given I start the interview "docassemble.base:data/questions/examples/dead-end.yml"

  # Scenario: Test the interview "Icon in corner"
  #   Given I start the interview "docassemble.base:data/questions/examples/decoration.yml"

  # Scenario: Test the interview "Whether variable is defined"
  #   Given I start the interview "docassemble.base:data/questions/examples/defined.yml"

  # Scenario: Test the interview "Mako functions"
  #   Given I start the interview "docassemble.base:data/questions/examples/def.yml"

  # Scenario: Test the interview "Re-ask a question with del"
  #   Given I start the interview "docassemble.base:data/questions/examples/del.yml"

  # Scenario: Test the interview "User IP"
  #   Given I start the interview "docassemble.base:data/questions/examples/device-ip.yml"

  # Scenario: Test the interview "User device"
  #   Given I start the interview "docassemble.base:data/questions/examples/device.yml"

  # Scenario: Test the interview "Dialog box"
  #   Given I start the interview "docassemble.base:data/questions/examples/dialog-box.yml"

  # Scenario: Test the interview "Disable others"
  #   Given I start the interview "docassemble.base:data/questions/examples/disable-others.yml"

  # Scenario: Test the interview "Dispatch"
  #   Given I start the interview "docassemble.base:data/questions/examples/dispatch-count.yml"

  # Scenario: Test the interview "Dispatch"
  #   Given I start the interview "docassemble.base:data/questions/examples/dispatch-track.yml"

  # Scenario: Test the interview "Dispatch"
  #   Given I start the interview "docassemble.base:data/questions/examples/dispatch.yml"

  # Scenario: Test the interview "Reassembling a document"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-cache-invalidate.yml"

  # Scenario: Test the interview "Document caching"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-cache.yml"

  # Scenario: Test the interview "DOCX format"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-docx.yml"

  # Scenario: Test the interview ""From .md file""
  #   Given I start the interview "docassemble.base:data/questions/examples/document-file.yml"

  # Scenario: Test the interview "Language"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-language-docx.yml"

  # Scenario: Test the interview "Language"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-language.yml"

  # Scenario: Test the interview "Document links"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-links-limited.yml"

  # Scenario: Test the interview "Document links"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-links.yml"

  # Scenario: Test the interview "Document formatting"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-markup.yml"

  # Scenario: Test the interview "Documents as links"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-variable-name-link.yml"

  # Scenario: Test the interview "Document as variable"
  #   Given I start the interview "docassemble.base:data/questions/examples/document-variable-name.yml"

  # Scenario: Test the interview "Assembling a document"
  #   Given I start the interview "docassemble.base:data/questions/examples/document.yml"

  # Scenario: Test the interview "Fill fields in a DOCX template"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-jinja2-demo.yml"

  # Scenario: Test the interview "Fill fields in a DOCX template"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-recipe.yml"

  # Scenario: Test the interview "Automatically fill fields in a DOCX template"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-template-auto.yml"

  # Scenario: Test the interview "Fill fields in a DOCX template with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-template-code.yml"

  # Scenario: Test the interview "Field variables"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-template-field-variables.yml"

  # Scenario: Test the interview "Fill fields in DOCX templates"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-template-multiple.yml"

  # Scenario: Test the interview "Tables in a DOCX template"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-template-table.yml"

  # Scenario: Test the interview "Fill fields in a DOCX template"
  #   Given I start the interview "docassemble.base:data/questions/examples/docx-template.yml"

  # Scenario: Test the interview "Ending screens"
  #   Given I start the interview "docassemble.base:data/questions/examples/doors.yml"

  # Scenario: Test the interview "Edit list"
  #   Given I start the interview "docassemble.base:data/questions/examples/edit-list.yml"

  # Scenario: Test the interview "E-mail address"
  #   Given I start the interview "docassemble.base:data/questions/examples/email-field.yml"

  # Scenario: Test the interview "E-mailing the interview"
  #   Given I start the interview "docassemble.base:data/questions/examples/email-to-case-simple.yml"

  # Scenario: Test the interview "Running code upon receipt of e-mail"
  #   Given I start the interview "docassemble.base:data/questions/examples/email-to-case.yml"

  # Scenario: Test the interview "Embedded fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/embed.yml"

  # Scenario: Test the interview "Inline emoji"
  #   Given I start the interview "docassemble.base:data/questions/examples/emoji-inline.yml"

  # Scenario: Test the interview "Empty choices list"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-checkboxes-solo.yml"

  # Scenario: Test the interview "Empty choices list"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-checkboxes.yml"

  # Scenario: Test the interview "Empty choices list in fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields-multiple.yml"

  # Scenario: Test the interview "Empty choices list in fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields-solo.yml"

  # Scenario: Test the interview "Empty choices list in fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields.yml"

  # Scenario: Test the interview "Empty object checkboxes"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-create.yml"

  # Scenario: Test the interview "Empty object checkboxes"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-solo-create.yml"

  # Scenario: Test the interview "Empty object checkboxes"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-solo.yml"

  # Scenario: Test the interview "Empty object checkboxes"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes.yml"

  # Scenario: Test the interview "Empty choices list"
  #   Given I start the interview "docassemble.base:data/questions/examples/empty-choices.yml"

  # Scenario: Test the interview "Special screen"
  #   Given I start the interview "docassemble.base:data/questions/examples/event-example.yml"

  # Scenario: Test the interview "Event"
  #   Given I start the interview "docassemble.base:data/questions/examples/event-role-event.yml"

  # Scenario: Test the interview "Value attributes"
  #   Given I start the interview "docassemble.base:data/questions/examples/exists.yml"

  # Scenario: Test the interview "Mixing special buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-buttons-mixed-code.yml"

  # Scenario: Test the interview "Mixing special buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-buttons-mixed.yml"

  # Scenario: Test the interview "Exit or restart"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-buttons.yml"

  # Scenario: Test the interview "Exit or restart with choices"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-choices.yml"

  # Scenario: Test the interview "Going full screen"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-url-referer-fullscreen-mobile.yml"

  # Scenario: Test the interview "Going full screen"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-url-referer-fullscreen.yml"

  # Scenario: Test the interview "Exit to referring URL"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-url-referer.yml"

  # Scenario: Test the interview "Exit or restart with url"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit-url.yml"

  # Scenario: Test the interview "Exit programmatically"
  #   Given I start the interview "docassemble.base:data/questions/examples/exit.yml"

  # Scenario: Test the interview "Javascript and CSS files"
  #   Given I start the interview "docassemble.base:data/questions/examples/external_files.yml"

  # Scenario: Test the interview "Optional override of question"
  #   Given I start the interview "docassemble.base:data/questions/examples/fallback2.yml"

  # Scenario: Test the interview "Optional override of question"
  #   Given I start the interview "docassemble.base:data/questions/examples/fallback.yml"

  # Scenario: Test the interview "Checkbox method"
  #   Given I start the interview "docassemble.base:data/questions/examples/false-values.yml"

  # Scenario: Test the interview "Note among fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/field-note.yml"

  # Scenario: Test the interview "Checkboxes with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-code.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-0.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-1.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-2.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-3.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-4.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-5.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-6.yml"

  # Scenario: Test the interview "Checkboxes with different labels"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-different-labels.yml"

  # Scenario: Test the interview "None of the above off"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-nota-false.yml"

  # Scenario: Test the interview "None of the above default"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-nota.yml"

  # Scenario: Test the interview "Checkboxes within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes.yml"

  # Scenario: Test the interview "Combobox within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-choices-combobox.yml"

  # Scenario: Test the interview "Multiple choice pulldown"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-choices-dropdown.yml"

  # Scenario: Test the interview "Multiple choice pulldown"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-choices.yml"

  # Scenario: Test the interview "Multiple choice with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-2.yml"

  # Scenario: Test the interview "Multiple choice with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-3.yml"

  # Scenario: Test the interview "Multiple choice with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-4.yml"

  # Scenario: Test the interview "Multiple choice with code and default"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-5.yml"

  # Scenario: Test the interview "Multiple choice with code and help"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-6.yml"

  # Scenario: Test the interview "Multiple choice with code and default"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-7.yml"

  # Scenario: Test the interview "Multiple choice with default and help"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-8.yml"

  # Scenario: Test the interview "With exclusion"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-exclude-manual.yml"

  # Scenario: Test the interview "With exclusion"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-exclude.yml"

  # Scenario: Test the interview "None of the above customized"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-nota.yml"

  # Scenario: Test the interview "Conditionally show"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc-with-showif.yml"

  # Scenario: Test the interview "Multiple choice with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-mc.yml"

  # Scenario: Test the interview ""Yes/no/maybe within fields (reversed)""
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-noyesmaybe.yml"

  # Scenario: Test the interview ""Yes/no/maybe within fields""
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-yesnomaybe.yml"

  # Scenario: Test the interview "Yes/no radio buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-yesnoradio.yml"

  # Scenario: Test the interview "Yes/no checkboxes with None of the above"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-yesno-uncheck-others-list.yml"

  # Scenario: Test the interview "Yes/no checkboxes with None of the above"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-yesno-uncheck-others.yml"

  # Scenario: Test the interview "Yes/no checkboxes (wide)"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-yesnowide.yml"

  # Scenario: Test the interview "Yes/no checkboxes"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-yesno.yml"

  # Scenario: Test the interview "Fields example"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields.yml"

  # Scenario: Test the interview "File upload"
  #   Given I start the interview "docassemble.base:data/questions/examples/file.yml"

  # Scenario: Test the interview "End-of-sentence punctuation"
  #   Given I start the interview "docassemble.base:data/questions/examples/fix-punctuation.yml"

  # Scenario: Test the interview "Flushleft"
  #   Given I start the interview "docassemble.base:data/questions/examples/flushleft.yml"

  # Scenario: Test the interview "Flushright"
  #   Given I start the interview "docassemble.base:data/questions/examples/flushright.yml"

  # Scenario: Test the interview "Force asking a question"
  #   Given I start the interview "docassemble.base:data/questions/examples/force-ask-full.yml"

  # Scenario: Test the interview "Force asking several questions"
  #   Given I start the interview "docassemble.base:data/questions/examples/force-ask-multiple.yml"

  # Scenario: Test the interview "Force asking a question"
  #   Given I start the interview "docassemble.base:data/questions/examples/force-ask.yml"

  # Scenario: Test the interview ""Insist question be asked""
  #   Given I start the interview "docassemble.base:data/questions/examples/force-gather.yml"

  # Scenario: Test the interview "Simple for loop"
  #   Given I start the interview "docassemble.base:data/questions/examples/for_fruit.yml"

  # Scenario: Test the interview "Miscellaneous formatting"
  #   Given I start the interview "docassemble.base:data/questions/examples/formatting.yml"

  # Scenario: Test the interview "Forward chaining"
  #   Given I start the interview "docassemble.base:data/questions/examples/forward-chaining.yml"

  # Scenario: Test the interview "Fill fields with Mako"
  #   Given I start the interview "docassemble.base:data/questions/examples/fruit-template-alt-1.yml"

  # Scenario: Test the interview "Fill fields with variables"
  #   Given I start the interview "docassemble.base:data/questions/examples/fruit-template-alt-2.yml"

  # Scenario: Test the interview "Function"
  #   Given I start the interview "docassemble.base:data/questions/examples/function.yml"

  # Scenario: Test the interview "Gather"
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-another.yml"

  # Scenario: Test the interview ""Dictionary: ask number""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-dict-number.yml"

  # Scenario: Test the interview ""Dictionary: gather keys, objects""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-dict-object.yml"

  # Scenario: Test the interview ""Dictionary: gather keys, values""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-dict-value.yml"

  # Scenario: Test the interview ""Dictionary: gather keys, values""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-dict.yml"

  # Scenario: Test the interview ""List: gather with minimum number""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-fruit-at-least-two.yml"

  # Scenario: Test the interview ""List: the .gather method""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-fruit-gather.yml"

  # Scenario: Test the interview ""List: gather by total number""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-fruit-number.yml"

  # Scenario: Test the interview ""List: gathering""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-fruit.yml"

  # Scenario: Test the interview "Gathering a list of e-mail recipients"
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-list-email-recipients.yml"

  # Scenario: Test the interview "Gathering a list of people"
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-list-friend-bad-order.yml"

  # Scenario: Test the interview "Gathering a list of people"
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-list-friend-good-order.yml"

  # Scenario: Test the interview "Gathering a list of objects"
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-list-objects.yml"

  # Scenario: Test the interview ""List: gathering other attributes""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-manual-gathered-object-simple.yml"

  # Scenario: Test the interview ""List: gathering other attributes""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-manual-gathered-object.yml"

  # Scenario: Test the interview ""List: .auto_gather and .gathered""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-manual-gathered.yml"

  # Scenario: Test the interview ""Set: gathering""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-set-number.yml"

  # Scenario: Test the interview ""Set: gather objects""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-set-object.yml"

  # Scenario: Test the interview ""Set: gather values""
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-set.yml"

  # Scenario: Test the interview "Gather"
  #   Given I start the interview "docassemble.base:data/questions/examples/gather-simple.yml"

  # Scenario: Test the interview "Generic object fallback"
  #   Given I start the interview "docassemble.base:data/questions/examples/generic-object-ein.yml"

  # Scenario: Test the interview "generic objects"
  #   Given I start the interview "docassemble.base:data/questions/examples/generic-object-phone-number.yml"

  # Scenario: Test the interview "Generic object"
  #   Given I start the interview "docassemble.base:data/questions/examples/generic-object.yml"

  # Scenario: Test the interview "Default timezone"
  #   Given I start the interview "docassemble.base:data/questions/examples/get-default-timezone.yml"

  # Scenario: Test the interview "Not object oriented"
  #   Given I start the interview "docassemble.base:data/questions/examples/hello-not-oop.yml"

  # Scenario: Test the interview "Object oriented"
  #   Given I start the interview "docassemble.base:data/questions/examples/hello-oop.yml"

  # Scenario: Test the interview "Audio help"
  #   Given I start the interview "docassemble.base:data/questions/examples/help-damages-audio.yml"

  # Scenario: Test the interview "Help with question"
  #   Given I start the interview "docassemble.base:data/questions/examples/help-damages.yml"

  # Scenario: Test the interview "Help with question"
  #   Given I start the interview "docassemble.base:data/questions/examples/help.yml"

  # Scenario: Test the interview "Conditionally hide"
  #   Given I start the interview "docassemble.base:data/questions/examples/hideif-boolean.yml"

  # Scenario: Test the interview "HTML"
  #   Given I start the interview "docassemble.base:data/questions/examples/html.yml"

  # Scenario: Test the interview "Conditional question"
  #   Given I start the interview "docassemble.base:data/questions/examples/if.yml"

  # Scenario: Test the interview "Images with attribution"
  #   Given I start the interview "docassemble.base:data/questions/examples/image-sets.yml"

  # Scenario: Test the interview "Images without attribution"
  #   Given I start the interview "docassemble.base:data/questions/examples/images.yml"

  # Scenario: Test the interview "Immediate file"
  #   Given I start the interview "docassemble.base:data/questions/examples/immediate_file.yml"

  # Scenario: Test the interview "Import Python module"
  #   Given I start the interview "docassemble.base:data/questions/examples/imports.yml"

  # Scenario: Test the interview "Include YAML file"
  #   Given I start the interview "docassemble.base:data/questions/examples/include.yml"

  # Scenario: Test the interview "List of periods"
  #   Given I start the interview "docassemble.base:data/questions/examples/income.yml"

  # Scenario: Test the interview "Indefinite article"
  #   Given I start the interview "docassemble.base:data/questions/examples/indefinite-article.yml"

  # Scenario: Test the interview "Indent paragraphs"
  #   Given I start the interview "docassemble.base:data/questions/examples/indent.yml"

  # Scenario: Test the interview "Index variables"
  #   Given I start the interview "docassemble.base:data/questions/examples/index-variable.yml"

  # Scenario: Test the interview "Infinite loop"
  #   Given I start the interview "docassemble.base:data/questions/examples/infinite-loop.yml"

  # Scenario: Test the interview "Initial code"
  #   Given I start the interview "docassemble.base:data/questions/examples/initial-code.yml"

  # Scenario: Test the interview "Initial code"
  #   Given I start the interview "docassemble.base:data/questions/examples/initial.yml"

  # Scenario: Test the interview "Interface in use"
  #   Given I start the interview "docassemble.base:data/questions/examples/interface.yml"

  # Scenario: Test the interview "Interview help"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-help.yml"

  # Scenario: Test the interview "Action from anywhere"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview_url_action.yml"

  # Scenario: Test the interview "Several interviews in one"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url-refer.yml"

  # Scenario: Test the interview "Destination interview"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url-session-two.yml"

  # Scenario: Test the interview "Link for sharing"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url-session.yml"

  # Scenario: Test the interview "Link for sharing"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url.yml"

  # Scenario: Test the interview "Join from monitor"
  #   Given I start the interview "docassemble.base:data/questions/examples/join.yml"

  # Scenario: Test the interview "Calling actions"
  #   Given I start the interview "docassemble.base:data/questions/examples/js_url_action_call.yml"

  # Scenario: Test the interview "Action links"
  #   Given I start the interview "docassemble.base:data/questions/examples/js_url_action.yml"

  # Scenario: Test the interview "Interview variables"
  #   Given I start the interview "docassemble.base:data/questions/examples/js_variables.yml"

  # Scenario: Test the interview "Separate label and field"
  #   Given I start the interview "docassemble.base:data/questions/examples/label.yml"

  # Scenario: Test the interview "User language from browser (restricted)"
  #   Given I start the interview "docassemble.base:data/questions/examples/language_from_browser_restricted.yml"

  # Scenario: Test the interview "User language from browser"
  #   Given I start the interview "docassemble.base:data/questions/examples/language_from_browser.yml"

  # Scenario: Test the interview "Language"
  #   Given I start the interview "docassemble.base:data/questions/examples/language.yml"

  # Scenario: Test the interview "The lastfirst method"
  #   Given I start the interview "docassemble.base:data/questions/examples/lastfirst.yml"

  # Scenario: Test the interview ""Command: leave""
  #   Given I start the interview "docassemble.base:data/questions/examples/leave.yml"

  # Scenario: Test the interview "Lists"
  #   Given I start the interview "docassemble.base:data/questions/examples/lists.yml"

  # Scenario: Test the interview "Live chat"
  #   Given I start the interview "docassemble.base:data/questions/examples/live_chat.yml"

  # Scenario: Test the interview "Loading legal module"
  #   Given I start the interview "docassemble.base:data/questions/examples/loading-legal.yml"

  # Scenario: Test the interview "Loading"
  #   Given I start the interview "docassemble.base:data/questions/examples/loading-util.yml"

  # Scenario: Test the interview "Actions"
  #   Given I start the interview "docassemble.base:data/questions/examples/lucky-number.yml"

  # Scenario: Test the interview "Mad libs"
  #   Given I start the interview "docassemble.base:data/questions/examples/madlibs.yml"

  # Scenario: Test the interview "Insert variable"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-01.yml"

  # Scenario: Test the interview "If statement"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-02.yml"

  # Scenario: Test the interview "If/else statement"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-03.yml"

  # Scenario: Test the interview "Nested if/else"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-04.yml"

  # Scenario: Test the interview "For loop"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-05.yml"

  # Scenario: Test the interview "For loop over list"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-06.yml"

  # Scenario: Test the interview "Python in template"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-07.yml"

  # Scenario: Test the interview "Stop rendering Mako"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-08.yml"

  # Scenario: Test the interview "Loop object"
  #   Given I start the interview "docassemble.base:data/questions/examples/mako-09.yml"

  # Scenario: Test the interview "Mandatory code"
  #   Given I start the interview "docassemble.base:data/questions/examples/mandatory-code.yml"

  # Scenario: Test the interview "Mandatory code"
  #   Given I start the interview "docassemble.base:data/questions/examples/mandatory.yml"

  # Scenario: Test the interview "Markdown demonstration"
  #   Given I start the interview "docassemble.base:data/questions/examples/markdown-demo.yml"

  # Scenario: Test the interview "Marking up text"
  #   Given I start the interview "docassemble.base:data/questions/examples/markdown.yml"

  # Scenario: Test the interview "Several interviews in one"
  #   Given I start the interview "docassemble.base:data/questions/examples/menu-items-refer.yml"

  # Scenario: Test the interview "Menu item"
  #   Given I start the interview "docassemble.base:data/questions/examples/menu-item.yml"

  # Scenario: Test the interview ""
  #   Given I start the interview "docassemble.base:data/questions/examples/menu-system.yml"

  # Scenario: Test the interview "Question generated with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/message.yml"

  # Scenario: Test the interview "|"
  #   Given I start the interview "docassemble.base:data/questions/examples/metadata.yml"

  # Scenario: Test the interview "Min/max length"
  #   Given I start the interview "docassemble.base:data/questions/examples/minlength.yml"

  # Scenario: Test the interview "Min/Max value"
  #   Given I start the interview "docassemble.base:data/questions/examples/min.yml"

  # Scenario: Test the interview ""List: mixed object types""
  #   Given I start the interview "docassemble.base:data/questions/examples/mixed-list.yml"

  # Scenario: Test the interview "Machine learning"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-ajax-classify.yml"

  # Scenario: Test the interview "Suggestions"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-ajax.yml"

  # Scenario: Test the interview "ML from text area"
  #   Given I start the interview "docassemble.base:data/questions/examples/mlarea-datatype.yml"

  # Scenario: Test the interview "Classify"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-classify.yml"

  # Scenario: Test the interview "ML from line of text"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-datatype.yml"

  # Scenario: Test the interview "Export to YAML"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-export-yaml.yml"

  # Scenario: Test the interview "Export to JSON"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-export.yml"

  # Scenario: Test the interview "Prediction with probabilities"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-predict-probabilities.yml"

  # Scenario: Test the interview "Predict"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-predict.yml"

  # Scenario: Test the interview "Save for classification"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-save-and-predict.yml"

  # Scenario: Test the interview "Import names from module"
  #   Given I start the interview "docassemble.base:data/questions/examples/modules.yml"

  # Scenario: Test the interview "Money"
  #   Given I start the interview "docassemble.base:data/questions/examples/money-field.yml"

  # Scenario: Test the interview "Name in Mako template"
  #   Given I start the interview "docassemble.base:data/questions/examples/name-company-question.yml"

  # Scenario: Test the interview "Name in Mako template"
  #   Given I start the interview "docassemble.base:data/questions/examples/name-company.yml"

  # Scenario: Test the interview "Names"
  #   Given I start the interview "docassemble.base:data/questions/examples/name.yml"

  # Scenario: Test the interview "Need directive"
  #   Given I start the interview "docassemble.base:data/questions/examples/need-directive.yml"

  # Scenario: Test the interview "Need"
  #   Given I start the interview "docassemble.base:data/questions/examples/need.yml"

  # Scenario: Test the interview "Nested for loops"
  #   Given I start the interview "docassemble.base:data/questions/examples/nested-for-loop.yml"

  # Scenario: Test the interview "Mako for loops"
  #   Given I start the interview "docassemble.base:data/questions/examples/nested-gather.yml"

  # Scenario: Test the interview "Specific and general index variable questions"
  #   Given I start the interview "docassemble.base:data/questions/examples/nested-veggies-override.yml"

  # Scenario: Test the interview "Nested index variables"
  #   Given I start the interview "docassemble.base:data/questions/examples/nested-veggies.yml"

  # Scenario: Test the interview "Number as word"
  #   Given I start the interview "docassemble.base:data/questions/examples/nice-number.yml"

  # Scenario: Test the interview "No label"
  #   Given I start the interview "docassemble.base:data/questions/examples/no-label-field.yml"

  # Scenario: Test the interview "Notes among fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/note.yml"

  # Scenario: Test the interview "Pluralizing"
  #   Given I start the interview "docassemble.base:data/questions/examples/noun-plural.yml"

  # Scenario: Test the interview "Yes means false"
  #   Given I start the interview "docassemble.base:data/questions/examples/noyes.yml"

  # Scenario: Test the interview "Numbers"
  #   Given I start the interview "docassemble.base:data/questions/examples/number-field.yml"

  # Scenario: Test the interview "Set variable to list of objects"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-checkboxes-dalist.yml"

  # Scenario: Test the interview "Set variable to list of objects"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-checkboxes-default.yml"

  # Scenario: Test the interview "Set variable to list of objects"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-checkboxes.yml"

  # Scenario: Test the interview "Groups"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-demo.yml"

  # Scenario: Test the interview "Existing or new"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-disable-others.yml"

  # Scenario: Test the interview "Object radio buttons"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-radio.yml"

  # Scenario: Test the interview "Selections from variable"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-selections.yml"

  # Scenario: Test the interview "Define objects"
  #   Given I start the interview "docassemble.base:data/questions/examples/objects.yml"

  # Scenario: Test the interview "Bad example 1"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-try-1.yml"

  # Scenario: Test the interview "Bad example 2"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-try-2.yml"

  # Scenario: Test the interview "Setting variable to object"
  #   Given I start the interview "docassemble.base:data/questions/examples/object-try-3.yml"

  # Scenario: Test the interview "Set variable to object"
  #   Given I start the interview "docassemble.base:data/questions/examples/object.yml"

  # Scenario: Test the interview "OCR text in the background "
  #   Given I start the interview "docassemble.base:data/questions/examples/ocr-background.yml"

  # Scenario: Test the interview "Optical character recognition in the background"
  #   Given I start the interview "docassemble.base:data/questions/examples/ocr-chord-refresh.yml"

  # Scenario: Test the interview "Optical character recognition in the background"
  #   Given I start the interview "docassemble.base:data/questions/examples/ocr-chord.yml"

  # Scenario: Test the interview "OCR machine learning"
  #   Given I start the interview "docassemble.base:data/questions/examples/ocr-classify.yml"

  # Scenario: Test the interview "OCR machine learning"
  #   Given I start the interview "docassemble.base:data/questions/examples/ocr-save-and-predict.yml"

  # Scenario: Test the interview "Optical character recognition"
  #   Given I start the interview "docassemble.base:data/questions/examples/ocr.yml"

  # Scenario: Test the interview "Optional field"
  #   Given I start the interview "docassemble.base:data/questions/examples/optional-field.yml"

  # Scenario: Test the interview "Order of blocks"
  #   Given I start the interview "docassemble.base:data/questions/examples/order-of-blocks.yml"

  # Scenario: Test the interview "Ordinal numbers"
  #   Given I start the interview "docassemble.base:data/questions/examples/ordinal-number.yml"

  # Scenario: Test the interview "|"
  #   Given I start the interview "docassemble.base:data/questions/examples/other.yml"

  # Scenario: Test the interview "Overriding a question"
  #   Given I start the interview "docassemble.base:data/questions/examples/override.yml"

  # Scenario: Test the interview "Adding page numbers"
  #   Given I start the interview "docassemble.base:data/questions/examples/page-numbers.yml"

  # Scenario: Test the interview "Password"
  #   Given I start the interview "docassemble.base:data/questions/examples/password-field.yml"

  # Scenario: Test the interview "Past tense"
  #   Given I start the interview "docassemble.base:data/questions/examples/past-tense.yml"

  # Scenario: Test the interview "File path and MIME type"
  #   Given I start the interview "docassemble.base:data/questions/examples/path-and-mimetype.yml"

  # Scenario: Test the interview "PDF/A files"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-a.yml"

  # Scenario: Test the interview "PDF fill-in with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-fill-code.yml"

  # Scenario: Test the interview "PDF fill-in not editable"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-fill-not-editable.yml"

  # Scenario: Test the interview "PDF fill-in with signature"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-fill-signature.yml"

  # Scenario: Test the interview "PDF fill-in"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-fill.yml"

  # Scenario: Test the interview "Fill fields with code in Mako"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-template-alt-1.yml"

  # Scenario: Test the interview "Fill fields with field code"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-template-alt-2.yml"

  # Scenario: Test the interview "Fill fields with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-template-alt-3.yml"

  # Scenario: Test the interview "Fill fields with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/pdf-template-alt-4.yml"

  # Scenario: Test the interview "Periodic amount"
  #   Given I start the interview "docassemble.base:data/questions/examples/periodic-amount.yml"

  # Scenario: Test the interview "Periodic value attributes"
  #   Given I start the interview "docassemble.base:data/questions/examples/periodic-value.yml"

  # Scenario: Test the interview "Disable back button"
  #   Given I start the interview "docassemble.base:data/questions/examples/prevent-back.yml"

  # Scenario: Test the interview "Disable back button"
  #   Given I start the interview "docassemble.base:data/questions/examples/prevent-going-back.yml"

  # Scenario: Test the interview "Progress bar"
  #   Given I start the interview "docassemble.base:data/questions/examples/progress-features.yml"

  # Scenario: Test the interview "Progress meter"
  #   Given I start the interview "docassemble.base:data/questions/examples/progress.yml"

  # Scenario: Test the interview "Pulldown with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/pull-down-with-code.yml"

  # Scenario: Test the interview "Pulldown"
  #   Given I start the interview "docassemble.base:data/questions/examples/pull-down.yml"

  # Scenario: Test the interview "QR code"
  #   Given I start the interview "docassemble.base:data/questions/examples/qr-code-demo.yml"

  # Scenario: Test the interview "QR code"
  #   Given I start the interview "docassemble.base:data/questions/examples/qr-code.yml"

  # Scenario: Test the interview "Quantity of noun"
  #   Given I start the interview "docassemble.base:data/questions/examples/quantity-noun.yml"

  # Scenario: Test the interview "Vocabulary"
  #   Given I start the interview "docassemble.base:data/questions/examples/question-autoterms.yml"

  # Scenario: Test the interview "Question text with markup"
  #   Given I start the interview "docassemble.base:data/questions/examples/question-markup.yml"

  # Scenario: Test the interview "Question sequence"
  #   Given I start the interview "docassemble.base:data/questions/examples/question-sequence.yml"

  # Scenario: Test the interview "Vocabulary"
  #   Given I start the interview "docassemble.base:data/questions/examples/question-terms.yml"

  # Scenario: Test the interview "Question text"
  #   Given I start the interview "docassemble.base:data/questions/examples/question.yml"

  # Scenario: Test the interview "Quote paragraphs"
  #   Given I start the interview "docassemble.base:data/questions/examples/quote_paragraphs.yml"

  # Scenario: Test the interview "Radio buttons within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/radio-list.yml"

  # Scenario: Test the interview "Range slider"
  #   Given I start the interview "docassemble.base:data/questions/examples/range.yml"

  # Scenario: Test the interview "Read QR code"
  #   Given I start the interview "docassemble.base:data/questions/examples/read-qr.yml"

  # Scenario: Test the interview "Reconsidering computed values"
  #   Given I start the interview "docassemble.base:data/questions/examples/reconsider.yml"

  # Scenario: Test the interview "Using redis"
  #   Given I start the interview "docassemble.base:data/questions/examples/redis.yml"

  # Scenario: Test the interview "Refresh button"
  #   Given I start the interview "docassemble.base:data/questions/examples/refresh.yml"

  # Scenario: Test the interview "Auto reload"
  #   Given I start the interview "docassemble.base:data/questions/examples/reload.yml"

  # Scenario: Test the interview "Optional field with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/required-code.yml"

  # Scenario: Test the interview "Resetting variables"
  #   Given I start the interview "docassemble.base:data/questions/examples/reset.yml"

  # Scenario: Test the interview "Custom response"
  #   Given I start the interview "docassemble.base:data/questions/examples/response-hello.yml"

  # Scenario: Test the interview "JSON response"
  #   Given I start the interview "docassemble.base:data/questions/examples/response-json.yml"

  # Scenario: Test the interview "Binary response"
  #   Given I start the interview "docassemble.base:data/questions/examples/response-svg.yml"

  # Scenario: Test the interview "Custom response"
  #   Given I start the interview "docassemble.base:data/questions/examples/response.yml"

  # Scenario: Test the interview "Custom button on review screen"
  #   Given I start the interview "docassemble.base:data/questions/examples/resume-button-label.yml"

  # Scenario: Test the interview "Review answers"
  #   Given I start the interview "docassemble.base:data/questions/examples/review-1.yml"

  # Scenario: Test the interview "Review answers"
  #   Given I start the interview "docassemble.base:data/questions/examples/review-2.yml"

  # Scenario: Test the interview "Review answers"
  #   Given I start the interview "docassemble.base:data/questions/examples/review-3.yml"

  # Scenario: Test the interview "Review answers"
  #   Given I start the interview "docassemble.base:data/questions/examples/review-4.yml"

  # Scenario: Test the interview "Review answers"
  #   Given I start the interview "docassemble.base:data/questions/examples/review.yml"

  # Scenario: Test the interview "Salutation"
  #   Given I start the interview "docassemble.base:data/questions/examples/salutation.yml"

  # Scenario: Test the interview "Custom function in module"
  #   Given I start the interview "docassemble.base:data/questions/examples/sample-function.yml"

  # Scenario: Test the interview "Save for classification"
  #   Given I start the interview "docassemble.base:data/questions/examples/save-and-predict.yml"

  # Scenario: Test the interview "Save URL to file"
  #   Given I start the interview "docassemble.base:data/questions/examples/save-url-to-file.yml"

  # Scenario: Test the interview "Opt out of variable seeking"
  #   Given I start the interview "docassemble.base:data/questions/examples/scan-for-variables-original.yml"

  # Scenario: Test the interview "Opt out of variable seeking"
  #   Given I start the interview "docassemble.base:data/questions/examples/scan-for-variables-sets.yml"

  # Scenario: Test the interview "Opt out of variable seeking"
  #   Given I start the interview "docassemble.base:data/questions/examples/scan-for-variables.yml"

  # Scenario: Test the interview "Javascript"
  #   Given I start the interview "docassemble.base:data/questions/examples/script.yml"

  # Scenario: Test the interview "Navigation with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/sections-keywords-code.yml"

  # Scenario: Test the interview "Sections as list"
  #   Given I start the interview "docassemble.base:data/questions/examples/sections-keywords-get-sections.yml"

  # Scenario: Test the interview "Navigation with review pages"
  #   Given I start the interview "docassemble.base:data/questions/examples/sections-keywords-review.yml"

  # Scenario: Test the interview "Redefine sections"
  #   Given I start the interview "docassemble.base:data/questions/examples/sections-keywords-set-sections.yml"

  # Scenario: Test the interview "Navigation with keywords"
  #   Given I start the interview "docassemble.base:data/questions/examples/sections-keywords.yml"

  # Scenario: Test the interview "Navigation bar"
  #   Given I start the interview "docassemble.base:data/questions/examples/sections.yml"

  # Scenario: Test the interview "Send e-mail with attachment"
  #   Given I start the interview "docassemble.base:data/questions/examples/send-email-with-attachment.yml"

  # Scenario: Test the interview "Send e-mail"
  #   Given I start the interview "docassemble.base:data/questions/examples/send-email.yml"

  # Scenario: Test the interview "Send SMS message"
  #   Given I start the interview "docassemble.base:data/questions/examples/send-sms.yml"

  # Scenario: Test the interview "Set language"
  #   Given I start the interview "docassemble.base:data/questions/examples/set-language.yml"

  # Scenario: Test the interview "Conditionally show"
  #   Given I start the interview "docassemble.base:data/questions/examples/showif-boolean.yml"

  # Scenario: Test the interview "Hide fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/showif.yml"

  # Scenario: Test the interview "Shuffle"
  #   Given I start the interview "docassemble.base:data/questions/examples/shuffle.yml"

  # Scenario: Test the interview "Signature"
  #   Given I start the interview "docassemble.base:data/questions/examples/signature.yml"

  # Scenario: Test the interview "Sign in button"
  #   Given I start the interview "docassemble.base:data/questions/examples/signin.yml"

  # Scenario: Test the interview "Spacing"
  #   Given I start the interview "docassemble.base:data/questions/examples/single-spacing.yml"

  # Scenario: Test the interview "SMS interface"
  #   Given I start the interview "docassemble.base:data/questions/examples/sms.yml"

  # Scenario: Test the interview ""
  #   Given I start the interview "docassemble.base:data/questions/examples/someone-already-mentioned2.yml"

  # Scenario: Test the interview "Space to underscore"
  #   Given I start the interview "docassemble.base:data/questions/examples/space-underscore.yml"

  # Scenario: Test the interview "State selection"
  #   Given I start the interview "docassemble.base:data/questions/examples/state.yml"

  # Scenario: Test the interview "Insert image with code"
  #   Given I start the interview "docassemble.base:data/questions/examples/static_image.yml"

  # Scenario: Test the interview "Subdivision type"
  #   Given I start the interview "docassemble.base:data/questions/examples/subdivision-type.yml"

  # Scenario: Test the interview "Question text"
  #   Given I start the interview "docassemble.base:data/questions/examples/subquestion.yml"

  # Scenario: Test the interview "Precedence of blocks"
  #   Given I start the interview "docassemble.base:data/questions/examples/supersede-order.yml"

  # Scenario: Test the interview "Precedence of blocks"
  #   Given I start the interview "docassemble.base:data/questions/examples/supersede-regular.yml"

  # Scenario: Test the interview "Precedence of blocks"
  #   Given I start the interview "docassemble.base:data/questions/examples/supersede.yml"

  # Scenario: Test the interview "Table block"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-alt.yml"

  # Scenario: Test the interview "Empty table"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-empty-message.yml"

  # Scenario: Test the interview "Empty table"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-empty.yml"

  # Scenario: Test the interview "Table block"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-if-then.yml"

  # Scenario: Test the interview "Table with Mako"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-mako.yml"

  # Scenario: Test the interview "Tables in Markdown"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-markdown-noheader.yml"

  # Scenario: Test the interview "Tables in Markdown"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-markdown-unaligned.yml"

  # Scenario: Test the interview "Tables in Markdown"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-markdown.yml"

  # Scenario: Test the interview "Table block"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-python.yml"

  # Scenario: Test the interview "Table block"
  #   Given I start the interview "docassemble.base:data/questions/examples/table-width.yml"

  # Scenario: Test the interview "Table block"
  #   Given I start the interview "docassemble.base:data/questions/examples/table.yml"

  # Scenario: Test the interview "Check in feedback"
  #   Given I start the interview "docassemble.base:data/questions/examples/target-code-multiple.yml"

  # Scenario: Test the interview "Check in, run code, and return template"
  #   Given I start the interview "docassemble.base:data/questions/examples/target-code-template.yml"

  # Scenario: Test the interview "Check in and run code"
  #   Given I start the interview "docassemble.base:data/questions/examples/target-code.yml"

  # Scenario: Test the interview "Check in and return template"
  #   Given I start the interview "docassemble.base:data/questions/examples/target-template.yml"

  # Scenario: Test the interview "Computed template filename"
  #   Given I start the interview "docassemble.base:data/questions/examples/template-code.yml"

  # Scenario: Test the interview "Template from file"
  #   Given I start the interview "docassemble.base:data/questions/examples/template-file.yml"

  # Scenario: Test the interview "Template subject"
  #   Given I start the interview "docassemble.base:data/questions/examples/template-subject.yml"

  # Scenario: Test the interview "Template"
  #   Given I start the interview "docassemble.base:data/questions/examples/template.yml"

  # Scenario: Test the interview "Final screen"
  #   Given I start the interview "docassemble.base:data/questions/examples/terminal-screen.yml"

  # Scenario: Test the interview "Vocabulary"
  #   Given I start the interview "docassemble.base:data/questions/examples/terms.yml"

  # Scenario: Test the interview "Age"
  #   Given I start the interview "docassemble.base:data/questions/examples/testage2.yml"

  # Scenario: Test the interview "DAList"
  #   Given I start the interview "docassemble.base:data/questions/examples/testdalist.yml"

  # Scenario: Test the interview "Message to output"
  #   Given I start the interview "docassemble.base:data/questions/examples/testmessage.yml"

  # Scenario: Test the interview "Text box"
  #   Given I start the interview "docassemble.base:data/questions/examples/text-box-field.yml"

  # Scenario: Test the interview "Default value with Mako"
  #   Given I start the interview "docassemble.base:data/questions/examples/text-default.yml"

  # Scenario: Test the interview "Text example"
  #   Given I start the interview "docassemble.base:data/questions/examples/text-field-example.yml"

  # Scenario: Test the interview "Text"
  #   Given I start the interview "docassemble.base:data/questions/examples/text-field.yml"

  # Scenario: Test the interview "Help on label"
  #   Given I start the interview "docassemble.base:data/questions/examples/text-help.yml"

  # Scenario: Test the interview "Hints"
  #   Given I start the interview "docassemble.base:data/questions/examples/text-hint.yml"

  # Scenario: Test the interview "Selecting a timezone"
  #   Given I start the interview "docassemble.base:data/questions/examples/timezone-list.yml"

  # Scenario: Test the interview "Title case"
  #   Given I start the interview "docassemble.base:data/questions/examples/title-case.yml"

  # Scenario: Test the interview ""Today's date""
  #   Given I start the interview "docassemble.base:data/questions/examples/today.yml"

  # Scenario: Test the interview "Checkbox method"
  #   Given I start the interview "docassemble.base:data/questions/examples/true-values.yml"

  # Scenario: Test the interview "Two columns"
  #   Given I start the interview "docassemble.base:data/questions/examples/twocol.yml"

  # Scenario: Test the interview "Several interviews in one"
  #   Given I start the interview "docassemble.base:data/questions/examples/umbrella-interview.yml"

  # Scenario: Test the interview "Text underneath"
  #   Given I start the interview "docassemble.base:data/questions/examples/under.yml"

  # Scenario: Test the interview "Upload and listen to audio"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload_audio_microphone.yml"

  # Scenario: Test the interview "Upload and listen to audio"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload_audio.yml"

  # Scenario: Test the interview "Upload photos"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload_images.yml"

  # Scenario: Test the interview "Maximum image size"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload-max-image-size-features.yml"

  # Scenario: Test the interview "Maximum image size"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload-max-image-size.yml"

  # Scenario: Test the interview "Upload multiple files"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload-multiple.yml"

  # Scenario: Test the interview "Upload file"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload-show-width.yml"

  # Scenario: Test the interview "Upload file"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload-show.yml"

  # Scenario: Test the interview "Upload file"
  #   Given I start the interview "docassemble.base:data/questions/examples/upload.yml"

  # Scenario: Test the interview "Link to static file"
  #   Given I start the interview "docassemble.base:data/questions/examples/url-of.yml"

  # Scenario: Test the interview "Including a question library"
  #   Given I start the interview "docassemble.base:data/questions/examples/use-question-library.yml"

  # Scenario: Test the interview "Objects have independent existence"
  #   Given I start the interview "docassemble.base:data/questions/examples/user-is-trustee.yml"

  # Scenario: Test the interview "Output formats"
  #   Given I start the interview "docassemble.base:data/questions/examples/valid-formats.yml"

  # Scenario: Test the interview "Value of a variable"
  #   Given I start the interview "docassemble.base:data/questions/examples/value.yml"

  # Scenario: Test the interview "Variables as JSON"
  #   Given I start the interview "docassemble.base:data/questions/examples/variables_as_json.yml"

  # Scenario: Test the interview "Video with YouTube"
  #   Given I start the interview "docassemble.base:data/questions/examples/video.yml"

  # Scenario: Test the interview "Video with Vimeo"
  #   Given I start the interview "docassemble.base:data/questions/examples/vimeo.yml"

  # Scenario: Test the interview "Interview, tweaked"
  #   Given I start the interview "docassemble.base:data/questions/examples/with-mandatory-tweak-a.yml"

  # Scenario: Test the interview "Interview, tweaked"
  #   Given I start the interview "docassemble.base:data/questions/examples/with-mandatory-tweak-b.yml"

  # Scenario: Test the interview "Interview"
  #   Given I start the interview "docassemble.base:data/questions/examples/with-mandatory.yml"

  # Scenario: Test the interview "An Interview"
  #   Given I start the interview "docassemble.base:data/questions/examples/yaml-markdown-python.yml"

  # Scenario: Test the interview "Custom yes/no"
  #   Given I start the interview "docassemble.base:data/questions/examples/yesno-custom.yml"

  # Scenario: Test the interview ""Yes/no/maybe""
  #   Given I start the interview "docassemble.base:data/questions/examples/yesnomaybe.yml"

  # Scenario: Test the interview "Yes/no"
  #   Given I start the interview "docassemble.base:data/questions/examples/yesno.yml"

  # Scenario: Test the interview "Custom objects from file"
  #   Given I start the interview "docassemble.demo:data/questions/examples/fish-example.yml"

  # Scenario: Test the interview "Multi-user interview"
  #   Given I start the interview "docassemble.demo:data/questions/examples/multi-user.yml"

  # Scenario: Test the interview "Import dictionary"
  #   Given I start the interview "docassemble.demo:data/questions/examples/objects-from-file-dadict.yml"

  # Scenario: Test the interview "Import and gather more"
  #   Given I start the interview "docassemble.demo:data/questions/examples/objects-from-file-gather.yml"

  # Scenario: Test the interview "Objects from file"
  #   Given I start the interview "docassemble.demo:data/questions/examples/objects-from-file.yml"

  # Scenario: Test the interview "Share training sets"
  #   Given I start the interview "docassemble.demo:data/questions/examples/predict-activity-activity.yml"

  # Scenario: Test the interview "Share training sets"
  #   Given I start the interview "docassemble.demo:data/questions/examples/predict-activity.yml"

  # Scenario: Test the interview "Machine Learning"
  #   Given I start the interview "docassemble.demo:data/questions/examples/predict-happy-sad-area.yml"

  # Scenario: Test the interview "Machine Learning"
  #   Given I start the interview "docassemble.demo:data/questions/examples/predict-happy-sad.yml"

  # Scenario: Test the interview "Objects from file"
  #   Given I start the interview "docassemble.demo:data/questions/examples/raw-data-example.yml"

  # Scenario: Test the interview "Run a Python module"
  #   Given I start the interview "docassemble.demo:data/questions/examples/run-python-module-2.yml"

  # Scenario: Test the interview "Run a Python module"
  #   Given I start the interview "docassemble.demo:data/questions/examples/run-python-module-3.yml"

  # Scenario: Test the interview "Run a Python module"
  #   Given I start the interview "docassemble.demo:data/questions/examples/run-python-module-tests.yml"

  # Scenario: Test the interview "Run a Python module"
  #   Given I start the interview "docassemble.demo:data/questions/examples/run-python-module.yml"

  # Scenario: Test the interview "Object with disable others"
  #   Given I start the interview "docassemble.demo:data/questions/examples/someone-already-mentioned.yml"

  # Scenario: Test the interview "Recipe"
  #   Given I start the interview "docassemble.demo:data/questions/examples/testcooking.yml"

  # Scenario: Test the interview "Google Map"
  #   Given I start the interview "docassemble.demo:data/questions/examples/testgeolocate.yml"

  # Scenario: Test the interview "Input validation"
  #   Given I start the interview "docassemble.demo:data/questions/examples/validation-code.yml"

  # Scenario: Test the interview "Input validation"
  #   Given I start the interview "docassemble.demo:data/questions/examples/validation-test-two.yml"

  # Scenario: Test the interview "Input validation"
  #   Given I start the interview "docassemble.demo:data/questions/examples/validation-test.yml"
