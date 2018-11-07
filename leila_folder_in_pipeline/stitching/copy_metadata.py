import os

channels = ["GFP"]

for ribbon in range(10,11):
	for session in range(1,2):
		for ch in channels:
			cmd = "cp /nas5/data/M335503_R3CBa_Ai139_medvol_run2/raw/data/Ribbon%04d/session0%d/%s/*Z00_metadata.txt /nas5/data/M335503_R3CBa_Ai139_medvol_run2/processed/Deconv_3d_r7_r10/raw/data/Ribbon%04d/session%04d/%s"%(ribbon,session,ch,ribbon,session,ch)
			print cmd
			os.system(cmd)	
