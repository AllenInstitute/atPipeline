#-------------------------------------------------------------------------------
# Name:        command line arguments for atcore
#
# Created:     23/05/2019
#-------------------------------------------------------------------------------
import argparse
import getpass
from atpipeline import __version__

def getUserName():
    try:
        return getpass.getuser()
    except:
        return "unknown"

def add_arguments(parser):
    #Don't allow this one to be set..
    parser.add_argument('--system_config_file',
        help=argparse.SUPPRESS,
        default="at-system-config.ini")

    parser.add_argument('--data',
        metavar="PATH",
        help='Full path to data folder for project data to process',
        required=False)

    parser.add_argument('--datasummary',
        help='Print data information summary',
        action='store_true')

    parser.add_argument('--projectname',
        help='Set project name used in render. Default: name of input data',
        required=False)

    parser.add_argument('--pipeline',
        help='Specify the pipeline to use',
        choices={'stitch', 'roughalign', 'finealign', 'register', 'singletile', 'fineregister'},
        required=False)

    parser.add_argument('--renderprojectowner',
        help='Specify owner for the render project being created',
        metavar="OWNER",
        default=getUserName(),
        required=False)

    parser.add_argument('--sessions',
        help='Specify sessions to process. Default is all sessions.',
        type=str)

    parser.add_argument('--ribbons',
        help='Specify ribbons to process. Default is all ribbons.',
        type=str)

    parser.add_argument('--firstsection', metavar='N',
        help='Specify first section (e.g. \'0\' to start with a datasets first section)',
        type=int)

    parser.add_argument('--lastsection', metavar='N',
        help='Specify last section',
        type=int)

    parser.add_argument('--overwritedata', '--force',
        help='Overwrite any already processed data',
        action='store_true',
        default=False)

    parser.add_argument('--skiploggingtofile',
        help='Skip logging to file (default = false). The logfile is written to the output datafolder and named "projectname".log',
        default=False,
        action='store_true')

    parser.add_argument('--deleterenderproject',
        help="Delete a render project (including its stacks and match collections) for a specific owner, --renderprojectowner",
        type=str,
        nargs='?'
        )

    parser.add_argument('--getprojectsbyowner',
        help="Get a list of projects by owner",
        type=str,
        nargs='?'
        )

    parser.add_argument('--getstacksforproject',
        help="Get a list of projects stacks by owner",
        type=str,
        nargs='?'
        )
