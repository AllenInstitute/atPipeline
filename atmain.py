import os
import source.atutils as u
from source import *
import timeit

if __name__ == '__main__':
    timeStart = timeit.default_timer()
    p = u.ATDataIni('ATData.ini')

    for sessionFolder in p.sessionFolders:
        #Start with the creation of state table files
        if p.createStateTables == True:
           print("Creating statetables for session: " + sessionFolder)
           create_state_tables.run(p, sessionFolder)

        #Create Renderstacks (multi) for the raw data
        if p.createRawDataRenderMultiStacks == True:
           print("Creating ACQ Stacks for session: " + sessionFolder)
           create_rawdata_render_multi_stacks.run(p, sessionFolder)

        #Calculate median files
        if p.createMedianFiles == True:
           print("Calculating Median Files for session: " + sessionFolder)
           create_median_files.run(p, sessionFolder)

        #Creating Flatfiled corrected data
        if p.createFlatFieldCorrectedData == True:
           print("Creating FlatField corrected data for session: " + sessionFolder)
           create_flatfield_corrected_data.run(p, sessionFolder)

        #Stitch the data
        if p.createStitchedSections == True:
           print("Stitching data for session: " + sessionFolder)
           create_stitched_sections.run(p, sessionFolder)

        #Drop stitching mistakes
        if p.dropStitchingMistakes == True:
           print("Stitching data for session: " + sessionFolder)
           drop_stitching_mistakes.run(p, sessionFolder)

        #Create lowres stacks
        if p.createLowResStacks == True:
           print("Create Lowres Stacks for Session: "+ sessionFolder)
           create_lowres_stacks.run(p, sessionFolder)

        #Create PointMatches
        if p.createPointMatches == True:
           print("Create Pointmatches: "+ sessionFolder)
           create_pointmatches.run(p, sessionFolder)

    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")