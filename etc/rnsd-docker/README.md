
# RNS TCP server
For encrypted connections and messages exchange.

## How to build
```bash
$ docker build . -t rnsd-docker:latest
```

## How to launch
* Docker `run` can be used to access a container and launch `rnsd` manually.
```bash
$ docker run rnsd-docker:latest
```
By default binds on `0.0.0.0:45454`. Use `--env CFG_RETICULUM_LISTEN_IP=X.X.X.X` and `--env CFG_RETICULUM_LISTEN_PORT=X` to overwrite.

* Or `docker-compose` can be invoked with the `docker-compose.yml` file.
```bash
$ docker-compose up
```

## How to connect
Use the TCPClient interface https://reticulum.network/manual/interfaces.html#tcp-client-interface
```text
  [[RNS rnsd-server]]
    type = TCPClientInterface
    interface_enabled = true
    target_host = 10.0.0.1
    target_port = 5000
    name = rnsd-server
    selected_interface_mode = 1
    configured_bitrate = None
```

