#!/bin/bash

cd $(echo "$(dirname "$(realpath "$0")")")
cd ..
python3 main.py
