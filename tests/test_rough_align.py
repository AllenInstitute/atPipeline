#-------------------------------------------------------------------------------
# Name:        test_1
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

AT_SYSTEM_CONFIG_FOLDER_NAME    = 'AT_SYSTEM_CONFIG_FOLDER'
AT_SYSTEM_CONFIG_FILE_NAME      = 'at-system-config.ini'
TEST_DATA_SET = 'Q1023'

def compareFileInFolders(the_file, folder_1,folder_2):
    f1 = open(os.path.join(folder_1, the_file)).read()
    f2 = open(os.path.join(folder_2, the_file)).read()

    diff_result = (f1 == f2)

    print (diff_result)
    return diff_result
