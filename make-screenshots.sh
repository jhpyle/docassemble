#! /bin/bash
tempfile=`mktemp /tmp/XXXXXXX.png`
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
    
    if [ "$file" = "audio" -o "$file" = "video" -o "$file" = "vimeo" -o "$file" = "video-static" -o "$file" = "immediate-file" -o "$file" = "table" -o "$file" = "table-alt" -o "$file" = "table-python" -o "$file" = "table-if-then" -o "$file" = "table-mako" -o "$file" = "no-mandatory" -o "$file" = "exit-url-referer-fullscreen" -o "$file" = "exit-url-referer-fullscreen-mobile" -o "$file" = "fields-choices-dropdown" ] || [[ $file == sections* ]]
    then
	continue
    fi
    if [ -f docassemble_webapp/docassemble/webapp/static/examples/$file.png -a docassemble_webapp/docassemble/webapp/static/examples/$file.png -nt $path ]
    then
    	continue
    fi
    casperjs screenshot.js $file.yml $tempfile $area
    if [ "$file" = "signature" -o "$file" = "metadata" -o "$file" = "help" -o "$file" = "help-damages" -o "$file" = "help-damages-audio" -o "$file" = "progress" -o "$file" = "progress-features" -o "$file" = "response" -o "$file" = "response-hello" -o "$file" = "menu-item" -o "$file" = "ml-export" -o "$file" = "ml-export-yaml" -o "$file" = "live_chat" -o "$file" = "bootstrap-theme" -o "$file" = "flash" -o "$file" = "log" ]
    then
	convert $tempfile -resize 650x9999 -trim docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "markdown" -o "$file" = "allow-emailing-true" -o "$file" = "allow-emailing-false" -o "$file" = "markdown-demo" -o "$file" = "document-links" -o "$file" = "document-links-limited" ]
    then
	convert $tempfile -crop 650x999+13+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "inverse-navbar" ]
    then
	convert $tempfile -crop 1005x260+0+0 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    elif [ "$file" = "fields" -o "$file" = "attachment-code" -o "$file" = "attachment-simple" -o "$file" = "document-markup" -o "$file" = "document-variable-name" -o "$file" = "document-cache-invalidate" ]
    then
	convert $tempfile -crop 650x1999+13+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    else
	convert $tempfile -crop 650x630+13+78 -background white -splice 0x1 -background black -splice 0x1 -trim +repage -chop 0x1 docassemble_webapp/docassemble/webapp/static/examples/$file.png
    fi
done
if [ -d ~/gh-pages-da ]
then
    ./get_yaml_from_example.py docassemble_base/docassemble/base/data/questions/examples > ~/gh-pages-da/_data/example.yml
    ./get_yaml_from_example.py docassemble_demo/docassemble/demo/data/questions/examples >> ~/gh-pages-da/_data/example.yml
    rsync -auv docassemble_webapp/docassemble/webapp/static/examples ~/gh-pages-da/img/
    psql -h localhost -T 'class="table table-striped"' -U docassemble -P footer=off -P border=0 -Hc "select table_name, column_name, data_type, character_maximum_length, column_default from information_schema.columns where table_schema='public'" docassemble > ~/gh-pages-da/_includes/db-schema.html
fi
rm $tempfile
