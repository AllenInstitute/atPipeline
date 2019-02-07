import os
import source.atutils as u
from source import *
import timeit

if __name__ == '__main__':
    timeStart = timeit.default_timer()
    p = u.ATDataIni('ATData.ini')

    for sessionFolder in p.sessionFolders:
        #Start with the creation of state table files
##        if p.createStateTables == True:
##           print("Creating statetables for session: " + sessionFolder)
##           create_state_tables.run(p, sessionFolder)
##
##        #Create Renderstacks (multi) for the raw data
##        if p.createRawDataRenderMultiStacks == True:
##           print("Creating Raw Data Stacks for session: " + sessionFolder)
##           create_rawdata_render_multi_stacks.run(p, sessionFolder)
##
##        #Calculate median files
##        if p.createMedianFiles == True:
##           print("Calculating Median Files for session: " + sessionFolder)
##           create_median_files.run(p, sessionFolder)
##
##        #Creating Flatfiled corrected data
##        if p.createFlatFieldCorrectedData == True:
##           print("Creating FlatField corrected data for session: " + sessionFolder)
##           create_flatfield_corrected_data.run(p, sessionFolder)
##
##        #Stitch the data
##        if p.createStitchedSections == True:
##           print("Stitching data for session: " + sessionFolder)
##           create_stitched_sections.run(p, sessionFolder)
##
##        #Drop stitching mistakes
##        if p.dropStitchingMistakes == True:
##           print("Stitching data for session: " + sessionFolder)
##           drop_stitching_mistakes.run(p, sessionFolder)
##
##        #Create lowres stacks
##        if p.createLowResStacks == True:
##           print("Create Lowres Stacks for Session: " + sessionFolder)
##           create_lowres_stacks.run(p, sessionFolder)
##
##        #Create TilePairs
##        if p.createLRTilePairs == True:
##           print("Create TilePairs for Session:" + sessionFolder)
##           create_LR_tilepairs.run(p, sessionFolder)
##
##        #Create PointMatches
##        if p.createLRPointMatches == True:
##           print("Create Pointmatches: "+ sessionFolder)
##           create_LR_pointmatches.run(p, sessionFolder)
##
##        #Rough Align
##        if p.createRoughAlignedStacks == True:
##           print("Create Rough Aligned Stacks: "+ sessionFolder)
##           create_rough_aligned_stacks.run(p, sessionFolder)
##
##        #Apply lowres transforms to highres stacks
##        if p.applyLowResToHighRes == True:
##           print("Applying low resolution alignment transforms to high resoloution stack: "+ sessionFolder)
##           apply_lowres_to_highres.run(p, sessionFolder)
##
##        #Consolidate transforms
##        if p.consolidateRoughAlignedStackTransforms == True:
##           print("Consolidating Rough Aligned RenderTransforms: "+ sessionFolder)
##           consolidate_stack_transforms.run(p, sessionFolder)

        #Create 2D point matches
        if p.create2DPointMatches == True:
           print("Create 2D pointmatches (tile on tile) for session: "+ sessionFolder)
           create_2D_pointmatches.run(p, sessionFolder)

       #Create HR tile pairs
        if p.createHRTilePairs == True:
           print("Create HighResolution tile pairs.")
           create_HR_tilepairs.run(p, sessionFolder)

        #Create HR pointmatches
        if p.createHRPointMatches == True:
           print("Create HighResolution point matches.")
           create_HR_pointmatches.run(p, sessionFolder)

        #Create FineAligned stack
        if p.createFineAlignedStacks == True:
           print("Create FineAligned Stacks.")
           create_fine_aligned_stacks.run(p, sessionFolder)


    timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
    print("Elapsed time: " + timeDuration + " minutes")