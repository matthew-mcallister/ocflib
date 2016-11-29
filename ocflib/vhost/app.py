import requests

import ocflib.constants as constants


def get_app_vhost_db():
    """Returns lines from the app vhost database. Loaded from the filesystem
    (if available), or from the web if not."""
    try:
        with open(constants.VHOST_APP_DB_PATH) as f:
            return list(map(str.strip, f))
    except IOError:
        # fallback to database loaded from web
        return list(map(str.strip, requests.get(constants.VHOST_APP_DB_URL).text.split('\n')))


def get_app_vhosts():
    """Returns all active app vhosts in a convenient format.

    >>> get_app_vhosts()
    {
        'upe.cs.berkeley.edu': {
            'username': 'upe',
            'socket_name': 'upe',
            'ssl_name': None,
        }
    }
    """
    vhosts = {}
    for line in get_app_vhost_db():
        if not line or line.startswith('#'):
            continue

        account, name, socket_name, ssl_name = line.split(' ')

        if name == '-':
            name = account + '.berkeley.edu'

        if socket_name == '-':
            socket_name = account

        if ssl_name == '-':
            ssl_name = None

        vhosts[name] = {
            'username': account,
            'socket_name': socket_name,
            'ssl_name': ssl_name,
        }

    return vhosts


def app_dev_alias(domain, dev=False):
    """Returns the development alias domain for a given app domain.

    If dev is True, then the domain will be for the development apphost server
    instead.

    >>> app_dev_alias('group.berkeley.edu')
    'group-berkeley-edu.apphost.ocf.berkeley.edu'
    """
    return domain.replace('.', '-') + ('.', '.dev-')[dev] + 'apphost.ocf.berkeley.edu'
