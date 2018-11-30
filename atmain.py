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
import drop_stitching_mistakes

import timeit

if __name__ == '__main__':
    timeStart = timeit.default_timer()
    p = atutils.ATDataIni('ATData_params.ini')

    for sessionFolder in p.sessionFolders:
        #Start with the creation of state table files
        #print("Creating statetables for session: " + sessionFolder)
        #create_state_tables.run(p, sessionFolder)

        #Create Renderstacks (multi) for the raw data
        #print("Creating ACQ Stacks for session: " + sessionFolder)
        #create_rawdata_render_multi_stacks.run(p, sessionFolder)

        #Calculate median files
        #print("Calculating Median Files for session: " + sessionFolder)
        #create_median_files.run(p, sessionFolder)

        #Creating Flatfiled corrected data
        #print("Creating FlatField corrected data for session: " + sessionFolder)
        #create_flatfield_corrected_data.run(p, sessionFolder)

        #Stitch the data
        #print("Stitching data for session: " + sessionFolder)
        #create_stitched_sections.run(p, sessionFolder)

        #Drop stitching mistakes
        drop_stitching_mistakes.run(p, sessionFolder)


    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")