#! /bin/bash
tempfile=`mktemp /tmp/XXXXXXX.png`
shopt -s nullglob
for path in docassemble_base/docassemble/base/data/questions/examples/*.yml
do
    file=${path##*/}
    file=${file%.*}
    if [ "$file" = "audio" -o "$file" = "video" -o "$file" = "vimeo" -o "$file" = "video-static" -o "$file" = "immediate-file" ]
    then
	continue
    fi
    if [ -f docassemble_webapp/docassemble/webapp/static/examples/$file.png -a docassemble_webapp/docassemble/webapp/static/examples/$file.png -nt $path ]
    then
    	continue
    fi
    casperjs screenshot.js $file.yml $tempfile
    if [ "$file" = "signature" -o "$file" = "metadata" -o "$file" = "help" -o "$file" = "help-damages" -o "$file" = "help-damages-audio" -o "$file" = "progress" -o "$file" = "progress-features" -o "$file" = "response" -o "$file" = "response-hello" -o "$file" = "response-svg" -o "$file" = "menu-item" -o "$file" = "ml-export" -o "$file" = "ml-export-yaml" -o "$file" = "live_chat" ]
    then
	convert $tempfile -resize 650x9999 -trim docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "markdown" -o "$file" = "allow-emailing-true" -o "$file" = "allow-emailing-false" ]
    then
	convert $tempfile -crop 650x999+13+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "fields" -o "$file" = "attachment-code" ]
    then
	convert $tempfile -crop 650x1999+13+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    else
	convert $tempfile -crop 650x630+13+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    fi
done
if [ -d ~/gh-pages-da ]
then
    ./get_yaml_from_example.py docassemble_base/docassemble/base/data/questions/examples > ~/gh-pages-da/_data/example.yml
    rsync -auv docassemble_webapp/docassemble/webapp/static/examples ~/gh-pages-da/img/
fi
rm $tempfile
