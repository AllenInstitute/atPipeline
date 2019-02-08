import paramiko
import os
import time
import json
import sys
sys.path.insert(0,'/pipeline/sharmi/allen_SB_code/celery/')
from celery import Celery
from tasks import run_celerycommand

def parse_project_directory(line):

	proj = line.split("raw")
	projectdirectory = proj[0]

	tok = line.split("/")
	ribbondir = tok[len(tok)-2]
	sessiondir = tok[len(tok)-1]
	ribbon = int(ribbondir[6:])
	session = int(sessiondir[7:])

	return [projectdirectory, ribbon, session]


def get_channel_names(directory):
	#return os.listdir(directory)
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
        #print projectdirectory
        tok = projectdirectory.split("/")
        dataind = tok.index('data')
        return tok[dataind+1]

def parsefile(fname):

        with open(fname) as f:
                content = f.readlines()

        if len(content)>1:
                print "File is corrupted..."
        else:
                #parse line

                fullline = content[0]
                fullinetok = fullline.split(",")
                section = int(fullinetok[1])
                owner = str(fullinetok[2])
                #owner = "TESTEXPERIMENT"

                line = fullinetok[0]

                proj = line.split("raw")
                projectdirectory = proj[0]

                tok = line.split("/")
                ribbondir = tok[len(tok)-2]
                sessiondir = tok[len(tok)-1]
                ribbon = int(ribbondir[6:])
                session = int(sessiondir[7:])

                return [projectdirectory, ribbon, session, section, owner,fullline]


def saveapplystitchingjson(appsti,applystitchingfile,owner, project, flatfield_stack,stitched_stack,stitched_dapi_stack):
	appsti['render']['owner'] = owner
        appsti['render']['project'] = project
        appsti['alignedStack'] = stitched_dapi_stack
        appsti['outputStack'] = stitched_stack
        appsti['inputStack'] = flatfield_stack

        with open(applystitchingfile, 'w') as outfile:
                json.dump(appsti, outfile,indent=4)


def saveregistrationjson(reg,registrationfile,owner,project,stack,referenceStack,outputStack,section):
	reg['owner'] = owner
	reg['project'] = project
	reg['stack'] = stack
	reg['referencestack']=referenceStack
	reg['outputStack'] = outputStack
	reg['section'] = section
	reg['steps'] =  5
	reg['maxEpsilon'] = 2
	reg['minOctaveSize'] = 1000
	reg['maxOctaveSize'] = 2000
	reg['initialSigma'] = 2.5
	reg['percentSaturated'] = 0.9
	reg['contrastEnhance'] = False

	with open(registrationfile,'w') as outfile:
		json.dump(reg,outfile,indent=4)
	


if __name__ == "__main__":

	owner = "multchan"
	mediantemplate = "template/median.json"
	flatfieldtemplate = "template/flatfield.json"
	deconvtemplate = "template/deconvolution.json"
	stitchingtemplate = "template/stitching.json"
	registrationtemplate = "template/registration.json"
	firstsection = 0
	lastsection = 5
	num_iter = 20
	bgrd_size = 50

	curdir = os.getcwd()
	
	for i in range (0,1):

                with open("/pipeline/forcron/registration/confirm_data2process2") as f:
                        alldirnames = f.readlines()

                for dirname in alldirnames:
                        for sectnum in range(firstsection,lastsection+1):
				close_stack = False

				if sectnum==lastsection:
					close_stack = True
				
				projectdirectory = dirname.strip()
				project = parseprojectroot(projectdirectory)
				channels = get_channel_names(projectdirectory)
				[projectroot, ribbon,session] = parse_project_directory(projectdirectory)
				z = ribbon*100+sectnum


				#create file that consists of celery job commands
				filename = "log/runme_sect_%s_%d_%d_%s.sh"%(project, ribbon,session,sectnum)
				f = open(filename,'w')
				registrationfile = "%s/log/registration_%s_%s_%s_%d.json"%(curdir,project,ribbon,session,sectnum)


				#stacks
				stitched_stack = "STI_FF_Session%d"%(int(session))
				registered_stack = "1_REG_FF_S0%d"%(int(session))
				reference_stack = "STI_FF_Session1"

				#directories
				flatfield_dir = "%s/processed/Flatfield/"%projectroot
				deconv_dir = "%s/processed/Deconv/"%projectroot


				#create files
				with open(registrationtemplate) as json_data:
					reg = json.load(json_data)
				saveregistrationjson(reg,registrationfile,owner,project,stitched_stack,reference_stack,registered_stack,z)


				#run

				if session > 1:
					print "found DAPI file"
					cmd5 = "java -cp /pipeline/sharmi/Sharmi_tools/atmodules-branches/fix_bug_phasecorr/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.Register --input_json %s"%registrationfile
					os.system(cmd5)
				else:
					cmd5 = ""


				f.close()
				rcmd = "sh %s"%filename
				print rcmd
				#os.system(rcmd)
				#result = run_celerycommand.apply_async(args=[rcmd,os.getcwd()])
				#time.sleep(10)
