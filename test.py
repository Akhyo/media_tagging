#!/usr/bin/env python3
import filerecord
import magic

python_cli=filerecord.CommandLine(['echo', '*test*','*test*'], 2)
print(python_cli.generate('./test.py', None))

python_filetype=magic.from_file(b'test.py',mime=True).decode('utf-8')
print(python_filetype)

python_container = filerecord.Container(python_filetype, 'default', 
                                        python_cli)
python_container.ext_open('test.py', None)

fr = filerecord.FileRecord('./test.py', 'md5')
fr.global_section.open_element(fr.global_section.get_start())
