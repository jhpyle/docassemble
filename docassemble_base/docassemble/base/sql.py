import copy
import os
# import sys
import json
import sqlalchemy
from docassemble.base.logger import logmessage
from docassemble.base.functions import server, this_thread
from docassemble.base.util import DAList, DAObjectPlusParameters
from docassemble.base.error import DAAttributeError, DAException
from alembic.config import Config
from alembic import command

__all__ = ['SQLObject', 'SQLObjectRelationship', 'SQLObjectList', 'SQLRelationshipList', 'StandardRelationshipList', 'alchemy_url', 'connect_args', 'upgrade_db']


class SQLObject:
    _required = []
    _uid = 'uid'
    _child_mapping = {}
    _parent_mapping = {}

    def sql_init(self):
        self._zombie = False
        db_entry = None
        if hasattr(self, 'id'):
            db_entry = self._session.query(self._model).filter(self._model.id == self.id).first()
            if db_entry is None:
                self._nascent = False
                self._zombie = True
                return
        if db_entry is None:
            db_entry = self.db_find_existing()
        if db_entry is not None:
            self.id = db_entry.id
            self._nascent = False
            db_values = {}
            for column in self._model.__dict__.keys():
                if column == 'id' or column.startswith('_'):
                    continue
                db_values[column] = getattr(db_entry, column)
                if db_values[column] is not None:
                    self.db_set(column, db_values[column])
                else:
                    try:
                        self.db_null(column)
                    except (DAAttributeError, AttributeError):
                        pass
                    except BaseException as err:
                        logmessage("On SQLObject null, " + err.__class__.__name__ + ": " + str(err))
            self._orig = db_values
            self.db_cache()
            return
        self._nascent = True
        self._orig = {}

    def __getstate__(self):
        try:
            self.db_save()
        except BaseException as err:
            logmessage("On SQLObject write, " + err.__class__.__name__ + ": " + str(err))
        dict_to_save = copy.copy(self.__dict__)
        if '_orig' in dict_to_save:
            del dict_to_save['_orig']
        return dict_to_save

    def __setstate__(self, pickle_dict):
        self.__dict__ = pickle_dict
        try:
            self.db_read()
        except BaseException as err:
            logmessage("On SQLObject read, " + err.__class__.__name__ + ": " + str(err))

    @classmethod
    def filter(cls, instance_name, **kwargs):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = {}
        listobj = DAList(instance_name, object_type=cls, auto_gather=False)
        filters = []
        for key, val in kwargs.items():
            if not hasattr(cls._model, key):
                raise DAException("filter: class " + cls.__name__ + " does not have column " + key)
            filters.append(getattr(cls._model, key) == val)
        for db_entry in list(cls._session.query(cls._model).filter(*filters).order_by(cls._model.id).all()):
            if cls._model.__name__ in this_thread.misc['dbcache'] and db_entry.id in this_thread.misc['dbcache'][cls._model.__name__]:
                listobj.append(this_thread.misc['dbcache'][cls._model.__name__][db_entry.id])
            else:
                obj = listobj.appendObject()
                obj.id = db_entry.id
                db_values = {}
                for column in cls._model.__dict__.keys():
                    if column == 'id' or column.startswith('_'):
                        continue
                    db_values[column] = getattr(db_entry, column)
                    if db_values[column] is not None:
                        obj.db_set(column, db_values[column])
                obj._orig = db_values
                obj.db_cache()
        listobj.gathered = True
        return listobj

    @classmethod
    def any(cls):
        db_entry = cls._session.query(cls._model).first()
        if db_entry is None:
            return False
        return True

    @classmethod
    def all(cls, instance_name=None):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = {}
        if instance_name:
            listobj = DAList(instance_name, object_type=cls)
        else:
            listobj = DAList(object_type=cls)
            listobj.set_random_instance_name()
        for db_entry in list(cls._session.query(cls._model).order_by(cls._model.id).all()):
            if cls._model.__name__ in this_thread.misc['dbcache'] and db_entry.id in this_thread.misc['dbcache'][cls._model.__name__]:
                listobj.append(this_thread.misc['dbcache'][cls._model.__name__][db_entry.id])
            else:
                obj = listobj.appendObject()
                obj.id = db_entry.id
                db_values = {}
                for column in cls._model.__dict__.keys():
                    if column == 'id' or column.startswith('_'):
                        continue
                    db_values[column] = getattr(db_entry, column)
                    if db_values[column] is not None:
                        obj.db_set(column, db_values[column])
                obj._orig = db_values
                obj.db_cache()
        listobj.gathered = True
        return listobj

    @classmethod
    def by_id(cls, the_id, instance_name=None):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = {}
        if cls._model.__name__ in this_thread.misc['dbcache'] and the_id in this_thread.misc['dbcache'][cls._model.__name__]:
            if instance_name is None:
                return this_thread.misc['dbcache'][cls._model.__name__][the_id]
            obj = this_thread.misc['dbcache'][cls._model.__name__][the_id]
            obj.fix_instance_name(obj.instanceName, instance_name)
        if instance_name is None:
            obj = cls(id=the_id)
            obj.set_random_instance_name()
        else:
            obj = cls(instance_name, id=the_id)
        return obj

    @classmethod
    def by_uid(cls, uid, instance_name=None):
        if cls._uid not in cls._model.__dict__:
            return None
        db_entry = cls._session.query(cls._model).filter(getattr(cls._model, cls._uid) == uid).first()
        if db_entry is not None:
            return cls.by_id(db_entry.id)
        if instance_name is None:
            obj = cls()
        else:
            obj = cls(instance_name)
        obj.db_set(cls._uid, uid)
        if instance_name is None:
            obj.set_random_instance_name()
        obj.ready()
        return obj

    @classmethod
    def delete_by_id(cls, the_id):
        cls._session.query(cls._model).filter(cls._model.id == the_id).delete()
        cls._session.commit()
        if 'dbcache' in this_thread.misc and cls._model.__name__ in this_thread.misc['dbcache'] and the_id in this_thread.misc['dbcache'][cls._model.__name__]:
            this_thread.misc['dbcache'][cls._model.__name__][the_id]._zombie = True

    @classmethod
    def delete_by_uid(cls, uid):
        if cls._uid not in cls._model.__dict__:
            return
        db_entry = cls._session.query(cls._model).filter(getattr(cls._model, cls._uid) == uid).first()
        if db_entry is not None:
            the_id = db_entry.id
            cls._session.query(cls._model).filter(getattr(cls._model, cls._uid) == uid).delete()
            cls._session.commit()
            if 'dbcache' in this_thread.misc and cls._model.__name__ in this_thread.misc['dbcache'] and the_id in this_thread.misc['dbcache'][cls._model.__name__]:
                this_thread.misc['dbcache'][cls._model.__name__][the_id]._zombie = True

    @classmethod
    def id_exists(cls, the_id):
        db_entry = cls._session.query(cls._model).filter(cls._model.id == the_id).first()
        if db_entry is None:
            return False
        return True

    @classmethod
    def uid_exists(cls, uid):
        if cls._uid not in cls._model.__dict__:
            return False
        db_entry = cls._session.query(cls._model).filter(getattr(cls._model, cls._uid) == uid).first()
        if db_entry is None:
            return False
        return True

    def db_from_cache(self, the_id):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = {}
        if self._model.__name__ not in this_thread.misc['dbcache']:
            this_thread.misc['dbcache'][self._model.__name__] = {}
        if the_id in this_thread.misc['dbcache'][self._model.__name__]:
            return this_thread.misc['dbcache'][self._model.__name__][the_id]
        return None

    def db_cache(self):
        if 'dbcache' not in this_thread.misc:
            this_thread.misc['dbcache'] = {}
        if self._model.__name__ not in this_thread.misc['dbcache']:
            this_thread.misc['dbcache'][self._model.__name__] = {}
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
        db_values = {}
        required_ok = True
        for column in self._model.__dict__.keys():
            if column == 'id' or column.startswith('_'):
                continue
            try:
                db_values[column] = self.db_get(column)  # pylint: disable=assignment-from-no-return
            except:
                if column == self._uid:
                    return
                if column in self._required:
                    if not self._nascent:
                        return
                    required_ok = False
        if self._nascent:
            try:
                db_entry = self.db_find_existing()
                assert db_entry is not None
                for key, val in db_values.items():
                    setattr(db_entry, key, val)
                new_db_values = {}
                for column in self._model.__dict__.keys():
                    if column not in db_values:
                        new_db_values[column] = getattr(db_entry, column)
                        if new_db_values[column] is not None:
                            self.db_set(column, new_db_values[column])
                        else:
                            try:
                                self.db_null(column)
                            except (DAAttributeError, AttributeError):
                                pass
                            except BaseException as err:
                                logmessage("On SQLObject null, " + err.__class__.__name__ + ": " + str(err))
            except BaseException as err:
                logmessage(err.__class__.__name__ + ": " + str(err))
                if not required_ok:
                    return
                db_entry = self._model(**db_values)
                self._session.add(db_entry)
            self._session.commit()
            self.id = db_entry.id
            self._nascent = False
        else:
            if self._orig == db_values:
                return
            db_entry = self._session.query(self._model).filter(self._model.id == self.id).first()
            if db_entry is None:
                self._zombie = True
                return
            for key, val in db_values.items():
                setattr(db_entry, key, val)
            null_keys = []
            for key, val in self._orig.items():
                if key not in db_values:
                    setattr(db_entry, key, None)
                    null_keys.append(key)
            self._session.commit()
            self._orig = db_values
            for key in null_keys:
                self._orig[key] = None

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
            db_entry = self._session.query(self._model).filter(self._model.id == self.id).first()
        else:
            try:
                db_entry = self.db_find_existing()
            except BaseException as err:
                logmessage("On SQLObject read, " + err.__class__.__name__ + ": " + str(err))
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
        db_values = {}
        for column in self._model.__dict__.keys():
            if column == 'id' or column.startswith('_'):
                continue
            db_values[column] = getattr(db_entry, column)
            if db_values[column] is not None:
                self.db_set(column, db_values[column])
            else:
                try:
                    self.db_null(column)
                except (DAAttributeError, AttributeError):
                    pass
                except BaseException as err:
                    logmessage("On SQLObject null, " + err.__class__.__name__ + ": " + str(err))
        self._orig = db_values
        self.db_cache()

    def db_find_existing(self):
        if self._uid not in self._model.__dict__:
            return None
        try:
            the_uid = self.db_get(self._uid)  # pylint: disable=assignment-from-no-return
        except:
            return None
        return self._session.query(self._model).filter(getattr(self._model, self._uid) == the_uid).first()

    def db_get(self, column):  # pylint: disable=unused-argument
        pass

    def db_set(self, column, value):  # pylint: disable=unused-argument
        pass

    def db_null(self, column):  # pylint: disable=unused-argument
        pass

    def has_child(self, rel_name, rel):
        if not (self.ready() and rel.ready()):
            raise DAException("has_child: cannot retrieve data")
        info = self._child_mapping[rel_name]
        model = info['relationship_class']._model
        db_entry = self._session.query(model).filter(model.getattr(info['parent_column']) == self.id, model.getattr(info['child_column']) == rel.id).first()
        if db_entry is None:
            return False
        return True

    def add_child(self, rel_name, child):
        if not self.has_child(rel_name, child):
            info = self._child_mapping[rel_name]
            arg_dict = {}
            arg_dict[info['parent_column']] = self.id
            arg_dict[info['child_column']] = child.id
            db_entry = info['relationship_class']._model(**arg_dict)
            self._session.add(db_entry)
            self._session.commit()

    def get_child(self, rel_name, instance_name=None):
        if not self.ready():
            raise DAException("get_child: cannot retrieve data")
        info = self._child_mapping[rel_name]
        model = info['relationship_class']._model
        if instance_name:
            results = DAList(instance_name, object_type=info['parent_class'])
        else:
            results = []
        indexno = 0
        if instance_name is None:
            for db_entry in list(self._session.query(model).filter(model.getattr(info['parent_column']) == self.id).all()):
                results.append(info['child_class'].by_id(db_entry.getattr(info['child_column'])))
        else:
            for db_entry in list(self._session.query(model).filter(model.getattr(info['parent_column']) == self.id).all()):
                results.append(info['child_class'].by_id(db_entry.getattr(info['child_column'])), instance_name=instance_name + '[' + str(indexno) + ']')
                indexno += 1
        return results

    def del_child(self, rel_name, child):
        if not (self.ready() and child.ready()):
            raise DAException("del_child: cannot retrieve data")
        info = self._child_mapping[rel_name]
        model = info['relationship_class']._model
        self._session.query(model).filter(model.getattr(info['parent_column']) == self.id, model.getattr(info['child_column']) == child.id).delete()
        self._session.commit()

    def has_parent(self, rel_name, rel):
        if not (self.ready() and rel.ready()):
            raise DAException("has_parent: cannot retrieve data")
        info = self._parent_mapping[rel_name]
        model = info['relationship_class']._model
        db_entry = self._session.query(model).filter(model.getattr(info['child_column']) == self.id, model.getattr(info['parent_column']) == rel.id).first()
        if db_entry is None:
            return False
        return True

    def add_parent(self, rel_name, parent):
        if not self.has_parent(rel_name, parent):
            info = self._parent_mapping[rel_name]
            arg_dict = {}
            arg_dict[info['child_column']] = self.id
            arg_dict[info['parent_column']] = parent.id
            db_entry = info['relationship_class']._model(**arg_dict)
            self._session.add(db_entry)
            self._session.commit()

    def get_parent(self, rel_name, instance_name=None):
        if not self.ready():
            raise DAException("get_parent: cannot retrieve data")
        info = self._parent_mapping[rel_name]
        model = info['relationship_class']._model
        if instance_name:
            results = DAList(instance_name, object_type=info['parent_class'])
        else:
            results = []
        indexno = 0
        if instance_name is None:
            for db_entry in list(self._session.query(model).filter(model.getattr(info['child_column']) == self.id).all()):
                results.append(info['parent_class'].by_id(db_entry.getattr(info['parent_column'])))
        else:
            for db_entry in list(self._session.query(model).filter(model.getattr(info['child_column']) == self.id).all()):
                results.append(info['parent_class'].by_id(db_entry.getattr(info['parent_column'])), instance_name=instance_name + '[' + str(indexno) + ']')
                indexno += 1
        return results

    def del_parent(self, rel_name, parent):
        if not (self.ready() and parent.ready()):
            raise DAException("del_parent: cannot retrieve data")
        info = self._parent_mapping[rel_name]
        model = info['relationship_class']._model
        self._session.query(model).filter(model.getattr(info['child_column']) == self.id, model.getattr(info['parent_column']) == parent.id).delete()
        self._session.commit()


def alchemy_url(db_config):
    """Returns a URL representing a database connection."""
    return server.alchemy_url(db_config)


def connect_args(db_config):
    """Returns PostgreSQL arguments for connecting via SSL."""
    return server.connect_args(db_config)


def upgrade_db(url, py_file, engine, version_table=None, name=None, conn_args=None):
    if name is None:
        name = 'alembic'
    if version_table is None:
        version_table = 'alembic_version'
    elif version_table == 'auto':
        version_table = 'alembic_version_' + os.path.abspath(py_file).split(os.sep)[-2]
    if not isinstance(conn_args, dict):
        conn_args = {}
    packagedir = os.path.dirname(os.path.abspath(py_file))
    alembic_path = os.path.join(packagedir, name)
    if not os.path.isdir(alembic_path):
        # logmessage(name + " directory not found in package directory " + packagedir)
        return
    ini_file = os.path.join(packagedir, name + '.ini')
    if not os.path.isfile(ini_file):
        logmessage(name + ".ini file not found at " + ini_file)
        return
    versions_path = os.path.join(alembic_path, 'versions')
    if not os.path.isdir(versions_path):
        os.makedirs(versions_path, exist_ok=True)
    alembic_cfg = Config(ini_file)
    alembic_cfg.set_main_option("sqlalchemy.url", url)
    alembic_cfg.set_main_option("connect_args", json.dumps(conn_args))
    alembic_cfg.set_main_option("script_location", alembic_path)
    if not sqlalchemy.inspect(engine).has_table(version_table):
        command.stamp(alembic_cfg, "head")
    command.upgrade(alembic_cfg, "head")


class SQLObjectRelationship(SQLObject):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._required = [cls._parent[2], cls._child[2]]
        if cls.__name__ not in cls._parent[0]._child_mapping:
            cls._parent[0]._child_mapping[cls.__name__] = {}
        cls._parent[0]._child_mapping[cls.__name__]['relationship_class'] = cls
        cls._parent[0]._child_mapping[cls.__name__]['child_class'] = cls._child[0]
        cls._parent[0]._child_mapping[cls.__name__]['parent_column'] = cls._parent[2]
        cls._parent[0]._child_mapping[cls.__name__]['child_column'] = cls._child[2]
        if cls.__name__ not in cls._child[0]._parent_mapping:
            cls._child[0]._parent_mapping[cls.__name__] = {}
        cls._child[0]._parent_mapping[cls.__name__]['relationship_class'] = cls
        cls._child[0]._parent_mapping[cls.__name__]['parent_class'] = cls._parent[0]
        cls._child[0]._parent_mapping[cls.__name__]['child_column'] = cls._child[2]
        cls._child[0]._parent_mapping[cls.__name__]['parent_column'] = cls._parent[2]

    @classmethod
    def filter_by_parent(cls, instance_name, parent):
        if not parent.ready():
            raise DAException("filter_by_parent: cannot retrieve data")
        filters = {}
        filters[cls._parent[2]] = parent.id
        return cls.filter(instance_name, **filters)

    @classmethod
    def filter_by_child(cls, instance_name, child):
        if not child.ready():
            raise DAException("filter_by_child: cannot retrieve data")
        filters = {}
        filters[cls._child[2]] = child.id
        return cls.filter(instance_name, **filters)

    @classmethod
    def filter_by_parent_child(cls, instance_name, parent, child):
        if not (child.ready() and parent.ready()):
            raise DAException("filter_by_parent_child: cannot retrieve data")
        filters = {}
        filters[cls._parent[2]] = parent.id
        filters[cls._child[2]] = child.id
        return cls.filter(instance_name, **filters)

    def rel_init(self, *pargs, **kwargs):  # pylint: disable=unused-argument
        self.sql_init()
        if not hasattr(self, self._parent[1]):
            self.initializeAttribute(self._parent[1], self._parent[0])
        if not hasattr(self, self._child[1]):
            self.initializeAttribute(self._child[1], self._child[0])

    def db_get(self, column):
        if column == self._parent[2]:
            return getattr(getattr(self, self._parent[1]), 'id')
        if column == self._child[2]:
            return getattr(getattr(self, self._child[1]), 'id')
        raise DAException("Invalid column " + column)

    def db_set(self, column, value):
        if column == self._parent[2]:
            self.reInitializeAttribute(self._parent[1], self._parent[0].using(id=value))
        elif column == self._child[2]:
            self.reInitializeAttribute(self._child[1], self._child[0].using(id=value))

    def db_find_existing(self):
        return self._session.query(self._model).filter(getattr(self._model, self._parent[2]) == getattr(getattr(self, self._parent[1]), 'id'), getattr(self._model, self._child[2]) == getattr(getattr(self, self._child[1]), 'id')).first()


class SQLObjectList(DAList):

    def init(self, *pargs, **kwargs):
        all_arg = kwargs.get('all', False)
        if 'all' in kwargs:
            del kwargs['all']
        super().init(*pargs, **kwargs)
        if all_arg:
            self.elements = self.object_type.all(self.instanceName)


class SQLRelationshipList(DAList):

    def init(self, *pargs, **kwargs):
        parent_arg = kwargs.get('parent', None)
        child_arg = kwargs.get('child', None)
        if 'object_type' in kwargs:
            params = {}
            if 'parent' in kwargs:
                params[kwargs['object_type']._parent[1]] = kwargs['parent']
            if 'child' in kwargs:
                params[kwargs['object_type']._child[1]] = kwargs['child']
            if isinstance(kwargs['object_type'], DAObjectPlusParameters):
                for key, val in params:
                    if key not in kwargs['object_type'].parameters:
                        kwargs['object_type'].parameters[key] = val
            else:
                kwargs['object_type'] = kwargs['object_type'].using(**params)
        if 'parent' in kwargs:
            del kwargs['parent']
        if 'child' in kwargs:
            del kwargs['child']
        super().init(*pargs, **kwargs)
        if parent_arg and not child_arg:
            self.elements = self.object_type.filter_by_parent(self.instanceName, parent_arg)
        elif child_arg and not parent_arg:
            self.elements = self.object_type.filter_by_child(self.instanceName, child_arg)
        elif child_arg and parent_arg:
            self.elements = self.object_type.filter_by_parent_child(self.instanceName, parent_arg, child_arg)

    def hook_on_remove(self, item, *pargs, **kwargs):
        item.db_delete()

    def reset_gathered(self, recursive=False, only_if_empty=False, mark_incomplete=False):
        return


class StandardRelationshipList(SQLRelationshipList):

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.there_is_another = False
        self.gathered = True
        self.complete_attribute = 'complete'
