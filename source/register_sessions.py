import atutils as u
import os
import json

def run(p : u.ATDataIni, sessionFolder):
    owner = "multchan"
    registrationtemplate = "template/registration.json"

    logger.info("Processing session folder: " + sessionFolder)
    [projectRoot, ribbon, session] = u.parse_session_folder(sessionFolder)

    renderProject     = u.RenderProject(p.renderProjectOwner, p.projectName, p.sys.renderHost)
    jsonOutputFolder  = os.path.join(projectRoot, p.dataOutputFolder, "registration")

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
    u.saveRegistrationJSON(t, inputJSON, p.renderHost, renderProject.owner, renderProject.projectName, stitched_stack, reference_stack, outputStack, z)

    #run
    if session > 1:
        cmd = "java -cp /pipeline/sharmi/Sharmi_tools/atmodules-branches/fix_bug_phasecorr/at_modules/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar"
        cmd = cmd + " at_modules.Register"
        cmd = cmd + " --input_json %s"%inputJSON

    #Run =============
    u.runPipelineStep(cmd, "create_state_tables")

if __name__ == "__main__":
    #This script need a valid INI file to be passed as an argument
    u.runAtCoreModule(run)
