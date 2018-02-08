Feature: Example interviews
  In order to ensure docassemble is running properly, I want
  to run the example interviews.

  # Scenario: Set up the server
  #   Given I am using the server "http://localhost"
  
  # Scenario: Test the interview "File upload"
  #   Given I start the interview "docassemble.base:data/questions/examples/file.yml"
  #   Then I should see the phrase "Please upload a file"
  #   And I upload the file "../../octocat.png"
  #   And I click the button "Continue"
  #   And I wait 2 seconds
  #   Then I should see the phrase "Here is the file you uploaded"

  Scenario: Test the interview "Action with arguments"
    Given I start the interview "docassemble.base:data/questions/examples/actions-parameters.yml"
    And I click the link "Add blue fish"
    When I wait 4 seconds
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
    Then I should see the phrase "What is your date of birth?"
    And I set the text box to "03/31/1977"
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

  Scenario: Test the interview "Disallowing e-mailing 1"
    Given I start the interview "docassemble.base:data/questions/examples/allow-emailing-false-pdf.yml"
    And I wait 5 seconds
    Then I should not see the phrase "E-mail this document"

  Scenario: Test the interview "Disallowing e-mailing 2"
    Given I start the interview "docassemble.base:data/questions/examples/allow-emailing-false.yml"
    And I wait 5 seconds
    Then I should not see the phrase "E-mail this document"

  Scenario: Test the interview "Allowing documents to be e-mailed"
    Given I start the interview "docassemble.base:data/questions/examples/allow-emailing-true.yml"
    And I wait 5 seconds
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
#    When I exit by clicking "Exit"
#    And I wait 5 seconds
#    Then I should see "A demonstration of docassemble" as the title of the page
#    And I should see "https://docassemble.org/demo.html" as the URL of the page
    
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
    And I wait 4 seconds
    Then I should see the phrase "The first document"
    And I should see the phrase "The second document"
    And I should see the phrase "The third document"

  Scenario: Test the interview "Attachment"
    Given I start the interview "docassemble.base:data/questions/examples/attachment-simple.yml"
    And I wait 4 seconds
    Then I should see the phrase "A hello world document"
    And I should see the phrase "A document with a classic message"

  Scenario: Test the interview "Allowing documents to be e-mailed"
    Given I start the interview "docassemble.base:data/questions/examples/attachment.yml"
    And I wait 4 seconds
    Then I should see the phrase "A hello world document"
    And I should see the phrase "A document with a classic message"
    And I should see the phrase "E-mail address"

  # Scenario: Test the interview "Inheritance"
  #   Given I start the interview "docassemble.base:data/questions/examples/attorney.yml"

  # Scenario: Test the interview "Audio upload"
  #   Given I start the interview "docassemble.base:data/questions/examples/audio-upload.yml"

  # Scenario: Test the interview "Audio"
  #   Given I start the interview "docassemble.base:data/questions/examples/audio.yml"

  Scenario: Test the interview "Global terms"
    Given I start the interview "docassemble.base:data/questions/examples/auto-terms.yml"
    Then I should see the phrase "Have you ever met a creeper?"
    And I click the link "creeper"
    Then I should see the phrase "A tall green creature that explodes if you get too close."
    And I click the button "No"
    Then I should see the phrase "You clearly need to play more Minecraft."

  Scenario: Test the interview "Return a value and show a message"
    Given I start the interview "docassemble.base:data/questions/examples/background_action_flash.yml"
    Then I should see the phrase "How much shall I add to 553?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "Your answer will appear shortly."
    And I wait 12 seconds
    Then I should see the phrase "The answer is 555."
    And I click the button "Continue"
    Then I should see the phrase "All done."
    And I should see the phrase "The answer is 555."

  # Scenario: Test the interview "Return a value and run Javascript"
  #   Given I start the interview "docassemble.base:data/questions/examples/background_action_javascript.yml"

  Scenario: Test the interview "Set a variable and refresh the screen"
    Given I start the interview "docassemble.base:data/questions/examples/background_action_refresh.yml"
    Then I should see the phrase "How much shall I add to 553?"
    And I set "Number" to "2"
    And I click the button "Continue"
    And I wait 12 seconds
    Then I should see the phrase "The answer is 555."

  Scenario: Test the interview "Set a variable"
    Given I start the interview "docassemble.base:data/questions/examples/background_action_with_response_action.yml"
    Then I should see the phrase "How much shall I add to 553?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "Hang tight."
    And I wait 12 seconds
    Then I should see the phrase "The answer is 555."

  Scenario: Test the interview "Return a value"
    Given I start the interview "docassemble.base:data/questions/examples/background_action.yml"
    Then I should see the phrase "How much shall I add to 553?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "Hang tight."
    And I wait 12 seconds
    Then I should see the phrase "The answer is 555."

  Scenario: Test the interview "Set a variable and show a message"
    Given I start the interview "docassemble.base:data/questions/examples/background_response_action_flash.yml"
    Then I should see the phrase "How much shall I add to 553?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "Your answer will appear shortly."
    And I wait 12 seconds
    Then I should see the phrase "The answer is 555."
    And I click the button "Continue"
    Then I should see the phrase "The answer is 555."

  Scenario: Test the interview "Blank label"
    Given I start the interview "docassemble.base:data/questions/examples/blank-label-field.yml"
    Then I should see the phrase "What is your Zodiac sign?"
    And I set the text box to "Aries"
    And I click the button "Continue"
    Then I should see the phrase "target_variable is: “Aries”"

  Scenario: Test the interview "Object"
    Given I start the interview "docassemble.base:data/questions/examples/branch-no-error.yml"
    Then I should see the phrase "What is the length of the branch on the tree?"
    And I set "Length" to "30"
    And I click the button "Continue"
    Then I should see the phrase "The length of the branch is 30."

  Scenario: Test the interview "Buttons that run code"
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code-color.yml"
    Then I should see the phrase "What is your favorite color?"
    And I click the button "Red"
    Then I should see the phrase "Dark red or light red?"
    And I click the button "Dark Red"
    Then I should see the phrase "Your favorite color is Dark Red."

  Scenario: Test the interview "Buttons defined with list" and understands
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list-equivalent.yml"
    Then I should see the phrase "Your use of this system does not mean that you have a lawyer. Do you understand this?"
    And I click the button "I understand"
    Then I should see the phrase "target_variable is: “understands”"

  Scenario: Test the interview "Buttons defined with list" and does not understand
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list-equivalent.yml"
    Then I should see the phrase "Your use of this system does not mean that you have a lawyer. Do you understand this?"
    And I click the button "I do not understand"
    Then I should see the phrase "target_variable is: “does not understand”"

  Scenario: Test the interview "Buttons defined with list" and is not sure
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list-equivalent.yml"
    Then I should see the phrase "Your use of this system does not mean that you have a lawyer. Do you understand this?"
    And I click the button "I’m not sure"
    Then I should see the phrase "target_variable is: “unsure”"

  Scenario: Test the interview "Buttons defined with code"
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list-partial.yml"
    Then I should see the phrase "Your use of this system does not mean that you have a lawyer. Do you understand this?"
    And I click the button "I understand"
    Then I should see the phrase "target_variable is: “understands”"

  Scenario: Test the interview "Buttons defined with code"
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code-list.yml"
    Then I should see the phrase "Your use of this system does not mean that you have a lawyer. Do you understand this?"
    And I click the button "I understand"
    Then I should see the phrase "target_variable is: “understands”"

  Scenario: Test the interview "Buttons that run code" with Ford Focus
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code.yml"
    Then I should see the phrase "What kind of car do you want?"
    And I click the button "Ford Focus"
    Then I should see the phrase "You need to go to a Ford dealership and ask if they have a Focus for sale."

  Scenario: Test the interview "Buttons that run code" with Toyota Camry
    Given I start the interview "docassemble.base:data/questions/examples/buttons-code.yml"
    Then I should see the phrase "What kind of car do you want?"
    And I click the button "Toyota Camry"
    Then I should see the phrase "You need to go to a Toyota dealership and ask if they have a Camry for sale."
    
  # Scenario: Test the interview "Buttons with icons from code"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-icons-code-upload.yml"

  Scenario: Test the interview "Buttons with icons from code"
    Given I start the interview "docassemble.base:data/questions/examples/buttons-icons-code.yml"
    Then I should see the phrase "What is the most important question to ask?"
    And I click the button "When?"
    Then I should see the phrase "In that case, when were you born?"
    And I set the text box to "1977"
    And I click the button "Continue"
    Then I should see the phrase "You were born in 1977."

  # Scenario: Test the interview "Buttons with icons"
  #   Given I start the interview "docassemble.base:data/questions/examples/buttons-icons.yml"

  Scenario: Test the interview "Labels ≠ values" first
    Given I start the interview "docassemble.base:data/questions/examples/buttons-labels.yml"
    Then I should see the phrase "How would you like to pay for your car?"
    And I click the button "Buy it"
    Then I should see the phrase "You are a purchaser."

  Scenario: Test the interview "Labels ≠ values" second
    Given I start the interview "docassemble.base:data/questions/examples/buttons-labels.yml"
    Then I should see the phrase "How would you like to pay for your car?"
    And I click the button "Lease it"
    Then I should see the phrase "You are a borrower."

  Scenario: Test the interview "Buttons" first
    Given I start the interview "docassemble.base:data/questions/examples/buttons-variation-1.yml"
    Then I should see the phrase "What is your gender?"
    And I click the button "Male"
    Then I should see the phrase "You are Male."

  Scenario: Test the interview "Buttons" second
    Given I start the interview "docassemble.base:data/questions/examples/buttons-variation-1.yml"
    Then I should see the phrase "What is your gender?"
    And I click the button "Female"
    Then I should see the phrase "You are Female."

  Scenario: Test the interview "Buttons variation two" first
    Given I start the interview "docassemble.base:data/questions/examples/buttons-variation-2.yml"
    Then I should see the phrase "What is your gender?"
    And I click the button "Male"
    Then I should see the phrase "You are Male."

  Scenario: Test the interview "Buttons variation two" second
    Given I start the interview "docassemble.base:data/questions/examples/buttons-variation-2.yml"
    Then I should see the phrase "What is your gender?"
    And I click the button "Female"
    Then I should see the phrase "You are Female."

  Scenario: Test the interview "Buttons" first
    Given I start the interview "docassemble.base:data/questions/examples/buttons.yml"
    Then I should see the phrase "What type of belly button do you have?"
    And I click the button "Innie"
    Then I should see the phrase "target_variable is: “Innie”"

  Scenario: Test the interview "Buttons" second
    Given I start the interview "docassemble.base:data/questions/examples/buttons.yml"
    Then I should see the phrase "What type of belly button do you have?"
    And I click the button "Outie"
    Then I should see the phrase "target_variable is: “Outie”"

  Scenario: Test the interview "Buttons" third
    Given I start the interview "docassemble.base:data/questions/examples/buttons.yml"
    Then I should see the phrase "What type of belly button do you have?"
    And I click the button "No belly button"
    Then I should see the phrase "target_variable is: “No belly button”"

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

  # Scenario: Test the interview "Dictionary: prepopuated objects"
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

  # Scenario: Test the interview "From .md file"
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

  Scenario: Test the interview "Empty choices list" with no checkboxes
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-checkboxes-solo.yml"
    Then I should see the phrase "Should the list of choices for the checkboxes field be empty?"
    And I click the button "Yes"
    Then I should see the phrase "No doors could be chosen."
    
  Scenario: Test the interview "Empty choices list" with checkboxes
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-checkboxes-solo.yml"
    Then I should see the phrase "Should the list of choices for the checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "What do you choose?"
    And I click the "Door Number 1" option
    And I click the button "Continue"
    Then I should see the phrase "You chose Door Number 1."
    
  Scenario: Test the interview "Empty choices list" with checkboxes and no selection
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-checkboxes-solo.yml"
    Then I should see the phrase "Should the list of choices for the checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "What do you choose?"
    And I click the "None of the above" option
    And I click the button "Continue"
    Then I should see the phrase "You chose no doors."

  Scenario: Test the interview "Empty choices list" with empty list
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-checkboxes.yml"
    Then I should see the phrase "Should the list of choices for the checkboxes field be empty?"
    And I click the button "Yes"
    Then I should not see the phrase "Door Number 1"
    And I set "Favorite fruit" to "apples"
    And I click the button "Continue"
    Then I should see the phrase "No doors could be chosen."

  Scenario: Test the interview "Empty choices list" with non-empty list
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-checkboxes.yml"
    Then I should see the phrase "Should the list of choices for the checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "What do you choose?"
    And I set "Favorite fruit" to "apples"
    And I click the "Door Number 1" option
    And I click the button "Continue"
    Then I should see the phrase "You chose Door Number 1."

  Scenario: Test the interview "Empty choices list in fields" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields-multiple.yml"
    Then I should see the phrase "Should the list of choices for the radio field be empty?"
    And I click the button "Yes"
    Then I should see the phrase "There were no choices available."
    And I should see the phrase "door is None."
    And I should see the phrase "bucket is None."
    
  Scenario: Test the interview "Empty choices list in fields" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields-multiple.yml"
    Then I should see the phrase "Should the list of choices for the radio field be empty?"
    And I click the button "No"
    Then I should see the phrase "What do you choose?"
    And I click the "Door Number 1" option
    And I click the "Green Bucket" option
    And I click the button "Continue"
    Then I should see the phrase "door is Door Number 1."
    And I should see the phrase "bucket is Green Bucket."

  Scenario: Test the interview "Empty choices list in fields" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields-solo.yml"
    Then I should see the phrase "Should the list of choices for the radio field be empty?"
    And I click the button "Yes"
    Then I should see the phrase "There were no choices available."
    And I should see the phrase "door is None."

  Scenario: Test the interview "Empty choices list in fields" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields-solo.yml"
    Then I should see the phrase "Should the list of choices for the radio field be empty?"
    And I click the button "No"
    Then I should see the phrase "What do you choose?"
    And I click the "Door Number 1" option
    And I click the button "Continue"
    Then I should see the phrase "door is Door Number 1."

  Scenario: Test the interview "Empty choices list in fields" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields.yml"
    Then I should see the phrase "Should the list of choices for the radio field be empty?"
    And I click the button "Yes"
    Then I should not see the phrase "Door Number 1."
    And I set "Fruit" to "apples"
    And I click the button "Continue"
    Then I should see the phrase "door is None."
    
  Scenario: Test the interview "Empty choices list in fields" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-fields.yml"
    Then I should see the phrase "Should the list of choices for the radio field be empty?"
    And I click the button "No"
    Then I should see the phrase "What do you choose?"
    And I set "Fruit" to "apples"
    And I click the "Door Number 1" option
    And I click the button "Continue"
    Then I should see the phrase "door is Door Number 1."

  Scenario: Test the interview "Empty object checkboxes" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-create.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "Yes"
    Then I should see the phrase "Please answer this."
    And I should not see the phrase "Harry Potter"
    And I set "Favorite fruit" to "apples"
    And I click the button "Continue"
    Then I should see the phrase "There are no villains here. In fact, no villains ever existed."
    
  Scenario: Test the interview "Empty object checkboxes" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-create.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "Please answer this."
    And I set "Favorite fruit" to "apples"
    And I click the "Harry Potter" option
    And I click the button "Continue"
    Then I should see the phrase "The villain includes Harry Potter."
    
  Scenario: Test the interview "Empty object checkboxes" with non-empty choices and nota
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-create.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "Please answer this."
    And I set "Favorite fruit" to "apples"
    And I click the "None of the above" option
    And I click the button "Continue"
    Then I should see the phrase "There are no villains here."
    
  Scenario: Test the interview "Empty object checkboxes" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-solo-create.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "Yes"
    Then I should see the phrase "There are no villains here. In fact, no villains ever existed."

  Scenario: Test the interview "Empty object checkboxes" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-solo-create.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "Who are the villains, if any?"
    And I click the "Harry Potter" option
    And I click the button "Continue"
    Then I should see the phrase "The villain includes Harry Potter."

  Scenario: Test the interview "Empty object checkboxes" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-solo.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "Yes"
    Then I should see the phrase "There are no villains here. In fact, no villains ever existed."
    
  Scenario: Test the interview "Empty object checkboxes" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes-solo.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "Who are the villains, if any?"
    And I click the "Tom Riddle" option
    And I click the button "Continue"
    Then I should see the phrase "The villain includes Tom Riddle."

  Scenario: Test the interview "Empty object checkboxes" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "Yes"
    Then I should see the phrase "Please answer this."
    And I should not see the phrase "Tom Riddle"
    And I set "Favorite fruit" to "apples"
    And I click the button "Continue"
    Then I should see the phrase "There are no villains here. In fact, no villains ever existed."
    And I should see the phrase "Your favorite fruit is apples."
  
  Scenario: Test the interview "Empty object checkboxes" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices-object-checkboxes.yml"
    Then I should see the phrase "Should the list of choices for the object_checkboxes field be empty?"
    And I click the button "No"
    Then I should see the phrase "Please answer this."
    And I set "Favorite fruit" to "apples"
    And I click the "Tom Riddle" option
    And I click the button "Continue"
    Then I should see the phrase "The villain includes Tom Riddle."
    And I should see the phrase "Your favorite fruit is apples."
  
  Scenario: Test the interview "Empty choices list" with empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices.yml"
    Then I should see the phrase "Should the list of choices for the multiple choice question be empty?"
    And I click the button "Yes"
    Then I should see the phrase "There were no choices available."
    And I should see the phrase "door is None"

  Scenario: Test the interview "Empty choices list" with non-empty choices
    Given I start the interview "docassemble.base:data/questions/examples/empty-choices.yml"
    Then I should see the phrase "Should the list of choices for the multiple choice question be empty?"
    And I click the button "No"
    Then I should see the phrase "What do you choose?"
    And I click the "Door Number 1" option
    And I click the button "Continue"
    Then I should see the phrase "You chose Door Number 1."
    And I should see the phrase "door is Door Number 1"

  Scenario: Test the interview "Special screen"
    Given I start the interview "docassemble.base:data/questions/examples/event-example.yml"
    Then I should see the phrase "This is a special screen."

  # Scenario: Test the interview "Event"
  #   Given I start the interview "docassemble.base:data/questions/examples/event-role-event.yml"

  Scenario: Test the interview "Value attributes" with answer yes
    Given I start the interview "docassemble.base:data/questions/examples/exists.yml"
    Then I should see the phrase "Do you have real estate holdings?"
    And I click the button "Yes"
    Then I should see the phrase "How much real estate do you own?"
    And I set "Value" to "100000"
    And I click the button "Continue"
    Then I should see the phrase "The value of your real estate holdings is $100,000.00."

  Scenario: Test the interview "Value attributes" with answer yes
    Given I start the interview "docassemble.base:data/questions/examples/exists.yml"
    Then I should see the phrase "Do you have real estate holdings?"
    And I click the button "No"
    Then I should see the phrase "You do not have real estate."

  Scenario: Test the interview "Mixing special buttons"
    Given I start the interview "docassemble.base:data/questions/examples/exit-buttons-mixed-code.yml"
    Then I should see the phrase "Warning!"
    And I should see the phrase "Proceeding with this interview may result in despair-inducing levels of liability."
    And I click the button "Keep going"
    Then I should see the phrase "Hey, I warned you."

  Scenario: Test the interview "Mixing special buttons" with button 1
    Given I start the interview "docassemble.base:data/questions/examples/exit-buttons-mixed.yml"
    Then I should see the phrase "Warning!"
    And I should see the phrase "Proceeding with this interview may result in despair-inducing levels of liability."
    And I click the button "I understand"
    Then I should see the phrase "Ok, we are proceeding with caution."
    
  Scenario: Test the interview "Mixing special buttons" with button 2
    Given I start the interview "docassemble.base:data/questions/examples/exit-buttons-mixed.yml"
    Then I should see the phrase "Warning!"
    And I should see the phrase "Proceeding with this interview may result in despair-inducing levels of liability."
    And I click the button "I do not care"
    Then I should see the phrase "You are foolish!"

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

  Scenario: Test the interview "Optional override of question"
    Given I start the interview "docassemble.base:data/questions/examples/fallback2.yml"
    Then I should see the phrase "Nice evening, isn’t it?"
    And I click the button "Yes"
    Then I should see the phrase "I forgot, did we already agree to go to the dance together?"
    And I click the button "Yes"
    Then I should see the phrase "That is splendid news!"

  Scenario: Test the interview "Optional override of question" version one
    Given I start the interview "docassemble.base:data/questions/examples/fallback.yml"    
    Then I should see the phrase "Nice evening, isn’t it?"
    And I click the button "Yes"
    Then I should see the phrase "Which of these statements is true?"
    And I click the option "I am old-fashioned"
    And I click the button "Continue"
    Then I should see the phrase "My darling, would you do me the honor of accompanying me to the dance this fine evening?"
    And I click the button "Yes"
    Then I should see the phrase "That is splendid news!"
    
  Scenario: Test the interview "Optional override of question" version one
    Given I start the interview "docassemble.base:data/questions/examples/fallback.yml"    
    Then I should see the phrase "Nice evening, isn’t it?"
    And I click the button "Yes"
    Then I should see the phrase "Which of these statements is true?"
    And I click the option "I am old-fashioned"
    And I click the button "Continue"
    Then I should see the phrase "My darling, would you do me the honor of accompanying me to the dance this fine evening?"
    And I click the button "Yes"
    Then I should see the phrase "That is splendid news!"
    
  Scenario: Test the interview "Optional override of question" version two
    Given I start the interview "docassemble.base:data/questions/examples/fallback.yml"    
    Then I should see the phrase "Nice evening, isn’t it?"
    And I click the button "Yes"
    Then I should see the phrase "Which of these statements is true?"
    And I click the option "I don’t care for flowerly language"
    And I click the button "Continue"
    Then I should see the phrase "Interested in going to the dance tonight?"
    And I click the button "Yes"
    Then I should see the phrase "That is splendid news!"

  Scenario: Test the interview "Checkbox method"
    Given I start the interview "docassemble.base:data/questions/examples/false-values.yml"
    Then I should see the phrase "Please tell me what you think."
    And I click the option "Apples"
    And I click the option "Peaches"
    And I click the button "Continue"
    Then I should see the phrase "You do not like Pears and Plums."

  Scenario: Test the interview "Note among fields"
    Given I start the interview "docassemble.base:data/questions/examples/field-note.yml"
    Then I should see the phrase "Tell me more about you."
    And I set "Favorite fruit" to "melon"
    And I set "Favorite vegetable" to "carrots"
    Then I should see the phrase "I understand that this next question is particularly difficult to answer, but please bear with me. We are almost done."
    And I set "Favorite tree" to "maple"
    And I click the button "Continue"
    Then I should see the phrase "If a maple falls in the forest, and there is no melon to hear it, would you eat carrots?"

  Scenario: Test the interview "Checkboxes with code"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-code.yml"
    Then I should see the phrase "Please tell me what you think."
    And I click the "Pears" option
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like pears."
    And I should see the phrase "Your favorite, though, is mango."

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-0.yml"
    Then I should see the phrase "Please tell me what you think."
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like pears."

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-1.yml"
    Then I should see the phrase "Please tell me what you think."
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should see the phrase "You like pears."

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-2.yml"
    Then I should see the phrase "Please tell me what you think."
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should see the phrase "You like pears."

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-3.yml"
    Then I should see the phrase "Please tell me what you think."
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should see the phrase "You like pears."

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-4.yml"
    Then I should see the phrase "Please tell me what you think."
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-5.yml"
    Then I should see the phrase "Please tell me what you think."
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-default-6.yml"
    Then I should see the phrase "Please tell me what you think."
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."

  Scenario: Test the interview "Checkboxes with different labels"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-different-labels.yml"
    Then I should see the phrase "Please tell me what you think."
    And I click the "Apples" option
    And I click the "Pears" option
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should see the phrase "You like pears."
    And I should see the phrase "'pear': True"
    And I should see the phrase "'apple': True"
    And I should see the phrase "'peach': False"

  Scenario: Test the interview "None of the above off"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-nota-false.yml"
    Then I should see the phrase "Please tell me what you think."
    And I should not see the phrase "None of the above"
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "'Peaches': False"
    And I should see the phrase "'Apples': False"
    And I should see the phrase "'Pears': False"

  Scenario: Test the interview "None of the above default"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes-nota.yml"
    Then I should see the phrase "Please tell me what you think."
    And I click the option "None of the above"
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "'Peaches': False"
    And I should see the phrase "'Apples': False"
    And I should see the phrase "'Pears': False"

  Scenario: Test the interview "Checkboxes within fields"
    Given I start the interview "docassemble.base:data/questions/examples/fields-checkboxes.yml"
    Then I should see the phrase "Please tell me what you think."
    And I click the "Apples" option
    And I click the "Pears" option
    And I set "What is your favorite fruit overall?" to "mango"
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should see the phrase "You like pears."
    And I should see the phrase "'apple': True"
    And I should see the phrase "'peach': False"
    And I should see the phrase "'pear': True"

  # Scenario: Test the interview "Combobox within fields"
  #   Given I start the interview "docassemble.base:data/questions/examples/fields-choices-combobox.yml"

  Scenario: Test the interview "Multiple choice pulldown"
    Given I start the interview "docassemble.base:data/questions/examples/fields-choices-dropdown.yml"
    And I select "Clogs" as the "Shoe Type"
    And I click the button "Continue"
    Then I should see the phrase "target_variable is: “Clogs”"

  Scenario: Test the interview "Multiple choice pulldown"
    Given I start the interview "docassemble.base:data/questions/examples/fields-choices.yml"
    And I select "Apples" as the "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the apple, which is the king of all fruits."    

  Scenario: Test the interview "Multiple choice with code"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-2.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the "Pears" option
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the "Oranges" option
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the pear, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the orange."

  Scenario: Test the interview "Multiple choice with code"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-3.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the "Pears" option
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the "Oranges" option
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the Pears, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the Oranges."

  Scenario: Test the interview "Multiple choice with code"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-4.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the "Pears" option
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the "Oranges" option
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the pear, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the orange."

  Scenario: Test the interview "Multiple choice with code and default"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-5.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the orange, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the orange."

  Scenario: Test the interview "Multiple choice with code and help"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-6.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the "Apples" option
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the "Oranges" option
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the apple, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the orange."    

  Scenario: Test the interview "Multiple choice with code and default"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-7.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the apple, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the apple."

  Scenario: Test the interview "Multiple choice with default and help"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-8.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the apple, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the apple."

  Scenario: Test the interview "With exclusion"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-exclude-manual.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the option "Apples" under "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "Your brother, who is not so wise, is partial to the None."

  Scenario: Test the interview "With exclusion"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-exclude.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the option "Apples" under "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit, assuming he does not like apple?"
    And I should not see the phrase "Apples"
    And I click the option "Oranges" under "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the apple, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the orange."

  Scenario: Test the interview "None of the above customized"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-nota.yml"
    Then I should see the phrase "Please fill in the following information."
    And I click the button "Continue"
    Then I should see the phrase "Please select one"
    And I click the option "Sunroof" under "Requested options"
    And I click the option "Automatic transmission" under "Requested options"
    And I click the option "Heated seats" under "Requested options"
    And I click the option "Nothing at all" under "Requested options"
    And I click the button "Continue"
    Then I should see the phrase "'Heated seats': False"
    And I should see the phrase "'Automatic transmission': False"
    And I should see the phrase "'Sunroof': False"

  Scenario: Test the interview "Conditionally show"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc-with-showif.yml"
    Then I should see the phrase "Please fill in the following information."
    And I should not see the phrase "What’s your favorite fruit?"
    And I should not see the phrase "Options"
    And I click the "Yes" option under "Do you like fruit?"
    Then I should see the phrase "What’s your favorite fruit?"
    And I should see the phrase "Options"

  Scenario: Test the interview "Multiple choice with code"
    Given I start the interview "docassemble.base:data/questions/examples/fields-mc.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the "Apples" option under "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "What is your brother’s favorite fruit?"
    And I click the "Oranges" option under "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is the apple, which is the king of all fruits."
    And I should see the phrase "Your brother, who is not so wise, is partial to the orange."

  Scenario: Test the interview "Yes/no/maybe within fields (reversed)" with yes
    Given I start the interview "docassemble.base:data/questions/examples/fields-noyesmaybe.yml"
    Then I should see the phrase "Please answer the following question."
    And I click the "Yes" option under "Was Washington the first U.S. president?"
    And I click the button "Continue"
    Then I should see the phrase "You were correct that Washington was the first President."
    
  Scenario: Test the interview "Yes/no/maybe within fields (reversed)" with no
    Given I start the interview "docassemble.base:data/questions/examples/fields-noyesmaybe.yml"
    Then I should see the phrase "Please answer the following question."
    And I click the "No" option under "Was Washington the first U.S. president?"
    And I click the button "Continue"
    Then I should see the phrase "You fool, of course Washington was the first president!"
    
  Scenario: Test the interview "Yes/no/maybe within fields (reversed)" with I don't know
    Given I start the interview "docassemble.base:data/questions/examples/fields-noyesmaybe.yml"
    Then I should see the phrase "Please answer the following question."
    And I click the "I don’t know" option under "Was Washington the first U.S. president?"
    And I click the button "Continue"
    Then I should see the phrase "Don’t you know anything about your U.S. presidents?"

  Scenario: Test the interview "Yes/no/maybe within fields" with yes
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnomaybe.yml"
    Then I should see the phrase "Please answer the following question."
    And I click the "No" option under "Is Topeka the capital of Kansas?"
    And I click the button "Continue"
    Then I should see the phrase "Actually, Topeka is the capital of Kansas."

  Scenario: Test the interview "Yes/no/maybe within fields" with don't know
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnomaybe.yml"
    Then I should see the phrase "Please answer the following question."
    And I click the "I don’t know" option under "Is Topeka the capital of Kansas?"
    And I click the button "Continue"
    Then I should see the phrase "You should know your state capitals!"

  Scenario: Test the interview "Yes/no radio buttons" with apricots
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnoradio.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the "Yes" option under "Do you like apricots?"
    And I click the "No" option under "Do you like pineapple?"
    And I click the button "Continue"
    Then I should see the phrase "You like apricots."
    Then I should see the phrase "You do not like pineapple."

  Scenario: Test the interview "Yes/no radio buttons" with pineapple
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnoradio.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the "No" option under "Do you like apricots?"
    And I click the "Yes" option under "Do you like pineapple?"
    And I click the button "Continue"
    Then I should not see the phrase "You like apricots."
    Then I should not see the phrase "You do not like pineapple."

  Scenario: Test the interview "Yes/no radio buttons" with apricots and pineapple
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnoradio.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the "Yes" option under "Do you like apricots?"
    And I click the "Yes" option under "Do you like pineapple?"
    And I click the button "Continue"
    Then I should see the phrase "You like apricots."
    Then I should not see the phrase "You do not like pineapple."

  Scenario: Test the interview "Yes/no radio buttons" with neither apricots nor pineapple
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnoradio.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the "No" option under "Do you like apricots?"
    And I click the "No" option under "Do you like pineapple?"
    And I click the button "Continue"
    Then I should not see the phrase "You like apricots."
    Then I should see the phrase "You do not like pineapple."

  Scenario: Test the interview "Yes/no checkboxes with None of the above"
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno-uncheck-others-list.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the button "Continue"
    Then I should see the phrase 'Check at least one option, or check "Neither"'
    And I should see the phrase 'Check at least one option, or check "I do not like these rocks"'
    And I click the "Apples" option
    And I click the "Obsidian" option
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should see the phrase "You like obsidian."
    
  Scenario: Test the interview "Yes/no checkboxes with None of the above" with nota checked
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno-uncheck-others-list.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the "Apples" option
    And I click the "Neither" option
    And I click the "Obsidian" option
    And I click the "I do not like these rocks" option
    And I click the button "Continue"
    Then I should see the phrase "Thank you for that information."
    And I should not see the phrase "You like apples."
    And I should not see the phrase "You like obsidian."    

  Scenario: Test the interview "Yes/no checkboxes with None of the above"
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno-uncheck-others.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the "Apples" option
    And I click the button "Continue"
    Then I should see the phrase "Thank you for that information."
    And I should see the phrase "You like apples."

  Scenario: Test the interview "Yes/no checkboxes with None of the above" with neither
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno-uncheck-others.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the "Apples" option
    And I click the "Neither" option
    And I click the button "Continue"
    Then I should see the phrase "Thank you for that information."
    And I should not see the phrase "You like apples."

  Scenario: Test the interview "Yes/no checkboxes (wide)" with peaches
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnowide.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the "Peaches" option
    And I click the button "Continue"
    Then I should see the phrase "You like peaches."
    And I should see the phrase "You dislike pears."

  Scenario: Test the interview "Yes/no checkboxes (wide)" with pears
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnowide.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the "Pears" option
    And I click the button "Continue"
    Then I should not see the phrase "You like peaches."
    And I should not see the phrase "You dislike pears."

  Scenario: Test the interview "Yes/no checkboxes (wide)" with peaches and pears
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnowide.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the "Peaches" option
    And I click the "Pears" option
    And I click the button "Continue"
    Then I should see the phrase "You like peaches."
    And I should not see the phrase "You dislike pears."

  Scenario: Test the interview "Yes/no checkboxes (wide)" with neither peaches nor pears
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesnowide.yml"
    Then I should see the phrase "Please provide the following information."
    And I click the button "Continue"
    Then I should not see the phrase "You like peaches."
    And I should see the phrase "You dislike pears."

  Scenario: Test the interview "Yes/no checkboxes" with apples
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the "Apples" option
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should see the phrase "You do not like turnips."

  Scenario: Test the interview "Yes/no checkboxes" with turnips
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the "Turnips" option
    And I click the button "Continue"
    Then I should not see the phrase "You like apples."
    And I should not see the phrase "You do not like turnips."

  Scenario: Test the interview "Yes/no checkboxes" with apples and turnips
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the "Apples" option
    And I click the "Turnips" option
    And I click the button "Continue"
    Then I should see the phrase "You like apples."
    And I should not see the phrase "You do not like turnips."

  Scenario: Test the interview "Yes/no checkboxes" without apples or turnips
    Given I start the interview "docassemble.base:data/questions/examples/fields-yesno.yml"
    Then I should see the phrase "Please provide the following information."
    And I set "What is your favorite food?" to "apple pie"
    And I click the button "Continue"
    Then I should not see the phrase "You like apples."
    And I should see the phrase "You do not like turnips."

  Scenario: Test the interview "Fields example"
    Given I start the interview "docassemble.base:data/questions/examples/fields.yml"
    And I set "Description" to "five foot two, eyes of blue"
    And I set "Annual income" to "50001"
    And I set "E-mail address" to "turnip@vegetable.com"
    And I click the "Been vaccinated" option
    And I click the "Seen Mount Rushmore" option
    And I click the "Outie" option under "Belly button type"
    And I click the "One" option under "Number of friends"
    And I click the "College" option under "Degrees obtained"
    And I select "Alabama" as the "State you grew up in"
    And I click the "Independent" option under "Party"
    And I click the button "Continue"
    Then I should see the phrase "All done"
    And I should see the phrase "Your income is 50001.0."

  Scenario: Test the interview "End-of-sentence punctuation" with no period
    Given I start the interview "docassemble.base:data/questions/examples/fix-punctuation.yml"
    And I set the text area to "The other side is evil"
    And I click the button "Continue"
    Then I should see the phrase "Tell the court, “Please grant my petition. The other side is evil.”"

  Scenario: Test the interview "End-of-sentence punctuation" with period
    Given I start the interview "docassemble.base:data/questions/examples/fix-punctuation.yml"
    And I set the text area to "The other side is stupid."
    And I click the button "Continue"
    Then I should see the phrase "Tell the court, “Please grant my petition. The other side is stupid.”"

  # Scenario: Test the interview "Flushleft"
  #   Given I start the interview "docassemble.base:data/questions/examples/flushleft.yml"

  # Scenario: Test the interview "Flushright"
  #   Given I start the interview "docassemble.base:data/questions/examples/flushright.yml"

  Scenario: Test the interview "Force asking a question" part 1
    Given I start the interview "docassemble.base:data/questions/examples/force-ask-full.yml"
    Then I should see the phrase "Are you a communist?"
    And I click the button "Yes"
    Then I should see the phrase "I suggest you reconsider your answer."
    And I click the button "Continue"
    Then I should see the phrase "Are you a communist?"
    And I click the button "Yes"
    Then I should see the phrase "I am referring your case to Mr. McCarthy."

  Scenario: Test the interview "Force asking a question" part 2
    Given I start the interview "docassemble.base:data/questions/examples/force-ask-full.yml"
    Then I should see the phrase "Are you a communist?"
    And I click the button "Yes"
    Then I should see the phrase "I suggest you reconsider your answer."
    And I click the button "Continue"
    Then I should see the phrase "Are you a communist?"
    And I click the button "No"
    Then I should see the phrase "I am glad you are a true American."

  Scenario: Test the interview "Force asking several questions"
    Given I start the interview "docassemble.base:data/questions/examples/force-ask-multiple.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I set "Favorite fruit" to "apples"
    And I click the button "Continue"
    Then I should see the phrase "What is your favorite vegetable?"
    And I set "Favorite vegetable" to "turnips"
    And I click the button "Continue"
    Then I should see the phrase "What is your favorite fungus?"
    And I set "Favorite" to "button mushrooms"
    And I click the button "Continue"
    Then I should see the phrase "Please verify your answers."
    And I click the button "Continue"
    Then I should see the phrase "What is your favorite fruit?"
    And I click the button "Continue"
    Then I should see the phrase "What is your favorite vegetable?"
    And I click the button "Continue"
    Then I should see the phrase "What is your favorite fungus?"
    And I click the button "Continue"
    Then I should see the phrase "You like apples, turnips, and button mushrooms."

  Scenario: Test the interview "Force asking a question"
    Given I start the interview "docassemble.base:data/questions/examples/force-ask.yml"
    Then I should see the phrase "Are you a communist?"
    And I click the button "Yes"
    Then I should see the phrase "I suggest you reconsider your answer."
    And I click the button "Continue"
    Then I should see the phrase "Are you a communist?"
    And I click the button "Yes"
    Then I should see the phrase "I am referring your case to Mr. McCarthy."

  Scenario: Test the interview "Insist question be asked"
    Given I start the interview "docassemble.base:data/questions/examples/force-gather.yml"
    Then I should see the phrase "All done with the interview!"
    And I click the link "Ask about food"
    Then I should see the phrase "What is your favorite food?"
    And I click the "Something else" option
    And I click the button "Continue"
    Then I should see the phrase "Ok, are any of these your favorite food?"
    And I click the "Something else" option
    And I click the button "Continue"
    Then I should see the phrase "I give up. Just tell me your favorite food."
    And I set "Favorite food" to "cake"
    And I click the button "Continue"
    Then I should see the phrase "All done with the interview!"

  Scenario: Test the interview "Simple for loop"
    Given I start the interview "docassemble.base:data/questions/examples/for_fruit.yml"
    Then I should see the phrase "I assume you like peaches. I assume you like pears. I assume you like apricots."

  # Scenario: Test the interview "Miscellaneous formatting"
  #   Given I start the interview "docassemble.base:data/questions/examples/formatting.yml"

  Scenario: Test the interview "Forward chaining"
    Given I start the interview "docassemble.base:data/questions/examples/forward-chaining.yml"
    Then I should see the phrase "George is green"

  # Scenario: Test the interview "Fill fields with Mako"
  #   Given I start the interview "docassemble.base:data/questions/examples/fruit-template-alt-1.yml"

  # Scenario: Test the interview "Fill fields with variables"
  #   Given I start the interview "docassemble.base:data/questions/examples/fruit-template-alt-2.yml"

  Scenario: Test the interview "Function"
    Given I start the interview "docassemble.base:data/questions/examples/function.yml"
    Then I should see the phrase "The word green becomes Green when passed through the capitalize() function."

  Scenario: Test the interview "Gather"
    Given I start the interview "docassemble.base:data/questions/examples/gather-another.yml"
    Then I should see the phrase "What’s the first fruit?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "Are there more fruits?"
    And I click the button "Yes"
    Then I should see the phrase "What’s the second fruit?"
    And I set "Fruit" to "orange"
    And I click the button "Continue"
    Then I should see the phrase "Are there more fruits?"
    And I click the button "Yes"
    Then I should see the phrase "What’s the third fruit?"
    And I set "Fruit" to "pear"
    And I click the button "Continue"
    Then I should see the phrase "Are there more fruits?"
    And I click the button "No"
    Then I should see the phrase "apple"
    And I should see the phrase "orange"
    And I should see the phrase "pear"

  Scenario: Test the interview "Dictionary: ask number"
    Given I start the interview "docassemble.base:data/questions/examples/gather-dict-number.yml"
    Then I should see the phrase "How many fruit should be added to the database?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "What fruit should be added to the database?"
    And I set "Fruit" to "peach"
    And I click the button "Continue"
    Then I should see the phrase "How many seeds does a peach have?"
    And I set "Number of seeds" to "1"
    And I click the button "Continue"
    Then I should see the phrase "What fruit should be added to the database?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "How many seeds does an apple have?"
    And I set "Number of seeds" to "10"
    And I click the button "Continue"
    Then I should see the phrase "There are two fruits in all."
    And I should see the phrase "The fruit apple has 10 seeds."
    And I should see the phrase "The fruit peach has 1 seeds."

  Scenario: Test the interview "Dictionary: gather keys, objects"
    Given I start the interview "docassemble.base:data/questions/examples/gather-dict-object.yml"
    Then I should see the phrase "Do you have any pets?"
    And I click the button "Yes"
    Then I should see the phrase "What kind of pet do you have?"
    And I set "Type of pet" to "rabbit"
    And I click the button "Continue"
    Then I should see the phrase "So far, you have told me about your rabbit. Do you have any other pets?"
    And I click the button "Yes"
    Then I should see the phrase "What kind of pet do you have?"
    And I set "Type of pet" to "worm"
    And I click the button "Continue"
    Then I should see the phrase "So far, you have told me about your rabbit and worm. Do you have any other pets?"
    And I click the button "No"
    Then I should see the phrase "Describe your pet"
    And I set "Name" to "Freddy"
    And I set "Number of feet" to "3"
    And I click the button "Continue"
    Then I should see the phrase "Describe your pet"
    And I set "Name" to "Buddy"
    And I set "Number of feet" to "2"
    And I click the button "Continue"
    Then I should see the phrase "You have two pets."

  Scenario: Test the interview "Dictionary: gather keys, values"
    Given I start the interview "docassemble.base:data/questions/examples/gather-dict-value.yml"    
    Then I should see the phrase "What fruit should be added to the database?"
    And I set "Fruit" to "peach"
    And I set "Number of seeds" to "1"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits in the database include peach. Are there any others?"
    And I click the button "Yes"
    Then I should see the phrase "What fruit should be added to the database?"
    And I set "Fruit" to "apple"
    And I set "Number of seeds" to "10"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits in the database include apple and peach. Are there any others?"
    And I click the button "No"
    Then I should see the phrase "There are two fruits in all."
    And I should see the phrase "The fruit apple has 10 seeds."
    And I should see the phrase "The fruit peach has 1 seeds."

  Scenario: Test the interview "Dictionary: gather keys, values"
    Given I start the interview "docassemble.base:data/questions/examples/gather-dict.yml"
    Then I should see the phrase "What fruit should be added to the database?"
    And I set "Fruit" to "peach"
    And I click the button "Continue"
    Then I should see the phrase "How many seeds does a peach have?"
    And I set "Number of seeds" to "1"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits in the database include peach. Are there any others?"
    And I click the button "Yes"
    Then I should see the phrase "What fruit should be added to the database?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "How many seeds does an apple have?"
    And I set "Number of seeds" to "10"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits in the database include apple and peach. Are there any others?"
    And I click the button "No"
    Then I should see the phrase "There are two fruits in all."
    And I should see the phrase "The fruit apple has 10 seeds."
    And I should see the phrase "The fruit peach has 1 seeds."

  Scenario: Test the interview "List: gather with minimum number"
    Given I start the interview "docassemble.base:data/questions/examples/gather-fruit-at-least-two.yml"
    Then I should see the phrase "What is the first fruit?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "What is the second fruit?"
    And I set "Fruit" to "peach"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits include apple and peach. Are there any others?"
    And I click the button "Yes"
    Then I should see the phrase "What is the third fruit?"
    And I set "Fruit" to "pear"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits include apple, peach, and pear. Are there any others?"
    And I click the button "No"
    Then I should see the phrase "There are three fruits in all."
    And I should see the phrase "The fruits are apple, peach, and pear."

  Scenario: Test the interview "List: the .gather method"
    Given I start the interview "docassemble.base:data/questions/examples/gather-fruit-gather.yml"
    Then I should see the phrase "What fruit should be added to the list?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits include apple. Are there any others?"
    And I click the button "Yes"
    Then I should see the phrase "What fruit should be added to the list?"
    And I set "Fruit" to "orange"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits include apple and orange. Are there any others?"
    And I click the button "No"
    Then I should see the phrase "The fruits are apple and orange."

  Scenario: Test the interview "List: gather by total number"
    Given I start the interview "docassemble.base:data/questions/examples/gather-fruit-number.yml"
    Then I should see the phrase "How many fruits are there?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "What is the name of the first fruit?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "What is the name of the second fruit?"
    And I should see the phrase "So far, you have mentioned apple."
    And I set "Fruit" to "orange"
    And I click the button "Continue"
    Then I should see the phrase "There are 2 fruits in all."
    And I should see the phrase "The fruits are apple and orange."

  Scenario: Test the interview "List: gathering"
    Given I start the interview "docassemble.base:data/questions/examples/gather-fruit.yml"
    Then I should see the phrase "Are there any fruit that you would like to add to the list?"
    And I click the button "Yes"
    Then I should see the phrase "What fruit should be added to the list?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits include apple. Are there any others?"
    And I click the button "Yes"
    Then I should see the phrase "What fruit should be added to the list?"
    And I set "Fruit" to "orange"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits include apple and orange. Are there any others?"
    And I click the button "No"
    Then I should see the phrase "There are two fruits in all."
    And I should see the phrase "The fruits are apple and orange."

  Scenario: Test the interview "Gathering a list of e-mail recipients"
    Given I start the interview "docassemble.base:data/questions/examples/gather-list-email-recipients.yml"
    Then I should see the phrase "What is the first e-mail address?"
    And I set "E-mail" to "fred@docassemble.org"
    And I click the button "Continue"
    Then I should see the phrase "Would you like to add another e-mail recipient?"
    And I click the button "Yes"
    Then I should see the phrase "What is the second e-mail address?"
    And I set "E-mail" to "sally@docassemble.org"
    And I click the button "Continue"
    Then I should see the phrase "Would you like to add another e-mail recipient?"
    And I click the button "No"
    Then I should see the phrase "The list of recipients"
    And I should see the phrase "fred@docassemble.org"
    And I should see the phrase "sally@docassemble.org"

  Scenario: Test the interview "Gathering a list of people"
    Given I start the interview "docassemble.base:data/questions/examples/gather-list-friend-bad-order.yml"
    Then I should see the phrase "What is the name of your first friend?"
    And I set "First Name" to "Fred"
    And I click the button "Continue"
    Then I should see the phrase "Do you have any other friends?"
    And I click the button "Yes"
    Then I should see the phrase "What is the name of your second friend?"
    And I set "First Name" to "Sally"
    And I click the button "Continue"
    Then I should see the phrase "Do you have any other friends?"
    And I click the button "No"
    Then I should see the phrase "What is Fred’s favorite animal?"
    And I set "Favorite animal" to "toad"
    And I click the button "Continue"
    Then I should see the phrase "What is Fred’s birthdate?"
    And I set "Birthdate" to "3/1/2000"
    And I click the button "Continue"
    Then I should see the phrase "What is Sally’s favorite animal?"
    And I set "Favorite animal" to "frog"
    And I click the button "Continue"
    Then I should see the phrase "What is Sally’s birthdate?"
    And I set "Birthdate" to "6/4/2003"
    And I click the button "Continue"
    Then I should see the phrase "Your friends"
    And I should see the phrase "Fred likes toads and is"
    And I should see the phrase "Sally likes frogs and is"

  Scenario: Test the interview "Gathering a list of people"
    Given I start the interview "docassemble.base:data/questions/examples/gather-list-friend-good-order.yml"
    Then I should see the phrase "What is the name of your first friend?"
    And I set "First Name" to "Fred"
    And I click the button "Continue"
    Then I should see the phrase "What is Fred’s birthdate?"
    And I set "Birthdate" to "3/1/2000"
    And I click the button "Continue"
    Then I should see the phrase "What is Fred’s favorite animal?"
    And I set "Favorite animal" to "toad"
    And I click the button "Continue"
    Then I should see the phrase "Do you have any other friends?"
    And I click the button "Yes"
    Then I should see the phrase "What is the name of your second friend?"
    And I set "First Name" to "Sally"
    And I click the button "Continue"
    Then I should see the phrase "What is Sally’s birthdate?"
    And I set "Birthdate" to "6/4/2003"
    And I click the button "Continue"
    Then I should see the phrase "What is Sally’s favorite animal?"
    And I set "Favorite animal" to "frog"
    And I click the button "Continue"
    Then I should see the phrase "Do you have any other friends?"
    And I click the button "No"
    Then I should see the phrase "Your friends"
    And I should see the phrase "Fred likes toads and is"
    And I should see the phrase "Sally likes frogs and is"

  Scenario: Test the interview "Gathering a list of objects"
    Given I start the interview "docassemble.base:data/questions/examples/gather-list-objects.yml"
    Then I should see the phrase "What is the address of the first location?"
    And I set "Address" to "123 Main St"
    And I set "City" to "Springfield"
    And I select "Georgia" as the "State"
    And I click the button "Continue"
    Then I should see the phrase "Would you like to add another location?"
    And I click the button "Yes"
    Then I should see the phrase "What is the address of the second location?"
    And I set "Address" to "432 Elm St"
    And I set "City" to "Oak Grove"
    And I select "Louisiana" as the "State"
    And I click the button "Continue"
    Then I should see the phrase "Would you like to add another location?"
    And I click the button "No"
    Then I should see the phrase "The locations"
    And I should see the phrase "432 Elm St"
    And I should see the phrase "123 Main St"

  Scenario: Test the interview "List: gathering other attributes"
    Given I start the interview "docassemble.base:data/questions/examples/gather-manual-gathered-object-simple.yml"
    Then I should see the phrase "Do you know about any fruit?"
    And I click the button "Yes"
    Then I should see the phrase "Tell me about the first fruit."
    And I set "Name" to "apple"
    And I set "Seeds" to "10"
    And I click the button "Continue"
    Then I should see the phrase "Do you know about any other fruit?"
    And I click the button "Yes"
    Then I should see the phrase "Tell me about another fruit."
    And I set "Name" to "pear"
    And I set "Seeds" to "0"
    And I click the button "Continue"
    Then I should see the phrase "Do you know about any other fruit?"
    And I click the button "No"
    Then I should see the phrase "Your knowledge of fruit."
    And I should see the phrase "apple has 10 seeds."
    And I should see the phrase "pear has 0 seeds."

  Scenario: Test the interview "List: gathering other attributes"
    Given I start the interview "docassemble.base:data/questions/examples/gather-manual-gathered-object.yml"
    Then I should see the phrase "Do you know about any fruit?"
    And I click the button "Yes"
    Then I should see the phrase "Tell me about the first fruit."
    And I set "Name" to "apple"
    And I set "Seeds" to "10"
    And I click the button "Continue"
    Then I should see the phrase "Do you know about any other fruit?"
    And I click the button "Yes"
    Then I should see the phrase "Tell me about another fruit."
    And I set "Name" to "pear"
    And I set "Seeds" to "0"
    And I click the button "Continue"
    Then I should see the phrase "Do you know about any other fruit?"
    And I click the button "No"

  Scenario: Test the interview "List: .auto_gather and .gathered"
    Given I start the interview "docassemble.base:data/questions/examples/gather-manual-gathered.yml"
    Then I should see the phrase "The fruits are apple, orange, and grape."

  Scenario: Test the interview "Set: gathering"
    Given I start the interview "docassemble.base:data/questions/examples/gather-set-number.yml"
    Then I should see the phrase "How many fruit should be added to the set?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "What fruit should be added to the set?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "What fruit should be added to the set?"
    And I set "Fruit" to "orange"
    And I click the button "Continue"
    Then I should see the phrase "There are two fruits in all."
    And I should see the phrase "The fruit include apple and orange."

  Scenario: Test the interview "Set: gather objects"
    Given I start the interview "docassemble.base:data/questions/examples/gather-set-object.yml"
    Then I should see the phrase "Do you like apples, oranges, pears, plums, or grapes?"
    And I click the button "Yes"
    Then I should see the phrase "Pick a fruit that you like."
    And I select "apples" as the "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "So far, you have indicated you like apples. Are there any other fruits you like?"
    And I click the button "Yes"
    Then I should see the phrase "Pick a fruit that you like."
    And I select "pears" as the "Fruit"
    And I click the button "Continue"
    Then I should see the phrase "So far, you have indicated you like apples and pears. Are there any other fruits you like?"
    And I click the button "No"
    Then I should see the phrase "There are two fruits in all."
    And I should see the phrase "The fruits you like include apples and pears."
    And I should see the phrase "The fruits we both like are apples and pears."

  Scenario: Test the interview "Set: gather values"
    Given I start the interview "docassemble.base:data/questions/examples/gather-set.yml"
    Then I should see the phrase "Should there be any fruits in the set?"
    And I click the button "Yes"
    Then I should see the phrase "What fruit should be added to the set?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits in the set include apple. Are there any others?"
    And I click the button "Yes"
    Then I should see the phrase "What fruit should be added to the set?"
    And I set "Fruit" to "pear"
    And I click the button "Continue"
    Then I should see the phrase "So far, the fruits in the set include apple and pear. Are there any others?"
    And I click the button "No"
    Then I should see the phrase "There are two fruits in all."
    And I should see the phrase "The fruit include apple and pear."

  Scenario: Test the interview "Gather"
    Given I start the interview "docassemble.base:data/questions/examples/gather-simple.yml"
    Then I should see the phrase "How many fruits are there?"
    And I set "Number" to "2"
    And I click the button "Continue"
    Then I should see the phrase "What’s the first fruit?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "What’s the second fruit?"
    And I set "Fruit" to "pear"
    And I click the button "Continue"
    Then I should see the phrase "Fruits"
    And I should see the phrase "The fruits are:"
    And I should see the phrase "apple"
    And I should see the phrase "pear"

  Scenario: Test the interview "Generic object fallback"
    Given I start the interview "docassemble.base:data/questions/examples/generic-object-ein.yml"
    Then I should see the phrase "What is the tax status of ABC Incorporated?"
    And I click the "Non-profit" option
    And I click the button "Continue"
    Then I should see the phrase "What is the tax status of XYZ Incorporated?"
    And I click the "For-profit" option
    And I click the button "Continue"
    Then I should see the phrase "What is the EIN of XYZ Incorporated?"
    And I set "EIN" to "98-23423423"
    And I click the button "Continue"
    Then I should see the phrase "Summary"
    And I should see the phrase "ABC Incorporated is a non-profit. Its EIN is 54-54349343."
    And I should see the phrase "XYZ Incorporated is not a non-profit. Its EIN is 98-23423423."
   
  Scenario: Test the interview "generic objects"
    Given I start the interview "docassemble.base:data/questions/examples/generic-object-phone-number.yml"
    Then I should see the phrase "What is the grantor’s name?"
    And I set "First Name" to "Graham"
    And I set "Last Name" to "Grantor"
    And I click the button "Continue"
    Then I should see the phrase "What is Graham Grantor’s phone number?"
    And I set "Phone Number" to "202-555-2032"
    And I click the button "Continue"
    Then I should see the phrase "What is the grantee’s name?"
    And I set "First Name" to "George"
    And I set "Last Name" to "Grantee"
    And I click the button "Continue"
    Then I should see the phrase "What is George Grantee’s phone number?"
    And I set "Phone Number" to "202-555-8932"
    And I click the button "Continue"
    Then I should see the phrase "What is the trustee’s name?"
    And I set "First Name" to "Travis"
    And I set "Last Name" to "Trustee"
    And I click the button "Continue"
    Then I should see the phrase "What is Travis Trustee’s phone number?"
    And I set "Phone Number" to "202-555-2544"
    And I click the button "Continue"
    Then I should see the phrase "How to reach people"
    And I should see the phrase "You can reach the grantor at 202-555-2032."
    And I should see the phrase "You can reach the grantee at 202-555-8932."
    And I should see the phrase "You can reach the trustee at 202-555-2544."

  Scenario: Test the interview "Generic object"
    Given I start the interview "docassemble.base:data/questions/examples/generic-object.yml"
    Then I should see the phrase "Does John Smith like cats?"
    And I click the button "Yes"
    Then I should see the phrase "Does Randy Jones like cats?"
    And I click the button "Yes"
    Then I should see the phrase "John Smith and Randy Jones both like cats."

  Scenario: Test the interview "Default timezone"
    Given I start the interview "docassemble.base:data/questions/examples/get-default-timezone.yml"
    Then I should see the phrase "The default time zone is America/New_York."

  Scenario: Test the interview "Not object oriented"
    Given I start the interview "docassemble.base:data/questions/examples/hello-not-oop.yml"
    Then I should see the phrase "What is your name?"
    And I set "First" to "John"
    And I set "Last" to "Smith"
    And I click the button "Continue"
    Then I should see the phrase "Hello, John Smith!"    

  Scenario: Test the interview "Object oriented"
    Given I start the interview "docassemble.base:data/questions/examples/hello-oop.yml"
    Then I should see the phrase "What’s your name?"
    And I set "First" to "John"
    And I set "Last" to "Smith"
    And I click the button "Continue"
    Then I should see the phrase "Hello, John Smith!"    

  # Scenario: Test the interview "Audio help"
  #   Given I start the interview "docassemble.base:data/questions/examples/help-damages-audio.yml"

  Scenario: Test the interview "Help with question"
    Given I start the interview "docassemble.base:data/questions/examples/help-damages.yml"
    Then I should see the phrase "How much money do you wish to seek in damages?"
    And I go to the help screen
    Then I should see the phrase "If you are not sure how much money to seek in damages, just ask for a million dollars, since you want Dastardly Defendant to suffer."
    And I go back to the question screen
    And I set "Money" to "40000"
    And I click the button "Continue"
    Then I should see the phrase "You are seeking $40,000.00 in damages"

  Scenario: Test the interview "Help with question"
    Given I start the interview "docassemble.base:data/questions/examples/help.yml"
    Then I should see the phrase "What is 2+2?"
    And I go to the help screen
    Then I should see the phrase "Hint: 2 + 2 = 4."
    And I go back to the question screen
    And I click the "4" option
    And I click the button "Continue"
    Then I should see the phrase "You are brilliant!"

  Scenario: Test the interview "Conditionally hide" with hiding
    Given I start the interview "docassemble.base:data/questions/examples/hideif-boolean.yml"
    Then I should see the phrase "Please fill in the following information."
    And I should see the phrase "What fruit do you need?"
    And I click the "Yes" option under "Do you have fruit?"
    And I wait 1 second
    And I should not see the phrase "What fruit do you need?"
    And I click the button "Continue"
    Then I should see the phrase "You have fruit."

  Scenario: Test the interview "Conditionally hide" with showing
    Given I start the interview "docassemble.base:data/questions/examples/hideif-boolean.yml"
    Then I should see the phrase "Please fill in the following information."
    And I click the "No" option under "Do you have fruit?"
    And I set "What fruit do you need?" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "You need some apple."

  # Scenario: Test the interview "HTML"
  #   Given I start the interview "docassemble.base:data/questions/examples/html.yml"

  Scenario: Test the interview "Conditional question"
    Given I start the interview "docassemble.base:data/questions/examples/if.yml"
    Then I should see the phrase "Describe your intelligence."e
    And I click the "Smart" option
    And I click the button "Continue"
    Then I should see the phrase "What is the square root of 50% of 32?"
    And I set "Answer" to "4"
    And I click the button "Continue"
    Then I should see the phrase "That is correct."

  Scenario: Test the interview "Images with attribution"
    Given I start the interview "docassemble.base:data/questions/examples/image-sets.yml"
    Then I should see the phrase "Icon made by Freepik"

  # Scenario: Test the interview "Images without attribution"
  #   Given I start the interview "docassemble.base:data/questions/examples/images.yml"

  # Scenario: Test the interview "Immediate file"
  #   Given I start the interview "docassemble.base:data/questions/examples/immediate_file.yml"

  Scenario: Test the interview "Import Python module"
    Given I start the interview "docassemble.base:data/questions/examples/imports.yml"
    Then I should see the phrase "Please write a sentence."
    And I set the text area to "I am a cow."
    And I click the button "Continue"
    Then I should see the phrase "Here is your transformed sentence."
    And I should see the phrase "I am AARGH! cow."

  Scenario: Test the interview "Include YAML file"
    Given I start the interview "docassemble.base:data/questions/examples/include.yml"
    Then I should see the phrase "What is your favorite fruit?"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "What is your favorite vegetable?"
    And I set "Vegetable" to "turnip"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite fruit is apple and your favorite vegetable is turnip."

  Scenario: Test the interview "List of periods"
    Given I start the interview "docassemble.base:data/questions/examples/income.yml"
    Then I should see the phrase "What is your income?"
    And I set "Income" to "5000"
    And I select "Per Week" as the "Period"
    And I click the button "Continue"
    Then I should see the phrase "Your income"
    And I should see the phrase "You earn $260,000.00 per year."

  Scenario: Test the interview "Indefinite article"
    Given I start the interview "docassemble.base:data/questions/examples/indefinite-article.yml"
    Then I should see the phrase "Would you prefer to have an apple as opposed to a squash?"
    And I click the button "Yes"
    Then I should see the phrase "You would prefer the apple"

  Scenario: Test the interview "Indent paragraphs"
    Given I start the interview "docassemble.base:data/questions/examples/indent.yml"
    Then I should see the phrase "Your allegations"
    And I should see the phrase "You have a house."

  Scenario: Test the interview "Index variables"
    Given I start the interview "docassemble.base:data/questions/examples/index-variable.yml"
    Then I should see the phrase "What is the first person’s name?"
    And I set "First" to "Harry"
    And I set "Last" to "Jones"
    And I click the button "Continue"
    Then I should see the phrase "Are there more people involved?"
    And I click the button "Yes"
    Then I should see the phrase "What is the second person’s name?"
    And I set "First" to "Larry"
    And I set "Last" to "Smith"
    And I click the button "Continue"
    Then I should see the phrase "Are there more people involved?"
    And I click the button "No"
    Then I should see the phrase "Harry Jones and Larry Smith"

  Scenario: Test the interview "Infinite loop"
    Given I start the interview "docassemble.base:data/questions/examples/infinite-loop.yml"
    Then I should see the phrase "The variable is foo."

  Scenario: Test the interview "Initial code" with counter on
    Given I start the interview "docassemble.base:data/questions/examples/initial-code.yml"
    Then I should see the phrase "Do you want to turn on the counter?"
    And I click the button "Yes"
    Then I should see the phrase "How many peaches do you have?"
    And I should see the phrase "The value of the counter is 1."
    And I set the text box to "2"
    And I click the button "Continue"
    Then I should see the phrase "How many pears do you have?"
    And I should see the phrase "The value of the counter is 2."
    And I set the text box to "1"
    And I click the button "Continue"
    Then I should see the phrase "You have 3 pieces of fruit."
    And I should see the phrase "The value of the counter is 4."    

  Scenario: Test the interview "Initial code" with counter off
    Given I start the interview "docassemble.base:data/questions/examples/initial-code.yml"
    Then I should see the phrase "Do you want to turn on the counter?"
    And I click the button "No"
    Then I should see the phrase "How many peaches do you have?"
    And I should see the phrase "The value of the counter is 0."
    And I set the text box to "2"
    And I click the button "Continue"
    Then I should see the phrase "How many pears do you have?"
    And I should see the phrase "The value of the counter is 0."
    And I set the text box to "1"
    And I click the button "Continue"
    Then I should see the phrase "You have 3 pieces of fruit."
    And I should see the phrase "The value of the counter is 0."    

  Scenario: Test the interview "Initial code"
    Given I start the interview "docassemble.base:data/questions/examples/initial.yml"
    Then I should see the phrase "How many peaches do you have?"
    And I should see the phrase "The value of the counter is 1."
    And I set the text box to "2"
    And I click the button "Continue"
    Then I should see the phrase "How many pears do you have?"
    And I should see the phrase "The value of the counter is 2."
    And I set the text box to "1"
    And I click the button "Continue"
    Then I should see the phrase "You have 3 pieces of fruit."
    And I should see the phrase "The value of the counter is 4."    

  Scenario: Test the interview "Interface in use"
    Given I start the interview "docassemble.base:data/questions/examples/interface.yml"
    Then I should see the phrase "You are using the web interface."

  Scenario: Test the interview "Interview help"
    Given I start the interview "docassemble.base:data/questions/examples/interview-help.yml"
    Then I should see the phrase "Are you ready to start the interview?"
    And I go to the help screen
    Then I should see the phrase "About this interview"
    And I should see the phrase "Answer each question to the best of your ability. If you do not know the answer to any question, panic."
    And I go back to the question screen
    And I click the button "Yes"
    Then I should see the phrase "This is the end of the interview."
    And I go to the help screen
    Then I should see the phrase "About this interview"
    And I should see the phrase "Answer each question to the best of your ability. If you do not know the answer to any question, panic."

  Scenario: Test the interview "Action from anywhere"
    Given I start the interview "docassemble.base:data/questions/examples/interview_url_action.yml"
    Then I should see the phrase "The current status is normal."
  #   And I click the link "danger"
  #   Then I should see the phrase "The current status is danger."
  #   And I click the link "normal"
  #   Then I should see the phrase "The current status is normal."

  Scenario: Test the interview "Several interviews in one" with first interview
    Given I start the interview "docassemble.base:data/questions/examples/interview-url-refer.yml"
    Then I should see the phrase "What interview would you like to use?"
  #  And I click the link "Fruit"
  #  Then I should see the phrase "What is your favorite fruit?"

  # Scenario: Test the interview "Several interviews in one" with second interview
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url-refer.yml"
  #   Then I should see the phrase "What interview would you like to use?"
  #   And I click the link "Vegetables"
  #   Then I should see the phrase "What is your favorite vegetable?"

  # Scenario: Test the interview "Destination interview"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url-session-two.yml"

  # Scenario: Test the interview "Link for sharing"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url-session.yml"

  # Scenario: Test the interview "Link for sharing"
  #   Given I start the interview "docassemble.base:data/questions/examples/interview-url.yml"

  # Scenario: Test the interview "Join from monitor"
  #   Given I start the interview "docassemble.base:data/questions/examples/join.yml"

  Scenario: Test the interview "Calling actions"
    Given I start the interview "docassemble.base:data/questions/examples/js_url_action_call.yml"
    Then I should see the phrase "The pie"
    And I should not see the phrase "The pie is called apple pie."
    And I click the button "Run"
    And I wait 1 second
    Then I should see the phrase "The pie is called apple pie."

  Scenario: Test the interview "Action links"
    Given I start the interview "docassemble.base:data/questions/examples/js_url_action.yml"
    Then I should see the phrase "Your dessert is cod liver oil."
    And I click the link "choose something tastier"
    Then I should see the phrase "Your dessert is apple pie."

  Scenario: Test the interview "Interview variables"
    Given I start the interview "docassemble.base:data/questions/examples/js_variables.yml"
    Then I should see the phrase "The fruit."
    And I wait 1 second
    And I should see the phrase "Fruit is apple."

  Scenario: Test the interview "Separate label and field"
    Given I start the interview "docassemble.base:data/questions/examples/label.yml"
    Then I should see the phrase "What are your favorite things to eat?"
    And I set "Vegetable" to "turnip"
    And I set "Fruit" to "apple"
    And I click the button "Continue"
    Then I should see the phrase "You must love turnip and apple pancakes. I know I do!"

  Scenario: Test the interview "User language from browser (restricted)"
    Given I start the interview "docassemble.base:data/questions/examples/language_from_browser_restricted.yml"
    Then I should see the phrase "I guess you do not speak Spanish or French."

  Scenario: Test the interview "User language from browser"
    Given I start the interview "docassemble.base:data/questions/examples/language_from_browser.yml"
    Then I should see the phrase "I think your language code is en."

  Scenario: Test the interview "Language"
    Given I start the interview "docassemble.base:data/questions/examples/language.yml"
    Then I should see the phrase "What language do you speak?"
    And I click the "Español" option
    And I click the button "Continue"
    Then I should see the phrase "¿Cuál es el significado de la vida?"
    And I set "Significado de la Vida" to "dormir"
    And I click the button "Continuar"
    Then I should see the phrase "The meaning of life"
    And I should see the phrase "The interviewee said the meaning of life is"
    And I should see the phrase "dormir"

  Scenario: Test the interview "The lastfirst method"
    Given I start the interview "docassemble.base:data/questions/examples/lastfirst.yml"
    Then I should see the phrase "Vader, Darth"
    And I should see the phrase "Death Star Corporation"
    And I should see the phrase "Ren, Kylo"

  # Scenario: Test the interview "Command: leave"
  #   Given I start the interview "docassemble.base:data/questions/examples/leave.yml"

  Scenario: Test the interview "Lists"
    Given I start the interview "docassemble.base:data/questions/examples/lists.yml"
    Then I should see the phrase "Your fears"
    Then I should see the phrase "You are afraid of spiders, snakes, and fish."

  # Scenario: Test the interview "Live chat"
  #   Given I start the interview "docassemble.base:data/questions/examples/live_chat.yml"

  Scenario: Test the interview "Loading legal module"
    Given I start the interview "docassemble.base:data/questions/examples/loading-legal.yml"
    Then I should see the phrase "Using legal functions"

  Scenario: Test the interview "Loading"
    Given I start the interview "docassemble.base:data/questions/examples/loading-util.yml"
    Then I should see the phrase "Using utility functions"

  Scenario: Test the interview "Actions"
    Given I start the interview "docassemble.base:data/questions/examples/lucky-number.yml"
    Then I should see the phrase "What is your lucky color?"
    And I set "Color" to "green"
    And I click the button "Continue"
    Then I should see the phrase "Please confirm the following information."
    And I should see the phrase "Your lucky number is 2."
    And I should see the phrase "Also, your lucky color is green."
    And I click the link "Increase"
    And I wait 1 second
    Then I should see the phrase "Your lucky number is 3."
    And I click the link "Decrease"
    And I wait 1 second
    Then I should see the phrase "Your lucky number is 2."
    And I click the link "Edit"
    Then I should see the phrase "What is your lucky color?"
    And I set "Color" to "red"
    And I click the button "Continue"
    Then I should see the phrase "Also, your lucky color is red."

  Scenario: Test the interview "Mad libs"
    Given I start the interview "docassemble.base:data/questions/examples/madlibs.yml"
    Then I should see the phrase "Give me a person."
    And I set the text box to "Sally"
    And I click the button "Continue"
    Then I should see the phrase "Give me a place."
    And I set the text box to "McDonalds"
    And I click the button "Continue"
    Then I should see the phrase "Give me a noun."
    And I set the text box to "turnip"
    And I click the button "Continue"
    Then I should see the phrase "Give me an adjective."
    And I set the text box to "silly"
    And I click the button "Continue"
    Then I should see the phrase "Give me another noun."
    And I set the text box to "shark"
    And I click the button "Continue"
    Then I should see the phrase "Give me another person."
    And I set the text box to "Antonio"
    And I click the button "Continue"
    Then I should see the phrase "A funny story"
    And I should see the phrase "Sally went to McDonalds to buy a turnip."
    And I should see the phrase "At the McDonalds, there was a silly shark, which tried to zap Sally."
    And I should see the phrase "But luckily, Antonio came out of the back room just in time and lunged at the shark, thereby saving the day."

  Scenario: Test the interview "Insert variable"
    Given I start the interview "docassemble.base:data/questions/examples/mako-01.yml"
    Then I should see the phrase "A summary"
    And I should see the phrase "You like apples and potatoes."

  Scenario: Test the interview "If statement"
    Given I start the interview "docassemble.base:data/questions/examples/mako-02.yml"
    Then I should see the phrase "Hello!"
    And I should see the phrase "I hope you are having a good day."

  Scenario: Test the interview "If/else statement"
    Given I start the interview "docassemble.base:data/questions/examples/mako-03.yml"
    Then I should see the phrase "Commentary on the day of the month"
    Then I should see the phrase "Let me tell you about today."

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

  # Scenario: Test the interview "List: mixed object types"
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

  Scenario: Test the interview "Yes means false"
    Given I start the interview "docassemble.base:data/questions/examples/noyes.yml"
    Then I should see the phrase "Are you at least 18 years of age?"
    And I click the button "Yes"
    Then I should see the phrase "user_is_minor is: “False”"

  Scenario: Test the interview "Yes means false" with other possibility
    Given I start the interview "docassemble.base:data/questions/examples/noyes.yml"
    Then I should see the phrase "Are you at least 18 years of age?"
    And I click the button "No"
    Then I should see the phrase "user_is_minor is: “True”"

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

  # Scenario: Test the interview "Today's date"
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

  Scenario: Test the interview "Yes/no/maybe" with yes
    Given I start the interview "docassemble.base:data/questions/examples/yesnomaybe.yml"
    Then I should see the phrase "Is Topeka the capital of Kansas?"
    And I click the button "Yes"
    Then I should see the phrase "You were right that Topeka is the capital of Kansas."

  Scenario: Test the interview "Yes/no/maybe" with no
    Given I start the interview "docassemble.base:data/questions/examples/yesnomaybe.yml"
    Then I should see the phrase "Is Topeka the capital of Kansas?"
    And I click the button "No"
    Then I should see the phrase "Actually, Topeka is the capital of Kansas."

  Scenario: Test the interview "Yes/no/maybe" with maybe
    Given I start the interview "docassemble.base:data/questions/examples/yesnomaybe.yml"
    Then I should see the phrase "Is Topeka the capital of Kansas?"
    And I click the button "I don’t know"
    Then I should see the phrase "You should know your state capitals!"

  Scenario: Test the interview "Yes/no" with yes
    Given I start the interview "docassemble.base:data/questions/examples/yesno.yml"
    Then I should see the phrase "Are you at least 18 years of age?"
    And I click the button "Yes"
    Then I should see the phrase "over_eighteen is: “True”"

  Scenario: Test the interview "Yes/no" with no
    Given I start the interview "docassemble.base:data/questions/examples/yesno.yml"
    Then I should see the phrase "Are you at least 18 years of age?"
    And I click the button "No"
    Then I should see the phrase "over_eighteen is: “False”"

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
