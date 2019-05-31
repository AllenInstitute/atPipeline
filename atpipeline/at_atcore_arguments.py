#-------------------------------------------------------------------------------
# Name:        command line arguments for atcore
#
# Created:     23/05/2019
#-------------------------------------------------------------------------------
import argparse
from atpipeline import __version__


def add_arguments(parser):
    parser.add_argument('--configfolder',
        metavar="PATH",
        help='Path to config folder',
        default=None)

    parser.add_argument('--configfile',
        metavar="PATH",
        help='Name of data processing config file. May include the path',
        default="at-data-processing-config.ini")

    #Don't allow this one to be set..
    parser.add_argument('--system_config_file',
        help=argparse.SUPPRESS,
        default="at-system-config.ini"
        )

    parser.add_argument('--data',
        metavar="PATH",
        help='Full path to data folder for project data to process',
        required=False)

    parser.add_argument('--datasummary',
        help='Print data information summary',
        action='store_true')

    parser.add_argument('--projectname',
        help='Set project name. Default: name of input datas basefolder',
        required=False)

    parser.add_argument('--pipeline',
        help='Specify the pipeline to use',
        choices={'stitch', 'roughalign', 'finealign', 'register', 'singletile'},
        required=False)

    parser.add_argument('--renderprojectowner',
        help='Specify a RenderProject owner',
        metavar="OWNER",
        type=str,
        nargs='?')

    parser.add_argument('--sessions',
        help='Specify sessions to process',
        type=str)

    parser.add_argument('--ribbons',
        help='Specify ribbons  to process',
        type=str)

    parser.add_argument('--firstsection', metavar='N',
        help='Specify first section (e.g. \'0\' to start with a datasets first section)',
        type=int)

    parser.add_argument('--lastsection', metavar='N',
        help='Specify last section',
        type=int)

    parser.add_argument('--overwritedata',
        help='Overwrite any already processed data',
        action='store_true')

    parser.add_argument('--loglevel',
        choices={'INFO', 'DEBUG', 'WARNING', 'ERROR'},
        help='Set program loglevel',
        default='INFO')

    parser.add_argument('--logtofile',
        help='Log messages to file. The logfile is written to the output datafolder and named "projectname".log',
        action='store_true')

    parser.add_argument('--define', '-D',
        action='append',
        default=[],
        help="Override a value in the config file (-D section.item=value)")

    parser.add_argument('--deleterenderproject',
        help="Delete a render project (including its stacks and match collections) for a specific owner, --renderprojectowner",
        #required='--renderprojectowner' in sys.argv,
        type=str,
        nargs='?'
        )

    parser.add_argument('--version', '-v',
        action='version',
        version=('%%(prog)s %s' % __version__))


def main():
    pass

if __name__ == '__main__':
    main()
