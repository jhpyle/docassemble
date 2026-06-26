from flask_wtf.csrf import CSRFProtect
from flask_babel import Babel
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from docassemble_flask_user import UserManager
from docassemblekvsession import KVSessionExtension
from docassemble.webapp.db_base import Base

csrf = CSRFProtect()
babel = Babel()
cors = CORS()
lm = LoginManager()
the_user_manager = UserManager()
kv_session = KVSessionExtension()
db = SQLAlchemy(model_class=Base)
