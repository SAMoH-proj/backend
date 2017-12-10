# This is a Singleton class to return values stored under resources/config.ini.
# Read that file for the meaning of each value.

"""
For an explanation of each config. item see comments in resource/config.ini
"""
from pkg_resources import resource_filename

import configparser
import shutil
import os

config = configparser.SafeConfigParser()

# initialize "home" variable for all configuration files
home = os.path.expanduser("~")
config.add_section('path')
config.set('path', 'home', home)


def get(section, key):
    return config.get(section, key)


def getboolean(section, key):
    return config.getboolean(section, key)


# init config
config_paths = []
config_paths.append(os.path.join(home, '.backend', 'backend.ini'))
config_paths.append(os.path.join('.', 'backend.ini'))
default_config_file = None

# combine the config files
found_paths = config.read(config_paths)

# fallback to bundled configuration file
if len(found_paths) == 0:
    print('No config files found in the default locations tried:')
    for path in config_paths:
        print(path)
    print('Creating default skeleton using default configuration')
    default_config_file = resource_filename(__name__, 'data/backend.ini')
    config.read(default_config_file)
else:
    print('Loaded configuration from: '),
    for path in found_paths:
        print(path)

backend_path = config.get("path", "backend")
if not os.path.exists(backend_path):
    print('Creating backend home directory: {0}'.format(backend_path))
    os.makedirs(backend_path)

# If still using default config file, copy it to backend_path
if default_config_file:
    shutil.copyfile(default_config_file,
                    os.path.join(backend_path, 'backend.ini'))

log_path = config.get("path", "log_dir")
if not os.path.exists(log_path):
    print('Creating logs directory: {0}'.format(log_path))
    os.makedirs(log_path)

data_path = config.get("path", "data_dir")
if not os.path.exists(data_path):
    print('Creating data directory: {0}'.format(data_path))
    os.makedirs(data_path)
