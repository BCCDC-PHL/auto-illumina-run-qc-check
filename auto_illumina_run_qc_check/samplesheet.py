import csv
import glob
import json
import logging
import os

from pathlib import Path

import auto_illumina_run_qc_check.instrument as instrument
from auto_illumina_run_qc_check.model import InstrumentType

from typing import Optional, Iterator

def find_samplesheet_path(run_dir: Path) -> Optional[Path]:
    """
    Given a run directory path, find the path to the SampleSheet.csv file that can be used
    to summarize num samples by project ID.
    
    :param run_dir: Path to the run directory
    :return: Path to the SampleSheet.csv file, or None if not found.
    """
    samplesheet_path = None
    run_id = run_dir.name
    instrument_type = instrument.determine_instrument_type(run_id)

    samplesheet_paths_glob = None
    if instrument_type == 'nextseq':
        samplesheet_paths_glob = str(run_dir / "Analysis/*/Data/SampleSheet*.csv")
    elif instrument_type == 'miseq':
        samplesheet_paths_glob = str(run_dir / "Alignment_*/*/SampleSheetUsed.csv")
    elif instrument_type == 'i100':
        samplesheet_paths_glob = str(run_dir / "Analysis/*/inputs/SampleSheet*.csv")
    else:
        return samplesheet_path

    samplesheets_found = glob.glob(samplesheet_paths_glob)
    if len(samplesheets_found) == 0:
        return None
    last_samplesheet = samplesheets_found[-1]

    if os.path.exists(last_samplesheet):
        samplesheet_path = Path(os.path.abspath(last_samplesheet))

    return samplesheet_path

def _read_until_next_section(file_iterator: Iterator) -> Iterator[str]:
    """
    Read lines until we find a [tag]
    """
    for line in file_iterator:
        # If we hit a new section tag, stop yielding lines
        if line.strip().startswith("[") and line.strip().rstrip(',').endswith("]"):
            break
        yield line


def _parse_samplesheet_miseq(samplesheet_path: Path) -> dict:
    """
    Parse a MiSeq SampleSheet to a dict.
    """
    target_section_tag = "[Data]"
    project_id_field = "Sample_Project"
    parsed_samplesheet = {'num_samples_by_project_id': {}}

    with open(samplesheet_path, 'r', newline="", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(target_section_tag):
                break
        bounded_stream = _read_until_next_section(f)
        reader = csv.DictReader(bounded_stream)
        for row in reader:
            project_id = row.get(project_id_field, None)
            if project_id:
                if project_id not in parsed_samplesheet['num_samples_by_project_id']:
                    parsed_samplesheet['num_samples_by_project_id'][project_id] = 1
                else:
                    parsed_samplesheet['num_samples_by_project_id'][project_id] += 1

    return parsed_samplesheet


def _parse_samplesheet_nextseq(samplesheet_path: Path) -> dict:
    """
    Parse a NextSeq SampleSheet to a dict.
    """
    target_section_tag = "[Cloud_Data]"
    project_id_field = "ProjectName"
    parsed_samplesheet = {'num_samples_by_project_id': {}}

    with open(samplesheet_path, 'r', newline="", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(target_section_tag):
                break
        bounded_stream = _read_until_next_section(f)
        reader = csv.DictReader(bounded_stream)
        for row in reader:
            project_id = row.get(project_id_field, None)
            if project_id:
                if project_id not in parsed_samplesheet['num_samples_by_project_id']:
                    parsed_samplesheet['num_samples_by_project_id'][project_id] = 1
                else:
                    parsed_samplesheet['num_samples_by_project_id'][project_id] += 1

    return parsed_samplesheet


def _parse_samplesheet_i100(samplesheet_path: Path) -> dict:
    """
    Parse an i100 SampleSheet to a dict.
    """
    target_section_tag = "[Cloud_Data]"
    project_id_field = "ProjectName"
    parsed_samplesheet = {'num_samples_by_project_id': {}}

    with open(samplesheet_path, 'r', newline="", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(target_section_tag):
                break
        bounded_stream = _read_until_next_section(f)
        reader = csv.DictReader(bounded_stream)
        for row in reader:
            project_id = row.get(project_id_field, None)
            if project_id:
                if project_id not in parsed_samplesheet['num_samples_by_project_id']:
                    parsed_samplesheet['num_samples_by_project_id'][project_id] = 1
                else:
                    parsed_samplesheet['num_samples_by_project_id'][project_id] += 1

    return parsed_samplesheet

    
def parse_samplesheet(samplesheet_path: Path, instrument_type: InstrumentType):
    """
    Parse a SampleSheet, given the path to the SampleSheet file and the Instrument type.
    """
    parsed_samplesheet = {}
    if instrument_type == 'nextseq':
        parsed_samplesheet = _parse_samplesheet_nextseq(samplesheet_path)
    elif instrument_type == 'miseq':
        parsed_samplesheet = _parse_samplesheet_miseq(samplesheet_path)
    elif instrument_type == 'i100':
        parsed_samplesheet = _parse_samplesheet_i100(samplesheet_path)
    
    return parsed_samplesheet
