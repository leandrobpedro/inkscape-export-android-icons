#!/usr/bin/python
import inkex
import sys
import optparse
import os
import subprocess
from sys import platform as _plataform

try:
    from subprocess import DEVNULL
except ImportError:
    DEVNULL = open(os.devnull, 'w')

class SizeGroup(optparse.OptionGroup):
    def add_size_option(self, name, size, dpi):
        self.add_option('--%s' % name, action='callback',
                        type='string', dest='sizes',
                        callback=append_size, callback_args=(name, size, dpi))

class ExportAndroidIcons(inkex.Effect):
    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--filename', action='store',
                                    type='string', dest='filename')
        self.OptionParser.add_option('--directory', action='store',
                                    type='string', dest='directory')
        self.OptionParser.add_option('--radio', action='store',
                                    type='string', dest='radio')

        group = SizeGroup(self.OptionParser, '')
        group.add_size_option('ldpi', 32, 67.5)
        group.add_size_option('mdpi', 48, 90)
        # group.add_size_option('tvdpi', 64, 120)
        group.add_size_option('hdpi', 72, 135)
        group.add_size_option('xhdpi', 96, 180)
        group.add_size_option('xxhdpi', 144, 270)
        group.add_size_option('xxxhdpi', 192, 360)
        group.add_size_option('web', 512, 960)

        self.OptionParser.add_option_group(group)

        (self.options, self.args) = self.OptionParser.parse_args()

    def effect(self):
        doc = self.document.getroot()
        svg = self.args[0]
        width  = self.unittouu(doc.get('width'))
        height = self.unittouu(doc.get('height'))

        export(self.options, svg)

def str_to_bool(s):
    if s.lower() == 'true':
         return True
    elif s.lower() == 'false':
        return False

def create_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)

def append_size(option, opt_str, value, parser, *size, **dpi):
    if not str_to_bool(value):
        return
    if getattr(parser.values, option.dest) is None:
        setattr(parser.values, option.dest, [])
    getattr(parser.values, option.dest).append(size)

def error(msg):
    inkex.debug(msg)
    sys.exit(1)

def export(options, svg):
    if not options.filename:
        error('The icon name must be non-null.')
    if not options.directory:
        error('No destination directory selected.')
    if not options.sizes:
        error('Please, select at least one option to export.')

    for (qualifier, size, dpi) in options.sizes:
        # For web icons, do not use subfolder, create on directory root.
        subfolder = ('%s-%s' % (options.radio, qualifier)
            if qualifier != 'web' else '')

        separator = ('\\' if _plataform.startswith('win') else '/')
        path = '%s%s%s' % (options.directory, separator, subfolder)
        png = path + '%s%s.png' % (separator, options.filename)

        # Size base icons for mipmap, and dpi for drawable.
        opt, val = (('width', size)
            if (options.radio == 'mipmap') else ('dpi', dpi))

        create_folder(path)

        subprocess.check_call(['inkscape',
                                '--export-area-page',
                                '--export-%s=%s' % (opt, val),
                                '--export-png=%s' % png,
                                svg])

effect = ExportAndroidIcons()
effect.affect()
