#------------------------------------------------------------------------------
# Name:        command line arguments for atbackend
#
# Created:     23/05/2019
#-------------------------------------------------------------------------------
import argparse
from atpipeline import __version__

def add_arguments(parser):
    #Get processing parameters
    cmdgroup = parser.add_mutually_exclusive_group()
    cmdgroup.add_argument('--startall',            help='Start the whole AT backend',          action='store_true')
    cmdgroup.add_argument('--startrenderbackend',  help='Start the Render backend',            action='store_true')
    cmdgroup.add_argument('--killall', '--stopall', help='Stop the AT backend',                nargs='?', const='testing', type=str)
    cmdgroup.add_argument('--pruneall',            help='Prune the AT backend',                action='store_true')
    cmdgroup.add_argument('--prunecontainers',     help='Prune the AT backend',                action='store_true')
    cmdgroup.add_argument('--pruneimages',         help='Prune the AT backend',                action='store_true')
    cmdgroup.add_argument('--restartall',          help='Restart all AT backend container',    action='store_true' )
    cmdgroup.add_argument('--status',              help='Get backend status',                  action='store_true' )

    #Container by container (not all implemented)
    cmdgroup.add_argument('-s', '--start',         help='Start a specific backend container, e.g. atcore',     nargs='?',const='atcore', type=str)
    cmdgroup.add_argument('-k', '--kill',          help='Stop a specific backend container',                  nargs='?',const='atcore', type=str)
    cmdgroup.add_argument('-r', '--restart',       help='Restart a specific backend container, e.g. atcore',   nargs='?',const='atcore', type=str)

    # Flags to alter behaviour
    parser.add_argument('--atcoreimagetag',       help='atcore image tag to use', default=None)

    parser.add_argument('--configfolder',
            metavar="PATH",
            help='Path to config folder',
            default=None)

    parser.add_argument('--define', '-D',
        action='append',
        default=[],
        help="Override a value in the config file (-D section.item=value)")

    parser.add_argument('--version', '-v', action='version', version=('%%(prog)s %s' % __version__))


def main():
    pass

if __name__ == '__main__':
    main()
