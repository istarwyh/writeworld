#!/bin/bash
PYTHONWARNINGS=ignore python -m pytest tests/unit/core/agent/translation_agent_case/test_translation_agent.py "$@"
