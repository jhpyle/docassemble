import copy
import os
import sys
from docassemble.base.logger import logmessage
from docassemble.base.functions import server, this_thread
from six import text_type

__all__ = ['SQLObject', 'alchemy_url', 'upgrade_db']

class SQLObject(object):
    _required = []
    _uid = 'uid'
    def get_session(self):
        return self._session()
    def sql_init(self):
        self._zombie = False
        db_entry = None
        if hasattr(self, 'id'):
            session = self.get_session()
            db_entry = session.query(self._model).filter(self._model.id == self.id).first()
            if db_entry is None:
                self._nascent = False
                self._zombie = True
                return
        if db_entry is None:
            db_entry = self.db_find_existing()
        if db_entry is not None:
            self.id = db_entry.id
            self._nascent = False
            db_values = dict()
            for column in self._model.__dict__.keys():
                if column == 'id' or column.startswith('_'):
                    continue
                db_values[column] = getattr(db_entry, column)
                if db_values[column] is not None:
                    self.db_set(column, db_values[column])
                else:
                    try:
                        self.db_null(column)
                    except:
                        pass
            self._orig = db_values
            self.db_cache()
            return
        self._nascent = True
        self._orig = dict()
    def __getstate__(self):
        try:
            self.db_save()
        except Exception as err:
            sys.stderr.write("On SQLObject write, " + err.__class__.__name__ + ": " + text_type(err) + "\n")
        dict_to_save = copy.copy(self.__dict__)
        if '_orig' in dict_to_save:
            del dict_to_save['_orig']
        return dict_to_save
    def __setstate__(self, pickle_dict):
        self.__dict__ = pickle_dict
        try:
            self.db_read()
        except Exception as err:
            sys.stderr.write("On SQLObject read, " + err.__class__.__name__ + ": " + text_type(err) + "\n")
    @classmethod
    def by_id(cls, id):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = dict()
        if cls._model.__name__ in this_thread.misc['dbcache'] and id in this_thread.misc['dbcache'][cls._model.__name__]:
            return this_thread.misc['dbcache'][cls._model.__name__][id]
        obj = cls(id=id)
        obj.set_random_instance_name()
        return obj
    @classmethod
    def by_uid(cls, uid):
        if cls._uid not in cls._model.__dict__:
            return None
        session = cls._session()
        db_entry = session.query(self._model).filter(getattr(cls._model, cls._uid) == uid).first()
        if db_entry is not None:
            return cls.by_id(db_entry.id)
        obj = cls()
        obj.db_set(cls._uid, uid)
        obj.set_random_instance_name()
        obj.ready()
        return obj
    @classmethod
    def delete_by_id(cls, id):
        session = cls._session()
        session.query(cls._model).filter(cls._model.id == id).delete()        
        session.commit()
        if 'dbcache' in this_thread.misc and cls._model.__name__ in this_thread.misc['dbcache'] and id in this_thread.misc['dbcache'][cls._model.__name__]:
            this_thread.misc['dbcache'][cls._model.__name__][id]._zombie = True
    @classmethod
    def delete_by_uid(cls, uid):
        if cls._uid not in cls._model.__dict__:
            return
        session = cls._session()
        db_entry = session.query(cls._model).filter(getattr(cls._model, cls._uid) == uid).first()
        if db_entry is not None:
            the_id = db_entry.id
            session.query(cls._model).filter(getattr(cls._model, cls._uid) == uid).delete()
            session.commit()
            if 'dbcache' in this_thread.misc and cls._model.__name__ in this_thread.misc['dbcache'] and the_id in this_thread.misc['dbcache'][cls._model.__name__]:
                this_thread.misc['dbcache'][cls._model.__name__][the_id]._zombie = True
    @classmethod
    def id_exists(cls, id):
        session = cls._session()
        db_entry = session.query(cls._model).filter(cls._model.id == id).first()
        if db_entry is None:
            return False
        return True
    @classmethod
    def uid_exists(cls, uid):
        if cls._uid not in cls._model.__dict__:
            return False
        session = cls._session()
        db_entry = session.query(cls._model).filter(getattr(cls._model, cls._uid) == uid).first()
        if db_entry is None:
            return False
        return True
    def db_from_cache(id):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = dict()
        if self._model.__name__ not in this_thread.misc['dbcache']:
            this_thread.misc['dbcache'][self._model.__name__] = dict()
        if id in this_thread.misc['dbcache'][self._model.__name__]:
            return this_thread.misc['dbcache'][self._model.__name__][id]
        return None
    def db_cache(self):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = dict()
        if self._model.__name__ not in this_thread.misc['dbcache']:
            this_thread.misc['dbcache'][self._model.__name__] = dict()
        if hasattr(self, 'id'):
            this_thread.misc['dbcache'][self._model.__name__][self.id] = self
    def __del__(self):
        if hasattr(self, 'id') and 'dbcache' in this_thread.misc and self._model.__name__ in this_thread.misc['dbcache'] and self.id in this_thread.misc['dbcache'][self._model.__name__]:
            del this_thread.misc['dbcache'][self._model.__name__][self.id]
    def db_delete(self):
        self.db_read()
        if self._nascent or self._zombie:
            return
        if hasattr(self, 'id'):
            self.delete_by_id(self.id)
            self._zombie = True
    def db_save(self):
        if self._zombie:
            return
        db_values = dict()
        required_ok = True
        for column in self._model.__dict__.keys():
            if column == 'id' or column.startswith('_'):
                continue
            try:
                db_values[column] = self.db_get(column)
            except:
                if column == self._uid:
                    return
                if column in self._required:
                    if not self._nascent:
                        return
                    required_ok = False
        if self._nascent:
            session = self.get_session()
            try:
                db_entry = self.db_find_existing()
                assert db_entry is not None
                for key, val in db_values.items():
                    setattr(db_entry, key, val)
                new_db_values = dict()
                for column in self._model.__dict__.keys():
                    if column not in db_values:
                        new_db_values[column] = getattr(db_entry, column)
                        if new_db_values[column] is not None:
                            self.db_set(column, new_db_values[column])
                        else:
                            try:
                                self.db_null(column)
                            except:
                                pass
            except:
                if not required_ok:
                    return
                db_entry = self._model(**db_values)
                session.add(db_entry)
            session.commit()
            self.id = db_entry.id
            self._nascent = False
        else:
            if self._orig == db_values:
                return
            session = self.get_session()
            db_entry = session.query(self._model).filter(self._model.id == self.id).first()
            if db_entry is None:
                self._zombie = True
                return
            for key, val in db_values.items():
                setattr(db_entry, key, val)
            session.commit()
            self._orig = db_values
    def save_if_nascent(self):
        if self._nascent:
            self.db_save()        
    def ready(self):
        self.save_if_nascent()
        return not (self._nascent or self._zombie)
    def db_read(self):
        if self._zombie:
            self.db_cache()
            return
        if hasattr(self, 'id'):
            session = self.get_session()
            db_entry = session.query(self._model).filter(self._model.id == self.id).first()
        else:
            try:
                db_entry = self.db_find_existing()
            except:
                db_entry = None
            if db_entry is None and self._nascent:
                self.db_cache()
                return
            if db_entry is not None:
                self.id = db_entry.id
        if db_entry is None:
            self._zombie = True
            self.db_cache()
            return
        if self._nascent is True:
            self._nascent = False
        db_values = dict()
        for column in self._model.__dict__.keys():
            if column == 'id' or column.startswith('_'):
                continue
            db_values[column] = getattr(db_entry, column)
            if db_values[column] is not None:
                self.db_set(column, db_values[column])
            else:
                try:
                    self.db_null(column)
                except:
                    pass
        self._orig = db_values
        self.db_cache()
    def db_find_existing(self):
        if self._uid not in self._model.__dict__:
            return None
        try:
            the_uid = self.db_get(self._uid)
        except:
            return None
        session = self.get_session()
        return session.query(self._model).filter(getattr(self._model, self._uid) == the_uid).first()
    def db_get(self, column):
        pass
    def db_set(self, column, value):
        pass
    def db_null(self, column):
        pass

def alchemy_url(db_config):
    """Returns a URL representing a database connection."""
    return server.alchemy_url(db_config)

def upgrade_db(url, py_file, engine, name=None):
    if name is None:
        name = 'alembic'
    packagedir = os.path.dirname(os.path.abspath(py_file))
    alembic_path = os.path.join(packagedir, name)
    if not os.path.isdir(alembic_path):
        logmessage(name + " directory not found in package directory " + packagedir)
        return
    ini_file = os.path.join(packagedir, name + '.ini')
    if not os.path.isfile(ini_file):
        logmessage(name + ".ini file not found at " + ini_file)
        return
    versions_path = os.path.join(alembic_path, 'versions')
    if not os.path.isdir(versions_path):
        os.makedirs(versions_path)
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config(ini_file)
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    alembic_cfg.set_main_option("script_location", alembic_path)
    if not engine.has_table('alembic_version'):
        command.stamp(alembic_cfg, "head")
    command.upgrade(alembic_cfg, "head")
