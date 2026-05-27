import argparse
import datetime
import glob
import json
import logging
import os
import uuid

from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth

from jinja2 import Environment, Template
from jinja2 import BaseLoader
from importlib.resources import files

from auto_illumina_run_qc_check.config import load_config


def _get_access_token(email_config: dict):
    """
    Get an access token from the MCMS auth service.

    :param config: A dict containing the MCMS auth service URL, client ID, and client secret.
                   Required keys are: ['auth_url', 'client_id', 'client_secret'].
    :type config: dict
    :return: A dict containing the access token and other info.
             Keys are: ['access_token', 'token_type', 'expires_in', 'timestamp_token_received'].
    :rtype: dict
    """
    auth_url = email_config['auth_url']
    client_id = email_config['client_id']
    client_secret = email_config['client_secret']

    auth = HTTPBasicAuth(client_id, client_secret)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": client_id,
        "grant_type": "client_credentials",
    }
    response = requests.post(auth_url, data=data, headers=headers, auth=auth)
    response_json = {}
    if response.status_code == 200:
        response_json = response.json()
        timestamp = datetime.datetime.now().isoformat()
        response_json['timestamp_token_received'] = timestamp
    else:
        logging.error(json.dumps({
            'event_type': 'email_authentication_failed',
            'status_code': response.status_code,
            'message': response.text
        }))
        return None

    access_token = response_json['access_token']

    return access_token


def _prepare_email_body(email_data: dict, notification_config: dict):
    """
    """
    message_id = str(uuid.uuid4())
    sender_email = notification_config['sender_email']
    recipients = notification_config['recipient_email_addresses']
    sequencing_run_id = email_data['sequencing_run_id']
    subject = f"[auto-illumina-run-qc-check] QC Check Complete: {sequencing_run_id}"

    template_path = files("auto_illumina_run_qc_check.templates").joinpath("qc_check_complete_email.html")
    template_text = template_path.read_text()

    env = Environment(loader=BaseLoader())
    template = env.from_string(template_text)
    
    body = template.render(email_data)
    
    email_request_body = {
        "messageId": message_id,
        "from": sender_email,
        "email": {
            "to": recipients,
            "subject": subject,
            "bodyType": "html",
            "body": body,
        }
    }

    return email_request_body


def _collect_email_data(qc_check_complete_path):
    """
    """
    email_data = {}
    with open(qc_check_complete_path, 'r') as f:
        email_data = json.load(f)

    return email_data
    

def send_notification_email(qc_check_complete_path: Path, notification_config: dict):
    """
    Collect relevant data from an analysis output dir
    """
    access_token = _get_access_token(notification_config)
    if not access_token:
        return None

    email_info = _collect_email_data(qc_check_complete_path)
    sequencing_run_id = email_info['sequencing_run_id']
    email_body = _prepare_email_body(email_info, notification_config)
        
    email_url = notification_config['email_url']
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token,
    }

    response = requests.post(email_url, data=json.dumps(email_body), headers=headers)
    
    # print(json.dumps(response.json(), indent=2))


def main(args):
    config = load_config(args.config)
    if 'notification' not in config:
        logging.error("Failed to load notification config")
        exit(-1)
    
    send_notification_email(args.qc_check_complete_file, config['notification'])
    logging.info(json.dumps({"event_type": "email_notification_sent", "qc_check_complete_file": os.path.abspath(args.qc_check_complete_file)}))
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--qc-check-complete-file')
    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    main(args)
