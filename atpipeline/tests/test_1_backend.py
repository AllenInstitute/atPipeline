#-------------------------------------------------------------------------------
# Name:        test-backend
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

AT_SYSTEM_CONFIG_FOLDER    = 'AT_SYSTEM_CONFIG_FOLDER'
AT_SYSTEM_CONFIG_FILE_NAME = 'at-system-config.ini'

#----------------------------------------------------------------------------------------------------------

#Test to check if environment variable is setup
def test_config_file_environment_variable():
    res = (AT_SYSTEM_CONFIG_FOLDER in os.environ)
    assert res == True

#Test to check if the system config file exists
def test_system_config_file_exists():
    config_file = os.path.join(os.environ.get(AT_SYSTEM_CONFIG_FOLDER), AT_SYSTEM_CONFIG_FILE_NAME)
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

