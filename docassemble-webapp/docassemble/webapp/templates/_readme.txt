# A flask Application routes URLs to model-view functions (in app/XYZ/views.py).
#
# A model-view function typically performs the following steps:
# - Retrieves objects from the database
# - Prepares a template context as a dictionary of name/value pairs
# - Calls render_template('filename.html')
#
# The render_template('filename.html', context) function
# uses the Jinja2 template engine to:
# - Retrieve the HTML template file app/templates/filename.html
# - Replace "{{ name }}" instances with the value of the context['name'] dictionary
# - Return an HTML string wrapped in an HTTP envelope
#
# Jinja2 allows template files to extend base template files.
#    E.g. home_page.html extends page_base.html which extends base.html.
# allowing page generic html to be defined in the base file and page specific html in the extended file.

Flask and Flask-User related subdirectories
- base_templates    # Base templates that other templates extend from
- flask_user        # Flask-User template files. These must be in app/templates/flask_user/

Application template files, organized by module.
Roughly follows the app/ directory structure.
- pages             # Web page templates
- users             # User form templates
