#!/bin/bash

lt -p 8000 -s thatcomputerscientist & python3 manage.py runserver && fg