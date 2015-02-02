# AvsP - an AviSynth editor
# 
# Copyright 2007 Peter Jang <http://www.avisynth.org/qwerpoi>
#           2010-2013 the AvsPmod authors <https://github.com/avspmod/avspmod>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# 
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA, or visit
#  http://www.gnu.org/copyleft/gpl.html .

# setup - AvsP py2exe setup script
# 
# Dependencies:
#     Python (tested on v2.6 and v2.7)
#     wxPython (tested on v2.8 Unicode and v2.9)
#     py2exe (tested on v0.6.9)
# Additional dependencies for x86-64:
#     cffi (tested on v0.8.1)
#     pycparser (tested on v2.10)
#     Visual Studio 2008 
#     avisynth_c.h (interface 5, or at least 3 + colorspaces from 5,
#                   tested with the header used by x264)
#
# Note: 
# py2exe v0.6.10a1 (to be exact p2exe r687+) always includes w9xpopen.exe 
# (even if excluded with 'dll_excludes')

from distutils.core import setup
import os, sys
import py2exe

import wxversion
wxversion.select('2.8')
import wx

import global_vars


x86_64 = sys.maxsize > 2**32
if x86_64:
    import avisynth_cffi
    ext_modules = [avisynth_cffi.ffi.verifier.get_extension()]
    arch = 'AMD64'
    crt_version = 'amd64_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_750b37ff97f4f68b'
else:
    ext_modules = []
    arch = 'x86'
    crt_version = 'x86_microsoft.vc90.crt_1fc8b3b9a1e18e3b_9.0.21022.8_none_bcb86ed6ac711f91'


manifest = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="{arch}"
    name="{prog}"
    type="win32"
  />
  <description>{prog}</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
            level="asInvoker"
            uiAccess="false">
        </requestedExecutionLevel>
      </requestedPrivileges>
    </security>
  </trustInfo>%(extra)s
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
            type="win32"
            name="Microsoft.VC90.CRT"
            version="9.0.21022.8"
            processorArchitecture="{arch}"
            publicKeyToken="1fc8b3b9a1e18e3b">
      </assemblyIdentity>
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="{arch}"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
  </dependency>
</assembly>
""".format(prog=global_vars.name, arch=arch)

lib_extra = []
if not x86_64:
    lib_extra.append(os.path.join(os.path.dirname(wx.__file__), 'gdiplus.dll'))

data_files = [
        ('', [
            'filterdb.dat',
            'readme.md',
            'changelog.txt',
            'copying.txt',
            ]
        ),
        ('lib', lib_extra),
        ('src', [
            'run.py',
            'avsp.py',
            'wxp.py',
            'avisynth.py',
            'avisynth_cffi.py',
            'pyavs.py',
            'pyavs_avifile.py',
            'build.py',
            'setup.py',
            'i18n.py',
            'AvsP.ico',
            'icons.py',
            'global_vars.py',
            'build_instructions_windows.txt',
        ]),
    ]

# Include the Microsoft Visual C runtime DLLs for Python 2.6+
# v9.0.21022.8, available in the Microsoft Visual C++ 2008 Redistributable Package
# 32-bit: <https://www.microsoft.com/en-us/download/details.aspx?id=29>
# 64-bit: <https://www.microsoft.com/en-us/download/details.aspx?id=15336>
crt_dst_dir = 'Microsoft.VC90.CRT'
crt_files = ('msvcm90.dll', 'msvcp90.dll', 'msvcr90.dll')
crt_dirs = (os.path.expandvars(os.path.join('%windir%', 'winsxs', crt_version)), 
            sys.prefix, os.path.join(sys.prefix, 'DLLs'))
crt_paths = []
for file in crt_files:
    for dir in crt_dirs:
        path = os.path.join(dir, file)
        if os.path.isfile(path):
            crt_paths.append(path)
            break
    else:
        crt_paths.append(file)
#data_files.append((crt_dst_dir, crt_paths)) # it doesn't seem to work
data_files.append(('', crt_paths))

# If a resource file doesn't exist in the current directory, take it from its parent
for i, (dsr, files) in enumerate(data_files):
    for j, file in enumerate(files):
        if not os.path.isfile(file):
            basename = os.path.basename(file)
            if basename != file and os.path.isfile(basename):
                data_files[i][1][j] = basename
                continue    
            file_up = os.path.join('..', basename)
            if os.path.isfile(file_up):
                data_files[i][1][j] = file_up
            else:
                exit("Couldn't find '%s'" % basename)

# Add whole directories, optionally filtering by extension and including explicitly some files
# If a directory doesn't exist within the current one, search in its parent
dirs = (
    ('help', None, None),
    ('translations', None, None), 
    ('macros', ('.py'), None), 
    ('tools', ('.py', '.presets'), ('avs2avi.exe', 'avs2avi_src.zip'))
       )
for dir, ext_filter, include in dirs:
    if not os.path.isdir(dir):
        dir_up = os.path.join('..', dir)
        if os.path.isdir(dir_up):
            dir = dir_up
        else:
            exit("Couldn't find '%s' directory" % dir)
    data_files.extend(
        [(root.split(os.sep, 1)[1] if root.startswith('..') else root, 
          [os.path.join(root, file) for file in files 
                if (not ext_filter or os.path.splitext(file)[1] in ext_filter or 
                    include and file in include)]
         ) for root, dirs, files in os.walk(dir)])

# Add also the C extension that will be generated on the same setup()
if x86_64:
    data_files.append(('', # XXX: this path shouldn't be hard-coded
        [os.path.join('build', 'lib.win-amd64-{0}.{1}'.format(*sys.version_info[:2]), 
         'avisynth_cffi_ext.pyd')]))

# Generate the dist files
packages = []
includes = ['glob', 'shutil']
excludes = ["translation", "Tkconstants", "Tkinter", "tcl", 'pyreadline', 
            'win32api', 'win32con', 'win32pipe', 'pywintypes', 'pyexpat']
dll_excludes = ['MSVCP90.dll', 'w9xpopen.exe', 'mswsock.dll', 'powrprof.dll']
if x86_64: # otherwise lextab and yacctab are generated on the working
    packages.extend(('pycparser',))  # directory on every start
else:
    excludes.extend(('avisynth_cffi',))
setup(
    name = global_vars.name,
    description = global_vars.description,
    version = global_vars.version,
    url = global_vars.url,
    license = global_vars.license,
    options = {"py2exe":{
        "compressed": True,
        "optimize": 1,
        "packages": packages,
        "includes": includes,
        "excludes": excludes,
        "dll_excludes": dll_excludes,
    }},
    zipfile = 'lib/library.zip',
    data_files = data_files,
    ext_modules= ext_modules,
    windows = [
        {  
            'copyright' : global_vars.license,
            "script": "run.py",
            "icon_resources": [(1, "AvsP.ico")],
            "other_resources" : [(24, 1, manifest)],
        }
    ],
)

# Write the manifest file for the CRT DLLs
manifest = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!-- Copyright (c) Microsoft Corporation.  All rights reserved. -->
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
    <noInheritable/>
    <assemblyIdentity
        type="win32"
        name="Microsoft.VC90.CRT"
        version="9.0.21022.8"
        processorArchitecture="{arch}"
        publicKeyToken="1fc8b3b9a1e18e3b"
    />
    <file name="msvcr90.dll" /> <file name="msvcp90.dll" /> <file name="msvcm90.dll" />
</assembly>'''.format(arch=arch)
for i, arg in enumerate(sys.argv):
    if arg.lower() == '-d':
        dist_dir = sys.argv[i+1].strip('"')
        break
    else:
        dir = arg.lower().partition('--dist-dir=')[2]
        if dir:
            dist_dir = dir.strip('"')
            break
else:
    dist_dir = 'dist'
#f = open(os.path.join(dist_dir, crt_dst_dir, crt_dst_dir + '.manifest'), 'w') # it doesn't seem to work
f = open(os.path.join(dist_dir, '', crt_dst_dir + '.manifest'), 'w')
f.write(manifest)
f.close()
