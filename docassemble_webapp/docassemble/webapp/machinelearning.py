import re
import random
import codecs
import pickle
import datetime
import os
import json
import threading
from sqlalchemy import and_, select, delete
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from pandas.api.types import CategoricalDtype
import numpy as np
import yaml
from docassemble_pattern.vector import KNN, SVM, PORTER, Document
from docassemble.base.util import DAObject, DAList, DADict
from docassemble.base.error import DAException
# from docassemble.base.logger import logmessage
from docassemble.webapp.backend import get_info_from_file_reference
from docassemble.webapp.core.models import MachineLearning
from docassemble.webapp.db_object import db
from docassemble.webapp.fixpickle import fix_pickle_obj
import docassemble.base.functions


class MlLocal(threading.local):

    def __init__(self):
        super().__init__()
        self.learners = {}
        self.lastmodtime = {}
        self.reset_counter = {}

ml_thread = MlLocal()


class MachineLearningEntry(DAObject):
    """An entry in the machine learning system"""

    def classify(self, dependent=None):
        """Sets the dependent variable of the machine learning entry"""
        if dependent is not None:
            self.dependent = dependent
        self.ml.set_dependent_by_id(self.id, self.dependent)
        return self

    def save(self):
        """Saves the entry to the data set.  The independent variable must be
        defined in order to save."""
        args = {'independent': self.independent}
        if hasattr(self, 'dependent') and self.dependent is not None:
            args['dependent'] = self.dependent
        if hasattr(self, 'key'):
            args['key'] = self.key
        if hasattr(self, 'id'):
            args['id'] = self.id
        if hasattr(self, 'info') and self.info is not None:
            args['info'] = self.info
        self.ml._save_entry(**args)
        return self

    def predict(self, probabilities=False):
        """Returns predictions for this entry's independent variable."""
        return self.ml.predict(self.independent, probabilities=probabilities)


class MachineLearner:
    """Base class for machine learning objects"""

    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0:
            if ':' in pargs[0]:
                raise DAException("MachineLearner: you cannot use a colon in a machine learning name")
            question = docassemble.base.functions.get_current_question()
            if question is not None:
                self.group_id = question.interview.get_ml_store() + ':' + pargs[0]
            else:
                self.group_id = pargs[0]
        if len(pargs) > 1:
            self.initial_file = pargs[1]
        if 'group_id' in kwargs:
            self.group_id = kwargs['group_id']
        if 'initial_file' in kwargs:
            self.initial_file = kwargs['initial_file']
        if kwargs.get('use_initial_file', False):
            question = docassemble.base.functions.get_current_question()
            if question is not None:
                self.initial_file = question.interview.get_ml_store()
        self.reset_counter = 0

    def reset(self):
        self.reset_counter += 1

    def _initialize(self, reset=False):
        if hasattr(self, 'initial_file'):
            self.start_from_file(self.initial_file)
        if hasattr(self, 'group_id'):
            if not reset and (self.group_id not in ml_thread.reset_counter or ml_thread.reset_counter[self.group_id] != self.reset_counter):
                reset = True
            if reset:
                ml_thread.lastmodtime[self.group_id] = datetime.datetime(year=1970, month=1, day=1)
                ml_thread.reset_counter[self.group_id] = self.reset_counter

    def export_training_set(self, output_format='json', key=None):
        self._initialize()
        output = []
        for entry in self.classified_entries(key=key):
            the_entry = {'independent': entry.independent, 'dependent': entry.dependent}
            if entry.info is not None:
                the_entry['info'] = entry.info
            output.append(the_entry)
        if output_format == 'json':
            return json.dumps(output, sort_keys=True, indent=4)
        if output_format == 'yaml':
            return yaml.safe_dump(output, default_flow_style=False)
        raise DAException("Unknown output format " + str(output_format))

    def dependent_in_use(self, key=None):
        in_use = set()
        if key is None:
            query = db.session.execute(select(MachineLearning.dependent).where(MachineLearning.group_id == self.group_id).group_by(MachineLearning.dependent))
        else:
            query = db.session.execute(select(MachineLearning.dependent).where(and_(MachineLearning.group_id == self.group_id, MachineLearning.key == key)).group_by(MachineLearning.dependent))
        for record in query:
            if record.dependent is not None:
                depend = fix_pickle_obj(codecs.decode(bytearray(record.dependent, encoding='utf-8'), 'base64'))
                if depend is not None:
                    in_use.add(depend)
        return sorted(in_use)

    def is_empty(self):
        existing_entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id)).first()
        if existing_entry is None:
            return True
        return False

    def start_from_file(self, fileref):
        # logmessage("Starting from file " + str(fileref))
        existing_entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id)).first()
        if existing_entry is not None:
            return
        file_info = get_info_from_file_reference(fileref, folder='sources')
        if 'fullpath' not in file_info or file_info['fullpath'] is None or not os.path.exists(file_info['fullpath']):
            return
            # raise DAException("File reference " + str(fileref) + " is invalid")
        with open(file_info['fullpath'], 'r', encoding='utf-8') as fp:
            content = fp.read()
        if 'mimetype' in file_info and file_info['mimetype'] == 'application/json':
            aref = json.loads(content)
        elif 'extension' in file_info and file_info['extension'].lower() in ['yaml', 'yml']:
            aref = yaml.load(content, Loader=yaml.FullLoader)
        if isinstance(aref, dict) and hasattr(self, 'group_id'):
            the_group_id = re.sub(r'.*:', '', self.group_id)
            if the_group_id in aref:
                aref = aref[the_group_id]
        if isinstance(aref, list):
            nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            for entry in aref:
                if 'independent' in entry:
                    depend = entry.get('dependent', None)
                    if depend is not None:
                        new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(depend), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None), info=codecs.encode(pickle.dumps(entry['info']), 'base64').decode() if entry.get('info', None) is not None else None)
                    else:
                        new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=False, key=entry.get('key', None), info=codecs.encode(pickle.dumps(entry['info']), 'base64').decode() if entry.get('info', None) is not None else None)
                    db.session.add(new_entry)
            db.session.commit()

    def add_to_training_set(self, independent, dependent, key=None, info=None):
        self._initialize()
        nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        if dependent is not None:
            new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(independent), 'base64').decode(), dependent=codecs.encode(pickle.dumps(dependent), 'base64').decode(), info=codecs.encode(pickle.dumps(info), 'base64').decode() if info is not None else None, create_time=nowtime, modtime=nowtime, active=True, key=key)
        else:
            new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(independent), 'base64').decode(), info=codecs.encode(pickle.dumps(info), 'base64').decode() if info is not None else None, create_time=nowtime, modtime=nowtime, active=False, key=key)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id

    def save_for_classification(self, indep, key=None, info=None):
        self._initialize()
        if key is None:
            existing_entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, dependent=None, independent=codecs.encode(pickle.dumps(indep), 'base64').decode())).scalar()
        else:
            existing_entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, dependent=None, key=key, independent=codecs.encode(pickle.dumps(indep), 'base64').decode())).scalar()
        if existing_entry is not None:
            # logmessage("entry is already there")
            return existing_entry.id
        new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(indep), 'base64').decode(), create_time=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None), active=False, key=key, info=codecs.encode(pickle.dumps(info), 'base64').decode() if info is not None else None)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id

    def retrieve_by_id(self, the_id):
        self._initialize()
        existing_entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, id=the_id)).scalar()
        if existing_entry is None:
            raise DAException("There was no entry in the database for id " + str(the_id) + " with group id " + str(self.group_id))
        if existing_entry.dependent:
            dependent = fix_pickle_obj(codecs.decode(bytearray(existing_entry.dependent, encoding='utf-8'), 'base64'))
            if dependent is not None:
                return MachineLearningEntry(ml=self, id=existing_entry.id, independent=fix_pickle_obj(codecs.decode(bytearray(existing_entry.independent, encoding='utf-8'), 'base64')), dependent=dependent, create_time=existing_entry.create_time, key=existing_entry.key, info=fix_pickle_obj(codecs.decode(bytearray(existing_entry.info, encoding='utf-8'), 'base64')) if existing_entry.info is not None else None)
        return MachineLearningEntry(ml=self, id=existing_entry.id, independent=fix_pickle_obj(codecs.decode(bytearray(existing_entry.independent, encoding='utf-8'), 'base64')), create_time=existing_entry.create_time, key=existing_entry.key, info=fix_pickle_obj(codecs.decode(bytearray(existing_entry.info, encoding='utf-8'), 'base64')) if existing_entry.info is not None else None)

    def one_unclassified_entry(self, key=None):
        self._initialize()
        if key is None:
            entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, active=False).order_by(MachineLearning.id)).scalar()
        else:
            entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, key=key, active=False).order_by(MachineLearning.id)).scalar()
        if entry is None:
            return None
        return MachineLearningEntry(ml=self, id=entry.id, independent=fix_pickle_obj(codecs.decode(bytearray(entry.independent, encoding='utf-8'), 'base64')), create_time=entry.create_time, key=entry.key, info=fix_pickle_obj(codecs.decode(bytearray(entry.info, encoding='utf-8'), 'base64')) if entry.info is not None else None)._set_instance_name_for_method()

    def new_entry(self, **kwargs):
        return MachineLearningEntry(ml=self, **kwargs)._set_instance_name_for_method()

    def unclassified_entries(self, key=None):
        self._initialize()
        results = DAList()._set_instance_name_for_method()
        results.gathered = True
        if key is None:
            query = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, active=False).order_by(MachineLearning.id)).scalars()
        else:
            query = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, key=key, active=False).order_by(MachineLearning.id)).scalars()
        for entry in query:
            results.appendObject(MachineLearningEntry, ml=self, id=entry.id, independent=fix_pickle_obj(codecs.decode(bytearray(entry.independent, encoding='utf-8'), 'base64')), create_time=entry.create_time, key=entry.key, info=fix_pickle_obj(codecs.decode(bytearray(entry.info, encoding='utf-8'), 'base64')) if entry.info is not None else None)
        return results

    def classified_entries(self, key=None):
        self._initialize()
        results = DAList()
        results.gathered = True
        results.set_random_instance_name()
        if key is None:
            query = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, active=True).order_by(MachineLearning.id)).scalars()
        else:
            query = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, active=True, key=key).order_by(MachineLearning.id)).scalars()
        for entry in query:
            depend = fix_pickle_obj(codecs.decode(bytearray(entry.dependent, encoding='utf-8'), 'base64'))
            if depend is not None:
                results.appendObject(MachineLearningEntry, ml=self, id=entry.id, independent=fix_pickle_obj(codecs.decode(bytearray(entry.independent, encoding='utf-8'), 'base64')), dependent=depend, info=fix_pickle_obj(codecs.decode(bytearray(entry.info, encoding='utf-8'), 'base64')) if entry.info is not None else None, create_time=entry.create_time, key=entry.key)
        return results

    def _save_entry(self, **kwargs):
        self._initialize()
        the_id = kwargs.get('id', None)
        need_to_reset = False
        if the_id is None:
            the_entry = MachineLearning(group_id=self.group_id)
            existing = False
        else:
            the_entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, id=the_id)).scalar()
            if the_entry is None:
                raise DAException("There was no entry in the database for id " + str(the_id) + " with group id " + str(self.group_id))
            existing = True
        if 'dependent' in kwargs:
            depend = codecs.encode(pickle.dumps(kwargs['dependent']), 'base64').decode()
            if existing and the_entry.dependent is not None and the_entry.dependent != depend:
                need_to_reset = True
            if kwargs['dependent'] is not None:
                the_entry.dependent = depend
                the_entry.active = True
        if 'independent' in kwargs:
            indep = codecs.encode(pickle.dumps(kwargs['independent']), 'base64').decode()
            if existing and the_entry.independent is not None and the_entry.independent != indep:
                need_to_reset = True
            the_entry.independent = indep
        if 'key' in kwargs:
            the_entry.key = kwargs['key']
        if 'info' in kwargs:
            the_entry.info = codecs.encode(pickle.dumps(kwargs['info']), 'base64').decode()
        the_entry.modtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        if not existing:
            db.session.add(the_entry)
        db.session.commit()
        if need_to_reset:
            self.reset()

    def set_dependent_by_id(self, the_id, the_dependent):
        self._initialize()
        existing_entry = db.session.execute(select(MachineLearning).filter_by(group_id=self.group_id, id=the_id).with_for_update()).scalar()
        if existing_entry is None:
            db.session.commit()
            raise DAException("There was no entry in the database for id " + str(the_id) + " with group id " + str(self.group_id))
        existing_entry.modtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        if the_dependent is None:
            existing_entry.dependent = None
            existing_entry.active = False
        else:
            existing_entry.dependent = codecs.encode(pickle.dumps(the_dependent), 'base64').decode()
            existing_entry.active = True
        db.session.commit()

    def delete_by_id(self, the_id):
        self._initialize()
        db.session.execute(delete(MachineLearning).filter_by(group_id=self.group_id, id=the_id))
        db.session.commit()
        self.reset()

    def delete_by_key(self, key):
        self._initialize()
        db.session.execute(delete(MachineLearning).filter_by(group_id=self.group_id, key=key))
        db.session.commit()
        self.reset()

    def save(self):
        db.session.commit()

    def _train_from_db(self):
        # logmessage("Doing train_from_db where group_id is " + self.group_id + " and lastmodtime is " + repr(ml_thread.lastmodtime[self.group_id]))
        self._initialize()
        nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        success = False
        for record in db.session.execute(select(MachineLearning.independent, MachineLearning.dependent).where(and_(MachineLearning.group_id == self.group_id, MachineLearning.active == True, MachineLearning.modtime > ml_thread.lastmodtime[self.group_id]))).all():  # noqa: E712 # pylint: disable=singleton-comparison
            # logmessage("Training...")
            if record.dependent is not None and record.independent is not None:
                indep = fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64'))
                depend = fix_pickle_obj(codecs.decode(bytearray(record.dependent, encoding='utf-8'), 'base64'))
                if indep is not None and depend is not None:
                    self._train(indep, depend)
                    success = True
        ml_thread.lastmodtime[self.group_id] = nowtime
        return success

    def delete_training_set(self):
        self._initialize()
        db.session.execute(delete(MachineLearning).filter_by(group_id=self.group_id))
        db.session.commit()

    def _train(self, indep, depend):
        pass

    def _predict(self, indep):
        pass


class SimpleTextMachineLearner(MachineLearner):
    """A class used to interact with the machine learning system, using the K Nearest Neighbors method"""

    def _learner(self):
        return KNN()

    def _initialize(self, reset=False):
        """Initializes a fresh machine learner."""
        if reset or self.group_id not in ml_thread.learners:
            ml_thread.learners[self.group_id] = self._learner()
            reset = True
        super()._initialize(reset=reset)

    def _train(self, indep, depend):
        """Trains the machine learner given an independent variable and a corresponding dependent variable."""
        if indep is None:
            return
        the_text = re.sub(r'[\n\r]+', r'  ', indep).lower()
        ml_thread.learners[self.group_id].train(Document(the_text.lower(), stemmer=PORTER), depend)

    def predict(self, indep, probabilities=False):
        """Returns a list of predicted dependent variables for a given independent variable."""
        indep = re.sub(r'[\n\r]+', r'  ', indep).lower()
        self._train_from_db()
        probs = {}
        for key, value in ml_thread.learners[self.group_id].classify(Document(indep.lower(), stemmer=PORTER), discrete=False).items():
            probs[key] = value
        if len(probs) == 0:
            single_result = ml_thread.learners[self.group_id].classify(Document(indep.lower(), stemmer=PORTER))
            if single_result is not None:
                probs[single_result] = 1.0
        if probabilities:
            return [(x, probs[x]) for x in sorted(probs.keys(), key=probs.get, reverse=True)]
        return sorted(probs.keys(), key=probs.get, reverse=True)

    def confusion_matrix(self, key=None, output_format=None, split=False):
        """Returns a confusion matrix for the model based on splitting the data set randomly into two pieces, training on one and testing on the other"""
        if split:
            list_of_dependent = self.dependent_in_use(key=key)
        else:
            list_of_dependent = [None]
        output = ''
        matrices = {}
        for current_dep in list_of_dependent:
            testing_set = []
            model = self._learner()
            for record in self.classified_entries(key=key):
                if split:
                    dep_result = str(record.dependent == current_dep)
                else:
                    dep_result = record.dependent
                if random.random() < 0.5:
                    model.train(Document(record.independent.lower(), stemmer=PORTER), dep_result)
                else:
                    testing_set.append((Document(record.independent.lower(), stemmer=PORTER), dep_result))
            matrix = model.confusion_matrix(documents=testing_set)
            matrices[current_dep] = matrix
            if output_format == 'html':
                if split:
                    output += '<h4>' + current_dep + "</h4>"
                vals = matrix.keys()
                output += '<table class="table table-bordered"><thead><tr><td></td><td></td><td style="text-align: center" colspan="' + str(len(vals)) + '">Actual</td></tr><tr><th></th><th></th>'
                first = True
                for val in vals:
                    output += '<th>' + val + '</th>'
                output += '</tr></thead><tbody>'
                for val_a in vals:
                    output += '<tr>'
                    if first:
                        output += '<td style="text-align: right; vertical-align: middle;" rowspan="' + str(len(vals)) + '">Predicted</td>'
                        first = False
                    output += '<th>' + val_a + '</th>'
                    for val_b in vals:
                        output += '<td>' + str(matrix[val_b].get(val_a, 0)) + '</td>'
                    output += '</tr>'
                output += '</tbody></table>'
                # output += "\n\n`" + str(matrix) + "`"
                # output += '<ul>'
                # for document, actual in testing_set:
                #     predicted = model.classify(document)
                #     output += '<li>Predicted: ' + predicted + '; Actual: ' + actual + '</li>'
                # output += '</ul>'
        if output_format == 'html':
            return output
        if split:
            ret_val = matrices
        else:
            ret_val = matrices[None]
        if output_format == 'json':
            return json.dumps(ret_val, sort_keys=True, indent=4)
        if output_format == 'yaml':
            return yaml.safe_dump(ret_val, default_flow_style=False)
        if output_format is None:
            return ret_val
        return ret_val

    def delete_by_key(self, key):
        """Deletes all of the training data in the database that was added with a given key"""
        return super().delete_training_set(key)

    def classified_entries(self, key=None):
        """Returns a list of entries in the data that have been classified."""
        return super().classified_entries(key=key)

    def unclassified_entries(self, key=None):
        """Returns a list of entries in the data that have not yet been classified."""
        return super().unclassified_entries(key=key)

    def one_unclassified_entry(self, key=None):
        """Returns the first entry in the data that has not yet been classified, or None if all entries have been classified."""
        return super().one_unclassified_entry(key=key)

    def save_for_classification(self, indep, key=None, info=None):
        """Creates a not-yet-classified entry in the data for the given independent variable and returns the ID of the entry."""
        return super().save_for_classification(indep, key=key, info=info)

    def dependent_in_use(self, key=None):
        """Returns a sorted list of unique dependent variables in the data."""
        return super().dependent_in_use(key=key)


class SVMMachineLearner(SimpleTextMachineLearner):
    """Machine Learning object using the Symmetric Vector Machine method"""

    def _learner(self):
        return SVM(extension='libsvm')


class RandomForestMachineLearner(MachineLearner):

    def _learner(self):
        return RandomForestClassifier()

    def feature_importances(self):
        """Returns the importances of each of the features"""
        if not self._train_from_db():
            return []
        return ml_thread.learners[self.group_id]['learner'].feature_importances_

    def _initialize(self, reset=False):
        """Initializes a fresh machine learner."""
        if not reset and (self.group_id not in ml_thread.reset_counter or self.reset_counter != ml_thread.reset_counter[self.group_id]):
            reset = True
        if hasattr(self, 'group_id') and (reset or self.group_id not in ml_thread.learners):
            ml_thread.learners[self.group_id] = {'learner': self._learner(), 'dep_type': None, 'indep_type': {}, 'indep_categories': {}, 'dep_categories': None}
        super()._initialize(reset=reset)

    def _train_from_db(self):
        # logmessage("Doing train_from_db")
        self._initialize()
        nowtime = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
        success = False
        data = []
        depend_data = []
        detected_columns = set()
        for record in db.session.execute(select(MachineLearning).where(and_(MachineLearning.group_id == self.group_id, MachineLearning.active == True, MachineLearning.modtime > ml_thread.lastmodtime[self.group_id]))).scalars().all():  # noqa: E712 # pylint: disable=singleton-comparison
            if record.independent is None or record.dependent is None:
                continue
            indep_var = fix_pickle_obj(codecs.decode(bytearray(record.independent, encoding='utf-8'), 'base64'))
            depend_var = fix_pickle_obj(codecs.decode(bytearray(record.dependent, encoding='utf-8'), 'base64'))
            if depend_var is None:
                continue
            if isinstance(depend_var, str):
                depend_var = str(depend_var)
            if ml_thread.learners[self.group_id]['dep_type'] is not None:
                if not isinstance(depend_var, ml_thread.learners[self.group_id]['dep_type']):
                    if isinstance(depend_var, int) and ml_thread.learners[self.group_id]['dep_type'] is float:
                        depend_var = float(depend_var)
                    elif isinstance(depend_var, float) and ml_thread.learners[self.group_id]['dep_type'] is int:
                        ml_thread.learners[self.group_id]['dep_type'] = float
                    else:
                        raise DAException("RandomForestMachineLearner: dependent variable type was not consistent")
            else:
                if not isinstance(depend_var, (str, int, bool, float)):
                    raise DAException("RandomForestMachineLearner: dependent variable type was not a standard variable type")
                ml_thread.learners[self.group_id]['dep_type'] = type(depend_var)
            depend_data.append(depend_var)
            if isinstance(indep_var, DADict):
                indep_var = indep_var.elements
            if not isinstance(indep_var, dict):
                raise DAException("RandomForestMachineLearner: independent variable was not a dictionary")
            for key, val in indep_var.items():
                detected_columns.add(key)
                if isinstance(val, str):
                    val = str(val)
                if key in ml_thread.learners[self.group_id]['indep_type']:
                    if not isinstance(val, ml_thread.learners[self.group_id]['indep_type'][key]):
                        if isinstance(val, int) and ml_thread.learners[self.group_id]['indep_type'][key] is float:
                            val = float(val)
                        elif isinstance(val, float) and ml_thread.learners[self.group_id]['indep_type'][key] is int:
                            ml_thread.learners[self.group_id]['indep_type'][key] = float
                        else:
                            raise DAException("RandomForestMachineLearner: independent variable type for key " + repr(key) + " was not consistent")
                else:
                    if not isinstance(val, (str, int, bool, float)):
                        raise DAException("RandomForestMachineLearner: independent variable type for key " + repr(key) + " was not a standard variable type")
                    ml_thread.learners[self.group_id]['indep_type'][key] = type(val)
            data.append(indep_var)
            success = True
        if success:
            df = pd.DataFrame(data, columns=sorted(detected_columns))
            for key, val in ml_thread.learners[self.group_id]['indep_type'].items():
                if val is str:
                    df[key] = pd.Series(df[key], dtype="category")
                    ml_thread.learners[self.group_id]['indep_categories'][key] = df[key].cat.categories
            df = pd.get_dummies(df, dummy_na=True)
            if ml_thread.learners[self.group_id]['dep_type'] is str:
                y = pd.Series(depend_data, dtype="category")
                ml_thread.learners[self.group_id]['dep_categories'] = y.cat.categories
            else:
                y = pd.Series(depend_data)
            ml_thread.learners[self.group_id]['learner'].fit(df, list(y))
            ml_thread.lastmodtime[self.group_id] = nowtime
        return success

    def predict(self, indep, probabilities=False):
        """Returns a list of predicted dependent variables for a given independent variable."""
        self._train_from_db()
        if isinstance(indep, DADict):
            indep = indep.elements
        if not isinstance(indep, dict):
            raise DAException("RandomForestMachineLearner: independent variable was not a dictionary")
        indep = process_independent_data(indep)
        indep_to_use = {}
        for key, val in indep.items():
            if key in ml_thread.learners[self.group_id]['indep_type']:
                if isinstance(val, str):
                    val = str(val)
                if not isinstance(val, ml_thread.learners[self.group_id]['indep_type'][key]):
                    if isinstance(val, int) and ml_thread.learners[self.group_id]['indep_type'][key] is float:
                        val = float(val)
                    elif isinstance(val, float) and ml_thread.learners[self.group_id]['indep_type'][key] is int:
                        ml_thread.learners[self.group_id]['indep_type'][key] = float
                    else:
                        raise DAException("RandomForestMachineLearner: the independent variable type for key " + repr(key) + " was not consistent.  Stored was " + str(ml_thread.learners[self.group_id]['indep_type'][key]) + " and type was " + str(type(val)))
            else:
                raise DAException("RandomForestMachineLearner: independent variable key " + repr(key) + " was not recognized")
            if isinstance(val, str):
                if val not in ml_thread.learners[self.group_id]['indep_categories'][key]:
                    val = np.nan
            indep_to_use[key] = val
        df = pd.DataFrame([indep_to_use], columns=sorted(indep_to_use.keys()))
        for key, val in indep_to_use.items():
            if ml_thread.learners[self.group_id]['indep_type'][key] is str:
                # df[key] = pd.Series(df[key]).astype('category', categories=ml_thread.learners[self.group_id]['indep_categories'][key])
                df[key] = pd.Series(df[key]).astype(CategoricalDtype(ml_thread.learners[self.group_id]['indep_categories'][key]))
        df = pd.get_dummies(df, dummy_na=True)
        pred = ml_thread.learners[self.group_id]['learner'].predict_proba(df)
        indexno = 0
        result = []
        for x in pred[0]:
            result.append((ml_thread.learners[self.group_id]['dep_categories'][indexno], x))
            indexno += 1
        result = sorted(result, key=lambda x: x[1], reverse=True)
        if probabilities:
            return result
        return [x[0] for x in result]

    def delete_by_key(self, key):
        """Deletes all of the training data in the database that was added with a given key"""
        return super().delete_training_set(key)

    def classified_entries(self, key=None):
        """Returns a list of entries in the data that have been classified."""
        return super().classified_entries(key=key)

    def unclassified_entries(self, key=None):
        """Returns a list of entries in the data that have not yet been classified."""
        return super().unclassified_entries(key=key)

    def one_unclassified_entry(self, key=None):
        """Returns the first entry in the data that has not yet been classified, or None if all entries have been classified."""
        return super().one_unclassified_entry(key=key)

    def save_for_classification(self, indep, key=None, info=None):
        """Creates a not-yet-classified entry in the data for the given independent variable and returns the ID of the entry."""
        indep = process_independent_data(indep)
        return super().save_for_classification(indep, key=key, info=info)

    def add_to_training_set(self, independent, dependent, key=None, info=None):
        """Creates an entry in the data for the given independent and dependent variable and returns the ID of the entry."""
        independent = process_independent_data(independent)
        return super().add_to_training_set(independent, dependent, key=key, info=info)

    def dependent_in_use(self, key=None):
        """Returns a sorted list of unique dependent variables in the data."""
        return super().dependent_in_use(key=key)

    def export_training_set(self, output_format='json', key=None):
        """Returns the classified entries in the data as JSON or YAML."""
        return super().export_training_set(output_format=output_format, key=key)

# def export_training_sets(prefix, output_format='json'):
#     output = {}
#     re_prefix = re.compile(r'^' + prefix + ':')
#     for record in db.session.query(MachineLearning).filter(MachineLearning.group_id.like(prefix + '%')).group_by(MachineLearning.group_id):
#         the_group_id = re_prefix.sub('', record.group_id)
#         output[the_group_id].append({'independent': record.independent, 'dependent': record.dependent})
#     if output_format == 'json':
#         return json.dumps(output, sort_keys=True, indent=4)
#     elif output_format == 'yaml':
#         return yaml.safe_dump(output, default_flow_style=False)
#     else:
#         raise DAException("Unknown output format " + str(output_format))


def process_independent_data(data):
    result = {}
    for key, val in data.items():
        if isinstance(val, (DADict, dict)):
            for subkey, subval in val.items():
                if not isinstance(subval, (str, bool, int, float)):
                    raise DAException('RandomForestMachineLearner: invalid data type ' + subval.__class__.__name__ + ' in data')
                result[key + '_' + subkey] = subval
        else:
            if not isinstance(val, (str, bool, int, float)):
                raise DAException('RandomForestMachineLearner: invalid data type ' + subval.__class__.__name__ + ' in data')
            result[key] = val
    return result
