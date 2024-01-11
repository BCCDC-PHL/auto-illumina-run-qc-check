import datetime
import glob
import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
import time
import uuid

from typing import Iterator, Optional

import auto_illumina_run_qc_check.parsers as parsers

def find_run_dirs(config, check_upload_complete=True):
    """
    Find sequencing run directories under the 'run_parent_dirs' listed in the config.

    :param config: Application config.
    :type config: dict[str, object]
    :param check_upload_complete: Check for presence of 'upload_complete.json' file.
    :type check_upload_complete: bool
    :return: Run directory. Keys: ['sequencing_run_id', 'path', 'instrument_type']
    :rtype: Iterator[Optional[dict[str, str]]]
    """
    miseq_run_id_regex = "\d{6}_M\d{5}_\d+_\d{9}-[A-Z0-9]{5}"
    nextseq_run_id_regex = "\d{6}_VH\d{5}_\d+_[A-Z0-9]{9}"
    run_parent_dirs = config['run_parent_dirs']

    for run_parent_dir in run_parent_dirs:
        subdirs = os.scandir(run_parent_dir)

        for subdir in subdirs:
            run_id = subdir.name
            matches_miseq_regex = re.match(miseq_run_id_regex, run_id)
            matches_nextseq_regex = re.match(nextseq_run_id_regex, run_id)
            instrument_type = 'unknown'
            if matches_miseq_regex:
                instrument_type = 'miseq'
            elif matches_nextseq_regex:
                instrument_type = 'nextseq'

            run_parameters = {}
            run_parameters_path = os.path.join(subdir, 'RunParameters.xml')
            if os.path.exists(run_parameters_path):
                run_parameters = parsers.parse_run_parameters_xml(run_parameters_path, instrument_type)
                    
            upload_complete = os.path.exists(os.path.join(subdir, 'upload_complete.json'))
            not_excluded = False
            if 'excluded_runs' in config:
                not_excluded = not run_id in config['excluded_runs']

            qc_check_complete = os.path.exists(os.path.join(subdir, 'qc_check_complete.json'))

            conditions_checked = {
                "is_directory": subdir.is_dir(),
                "matches_illumina_run_id_format": ((matches_miseq_regex is not None) or
                                                   (matches_nextseq_regex is not None)),
                "upload_complete": upload_complete,
                "qc_check_not_complete": not qc_check_complete,
                "not_excluded": not_excluded,
            }

            conditions_met = list(conditions_checked.values())
            run = {}
            if all(conditions_met):
                logging.info(json.dumps({"event_type": "run_directory_found", "sequencing_run_id": run_id, "run_directory_path": os.path.abspath(subdir.path)}))
                run['path'] = os.path.abspath(subdir.path)
                run['sequencing_run_id'] = run_id
                run['instrument_type'] = instrument_type
                run['run_parameters'] = run_parameters
                yield run
            else:
                logging.debug(json.dumps({"event_type": "directory_skipped", "run_directory_path": os.path.abspath(subdir.path), "conditions_checked": conditions_checked}))
                yield None


def scan(config: dict[str, object]) -> Iterator[Optional[dict[str, object]]]:
    """
    Scanning involves looking for all existing runs and storing them to the database,
    then looking for all existing symlinks and storing them to the database.
    At the end of a scan, we should be able to determine which (if any) symlinks need to be created.

    :param config: Application config.
    :type config: dict[str, object]
    :return: A run directory to analyze, or None
    :rtype: Iterator[Optional[dict[str, object]]]
    """
    logging.info(json.dumps({"event_type": "scan_start"}))
    for run_dir in find_run_dirs(config):    
        yield run_dir


def qc_check(config, run):
    """
    Initiate an analysis on one directory of fastq files.

    :param config: Application config.
    :type config: dict[str, object]
    :param run: Run directory. Keys: ['sequencing_run_id', 'path', 'instrument_type']
    :type run: dict[str, str]
    :return: None
    :rtype: None
    """
    run_id = run['sequencing_run_id']

    interop_command = [
        'interop_summary',
        run['path'],
        '--csv=1',
    ]

    logging.info(json.dumps({"event_type": "qc_check_started", "sequencing_run_id": run_id, "interop_command": " ".join(interop_command)}))
    timestamp_qc_check_started = datetime.datetime.now().isoformat()
    
    try:
        qc_check_complete = False
        interop_result = subprocess.run(interop_command, capture_output=True, check=True, text=True)
        if interop_result.returncode == 0:
            qc_check_complete = True
            timestamp_qc_check_completed = datetime.datetime.now().isoformat()
        logging.info(json.dumps({"event_type": "qc_check_completed", "sequencing_run_id": run_id, "interop_command": " ".join(interop_command)}))
    except subprocess.CalledProcessError as e:
        logging.error(json.dumps({"event_type": "qc_check_failed", "sequencing_run_id": run_id, "interop_command": " ".join(interop_command)}))

    if qc_check_complete:
        summary_lines = interop_result.stdout.splitlines()
        qc_metrics = parsers.parse_interop_summary(summary_lines)
        qc_metrics_output_path = os.path.join(run['path'], run_id + '_qc_metrics.json')
        with open(qc_metrics_output_path, 'w') as f:
            json.dump(qc_metrics, f, indent=2)
            f.write("\n")
        qc_check_result = {}
        qc_check_result['checked_metrics'] = []
        for qc_threshold in config['qc_thresholds']:
            instrument_type_matches = qc_threshold.get('instrument_type', '').lower() == run['instrument_type']
            instrument_type_not_specified = 'instrument_type' not in qc_threshold
            flowcell_version_matches = qc_threshold.get('flowcell_version', '') == run['run_parameters'].get('flowcell_version', None)
            flowcell_version_not_specified = 'flowcell_version' not in qc_threshold
            qc_threshold_application_conditions_met = [
                (instrument_type_matches or instrument_type_not_specified),
                (flowcell_version_matches or flowcell_version_not_specified),
            ]
            if all(qc_threshold_application_conditions_met):
                metric = qc_threshold['metric']
                threshold = qc_threshold['threshold']
                checked_metric = {}
                checked_metric['metric'] = metric
                checked_metric['value'] = qc_metrics[metric]
                checked_metric['threshold'] = threshold
                checked_metric['pass_above_or_below'] = qc_threshold['pass_above_or_below']
                if qc_threshold['pass_above_or_below'] == 'above':
                    if qc_metrics[metric] >= threshold:
                        checked_metric['pass_fail'] = "PASS"
                    else:
                        checked_metric['pass_fail'] = "FAIL"
                elif qc_threshold['pass_above_or_below'] == 'below':
                    if qc_metrics[metric] <= threshold:
                        checked_metric['pass_fail'] = "PASS"
                    else:
                        checked_metric['pass_fail'] = "FAIL"
                qc_check_result['checked_metrics'].append(checked_metric)

        qc_check_result['overall_pass_fail'] = "FAIL"
        qc_pass_conditions_met = [m['pass_fail'] == "PASS" for m in qc_check_result['checked_metrics']]
        if all(qc_pass_conditions_met):
            qc_check_result['overall_pass_fail'] = "PASS"
        qc_check_result['sequencing_run_id'] = run_id
        qc_check_result['instrument_type'] = run['instrument_type']
        qc_check_result['run_parameters'] = run['run_parameters']
        qc_check_result['timestamp_qc_check_started'] = timestamp_qc_check_started
        qc_check_result['timestamp_qc_check_completed'] = timestamp_qc_check_completed
        qc_check_complete_output_path = os.path.join(run['path'], 'qc_check_complete.json')
        with open(qc_check_complete_output_path, 'w') as f:
            json.dump(qc_check_result, f, indent=2)
            f.write("\n")
        logging.info(json.dumps({"event_type": "qc_check_complete", "sequencing_run_id": run_id, "qc_check_result": qc_check_result['overall_pass_fail']}))
