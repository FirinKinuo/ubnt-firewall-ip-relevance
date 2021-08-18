from sys import path as sys_path
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(sys_path[0], 'config.env')
DOT_ENV_PATH = _env_path if _env_path.exists() else exit()

load_dotenv(DOT_ENV_PATH)
