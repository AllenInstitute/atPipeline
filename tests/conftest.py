import pytest
import os

AT_SYSTEM_CONFIG_FOLDER_NAME    = 'AT_SYSTEM_CONFIG_FOLDER'
AT_SYSTEM_CONFIG_FILE_NAME      = 'at-system-config.ini'
TEST_DATA_SET = 'Q1023'

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

@pytest.fixture
def test_data_set():
    return TEST_DATA_SET
