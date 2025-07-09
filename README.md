# RNS tools
This package provides a small range of RNS tools, driven by my curiosity about Reticulum stack.

## Docker
This package can be built and ran with docker.

```bash
$ docker build . -t rns_tools:latest
$ docker run rns_tools:latest --follow-anounces
```

## RNode interface using Docker
For RNode interface, check this [README.md](https://github.com/antlas0/rns_tools/blob/9c0ee27261b857ecf39be709ec67e4ec0e4238ca/etc/rnsd-docker/README.md) file.

To create a TCP server to which TCPInterfaces can connect, check this [README.md](https://github.com/antlas0/rns_tools/tree/4c4aca1df67e631ccc1f03c64cb6da66602bed88/etc/rnsd-docker) file.

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

