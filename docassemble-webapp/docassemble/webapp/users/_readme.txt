This is the root directory of a Flask application.

It contains the following Flask-specific subdirectories:
- static       # This subdirectory will be mapped to the "/static/" URL
- templates    # Jinja2 HTML template files

It contains the following special App subdirectories:
- config       # Application setting files
- startup      # Application startup code

The remaining subdirectories organizes the code into functional modules:
- pages        # Web pages (without a CMS for now)
- users        # User and Role related code

Each functional models organizes code in the following way:
- models.py    # Database/Object models
- views.py     # Model-View functions that typically:
               # - Loads objects from the database
               # - Prepares a template data context
               # - Renders the context using a Jinja2 template file

It contains the following Python-specific files:
- __init__.py  # special Python file to turn a subdirectory into a Python 'package'
               # Python packages can be accessed using the Python 'import' statement
