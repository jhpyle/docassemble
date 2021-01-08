Feature: Example interviews
  In order to ensure docassemble is running properly, I want
  to run the example interviews.

  Scenario: Test the interview "Back button inside question"
    Given I start the interview "docassemble.base:data/questions/examples/question-back-button.yml"
    Then I should see the phrase "Are you doing well?"
    And I click the button "Yes"
    Then I should see the phrase "Is the sky blue?"
    And I click the question back button
    Then I should see the phrase "Are you doing well?"

  Scenario: Test the interview "Flash message"
    Given I start the interview "docassemble.base:data/questions/examples/ajax-flash.yml"
    Then I should see the phrase "What is your favorite food?"
    And I set "Favorite food" to "soup"
    And I unfocus
    And I set "Favorite drink" to "water"
    And I unfocus
    And I wait 4 seconds
    Then I should see the phrase "What? You like SOUP?"
    And I click the button "Continue"
    Then I should see the phrase "Your favorite food is soup and your favorite drink is water."

  Scenario: Test the interview "Interview variables"
    Given I start the interview "docassemble.base:data/questions/examples/js_variables.yml"
    And I wait 3 seconds
    Then I should see the phrase "The fruit."
    And I wait 3 seconds
    And I should see the phrase "Fruit is apple."

  Scenario: Test the interview "Checking in"
    Given I start the interview "docassemble.base:data/questions/examples/check-in.yml"
    Then I should see the phrase "What is your favorite food?"
    And I set "Favorite food" to "potatoes"
    And I unfocus
    And I wait 12 seconds
    And I set "Favorite food" to "tomatoes"
    And I unfocus
    And I wait 12 seconds
    And I click the button "Continue"
    Then I should see the phrase "Your favorite food"
    And I should see the phrase "potatoes"
    And I should see the phrase "tomatoes"

  Scenario: Test the interview "Test URL args" with argument
    Given I start the interview "docassemble.demo:data/questions/testurlarg.yml&from=moon"
    Then I should see the phrase "You came from the moon."

  Scenario: Test the interview "Geolocate from address"
    Given I start the interview "docassemble.base:data/questions/examples/geolocate-from-address.yml"
    Then I should see the phrase "Enter an address"
    And I set "Address" to "5901 Broken Sound Pkwy NW, Boca Raton, FL 33487"
    And I click the button "Continue"
    Then I should see the phrase "Information about your address"
    And I should see the phrase "The address is located in Boca Raton."
    And I should see the phrase "The latitude and longitude are 26.4024364 and -80.1167301."

  Scenario: Test the interview "Geolocate address"
    Given I start the interview "docassemble.base:data/questions/examples/geolocate.yml"
    Then I should see the phrase "Enter an address"
    And I set "Address" to "211 S 11th St"
    And I set "City" to "Philadelphia"
    And I select "Pennsylvania" as the "State"
    And I click the button "Continue"
    Then I should see the phrase "Philadelphia, PA 19107"

  Scenario: Test the interview "Normalize address"
    Given I start the interview "docassemble.base:data/questions/examples/normalize.yml"
    Then I should see the phrase "Enter an address"
    And I set "Address" to "211 S 11th St"
    And I set "City" to "Philadelphia"
    And I set "State" to "PA"
    And I click the button "Continue"
    Then I should see the phrase "Philadelphia, PA 19107"

  Scenario: Test the interview "Google Map"
    Given I start the interview "docassemble.demo:data/questions/examples/testgeolocate.yml"
    Then I should see the phrase "Welcome to the map tester"
    And I click the button "Continue"
    Then I should see the phrase "Where do you live?"
    And I set "Address" to "211 S 11th St"
    And I set "City" to "Philadelphia"
    And I select "Pennsylvania" as the "State"
    And I click the button "Continue"
    Then I should see the phrase "What is the enemy’s name?"
    And I set "First Name" to "Emil"
    And I set "Last Name" to "Enemy"
    And I click the button "Continue"
    Then I should see the phrase "Where does Emil Enemy live?"
    And I set "Address" to "4000 Walnut St"
    And I set "City" to "Philadelphia"
    And I select "Pennsylvania" as the "State"
    And I set "Zip" to "19104"
    And I click the button "Continue"
    Then I should see the phrase "Map of you and your enemy"

  # Scenario: Test the interview "Machine learning" 1
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-ajax-classify.yml"

  # Scenario: Test the interview "Suggestions"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-ajax.yml"

  Scenario: Test the interview "ML from text area"
    Given I start the interview "docassemble.base:data/questions/examples/mlarea-datatype.yml"
    Then I should see the phrase "Describe how you feel."
    And I set the text area to "I feel terrible and I have an üpset stomach."
    And I click the button "Continue"
    Then I should see the phrase "You sound"

  # Scenario: Test the interview "Classify"
  #   Given I start the interview "docassemble.base:data/questions/examples/ml-classify.yml"

  Scenario: Test the interview "ML from line of text"
    Given I start the interview "docassemble.base:data/questions/examples/ml-datatype.yml"
    Then I should see the phrase "Describe how you feel."
    And I set the text box to "I feel terrible and I have an üpset stomach."
    And I click the button "Continue"
    Then I should see the phrase "You sound"

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

  Scenario: Test the interview "Share training sets" 1
    Given I start the interview "docassemble.demo:data/questions/examples/predict-activity-activity.yml"
    Then I should see the phrase "What kind of work do you do now?"
    And I set "Work" to "Analyzing briefs, writing memos, and taking cases"
    And I click the button "Continue"
    Then I should see the phrase "What kind of work do you see yourself doing in five years?"
    And I set "Work" to "Writing briefs, writing memos, and taking even more cases"
    And I click the button "Continue"
    Then I should see the phrase "It seems that you are fairly content with your current work."

  Scenario: Test the interview "Share training sets" 2
    Given I start the interview "docassemble.demo:data/questions/examples/predict-activity.yml"
    Then I should see the phrase "What kind of work do you do now?"
    And I set "Work" to "Analyzing briefs, writing memos, and taking cases"
    And I click the button "Continue"
    Then I should see the phrase "What kind of work do you see yourself doing in five years?"
    And I set "Work" to "Writing briefs, writing memos, and taking even more cases"
    And I click the button "Continue"
    Then I should see the phrase "It seems that you are fairly content with your current work."

  Scenario: Test the interview "Machine Learning" 2
    Given I start the interview "docassemble.demo:data/questions/examples/predict-happy-sad-area.yml"
    Then I should see the phrase "Describe how you feel."
    And I set the text area to "Lousy"
    And I click the button "Continue"
    Then I should see the phrase "You sound sad."

  Scenario: Test the interview "Machine Learning" 3
    Given I start the interview "docassemble.demo:data/questions/examples/predict-happy-sad.yml"
    Then I should see the phrase "Describe how you feel."
    And I set the text box to "Lousy"
    And I click the button "Continue"
    Then I should see the phrase "You sound sad."

  Scenario: Test the interview "Address autocomplete"
    Given I start the interview "docassemble.base:data/questions/examples/address-autocomplete.yml"
    Then I should see the phrase "What is the address of the adverse party?"
    And I set "Address" to "211 S 11th St"
    And I set "City" to "Philadelphia"
    And I select "Pennsylvania" as the "State"
    And I set "County" to "Philadelphia County"
    And I click the button "Continue"
    Then I should see the phrase "The adverse party’s zip code is"

  Scenario: Test the interview "Language"
    Given I start the interview "docassemble.base:data/questions/examples/language.yml"
    Then I should see the phrase "What language do you speak?"
    And I click the "Español" option
    And I click the button "Continue"
    Then I should see the phrase "¿Cuál es el significado de la vida?"
    And I set "Significado de la Vida" to "dormir"
    And I click the button "Seguir"
    Then I should see the phrase "The meaning of life"
    And I should see the phrase "The interviewee said the meaning of life is"
    And I should see the phrase "dormir"

  Scenario: Test the interview "Set language"
    Given I start the interview "docassemble.base:data/questions/examples/set-language.yml"
    Then I should see the phrase "What language do you speak?"
    And I click the option "Español"
    And I click the button "Continue"
    Then I should see the phrase "¿Cuál es el significado de la vida?"
    And I set "Significado de la Vida" to "dinero"
    And I click the button "Seguir"
    Then I should see the phrase "The meaning of life"
    And I should see the phrase "The interviewee said the meaning of life is:"
    And I should see the phrase "dinero"

  Scenario: Test the interview "Font Awesome"
    Given I start the interview "docassemble.base:data/questions/examples/font-awesome.yml"
    Then I should see the phrase "Third quarter metrics"
    And I should not see the phrase ":bed:"

  # Scenario: Test the interview "Store data in Google Sheet"
  #   Given I start the interview "docassemble.demo:data/questions/examples/google-sheet.yml"
  #   Then I should see the phrase "What is your first name?"
  #   And I set "Name" to "Auto tester"
  #   And I click the button "Continue"
  #   Then I should see the phrase "What is your favorite fruit?"
  #   And I set "Fruit" to "apples"
  #   And I click the button "Continue"
  #   Then I should see the phrase "What is your favorite vegetable?"
  #   And I set "Vegetable" to "turnips"
  #   And I click the button "Continue"
  #   Then I should see the phrase "Thank you for your input!"

  # Scenario: Test the interview "Get files from Google Drive"
  #   Given I start the interview "docassemble.demo:data/questions/examples/google-drive.yml"
  #   Then I should see the phrase "Files in your Google Drive"

  Scenario: Test the interview "Review answers"
    Given I start the interview "docassemble.base:data/questions/examples/review-8.yml"
    Then I should see the phrase "What is your address?"
    And I set "Street address" to "418 South 20th Street"
    And I set "City" to "Philadelphia"
    And I select "Pennsylvania" as the "State"
    And I set "Zip" to "19146"
    And I click the button "Continue"
    Then I should see the phrase "You live in Philadelphia County."
    And I click the link "Review your answers"
    Then I should see the phrase "This address is located in Philadelphia County."
    And I click the link "Edit"
    Then I should see the phrase "What is your address?"
    And I set "Street address" to "651 College Drive"
    And I set "City" to "Blackwood"
    And I select "New Jersey" as the "State"
    And I set "Zip" to "08012"
    And I click the button "Continue"

  Scenario: Test the interview "Action button"
    Given I start the interview "docassemble.base:data/questions/examples/action-button-html.yml"
    Then I should see the phrase "Need more information?"
    And I click the final link "Visit our web site"

  Scenario: Test the interview "Action buttons"
    Given I start the interview "docassemble.base:data/questions/examples/action-buttons-http.yml"
    Then I should see the phrase "You may wish to wait until"
    And I click the final link " Come back later"

  # Scenario: Test the interview "DAWeb"
  #   Given I start the interview "docassemble.base:data/questions/examples/daweb.yml"

