#! /bin/bash

STATIC=docassemble_webapp/docassemble/webapp/static

for css_file in app/app.css app/pygments.css; do
    orig_file="${css_file/.css/.scss}"
    if [[ docassemble_webapp/docassemble/webapp/static/${orig_file} -nt docassemble_webapp/docassemble/webapp/static/${css_file} ]]; then
	/usr/bin/sass docassemble_webapp/docassemble/webapp/static/${orig_file} docassemble_webapp/docassemble/webapp/static/${css_file}
    fi
done
for min_file in app/app.min.css app/pygments.min.css bootstrap-slider/dist/css/bootstrap-slider.min.css bootstrap-combobox/css/bootstrap-combobox.min.css; do
    orig_file="${min_file/.min/}"
    if [[ docassemble_webapp/docassemble/webapp/static/${orig_file} -nt docassemble_webapp/docassemble/webapp/static/${min_file} ]]; then
	/usr/bin/sass --style compressed docassemble_webapp/docassemble/webapp/static/${orig_file} docassemble_webapp/docassemble/webapp/static/${min_file}
    fi
done

for min_file in app/app.min.js app/config.min.js app/manage_api.min.js app/update_package.min.js app/updatingpackages.min.js app/pullplaygroundpacakge.min.js app/501.min.js app/train.min.js app/admin.min.js app/cm6.min.js app/monitor.min.js app/playground.min.js bootstrap-combobox/js/bootstrap-combobox.min.js ; do
    orig_file="${min_file/.min/}"
    map_file=$(basename $min_file).map
    if [[ docassemble_webapp/docassemble/webapp/static/${orig_file} -nt docassemble_webapp/docassemble/webapp/static/${min_file} ]]; then
	uglifyjs docassemble_webapp/docassemble/webapp/static/${orig_file} --source-map "url='$map_file',includeSources" --output docassemble_webapp/docassemble/webapp/static/${min_file}
    fi
done

cat ${STATIC}/bootstrap/css/bootstrap-icons.css ${STATIC}/bootstrap-combobox/css/bootstrap-combobox.css ${STATIC}/bootstrap-slider/dist/css/bootstrap-slider.css ${STATIC}/app/app.css > ${STATIC}/app/bundle.css
/usr/bin/sass --style compressed docassemble_webapp/docassemble/webapp/static/app/bundle.css docassemble_webapp/docassemble/webapp/static/app/bundle.min.css
cat ${STATIC}/app/pygments.css ${STATIC}/bootstrap/css/bootstrap-icons.css > ${STATIC}/app/playgroundbundle.css
/usr/bin/sass --style compressed docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.css docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.min.css
cat ${STATIC}/app/jquery.js ${STATIC}/app/jquery.validate.js ${STATIC}/app/additional-methods.js ${STATIC}/app/jquery.visible.js ${STATIC}/bootstrap/js/bootstrap.bundle.js ${STATIC}/bootstrap-slider/dist/bootstrap-slider.js ${STATIC}/app/app.js ${STATIC}/bootstrap-combobox/js/bootstrap-combobox.js ${STATIC}/app/socket.io.js ${STATIC}/app/signature_pad.umd.min.js > ${STATIC}/app/bundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/bundle.js --source-map "url='bundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/bundle.min.js
cat ${STATIC}/app/socket.io.js ${STATIC}/app/monitor.js > ${STATIC}/app/monitorbundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/monitorbundle.js --source-map "url='monitorbundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/monitorbundle.min.js
cat ${STATIC}/app/jquery.validate.js ${STATIC}/app/additional-methods.js ${STATIC}/app/jquery.visible.js ${STATIC}/bootstrap/js/bootstrap.bundle.js ${STATIC}/bootstrap-slider/dist/bootstrap-slider.js ${STATIC}/app/app.js ${STATIC}/bootstrap-combobox/js/bootstrap-combobox.js ${STATIC}/app/socket.io.js > ${STATIC}/app/bundlewrapjquery.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js --source-map "url='bundlewrapjquery.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.min.js
cat ${STATIC}/app/jquery.validate.js ${STATIC}/app/additional-methods.js ${STATIC}/app/jquery.visible.js ${STATIC}/bootstrap/js/bootstrap.bundle.js ${STATIC}/bootstrap-slider/dist/bootstrap-slider.js ${STATIC}/app/app.js ${STATIC}/bootstrap-combobox/js/bootstrap-combobox.js ${STATIC}/app/socket.io.js > ${STATIC}/app/bundlenojquery.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js --source-map "url='bundlenojquery.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.min.js
cat ${STATIC}/areyousure/jquery.are-you-sure.js ${STATIC}/app/cm6.js ${STATIC}/app/playground.js > ${STATIC}/app/playgroundbundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.js --source-map "url='playgroundbundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.min.js
cat ${STATIC}/app/jquery.js ${STATIC}/bootstrap/js/bootstrap.bundle.js ${STATIC}/app/admin.js > ${STATIC}/app/adminbundle.js
uglifyjs docassemble_webapp/docassemble/webapp/static/app/adminbundle.js --source-map "url='adminbundle.min.js.map',includeSources" --output docassemble_webapp/docassemble/webapp/static/app/adminbundle.min.js
