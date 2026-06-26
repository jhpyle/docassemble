import datetime
import codecs
import json
import pickle
import re
import tempfile
import os
import operator
from flask import render_template, make_response, redirect, flash, current_app, request
from flask_login import current_user
from markupsafe import Markup
import werkzeug.utils
from sqlalchemy import select, and_, delete
from docassemble_flask_user import login_required, roles_required
from docassemble.base.functions import package_data_filename
from docassemble.base.language.words import word
from docassemble.base.util import DAFile, DAFileList, DADict
from docassemble.webapp.extensions import db
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.utils.fixpickle import fix_pickle_obj
from docassemble.webapp.interview.helpers import get_corresponding_interview
from docassemble.webapp.ml.machinelearning import SimpleTextMachineLearner
from docassemble.webapp.translations import setup_translation
from docassemble.webapp.utils.filenames import secure_filename_spaces_ok
from docassemble.webapp.utils.helpers import (
    get_url_from_file_reference,
    version_warning,
    custom_send_file,
)
from docassemble.webapp.utils.hooks import url_for
from docassemble.webapp.utils.logger import logmessage
from .blueprint import ml_bp
from .common import is_package_ml
from .forms import TrainingForm, TrainingUploadForm
from .helpers import fix_group_id, ml_prefix
from .models import MachineLearning

@ml_bp.route('/train', methods=['GET', 'POST'])
@login_required
@roles_required(['admin', 'developer', 'trainer'])
def train():
    if not current_app.config['ENABLE_TRAINING']:
        return ('File not found', 404)
    setup_translation()
    the_package = request.args.get('package', None)
    if the_package is not None:
        if the_package.startswith('_'):
            the_package = '_' + werkzeug.utils.secure_filename(the_package)
        else:
            the_package = werkzeug.utils.secure_filename(the_package)
    the_file = request.args.get('file', None)
    if the_file is not None:
        if the_file.startswith('_'):
            the_file = '_' + secure_filename_spaces_ok(the_file)
        else:
            the_file = secure_filename_spaces_ok(the_file)
    the_group_id = request.args.get('group_id', None)
    show_all = int(request.args.get('show_all', 0))
    form = TrainingForm(request.form)
    uploadform = TrainingUploadForm(request.form)
    extra_js = f"""
    <script src="{url_for('static', filename='app/train.min.js')}"></script>"""
    if request.method == 'POST' and the_package is not None and the_file is not None:
        if the_package == '_global':
            the_prefix = ''
        else:
            the_prefix = ml_prefix(the_package, the_file)
        json_file = None
        if the_package != '_global' and uploadform.usepackage.data == 'yes':
            the_file = package_data_filename(the_prefix)
            if the_file is None or not os.path.isfile(the_file):
                flash(word("Error reading JSON file from package.  File did not exist."), 'error')
                return redirect(url_for('ml.train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
            json_file = open(the_file, 'r', encoding='utf-8')
        if uploadform.usepackage.data == 'no' and 'jsonfile' in request.files and request.files['jsonfile'].filename:
            json_file = tempfile.NamedTemporaryFile(prefix="datemp", suffix=".json")
            request.files['jsonfile'].save(json_file.name)
            json_file.seek(0)
        if json_file is not None:
            try:
                href = json.load(json_file)
            except:
                flash(word("Error reading JSON file.  Not a valid JSON file."), 'error')
                return redirect(url_for('ml.train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
            json_file.close()
            if not isinstance(href, dict):
                flash(word("Error reading JSON file.  The JSON file needs to contain a dictionary at the root level."), 'error')
                return redirect(url_for('ml.train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
            nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            for group_id, train_list in href.items():
                if not isinstance(train_list, list):
                    logmessage("train: could not import part of JSON file.  Items in dictionary must be lists.")
                    continue
                if uploadform.importtype.data == 'replace':
                    db.session.execute(delete(MachineLearning).filter_by(group_id=the_prefix + ':' + group_id))
                    db.session.commit()
                    for entry in train_list:
                        if 'independent' in entry:
                            depend = entry.get('dependent', None)
                            if depend is not None:
                                new_entry = MachineLearning(group_id=the_prefix + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(depend), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None))
                            else:
                                new_entry = MachineLearning(group_id=the_prefix + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=False, key=entry.get('key', None))
                            db.session.add(new_entry)
                elif uploadform.importtype.data == 'merge':
                    indep_in_use = set()
                    for record in db.session.execute(select(MachineLearning).filter_by(group_id=the_prefix + ':' + group_id)).scalars():
                        indep = fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64'))
                        if indep is not None:
                            indep_in_use.add(indep)
                    for entry in train_list:
                        if 'independent' in entry and entry['independent'] not in indep_in_use:
                            depend = entry.get('dependent', None)
                            if depend is not None:
                                new_entry = MachineLearning(group_id=the_prefix + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(depend), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None))
                            else:
                                new_entry = MachineLearning(group_id=the_prefix + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=False, key=entry.get('key', None))
                            db.session.add(new_entry)
            db.session.commit()
            flash(word("Training data were successfully imported."), 'success')
            return redirect(url_for('ml.train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
        if form.cancel.data:
            return redirect(url_for('ml.train', package=the_package, file=the_file, show_all=show_all))
        if form.submit.data:
            group_id_to_use = fix_group_id(the_package, the_file, the_group_id)
            post_data = request.form.copy()
            deleted = set()
            for key, val in post_data.items():
                m = re.match(r'delete([0-9]+)', key)
                if not m:
                    continue
                entry_id = int(m.group(1))
                model = SimpleTextMachineLearner(group_id=group_id_to_use)
                model.delete_by_id(entry_id)
                deleted.add('dependent' + m.group(1))
            for key in deleted:
                if key in post_data:
                    del post_data[key]
            for key, val in post_data.items():
                m = re.match(r'dependent([0-9]+)', key)
                if not m:
                    continue
                orig_key = 'original' + m.group(1)
                if orig_key in post_data and post_data[orig_key] != val and val != '':
                    entry_id = int(m.group(1))
                    model = SimpleTextMachineLearner(group_id=group_id_to_use)
                    model.set_dependent_by_id(entry_id, val)
            if post_data.get('newindependent', '') != '':
                model = SimpleTextMachineLearner(group_id=group_id_to_use)
                if post_data.get('newdependent', '') != '':
                    model.add_to_training_set(post_data['newindependent'], post_data['newdependent'])
                else:
                    model.save_for_classification(post_data['newindependent'])
            return redirect(url_for('ml.train', package=the_package, file=the_file, group_id=the_group_id, show_all=show_all))
    if show_all:
        show_all = 1
        show_cond = MachineLearning.id != None  # noqa: E711 # pylint: disable=singleton-comparison
    else:
        show_all = 0
        show_cond = MachineLearning.dependent == None  # noqa: E711 # pylint: disable=singleton-comparison
    package_list = {}
    file_list = {}
    group_id_list = {}
    entry_list = []
    if current_user.has_role('admin', 'developer'):
        playground_package = 'docassemble.playground' + str(current_user.id)
    else:
        playground_package = None
    if the_package is None:
        for record in db.session.execute(select(MachineLearning.group_id, db.func.count(MachineLearning.id).label('cnt')).where(show_cond).group_by(MachineLearning.group_id)):  # pylint: disable=not-callable
            group_id = record.group_id
            parts = group_id.split(':')
            if is_package_ml(parts):
                if parts[0] not in package_list:
                    package_list[parts[0]] = 0
                package_list[parts[0]] += record.cnt
            else:
                if '_global' not in package_list:
                    package_list['_global'] = 0
                package_list['_global'] += record.cnt
        if not show_all:
            for record in db.session.execute(select(MachineLearning.group_id).group_by(MachineLearning.group_id)):
                parts = record.group_id.split(':')
                if is_package_ml(parts):
                    if parts[0] not in package_list:
                        package_list[parts[0]] = 0
            if '_global' not in package_list:
                package_list['_global'] = 0
        if playground_package and playground_package not in package_list:
            package_list[playground_package] = 0
        package_list = [(x, package_list[x]) for x in sorted(package_list)]
        response = make_response(render_template('ml/train.html', version_warning=version_warning, bodyclass='daadminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_file=the_file, the_group_id=the_group_id, package_list=package_list, file_list=file_list, group_id_list=group_id_list, entry_list=entry_list, show_all=show_all, show_package_list=True, playground_package=playground_package), 200)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    if playground_package and the_package == playground_package:
        the_package_display = word("My Playground")
    else:
        the_package_display = the_package
    if the_file is None:
        file_list = {}
        for record in db.session.execute(select(MachineLearning.group_id, db.func.count(MachineLearning.id).label('cnt')).where(and_(MachineLearning.group_id.like(the_package + ':%'), show_cond)).group_by(MachineLearning.group_id)):  # pylint: disable=not-callable
            parts = record.group_id.split(':')
            # logmessage("Group id is " + str(parts))
            if not is_package_ml(parts):
                continue
            if re.match(r'data/sources/ml-.*\.json$', parts[1]):
                parts[1] = re.sub(r'^data/sources/ml-|\.json$', '', parts[1])
            if parts[1] not in file_list:
                file_list[parts[1]] = 0
            file_list[parts[1]] += record.cnt
        if not show_all:
            for record in db.session.execute(select(MachineLearning.group_id).where(MachineLearning.group_id.like(the_package + ':%')).group_by(MachineLearning.group_id)):
                parts = record.group_id.split(':')
                # logmessage("Other group id is " + str(parts))
                if not is_package_ml(parts):
                    continue
                if re.match(r'data/sources/ml-.*\.json$', parts[1]):
                    parts[1] = re.sub(r'^data/sources/ml-|\.json$', '', parts[1])
                if parts[1] not in file_list:
                    file_list[parts[1]] = 0
        if playground_package and the_package == playground_package:
            area = SavedFile(current_user.id, fix=False, section='playgroundsources')
            for filename in area.list_of_files():
                # logmessage("hey file is " + str(filename))
                if re.match(r'ml-.*\.json$', filename):
                    short_file_name = re.sub(r'^ml-|\.json$', '', filename)
                    if short_file_name not in file_list:
                        file_list[short_file_name] = 0
        file_list = [(x, file_list[x]) for x in sorted(file_list)]
        response = make_response(render_template('ml/train.html', version_warning=version_warning, bodyclass='daadminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_package_display=the_package_display, the_file=the_file, the_group_id=the_group_id, package_list=package_list, file_list=file_list, group_id_list=group_id_list, entry_list=entry_list, show_all=show_all, show_file_list=True), 200)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    if the_group_id is None:
        the_prefix = ml_prefix(the_package, the_file)
        the_package_file = package_data_filename(the_prefix)
        package_file_available = bool(the_package_file is not None and os.path.isfile(the_package_file))
        if 'download' in request.args and request.args['download']:
            output = {}
            if the_package == '_global':
                json_filename = 'ml-global.json'
                for record in db.session.execute(select(MachineLearning.id, MachineLearning.group_id, MachineLearning.independent, MachineLearning.dependent, MachineLearning.key)):
                    if is_package_ml(record.group_id.split(':')):
                        continue
                    if record.group_id not in output:
                        output[record.group_id] = []
                    if record.dependent is None:
                        the_dependent = None
                    else:
                        the_dependent = fix_pickle_obj(codecs.decode(bytearray(record.dependent, encoding='utf-8'), 'base64'))
                    the_independent = fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64'))
                    try:
                        str(the_independent) + ""  # pylint: disable=expression-not-assigned
                        str(the_dependent) + ""  # pylint: disable=expression-not-assigned
                    except BaseException as e:
                        logmessage("Bad record: id " + str(record.id) + " where error was " + str(e))
                        continue
                    the_entry = {'independent': fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64')), 'dependent': the_dependent}
                    if record.key is not None:
                        the_entry['key'] = record.key
                    output[record.group_id].append(the_entry)
            else:
                json_filename = 'ml-' + the_file + '.json'
                prefix = ml_prefix(the_package, the_file)
                for record in db.session.execute(select(MachineLearning.group_id, MachineLearning.independent, MachineLearning.dependent, MachineLearning.key).where(MachineLearning.group_id.like(prefix + ':%'))):
                    parts = record.group_id.split(':')
                    if not is_package_ml(parts):
                        continue
                    if parts[2] not in output:
                        output[parts[2]] = []
                    if record.dependent is None:
                        the_dependent = None
                    else:
                        the_dependent = fix_pickle_obj(codecs.decode(bytearray(record.dependent, encoding='utf-8'), 'base64'))
                    the_entry = {'independent': fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64')), 'dependent': the_dependent}
                    if record.key is not None:
                        the_entry['key'] = record.key
                    output[parts[2]].append(the_entry)
            if len(output) > 0:
                the_json_file = tempfile.NamedTemporaryFile(mode='w', prefix="datemp", suffix=".json", delete=False, encoding='utf-8')
                json.dump(output, the_json_file, sort_keys=True, indent=2)
                the_json_file.close()
                response = custom_send_file(the_json_file.name, mimetype='application/json', as_attachment=True, download_name=json_filename)
                response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
                return response
            flash(word("No data existed in training set.  JSON file not created."), "error")
            return redirect(url_for('ml.train', package=the_package, file=the_file, show_all=show_all))
        if the_package == '_global':
            for record in db.session.execute(select(MachineLearning.group_id, db.func.count(MachineLearning.id).label('cnt')).where(show_cond).group_by(MachineLearning.group_id)):  # pylint: disable=not-callable
                if is_package_ml(record.group_id.split(':')):
                    continue
                if record.group_id not in group_id_list:
                    group_id_list[record.group_id] = 0
                group_id_list[record.group_id] += record.cnt
            if not show_all:
                for record in db.session.execute(select(MachineLearning.group_id).group_by(MachineLearning.group_id)):
                    if is_package_ml(record.group_id.split(':')):
                        continue
                    if record.group_id not in group_id_list:
                        group_id_list[record.group_id] = 0
        else:
            the_prefix = ml_prefix(the_package, the_file)
            # logmessage("My prefix is " + the_prefix)
            for record in db.session.execute(select(MachineLearning.group_id, db.func.count(MachineLearning.id).label('cnt')).where(and_(MachineLearning.group_id.like(the_prefix + ':%'), show_cond)).group_by(MachineLearning.group_id)):  # pylint: disable=not-callable
                parts = record.group_id.split(':')
                if not is_package_ml(parts):
                    continue
                if parts[2] not in group_id_list:
                    group_id_list[parts[2]] = 0
                group_id_list[parts[2]] += record.cnt
            if not show_all:
                for record in db.session.execute(select(MachineLearning.group_id).where(MachineLearning.group_id.like(the_prefix + ':%')).group_by(MachineLearning.group_id)):
                    parts = record.group_id.split(':')
                    if not is_package_ml(parts):
                        continue
                    if parts[2] not in group_id_list:
                        group_id_list[parts[2]] = 0
        if the_package != '_global' and not re.search(r'^data/', the_file):
            interview = get_corresponding_interview(the_package, the_file)
            if interview is not None and len(interview.mlfields):
                for saveas in interview.mlfields:
                    if 'ml_group' in interview.mlfields[saveas] and not interview.mlfields[saveas]['ml_group'].uses_mako:
                        the_saveas = interview.mlfields[saveas]['ml_group'].original_text
                    else:
                        the_saveas = saveas
                    if not re.search(r':', the_saveas):
                        if the_saveas not in group_id_list:
                            group_id_list[the_saveas] = 0
        group_id_list = [(x, group_id_list[x]) for x in sorted(group_id_list)]
        response = make_response(render_template('ml/train.html', extra_js=Markup(extra_js), version_warning=version_warning, bodyclass='daadminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_package_display=the_package_display, the_file=the_file, the_group_id=the_group_id, package_list=package_list, file_list=file_list, group_id_list=group_id_list, entry_list=entry_list, show_all=show_all, show_group_id_list=True, package_file_available=package_file_available, the_package_location=the_prefix, uploadform=uploadform), 200)
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        return response
    group_id_to_use = fix_group_id(the_package, the_file, the_group_id)
    model = SimpleTextMachineLearner(group_id=group_id_to_use)
    for record in db.session.execute(select(MachineLearning.id, MachineLearning.group_id, MachineLearning.key, MachineLearning.info, MachineLearning.independent, MachineLearning.dependent, MachineLearning.create_time, MachineLearning.modtime, MachineLearning.active).where(and_(MachineLearning.group_id == group_id_to_use, show_cond))):
        new_entry = {'id': record.id, 'group_id': record.group_id, 'key': record.key, 'independent': fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64')) if record.independent is not None else None, 'dependent': fix_pickle_obj(codecs.decode(bytearray(record.dependent, encoding='utf-8'), 'base64')) if record.dependent is not None else None, 'info': fix_pickle_obj(codecs.decode(bytearray(record.info, encoding='utf-8'), 'base64')) if record.info is not None else None, 'create_type': record.create_time, 'modtime': record.modtime, 'active': MachineLearning.active}
        if new_entry['dependent'] is None and new_entry['active'] is True:
            new_entry['active'] = False
        if isinstance(new_entry['independent'], (DADict, dict)):
            new_entry['independent_display'] = '<div class="damldatacontainer">' + '<br>'.join(['<span class="damldatakey">' + str(key) + '</span>: <span class="damldatavalue">' + str(val) + ' (' + str(val.__class__.__name__) + ')</span>' for key, val in new_entry['independent'].items()]) + '</div>'
            new_entry['type'] = 'data'
        else:
            new_entry['type'] = 'text'
        if new_entry['dependent'] is None:
            new_entry['predictions'] = model.predict(new_entry['independent'], probabilities=True)
            if len(new_entry['predictions']) == 0:
                new_entry['predictions'] = None
            elif len(new_entry['predictions']) > 10:
                new_entry['predictions'] = new_entry['predictions'][0:10]
            if new_entry['predictions'] is not None:
                new_entry['predictions'] = [(prediction, '%d%%' % (100.0*probability)) for prediction, probability in new_entry['predictions']]
        else:
            new_entry['predictions'] = None
        if new_entry['info'] is not None:
            if isinstance(new_entry['info'], DAFile):
                image_file_list = [new_entry['info']]
            elif isinstance(new_entry['info'], DAFileList):
                image_file_list = new_entry['info']
            else:
                logmessage("train: info is not a DAFile or DAFileList")
                continue
            new_entry['image_files'] = []
            for image_file in image_file_list:
                if not isinstance(image_file, DAFile):
                    logmessage("train: file is not a DAFile")
                    continue
                if not image_file.ok:
                    logmessage("train: file does not have a number")
                    continue
                if image_file.extension not in ('pdf', 'png', 'jpg', 'jpeg', 'gif'):
                    logmessage("train: file did not have a recognizable image type")
                    continue
                doc_url = get_url_from_file_reference(image_file, {})
                if image_file.extension == 'pdf':
                    image_url = get_url_from_file_reference(image_file, {"size": "screen", "page": 1, "ext": 'pdf'})
                else:
                    image_url = doc_url
                new_entry['image_files'].append({'doc_url': doc_url, 'image_url': image_url})
        entry_list.append(new_entry)
    if len(entry_list) == 0:
        record = db.session.execute(select(MachineLearning.independent).where(and_(MachineLearning.group_id == group_id_to_use, MachineLearning.independent != None))).first()  # noqa: E711 # pylint: disable=singleton-comparison
        if record is not None:
            sample_indep = fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64'))
        else:
            sample_indep = None
    else:
        sample_indep = entry_list[0]['independent']
    is_data = isinstance(sample_indep, (DADict, dict))
    choices = {}
    for record in db.session.execute(select(MachineLearning.dependent, db.func.count(MachineLearning.id).label('cnt')).where(and_(MachineLearning.group_id == group_id_to_use)).group_by(MachineLearning.dependent)):  # pylint: disable=not-callable
        # logmessage("There is a choice")
        if record.dependent is None:
            continue
        key = fix_pickle_obj(codecs.decode(bytearray(record.dependent, encoding='utf-8'), 'base64'))
        if key is not None:
            choices[key] = record.cnt
    if len(choices) > 0:
        # logmessage("There are choices")
        choices = [(x, choices[x]) for x in sorted(choices, key=operator.itemgetter(0), reverse=False)]
    else:
        # logmessage("There are no choices")
        choices = None
    response = make_response(render_template('ml/train.html', extra_js=Markup(extra_js), form=form, version_warning=version_warning, bodyclass='daadminbody', tab_title=word("Train"), page_title=word("Train machine learning models"), the_package=the_package, the_package_display=the_package_display, the_file=the_file, the_group_id=the_group_id, entry_list=entry_list, choices=choices, show_all=show_all, show_entry_list=True, is_data=is_data), 200)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    return response
