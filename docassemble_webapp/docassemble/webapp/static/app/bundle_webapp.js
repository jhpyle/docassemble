/** Help with local development in the webapp/static dir by copying code from server.py.
*   If a file is added to the server.py lists, it needs to be added here too.
* 
* To run on the command line in your running docker container:
docker exec -it your_docker_container_name /bin/bash
cd /tmp/docassemble
node docassemble_webapp/docassemble/webapp/static/app/bundle_webapp.js
su www-data
source /usr/share/docassemble/local3.10/bin/activate
pip install --no-deps --no-index --upgrade --force-reinstall ./docassemble_base ./docassemble_webapp ./docassemble ./docassemble_demo && exit
supervisorctl start reset
* 
* Then wait for the server to restart. You can pip install fewer of those
*   directories if you know what you're doing.
*/
let fs = require('fs');

// No minification. That can be done at the very end with a command like
// minify docassemble_webapp/docassemble/webapp/static/app/app.js > docassemble_webapp/docassemble/webapp/static/app/app.min.js
fs.copyFileSync('docassemble_webapp/docassemble/webapp/static/app/app.js', 'docassemble_webapp/docassemble/webapp/static/app/app.min.js');
fs.copyFileSync('docassemble_webapp/docassemble/webapp/static/app/app.css', 'docassemble_webapp/docassemble/webapp/static/app/app.min.css');

// @app.route('/bundle.css', methods=['GET'])
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

// @app.route('/playgroundbundle.css', methods=['GET'])
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

// @app.route('/bundle.js', methods=['GET'])
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

// @app.route('/playgroundbundle.js', methods=['GET'])
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


// @app.route('/adminbundle.js', methods=['GET'])
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

// @app.route('/bundlewrapjquery.js', methods=['GET'])
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

// @app.route('/bundlenojquery.js', methods=['GET'])
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
};

// Bundle everything
css_bundle();
playground_css_bundle();
js_bundle();
playground_js_bundle();
js_admin_bundle();
js_bundle_wrap();
js_bundle_no_query();

console.log(`Done bundling ".../webapp/static" files`);
