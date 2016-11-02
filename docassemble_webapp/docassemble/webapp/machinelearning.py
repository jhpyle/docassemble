from docassemble.webapp.core.models import MachineLearning
from docassemble.webapp.app_and_db import app, db
from sqlalchemy import or_, and_
import re
import cPickle as pickle
import datetime
import os
import yaml
import json
import sys
from pattern.vector import count, KNN, stem, PORTER, words, Document
from docassemble.base.logger import logmessage
from docassemble.webapp.backend import get_info_from_file_reference

knns = dict()
lastmodtime = dict()

class MachineLearningEntry(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
    def classify(self, dependent):
        self.ml.set_dependent_by_id(self.id, dependent)

class MachineLearner(object):
    def initialize(self, *pargs, **kwargs):
        if hasattr(self, 'initial_file'):
            self.start_from_file(self.initial_file)
        if hasattr(self, 'group_id') and self.group_id not in lastmodtime:
            lastmodtime[self.group_id] = datetime.datetime(year=1970, month=1, day=1)
    def export_training_set(self, output_format='json'):
        self.initialize()
        output = list()
        for entry in self.classified_entries():
            output.append(dict(independent=entry.independent, dependent=entry.dependent))
        if output_format == 'json':
            return json.dumps(output, sort_keys=True, indent=4)
        elif output_format == 'yaml':
            return yaml.safe_dump(output, default_flow_style=False)
        else:
            raise Exception("Unknown output format " + str(output_format))
    def start_from_file(self, fileref):
        #logmessage("Starting from file " + str(fileref))
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id).first()
        if existing_entry is not None:
            return
        file_info = get_info_from_file_reference(fileref)
        if 'fullpath' not in file_info or file_info['fullpath'] is None or not os.path.exists(file_info['fullpath']):
            raise Exception("File reference " + str(fileref) + " is invalid")
        with open(file_info['fullpath'], 'rU') as fp:
            content = fp.read().decode('utf8')
        if 'mimetype' in file_info and file_info['mimetype'] == 'application/json':
            aref = json.loads(content)
        elif 'extension' in file_info and file_info['extension'].lower() in ['yaml', 'yml']:
            aref = yaml.load(content)
        if type(aref) is list:
            nowtime = datetime.datetime.utcnow()
            for entry in aref:
                new_entry = MachineLearning(group_id=self.group_id, independent=pickle.dumps(entry['independent']), dependent=pickle.dumps(entry['dependent']), modtime=nowtime, create_time=nowtime, active=True)
                db.session.add(new_entry)
            db.session.commit()
    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0:
            self.group_id = pargs[0]
        if len(pargs) > 1:
            self.initial_file = pargs[1]
        if 'group_id' in kwargs:
            self.group_id = kwargs['group_id']
            del kwargs['group_id']
    def add_to_training_set(self, independent, dependent):
        self.initialize()
        nowtime = datetime.datetime.utcnow()
        new_entry = MachineLearning(group_id=self.group_id, independent=pickle.dumps(independent), dependent=pickle.dumps(dependent), create_time=nowtime, modtime=nowtime, active=True)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    def save_for_classification(self, text, **kwargs):
        self.initialize()
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id, independent=pickle.dumps(text)).first()
        if existing_entry is not None:
            logmessage(str(text) + " is already there")
            return existing_entry.id
        new_entry = MachineLearning(group_id=self.group_id, independent=pickle.dumps(text), create_time=datetime.datetime.utcnow(), active=False)
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    def retrieve_by_id(self, the_id):
        self.initialize()
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id, id=the_id).first()
        if existing_entry is None:
            raise Exception("There was no entry in the database for id " + str(the_id))
        return MachineLearningEntry(ml=self, id=existing_entry.id, independent=pickle.loads(existing_entry.independent), create_time=existing_entry.create_time)
    def one_unclassified_entry(self):
        self.initialize()
        entry = MachineLearning.query.filter_by(group_id=self.group_id, active=False).order_by(MachineLearning.id).first()
        if entry is None:
            return None
        return MachineLearningEntry(ml=self, id=entry.id, independent=pickle.loads(entry.independent), create_time=entry.create_time)
    def unclassified_entries(self):
        self.initialize()
        results = list()
        for entry in MachineLearning.query.filter_by(group_id=self.group_id, active=False).order_by(MachineLearning.id).all():
            results.append(MachineLearningEntry(ml=self, id=entry.id, independent=pickle.loads(entry.independent), create_time=entry.create_time))
        return results
    def classified_entries(self):
        self.initialize()
        results = list()
        for entry in MachineLearning.query.filter_by(group_id=self.group_id, active=True).order_by(MachineLearning.id).all():
            results.append(MachineLearningEntry(ml=self, id=entry.id, independent=pickle.loads(entry.independent), dependent=pickle.loads(entry.dependent), create_time=entry.create_time))
        return results
    def set_dependent_by_id(self, the_id, the_dependent):
        self.initialize()
        existing_entry = MachineLearning.query.filter_by(group_id=self.group_id, id=the_id).first()
        if existing_entry is None:
            raise Exception("There was no entry in the database for id " + str(the_id))
        existing_entry.dependent = pickle.dumps(the_dependent)
        existing_entry.modtime = datetime.datetime.utcnow()
        existing_entry.active = True
        db.session.commit()
    def delete_by_id(self, the_id):
        self.initialize()
        MachineLearning.query.filter_by(group_id=self.group_id, id=the_id).delete()
        db.session.commit()
    def save(self):
        db.session.commit()
    def train_from_db(self):
        logmessage("Doing train_from_db")
        self.initialize()
        nowtime = datetime.datetime.utcnow()
        for record in MachineLearning.query.filter(and_(MachineLearning.group_id == self.group_id, MachineLearning.active == True, MachineLearning.modtime > lastmodtime[self.group_id])).all():
            logmessage("Training...")
            self.train(pickle.loads(record.independent), pickle.loads(record.dependent))
        lastmodtime[self.group_id] = nowtime
    def delete_training_set(self):
        self.initialize()
        MachineLearning.query.filter_by(group_id=self.group_id).all().delete()
        db.session.commit()
    def train(self, indep, depend, **kwargs):
        pass
    def predict(self, text, **kwargs):
        pass

class SimpleTextMachineLearner(MachineLearner):
    """A class used to interact with the machine learning system"""
    def initialize(self, *pargs, **kwargs):
        if hasattr(self, 'group_id') and self.group_id not in knns:
            knns[self.group_id] = KNN()
        return super(SimpleTextMachineLearner, self).initialize(*pargs, **kwargs)
    def __init__(self, *pargs, **kwargs):
        if len(pargs) > 0:
            self.group_id = pargs[0]
        if 'group_id' in kwargs:
            self.group_id = kwargs['group_id']
            del kwargs['group_id']
        return super(SimpleTextMachineLearner, self).__init__(*pargs, **kwargs)
    def train(self, indep, depend, **kwargs):
        the_text = re.sub(r'[\n\r]+', r'  ', indep).lower()
        knns[self.group_id].train(Document(the_text, stemmer=PORTER), depend)
    def predict(self, indep, **kwargs):
        indep = re.sub(r'[\n\r]+', r'  ', indep).lower()
        self.train_from_db()
        probs = dict()
        for key, value in knns[self.group_id].classify(Document(indep, stemmer=PORTER), discrete=False).iteritems():
            probs[key] = value
        if not len(probs):
            single_result = knns[self.group_id].classify(Document(indep, stemmer=PORTER))
            if single_result is not None:
                probs[single_result] = 1.0
        return sorted(probs.keys(), key=probs.get, reverse=True)
    
