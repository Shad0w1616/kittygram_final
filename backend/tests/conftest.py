import os
from pathlib import Path

import pytest
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]


@pytest.fixture(scope='session')
def base_dir():
    return BASE_DIR


@pytest.fixture(scope='session')
def backend_dir_info():
    return BASE_DIR / 'backend', 'backend'


@pytest.fixture(scope='session')
def nginx_dir_info():
    return BASE_DIR / 'nginx', 'nginx'


@pytest.fixture(scope='session')
def expected_nginx_files():
    return {'nginx.conf', 'Dockerfile'}


@pytest.fixture(scope='session')
def dockerfile_name():
    return 'Dockerfile'


@pytest.fixture(scope='session')
def workflow_file_name():
    return 'kittygram_workflow.yml'


@pytest.fixture(scope='session')
def docker_compose_prod_file_name():
    return 'docker-compose.production.yml'


@pytest.fixture(scope='session')
def deploy_file_info():
    path = BASE_DIR / 'tests.yml'
    assert path.is_file(), 'Create tests.yml in the project root.'
    return path, 'tests.yml'


@pytest.fixture(scope='session')
def deploy_info_file_content(deploy_file_info):
    content = yaml.safe_load(deploy_file_info[0].read_text(encoding='utf-8'))
    assert isinstance(content, dict), 'tests.yml must contain a YAML mapping.'
    return content


@pytest.fixture(scope='session')
def expected_deploy_info_file_content():
    return {
        'repo_owner': 'GitHub owner',
        'kittygram_domain': 'Kittygram URL (localhost is supported)',
        'dockerhub_username': 'Docker Hub username',
    }


@pytest.fixture(scope='session')
def kittygram_url(deploy_info_file_content):
    url = os.getenv('KITTYGRAM_URL', deploy_info_file_content['kittygram_domain'])
    assert url.startswith(('http://', 'https://')), 'Expected an HTTP(S) URL.'
    return url.rstrip('/')


@pytest.fixture(scope='session')
def dockerhub_username_key():
    return 'dockerhub_username'
