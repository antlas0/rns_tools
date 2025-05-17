# RNS tool
This package provides a small range of RNS tools,driven by my curiosity about Reticulum stack.

## Docker
This package can be built and ran with docker.

```bash
$ docker build . -t rns_server:latest
$ docker run rns_server:latest --follow-anounces
```

## Features

### Displaying incoming announces

```bash
$ python -m rns_server --follow-announces
```

### LXMF

#### Receive messages
```
$ python -m rns_server --lxmf
```

#### Send a message 
```bash
$ python -m rns_server --lxmf --lxmf-peer xxxxxxxxxxxxxx  --lxmf-message "test!"
```

### Link File exchange
A server with an announced destination serves a directory. A client connect to it and requests a filename, which must exist inside the directory.

#### Server
```bash
$ python -m rns_server --announce -s served_dir/
```

#### Client
```bash
$ python -m rns_server -d xxxxxxxxxxxxxx -F file.txt
```

