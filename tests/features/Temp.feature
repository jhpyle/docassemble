Feature: Example interviews
  In order to ensure docassemble is running properly, I want
  to run the example interviews.

  Scenario: Set up the server
    Given I am using the server "http://localhost"
  
  Scenario: Test the interview "Help with question"
    Given I start the interview "docassemble.base:data/questions/examples/help.yml"
    Then I should see the phrase "What is 2+2?"
    And I go to the help screen
    Then I should see the phrase "Hint: 2 + 2 = 4."
    And I go back to the question screen
    And I click the "4" option
    And I click the button "Continue"
    Then I should see the phrase "You are brilliant!"
