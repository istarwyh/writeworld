#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os
from pathlib import Path

from agentuniverse.agent_serve.web.web_booster import start_web_server
from agentuniverse.base.agentuniverse import AgentUniverse


class ServerApplication:
    """Server application for WriteWorld."""

    @classmethod
    def start(cls) -> None:
        """Start the server application."""
        # Get the project root directory (two levels up from this file)
        project_root = Path(__file__).parent.parent
        config_path = project_root / 'config' / 'config.toml'
        AgentUniverse().start(config_path=str(config_path))
        start_web_server()


if __name__ == "__main__":
    # Change working directory to bootstrap to satisfy agentuniverse's requirement
    os.chdir(Path(__file__).parent)
    ServerApplication.start()
