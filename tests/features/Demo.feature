Feature: Demonstration interview
  In order to ensure docassemble is running properly, I want
  to run the example interviews.

  @all
  Scenario: Start to "Were you injured?"
    Given I am using the server "https://dev.upsolve.org"
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
    And I wait forever
