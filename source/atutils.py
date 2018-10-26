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
import json

#Some hardcoded paths..
templates_folder = "p:\\atExplorer\\ThirdParty\\atPipeline\\templates"
mediantemplate    = os.path.join(templates_folder, "median.json")
stitchingtemplate = os.path.join(templates_folder, "stitching.json")


class RenderProject:
    def __init__(self, owner, host, name):
        self.name = name
        self.host = host
        self.owner = owner


def parse_session_folder(path):
    proj = path.split("raw")
    projectdirectory = proj[0]
    tok = path.split(os.sep)
    ribbondir = tok[len(tok)-2]
    sessiondir = tok[len(tok)-1]
    ribbon = int(ribbondir[6:])
    session = int(sessiondir[7:])
    return [projectdirectory, ribbon, session]

#Input is a sessionfolder path
def getProjectNameFromSessionFolder(sessionFolder):
    print ("Session directory: " + sessionFolder)
    tok = sessionFolder.split(os.sep)
    dataind = tok.index('data')
    print ("Project data folder: " + tok[dataind+1])
    return tok[dataind+1]

def getChannelNamesInSessionFolder(directory):
    directory_list = list()
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in dirs:
            directory_list.append(os.path.join(root, name))
    return dirs

def toPosixPath(winpath, prefix):
    p = posixpath.normpath(winpath.replace('\\', '/'))
    p = p[p.index(':') + 1:]

    if len(prefix):
       p = prefix + p
    return p

def dump_json(data, fileName):
    with open(fileName, 'w') as outfile:
         json.dump(data, outfile, indent=4)

def savemedianjson(med, medianfile, render_host, owner, project, acq_stack, median_stack, median_dir, minz, maxz, close_stack):
    med['render']['host']    = render_host
    med['render']['owner']   = owner
    med['render']['project'] = project
    med['input_stack']       = acq_stack
    med['output_stack']      = median_stack
    med['minZ']              = minz
    med['maxZ']              = maxz
    med['output_directory']  = median_dir
    med['close_stack']       = close_stack
    dump_json(med, medianfile)

def main():
    pass

if __name__ == '__main__':
    main()
