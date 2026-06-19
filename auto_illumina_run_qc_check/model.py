from dataclasses import dataclass, field, fields
from enum import StrEnum
from pathlib import Path
from typing import Optional



@dataclass
class Config:
    scan_interval_seconds: int = 3600
    notification: dict = field(default_factory=dict)
    qc_thresholds: list[dict] = field(default_factory=list)
    run_parent_dirs: list[Path] = field(default_factory=list)
    excluded_runs_list: Optional[Path] = None
    excluded_runs: list[str] = field(default_factory=list)
    projects_definition_file: Optional[Path] = None
    projects: list[dict] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict):
        # Get all valid field names for this dataclass
        valid_fields = {f.name for f in fields(cls)}
        # Filter the input dictionary
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
class InstrumentType(StrEnum):
    miseq   = "miseq"
    nextseq = "nextseq"
    i100    = "i100"
    unknown = "unknown"
