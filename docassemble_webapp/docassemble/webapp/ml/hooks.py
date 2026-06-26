import datetime
import json
import re
import codecs
import pickle
import os
from sqlalchemy import select
from docassemble.base.functions import package_data_filename
from docassemble.webapp.develop.common import project_name
from docassemble.webapp.extensions import db
from docassemble.webapp.files.savedfile import SavedFile
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.utils.fixpickle import fix_pickle_obj
from docassemble.webapp.utils.logger import logmessage
from .common import is_package_ml
from .models import MachineLearning

@hookimpl
def write_ml_source(playground, playground_number, current_project, filename, finalize):
    if re.match(r'ml-.*\.json', filename):
        output = {}
        prefix = 'docassemble.playground' + str(playground_number) + project_name(current_project) + ':data/sources/' + str(filename)
        for record in db.session.execute(select(MachineLearning.group_id, MachineLearning.independent, MachineLearning.dependent, MachineLearning.key).where(MachineLearning.group_id.like(prefix + ':%'))).all():
            parts = record.group_id.split(':')
            if not is_package_ml(parts):
                continue
            if parts[2] not in output:
                output[parts[2]] = []
            the_independent = record.independent
            if the_independent is not None:
                the_independent = fix_pickle_obj(codecs.decode(bytearray(the_independent, encoding='utf-8'), 'base64'))
            the_dependent = record.dependent
            if the_dependent is not None:
                the_dependent = fix_pickle_obj(codecs.decode(bytearray(the_dependent, encoding='utf-8'), 'base64'))
            the_entry = {'independent': the_independent, 'dependent': the_dependent}
            if record.key is not None:
                the_entry['key'] = record.key
            output[parts[2]].append(the_entry)
        if len(output) > 0:
            playground.write_as_json(output, filename=filename, project=current_project)
            if finalize:
                playground.finalize()
            return True
    return False

@hookimpl
def fix_ml_files(playground_number, current_project):
    playground = SavedFile(playground_number, section='playgroundsources', fix=False)
    changed = False
    for filename in playground.list_of_files():
        if re.match(r'^ml-.*\.json', filename):
            playground.fix()
            try:
                if write_ml_source(playground, playground_number, current_project, filename, finalize=False):
                    changed = True
            except:
                logmessage("Error writing machine learning source file " + str(filename))
    if changed:
        playground.finalize()

@hookimpl
def ensure_training_loaded(interview):
    # parts = yaml_filename.split(':')
    # if len(parts) != 2:
    #     logmessage("ensure_training_loaded: could not read yaml_filename " + str(yaml_filename))
    #     return
    # source_filename = parts[0] + ':data/sources/ml-' + re.sub(r'\.ya?ml$', '', re.sub(r'.*/', '', parts[1])) + '.json'
    # logmessage("Source filename is " + source_filename)
    source_filename = interview.get_ml_store()
    parts = source_filename.split(':')
    if len(parts) == 3 and parts[0].startswith('docassemble.') and re.match(r'data/sources/.*\.json$', parts[1]):
        the_file = package_data_filename(source_filename)
        if the_file is not None:
            record = db.session.execute(select(MachineLearning.group_id).where(MachineLearning.group_id.like(source_filename + ':%'))).first()
            if record is None:
                if os.path.isfile(the_file):
                    with open(the_file, 'r', encoding='utf-8') as fp:
                        content = fp.read()
                    if len(content) > 0:
                        try:
                            href = json.loads(content)
                            if isinstance(href, dict):
                                nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                                for group_id, train_list in href.items():
                                    if isinstance(train_list, list):
                                        for entry in train_list:
                                            if 'independent' in entry:
                                                depend = entry.get('dependent', None)
                                                if depend is not None:
                                                    new_entry = MachineLearning(group_id=source_filename + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(depend), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None))
                                                else:
                                                    new_entry = MachineLearning(group_id=source_filename + ':' + group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=False, key=entry.get('key', None))
                                                db.session.add(new_entry)
                                db.session.commit()
                            else:
                                logmessage("ensure_training_loaded: source filename " + source_filename + " not used because it did not contain a dict")
                        except:
                            logmessage("ensure_training_loaded: source filename " + source_filename + " not used because it did not contain valid JSON")
                    else:
                        logmessage("ensure_training_loaded: source filename " + source_filename + " not used because its content was empty")
                else:
                    logmessage("ensure_training_loaded: source filename " + source_filename + " not used because it did not exist")
            else:
                logmessage("ensure_training_loaded: source filename " + source_filename + " not used because training data existed")
        else:
            logmessage("ensure_training_loaded: source filename " + source_filename + " did not exist")
    else:
        logmessage("ensure_training_loaded: source filename " + source_filename + " was not part of a package")
