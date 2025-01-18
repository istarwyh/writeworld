#!/bin/bash
PYTHONWARNINGS=ignore python -m pytest tests/test_translation_agent.py "$@"
