from types import IntType, FloatType, LongType, StringTypes
from copy import deepcopy
from binascii import hexlify

from Renderer import Renderer
from Constants import *
from Styles import *
from PropertySets import StandardColours, StandardFonts, StandardPaper

from docassemble.base.rtfng.document.base import TAB, LINE, RawCode
from docassemble.base.rtfng.document.section import Section
from docassemble.base.rtfng.document.character import Text, Inline

#class UnhandledParamError( Exception ) :  # Currently unused.
#    def __init__( self, param ) :
#        Exception.__init__( self, "Don't know what to do with param %s" % param )

#
#    Finally a StyleSheet in which all of this stuff is put together
#
class StyleSheet :
    def __init__( self, colours=None, fonts=None ) :

        self.Colours = colours or deepcopy( StandardColours )
        self.Fonts   = fonts   or deepcopy( StandardFonts   )

        self.TextStyles      = AttributedList()
        self.ParagraphStyles = AttributedList()

    def Copy(self):
        return deepcopy(self)

def MakeDefaultStyleSheet( ) :
    result = StyleSheet()

    NormalText = TextStyle( TextPropertySet( result.Fonts.Arial, 22 ) )

    ps = ParagraphStyle( 'Normal',
                         NormalText.Copy(),
                         ParagraphPropertySet( space_before = 60,
                                               space_after  = 60 ) )
    result.ParagraphStyles.append( ps )

    ps = ParagraphStyle( 'Normal Short',
                         NormalText.Copy() )
    result.ParagraphStyles.append( ps )

    NormalText.textProps.size = 32
    ps = ParagraphStyle( 'Heading 1',
                         NormalText.Copy(),
                         ParagraphPropertySet( space_before = 240,
                                               space_after  = 60 ) )
    result.ParagraphStyles.append( ps )

    NormalText.textProps.size = 24
    NormalText.textProps.bold = True
    ps = ParagraphStyle( 'Heading 2',
                         NormalText.Copy(),
                         ParagraphPropertySet( space_before = 240,
                                               space_after  = 60 ) )
    result.ParagraphStyles.append( ps )

    #    Add some more in that are based on the normal template but that
    #    have some indenting set that makes them suitable for doing numbered
    normal_numbered = result.ParagraphStyles.Normal.Copy()
    normal_numbered.name = 'Normal Numbered'
    normal_numbered.ParagraphPropertySet.SetFirstLineIndent( TabPropertySet.DEFAULT_WIDTH * -1 )
    normal_numbered.ParagraphPropertySet.SetLeftIndent     ( TabPropertySet.DEFAULT_WIDTH )

    result.ParagraphStyles.append( normal_numbered )

    normal_numbered2 = result.ParagraphStyles.Normal.Copy()
    normal_numbered2.name = 'Normal Numbered 2'
    normal_numbered2.ParagraphPropertySet.SetFirstLineIndent( TabPropertySet.DEFAULT_WIDTH * -1 )
    normal_numbered2.ParagraphPropertySet.SetLeftIndent     ( TabPropertySet.DEFAULT_WIDTH *  2 )

    result.ParagraphStyles.append( normal_numbered2 )

    ## LIST STYLES
    for idx, indent in [ (1, TabPropertySet.DEFAULT_WIDTH    ),
                         (2, TabPropertySet.DEFAULT_WIDTH * 2),
                         (3, TabPropertySet.DEFAULT_WIDTH * 3) ] :
        indent = TabPropertySet.DEFAULT_WIDTH
        ps = ParagraphStyle( 'List %s' % idx,
                             TextStyle( TextPropertySet( result.Fonts.Arial, 22 ) ),
                             ParagraphPropertySet( space_before = 60,
                                                   space_after  = 60,
                                                   first_line_indent = -indent,
                                                   left_indent       = indent) )
        result.ParagraphStyles.append( ps )

    return result

PAGE_NUMBER   = RawCode( r'{\field{\fldinst page}}'   )
TOTAL_PAGES   = RawCode( r'{\field{\fldinst numpages}}' )
SECTION_PAGES = RawCode( r'{\field{\fldinst sectionpages}}' )
ARIAL_BULLET  = RawCode( r'{\f2\'95}' )

class Document :
    def __init__( self, style_sheet=None, default_language=None, view_kind=None, view_zoom_kind=None, view_scale=None ) :
        self.StyleSheet = style_sheet or MakeDefaultStyleSheet()
        self.Sections = AttributedList( Section )

        self.SetTitle( None )

        self.DefaultLanguage = default_language or Languages.DEFAULT
        self.ViewKind        = view_kind        or ViewKind.DEFAULT
        self.ViewZoomKind    = view_zoom_kind
        self.ViewScale       = view_scale

    def NewSection( self, *params, **kwargs ) :
        result = Section( *params, **kwargs )
        self.Sections.append( result )
        return result

    def SetTitle( self, value ) :
        self.Title = value
        return self

    def Copy( self ) :
        result = Document( style_sheet      = self.StyleSheet.Copy(),
                           default_language = self.DefaultLanguage,
                           view_kind        = self.ViewKind,
                           view_zoom_kind   = self.ViewZoomKind,
                           view_scale       = self.ViewScale )
        result.SetTitle( self.Title )
        result.Sections = self.Sections.Copy()

        return result

    # XXX this is a temporary fix until I figure out the best way to refactor
    # the renderer
    def write(self, fhOrFilename):
        if isinstance(fhOrFilename, str):
            fh = open(fhOrFilename, 'w+')
        else:
            fh = fhOrFilename
        r = Renderer()
        r.Write(self, fh)

