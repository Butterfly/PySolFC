#!/usr/bin/env python
# -*- mode: python; -*-

import os
from glob import glob

from pysollib.settings import PACKAGE_URL
from pysollib.settings import VERSION

from setuptools import setup

if os.name == 'nt':
    import py2exe  # noqa: F401

if os.name == 'posix':
    data_dir = 'share/PySolFC'
elif os.name == 'nt':
    data_dir = 'data'
else:
    data_dir = 'data'

ddirs = [
    'html',
    'images',
    'sound',
    'tiles',
    'toolbar',
    'themes',
    'tcl',
    ]
for s in open('MANIFEST.in'):
    if s.startswith('graft data/cardset-'):
        ddirs.append(s[11:].strip())

data_files = []

for d in ddirs:
    for root, dirs, files in os.walk(os.path.join('data', d)):
        if root.find('.svn') >= 0:
            continue
        if files:
            # files = map(lambda f: os.path.join(root, f), files)
            files = [os.path.join(root, f) for f in files]
            data_files.append((os.path.join(data_dir, root[5:]), files))

if os.name == 'posix':
    data_files.append(('share/pixmaps', ['data/pysol.xbm', 'data/pysol.xpm']))
    for size in os.listdir('data/images/icons'):
        data_files.append(('share/icons/hicolor/%s/apps' % size,
                           ['data/images/icons/%s/pysol.png' % size]))
    for mofile in glob('locale/*/*/*.mo'):
        data_files.append(('share/' + os.path.dirname(mofile), [mofile]))
    data_files.append((data_dir, ['data/pysolfc.glade']))
    data_files.append(('share/applications', ['data/pysol.desktop']))

# from pprint import pprint; pprint(data_files)
# import sys; sys.exit()

long_description = '''\
PySolFC is a collection of more than 1000 solitaire card games.
Its features include modern look and feel (uses Tile widget set), multiple
cardsets and tableau backgrounds, sound, unlimited undo, player statistics,
a hint system, demo games, a solitaire wizard, support for user written
plug-ins, an integrated HTML help browser, and lots of documentation.
'''

kw = {
    'name': 'PySolFC',
    'version': VERSION,
    'url': PACKAGE_URL,
    'author': 'Skomoroh',
    'author_email': 'skomoroh@gmail.com',
    'description': 'a Python solitaire game collection',
    'install_requires': [
        'attrs',
        'configobj',
        'pycotap',
        'pysol_cards',
        'random2',
        'six',
    ],
    'long_description': long_description,
    'license': 'GPL',
    'scripts': ['pysol.py'],
    'packages': ['pysollib',
                 'pysollib.macosx',
                 'pysollib.winsystems',
                 'pysollib.tk',
                 'pysollib.tile',
                 'pysollib.pysolgtk',
                 'pysollib.ui',
                 'pysollib.ui.tktile',
                 'pysollib.kivy',
                 'pysollib.games',
                 'pysollib.games.special',
                 'pysollib.games.ultra',
                 'pysollib.games.mahjongg'],
    'data_files': data_files,
    }

if os.name == 'nt':
    kw['windows'] = [{'script': 'pysol.py',
                      'icon_resources': [(1, 'data/pysol.ico')], }]
    kw['packages'].remove('pysollib.pysolgtk')

setup(**kw)
