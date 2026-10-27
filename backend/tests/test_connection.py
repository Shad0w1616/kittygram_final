from urllib.parse import urljoin
import re

import pytest
import requests

pytestmark = pytest.mark.integration


def test_kittygram_page_and_deep_link(kittygram_url):
    for path in ('/', '/signin', '/cats/1'):
        response = requests.get(kittygram_url + path, timeout=15)
        assert response.status_code == 200
        assert 'Kittygram' in response.text


def test_kittygram_static_is_available(kittygram_url):
    response = requests.get(kittygram_url + '/', timeout=15)
    assert response.status_code == 200
    match = re.search(r'src="([^"]+\.js)"', response.text)
    assert match, 'The page must reference the built JavaScript bundle.'
    script = requests.get(urljoin(kittygram_url + '/', match.group(1)), timeout=15)
    assert script.status_code == 200
    assert 'javascript' in script.headers.get('Content-Type', '')


def test_admin_and_static(kittygram_url):
    response = requests.get(kittygram_url + '/admin/', timeout=15)
    assert response.status_code == 200
    assert '/kittygram/admin/login/' in response.url
    css = requests.get(kittygram_url + '/static/admin/css/base.css', timeout=15)
    assert css.status_code == 200
    assert 'text/css' in css.headers.get('Content-Type', '')


def test_kittygram_api_available(kittygram_url):
    response = requests.post(
        kittygram_url + '/api/users/',
        json={'username': 'validation_only', 'password': ''}, timeout=15,
    )
    assert response.status_code == 400
    assert 'password' in response.json()
    response = requests.get(kittygram_url + '/api/cats/', timeout=15)
    assert response.status_code == 401


def test_missing_media_returns_404(kittygram_url):
    response = requests.get(
        kittygram_url + '/media/nonexistent-ci-image.png', timeout=15,
    )
    assert response.status_code == 404
