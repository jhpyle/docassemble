from sphinx.application import TemplateBridge
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.highlighting import PygmentsBridge
from sphinx.jinja2glue import BuiltinTemplateLoader
from pygments import highlight
from pygments.lexer import RegexLexer, bygroups, using
from pygments.token import *
from pygments.filter import Filter, apply_filters
from pygments.lexers import PythonLexer, PythonConsoleLexer
from pygments.formatters import HtmlFormatter, LatexFormatter
import re
import os
from mako.lookup import TemplateLookup
from mako.template import Template
from mako.ext.pygmentplugin import MakoLexer

rtd = os.environ.get('READTHEDOCS', None) == 'True'

class MakoBridge(TemplateBridge):
    def init(self, builder, *args, **kw):
        self.jinja2_fallback = BuiltinTemplateLoader()
        self.jinja2_fallback.init(builder, *args, **kw)

        builder.config.html_context['site_base'] = builder.config['site_base']

        self.lookup = TemplateLookup(
            directories=builder.config.templates_path,
            imports=[
                "from builder import util"
            ],
            #format_exceptions=True,
        )

    def render(self, template, context):
        template = template.replace(".html", ".mako")
        context['prevtopic'] = context.pop('prev', None)
        context['nexttopic'] = context.pop('next', None)

        # RTD layout
        if rtd:
            # add variables if not present, such
            # as if local test of READTHEDOCS variable
            if 'MEDIA_URL' not in context:
                context['MEDIA_URL'] = "http://media.readthedocs.org/"
            if 'slug' not in context:
                context['slug'] = "mako-test-slug"
            if 'url' not in context:
                context['url'] = "/some/test/url"
            if 'current_version' not in context:
                context['current_version'] = "some_version"
            if 'versions' not in context:
                context['versions'] = [('default', '/default/')]

            context['docs_base'] = "http://readthedocs.org"
            context['toolbar'] = True
            context['layout'] = "rtd_layout.mako"
            context['pdf_url'] = "%spdf/%s/%s/%s.pdf" % (
                    context['MEDIA_URL'],
                    context['slug'],
                    context['current_version'],
                    context['slug']
            )
        # local docs layout
        else:
            context['toolbar'] = False
            context['docs_base'] = "/"
            context['layout'] = "layout.mako"

        context.setdefault('_', lambda x:x)
        return self.lookup.get_template(template).render_unicode(**context)

    def render_string(self, template, context):
        # this is used for  .js, .css etc. and we don't have
        # local copies of that stuff here so use the jinja render.
        return self.jinja2_fallback.render_string(template, context)

class StripDocTestFilter(Filter):
    def filter(self, lexer, stream):
        for ttype, value in stream:
            if ttype is Token.Comment and re.match(r'#\s*doctest:', value):
                continue
            yield ttype, value


def autodoc_skip_member(app, what, name, obj, skip, options):
    if what == 'class' and skip and name == '__init__':
        return False
    else:
        return skip

def setup(app):
#    app.connect('autodoc-skip-member', autodoc_skip_member)
    # Mako is already in Pygments, adding the local
    # lexer here so that the latest syntax is available
    app.add_lexer('mako', MakoLexer())
    app.add_config_value('site_base', "", True)

