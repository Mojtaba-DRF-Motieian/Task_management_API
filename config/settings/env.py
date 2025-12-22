from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
# env.py → settings → config → config

env = environ.Env()
env.read_env(BASE_DIR / ".env")
