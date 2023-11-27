#! /bin/bash
#tempfile=`mktemp /tmp/XXXXXXX.png`
datafile=`mktemp /tmp/XXXXXXX.txt`
featurefile=tests/features/Screenshots.feature
echo -e -n "Feature: screenshots\n  Make screenshots" > $featurefile

shopt -s nullglob
for path in docassemble_base/docassemble/base/data/questions/examples/*.yml docassemble_demo/docassemble/demo/data/questions/examples/*.yml
do
    area=${path%/docassemble*}
    area=${area##*_}
    tfile=${path##*/}
    tfile=${tfile%.*}

    # url="http://localhost?i=docassemble.$area:data/questions/examples/$tfile.yml&json=1"
    # wget --quiet -O "json_files/"$tfile".json" "$url"
    # sleep 1
    # continue

    # create anyway:
    # radio-list-mobile
    # yaml-markdown-python
    # turnips-worms

    # do manually:
    # exit-url-referer-fullscreen
    # exit-url-referer-fullscreen-mobile
    # session-interview

    # previously done manually:
    # help-damages-audio
    # help-damages
    # audio

    if [ "$tfile" = "immediate-file" -o \
	 "$tfile" = "exit-url-referer-fullscreen" -o \
	 "$tfile" = "exit-url-referer-fullscreen-mobile" -o \
	 "$tfile" = "session-interview" -o \
	 "$tfile" = "address-autocomplete-nz" -o \
	 "$tfile" = "advocate" -o \
	 "$tfile" = "alarm-clock" -o \
	 "$tfile" = "allow-emailing-false-pdf" -o \
	 "$tfile" = "append-list" -o \
	 "$tfile" = "attachment" -o \
	 "$tfile" = "background_action_test_timing" -o \
	 "$tfile" = "buttons-code-color-iterator" -o \
	 "$tfile" = "buttons-code-iterator" -o \
	 "$tfile" = "chat" -o \
	 "$tfile" = "chat-example-2" -o \
	 "$tfile" = "checkbox-dict-dict" -o \
	 "$tfile" = "checkbox-export-value" -o \
	 "$tfile" = "combobox" -o \
	 "$tfile" = "command" -o \
	 "$tfile" = "companies" -o \
	 "$tfile" = "conflict_check" -o \
	 "$tfile" = "continue-serial" -o \
	 "$tfile" = "continue-special" -o \
	 "$tfile" = "custody" -o \
	 "$tfile" = "dadatetime" -o \
	 "$tfile" = "dalist" -o \
	 "$tfile" = "dalist2" -o \
	 "$tfile" = "declarative" -o \
	 "$tfile" = "declarative-classes" -o \
	 "$tfile" = "default-screen-parts-override" -o \
	 "$tfile" = "demo-basic-questions" -o \
	 "$tfile" = "demo-basic-questions-address" -o \
	 "$tfile" = "demo-basic-questions-name" -o \
	 "$tfile" = "discovery" -o \
	 "$tfile" = "dispatch-count" -o \
	 "$tfile" = "document-language-docx" -o \
	 "$tfile" = "docx-template-auto" -o \
	 "$tfile" = "docx-template-code" -o \
	 "$tfile" = "docx-template-code-2" -o \
	 "$tfile" = "docx-template-multiple" -o \
	 "$tfile" = "dual-dict" -o \
	 "$tfile" = "edit-list-complete-complex" -o \
	 "$tfile" = "edit-list-manual" -o \
	 "$tfile" = "empty-choices" -o \
	 "$tfile" = "empty-choices-checkboxes" -o \
	 "$tfile" = "empty-choices-checkboxes-solo" -o \
	 "$tfile" = "empty-choices-fields" -o \
	 "$tfile" = "empty-choices-fields-multiple" -o \
	 "$tfile" = "empty-choices-fields-solo" -o \
	 "$tfile" = "empty-choices-object-checkboxes" -o \
	 "$tfile" = "empty-choices-object-checkboxes-create" -o \
	 "$tfile" = "empty-choices-object-checkboxes-solo" -o \
	 "$tfile" = "empty-choices-object-checkboxes-solo-create" -o \
	 "$tfile" = "exit-url-referer-fullscreen" -o \
	 "$tfile" = "exit-url-referer-fullscreen-mobile" -o \
	 "$tfile" = "field-note" -o \
	 "$tfile" = "fields-ajax-list-collect" -o \
	 "$tfile" = "fields-mc-exclude-manual" -o \
	 "$tfile" = "fields-mc-with-showif" -o \
	 "$tfile" = "file" -o \
	 "$tfile" = "flags" -o \
	 "$tfile" = "flushleft" -o \
	 "$tfile" = "flushright" -o \
	 "$tfile" = "forward-chaining" -o \
	 "$tfile" = "forward-chaining-assumptions" -o \
	 "$tfile" = "gather" -o \
	 "$tfile" = "gather-dict-number" -o \
	 "$tfile" = "gather-fruit-incomplete" -o \
	 "$tfile" = "gather-manual-gathered-object" -o \
	 "$tfile" = "gather-manual-gathered-object-simple" -o \
	 "$tfile" = "gather-set-number" -o \
	 "$tfile" = "get-docx-variables" -o \
	 "$tfile" = "get-pdf-fields" -o \
	 "$tfile" = "get-pdf-fields-2" -o \
	 "$tfile" = "google-drive" -o \
	 "$tfile" = "google-sheet-2" -o \
	 "$tfile" = "harry-potter-or-heidegger" -o \
	 "$tfile" = "hello" -o \
	 "$tfile" = "hello2" -o \
	 "$tfile" = "hello3" -o \
	 "$tfile" = "hello4" -o \
	 "$tfile" = "hello5" -o \
	 "$tfile" = "hello6" -o \
	 "$tfile" = "hello7" -o \
	 "$tfile" = "immediate_file" -o \
	 "$tfile" = "infinite-loop" -o \
	 "$tfile" = "infinite-loop-2" -o \
	 "$tfile" = "initial-code" -o \
	 "$tfile" = "interview-about-flowers" -o \
	 "$tfile" = "interview-about-fruit" -o \
	 "$tfile" = "interview-about-vegetables" -o \
	 "$tfile" = "interview-flowers" -o \
	 "$tfile" = "interview-fruit" -o \
	 "$tfile" = "interview-list" -o \
	 "$tfile" = "interview-url-session" -o \
	 "$tfile" = "interview-url-session-two" -o \
	 "$tfile" = "interview-vegetables" -o \
	 "$tfile" = "jinjayaml-included" -o \
	 "$tfile" = "join" -o \
	 "$tfile" = "json-response" -o \
	 "$tfile" = "language-change" -o \
	 "$tfile" = "leave" -o \
	 "$tfile" = "life_story" -o \
	 "$tfile" = "list" -o \
	 "$tfile" = "list-collect-disable-others" -o \
	 "$tfile" = "list-collect-string" -o \
	 "$tfile" = "list-collect-uncheck-others" -o \
	 "$tfile" = "list-table-manual-gather" -o \
	 "$tfile" = "list-table-manual-gather-simple" -o \
	 "$tfile" = "live_chat" -o \
	 "$tfile" = "main-page" -o \
	 "$tfile" = "mainpage-demo-parts" -o \
	 "$tfile" = "markdown-template" -o \
	 "$tfile" = "material-icons" -o \
	 "$tfile" = "ml-ajax" -o \
	 "$tfile" = "ml-ajax-classify" -o \
	 "$tfile" = "ml-export-playground" -o \
	 "$tfile" = "multi-signature" -o \
	 "$tfile" = "nested-gather" -o \
	 "$tfile" = "nested-objects-list" -o \
	 "$tfile" = "no-mandatory" -o \
	 "$tfile" = "non-required-radio" -o \
	 "$tfile" = "oauth-test-4" -o \
	 "$tfile" = "object-default" -o \
	 "$tfile" = "object-demo" -o \
	 "$tfile" = "object-radio-address-2" -o \
	 "$tfile" = "objects-from-file-template" -o \
	 "$tfile" = "ocr-classify" -o \
	 "$tfile" = "ocr-save-and-predict" -o \
	 "$tfile" = "pdf-fill-export-values" -o \
	 "$tfile" = "pdf-fill-signature-alt" -o \
	 "$tfile" = "pdf-fill-skip-undefined" -o \
	 "$tfile" = "question-library" -o \
	 "$tfile" = "question-sequence" -o \
	 "$tfile" = "questionless" -o \
	 "$tfile" = "questions" -o \
	 "$tfile" = "quotes-in-code" -o \
	 "$tfile" = "relationships" -o \
	 "$tfile" = "report-version" -o \
	 "$tfile" = "response-hello" -o \
	 "$tfile" = "review-9" -o \
	 "$tfile" = "roletest" -o \
	 "$tfile" = "roletestmany" -o \
	 "$tfile" = "samplequestion" -o \
	 "$tfile" = "samplesignature" -o \
	 "$tfile" = "send-sms" -o \
	 "$tfile" = "session-interview-redirect" -o \
	 "$tfile" = "setparts-demo" -o \
	 "$tfile" = "sets-exit" -o \
	 "$tfile" = "sets-exit-choices" -o \
	 "$tfile" = "sets-exit-url" -o \
	 "$tfile" = "showif-boolean-yesno-false" -o \
	 "$tfile" = "showif-nested-checkbox" -o \
	 "$tfile" = "sign" -o \
	 "$tfile" = "signature-diversion" -o \
	 "$tfile" = "signature-template" -o \
	 "$tfile" = "signdoc" -o \
	 "$tfile" = "single-code" -o \
	 "$tfile" = "sms" -o \
	 "$tfile" = "some-questions" -o \
	 "$tfile" = "someone-already-mentioned-bad" -o \
	 "$tfile" = "someone-already-mentioned2" -o \
	 "$tfile" = "suppress-loading-util" -o \
	 "$tfile" = "test" -o \
	 "$tfile" = "test-docx-template" -o \
	 "$tfile" = "test-example-list" -o \
	 "$tfile" = "test-sig-form" -o \
	 "$tfile" = "test-url" -o \
	 "$tfile" = "testaction" -o \
	 "$tfile" = "testaction2" -o \
	 "$tfile" = "testage" -o \
	 "$tfile" = "testattach" -o \
	 "$tfile" = "testbuildfl" -o \
	 "$tfile" = "testbuildfl2" -o \
	 "$tfile" = "testcron" -o \
	 "$tfile" = "testcron2" -o \
	 "$tfile" = "testcronbg" -o \
	 "$tfile" = "testdadict" -o \
	 "$tfile" = "testdalist2" -o \
	 "$tfile" = "testdaobjectfail" -o \
	 "$tfile" = "testdaobjectsucceed" -o \
	 "$tfile" = "testdivorce" -o \
	 "$tfile" = "testdocx" -o \
	 "$tfile" = "testemail" -o \
	 "$tfile" = "testfields" -o \
	 "$tfile" = "testforloop" -o \
	 "$tfile" = "testgeneric" -o \
	 "$tfile" = "testimage" -o \
	 "$tfile" = "testlist0" -o \
	 "$tfile" = "testlist1" -o \
	 "$tfile" = "testlist2" -o \
	 "$tfile" = "testlist3" -o \
	 "$tfile" = "testmcmako" -o \
	 "$tfile" = "testobjectfield" -o \
	 "$tfile" = "testobjectfieldradio" -o \
	 "$tfile" = "testobjectlist" -o \
	 "$tfile" = "testobjects" -o \
	 "$tfile" = "testperson" -o \
	 "$tfile" = "testpg" -o \
	 "$tfile" = "testpickle" -o \
	 "$tfile" = "testplural" -o \
	 "$tfile" = "testproblem" -o \
	 "$tfile" = "testpulldown" -o \
	 "$tfile" = "testqr" -o \
	 "$tfile" = "testqr2" -o \
	 "$tfile" = "testresponse" -o \
	 "$tfile" = "testreview" -o \
	 "$tfile" = "testreview2" -o \
	 "$tfile" = "testreview3" -o \
	 "$tfile" = "testreview4" -o \
	 "$tfile" = "testsandbox" -o \
	 "$tfile" = "testssn" -o \
	 "$tfile" = "testunicode" -o \
	 "$tfile" = "testurlarg" -o \
	 "$tfile" = "testurlarg2" -o \
	 "$tfile" = "translation" -o \
	 "$tfile" = "twocol" -o \
	 "$tfile" = "upload_images" -o \
	 "$tfile" = "video-static" -o \
	 "$tfile" = "vimeo" -o \
	 "$tfile" = "wc_common" -o \
	 "$tfile" = "wc_side_of_bed" -o \
	 "$tfile" = "with-mandatory" -o \
	 "$tfile" = "with-mandatory-tweak-a" -o \
	 "$tfile" = "with-mandatory-tweak-b" -o \
         "$tfile" = "upload-handler" ]
    then
	continue
    fi
    if [ -f ~/gh-pages-da/img/examples/$tfile.png -a ~/gh-pages-da/img/examples/$tfile.png -nt $path ]
    then
        continue
    fi
    tempfile=`mktemp /tmp/XXXXXXX.png`
    echo -e -n "\n\n  Scenario: make screenshot for $tfile\n    Given I launch the interview \"docassemble.${area}:data/questions/examples/${tfile}.yml\"" >> $featurefile
    if [ "$tfile" = "signature" -o \
	 "$tfile" = "metadata" -o \
         "$tfile" = "help" ]
    then
	echo -e -n "\n    And I wait 6 seconds\n    And I set the window size to 650x1136\n    And I wait 2 seconds\n    And I save a screenshot to \"$tempfile\"\n    And I set the window size to 1005x9999\n    And I wait 2 seconds" >> $featurefile
    elif [ "$tfile" = "radio-list-mobile" -o \
	   "$tfile" = "sections-small-screen-dropdown" -o \
	   "$tfile" = "sections-small-screen-false" ]
    then
	echo -e -n "\n    And I wait 6 seconds\n    And I set the window size to 385x1136\n    And I wait 2 seconds\n    And I save a screenshot to \"$tempfile\"\n    And I set the window size to 1005x9999\n    And I wait 2 seconds" >> $featurefile
    elif [ "$tfile" = "mainpage-demo-parts" -o \
           "$tfile" = "setparts-demo" -o \
           "$tfile" = "default-screen-parts-override" -o \
           "$tfile" = "metadata-screen-parts" -o \
           "$tfile" = "default-screen-parts" -o \
           "$tfile" = "set-parts" ]
    then
	echo -e -n "\n    And I wait 6 seconds\n    And I set the window size to 1005x700\n    And I wait 2 seconds\n    And I save a screenshot to \"$tempfile\"\n    And I set the window size to 1005x9999\n    And I wait 2 seconds" >> $featurefile
    elif [ "$tfile" = "table" -o "$tfile" = "table-alt" -o "$tfile" = "table-mako" -o "$tfile" = "table-reorder" ]
    then
	echo -e -n "\n    And I set \"Fruit\" to \"apples\"\n    And I set \"Number of seeds\" to \"10\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"oranges\"\n    And I set \"Number of seeds\" to \"6\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"pears\"\n    And I set \"Number of seeds\" to \"0\"\n    And I click the button \"Continue\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "table-python" ]
    then
	echo -e -n "\n    And I set \"Fruit\" to \"apple\"\n    And I set \"Number of seeds\" to \"12\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"pear\"\n    And I set \"Number of seeds\" to \"0\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"watermelon\"\n    And I set \"Number of seeds\" to \"1736\"\n    And I click the button \"Continue\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "table-if-then" ]
    then
	echo -e -n "\n    And I set \"Fruit\" to \"apple\"\n    And I set \"Number of seeds\" to \"3\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"pear\"\n    And I set \"Number of seeds\" to \"0\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"watermelon\"\n    And I set \"Number of seeds\" to \"1736\"\n    And I click the button \"Continue\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "sections" -o "$tfile" = "sections-horizontal" ]
    then
	echo -e -n "\n    And I click the button \"Continue\"\n    And I select \"Roadmap\" from the menu\n    And I wait 5 seconds\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-1" -o "$tfile" = "review-2" -o "$tfile" = "review-3" -o "$tfile" = "resume-button-label" -o "$tfile" = "review-5" -o "$tfile" = "review-6" ]
    then
	echo -e -n "\n    And I set the text box to \"apple\"\n    And I click the button \"Continue\"\n    And I set the text box to \"turnip\"\n    And I click the button \"Continue\"\n    And I select \"Review Answers\" from the menu\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-tabular" -o "$tfile" = "review-tabular-class" ]
    then
	echo -e -n "\n    And I set the text box to \"apple\"\n    And I click the button \"Continue\"\n    And I set the text box to \"turnip\"\n    And I click the button \"Continue\"\n    And I set the text box to \"button mushrooms\"\n    And I click the button \"Continue\"\n    And I select \"Review Answers\" from the menu\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-4" ]
    then
	echo -e -n "\n    And I set the text box to \"apple\"\n    And I click the button \"Continue\"\n    And I select \"Review Answers\" from the menu\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-7" ]
    then
	echo -e -n "\n    And I set the text box to \"apple\"\n    And I click the button \"Continue\"\n    And I set the text box to \"turnip\"\n    And I click the button \"Continue\"\n    And I set the text box to \"button mushrooms\"\n    And I click the button \"Continue\"\n    And I select \"Review Answers\" from the menu\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-8" ]
    then
	echo -e -n "\n    Then I should see the phrase \"What is your address?\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
	#echo -e -n "\n    Then I should see the phrase \"What is your address?\"\n    And I set \"Street address\" to \"418 South 20th Street\"\n    And I set \"City\" to \"Philadelphia\"\n    And I select \"Pennsylvania\" as the \"State\"\n    And I set \"Zip\" to \"19146\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"You live in Philadelphia County.\"\n    And I click the link \"Review your answers\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-9" ]
    then
	echo -e -n "\n    Then I should see the phrase \"What is a?\"\n    And I set \"a\" to \"10\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is b?\"\n    And I set \"b\" to \"5\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is c?\"\n    And I set \"c\" to \"2\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"The answer is 13.0.\"\n    And I click the link \"change this\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "sections-keywords" ]
    then
	echo -e -n "\n    And I click the button \"Continue\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "audio" ]
    then
	echo -e -n "\n    And I wait 1 second\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "table-read-only" -o "$tfile" = "table-read-only-2" ]
    then
	echo -e -n "\n    Then I should see the phrase \"Do you want to add another fruit to the list?\"\n    And I click the button \"Yes\"\n    Then I should see the phrase \"Tell me about the fruit.\"\n    And I set \"Name\" to \"Grape\"\n    And I set \"Seeds\" to \"0\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Do you want to add another fruit to the list?\"\n    And I click the button \"Yes\"\n    Then I should see the phrase \"Tell me about the fruit.\"\n    And I set \"Name\" to \"Watermelon\"\n    And I set \"Seeds\" to \"43\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Do you want to add another fruit to the list?\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "table-dict-edit" -o "$tfile" = "table-dict-edit-minimum-number" -o "$tfile" = "table-dict-edit-delete-buttons" -o "$tfile" = "table-dict-delete-buttons" -o "$tfile" = "table-dict-confirm" ]
    then
	echo -e -n "\n    And I click the option \"Yes\" under \"Do you get income from benefits?\"\n    And I wait 1 second\n    And I set \"How much do you get from benefits?\" to \"434\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Income from employment\"\n    And I click the option \"No\" under \"Do you get income from employment?\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Income from interest\"\n    And I click the option \"Yes\" under \"Do you get income from interest?\"\n    And I wait 1 second\n    And I set \"How much do you get from interest?\" to \"532\"\n    And I click the button \"Continue\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-edit-list-table" ]
    then
	echo -e -n "\n    Then I should see the phrase \"Who is the first person?\"\n    And I set \"First Name\" to \"John\"\n    And I set \"Last Name\" to \"Smith\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is John Smith’s favorite fruit?\"\n    And I set \"Fruit\" to \"apple\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"Yes\"\n    Then I should see the phrase \"Who is the second person?\"\n    And I set \"First Name\" to \"Sally\"\n    And I set \"Last Name\" to \"Jones\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is Sally Jones’s favorite fruit?\"\n    And I set \"Fruit\" to \"orange\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"No\"\n    And I click the link \"edit your answers\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "edit-list-non-editable" ]
    then
	echo -e -n "\n    Then I should see the phrase \"Who is the first person?\"\n    And I set \"First Name\" to \"John\"\n    And I set \"Last Name\" to \"Smith\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is John Smith’s favorite fruit?\"\n    And I set \"Fruit\" to \"apple\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"Yes\"\n    Then I should see the phrase \"Who is the second person?\"\n    And I set \"First Name\" to \"Sally\"\n    And I set \"Last Name\" to \"Jones\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is Sally Jones’s favorite fruit?\"\n    And I set \"Fruit\" to \"orange\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "edit-list" ]
    then
	echo -e -n "\n    Then I should see the phrase \"Who is the first person?\"\n    And I set \"First Name\" to \"John\"\n    And I set \"Last Name\" to \"Smith\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is John Smith’s favorite fruit?\"\n    And I set \"Fruit\" to \"apples\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"Yes\"\n    Then I should see the phrase \"Who is the second person?\"\n    And I set \"First Name\" to \"Amanda\"\n    And I set \"Last Name\" to \"Martin\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is Amanda Martin’s favorite fruit?\"\n    And I set \"Fruit\" to \"apples\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"No\"\n    Then I should see the phrase \"Who is your favorite person?\"\n    And I select \"John Smith\" as the \"Favorite\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"All done\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "review-edit-list" ]
    then
	echo -e -n "\n    Then I should see the phrase \"Who is the first person?\"\n    And I set \"First Name\" to \"John\"\n    And I set \"Last Name\" to \"Smith\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is John Smith’s favorite fruit?\"\n    And I set \"Fruit\" to \"apples\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"Yes\"\n    Then I should see the phrase \"Who is the second person?\"\n    And I set \"First Name\" to \"Jane\"\n    And I set \"Last Name\" to \"Doe\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is Jane Doe’s favorite fruit?\"\n    And I set \"Fruit\" to \"kiwi\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"No\"\n    Then I should see the phrase \"Who is your favorite person?\"\n    And I select \"Jane Doe\" as the \"Favorite\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Thank you for your answers!\"\n    And I should see the phrase \"The people are John Smith and Jane Doe and your favorite is Jane Doe.\"\n    And I click the link \"edit your answers\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$tfile" = "breadcrumbs" ]
    then
	echo -e -n "\n    Then I should see the phrase \"Who is the first person?\"\n    And I set \"First Name\" to \"John\"\n    And I set \"Last Name\" to \"Smith\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is John Smith’s favorite fruit?\"\n    And I set \"Fruit\" to \"apples\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"Yes\"\n    Then I should see the phrase \"Who is the second person?\"\n    And I set \"First Name\" to \"Jane\"\n    And I set \"Last Name\" to \"Doe\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"What is Jane Doe’s favorite fruit?\"\n    And I set \"Fruit\" to \"peaches\"\n    And I click the button \"Continue\"\n    Then I should see the phrase \"Are there any more people you would like to mention?\"\n    And I click the button \"No\"\n    Then I should see the phrase \"Thank you for your answers!\"\n    And I click the link \"edit your answers\"\n    Then I should see the phrase \"Edit your answers\"\n    And I click the first link \" Edit\"\n    And I click the button \"Continue\"\n    And I click the link \"types of fruit\"\n    Then I should see the phrase \"Fruit types\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    else
	echo -e -n "\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    fi
    echo -e -n "${tfile}\t${area}\t${tempfile}\n" >> $datafile
done

cd tests
behave --stop features/Screenshots.feature
if [ $? -ne 0 ]
then
    echo "Failure while making screenshots"
    exit 1
fi
cd ..

while IFS=$'\t' read -r -a col
do
    tfile=${col[0]}
    area=${col[1]}
    tempfile=${col[2]}
    if [ "$tfile" = "signature" -o \
         "$tfile" = "breadcrumbs" -o \
	 "$tfile" = "metadata" -o \
	 "$tfile" = "no-mandatory" -o \
         "$tfile" = "help" -o \
         "$tfile" = "help-damages" -o \
         "$tfile" = "progress" -o \
         "$tfile" = "progress-features" -o \
         "$tfile" = "progress-features-percentage" -o \
	 "$tfile" = "progress-multi" -o \
         "$tfile" = "response" -o \
         "$tfile" = "response-hello" -o \
         "$tfile" = "menu-item" -o \
         "$tfile" = "ml-export" -o \
         "$tfile" = "ml-export-yaml" -o \
         "$tfile" = "live_chat" -o \
         "$tfile" = "review-side-note" -o \
         "$tfile" = "side-html" -o \
         "$tfile" = "side-note" -o \
         "$tfile" = "bootstrap-theme" -o \
         "$tfile" = "flash" -o \
         "$tfile" = "log" -o \
         "$tfile" = "show-login" -o \
         "$tfile" = "branch-error" -o \
         "$tfile" = "error-help" -o \
         "$tfile" = "error-help-language" -o \
         "$tfile" = "set-logo-title" -o \
         "$tfile" = "question-help-button" -o \
         "$tfile" = "question-help-button-off" -o \
         "$tfile" = "right" -o \
         "$tfile" = "sections" -o \
         "$tfile" = "sections-horizontal" -o \
         "$tfile" = "sections-keywords" -o \
         "$tfile" = "sections-keywords-code" -o \
         "$tfile" = "sections-keywords-get-sections" -o \
         "$tfile" = "sections-keywords-review" -o \
         "$tfile" = "sections-keywords-set-sections" -o \
	 "$tfile" = "sections-non-progressive" -o \
         "$tfile" = "sections-auto-open" -o \
         "$tfile" = "centered" -o \
	 "$tfile" = "pre" -o \
         "$tfile" = "mainpage-demo-parts" -o \
         "$tfile" = "setparts-demo" -o \
         "$tfile" = "default-screen-parts-override" -o \
         "$tfile" = "metadata-screen-parts" -o \
         "$tfile" = "default-screen-parts" -o \
         "$tfile" = "set-parts" -o \
         "$tfile" = "navbar-language" -o \
         "$tfile" = "preview" ]
    then
	convert $tempfile -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 -resize 488x9999 ~/gh-pages-da/img/examples/$tfile.png
    elif [ "$tfile" = "radio-list-mobile" -o \
           "$tfile" = "sections-small-screen-dropdown" -o \
	   "$tfile" = "sections-small-screen-false" ]
    then
	convert $tempfile -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 ~/gh-pages-da/img/examples/$tfile.png
    elif [ "$tfile" = "markdown" -o "$tfile" = "allow-emailing-true" -o "$tfile" = "allow-emailing-false" -o "$tfile" = "markdown-demo" -o "$tfile" = "document-links" -o "$tfile" = "document-links-limited" -o "$tfile" = "allow-downloading-true" ]
    then
	convert $tempfile -crop 488x999+259+92 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 ~/gh-pages-da/img/examples/$tfile.png
    elif [ "$tfile" = "inverse-navbar" ]
    then
	convert $tempfile -crop 1005x260+0+0 ~/gh-pages-da/img/examples/$tfile.png
    elif [ "$tfile" = "fields" -o "$tfile" = "attachment-code" -o "$tfile" = "attachment-simple" -o "$tfile" = "document-markup" -o "$tfile" = "document-variable-name" -o "$tfile" = "document-cache-invalidate" -o "$tfile" = "address-autocomplete-test"  -o "$tfile" = "address-autocomplete-test" -o "$tfile" = "table-width" -o "$tfile" = "document-language" -o "$tfile" = "allow-downloading-true" -o "$tfile" = "allow-downloading-true-zip-filename" -o "$tfile" = "document-docx" -o "$tfile" = "document-docx-from-rtf" -o "$tfile" = "document-file" -o "$tfile" = "google-sheet-3" ]
    then
	convert $tempfile -crop 488x1999+259+92 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 ~/gh-pages-da/img/examples/$tfile.png
    else
	convert $tempfile -crop 488x630+259+92 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 ~/gh-pages-da/img/examples/$tfile.png
    fi
    touch ~/gh-pages-da/img/examples/$tfile.png
    rm -f $tempfile
done < $datafile
rm -f $datafile

if [ -d ~/gh-pages-da ]
then
    ./get_yaml_from_example.py docassemble_base/docassemble/base/data/questions/examples ~/gh-pages-da/img/examples > ~/gh-pages-da/_data/example.yml
    ./get_yaml_from_example.py docassemble_demo/docassemble/demo/data/questions/examples ~/gh-pages-da/img/examples >> ~/gh-pages-da/_data/example.yml
    #rsync -auv docassemble_webapp/docassemble/webapp/static/examples ~/gh-pages-da/img/
    list_of_files=`mktemp /tmp/XXXXXXX.txt`
    grep '^    - ' docassemble_base/docassemble/base/data/questions/example-list.yml | sed 's/^    - \(.*\)/\1.png/' > $list_of_files
    rsync -auv --files-from=$list_of_files ~/gh-pages-da/img/examples docassemble_webapp/docassemble/webapp/static/examples/
    rm $list_of_files
    psql -h localhost -T 'class="table table-striped"' -U docassemble -P footer=off -P border=0 -Hc "select table_name, column_name, data_type, character_maximum_length, column_default from information_schema.columns where table_schema='public'" docassemble > ~/gh-pages-da/_includes/db-schema.html
fi
