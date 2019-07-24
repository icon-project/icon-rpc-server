help:
	@awk '/^#/{c=substr($$0,3);next}c&&/^[[:alpha:]][-_[:alnum:]]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}' $(MAKEFILE_LIST) | column -s: -t

SHELL := /bin/bash

PROTO_VENV := proto_venv

# Generate python gRPC proto
generate-proto:
	@python3 -m venv ${PROTO_VENV}
	@source ${PROTO_VENV}/bin/activate && pip3 install -U grpcio==1.20.1 grpcio-tools==1.20.1 protobuf==3.7.0

	@echo "Generating python grpc code from proto into > " `pwd`
	@source ${PROTO_VENV}/bin/activate && python3 -m grpc.tools.protoc -I'./iconrpcserver/protos' \
		--python_out='./iconrpcserver/protos' \
		--grpc_python_out='./iconrpcserver/protos' \
		'./iconrpcserver/protos/loopchain.proto'
	@rm -rf ${PROTO_VENV}

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
	@if [ "$$(python -c 'import sys; print(sys.version_info[0])')" != 3 ]; then\
		@echo "The script should be run on python3.";\
		exit -1;\
	fi

	python3 setup.py bdist_wheel
