#!/bin/bash
 pyenv exec python3 -m debugpy --listen 5678 -m pytest $1 -k $2