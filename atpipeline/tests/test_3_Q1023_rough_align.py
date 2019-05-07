#-------------------------------------------------------------------------------
# Name:        test_rough_align
# Purpose:     test integrity of input/output data, from stitching to rough align
#              These are tests for the Q1023 TestDataset
#
# Author:      matsk
#
# Created:     Apr 23, 2019
#-------------------------------------------------------------------------------
import pytest
import os
import docker
import json
import difflib
import renderapi
from atpipeline import at_test_utils as tu

#Projectname will create data in a folder with the same name
#Render stacks are also created using the project name
PROJECT_NAME                    = 'pytest_1'


@pytest.fixture
def test_data_set():
    return 'Q1023'


#Create output data and compare output
def test_low_res_folder(test_data_folder, test_data_set):
    from atpipeline import at_utils as u
    data_root = os.path.join(test_data_folder, test_data_set)
    cmd = r'atcore --dataroot ' + data_root + ' --pipeline roughalign --overwritedata --renderprojectowner PyTest'

    #This will take about 15 minutes ===============
    print (cmd)
    out = u.runShellCMD(cmd)
    #assert False

def test_dropped_jsons(test_data_folder, test_data_set):
    sub_dir = 'dropped'
    ref_folder  = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
                'S2_Stitched_Dropped_z1000.json',
                'S2_Stitched_Dropped_z1001.json',
                'S2_Stitched_Dropped_z1002.json',
                'S2_Stitched_Dropped_z1003.json',
                'S2_Stitched_Dropped_z1004.json',
                'S2_Stitched_Dropped_z1005.json',
                'S2_Stitched_Dropped_z1100.json',
                'S2_Stitched_Dropped_z1101.json',
                'S2_Stitched_Dropped_z1102.json',
                'S2_Stitched_Dropped_z1103.json'
            ]

    for f in files:
        #For now, just check existence of files
        assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True
        #assert os.path.exists(os.path.join(test_folder, f))

