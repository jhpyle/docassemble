#! /bin/bash

SERVER=http://localhost

file_changed=false
for css_file in app/app.css app/pygments.css; do
    orig_file="${css_file/.css/.scss}"
    if [[ docassemble_webapp/docassemble/webapp/static/${orig_file} -nt docassemble_webapp/docassemble/webapp/static/${css_file} ]]; then
	sass docassemble_webapp/docassemble/webapp/static/${orig_file} docassemble_webapp/docassemble/webapp/static/${css_file}
	file_changed=true
    fi
done
for min_file in app/app.min.css app/pygments.min.css bootstrap-slider/dist/css/bootstrap-slider.min.css bootstrap-combobox/css/bootstrap-combobox.min.css; do
    orig_file="${min_file/.min/}"
    if [[ docassemble_webapp/docassemble/webapp/static/${orig_file} -nt docassemble_webapp/docassemble/webapp/static/${min_file} ]]; then
	sass --style compressed docassemble_webapp/docassemble/webapp/static/${orig_file} docassemble_webapp/docassemble/webapp/static/${min_file}
	file_changed=true
    fi
done

for min_file in app/app.min.js app/config.min.js app/manage_api.min.js app/update_package.min.js app/updatingpackages.min.js app/pullplaygroundpacakge.min.js app/501.min.js app/train.min.js app/admin.min.js app/cm6.min.js app/monitor.min.js app/playground.min.js labelauty/source/jquery-labelauty.min.js bootstrap-combobox/js/bootstrap-combobox.min.js ; do
    orig_file="${min_file/.min/}"
    map_file=$(basename $min_file).map
    if [[ docassemble_webapp/docassemble/webapp/static/${orig_file} -nt docassemble_webapp/docassemble/webapp/static/${min_file} ]]; then
	uglifyjs docassemble_webapp/docassemble/webapp/static/${orig_file} --source-map "url='$map_file',includeSources" --output docassemble_webapp/docassemble/webapp/static/${min_file}
	file_changed=true
    fi
done
if [ "$file_changed" = true ]; then
    echo "A file was modified. Install docassemble.webapp on ${SERVER}, re-run this script, and install again."
    exit
fi

wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundle.css ${SERVER}/bundle.css
/usr/bin/sass --style compressed docassemble_webapp/docassemble/webapp/static/app/bundle.css docassemble_webapp/docassemble/webapp/static/app/bundle.min.css
wget -q -O docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.css ${SERVER}/playgroundbundle.css
/usr/bin/sass --style compressed docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.css docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.min.css
wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundle.js ${SERVER}/bundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/bundle.js --source-map "url='bundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/bundle.min.js
wget -q -O docassemble_webapp/docassemble/webapp/static/app/monitorbundle.js ${SERVER}/monitorbundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/monitorbundle.js --source-map "url='monitorbundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/monitorbundle.min.js
wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js ${SERVER}/bundlewrapjquery.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js --source-map "url='bundlewrapjquery.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.min.js
wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js ${SERVER}/bundlenojquery.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js --source-map "url='bundlenojquery.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.min.js
wget -q -O docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.js ${SERVER}/playgroundbundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.js --source-map "url='playgroundbundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.min.js
wget -q -O docassemble_webapp/docassemble/webapp/static/app/adminbundle.js ${SERVER}/adminbundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/adminbundle.js --source-map "url='adminbundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/adminbundle.min.js
