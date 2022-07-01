# do not pre-load
# Import any DAObject classes that you will need
from docassemble.base.util import Individual, Person, DAObject
# Import the SQLObject and some associated utility functions
from docassemble.base.sql import alchemy_url, connect_args, upgrade_db, SQLObject, SQLObjectRelationship
# Import SQLAlchemy names
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Only allow these names (DAObject classes) to be imported with a modules block
__all__ = ['Bank', 'Customer', 'BankCustomer']

# Create the base class for SQLAlchemy table definitions
Base = declarative_base()

# SQLAlchemy table definition for a Bank
class BankModel(Base):
    __tablename__ = 'bank'
    id = Column(Integer, primary_key=True)
    routing = Column(String(250), unique=True)
    name = Column(String(250))

# SQLAlchemy table definition for a Customer
class CustomerModel(Base):
    __tablename__ = 'customer'
    id = Column(Integer, primary_key=True)
    ssn = Column(String(250), unique=True)
    first_name = Column(String(250))
    last_name = Column(String(250))
    address = Column(String(250))
    unit = Column(String(250))
    city = Column(String(250))
    state = Column(String(250))
    zip = Column(String(250))

# SQLAlchemy table definition for keeping track of which Banks have which Customers
class BankCustomerModel(Base):
    __tablename__ = 'bank_customer'
    id = Column(Integer, primary_key=True)
    bank_id = Column(Integer, ForeignKey('bank.id', ondelete='CASCADE'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customer.id', ondelete='CASCADE'), nullable=False)

# Form the URL for connecting to the database based on the "demo db" directive in the Configuration
url = alchemy_url('demo db')

# Build the "engine" for connecting to the SQL server, using the URL for the database.
conn_args = connect_args('demo db')
if url.startswith('postgres'):
    engine = create_engine(url, connect_args=conn_args, pool_pre_ping=False)
else:
    engine = create_engine(url, pool_pre_ping=False)

# Create the tables
Base.metadata.create_all(engine)

# Get SQLAlchemy ready
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)()

# Perform any necessary database schema updates using alembic, if there is an alembic
# directory and alembic.ini file in the package.
upgrade_db(url, __file__, engine, conn_args=conn_args)

# Define Bank as both a DAObject and SQLObject
class Bank(Person, SQLObject):
    # This tells the SQLObject code what the SQLAlchemy model is
    _model = BankModel
    # This tells the SQLObject code how to access the database
    _session = DBSession
    # This indicates that an object is not ready to be saved to SQL unless the "name" column is defined
    _required = ['name']
    # This indicates that the human-readable unique identifier for the table is the column "routing"
    _uid = 'routing'
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        # This runs necessary SQLObject initialization code for the instance
        self.sql_init()
    # The db_get function specifies how to get attributes from the DAObject for purposes of setting SQL column values
    def db_get(self, column):
        if column == 'name':
            return self.name.text
        if column == 'routing':
            return self.routing
        raise Exception("Invalid column " + column)
    # The db_set function specifies how to set attributes of the DAObject on the basis of non-null SQL column values
    def db_set(self, column, value):
        if column == 'name':
            self.name.text = value
        elif column == 'routing':
            self.routing = value
        else:
            raise Exception("Invalid column " + column)
    # The db_null function specifies how to delete attributes of the DAObject when the SQL column value becomes null
    def db_null(self, column):
        if column == 'name':
            del self.name.text
        elif column == 'routing':
            del self.routing
        else:
            raise Exception("Invalid column " + column)
    # This is an example of a method that uses SQLAlchemy to return True or False
    def has_customer(self, customer):
        if not (self.ready() and customer.ready()):
            raise Exception("has_customer: cannot retrieve data")
        # this opens a connection to the SQL database
        db_entry = self._session.query(BankCustomerModel).filter(BankCustomerModel.bank_id == self.id, BankCustomerModel.customer_id == customer.id).first()
        if db_entry is None:
            return False
        return True
    # This is an example of a method that uses SQLAlchemy to add a record to the BankCustomer SQL table
    # to indicate that a bank has a customer.  Note that it is designed to be idempotent; it will not add
    # a duplicate record.
    def add_customer(self, customer):
        if not self.has_customer(customer):
            db_entry = BankCustomerModel(bank_id=self.id, customer_id=customer.id)
            self._session.add(db_entry)
            self._session.commit()
    # This is an example of a method that uses SQLAlchemy to return a list of Customer objects.
    # It uses the by_id() class method to return a Customer object for the given id.
    def get_customers(self):
        if not self.ready():
            raise Exception("get_customers: cannot retrieve data")
        results = []
        for db_entry in self._session.query(BankCustomerModel).filter(BankCustomerModel.bank_id == self.id).all():
            results.append(Customer.by_id(db_entry.customer_id))
        return results
    # This is an example of a method that uses SQLAlchemy to delete a bank-customer relationship
    def del_customer(self, customer):
        if not (self.ready() and customer.ready()):
            raise Exception("del_customer: cannot retrieve data")
        self._session.query(BankCustomerModel).filter(BankCustomerModel.bank_id == self.id, BankCustomerModel.customer_id == customer.id).delete()
        self._session.commit()

class Customer(Individual, SQLObject):
    _model = CustomerModel
    _session = DBSession
    _required = ['first_name']
    _uid = 'ssn'
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
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
        raise Exception("Invalid column " + column)
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

class BankCustomer(DAObject, SQLObjectRelationship):
    _model = BankCustomerModel
    _session = DBSession
    _parent = [Bank, 'bank', 'bank_id']
    _child = [Customer, 'customer', 'customer_id']
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self.rel_init(*pargs, **kwargs)
    def db_get(self, column):
        if column == 'bank_id':
            return self.bank.id
        if column == 'customer_id':
            return self.customer.id
        raise Exception("Invalid column " + column)
    def db_set(self, column, value):
        if column == 'bank_id':
            self.bank = Bank.by_id(value)
        elif column == 'customer_id':
            self.customer = Customer.by_id(value)
        else:
            raise Exception("Invalid column " + column)
    # A db_find_existing method is defined here because the default db_find_existing() method for
    # the SQLObject class tries to find existing records based on a unique identifier column indicated
    # by the _uid attribute.  Since the unique identifier for a bank-customer relationship record is
    # not a single column, but rather the combination of bank ID and customer ID, there is no _uid
    # column for the default db_find_existing() method to use.  But we can write our own method for
    # how to locate an existing record based on Python object attributes (.bank.id and .customer.id).
    def db_find_existing(self):
        try:
            return self._session.query(BankCustomerModel).filter(BankCustomerModel.bank_id == self.bank.id, BankCustomerModel.customer_id == self.customer.id).first()
        except:
            return None
