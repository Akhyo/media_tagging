#!/usr/bin/env python3
import sys
import os
import os.path
import hashlib
import magic
import subprocess

prefered_block_size = 4096
containers = {}
#all_tags{category:{section object}}
all_tags={}
filerecords=set()

all_data=(filerecords, all_tags, containers)

class Section:
    def get_start(self):
        return self.elemlist[0]

    def get_end(self):
        return self.elemlist[-1]

    def is_in_section(self, element):
        return element in self.elemlist

    def copy_elements(self):
        return self.elemlist[:]

    def open_element(self, element):
        if self.is_in_section(element):
            self.filerecord.container.ext_open(self.filerecord.canon_path, 
                                               element)
        else:
            raise ValueError('Element not found in section')

    def open_offset(self, offset=0):
        #should check for array length here?
        self.filerecord.container.ext_open(self.filerecord.canon_path, 
                                           self.elemlist[offset])

    def add_tag(self, category, value=None):
        #if implemented tag class, it will be searched by category
        self.tag_vals[category]=value
        if category not in all_tags:
            all_tags[category] = set([self]) 
        else:
            all_tags[category].add(self)

    def remove_tag(self, category):
        if category in self.tag_vals:
            del self.tag_vals[category]
            all_tags[category].remove(self)
        else:
            pass
        #raise error

    def add_subsection(self, subsection):
        self.subsections[subsection.name] = subsection

    def overlaps(self, other_section):
        if self is other_section:
            raise ValueError('Comparing with same section')
        else:
            return False

    def __init__(self, filerecord, name = None, parent = None, elemlist = [None]):
        self.filerecord = filerecord
        self.parent = parent
        self.tag_vals={}
        self.subsections={} 
        if self.parent:
            self.elemlist = elemlist
            if name and name not in parent.subsection.keys:
                self.name = name
            elif name in parent.subsections.keys():
                raise ValueError('Section of that name already exists')
            else:
                for i in range(len(parent.subsections)-1, 999):
                    name = 'subsection{0}'.format(i)
                    if name not in parent.subsections.keys():
                        self.name = name
                        break
                else:
                    raise ValueError('Section out of arbitrary range')
            self.parent.add_subsection(self)
        else:
            self.elemlist = self.filerecord.container.generate_elements(self.filerecord)
            self.name = "global"
            self.subsections[self.name]=self


class CommandLine:
    def generate(self, namepath, element):
        outlist=self.arguments[:]
        outlist.insert(self.filepos, namepath)
        if self.elempos:
            outlist.insert(self.elempos, element)
            #add warning when there is no elempos but there is element 
            #and error for vice-versa
        return outlist

    def __init__(self, arguments, filepos, elempos = None, ):
        self.arguments=arguments
        self.filepos=filepos
        self.elempos=elempos


class ElementGenerator:
    def get_elements(filename):
        return [None]

class Container:

    def generate_elements(self, filerecord):
        return self.elem_gen.get_elements(filerecord.canon_path)

    def ext_open(self, namepath, element):
        subprocess.Popen(self.cli.generate(namepath, element))

    def __init__(self, file_type, media_type, cli, section_class=Section,
                 elem_gen = ElementGenerator ):
        self.section_class = section_class
        self.cli = cli
        self.elem_gen = elem_gen
        containers[(file_type, media_type)] = self


class FileRecord:

    hash_values={}
    container = None
    
    def add_section(self, name = None, elem_list = [None]):
         self.container.section_class(self, name, self.global_section, elem_list)

    def accesible(self):
        return os.access(self.canon_path, os.R_OK) and os.path.isfile(self.canon_path)

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
            for hash_type in hash_values:
                self.update_file_hash(hash_type)

    def assign_container(self, overwrite = False):
        if overwrite or self.container == None:
            if (self.file_type, self.media_type) in containers:
                self.container = containers[(self.file_type, self.media_type)]
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
            self.file_type = magic.from_file(self.canon_path,
                                             mime=True).decode('utf-8')
            self.assign_container()
            self.global_section = self.container.section_class(self)
            filerecords.add(self)
        else:
            raise ValueError('Not a file.')

    def __repr__(self):
        return "<Filerecord({0},{1},{2}): TODO >".format(self.file_name, 
                                                     self.canon_path, 
                                                     self.file_size, 
                                                     )


def gen_sections_with_tag(category, value_comparator=lambda value: True ):
    section_comparator=lambda section:value_comparator(section.tag_vals[category])
    for out_section in filter(all_tags[category], section_comparator):
            yield out_section

def gen_files_with_tag(category, value_comparator=lambda value: True ):
    for out_section in gen_sections_with_tag(category, value_comparator):
        yield out_section.filerecord.canon_path

