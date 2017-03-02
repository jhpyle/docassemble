#! /bin/bash

grep --include='*.py' -Roh -e 'word("[^"]*")' -e "word('[^']*')" | sed -e 's/word("\(.*\)")/"\1": Null/' -e "s/word('\(.*\)')/\"\1\": \Null/" | sort | uniq
