# RNS tools
This package provides a small range of RNS tools, driven by my curiosity about Reticulum stack.

## Docker
This package can be built and ran with docker.

```bash
$ docker build . -t rns_tools:latest
$ docker run rns_tools:latest --follow-anounces
```

## Features

### LXMF

#### Announce an LXMF peer
```
$ python -m rns_tools --announce --lxmf --lxmf-display-name "LXMF_PEER"
```

#### Receive messages
```
$ uv run rns_tools --lxmf
```

#### Send a message 
```bash
$ uv run rns_tools --lxmf --lxmf-peer xxxxxxxxxxxxxx  --lxmf-message "test!"
```

### Link File exchange
A server with an announced destination serves a directory. A client connect to it and requests a filename, which must exist inside the directory.

#### Server
```bash$
$ uv run rns_tools --announce -s served_dir/
```

#### Client
```bash
$ uv run rns_tools -d xxxxxxxxxxxxxx -F file.txt
```

