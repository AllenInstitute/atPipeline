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
import create_stitched_sections
import timeit
import configparser
import ast

if __name__ == '__main__':
    timeStart = timeit.default_timer()
    config = configparser.ConfigParser()

    config.read('Tottes.ini')
    ini = config['GENERAL']

    renderProjectOwner = ini['RENDER_PROJECT_OWNER']

    #What data to process??
    prefixPath = ini['PREFIX_PATH']
    dataRootFolder = ini['DATA_ROOT_FOLDER']
    dataRootFolder = os.path.join(prefixPath, dataRootFolder)

    #Process with what?
    rpaContainer = ini['RENDER_PYTHON_APPS_CONTAINER']
    atmContainer = ini['AT_MODULES_CONTAINER']
    renderHost = ini['RENDER_HOST']

    ribbons = ast.literal_eval(ini['RIBBONS'])
    sessions = ast.literal_eval(ini['SESSIONS'])

    sessionFolders = []

    for session in sessions:
        sessionFolders.append(os.path.join(dataRootFolder, "raw", "data", ribbons[0], session))

    startSection = int(ini['START_SECTION'])
    endSection   = int(ini['END_SECTION'])

        #Render info
    renderProjectName = atutils.getProjectNameFromSessionFolder(sessionFolders[0])
    renderProject  = atutils.RenderProject(renderProjectOwner, renderHost, renderProjectName)
    for sessionFolder in sessionFolders:
        print("Processing Session: " + sessionFolder)

        #Start with the creation of state table files
        print("Creating statetables for session: " + sessionFolder)
        create_state_tables.run(sessionFolder, startSection, endSection, rpaContainer, prefixPath)

        #Create Renderstacks (multi) for the raw data
        print("Creating ACQ Stacks for session: " + sessionFolder)
        create_rawdata_render_multi_stacks.run(sessionFolder, startSection, endSection, rpaContainer, renderProject, prefixPath)

        #Calculate median files
        print("Calculating Median Files for session: " + sessionFolder)
        create_median_files.run(startSection, endSection, sessionFolder, rpaContainer, renderProject, prefixPath)

        #Creating Flatfiled corrected data
        print("Creating FlatField corrected data for session: " + sessionFolder)
        create_flatfield_corrected_data.run(startSection, endSection, sessionFolder, rpaContainer, renderProject, prefixPath)

        #Stitch the data
        print("Stitching data for session: " + sessionFolder)
        create_stitched_sections.run(startSection, endSection, sessionFolder, atmContainer, renderProject, prefixPath)

    timeEnd = timeit.default_timer()
    print("Elapsed time: " + str((timeEnd - timeStart)/60.0) + " minutes" )
