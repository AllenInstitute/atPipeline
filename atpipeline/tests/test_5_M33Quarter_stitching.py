#-------------------------------------------------------------------------------
# Name:        test-stitching
# Purpose:     test integrity of input/output data, up to stitching
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
import shutil
from atpipeline import at_test_utils as tu

#Projectname will create data in a folder with the same name
#Render stacks are also created using the project name
PROJECT_NAME                    = 'pytest_M33Quarter'
PROJECT_INI                     = 'M33Quarter.ini'
@pytest.fixture
def test_data_set():
    return 'M33Quarter'

##============ Tests below
#Test integrity of input data.
def test_meta_data(test_data_folder, test_data_set):
    from atpipeline import at_utils as u

    data_root = os.path.join(test_data_folder, 'input', test_data_set)
    cmd = 'atcore --dataroot ' + data_root
    out = u.getJSON(cmd)
    data = json.loads(out)

    #Values for the Q1023 dataset
    assert data['NumberOfRibbons']      == 1
    assert data['NumberOfSections']     == 2
    assert data['NumberOfTiles']        == 60
    assert data['NumberOfSessions']     == 2
    assert data['NumberOfChannels']     == 4
    assert data['RibbonFolders']        == 'Ribbon0004'
    assert data['SessionFolders']       == 'session01,session02'
    assert data['SectionsInRibbons'][0] ==  2

#Create output data and compare output
def test_data_creation(test_data_folder, test_data_set):
    from atpipeline import at_utils as u
    data_input_root = os.path.join(test_data_folder, 'input', test_data_set)
    data_ini_file = os.path.join(test_data_folder, PROJECT_INI)

    #remove any output data
    data_output_folder = os.path.join(data_input_root, 'processed', PROJECT_NAME)

    if os.path.exists(data_output_folder):
        shutil.rmtree(data_output_folder)

    #Remove all data that exists in render
    cmd = r'atcore --dataroot ' + data_input_root + ' --pipeline stitch --renderprojectowner PyTest --project_name ' + PROJECT_NAME + ' --config_file_name ' + data_ini_file

    #This will take about 15 minutes
    try:
        out = u.runShellCMD(cmd)
    except Exception:
        assert False

def test_state_tables(test_data_folder, test_data_set):
    #If we get here, start checking output files
    test_output_data_root = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME)
    assert os.path.exists(test_output_data_root) == True

    ref_state_tables_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, 'statetables')

    #Pipeline step 1: Check statetables folder ================================================
    test_state_tables_folder = os.path.join(test_output_data_root,    'statetables')

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    state_tables = ['statetable_ribbon_4_session_1_section_0',
                    'statetable_ribbon_4_session_1_section_1',
                    'statetable_ribbon_4_session_2_section_0',
                    'statetable_ribbon_4_session_2_section_1'
                 ]
    for f in state_tables:
        assert tu.compare_file_in_folders(f, test_state_tables_folder, ref_state_tables_folder) == True

def test_stacks(render_client):
    stacks= renderapi.render.get_stacks_by_owner_project(owner='PyTest', project=PROJECT_NAME, render = render_client)
    assert 'S2_Session2'            in stacks
    assert 'S2_Medians'             in stacks
    assert 'S2_FlatFielded'         in stacks
    assert 'S2_Stitched'            in stacks
    assert 'S2_Stitched_Dropped'    in stacks

def test_images_and_tilespec_folders(test_data_folder, test_data_set):
    #Just check that the downsamp_images and downsamp_tilespec folders exists
    test_output_data_root = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME)
    assert os.path.exists(os.path.join(test_output_data_root, 'downsamp_images')) == True
    assert os.path.exists(os.path.join(test_output_data_root, 'downsamp_tilespec')) == True

def test_median_jsons(test_data_folder, test_data_set):
    sub_dir = 'medians'
    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
               'median_4_1_0_1.json',
               'median_4_2_0_1.json'
            ]
    for f in files:
        assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True

def test_flatfield_jsons(test_data_folder, test_data_set):
    sub_dir = 'flatfield'
    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
                'flatfield_' + PROJECT_NAME + '_4_1_0.json',
                'flatfield_' + PROJECT_NAME + '_4_1_1.json',
                'flatfield_' + PROJECT_NAME + '_4_2_0.json',
                'flatfield_' + PROJECT_NAME + '_4_2_1.json'
            ]
    for f in files:
        assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True

def test_stitching_jsons(test_data_folder, test_data_set):
    sub_dir = 'stitching'
    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
                'stitched_4_1_0.json',
                'stitched_4_1_1.json',
                'stitched_4_2_0.json',
                'stitched_4_2_1.json'
            ]
    for f in files:
        assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True

def test_dropped_jsons(test_data_folder, test_data_set):
    sub_dir = 'dropped'
    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
    test_folder = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME, sub_dir)

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    files = [
                'S1_Stitched_Dropped_z0400.json',
                'S1_Stitched_Dropped_z0401.json',
                'S1_Stitched_Dropped_z0400.json',
                'S1_Stitched_Dropped_z0401.json'
            ]

    for f in files:
        #For now, just check existence of files
        #assert tu.compare_file_in_folders(f, test_folder, ref_folder) == True
        assert os.path.exists(os.path.join(test_folder, f))
