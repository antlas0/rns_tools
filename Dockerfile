FROM python:3.11-bookworm

RUN apt-get update \
    && apt-get install -y sudo \
    && apt-get clean \ 
    && rm -rf /var/lib/apt/lists/*

RUN useradd -ms /bin/bash runner
RUN usermod -aG sudo runner

WORKDIR /home/runner
USER runner
RUN mkdir .reticulum
COPY rns_server rns_server
COPY config .reticulum/config
COPY setup.py setup.py
COPY requirements.txt requirements.txt

RUN python -m venv --copies .venv
ENV PATH="/home/runner/.venv:$PATH"
RUN python -m pip install -r requirements.txt
RUN python -m pip install . --user

ENTRYPOINT [ "python", "-m", "rns_tools" ]
