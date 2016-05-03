#! /bin/bash
tempfile=`mktemp /tmp/XXXXXXX.png`
shopt -s nullglob
for path in docassemble_base/docassemble/base/data/questions/examples/*.yml
do
    file=${path##*/}
    file=${file%.*}
    if [ "$file" = "audio" -o "$file" = "video" -o "$file" = "vimeo" -o "$file" = "video-nyc" ]
    then
	continue
    fi
    if [ -f docassemble_webapp/docassemble/webapp/static/examples/$file.png -a docassemble_webapp/docassemble/webapp/static/examples/$file.png -nt $path ]
    then
	continue
    fi
    casperjs screenshot.js $file.yml $tempfile
    if [ "$file" = "signature" -o "$file" = "metadata" -o "$file" = "help" -o "$file" = "help-damages" -o "$file" = "help-damages-audio" -o "$file" = "progress" -o "$file" = "progress-features" ]
    then
	convert $tempfile -resize 496x9999 -trim docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "markdown" ]
    then
	convert $tempfile -crop 496x999+86+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "fields" ]
    then
	convert $tempfile -crop 496x1999+86+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    else
	convert $tempfile -crop 496x630+86+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    fi
done
if [ -d ~/gh-page-da ]
then
    ./get_yaml_from_example.py docassemble_base/docassemble/base/data/questions/examples > ~/gh-page-da/_data/example.yml
    rsync -auv docassemble_webapp/docassemble/webapp/static/examples ~/gh-page-da/img/
fi
rm $tempfile
