#------------------------------------------------------------------------------
# Name:        common command line arguments use between front and back end
#
# Created:     23/05/2019
#-------------------------------------------------------------------------------
import argparse
from atpipeline import __version__

def add_arguments(parser):
    parser.add_argument('--configfolder', '--configpath',
        metavar="PATH",
        help='Path to config folder',
        default=None)

    parser.add_argument('--define', '-D',
        action='append',
        default=[],
        help="Override a value in the config file (-D SECTION.item=value)")

    parser.add_argument('--printsettings',
        help='Print settings',
        action='store_true')

    parser.add_argument('--loglevel',
        choices={'INFO', 'DEBUG', 'WARNING', 'ERROR'},
        help='Set program loglevel',
        default='INFO')

    parser.add_argument('--version', '-v',
        action='version',
        version=('%%(prog)s %s' % __version__))
