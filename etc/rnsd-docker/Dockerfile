FROM python:3.11-bookworm

ENV CONFIG_FILE_PATH=".reticulum/config"
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y sudo pipx build-essential \
    && apt-get clean \ 
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash runner
RUN usermod -aG sudo runner
RUN usermod -aG dialout runner
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
