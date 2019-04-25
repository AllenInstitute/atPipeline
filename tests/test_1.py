#-------------------------------------------------------------------------------
# Name:        test_1
# Purpose:     test integrity of input/output data, up to stitching
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

AT_SYSTEM_CONFIG_FOLDER_NAME    = 'AT_SYSTEM_CONFIG_FOLDER'
AT_SYSTEM_CONFIG_FILE_NAME      = 'at-system-config.ini'

def compareFileInFolders(the_file, folder_1,folder_2):
    f1 = open(os.path.join(folder_1, the_file)).read()
    f2 = open(os.path.join(folder_2, the_file)).read()

    diff_result = (f1 == f2)

    print (diff_result)
    return diff_result

@pytest.fixture
def at_backend():
    import at_docker_manager
    return at_docker_manager.DockerManager()

@pytest.fixture
def system_config():
    import at_system_config
    configFolder = os.environ[AT_SYSTEM_CONFIG_FOLDER_NAME]
    return at_system_config.ATSystemConfig(os.path.join(configFolder, AT_SYSTEM_CONFIG_FILE_NAME))

@pytest.fixture
def render_client(system_config):
    import renderapi
    render_project_owner = 'PyTest'

    args = {
        'host': system_config.renderHost,
        'port': system_config.renderHostPort,
        'owner': '',
        'project': '',
        'client_scripts': system_config.clientScripts
    }

    return renderapi.render.connect(**args)

@pytest.fixture
def test_data_folder(system_config):
    return system_config.config['GENERAL']['TEST_DATA_FOLDER']

#Test to check if environment variable is setup
def test_config_file_environment_variable():
    res = (AT_SYSTEM_CONFIG_FOLDER_NAME in os.environ)
    assert res == True

#Test to check if system config file exists
def test_config_file_exists():
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
    import at_utils as u
    out = u.runShellCMD('python ..\\atcore.py --version --dataroot')
    res = (out == ['0.0.1\n'])
    assert res == True

#Test integrity of input data.
def test_Q1023_meta_data(test_data_folder):
    import at_utils as u

    data_root = os.path.join(test_data_folder, 'Q1023')
    cmd = 'python ..\\atcore.py --dataroot ' + data_root
    out = u.getJSON(cmd)
    data = json.loads(out)

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
def test_Q1023_data_creation(test_data_folder):
    import at_utils as u
    data_root = os.path.join(test_data_folder, 'Q1023')
    cmd = 'python ..\\atcore.py --dataroot ' + data_root + ' --pipeline stitch --overwritedata --renderprojectowner PyTest'

    #This will take about 15 minutes
    #out = u.runShellCMD(cmd)
    #print (out)

def test_Q1023_state_tables(test_data_folder):
    #If we get here, start checking output files
    test_output_data_root = os.path.join(test_data_folder, 'Q1023', 'processed', 'Q1023')
    assert os.path.exists(test_output_data_root) == True

    ref_state_tables_folder = os.path.join(test_data_folder, 'results', 'Q1023', 'statetables')

    #Pipeline step 1: Check statetables folder ================================================
    test_state_tables_folder = os.path.join(test_output_data_root,    'statetables')

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

def test_Q1023_stacks(render_client):
    stacks= renderapi.render.get_stacks_by_owner_project(owner='PyTest', project='Q1023', render = render_client)
    assert 'S2_Session2' in stacks
