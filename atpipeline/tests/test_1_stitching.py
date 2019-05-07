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

AT_SYSTEM_CONFIG_FOLDER_NAME    = 'AT_SYSTEM_CONFIG_FOLDER'
AT_SYSTEM_CONFIG_FILE_NAME      = 'at-system-config.ini'

TEST_DATA_CONFIG_FILE_NAME      = 'Q1023.ini'

#Projectname will create data in a folder with the same name
#Render stacks are also created using the project name
PROJECT_NAME                    = 'pytest_1'

@pytest.fixture
def test_data_set():
    return 'Q1023'

def compareFileInFolders(the_file, folder_1,folder_2):
    f1 = open(os.path.join(folder_1, the_file)).read()
    f2 = open(os.path.join(folder_2, the_file)).read()

    diff_result = (f1 == f2)

    print (diff_result)
    return diff_result
#----------------------------------------------------------------------------------------------------------

#Test to check if environment variable is setup
def test_config_file_environment_variable():
    res = (AT_SYSTEM_CONFIG_FOLDER_NAME in os.environ)
    assert res == True

#Test to check if the system config file exists
def test_system_config_file_exists():
    config_file = os.path.join(os.environ.get(AT_SYSTEM_CONFIG_FOLDER_NAME), AT_SYSTEM_CONFIG_FILE_NAME)
    res = os.path.exists(config_file)
    assert res == True

#Test to check status of at backend
def test_status_at_backend(at_backend):
    #Success response from the status call is 0
    response = at_backend.status()
    assert response == 0

#Test to check that the folder for test data exists
def test_test_data_folder(test_data_folder):
    res = os.path.exists(test_data_folder)
    assert res == True

def test_atcore_version():
    from atpipeline import at_utils as u
    from atpipeline import atcore

    out = u.runShellCMD(r'atcore --version')
    res = (out == ['atcore 0.5.0\n'])
    assert res == True

#Test integrity of input data.
def test_meta_data(test_data_folder, test_data_set):
    from atpipeline import at_utils as u

    data_root = os.path.join(test_data_folder, 'input', test_data_set)
    cmd = 'atcore --dataroot ' + data_root
    out = u.getJSON(cmd)
    data = json.loads(out)

    #Values for the Q1023 dataset
    assert data['NumberOfRibbons']      == 2
    assert data['NumberOfSections']     == 10
    assert data['NumberOfTiles']        == 180
    assert data['NumberOfSessions']     == 1
    assert data['NumberOfChannels']     == 2
    assert data['RibbonFolders']        == 'Ribbon0010,Ribbon0011'
    assert data['SessionFolders']       == 'session02'
    assert data['SectionsInRibbons'][0] ==  6
    assert data['SectionsInRibbons'][1] ==  4

#Create output data and compare output
def test_data_creation(test_data_folder, test_data_set):
    from atpipeline import at_utils as u
    data_input_root = os.path.join(test_data_folder, 'input', test_data_set)


    #remove any output data
    data_output_folder = os.path.join(data_input_root, 'processed', PROJECT_NAME)

    if os.path.exists(data_output_folder):
        shutil.rmtree(data_output_folder)

    #Remove data that exists in render
    cmd = r'atcore --dataroot ' + data_input_root + ' --pipeline stitch --renderprojectowner PyTest --project_name ' + PROJECT_NAME

    #This will take about 15 minutes
    out = u.runShellCMD(cmd)


def test_state_tables(test_data_folder, test_data_set):
    #If we get here, start checking output files
    test_output_data_root = os.path.join(test_data_folder, 'input', test_data_set, 'processed', PROJECT_NAME)
    assert os.path.exists(test_output_data_root) == True

    ref_state_tables_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, 'statetables')

    #Pipeline step 1: Check statetables folder ================================================
    test_state_tables_folder = os.path.join(test_output_data_root,    'statetables')

    #TODO populate this automatically later on, so we can run the whole test on any dataset
    #Values for the Q1023 dataset
    state_tables = ['statetable_ribbon_10_session_2_section_0',
                    'statetable_ribbon_10_session_2_section_1',
                    'statetable_ribbon_10_session_2_section_2',
                    'statetable_ribbon_10_session_2_section_3',
                    'statetable_ribbon_10_session_2_section_4',
                    'statetable_ribbon_10_session_2_section_5',
                    'statetable_ribbon_11_session_2_section_0',
                    'statetable_ribbon_11_session_2_section_1',
                    'statetable_ribbon_11_session_2_section_2',
                    'statetable_ribbon_11_session_2_section_3'
                 ]
    for f in state_tables:
        assert compareFileInFolders(f, test_state_tables_folder, ref_state_tables_folder) == True

def test_stacks(render_client):
    stacks= renderapi.render.get_stacks_by_owner_project(owner='PyTest', project=PROJECT_NAME, render = render_client)
    assert 'S2_Session2'            in stacks
    assert 'S2_Medians'             in stacks
    assert 'S2_FlatFielded'         in stacks
    assert 'S2_Stitched'            in stacks
    assert 'S2_Stitched_Dropped'    in stacks

##def test_images_and_tilespec_folders(test_data_folder):
##    #Just check that the downsamp_images and downsamp_tilespec folders exists
##    test_output_data_root = os.path.join(test_data_folder, test_data_set, 'processed', PROJECT_NAME)
##    assert os.path.exists(os.path.join(test_output_data_root, 'downsamp_images')) == True
##    assert os.path.exists(os.path.join(test_output_data_root, 'downsamp_tilespec')) == True
##
##def test_median_jsons(test_data_folder, test_data_set):
##    sub_dir = 'medians'
##    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
##    test_folder = os.path.join(test_data_folder, test_data_set, 'processed', PROJECT_NAME, sub_dir)
##
##    #TODO populate this automatically later on, so we can run the whole test on any dataset
##    #Values for the Q1023 dataset
##    files = [
##               'median_10_2_0_5.json',
##               'median_11_2_0_3.json'
##            ]
##    for f in files:
##        assert compareFileInFolders(f, test_folder, ref_folder) == True
##
##def test_flatfield_jsons(test_data_folder, test_data_set):
##    sub_dir = 'flatfield'
##    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
##    test_folder = os.path.join(test_data_folder, test_data_set, 'processed', PROJECT_NAME, sub_dir)
##
##    #TODO populate this automatically later on, so we can run the whole test on any dataset
##    #Values for the Q1023 dataset
##    files = [
##                'flatfield_Q1023_10_2_0.json',
##                'flatfield_Q1023_10_2_1.json',
##                'flatfield_Q1023_10_2_2.json',
##                'flatfield_Q1023_10_2_3.json',
##                'flatfield_Q1023_10_2_4.json',
##                'flatfield_Q1023_10_2_5.json',
##                'flatfield_Q1023_11_2_0.json',
##                'flatfield_Q1023_11_2_1.json',
##                'flatfield_Q1023_11_2_2.json',
##                'flatfield_Q1023_11_2_3.json'
##            ]
##    for f in files:
##        assert compareFileInFolders(f, test_folder, ref_folder) == True
##
##def test_stitching_jsons(test_data_folder, test_data_set):
##    sub_dir = 'stitching'
##    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
##    test_folder = os.path.join(test_data_folder, test_data_set, 'processed', PROJECT_NAME, sub_dir)
##
##    #TODO populate this automatically later on, so we can run the whole test on any dataset
##    #Values for the Q1023 dataset
##    files = [
##                'stitched_11_2_3.json',
##                'stitched_11_2_2.json',
##                'stitched_11_2_1.json',
##                'stitched_11_2_0.json',
##                'stitched_10_2_5.json',
##                'stitched_10_2_4.json',
##                'stitched_10_2_3.json',
##                'stitched_10_2_2.json',
##                'stitched_10_2_1.json',
##                'stitched_10_2_0.json'
##            ]
##    for f in files:
##        assert compareFileInFolders(f, test_folder, ref_folder) == True
##
##def test_dropped_jsons(test_data_folder, test_data_set):
##    sub_dir = 'dropped'
##    ref_folder = os.path.join(test_data_folder, 'validation-data', PROJECT_NAME, sub_dir)
##    test_folder = os.path.join(test_data_folder, test_data_set, 'processed', PROJECT_NAME, sub_dir)
##
##    #TODO populate this automatically later on, so we can run the whole test on any dataset
##    #Values for the Q1023 dataset
##    files = [
##                'S2_Stitched_Dropped_z1000.json',
##                'S2_Stitched_Dropped_z1001.json',
##                'S2_Stitched_Dropped_z1002.json',
##                'S2_Stitched_Dropped_z1003.json',
##                'S2_Stitched_Dropped_z1004.json',
##                'S2_Stitched_Dropped_z1005.json',
##                'S2_Stitched_Dropped_z1100.json',
##                'S2_Stitched_Dropped_z1101.json',
##                'S2_Stitched_Dropped_z1102.json',
##                'S2_Stitched_Dropped_z1103.json'
##            ]
##
##    for f in files:
##        #For now, just check existence of files
##        #assert compareFileInFolders(f, test_folder, ref_folder) == True
##        assert os.path.exists(os.path.join(test_folder, f))
