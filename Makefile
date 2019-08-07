SHELL := /bin/bash

help:
	@awk '/^##/{c=substr($$0,3);next}c&&/^[[:alpha:]][-_[:alnum:]]+:/{print substr($$1,1,index($$1,":")),c}1{c=0}'\
	 $(MAKEFILE_LIST) | column -s: -t

## Generate python gRPC proto
all: generate-proto

generate-proto:
	@echo "Generating python grpc code from proto"
	@python3 setup.py build_proto_modules

## Run unittest
test:
	@python3 -m unittest discover -v tests/ || exit -1

## Clean all - clean-build, clean-proto
clean: clean-build clean-proto

clean-build:
	@$(RM) -r build/ dist/
	@$(RM) -r .eggs/ eggs/ *.egg-info/

clean-proto:
	@$(RM) iconrpcserver/protos/*pb*.py

## Build python wheel
build: clean-build clean-proto
	@if [ "$$(python -c 'import sys; print(sys.version_info[0])')" != 3 ]; then \
		@echo "The script should be run on python3."; \
		exit -1; \
	fi

	@if ! python -c 'import wheel' &> /dev/null; then \
		pip install wheel; \
	fi

	python3 setup.py bdist_wheel
