#!/usr/bin/env python3
import sys
import os.path
import hashlib
import magic
import subprocess

prefered_block_size = 4096
containers = {}


class Section:
    def get_start(self):
        return self.elemlist[0]

    def get_end(self):
        return self.elemlist[-1]

    def is_in_section(self, element):
        return element in self.elemlist

    def get_elements(self):
        return self.elemlist[:]

    def open_element(self, element):
        if is_in_section(element):
            container.ext_open(filerecord.canonpath, element)
        else:
            raise ValueError('Element not found in section')


    def open_offset(self, offset=0):
        #should check for array length here?
        container.ext_open(filerecord.canonpath, self.elemlist[offset])

    def overlaps(self, other_section):
        if self is other_section:
            raise ValueError('Comparing with same section')
        else:
            return False

    def __init__(self, filerecord, container, parent = None, elemlist = [None]):
        self.filerecord = filerecord
        self.container = container
        self.parent = parent
        if self.parent:
            self.elemlist = elemlist
        else:
            self.elemlist = Container.generate_elements(filerecord)

class CommandLine:
    def generate(self, namepath, element):
        outlist=self.arguments[:]
        outlist.insert(self.filepos, namepath)
        if self.elempos:
            outlist.insert(self.elempos, element)
            #add warning when there is no elempos but there is element 
            #and error for vice-versa
        return outlist

    def __init__(self, arguments, filepos, elempos = None):
        self.arguments=arguments
        self.filepos=filepos
        self.elempos=elempos
       

class Container:

    def generate_elements(self, filerecord, sections_class):
        if section_class in self.elem_methods:
            return self.elem_methods[section_class](filerecord)
        else:
            raise ValueError("Section not allowed for this container")

    def ext_open(self, namepath, element):
        subprocess.Popen(self.cli.generate(namepath, element))

    def __init__(self, section_class, file_type, media_type, cli, 
                 elem_methods = { Section : lambda filename: [None] } ):
        self.section_class = section_class
        self.cli = cli
        self.elem_methods = elem_methods
        containers[(file_type, media_type)] = self


class FileRecord:

    hash_values={}
    container = None
    
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
            self.update_size()
        #TODO

    def assign_container(self, overwrite = False):
        if overwrite or self.container == None:
            if (file_type, media_type) in containers:
                self.container = containers[(file_type, media_type)]
            else:
                raise ValueError('Container not found for this file')
        else:
            raise ValueError('Container already defined')


    def __init__(self, pathname, hash_type='', media_type='default'):
        if os.path.exists(pathname) and os.path.isfile(pathname):
            self.canon_path  = os.path.realpath(pathname)
            self.file_name = os.path.basename(self.canon_path)
            self.file_size = os.path.getsize(self.canon_path)
            if hash_type:
                self.update_file_hash(hash_type)
            self.media_type = media_type
            self.file_type = magic.from_file(self.canonpath.encode('utf-8'),
                                             mime=True).decode('utf-8')
            assign_container()
        else:
            raise ValueError('Not a file.')

    def __repr__(self):
        return "<Filerecord('%s','%s','%s'): %s>" % (self.file_name, 
                                                     self.canon_path, 
                                                     self.file_size, 
                                                     self.tag_entries)

