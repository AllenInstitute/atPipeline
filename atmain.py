import os
import logging
import timeit
import pathlib
import docker
from source import *
import source.atutils as u

def main():
    logger = logging.getLogger("atPipeline")
    logger.setLevel(logging.DEBUG)
    timeStart = timeit.default_timer()

    try:
        #Get processing parameters
        parameters =u.validateATCoreInputAndOutput()

        dockerClient = docker.from_env()
        atcore = dockerClient.containers.get("atcore")
        render = dockerClient.containers.get("tk_render")

        if render.status != "running":
            raise ValueError("The Render docker container is not running!")

        if atcore.status != "running":
            raise ValueError("The atcore docker container is not running!")

        for sessionFolder in parameters.sessionFolders:
            #Start with the creation of state table files
            if parameters.createStateTables == True:
               print("Creating statetables for session: " + sessionFolder)
               create_state_tables.run(parameters, sessionFolder)

            #Create Renderstacks (multi) for the raw data
            if parameters.createRawDataRenderMultiStacks == True:
               print("Creating Raw Data Stacks for session: " + sessionFolder)
               create_rawdata_render_multi_stacks.run(parameters, sessionFolder)

            #Calculate median files
            if parameters.createMedianFiles == True:
               print("Calculating Median Files for session: " + sessionFolder)
               create_median_files.run(parameters, sessionFolder)

            #Creating Flatfiled corrected data
            if parameters.createFlatFieldCorrectedData == True:
               print("Creating FlatField corrected data for session: " + sessionFolder)
               create_flatfield_corrected_data.run(parameters, sessionFolder)

            #Stitch the data
            if parameters.createStitchedSections == True:
               print("Stitching data for session: " + sessionFolder)
               create_stitched_sections.run(parameters, sessionFolder)

            #Drop stitching mistakes
            if parameters.dropStitchingMistakes == True:
               print("Stitching data for session: " + sessionFolder)
               drop_stitching_mistakes.run(parameters, sessionFolder)

            #Create lowres stacks
            if parameters.createLowResStacks == True:
               print("Create Lowres Stacks for Session: " + sessionFolder)
               create_lowres_stacks.run(parameters, sessionFolder)

            #Create TilePairs
            if parameters.createLRTilePairs == True:
               print("Create TilePairs for Session:" + sessionFolder)
               create_LR_tilepairs.run(parameters, sessionFolder)

            #Create PointMatches
            if parameters.createLRPointMatches == True:
               print("Create Pointmatches: "+ sessionFolder)
               create_LR_pointmatches.run(parameters, sessionFolder)

            #Rough Align
            if parameters.createRoughAlignedStacks == True:
               print("Create Rough Aligned Stacks: "+ sessionFolder)
               create_rough_aligned_stacks.run(parameters, sessionFolder)

            #Apply lowres transforms to highres stacks
            if parameters.applyLowResToHighRes == True:
               print("Applying low resolution alignment transforms to high resoloution stack: "+ sessionFolder)
               apply_lowres_to_highres.run(parameters, sessionFolder)

            #Consolidate transforms
            if parameters.consolidateRoughAlignedStackTransforms == True:
               print("Consolidating Rough Aligned RenderTransforms: "+ sessionFolder)
               consolidate_stack_transforms.run(parameters, sessionFolder)

            #Create 2D point matches
            if parameters.create2DPointMatches == True:
               print("Create 2D pointmatches (tile on tile) for session: "+ sessionFolder)
               create_2D_pointmatches.run(parameters, sessionFolder)

           #Create HR tile pairs
            if parameters.createHRTilePairs == True:
               print("Create HighResolution tile pairs.")
               create_HR_tilepairs.run(parameters, sessionFolder)

            #Create HR pointmatches
            if parameters.createHRPointMatches == True:
               print("Create HighResolution point matches.")
               create_HR_pointmatches.run(parameters, sessionFolder)

            #Create FineAligned stack
            if parameters.createFineAlignedStacks == True:
               print("Create FineAligned Stacks.")
               create_fine_aligned_stacks.run(parameters, sessionFolder)


        timeDuration = "{0:.2f}".format((timeit.default_timer() - timeStart)/60.0)
        print("Elapsed time: " + timeDuration + " minutes")

    except ValueError as error:
        print ("An error occured: " + str(error))


if __name__ == '__main__':
    main()
