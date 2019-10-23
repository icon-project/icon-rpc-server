
[![Build Status](https://travis-ci.org/icon-project/icon-rpc-server.svg?branch=master)](https://travis-ci.org/icon-project/icon-rpc-server)
[![PyPI](https://img.shields.io/pypi/v/iconrpcserver.svg)](https://pypi.org/project/iconrpcserver)

# ICON RPC Server

This is intended to give an introduction ICON RPC Server. ICON RPC Server receives request messages from external clients, and send a response to clients. when receiving the message, ICON RPC Server checks the method of requests and transfer it to appropriate components (loopchain or ICON Service). ICON RPC Server also checks the basic syntax error of messages. 

- ICON RPC Server provides old version protocol

## Building source code
 First, clone this project. Then go to the project folder and create a user environment and run build script.
```
$ python3 -m venv venv        # Create a virtual environment.
$ source venv/bin/activate    # Enter the virtual environment.
(venv)$ make build            # run build
(venv)$ ls dist/              # check result wheel file
iconrpcserver-x.x.x-py3-none-any.whl
```

## Installation

This chapter will explain how to install ICON RPC Server on your system. 

### Requirements

ICON RPC Server development and execution requires following environments.

* OS: MacOS, Linux
    * Windows are not supported yet.
* Python
  * Make Virtual Env for Python 3.7.x

    **Now we support 3.7.x only. Please upgrade python version to 3.7.x.**

  * check your python version
    ```bash
    $ python3 -V
    ```
  * IDE: Pycharm is recommended.

### Setup on MacOS / Linux

```bash
$ python3 -m venv work      # Create a virtual environment.
# Install the ICON RPC Server
(work) $ pip install iconrpcserver
```

##  Reference

- [ICON JSON-RPC API v3](https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md)
- [ICON Commons](https://github.com/icon-project/icon-commons)  
- [Earlgrey](https://github.com/icon-project/earlgrey)

## License

This project follows the Apache 2.0 License. Please refer to [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.
