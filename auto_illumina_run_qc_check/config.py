import csv
import json
import os


def load_config(config_path: str) -> dict[str, object]:
    """
    Load the application config file.

    :param config_path: Path to config file.
    :type config_path: str
    :return: A dictionary containing configuration data.
    :rtype: dict[str, object]
    """
    config = {}
    with open(config_path, 'r') as f:
        config = json.load(f)

    config['excluded_runs'] = []
    if 'excluded_runs_list' in config and os.path.exists(config['excluded_runs_list']):
        with open(config['excluded_runs_list'], 'r') as f:
            for line in f.readlines():
                config['excluded_runs'].append(line.strip())

    config['projects'] = []
    if 'projects_definition_file' in config and os.path.exists(config['projects_definition_file']):
        with open(config['projects_definition_file'], 'r') as f:
            reader = csv.DictReader(f, dialect='unix')
            for row in reader:
                config['projects'].append(row)

    return config
