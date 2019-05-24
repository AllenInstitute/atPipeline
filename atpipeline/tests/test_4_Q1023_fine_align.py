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
PROJECT_NAME                    = 'pytest_Q1023'
PROJECT_INI                     = 'Q1023.ini'

@pytest.fixture
def test_data_set():
    return 'Q1023'


#Create output data and compare output
def test_fine_aligning(test_data_folder, test_data_set):
    from atpipeline import at_utils as u
    data_root = os.path.join(test_data_folder, 'input', test_data_set)
    data_ini_file = os.path.join(test_data_folder, 'input', PROJECT_INI)
    cmd = r'atcore --data ' + data_root + ' --pipeline finealign --renderprojectowner PyTest --configfile ' + data_ini_file + ' --projectname ' + PROJECT_NAME

    #This will take about 15 minutes ===============
    print (cmd)
    try:
        out = u.runShellCMD(cmd)
    except Exception:
        assert False

def test_stacks(render_client):
    stacks= renderapi.render.get_stacks_by_owner_project(owner='PyTest', project=PROJECT_NAME, render = render_client)
    assert 'S2_RoughAligned_Consolidated'     in stacks
    assert 'S2_FineAligned'                  in stacks


def test_highres_tilepairs_jsons(test_data_folder, test_data_set):
    sub_dir = 'high_res_tilepairfiles'
    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
                'tilepairs-2-1-0-9-nostitch.json',
                'tilepairs-2-1-0-9-nostitch-EDIT.json'
            ]
    for f in files:
        assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True

def test_fine_aligned_jsons(test_data_folder, test_data_set):
    sub_dir = 'fine_aligned'
    ref_folder  = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
                'input_fine_alignment_2_0_9.json',
                'output_fine_alignment_2_0_9.json'
            ]
    for f in files:
        assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True

def test_point_match_in_place(test_data_folder, test_data_set):
    sub_dir = 'point_match_in_place'
    ref_folder  = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
                'in_section_pairs_S2_RoughAligned_z0009.json',
                'in_section_pairs_S2_RoughAligned_z0008.json',
                'in_section_pairs_S2_RoughAligned_z0007.json',
                'in_section_pairs_S2_RoughAligned_z0006.json',
                'in_section_pairs_S2_RoughAligned_z0005.json',
                'in_section_pairs_S2_RoughAligned_z0004.json',
                'in_section_pairs_S2_RoughAligned_z0003.json',
                'in_section_pairs_S2_RoughAligned_z0002.json',
                'in_section_pairs_S2_RoughAligned_z0001.json',
                'in_section_pairs_S2_RoughAligned_z0000.json'
            ]

    for f in files:
        assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True
