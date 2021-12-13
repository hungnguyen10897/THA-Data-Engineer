#!/bin/bash
gunicorn run:app -w 10 --threads 10 -b 0.0.0.0:8080