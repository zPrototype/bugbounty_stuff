#!/bin/bash

dataset=$1
host=$2

zcat $dataset | strings | grep $host | cut -d '\' -f 8 | grep -v $host \
| tr ":" " " | awk '{print $3}' | tr '"' ' ' | awk '{print $1}' 
