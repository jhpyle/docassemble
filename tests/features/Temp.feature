Feature: Example interviews
  In order to ensure docassemble is running properly, I want
  to run the example interviews.

  Scenario: Test the interview "Other field" with pull-down
    Given I start the interview "docassemble.base:data/questions/examples/other.yml"
    Then I should see the phrase "What kind of car do you drive?"
    And I select "Toyota" as the "Make"
    Then I should not see the phrase "Other make"
    And I click the button "Continue"
    Then I should see the phrase "You drive a Toyota."

  Scenario: Test the interview "Other field" with other
    Given I start the interview "docassemble.base:data/questions/examples/other.yml"
    Then I should see the phrase "What kind of car do you drive?"
    And I select "Other" as the "Make"
    And I wait 1 second
    And I set "Other make" to "Ferrari"
    And I click the button "Continue"
    Then I should see the phrase "You drive a Ferrari."
