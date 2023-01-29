/**
* Copying code from server.py to help local development of app folder
* to run on the command line:
* npm install fs
* node docassemble_webapp/docassemble/webapp/static/app/bundle_app.mjs
* su www-data
* source /usr/share/docassemble/local3.10/bin/activate
* pip install --no-deps --no-index --upgrade --force-reinstall ./docassemble_base ./docassemble_webapp ./docassemble && exit
*/

// Must `npm install` all libs used in here. Can't do that from inside here.
import fs from 'fs';
import * as cp from 'child_process';

// Destination will be created or overwritten by default.
// No minification. That can be done at the very end with a command like
// minify docassemble_webapp/docassemble/webapp/static/app/app.js > docassemble_webapp/docassemble/webapp/static/app/app.min.js
fs.copyFileSync('docassemble_webapp/docassemble/webapp/static/app/app.js', 'docassemble_webapp/docassemble/webapp/static/app/app.min.js');
// Q: Are there any other things that need to be copied over?
fs.copyFileSync('docassemble_webapp/docassemble/webapp/static/app/app.css', 'docassemble_webapp/docassemble/webapp/static/app/app.min.css');

// wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundle.css http://localhost/bundle.css
// @app.route('/bundle.css', methods=['GET'])
// def css_bundle():
//     // ...
//     for parts in [['bootstrap-fileinput', 'css', 'fileinput.min.css'], ['labelauty', 'source', 'jquery-labelauty.min.css'], ['bootstrap-combobox', 'css', 'bootstrap-combobox.min.css'], ['bootstrap-slider', 'dist', 'css', 'bootstrap-slider.min.css'], ['app', 'app.min.css']]:
//     // ...
function css_bundle() {
  /** WARNING: If you change the file list in here, you have to change it in ...app/server.py as well. */
  let container_path = `docassemble_webapp/docassemble/webapp/static/`;
  let target_path = `${ container_path }app/bundle.css`;
  let filepaths = [
    `${ container_path }bootstrap-fileinput/css/fileinput.min.css`,
    `${ container_path }labelauty/source/jquery-labelauty.min.css`,
    `${ container_path }bootstrap-combobox/css/bootstrap-combobox.min.css`,
    `${ container_path }bootstrap-slider/dist/css/bootstrap-slider.min.css`,
    `${ container_path }app/app.min.css`,
  ];
  bundle( target_path, filepaths );
};

// wget -q -O docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.css http://localhost/playgroundbundle.css
// @app.route('/playgroundbundle.css', methods=['GET'])
// def playground_css_bundle():
//     // ...
//     for parts in [['codemirror', 'lib', 'codemirror.css'], ['codemirror', 'addon', 'search', 'matchesonscrollbar.css'], ['codemirror', 'addon', 'display', 'fullscreen.css'], ['codemirror', 'addon', 'scroll', 'simplescrollbars.css'], ['codemirror', 'addon', 'hint', 'show-hint.css'], ['app', 'pygments.min.css'], ['bootstrap-fileinput', 'css', 'fileinput.min.css']]:
//     // ...
function playground_css_bundle() {
  /** WARNING: If you change the file list in here, you have to change it in ...app/server.py as well. */
  let container_path = `docassemble_webapp/docassemble/webapp/static/`;
  let target_path = `${ container_path }app/playgroundbundle.css`;
  let filepaths = [
    `${ container_path }codemirror/lib/codemirror.css`,
    `${ container_path }codemirror/addon/search/matchesonscrollbar.css`,
    `${ container_path }codemirror/addon/display/fullscreen.css`,
    `${ container_path }codemirror/addon/scroll/simplescrollbars.css`,
    `${ container_path }codemirror/addon/hint/show-hint.css`,
    `${ container_path }app/pygments.min.css`,
    `${ container_path }bootstrap-fileinput/css/fileinput.min.css`,
  ];
  bundle( target_path, filepaths );
};

//wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundle.js http://localhost/bundle.js
// @app.route('/bundle.js', methods=['GET'])
// def js_bundle():
//     // ...
//     for parts in [['app', 'jquery.min.js'], ['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['app', 'jquery.visible.min.js'], ['bootstrap', 'js', 'bootstrap.bundle.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.min.js'], ['labelauty', 'source', 'jquery-labelauty.min.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.min.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.min.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.min.js'], ['app', 'socket.io.min.js']]:
//     // ...
function js_bundle() {
  /** WARNING: If you change the file list in here, you have to change it in ...app/server.py as well. */
  let container_path = `docassemble_webapp/docassemble/webapp/static/`;
  let target_path = `${ container_path }app/bundle.js`;
  let filepaths = [
    `${ container_path }app/jquery.min.js`,
    `${ container_path }app/jquery.validate.min.js`,
    `${ container_path }app/additional-methods.min.js`,
    `${ container_path }app/jquery.visible.min.js`,
    `${ container_path }bootstrap/js/bootstrap.bundle.min.js`,
    `${ container_path }bootstrap-slider/dist/bootstrap-slider.min.js`,
    `${ container_path }labelauty/source/jquery-labelauty.min.js`,
    `${ container_path }bootstrap-fileinput/js/plugins/piexif.min.js`,
    `${ container_path }bootstrap-fileinput/js/fileinput.min.js`,
    `${ container_path }bootstrap-fileinput/themes/fas/theme.min.js`,
    `${ container_path }app/app.min.js`,
    `${ container_path }bootstrap-combobox/js/bootstrap-combobox.min.js`,
    `${ container_path }app/socket.io.min.js`,
  ];
  let extra_start = ``; //`//test4\n`;
  bundle( target_path, filepaths, extra_start );
};


// wget -q -O docassemble_webapp/docassemble/webapp/static/app/playgroundbundle.js http://localhost/playgroundbundle.js
// @app.route('/playgroundbundle.js', methods=['GET'])
// def playground_js_bundle():
//     // ...
//     for parts in [['areyousure', 'jquery.are-you-sure.js'], ['codemirror', 'lib', 'codemirror.js'], ['codemirror', 'addon', 'search', 'searchcursor.js'], ['codemirror', 'addon', 'scroll', 'annotatescrollbar.js'], ['codemirror', 'addon', 'search', 'matchesonscrollbar.js'], ['codemirror', 'addon', 'display', 'fullscreen.js'], ['codemirror', 'addon', 'edit', 'matchbrackets.js'], ['codemirror', 'addon', 'hint', 'show-hint.js'], ['codemirror', 'mode', 'yaml', 'yaml.js'], ['codemirror', 'mode', 'python', 'python.js'], ['yamlmixed', 'yamlmixed.js'], ['codemirror', 'mode', 'markdown', 'markdown.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.min.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js']]:
//     // ...
function playground_js_bundle() {
  /** WARNING: If you change the file list in here, you have to change it in ...app/server.py as well. */
  let container_path = `docassemble_webapp/docassemble/webapp/static/`;
  let target_path = `${ container_path }app/playgroundbundle.js`;
  let filepaths = [
    `${ container_path }areyousure/jquery.are-you-sure.js`,
    `${ container_path }codemirror/lib/codemirror.js`,
    `${ container_path }codemirror/addon/search/searchcursor.js`,
    `${ container_path }codemirror/addon/scroll/annotatescrollbar.js`,
    `${ container_path }codemirror/addon/search/matchesonscrollbar.js`,
    `${ container_path }codemirror/addon/display/fullscreen.js`,
    `${ container_path }codemirror/addon/edit/matchbrackets.js`,
    `${ container_path }codemirror/addon/hint/show-hint.js`,
    `${ container_path }codemirror/mode/yaml/yaml.js`,
    `${ container_path }codemirror/mode/python/python.js`,
    `${ container_path }yamlmixed/yamlmixed.js`,
    `${ container_path }codemirror/mode/markdown/markdown.js`,
    `${ container_path }bootstrap-fileinput/js/plugins/piexif.min.js`,
    `${ container_path }bootstrap-fileinput/js/fileinput.min.js`,
    `${ container_path }bootstrap-fileinput/themes/fas/theme.min.js`,
  ];
  bundle( target_path, filepaths );
};


// wget -q -O docassemble_webapp/docassemble/webapp/static/app/adminbundle.js http://localhost/adminbundle.js
// @app.route('/adminbundle.js', methods=['GET'])
// def js_admin_bundle():
//     // ...
//     for parts in [['app', 'jquery.min.js'], ['bootstrap', 'js', 'bootstrap.bundle.min.js']]:
//     // ...
function js_admin_bundle() {
  /** WARNING: If you change the file list in here, you have to change it in ...app/server.py as well. */
  let container_path = `docassemble_webapp/docassemble/webapp/static/`;
  let target_path = `${ container_path }app/adminbundle.js`;
  let filepaths = [
    `${ container_path }app/jquery.min.js`,
    `${ container_path }bootstrap/js/bootstrap.bundle.min.js`,
  ];
  bundle( target_path, filepaths );
};

// wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundlewrapjquery.js http://localhost/bundlewrapjquery.js
// @app.route('/bundlewrapjquery.js', methods=['GET'])
// def js_bundle_wrap():
//     base_path = pkg_resources.resource_filename(pkg_resources.Requirement.parse('docassemble.webapp'), os.path.join('docassemble', 'webapp', 'static'))
//     output = '(function($) {'
//     for parts in [['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['app', 'jquery.visible.js'], ['bootstrap', 'js', 'bootstrap.bundle.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.min.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.min.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.min.js'], ['labelauty', 'source', 'jquery-labelauty.min.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.min.js'], ['app', 'socket.io.min.js']]:
//     // ...
//     output += '})(jQuery);'
function js_bundle_wrap() {
  /** WARNING: If you change the file list in here, you have to change it in ...app/server.py as well. */
  let container_path = `docassemble_webapp/docassemble/webapp/static/`;
  let target_path = `${ container_path }app/bundlewrapjquery.js`;
  let filepaths = [
    `${ container_path }app/jquery.validate.min.js`,
    `${ container_path }app/additional-methods.min.js`,
    `${ container_path }app/jquery.visible.js`,
    `${ container_path }bootstrap/js/bootstrap.bundle.min.js`,
    `${ container_path }bootstrap-slider/dist/bootstrap-slider.min.js`,
    `${ container_path }bootstrap-fileinput/js/plugins/piexif.min.js`,
    `${ container_path }bootstrap-fileinput/js/fileinput.min.js`,
    `${ container_path }bootstrap-fileinput/themes/fas/theme.min.js`,
    `${ container_path }app/app.min.js`,
    `${ container_path }labelauty/source/jquery-labelauty.min.js`,
    `${ container_path }bootstrap-combobox/js/bootstrap-combobox.min.js`,
    `${ container_path }app/socket.io.min.js`,
  ];
  let extra_start = `(function($) {\n`;
  let extra_end = `})(jQuery);`;
  bundle( target_path, filepaths, extra_start, extra_end );
};


// wget -q -O docassemble_webapp/docassemble/webapp/static/app/bundlenojquery.js http://localhost/bundlenojquery.js
// @app.route('/bundlenojquery.js', methods=['GET'])
// def js_bundle_no_query():
//     // ...
//     for parts in [['app', 'jquery.validate.min.js'], ['app', 'additional-methods.min.js'], ['app', 'jquery.visible.min.js'], ['bootstrap', 'js', 'bootstrap.bundle.min.js'], ['bootstrap-slider', 'dist', 'bootstrap-slider.min.js'], ['bootstrap-fileinput', 'js', 'plugins', 'piexif.min.js'], ['bootstrap-fileinput', 'js', 'fileinput.min.js'], ['bootstrap-fileinput', 'themes', 'fas', 'theme.min.js'], ['app', 'app.min.js'], ['labelauty', 'source', 'jquery-labelauty.min.js'], ['bootstrap-combobox', 'js', 'bootstrap-combobox.min.js'], ['app', 'socket.io.min.js']]:
//     // ...
function js_bundle_no_query() {
  /** WARNING: If you change the file list in here, you have to change it in ...app/server.py as well. */
  let container_path = `docassemble_webapp/docassemble/webapp/static/`;
  let target_path = `${ container_path }app/bundlenojquery.js`;
  let filepaths = [
    `${ container_path }app/jquery.validate.min.js`,
    `${ container_path }app/additional-methods.min.js`,
    `${ container_path }app/jquery.visible.min.js`,
    `${ container_path }bootstrap/js/bootstrap.bundle.min.js`,
    `${ container_path }bootstrap-slider/dist/bootstrap-slider.min.js`,
    `${ container_path }bootstrap-fileinput/js/plugins/piexif.min.js`,
    `${ container_path }bootstrap-fileinput/js/fileinput.min.js`,
    `${ container_path }bootstrap-fileinput/themes/fas/theme.min.js`,
    `${ container_path }app/app.min.js`,
    `${ container_path }labelauty/source/jquery-labelauty.min.js`,
    `${ container_path }bootstrap-combobox/js/bootstrap-combobox.min.js`,
    `${ container_path }app/socket.io.min.js`,
  ];
  bundle( target_path, filepaths );
};


function bundle( pathToOverwrite, pathsToBundle, extra_start='', extra_end='' ) {
  fs.writeFileSync( pathToOverwrite, `` );
  for ( let filepath of pathsToBundle ) {
    let contents = fs.readFileSync( filepath );
    fs.appendFileSync( pathToOverwrite, `\n${ extra_start }${ contents }${ extra_end }`);
  }
};  // Ends bundle()


// Bundle everything
css_bundle();
playground_css_bundle();
js_bundle();
playground_js_bundle();
js_admin_bundle();
js_bundle_wrap();
js_bundle_no_query();


console.log(`Done bundling ".../app"`);


// su www-data
// source /usr/share/docassemble/local3.10/bin/activate
// pip install --no-deps --no-index --upgrade --force-reinstall ./docassemble_base ./docassemble_webapp ./docassemble && exit

// let result = cp.execSync('su www-data');//, {env: {'PATH': '/tmp/docassemble'}});
// console.log( result );
// cp.execSync('source /usr/share/docassemble/local3.10/bin/activate');
// cp.execSync('pip install --no-deps --no-index --upgrade --force-reinstall ./docassemble_base ./docassemble_webapp ./docassemble && exit');

