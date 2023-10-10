import json
from pathlib import Path
from typing import Dict, Any

import yaml


def parse_config(config_path: str) -> Dict[str, Any]:
    """Loads config file into a dictionary.

    Args:
        config_path: Path to the config file. Supports: yaml, json.

    Returns:
        Config file converted to dictionary.
    """
    config_file = Path(config_path)
    if not config_file.is_file():
        raise ValueError('Cannot find cfg file at path %s.' % config_path)
    ext = config_file.suffix
    if ext not in ['.yaml', '.json']:
        raise ValueError(f'Unknown extension: {ext}.')

    with config_file.open() as file:
        config = yaml.load(file, Loader=yaml.FullLoader) if ext == '.yaml' else json.load(file)

    return config
