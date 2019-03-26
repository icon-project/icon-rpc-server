# ICON RPC Server

This is intended to give an introduction ICON RPC Server. ICON RPC Server receives request messages from external clients, and send a response to clients. when receiving the message, ICON RPC Server checks the method of requests and transfer it to appropriate components (loopchain or ICON Service). ICON RPC Server also checks the basic syntax error of messages. 

- ICON RPC Server provides old version protocol

## Building source code
 First, clone this project. Then go to the project folder and create a user environment and run build script.
```
$ virtualenv -p python3 venv  # Create a virtual environment.
$ source venv/bin/activate    # Enter the virtual environment.
(venv)$ ./build.sh            # run build script
(venv)$ ls dist/              # check result wheel file
iconrpcserver-1.0.0-py3-none-any.whl
```

## Installation

This chapter will explain how to install ICON RPC Server on your system. 

### Requirements

ICON RPC Server development and execution requires following environments.

* OS: MacOS, Linux
    * Windows are not supported yet.
* Python
  * Make Virtual Env for Python 3.6.5+ or 3.7.x (recommended version)

    **We will support 3.7.x only in future. Please upgrade python version to 3.7.x.**

  * check your python version
    ```bash
    $ python3 -V
    ```
  * IDE: Pycharm is recommended.

### Setup on MacOS / Linux

```bash
# Install the ICON RPC Server
(work) $ pip install iconrpcserver
```

##  Reference

- [ICON JSON-RPC API v3](https://github.com/icon-project/icon-rpc-server/blob/master/docs/icon-json-rpc-v3.md)
- [ICON Commons](https://github.com/icon-project/icon-commons)  
- [Earlgrey](https://github.com/icon-project/earlgrey)

## License

This project follows the Apache 2.0 License. Please refer to [LICENSE](https://www.apache.org/licenses/LICENSE-2.0) for details.
