import json
import os


def load_config():
    # Get the current directory of the script
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the config.json file
    config_path = os.path.join(current_dir, "../config.json")

    # Load JSON configuration
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        print("JSON loaded successfully.")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)
    return config
