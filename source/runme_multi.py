import paramiko
import os
import time
import json
import sys
sys.path.insert(0,'/pipeline/sharmi/allen_SB_code/celery/')
from celery import Celery
from tasks import run_celerycommand

def parse_project_directory(line):

	proj = line.split("raw")
	projectdirectory = proj[0]

	tok = line.split("/")
	ribbondir = tok[len(tok)-2]
	sessiondir = tok[len(tok)-1]
	ribbon = int(ribbondir[6:])
	session = int(sessiondir[7:])

	return [projectdirectory, ribbon, session]


def get_channel_names(directory):
	#return os.listdir(directory)
	directory_list = list()
	for root, dirs, files in os.walk(directory, topdown=False):
			for name in dirs:
				directory_list.append(os.path.join(root, name))
	return dirs
############### trying to read section number #####################
#def get_section_num(directory):
#	with open('session_metadata.txt') as f:
#		content = f.readlines()
#		last_sect = int(content.split("Length")[1])-1
#	return last_sect


def get_channel_nums(statetablefile):
		df=pd.read_csv(statetablefile)
		uniq_ch=df.groupby(['ch']).groups.keys()
		return uniq_ch

def parseprojectroot(projectdirectory):
		print "this is your directory: " + projectdirectory
		tok = projectdirectory.split("/")
		dataind = tok.index('data')
		print "this is your root: " + tok[dataind+1]
	return tok[dataind+1]

def parsefile(fname):

		with open(fname) as f:
				content = f.readlines()

		if len(content)>1:
				print "File is corrupted..."
		else:
				#parse line

				fullline = content[0]
				fullinetok = fullline.split(",")
				section = int(fullinetok[1])
				owner = str(fullinetok[2])
				#owner = "TESTEXPERIMENT"

				line = fullinetok[0]

				proj = line.split("raw")
				projectdirectory = proj[0]

				tok = line.split("/")
				ribbondir = tok[len(tok)-2]
				sessiondir = tok[len(tok)-1]
				ribbon = int(ribbondir[6:])
				session = int(sessiondir[7:])

				return [projectdirectory, ribbon, session, section, owner,fullline]

def savemedianjson(med,medianfile,owner, project,acq_stack,median_stack,median_dir,minz,maxz,close_stack):

	med['render']['owner'] = owner
	med['render']['project'] = project
	med['input_stack'] = acq_stack
	med['output_stack'] = median_stack
	med['minZ'] = minz
	med['maxZ'] = maxz
	med['output_directory'] = median_dir
	med['close_stack'] = close_stack
	with open(medianfile, 'w') as outfile:
			json.dump(med, outfile,indent=4)

def saveflatfieldjson(ff,flatfieldfile,owner, project, acq_stack,median_stack,flatfield_stack,flatfield_dir,sectnum,close_stack):
	ff['render']['owner'] = owner
		ff['render']['project'] = project
	ff['input_stack'] = acq_stack
	ff['correction_stack'] = median_stack
		ff['output_stack'] = flatfield_stack
		ff['z_index'] = sectnum
		ff['output_directory'] = flatfield_dir
	ff['close_stack'] = close_stack
		with open(flatfieldfile, 'w') as outfile:
				json.dump(ff, outfile,indent=4)


def savedeconvjson(dd,deconvfile,owner, project, flatfield_stack,deconv_stack,deconv_dir,sectnum,psf_file, num_iter,bgrd_size,scale_factor):
	dd['render']['owner'] = owner
		dd['render']['project'] = project
	dd['input_stack'] = flatfield_stack
		dd['output_stack'] = deconv_stack
	dd['psf_file'] = psf_file
	dd['num_iter']=num_iter
	dd['bgrd_size'] = bgrd_size
		dd['z_index'] = sectnum
		dd['output_directory'] = deconv_dir
	dd['scale_factor'] = scale_factor
	dd['close_stack'] = close_stack
	dd['pool_size'] = 21
		with open(deconvfile, 'w') as outfile:
				json.dump(dd, outfile,indent=4)


def savestitchingjson(sti,stitchingfile,owner, project, flatfield_stack,stitched_stack,sectnum):
	sti['owner'] = owner
		sti['project'] = project
		sti['stack'] = flatfield_stack
		sti['outputStack'] = stitched_stack
		sti['section'] = sectnum
		with open(stitchingfile, 'w') as outfile:
				json.dump(sti, outfile,indent=4)


def saveapplystitchingjson(appsti,applystitchingfile,owner, project, flatfield_stack,stitched_stack,stitched_dapi_stack):
	appsti['render']['owner'] = owner
		appsti['render']['project'] = project
		appsti['alignedStack'] = stitched_dapi_stack
		appsti['outputStack'] = stitched_stack
		appsti['inputStack'] = flatfield_stack

		with open(applystitchingfile, 'w') as outfile:
				json.dump(appsti, outfile,indent=4)


if __name__ == "__main__":

	owner = "multchan"
	mediantemplate = "template/median.json"
	flatfieldtemplate = "template/flatfield.json"
	deconvtemplate = "template/deconvolution.json"
	stitchingtemplate = "template/stitching.json"
	firstsection = 14
	lastsection = 24
	num_iter = 20
	#bgrd_size = 50

	curdir = os.getcwd()

	for i in range (0,1):

				with open("/pipeline/leila/stitching/confirm_data2process") as f:
						alldirnames = f.readlines()

				for dirname in alldirnames:
			flatfield_dirname =  "%s/../../../../processed/Flatfield_Test" %dirname.strip('\n')
			print "thiis is dirname: " + dirname
			print flatfield_dirname
			if not os.path.exists(flatfield_dirname):
				os.makedirs(flatfield_dirname)
						for sectnum in range(firstsection,lastsection+1):
				close_stack = False

				if sectnum==lastsection:
					close_stack = True

				projectdirectory = dirname.strip()
				project = parseprojectroot(projectdirectory)
				channels = get_channel_names(projectdirectory)
				[projectroot, ribbon,session] = parse_project_directory(projectdirectory)
				z = ribbon*100+sectnum
				print  "this is your projectroot: " + projectroot



				#create file that consists of celery job commands
				filename = "log/runme_sect_%s_%d_%d_%s.sh"%(project, ribbon,session,sectnum)
				f = open(filename,'w')


				#create state table

				#projectroot = "/nas/data/M246930_Scnn1a_4/"
				statetablefile =projectroot+ "scripts/statetable_ribbon_%d_session_%d_section_%d"%(ribbon,session,sectnum)
				#statetablefile = "/nas/data/M246930_Scnn1a_4/scripts/statetable_ribbon_%d_session_%d_section_%d"%(ribbon,session,sectnum)
				print projectroot
				print statetablefile
				#exit(0)
				#make state table
				cmd = "docker exec luigiscripts python make_state_table_ext_multi_pseudoz.py "
				cmd = cmd + "--projectDirectory %s "%projectroot
				cmd = cmd + "--outputFile  %s "%statetablefile
				cmd = cmd + "--oneribbononly True "
				cmd = cmd + "--ribbon %d "%ribbon
				cmd = cmd + "--session %d "%session
				cmd = cmd + "--section %d "%sectnum
				#f.write(cmd+"\n")
				#os.system(cmd)

				#upload acquisition stacks
				dcmd = "docker exec renderapps_multchan python -m renderapps.dataimport.create_fast_stacks_multi "
				dcmd = dcmd + "--render.host ibs-forrestc-ux1 "
 				dcmd = dcmd + "--render.client_scripts /shared/render/render-ws-java-client/src/main/scripts "
 				dcmd = dcmd + "--render.port 80 "
 				dcmd = dcmd + "--render.memGB 5G "
 				dcmd = dcmd + "--log_level INFO "
				dcmd = dcmd + "--statetableFile %s "%statetablefile
				dcmd = dcmd + "--render.project %s "%project
 				dcmd = dcmd + "--projectDirectory %s "%projectroot
 				dcmd = dcmd + "--outputStackPrefix ACQ_"
				dcmd = dcmd + " --render.owner %s "%owner
				#f.write(dcmd+"\n")
 				#os.system(dcmd)
				#exit(0)
				#dcmd = dcmd + "--projectDirectory %s "%projectroot


				#print channels



				medianfile = "%s/log/median_%s_%s_%s_%d.json"%(curdir,project,ribbon,session,sectnum)
				flatfieldfile = "%s/log/flatfield_%s_%s_%s_%d.json"%(curdir,project,ribbon,session,sectnum)
				deconvfile = "%s/log/deconv_%s_%s_%s_%d.json"%(curdir,project,ribbon,session,sectnum)
				stitchingfile = "%s/log/stitching_%s_%s_%s_%d.json"%(curdir,project,ribbon,session,sectnum)

				#stacks
				acq_stack = "ACQ_Session%d"%(int(session))
				median_stack = "MED_Session%d"%(int(session))
				flatfield_stack = "FF_Session%d"%(int(session))
				deconv_stack = "DCV_FF_Session%d"%(int(session))
				stitched_stack = "STI_FF_Session%d"%(int(session))

				#directories
				median_dir = "%s/processed/Medians_Test/"%projectroot
				flatfield_dir = "%s/processed/Flatfield_Test/"%projectroot
				deconv_dir = "%s/processed/Deconv/"%projectroot

				#psf file, scale factor, and background size for deconvolution
				#print ch

				#if ch=="TdTomato":
					#print "Im gfp"
				#	psf_file = "/nas5/data/M362218_CSATlx3_small_volume/processed/psfs/psf_MBP.tif"
				#	scale_factor = 3
				#	bgrd_size = 50
				#elif ch=="DAPI_1":
					#print "im dapi"
				#	psf_file = "/nas5/data/M362218_CSATlx3_small_volume/processed/psfs/psf_DAPI.tif"
								 #	   scale_factor = 1
								  #	  bgrd_size = 20
				#elif ch=="Gephyrin":
					#print "im geph"
				#	psf_file = "/nas5/data/M362218_CSATlx3_small_volume/processed/psfs/psf_Gephyrin.tif"
								 #	   scale_factor = 10
								  #	  bgrd_size = 20
				#elif ch=="PSD95":
					#print "im psd"
				#	psf_file = "/nas5/data/M362218_CSATlx3_small_volume/processed/psfs/psf_PSD95.tif"
								 #	   scale_factor = 6
								  #	  bgrd_size = 20
				#else:
				#	psf_file = ""
								   #	 scale_factor = 3
								 #	   bgrd_size = 20
					#print psf_file



					#create files
				#with open(mediantemplate) as json_data:
					#	med = json.load(json_data)
				#savemedianjson(med,medianfile,owner, project,acq_stack,median_stack,median_dir,firstsection,lastsection,close_stack)

				#with open(flatfieldtemplate) as json_data:
				#	ff = json.load(json_data)
				#saveflatfieldjson(ff,flatfieldfile,owner, project, acq_stack,median_stack,flatfield_stack,flatfield_dir,z,close_stack)


				#with open(deconvtemplate) as json_data:
				#	dd = json.load(json_data)
				#savedeconvjson(dd,deconvfile,owner, project, flatfield_stack,deconv_stack,deconv_dir,z,psf_file, num_iter,bgrd_size,scale_factor)

				with open(stitchingtemplate) as json_data:
										sti = json.load(json_data)
								savestitchingjson(sti,stitchingfile,owner, project, flatfield_stack,stitched_stack,z)


				if close_stack:
					with open(mediantemplate) as json_data:
											med = json.load(json_data)
									savemedianjson(med,medianfile,owner, project,acq_stack,median_stack,median_dir,ribbon*100+firstsection,ribbon*100+lastsection,close_stack)
				#run
					mystr = "DAPI"
					cmd1 = "docker exec renderapps_multchan python -m rendermodules.intensity_correction.calculate_multiplicative_correction --render.port 80 --input_json %s"%medianfile
					#os.system(cmd1)
					#f.write(cmd1+"\n")

					for sectnum in range(firstsection,lastsection+1):
						ff_z = ribbon*100+sectnum
						with open(flatfieldtemplate) as json_data:
												ff = json.load(json_data)
										saveflatfieldjson(ff,flatfieldfile,owner, project, acq_stack,median_stack,flatfield_stack,flatfield_dir,ff_z,close_stack)
						print ff_z
						cmd2 = "docker exec renderapps_multchan python -m rendermodules.intensity_correction.apply_multiplicative_correction --render.port 80 --input_json %s"%flatfieldfile
						#cmd3 = "docker exec renderapps_develop python -m renderapps.intensity_correction.apply_deconvolution --render.port 8988 --input_json %s"%deconvfile
						#os.system(cmd2)
						#f.write(cmd2+"\n")




				#print "Flatfield written"
				#f.write(cmd3+"\n")
				#print "Deconv written"

				#if ch.find(mystr) > -1 :
				cmd4 = "java -cp /pipeline/sharmi/at_modules/allen/target/allen-1.0-SNAPSHOT-jar-with-dependencies.jar at_modules.StitchImagesByCC --input_json %s"%stitchingfile
				f.write(cmd4+"\n")

				#else:
				#	cmd4 = ""


				#for ch in channels:
					#if ch.find("DAPI")>-1:
						#print "Do Nothing"
					#	c = 1
					#else:
						#print "###############################Apply Stitching###############################"
						#print session
						#applystitchingtemplate ="template/applystitching.json"
						#applystitchingfile = "%s/log/applystitch_%s_%d.json"%(curdir,ch,int(session))
						#stitched_dapi_stack = "STI_FF_S0%d_DAPI_%d"%(int(session),int(session))
						#stitched_dapi_stack = "STI_FF_S0%d_DAPI_%d"%(int(session),int(session))
						#deconv_stack = "DCV_FF_S0%d_%s"%(int(session),ch)
						#flatfield_stack = "FF_S0%d_%s"%(int(session),ch)
						#stitched_stack = "STI_FF_S0%d_%s"%(int(session),ch)
						#with open(applystitchingtemplate) as json_data:
											#		appsti = json.load(json_data)
											#saveapplystitchingjson(appsti,applystitchingfile,owner, project, flatfield_stack,stitched_stack,stitched_dapi_stack)
						#print "Stitching file saved"
						#cmdapp = "docker exec renderapps_develop python -m renderapps.registration.apply_transforms_by_frame --render.port 8988 --cyclenumber 2 --input_json %s"%applystitchingfile
						#os.system(cmdapp)
						#f.write(cmdapp+"\n")


				f.close()
				rcmd = "sh %s"%filename
				print rcmd
				#result = run_celerycommand.apply_async(args=[rcmd,os.getcwd()])
				os.system(rcmd)
				time.sleep(1)
