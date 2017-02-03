#!/usr/bin/env python2
# coding=utf8
# version: 1.0.0

version = "1.0.0"
projectName = "Nerd Fonts"
projectNameAbbreviation = "NF"
projectNameSingular = projectName[:-1]

import sys

try:
    import psMat
except ImportError:
    sys.stderr.write(projectName + ": FontForge module is probably not installed. [See: http://designwithfontforge.com/en-US/Installing_Fontforge.html]\n")
    sys.exit(1)

import re
import os
import argparse
from argparse import RawTextHelpFormatter
import errno
import time
import subprocess

try:
    #Load the module
    import fontforge

except ImportError:
    sys.stderr.write(projectName + ": FontForge module could not be loaded. Try installing fontforge python bindings [e.g. on Linux Debian or Ubuntu: `sudo apt-get install fontforge python-fontforge`]\n")
    sys.exit(1)

# argparse stuff

parser = argparse.ArgumentParser(description='Nerd Fonts Font Patcher: patches a given font with programming and development related glyphs\n\nWebsite: https://github.com/ryanoasis/nerd-fonts', formatter_class=RawTextHelpFormatter)
parser.add_argument('-v', '--version', action='version', version=projectName + ": %(prog)s ("+version+")")
parser.add_argument('font', help='The path to the font to patch (e.g., Inconsolata.otf)')
parser.add_argument('-s', '--mono', '--use-single-width-glyphs', dest='single', action='store_true', help='Whether to generate the glyphs as single-width not double-width (default is double-width)', default=False)
parser.add_argument('-q', '--quiet', '--shutup', dest='quiet', action='store_true', help='Do not generate verbose output', default=False)
parser.add_argument('-w', '--windows', dest='windows', action='store_true', help='Limit the internal font name to 31 characters (for Windows compatibility)', default=False)
parser.add_argument('-c', '--complete', dest='complete', action='store_true', help='Add all available Glyphs', default=False)
parser.add_argument('--fontawesome', dest='fontawesome', action='store_true', help='Add Font Awesome Glyphs (http://fortawesome.github.io/Font-Awesome)', default=False)
parser.add_argument('--fontawesomeextension', dest='fontawesomeextension', action='store_true', help='Add Font Awesome Extension Glyphs (http://andrelgava.github.io/font-awesome-extension)', default=False)
parser.add_argument('--fontlinux', dest='fontlinux', action='store_true', help='Add Font Linux Glyphs (https://github.com/Lukas-W/font-linux)', default=False)
parser.add_argument('--octicons', dest='octicons', action='store_true', help='Add Octicons Glyphs (https://octicons.github.com)', default=False)
parser.add_argument('--powersymbols', dest='powersymbols', action='store_true', help='Add IEC Power Symbols (http://unicodepowersymbol.com)', default=False)
parser.add_argument('--pomicons', dest='pomicons', action='store_true', help='Add Pomicon Glyphs (https://github.com/gabrielelana/pomicons)', default=False)
parser.add_argument('--powerline', dest='powerline', action='store_true', help='Add Powerline Glyphs', default=False)
parser.add_argument('--powerlineextra', dest='powerlineextra', action='store_true', help='Add Powerline Glyphs (https://github.com/ryanoasis/powerline-extra-symbols)', default=False)
parser.add_argument('--custom', type=str, nargs='?', dest='custom', help='Specify a custom symbol font. All new glyphs will be copied, with no scaling applied.', default=False)
parser.add_argument('--postprocess', type=str, nargs='?', dest='postprocess', help='Specify a Script for Post Processing', default=False)

# http://stackoverflow.com/questions/15008758/parsing-boolean-values-with-argparse
progressbars_group_parser = parser.add_mutually_exclusive_group(required=False)
progressbars_group_parser.add_argument('--progressbars', dest='progressbars', action='store_true', help='Show percentage completion progress bars per Glyph Set')
progressbars_group_parser.add_argument('--no-progressbars', dest='progressbars', action='store_false', help='Don\'t show percentage completion progress bars per Glyph Set')
parser.set_defaults(progressbars=True)

parser.add_argument('--careful', dest='careful', action='store_true', help='Do not overwrite existing glyphs if detected', default=False)
parser.add_argument('-ext', '--extension', type=str, nargs='?', dest='extension', help='Change font file type to create (e.g., ttf, otf)', default="")
parser.add_argument('-out', '--outputdir', type=str, nargs='?', dest='outputdir', help='The directory to output the patched font file to', default=".")
args = parser.parse_args()

changelog = open("changelog.md", "r")
minimumVersion = 20141231
actualVersion = int(fontforge.version())
# un-comment following line for testing invalid version error handling
#actualVersion = 20120731
# versions tested: 20150612, 20150824

if actualVersion < minimumVersion:
    print projectName + ": You seem to be using an unsupported (old) version of fontforge: " + str(actualVersion)
    print projectName + ": Please use at least version: " + str(minimumVersion)
    sys.exit(1)

verboseAdditionalFontNameSuffix = " " + projectNameSingular

if args.complete:
    args.fontawesome = True
    args.fontawesomeextension = True
    args.fontlinux = True
    args.octicons = True
    args.powersymbols = True
    args.pomicons = True
    args.powerline = True
    args.powerlineextra = True

if args.windows:
    # attempt to shorten here on the additional name BEFORE trimming later
    additionalFontNameSuffix = " " + projectNameAbbreviation
else:
    additionalFontNameSuffix = verboseAdditionalFontNameSuffix

if args.fontawesome:
    additionalFontNameSuffix += " A"
    verboseAdditionalFontNameSuffix += " Plus Font Awesome"

if args.fontawesomeextension:
    additionalFontNameSuffix += " AE"
    verboseAdditionalFontNameSuffix += " Plus Font Awesome Extension"

if args.octicons:
    additionalFontNameSuffix += " O"
    verboseAdditionalFontNameSuffix += " Plus Octicons"

if args.powersymbols:
    additionalFontNameSuffix += " PS"
    verboseAdditionalFontNameSuffix += " Plus Power Symbols"

if args.pomicons:
    additionalFontNameSuffix += " P"
    verboseAdditionalFontNameSuffix += " Plus Pomicons"

if args.fontlinux:
    additionalFontNameSuffix += " L"
    verboseAdditionalFontNameSuffix += " Plus Font Linux"

# if all source glyphs included simplify the name
if args.fontawesome and args.fontawesomeextension and args.octicons and args.powersymbols and args.pomicons and args.powerlineextra and args.fontlinux:
    additionalFontNameSuffix = " " + projectNameSingular + " C"
    verboseAdditionalFontNameSuffix = " " + projectNameSingular + " Complete"

# add mono signifier to end of name
if args.single:
    additionalFontNameSuffix += " M"
    verboseAdditionalFontNameSuffix += " Mono"

sourceFont = fontforge.open(args.font)

# basically split the font name around the dash "-" to get the fontname and the style (e.g. Bold)
# this does not seem very reliable so only use the style here as a fallback if the font does not
# have an internal style defined (in sfnt_names)
# using '([^-]*?)' to get the item before the first dash "-"
# using '([^-]*(?!.*-))' to get the item after the last dash "-"
fontname, fallbackStyle = re.match("^([^-]*).*?([^-]*(?!.*-))$", sourceFont.fontname).groups()
# dont trust 'sourceFont.familyname'
familyname = fontname
# fullname (filename) can always use long/verbose font name, even in windows
fullname = sourceFont.fullname + verboseAdditionalFontNameSuffix
fontname = fontname + additionalFontNameSuffix.replace(" ", "")

# let us try to get the 'style' from the font info in sfnt_names and fallback to the
# parse fontname if it fails:
try:
    # search tuple:
    subFamilyTupleIndex = [x[1] for x in sourceFont.sfnt_names].index("SubFamily")
    # String ID is at the second index in the Tuple lists
    sfntNamesStringIDIndex = 2
    # now we have the correct item:
    subFamily = sourceFont.sfnt_names[sfntNamesStringIDIndex][subFamilyTupleIndex]
except IndexError:
    print projectName + ": Could not find 'SubFamily' for given font, falling back to parsed fontname"
    subFamily = fallbackStyle

# some fonts have inaccurate 'SubFamily', if it is Regular let us trust the filename more:
if subFamily == "Regular":
    subFamily = fallbackStyle

if args.windows:
    maxFamilyLength = 31
    maxFontLength = maxFamilyLength-len('-' + subFamily)
    familyname += " " + projectNameAbbreviation
    fullname += " Windows Compatible"
    # now make sure less than 32 characters name length
    if len(fontname) > maxFontLength:
        fontname = fontname[:maxFontLength]
    if len(familyname) > maxFamilyLength:
        familyname = familyname[:maxFamilyLength]
else:
    familyname += " " + projectNameSingular

# Don't truncate the subfamily to keep fontname unique.  MacOS treats fonts with
# the same name as the same font, even if subFamily is different.
fontname += '-' + subFamily

# rename font

def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text


def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

make_sure_path_exists(args.outputdir)

# comply with SIL Open Font License (OFL)
reservedFontNameReplacements = {
    'source'  : 'sauce',
    'Source'  : 'Sauce',
    'hermit'  : 'hurmit',
    'Hermit'  : 'Hurmit',
    'fira'    : 'fura',
    'Fira'    : 'Fura',
    'hack'    : 'knack',
    'Hack'    : 'Knack',
    'hasklig' : 'hasklug',
    'Hasklig' : 'Hasklug',
    'Share'   : 'Shure',
    'share'   : 'shure',
    'terminus': 'terminess',
    'Terminus': 'Terminess'
}

projectInfo = "Patched with '" + projectName + " Patcher' (https://github.com/ryanoasis/nerd-fonts)"

sourceFont.familyname = replace_all(familyname, reservedFontNameReplacements)
sourceFont.fullname = replace_all(fullname, reservedFontNameReplacements)
sourceFont.fontname = replace_all(fontname, reservedFontNameReplacements)
sourceFont.appendSFNTName('English (US)', 'Preferred Family', sourceFont.familyname)
sourceFont.appendSFNTName('English (US)', 'Compatible Full', sourceFont.fullname)
sourceFont.appendSFNTName('English (US)', 'SubFamily', subFamily)
sourceFont.comment = projectInfo
sourceFont.fontlog = projectInfo + "\n\n" + changelog.read()

# todo version not being set for all font types (e.g. ttf)
#print "Version was " + sourceFont.version
sourceFont.version += ";" + projectName + " " + version
#print "Version now is " + sourceFont.version

# Prevent glyph encoding position conflicts between glyph sets

octiconsExactEncodingPosition = True
if args.fontawesome and args.octicons:
    octiconsExactEncodingPosition = False

fontlinuxExactEncodingPosition = True
if args.fontawesome or args.octicons:
    fontlinuxExactEncodingPosition = False

# Supported params: overlap | careful

# Powerline dividers
SYM_ATTR_POWERLINE = {
    'default': { 'align': 'c', 'valign': 'c', 'stretch': 'pa', 'params': '' },

    # Arrow tips
    0xe0b0: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0b1: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0b2: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0b3: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },

    # Rounded arcs
    0xe0b4: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },
    0xe0b5: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },
    0xe0b6: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },
    0xe0b7: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },

    # Bottom Triangles
    0xe0b8: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0b9: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0ba: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0bb: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },

    # Top Triangles
    0xe0bc: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0bd: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0be: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0bf: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },

    # Flames
    0xe0c0: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },
    0xe0c1: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },
    0xe0c2: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },
    0xe0c3: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },

    # Small squares
    0xe0c4: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': '' },
    0xe0c5: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': '' },

    # Bigger squares
    0xe0c6: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': '' },
    0xe0c7: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': '' },

    # Waveform
    0xe0c8: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.01} },

    # Hexagons
    0xe0cc: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': '' },
    0xe0cd: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': '' },

    # Legos
    0xe0ce: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': '' },
    0xe0cf: { 'align': 'c', 'valign': 'c', 'stretch': 'xy', 'params': '' },
    0xe0d1: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },

    # Top and bottom trapezoid
    0xe0d2: { 'align': 'l', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
    0xe0d4: { 'align': 'r', 'valign': 'c', 'stretch': 'xy', 'params': {'overlap':0.02} },
}

SYM_ATTR_DEFAULT = {
    # 'pa' == preserve aspect ratio
    'default': { 'align': 'c', 'valign': 'c', 'stretch': 'pa', 'params': '' },
}

SYM_ATTR_FONTA = {
    # 'pa' == preserve aspect ratio
    'default': { 'align': 'c', 'valign': 'c', 'stretch': 'pa', 'params': '' },

    # Don't center these arrows vertically
    0xf0dc: { 'align': 'c', 'valign': '', 'stretch': 'pa', 'params': '' },
    0xf0dd: { 'align': 'c', 'valign': '', 'stretch': 'pa', 'params': '' },
    0xf0de: { 'align': 'c', 'valign': '', 'stretch': 'pa', 'params': '' },
}

CUSTOM_ATTR = {
    # 'pa' == preserve aspect ratio
    'default': { 'align': 'c', 'valign': '', 'stretch': '', 'params': '' },
}

# Most glyphs we want to maximize during the scale.  However, there are some
# that need to be small or stay relative in size to each other.
# The following list are those glyphs.  A tuple represents a range.
DEVI_SCALE_LIST  = { 'ScaleGlyph': 0xE60E, 'GlyphsToScale': [ (0xe6bd, 0xe6c3), ] }
FONTA_SCALE_LIST = { 'ScaleGlyph': 0xF17A, 'GlyphsToScale': [ 0xf005, 0xf006, (0xf026, 0xf028), 0xf02b, 0xf02c, (0xf031, 0xf035), (0xf044, 0xf054), (0xf060, 0xf063), 0xf077, 0xf078, 0xf07d, 0xf07e, 0xf089, (0xf0d7, 0xf0da), (0xf0dc, 0xf0de), (0xf100, 0xf107), 0xf141, 0xf142, (0xf153, 0xf15a), (0xf175, 0xf178), 0xf182, 0xf183, (0xf221, 0xf22d), (0xf255, 0xf25b), ] }
OCTI_SCALE_LIST  = { 'ScaleGlyph': 0xF02E, 'GlyphsToScale': [ (0xf03d, 0xf040), 0xf044, (0xf051, 0xf053), 0xf05a, 0xf05b, 0xf071, 0xf078, (0xf09f, 0xf0aa), 0xf0ca, ] }

# Define the character ranges
# Symbol font ranges

PATCH_SET = [
    { 'Enabled': True,                      'Name': "Seti-UI + Custom", 'Filename': "original-source.otf",         'Exact': False,'SymStart': 0xE4FA, 'SymEnd': 0xE52B, 'SrcStart': 0xE5FA,'SrcEnd': 0xE62B,'ScaleGlyph': None,  'Attributes': SYM_ATTR_DEFAULT },
    { 'Enabled': True,                      'Name': "Devicons", 'Filename': "devicons.ttf",                'Exact': False,'SymStart': 0xE600, 'SymEnd': 0xE6C5, 'SrcStart': 0xE700,'SrcEnd': 0xE7C5,'ScaleGlyph': DEVI_SCALE_LIST,'Attributes': SYM_ATTR_DEFAULT },
    { 'Enabled': args.powerline,            'Name': "Powerline Symbols", 'Filename': "PowerlineSymbols.otf",        'Exact': True, 'SymStart': 0xE0A0, 'SymEnd': 0xE0A2, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_POWERLINE },
    { 'Enabled': args.powerline,            'Name': "Powerline Symbols", 'Filename': "PowerlineSymbols.otf",        'Exact': True, 'SymStart': 0xE0B0, 'SymEnd': 0xE0B3, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_POWERLINE },
    { 'Enabled': args.powerlineextra,       'Name': "Powerline Extra Symbols", 'Filename': "PowerlineExtraSymbols.otf",   'Exact': True, 'SymStart': 0xE0A3, 'SymEnd': 0xE0A3, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_POWERLINE },
    { 'Enabled': args.powerlineextra,       'Name': "Powerline Extra Symbols", 'Filename': "PowerlineExtraSymbols.otf",   'Exact': True, 'SymStart': 0xE0B4, 'SymEnd': 0xE0C8, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_POWERLINE },
    { 'Enabled': args.powerlineextra,       'Name': "Powerline Extra Symobls", 'Filename': "PowerlineExtraSymbols.otf",   'Exact': True, 'SymStart': 0xE0CC, 'SymEnd': 0xE0D4, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_POWERLINE },
    { 'Enabled': args.pomicons,             'Name': "Pomicons", 'Filename': "Pomicons.otf",                'Exact': True, 'SymStart': 0xE000, 'SymEnd': 0xE00A, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_DEFAULT  },
    { 'Enabled': args.fontawesome,          'Name': "Font Awesome", 'Filename': "FontAwesome.otf",             'Exact': True, 'SymStart': 0xF000, 'SymEnd': 0xF2E0, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': FONTA_SCALE_LIST,'Attributes': SYM_ATTR_FONTA },
    { 'Enabled': args.fontawesomeextension, 'Name': "Font Awesome Extension", 'Filename': "font-awesome-extension.ttf",  'Exact': False, 'SymStart': 0xE000, 'SymEnd': 0xE0A9, 'SrcStart': 0xE200,  'SrcEnd': 0xE2A9,  'ScaleGlyph': None, 'Attributes': SYM_ATTR_DEFAULT }, # Maximize
    { 'Enabled': args.fontlinux,            'Name': "Font Linux", 'Filename': "font-linux.ttf",              'Exact': fontlinuxExactEncodingPosition, 'SymStart': 0xF100, 'SymEnd': 0xF115, 'SrcStart': 0xF300, 'SrcEnd': 0xF315, 'ScaleGlyph': None, 'Attributes': SYM_ATTR_DEFAULT },
    { 'Enabled': args.powersymbols,         'Name': "Power Symbols", 'Filename': "Unicode_IEC_symbol_font.otf", 'Exact': True, 'SymStart': 0x23FB, 'SymEnd': 0x23FE, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_DEFAULT  }, # Power, Power On/Off, Power On, Sleep
    { 'Enabled': args.powersymbols,         'Name': "Power Symbols", 'Filename': "Unicode_IEC_symbol_font.otf", 'Exact': True, 'SymStart': 0x2B58, 'SymEnd': 0x2B58, 'SrcStart': None,  'SrcEnd': None,  'ScaleGlyph': None,  'Attributes': SYM_ATTR_DEFAULT  }, # Heavy Circle (aka Power Off)
    { 'Enabled': args.octicons,             'Name': "Octions", 'Filename': "octicons.ttf",                'Exact': octiconsExactEncodingPosition,  'SymStart': 0xF000, 'SymEnd': 0xF105, 'SrcStart': 0xF400, 'SrcEnd': 0xF505, 'ScaleGlyph': OCTI_SCALE_LIST, 'Attributes': SYM_ATTR_DEFAULT },  # Magnifying glass
    { 'Enabled': args.octicons,             'Name': "Octicons", 'Filename': "octicons.ttf",                'Exact': octiconsExactEncodingPosition,  'SymStart': 0x2665, 'SymEnd': 0x2665, 'SrcStart': None, 'SrcEnd': None, 'ScaleGlyph': OCTI_SCALE_LIST, 'Attributes': SYM_ATTR_DEFAULT },  # Heart
    { 'Enabled': args.octicons,             'Name': "Octicons", 'Filename': "octicons.ttf",                'Exact': octiconsExactEncodingPosition,  'SymStart': 0X26A1, 'SymEnd': 0X26A1, 'SrcStart': None, 'SrcEnd': None, 'ScaleGlyph': OCTI_SCALE_LIST, 'Attributes': SYM_ATTR_DEFAULT },  # Zap
    { 'Enabled': args.octicons,             'Name': "Octicons", 'Filename': "octicons.ttf",                'Exact': octiconsExactEncodingPosition,  'SymStart': 0xF27C, 'SymEnd': 0xF27C, 'SrcStart': 0xF67C, 'SrcEnd': 0xF67C, 'ScaleGlyph': OCTI_SCALE_LIST, 'Attributes': SYM_ATTR_DEFAULT },  # Desktop
    { 'Enabled': args.custom,               'Name': "Custom", 'Filename': args.custom,                   'Exact': True,  'SymStart': 0x0000, 'SymEnd': 0x0000, 'SrcStart': 0x0000, 'SrcEnd': 0x0000, 'ScaleGlyph': None, 'Attributes': CUSTOM_ATTR },
]

# win_ascent and win_descent are used to set the line height for windows fonts.
# hhead_ascent and hhead_descent are used to set the line height for mac fonts.
#
# Make the total line size even.  This seems to make the powerline separators
# center more evenly.
if (sourceFont.os2_winascent + sourceFont.os2_windescent) % 2 != 0:
    sourceFont.os2_winascent += 1

# Make the line size identical for windows and mac
sourceFont.hhea_ascent = sourceFont.os2_winascent
sourceFont.hhea_descent = -sourceFont.os2_windescent

# Line gap add extra space on the bottom of the line which doesn't allow
# the powerline glyphs to fill the entire line.
sourceFont.hhea_linegap = 0
sourceFont.os2_typolinegap = 0

# Initial font dimensions
font_dim = {
    'xmin'  :    0,
    'ymin'  :    -sourceFont.os2_windescent,
    'xmax'  :    0,
    'ymax'  :    sourceFont.os2_winascent,
    'width' :    0,
    'height':    0,
}

# Find the biggest char width
# Ignore the y-values, os2_winXXXXX values set above are used for line height
#
# 0x00-0x17f is the Latin Extended-A range
for glyph in range(0x00, 0x17f):
    try:
        (xmin, ymin, xmax, ymax) = sourceFont[glyph].boundingBox()
    except TypeError:
        continue

    if font_dim['width'] < sourceFont[glyph].width:
        font_dim['width'] = sourceFont[glyph].width

    if xmax > font_dim['xmax']: font_dim['xmax'] = xmax

# Calculate font height
font_dim['height'] = abs(font_dim['ymin']) + font_dim['ymax']

# Update the font encoding to ensure that the Unicode glyphs are available.
sourceFont.encoding = 'UnicodeFull'

# Fetch this property before adding outlines
onlybitmaps = sourceFont.onlybitmaps

def get_dim(glyph):
    bbox = glyph.boundingBox()

    return  {
        'xmin'  : bbox[0],
        'ymin'  : bbox[1],
        'xmax'  : bbox[2],
        'ymax'  : bbox[3],

        'width' : bbox[2] + (-bbox[0]),
        'height': bbox[3] + (-bbox[1]),
    }

def set_width(sourceFont, width):
    sourceFont.selection.all()
    for glyph in sourceFont.selection.byGlyphs:
        glyph.width = width

def get_scale_factor(font_dim, sym_dim):
    scale_ratio = 1
    # We want to preserve x/y aspect ratio, so find biggest scale factor that allows symbol to fit
    scale_ratio_x = font_dim['width'] / sym_dim['width']
    # font_dim['height'] represents total line height, keep our symbols sized based upon font's em
    scale_ratio_y = sourceFont.em / sym_dim['height']
    if scale_ratio_x > scale_ratio_y:
        scale_ratio = scale_ratio_y
    else:
        scale_ratio = scale_ratio_x
    return scale_ratio

def use_scale_glyph( unicode_value, glyph_list ):
    for i in glyph_list:
        if isinstance(i, tuple):
            if unicode_value >= i[0] and unicode_value <= i[1]:
                return True
        else:
            if unicode_value == i:
                return True
    return False

## modified from: http://stackoverflow.com/questions/3160699/python-progress-bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value at 1 or bigger represents 100%
def update_progress(progress, status=""):
    barLength = 40 # Modify this to change the length of the progress bar
    if isinstance(progress, int):
        progress = float(progress)
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\r[{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def copy_glyphs(sourceFont, sourceFontStart, sourceFontEnd, symbolFont, symbolFontStart, symbolFontEnd, exactEncoding, scaleGlyph, attributes):

    progressText = ''
    careful = False
    if args.careful:
        careful = True

    if exactEncoding is False:
        sourceFontList = []
        sourceFontCounter = 0

        for i in xrange(sourceFontStart, sourceFontEnd + 1):
            sourceFontList.append(format(i, 'X'))

    scale_factor = 0
    if scaleGlyph:
        sym_dim = get_dim(symbolFont[scaleGlyph['ScaleGlyph']])
        scale_factor = get_scale_factor(font_dim, sym_dim)

    # Create glyphs from symbol font

    # If we are going to copy all Glyphs, then assume we want to be careful
    # and only copy those that are not already contained in the source font
    if symbolFontStart == 0:
        symbolFont.selection.all()
        sourceFont.selection.all()
        careful = True
    else:
        symbolFont.selection.select(("ranges","unicode"),symbolFontStart,symbolFontEnd)
        sourceFont.selection.select(("ranges","unicode"),sourceFontStart,sourceFontEnd)

    glyphSetLength = max(1, symbolFontEnd-symbolFontStart)

    for index, sym_glyph in enumerate(symbolFont.selection.byGlyphs):

        index = max(1, index)

        try:
            sym_attr = attributes[sym_glyph.unicode]
        except KeyError:
            sym_attr = attributes['default']

        if exactEncoding:
            # use the exact same hex values for the source font as for the symbol font
            currentSourceFontGlyph = sym_glyph.encoding
            # Save as a hex string without the '0x' prefix
            copiedToSlot = format(sym_glyph.unicode, 'X')
        else:
            # use source font defined hex values based on passed in start and end
            # convince that this string really is a hex:
            currentSourceFontGlyph = int("0x" + sourceFontList[sourceFontCounter], 16)
            copiedToSlot = sourceFontList[sourceFontCounter]
            sourceFontCounter += 1

        if int(copiedToSlot, 16) < 0:
            print "Found invalid glyph slot number. Skipping."
            continue

        if args.quiet == False:
            if args.progressbars:
                if glyphSetLength == index+1:
                    progressText = ' '*len(progressText)
                else:
                    progressText = " " + str(sym_glyph.glyphname) + " to " + copiedToSlot + " " + str(glyphSetLength) + " " + str(index);

                update_progress(round(float(index)/glyphSetLength,2), progressText)
            else:
                progressText = "\nUpdating glyph: " + str(sym_glyph) + " " + str(sym_glyph.glyphname) + " putting at: " + copiedToSlot;
                sys.stdout.write(progressText)
                sys.stdout.flush()

        # Prepare symbol glyph dimensions
        sym_dim = get_dim(sym_glyph)

        # check if a glyph already exists in this location
        if careful or 'careful' in sym_attr['params']:
            if copiedToSlot.startswith("uni"):
                copiedToSlot = copiedToSlot[3:]

            codepoint = int("0x" + copiedToSlot, 16)
            if codepoint in sourceFont:
                if args.quiet == False:
                    print "  Found existing Glyph at "+ copiedToSlot +".  Skipping..."
                # We don't want to touch anything so move to next Glyph
                continue

        # Select and copy symbol from its encoding point
        # We need to do this select after the careful check, this way we don't
        # reset our selection before starting the next loop
        symbolFont.selection.select(sym_glyph.encoding)
        symbolFont.copy()

        # Paste it
        sourceFont.selection.select(currentSourceFontGlyph)
        sourceFont.paste()

        sourceFont[currentSourceFontGlyph].glyphname = sym_glyph.glyphname

        # Now that we have copy/pasted the glyph, if we are creating a monospace
        # font we need to scale and move the glyphs.  It is possible to have
        # empty glyphs, so we need to skip those.
        if args.single and sym_dim['width'] and sym_dim['height']:
            scale_ratio_x = 1
            scale_ratio_y = 1
            # If we want to preserve that aspect ratio of the glyphs we need to
            # find the largest possible scaling factor that will allow the glyph
            # to fit in both the x and y directions
            if sym_attr['stretch'] == 'pa':
                if scale_factor and use_scale_glyph(sym_glyph.unicode, scaleGlyph['GlyphsToScale'] ):
                    # We want to preserve the relative size of each glyph to other glyphs
                    # in the same symbol font.
                    scale_ratio_x = scale_factor
                    scale_ratio_y = scale_factor
                else:
                    # In this case, each glyph is sized independantly to each other
                    scale_ratio_x = get_scale_factor(font_dim, sym_dim)
                    scale_ratio_y = scale_ratio_x
            else:
                if 'x' in sym_attr['stretch']:
                    # Stretch the glyph horizontally to fit the entire available width
                    scale_ratio_x = font_dim['width'] / sym_dim['width']
                if 'y' in sym_attr['stretch']:
                    # Stretch the glyph vertically to total line height (good for powerline separators)
                    scale_ratio_y = font_dim['height'] / sym_dim['height']

            if scale_ratio_x != 1 or scale_ratio_y != 1:
                if 'overlap' in sym_attr['params']:
                    scale_ratio_x *= 1+sym_attr['params']['overlap']
                    scale_ratio_y *= 1+sym_attr['params']['overlap']
                sourceFont.transform(psMat.scale(scale_ratio_x, scale_ratio_y))

            # Use the dimensions from the newly pasted and stretched glyph
            sym_dim = get_dim(sourceFont[currentSourceFontGlyph])

            y_align_distance = 0
            if sym_attr['valign'] == 'c':
                # Center the symbol vertically by matching the center of the line height and center of symbol
                sym_ycenter = sym_dim['ymax'] - (sym_dim['height'] / 2)
                font_ycenter = font_dim['ymax'] - (font_dim['height'] / 2)
                y_align_distance = font_ycenter - sym_ycenter

            # Handle glyph l/r/c alignment
            x_align_distance = 0
            if sym_attr['align']:
                # First find the baseline x-alignment (left alignment amount)
                x_align_distance = font_dim['xmin']-sym_dim['xmin']
                if sym_attr['align'] == 'c':
                    # Center align
                    x_align_distance += (font_dim['width']/2) - (sym_dim['width']/2)
                elif sym_attr['align'] == 'r':
                    # Right align
                    x_align_distance += font_dim['width'] - sym_dim['width']

            if 'overlap' in sym_attr['params']:
                overlap_width = font_dim['width'] * sym_attr['params']['overlap']
                if sym_attr['align'] == 'l':
                    x_align_distance -= overlap_width
                if sym_attr['align'] == 'r':
                    x_align_distance += overlap_width

            align_matrix = psMat.translate(x_align_distance, y_align_distance)
            sourceFont.transform(align_matrix)

        if args.single:
            # Ensure the font is considered monospaced on Windows by setting the same
            # width for all character glyphs.
            # This needs to be done for all glyphs, even the ones that are empty and
            # didn't go through the scaling operations.
            sourceFont[currentSourceFontGlyph].width = font_dim['width']

        # reset selection so iteration works propertly @todo fix? rookie misunderstanding?
        # This is likely needed because the selection was changed when the glyph was copy/pasted
        if symbolFontStart == 0:
            symbolFont.selection.all()
        else:
            symbolFont.selection.select(("ranges","unicode"),symbolFontStart,symbolFontEnd)
    # end for

    if args.quiet == False or args.progressbars:
        sys.stdout.write("\n")

    return

if args.extension == "":
    extension = os.path.splitext(sourceFont.path)[1]
else:
    extension = '.'+args.extension

if args.single and extension == '.ttf':
    # Force width to be equal on all glyphs to ensure the font is considered monospaced on Windows.
    # This needs to be done on all characters, as some information seems to be lost from the original font file.
    # This is only a problem with ttf files, otf files seem to be okay.
    set_width(sourceFont, font_dim['width'])

# Prevent opening and closing the fontforge font. Makes things faster when patching
# multiple ranges using the same symbol font.
PreviousSymbolFilename = ""
symfont = None

for patch in PATCH_SET:
    if patch['Enabled']:
        if PreviousSymbolFilename != patch['Filename']:
            # We have a new symbol font, so close the previous one if it exists
            if symfont:
                symfont.close()
                symfont = None
            symfont = fontforge.open("src/glyphs/"+patch['Filename'])
            # Match the symbol font size to the source font size
            symfont.em = sourceFont.em
            PreviousSymbolFilename = patch['Filename']
        # If patch table doesn't include a source start and end, re-use the symbol font values
        SrcStart = patch['SrcStart']
        SrcEnd = patch['SrcEnd']
        if not SrcStart:
            SrcStart = patch['SymStart']
        if not SrcEnd:
            SrcEnd = patch['SymEnd']

        if args.quiet == False:
            sys.stdout.write("Adding " + str(max(1, patch['SymEnd']-patch['SymStart'])) + " Glyphs from " + patch['Name'] + " Set \n")

        copy_glyphs(sourceFont, SrcStart, SrcEnd, symfont, patch['SymStart'], patch['SymEnd'],  patch['Exact'], patch['ScaleGlyph'], patch['Attributes'])

if symfont:
    symfont.close()

print "\nDone with Path Sets, generating font..."

# the `PfEd-comments` flag is required for Fontforge to save
# '.comment' and '.fontlog'.
sourceFont.generate(args.outputdir + "/" + sourceFont.fullname + extension, flags=('opentype', 'PfEd-comments'))

print "\nGenerated: " + sourceFont.fullname

if args.postprocess:
    subprocess.call([args.postprocess, args.outputdir + "/" + sourceFont.fullname + extension])
    print "\nPost Processed: " + sourceFont.fullname
