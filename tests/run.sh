#!/bin/bash

python -m flake8 joker/
python -m pytest -vs tests/test_*.py
