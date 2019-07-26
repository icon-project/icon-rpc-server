SHELL := /bin/bash

help:
	@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][-_[:alnum:]]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' $(MAKEFILE_LIST) | column -s: -t

all: generate-proto

# Generate python gRPC proto
generate-proto:
	@echo "Generating python grpc code from proto into > " `pwd`
	python3 -m grpc_tools.protoc -I'./iconrpcserver/protos' \
		--python_out='./iconrpcserver/protos' \
		--grpc_python_out='./iconrpcserver/protos' \
		'./iconrpcserver/protos/loopchain.proto'

# Run unittest
test:
	@python3 -m unittest discover -v tests/ || exit -1

# Clean all - clean-build
clean: clean-build

clean-build:
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info
	@rm -rf .eggs/

# build
build: clean-build
	@if [ "$$(python -c 'import sys; print(sys.version_info[0])')" != 3 ]; then \
		@echo "The script should be run on python3."; \
		exit -1; \
	fi

	@if ! python -c 'import wheel' &> /dev/null; then \
		pip install wheel; \
	fi

	@if ! python -c 'import grpc_tools' &> /dev/null; then \
		pip install grpcio==1.20.1; \
		pip install grpcio-tools==1.20.1; \
		pip install protobuf==3.7.0; \
	fi

	python3 setup.py bdist_wheel
