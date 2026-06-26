from docassemble.webapp.extensions import db
from docassemble.webapp.hooks.impl import hookimpl
from docassemble.webapp.main.models import Uploads

@hookimpl
def get_new_file_number(user_code, file_name, yaml_file_name):
    new_upload = Uploads(key=user_code, filename=file_name, yamlfile=yaml_file_name)
    db.session.add(new_upload)
    db.session.commit()
    return new_upload.indexno
