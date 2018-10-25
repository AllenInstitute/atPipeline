import os
import time
import json
import sys
import subprocess
import posixpath

def parseprojectroot(projectdirectory):
    print ("Project directory: " + projectdirectory)
    tok = projectdirectory.split(os.sep)
    dataind = tok.index('data')
    print ("Project data folder: " + tok[dataind+1])
    return tok[dataind+1]

def parse_project_directory(line):
    proj = line.split("raw")
    projectdirectory = proj[0]
    tok = line.split(os.sep)
    ribbondir = tok[len(tok)-2]
    sessiondir = tok[len(tok)-1]
    ribbon = int(ribbondir[6:])
    session = int(sessiondir[7:])
    return [projectdirectory, ribbon, session]

def get_channel_names(directory):
    directory_list = list()
    for root, dirs, files in os.walk(directory, topdown=False):
            for name in dirs:
                directory_list.append(os.path.join(root, name))
    return dirs

def get_channel_nums(statetablefile):
    df=pd.read_csv(statetablefile)
    uniq_ch=df.groupby(['ch']).groups.keys()
    return uniq_ch

def parsefile(fname):

    with open(fname) as f:
        content = f.readlines()

    if len(content)>1:
        print ("The File: "  + fname + " is corrupted!")
    else:
        #parse line
        fullline = content[0]
        fullinetok = fullline.split(",")
        section = int(fullinetok[1])
        owner = str(fullinetok[2])

        line = fullinetok[0]

        proj = line.split("raw")
        projectdirectory = proj[0]

        tok = line.split("/")
        ribbondir = tok[len(tok)-2]
        sessiondir = tok[len(tok)-1]
        ribbon = int(ribbondir[6:])
        session = int(sessiondir[7:])
        return [projectdirectory, ribbon, session, section, owner,fullline]

if __name__ == "__main__":
    owner = "TestOwner"
    firstsection = 0
    lastsection = 1

    dirname = "f:\\data\\M33\\raw\\data\\Ribbon0004\\session02"

    print ("Processing folder: " + dirname)

    for sectnum in range(firstsection,lastsection+1):

        print("Processing section: " + str(sectnum))
        projectdirectory = dirname.strip()
        render_project = parseprojectroot(projectdirectory)
        channels = get_channel_names(projectdirectory)
        [projectroot, ribbon,session] = parse_project_directory(projectdirectory)

        print  ("Project root folder: " + projectroot)

        #create state table
        statetablefile = projectroot + "scripts\\statetable_ribbon_%d_session_%d_section_%d"%(ribbon,session,sectnum)

        #Need to pass posix paths to docker
        (drive, projectRootPathP) = os.path.splitdrive(projectroot)
        projectRootPathP =posixpath.normpath(projectRootPathP.replace('\\', '/'))
        projectRootPathP = "/mnt" + projectRootPathP
        print (projectRootPathP)

        (drive, stateTablePathP) = os.path.splitdrive(statetablefile)
        stateTablePathP = stateTablePathP.replace('\\', '/')
        stateTablePathP = '/mnt' +  stateTablePathP

        print (stateTablePathP)

        #Example
        #docker exec renderapps python -m renderapps.dataimport.create_fast_stacks_multi
        #--render.host localhost
        #--render.client_scripts /shared/render/render-ws-java-client/src/main/scripts
        #--render.port 8080
        #--render.memGB 5G
        #--log_level INFO
        #--statetableFile /data/test
        #--render.project test_project
        #--projectDirectory /data/M33
        #--outputStackPrefix ACQ_S01
        # --render.owner test


        #upload acquisition stacks
        cmd = "docker exec renderapps python -m renderapps.dataimport.create_fast_stacks_multi"
        cmd = cmd + " --render.host W10DTMJ03EG6Z.corp.alleninstitute.org"
        cmd = cmd + " --render.owner %s "%owner
        cmd = cmd + " --render.project %s"%render_project
        cmd = cmd + " --render.client_scripts /shared/render/render-ws-java-client/src/main/scripts"
        cmd = cmd + " --render.port 8080"
        cmd = cmd + " --render.memGB 5G"
        cmd = cmd + " --log_level INFO"
        cmd = cmd + " --statetableFile %s"%stateTablePathP
        cmd = cmd + " --projectDirectory %s"%projectRootPathP
        cmd = cmd + " --outputStackPrefix ACQ_"


        print (cmd)

        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        for line in p.stdout.readlines():
            print (line)

    print ("done")