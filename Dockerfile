FROM archlinux:latest

# Base System

# - install packages
RUN pacman -Syu --noconfirm \
    base-devel \
    glibc \
    wget \
    curl \
    zip \
    unzip \
    ripgrep \
    file \
    sudo \
    git \
    openssl \
    gdb \
    openbsd-netcat \
    openssh \
    vim \
    docker

# - setup timezone
ENV TZ=Asia/Taipei

# - setup locale
COPY ./sandbox/locale.gen   /etc/locale.gen
COPY ./sandbox/locale.conf  /etc/locale.conf
RUN chmod 644 /etc/locale.gen
RUN chmod 644 /etc/locale.conf
RUN locale-gen

ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

# - setup sudo
COPY ./sandbox/sudoers /etc/sudoers
RUN chmod 440 /etc/sudoers

# - setup user:agent
RUN useradd -m agent
RUN usermod -aG wheel agent
RUN usermod -aG docker agent

# - setup yay
USER agent
RUN cd ~ && \
    git clone https://aur.archlinux.org/yay.git && \
    cd yay && \
    makepkg -si --noconfirm
USER root

# - setup docker compose
USER agent
RUN DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker} && \
    mkdir -p $DOCKER_CONFIG/cli-plugins && \
    curl -SL https://github.com/docker/compose/releases/download/v5.0.1/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose && \
    chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
USER root

# Programming Languages

RUN pacman -Syu --noconfirm \
    ruby \
    nodejs npm \
    python3 python-uv

# - python packages
RUN pacman -Syu --noconfirm \
    python-requests

# AI Agents

USER agent

RUN yay -Syy --noconfirm --mflags "--nocheck" python-mcp

# - install opencode
RUN cd ~ && curl -fsSL https://opencode.ai/install | bash

# - install codex
RUN sudo npm install -g @openai/codex

USER root

# Pwn tools

RUN pacman -Syy --noconfirm python-pwntools \
    checksec

RUN gem install one_gadget seccomp-tools --no-user-install

USER agent
RUN cd ~ && git clone https://github.com/pwndbg/pwndbg.git && cd ~/pwndbg && yes | ./setup.sh
USER root

# user & workdir

USER agent
WORKDIR /home/agent/challenge
