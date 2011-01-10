from __future__ import with_statement
from ConfigParser import SafeConfigParser as ConfigParser
import os

class Config(object):
    _config_file = None
    _parser = None

    def __init__(self):
        default_config_dir = os.path.join(os.environ['HOME'], '.config')
        config_dir = os.environ.get('XDG_CONFIG_HOME', default_config_dir)
        config_file = os.path.join(config_dir, 'procalc', 'config.ini')

        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        self._config_file = config_file
        self._parser = ConfigParser(dict(
            orientation='0',
            precision='-1:-1',
            base='10',
            view_mode='0'
            ))

    def load(self):
        self._parser.read(self._config_file)

    def save(self):
        with open(self._config_file, 'wb') as f:
            self._parser.write(f)

    def __getitem__(self, name):
        return self._parser.get('DEFAULT', name)

    def __setitem__(self, name, value):
        self._parser.set('DEFAULT', name, str(value))

