from binascii import hexlify
from six import text_type, PY2

from docassemble.base.rtfng.document.base import RawCode


def _get_jpg_dimensions( fin ):
    """
    converted from: http://dev.w3.org/cvsweb/Amaya/libjpeg/rdjpgcom.c?rev=1.2
    """

    M_SOF0   = chr( 0xC0 )    #    /* Start Of Frame N */
    M_SOF1   = chr( 0xC1 )    #    /* N indicates which compression process */
    M_SOF2   = chr( 0xC2 )    #    /* Only SOF0-SOF2 are now in common use */
    M_SOF3   = chr( 0xC3 )    #
    M_SOF5   = chr( 0xC5 )    #    /* NB: codes C4 and CC are NOT SOF markers */
    M_SOF6   = chr( 0xC6 )    #
    M_SOF7   = chr( 0xC7 )    #
    M_SOF9   = chr( 0xC9 )    #
    M_SOF10  = chr( 0xCA )    #
    M_SOF11  = chr( 0xCB )    #
    M_SOF13  = chr( 0xCD )    #
    M_SOF14  = chr( 0xCE )    #
    M_SOF15  = chr( 0xCF )    #
    M_SOI    = chr( 0xD8 )    #    /* Start Of Image (beginning of datastream) */
    M_EOI    = chr( 0xD9 )  #    /* End Of Image (end of datastream) */

    M_FF = chr( 0xFF )

    MARKERS = [ M_SOF0, M_SOF1,  M_SOF2,  M_SOF3,
                M_SOF5, M_SOF6,  M_SOF7,  M_SOF9,
                M_SOF10,M_SOF11, M_SOF13, M_SOF14,
                M_SOF15 ]

    def get_length() :
        b1 = fin.read( 1 )
        b2 = fin.read( 1 )
        return (ord(b1) << 8) + ord(b2)

    def next_marker() :
        #  markers come straight after an 0xFF so skip everything
        #  up to the first 0xFF that we find
        while fin.read(1) != M_FF :
            pass

        #  there can be more than one 0xFF as they can be used
        #  for padding so we are now looking for the first byte
        #  that isn't an 0xFF, this will be the marker
        while True :
            result = fin.read(1)
            if result != M_FF :
                return result

        raise Exception( 'Invalid JPEG' )

    #  BODY OF THE FUNCTION
    if not ((fin.read(1) == M_FF) and (fin.read(1) == M_SOI)) :
        raise Exception( 'Invalid Jpeg' )

    while True :
        marker = next_marker()

        #  the marker is always followed by two bytes representing the length of the data field
        length = get_length ()
        if length < 2 : raise Exception( "Erroneous JPEG marker length" )

        #  if it is a compression process marker then it will contain the dimension of the image
        if marker in MARKERS :
            #  the next byte is the data precision, just skip it
            fin.read(1)

            #  bingo
            image_height = get_length()
            image_width  = get_length()
            return image_width, image_height

        #  just skip whatever data it contains
        fin.read( length - 2 )

    raise Exception( 'Invalid JPEG, end of stream reached' )

_PNG_HEADER = b'\x89\x50\x4e'
    
def _get_png_dimensions( data ) :
    import sys
    if data[0:3] != _PNG_HEADER :
        raise Exception( 'Invalid PNG image' )
    if PY2:
        width  = (ord(data[18]) * 256) + (ord(data[19]))
        height = (ord(data[22]) * 256) + (ord(data[23]))
    else:
        width  = (data[18] * 256) + (data[19])
        height = (data[22] * 256) + (data[23])
    return width, height


class Image( RawCode ) :

    #  Need to add in the width and height in twips as it crashes
    #  word xp with these values.  Still working out the most
    #  efficient way of getting these values.
    # \picscalex100\picscaley100\piccropl0\piccropr0\piccropt0\piccropb0
    # picwgoal900\pichgoal281

    PNG_LIB = 'pngblip'
    JPG_LIB = 'jpegblip'
    PICT_TYPES = { 'png' : PNG_LIB,
                   'jpg' : JPG_LIB }

    def __init__( self, file_name, **kwargs ) :
        import sys
        fin = open( file_name, 'rb' )

        pict_type = self.PICT_TYPES[ file_name[ -3 : ].lower() ]
        if pict_type == self.PNG_LIB :
            width, height = _get_png_dimensions( fin.read( 100 ) )
        else :
            width, height = _get_jpg_dimensions( fin )

        codes = [ pict_type,
                  'picwgoal%s' % (width  * 20),
                  'pichgoal%s' % (height * 20) ]
        for kwarg, code, default in [ ( 'scale_x',     'scalex', '100' ),
                                      ( 'scale_y',     'scaley', '100' ),
                                      ( 'crop_left',   'cropl',    '0' ),
                                      ( 'crop_right',  'cropr',    '0' ),
                                      ( 'crop_top',    'cropt',    '0' ),
                                      ( 'crop_bottom', 'cropb',    '0' ) ] :
            codes.append( 'pic%s%s' % ( code, kwargs.pop( kwarg, default ) ) )


        #  reset back to the start of the file to get all of it and now
        #  turn it into hex.
        fin.seek( 0, 0 )
        data = []
        image = hexlify( fin.read() )
        for i in range( 0, len( image ), 128 ) :
            data.append( image[ i : i + 128 ] )
        data = r'{\pict{\%s}%s}' % ( '\\'.join( codes ), '\n'.join( x.decode() for x in data ) )
        RawCode.__init__( self, data )

    def ToRawCode( self, var_name ) :
        return '%s = RawCode( """%s""" )' % ( var_name, self.Data )

