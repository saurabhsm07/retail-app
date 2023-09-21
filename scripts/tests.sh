#!/bin/bash

FLASK_APP="src/entrypoints/flask_app.py"
flask run --host=0.0.0.0 --port=80 &
pytest --cov=src