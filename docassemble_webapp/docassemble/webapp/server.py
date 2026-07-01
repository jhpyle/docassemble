from docassemble.webapp.flask_app import flaskapp as app
from docassemble.webapp.testing import TestContext  # noqa: F401 # pylint: disable=unused-import
from docassemble.webapp.startup import initialize

application = app
initialize(app)

if __name__ == "__main__":
    app.run()
