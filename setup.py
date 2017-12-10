"""Setup tools configuration file"""
from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,

    package_data={
        'backend': ['data/*',],
    },

    install_requires=['bottle==0.12.13',],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'backend = backend.server:runserver',
        ]
    }
)
