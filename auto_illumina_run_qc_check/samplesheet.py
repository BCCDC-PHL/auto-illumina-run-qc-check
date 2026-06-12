import csv
import glob
import json
import logging
import os

from pathlib import Path

from auto_illumina_run_qc_check.core import determine_instrument_type

from typing import Optional

def find_samplesheet_path(run_dir: Path) -> Optional[Path]:
    """
    """
    samplesheet_path = None
    run_id = run_dir.name
    instrument_type = determine_instrument_type(run_id)

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
    
    
def parse_samplesheet(samplesheet_path: Path, instrument_type: str):
    """
    """
    parsed_samplesheet = {}
    
    return parsed_samplesheet
