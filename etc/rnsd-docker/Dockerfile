FROM python:3.11-bookworm

ENV TCP_SERVER_LISTEN_IP="0.0.0.0"
ENV TCP_SERVER_LISTEN_PORT=45454
ENV CONFIG_FILE_PATH=".reticulum/config"

RUN apt-get update \
    && apt-get install -y sudo pipx build-essential \
    && apt-get clean \ 
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash runner
RUN usermod -aG sudo runner
RUN echo "%sudo   ALL=(ALL:ALL) NOPASSWD:ALL" > /etc/sudoers

COPY --chmod=0755 entrypoint.sh /entrypoint.sh

USER runner
WORKDIR /home/runner

RUN mkdir -p .reticulum/
COPY config $CONFIG_FILE_PATH

RUN pipx install rns \
      && pipx ensurepath

ENTRYPOINT ["/entrypoint.sh"]
CMD ["rnsd", "-v"]
