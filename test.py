#!/usr/bin/env python3
import filerecord
import magic
import pickle

python_cli=filerecord.CommandLine(['echo', '*test*','*test*'], 2)
print(python_cli.generate('./test.py', None))

python_filetype=magic.from_file('test.py',mime=True).decode('utf-8')
print(python_filetype)

python_container = filerecord.Container(python_filetype, 'default', 
                                        python_cli)
python_container.ext_open('test.py', None)

fr = filerecord.FileRecord('./test.py', 'md5')
fr.global_section.open_element(fr.global_section.get_start())
fr.global_section.add_tag('global tag')

fr.add_section()
fr.add_section()
count=0
for section in filter(lambda section : None in section.elemlist, fr.global_section.subsections.values() ) :
    section.add_tag('localtag{0}'.format(count))
    count+=1

for tag in filerecord.all_tags:
    for section in filerecord.all_tags[tag]:
        print('{tag}:{value}:{section}'.format(tag=tag, section=section.name,
             value=section.tag_vals[tag]))
dumpfile = open('filedata.test','wb') 
pickle.dump(filerecord.all_data, dumpfile)
