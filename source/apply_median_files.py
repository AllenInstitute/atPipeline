import paramiko
import os
import time
import json
import sys
import subprocess
import posixpath

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

def parseprojectroot(projectdirectory):
    print ("Project directory: " + projectdirectory)
    tok = projectdirectory.split(os.sep)
    dataind = tok.index('data')
    print ("Project data folder: " + tok[dataind+1])
    return tok[dataind+1]

def parsefile(fname):
    with open(fname) as f:
         content = f.readlines()

    if len(content) > 1:
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

def savemedianjson(med,medianfile, render_host, owner, project,acq_stack,median_stack,median_dir,minz,maxz,close_stack):
    med['render']['host'] = render_host
    med['render']['owner'] = owner
    med['render']['project'] = project
    med['input_stack'] = acq_stack
    med['output_stack'] = median_stack
    med['minZ'] = minz
    med['maxZ'] = maxz
    med['output_directory'] = median_dir
    med['close_stack'] = close_stack
    with open(medianfile, 'w') as outfile:
         json.dump(med, outfile,indent=4)

def saveflatfieldjson(ff,flatfieldfile,render_host, owner, project, acq_stack,median_stack,flatfield_stack,flatfield_dir,sectnum,close_stack):
    ff['render']['host'] = render_host
    ff['render']['owner'] = owner
    ff['render']['project'] = project
    ff['input_stack'] = acq_stack
    ff['correction_stack'] = median_stack
    ff['output_stack'] = flatfield_stack
    ff['z_index'] = sectnum
    ff['output_directory'] = flatfield_dir
    ff['close_stack'] = close_stack
    with open(flatfieldfile, 'w') as outfile:
         json.dump(ff, outfile,indent=4)


def savedeconvjson(dd,deconvfile,owner, project, flatfield_stack,deconv_stack,deconv_dir,sectnum,psf_file, num_iter,bgrd_size,scale_factor):
    dd['render']['owner'] = owner
    dd['render']['project'] = project
    dd['input_stack'] = flatfield_stack
    dd['output_stack'] = deconv_stack
    dd['psf_file'] = psf_file
    dd['num_iter']=num_iter
    dd['bgrd_size'] = bgrd_size
    dd['z_index'] = sectnum
    dd['output_directory'] = deconv_dir
    dd['scale_factor'] = scale_factor
    dd['close_stack'] = close_stack
    dd['pool_size'] = 21
    with open(deconvfile, 'w') as outfile:
         json.dump(dd, outfile,indent=4)

def savestitchingjson(sti,stitchingfile,owner, project, flatfield_stack,stitched_stack,sectnum):
    sti['owner'] = owner
    sti['project'] = project
    sti['stack'] = flatfield_stack
    sti['outputStack'] = stitched_stack
    sti['section'] = sectnum
    with open(stitchingfile, 'w') as outfile:
         json.dump(sti, outfile,indent=4)

def saveapplystitchingjson(appsti,applystitchingfile,owner, project, flatfield_stack,stitched_stack,stitched_dapi_stack):
    appsti['render']['owner'] = owner
    appsti['render']['project'] = project
    appsti['alignedStack'] = stitched_dapi_stack
    appsti['outputStack'] = stitched_stack
    appsti['inputStack'] = flatfield_stack

    with open(applystitchingfile, 'w') as outfile:
         json.dump(appsti, outfile,indent=4)

if __name__ == "__main__":

    owner       = "ATExplorer"
    render_host = "W10DTMJ03EG6Z.corp.alleninstitute.org"
    dirname="F:\\data\\M33\\raw\\data\\Ribbon0004\\session01"

    projectdirectory = dirname.strip()
    project = parseprojectroot(projectdirectory)
    channels = get_channel_names(projectdirectory)
    [projectroot, ribbon,session] = parse_project_directory(projectdirectory)

    print  ("Projectroot: " + projectroot)

    flatfield_dirname =  "%s/../../../../processed/Flatfield_Test" %dirname.strip('\n')
    print ("Processing session folder: " + dirname)
    print ("flatfield_dirname: " + flatfield_dirname)

    templatesFolder = "p:\\atExplorer\\atPipeline\\templates"
    mediantemplate    = os.path.join(templatesFolder, "median.json")
    flatfieldtemplate = os.path.join(templatesFolder,"flatfield.json")
    deconvtemplate    = os.path.join(templatesFolder,"deconvolution.json")
    stitchingtemplate = os.path.join(templatesFolder,"stitching.json")

    firstsection = 0
    lastsection = 10
    num_iter = 20

    if not os.path.exists(flatfield_dirname):
        os.makedirs(flatfield_dirname)

    for sectnum in range(firstsection, lastsection + 1):
        close_stack = False

        z = (ribbon * 100) + sectnum
        if sectnum == lastsection:
            close_stack = True

        statetablefile = projectroot + "scripts/statetable_ribbon_%d_session_%d_section_%d"%(ribbon,session,sectnum)
        print ("Project Root: " + projectroot)
        print ("StateTable File: " + statetablefile)

        medianfile       = "%s/logs/median_%s_%s_%s_%d.json"   %(projectroot,project,ribbon,session,sectnum)
        flatfieldfile    = "%s/logs/flatfield_%s_%s_%s_%d.json"%(projectroot,project,ribbon,session,sectnum)
        deconvfile       = "%s/logs/deconv_%s_%s_%s_%d.json"   %(projectroot,project,ribbon,session,sectnum)
        stitchingfile    = "%s/logs/stitching_%s_%s_%s_%d.json"%(projectroot,project,ribbon,session,sectnum)

        #stacks
        acq_stack        = "ACQ_Session%d"%(int(session))
        median_stack     = "MED_Session%d"%(int(session))
        flatfield_stack  = "FF_Session%d"%(int(session))
        deconv_stack     = "DCV_FF_Session%d"%(int(session))
        stitched_stack   = "STI_FF_Session%d"%(int(session))

        #directories
        median_dir       = toPosixPath("%s/processed/Medians_Test/"%projectroot, "/mnt")
        flatfield_dir    = toPosixPath("%s/processed/Flatfield_Test/"%projectroot, "/mnt")
        deconv_dir       = toPosixPath("%s/processed/Deconv/"%projectroot, "/mnt")

        with open(stitchingtemplate) as json_data:
             sti = json.load(json_data)

        #Create 'logs' folder
        logsFolder=os.path.join(projectroot, "logs")
        if os.path.isdir(logsFolder) == False:
           os.mkdir(logsFolder)

        savestitchingjson(sti,stitchingfile,owner, project, flatfield_stack,stitched_stack,z)

        if close_stack:
            with open(mediantemplate) as json_data:
                 med = json.load(json_data)
            savemedianjson(med,medianfile,render_host, owner, project,acq_stack,median_stack, median_dir, ribbon*100+firstsection, ribbon*100+lastsection, close_stack)

            #Run =============
            cmd1 = "docker exec renderapps_multchan python -m rendermodules.intensity_correction.calculate_multiplicative_correction"
            cmd1 = cmd1 + " --render.port 80"
            cmd1 = cmd1 + " --input_json %s"%(toPosixPath(medianfile, "/mnt"))
            print ("Running: " + cmd1)

            p = subprocess.Popen(cmd1, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in p.stdout.readlines():
                print (line)

            for sectnum in range(firstsection,lastsection + 1):
                with open(flatfieldtemplate) as json_data:
                     ff = json.load(json_data)

                ff_z = (ribbon * 100) + sectnum
                saveflatfieldjson(ff,flatfieldfile,render_host, owner, project, acq_stack,median_stack,flatfield_stack,flatfield_dir,ff_z,close_stack)
                print (ff_z)
                cmd2 = "docker exec renderapps_multchan python -m rendermodules.intensity_correction.apply_multiplicative_correction"
                cmd2 = cmd2 + " --render.port 80"
                cmd2 = cmd2 + " --input_json %s"%(toPosixPath(flatfieldfile, "/mnt"))
                p = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    print (line)

##        cmd4 = "java -cp /pipeline/sharmi/at_modules/allen/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC --input_json %s"%stitchingfile
##        f.write(cmd4 + "\n")



