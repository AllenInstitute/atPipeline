#------------------------------------------------
# Name:        atMain
# Purpose:     Run multiple AT processing scripts
#------------------------------------------------

import os
import atutils
import create_state_tables
import create_rawdata_render_multi_stacks


if __name__ == '__main__':

    #What data to process??
    dataRootFolder = "F:\\data\\M33"
    ribbons = ["Ribbon0004"]
    sessions = [#"Session01",
                "Session02",
                'Session03']

    sessionFolders = []
    for session in sessions:
        sessionFolders.append(os.path.join(dataRootFolder, "raw", "data", ribbons[0], session))
    startSection = 1
    endSection = 24

    #Process with what?
    dockerContainer = "renderapps_multchan"

    #Start with the creation of state table files
    #create state tables function takes a sessionFolder and start, end section and a dockerContainer as parameters
    for sessionFolder in sessionFolders:
        create_state_tables.run(sessionFolder, startSection, endSection, dockerContainer)

    #Render info
    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolders[0])
    renderProject  = atutils.RenderProject("ATExplorer", "W10DTMJ03EG6Z.corp.alleninstitute.org", renderProjectName)

    #Create Renderstacks (multi) for the raw data
    for sessionFolder in sessionFolders:
        create_rawdata_render_multi_stacks.run(sessionFolder, startSection, endSection, dockerContainer, renderProject)
