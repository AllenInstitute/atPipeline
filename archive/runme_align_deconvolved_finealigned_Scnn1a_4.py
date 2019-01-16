import os
import json
import time

#Params to change
#render params
host = "ibs-forrestc-ux1"
client_scripts = "/var/www/render/render-ws-java-client/src/main/scripts"
port = 8080
memGB = "5G"
loglevel = "INFO"

#project params
owner = "Forrest"
project = "M246930_Scnn1a_4"
firstribbon = 1
lastribbon = 3

#stack params
acquisition_Stack = "Acquisition_1_DAPI_1"
stitched_dapi_Stack = "Stitched_1_DAPI_1_flatfield"
dropped_dapi_Stack = "Stitched_1_DAPI_1_dropped"
channelnames = ["1_DAPI_1", "1_Gephyrin", "1_PSD95", "1_VGlut1"]

#directories
rootdir = "/nas/data"
project_root_dir = "%s/%s"%(rootdir,project)
project_root_dir = "/nas/data/M246930_Scnn1a_4/processed_old/focusmappeddata"

pool_size = 20

#other
distance = 100
edge_threshold = 1873
scale = 0.05
deltaZ = 10
minZ = 0


#directories
pm_script_dir = "/pipeline/sharmi/Sharmi_tools/render-branches/from_fcollman/render/render-ws-spark-client/src/main/scripts"
pm_scrpt_dir = "/allen/aibs/pipeline/image_processing/volume_assembly/render-jars/production/render-ws-spark-client-standalone.jar"
dropped_dir = "%s/processed/dropped"%project_root_dir
downsample_dir = "%s/processed/Low_res"%project_root_dir
roughalign_ts_dir = "%s/processed/RoughAlign_%d_to_%d"%(project_root_dir,firstribbon,lastribbon)
numsectionsfile = "%s/numsections"%downsample_dir

#stacks
lowres_stack = "Stitched_DAPI_1_Lowres"
lowres_roughalign_stack = "Stitched_DAPI_1_Lowres_RoughAlign_1"
lowres_pm_collection = "%s_DAPI_1_lowres_round1_TESTING"%(project)
highres_pm_collection = "%s_DAPI_1_highres_TEST"%(project)
roughaligned_stack = "%s_RoughAligned"%lowres_stack

#docker string
d_str = "docker exec renderapps_develop "
render_str = "--render.host %s --render.client_scripts %s --render.port %d --render.memGB %s --log_level %s "%(host,client_scripts,port,memGB,loglevel)
project_str = "--render.project %s --render.owner %s" %(project, owner)
dropstitchmistakes_str = "--prestitchedStack %s --poststitchedStack %s --outputStack %s --jsonDirectory %s --edge_threshold %d --pool_size %d --distance_threshold %d"%(acquisition_Stack,stitched_dapi_Stack,dropped_dapi_Stack,dropped_dir,edge_threshold,pool_size,distance)
downsample_str = "--input_stack %s --output_stack %s --image_directory %s --pool_size %d --scale %f --minZ %d --maxZ %d --numsectionsfile %s"%(dropped_dapi_Stack,lowres_stack,downsample_dir,pool_size,scale,firstribbon*100, ((lastribbon+1)*100 - 1), numsectionsfile)
applych_str = "--prealigned_stack %s --lowres_stack %s --pool_size %d --scale %f"%(dropped_dapi_Stack, roughaligned_stack,  pool_size, scale)

#calculate the number of sections
f = open(numsectionsfile)
numberofsections = int(f.readline())
print (numberofsections)


#Extract point matches
##cmd_pointmatches = "sh %s/run_tilepair_and_sift.sh --owner %s --project %s --stack %s --minZ 0 --maxZ %d --collection %s --deltaZ %d"%(pm_script_dir,owner,project,lowres_stack, 2090, lowres_pm_collection,deltaZ)
cmd_pointmatches = "sh %s/run_tilepair_and_sift.sh --owner %s --project %s --stack %s --minZ 0 --maxZ %d --collection %s --deltaZ %d"%(pm_script_dir,owner,project,lowres_stack,numberofsections,lowres_pm_collection,deltaZ)
cmd_pointmatches = cmd_pointmatches + " --renderScale 1.0 --SIFTminScale 0.5 --SIFTmaxScale 1.0 --SIFTsteps 7"
print (cmd_pointmatches)

for ch in channelnames:

    if ch == "1_DAPI_1":
        #apply
        cmd_ch = "%s python -m renderapps.rough_align.ApplyLowRes2HighRes %s %s %s "%(d_str,render_str,project_str,applych_str)
        cmd_ch = cmd_ch + "--input_stack Stitched_%s_dropped --output_stack Rough_Aligned_%s --tilespec_directory %s "%(ch,ch,roughalign_ts_dir)
        cmd_ch = cmd_ch + "--minZ %d --maxZ %d "%(firstribbon*100, (lastribbon+1) * 100)
        print (cmd_ch)
        #os.system(cmd_ch)
    else:
	     print ("Do Nothing")


