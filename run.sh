#!/bin/sh
export FLASK_APP=chatbot.py
python -m flask --debug run -h 0.0.0.0