#!/usr/bin/env python
import inkex
import sys
import optparse
import os
import subprocess

try:
  from subprocess import DEVNULL
except ImportError:
  DEVNULL = open(os.devnull, 'w')

def str_to_bool(s):
    if s.lower() == 'true':
         return True
    elif s.lower() == 'false':
         return False

def create_folder(path):
    if not os.path.exists(path):
        os.mkdir(path)

def append_size(option, opt_str, value, parser, *size):
    if not str_to_bool(value):
        return
    if getattr(parser.values, option.dest) is None:
        setattr(parser.values, option.dest, [])
    getattr(parser.values, option.dest).append(size)

class SizeGroup(optparse.OptionGroup):
    def add_size_option(self, name, size):
        self.add_option('--%s' % name, action='callback', type='string', dest='sizes',
                callback=append_size, callback_args=(name, size))


class ExportAndroidIcons(inkex.Effect):

    def __init__(self):

        inkex.Effect.__init__(self)
        self.OptionParser.add_option('--filename', action='store', type='string', dest='filename')
        self.OptionParser.add_option('--directory', action='store',type='string', dest='directory', default='c:')
        self.OptionParser.add_option('--radio', action='store', type='string', dest='radio')

        group = SizeGroup(self.OptionParser, '')
        group.add_size_option('ldpi', 32)
        group.add_size_option('mdpi', 48)
        # group.add_size_option('tvdpi', 64)
        group.add_size_option('hdpi', 72)
        group.add_size_option('xhdpi', 96)
        group.add_size_option('xxhdpi', 144)
        group.add_size_option('xxxhdpi', 192)
        group.add_size_option('web', 512)
        self.OptionParser.add_option_group(group)

        (self.options, self.args) = self.OptionParser.parse_args()

    def effect(self):
        doc = self.document.getroot()
        svg = self.args[0]
        width  = self.unittouu(doc.get('width'))
        height = self.unittouu(doc.attrib['height'])

        for qualifier, size in self.options.sizes:
            subfolder = '%s-%s' % (self.options.radio, qualifier) if qualifier != 'web' else ''
            path = '%s\%s' % (self.options.directory, subfolder)
            png = path + '\%s.png' % self.options.filename

            create_folder(path)

            subprocess.check_call([
            		'inkscape',
            		'--export-area-page',
            		# '--export-dpi=%s' % dpi,
                    '--export-width=%s' % size,
                    '--export-height=%s' % size,
            		'--export-png=%s' % png,
            		svg])

effect = ExportAndroidIcons()
effect.affect()
