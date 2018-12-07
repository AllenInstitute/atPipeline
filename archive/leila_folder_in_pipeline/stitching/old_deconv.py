import paramiko
import os
import time
import json
import sys
sys.path.insert(0,'/pipeline/sharmi/allen_SB_code/celery/')
from celery import Celery
from tasks import run_celerycommand


#def parse_project_directory(line):

 #       proj = line.split("raw")
  #      projectdirectory = proj[0]
#
 #       tok = line.split("/")
  #      ribbondir = tok[len(tok)-2]
   #     sessiondir = tok[len(tok)-1]
    #    ribbon = int(ribbondir[6:])
     #   session = int(sessiondir[7:])

      #  return [projectdirectory, ribbon, session]

def savedeconvjson(dd,deconvfile,owner, project, flatfield_stack,deconv_stack,deconv_dir,sectnum,psf_file, num_iter,bgrd_size,scale_factor):
        dd['render']['owner'] = owner
        dd['render']['project'] = project
        dd['input_stack'] = input_stack
        dd['output_stack'] = deconv_stack
        dd['psf_file'] = psf_file
        dd['num_iter']=num_iter
        dd['bgrd_size'] = bgrd_size
        dd['z_index'] = z
        dd['output_directory'] = deconv_dir
	dd['output_stack'] = deconv_stack
        dd['scale_factor'] = scale_factor
        dd['close_stack'] = close_stack
	dd['pool_size'] = pool_size
        with open(deconvfile, 'w') as outfile:
                json.dump(dd, outfile,indent=4)


if __name__ == "__main__":

        owner = "Forrest"
	project = "M247514_Rorb_1"
        deconvtemplate = "template/deconvolution.json"
        firstsection = 0
        lastsection = 2
        num_iter = 20
	pool_size = 20
	channels = ["DAPI_3","GABA", "MBP", "synapsin"]

	curdir = os.getcwd()

	with open("/pipeline/leila/stitching/confirm_data2process") as f:
                alldirnames = f.readlines()
	
        	for dirname in alldirnames:
                        print dirname
			proj = dirname.split('raw')
			tok = dirname.split('/')
			sessiondir = tok[len(tok)-1]
			ribbondir = tok[len(tok)-2]
			ribbon = int(ribbondir[6:])
			session = int(sessiondir[7:])

                        for sectnum in range(firstsection,(lastsection+1)):
                                close_stack = False

                        	if sectnum==lastsection:
                                        close_stack = True
				
				#projectdirectory = dirname.strip()
				#[projectroot, ribbon,session] = parse_project_directory(projectdirectory)
                                z = (ribbon*50)+sectnum

				#create file that consists of celery job commands
				filename = "log/runme_sect_%s_%d_%d_%s.sh"%(project, ribbon,session,sectnum)
                                f = open(filename,'w')
	
				for i in range(4):
					ch= channels[i]
					deconv_dir = "/nas3/data/M247514_Rorb_1/processed/deconvolveddata_new/%s/Session0003/%s/"%(ribbondir,ch)
					deconvfile = "%s/log/deconv_%s_%s_%s_%s_%d.json"%(curdir,project,ch,ribbon,session,sectnum)
					psf_file = "/nas/data/M247514_Rorb_1/processed/psfs/psf_%s.tif"%(ch)
					
					#stacks
					input_stack = "STI%s"%(ch)
					deconv_stack = "Deconvolved_%s_LEILA"%(input_stack)


                			#directories
            	    			#deconv_dir = "/nas3/data/M247514_Rorb_1/processed/deconvolveddata_new/Ribbon0001/Session0003/%s/"%(ch)

                			#psf file, scale factor, and background size for deconvolution
                                        #print ch


                			if ch=="GABA":
                				#print "Im gfp"
                        			#psf_file = "/nas2/data/M335503_Ai139_smallvol/processed/psfs/psf_ATubulin.tif"
                        			scale_factor = 4
                        			bgrd_size = 20
                			elif ch=="DAPI_3":
                                                #print "im dapi"
                        			psf_file = "/nas/data/M247514_Rorb_1/processed/psfs/psf_DAPI.tif"
                         			scale_factor = 1
                         			bgrd_size = 20
                			elif ch=="MBP":
                        			#print "im geph"
                         			#psf_file = "/nas2/data/M335503_Ai139_smallvol/processed/psfs/psf_VGlut1.tif"
                         			scale_factor = 1
                        			bgrd_size = 20
                                        elif ch=="synapsin":
                                                #print "im psd"
                                                #psf_file = "/nas1/data/M247514_Rorb_1/processed/psfs/psf_synapsin.tif"
                                                scale_factor = 5
                                                bgrd_size = 20
                			else:
                        			psf_file = ""
                       				scale_factor = 3
                        			bgrd_size = 20

					

					with open(deconvtemplate) as json_data:
                				dd = json.load(json_data)
                			savedeconvjson(dd,deconvfile,owner, project, input_stack,deconv_stack,deconv_dir,z,psf_file, num_iter,bgrd_size,scale_factor)

					#run
					cmd = "docker exec renderapps_develop python -m renderapps.intensity_correction.apply_deconvolution --input_json %s"%deconvfile

					f.write(cmd+"\n")



				f.close()
        			rcmd = "sh %s"%filename
        			print rcmd
        			#result = run_celerycommand.apply_async(args=[rcmd,os.getcwd()])
        			os.system(rcmd)
        			time.sleep(10)
