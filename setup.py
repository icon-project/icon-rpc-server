#!/usr/bin/env python
import os

from setuptools import setup, find_packages

version = os.environ.get('VERSION')

if version is None:
    with open(os.path.join('.', 'VERSION')) as version_file:
        version = version_file.read().strip()

install_requires = []

with open('requirements.txt') as requirements:
    for line in requirements:
        req = line.strip()
        install_requires.append(req)


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
    'package_dir': {'': '.'},
    'package_data': {'iconrpcserver': ['icon_rpcserver_config.json']},
    'py_modules': ['iconrpcserver', ''],
    'license': "Apache License 2.0",
    'install_requires': install_requires,
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
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ]
}

setup(**setup_options)
