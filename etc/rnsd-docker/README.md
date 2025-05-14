
# RNS TCP server
For encrypted connections and messages exchange.

## How to build
```bash
$ docker build . -t rnsd-docker:latest
```

## How to launch
```bash
$ docker run rnsd-docker:latest
```

By default binds on `0.0.0.0:45454`. Use `--env CFG_RETICULUM_LISTEN_IP=X.X.X.X` and `--env CFG_RETICULUM_LISTEN_PORT=X` to overwrite.

## How to connect
Use the TCPClient interface https://reticulum.network/manual/interfaces.html#tcp-client-interface

