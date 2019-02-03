from docassemble.base.rtfng.PropertySets import StandardPaper, MarginsPropertySet
 
class Section( list ) :
    NONE   = 1
    COLUMN = 2
    PAGE   = 3
    EVEN   = 4
    ODD    = 5
    BREAK_TYPES = [ NONE, COLUMN, PAGE, EVEN, ODD ]

    def __init__( self, paper=None, margins=None, break_type=None, headery=None, footery=None, landscape=None, first_page_number=None ) :
        super( Section, self ).__init__()

        self.Paper   = paper   or StandardPaper.A4
        self.SetMargins( margins )

        self.Header = []
        self.Footer = []
        self.FirstHeader = []
        self.FirstFooter = []

        self.SetBreakType( break_type or self.NONE )
        self.SetHeaderY( headery )
        self.SetFooterY( footery )
        self.SetLandscape( landscape )
        self.SetFirstPageNumber( first_page_number )

    def TwipsToRightMargin( self ) :
        return self.Paper.Width - ( self.Margins.Left + self.Margins.Right )

    def SetMargins( self, value ) :
        self.Margins = value or MarginsPropertySet( top=1000, left=1200, bottom=1000, right=1200 )
        self.Width   = self.Paper.Width - ( self.Margins.Left + self.Margins.Right )

    def SetBreakType( self, value ) :
        assert value in self.BREAK_TYPES
        self.BreakType = value
        return self

    def SetHeaderY( self, value ) :
        self.HeaderY = value
        return self

    def SetFooterY( self, value ) :
        self.FooterY = value
        return self

    def SetLandscape( self, value ) :
        self.Landscape = False
        if value : self.Landscape = True
        return self

    def SetFirstPageNumber( self, value ) :
        self.FirstPageNumber = value
        return self

