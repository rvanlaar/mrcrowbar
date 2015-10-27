#!/usr/bin/python3

from mrcrowbar import models as mrc
from mrcrowbar import utils

from PIL import Image

import array
import itertools


class Colour( mrc.Block ):
    _block_size = 0
    r_8 = 0
    g_8 = 0
    b_8 = 0
    a_8 = 255

    @property
    def r( self ):
        return self.r_8/255

    @property
    def g( self ):
        return self.g_8/255

    @property
    def b( self ):
        return self.b_8/255

    @property
    def a( self ):
        return self.a_8/255

    def __str__( self ):
        return '#{:02X}{:02X}{:02X}{:02X}'.format( self.r_8, self.g_8, self.b_8, self.a_8 )

    def __eq__( self, other ):
        return (self.r_8 == other.r_8) and (self.g_8 == other.g_8) and (self.b_8 == other.b_8) and (self.a_8 == other.a_8)

class Transparent( Colour ):
    a_8 = 0


class RGBColour( Colour ):
    _block_size = 3

    r_8 = mrc.UInt8( 0x00 )
    g_8 = mrc.UInt8( 0x01 )
    b_8 = mrc.UInt8( 0x02 )


class RawIndexedImage( mrc.Block ):
    _width =            0
    _height =           0
    _palette =          []

    data = mrc.Bytes( 0x0000 )

    def __init__( self, buffer, width=0, height=0, palette=None, **kwargs ):
        self._width = width
        self._height = height
        if palette is not None:
            self._palette = palette
        #assert len( buffer ) == width*height
        super( RawIndexedImage, self ).__init__( buffer, **kwargs )

    def get_image( self ):
        im = Image.new( 'P', (self._width, self._height) )
        im.putdata( self.data[:self._width*self._height] )
        im.putpalette( itertools.chain( *[(c.r_8, c.g_8, c.b_8) for c in self._palette] ) )
        return im

    def ansi_format( self ):
        result = []
        for y in range( 0, self._height, 2 ):
            for x in range( 0, self._width ):
                p1 = self._palette[self.data[self._width*y + x]]
                p2 = self._palette[self.data[self._width*(y+1) + x]] if (self._width*(y+1) + x) < len( self.data ) else Transparent()
                if p1.a_8 == 0 and p2.a_8 == 0:
                    result.append( u'\x1b[0m ' )
                elif p1 == p2:
                    result.append( u'\x1b[38;2;{};{};{}m█'.format( p1.r_8, p1.g_8, p1.b_8 ) )
                elif p1.a_8 == 0 and p2.a_8 != 0:
                    result.append( u'\x1b[38;2;{};{};{}m▄'.format( p2.r_8, p2.g_8, p2.b_8 ) )
                elif p1.a_8 != 0 and p2.a_8 == 0:
                    result.append( u'\x1b[38;2;{};{};{}m▀'.format( p1.r_8, p1.g_8, p1.b_8 ) )
                else:
                    result.append( u'\x1b[38;2;{};{};{};48;2;{};{};{}m▀\x1b[0m'.format( p1.r_8, p1.g_8, p1.b_8, p2.r_8, p2.g_8, p2.b_8 ) )

            result.append( u'\x1b[0m\n' )
        return u''.join( result )
    
    def print( self ):
        print( self.ansi_format() )

    def __str__( self ):
        return self.ansi_format()

    def __repr__( self ):
        return '<{}: {} bytes, {}x{}>'.format( self.__class__.__name__, len( self.data ), self._width, self._height )
    
class Planarizer( mrc.Transform ):
    def __init__( self, width, height, bpp, frame_offset=0, frame_stride=0, frame_count=1 ):
        self.width = width
        self.height = height
        self.bpp = bpp
        self.frame_offset = frame_offset
        self.frame_stride = frame_stride
        self.frame_count = frame_count

    def export_data( self, buffer ):
        assert type( buffer ) == bytes

        

    def import_data( self, buffer ):
        assert type( buffer ) == bytes
        raw_image = array.array( 'B', b'\x00'*self.width*self.height*self.frame_count )

        for f in range( self.frame_count ):
            stream = utils.BitReader( buffer, self.frame_offset+f*self.frame_stride, bits_reverse=True )
            for b in range( self.bpp ):
                for i in range( self.width*self.height ):
                    raw_image[f*self.width*self.height + i] += stream.get_bits( 1 ) << b
    
        if self.frame_count > 1:
            end_offset = self.frame_offset + self.frame_count*self.frame_stride
        else:
            bits = self.width*self.height*self.bpp
            end_offset = self.frame_offset + (bits)//8 + (1 if (bits % 8) else 0)

        result = {
            'payload': bytes( raw_image ),
            'end_offset': end_offset
        }

        return result

