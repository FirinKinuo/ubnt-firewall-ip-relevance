from pathlib import Path
from sys import path as sys_path

_env_path = Path(sys_path[0], 'config.env')
DOT_ENV_PATH = _env_path if _env_path.exists() else exit()
