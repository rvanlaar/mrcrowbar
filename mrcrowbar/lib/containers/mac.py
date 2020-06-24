"""
    Macintosh resource fileformat is described here:
    https://github.com/kreativekorp/ksfl/wiki/Macintosh-Resource-File-Format
"""

from mrcrowbar import models as mrc

class MacBinary( mrc.Block ):
    version_old =   mrc.Const( mrc.UInt8( 0x00 ), 0 )
    name_size =     mrc.UInt8( 0x01, range=range( 1, 64 ) )
    name =          mrc.Bytes( 0x02, length=mrc.Ref( 'name_size' ) )
    type =          mrc.Bytes( 0x41, length=4 )
    creator =       mrc.Bytes( 0x45, length=4 )
    locked =        mrc.Bits( 0x49, 0b10000000 )
    invisible =     mrc.Bits( 0x49, 0b01000000 )
    bundle =        mrc.Bits( 0x49, 0b00100000 )
    system =        mrc.Bits( 0x49, 0b00010000 )
    bozo =          mrc.Bits( 0x49, 0b00001000 )
    busy =          mrc.Bits( 0x49, 0b00000100 )
    changed =       mrc.Bits( 0x49, 0b00000010 )
    inited =        mrc.Bits( 0x49, 0b00000001 )
    const1 =        mrc.Const( mrc.UInt8( 0x4a ), 0 )
    pos_y =         mrc.UInt16_BE( 0x4b )
    pos_x =         mrc.UInt16_BE( 0x4d )
    folder_id =     mrc.UInt16_BE( 0x4f )
    protected =     mrc.Bits( 0x51, 0b00000001 )
    const2 =        mrc.Const( mrc.UInt8( 0x52 ), 0 )
    data_size =     mrc.UInt32_BE( 0x53 )
    resource_size = mrc.UInt32_BE( 0x57 )
    created =       mrc.UInt32_BE( 0x5a )
    modified =      mrc.UInt32_BE( 0x5e )


    data =          mrc.Bytes( 0x80, length=mrc.Ref( 'data_size' ) )
    resource =      mrc.Bytes( mrc.EndOffset( 'data', align=0x80 ), length=mrc.Ref( 'resource_size' ) )

class ResourceData( mrc.Block ):
    """
    Read the Resource Data.

    Currently only reads the first element, instead of them all.
    """
    length =                mrc.UInt32_BE(0x00)
    data =                  mrc.Bytes(offset=0x04, length=mrc.Ref("length"))

class ResourceType( mrc.Block):
    type =                  mrc.UInt32_BE(0x00)
    resourceCount =         mrc.UInt16_BE(0x04)
    resourceListOffset =    mrc.UInt16_BE(0x02)

class MapData( mrc.Block ):
    """
    Read the Resource Map Data.

    Only the header is implemented.
    """
    resourceDataOffset =    mrc.UInt32_BE(0x00)
    resourceMapOffset =     mrc.UInt32_BE(0x04)
    resourceDataSize =      mrc.UInt32_BE(0x08)
    resourceMapSize =       mrc.UInt32_BE(0x0c)

    nextResourceMap =       mrc.UInt32_BE(0x10)
    fileRef =               mrc.UInt16_BE(0x14)
    attributes =            mrc.UInt16_BE(0x16)

    typeListOffset =        mrc.UInt16_BE(0x18)
    nameListOffset =        mrc.UInt16_BE(0x1a)
    typeCount =             mrc.UInt16_BE(0x1c)

    def get_count(self):
        """The type count is off by -1."""
        return self.typeCount + 1

class ResourceFork( mrc.Block ):
    """
    """
    resourceDataOffset =    mrc.UInt32_BE(0x00)
    resourceMapOffset =     mrc.UInt32_BE(0x04)
    resourceDataSize =      mrc.UInt32_BE(0x08)
    resourceMapSize =       mrc.UInt32_BE(0x0c)
    resourceData =          mrc.BlockField(
                                    ResourceData,
                                    offset=mrc.Ref("resourceDataOffset"),
                                    length=mrc.Ref("resourceDataSize" )
                            )
    resourceMap =           mrc.BlockField(
                                    MapData,
                                    offset=mrc.Ref("resourceMapOffset"),
                                    length=mrc.Ref("resourceMapSize")
                            )