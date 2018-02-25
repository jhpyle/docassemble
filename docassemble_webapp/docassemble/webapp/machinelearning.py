from docassemble.webapp.core.models import MachineLearning
from docassemble.base.core import DAObject, DAList, DADict
from docassemble.webapp.db_object import db
from sqlalchemy import or_, and_
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np
import re
import random
import codecs
import cPickle as pickle
import datetime
import os
import yaml
import json
import sys
from pattern.vector import count, KNN, SVM, stem, PORTER, words, Document
from docassemble.base.logger import logmessage
from docassemble.webapp.backend import get_info_from_file_reference
import docassemble.base.functions

learners = dict()
svms = dict()
lastmodtime = dict()
reset_counter = dict()

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
        args = dict(independent=self.independent)
        if hasattr(self, 'dependent'):
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

class MachineLearner(object):
    """Base class for machine learning objects"""
    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0:
            if ':' in pargs[0]:
                raise Exception("MachineLearner: you cannot use a colon in a machine learning name")
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
        if hasattr(self, 'group_id') and (self.group_id not in lastmodtime or reset):
            lastmodtime[self.group_id] = datetime.datetime(year=1970, month=1, day=1)
            reset_counter = self.reset_counter
    def export_training_set(self, output_format='json', key=None):
        self._initialize()
        output = list()
        for entry in self.classified_entries(key=key):
            the_entry = dict(independent=entry.independent, dependent=entry.dependent)
            if entry.info is not None:
                the_entry['info'] = entry.info
            output.append(the_entry)
        if output_format == 'json':
            return json.dumps(output, sort_keys=True, indent=4)
        elif output_format == 'yaml':
            return yaml.safe_dump(output, default_flow_style=False)
        else:
            raise Exception("Unknown output format " + str(output_format))
    def dependent_in_use(self, key=None):
        in_use = set()
        if key is None:
            query = db.session.query(MachineLearning.dependent).filter(MachineLearning.group_id == self.group_id).group_by(MachineLearning.dependent)
        else:
            query = db.session.query(MachineLearning.dependent).filter(and_(MachineLearning.group_id == self.group_id, MachineLearning.key == key)).group_by(MachineLearning.dependent)
        for record in query:
            if record.dependent is not None:
                in_use.add(pickle.loads(codecs.decode(record.dependent, 'base64')))
        return sorted(in_use)
    def is_empty(self):
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id).first()
        if existing_entry is None:
            return True
        return False
    def start_from_file(self, fileref):
        #logmessage("Starting from file " + str(fileref))
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id).first()
        if existing_entry is not None:
            return
        file_info = get_info_from_file_reference(fileref, folder='sources')
        if 'fullpath' not in file_info or file_info['fullpath'] is None or not os.path.exists(file_info['fullpath']):
            return
            #raise Exception("File reference " + str(fileref) + " is invalid")
        with open(file_info['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
        if 'mimetype' in file_info and file_info['mimetype'] == 'application/json':
            aref = json.loads(content)
        elif 'extension' in file_info and file_info['extension'].lower() in ['yaml', 'yml']:
            aref = yaml.load(content)
        if type(aref) is dict and hasattr(self, 'group_id'):
            the_group_id = re.sub(r'.*:', '', self.group_id)
            if the_group_id in aref:
                aref = aref[the_group_id]
        if type(aref) is list:
            nowtime = datetime.datetime.utcnow()
            for entry in aref:
                if 'independent' in entry:
                    new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(entry['independent']), 'base64').decode(), dependent=codecs.encode(pickle.dumps(entry.get('dependent', None)), 'base64').decode(), modtime=nowtime, create_time=nowtime, active=True, key=entry.get('key', None), info=codecs.encode(pickle.dumps(entry['info']), 'base64').decode() if entry.get('info', None) is not None else None)
                    db.session.add(new_entry)
            db.session.commit()
    def add_to_training_set(self, independent, dependent, key=None, info=None):
        self._initialize()
        nowtime = datetime.datetime.utcnow()
        new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(independent), 'base64').decode(), dependent=codecs.encode(pickle.dumps(dependent), 'base64').decode(), info=codecs.encode(pickle.dumps(info), 'base64').decode() if info is not None else None, create_time=nowtime, modtime=nowtime, active=True, key=key)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    def save_for_classification(self, indep, key=None, info=None):
        self._initialize()
        if key is None:
            existing_entry = MachineLearning.query.filter_by(group_id=self.group_id, dependent=None, independent=codecs.encode(pickle.dumps(indep), 'base64').decode()).first()
        else:
            existing_entry = MachineLearning.query.filter_by(group_id=self.group_id, key=key, independent=codecs.encode(pickle.dumps(indep), 'base64').decode()).first()
        if existing_entry is not None:
            logmessage("entry is already there")
            return existing_entry.id
        new_entry = MachineLearning(group_id=self.group_id, independent=codecs.encode(pickle.dumps(indep), 'base64').decode(), create_time=datetime.datetime.utcnow(), active=False, key=key, info=codecs.encode(pickle.dumps(info), 'base64').decode() if info is not None else None)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    def retrieve_by_id(self, the_id):
        self._initialize()
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id, id=the_id).first()
        if existing_entry is None:
            raise Exception("There was no entry in the database for id " + str(the_id) + " with group id " + str(self.group_id))
        if existing_entry.dependent:
            dependent = pickle.loads(codecs.decode(existing_entry.dependent, 'base64'))
            return MachineLearningEntry(ml=self, id=existing_entry.id, independent=pickle.loads(codecs.decode(existing_entry.independent, 'base64')), dependent=dependent, create_time=existing_entry.create_time, key=existing_entry.key, info=pickle.loads(codecs.decode(existing_entry.info, 'base64')) if existing_entry.info is not None else None)
        else:
            return MachineLearningEntry(ml=self, id=existing_entry.id, independent=pickle.loads(codecs.decode(existing_entry.independent, 'base64')), create_time=existing_entry.create_time, key=existing_entry.key, info=pickle.loads(codecs.decode(existing_entry.info, 'base64')) if existing_entry.info is not None else None)
    def one_unclassified_entry(self, key=None):
        self._initialize()
        if key is None:
            entry = MachineLearning.query.filter_by(group_id=self.group_id, active=False).order_by(MachineLearning.id).first()
        else:
            entry = MachineLearning.query.filter_by(group_id=self.group_id, key=key, active=False).order_by(MachineLearning.id).first()
        if entry is None:
            return None
        return MachineLearningEntry(ml=self, id=entry.id, independent=pickle.loads(codecs.decode(entry.independent, 'base64')), create_time=entry.create_time, key=entry.key, info=pickle.loads(codecs.decode(entry.info, 'base64')) if entry.info is not None else None)._set_instance_name_for_method()
    def new_entry(self, **kwargs):
        return MachineLearningEntry(ml=self, **kwargs)._set_instance_name_for_method()
    def unclassified_entries(self, key=None):
        self._initialize()
        results = DAList()._set_instance_name_for_method()
        results.gathered = True
        if key is None:
            query = MachineLearning.query.filter_by(group_id=self.group_id, active=False).order_by(MachineLearning.id).all()
        else:
            query = MachineLearning.query.filter_by(group_id=self.group_id, key=key, active=False).order_by(MachineLearning.id).all()
        for entry in query:
            results.appendObject(MachineLearningEntry, ml=self, id=entry.id, independent=pickle.loads(codecs.decode(entry.independent, 'base64')), create_time=entry.create_time, key=entry.key, info=pickle.loads(codecs.decode(entry.info, 'base64')) if entry.info is not None else None)
        return results
    def classified_entries(self, key=None):
        self._initialize()
        results = DAList()
        results.gathered = True
        results.set_random_instance_name()
        if key is None:
            query = MachineLearning.query.filter_by(group_id=self.group_id, active=True).order_by(MachineLearning.id).all()
        else:
            query = MachineLearning.query.filter_by(group_id=self.group_id, active=True, key=key).order_by(MachineLearning.id).all()
        for entry in query:
            results.appendObject(MachineLearningEntry, ml=self, id=entry.id, independent=pickle.loads(codecs.decode(entry.independent, 'base64')), dependent=pickle.loads(codecs.decode(entry.dependent, 'base64')), info=pickle.loads(codecs.decode(entry.info, 'base64')) if entry.info is not None else None, create_time=entry.create_time, key=entry.key)
        return results
    def _save_entry(self, **kwargs):
        self._initialize()
        the_id = kwargs.get('id', None)
        need_to_reset = False
        if the_id is None:
            the_entry = MachineLearning(group_id=self.group_id)
            existing = False
        else:
            the_entry = MachineLearning.query.filter_by(group_id=self.group_id, id=the_id).first()
            existing = True
        if the_entry is None:
            raise Exception("There was no entry in the database for id " + str(the_id) + " with group id " + str(self.group_id))
        if 'dependent' in kwargs:
            if existing and the_entry.dependent is not None and the_entry.dependent != kwargs['dependent']:
                need_to_reset = True
            the_entry.dependent = codecs.encode(pickle.dumps(kwargs['dependent']), 'base64').decode()
            the_entry.active = True
        if 'independent' in kwargs:
            if existing and the_entry.independent is not None and the_entry.independent != kwargs['independent']:
                need_to_reset = True
            the_entry.independent = codecs.encode(pickle.dumps(kwargs['independent']), 'base64').decode()
        if 'key' in kwargs:
            the_entry.key = kwargs['key']
        if 'info' in kwargs:
            the_entry.info = codecs.encode(pickle.dumps(kwargs['info']), 'base64').decode()
        the_entry.modtime = datetime.datetime.utcnow()
        if not existing:
            db.session.add(the_entry)
        db.session.commit()
        if need_to_reset:
            self.reset()
    def set_dependent_by_id(self, the_id, the_dependent):
        self._initialize()
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id, id=the_id).first()
        if existing_entry is None:
            raise Exception("There was no entry in the database for id " + str(the_id) + " with group id " + str(self.group_id))
        existing_entry.dependent = codecs.encode(pickle.dumps(the_dependent), 'base64').decode()
        existing_entry.modtime = datetime.datetime.utcnow()
        existing_entry.active = True
        db.session.commit()
    def delete_by_id(self, the_id):
        self._initialize()
        MachineLearning.query.filter_by(group_id=self.group_id, id=the_id).delete()
        db.session.commit()
        self.reset()
    def delete_by_key(self, key):
        self._initialize()
        MachineLearning.query.filter_by(group_id=self.group_id, key=key).delete()
        db.session.commit()
        self.reset()
    def save(self):
        db.session.commit()
    def _train_from_db(self):
        #logmessage("Doing train_from_db")
        self._initialize()
        nowtime = datetime.datetime.utcnow()
        success = False
        for record in MachineLearning.query.filter(and_(MachineLearning.group_id == self.group_id, MachineLearning.active == True, MachineLearning.modtime > lastmodtime[self.group_id])).all():
            #logmessage("Training...")
            self._train(pickle.loads(codecs.decode(record.independent, 'base64')), pickle.loads(codecs.decode(record.dependent, 'base64')))
            success = True
        lastmodtime[self.group_id] = nowtime
        return success
    def delete_training_set(self):
        self._initialize()
        MachineLearning.query.filter_by(group_id=self.group_id).all().delete()
        db.session.commit()
    def _train(self, indep, depend):
        pass
    def _predict(self, indep):
        pass

class SimpleTextMachineLearner(MachineLearner):
    """A class used to interact with the machine learning system, using the K Nearest Neighbors method"""
    def _learner(self):
        return KNN()
    def _initialize(self):
        """Initializes a fresh machine learner."""
        if self.group_id not in reset_counter or self.reset_counter != reset_counter[self.group_id]:
            need_to_reset = True
        if hasattr(self, 'group_id') and (self.group_id not in learners or need_to_reset):
            learners[self.group_id] = self._learner()
        return super(SimpleTextMachineLearner, self)._initialize(reset=need_to_reset)
    def _train(self, indep, depend):
        """Trains the machine learner given an independent variable and a corresponding dependent variable."""
        if indep is None:
            return
        the_text = re.sub(r'[\n\r]+', r'  ', indep).lower()
        learners[self.group_id].train(Document(the_text.lower(), stemmer=PORTER), depend)
    def predict(self, indep, probabilities=False):
        """Returns a list of predicted dependent variables for a given independent variable."""
        indep = re.sub(r'[\n\r]+', r'  ', indep).lower()
        if not self._train_from_db():
            return list()
        probs = dict()
        for key, value in learners[self.group_id].classify(Document(indep.lower(), stemmer=PORTER), discrete=False).iteritems():
            probs[key] = value
        if not len(probs):
            single_result = learners[self.group_id].classify(Document(indep.lower(), stemmer=PORTER))
            if single_result is not None:
                probs[single_result] = 1.0
        if probabilities:
            return [(x, probs[x]) for x in sorted(probs.keys(), key=probs.get, reverse=True)]
        else:
            return sorted(probs.keys(), key=probs.get, reverse=True)
    def confusion_matrix(self, key=None, output_format=None, split=False):
        """Returns a confusion matrix for the model based on splitting the data set randomly into two pieces, training on one and testing on the other"""
        if split:
            list_of_dependent = self.dependent_in_use(key=key)
        else:
            list_of_dependent = [None]
        output = ''
        matrices = dict()
        for current_dep in list_of_dependent:
            testing_set = list()
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
                #output += "\n\n`" + str(matrix) + "`"
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
    def reset(self):
        """Clears the cache of the machine learner"""
        return super(SimpleTextMachineLearner, self).reset()
    def delete_training_set(self):
        """Deletes all of the training data in the database"""
        return super(SimpleTextMachineLearner, self).delete_training_set()
    def delete_by_key(self, key):
        """Deletes all of the training data in the database that was added with a given key"""
        return super(SimpleTextMachineLearner, self).delete_training_set(key)
    def delete_by_id(self, the_id):
        """Deletes the entry in the training data with the given ID"""
        return super(SimpleTextMachineLearner, self).delete_by_id(the_id)
    def set_dependent_by_id(self, the_id, depend):
        """Sets the dependent variable for the entry in the training data with the given ID"""
        return super(SimpleTextMachineLearner, self).set_dependent_by_id(the_id, depend)
    def classified_entries(self, key=None):
        """Returns a list of entries in the data that have been classified."""
        return super(SimpleTextMachineLearner, self).classified_entries(key=key)
    def unclassified_entries(self, key=None):
        """Returns a list of entries in the data that have not yet been classified."""
        return super(SimpleTextMachineLearner, self).unclassified_entries(key=key)
    def one_unclassified_entry(self, key=None):
        """Returns the first entry in the data that has not yet been classified, or None if all entries have been classified."""
        return super(SimpleTextMachineLearner, self).one_unclassified_entry(key=key)
    def retrieve_by_id(self, the_id):
        """Returns the entry in the data that has the given ID."""
        return super(SimpleTextMachineLearner, self).retrieve_by_id(the_id)
    def save_for_classification(self, indep, key=None, info=None):
        """Creates a not-yet-classified entry in the data for the given independent variable and returns the ID of the entry."""
        return super(SimpleTextMachineLearner, self).save_for_classification(indep, key=key, info=info)
    def add_to_training_set(self, indep, depend, key=None, info=None):
        """Creates an entry in the data for the given independent and dependent variable and returns the ID of the entry."""
        return super(SimpleTextMachineLearner, self).add_to_training_set(indep, depend, key=key, info=info)
    def is_empty(self):
        """Returns True if no data have been defined, otherwise returns False."""
        return super(SimpleTextMachineLearner, self).is_empty()
    def dependent_in_use(self, key=None):
        """Returns a sorted list of unique dependent variables in the data."""
        return super(SimpleTextMachineLearner, self).dependent_in_use(key=key)
    def export_training_set(self, output_format='json'):
        """Returns the classified entries in the data as JSON or YAML."""
        return super(SimpleTextMachineLearner, self).export_training_set(output_format=output_format)
    def new_entry(self, **kwargs):
        """Creates a new entry in the data."""
        return super(SimpleTextMachineLearner, self).new_entry(**kwargs)
    
class SVMMachineLearner(SimpleTextMachineLearner):
    """Machine Learning object using the Symmetric Vector Machine method"""
    def _learner(self):
        return SVM(extension='libsvm')

class RandomForestMachineLearner(MachineLearner):
    def _learner(self):
        return RandomForestClassifier(n_jobs=2)
    def feature_importances(self):
        """Returns the importances of each of the features"""
        if not self._train_from_db():
            return list()
        return learners[self.group_id]['learner'].feature_importances_
    def _initialize(self):
        """Initializes a fresh machine learner."""
        if self.group_id not in reset_counter or self.reset_counter != reset_counter[self.group_id]:
            need_to_reset = True
        if hasattr(self, 'group_id') and (self.group_id not in learners or need_to_reset):
            learners[self.group_id] = dict(learner=self._learner(), dep_type=None, indep_type=dict(), indep_categories=dict(), dep_categories=None)
        return super(RandomForestMachineLearner, self)._initialize(reset=need_to_reset)
    def _train_from_db(self):
        #logmessage("Doing train_from_db")
        self._initialize()
        nowtime = datetime.datetime.utcnow()
        success = False
        data = list()
        depend_data = list()
        for record in MachineLearning.query.filter(and_(MachineLearning.group_id == self.group_id, MachineLearning.active == True, MachineLearning.modtime > lastmodtime[self.group_id])).all():
            indep_var = pickle.loads(codecs.decode(record.independent, 'base64'))
            depend_var = pickle.loads(codecs.decode(record.dependent, 'base64'))
            if type(depend_var) is str:
                depend_var = unicode(depend_var)
            if learners[self.group_id]['dep_type'] is not None:
                if type(depend_var) is not learners[self.group_id]['dep_type']:
                    if type(depend_var) is int and learners[self.group_id]['dep_type'] is float:
                        depend_var = float(depend_var)
                    elif type(depend_var) is float and learners[self.group_id]['dep_type'] is int:
                        learners[self.group_id]['dep_type'] = float
                    else:
                        raise Exception("RandomForestMachineLearner: dependent variable type was not consistent")
            else:
                if type(depend_var) not in [unicode, int, bool, float]:
                    raise Exception("RandomForestMachineLearner: dependent variable type for key " + repr(key) + " was not a standard variable type")
                learners[self.group_id]['dep_type'] = type(depend_var)
            depend_data.append(depend_var)
            if isinstance(indep_var, DADict):
                indep_var = indep_var.elements
            if type(indep_var) is not dict:
                raise Exception("RandomForestMachineLearner: independent variable was not a dictionary")
            for key, val in indep_var.iteritems():
                if type(val) is str:
                    val = unicode(val)
                if key in learners[self.group_id]['indep_type']:
                    if type(val) is not learners[self.group_id]['indep_type'][key]:
                        if type(val) is int and learners[self.group_id]['indep_type'][key] is float:
                            val = float(val)
                        elif type(val) is float and learners[self.group_id]['indep_type'][key] is int:
                            learners[self.group_id]['indep_type'][key] = float
                        else:
                            raise Exception("RandomForestMachineLearner: independent variable type for key " + repr(key) + " was not consistent")
                else:
                    if type(val) not in [unicode, int, bool, float]:
                        raise Exception("RandomForestMachineLearner: independent variable type for key " + repr(key) + " was not a standard variable type")
                    learners[self.group_id]['indep_type'][key] = type(val)
            data.append(indep_var)
            success = True
        if success:
            df = pd.DataFrame(data)
            for key, val in learners[self.group_id]['indep_type'].iteritems():
                if val is unicode:
                    df[key] = pd.Series(df[key], dtype="category")
                    learners[self.group_id]['indep_categories'][key] = df[key].cat.categories
            df = pd.get_dummies(df, dummy_na=True)
            if learners[self.group_id]['dep_type'] is unicode:
                y = pd.Series(depend_data, dtype="category")
                learners[self.group_id]['dep_categories'] = y.cat.categories
            else:
                y = pd.Series(depend_data)
            learners[self.group_id]['learner'].fit(df, list(y))
            lastmodtime[self.group_id] = nowtime
        return success
    def predict(self, indep, probabilities=False):
        """Returns a list of predicted dependent variables for a given independent variable."""
        if not self._train_from_db():
            return list()
        if isinstance(indep, DADict):
            indep = indep.elements
        if type(indep) is not dict:
            raise Exception("RandomForestMachineLearner: independent variable was not a dictionary")
        indep = process_independent_data(indep)
        indep_to_use = dict()
        for key, val in indep.iteritems():
            if key in learners[self.group_id]['indep_type']:
                if type(val) is str:
                    val = unicode(val)
                if type(val) is not learners[self.group_id]['indep_type'][key]:
                    if type(val) is int and learners[self.group_id]['indep_type'][key] is float:
                        val = float(val)
                    elif type(val) is float and learners[self.group_id]['indep_type'][key] is int:
                        learners[self.group_id]['indep_type'][key] = float
                    else:
                        raise Exception("RandomForestMachineLearner: the independent variable type for key " + repr(key) + " was not consistent.  Stored was " + str(learners[self.group_id]['indep_type'][key]) + " and type was " + str(type(val)))
            else:
                raise Exception("RandomForestMachineLearner: independent variable key " + repr(key) + " was not recognized")
            if type(val) is unicode:
                if val not in learners[self.group_id]['indep_categories'][key]:
                    val = np.nan
            indep_to_use[key] = val
        df = pd.DataFrame([indep_to_use])
        for key, val in indep_to_use.iteritems():
            if learners[self.group_id]['indep_type'][key] is unicode:
                df[key] = pd.Series(df[key]).astype('category', categories=learners[self.group_id]['indep_categories'][key])
        df = pd.get_dummies(df, dummy_na=True)
        pred = learners[self.group_id]['learner'].predict_proba(df)
        indexno = 0
        result = list()
        for x in pred[0]:
            result.append((learners[self.group_id]['dep_categories'][indexno], x))
            indexno += 1
        result = sorted(result, key=lambda x: x[1], reverse=True)
        if probabilities:
            return result
        return [x[0] for x in result]
    def reset(self):
        """Clears the cache of the machine learner"""
        return super(RandomForestMachineLearner, self).reset()
    def delete_training_set(self):
        """Deletes all of the training data in the database"""
        return super(RandomForestMachineLearner, self).delete_training_set()
    def delete_by_key(self, key):
        """Deletes all of the training data in the database that was added with a given key"""
        return super(RandomForestMachineLearner, self).delete_training_set(key)
    def delete_by_id(self, the_id):
        """Deletes the entry in the training data with the given ID"""
        return super(RandomForestMachineLearner, self).delete_by_id(the_id)
    def set_dependent_by_id(self, the_id, depend):
        """Sets the dependent variable for the entry in the training data with the given ID"""
        return super(RandomForestMachineLearner, self).set_dependent_by_id(the_id, depend)
    def classified_entries(self, key=None):
        """Returns a list of entries in the data that have been classified."""
        return super(RandomForestMachineLearner, self).classified_entries(key=key)
    def unclassified_entries(self, key=None):
        """Returns a list of entries in the data that have not yet been classified."""
        return super(RandomForestMachineLearner, self).unclassified_entries(key=key)
    def one_unclassified_entry(self, key=None):
        """Returns the first entry in the data that has not yet been classified, or None if all entries have been classified."""
        return super(RandomForestMachineLearner, self).one_unclassified_entry(key=key)
    def retrieve_by_id(self, the_id):
        """Returns the entry in the data that has the given ID."""
        return super(RandomForestMachineLearner, self).retrieve_by_id(the_id)
    def save_for_classification(self, indep, key=None, info=None):
        """Creates a not-yet-classified entry in the data for the given independent variable and returns the ID of the entry."""
        indep = process_independent_data(indep)
        return super(RandomForestMachineLearner, self).save_for_classification(indep, key=key, info=info)
    def add_to_training_set(self, indep, depend, key=None, info=None):
        """Creates an entry in the data for the given independent and dependent variable and returns the ID of the entry."""
        indep = process_independent_data(indep)
        return super(RandomForestMachineLearner, self).add_to_training_set(indep, depend, key=key, info=info)
    def is_empty(self):
        """Returns True if no data have been defined, otherwise returns False."""
        return super(RandomForestMachineLearner, self).is_empty()
    def dependent_in_use(self, key=None):
        """Returns a sorted list of unique dependent variables in the data."""
        return super(RandomForestMachineLearner, self).dependent_in_use(key=key)
    def export_training_set(self, output_format='json'):
        """Returns the classified entries in the data as JSON or YAML."""
        return super(RandomForestMachineLearner, self).export_training_set(output_format=output_format)
    def new_entry(self, **kwargs):
        """Creates a new entry in the data."""
        return super(RandomForestMachineLearner, self).new_entry(**kwargs)
    
    
# def export_training_sets(prefix, output_format='json'):
#     output = dict()
#     re_prefix = re.compile(r'^' + prefix + ':')
#     for record in db.session.query(MachineLearning).filter(MachineLearning.group_id.like(prefix + '%')).group_by(MachineLearning.group_id):
#         the_group_id = re_prefix.sub('', record.group_id)
#         output[the_group_id].append(dict(independent=record.independent, dependent=record.dependent))
#     if output_format == 'json':
#         return json.dumps(output, sort_keys=True, indent=4)
#     elif output_format == 'yaml':
#         return yaml.safe_dump(output, default_flow_style=False)
#     else:
#         raise Exception("Unknown output format " + str(output_format))

def process_independent_data(data):
    result = dict()
    for key, val in data.iteritems():
        if isinstance(val, DADict) or type(val) is dict:
            for subkey, subval in val.iteritems():
                if type(subval) not in (unicode, str, bool, int, float):
                    raise Exception('RandomForestMachineLearner: invalid data type ' + subval.__class__.__name__ + ' in data')
                result[key + '_' + subkey] = subval
        else:
            if type(val) not in (unicode, str, bool, int, float):
                raise Exception('RandomForestMachineLearner: invalid data type ' + subval.__class__.__name__ + ' in data')
            result[key] = val
    return result
