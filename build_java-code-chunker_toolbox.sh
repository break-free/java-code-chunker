#!/bin/bash

# Create container
NAME=java-code-chunker
RUN="toolbox run --container $NAME"
toolbox rm --force $NAME || true
toolbox create --container $NAME

# Install applications
APPLICATIONS=" python3-devel python3-javalang "

## Install applications
$RUN sudo dnf install -y $APPLICATIONS;

## Install Python packages
$RUN sudo pip install --upgrade -r requirements.txt

