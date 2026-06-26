# do not pre-load
# Import SQLAlchemy names
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
# Import any DAObject classes or functions that you will need
from docassemble.base.util import (
    Individual,
    Person,
    DAObject,
    DAFileList,
    DAFile,
    Thing,
    as_datetime,
)
# Import the SQLObject and some associated utility functions
from docassemble.base.sql import (
    register_db,
    create_objects,
    SQLObject,
    SQLObjectRelationship,
    StandardRelationshipList,
)

# Only allow these names (DAObject classes) to be imported with a modules block
__all__ = ['Company', 'Shareholder', 'CompanyShareholder', 'Lawsuit', 'CompanyLawsuit', 'Document', 'LawsuitDocument', 'StandardRelationshipList']

# Set the name of the key in the Configuration with the information about the database
DB_NAME = 'demo db'

# Register the database with flask_sqlalchemy
db = register_db(DB_NAME)


# SQLAlchemy table definition for a Company

class CompanyModel(db.Model):
    __tablename__ = 'company'
    __bind_key__ = DB_NAME
    id = Column(Integer, primary_key=True)
    name = Column(String(250))


# SQLAlchemy table definition for a Shareholder

class ShareholderModel(db.Model):
    __tablename__ = 'shareholder'
    __bind_key__ = DB_NAME
    id = Column(Integer, primary_key=True)
    ssn = Column(String(250), unique=True)
    first_name = Column(String(250))
    last_name = Column(String(250))
    address = Column(String(250))
    unit = Column(String(250))
    city = Column(String(250))
    state = Column(String(250))
    zip = Column(String(250))
    shares = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)


# SQLAlchemy table definition for keeping track of which Companies have which Shareholders

class CompanyShareholderModel(db.Model):
    __tablename__ = 'company_shareholder'
    __bind_key__ = DB_NAME
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    shareholder_id = Column(Integer, ForeignKey('shareholder.id', ondelete='CASCADE'), nullable=False)


# SQLAlchemy table definition for a Lawsuit

class LawsuitModel(db.Model):
    __tablename__ = 'lawsuit'
    __bind_key__ = DB_NAME
    id = Column(Integer, primary_key=True)
    court = Column(String(250))
    docket_number = Column(String(250))
    plaintiff_first_name = Column(String(250))
    plaintiff_last_name = Column(String(250))
    filing_date = Column(DateTime)


# SQLAlchemy table definition for keeping track of which Companies have which Lawsuits

class CompanyLawsuitModel(db.Model):
    __tablename__ = 'company_lawsuit'
    __bind_key__ = DB_NAME
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('company.id', ondelete='CASCADE'), nullable=False)
    lawsuit_id = Column(Integer, ForeignKey('lawsuit.id', ondelete='CASCADE'), nullable=False)


# SQLAlchemy table definition for a Document

class DocumentModel(db.Model):
    __tablename__ = 'document'
    __bind_key__ = DB_NAME
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    upload_id = Column(Integer, unique=True)
    date = Column(DateTime)
    filename = Column(String(250))
    extension = Column(String(250))
    mimetype = Column(String(250))


# SQLAlchemy table definition for keeping track of which Lawsuits have which Documents

class LawsuitDocumentModel(db.Model):
    __tablename__ = 'lawsuit_document'
    __bind_key__ = DB_NAME
    id = Column(Integer, primary_key=True)
    lawsuit_id = Column(Integer, ForeignKey('lawsuit.id', ondelete='CASCADE'), nullable=False)
    document_id = Column(Integer, ForeignKey('document.id', ondelete='CASCADE'), nullable=False)

# Create database objects if any of the above table definitions do not exist, and run alembic if applicable
create_objects(__file__, DB_NAME)


# Python class for a Company

class Company(Person, SQLObject):
    _model = CompanyModel
    _session = db.session
    _required = ['name']
    _uid = 'name'

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.sql_init()

    def db_get(self, column):
        if column == 'name':
            return self.name.text
        raise RuntimeError("Invalid column " + column)

    def db_set(self, column, value):
        if column == 'name':
            self.name.text = value
        else:
            raise RuntimeError("Invalid column " + column)

    def db_null(self, column):
        if column == 'name':
            del self.name.text
        else:
            raise RuntimeError("Invalid column " + column)


# Python class for a Shareholder

class Shareholder(Individual, SQLObject):
    _model = ShareholderModel
    _session = db.session
    _required = ['first_name', 'ssn']
    _uid = 'ssn'

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # The attribute "active" is not stored in SQL.  The default is True but it is
        # set to False by the db_set() function if the value in SQL is null.
        self.active = True
        self.sql_init()

    def db_get(self, column):
        if column == 'ssn':
            return self.ssn
        if column == 'first_name':
            return self.name.first
        if column == 'last_name':
            return self.name.last
        if column == 'address':
            return self.address.address
        if column == 'unit':
            return self.address.unit
        if column == 'city':
            return self.address.city
        if column == 'state':
            return self.address.state
        if column == 'zip':
            return self.address.zip
        if column == 'shares':
            return self.shares
        if column == 'start_date':
            return self.start_date
        if column == 'end_date':
            return self.end_date
        raise RuntimeError("Invalid column " + column)

    def db_set(self, column, value):
        if column == 'ssn':
            self.ssn = value
        elif column == 'first_name':
            self.name.first = value
        elif column == 'last_name':
            self.name.last = value
        elif column == 'address':
            self.address.address = value
        elif column == 'unit':
            self.address.unit = value
        elif column == 'city':
            self.address.city = value
        elif column == 'state':
            self.address.state = value
        elif column == 'zip':
            self.address.zip = value
        elif column == 'shares':
            self.shares = value
        elif column == 'start_date':
            # Docassemble uses a special subclass of the datetime.datetime object, so
            # the as_datetime() function is used to convert the value obtained from SQL.
            self.start_date = as_datetime(value)
        elif column == 'end_date':
            self.end_date = as_datetime(value)
            self.active = False
        else:
            raise RuntimeError("Invalid column " + column)

    def db_null(self, column):
        if column == 'ssn':
            del self.ssn
        elif column == 'first_name':
            del self.name.first
        elif column == 'last_name':
            del self.name.last
        elif column == 'address':
            del self.address.address
        elif column == 'unit':
            del self.address.unit
        elif column == 'city':
            del self.address.city
        elif column == 'state':
            del self.address.state
        elif column == 'zip':
            del self.address.zip
        elif column == 'shares':
            del self.shares
        elif column == 'start_date':
            del self.start_date
        elif column == 'end_date':
            del self.end_date
        else:
            raise RuntimeError("Invalid column " + column)


# Python class for a relationship between a Company and a Shareholder

class CompanyShareholder(DAObject, SQLObjectRelationship):
    _model = CompanyShareholderModel
    _session = db.session
    _parent = [Company, 'company', 'company_id']
    _child = [Shareholder, 'shareholder', 'shareholder_id']

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.rel_init(*pargs, **kwargs)


# Python class for a lawsuit

class Lawsuit(Individual, SQLObject):
    _model = LawsuitModel
    _session = db.session
    _required = ['docket_number', 'court']

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # A lawsuit needs a plaintiff, so the "plaintiff" attribute is
        # initialized when the object itself is initialized.
        self.initializeAttribute('plaintiff', Individual)
        self.sql_init()

    def db_get(self, column):
        if column == 'court':
            return self.court
        if column == 'docket_number':
            return self.docket_number
        if column == 'plaintiff_first_name':
            return self.plaintiff.name.first
        if column == 'plaintiff_last_name':
            return self.plaintiff.name.last
        if column == 'filing_date':
            return self.filing_date
        raise RuntimeError("Invalid column " + column)

    def db_set(self, column, value):
        if column == 'court':
            self.court = value
        elif column == 'docket_number':
            self.docket_number = value
        elif column == 'plaintiff_first_name':
            self.plaintiff.name.first = value
        elif column == 'plaintiff_last_name':
            self.plaintiff.name.last = value
        elif column == 'filing_date':
            self.filing_date = as_datetime(value)
        else:
            raise RuntimeError("Invalid column " + column)

    def db_null(self, column):
        if column == 'court':
            del self.court
        elif column == 'docket_number':
            del self.docket_number
        elif column == 'plaintiff_first_name':
            del self.plaintiff.name.first
        elif column == 'plaintiff_last_name':
            del self.plaintiff.name.last
        elif column == 'filing_date':
            del self.filing_date
        else:
            raise RuntimeError("Invalid column " + column)
    # Since the unique identifier for a lawsuit isn't really the docket number, but the combination of the
    # court and the docket number, we use a db_find_existing method.

    def db_find_existing(self):
        try:
            return self._session.query(LawsuitModel).filter(LawsuitModel.court == self.court, LawsuitModel.docket_number == self.docket_number).first()
        except:
            return None


# Python class for a relationship between a Company and a Lawsuit

class CompanyLawsuit(DAObject, SQLObjectRelationship):
    _model = CompanyLawsuitModel
    _session = db.session
    _parent = [Company, 'company', 'company_id']
    _child = [Lawsuit, 'lawsuit', 'lawsuit_id']

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.rel_init(*pargs, **kwargs)


# Python class for a document in a lawsuit

class Document(Thing, SQLObject):
    _model = DocumentModel
    _session = db.session
    _required = ['name', 'upload_id', 'filename', 'extension', 'mimetype', 'upload_id']
    _uid = 'upload_id'

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.sql_init()

    def db_get(self, column):
        if column == 'name':
            return self.name.text
        if column == 'upload_id':
            return self.upload[0].number
        if column == 'date':
            return self.date
        if column == 'filename':
            return self.upload[0].filename
        if column == 'extension':
            return self.upload[0].extension
        if column == 'mimetype':
            return self.upload[0].mimetype
        raise RuntimeError("Invalid column " + column)

    def ensure_upload_exists(self):
        # Since file uploads are a special type of object in Docassemble,
        # we need to make sure the object exists before we can populate
        # its attributes based on values in SQL.
        # We use this method in db_set() to make sure the object exists in case
        # any of the relevant columns in SQL are populated.
        if not hasattr(self, 'upload'):
            self.initializeAttribute('upload', DAFileList)
            self.upload.appendObject(DAFile)

    def db_set(self, column, value):
        if column == 'name':
            self.name.text = value
        elif column == 'upload_id':
            self.ensure_upload_exists()
            self.upload[0].number = value
            # The "ok" attribute should be set to True when a DAFile object
            # has a "number."
            self.upload[0].ok = True
        elif column == 'date':
            self.date = as_datetime(value)
        elif column == 'filename':
            self.ensure_upload_exists()
            self.upload[0].filename = value
            # The "has_specific_filename" attribute should be set to True
            # when a DAFile object has a "filename."
            self.upload[0].has_specific_filename = True
        elif column == 'extension':
            self.ensure_upload_exists()
            self.upload[0].extension = value
        elif column == 'mimetype':
            self.ensure_upload_exists()
            self.upload[0].mimetype = value
        else:
            raise RuntimeError("Invalid column " + column)

    def db_null(self, column):
        if column == 'name':
            del self.name.text
        elif column == 'upload_id':
            del self.upload[0].number
            self.upload[0].ok = False
            if hasattr(self.upload[0], 'initialized'):
                del self.upload[0].initialized
        elif column == 'date':
            del self.date
        elif column == 'filename':
            del self.upload[0].filename
            self.upload[0].has_specific_filename = False
        elif column == 'extension':
            del self.upload[0].extension
        elif column == 'mimetype':
            del self.upload[0].mimetype
        else:
            raise RuntimeError("Invalid column " + column)


# Python class for a relationship between a Lawsuit and a Document

class LawsuitDocument(DAObject, SQLObjectRelationship):
    _model = LawsuitDocumentModel
    _session = db.session
    _parent = [Lawsuit, 'lawsuit', 'lawsuit_id']
    _child = [Document, 'document', 'document_id']

    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.rel_init(*pargs, **kwargs)
