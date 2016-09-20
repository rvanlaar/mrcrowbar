import os, re
from collections import OrderedDict

class Loader( object ):
    _SEP = re.escape( os.path.sep )

    def __init__( self, file_class_map, case_sensitive=False ):
        self.file_class_map = file_class_map
        self.re_flags = re.IGNORECASE if not case_sensitive else 0
        self.file_re_map = { key: re.compile( key, flags=self.re_flags ) for key, klass in file_class_map.items() if klass } 
        self._files = OrderedDict()

    def load( self, target_path, verbose=False ):
        #target_path = os.path.abspath( target_path )
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