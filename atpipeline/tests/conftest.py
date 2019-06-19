import pytest
import os
import argparse
from atpipeline import at_backend_arguments
from atpipeline import at_atcore_arguments
from atpipeline import at_system_config

@pytest.fixture
def system_config():
    from atpipeline import at_system_config
    from atpipeline import at_atcore_arguments, at_common_arguments

    parser = argparse.ArgumentParser('backend')
    at_backend_arguments.add_arguments(parser)
    at_common_arguments.add_arguments(parser)
    args = parser.parse_args([])

    return at_system_config.ATSystemConfig(args, client = 'backend')

@pytest.fixture
def at_backend(system_config):
    from atpipeline import at_docker_manager
    dm = at_docker_manager.DockerManager(system_config)
    return dm

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

