#!/usr/bin/env python
import os

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.develop import develop as _develop

version = os.environ.get('VERSION')

if version is None:
    with open(os.path.join('.', 'VERSION')) as version_file:
        version = version_file.read().strip()

with open('requirements.txt') as requirements:
    requires = list(requirements)


def generate_proto():
    import grpc_tools.protoc

    proto_path = './iconrpcserver/protos'
    proto_file = os.path.join(proto_path, 'loopchain.proto')

    grpc_tools.protoc.main([
        'grcp_tools.protoc',
        f'-I{proto_path}',
        f'--python_out={proto_path}',
        f'--grpc_python_out={proto_path}',
        f'{proto_file}'
    ])


class build_py(_build_py):
    def run(self):
        generate_proto()
        _build_py.run(self)


class develop(_develop):
    def run(self):
        generate_proto()
        _develop.run(self)


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
    'cmdclass': {
        'build_py': build_py,
        'develop': develop
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
