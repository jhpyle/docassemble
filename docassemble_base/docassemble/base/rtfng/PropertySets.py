"""
PropertySets group common attributes together, each property set is used to control a specific part of the rendering.

PropertySets can be used in different elements of the document.

For example the FramePropertySet is used in paragraphs, tables, cells, etc.

The TextPropertySet can be used for text or in a Paragraph Style.

"""

from types import StringType
from copy import deepcopy


#
#    We need some basic Type like fonts, colours and paper definitions
#
def MakeAttributeName(value):
    assert value and type(value)is StringType
    value = value.replace(' ', '')
    return value

class AttributedList(list):
    def __init__(self, accepted_type=None):
        super(AttributedList, self).__init__()
        self.AcceptedType = accepted_type
        self._append = super(AttributedList, self).append

    def append(self, *values):
        for value in values:
            if self.AcceptedType:
                assert isinstance(value, self.AcceptedType)
            self._append(value)
            name = getattr(value, 'name', None)
            if name:
                name = MakeAttributeName(value.name)
                setattr(self, name, value)

    def Copy(self):
        return deepcopy(self)

    def __deepcopy__(self, memo):
        result = self.__class__()
        result.append(*self[:])
        return result

class Colour:
    def __init__(self, name, red, green, blue):
        self.name = name
        self.SetRed(red)
        self.SetGreen(green)
        self.SetBlue(blue)

    def SetRed(self, value):
        self.Red = value
        return self

    def SetGreen(self, value):
        self.Green = value
        return self

    def SetBlue(self, value):
        self.Blue = value
        return self

class Colours(AttributedList):
    def __init__(self):
        super(Colours, self).__init__(Colour)

class Font:
    def __init__(self, name, family, character_set=0, pitch=None, panose=None,
                 alternate=None):
        self.name = name
        self.SetFamily(family)
        self.SetCharacterSet(character_set)
        self.SetPitch(pitch)
        self.SetPanose(panose)
        self.SetAlternate(alternate)

    def SetFamily(self, value):
        self.Family = value
        return self

    def SetCharacterSet(self, value):
        self.CharacterSet = value
        return self

    def SetPitch(self, value):
        self.Pitch = value
        return self

    def SetPanose(self, value):
        self.Panose = value
        return self

    def SetAlternate(self, value):
        self.Alternate = value
        return self

class Fonts(AttributedList):
    def __init__(self):
        super(Fonts, self).__init__(Font)

class Paper:
    def __init__(self, name, code, description, width, height):
        self.name = name
        self.SetCode(code)
        self.SetDescription(description)
        self.SetWidth(width)
        self.SetHeight(height)

    def SetCode(self, value):
        self.Code = value
        return self

    def SetDescription(self, value):
        self.Description = value
        return self

    def SetWidth(self, value):
        self.Width = value
        return self

    def SetHeight(self, value):
        self.Height = value
        return self

class Papers(AttributedList):
    def __init__(self):
        super(Papers, self).__init__(Paper)

#
#    Then we have property sets which represent different aspects of Styles
#
class MarginsPropertySet:
    def __init__(self, top=None, left=None, bottom=None, right=None):
        self.SetTop(top)
        self.SetLeft(left)
        self.SetBottom(bottom)
        self.SetRight(right)

    def SetTop(self, value):
        self.Top = value
        return self

    def SetLeft(self, value):
        self.Left = value
        return self

    def SetBottom(self, value):
        self.Bottom = value
        return self

    def SetRight(self, value):
        self.Right = value
        return self

class ShadingPropertySet:
    HORIZONTAL =  1
    VERTICAL =  2
    FORWARD_DIAGONAL =  3
    BACKWARD_DIAGONAL =  4
    VERTICAL_CROSS =  5
    DIAGONAL_CROSS =  6
    DARK_HORIZONTAL =  7
    DARK_VERTICAL =  8
    DARK_FORWARD_DIAGONAL =  9
    DARK_BACKWARD_DIAGONAL = 10
    DARK_VERTICAL_CROSS = 11
    DARK_DIAGONAL_CROSS = 12
    PATTERNS = [
        HORIZONTAL,
        VERTICAL,
        FORWARD_DIAGONAL,
        BACKWARD_DIAGONAL,
        VERTICAL_CROSS,
        DIAGONAL_CROSS,
        DARK_HORIZONTAL,
        DARK_VERTICAL,
        DARK_FORWARD_DIAGONAL,
        DARK_BACKWARD_DIAGONAL,
        DARK_VERTICAL_CROSS,
        DARK_DIAGONAL_CROSS
        ]

    def __init__(self, shading=None, pattern=None, foreground=None,
                 background=None):
        self.SetShading(shading)
        self.SetForeground(foreground)
        self.SetBackground(background)
        self.SetPattern(pattern)

    def __deepcopy__(self, memo):
        return ShadingPropertySet(
            self.Shading, self.Foreground, self.Background, self.Pattern)

    def SetShading(self, value):
        self.Shading = value
        return self

    def SetPattern(self, value):
        assert value is None or value in self.PATTERNS
        self.Pattern = value
        return self

    def SetForeground(self, value):
        assert not value or isinstance(value, Colour)
        self.Foreground = value
        return self

    def SetBackground(self, value):
        assert not value or isinstance(value, Colour)
        self.Background = value
        return self


class BorderPropertySet:
    SINGLE = 1
    DOUBLE = 2
    SHADOWED = 3
    DOUBLED = 4
    DOTTED = 5
    DASHED = 6
    HAIRLINE = 7
    STYLES = [ SINGLE, DOUBLE, SHADOWED, DOUBLED, DOTTED, DASHED, HAIRLINE ]

    def __init__(self, width=None, style=None, colour=None, spacing=None):
        self.SetWidth(width)
        self.SetStyle(style or self.SINGLE)
        self.SetColour(colour)
        self.SetSpacing(spacing)

    def SetWidth(self, value):
        self.Width = value
        return self

    def SetStyle(self, value):
        assert value is None or value in self.STYLES
        self.Style = value
        return self

    def SetColour(self, value):
        assert value is None or isinstance(value, Colour)
        self.Colour = value
        return self

    def SetSpacing(self, value):
        self.Spacing = value
        return self

class FramePropertySet:
    def __init__(self, top=None, left=None, bottom=None, right=None):
        self.SetTop(top)
        self.SetLeft(left)
        self.SetBottom(bottom)
        self.SetRight(right)

    def SetTop(self, value):
        assert value is None or isinstance(value, BorderPropertySet)
        self.Top = value
        return self

    def SetLeft(self, value):
        assert value is None or isinstance(value, BorderPropertySet)
        self.Left = value
        return self

    def SetBottom(self, value):
        assert value is None or isinstance(value, BorderPropertySet)
        self.Bottom = value
        return self

    def SetRight(self, value):
        assert value is None or isinstance(value, BorderPropertySet)
        self.Right = value
        return self

class TabPropertySet:
    DEFAULT_WIDTH = 720

    LEFT = 1
    RIGHT = 2
    CENTER = 3
    DECIMAL = 4
    ALIGNMENT = [ LEFT, RIGHT, CENTER, DECIMAL ]

    DOTS = 1
    HYPHENS = 2
    UNDERLINE = 3
    THICK_LINE = 4
    EQUAL_SIGN = 5
    LEADERS = [ DOTS, HYPHENS, UNDERLINE, THICK_LINE, EQUAL_SIGN ]

    def __init__(self, width=None, alignment=None, leader=None):
        self.SetWidth(width)
        self.SetAlignment(alignment or self.LEFT)
        self.SetLeader(leader)

    def SetWidth(self, value):
        self.Width = value
        return self

    def SetAlignment(self, value):
        assert value in self.ALIGNMENT
        self.Alignment = value
        return self

    def SetLeader(self, value):
        assert not value or value in self.LEADERS
        self.Leader = value
        return self

class TextPropertySet:

    def __init__(self, font=None, size=None, bold=False, italic=False,
                 underline=False, colour=None, frame=None, expansion=None,
                 unicodeText=False):
        self.font = font
        self.size = size
        self.unicode = unicodeText
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.colour = colour
        self.frame = frame
        self.strikeThrough = False
        self.dottedUnderline = False
        self.doubleUnderline = False
        self.wordUnderline = False
        self.expansion = expansion

    def Copy(self):
        return deepcopy(self)

    def __deepcopy__(self, memo):
        # the font must remain a reference to the same font that we are looking
        # at so we want to stop the recursiveness at this point and return an
        # object with the right references.
        result = TextPropertySet(
            self.font, self.size, self.bold, self.italic, self.underline,
            self.colour, deepcopy(self.frame, memo))
        result.strikeThrough = self.strikeThrough
        return result

class ParagraphPropertySet:
    LEFT = 1
    RIGHT = 2
    CENTER = 3
    JUSTIFY = 4
    DISTRIBUTE = 5
    ALIGNMENT = [ LEFT, RIGHT, CENTER, JUSTIFY, DISTRIBUTE ]

    def __init__(self, alignment=None, space_before=None, space_after=None,
                 tabs=None, first_line_indent=None, left_indent=None,
                 right_indent=None, page_break_before=None):
        self.SetAlignment  (alignment or self.LEFT)
        self.SetSpaceBefore(space_before)
        self.SetSpaceAfter (space_after)
        self.Tabs = []
        if tabs:
            apply(self.SetTabs, tabs)
        self.SetFirstLineIndent(first_line_indent or None)
        self.SetLeftIndent(left_indent or None)
        self.SetRightIndent(right_indent or None)
        self.SetPageBreakBefore(page_break_before)
        self.SetSpaceBetweenLines(None)

    def Copy(self):
        return deepcopy(self)

    def SetAlignment(self, value):
        assert not value or value in self.ALIGNMENT
        self.Alignment = value or self.LEFT
        return self

    def SetSpaceBefore(self, value):
        self.SpaceBefore = value
        return self

    def SetSpaceAfter(self, value):
        self.SpaceAfter = value
        return self

    def SetTabs(self, *params):
        self.Tabs = params
        return self

    def SetFirstLineIndent(self, value):
        self.FirstLineIndent = value
        return self

    def SetLeftIndent(self, value):
        self.LeftIndent = value
        return self

    def SetRightIndent(self, value):
        self.RightIndent = value
        return self

    def SetSpaceBetweenLines(self, value):
        self.SpaceBetweenLines = value
        return self

    def SetPageBreakBefore(self, value):
        self.PageBreakBefore = False
        if value: self.PageBreakBefore = True
        return self


#                                               red green blue
StandardColours = Colours()
StandardColours.append(Colour('Black', 0, 0, 0))
StandardColours.append(Colour('Blue', 0, 0, 255))
StandardColours.append(Colour('Turquoise', 0, 255, 255))
StandardColours.append(Colour('Green', 0, 255, 0))
StandardColours.append(Colour('Pink', 255, 0, 255))
StandardColours.append(Colour('Red', 255, 0, 0))
StandardColours.append(Colour('Yellow', 255, 255, 0))
StandardColours.append(Colour('White', 255, 255, 255))
StandardColours.append(Colour('Blue Dark', 0, 0, 128))
StandardColours.append(Colour('Teal', 0, 128, 128))
StandardColours.append(Colour('Green Dark', 0, 128, 0))
StandardColours.append(Colour('Violet', 128, 0, 128))
StandardColours.append(Colour('Red Dark', 128, 0, 0))
StandardColours.append(Colour('Yellow Dark', 128, 128, 0))
StandardColours.append(Colour('Grey Dark', 128, 128, 128))
StandardColours.append(Colour('Grey', 192, 192, 192))

StandardFonts = Fonts()
StandardFonts.append(Font('Arial', 'swiss', 0, 2, '020b0604020202020204'))
StandardFonts.append(Font('Arial Black', 'swiss', 0, 2, '020b0a04020102020204'))
StandardFonts.append(Font('Arial Narrow', 'swiss', 0, 2, '020b0506020202030204'))
StandardFonts.append(Font('Bitstream Vera Sans Mono', 'modern', 0, 1, '020b0609030804020204'))
StandardFonts.append(Font('Bitstream Vera Sans', 'swiss', 0, 2, '020b0603030804020204'))
StandardFonts.append(Font('Bitstream Vera Serif', 'roman', 0, 2, '02060603050605020204'))
StandardFonts.append(Font('Book Antiqua', 'roman', 0, 2, '02040602050305030304'))
StandardFonts.append(Font('Bookman Old Style', 'roman', 0, 2, '02050604050505020204'))
StandardFonts.append(Font('Castellar', 'roman', 0, 2, '020a0402060406010301'))
StandardFonts.append(Font('Century Gothic', 'swiss', 0, 2, '020b0502020202020204'))
StandardFonts.append(Font('Comic Sans MS', 'script', 0, 2, '030f0702030302020204'))
StandardFonts.append(Font('Courier New', 'modern', 0, 1, '02070309020205020404'))
StandardFonts.append(Font('Franklin Gothic Medium', 'swiss', 0, 2, '020b0603020102020204'))
StandardFonts.append(Font('Garamond', 'roman', 0, 2, '02020404030301010803'))
StandardFonts.append(Font('Georgia', 'roman', 0, 2, '02040502050405020303'))
StandardFonts.append(Font('Haettenschweiler', 'swiss', 0, 2, '020b0706040902060204'))
StandardFonts.append(Font('Impact', 'swiss', 0, 2, '020b0806030902050204'))
StandardFonts.append(Font('Lucida Console', 'modern', 0, 1, '020b0609040504020204'))
StandardFonts.append(Font('Lucida Sans Unicode', 'swiss', 0, 2, '020b0602030504020204'))
StandardFonts.append(Font('Microsoft Sans Serif', 'swiss', 0, 2, '020b0604020202020204'))
StandardFonts.append(Font('Monotype Corsiva', 'script', 0, 2, '03010101010201010101'))
StandardFonts.append(Font('Palatino Linotype', 'roman', 0, 2, '02040502050505030304'))
StandardFonts.append(Font('Papyrus', 'script', 0, 2, '03070502060502030205'))
StandardFonts.append(Font('Sylfaen', 'roman', 0, 2, '010a0502050306030303'))
StandardFonts.append(Font('Symbol', 'roman', 2, 2, '05050102010706020507'))
StandardFonts.append(Font('Tahoma', 'swiss', 0, 2, '020b0604030504040204'))
StandardFonts.append(Font('Times New Roman', 'roman', 0, 2, '02020603050405020304'))
StandardFonts.append(Font('Trebuchet MS', 'swiss', 0, 2, '020b0603020202020204'))
StandardFonts.append(Font('Verdana', 'swiss', 0, 2, '020b0604030504040204'))

StandardFonts.Castellar.SetAlternate(StandardFonts.Georgia)

"""
Found the following definition at http://www.pbdr.com/vbtips/gen/convtwip.htm

Twips are screen-independent units used to ensure that the placement and
proportion of screen elements in your screen application are the same on all
display systems. A twip is a unit of screen measurement equal to 1/20 of a
printer's point. The conversion between twips and
inches/centimeters/millimeters is as follows:

There are approximately 1440 twips to a inch (the length of a screen item
measuring one inch when printed).

As there are 2.54 centimeters to 1 inch, then there are approximately 567
twips to a centimeter (the length of a screen item measuring one centimeter
when printed).

Or in millimeters, as there are 25.4 millimeters to 1 inch, therefore there
are approximately 56.7 twips to a millimeter (the length of a screen item
measuring one millimeter when printed)."""

# Width default is 12240, Height default is 15840
StandardPaper = Papers()
StandardPaper.append(Paper('LETTER', 1, 'Letter 8 1/2 x 11 in', 12240, 15840))
StandardPaper.append(Paper('LETTERSMALL', 2, 'Letter Small 8 1/2 x 11 in', 12240, 15840))
StandardPaper.append(Paper('TABLOID', 3, 'Tabloid 11 x 17 in', 15840, 24480))
StandardPaper.append(Paper('LEDGER', 4, 'Ledger 17 x 11 in', 24480, 15840))
StandardPaper.append(Paper('LEGAL', 5, 'Legal 8 1/2 x 14 in', 12240, 20160))
StandardPaper.append(Paper('STATEMENT', 6, 'Statement 5 1/2 x 8 1/2 in', 7920, 12240))
StandardPaper.append(Paper('EXECUTIVE', 7, 'Executive 7 1/4 x 10 1/2 in', 10440, 15120))
StandardPaper.append(Paper('A3', 8, 'A3 297 x 420 mm', 16838, 23811))
StandardPaper.append(Paper('A4', 9, 'A4 210 x 297 mm', 11907, 16838))
StandardPaper.append(Paper('A4SMALL', 10, 'A4 Small 210 x 297 mm', 11907, 16838))
StandardPaper.append(Paper('A5', 11, 'A5 148 x 210 mm', 8391, 11907))
StandardPaper.append(Paper('B4', 12, 'B4 (JIS)250 x 354', 14175, 20072))
StandardPaper.append(Paper('B5', 13, 'B5 (JIS)182 x 257 mm', 10319, 14572))
StandardPaper.append(Paper('FOLIO', 14, 'Folio 8 1/2 x 13 in', 12240, 18720))
StandardPaper.append(Paper('QUARTO', 15, 'Quarto 215 x 275 mm', 12191, 15593))
StandardPaper.append(Paper('10X14', 16, '10x14 in', 14400, 20160))
StandardPaper.append(Paper('11X17', 17, '11x17 in', 15840, 24480))
StandardPaper.append(Paper('NOTE', 18, 'Note 8 1/2 x 11 in', 12240, 15840))
StandardPaper.append(Paper('ENV_9', 19, 'Envelope #9 3 7/8 x 8 7/8', 5580, 12780))
StandardPaper.append(Paper('ENV_10', 20, 'Envelope #10 4 1/8 x 9 1/2', 5940, 13680))
StandardPaper.append(Paper('ENV_11', 21, 'Envelope #11 4 1/2 x 10 3/8', 6480, 14940))
StandardPaper.append(Paper('ENV_12', 22, 'Envelope #12 4 3/4 x 11', 6840, 15840))
StandardPaper.append(Paper('ENV_14', 23, 'Envelope #14 5 x 11 1/2', 7200, 16560))
StandardPaper.append(Paper('CSHEET', 24, 'C size sheet 18 x 24 in', 29520, 34560))
StandardPaper.append(Paper('DSHEET', 25, 'D size sheet 22 x 34 in', 31680, 48960))
StandardPaper.append(Paper('ESHEET', 26, 'E size sheet 34 x 44 in', 48960, 63360))
StandardPaper.append(Paper('ENV_DL', 27, 'Envelope DL 110 x 220mm', 6237, 12474))
StandardPaper.append(Paper('ENV_C5', 28, 'Envelope C5 162 x 229 mm', 9185, 12984))
StandardPaper.append(Paper('ENV_C3', 29, 'Envelope C3  324 x 458 mm', 18371, 25969))
StandardPaper.append(Paper('ENV_C4', 30, 'Envelope C4  229 x 324 mm', 12984, 18371))
StandardPaper.append(Paper('ENV_C6', 31, 'Envelope C6  114 x 162 mm', 6464, 9185))
StandardPaper.append(Paper('ENV_C65', 32, 'Envelope C65 114 x 229 mm', 6464, 12984))
StandardPaper.append(Paper('ENV_B4', 33, 'Envelope B4  250 x 353 mm', 14175, 20015))
StandardPaper.append(Paper('ENV_B5', 34, 'Envelope B5  176 x 250 mm', 9979, 14175))
StandardPaper.append(Paper('ENV_B6', 35, 'Envelope B6  176 x 125 mm', 9979, 7088))
StandardPaper.append(Paper('ENV_ITALY', 36, 'Envelope 110 x 230 mm', 6237, 13041))
StandardPaper.append(Paper('ENV_MONARCH', 37, 'Envelope Monarch 3.875 x 7.5 in', 5580, 10800))
StandardPaper.append(Paper('ENV_PERSONAL', 38, '6 3/4 Envelope 3 5/8 x 6 1/2 in', 5220, 9360))
StandardPaper.append(Paper('FANFOLD_US', 39, 'US Std Fanfold 14 7/8 x 11 in', 21420, 15840))
StandardPaper.append(Paper('FANFOLD_STD_GERMAN', 40, 'German Std Fanfold 8 1/2 x 12 in', 12240, 17280))
StandardPaper.append(Paper('FANFOLD_LGL_GERMAN', 41, 'German Legal Fanfold 8 1/2 x 13 in', 12240, 18720))

