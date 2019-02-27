import os

ribbon = 10
sections = 32
frames = 24
root_dir = "/nas5/data/M335503_R3CBa_Ai139_medvol_run2/processed/Deconv_3d_r7_r10/raw/data/Ribbon0010/session0001/GFP"

for section in range(0,sections):
	z = (ribbon*100)+ section
	for frame in range(0, frames):

		cmd = "mv %s/GFP_S%04d_F%04d_Z00_metadata.txt %s/Deconvolved_1_GFP_%d_Flatfieldcorrected_1_GFP_%d_GFP_S%04d_F%04d_Z00_metadata.txt"%(root_dir,section, frame,root_dir,z,z,section,frame)
		print cmd
		os.system(cmd)
