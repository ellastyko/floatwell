import tomli
from utils.helpers import resource_path

config = None

if config is None:
    config_file = resource_path("config.toml")
    with open(config_file, "rb") as f:
        config = tomli.load(f)
