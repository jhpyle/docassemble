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
    file=${path##*/}
    file=${file%.*}
    
    # url="http://localhost?i=docassemble.$area:data/questions/examples/$file.yml&json=1"
    # wget --quiet -O "json_files/"$file".json" "$url"
    # sleep 1
    # continue
    
    if [ "$file" = "immediate-file" -o "$file" = "exit-url-referer-fullscreen" -o "$file" = "exit-url-referer-fullscreen-mobile" -o "$file" = "session-interview" -o "$file" = "audio" -o "$file" = "help-damages-audio" ]
    then
	continue
    fi
    if [ -f docassemble_webapp/docassemble/webapp/static/examples/$file.png -a docassemble_webapp/docassemble/webapp/static/examples/$file.png -nt $path ]
    then
    	continue
    fi
    tempfile=`mktemp /tmp/XXXXXXX.png`
    echo -e -n "\n\n  Scenario: make screenshot for $file\n    Given I launch the interview \"docassemble.${area}:data/questions/examples/${file}.yml\"" >> $featurefile
    if [ "$file" = "signature" -o \
	 "$file" = "metadata" -o \
         "$file" = "help" ]
    then
	echo -e -n "\n    And I wait 6 seconds\n    And I set the window size to 650x1136\n    And I wait 2 seconds\n    And I save a screenshot to \"$tempfile\"\n    And I set the window size to 1005x9999\n    And I wait 2 seconds" >> $featurefile
    elif [ "$file" = "radio-list-mobile" ]
    then
	echo -e -n "\n    And I wait 6 seconds\n    And I set the window size to 385x1136\n    And I wait 2 seconds\n    And I save a screenshot to \"$tempfile\"\n    And I set the window size to 1005x9999\n    And I wait 2 seconds" >> $featurefile
    elif [ "$file" = "table" -o "$file" = "table-alt" -o "$file" = "table-mako" ]
    then
	echo -e -n "\n    And I set \"Fruit\" to \"apples\"\n    And I set \"Number of seeds\" to \"10\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"oranges\"\n    And I set \"Number of seeds\" to \"6\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"pears\"\n    And I set \"Number of seeds\" to \"0\"\n    And I click the button \"Continue\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$file" = "table-python" ]
    then
	echo -e -n "\n    And I set \"Fruit\" to \"apple\"\n    And I set \"Number of seeds\" to \"12\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"pear\"\n    And I set \"Number of seeds\" to \"0\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"watermelon\"\n    And I set \"Number of seeds\" to \"1736\"\n    And I click the button \"Continue\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$file" = "table-if-then" ]
    then
	echo -e -n "\n    And I set \"Fruit\" to \"apple\"\n    And I set \"Number of seeds\" to \"3\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"pear\"\n    And I set \"Number of seeds\" to \"0\"\n    And I click the button \"Continue\"\n    And I click the button \"Yes\"\n    And I set \"Fruit\" to \"watermelon\"\n    And I set \"Number of seeds\" to \"1736\"\n    And I click the button \"Continue\"\n    And I click the button \"No\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$file" = "sections" -o "$file" = "sections-horizontal" ]
    then
	echo -e -n "\n    And I click the button \"Continue\"\n    And I select \"Roadmap\" from the menu\n    And I wait 5 seconds\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$file" = "review-1" -o "$file" = "review-2" -o "$file" = "review-3" -o "$file" = "resume-button-label" -o "$file" = "review-5" -o "$file" = "review-6" ]
    then
	echo -e -n "\n    And I set the text box to \"apple\"\n    And I click the button \"Continue\"\n    And I set the text box to \"turnip\"\n    And I click the button \"Continue\"\n    And I select \"Review Answers\" from the menu\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$file" = "review-4" ]
    then
	echo -e -n "\n    And I set the text box to \"apple\"\n    And I click the button \"Continue\"\n    And I select \"Review Answers\" from the menu\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$file" = "sections-keywords" ]
    then
	echo -e -n "\n    And I click the button \"Continue\"\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    elif [ "$file" = "audio" ]
    then
	echo -e -n "\n    And I wait 1 second\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    else
	echo -e -n "\n    And I save a screenshot to \"$tempfile\"" >> $featurefile
    fi
    echo -e -n "${file}\t${area}\t${tempfile}\n" >> $datafile
done

cd tests
lettuce -v 3 -r --failfast features/Screenshots.feature
if [ $? -ne 0 ]
then
    echo "Failure while making screenshots"
    exit 1
fi
cd ..

while IFS=$'\t' read -r -a col
do
    file=${col[0]}
    area=${col[1]}
    tempfile=${col[2]}
    if [ "$file" = "signature" -o \
	 "$file" = "metadata" -o \
	 "$file" = "no-mandatory" -o \
         "$file" = "help" -o \
         "$file" = "help-damages" -o \
         "$file" = "progress" -o \
         "$file" = "progress-features" -o \
	 "$file" = "progress-multi" -o \
         "$file" = "response" -o \
         "$file" = "response-hello" -o \
         "$file" = "menu-item" -o \
         "$file" = "ml-export" -o \
         "$file" = "ml-export-yaml" -o \
         "$file" = "live_chat" -o \
         "$file" = "bootstrap-theme" -o \
         "$file" = "flash" -o \
         "$file" = "log" -o \
         "$file" = "branch-error" -o \
         "$file" = "set-title" -o \
         "$file" = "set-logo-title" -o \
         "$file" = "question-help-button" -o \
         "$file" = "question-help-button-off" -o \
         "$file" = "right" -o \
         "$file" = "sections" -o \
         "$file" = "sections-horizontal" -o \
         "$file" = "sections-keywords" -o \
         "$file" = "sections-keywords-code" -o \
         "$file" = "sections-keywords-get-sections" -o \
         "$file" = "sections-keywords-review" -o \
         "$file" = "sections-keywords-set-sections" -o \
         "$file" = "centered" ]
    then
	convert $tempfile -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 -resize 478x9999 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "radio-list-mobile" ]
    then
	convert $tempfile -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "markdown" -o "$file" = "allow-emailing-true" -o "$file" = "allow-emailing-false" -o "$file" = "markdown-demo" -o "$file" = "document-links" -o "$file" = "document-links-limited" -o "$file" = "allow-downloading-true" ]
    then
	convert $tempfile -crop 478x999+264+92 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "inverse-navbar" ]
    then
	convert $tempfile -crop 1005x260+0+0 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "fields" -o "$file" = "attachment-code" -o "$file" = "attachment-simple" -o "$file" = "document-markup" -o "$file" = "document-variable-name" -o "$file" = "document-cache-invalidate" -o "$file" = "address-autocomplete-test"  -o "$file" = "address-autocomplete-test" -o "$file" = "table-width" -o "$file" = "document-language" -o "$file" = "allow-downloading-true" -o "$file" = "allow-downloading-true-zip-filename" -o "$file" = "document-docx" -o "$file" = "document-docx-from-rtf" -o "$file" = "document-file" ]
    then
	convert $tempfile -crop 478x1999+264+92 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    else
	convert $tempfile -crop 478x630+264+92 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    fi
    rm -f $tempfile
done < $datafile
rm -f $datafile

if [ -d ~/gh-pages-da ]
then
    ./get_yaml_from_example.py docassemble_base/docassemble/base/data/questions/examples > ~/gh-pages-da/_data/example.yml
    ./get_yaml_from_example.py docassemble_demo/docassemble/demo/data/questions/examples >> ~/gh-pages-da/_data/example.yml
    rsync -auv docassemble_webapp/docassemble/webapp/static/examples ~/gh-pages-da/img/
    psql -h localhost -T 'class="table table-striped"' -U docassemble -P footer=off -P border=0 -Hc "select table_name, column_name, data_type, character_maximum_length, column_default from information_schema.columns where table_schema='public'" docassemble > ~/gh-pages-da/_includes/db-schema.html
fi
