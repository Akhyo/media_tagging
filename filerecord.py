import sys
import os.path
import hashlib

prefered_block_size = 4096
media_types = {}


class Section:
    pass

class Container:
    pass

class FileRecord:

    hash_values={}
    
    def add_section(self):
        pass
    #TODO

    def accesible(self):
        return os.path.exists(self.canon_path) and os.path.isfile(self.canon_path)

    def update_size(self):
        if self.accesible():
            self.file_size = os.path.getsize(self.canon_path)

    def update_file_hash(self, hash_type):
        if self.accesible():
            if hash_type not in hashlib.algorithms_guaranteed:
                raise ValueError('Hash currently not supported.')
                return
            else:
                hash_obj = hashlib.new(hash_type)
                with open(self.canon_path,'rb') as f: 
                    while True:
                        data = f.read(prefered_block_size)
                        if not data:
                            break
                        hash_obj.update(data)
                    self.hash_values[hash_type] = hash_obj.digest()
        else:
            pass
        #TODO

    def recalculate_all(self):
        if self.accesible():
            self.update_size
        #TODO

    def __init__(self, pathname, hash_type=''):
        if os.path.exists(pathname) and os.path.isfile(pathname):
            self.canon_path  = os.path.realpath(pathname)
            self.file_name = os.path.basename(self.canon_path)
            self.file_size = os.path.getsize(self.canon_path)
            if hash_type:
                self.update_file_hash(hash_type)
        else:
            raise ValueError('Not a file.')

    def __repr__(self):
        return "<Filerecord('%s','%s','%s'): %s>" % (self.file_name, 
                                                     self.canon_path, 
                                                     self.file_size, 
                                                     self.tag_entries)
   
