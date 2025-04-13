from docassemble.webapp.db_object import db
from docassemble.webapp.packages.models import Package
from sqlalchemy import select


def retrieve_package_info(package_name):
    output = None
    for package_row in db.session.execute(select(Package).filter_by(active=True, name=package_name)).scalars():
        output = {k: getattr(package_row, k) for k in ('name', 'type', 'giturl', 'gitsubdir', 'gitbranch', 'version')}
    return output
