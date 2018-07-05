#!/usr/bin/env python

from setuptools import setup, find_packages
from rest import __version__

requires = [
    "setproctitle",
    "requests==2.19.1",
    "jsonrpcserver==3.5.3",
    "sanic==0.7.0",
    "gunicorn == 19.7.1",
    "grpcio == 1.3.5",
    "grpcio-tools == 1.3.5",
    "protobuf == 3.5.1",
    "aiohttp == 3.0.9",
    "jsonrpcclient == 2.5.2",
    "secp256k1==0.13.2"
]

setup_options = {
    'name': 'rest',
    'version': __version__,
    'description': '`Rest server` for LoopChain',
    'author': 'ICON foundation',
    'author_email': 'foo@icon.foundation',
    'packages': find_packages(exclude=['tests*', 'docs']),
    'package_data': {'rest': ['rest_config.json']},
    'py_modules': ['rest'],
    'license': "Apache License 2.0",
    'install_requires': requires,
    'test_suite': 'tests',
    'entry_points': {
        'console_scripts': [
            'rest=rest:main'
        ],
    },
    'classifiers': [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6'
    ]
}

setup(**setup_options)
