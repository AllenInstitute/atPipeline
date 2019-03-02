import atutils as u
import os
import json

def run(p, sessionFolder):
    owner = "multchan"
    registrationtemplate = "template/registration.json"

    print ("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.renderHost, p.projectName)
    jsonOutputFolder  = os.path.join(p.dataOutputFolder, "registration")

    # Make sure that the output folder exist
    if os.path.isdir(jsonOutputFolder) == False:
        os.mkdir(jsonOutputFolder)

    #stacks
    reference_stack     = "S1_Stitched"
    stitched_stack      = "S%d_Stitched"%(int(session))
    outputStack         = "S%d_Registered"%(int(session))

    #Loop over sections?
    sectnum = 1

    #This is the registration input (json) file
    inputJSON = os.path.join(jsonOutputFolder, "registration_%s_%s_%d.json"%(ribbon, session, sectnum))

    #create input file for registration
    with open(u.registrationTemplate) as json_data:
        t = json.load(json_data)

    z = ribbon*100+sectnum
    u.saveRegistrationJSON(t, inputJSON, p.renderHost, renderProject.owner, renderProject.name, stitched_stack, reference_stack, outputStack, z)

    #run
    if session > 1:
        cmd = "java -cp /pipeline/sharmi/Sharmi_tools/atmodules-branches/fix_bug_phasecorr/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar"
        cmd = cmd + " at_modules.Register"
        cmd = cmd + " --input_json %s"%inputJSON

    #Run =============
    print ("Running: " + cmd.replace('--', '\n--'))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    for line in proc.stdout.readlines():
        print (line)

    proc.wait()
    if proc.returncode:
        print ("PROC_RETURN_CODE:" + str(proc.returncode))
        raise Exception(os.path.basename(__file__) + " threw an Exception")

if __name__ == "__main__":
    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
