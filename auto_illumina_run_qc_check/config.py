import csv
import json
import logging
import os

from auto_illumina_run_qc_check.model import Config

log = logging.getLogger(__name__)

def load_config(config_path: os.PathLike) -> Config:
    """
    Load the application config file.

    :param config_path: Path to config file.
    :type config_path: Path
    :return: A dictionary containing configuration data.
    :rtype: auto_illumina_run_qc_check.dataclasses.Config
    """
    config_dict = {}

    with open(config_path, 'r') as f:
        config_dict = json.load(f)

    config_dict['excluded_runs'] = []
    if 'excluded_runs_list' in config_dict and os.path.exists(config_dict['excluded_runs_list']):
        with open(config_dict['excluded_runs_list'], 'r') as f:
            for line in f.readlines():
                config_dict['excluded_runs'].append(line.strip())

    config_dict['projects'] = []
    if 'projects_definition_file' in config_dict and os.path.exists(config_dict['projects_definition_file']):
        with open(config_dict['projects_definition_file'], 'r') as f:
            reader = csv.DictReader(f, dialect='unix')
            for row in reader:
                config_dict['projects'].append(row)

    if 'notification' in config_dict:
        notification_system_config_file = config_dict['notification'].get('system_config_file', None)
        if notification_system_config_file and os.path.exists(notification_system_config_file):
            with open(notification_system_config_file, 'r') as f:
                notification_system_config = json.load(f)
                for k, v in notification_system_config.items():
                    config_dict['notification'][k] = v

    config = Config(**config_dict)

    return config
