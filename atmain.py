#------------------------------------------------
# Name:        atMain
# Purpose:     Run multiple AT processing scripts
#------------------------------------------------

import os
import atutils
import create_state_tables
import create_rawdata_render_multi_stacks
import create_median_files
import create_flatfield_corrected_data
import timeit

if __name__ == '__main__':
    timeStart = timeit.default_timer()

    #What data to process??
    dataRootFolder = "F:\\data\\M33"
    ribbons = ["Ribbon0004"]
    sessions = ["Session01",
                "Session02",
                "Session03"
                ]

    sessionFolders = []
    for session in sessions:
        sessionFolders.append(os.path.join(dataRootFolder, "raw", "data", ribbons[0], session))
    startSection = 1
    endSection   = 5

    #Process with what?
    dockerContainer = "renderapps_multchan"

    #Render info
    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolders[0])
    renderProject  = atutils.RenderProject("ATExplorer", "W10DTMJ03EG6Z.corp.alleninstitute.org", renderProjectName)
    for sessionFolder in sessionFolders:
        #Start with the creation of state table files
        create_state_tables.run(sessionFolder, startSection, endSection, dockerContainer)

        #Create Renderstacks (multi) for the raw data
        create_rawdata_render_multi_stacks.run(sessionFolder, startSection, endSection, dockerContainer, renderProject)

        #Calculate median files
        create_median_files.run(startSection, endSection, sessionFolder, dockerContainer, renderProject)

        #Calculate median files
        create_flatfield_corrected_data.run(startSection, endSection, sessionFolder, dockerContainer, renderProject)

    timeEnd = timeit.default_timer()
    print("Elapsed time in apply_medians: " + str(timeEnd - timeStart))
