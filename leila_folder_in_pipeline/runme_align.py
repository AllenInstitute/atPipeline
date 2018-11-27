import os
import json
import time

#Params to change
#render params
host = "ibs-forrestc-ux1"
client_scripts = "/var/www/render/render-ws-java-client/src/main/scripts"
port = 80
memGB = "5G"
loglevel = "INFO"

#project params
owner = "Antibody_testing_2018"
project = "M367240_B_SSTPV_Lamin_B1"
firstribbon = 5
lastribbon = 5
ribbon = 'R5'

#stack params
acquisition_Stack = "ACQ_S01_DAPI_1"
stitched_dapi_Stack = "STI_S01_DAPI_1"
dropped_dapi_Stack = "DRP_STI_S01_DAPI_1"
#channelnames = ["3_DAPI_3", "3_VGlut1", "3_GABA","3_Synapsin1"]
#channelnames = ["2_GABA", "2_Synapsin1", "2_SAP102_2", "2_DAPI_2"]
#channelnames = ["3_DAPI_3", "3_GABA","3_Synapsin" , "3_MBP"]
#channelnames = ["DAPI_1", "Synapsin1", "SST", "GABA"]
channelnames = ["DAPI_1", "LaminB1"]

#channelnames = ["3_DAPI_3"]

#directories
rootdir = "/nas5/data"
project_root_dir = "%s/%s"%(rootdir,project)


#test comments

#parallelizatgit filter-branch -f --index-filter "git rm -rf --cached --ignore-unmatch FOLDERNAME" -- --allion params
pool_size = 20

#other
distance = 100
edge_threshold = 1873
scale = 0.05
deltaZ = 10
minZ = 0
#maxZ = 173 #############need to make this obsolete

############derived params

#directories
#pm_script_dir = "/data/array_tomography/ForSharmi/sharmirender/render/render-ws-spark-client/src/main/scripts"
#pm_script_dir = "/pipeline/forrestrender/render-ws-spark-client/src/main/scripts"
pm_script_dir = "/pipeline/sharmi/Sharmi_tools/render-branches/from_fcollman/render/render-ws-spark-client/src/main/scripts"
dropped_dir = "%s/processed/dropped"%project_root_dir
downsample_dir = "%s/processed/Low_res"%project_root_dir
roughalign_ts_dir = "%s/processed/RA_%d_to_%d"%(project_root_dir,firstribbon,lastribbon)
numsectionsfile = "%s/numsections"%downsample_dir


#stacks
#lowres_stack = "Stitched_DAPI_1_Lowres_%d_to_%d"%(firstribbon,lastribbon)
lowres_stack = "LR_DRP_STI_S01_DAPI_1_%s"%(ribbon)
#lowres_stack = "Stitched_DAPI_1_Lowres_R4"
lowres_roughalign_stack = "RA_LR_DRP_STI_S01_DAPI_1_%s"%(ribbon)
#lowres_pm_collection = "%s_%d_to_%d_DAPI_1_lowres" %(project,firstribbon,lastribbon)
lowres_pm_collection = "%s_DAPI_Lowres_3D_%s"%(project,ribbon)
#lowres_pm_collection = "%s_DAPI_lowres_R4"%(project)
#lowres_pm_collection2 = "%s_DAPI_lowres_R5"%(project)
#highres_pm_collection = "%s_DAPI_1_highres_R2"%(project)
highres_pm_collection = "%s_DAPI_1_3D_%s"%(project,ribbon)
roughaligned_stack = "RA_%s"%lowres_stack

#docker string
d_str = "docker exec renderapps_develop "
render_str = "--render.host %s --render.client_scripts %s --render.port %d --render.memGB %s --log_level %s "%(host,client_scripts,port,memGB,loglevel)
project_str = "--render.project %s --render.owner %s" %(project, owner)
dropstitchmistakes_str = "--prestitchedStack %s --poststitchedStack %s --outputStack %s --jsonDirectory %s --edge_threshold %d --pool_size %d --distance_threshold %d"%(acquisition_Stack,stitched_dapi_Stack,dropped_dapi_Stack,dropped_dir,edge_threshold,pool_size,distance)
downsample_str = "--input_stack %s --output_stack %s --image_directory %s --pool_size %d --scale %f --minZ %d --maxZ %d --numsectionsfile %s"%(dropped_dapi_Stack,lowres_stack,downsample_dir,pool_size,scale,firstribbon*100, ((lastribbon+1)*100 - 1), numsectionsfile)
#downsample_str = "--input_stack %s --output_stack %s --image_directory %s --pool_size %d --scale %f --minZ %d --maxZ %d --numsectionsfile %s"%(dropped_dapi_Stack,lowres_stack,downsample_dir,pool_size,scale,200,210, numsectionsfile)
applych_str = "--prealigned_stack %s --lowres_stack %s --pool_size %d --scale %f"%(dropped_dapi_Stack, roughaligned_stack,  pool_size, scale)
#applych_str = "--prealigned_stack Stitched_1_DAPI_1 --lowres_stack %s --pool_size %d --scale %f"%(roughaligned_stack,  pool_size, scale)

#dropstitchmistakes_str = "--prestitchedStack %s --poststitchedStack %s --outputStack %s --jsonDirectory %s --edge_threshold %d --pool_size %d --distance_threshold %d"%("Acquisition_3_DAPI_3","Stitched_3_DAPI_3","Stitched_3_DAPI_3_dropped",dropped_dir,edge_threshold,pool_size,distance)

#drop stitching mistakestwoD_str = "--minZ %d --maxZ %d --delta %d --dataRoot %s --stack Stitched_DAPI_1 --matchCollection %s"%(minZ, maxZ, delta, rootdir, highres_pm_collection_2D)

cmd_drop = "%s python -m renderapps.stitching.detect_and_drop_stitching_mistakes %s %s %s"%(d_str,render_str, project_str, dropstitchmistakes_str)
print cmd_drop
#os.system(cmd_drop)
#exit(0)


#downsample
cmd_downsample = "%s python -m renderapps.materialize.make_downsample_image_stack %s %s %s"%(d_str,render_str,project_str,downsample_str)
print cmd_downsample
#for i in range(0,2):
#    os.system(cmd_downsample)
#due to pool size issue, it doesn't always finish in the first round two runs are usually enough. need to update code to deal with this bug
#exit(0)

#calculate the number of sections
f = open(numsectionsfile)
numberofsections = int(f.readline())
print numberofsections



#Extract point matches
##cmd_pointmatches = "sh %s/run_tilepair_and_sift.sh --owner %s --project %s --stack %s --minZ 0 --maxZ %d --collection %s --deltaZ %d"%(pm_script_dir,owner,project,lowres_stack, 2090, lowres_pm_collection,deltaZ)
cmd_pointmatches = "sh %s/run_tilepair_and_sift.sh --owner %s --project %s --stack %s --minZ 0 --maxZ %d --collection %s --deltaZ %d"%(pm_script_dir,owner,project,lowres_stack,numberofsections,lowres_pm_collection,deltaZ)
cmd_pointmatches = cmd_pointmatches + " --renderScale 1.0 --SIFTminScale 0.6 --SIFTmaxScale 1.0 --SIFTsteps 3"
print "############################## Cmd Pointmatches"
print cmd_pointmatches
#os.system(cmd_pointmatches)
#exit(0)

#time.sleep(600)

#Manual Step:
#Use ipython notebook at: ibs-forrestc-ux1:8888 -> old_notebooks -> create_pointmatches.ipynb to create matches in a collection called :
#S3_Run1_Master_DAPI_1_Manual

#Rough Align

#create_json
j = {
        "input_stack": "%s"%lowres_stack,
        "output_stack" : "%s"%roughaligned_stack,
        "pointmatch_collection" : "%s"%lowres_pm_collection,
        "pointmatch_collection_append1" : "%s"%lowres_pm_collection,
        "pointmatch_collection_append2": "%s"%lowres_pm_collection,
        "degree": 1,
        "nfirst": 0,
        "nlast": numberofsections,
        "host":"%s"%host,
        "client_scripts":"/pipeline/render/render-ws-java-client/src/main/scripts",
        "owner": "%s"%owner,
        "project" : "%s"%project
}





with open('/pipeline/forcron/runjson_master.json', 'w') as outfile:
    json.dump(j, outfile)

#run matlab
cmd_matlab = "sh /pipeline/EM_aligner/template_production_scripts/pipeline_scripts/run_roughalign_json.sh /pipeline/MATLAB/R2016b /pipeline/forcron/runjson_master.json"
print cmd_matlab
#os.system(cmd_matlab)
#exit(0)
#Apply to other channels

#fix rough ALIGNMENT
cmd_fix1 = "docker exec renderapps_develop python -m renderapps.TrakEM2.create_trakem2_subvolume_from_render"
cmd_fix2 = "docker exec renderapps_develop python -m renderapps.TrakEM2.reimport_trakem2_to_render"
print cmd_fix1
print cmd_fix2
#os.system(cmd_fix1)
#os.system(cmd_fix2)
#exit(0)

for ch in channelnames:

    if ch == "DAPI_1":
        #apply
        cmd_ch = "%s python -m renderapps.rough_align.ApplyLowRes2HighRes %s %s %s "%(d_str,render_str,project_str,applych_str)
        cmd_ch = cmd_ch + "--input_stack DRP_STI_S01_%s --output_stack RA00_STI_S01_%s_%s --tilespec_directory %s "%(ch,ch,ribbon,roughalign_ts_dir)
	cmd_ch = cmd_ch + "--minZ %d --maxZ %d "%(firstribbon*100, (lastribbon+1) * 100)
	print cmd_ch
        os.system(cmd_ch)
    else:
	print "Do Nothing"
exit(0)
for ch in channelnames:
    #if ch == "1_DAPI_1":
#	print "DAPI has been rough aligned"
 #   else:



	cmd_cons = "%s python -m renderapps.stack.consolidate_render_transforms %s %s "%(d_str,render_str,project_str)
	cmd_cons = cmd_cons + "--stack DCV_FF_%s --output_stack DCV_FF_%s_CONS --postfix CONS  "%(ch,ch)
	cmd_cons = cmd_cons + "--output_directory %s/processed/json_tilespecs_reg_cons --pool_size 20"%project_root_dir
	#print cmd_cons


	cmdappstitch = "docker exec renderapps_develop python -m renderapps.registration.apply_transforms_by_frame %s %s --cyclenumber 200 --alignedStack Stitched_1_DAPI_1_dropped --inputStack Deconvolved_%s --outputStack Stitched_deconv_%s_dropped --pool_size 20"%(render_str,project_str,ch,ch)
        cmd_ch = "%s python -m renderapps.rough_align.ApplyLowRes2HighRes %s %s %s "%(d_str,render_str,project_str,applych_str)
        cmd_ch = cmd_ch + "--input_stack STI_S01_%s --output_stack RA00_STI_S01_%s_%s --tilespec_directory %s_%s "%(ch,ch,ribbon,roughalign_ts_dir,ch)
        cmd_ch = cmd_ch + "--minZ %d --maxZ %d "%(firstribbon*100, (lastribbon+1) * 100)
        
	#for deconv stacks
	#need to created stitchedstacks
	#cmd_ch = "%s python -m renderapps.rough_align.ApplyLowRes2HighRes %s %s %s "%(d_str,render_str,project_str,applych_str)
        #cmd_ch = cmd_ch + "--input_stack Deconvolved_%s --output_stack Rough_Aligned_Deconv_%s "%(ch,ch)
        #cmd_ch = cmd_ch + "--minZ %d --maxZ %d "%(firstribbon*100, (lastribbon+1) * 100)
	
	#os.system(cmdappstitch)

	#print cmd_cons
	print cmd_ch
	
	#os.system(cmd_cons)
        #os.system(cmd_ch)
	

#exit(0)


##############FINE ALIGNMENT#################forre

#apply scale parameter
#cmd_sc = "%s python -m renderapps.stack.apply_global_affine_to_stack %s %s "%(d_str,render_str,project_str)
#cmd_sc = cmd_sc + "--input_stack Rough_Aligned_1_DAPI_1 --output_stack Rough_Aligned_DAPI_1_fullscale "
#cmd_sc = cmd_sc + "--M00 20.0 --M11 20.0 "
#print cmd_sc
#os.system(cmd_sc)
#exit(0)

#consolidate
cmd_cons = "%s python -m renderapps.stack.consolidate_render_transforms %s %s "%(d_str,render_str,project_str)
cmd_cons = cmd_cons + "--stack RA00_STI_S01_DAPI_1_R5 --output_stack CONS_RA00_STI_S01_DAPI_1_R5 --postfix CONS  "
cmd_cons = cmd_cons + "--output_directory %s/processed/json_tilespecs_consolidation_master --pool_size 20"%project_root_dir
print cmd_cons
os.system(cmd_cons)
exit(0)

#2D point matches
delta = 150
minZ = 0
maxZ = 5
#maxZ = numberofsections
pm2dstack = "Rough_Aligned_1_DAPI_1_R0"
highres_pm_collection_2D = "%s_DAPI_1_highres_2D_R0"%(project)

twoD_str = "--minZ %d --maxZ %d --delta %d --dataRoot %s --stack %s --matchCollection %s"%(minZ, maxZ, delta, rootdir, pm2dstack, highres_pm_collection_2D)
cmd_2D = "%s python -m renderapps.stitching.create_montage_pointmatches_in_place %s %s %s"%(d_str, render_str,project_str, twoD_str)
print cmd_2D
#os.system(cmd_2D)
#exit(0)

#3D point matches
#json_file = "/nas4/data/%s/processed/tilepairfiles1/tilepairs-10-%d-%d-nostitch-EDIT.json"%(project,minZ,maxZ)
#cmd_ex1 = "/pipeline/forrestrender/render-ws-spark-client/src/main/scripts/run_tilepair_only.sh --owner %s --project %s --stack Rough_Aligned_1_DAPI_1_deconv_masked_CONS --minZ %d --maxZ  %d --collection %s --deltaZ 10 --renderWithFilter true"%#(owner,project,minZ,maxZ,highres_pm_collection)
#cmd_ex2 = "/pipeline/forrestrender/render-ws-spark-client/src/main/scripts/run_sift_on_tilepair_client.sh --owner %s --project %s --stack Rough_Aligned_1_DAPI_1_deconv_masked_CONS --minZ %d --maxZ %d --collection %s --deltaZ 10  --jsonFile %s --renderWithFilter true --siftsteps 3 --#renderScale .5 --SIFTminScale .5 --SIFTmaxScale .8 --mininliers 8"%(owner,project,minZ, maxZ, highres_pm_collection,json_file)
#print json_file
#os.system(cmd_ex1)
#os.system(cmd_ex2)

mychannel = "DAPI_1"

beg_indices = [0]
end_indices = [5]

for i in range(0, len(beg_indices)):
	minZ = beg_indices[i]
	maxZ = end_indices[i]
	json_file = "/nas5/data/%s/processed/tilepairfiles1/tilepairs-10-%d-%d-nostitch-EDIT.json"%(project,minZ,maxZ)
	cmd_ex1 = "%s/run_tilepair_only.sh --owner %s --project %s --stack Rough_Aligned_1_DAPI_1_R0_CONS --minZ %d --maxZ  %d --collection %s_%s --deltaZ 10 --renderWithFilter true --jsonFile %s"%(pm_script_dir,owner,project,minZ,maxZ,highres_pm_collection,mychannel,json_file)
	cmd_ex2 = "%s/run_sift_on_tilepair_client.sh --owner %s --project %s --stack Rough_Aligned_1_DAPI_1_R0_CONS --minZ %d --maxZ %d --collection %s_%s --deltaZ 10  --jsonFile %s --renderWithFilter true --siftsteps 5 --renderScale .5 --SIFTminScale .5 --SIFTmaxScale .8 --mininliers 8"%(pm_script_dir,owner,project,minZ, maxZ, highres_pm_collection,mychannel,json_file)
	print json_file
	print cmd_ex1
	print cmd_ex2
	#os.system(cmd_ex1)
	#os.system(cmd_ex2)

#exit(0)
############apply fine alignment
	

for ch in channelnames:
	#ch = "PSD95"
	#if ch == "1_DAPI_1":
        # 	print "Do Nothing"
	#else:
	cmdappalign = "docker exec renderapps_develop python -m renderapps.registration.apply_transforms_by_frame %s %s --cyclenumber 200 --alignedStack  Fine_Aligned_DAPI_1_R0 --inputStack  Rough_Aligned_%s_R0 --outputStack Fine_Aligned_%s_R0 --pool_size 20"%(render_str,project_str,ch,ch)
        #cmdappalignbyID = "docker exec renderapps_develop python -m renderapps.registration.apply_transforms_by_tileId %s %s --alignedStack  Fine_Aligned_DAPI_1 --inputStack  Rough_Aligned_Deconvolved_%s --outputStack Fine_Aligned_Deconvolved_%s --pool_size 20"%(render_str,project_str,ch,ch)
	
	print cmdappalign
	#print cmdappalignbyID
	os.system(cmdappalign)
	#os.system(cmdappalignbyID)
exit(0)

for ch in channelnames:
	#if ch == "1_DAPI_1":
	#	print "Do Nothing"
	#else:
	#ch = "PSD95"
#for i in range (0,1):
#	ch = "3_MBP"
	cmdappalign = "docker exec renderapps_develop python -m renderapps.registration.apply_alignment_transform_from_registered_stack %s %s --prealigned_stack Rough_Aligned_1_DAPI_1_CONS --postaligned_stack  Fine_Aligned_DAPI_1 --source_stack  Rough_Aligned_registered_%s --output_stack Fine_Aligned_registered_%s --pool_size 20"%(render_str,project_str,ch,ch)
        
	
	print cmdappalign
	os.system(cmdappalign)




 	cmdsetstackstate = "docker exec renderapps_smallvol python -m renderapps.stack.set_stack_metadata \
                                       --render.host ibs-forrestc-ux1 \
                                       --render.port 8080 \
                                       --render.client_scripts /var/www/render/render-ws-java-client/src/main/scripts \
                                       --render.memGB 5G \
                                       --log_level INFO \
                                       --render.project M246930_Scnn1a_4_f1 \
                                       --render.owner Forrest \
                                      --input_stack  Fine_Aligned_Deconvolved_%s \
                                       --cycleNumber 200"%ch
	os.system(cmdsetstackstate)



exit(0)

