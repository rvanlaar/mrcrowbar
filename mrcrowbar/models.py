from six import add_metaclass, iteritems, iterkeys

import os, re

from mrcrowbar.collections import OrderedDict

from mrcrowbar.fields import *


class Magic:
    pass


class Store:
    pass


# how do we define a block?

# - we want to be able to scan through a stream of bollocks and identify a magic number
# - scanning will provide a start offset (in other words, a list sliced to the beginning)
# - further pounding 


# borrowed from schematic

class FieldDescriptor( object ):

    """
    The FieldDescriptor serves as a wrapper for Types that converts them into
    fields.

    A field is then the merger of a Type and it's Model.
    """

    def __init__( self, name ):
        """
        :param name:
            The field's name
        """
        self.name = name

    def __get__( self, instance, cls ):
        """
        Checks the field name against the definition of the model and returns
        the corresponding data for valid fields or raises the appropriate error
        for fields missing from a class.
        """
        try:
            if instance is None:
                return cls._fields[self.name]
            return instance._field_data[self.name]
        except KeyError:
            raise AttributeError( self.name )

    def __set__( self, instance, value ):
        """
        Checks the field name against a model and sets the value.
        """
        #from .types.compound import ModelType
        #field = instance._fields[self.name]
        #if not isinstance( value, Model ) and isinstance( field, ModelType ):
        #    value = field.model_class( value )
        if instance is None:
            return
        instance._field_data[self.name] = value
        return

    def __delete__( self, instance ):
        """
        Checks the field name against a model and deletes the field.
        """
        if self.name not in instance._fields:
            raise AttributeError( "{} has no attribute {}".format( 
                                    type( instance ).__name__, self.name ) )
        del instance._fields[self.name]


class RefDescriptor( object ):    
    def __init__( self, name ):
        self.name = name

    def __get__( self, instance, cls ):
        try:
            if instance is None:
                return cls._refs[self.name]
            # FIXME: don't cache until we evaluate if the performance suffers
            if True: #self.name not in instance._ref_cache:
                instance._ref_cache[self.name] = instance._refs[self.name].get( instance )
            return instance._ref_cache[self.name]
        except KeyError:
            raise AttributeError( self.name )
    
    def __set__( self, instance, value ):
        if instance is None:
            return
        instance._refs[self.name].set( instance, value )
        return

    def __delete__( self, instance ):
        raise AttributeError( "can't delete Ref" )


class ModelMeta( type ):

    """
    Meta class for Models.
    """

    def __new__( mcs, name, bases, attrs ):
        """
        This metaclass adds four attributes to host classes: mcs._fields,
        mcs._serializables, mcs._validator_functions, and mcs._options.

        This function creates those attributes like this:

        ``mcs._fields`` is list of fields that are schematics types
        ``mcs._serializables`` is a list of functions that are used to generate
        values during serialization
        ``mcs._validator_functions`` are class level validation functions
        ``mcs._options`` is the end result of parsing the ``Options`` class
        """

        # Structures used to accumulate meta info
        fields = OrderedDict()
        refs = OrderedDict()

        serializables = {}
        #validator_functions = {}  # Model level

        # Parse this class's attributes into meta structures
        for key, value in iteritems( attrs ):
            if isinstance( value, Field ):
                fields[key] = value
            elif isinstance( value, Ref ):
                refs[key] = value
        #    elif isinstance( value, View ):
        #        views[key] = value

        # Convert list of types into fields for new klass
        fields.sort( key=lambda i: i[1]._position_hint )
        for key, field in iteritems( fields ):
            attrs[key] = FieldDescriptor( key )
        for key, ref in iteritems( refs ):
            attrs[key] = RefDescriptor( key )

        # Ready meta data to be klass attributes
        attrs['_fields'] = fields
        attrs['_refs'] = refs

        klass = type.__new__( mcs, name, bases, attrs )

        # Add reference to klass to each field instance
        #def set_owner_model( field, klass ):
        #    field.owner_model = klass
        #    if hasattr( field, 'field' ):
        #        set_owner_model( field.field, klass )

        for field_name, field in fields.items():
        #    set_owner_model(field, klass)
            field._name = field_name

        # Register class on ancestor models
        #klass._subclasses = []
        #for base in klass.__mro__[1:]:
        #    if isinstance(base, ModelMeta):
        #        base._subclasses.append(klass)

        return klass

    @property
    def fields( cls ):
        return cls._fields

    @property
    def refs( cls ):
        return cls._refs


@add_metaclass( ModelMeta )
class Block( object ):
    _magic = Magic()
    _block_size = 0
    _parent = None

    def __init__( self, raw_buffer=None ):
        self._field_data = {}
        self._ref_cache = {}
        
        # start the initial load of data
        self.import_data( raw_buffer )
        

    def __repr__( self ):
        return '<{}: {}>'.format( self.__class__.__name__, str( self ) )

    def __str__( self ):

    def import_data( self, raw_buffer, **kw ):
        klass = self.__class__
        if raw_buffer:
            assert type( raw_buffer ) == bytes
            assert len( raw_buffer ) >= klass._block_size
        
        self._field_data = {}

        for name in klass._fields:
            if raw_buffer:
                self._field_data[name] = klass._fields[name].get_from_buffer( raw_buffer, parent=self )
            else:
                self._field_data[name] = klass._fields[name].default
        return

    def export_data( self, **kw ):
        klass = self.__class__

        output = bytearray( b'\x00'*klass._block_size )

        for name in klass._fields:
            klass._fields[name].update_buffer_with_value( self._field_data[name], output, parent=self )
        return output

    def size( self ):
        return self._block_size

    def validate( self, **kw ):
        klass = self.__class__
        for name in klass._fields:
            klass._fields[name].validate( self._field_data[name], parent=self )
        return


class Check( object ):
    def __init__( self, instance, value ):
        pass


class Transform( object ):
    def export_data( self, buffer ):
        return None
    
    def import_data( self, buffer ):
        return {
            'payload': b'',
            'end_offset': 0
        }


# screw whatever it was I was saying before about foreign properties
# first, we should have views
# - views should have references 1 level deep, i.e. properties on the parent object
# - they can, however, refer to foreign properties

# on Block creation time, first there's a process which wires up the fields to data
# from the object (including injection). then, there's a process which injects the 
# parent object into each of the foreignprop/views 

# foreignprops would be evaluated once at runtime, this value would be cached.
# these properties would be safeguarded against set operations.




class LookupTable( Store ):
    def __init__( self, offset, length=None, fill=b'\x00', **kwargs ):
        super( LookupTable, self ).__init__( **kwargs )
        self.offset = offset
        self.length = length
        self.fill = fill
        self.length = length

    def import_data( self, buffer ):
        pass

    def export_data( self ):
        return b''
    
    
class Loader( object ):
    def __init__( self, file_class_map, case_sensitive=False ):
        self.file_class_map = file_class_map
        self.re_flags = re.IGNORECASE if not case_sensitive else 0
        self.file_re_map = { key: re.compile( key, flags=self.re_flags ) for key, klass in file_class_map.items() if klass } 
        self._files = {}

    def load( self, target_path, verbose=False ):
        target_path = os.path.abspath( target_path )
        for root, subFolders, files in os.walk( target_path ):
            for f in files:
                full_path = os.path.join( root, f )

                for key, regex in self.file_re_map.items():
                    match = regex.search( full_path )
                    if match:
                        data = open( full_path, 'rb' ).read()
                        if verbose:
                            print( '{} => {}'.format( full_path, self.file_class_map[key] ) )
                        self._files[full_path] = {
                            'klass': self.file_class_map[key],
                            'match': match.groups(),
                            'obj': self.file_class_map[key]( data )
                        }

        self.post_load( verbose )
        return

    def post_load( self, verbose=False ):
        pass
        

    def keys( self ):
        return self._files.keys()

    def __len__( self ):
        return len( self._files )

    def __getitem__( self, key ):
        return self._files[key]['obj']

    def __contains__( self, key ):
        return key in self._files
