#!/bin/bash

# Ignore this file. This is only for updating the docker build on dockerhub.
sudo docker buildx build --no-cache --push --platform linux/amd64,linux/arm64/v8 --tag 0xprototype/subkiller:20220115 --tag 0xprototype/subkiller:v1 --tag 0xprototype/subkiller:latest .
