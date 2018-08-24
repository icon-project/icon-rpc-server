#!/usr/bin/env python
import os

from setuptools import setup, find_packages

version = os.environ.get('VERSION')

if version is None:
	with open(os.path.join('.', 'VERSION')) as version_file:
		version = version_file.read().strip()

requires = [
    "earlgrey",
    "iconcommons",
    "jsonschema",
    "requests==2.19.1",
    "jsonrpcserver==3.5.3",
    "sanic==0.7.0",
    "gunicorn == 19.7.1",
    "grpcio == 1.3.5",
    "grpcio-tools == 1.3.5",
    "protobuf == 3.5.1",
    "aiohttp == 3.0.9",
    "jsonrpcclient == 2.6.0",
    "secp256k1==0.13.2",
    "sanic-cors==0.9.4"
]

setup_options = {
    'name': 'iconrpcserver',
    'version': version,
    'description': 'ICON RPC Server',
    'long_description': open('README.md').read(),
    'long_description_content_type': 'text/markdown',
    'url': 'https://github.com/icon-project/icon-rpc-server',
    'author': 'ICON Foundation',
    'author_email': 'foo@icon.foundation',
    'packages': find_packages(exclude=['tests*', 'docs']),
    'package_data': {'iconrpcserver': ['icon_rpcserver_config.json']},
    'py_modules': ['iconrpcserver', ''],
    'license': "Apache License 2.0",
    'install_requires': requires,
    'test_suite': 'tests',
    'entry_points': {
        'console_scripts': [
            'iconrpcserver=iconrpcserver:main'
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
