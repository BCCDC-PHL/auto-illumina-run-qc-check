import csv
import glob
import json
import logging
import os

from pathlib import Path

import auto_illumina_run_qc_check.instrument as instrument

from typing import Optional

def find_samplesheet_path(run_dir: Path) -> Optional[Path]:
    """
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

    print(instrument_type)
    samplesheets_found = glob.glob(samplesheet_paths_glob)
    if len(samplesheets_found) == 0:
        return None
    last_samplesheet = samplesheets_found[-1]

    if os.path.exists(last_samplesheet):
        samplesheet_path = Path(os.path.abspath(last_samplesheet))

    return samplesheet_path

def _read_until_next_section(file_iterator):
    """
    """
    for line in file_iterator:
        # If we hit a new section tag, stop yielding lines
        if line.strip().startswith("[") and line.strip().endswith("]"):
            break
        yield line


def _parse_samplesheet_miseq(samplesheet_path):
    """
    """
    target_section_tag = "[Data]"
    project_id_field = "Sample_Project"
    parsed_samplesheet = {}

    with open(samplesheet_path, 'r', newline="", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(target_section_tag):
                break
        bounded_stream = _read_until_next_section(f)
        reader = csv.DictReader(bounded_stream)
        for row in reader:
            print(json.dumps(row))
            exit()


def _parse_samplesheet_nextseq(samplesheet_path):
    """
    """
    target_section_tag = "[Cloud_Data]"
    project_id_field = "ProjectName"
    parsed_samplesheet = {}

    with open(samplesheet_path, 'r', newline="", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(target_section_tag):
                break
    


def _parse_samplesheet_i100(samplesheet_path):
    """
    """
    target_section_tag = "[Cloud_Data]"
    project_id_field = "ProjectName"
    parsed_samplesheet = {}

    with open(samplesheet_path, 'r', newline="", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith(target_section_tag):
                break
        

    
def parse_samplesheet(samplesheet_path: Path, instrument_type: str):
    """
    """
    parsed_samplesheet = {}
    if instrument_type == 'nextseq':
        parsed_samplesheet = _parse_samplesheet_nextseq(samplesheet_path)
    elif instrument_type == 'miseq':
        parsed_samplesheet = _parse_samplesheet_miseq(samplesheet_path)
    elif instrument_type == 'i100':
        parsed_samplesheet = _parse_samplesheet_i100(samplesheet_path)
    
    return parsed_samplesheet
