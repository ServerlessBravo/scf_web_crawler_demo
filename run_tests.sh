#!/bin/sh

if [ -z "$1" ]; then
    pyenv exec python3 -m pytest -k 'not TestForEdgeCases'
    pyenv exec python3 -m pytest -k 'TestForEdgeCases'
else
    pyenv exec python3 -m pytest "$1" -k "$2"
fi