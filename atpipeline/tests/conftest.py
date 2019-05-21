import pytest
import os

AT_SYSTEM_CONFIG_FOLDER    = 'AT_SYSTEM_CONFIG_FOLDER'
AT_SYSTEM_CONFIG_FILE_NAME      = 'at-system-config.ini'


@pytest.fixture
def at_backend():
    from atpipeline import at_docker_manager
    return at_docker_manager.DockerManager()

@pytest.fixture
def system_config():
    from atpipeline import at_system_config
    config_folder = os.environ[AT_SYSTEM_CONFIG_FOLDER]
    print ("ConfigFolder: " + config_folder)
    return at_system_config.ATSystemConfig(os.path.join(config_folder, AT_SYSTEM_CONFIG_FILE_NAME))

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

