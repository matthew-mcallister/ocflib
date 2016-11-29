import mock
import pytest

from ocflib.vhost.app import app_dev_alias
from ocflib.vhost.app import get_app_vhost_db
from ocflib.vhost.app import get_app_vhosts


VHOSTS_EXAMPLE = """
asucapp api-dev.asuc.ocf.berkeley.edu dev api.asuc.ocf.berkeley.edu
bicycal - - -
"""  # noqa

VHOSTS_EXAMPLE_PARSED = {
    'api-dev.asuc.ocf.berkeley.edu': {
        'socket_name': 'dev',
        'ssl_name': 'api.asuc.ocf.berkeley.edu',
        'username': 'asucapp',
    },
    'bicycal.berkeley.edu': {
        'socket_name': 'bicycal',
        'ssl_name': None,
        'username': 'bicycal',
    },
}


@pytest.yield_fixture
def mock_get_app_vhosts_db():
    with mock.patch(
        'ocflib.vhost.app.get_app_vhost_db',
        return_value=VHOSTS_EXAMPLE.splitlines()
    ):
        yield


class TestAppVirtualHosts:

    def test_reads_file_if_exists(self):
        with mock.patch('builtins.open', mock.mock_open()) as mock_open:
            lines = ['hello', 'world']
            mock_open.return_value.__iter__.return_value = lines
            assert get_app_vhost_db() == lines

    @mock.patch('builtins.open')
    @mock.patch('requests.get')
    def test_reads_web_if_no_file(self, get, mock_open):
        def raise_error(__):
            raise IOError()

        mock_open.side_effect = raise_error
        get.return_value.text = 'hello\nworld'

        assert get_app_vhost_db() == ['hello', 'world']

    def test_proper_parse(self, mock_get_app_vhosts_db):
        assert get_app_vhosts() == VHOSTS_EXAMPLE_PARSED


class TestAppDevAlias:

    @pytest.mark.parametrize('name,dev,expected', [
        ('test.berkeley.edu', False, 'test-berkeley-edu.apphost.ocf.berkeley.edu'),
        ('test.berkeley.edu', True, 'test-berkeley-edu.dev-apphost.ocf.berkeley.edu')
    ])
    def test_app_dev_alias(self, name, dev, expected):
        assert app_dev_alias(name, dev) == expected
