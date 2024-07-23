import json
import os
import logging

logger = logging.getLogger(__name__)


def load_config():
    logger.info("Loading configuration")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "../config/config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
    logger.debug(f"Configuration loaded: {config}")
    return config
