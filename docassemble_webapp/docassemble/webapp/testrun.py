#from werkzeug.contrib.profiler import ProfilerMiddleware
from docassemble.webapp.server import app
#app.wsgi_app = ProfilerMiddleware(app.wsgi_app)
app.run(debug=True, port=4041)
