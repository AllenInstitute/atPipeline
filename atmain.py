#------------------------------------------------
# Name:        atMain
# Purpose:     Run multiple at processing scripts
#------------------------------------------------

import os
import create_state_tables


if __name__ == '__main__':
    #What data to process??

    dataRootFolder = "F:\\data\\M33"
    ribbons = ["Ribbon0004"]
    sessions = ["Session01", "Session02", 'Session03']

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
