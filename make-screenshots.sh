#! /bin/bash
tempfile=`mktemp /tmp/XXXXXXX.png`
shopt -s nullglob
for path in docassemble_base/docassemble/base/data/questions/examples/*.yml
do
    file=${path##*/}
    file=${file%.*}
    casperjs screenshot.js $file.yml $tempfile
    if [ "$file" = "signature" ]
    then
	convert $tempfile -resize 496x9999 -trim docassemble_webapp/docassemble/webapp/static/examples/$file.png
    else
	convert $tempfile -crop 496x520+86+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    fi
done
rm $tempfile
