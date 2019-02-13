import atutils as u
import os

##def parse_project_directory(line):
##	proj = line.split("raw")
##	projectdirectory = proj[0]
##
##	tok = line.split("/")
##	ribbondir = tok[len(tok)-2]
##	sessiondir = tok[len(tok)-1]
##	ribbon = int(ribbondir[6:])
##	session = int(sessiondir[7:])
##
##	return [projectdirectory, ribbon, session]
##
##def get_channel_names(directory):
##	#return os.listdir(directory)
##	directory_list = list()
##	for root, dirs, files in os.walk(directory, topdown=False):
##	   for name in dirs:
##  		    directory_list.append(os.path.join(root, name))
##	return dirs
##
##def parseprojectroot(projectdirectory):
##    #print projectdirectory
##    tok = projectdirectory.split("/")
##    dataind = tok.index('data')
##    return tok[dataind+1]

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


def run(p, sessionFolder):
    owner = "multchan"
    registrationtemplate = "template/registration.json"

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    ##This file seem to contain session folders, e.g.
    ##/nas5/data/M367240B_SSTPV_LaminB1_smallvol/raw/data/Ribbon0011/session01
##    with open("/pipeline/forcron/registration/confirm_data2process2") as f:
##        alldirnames = f.readlines()


    channels = u.getChannelNamesInSessionFolder(sessionFolder)

    z = ribbon*100+sectnum

    #create file that consists of celery job commands
    filename = "log/runme_sect_%s_%d_%d_%s.sh"%(project, ribbon,session,sectnum)
    f = open(filename,'w')

    registrationfile = "%s/log/registration_%s_%s_%s_%d.json"%(curdir,project,ribbon,session,sectnum)

    #stacks
    reference_stack     = "STI_FF_Session1"
    stitched_stack      = "STI_FF_Session%d"%(int(session))
    registered_stack    = "1_REG_FF_S0%d"%(int(session))

    #directories
    flatfield_dir = "%s/processed/Flatfield/"%projectroot
    deconv_dir = "%s/processed/Deconv/"%projectroot

    #create files
    with open(registrationtemplate) as json_data:
   	    reg = json.load(json_data)

    saveregistrationjson(reg,registrationfile,owner,project,stitched_stack,reference_stack,registered_stack,z)

    #run
    if session > 1:
   	    print ("found DAPI file")
   	    cmd5 = "java -cp /pipeline/sharmi/Sharmi_tools/atmodules-branches/fix_bug_phasecorr/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.Register --input_json %s"%registrationfile
   	    os.system(cmd5)
    else:
    	cmd5 = ""


    f.close()

if __name__ == "__main__":
    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
