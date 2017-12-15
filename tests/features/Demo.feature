Feature: Demonstration interview
  In order to ensure docassemble is running properly, I want
  to run the example interviews.

  @all
  Scenario: Start to "Were you injured?"
    Given I am using the server "http://localhost"
    And I start the interview "docassemble.demo:data/questions/questions.yml"
    Then I should see the phrase "What language do you speak?"
    And I click the "English" option
    And I click the button "Continue"
    Then I should see the phrase "Welcome to the docassemble demonstration."
    And I click the button "Ok, got it"
    Then I should see the phrase "Your use of this system does not mean that you have a lawyer."
    And I click the button "I understand"
    Then I should see the phrase "Were you injured?"

  @injured
  Scenario: "Were you injured?" to "Where do you live?" as injured person
    Given I click the button "Yes"
    Then I should see the phrase "Where do you live?"

  @notinjured
  Scenario: "Were you injured?" to "Where do you live?" as a non-injured person
    Given I click the button "No"
    Then I should see the phrase "Where do you live?"

  @all
  Scenario: "Where do you live?"
    And I set "Address" to "123 Elm St"
    And I set "City" to "Springfield"
    And I select "Pennsylvania" as the "State"    
    And I set "Zip" to "99232"
    And I click the button "Continue"
    
  @injured
    Then I should see the phrase "I understand that you live in Springfield. Were you injured in Pennsylvania?"
    And I click the button "Yes"
    Then I should see the phrase "When did your injury take place?"
    And I set "Date of Injury" to "05/05/2015"
    And I click the button "Continue"
    Then I should see the phrase "What is your name?"

  @all
  Scenario: "What is your name?" to "Are you a plaintiff in this case?"
    And I set "First Name" to "John"
    And I set "Last Name" to "Smith"
    And I click the button "Continue"
    Then I should see the phrase "What is your gender?"
    And I click the "Male" option
    And I click the button "Continue"
    Then I should see the phrase "What is your marital status?"
    And I click the "Single" option
    And I click the button "Continue"
    Then I should see the phrase "Are you a plaintiff in this case?"
    And I click the button "Yes"
    Then I should see the phrase "You have told me that there is one plaintiff, John Smith. Is there another plaintiff?"
    And I click the button "No"
    Then I should see the phrase "What is the name of the first defendant in the case?"
    And I set "First Name" to "Daniel"
    And I set "Last Name" to "Defoe"
    And I click the button "Continue"
    Then I should see the phrase "You have told me that there is one defendant, Daniel Defoe. Is there another defendant?"
    And I click the button "No"
    Then I should see the phrase "What is the village idiot’s name?"
    And I set "First Name" to "William"
    And I set "Last Name" to "Dunce"
    And I click the button "Continue"
    Then I should see the phrase "What kinds of income do you have?"
    And I click the "SSI" option
    And I click the button "Continue"
    Then I should see the phrase "How much do you make from SSI?"
    And I set "SSI Income" to "704"
    And I click the button "Continue"
    Then I should see the phrase "Do you have income from rent?"
    And I click the button "No"
    Then I should see the phrase "Do you own any automobiles?"
    And I click the button "No"
    Then I should see the phrase "What kinds of assets do you own?"
    And I click the "Stocks and Bonds" option
    And I click the button "Continue"
    Then I should see the phrase "How much do you have in stocks and bonds?"
    And I set "Amount in Stocks and Bonds" to "203200"
    And I click the button "Continue"
    And I wait forever
