#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      matsk
#
# Created:     Oct 24, 2018
#-------------------------------------------------------------------------------

import os
import posixpath
import sys

def toPosixPath(winpath, prefix):
    p = posixpath.normpath(winpath.replace('\\', '/'))
    p = p[p.index(':') + 1:]

    if len(prefix):
       p = prefix + p
    return p

def main():
    pass

if __name__ == '__main__':
    main()
